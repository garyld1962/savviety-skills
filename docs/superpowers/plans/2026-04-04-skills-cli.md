# Skills CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI called `skills` with `init`, `add`, `update`, and `push` commands that manages AI coding skill files across three platforms (Claude Code, VS Code Copilot, Copilot Native CLI).

**Architecture:** Click CLI with subcommands. Each command reads/writes a `.skills.json` manifest in the project root. A copier module handles file sync with shared/local/protected classification. A diff module powers the `push` command's interactive pick list via `rich`.

**Tech Stack:** Python 3.12+, click, rich, uv (project/tool management)

**Spec:** `docs/superpowers/specs/2026-04-04-skills-cli-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Project metadata, dependencies, `skills` entry point |
| `src/skills_cli/__init__.py` | Package marker |
| `src/skills_cli/config.py` | Platform definitions (source dirs, dest dirs, local files, exclusions) |
| `src/skills_cli/manifest.py` | Read/write/validate `.skills.json` |
| `src/skills_cli/source.py` | Ensure source repo exists (local check or git clone), git pull |
| `src/skills_cli/copier.py` | Copy shared files, copy-once local files, protect `_project/`, git excludes |
| `src/skills_cli/diff.py` | Hash-compare project files vs source, categorize changed/new files |
| `src/skills_cli/cli.py` | Click group with `init`, `add`, `update`, `push` subcommands |
| `tests/test_config.py` | Platform definition tests |
| `tests/test_manifest.py` | Manifest read/write/validation tests |
| `tests/test_source.py` | Source resolution tests |
| `tests/test_copier.py` | File copy logic tests |
| `tests/test_diff.py` | Diff/hash comparison tests |
| `tests/test_cli.py` | CLI integration tests (click CliRunner) |
| `tests/conftest.py` | Shared fixtures (tmp dirs, fake source repos, fake projects) |

---

### Task 1: Project Scaffold

**Files:**
- Create: `skills-cli/pyproject.toml`
- Create: `skills-cli/src/skills_cli/__init__.py`
- Create: `skills-cli/src/skills_cli/cli.py`

- [ ] **Step 1: Create the project directory**

```bash
mkdir -p skills-cli/src/skills_cli skills-cli/tests
```

- [ ] **Step 2: Write pyproject.toml**

```toml
[project]
name = "skills-cli"
version = "0.1.0"
description = "Manage AI coding skills across Claude Code, VS Code Copilot, and Copilot CLI"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "rich>=13.0",
]

[project.scripts]
skills = "skills_cli.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/skills_cli"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write __init__.py**

```python
"""Skills CLI — manage AI coding skills across platforms."""
```

- [ ] **Step 4: Write minimal cli.py with click group**

```python
"""CLI entry point."""

import click


@click.group()
@click.version_option()
def main() -> None:
    """Manage AI coding skills across Claude Code, VS Code Copilot, and Copilot CLI."""


@main.command()
def init() -> None:
    """Initialize a project with skills."""
    click.echo("init: not yet implemented")


@main.command()
def add() -> None:
    """Add another platform's skills."""
    click.echo("add: not yet implemented")


@main.command()
def update() -> None:
    """Refresh installed skills from the source repo."""
    click.echo("update: not yet implemented")


@main.command()
def push() -> None:
    """Push skill edits back to the source repo."""
    click.echo("push: not yet implemented")
```

- [ ] **Step 5: Initialize uv project and verify**

```bash
cd skills-cli
uv sync
uv run skills --version
uv run skills --help
```

Expected: Version prints, help shows four subcommands (init, add, update, push).

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "feat: scaffold skills-cli with click subcommands"
```

---

### Task 2: Config — Platform Definitions

**Files:**
- Create: `skills-cli/src/skills_cli/config.py`
- Create: `skills-cli/tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for platform config definitions."""

from skills_cli.config import PLATFORMS, GITHUB_REPO, SOURCE_DIR


def test_three_platforms_defined():
    assert set(PLATFORMS.keys()) == {"claude", "vscode", "copilot"}


def test_claude_platform_paths():
    p = PLATFORMS["claude"]
    assert p.source_subdir == "claude"
    assert p.dest_subdir == ".claude/skills"
    assert "CLAUDE.local.md" in [lf.dest for lf in p.local_files]


def test_vscode_platform_paths():
    p = PLATFORMS["vscode"]
    assert p.source_subdir == "vscode"
    assert p.dest_subdir == ".github"


def test_copilot_platform_paths():
    p = PLATFORMS["copilot"]
    assert p.source_subdir == "copilot-native"
    assert p.dest_subdir == ".github"


def test_vscode_copilot_mutually_exclusive():
    assert PLATFORMS["vscode"].conflicts_with == ["copilot"]
    assert PLATFORMS["copilot"].conflicts_with == ["vscode"]


def test_claude_has_no_conflicts():
    assert PLATFORMS["claude"].conflicts_with == []


def test_source_dir():
    assert SOURCE_DIR.name == "skills"


def test_github_repo():
    assert GITHUB_REPO == "garyld1962/savviety-skills"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_config.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'skills_cli.config'` (module exists but has no content) or ImportError.

- [ ] **Step 3: Write config.py**

```python
"""Platform definitions and constants."""

from dataclasses import dataclass, field
from pathlib import Path


GITHUB_REPO = "garyld1962/savviety-skills"
SOURCE_DIR = Path.home() / "repos" / "skills"


@dataclass(frozen=True)
class LocalFile:
    """A file that is copied once and never overwritten."""

    source: str  # relative to platform source dir (or "templates/")
    dest: str  # relative to project root
    git_exclude: bool = True  # add to .git/info/exclude


@dataclass(frozen=True)
class Platform:
    """A platform's file layout and copy rules."""

    source_subdir: str  # dir name inside source repo
    dest_subdir: str  # dir name inside project root
    shared_dirs: list[str] = field(default_factory=list)  # subdirs to copy (empty = copy all)
    local_files: list[LocalFile] = field(default_factory=list)
    conflicts_with: list[str] = field(default_factory=list)


