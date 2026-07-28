# Skill Factory Publish Toolchain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the publish pipeline: Merkle tree computation, MANIFEST.json generation, copy to published repo, verification CLI, and SQLite recording.

**Architecture:** Three modules under `publish/`: `merkle.py` (SHA-256 hash tree), `publish.py` (orchestrator + CLI), `verify.py` (verification CLI). The publish step reads compiled output from `working/`, copies to the published repo, computes the Merkle tree, writes MANIFEST.json, and records in SQLite.

**Tech Stack:** Python 3.12+, hashlib (stdlib), shutil (stdlib), pytest, uv

**Spec:** `~/repos/skills/docs/superpowers/specs/2026-03-25-skill-factory-design.md` (section: Publish Pipeline and Merkle Tree)

**Depends on:** Plans 1-3 (scaffolding + state DB + compiler)

---

## File Structure

```
~/repos/skill-factory/
├── publish/
│   ├── __init__.py        # (exists)
│   ├── merkle.py          # SHA-256 Merkle tree computation
│   ├── publish.py         # Publish orchestrator + CLI
│   └── verify.py          # Verification CLI
└── tests/
    ├── test_merkle.py     # Tests for Merkle tree
    ├── test_publish.py    # Tests for publish orchestrator
    └── test_verify.py     # Tests for verification
```

---

### Task 1: Implement and test merkle.py

**Files:**
- Create: `publish/merkle.py`
- Create: `tests/test_merkle.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_merkle.py`:

```python
"""Tests for publish.merkle — SHA-256 Merkle tree."""

import hashlib
from pathlib import Path

import pytest

from publish.merkle import hash_file, hash_directory, build_release_tree


class TestHashFile:
    def test_hashes_file_content(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert hash_file(f) == expected

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello")
        f2.write_text("world")
        assert hash_file(f1) != hash_file(f2)

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("same")
        f2.write_text("same")
        assert hash_file(f1) == hash_file(f2)


class TestHashDirectory:
    def test_single_file_directory(self, tmp_path):
        (tmp_path / "file.txt").write_text("content")
        tree = hash_directory(tmp_path)
        assert tree["type"] == "directory"
        assert tree["hash"] is not None
        assert len(tree["children"]) == 1
        assert tree["children"][0]["type"] == "file"

    def test_nested_directories(self, tmp_path):
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "file.txt").write_text("nested")
        tree = hash_directory(tmp_path)
        assert len(tree["children"]) == 1
        assert tree["children"][0]["type"] == "directory"
        assert len(tree["children"][0]["children"]) == 1

    def test_deterministic_hash(self, tmp_path):
        (tmp_path / "a.txt").write_text("alpha")
        (tmp_path / "b.txt").write_text("beta")
        hash1 = hash_directory(tmp_path)["hash"]
        hash2 = hash_directory(tmp_path)["hash"]
        assert hash1 == hash2

    def test_ignores_dotfiles(self, tmp_path):
        (tmp_path / "visible.txt").write_text("yes")
        (tmp_path / ".hidden").write_text("no")
        tree = hash_directory(tmp_path)
        names = [c["path"] for c in tree["children"]]
        assert "visible.txt" in names
        assert ".hidden" not in names

    def test_sorted_children(self, tmp_path):
        (tmp_path / "z.txt").write_text("last")
        (tmp_path / "a.txt").write_text("first")
        tree = hash_directory(tmp_path)
        paths = [c["path"] for c in tree["children"]]
        assert paths == sorted(paths)

    def test_content_change_changes_hash(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("original")
        hash1 = hash_directory(tmp_path)["hash"]
        f.write_text("modified")
        hash2 = hash_directory(tmp_path)["hash"]
        assert hash1 != hash2


class TestBuildReleaseTree:
    def test_builds_tree_across_platforms(self, tmp_path):
        for platform in ["claude", "vscode", "copilot-native"]:
            d = tmp_path / platform
            d.mkdir()
            (d / "SKILL.md").write_text(f"# {platform} skill")

        tree = build_release_tree(tmp_path)
        assert tree["type"] == "root"
        assert tree["hash"] is not None
        child_names = [c["path"] for c in tree["children"]]
        assert "claude" in child_names
        assert "vscode" in child_names
        assert "copilot-native" in child_names

    def test_root_hash_changes_with_content(self, tmp_path):
        (tmp_path / "claude").mkdir()
        (tmp_path / "claude" / "SKILL.md").write_text("v1")
        hash1 = build_release_tree(tmp_path)["hash"]
        (tmp_path / "claude" / "SKILL.md").write_text("v2")
        hash2 = build_release_tree(tmp_path)["hash"]
        assert hash1 != hash2

    def test_empty_directory_produces_tree(self, tmp_path):
        tree = build_release_tree(tmp_path)
        assert tree["type"] == "root"
        assert tree["hash"] is not None
        assert len(tree["children"]) == 0
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_merkle.py -v
```

- [ ] **Step 3: Implement merkle.py**

Create `publish/merkle.py`:

