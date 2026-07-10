#!/usr/bin/env python3
"""Probe whether workflow commands are available on PATH."""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Probe:
    label: str
    token: str
    path: str | None
    version: str | None = None


def first_token(command: str) -> str:
    parts = shlex.split(command)
    return parts[0] if parts else ""


def version_for(token: str) -> str | None:
    for args in ([token, "--version"], [token, "-v"]):
        try:
            result = subprocess.run(args, text=True, capture_output=True, timeout=5, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        output = (result.stdout or result.stderr).strip().splitlines()
        if output:
            return output[0][:160]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", action="append", default=[], help="Command string declared by repo delivery config.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    probes: list[Probe] = []
    missing: list[str] = []

    for command in args.command:
        token = first_token(command)
        if not token:
            continue
        path = shutil.which(token)
        if path is None:
            missing.append(token)
        probes.append(Probe(label=command, token=token, path=path, version=version_for(token) if path else None))

    if args.json:
        print(json.dumps({"ok": not missing, "missing": missing, "probes": [p.__dict__ for p in probes]}, indent=2))
    elif missing:
        print("Required toolchain missing on PATH.")
        print("  Missing: " + ", ".join(sorted(set(missing))))
    else:
        versions = [f"{p.token} ({p.version or p.path})" for p in probes]
        print("Toolchain probe OK: " + ", ".join(versions))

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