PLATFORMS: dict[str, Platform] = {
    "claude": Platform(
        source_subdir="claude",
        dest_subdir=".claude/skills",
        local_files=[
            LocalFile(
                source="templates/CLAUDE.local.md",
                dest="CLAUDE.local.md",
            ),
        ],
    ),
    "vscode": Platform(
        source_subdir="vscode",
        dest_subdir=".github",
        shared_dirs=["prompts", "skills", "agents", "instructions"],
        local_files=[
            LocalFile(
                source="vscode/copilot-instructions.md",
                dest=".github/copilot-instructions.md",
            ),
            LocalFile(
                source="vscode/instructions/personal.instructions.md",
                dest=".github/instructions/personal.instructions.md",
            ),
        ],
        conflicts_with=["copilot"],
    ),
    "copilot": Platform(
        source_subdir="copilot-native",
        dest_subdir=".github",
        shared_dirs=["prompts", "skills", "agents", "instructions"],
        local_files=[
            LocalFile(
                source="copilot-native/copilot-instructions.md",
                dest=".github/copilot-instructions.md",
            ),
            LocalFile(
                source="copilot-native/instructions/personal.instructions.md",
                dest=".github/instructions/personal.instructions.md",
                git_exclude=True,
            ),
        ],
        conflicts_with=["vscode"],
    ),
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_config.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/config.py tests/test_config.py
git commit -m "feat: platform config definitions for claude, vscode, copilot"
```

---

### Task 3: Manifest — Read/Write `.skills.json`

**Files:**
- Create: `skills-cli/src/skills_cli/manifest.py`
- Create: `skills-cli/tests/test_manifest.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for .skills.json manifest."""

import json
from pathlib import Path

import pytest

from skills_cli.manifest import (
    Manifest,
    read_manifest,
    write_manifest,
    ManifestNotFoundError,
    ManifestExistsError,
)


def test_write_manifest_creates_file(tmp_path: Path):
    write_manifest(tmp_path, platforms=["claude"])
    path = tmp_path / ".skills.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["version"] == 1
    assert data["platforms"] == ["claude"]
    assert "installed_at" in data
    assert "updated_at" in data
    assert data["source"] == "garyld1962/savviety-skills"


def test_read_manifest(tmp_path: Path):
    write_manifest(tmp_path, platforms=["claude", "copilot"])
    m = read_manifest(tmp_path)
    assert isinstance(m, Manifest)
    assert m.platforms == ["claude", "copilot"]
    assert m.version == 1


def test_read_manifest_not_found(tmp_path: Path):
    with pytest.raises(ManifestNotFoundError, match="skills init"):
        read_manifest(tmp_path)


def test_write_manifest_errors_if_exists(tmp_path: Path):
    write_manifest(tmp_path, platforms=["claude"])
    with pytest.raises(ManifestExistsError, match="skills add"):
        write_manifest(tmp_path, platforms=["vscode"])


def test_add_platform_to_manifest(tmp_path: Path):
    write_manifest(tmp_path, platforms=["claude"])
    m = read_manifest(tmp_path)
    m.platforms.append("copilot")
    m.save(tmp_path)
    reloaded = read_manifest(tmp_path)
    assert reloaded.platforms == ["claude", "copilot"]


def test_update_timestamp(tmp_path: Path):
    write_manifest(tmp_path, platforms=["claude"])
    m = read_manifest(tmp_path)
    old_updated = m.updated_at
    m.touch_updated()
    m.save(tmp_path)
    reloaded = read_manifest(tmp_path)
    assert reloaded.updated_at >= old_updated
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_manifest.py -v
```

Expected: FAIL — cannot import from `skills_cli.manifest`.

- [ ] **Step 3: Write manifest.py**

```python
"""Read/write .skills.json manifest."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from skills_cli.config import GITHUB_REPO

MANIFEST_FILE = ".skills.json"


class ManifestNotFoundError(FileNotFoundError):
    """Raised when .skills.json doesn't exist."""

    def __init__(self) -> None:
        super().__init__(
            f"{MANIFEST_FILE} not found. Run `skills init` first."
        )


class ManifestExistsError(FileExistsError):
    """Raised when .skills.json already exists on init."""

    def __init__(self) -> None:
        super().__init__(
            f"{MANIFEST_FILE} already exists. Use `skills add` or `skills update`."
        )


@dataclass
class Manifest:
    """In-memory representation of .skills.json."""

    version: int
    source: str
    platforms: list[str]
    installed_at: str
    updated_at: str

    def touch_updated(self) -> None:
        self.updated_at = _now_iso()

    def save(self, project_root: Path) -> None:
        path = project_root / MANIFEST_FILE
        data = {
            "version": self.version,
            "source": self.source,
            "platforms": self.platforms,
            "installed_at": self.installed_at,
            "updated_at": self.updated_at,
        }
        path.write_text(json.dumps(data, indent=2) + "\n")


def read_manifest(project_root: Path) -> Manifest:
    path = project_root / MANIFEST_FILE
    if not path.exists():
        raise ManifestNotFoundError()
    data = json.loads(path.read_text())
    return Manifest(**data)


def write_manifest(project_root: Path, *, platforms: list[str]) -> Manifest:
    path = project_root / MANIFEST_FILE
    if path.exists():
        raise ManifestExistsError()
    now = _now_iso()
    m = Manifest(
        version=1,
        source=GITHUB_REPO,
        platforms=platforms,
        installed_at=now,
        updated_at=now,
    )
    m.save(project_root)
    return m


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_manifest.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/manifest.py tests/test_manifest.py
git commit -m "feat: manifest read/write for .skills.json"
```

---

### Task 4: Source Resolution

**Files:**
- Create: `skills-cli/src/skills_cli/source.py`
- Create: `skills-cli/tests/test_source.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for source repo resolution."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from skills_cli.source import ensure_source, pull_source


def test_ensure_source_returns_existing_dir(tmp_path: Path):
    source = tmp_path / "skills"
    source.mkdir()
    (source / ".git").mkdir()  # fake git repo marker
    with patch("skills_cli.source.SOURCE_DIR", source):
        result = ensure_source()
    assert result == source


def test_ensure_source_clones_when_missing(tmp_path: Path):
    source = tmp_path / "skills"
    with (
        patch("skills_cli.source.SOURCE_DIR", source),
        patch("skills_cli.source.subprocess.run") as mock_run,
    ):
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        result = ensure_source()
    assert result == source
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "git" in args
    assert "clone" in args


def test_pull_source_runs_git_pull(tmp_path: Path):
    source = tmp_path / "skills"
    source.mkdir()
    with (
        patch("skills_cli.source.SOURCE_DIR", source),
        patch("skills_cli.source.subprocess.run") as mock_run,
    ):
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        pull_source(source)
    args = mock_run.call_args[0][0]
    assert args == ["git", "-C", str(source), "pull", "--ff-only"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_source.py -v
```

Expected: FAIL — cannot import from `skills_cli.source`.

- [ ] **Step 3: Write source.py**

```python
"""Ensure the source skills repo is available."""

import subprocess
from pathlib import Path

import click

from skills_cli.config import GITHUB_REPO, SOURCE_DIR


def ensure_source() -> Path:
    """Return path to source repo, cloning if needed."""
    if SOURCE_DIR.exists() and (SOURCE_DIR / ".git").exists():
        return SOURCE_DIR

    click.echo(f"Source repo not found at {SOURCE_DIR}")
    click.echo(f"Cloning {GITHUB_REPO}...")
    SOURCE_DIR.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", f"https://github.com/{GITHUB_REPO}.git", str(SOURCE_DIR)],
        check=True,
    )
    click.echo(f"Cloned to {SOURCE_DIR}")
    return SOURCE_DIR


def pull_source(source_dir: Path) -> None:
    """Pull latest from remote."""
    click.echo("Pulling latest from source repo...")
    subprocess.run(
        ["git", "-C", str(source_dir), "pull", "--ff-only"],
        check=True,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_source.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/source.py tests/test_source.py
git commit -m "feat: source resolution with auto-clone fallback"
```

---

### Task 5: Copier — File Copy Logic

**Files:**
- Create: `skills-cli/src/skills_cli/copier.py`
- Create: `skills-cli/tests/test_copier.py`
- Create: `skills-cli/tests/conftest.py`

- [ ] **Step 1: Write conftest.py with shared fixtures**

```python
"""Shared test fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def source_repo(tmp_path: Path) -> Path:
    """Create a fake source repo with skills for all three platforms."""
    repo = tmp_path / "source"

    # Claude skills
    claude = repo / "claude"
    (claude / "review-api").mkdir(parents=True)
    (claude / "review-api" / "SKILL.md").write_text("# Review API\n")
    (claude / "checkpoint").mkdir()
    (claude / "checkpoint" / "SKILL.md").write_text("# Checkpoint\n")

    # VS Code skills
    vscode = repo / "vscode"
    (vscode / "prompts" / "dev").mkdir(parents=True)
    (vscode / "prompts" / "dev" / "plan.prompt.md").write_text("# Plan\n")
    (vscode / "skills" / "api-patterns").mkdir(parents=True)
    (vscode / "skills" / "api-patterns" / "SKILL.md").write_text("# API Patterns\n")
    (vscode / "agents").mkdir()
    (vscode / "agents" / "security.agent.md").write_text("# Security\n")
    (vscode / "instructions").mkdir()
    (vscode / "instructions" / "code-generation.instructions.md").write_text("# Codegen\n")
    (vscode / "instructions" / "personal.instructions.md").write_text("# Personal\n")
    (vscode / "copilot-instructions.md").write_text("# Copilot Instructions\n")

    # Copilot Native skills
    copilot = repo / "copilot-native"
    (copilot / "prompts" / "dev").mkdir(parents=True)
    (copilot / "prompts" / "dev" / "plan.prompt.md").write_text("# Plan Native\n")
    (copilot / "skills" / "code-investigation-orchestrator").mkdir(parents=True)
    (copilot / "skills" / "code-investigation-orchestrator" / "SKILL.md").write_text("# Code Investigation\n")
    (copilot / "agents").mkdir()
    (copilot / "agents" / "adversarial-reviewer.agent.md").write_text("# Adversarial\n")
    (copilot / "instructions").mkdir()
    (copilot / "instructions" / "execution-environment.instructions.md").write_text("# Exec Env\n")
    (copilot / "instructions" / "personal.instructions.md").write_text("# Personal\n")
    (copilot / "copilot-instructions.md").write_text("# Copilot Native Instructions\n")

    # Templates
    (repo / "templates").mkdir()
    (repo / "templates" / "CLAUDE.local.md").write_text("# Local Overrides\n")

    return repo


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a fake project directory with a git repo."""
    project = tmp_path / "my-project"
    project.mkdir()
    git_dir = project / ".git" / "info"
    git_dir.mkdir(parents=True)
    (git_dir / "exclude").write_text("# git exclude\n")
    return project
```

- [ ] **Step 2: Write the failing tests**

```python
"""Tests for file copy logic."""

from pathlib import Path

from skills_cli.config import PLATFORMS
from skills_cli.copier import copy_platform, setup_git_excludes


def test_copy_claude_creates_skill_dirs(source_repo: Path, project_dir: Path):
    copy_platform("claude", source_repo, project_dir, dry_run=False)
    assert (project_dir / ".claude" / "skills" / "review-api" / "SKILL.md").exists()
    assert (project_dir / ".claude" / "skills" / "checkpoint" / "SKILL.md").exists()


def test_copy_claude_creates_local_file(source_repo: Path, project_dir: Path):
    copy_platform("claude", source_repo, project_dir, dry_run=False)
    assert (project_dir / "CLAUDE.local.md").exists()


def test_copy_claude_does_not_overwrite_local(source_repo: Path, project_dir: Path):
    (project_dir / "CLAUDE.local.md").write_text("my custom stuff\n")
    copy_platform("claude", source_repo, project_dir, dry_run=False)
    assert (project_dir / "CLAUDE.local.md").read_text() == "my custom stuff\n"


def test_copy_claude_force_local_overwrites(source_repo: Path, project_dir: Path):
    (project_dir / "CLAUDE.local.md").write_text("my custom stuff\n")
    copy_platform("claude", source_repo, project_dir, dry_run=False, force_local=True)
    assert (project_dir / "CLAUDE.local.md").read_text() == "# Local Overrides\n"


def test_copy_vscode_creates_shared_dirs(source_repo: Path, project_dir: Path):
    copy_platform("vscode", source_repo, project_dir, dry_run=False)
    assert (project_dir / ".github" / "prompts" / "dev" / "plan.prompt.md").exists()
    assert (project_dir / ".github" / "skills" / "api-patterns" / "SKILL.md").exists()
    assert (project_dir / ".github" / "agents" / "security.agent.md").exists()
    assert (project_dir / ".github" / "instructions" / "code-generation.instructions.md").exists()


def test_copy_vscode_local_files(source_repo: Path, project_dir: Path):
    copy_platform("vscode", source_repo, project_dir, dry_run=False)
    assert (project_dir / ".github" / "copilot-instructions.md").exists()
    assert (project_dir / ".github" / "instructions" / "personal.instructions.md").exists()


def test_copy_copilot_creates_shared_dirs(source_repo: Path, project_dir: Path):
    copy_platform("copilot", source_repo, project_dir, dry_run=False)
    assert (project_dir / ".github" / "prompts" / "dev" / "plan.prompt.md").exists()
    assert (project_dir / ".github" / "agents" / "adversarial-reviewer.agent.md").exists()


def test_copy_preserves_project_dir(source_repo: Path, project_dir: Path):
    project_skills = project_dir / ".claude" / "skills" / "review-api" / "_project"
    project_skills.mkdir(parents=True)
    (project_skills / "custom.md").write_text("project-specific\n")
    copy_platform("claude", source_repo, project_dir, dry_run=False)
    assert (project_skills / "custom.md").read_text() == "project-specific\n"


def test_copy_shared_overwrites_existing(source_repo: Path, project_dir: Path):
    skill_file = project_dir / ".claude" / "skills" / "review-api" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text("old content\n")
    copy_platform("claude", source_repo, project_dir, dry_run=False)
    assert skill_file.read_text() == "# Review API\n"


def test_dry_run_copies_nothing(source_repo: Path, project_dir: Path):
    copy_platform("claude", source_repo, project_dir, dry_run=True)
    assert not (project_dir / ".claude").exists()


def test_setup_git_excludes(project_dir: Path):
    platforms = PLATFORMS
    setup_git_excludes(project_dir, ["claude", "vscode"])
    content = (project_dir / ".git" / "info" / "exclude").read_text()
    assert "CLAUDE.local.md" in content
    assert "copilot-instructions.md" in content
    assert "personal.instructions.md" in content


def test_setup_git_excludes_idempotent(project_dir: Path):
    setup_git_excludes(project_dir, ["claude"])
    setup_git_excludes(project_dir, ["claude"])
    content = (project_dir / ".git" / "info" / "exclude").read_text()
    assert content.count("skills-cli") == 1
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_copier.py -v
```

Expected: FAIL — cannot import from `skills_cli.copier`.

- [ ] **Step 4: Write copier.py**

```python
"""File copy logic with shared/local/protected classification."""

import shutil
from pathlib import Path

import click

from skills_cli.config import PLATFORMS, LocalFile

EXCLUDE_MARKER = "# skills-cli local files"


def copy_platform(
    platform_id: str,
    source_repo: Path,
    project_root: Path,
    *,
    dry_run: bool,
    force_local: bool = False,
) -> None:
    """Copy a platform's files from source repo to project."""
    platform = PLATFORMS[platform_id]

    # Shared files
    _copy_shared(platform, source_repo, project_root, dry_run=dry_run)

    # Local files (copy-once)
    for lf in platform.local_files:
        _copy_local(lf, source_repo, project_root, dry_run=dry_run, force=force_local)


def _copy_shared(
    platform: "Platform",
    source_repo: Path,
    project_root: Path,
    *,
    dry_run: bool,
) -> None:
    """Copy shared files, preserving _project/ directories."""
    src_base = source_repo / platform.source_subdir
    dst_base = project_root / platform.dest_subdir

    if not src_base.exists():
        click.echo(f"  SKIP  source not found: {src_base}", err=True)
        return

    if platform.shared_dirs:
        # Copy only specified subdirectories
        for subdir in platform.shared_dirs:
            src_dir = src_base / subdir
            dst_dir = dst_base / subdir
            if src_dir.exists():
                _copy_tree(src_dir, dst_dir, dry_run=dry_run)
    else:
        # Copy everything at top level (claude/ has skill dirs directly)
        for item in sorted(src_base.iterdir()):
            if not item.is_dir():
                continue
            dst_dir = dst_base / item.name
            _copy_tree(item, dst_dir, dry_run=dry_run)


def _copy_tree(src: Path, dst: Path, *, dry_run: bool) -> None:
    """Recursively copy src to dst, skipping _project/ dirs at destination."""
    if dry_run:
        click.echo(f"  DRY   {src.name}/ -> {dst}")
        return

    dst.mkdir(parents=True, exist_ok=True)

    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)

        # Skip if any path component is _project
        if "_project" in rel.parts:
            continue

        dest_item = dst / rel
        if item.is_dir():
            dest_item.mkdir(parents=True, exist_ok=True)
        else:
            # Preserve _project/ dirs that already exist at destination
            dest_parent = dest_item.parent
            if dest_parent.exists() and (dest_parent / "_project").exists():
                pass  # _project/ is safe — just copy the file
            dest_item.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_item)

    click.echo(f"  OK    {src.name}/")


