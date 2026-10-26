#!/usr/bin/env python3
"""Read-only task-graph validation. Requires Python 3 and PyYAML."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("FAIL: PyYAML is required; install it in the project's Python environment.")


class UniqueLoader(yaml.SafeLoader):
    pass


# Treat date-like metadata as strings, so --json has the same read-only behavior.
UniqueLoader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in values if tag != "tag:yaml.org,2002:timestamp"]
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("YAML mapping keys must be strings")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
TASK = re.compile(r"^## Task ([1-9][0-9]*):\s+(.+)$")
GLOB = re.compile(r"[*?\[]")
PLACEHOLDER = re.compile(r"^(?:TBD|TODO|FIXME|<FILL IN>|\?\?\?)$", re.I)


def mapping(text, label, errors):
    try:
        result = yaml.load(text, Loader=UniqueLoader)
        if not isinstance(result, dict):
            raise ValueError("expected a YAML mapping")
        return result
    except (yaml.YAMLError, ValueError, TypeError, RecursionError) as exc:
        errors.append(f"{label}: {exc}")
        return {}


def outside_fences(lines):
    """Yield line numbers outside both backtick and tilde fenced code blocks."""
    fence = None
    for i, line in enumerate(lines):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            yield i


def valid_scope(scope):
    return (isinstance(scope, str) and bool(scope) and not scope.startswith(("/", "~", "!"))
            and not any(c in scope for c in "\\{}:\n\r")
            and not any(part in ("", ".", "..") for part in scope.split("/")))


def overlap(a, b):
    ag, bg = GLOB.search(a), GLOB.search(b)
    if not ag and not bg:
        return a == b
    if not ag:
        return fnmatch.fnmatchcase(a, b)
    if not bg:
        return fnmatch.fnmatchcase(b, a)
    ap, bp = a[:ag.start()], b[:bg.start()]
    return ap.startswith(bp) or bp.startswith(ap)


def parse_plan(path):
    errors = []
    raw = path.read_bytes()
    lines = raw.decode("utf-8-sig").splitlines()
    result = {"plan_file": str(path), "plan_sha": hashlib.sha256(raw).hexdigest(),
              "metadata": {}, "tasks": [], "errors": errors}
    if not lines or lines[0] != "---":
        errors.append("required YAML frontmatter is missing")
        return result
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append("YAML frontmatter is unterminated")
        return result
    meta = mapping("\n".join(lines[1:end]), "frontmatter", errors)
    try:
        json.dumps(meta, allow_nan=False)
    except (ValueError, TypeError, RecursionError):
        errors.append("frontmatter must contain finite JSON-compatible YAML values")
        meta = {}
    result["metadata"] = meta
    for field in ("slug", "source_prd", "intent", "type"):
        value = meta.get(field)
        if not isinstance(value, str) or not value.strip() or PLACEHOLDER.fullmatch(value):
            errors.append(f"frontmatter requires a substantive string: {field}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(meta.get("slug", ""))):
        errors.append("slug must be kebab-case")
    if meta.get("type") not in ("bug", "feature", "refactor", "infra"):
        errors.append("type must be bug, feature, refactor, or infra")
    body = lines[end + 1:]
    visible = list(outside_fences(body))
    nonblank = [body[i] for i in visible if body[i].strip()]
    if not nonblank or not nonblank[0].startswith("# "):
        errors.append("first content after frontmatter must be an H1 title")
    starts = [(i, TASK.fullmatch(body[i])) for i in visible if TASK.fullmatch(body[i])]
    header_end = starts[0][0] if starts else len(body)
    header = [body[i] for i in visible if i < header_end]
    if not any(re.match(r"^\*\*Source:\*\*\s+\S", line) for line in header):
        errors.append("a nonempty **Source:** line is required before tasks")
    for i in visible:
        if re.match(r"^## (?:Waves\b|Parallel Execution\b|--- WAVE\b)", body[i]):
            errors.append(f"line {end + i + 2}: migrate legacy wave/lane metadata to dependencies")
        if re.match(r"^#{1,6}\s+Task\b", body[i]) and not TASK.fullmatch(body[i]):
            errors.append(f"invalid task heading: {body[i]}")
    if not starts:
        errors.append("no ## Task N: Title sections")
    for index, (start, match) in enumerate(starts):
        stop = starts[index + 1][0] if index + 1 < len(starts) else len(body)
        # A later non-task H2 ends the task; its bullets cannot prove this task.
        stop = next((i for i in visible if start < i < stop and body[i].startswith("## ")), stop)
        chunk = body[start + 1:stop]
        while chunk and not chunk[0].strip():
            chunk.pop(0)
        task_id = int(match.group(1))
        label = f"Task {task_id}"
        task_meta = {}
        if not chunk or chunk[0].strip() != "```yaml":
            errors.append(f"{label}: first content must be a fenced yaml metadata block")
        else:
            try:
                close = next(i for i in range(1, len(chunk)) if chunk[i].strip() == "```")
                task_meta = mapping("\n".join(chunk[1:close]), label, errors)
                chunk = chunk[close + 1:]
            except StopIteration:
                errors.append(f"{label}: unterminated metadata block")
        deps, scopes = task_meta.get("depends_on"), task_meta.get("write_scope")
        if not isinstance(deps, list) or not all(type(d) is int and d > 0 for d in deps):
            errors.append(f"{label}: depends_on must be a list of positive integer IDs")
            deps = []
        if len(set(deps)) != len(deps):
            errors.append(f"{label}: duplicate dependencies")
        if not isinstance(scopes, list) or not scopes or not all(valid_scope(s) for s in scopes):
            errors.append(f"{label}: write_scope requires nonempty repository-relative paths/globs")
            scopes = []
        if type(task_meta.get("milestone_end")) is not bool:
            errors.append(f"{label}: milestone_end must be a YAML boolean")
        acceptance, in_acceptance = [], False
        for i in outside_fences(chunk):
            line = chunk[i].strip()
            if line == "**Acceptance:**":
                in_acceptance = True
            elif in_acceptance and (line.startswith("#") or re.match(r"^\*\*.+:\*\*", line)):
                in_acceptance = False
            elif in_acceptance and re.match(r"^[-*] \S", line):
                criterion = line[2:].strip()
                if PLACEHOLDER.fullmatch(criterion):
                    errors.append(f"{label}: placeholder acceptance criterion")
                acceptance.append(criterion)
        if not acceptance:
            errors.append(f"{label}: missing nonempty **Acceptance:** bullets")
        result["tasks"].append({"id": task_id, "title": match.group(2),
                                "depends_on": deps, "write_scope": scopes,
                                "milestone_end": task_meta.get("milestone_end"),
                                "acceptance": acceptance})
    tasks = result["tasks"]
    ids = [t["id"] for t in tasks]
    if ids != sorted(set(ids)):
        errors.append("task IDs must be unique and ascending")
    by_id = {t["id"]: t for t in tasks}
    for task in tasks:
        for dep in task["depends_on"]:
            if dep not in by_id or dep == task["id"]:
                errors.append(f"Task {task['id']}: unknown or self dependency {dep}")
    ancestors = {}
    def visit(task_id, trail):
        if task_id in trail:
            raise ValueError(f"dependency cycle involving Task {task_id}")
        if task_id not in ancestors:
            found = set()
            for dep in by_id[task_id]["depends_on"]:
                if dep in by_id:
                    found.add(dep)
                    found.update(visit(dep, trail | {task_id}))
            ancestors[task_id] = found
        return ancestors[task_id]
    try:
        for task_id in by_id:
            visit(task_id, set())
    except (ValueError, RecursionError) as exc:
        errors.append(str(exc))
        return result
    for i, a in enumerate(tasks):
        for b in tasks[i + 1:]:
            if a["id"] in ancestors[b["id"]] or b["id"] in ancestors[a["id"]]:
                continue
            collision = next(((x, y) for x in a["write_scope"] for y in b["write_scope"] if overlap(x, y)), None)
            if collision:
                errors.append(f"Tasks {a['id']} and {b['id']} may overlap: {collision}; narrow scopes or add a dependency")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true", help="emit parsed graph, plan hash and errors")
    args = parser.parse_args()
    try:
        result = parse_plan(args.path)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"errors": [str(exc)]}
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["errors"]:
        print("FAIL:\n" + "\n".join(f"- {e}" for e in result["errors"]))
    else:
        print(f"Structural validation passed: {args.path}; semantic/readiness review still required.")
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
