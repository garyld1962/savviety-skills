#!/usr/bin/env python3
"""Summarize a .test-plan/plan-latest.json file."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", default=".test-plan/plan-latest.json")
    args = parser.parse_args()

    path = Path(args.plan)
    data = json.loads(path.read_text())
    specs = data.get("specifications") or data.get("specs") or []
    priorities = Counter(str(spec.get("priority", "unknown")).upper() for spec in specs if isinstance(spec, dict))
    files = Counter(str(spec.get("testFile", spec.get("test_file", "unknown"))) for spec in specs if isinstance(spec, dict))

    print(f"Plan: {path}")
    print(f"Verdict: {data.get('verdict', 'unknown')}")
    print(f"Specs: {len(specs)}")
    if priorities:
        print("Priorities: " + ", ".join(f"{k}={v}" for k, v in sorted(priorities.items())))
    if files:
        print("Files:")
        for file, count in sorted(files.items()):
            print(f"  {file}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