def _copy_local(
    lf: LocalFile,
    source_repo: Path,
    project_root: Path,
    *,
    dry_run: bool,
    force: bool,
) -> None:
    """Copy a local file (copy-once unless forced)."""
    src = source_repo / lf.source
    dst = project_root / lf.dest

    if not src.exists():
        click.echo(f"  SKIP  {lf.dest} — source not found")
        return

    if dst.exists() and not force:
        click.echo(f"  SKIP  {lf.dest} — already exists")
        return

    if dry_run:
        label = "OVERWRITE" if dst.exists() else "NEW"
        click.echo(f"  DRY   {lf.dest} ({label})")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    label = "refreshed" if force else "created"
    click.echo(f"  NEW   {lf.dest} ({label})")


def setup_git_excludes(project_root: Path, platform_ids: list[str]) -> None:
    """Append local file exclude rules to .git/info/exclude."""
    git_dir = project_root / ".git"
    if not git_dir.exists():
        click.echo("  SKIP  git excludes — not a git repository")
        return

    exclude_file = git_dir / "info" / "exclude"
    exclude_file.parent.mkdir(parents=True, exist_ok=True)

    existing = exclude_file.read_text() if exclude_file.exists() else ""
    if EXCLUDE_MARKER in existing:
        click.echo("  SKIP  git excludes — already configured")
        return

    # Collect all local files that need excluding
    exclude_paths: set[str] = set()
    for pid in platform_ids:
        for lf in PLATFORMS[pid].local_files:
            if lf.git_exclude:
                exclude_paths.add(lf.dest)

    # Always exclude _project dirs
    exclude_paths.add(".github/*/_project/")
    exclude_paths.add(".claude/skills/_project/")

    lines = [
        "",
        EXCLUDE_MARKER,
        *sorted(exclude_paths),
    ]

    with open(exclude_file, "a") as f:
        f.write("\n".join(lines) + "\n")

    click.echo("  OK    git excludes configured")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_copier.py -v
