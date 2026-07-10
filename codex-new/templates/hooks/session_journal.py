#!/usr/bin/env python3
"""Append minimal prompt metadata to .codex/journal/session-prompts.jsonl."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone


def main() -> int:
    payload = json.load(sys.stdin)
    cwd = git_root(pathlib.Path(payload.get("cwd") or "."))
    journal_dir = cwd / ".codex" / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": payload.get("session_id"),
        "turn_id": payload.get("turn_id"),
        "prompt": payload.get("prompt"),
    }
    with (journal_dir / "session-prompts.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    return 0


def git_root(cwd: pathlib.Path) -> pathlib.Path:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return pathlib.Path(out)
    except Exception:
        return cwd


if __name__ == "__main__":
    raise SystemExit(main())
