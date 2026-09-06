"""Hermes profile installation, conflict protection and packaged helper smoke tests."""
import json
import argparse
import contextlib
import io
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class HermesInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "source checkout"
        self.source.mkdir()
        for name in ("manifest.json", "cli/skill.sh", "bin/install-hermes-skills"):
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        shutil.copytree(ROOT / "hermes", self.source / "hermes")
        self.profile = self.base / "coder profile"
        self.env = dict(os.environ, REPO_SKILLS_HOME=str(self.source),
                        HOME=str(self.base / "home"), HERMES_HOME=str(self.profile))
        self.env.pop("BASH_ENV", None)

    def install(self, action="--init", *args):
        return subprocess.run(["bash", str(self.source / "cli/skill.sh"),
                               "--hermes", action, *args], env=self.env,
                              capture_output=True, text=True, timeout=20)

    def ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def tree(self, root):
        return {str(p.relative_to(root)): p.read_bytes()
                for p in root.rglob("*") if p.is_file()} if root.exists() else {}

    def test_profile_install_preserves_other_skills_and_configuration(self):
        (self.profile / "skills/user-skill").mkdir(parents=True)
        (self.profile / "skills/user-skill/SKILL.md").write_text("User knowledge")
        for name in ("config.yaml", ".env", "SOUL.md", "settings.json"):
            (self.profile / name).write_text("user-owned content")
        before = self.tree(self.profile)
        self.ok(self.install())
        for name, content in before.items():
            self.assertEqual((self.profile / name).read_bytes(), content)
        self.assertEqual({p.parent.name for p in (self.profile / "skills").glob("*/SKILL.md")},
                         {"user-skill", "simplify", "validate-plan", "execute-prd", "execute-plan"})
        self.assertFalse((self.profile / "hooks").exists())
        self.assertFalse((self.profile / ".git").exists())
        state = self.profile / ".savviety-skills.json"
        mtime = state.stat().st_mtime_ns
        self.ok(self.install("--update"))
        self.assertEqual(state.stat().st_mtime_ns, mtime)

    def test_default_home_and_explicit_profile_override(self):
        del self.env["HERMES_HOME"]
        self.ok(self.install())
        self.assertTrue((Path(self.env["HOME"]) / ".hermes/skills/simplify/SKILL.md").exists())
        self.env["HERMES_HOME"] = str(self.profile)
        explicit = self.base / "other profile"
        self.ok(self.install("--init", str(explicit)))
        self.assertTrue((explicit / "skills/simplify/SKILL.md").exists())
        self.assertFalse(self.profile.exists())

    def test_dry_run_init_and_update_write_nothing(self):
        self.ok(self.install("--init", "--dry-run"))
        self.assertFalse(self.profile.exists())
        self.ok(self.install())
        before = self.tree(self.profile)
        source = self.source / "hermes/skills/simplify/SKILL.md"
        source.write_text(source.read_text() + "\nNew source instruction.\n")
        self.ok(self.install("--update", "--dry-run"))
        self.assertEqual(self.tree(self.profile), before)

    def test_update_refreshes_owned_files_and_removes_retired_resources(self):
        source = self.source / "hermes/skills/simplify"
        (source / "old.txt").write_text("retired guidance")
        self.ok(self.install())
        (source / "old.txt").unlink()
        (source / "new.txt").write_text("new guidance")
        self.ok(self.install("--update"))
        self.assertFalse((self.profile / "skills/simplify/old.txt").exists())
        self.assertEqual((self.profile / "skills/simplify/new.txt").read_text(), "new guidance")
        # Withdrawn skills are retained, including their ownership record.
        shutil.rmtree(self.source / "hermes/skills/execute-prd")
        self.ok(self.install("--update"))
        self.assertTrue((self.profile / "skills/execute-prd/SKILL.md").exists())

    def test_local_edits_additions_and_deletions_stop_entire_update(self):
        self.ok(self.install())
        original = self.tree(self.profile)
        source = self.source / "hermes/skills/execute-plan/SKILL.md"
        source.write_text(source.read_text() + "\nUpstream change\n")
        for change in ("edit", "add", "delete"):
            with self.subTest(change=change):
                shutil.rmtree(self.profile)
                for name, data in original.items():
                    target = self.profile / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                skill = self.profile / "skills/simplify/SKILL.md"
                if change == "edit":
                    skill.write_text("Learned local instructions")
                elif change == "add":
                    skill.with_name("learned.md").write_text("Learned local instructions")
                else:
                    skill.unlink()
                before = self.tree(self.profile)
                result = self.install("--update")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("locally edited", result.stderr)
                self.assertEqual(self.tree(self.profile), before)

    def test_unmanaged_collision_and_invalid_state_do_not_write(self):
        (self.profile / "skills/simplify").mkdir(parents=True)
        (self.profile / "skills/simplify/SKILL.md").write_text("Existing unrelated skill")
        before = self.tree(self.profile)
        self.assertEqual(self.install().returncode, 2)
        self.assertEqual(self.tree(self.profile), before)
        (self.profile / ".savviety-skills.json").write_text("not json")
        before = self.tree(self.profile)
        self.assertEqual(self.install("--update").returncode, 2)
        self.assertEqual(self.tree(self.profile), before)

    def test_symlinks_never_redirect_skill_writes(self):
        external = self.base / "external"
        external.mkdir()
        self.profile.mkdir()
        (self.profile / "skills").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.install().returncode, 2)
        self.assertEqual(list(external.iterdir()), [])
        (self.profile / "skills").unlink()
        self.ok(self.install())
        target = self.profile / "skills/simplify/SKILL.md"
        target.unlink()
        target.symlink_to(external / "do-not-create.md")
        self.assertEqual(self.install("--update").returncode, 2)
        self.assertFalse((external / "do-not-create.md").exists())

    def test_categorized_same_name_skill_is_not_shadowed(self):
        skill = self.profile / "skills/writing/explain"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text('---\nname: "simplify"\ndescription: Explain text\n---\nExisting skill\n')
        before = self.tree(self.profile)
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("already uses the name simplify", result.stderr)
        self.assertEqual(self.tree(self.profile), before)

    def test_filesystem_failure_restores_previous_skills_and_record(self):
        self.ok(self.install())
        before = self.tree(self.profile)
        for name in ("execute-plan", "simplify"):
            source = self.source / "hermes/skills" / name / "SKILL.md"
            source.write_text(source.read_text() + "\nUpstream improvement\n")
        module = runpy.run_path(str(self.source / "bin/install-hermes-skills"))
        args = argparse.Namespace(source=self.source, target=self.profile,
                                  action="update", dry_run=False)
        with contextlib.redirect_stdout(io.StringIO()):
            with patch("os.replace", side_effect=OSError("simulated state write failure")):
                with self.assertRaises(OSError):
                    module["install"](args)
        self.assertEqual(self.tree(self.profile), before)
        self.assertEqual(list(self.profile.glob(".savviety-stage-*")), [])

    def test_bad_modes_and_missing_sources_do_not_write(self):
        self.assertEqual(self.install("--update").returncode, 2)
        for flag in ("--force", "--prune", "--yes"):
            self.assertNotEqual(self.install("--update", flag).returncode, 0)
        shutil.rmtree(self.source / "hermes/skills")
        self.assertEqual(self.install().returncode, 2)
        self.assertFalse(self.profile.exists())

    def test_packaged_helpers_accept_valid_plan_and_reject_unproved_success(self):
        self.ok(self.install())
        # Run from outside the source checkout, using only installed resources.
        scripts = self.profile / "skills/validate-plan/scripts"
        plan = self.base / "plan.md"
        plan.write_text('''---
slug: greeting
source_prd: request.md
intent: Print a greeting.
type: feature
---
# Greeting

**Source:** request.md

## Task 1: Print a greeting
```yaml
depends_on: []
write_scope: [greeting.py]
milestone_end: true
```
Print Hello.

**Acceptance:**
- `python3 greeting.py` prints Hello and exits 0.
''')
        valid = subprocess.run([sys.executable, str(scripts / "validate_plan.py"), str(plan)],
                               cwd=self.base, capture_output=True, text=True)
        self.ok(valid)
        plan.write_text(plan.read_text().replace("depends_on: []", "depends_on: [1]"))
        invalid = subprocess.run([sys.executable, str(scripts / "validate_plan.py"), str(plan)],
                                 cwd=self.base, capture_output=True, text=True)
        self.assertNotEqual(invalid.returncode, 0)
        plan.write_text(plan.read_text().replace("depends_on: [1]", "depends_on: []"))
        report = self.base / "execution-report.json"
        report.write_text(json.dumps({"schema_version": 2, "verdict": "PASS"}))
        unproved = subprocess.run([sys.executable, str(scripts / "validate_report.py"),
                                   str(report), "--plan", str(plan)], cwd=self.base,
                                  capture_output=True, text=True)
        self.assertNotEqual(unproved.returncode, 0)
        self.assertNotIn("ModuleNotFoundError", unproved.stderr)
        self.ok(self.install("--update"))  # Running scripts can create __pycache__.


if __name__ == "__main__":
    unittest.main()