```

Expected: All 12 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/skills_cli/copier.py tests/test_copier.py tests/conftest.py
git commit -m "feat: copier with shared/local/protected file copy rules"
```

---

### Task 6: Diff — Compare Project vs Source

**Files:**
- Create: `skills-cli/src/skills_cli/diff.py`
- Create: `skills-cli/tests/test_diff.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for diff comparison between project and source."""

from pathlib import Path

from skills_cli.diff import diff_platform, DiffResult


def test_detect_changed_file(source_repo: Path, project_dir: Path):
    # Set up project with a modified file
    skill_dir = project_dir / ".claude" / "skills" / "review-api"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Modified Review API\n")

    # Also copy an unchanged file
    checkpoint_dir = project_dir / ".claude" / "skills" / "checkpoint"
    checkpoint_dir.mkdir(parents=True)
    (checkpoint_dir / "SKILL.md").write_text("# Checkpoint\n")  # same as source

    result = diff_platform("claude", source_repo, project_dir)
    assert "review-api/SKILL.md" in result.changed
    assert "review-api/SKILL.md" not in result.new
    assert "checkpoint/SKILL.md" not in result.changed


def test_detect_new_file(source_repo: Path, project_dir: Path):
    # File in project but not in source
    new_skill = project_dir / ".claude" / "skills" / "my-custom" / "SKILL.md"
    new_skill.parent.mkdir(parents=True)
    new_skill.write_text("# My Custom Skill\n")

    result = diff_platform("claude", source_repo, project_dir)
    assert "my-custom/SKILL.md" in result.new


def test_ignores_project_dirs(source_repo: Path, project_dir: Path):
    project_subdir = project_dir / ".claude" / "skills" / "review-api" / "_project"
    project_subdir.mkdir(parents=True)
    (project_subdir / "custom.md").write_text("custom\n")

    result = diff_platform("claude", source_repo, project_dir)
    assert not any("_project" in f for f in result.changed)
    assert not any("_project" in f for f in result.new)


def test_diff_vscode_shared_dirs(source_repo: Path, project_dir: Path):
    prompts = project_dir / ".github" / "prompts" / "dev"
    prompts.mkdir(parents=True)
    (prompts / "plan.prompt.md").write_text("# Modified Plan\n")

    result = diff_platform("vscode", source_repo, project_dir)
    assert "prompts/dev/plan.prompt.md" in result.changed


def test_diff_excludes_local_files(source_repo: Path, project_dir: Path):
    github = project_dir / ".github"
    github.mkdir(parents=True)
    (github / "copilot-instructions.md").write_text("modified\n")

    result = diff_platform("vscode", source_repo, project_dir)
    # copilot-instructions.md is a local file — should not appear in diff
    assert "copilot-instructions.md" not in result.changed
    assert "copilot-instructions.md" not in result.new


def test_empty_diff_when_unchanged(source_repo: Path, project_dir: Path):
    # Copy files identically
    skill_dir = project_dir / ".claude" / "skills" / "review-api"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Review API\n")  # identical to source

    result = diff_platform("claude", source_repo, project_dir)
    assert len(result.changed) == 0
    assert len(result.new) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_diff.py -v
```

