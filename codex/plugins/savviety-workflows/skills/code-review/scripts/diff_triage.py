#!/usr/bin/env python3
"""Create a lightweight review manifest from changed file paths."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


LANG_BY_SUFFIX = {
    ".cs": "csharp",
    ".fs": "fsharp",
    ".go": "go",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".kt": "kotlin",
    ".py": "python",
    ".rs": "rust",
    ".sql": "sql",
    ".ts": "typescript",
    ".tsx": "typescript-react",
}


def classify(path: str) -> dict[str, object]:
    p = pathlib.PurePosixPath(path.replace("\\", "/"))
    lowered = path.lower()
    parts = set(p.parts)
    suffix = p.suffix.lower()
    return {
        "path": path,
        "language": LANG_BY_SUFFIX.get(suffix, suffix.lstrip(".") or "unknown"),
        "persistence": any(x in lowered for x in ("migration", "schema", "repository", "db/", "database", ".sql")),
        "public_surface": any(x in lowered for x in ("controller", "route", "handler", "openapi", "swagger", ".proto", "sdk", "cli")),
        "auth_security": any(x in lowered for x in ("auth", "session", "token", "permission", "crypto", "secret")),
        "concurrency": any(x in lowered for x in ("async", "queue", "worker", "lock", "thread", "job")),
        "dependency_manifest": p.name in {"package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json", "requirements.txt", "pyproject.toml", "Cargo.toml", "Cargo.lock", "go.mod", "go.sum"},
        "tests": "test" in lowered or "spec" in lowered or "__tests__" in parts,
        "generated": "generated" in parts or lowered.endswith((".g.cs", ".generated.ts")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Changed file paths. Reads stdin when omitted.")
    args = parser.parse_args()

    paths = args.paths or [line.strip() for line in sys.stdin if line.strip()]
    files = [classify(path) for path in paths]
    flags = {
        key: any(bool(file[key]) for file in files)
        for key in ("persistence", "public_surface", "auth_security", "concurrency", "dependency_manifest", "tests", "generated")
    }
    print(json.dumps({"files": files, "flags": flags}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

