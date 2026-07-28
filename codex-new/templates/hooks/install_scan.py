#!/usr/bin/env python3
"""Surface a note after dependency installation commands.

This first Codex port keeps the hook local and non-blocking. A later pass can
wire OSV or SBOM scanning once network policy and package extraction are settled.
"""

from __future__ import annotations

import json
import re
import sys


INSTALL_RE = re.compile(
    r"(^|\s)(npm|pnpm|yarn|pip|cargo|go|dotnet|gem|brew)\s+(install|add|tool\s+install)\b"
)


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if not INSTALL_RE.search(command):
        return 0

    print(
        json.dumps(
            {
                "systemMessage": "Dependency install detected. Review lockfile changes and run dependency audit before shipping."
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