Expected: FAIL — cannot import from `skills_cli.diff`.

- [ ] **Step 3: Write diff.py**

```python
"""Compare project files against source repo for push."""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from skills_cli.config import PLATFORMS


@dataclass
class DiffResult:
    """Files that differ between project and source."""

    changed: list[str] = field(default_factory=list)  # exist in both, content differs
    new: list[str] = field(default_factory=list)  # exist in project only


def diff_platform(
    platform_id: str,
    source_repo: Path,
    project_root: Path,
) -> DiffResult:
    """Compare project's platform files against source repo."""
    platform = PLATFORMS[platform_id]
    src_base = source_repo / platform.source_subdir
    dst_base = project_root / platform.dest_subdir

    # Collect local file destinations to exclude from diff
    local_dests: set[str] = set()
    for lf in platform.local_files:
        # Convert absolute dest to relative within dest_subdir
        if lf.dest.startswith(platform.dest_subdir + "/"):
            local_dests.add(lf.dest[len(platform.dest_subdir) + 1:])
        else:
            local_dests.add(lf.dest)

    result = DiffResult()

    if not dst_base.exists():
        return result

    if platform.shared_dirs:
        for subdir in platform.shared_dirs:
            _diff_tree(
                src_base / subdir,
                dst_base / subdir,
                prefix=subdir,
                local_dests=local_dests,
                result=result,
            )
    else:
        # Claude: each dir under dest is a skill
        for item in sorted(dst_base.iterdir()):
            if not item.is_dir():
                continue
            if item.name == "_project":
                continue
            _diff_tree(
                src_base / item.name,
                item,
                prefix=item.name,
                local_dests=local_dests,
                result=result,
            )

    return result


def _diff_tree(
    src_dir: Path,
    dst_dir: Path,
    *,
    prefix: str,
    local_dests: set[str],
    result: DiffResult,
) -> None:
    """Compare files in dst_dir against src_dir."""
    if not dst_dir.exists():
        return

    for dst_file in sorted(dst_dir.rglob("*")):
        if not dst_file.is_file():
            continue

        rel = dst_file.relative_to(dst_dir)

        # Skip _project dirs
        if "_project" in rel.parts:
            continue

        rel_with_prefix = f"{prefix}/{rel}"

        # Skip local files
        if rel_with_prefix in local_dests:
            continue

        src_file = src_dir / rel

        if src_file.exists():
            if _hash_file(src_file) != _hash_file(dst_file):
                result.changed.append(rel_with_prefix)
        else:
            result.new.append(rel_with_prefix)


def _hash_file(path: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_diff.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/diff.py tests/test_diff.py
git commit -m "feat: diff engine for push — hash compare project vs source"
```

