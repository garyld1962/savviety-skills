#!/usr/bin/env python3
"""Probe external AI CLIs for adversarial review availability."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


COMMANDS = {
    "claude": [["claude", "--version"], ["claude", "-p", "ok"]],
    "gemini": [["gemini", "--version"], ["gemini", "-p", "ok"]],
    "codex": [["codex", "--version"]],
}


def probe(name: str) -> dict[str, object]:
    path = shutil.which(name)
    result: dict[str, object] = {"name": name, "path": path, "available": False, "checks": []}
    if path is None:
        return result

    checks = []
    for command in COMMANDS[name]:
        try:
            completed = subprocess.run(command, text=True, capture_output=True, timeout=10, check=False)
            ok = completed.returncode == 0
            output = (completed.stdout or completed.stderr).strip().splitlines()
            checks.append({"command": command, "ok": ok, "output": output[0][:160] if output else ""})
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"command": command, "ok": False, "output": str(exc)})
    result["checks"] = checks
    result["available"] = all(bool(check["ok"]) for check in checks)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefer", choices=["claude", "gemini", "codex"], action="append", default=[])
    args = parser.parse_args()

    order = args.prefer or ["claude", "gemini", "codex"]
    seen = []
    ordered = []
    for name in order + ["claude", "gemini", "codex"]:
        if name not in seen:
            seen.append(name)
            ordered.append(name)

    probes = [probe(name) for name in ordered]
    selected = next((item["name"] for item in probes if item["available"]), None)
    print(json.dumps({"selected": selected, "probes": probes}, indent=2))
    return 0 if selected else 1


if __name__ == "__main__":
    sys.exit(main())

