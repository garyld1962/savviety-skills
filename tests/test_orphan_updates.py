"""Exercise default orphan prompts through a terminal and unattended updates."""
import json
import os
from pathlib import Path
import pty
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("jq") and shutil.which("rsync"), "requires jq and rsync")
class OrphanUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "source"
        (self.source / "claude").mkdir(parents=True)
        (self.source / "claude/README.md").write_text("Fixture")
        self.manifest = {"user_owned": []}
        for platform in ("claude", "kimi"):
            skill = self.source / platform / "skills/current"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("Updated shared skill")
            self.manifest[platform] = {"skills": {"from": f"{platform}/skills", "to": f".{platform}/skills",
                                                   "skip": [], "preserve_subdirs": ["_local", "_project"]},
                                       "trees": [], "extras": [], "starters": []}
        (self.source / "manifest.json").write_text(json.dumps(self.manifest))
        self.env = dict(os.environ, REPO_SKILLS_HOME=str(self.source), REPO_SKILLS_NO_RTK="1")

    def fixture(self, platform):
        repo = Path(tempfile.mkdtemp(dir=self.base, prefix="target "))
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        skills = repo / f".{platform}/skills"
        for name in ("current", "alpha-old", "beta-old", "_project", "_local", "_private", ".hidden"):
            (skills / name).mkdir(parents=True)
            (skills / name / "SKILL.md").write_text("Keep my content")
        return repo, skills

    def update(self, platform, repo, *flags, answers="", terminal=False):
        command = ["bash", str(ROOT / "cli/skill.sh"), f"--{platform}", "--update", str(repo), *flags]
        if not terminal:
            return subprocess.run(command, env=self.env, input=answers, capture_output=True,
                                  text=True, timeout=20)
        master, slave = pty.openpty()
        try:
            with subprocess.Popen(command, env=self.env, stdin=slave, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True) as proc:
                try:
                    if answers:
                        os.write(master, answers.encode())
                    output, _ = proc.communicate(timeout=20)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.communicate()
                    raise
                return subprocess.CompletedProcess(command, proc.returncode, output, "")
        finally:
            os.close(master)
            os.close(slave)

    def assert_protected(self, skills):
        for name in ("_project", "_local", "_private", ".hidden"):
            self.assertEqual((skills / name / "SKILL.md").read_text(), "Keep my content")

    def test_default_update_asks_and_respects_keep_and_remove_for_each_skill(self):
        for platform in ("claude", "kimi"):
            with self.subTest(platform=platform):
                repo, skills = self.fixture(platform)
                result = self.update(platform, repo, terminal=True, answers="\ny\n")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Remove orphaned skill 'alpha-old'?", result.stdout)
                self.assertTrue((skills / "alpha-old/SKILL.md").exists())
                self.assertFalse((skills / "beta-old").exists())
                self.assertEqual((skills / "current/SKILL.md").read_text(), "Updated shared skill")
                self.assert_protected(skills)

    def test_all_and_quit_choices(self):
        for answers, remaining in (("a\n", set()), ("q\n", {"alpha-old", "beta-old"}),
                                    ("n\nq\n", {"alpha-old", "beta-old"}), ("invalid\nn\nn\n", {"alpha-old", "beta-old"})):
            with self.subTest(answers=answers):
                repo, skills = self.fixture("claude")
                result = self.update("claude", repo, terminal=True, answers=answers)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual({name for name in ("alpha-old", "beta-old") if (skills / name).exists()}, remaining)
                self.assert_protected(skills)

    def test_unattended_update_preserves_orphans_even_with_piped_yes(self):
        for flags in ((), ("--prune",)):
            repo, skills = self.fixture("claude")
            result = self.update("claude", repo, *flags, answers="y\ny\n")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("No interactive input", result.stdout)
            self.assertTrue((skills / "alpha-old").exists())
            self.assertTrue((skills / "beta-old").exists())
            self.assert_protected(skills)

    def test_explicit_prune_yes_remains_available_for_scripts(self):
        for platform in ("claude", "kimi"):
            repo, skills = self.fixture(platform)
            result = self.update(platform, repo, "--prune", "--yes")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((skills / "alpha-old").exists())
            self.assertFalse((skills / "beta-old").exists())
            self.assert_protected(skills)

    def test_dry_run_never_prompts_or_deletes_even_with_prune_yes(self):
        for flags in (("--dry-run",), ("--dry-run", "--prune", "--yes")):
            repo, skills = self.fixture("claude")
            result = self.update("claude", repo, *flags, terminal=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[dry-run] would", result.stdout)
            self.assertNotIn("Remove orphaned skill '", result.stdout)
            self.assertTrue((skills / "alpha-old").exists())
            self.assertTrue((skills / "beta-old").exists())
            self.assertEqual((skills / "current/SKILL.md").read_text(), "Keep my content")
            self.assert_protected(skills)


if __name__ == "__main__":
    unittest.main()