---

### Task 7: CLI — Wire Up `init` and `add` Commands

**Files:**
- Modify: `skills-cli/src/skills_cli/cli.py`
- Create: `skills-cli/tests/test_cli.py`

- [ ] **Step 1: Write the failing tests for init**

```python
"""Tests for CLI commands."""

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from skills_cli.cli import main


def _make_source(tmp_path: Path) -> Path:
    """Minimal source repo for CLI tests."""
    repo = tmp_path / "source-repo"
    claude = repo / "claude" / "review-api"
    claude.mkdir(parents=True)
    (claude / "SKILL.md").write_text("# Review API\n")
    templates = repo / "templates"
    templates.mkdir()
    (templates / "CLAUDE.local.md").write_text("# Local\n")
    return repo


def _make_project(tmp_path: Path) -> Path:
    """Minimal project directory."""
    project = tmp_path / "project"
    project.mkdir()
    git_info = project / ".git" / "info"
    git_info.mkdir(parents=True)
    (git_info / "exclude").write_text("")
    return project


def test_init_claude(tmp_path: Path):
    source = _make_source(tmp_path)
    project = _make_project(tmp_path)

    runner = CliRunner()
    with patch("skills_cli.cli.ensure_source", return_value=source):
        result = runner.invoke(main, ["init", "--claude"], catch_exceptions=False, args=None)
        # CliRunner needs to be in the project dir
        # We'll use the --project flag or monkeypatch cwd

    # For testability, we'll add a hidden --project-dir option
    # Tested via integration approach below


def test_init_errors_if_already_initialized(tmp_path: Path):
    source = _make_source(tmp_path)
    project = _make_project(tmp_path)
    (project / ".skills.json").write_text('{"version":1}')

    runner = CliRunner()
    with (
        patch("skills_cli.cli.ensure_source", return_value=source),
        patch("skills_cli.cli._get_project_root", return_value=project),
    ):
        result = runner.invoke(main, ["init", "--claude"])
    assert result.exit_code != 0
    assert "already exists" in result.output or "already exists" in str(result.exception)


def test_add_errors_without_init(tmp_path: Path):
    project = _make_project(tmp_path)

    runner = CliRunner()
    with patch("skills_cli.cli._get_project_root", return_value=project):
        result = runner.invoke(main, ["add", "--claude"])
    assert result.exit_code != 0


def test_add_errors_on_vscode_copilot_conflict(tmp_path: Path):
    source = _make_source(tmp_path)
    project = _make_project(tmp_path)
    # Manifest says copilot is installed
    manifest = {"version": 1, "source": "x", "platforms": ["copilot"],
                "installed_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
    (project / ".skills.json").write_text(json.dumps(manifest))

    runner = CliRunner()
    with (
        patch("skills_cli.cli.ensure_source", return_value=source),
        patch("skills_cli.cli._get_project_root", return_value=project),
    ):
        result = runner.invoke(main, ["add", "--vscode"])
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output.lower() or "conflict" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL — stubs in cli.py don't implement the logic.

- [ ] **Step 3: Rewrite cli.py with init and add**

```python
"""CLI entry point."""

from pathlib import Path

import click

from skills_cli.config import PLATFORMS
from skills_cli.copier import copy_platform, setup_git_excludes
from skills_cli.manifest import (
    ManifestExistsError,
    ManifestNotFoundError,
    read_manifest,
    write_manifest,
)
from skills_cli.source import ensure_source

PLATFORM_FLAGS = ["claude", "vscode", "copilot"]


def _get_project_root() -> Path:
    return Path.cwd()


def _parse_platforms(claude: bool, vscode: bool, copilot: bool) -> list[str]:
    """Convert boolean flags to platform list."""
    selected = []
    if claude:
        selected.append("claude")
    if vscode:
        selected.append("vscode")
    if copilot:
        selected.append("copilot")
    return selected


def _check_conflicts(existing: list[str], adding: list[str]) -> None:
    """Raise if any platform conflicts with already-installed ones."""
    all_platforms = existing + adding
    for pid in adding:
        for conflict in PLATFORMS[pid].conflicts_with:
            if conflict in all_platforms:
                raise click.ClickException(
                    f"Cannot install '{pid}' — mutually exclusive with '{conflict}' "
                    f"(both target .github/). Remove one first."
                )


@click.group()
@click.version_option()
def main() -> None:
    """Manage AI coding skills across Claude Code, VS Code Copilot, and Copilot CLI."""


@main.command()
@click.option("--claude", is_flag=True, help="Install Claude Code skills")
@click.option("--vscode", is_flag=True, help="Install VS Code Copilot skills")
@click.option("--copilot", is_flag=True, help="Install Copilot CLI skills")
@click.option("--dry-run", is_flag=True, help="Preview without writing files")
def init(claude: bool, vscode: bool, copilot: bool, dry_run: bool) -> None:
    """Initialize a project with skills."""
    project_root = _get_project_root()

    # Error if already initialized
    if (project_root / ".skills.json").exists():
        raise click.ClickException(
            ".skills.json already exists. Use `skills add` or `skills update`."
        )

    # Interactive prompt if no flags
    platforms = _parse_platforms(claude, vscode, copilot)
    if not platforms:
        platforms = _prompt_platforms()

    # Check for conflicts within selection
    _check_conflicts([], platforms)

    # Ensure source repo
    source_repo = ensure_source()

    click.echo(f"\nInitializing skills: {', '.join(platforms)}")

    for pid in platforms:
        click.echo(f"\n--- {pid} ---")
        copy_platform(pid, source_repo, project_root, dry_run=dry_run)

    if not dry_run:
        setup_git_excludes(project_root, platforms)
        write_manifest(project_root, platforms=platforms)
        click.echo("\n.skills.json created.")

    click.echo("\nDone.")