```python
"""SHA-256 Merkle tree computation for skill factory publish pipeline."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_file(path: Path) -> str:
    """SHA-256 hash of file content."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_directory(path: Path) -> dict:
    """Recursively build Merkle tree for a directory."""
    tree: dict = {"path": path.name, "children": [], "type": "directory"}

    for child in sorted(path.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_file():
            tree["children"].append({
                "path": child.name,
                "hash": hash_file(child),
                "type": "file",
            })
        elif child.is_dir():
            tree["children"].append(hash_directory(child))

    child_hashes = "".join(
        c["hash"] for c in sorted(tree["children"], key=lambda c: c["path"])
    )
    tree["hash"] = hashlib.sha256(child_hashes.encode()).hexdigest()
    return tree


def build_release_tree(working_dir: Path) -> dict:
    """Build full Merkle tree across all platform directories."""
    tree: dict = {"path": "release", "children": [], "type": "root"}

    for platform in sorted(working_dir.iterdir()):
        if platform.is_dir() and not platform.name.startswith("."):
            tree["children"].append(hash_directory(platform))

    child_hashes = "".join(
        c["hash"] for c in sorted(tree["children"], key=lambda c: c["path"])
    )
    tree["hash"] = hashlib.sha256(child_hashes.encode()).hexdigest()
    return tree
```

- [ ] **Step 4: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_merkle.py -v
```

- [ ] **Step 5: Commit**

```bash
git add publish/merkle.py tests/test_merkle.py
git commit -m "feat: implement SHA-256 Merkle tree computation"
```

---

### Task 2: Implement and test publish.py

**Files:**
- Create: `publish/publish.py`
- Create: `tests/test_publish.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_publish.py`:

```python
"""Tests for publish.publish — publish orchestrator."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from publish.publish import publish, PublishResult


@pytest.fixture
def factory_root(tmp_path):
    """Create a minimal factory-like directory structure."""
    # working/ with compiled output
    for platform in ["claude", "vscode", "copilot-native"]:
        d = tmp_path / "working" / platform / "_example"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"# {platform} example skill")

    # templates/
    t = tmp_path / "templates"
    t.mkdir()
    (t / "CLAUDE.local.md").write_text("# Local overrides")

    # compiler/config.yml
    (tmp_path / "compiler").mkdir()
    config = {
        "paths": {"working": "working"},
        "publish": {"repo": str(tmp_path / "published"), "include_templates": True},
    }
    import yaml
    (tmp_path / "compiler" / "config.yml").write_text(yaml.dump(config))

    # .factory/
    (tmp_path / ".factory").mkdir()

    return tmp_path


@pytest.fixture
def published_repo(factory_root):
    """Create the published repo target."""
    repo = factory_root / "published"
    repo.mkdir()
    # Init as git repo for commit step
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), capture_output=True)
    return repo


class TestPublish:
    def test_copies_working_to_published(self, factory_root, published_repo):
        result = publish(factory_root)
        assert (published_repo / "claude" / "_example" / "SKILL.md").exists()
        assert (published_repo / "vscode" / "_example" / "SKILL.md").exists()

    def test_copies_templates(self, factory_root, published_repo):
        result = publish(factory_root)
        assert (published_repo / "templates" / "CLAUDE.local.md").exists()

    def test_writes_manifest(self, factory_root, published_repo):
        result = publish(factory_root)
        manifest_path = published_repo / "MANIFEST.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert "version" in manifest
        assert "root_hash" in manifest
        assert "platforms" in manifest
        assert "tree" in manifest

    def test_manifest_has_platform_hashes(self, factory_root, published_repo):
        result = publish(factory_root)
        manifest = json.loads((published_repo / "MANIFEST.json").read_text())
        assert "claude" in manifest["platforms"]
        assert "hash" in manifest["platforms"]["claude"]

    def test_returns_publish_result(self, factory_root, published_repo):
        result = publish(factory_root)
        assert isinstance(result, PublishResult)
        assert result.root_hash is not None
        assert result.version is not None
        assert len(result.platform_hashes) > 0

    def test_content_change_changes_hash(self, factory_root, published_repo):
        result1 = publish(factory_root, version="2026.03.27.1")
        (factory_root / "working" / "claude" / "_example" / "SKILL.md").write_text("# Changed")
        result2 = publish(factory_root, version="2026.03.27.2")
        assert result1.root_hash != result2.root_hash

    def test_dry_run_doesnt_copy(self, factory_root, published_repo):
        result = publish(factory_root, dry_run=True)
        assert not (published_repo / "claude").exists()
        assert result.root_hash is not None  # hash still computed
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_publish.py -v
```

- [ ] **Step 3: Implement publish.py**

Create `publish/publish.py` with:

**`PublishResult` dataclass**: version, root_hash, platform_hashes, manifest_path, factory_commit

**`publish(factory_root, version=None, dry_run=False) -> PublishResult`**:
1. Load config from compiler/config.yml
2. Determine published repo path from config
3. Auto-generate version if not provided: `YYYY.MM.DD.N` format
4. Copy `working/<platform>/` → published repo `<platform>/` (using shutil.copytree with dirs_exist_ok=True)
5. If `include_templates`, copy `templates/` → published repo `templates/`
6. Compute Merkle tree over published content (excluding MANIFEST.json, .git/)
7. Get factory commit hash from git
8. Build MANIFEST.json with version, timestamp, root_hash, factory_commit, platform hashes, intent versions, full tree
9. Write MANIFEST.json to published repo root
10. Record in SQLite (best-effort)
11. Return PublishResult

If `dry_run`: compute hash over working/ directly without copying, still return result.

**CLI (`_cli()`)**: argparse with:
- `--version` (optional, auto-generated if omitted)
- `--dry-run` flag
- Prints version and root hash on success

- [ ] **Step 4: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_publish.py -v
```

- [ ] **Step 5: Commit**

```bash
git add publish/publish.py tests/test_publish.py
git commit -m "feat: implement publish pipeline with MANIFEST.json"
```

---

### Task 3: Implement and test verify.py

**Files:**
- Create: `publish/verify.py`
- Create: `tests/test_verify.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_verify.py`:

```python
"""Tests for publish.verify — verification CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from publish.verify import verify_manifest, verify_skill, VerifyResult


