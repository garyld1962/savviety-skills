#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CODEX = ROOT / "codex"
PLUGIN = CODEX / "plugins" / "savviety-workflows"


def main() -> int:
    failures: list[str] = []
    failures.extend(validate_plugin())
    failures.extend(validate_marketplace())
    failures.extend(validate_skills())
    failures.extend(validate_agents())
    failures.extend(validate_json(CODEX / "templates" / "hooks.json"))
    failures.extend(validate_json(PLUGIN / "hooks" / "hooks.json", optional=True))
    failures.extend(validate_rules())

    if failures:
        print("Codex asset validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Codex asset validation passed.")
    return 0


def validate_plugin() -> list[str]:
    failures = []
    path = PLUGIN / ".codex-plugin" / "plugin.json"
    data, error = load_json(path)
    if error:
        return [error]
    for field in ["name", "version", "description", "skills"]:
        if not data.get(field):
            failures.append(f"{path}: missing {field}")
    skills_path = PLUGIN / data.get("skills", "")
    if not skills_path.exists():
        failures.append(f"{path}: skills path does not exist: {skills_path}")
    return failures


def validate_marketplace() -> list[str]:
    candidates = [ROOT / ".agents" / "plugins" / "marketplace.json", ROOT / ".claude-plugin" / "marketplace.json"]
    existing = [path for path in candidates if path.exists()]
    if not existing:
        return ["missing repo plugin marketplace (.agents/plugins/marketplace.json or .claude-plugin/marketplace.json)"]
    failures = []
    for path in existing:
        data, error = load_json(path)
        if error:
            failures.append(error)
            continue
        if not data.get("plugins"):
            failures.append(f"{path}: plugins array is empty")
    return failures


def validate_skills() -> list[str]:
    failures = []
    skills_root = PLUGIN / "skills"
    if not skills_root.exists():
        return [f"missing skills directory: {skills_root}"]
    for skill in sorted(skills_root.iterdir()):
        if not skill.is_dir():
            continue
        path = skill / "SKILL.md"
        if not path.exists():
            failures.append(f"{skill}: missing SKILL.md")
            continue
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            failures.append(f"{path}: missing YAML frontmatter")
            continue
        frontmatter = match.group(1)
        if not re.search(r"^name:\s*[\w-]+", frontmatter, re.M):
            failures.append(f"{path}: missing name")
        desc = re.search(r"^description:\s*(.+)", frontmatter, re.M)
        if not desc or len(desc.group(1).strip().strip('"')) < 20:
            failures.append(f"{path}: description missing or too short")
    return failures


def validate_agents() -> list[str]:
    failures = []
    for path in sorted((CODEX / "agents").glob("*.toml")):
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"{path}: invalid TOML: {exc}")
            continue
        for field in ["name", "description", "developer_instructions"]:
            if not data.get(field):
                failures.append(f"{path}: missing {field}")
    return failures


def validate_rules() -> list[str]:
    failures = []
    for path in sorted((CODEX / "templates" / "rules").glob("*.rules")):
        text = path.read_text(encoding="utf-8")
        if "prefix_rule(" not in text:
            failures.append(f"{path}: no prefix_rule entries")
        if "pattern =" not in text:
            failures.append(f"{path}: no pattern field")
    return failures


def validate_json(path: Path, optional: bool = False) -> list[str]:
    if optional and not path.exists():
        return []
    _, error = load_json(path)
    return [error] if error else []


def load_json(path: Path) -> tuple[dict, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return {}, f"{path}: invalid JSON: {exc}"


if __name__ == "__main__":
    raise SystemExit(main())