@main.command()
@click.option("--claude", is_flag=True, help="Add Claude Code skills")
@click.option("--vscode", is_flag=True, help="Add VS Code Copilot skills")
@click.option("--copilot", is_flag=True, help="Add Copilot CLI skills")
@click.option("--dry-run", is_flag=True, help="Preview without writing files")
def add(claude: bool, vscode: bool, copilot: bool, dry_run: bool) -> None:
    """Add another platform's skills to this project."""
    project_root = _get_project_root()

    manifest = read_manifest(project_root)

    platforms = _parse_platforms(claude, vscode, copilot)
    if not platforms:
        raise click.ClickException("Specify a platform: --claude, --vscode, or --copilot")

    # Check for duplicates
    for pid in platforms:
        if pid in manifest.platforms:
            raise click.ClickException(f"'{pid}' is already installed.")

    # Check for conflicts
    _check_conflicts(manifest.platforms, platforms)

    source_repo = ensure_source()

    for pid in platforms:
        click.echo(f"\n--- {pid} ---")
        copy_platform(pid, source_repo, project_root, dry_run=dry_run)

    if not dry_run:
        manifest.platforms.extend(platforms)
        setup_git_excludes(project_root, manifest.platforms)
        manifest.touch_updated()
        manifest.save(project_root)
        click.echo(f"\nAdded: {', '.join(platforms)}")


@main.command()
@click.option("--dry-run", is_flag=True, help="Preview without writing files")
def update(dry_run: bool) -> None:
    """Refresh installed skills from the source repo."""
    click.echo("update: not yet implemented")


@main.command()
def push() -> None:
    """Push skill edits back to the source repo."""
    click.echo("push: not yet implemented")


