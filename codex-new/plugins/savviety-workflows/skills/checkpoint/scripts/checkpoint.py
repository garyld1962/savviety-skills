#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> int:
    commands = discover_commands()
    if not commands:
        print("No checkpoint commands discovered. Provide lint, build/typecheck, and test commands.")
        return 1

    failed = []
    for label, command in commands:
        print(f"\n== {label}: {command}")
        proc = subprocess.run(command, shell=True)
        if proc.returncode != 0:
            failed.append((label, command, proc.returncode))

    if failed:
        print("\nCheckpoint failed:")
        for label, command, code in failed:
            print(f"- {label} exited {code}: {command}")
        return 1

    print("\nCheckpoint passed.")
    return 0


def discover_commands() -> list[tuple[str, str]]:
    root = Path.cwd()
    pkg = root / "package.json"
    if pkg.exists():
        data = json.loads(pkg.read_text(encoding="utf-8"))
        scripts = data.get("scripts") or {}
        runner = "pnpm" if (root / "pnpm-lock.yaml").exists() else "yarn" if (root / "yarn.lock").exists() else "npm"
        run = "run" if runner != "yarn" else ""
        commands = []
        for label, names in [
            ("lint", ["lint"]),
            ("typecheck", ["typecheck", "tsc"]),
            ("build", ["build"]),
            ("test", ["test"]),
        ]:
            name = next((n for n in names if n in scripts), None)
            if name:
                commands.append((label, " ".join(part for part in [runner, run, name] if part)))
        return commands
    if (root / "pyproject.toml").exists():
        return [("test", "pytest")]
    if (root / "go.mod").exists():
        return [("test", "go test ./...")]
    if (root / "Cargo.toml").exists():
        return [("test", "cargo test")]
    return []


if __name__ == "__main__":
    raise SystemExit(main())
