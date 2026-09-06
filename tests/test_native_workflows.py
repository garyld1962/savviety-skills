"""Behavioral contract tests: graph safety, truthful verdicts, exports and installation."""
import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared/workflow-contracts/scripts"))
from validate_plan import parse_plan
from validate_report import validate

spec = importlib.util.spec_from_file_location("drawio_url", ROOT / "shared/drawio/scripts/drawio_url.py")
drawio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drawio)

HEADER = """---
slug: export-items
source_prd: docs/PRD.md
intent: Export saved items.
type: feature
---
# Export items

**Source:** docs/PRD.md
"""


def task(number, deps="[]", scope="[src/export/**]", acceptance="- `python3 -m unittest` exits 0."):
    return f"""
## Task {number}: Implement slice {number}
```yaml
depends_on: {deps}
write_scope: {scope}
milestone_end: false
```
Implement the requested behavior.

**Acceptance:**
{acceptance}
"""


class NativeContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "plan.md"

    def plan(self, text=None):
        self.path.write_text(text or HEADER + task(1))
        return parse_plan(self.path)

    def report(self, plan):
        head = "a" * 40
        return dict(schema_version=2, verdict="PASS", code_committed=True, plan_file=str(self.path),
                    plan_sha=plan["plan_sha"], base_sha="b" * 40, head_sha=head,
                    branch="feature/export", mode="sequential", started_at="2026-09-04T10:00:00Z",
                    ended_at="2026-09-04T10:10:00Z", retry_stats={"total": 0},
                    required_gates=["checkpoint", "code-review", "alignment"],
                    tasks=[{"id": t["id"], "status": "done", "proof": [
                        {"criterion": c, "status": "passed", "evidence": "checks/test-output.txt",
                         "verified_sha": head} for c in t["acceptance"]]} for t in plan["tasks"]],
                    gates=[{"name": name, "status": "passed", "head_sha": head,
                            "evidence": "checks/" + name + ".txt", "all_tasks_implemented": True}
                           for name in ("checkpoint", "code-review", "alignment")],
                    findings=[], deviations=[], open_questions=[])

    def test_valid_fanout_and_transitive_serialization(self):
        plan = self.plan(HEADER + task(1, scope="[src/contracts/**]")
                         + task(2, "[1]", "[src/api/**]")
                         + task(3, "[1]", "[src/ui/**]")
                         + task(4, "[2, 3]", "[src/contracts/**]"))
        self.assertEqual(plan["errors"], [])
        self.assertEqual(len(plan["tasks"]), 4)
        self.assertEqual(len(plan["plan_sha"]), 64)

    def test_invalid_graphs(self):
        cases = {
            "overlap": task(1) + task(2),
            "future_overlap": task(1, scope="[src/a*.ts]") + task(2, scope="[src/ab*.ts]"),
            "unknown": task(1, "[7]"), "self": task(1, "[1]"),
            "cycle": task(1, "[2]") + task(2, "[1]"),
            "duplicate_id": task(1) + task(1),
            "descending": task(2) + task(1),
            "boolean_dependency": task(1, "[true]"),
            "traversal": task(1, scope="[../outside/**]"),
            "empty_scope": task(1, scope="[]"),
            "absolute_scope": task(1, scope="[/tmp/**]"),
            "missing_acceptance": task(1, acceptance=""),
            "notes_are_not_acceptance": task(1, acceptance="") + "\n## Notes\n- Tests pass.\n",
            "duplicate_yaml": task(1).replace("depends_on: []", "depends_on: []\ndepends_on: [2]"),
            "legacy_waves": task(1) + "\n## Waves\nOld scheduling table\n",
            "hidden_task_heading": task(1) + task(2).replace("## Task", "#### Task"),
        }
        for name, body in cases.items():
            with self.subTest(name=name):
                self.assertTrue(self.plan(HEADER + body)["errors"])

    def test_code_example_does_not_add_tasks(self):
        plan = self.plan(HEADER + task(1) + "\n```markdown\n## Task 22: Example only\n```\n")
        self.assertEqual(plan["errors"], [])
        self.assertEqual([t["id"] for t in plan["tasks"]], [1])

    def test_block_yaml_and_observable_acceptance(self):
        text = HEADER + task(1, scope="\n  - src/export/**", acceptance="- An empty export contains exactly one header row.")
        self.assertEqual(self.plan(text)["errors"], [])

    def test_missing_or_invalid_plan_fails_cli(self):
        for text in ("", "---\nslug: [\n---\n", HEADER.replace("type: feature", "type: research") + task(1)):
            self.path.write_text(text)
            result = subprocess.run([sys.executable, str(ROOT / "shared/workflow-contracts/scripts/validate_plan.py"), str(self.path)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)

    def test_date_metadata_json_output(self):
        self.path.write_text((HEADER + task(1)).replace("slug: export-items", "slug: export-items\ncreated: 2026-09-04"))
        result = subprocess.run([sys.executable, str(ROOT / "shared/workflow-contracts/scripts/validate_plan.py"), str(self.path), "--json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["metadata"]["created"], "2026-09-04")

    def test_fenced_source_is_not_source(self):
        text = (HEADER + task(1)).replace("**Source:** docs/PRD.md", "```markdown\n**Source:** docs/PRD.md\n```")
        self.assertTrue(self.plan(text)["errors"])

    def test_complete_report_passes(self):
        plan = self.plan()
        self.assertEqual(validate(self.report(plan), plan), ([], "PASS"))

    def test_unproved_reports_cannot_pass(self):
        plan = self.plan()
        changes = {
            "missing_review": lambda r: r["gates"].pop(1),
            "null_review": lambda r: r["gates"].__setitem__(1, None),
            "false_alignment": lambda r: r["gates"][2].update(all_tasks_implemented=False),
            "stale_head": lambda r: r["gates"][0].update(head_sha="c" * 40),
            "missing_proof": lambda r: r["tasks"][0].update(proof=[]),
            "manual_is_not_pass": lambda r: r["tasks"][0]["proof"][0].update(status="manual"),
            "missing_task": lambda r: r.update(tasks=[]),
            "duplicate_task": lambda r: r["tasks"].append(copy.deepcopy(r["tasks"][0])),
            "changed_plan": lambda r: r.update(plan_sha="d" * 64),
            "removed_required_gate": lambda r: r.update(required_gates=["checkpoint"]),
            "unavailable_check": lambda r: r["gates"][0].update(status="unavailable"),
            "unresolved_question": lambda r: r.update(open_questions=["Which account owns exports?"]),
            "boolean_proof": lambda r: r["tasks"][0]["proof"][0].update(evidence=True),
            "boolean_gate": lambda r: r["gates"][1].update(evidence=True),
            "wrong_sha_length": lambda r: r.update(head_sha="a" * 41),
            "numeric_sha": lambda r: r["tasks"][0]["proof"][0].update(verified_sha=int("1" * 40)),
            "boolean_timestamp": lambda r: r.update(started_at=True),
            "retry_exhaustion": lambda r: r.update(retry_stats={"exhausted": True}),
            "uncommitted_code": lambda r: r.update(code_committed=False),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                report = self.report(plan)
                change(report)
                errors, verdict = validate(report, plan)
                self.assertTrue(errors)
                self.assertEqual(verdict, "FAIL")

    def test_disposition_evidence_and_risk(self):
        plan = self.plan()
        base = {"id": "F1", "evidence": "src/export.py:9", "severity": "minor"}
        for extra, expected in [
            ({"status": "open"}, "FAIL"),
            ({"status": "fixed"}, "FAIL"),
            ({"status": "fixed", "verification": True}, "FAIL"),
            ({"status": "fixed", "verification": "checks/regression.txt"}, "PASS"),
            ({"status": "accepted-risk", "rationale": "scheduled follow-up"}, "FAIL"),
            ({"status": "accepted-risk", "rationale": "scheduled follow-up", "authorization": "user accepted F1 in this run"}, "WARN"),
            ({"status": "defer", "follow_up": "Owner: maintainer; issue #3"}, "WARN"),
            ({"status": "defer", "follow_up": "issue #3", "severity": "critical"}, "FAIL"),
        ]:
            with self.subTest(extra=extra):
                report = self.report(plan)
                report["findings"] = [base | extra]
                report["verdict"] = expected
                self.assertEqual(validate(report, plan)[1], expected)

    def test_drawio_url_round_trip_and_invalid_graph(self):
        xml = '<mxfile><diagram><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="a" vertex="1" value="Café &amp; tea" parent="1"/><mxCell id="e" edge="1" parent="1" source="a" target="a"/></root></mxGraphModel></diagram></mxfile>'
        url = drawio.editor_url(xml)
        decoded = unquote(zlib.decompress(base64.b64decode(url.split("#R")[1]), -15).decode())
        self.assertEqual(decoded, xml)
        for bad in (xml.replace('target="a"', 'target="missing"'), xml.replace('id="a"', 'id="1"'), xml.replace('target="a"', 'target="0"'), xml.replace('id="a" ', ''), '<mxfile><diagram>compressed</diagram></mxfile>', '<mxfile><diagram><mxGraphModel><foo id="0"/><bar id="1"/></mxGraphModel></diagram></mxfile>'):
            with self.assertRaises(ValueError):
                drawio.editor_url(bad)


@unittest.skipUnless(shutil.which("rsync") and shutil.which("jq"), "installer requires rsync and jq")
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "target repo"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        self.env = dict(os.environ, REPO_SKILLS_HOME=str(ROOT), REPO_SKILLS_NO_RTK="1")

    def install(self, platform, action):
        return subprocess.run(["bash", str(ROOT / "cli/skill.sh"), "--" + platform, "--" + action, str(self.target)], env=self.env, capture_output=True, text=True)

    def test_claude_installs_without_hooks_or_template_permissions(self):
        settings = self.target / ".claude/settings.json"
        local = self.target / ".claude/settings.local.json"
        for action in ("init", "update"):
            with self.subTest(action=action):
                result = self.install("claude", action)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                installed = json.loads(settings.read_text())
                self.assertNotIn("permissions", installed)
                self.assertNotIn("hooks", installed)
                self.assertEqual(json.loads(local.read_text()), {})
                local.unlink()  # Update must also recreate a missing file without grants.

    def test_claude_preserves_existing_hooks_permissions_and_settings_by_default(self):
        settings = self.target / ".claude/settings.json"
        settings.parent.mkdir()
        local = self.target / ".claude/settings.local.json"
        permissions = {"allow": ["Read"], "deny": ["Bash(rm:*)"], "ask": ["Write"]}
        local_content = '{ "permissions": { "allow": ["Bash(project-task)"] } }\n'
        local.write_text(local_content)
        old_hooks = {
            event: [{"hooks": [{"type": "command", "command": "echo old-hook"}]}]
            for event in ("SessionStart", "SessionEnd", "PreToolUse", "PostToolUse")
        }
        for action in ("init", "update"):
            with self.subTest(action=action):
                settings.write_text(json.dumps({"permissions": permissions, "hooks": old_hooks, "env": {"CUSTOM": "value"}}))
                result = self.install("claude", action)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                installed = json.loads(settings.read_text())
                self.assertEqual(installed["permissions"], permissions)
                self.assertEqual(installed["hooks"], old_hooks)
                self.assertEqual(installed["env"], {"CUSTOM": "value"})
                self.assertEqual(local.read_text(), local_content)

    def test_copilot_install_update_and_user_settings(self):
        result = self.install("copilot", "init")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for path in (".github/skills/bug-session/SKILL.md", ".github/skills/execute-plan/SKILL.md", ".github/skills/validate-plan/scripts/validate_plan.py", ".github/docs/process/document-schema.md"):
            self.assertTrue((self.target / path).is_file(), path)
        personal = self.target / ".github/instructions/personal.instructions.md"
        personal.write_text("Keep my preferences.\n")
        result = self.install("copilot", "update")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(personal.read_text(), "Keep my preferences.\n")
        plan = self.target / "plan.md"
        plan.write_text(HEADER + task(1))
        check = subprocess.run([sys.executable, str(self.target / ".github/skills/validate-plan/scripts/validate_plan.py"), str(plan)], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_codex_install_update_preserves_config(self):
        result = self.install("codex", "init")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        config = self.target / ".codex/config.toml"
        config.write_text('model = "user-choice"\n')
        agents = self.target / "AGENTS.md"
        agents.write_text("Keep my project commands.\n")
        result = self.install("codex", "update")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(config.read_text(), 'model = "user-choice"\n')
        self.assertEqual(agents.read_text(), "Keep my project commands.\n")
        self.assertTrue((self.target / ".codex/plugins/savviety-workflows/skills/vault/agents/openai.yaml").exists())
        self.assertTrue((self.target / ".codex/plugins/savviety-workflows/skills/drawio/scripts/drawio_url.py").exists())

    def test_missing_source_fails_before_writes(self):
        source = Path(self.tmp.name) / "broken source"
        (source / "claude").mkdir(parents=True)
        (source / "claude/README.md").write_text("Source fixture")
        (source / "manifest.json").write_text(json.dumps({"copilot": {"trees": [{"from": "missing", "to": ".github/skills"}]}}))
        self.env["REPO_SKILLS_HOME"] = str(source)
        result = self.install("copilot", "init")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("manifest source missing", result.stderr)
        self.assertFalse((self.target / ".github").exists())


if __name__ == "__main__":
    unittest.main()