def _prompt_platforms() -> list[str]:
    """Interactive platform picker."""
    click.echo("Select platforms to install:\n")
    choices = [
        ("1", "claude", "Claude Code (.claude/skills/)"),
        ("2", "vscode", "VS Code Copilot (.github/)"),
        ("3", "copilot", "Copilot CLI (.github/)"),
        ("4", "all", "All (claude + pick one of vscode/copilot)"),
    ]
    for key, _, label in choices:
        click.echo(f"  {key}) {label}")

    choice = click.prompt("\nChoice", type=click.Choice(["1", "2", "3", "4"]))

    if choice == "1":
        return ["claude"]
    elif choice == "2":
        return ["vscode"]
    elif choice == "3":
        return ["copilot"]
    else:
        # "all" — claude + pick one github platform
        click.echo("\nClaude selected. Pick the GitHub platform:")
        click.echo("  a) VS Code Copilot")
        click.echo("  b) Copilot CLI")
        gh_choice = click.prompt("Choice", type=click.Choice(["a", "b"]))
        return ["claude", "vscode" if gh_choice == "a" else "copilot"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/cli.py tests/test_cli.py
git commit -m "feat: wire up init and add commands with conflict checking"
```

---

### Task 8: CLI — Wire Up `update` Command

**Files:**
- Modify: `skills-cli/src/skills_cli/cli.py`
- Modify: `skills-cli/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_cli.py`:

```python
def test_update_refreshes_installed_platforms(tmp_path: Path):
    source = _make_source(tmp_path)
    project = _make_project(tmp_path)

    # Pre-existing manifest
    manifest = {"version": 1, "source": "x", "platforms": ["claude"],
                "installed_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
    (project / ".skills.json").write_text(json.dumps(manifest))

    runner = CliRunner()
    with (
        patch("skills_cli.cli.ensure_source", return_value=source),
        patch("skills_cli.cli._get_project_root", return_value=project),
        patch("skills_cli.source.pull_source") as mock_pull,
    ):
        result = runner.invoke(main, ["update"], catch_exceptions=False)

    assert result.exit_code == 0
    assert (project / ".claude" / "skills" / "review-api" / "SKILL.md").exists()

    # updated_at should have changed
    updated = json.loads((project / ".skills.json").read_text())
    assert updated["updated_at"] != "2026-01-01T00:00:00Z"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py::test_update_refreshes_installed_platforms -v
```

Expected: FAIL — update prints "not yet implemented".

- [ ] **Step 3: Implement update command in cli.py**

Replace the `update` stub:

```python
@main.command()
@click.option("--dry-run", is_flag=True, help="Preview without writing files")
def update(dry_run: bool) -> None:
    """Refresh installed skills from the source repo."""
    project_root = _get_project_root()
    manifest = read_manifest(project_root)

    source_repo = ensure_source()

    from skills_cli.source import pull_source
    pull_source(source_repo)

    click.echo(f"\nUpdating: {', '.join(manifest.platforms)}")

    for pid in manifest.platforms:
        click.echo(f"\n--- {pid} ---")
        copy_platform(pid, source_repo, project_root, dry_run=dry_run)

    if not dry_run:
        manifest.touch_updated()
        manifest.save(project_root)

    click.echo("\nDone.")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_cli.py::test_update_refreshes_installed_platforms -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/cli.py tests/test_cli.py
git commit -m "feat: update command — pull and refresh installed platforms"
```

---

### Task 9: CLI — Wire Up `push` Command

**Files:**
- Modify: `skills-cli/src/skills_cli/cli.py`
- Modify: `skills-cli/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_cli.py`:

```python
def test_push_shows_changed_files(tmp_path: Path):
    source = _make_source(tmp_path)
    project = _make_project(tmp_path)

    # Install claude skill, then modify it
    skill_dir = project / ".claude" / "skills" / "review-api"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Modified\n")

    manifest = {"version": 1, "source": "x", "platforms": ["claude"],
                "installed_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
    (project / ".skills.json").write_text(json.dumps(manifest))

    runner = CliRunner()
    with (
        patch("skills_cli.cli.ensure_source", return_value=source),
        patch("skills_cli.cli._get_project_root", return_value=project),
    ):
        # Simulate selecting nothing (user presses enter with no selection)
        result = runner.invoke(main, ["push", "--dry-run"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "review-api/SKILL.md" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py::test_push_shows_changed_files -v
```

Expected: FAIL — push prints "not yet implemented".

- [ ] **Step 3: Implement push command in cli.py**

Replace the `push` stub:

```python
@main.command()
@click.option("--dry-run", is_flag=True, help="List changes without copying")
def push(dry_run: bool) -> None:
    """Push skill edits back to the source repo."""
    project_root = _get_project_root()
    manifest = read_manifest(project_root)
    source_repo = ensure_source()

    from skills_cli.diff import diff_platform, DiffResult

    # Collect diffs across all installed platforms
    all_diffs: dict[str, DiffResult] = {}
    for pid in manifest.platforms:
        result = diff_platform(pid, source_repo, project_root)
        if result.changed or result.new:
            all_diffs[pid] = result

    if not all_diffs:
        click.echo("No changes to push.")
        return

    # Display changes
    for pid, result in all_diffs.items():
        if result.changed:
            click.echo(f"\nChanged files ({pid}):")
            for f in result.changed:
                click.echo(f"  {f}")
        if result.new:
            click.echo(f"\nNew files ({pid}):")
            for f in result.new:
                click.echo(f"  {f}")

    if dry_run:
        click.echo("\n--dry-run: no files copied.")
        return

    # Interactive pick list
    selected = _pick_files(all_diffs)
    if not selected:
        click.echo("Nothing selected.")
        return

    # Copy selected files back to source
    for pid, rel_path in selected:
        platform = PLATFORMS[pid]
        src = project_root / platform.dest_subdir
        dst = source_repo / platform.source_subdir

        if platform.shared_dirs:
            # rel_path is like "prompts/dev/plan.prompt.md"
            src_file = src / rel_path
            dst_file = dst / rel_path
        else:
            # Claude: rel_path is like "review-api/SKILL.md"
            src_file = src / rel_path
            dst_file = dst / rel_path

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(src_file, dst_file)
        click.echo(f"  OK    {pid}/{rel_path}")

    click.echo(f"\nChanges copied to {source_repo}")
    click.echo("Commit and push when ready.")


def _pick_files(
    all_diffs: dict[str, "DiffResult"],
) -> list[tuple[str, str]]:
    """Interactive checkbox picker for files to push."""
    try:
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()

        # Build flat list of (platform, path, label)
        items: list[tuple[str, str, str]] = []
        for pid, result in all_diffs.items():
            for f in result.changed:
                items.append((pid, f, f"[changed] {pid}/{f}"))
            for f in result.new:
                items.append((pid, f, f"[new]     {pid}/{f}"))

        # Show numbered list
        console.print("\nSelect files to push (comma-separated numbers, or 'all'):\n")
        for i, (_, _, label) in enumerate(items, 1):
            console.print(f"  {i}) {label}")

        choice = Prompt.ask("\nSelection", default="all")

        if choice.strip().lower() == "all":
            return [(pid, path) for pid, path, _ in items]

        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
        return [(items[i][0], items[i][1]) for i in indices if 0 <= i < len(items)]

    except ImportError:
        # Fallback without rich
        return [(pid, f) for pid, result in all_diffs.items()
                for f in result.changed + result.new]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: All CLI tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skills_cli/cli.py tests/test_cli.py
git commit -m "feat: push command with diff display and file picker"
```

---

### Task 10: Full Integration Test and Install

**Files:**
- Modify: `skills-cli/tests/test_cli.py`

- [ ] **Step 1: Write end-to-end integration test**

Add to `tests/test_cli.py`:

```python
def test_full_lifecycle(tmp_path: Path):
    """init → modify → push → update — full round trip."""
    source = _make_source(tmp_path)
    project = _make_project(tmp_path)

    runner = CliRunner()
    patches = {
        "skills_cli.cli.ensure_source": source,
        "skills_cli.cli._get_project_root": project,
    }

    def run(args):
        with (
            patch("skills_cli.cli.ensure_source", return_value=source),
            patch("skills_cli.cli._get_project_root", return_value=project),
            patch("skills_cli.source.pull_source"),
        ):
            return runner.invoke(main, args, catch_exceptions=False)

    # 1. Init
    result = run(["init", "--claude"])
    assert result.exit_code == 0
    assert (project / ".skills.json").exists()
    assert (project / ".claude" / "skills" / "review-api" / "SKILL.md").exists()

    # 2. Update
    result = run(["update"])
    assert result.exit_code == 0

    # 3. Modify a file
    (project / ".claude" / "skills" / "review-api" / "SKILL.md").write_text("# Edited\n")

    # 4. Push --dry-run
    result = run(["push", "--dry-run"])
    assert result.exit_code == 0
    assert "review-api/SKILL.md" in result.output
```

- [ ] **Step 2: Run all tests**

```bash
uv run pytest -v
```

Expected: All tests PASS.

- [ ] **Step 3: Install globally with uv**

```bash
cd skills-cli
uv tool install --force .
```

- [ ] **Step 4: Verify CLI is on PATH**

```bash
skills --help
skills --version
```

Expected: Help shows four subcommands, version shows 0.1.0.

- [ ] **Step 5: Smoke test on a real project**

```bash
cd /tmp
mkdir test-project && cd test-project
git init
skills init --claude --dry-run
```

Expected: Shows DRY output listing Claude skills that would be copied.

- [ ] **Step 6: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: full lifecycle integration test"
```

---

## Post-Implementation

- [ ] Remove old `deploy-skills` from `~/.local/bin/deploy-skills` after confirming `skills` works
- [ ] Update `CLAUDE.local.md` template comment to reference `skills` instead of `deploy-skills`
- [ ] Update memory files in `~/repos/skills` to reference the new CLI
