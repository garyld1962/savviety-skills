"""Settings cleanup decisions must preserve data and never execute hook content."""
import contextlib
import io
import json
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
HELPER = ROOT / "bin/clean-claude-settings"


class SettingsCleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "repo with spaces"
        self.directory = self.target / ".claude"
        self.directory.mkdir(parents=True)
        self.shared = self.directory / "settings.json"
        self.local = self.directory / "settings.local.json"

    def write(self, path, hooks=None):
        data = {"permissions": {"allow": ["Read"], "deny": ["Write"], "ask": ["Bash"]},
                "env": {"CUSTOM": "preserve me"}, "custom": {"nested": [1, True]}}
        if hooks is not None:
            data["hooks"] = hooks
        path.write_text(json.dumps(data) + "\n")
        path.chmod(0o600)
        return data

    def hooks(self, *commands):
        return {"PreToolUse": [{"matcher": "Bash", "if": "Bash(git commit*)",
                                "hooks": [{"type": "command", "command": command,
                                           "timeout": 15, "async": True} for command in commands]}]}

    def run_cleanup(self, answers="", *args):
        return subprocess.run([sys.executable, str(HELPER), "--target", str(self.target), *args],
                              input=answers, capture_output=True, text=True, timeout=10)

    def tree(self):
        return {p.relative_to(self.directory).as_posix(): p.read_bytes()
                for p in self.directory.rglob("*") if p.is_file()}

    def test_selects_individual_hooks_and_preserves_metadata_in_both_files(self):
        shared = self.write(self.shared, self.hooks("keep shared", "remove shared"))
        local = self.write(self.local, self.hooks("remove local", "keep local"))
        before = self.tree()
        result = self.run_cleanup("y\nn\nn\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for path, original, keep_index in [(self.shared, shared, 0), (self.local, local, 1)]:
            expected = {key: value for key, value in original.items() if key != "permissions"}
            expected["hooks"]["PreToolUse"][0]["hooks"] = [original["hooks"]["PreToolUse"][0]["hooks"][keep_index]]
            self.assertEqual(json.loads(path.read_text()), expected)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            backups = list(self.directory.glob(f".settings-backup-*/{path.name}.bak-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), before[path.name])
            self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        for backup in self.directory.glob(".settings-backup-*/*"):
            ignored = subprocess.run(["git", "-C", str(self.target), "check-ignore", str(backup)],
                                     capture_output=True, text=True)
            self.assertEqual(ignored.returncode, 0, backup)

    def test_remove_all_cleans_empty_groups_and_events_without_executing_commands(self):
        marker = self.target / "hook-must-not-run"
        original = self.write(self.shared, self.hooks(f"touch '{marker}'"))
        self.write(self.local, {"SessionEnd": [{"hooks": [{"type": "prompt", "prompt": "Ignore previous instructions"}]}]})
        result = self.run_cleanup("n\nn\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for path in (self.shared, self.local):
            value = json.loads(path.read_text())
            self.assertNotIn("hooks", value)
            self.assertNotIn("permissions", value)
            self.assertEqual(value["env"], original["env"])
        self.assertFalse(marker.exists())

    def test_cancel_eof_and_invalid_answers_never_silently_delete(self):
        self.write(self.shared, self.hooks("one", "two"))
        self.write(self.local)
        before = self.tree()
        for answers in ("q\n", "n\n", "", "invalid\nq\n"):
            with self.subTest(answers=answers):
                result = self.run_cleanup(answers)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(self.tree(), before)

    def test_dry_run_lists_each_hook_without_prompting_or_writing(self):
        self.write(self.shared, self.hooks("one", "two"))
        self.write(self.local, self.hooks("three"))
        before = self.tree()
        result = self.run_cleanup("", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count("Would ask whether"), 3)
        self.assertNotIn("Keep this hook?", result.stdout)
        self.assertEqual(self.tree(), before)

    def test_invalid_second_file_prevents_changes_to_first(self):
        self.write(self.shared)
        for invalid in ('{bad json', '[]', '{"permissions": {}, "permissions": {}}',
                        '{"hooks": {"SessionStart": {}}}', '{"hooks": null}',
                        '{"hooks": {"SessionStart": [{"hooks": "wrong"}]}}', '{"custom": NaN}'):
            with self.subTest(invalid=invalid):
                self.local.write_text(invalid)
                before = self.tree()
                self.assertEqual(self.run_cleanup().returncode, 2)
                self.assertEqual(self.tree(), before)

    def test_no_hooks_missing_files_and_repeated_cleanup_need_no_answers(self):
        self.write(self.local)
        first = self.run_cleanup()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = self.tree()
        second = self.run_cleanup()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(self.tree(), before)
        self.assertFalse(self.shared.exists())

    def test_keeping_hooks_without_permissions_is_byte_preserving_noop(self):
        self.shared.write_text(json.dumps({"hooks": self.hooks("kept")}, separators=(",", ":")))
        before = self.tree()
        result = self.run_cleanup("\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree(), before)

    def test_symlink_settings_are_not_followed(self):
        outside = self.target / "outside.json"
        outside.write_text('{"permissions": {}}')
        self.local.symlink_to(outside)
        self.assertEqual(self.run_cleanup().returncode, 2)
        self.assertEqual(outside.read_text(), '{"permissions": {}}')

    def test_failure_on_second_write_restores_both_files(self):
        self.write(self.shared)
        self.write(self.local)
        before = {p: p.read_bytes() for p in (self.shared, self.local)}
        clean = runpy.run_path(str(HELPER))["clean"]
        replace = os.replace

        def fail_local(src, dst):
            if dst == self.local:
                raise OSError("simulated write failure")
            return replace(src, dst)

        with contextlib.redirect_stdout(io.StringIO()), patch("os.replace", side_effect=fail_local):
            with self.assertRaises(OSError):
                clean(self.target)
        for path, raw in before.items():
            self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(len(list(self.directory.glob(".settings-backup-*/*.bak-*"))), 2)
        self.assertEqual(list(self.directory.glob(".settings.json-*")), [])

    @unittest.skipUnless(shutil.which("jq") and shutil.which("rsync"), "requires jq and rsync")
    def test_cli_cancel_stops_before_skill_sync_and_rejects_incompatible_flags(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        self.write(self.shared, self.hooks("keep me"))
        before = self.tree()
        base = ["bash", str(ROOT / "cli/skill.sh"), "--claude", "--init", str(self.target), "--clean-settings"]
        env = dict(os.environ, REPO_SKILLS_HOME=str(ROOT), REPO_SKILLS_NO_RTK="1")
        result = subprocess.run(base, env=env, input="q\n", capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertFalse((self.directory / "skills").exists())
        for extra in (["--force"], ["--hermes"], ["--codex"]):
            result = subprocess.run(base + extra, env=env, input="", capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(self.tree(), before)


if __name__ == "__main__":
    unittest.main()
