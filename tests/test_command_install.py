"""Exercise command installation with isolated homes and a movable checkout."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
ZSH = shutil.which("zsh")


class CommandInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.user_dir = self.base / "user with spaces"
        self.user_dir.mkdir()
        self.source = self.base / "checkout with spaces"
        (self.source / "cli").mkdir(parents=True)
        for name in ("install.sh", "cli/skill.sh"):
            shutil.copy2(ROOT / name, self.source / name)
        (self.source / "claude").mkdir()
        (self.source / "claude/README.md").write_text("Source fixture\n")
        (self.source / "codex/agents").mkdir(parents=True)
        (self.source / "codex/agents/example.toml").write_text('name = "example"\n')
        (self.source / "manifest.json").write_text(json.dumps({
            "codex": {"trees": [{"from": "codex/agents", "to": ".codex/agents"}]},
            "user_owned": [],
        }))
        self.link = self.user_dir / ".local/bin/skills"
        self.env = dict(os.environ, HOME=str(self.user_dir), SHELL=BASH,
                        PATH=os.defpath, REPO_SKILLS_NO_RTK="1")
        for key in ("REPO_SKILLS_HOME", "ZDOTDIR", "BASH_ENV", "ENV"):
            self.env.pop(key, None)

    def run_command(self, *args, env=None):
        return subprocess.run(args, cwd=self.base, env=env or self.env,
                              capture_output=True, text=True, timeout=20)

    def install(self):
        result = self.run_command(str(self.source / "install.sh"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.link.resolve(), self.source / "cli/skill.sh")
        return result

    def test_bash_install_is_repeatable_and_available_in_new_shell(self):
        profile = self.user_dir / ".profile"
        rc = self.user_dir / ".bashrc"
        original = 'export KEEP_ME="user configuration"'  # no trailing newline
        profile.write_text(original)
        rc.write_text(original)
        self.install()
        first = (profile.read_bytes(), rc.read_bytes())
        self.install()
        self.assertEqual(first, (profile.read_bytes(), rc.read_bytes()))
        self.assertTrue(profile.read_text().startswith(original + "\n"))
        result = self.run_command(BASH, "--noprofile", "--rcfile", str(rc), "-ic",
                                  'command -v skills; skills --version; printf "%s\\n" "$KEEP_ME"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [str(self.link), "skills 0.1.0", "user configuration"])
        # Re-sourcing a login profile must not add duplicate PATH entries.
        result = self.run_command(BASH, "--noprofile", "--norc", "-c",
                                  '. "$1"; . "$1"; printf "%s" "$PATH"', "bash", str(profile))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split(":").count(str(self.link.parent)), 1)
        help_result = self.run_command(str(self.link), "--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("skills --claude", help_result.stdout)
        self.assertNotIn("skill.sh", help_result.stdout)

    def test_bash_updates_the_active_login_profile(self):
        for name in (".bash_login", ".bash_profile"):
            with self.subTest(name=name):
                active = self.user_dir / name
                active.write_text("# User login configuration\n")
                self.install()
                result = self.run_command(BASH, "--noprofile", "--norc", "-c",
                                          '. "$1"; command -v skills', "bash", str(active))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), str(self.link))
                self.assertFalse((self.user_dir / ".profile").exists())

    @unittest.skipUnless(ZSH, "Zsh is not installed")
    def test_zsh_startup_uses_home_or_zdotdir(self):
        self.env["SHELL"] = ZSH
        for config_dir in (self.user_dir, self.user_dir / "zsh config"):
            with self.subTest(config_dir=config_dir):
                if config_dir != self.user_dir:
                    self.env["ZDOTDIR"] = str(config_dir)
                self.install()
                before = [(config_dir / name).read_bytes() for name in (".zprofile", ".zshrc")]
                self.install()
                self.assertEqual(before, [(config_dir / name).read_bytes() for name in (".zprofile", ".zshrc")])
                for mode in ("-ic", "-lc"):
                    result = self.run_command(ZSH, mode, "command -v skills; skills --version")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.splitlines(), [str(self.link), "skills 0.1.0"])

    @unittest.skipUnless(shutil.which("jq") and shutil.which("rsync"), "jq and rsync are required")
    def test_link_uses_its_checkout_after_move_and_accepts_source_override(self):
        self.install()
        moved = self.base / "moved checkout"
        self.source.rename(moved)
        self.source = moved
        self.install()  # Repair the now-dangling symlink.
        # Resolve a chain containing a relative symlink, from another directory.
        alias = self.link.parent / "skills-alias"
        alias.symlink_to("skills")
        target = self.base / "target repo"
        target.mkdir()
        subprocess.run(["git", "init", "-q", str(target)], check=True)
        result = self.run_command(str(alias), "--codex", "--init", str(target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed = target / ".codex/agents/example.toml"
        self.assertEqual(installed.read_text(), 'name = "example"\n')
        override = self.base / "override source"
        shutil.copytree(self.source, override)
        (override / "codex/agents/example.toml").write_text('name = "override"\n')
        result = self.run_command(str(self.link), "--codex", "--update", str(target),
                                  env=dict(self.env, REPO_SKILLS_HOME=str(override)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(installed.read_text(), 'name = "override"\n')

    def test_existing_files_and_directories_are_preserved(self):
        self.link.parent.mkdir(parents=True)
        for kind in ("file", "directory"):
            with self.subTest(kind=kind):
                if kind == "file":
                    self.link.write_text("existing command\n")
                else:
                    self.link.mkdir()
                    (self.link / "keep.txt").write_text("existing directory\n")
                result = self.run_command(str(self.source / "install.sh"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Refusing to replace", result.stderr)
                self.assertFalse(self.link.is_symlink())
                self.assertFalse((self.user_dir / ".profile").exists())
                self.assertFalse((self.user_dir / ".bashrc").exists())
                if kind == "file":
                    self.assertEqual(self.link.read_text(), "existing command\n")
                    self.link.unlink()
                else:
                    self.assertEqual((self.link / "keep.txt").read_text(), "existing directory\n")


if __name__ == "__main__":
    unittest.main()
