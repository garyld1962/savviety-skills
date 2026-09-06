"""Verify uv bootstrapping without network access or host package installation."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


class AgenticToolsInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.user_dir = self.base / "user with spaces"
        self.user_dir.mkdir()
        self.install_dir = self.user_dir / ".local/bin"
        self.log = self.base / "calls"
        # Only expose fixture tools and the small set of shell dependencies.
        for command in ("sh", "awk", "mktemp", "rm", "mkdir", "cp", "chmod"):
            (self.bin / command).symlink_to(shutil.which(command))
        for command in ("rg", "fd", "jq", "rsync", "shellcheck", "ast-grep", "sd", "gh", "gh-axi", "just", "hyperfine", "xh"):
            self.script(self.bin / command, "exit 0\n")
        self.uv = self.base / "uv-fixture"
        self.script(self.uv, '''case "$*" in
  --version) echo 'uv fixture' ;;
  'tool dir --bin') printf '%s\\n' "$TEST_UV_DIR" ;;
  'python find') echo /fixture/python ;;
  *) exit 1 ;;
esac
''')
        self.installer = self.base / "installer"
        self.script(self.installer, '''echo install >> "$TEST_LOG"
[ "${TEST_INSTALL_FAIL:-}" != 1 ] || exit 1
mkdir -p "$UV_INSTALL_DIR"
cp "$TEST_UV" "$UV_INSTALL_DIR/uv"
chmod +x "$UV_INSTALL_DIR/uv"
''')
        self.script(self.bin / "curl", '''echo download >> "$TEST_LOG"
cp "$TEST_INSTALLER" "$4"
[ "${TEST_DOWNLOAD_FAIL:-}" != 1 ]
''')
        self.env = dict(HOME=str(self.user_dir), PATH=str(self.bin),
                        TEST_UV_DIR=str(self.install_dir), TEST_UV=str(self.uv),
                        TEST_INSTALLER=str(self.installer), TEST_LOG=str(self.log))

    def script(self, path, body):
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def run_installer(self, *args):
        return subprocess.run([BASH, str(ROOT / "bin/install-agentic-tools"), *args],
                              cwd=self.base, env=self.env, capture_output=True,
                              text=True, timeout=20)

    def test_missing_uv_installs_and_continues_in_same_process(self):
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All tools present", result.stdout)
        self.assertTrue((self.install_dir / "uv").is_file())
        self.assertEqual(self.log.read_text().splitlines(), ["download", "install"])
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), ["download", "install"])

    def test_check_does_not_download_or_install(self):
        result = self.run_installer("--check")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(self.log.exists())
        self.assertFalse(self.install_dir.exists())

    def test_uv_on_path_is_reused(self):
        (self.bin / "uv").symlink_to(self.uv)
        self.env["TEST_UV_DIR"] = str(self.bin)
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.log.exists())

    def test_failed_download_never_executes_partial_installer(self):
        self.env["TEST_DOWNLOAD_FAIL"] = "1"
        result = self.run_installer()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), ["download"])
        self.assertFalse(self.install_dir.exists())
        self.assertNotIn("== tools", result.stdout)

    def test_failed_install_stops_before_tool_installation(self):
        self.env["TEST_INSTALL_FAIL"] = "1"
        result = self.run_installer()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("== tools", result.stdout)

    def test_wget_fallback_and_custom_install_directory(self):
        (self.bin / "curl").unlink()
        self.script(self.bin / "wget", '''echo download >> "$TEST_LOG"
cp "$TEST_INSTALLER" "$4"
''')
        self.install_dir = self.base / "custom uv"
        self.env.update(UV_INSTALL_DIR=str(self.install_dir), TEST_UV_DIR=str(self.install_dir))
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.install_dir / "uv").is_file())

    def test_missing_python_and_tool_path_are_configured_only_in_install_mode(self):
        (self.bin / "uv").symlink_to(self.uv)
        self.script(self.uv, '''case "$*" in
  --version) echo 'uv fixture' ;;
  'tool dir --bin') printf '%s\\n' "$TEST_UV_DIR" ;;
  'tool update-shell') echo path >> "$TEST_LOG" ;;
  'python find') [ -f "$TEST_LOG.python" ] && echo /fixture/python ;;
  'python install') echo python >> "$TEST_LOG"; echo ready > "$TEST_LOG.python" ;;
  *) exit 1 ;;
esac
''')
        result = self.run_installer("--check")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(self.log.exists())
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), ["path", "python"])

    def prepare_missing_tool(self, name):
        (self.bin / "uv").symlink_to(self.uv)
        self.env["TEST_UV_DIR"] = str(self.bin)
        (self.bin / name).unlink()

    def test_gh_axi_installs_under_user_prefix_without_hooks(self):
        self.prepare_missing_tool("gh-axi")
        self.script(self.bin / "node", 'exit 0\n')
        self.script(self.bin / "npm", '''printf '%s\\n' "$@" >> "$TEST_LOG"
[ "$1" = install ] && [ "$2" = --global ] && [ "$3" = --prefix ] || exit 1
mkdir -p "$4/bin"
printf '#!/bin/sh\\necho unexpected-hook >> "$TEST_LOG"\\n' > "$4/bin/gh-axi"
chmod +x "$4/bin/gh-axi"
''')
        result = self.run_installer("--check")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(self.log.exists())
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.log.read_text().splitlines(),
                         ["install", "--global", "--prefix", str(self.user_dir / ".local"), "gh-axi"])

    def test_gh_axi_reports_missing_or_old_node_without_installing(self):
        self.prepare_missing_tool("gh-axi")
        self.script(self.bin / "npm", 'echo unexpected-install >> "$TEST_LOG"\n')
        for old_node in (False, True):
            with self.subTest(old_node=old_node):
                if old_node:
                    self.script(self.bin / "node", 'exit 1\n')
                result = self.run_installer()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("requires Node.js 20+ and npm", result.stdout)
                self.assertFalse(self.log.exists())

    def test_shellcheck_installs_through_system_package_manager(self):
        self.prepare_missing_tool("shellcheck")
        self.script(self.bin / "brew", '''printf '%s\\n' "$*" >> "$TEST_LOG"
[ "$1" = install ] && [ "$2" = shellcheck ] || exit 1
printf '#!/bin/sh\\nexit 0\\n' > "$TEST_UV_DIR/shellcheck"
chmod +x "$TEST_UV_DIR/shellcheck"
''')
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), ["install shellcheck"])


if __name__ == "__main__":
    unittest.main()
