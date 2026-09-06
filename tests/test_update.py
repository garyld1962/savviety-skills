"""Exercise the update entrypoint with real settings updates and stubbed packages."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("jq") and shutil.which("rsync"), "requires jq and rsync")
class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "source checkout"
        self.target = self.base / "target repo"
        self.user_dir = self.base / "user home"
        for path in (self.source, self.target, self.user_dir):
            path.mkdir()
        for name in ("update.sh", "install.sh", "cli/skill.sh"):
            destination = self.source / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        (self.source / "claude/example").mkdir(parents=True)
        (self.source / "claude/README.md").write_text("Fixture\n")
        (self.source / "claude/example/SKILL.md").write_text("Example skill\n")
        shutil.copy2(ROOT / "claude/settings.template.json", self.source / "claude/settings.template.json")
        (self.source / "manifest.json").write_text(json.dumps({
            "claude": {
                "skills": {"from": "claude", "to": ".claude/skills",
                           "skip": ["README.md", "settings.template.json"], "preserve_subdirs": []},
                "extras": [{"from": "claude/settings.template.json", "to": ".claude/settings.json"}],
                "ensure": [{"to": ".claude/settings.local.json", "content": "{}\n"}],
                "starters": [],
            }, "user_owned": [".claude/settings.local.json"],
        }))
        (self.source / "bin").mkdir()
        shutil.copy2(ROOT / "bin/install-hermes-skills", self.source / "bin/install-hermes-skills")
        shutil.copytree(ROOT / "hermes", self.source / "hermes")
        manifest_path = self.source / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["hermes"] = {"skills": {"from": "hermes/skills", "to": "skills"}}
        manifest_path.write_text(json.dumps(manifest))
        (self.source / "bin/install-agentic-tools").write_text('''#!/bin/bash
command -v skills >/dev/null || exit 9
echo tools >> "$TEST_LOG"
exit "${TEST_TOOLS_EXIT:-0}"
''')
        self.log = self.base / "calls"
        self.env = dict(os.environ, HOME=str(self.user_dir), SHELL=shutil.which("bash"),
                        PATH=os.defpath, TEST_LOG=str(self.log),
                        REPO_SKILLS_HOME="/invalid/stale-checkout")
        for name in ("BASH_ENV", "ENV", "ZDOTDIR"):
            self.env.pop(name, None)
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)

    def update(self, *args):
        return subprocess.run([str(self.source / "update.sh"), *args], cwd=self.target,
                              env=self.env, capture_output=True, text=True, timeout=20)

    def test_initializes_then_updates_settings_without_changing_local_configuration(self):
        result = self.update()  # Default target is the caller's current directory.
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((self.target / ".claude/settings.json").read_text()), {})
        local = self.target / ".claude/settings.local.json"
        self.assertEqual(json.loads(local.read_text()), {})
        local_content = '{ "permissions": { "allow": ["Read"] }, "hooks": {} }\n'
        local.write_text(local_content)
        settings = self.target / ".claude/settings.json"
        settings.write_text(json.dumps({"permissions": {"deny": ["Write"]},
                                        "hooks": {"SessionStart": [{"hooks": []}]}}))
        result = self.update(str(self.target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(settings.read_text()), {"permissions": {"deny": ["Write"]}})
        self.assertEqual(local.read_text(), local_content)
        self.assertTrue((self.target / ".claude/skills/example/SKILL.md").is_file())
        self.assertEqual(self.log.read_text().splitlines(), ["tools", "tools"])
        self.assertEqual((self.user_dir / ".local/bin/skills").resolve(), self.source / "cli/skill.sh")

    def test_tool_failure_stops_before_settings_are_changed(self):
        settings = self.target / ".claude/settings.json"
        settings.parent.mkdir()
        original = '{"hooks": {"SessionStart": []}}\n'
        settings.write_text(original)
        self.env["TEST_TOOLS_EXIT"] = "1"
        result = self.update()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(settings.read_text(), original)
        self.assertFalse((self.target / ".claude/skills").exists())
        self.assertNotIn("utilities are installed", result.stdout)

    def test_help_and_invalid_targets_do_not_install(self):
        for args, expected in [(('--help',), 0), ((str(self.base),), 2),
                               (('--unknown',), 1), (('a', 'b'), 1)]:
            with self.subTest(args=args):
                result = self.update(*args)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertFalse(self.log.exists())
                self.assertFalse((self.user_dir / ".local").exists())

    def test_hermes_update_uses_profile_and_shared_utilities(self):
        profile = self.base / "Hermes profile"
        self.env["HERMES_HOME"] = str(profile)
        for _ in range(2):
            result = self.update("--hermes")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((profile / "skills/execute-plan/SKILL.md").exists())
        self.assertEqual(self.log.read_text().splitlines(), ["tools", "tools"])
        self.assertFalse((self.target / ".claude").exists())
        self.assertFalse((profile / "config.yaml").exists())

    def test_hermes_collision_stops_before_installing_utilities(self):
        profile = self.base / "Hermes profile"
        skill = profile / "skills/simplify"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("Existing skill")
        result = self.update("--hermes", str(profile))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(self.log.exists())
        self.assertFalse((self.user_dir / ".local").exists())
        self.assertEqual((skill / "SKILL.md").read_text(), "Existing skill")


if __name__ == "__main__":
    unittest.main()