@pytest.fixture
def published_repo(tmp_path):
    """Create a published repo with valid MANIFEST.json."""
    from publish.merkle import build_release_tree

    # Create platform content
    for platform in ["claude", "vscode"]:
        d = tmp_path / platform / "_example"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"# {platform} skill")

    # Build real Merkle tree and manifest
    tree = build_release_tree(tmp_path)
    manifest = {
        "version": "2026.03.27.1",
        "timestamp": "2026-03-27T00:00:00Z",
        "root_hash": tree["hash"],
        "factory_commit": "abc123",
        "platforms": {
            c["path"]: {"hash": c["hash"], "skills_count": 1}
            for c in tree["children"]
        },
        "tree": tree,
    }
    (tmp_path / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))

    return tmp_path


class TestVerifyManifest:
    def test_valid_manifest_passes(self, published_repo):
        result = verify_manifest(published_repo)
        assert result.valid is True

    def test_tampered_file_fails(self, published_repo):
        (published_repo / "claude" / "_example" / "SKILL.md").write_text("# Tampered")
        result = verify_manifest(published_repo)
        assert result.valid is False
        assert "mismatch" in result.reason.lower() or "tamper" in result.reason.lower()

    def test_missing_manifest_fails(self, tmp_path):
        result = verify_manifest(tmp_path)
        assert result.valid is False

    def test_deep_verification(self, published_repo):
        result = verify_manifest(published_repo, deep=True)
        assert result.valid is True
        assert result.files_checked > 0


class TestVerifySkill:
    def test_valid_skill_passes(self, published_repo):
        result = verify_skill(published_repo, "claude/_example")
        assert result.valid is True

    def test_tampered_skill_fails(self, published_repo):
        (published_repo / "claude" / "_example" / "SKILL.md").write_text("# Tampered")
        result = verify_skill(published_repo, "claude/_example")
        assert result.valid is False

    def test_missing_skill_fails(self, published_repo):
        result = verify_skill(published_repo, "claude/nonexistent")
        assert result.valid is False
```

- [ ] **Step 2: Run to verify failure**

- [ ] **Step 3: Implement verify.py**

Create `publish/verify.py` with:

**`VerifyResult` dataclass**: valid (bool), reason (str), files_checked (int)

**`verify_manifest(repo_path, deep=False) -> VerifyResult`**:
- Quick mode: read MANIFEST.json, rebuild Merkle tree, compare root hash
- Deep mode: also verify every file hash in the tree against actual files

**`verify_skill(repo_path, skill_path) -> VerifyResult`**:
- Find the skill in the Merkle tree
- Verify its hash against the actual file(s)

**CLI**: argparse with:
- positional `repo` (defaults to cwd)
- `--deep` flag
- `--skill <path>` for single skill check
- `--version <X>` to verify a specific version

- [ ] **Step 4: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_verify.py -v
```

- [ ] **Step 5: Commit**

```bash
git add publish/verify.py tests/test_verify.py
git commit -m "feat: implement verification CLI for published repos"
```

---

### Task 4: Run full suite, validate end-to-end, and tag

- [ ] **Step 1: Run ALL tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/ -v --tb=short
```

Report total count.

- [ ] **Step 2: End-to-end test**

```bash
cd ~/repos/skill-factory
# Compile
python compiler/compile.py _example
# Publish (dry run — we don't want to actually modify the published repo)
python publish/publish.py --dry-run
```

Verify the dry run reports a root hash and version.

- [ ] **Step 3: Clean up**

```bash
rm -rf working/claude/_example working/vscode/prompts working/vscode/skills
rm -rf working/copilot-native/prompts working/copilot-native/skills
rm -f .factory/state.db
```

- [ ] **Step 4: Commit and tag**

```bash
git add -A
git status
git commit -m "chore: complete publish toolchain" --allow-empty
git tag v0.4.0-publish -m "Publish toolchain (Merkle tree, MANIFEST, verify) complete"
```
