#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TASK_RE = re.compile(r"^(#{2,3}\s+Task\s+\d+[:.]|\d+\.\s+|- \[[ xX]\]\s+)")
PLACEHOLDER_RE = re.compile(r"\b(TBD|TODO|FIXME|TK)\b|\?\?\?|\[placeholder\]|<fill in>", re.I)
AMBIG_RE = re.compile(r"^(#{2,3}\s+Task\s+\d+[:.]\s*)?(Consider|Maybe|Possibly|Look into|Investigate whether|Explore|Think about)\b", re.I)
VERIFY_RE = re.compile(r"(test -f|npm test|pnpm test|yarn test|pytest|go test|cargo test|dotnet test|tsc\b|jq -e|grep -q|curl\b|HTTP \d{3}|\.test\.|\.spec\.)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?")
    ns = parser.parse_args()
    path = Path(ns.path) if ns.path else newest_plan()
    failures: list[str] = []

    if not path or not path.exists() or path.suffix != ".md" or not path.read_text(encoding="utf-8").strip():
        print(f"FAIL: Plan file not found, unreadable, empty, or not markdown: {path}")
        return 1

    lines = path.read_text(encoding="utf-8").splitlines()
    body_start = skip_frontmatter(lines)
    first_content = next(((i, line) for i, line in enumerate(lines[body_start:], start=body_start + 1) if line.strip()), None)
    if not first_content or not first_content[1].startswith("# "):
        failures.append("Plan has no H1 title after optional YAML frontmatter.")

    task_lines = [(i + 1, line) for i, line in enumerate(lines) if TASK_RE.search(line)]
    if not task_lines:
        failures.append("Plan has no discrete tasks. Use task headings, numbered list items, or checkboxes.")

    placeholder_hits = [(i + 1, line.strip()) for i, line in enumerate(lines) if PLACEHOLDER_RE.search(line)]
    if placeholder_hits:
        sample = ", ".join(f"line {n}" for n, _ in placeholder_hits[:10])
        failures.append(f"Plan contains {len(placeholder_hits)} placeholder(s): {sample}.")

    ambiguous = [(i + 1, line.strip()) for i, line in enumerate(lines) if AMBIG_RE.search(line.strip("# -0123456789.[]xX "))]
    if ambiguous:
        sample = "; ".join(f"line {n}: {text}" for n, text in ambiguous[:5])
        failures.append(f"Task title uses ambiguous opener: {sample}.")

    acceptance_failures = check_acceptance(lines, task_lines)
    failures.extend(acceptance_failures[:5])

    failures.extend(check_closed_decisions(lines))
    failures.extend(check_parallel_execution(lines))

    if failures:
        print("Plan validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Plan validation passed: {path}")
    return 0


def newest_plan() -> Path | None:
    root = Path("docs/plans")
    if not root.exists():
        return None
    plans = sorted(root.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return plans[0] if plans else None


def skip_frontmatter(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return i + 1
    return 0


def check_acceptance(lines: list[str], task_lines: list[tuple[int, str]]) -> list[str]:
    failures = []
    if not task_lines:
        return failures
    starts = [n - 1 for n, _ in task_lines] + [len(lines)]
    for idx, start in enumerate(starts[:-1], start=1):
        chunk = lines[start : starts[idx]]
        acceptance = [line for line in chunk if "acceptance" in line.lower() or VERIFY_RE.search(line)]
        if not acceptance or not any(VERIFY_RE.search(line) for line in acceptance):
            failures.append(
                f"Task {idx} has no verifiable acceptance criteria. Use a test, command, observable state, or schema check."
            )
    return failures


def section(lines: list[str], heading: str) -> tuple[int, int] | None:
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return start, end


def check_closed_decisions(lines: list[str]) -> list[str]:
    loc = section(lines, "## Closed Decisions")
    if not loc:
        return []
    failures = []
    start, end = loc
    bullet_re = re.compile(r"^-\s+\*\*[^*]+:\*\*\s+.+\bSource:\s+.+")
    ref_re = re.compile(r"^-\s+@closed-decisions/[\w./-]+$")
    for i, line in enumerate(lines[start + 1 : end], start=start + 2):
        if not line.strip() or line.startswith("#"):
            continue
        if line.lstrip().startswith("- ") and not (bullet_re.search(line.strip()) or ref_re.search(line.strip())):
            failures.append(f"Closed Decision on line {i} is not a supported inline decision or library reference.")
    return failures


def check_parallel_execution(lines: list[str]) -> list[str]:
    loc = section(lines, "## Parallel Execution")
    if not loc:
        return []
    start, end = loc
    text = "\n".join(lines[start:end])
    failures = []
    if not re.search(r"\*\*Mode:\*\*\s+(parallel|sequential)", text):
        failures.append("Parallel Execution section missing '**Mode:** parallel' or '**Mode:** sequential'.")
    for required in ["### Ownership", "### Barriers", "### Single-Owner Files", "### Parallel Safety Checks"]:
        if required not in text:
            failures.append(f"Parallel Execution section missing {required}.")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
