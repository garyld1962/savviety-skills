#!/usr/bin/env python3
"""Reject unproved native execution success; does not attest evidence truth."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from datetime import datetime

from validate_plan import parse_plan


def text(value):
    return isinstance(value, str) and bool(value.strip())


def sha(value):
    return isinstance(value, str) and bool(re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value))


def validate(report, plan):
    errors, warnings = list(plan["errors"]), []
    if not isinstance(report, dict):
        return ["report must be an object"], "FAIL"
    if report.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if report.get("code_committed") is not True:
        errors.append("final code must be committed for this execution proof contract")
    if report.get("plan_sha") != plan.get("plan_sha"):
        errors.append("plan hash differs from the current plan bytes")
    head = report.get("head_sha", "")
    for field in ("head_sha", "base_sha"):
        if not sha(report.get(field)):
            errors.append(f"{field} must be a full commit SHA")
    for field in ("plan_file", "branch", "mode", "started_at", "ended_at"):
        if not text(report.get(field)):
            errors.append(f"missing {field}")
    if report.get("mode") not in ("sequential", "parallel"):
        errors.append("mode must be sequential or parallel")
    for field in ("started_at", "ended_at"):
        try:
            if datetime.fromisoformat(report.get(field, "").replace("Z", "+00:00")).tzinfo is None:
                raise ValueError("timezone missing")
        except (AttributeError, TypeError, ValueError):
            errors.append(f"{field} must be an ISO timestamp with timezone")
    def objects(field):
        items = report.get(field)
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            errors.append(f"{field} must be an array of objects")
            return []
        return items
    tasks = objects("tasks")
    actual_ids = [t.get("id") for t in tasks]
    expected_ids = [t["id"] for t in plan.get("tasks", [])]
    if any(type(i) is not int for i in actual_ids) or sorted(actual_ids) != sorted(expected_ids):
        errors.append("report must contain each planned task exactly once")
    for task in plan.get("tasks", []):
        found = next((t for t in tasks if t.get("id") == task["id"]), {})
        if found.get("status") != "done":
            errors.append(f"Task {task['id']} is not done")
        proof = found.get("proof", [])
        if not isinstance(proof, list) or not all(isinstance(p, dict) for p in proof):
            proof = []
        for criterion in task["acceptance"]:
            if not any(p.get("criterion") == criterion and p.get("status") == "passed"
                       and text(p.get("evidence")) and sha(p.get("verified_sha"))
                       for p in proof):
                errors.append(f"Task {task['id']} has unproved acceptance: {criterion}")
    required = report.get("required_gates")
    if not isinstance(required, list) or not all(isinstance(g, str) for g in required):
        required = []
    if not {"checkpoint", "code-review", "alignment"}.issubset(required):
        errors.append("required_gates must include checkpoint, code-review and alignment")
    gates = objects("gates")
    for name in required:
        found = [g for g in gates if g.get("name") == name]
        if len(found) != 1 or found[0].get("status") != "passed" or not text(found[0].get("evidence")):
            errors.append(f"required gate missing, malformed or not passed: {name}")
            continue
        gate = found[0]
        if gate.get("head_sha") != head:
            errors.append(f"gate {name} is stale against final head")
        if name == "alignment" and gate.get("all_tasks_implemented") is not True:
            errors.append("alignment did not confirm all tasks implemented")
    if any(g.get("name") not in required and g.get("status") != "passed" for g in gates):
        warnings.append("optional gate not passed")
    for f in objects("findings"):
        label = str(f.get("id", "unnamed"))
        if not text(f.get("id")) or not text(f.get("evidence")) or f.get("severity") not in ("critical", "major", "minor", "nit"):
            errors.append(f"finding {label} lacks ID, evidence or valid severity")
        status = f.get("status")
        if status in ("fixed", "disagree-with-evidence"):
            if not text(f.get("verification")) or (status == "disagree-with-evidence" and not text(f.get("rationale"))):
                errors.append(f"finding {label} lacks verified resolution")
        elif status == "accepted-risk":
            if not text(f.get("authorization")) or not text(f.get("rationale")):
                errors.append(f"finding {label} lacks explicit risk acceptance")
            warnings.append(label)
        elif status == "defer":
            if not text(f.get("follow_up")) or f.get("severity") in ("critical", "major"):
                errors.append(f"finding {label} cannot be deferred at completion")
            warnings.append(label)
        else:
            errors.append(f"finding {label} has no terminal disposition")
    for deviation in objects("deviations"):
        if not all(text(deviation.get(k)) for k in ("reason", "evidence", "authorization")):
            errors.append("unresolved or unsupported deviation")
        warnings.append("deviation")
    if not isinstance(report.get("open_questions"), list) or report["open_questions"]:
        errors.append("missing or unresolved open_questions")
    if not isinstance(report.get("retry_stats"), dict):
        errors.append("retry_stats must be an object")
    elif report["retry_stats"].get("exhausted"):
        errors.append("retry budget exhausted")
    if report.get("limitations"):
        warnings.append("limitations")
    verdict = "FAIL" if errors else "WARN" if warnings else "PASS"
    if report.get("verdict") != verdict:
        errors.append(f"claimed verdict {report.get('verdict')} does not match derived {verdict}")
    return errors, verdict


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    try:
        errors, verdict = validate(json.loads(args.report.read_text()), parse_plan(args.plan))
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        errors, verdict = [str(exc)], "FAIL"
    print(f"Derived verdict: {verdict}")
    for error in errors:
        print(f"- {error}")
    return int(bool(errors) or verdict == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
