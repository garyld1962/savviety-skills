#!/usr/bin/env python3
"""Block accidental `gh pr create` when the branch already has an open PR."""

from __future__ import annotations

import json
import subprocess
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if "gh pr create" not in command:
        return 0

    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        branch = ""

    if not branch:
        return 0

    try:
        prs = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--head",
                branch,
                "--state",
                "open",
                "--json",
                "number,title,url",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        open_prs = json.loads(prs)
    except Exception:
        return 0

    if not open_prs:
        return 0

    first = open_prs[0]
    reason = (
        f"Current branch already has an open PR: "
        f"#{first.get('number')} {first.get('title')} {first.get('url')}. "
        "Update the existing PR or confirm that a second PR is intentional."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
