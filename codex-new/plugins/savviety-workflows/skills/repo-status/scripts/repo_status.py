#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
from datetime import datetime, timezone


def run(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(args, text=True, capture_output=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git(args: list[str]) -> tuple[int, str, str]:
    return run(["git", *args])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    ns = parser.parse_args()

    code, root, _ = git(["rev-parse", "--show-toplevel"])
    if code != 0:
        print("Not a git repository.")
        return 1

    _, branch, _ = git(["branch", "--show-current"])
    detached = not branch
    if detached:
        _, branch, _ = git(["rev-parse", "--short", "HEAD"])
        branch = f"detached@{branch}"

    up_code, upstream, _ = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    ahead = behind = None
    if up_code == 0:
        count_code, counts, _ = git(["rev-list", "--left-right", "--count", "@{u}...HEAD"])
        if count_code == 0 and counts:
            left, right = counts.split()
            behind, ahead = int(left), int(right)

    _, status, _ = git(["status", "--short"])
    status_lines = [line for line in status.splitlines() if line]
    modified = sum(1 for line in status_lines if not line.startswith("??"))
    untracked = sum(1 for line in status_lines if line.startswith("??"))

    _, stashes, _ = git(["stash", "list"])
    stash_lines = [line for line in stashes.splitlines() if line]

    log_n = "10" if ns.full else "5"
    _, recent, _ = git(["log", f"-{log_n}", "--oneline"])

    unpushed = ""
    if upstream and ahead and ahead > 0:
        _, unpushed, _ = git(["log", "--oneline", f"{upstream}..HEAD"])

    print(f"{os.path.basename(root)} - {branch} @ {socket.gethostname()}")
    if upstream:
        print(f"Tracking: {upstream} ({ahead} ahead, {behind} behind)")
    else:
        print("Tracking: no upstream")
    if not status_lines:
        print("Working tree: clean")
    else:
        print(f"Working tree: {modified} modified, {untracked} untracked")
    if stash_lines:
        print(f"Stashes: {len(stash_lines)}")

    if unpushed:
        print("\nUnpushed commits:")
        print(indent(unpushed))

    print("\nRecent commits:")
    print(indent(recent or "(none)"))

    pr_note = pr_summary(branch, ns.full)
    if pr_note:
        print("\n" + pr_note)

    warnings = []
    if detached:
        warnings.append("Detached HEAD - not on a branch.")
    if not upstream:
        warnings.append("Branch has no upstream - push with -u before opening a PR.")
    if behind and behind > 0:
        warnings.append(f"Behind upstream by {behind}.")
    if ahead and ahead > 0:
        warnings.append(f"Unpushed commits on current branch: {ahead}.")
    if stash_lines:
        warnings.append(f"Stashed work exists: {len(stash_lines)} stash(es).")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    return 0


def indent(text: str) -> str:
    return "\n".join(f"  {line}" for line in text.splitlines())


def pr_summary(branch: str, full: bool) -> str:
    code, out, _ = run(
        [
            "gh",
            "pr",
            "list",
            "--author",
            "@me",
            "--state",
            "open",
            "--json",
            "number,title,headRefName,updatedAt,isDraft,statusCheckRollup",
        ]
    )
    if code != 0:
        return "Open PRs: skipped (gh unavailable or unauthenticated)."
    try:
        prs = json.loads(out)
    except json.JSONDecodeError:
        return "Open PRs: skipped (could not parse gh output)."
    lines = [f"Open PRs (you): {len(prs)}"]
    now = datetime.now(timezone.utc)
    for pr in prs:
        flags = []
        if pr.get("isDraft"):
            flags.append("draft")
        updated = pr.get("updatedAt") or ""
        stale = ""
        try:
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            days = (now - dt).days
            if days >= 3:
                stale = f", stale {days}d"
        except ValueError:
            days = None
        marker = " current-branch" if pr.get("headRefName") == branch else ""
        flag_text = f" [{', '.join(flags)}]" if flags else ""
        lines.append(f"  #{pr.get('number')} {pr.get('title')} - {pr.get('headRefName')}{flag_text}{marker}{stale}")
        if full:
            checks = pr.get("statusCheckRollup") or []
            if checks:
                lines.append(f"    checks: {len(checks)} reported")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
