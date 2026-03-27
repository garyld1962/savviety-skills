# Skill Factory Compiler Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 4-stage compilation pipeline (RESOLVE → DECIDE → EMIT → RECORD) that reads intent documents and platform definitions, then generates platform-specific skill artifacts in `working/`.

**Architecture:** Four modules under `compiler/`: `resolve.py` (load + validate inputs), `decide.py` (emission planning), `emit/` (per-platform artifact generators), and `compile.py` (orchestrator + CLI). Each module is independently testable. The compiler uses `FactoryDB` from `compiler/db.py` (Plan 2) for the RECORD stage.

**Tech Stack:** Python 3.12+, pyyaml, python-frontmatter, pytest, uv

**Spec:** `~/repos/skills/docs/superpowers/specs/2026-03-25-skill-factory-design.md` (section: Compilation Pipeline)

**Depends on:** Plan 1 (scaffolding) + Plan 2 (SQLite state DB)

---

## File Structure

```
~/repos/skill-factory/
├── compiler/
│   ├── __init__.py              # (exists)
│   ├── db.py                    # (exists — Plan 2)
│   ├── config.yml               # (exists — Plan 1)
│   ├── resolve.py               # RESOLVE stage: load intents, platforms, stacks, shared refs
│   ├── decide.py                # DECIDE stage: emission plan per component per platform
│   ├── compile.py               # Orchestrator + CLI entry point
│   └── emit/
│       ├── __init__.py          # (exists)
│       ├── base.py              # Base emitter class + data types
│       ├── claude.py            # Claude Code emitter
│       ├── vscode.py            # VS Code emitter
│       └── copilot_native.py    # Copilot Native emitter
├── intents/
│   └── _example/                # Test fixture: a minimal example intent
│       └── intent.md
└── tests/
    ├── test_db.py               # (exists — Plan 2)
    ├── test_resolve.py          # Tests for resolve.py
    ├── test_decide.py           # Tests for decide.py
    ├── test_emit.py             # Tests for all emitters
    └── test_compile.py          # Integration tests for compile.py
```

---

### Task 1: Create a test fixture intent

**Files:**
- Create: `intents/_example/intent.md`

We need a real intent document to test with. This is a minimal but complete example.

- [ ] **Step 1: Write the example intent**

Create `intents/_example/intent.md`:

```markdown
---
name: _example
version: 1.0.0
description: "Minimal example intent for testing the compiler"

components:
  - id: greeter
    type: prompt
    description: "A simple greeting prompt"
  - id: greeting-rules
    type: skill
    description: "Rules for generating greetings"

shared_refs:
  - shared/rubrics/severity.md

stack_aware: false

platform_notes:
  claude:
    strategy: "Merge into single SKILL.md"
  vscode:
    strategy: "Emit prompt + skill reference"
  copilot-native:
    strategy: "Emit prompt only, defer to built-in for rules"
    limitations:
      - "No standalone skill reference needed"
---

# Example Intent

## Goal

A minimal intent for testing the compilation pipeline end-to-end.

## Constraints

- Must produce valid artifacts for all three platforms
- Used only for testing — never published

## Component: greeter

### Inputs
- User's name (optional)

### Outputs
- A greeting message

### Behavior
1. If name provided, greet by name
2. Otherwise, use a generic greeting

## Component: greeting-rules

### Rules
- Greetings must be professional
- No slang or informal language
- Maximum 50 words
```

- [ ] **Step 2: Commit**

```bash
git add intents/_example/
git commit -m "test: add example intent fixture for compiler testing"
```

---

### Task 2: Implement and test resolve.py

**Files:**
- Create: `compiler/resolve.py`
- Create: `tests/test_resolve.py`

This module handles RESOLVE: loading and validating all inputs.

- [ ] **Step 1: Write failing tests**

Create `tests/test_resolve.py`:

```python
"""Tests for compiler.resolve — RESOLVE stage."""

import pytest
from pathlib import Path

from compiler.resolve import (
    load_intent,
    load_platform,
    resolve_stack,
    load_shared_ref,
    Intent,
    Platform,
    Stack,
    ResolveError,
)

REPO_ROOT = Path(__file__).parent.parent


class TestLoadIntent:
    def test_loads_example_intent(self):
        intent = load_intent(REPO_ROOT / "intents" / "_example")
        assert intent.name == "_example"
        assert intent.version == "1.0.0"
        assert len(intent.components) == 2
        assert intent.components[0].id == "greeter"
        assert intent.components[0].type == "prompt"
        assert intent.components[1].id == "greeting-rules"
        assert intent.components[1].type == "skill"

    def test_loads_shared_refs(self):
        intent = load_intent(REPO_ROOT / "intents" / "_example")
        assert "shared/rubrics/severity.md" in intent.shared_refs

    def test_loads_platform_notes(self):
        intent = load_intent(REPO_ROOT / "intents" / "_example")
        assert "claude" in intent.platform_notes
        assert "strategy" in intent.platform_notes["claude"]

    def test_loads_body_content(self):
        intent = load_intent(REPO_ROOT / "intents" / "_example")
        assert "## Goal" in intent.body
        assert "## Component: greeter" in intent.body

    def test_missing_intent_raises(self, tmp_path):
        with pytest.raises(ResolveError, match="not found"):
            load_intent(tmp_path / "nonexistent")

    def test_missing_intent_md_raises(self, tmp_path):
        (tmp_path / "bad-intent").mkdir()
        with pytest.raises(ResolveError, match="intent.md"):
            load_intent(tmp_path / "bad-intent")


class TestLoadPlatform:
    def test_loads_claude_platform(self):
        platform = load_platform(REPO_ROOT / "platforms" / "claude")
        assert platform.name == "claude-code"
        assert platform.capabilities["parallel_dispatch"] is True
        assert platform.rules["compilation"]["component_merge"] is True

    def test_loads_vscode_platform(self):
        platform = load_platform(REPO_ROOT / "platforms" / "vscode")
        assert platform.name == "vscode-copilot"
        assert platform.rules["compilation"]["prompt_emit"] == "prompt"

    def test_loads_copilot_native_builtins(self):
        platform = load_platform(REPO_ROOT / "platforms" / "copilot-native")
        assert platform.capabilities.get("built_in_plan") is True

    def test_loads_extensions(self):
        platform = load_platform(REPO_ROOT / "platforms" / "claude")
        ext_names = [e["name"] for e in platform.extensions]
        assert "superpowers" in ext_names

    def test_missing_platform_raises(self, tmp_path):
        with pytest.raises(ResolveError):
            load_platform(tmp_path / "nonexistent")


class TestResolveStack:
    def test_resolves_base_stack(self):
        stack = resolve_stack("dotnet", REPO_ROOT / "stacks")
        assert stack.name == "dotnet"
        assert "naming" in stack.rules
        assert stack.language == "C#"

    def test_resolves_child_with_inheritance(self):
        stack = resolve_stack("dotnet-api", REPO_ROOT / "stacks")
        assert "naming" in stack.rules  # from parent
        assert "api" in stack.rules     # from child
        assert stack.framework == "ASP.NET Core Minimal APIs"

    def test_resolves_deep_chain(self):
        stack = resolve_stack("nextjs-app", REPO_ROOT / "stacks")
        assert "quality" in stack.rules     # from typescript (grandparent)
        assert "rendering" in stack.rules   # from nextjs (parent)
        assert "structure" in stack.rules   # from nextjs-app (self)

    def test_missing_stack_raises(self):
        with pytest.raises(ResolveError, match="not found"):
            resolve_stack("eiffel", REPO_ROOT / "stacks")

    def test_circular_inheritance_raises(self, tmp_path):
        (tmp_path / "a.yml").write_text("name: a\nextends: b\nrules: {}")
        (tmp_path / "b.yml").write_text("name: b\nextends: a\nrules: {}")
        with pytest.raises(ResolveError, match="[Cc]ircular"):
            resolve_stack("a", tmp_path)


class TestLoadSharedRef:
    def test_loads_severity_rubric(self):
        content = load_shared_ref("shared/rubrics/severity.md", REPO_ROOT)
        assert len(content) > 0
        assert "severity" in content.lower() or "Severity" in content

    def test_missing_ref_raises(self):
        with pytest.raises(ResolveError, match="not found"):
            load_shared_ref("shared/nonexistent.md", REPO_ROOT)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_resolve.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement resolve.py**

Create `compiler/resolve.py` with:

- **Data classes**: `Component` (id, type, description), `Intent` (name, version, description, components, shared_refs, stack_aware, stack_hints, platform_notes, body), `Platform` (name, version, capabilities, rules, extensions, artifact_types), `Stack` (name, language, runtime, framework, rules)
- **`ResolveError`**: exception class for resolve failures
- **`load_intent(path)`**: reads `intent.md` using python-frontmatter, parses components into `Component` objects, returns `Intent`
- **`load_platform(path)`**: reads `capabilities.yml` and `rules.yml`, merges into `Platform`
- **`resolve_stack(name, stacks_dir)`**: loads YAML, recursively resolves `extends`, detects circular refs, merges rules (child extends parent per category), returns `Stack`
- **`load_shared_ref(ref_path, repo_root)`**: reads the file content, raises if missing

Use `@dataclass` for all data types. Use `yaml.safe_load` for YAML. Use `frontmatter.load` for intent.md.

- [ ] **Step 4: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_resolve.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add compiler/resolve.py tests/test_resolve.py
git commit -m "feat: implement RESOLVE stage (load intents, platforms, stacks, shared refs)"
```

---

### Task 3: Implement and test decide.py

**Files:**
- Create: `compiler/decide.py`
- Create: `tests/test_decide.py`

This module handles DECIDE: determining what to emit per component per platform.

- [ ] **Step 1: Write failing tests**

Create `tests/test_decide.py`:

```python
"""Tests for compiler.decide — DECIDE stage."""

import pytest
from compiler.resolve import Component, Intent, Platform, Stack
from compiler.decide import decide, EmissionPlan, Action


def _make_intent(components=None, shared_refs=None, stack_aware=False, platform_notes=None):
    return Intent(
        name="test",
        version="1.0.0",
        description="test intent",
        components=components or [],
        shared_refs=shared_refs or [],
        stack_aware=stack_aware,
        stack_hints=[],
        platform_notes=platform_notes or {},
        body="",
    )


def _make_platform(name="test-platform", builtins=None, extensions=None, compilation=None):
    caps = builtins or {}
    return Platform(
        name=name,
        version="2026.03.1",
        capabilities=caps,
        rules={"compilation": compilation or {
            "shared_ref_strategy": "reference",
            "component_merge": False,
            "agent_emit": "standalone",
            "prompt_emit": "prompt",
        }},
        extensions=extensions or [],
        artifact_types={
            "skill": {"supported": True},
            "prompt": {"supported": True},
            "agent": {"supported": True, "standalone_definition": True},
        },
    )


class TestDecideAction:
    def test_full_emit_when_no_builtin(self):
        intent = _make_intent(components=[
            Component(id="greeter", type="prompt", description="greeting"),
        ])
        platform = _make_platform()
        plan = decide(intent, platform, stacks={}, shared={})
        assert plan.components[0].action == Action.FULL_EMIT

    def test_skip_when_builtin_covers(self):
        intent = _make_intent(components=[
            Component(id="planner", type="prompt", description="planning"),
        ])
        platform = _make_platform(builtins={"built_in_plan": True})
        plan = decide(intent, platform, stacks={}, shared={})
        assert plan.components[0].action == Action.SKIP

    def test_thin_wrapper_when_extension_covers(self):
        intent = _make_intent(components=[
            Component(id="planner", type="prompt", description="planning"),
        ])
        platform = _make_platform(extensions=[
            {"name": "superpowers", "status": "default", "provides": ["planning"]},
        ])
        plan = decide(intent, platform, stacks={}, shared={})
        assert plan.components[0].action == Action.THIN_WRAPPER

    def test_full_emit_when_extension_is_optional(self):
        intent = _make_intent(components=[
            Component(id="planner", type="prompt", description="planning"),
        ])
        platform = _make_platform(extensions=[
            {"name": "superpowers", "status": "optional", "provides": ["planning"]},
        ])
        plan = decide(intent, platform, stacks={}, shared={})
        assert plan.components[0].action == Action.FULL_EMIT

    def test_prompt_maps_to_skill_on_claude(self):
        intent = _make_intent(components=[
            Component(id="greeter", type="prompt", description="greeting"),
        ])
        platform = _make_platform(compilation={
            "shared_ref_strategy": "sub_file",
            "component_merge": True,
            "agent_emit": "sub_file",
            "prompt_emit": "skill",
        })
        plan = decide(intent, platform, stacks={}, shared={})
        assert plan.components[0].artifact_type == "skill"

    def test_empty_components_produces_empty_plan(self):
        intent = _make_intent(components=[])
        platform = _make_platform()
        plan = decide(intent, platform, stacks={}, shared={})
        assert len(plan.components) == 0


class TestEmissionPlan:
    def test_plan_has_intent_name(self):
        intent = _make_intent()
        platform = _make_platform()
        plan = decide(intent, platform, stacks={}, shared={})
        assert plan.intent_name == "test"

    def test_plan_tracks_emitted_and_skipped(self):
        intent = _make_intent(components=[
            Component(id="planner", type="prompt", description="planning"),
            Component(id="greeter", type="prompt", description="greeting"),
        ])
        platform = _make_platform(builtins={"built_in_plan": True})
        plan = decide(intent, platform, stacks={}, shared={})
        assert len(plan.emitted) >= 1
        assert len(plan.skipped) >= 1
```

- [ ] **Step 2: Run tests to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_decide.py -v
```

- [ ] **Step 3: Implement decide.py**

Create `compiler/decide.py` with:

- **`Action` enum**: SKIP, THIN_WRAPPER, FULL_EMIT
- **`ComponentPlan` dataclass**: id, action, reason, artifact_type, shared_ref_strategy
- **`EmissionPlan` dataclass**: intent_name, components list, with `emitted` and `skipped` properties
- **`decide(intent, platform, stacks, shared)`**: returns EmissionPlan
  - For each component, check:
    1. Is there a `built_in_*` capability matching the component's purpose? → SKIP
    2. Is there a default/approved extension providing the capability? → THIN_WRAPPER
    3. Otherwise → FULL_EMIT
  - Determine `artifact_type` from platform rules compilation directives (e.g., `prompt_emit: skill` means prompts become skills on that platform)
  - Determine `shared_ref_strategy` from platform rules

The builtin matching logic: map component descriptions/IDs to builtin capability keys. A component with id containing "plan" matches `built_in_plan`. A component with id containing "review" matches `built_in_review`. This is heuristic — the compiler can be refined later.

The extension matching logic: check if any extension with status "default" or "approved" has a `provides` entry that fuzzy-matches the component's purpose.

- [ ] **Step 4: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_decide.py -v
```

- [ ] **Step 5: Commit**

```bash
git add compiler/decide.py tests/test_decide.py
git commit -m "feat: implement DECIDE stage (emission planning per component per platform)"
```

---

### Task 4: Implement and test base emitter + Claude emitter

**Files:**
- Create: `compiler/emit/base.py`
- Create: `compiler/emit/claude.py`
- Create: `tests/test_emit.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_emit.py`:

```python
"""Tests for compiler.emit — EMIT stage."""

import pytest
from pathlib import Path

from compiler.resolve import Component, Intent, load_intent
from compiler.decide import Action, ComponentPlan, EmissionPlan
from compiler.emit.base import Emitter
from compiler.emit.claude import ClaudeEmitter

REPO_ROOT = Path(__file__).parent.parent


def _make_plan(components=None):
    return EmissionPlan(
        intent_name="_example",
        components=components or [],
    )


def _make_intent():
    return load_intent(REPO_ROOT / "intents" / "_example")


class TestClaudeEmitter:
    def test_emits_skill_md(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.FULL_EMIT,
                          artifact_type="skill", shared_ref_strategy="sub_file",
                          reason="No builtin coverage"),
            ComponentPlan(id="greeting-rules", action=Action.FULL_EMIT,
                          artifact_type="skill", shared_ref_strategy="sub_file",
                          reason="No builtin coverage"),
        ])
        shared = {"shared/rubrics/severity.md": "# Severity\nCritical, Major, Minor"}
        emitter = ClaudeEmitter()
        files = emitter.emit(intent, plan, shared, {}, tmp_path)
        skill_md = tmp_path / "_example" / "SKILL.md"
        assert skill_md.exists()
        content = skill_md.read_text()
        assert "name: _example" in content  # frontmatter
        assert "greeter" in content.lower() or "greeting" in content.lower()

    def test_emits_shared_refs_as_sub_files(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.FULL_EMIT,
                          artifact_type="skill", shared_ref_strategy="sub_file",
                          reason="No builtin coverage"),
        ])
        shared = {"shared/rubrics/severity.md": "# Severity\nContent here"}
        emitter = ClaudeEmitter()
        emitter.emit(intent, plan, shared, {}, tmp_path)
        ref_file = tmp_path / "_example" / "foundations" / "severity.md"
        assert ref_file.exists()
        assert "Content here" in ref_file.read_text()

    def test_skipped_components_not_emitted(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.SKIP,
                          artifact_type="skill", shared_ref_strategy="sub_file",
                          reason="Built-in covers"),
        ])
        emitter = ClaudeEmitter()
        files = emitter.emit(intent, plan, {}, {}, tmp_path)
        # Should still create the skill dir but with minimal content
        assert len(files) == 0 or not (tmp_path / "_example" / "SKILL.md").exists()

    def test_returns_list_of_written_files(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.FULL_EMIT,
                          artifact_type="skill", shared_ref_strategy="sub_file",
                          reason="Full emit"),
        ])
        emitter = ClaudeEmitter()
        files = emitter.emit(intent, plan, {}, {}, tmp_path)
        assert isinstance(files, list)
        assert all(isinstance(f, Path) for f in files)
        assert len(files) > 0
```

- [ ] **Step 2: Run tests to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_emit.py -v
```

- [ ] **Step 3: Implement base.py**

Create `compiler/emit/base.py` with:

```python
"""Base emitter interface and shared data types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from compiler.resolve import Intent
from compiler.decide import EmissionPlan


class Emitter(ABC):
    """Base class for platform-specific emitters."""

    @abstractmethod
    def emit(
        self,
        intent: Intent,
        plan: EmissionPlan,
        shared: dict[str, str],
        stacks: dict[str, object],
        output_dir: Path,
    ) -> list[Path]:
        """Emit artifacts to output_dir. Return list of files written."""
        ...
```

- [ ] **Step 4: Implement claude.py**

Create `compiler/emit/claude.py`:

The Claude emitter merges all components into a single SKILL.md with:
- YAML frontmatter (name, description from intent)
- Body content extracted from the intent's markdown body
- Component sections from the intent body (extracted by `## Component: <id>` headings)
- Shared references emitted as sub-files in `foundations/` directory

```python
"""Claude Code emitter — merges components into single SKILL.md with sub-files."""

from __future__ import annotations

from pathlib import Path

from compiler.resolve import Intent
from compiler.decide import Action, EmissionPlan
from compiler.emit.base import Emitter


class ClaudeEmitter(Emitter):

    def emit(self, intent, plan, shared, stacks, output_dir):
        emitted_components = [c for c in plan.components if c.action != Action.SKIP]
        if not emitted_components:
            return []

        skill_dir = output_dir / intent.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        files = []

        # Build SKILL.md
        lines = []
        lines.append("---")
        lines.append(f"name: {intent.name}")
        lines.append(f'description: "{intent.description}"')
        lines.append("---")
        lines.append("")
        lines.append(f"# /{intent.name} — {intent.description}")
        lines.append("")

        # Include intent body (goal, constraints, component specs)
        if intent.body:
            lines.append(intent.body.strip())
            lines.append("")

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("\n".join(lines))
        files.append(skill_md)

        # Emit shared refs as sub-files in foundations/
        if shared:
            foundations = skill_dir / "foundations"
            foundations.mkdir(exist_ok=True)
            for ref_path, content in shared.items():
                ref_name = Path(ref_path).name
                ref_file = foundations / ref_name
                ref_file.write_text(content)
                files.append(ref_file)

        return files
```

- [ ] **Step 5: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_emit.py -v
```

- [ ] **Step 6: Commit**

```bash
git add compiler/emit/base.py compiler/emit/claude.py tests/test_emit.py
git commit -m "feat: implement Claude Code emitter"
```

---

### Task 5: Implement VS Code and Copilot Native emitters

**Files:**
- Create: `compiler/emit/vscode.py`
- Create: `compiler/emit/copilot_native.py`
- Modify: `tests/test_emit.py`

- [ ] **Step 1: Add failing tests for VS Code emitter**

Append to `tests/test_emit.py`:

```python
from compiler.emit.vscode import VSCodeEmitter


class TestVSCodeEmitter:
    def test_emits_prompt_file(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.FULL_EMIT,
                          artifact_type="prompt", shared_ref_strategy="reference",
                          reason="Full emit"),
        ])
        emitter = VSCodeEmitter()
        files = emitter.emit(intent, plan, {}, {}, tmp_path)
        prompt_file = tmp_path / "prompts" / "dev" / "_example.prompt.md"
        assert prompt_file.exists()
        content = prompt_file.read_text()
        assert "description:" in content

    def test_emits_skill_reference(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeting-rules", action=Action.FULL_EMIT,
                          artifact_type="skill", shared_ref_strategy="reference",
                          reason="Full emit"),
        ])
        emitter = VSCodeEmitter()
        files = emitter.emit(intent, plan, {}, {}, tmp_path)
        skill_file = tmp_path / "skills" / "greeting-rules" / "SKILL.md"
        assert skill_file.exists()

    def test_emits_shared_refs_as_skill_files(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.FULL_EMIT,
                          artifact_type="prompt", shared_ref_strategy="reference",
                          reason="Full emit"),
        ])
        shared = {"shared/rubrics/severity.md": "# Severity\nContent"}
        emitter = VSCodeEmitter()
        emitter.emit(intent, plan, shared, {}, tmp_path)
        # Shared refs go to skills/ as reference files
        ref_file = tmp_path / "skills" / "review-foundations" / "severity.md"
        assert ref_file.exists()
```

- [ ] **Step 2: Add failing tests for Copilot Native emitter**

Append to `tests/test_emit.py`:

```python
from compiler.emit.copilot_native import CopilotNativeEmitter


class TestCopilotNativeEmitter:
    def test_skips_builtin_covered_components(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="planner", action=Action.SKIP,
                          artifact_type="prompt", shared_ref_strategy="reference",
                          reason="Built-in /plan covers this"),
        ])
        emitter = CopilotNativeEmitter()
        files = emitter.emit(intent, plan, {}, {}, tmp_path)
        assert len(files) == 0

    def test_emits_thin_wrapper(self, tmp_path):
        intent = _make_intent()
        plan = _make_plan(components=[
            ComponentPlan(id="greeter", action=Action.THIN_WRAPPER,
                          artifact_type="prompt", shared_ref_strategy="reference",
                          reason="Extension covers base case"),
        ])
        emitter = CopilotNativeEmitter()
        files = emitter.emit(intent, plan, {}, {}, tmp_path)
        assert len(files) > 0
        prompt_file = tmp_path / "prompts" / "dev" / "_example.prompt.md"
        assert prompt_file.exists()
        content = prompt_file.read_text()
        # Thin wrapper should be shorter than full emit
        assert len(content) < 500
```

- [ ] **Step 3: Run tests to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_emit.py -v -k "VSCode or CopilotNative"
```

- [ ] **Step 4: Implement vscode.py**

The VS Code emitter separates artifacts:
- Prompts → `prompts/<category>/<intent-name>.prompt.md` with YAML frontmatter (description, agent, tools)
- Skills → `skills/<component-id>/SKILL.md` with YAML frontmatter (name, description)
- Agents → `agents/<component-id>.agent.md` with YAML frontmatter (description, tools)
- Shared refs → `skills/review-foundations/<ref-name>` as reference files

Category is determined from the intent name or defaults to "dev".

- [ ] **Step 5: Implement copilot_native.py**

The Copilot Native emitter is like VS Code but:
- SKIPs components where a built-in exists (already handled by the plan)
- Emits THIN_WRAPPER as a shorter prompt that references the built-in
- FULL_EMIT is identical to VS Code

- [ ] **Step 6: Run all emitter tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_emit.py -v
```

- [ ] **Step 7: Commit**

```bash
git add compiler/emit/vscode.py compiler/emit/copilot_native.py tests/test_emit.py
git commit -m "feat: implement VS Code and Copilot Native emitters"
```

---

### Task 6: Implement and test compile.py (orchestrator + CLI)

**Files:**
- Create: `compiler/compile.py`
- Create: `tests/test_compile.py`

This is the top-level orchestrator that ties RESOLVE → DECIDE → EMIT → RECORD together.

- [ ] **Step 1: Write failing tests**

Create `tests/test_compile.py`:

```python
"""Tests for compiler.compile — orchestrator + CLI."""

import subprocess
import sys
from pathlib import Path

import pytest

from compiler.compile import compile_intent, compile_all

REPO_ROOT = Path(__file__).parent.parent


class TestCompileIntent:
    def test_compiles_example_for_all_platforms(self):
        results = compile_intent("_example", repo_root=REPO_ROOT)
        assert "claude" in results
        assert "vscode" in results
        assert "copilot-native" in results
        for platform, result in results.items():
            assert result["status"] in ("success", "warning")

    def test_compiles_example_for_single_platform(self):
        results = compile_intent("_example", platforms=["claude"], repo_root=REPO_ROOT)
        assert "claude" in results
        assert "vscode" not in results

    def test_produces_files_in_working_dir(self):
        compile_intent("_example", repo_root=REPO_ROOT)
        working = REPO_ROOT / "working"
        assert (working / "claude" / "_example" / "SKILL.md").exists()
        assert (working / "vscode" / "prompts").exists()

    def test_returns_error_for_missing_intent(self):
        with pytest.raises(Exception):
            compile_intent("nonexistent", repo_root=REPO_ROOT)


class TestCompileAll:
    def test_compiles_all_intents(self):
        results = compile_all(repo_root=REPO_ROOT)
        assert "_example" in results


class TestCLI:
    def test_compile_single_intent(self):
        result = subprocess.run(
            [sys.executable, "compiler/compile.py", "_example"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0

    def test_compile_all(self):
        result = subprocess.run(
            [sys.executable, "compiler/compile.py", "--all"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0

    def test_dry_run(self):
        result = subprocess.run(
            [sys.executable, "compiler/compile.py", "_example", "--dry-run"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        assert "dry" in result.stdout.lower() or "plan" in result.stdout.lower()

    def test_platform_filter(self):
        result = subprocess.run(
            [sys.executable, "compiler/compile.py", "_example", "--platform", "claude"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
```

- [ ] **Step 2: Run tests to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_compile.py -v
```

- [ ] **Step 3: Implement compile.py**

Create `compiler/compile.py` — the orchestrator:

```python
"""Skill factory compiler — orchestrates RESOLVE → DECIDE → EMIT → RECORD."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

from compiler.resolve import load_intent, load_platform, resolve_stack, load_shared_ref, ResolveError
from compiler.decide import decide
from compiler.emit.claude import ClaudeEmitter
from compiler.emit.vscode import VSCodeEmitter
from compiler.emit.copilot_native import CopilotNativeEmitter


EMITTERS = {
    "claude": ClaudeEmitter(),
    "vscode": VSCodeEmitter(),
    "copilot-native": CopilotNativeEmitter(),
}


def _load_config(repo_root: Path) -> dict:
    config_path = repo_root / "compiler" / "config.yml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text()) or {}
    return {}


def compile_intent(
    intent_name: str,
    platforms: list[str] | None = None,
    repo_root: Path | None = None,
    dry_run: bool = False,
) -> dict:
    repo_root = repo_root or Path.cwd()
    config = _load_config(repo_root)
    paths = config.get("paths", {})

    # RESOLVE
    intent = load_intent(repo_root / paths.get("intents", "intents") / intent_name)

    # Load shared refs
    shared = {}
    for ref in intent.shared_refs:
        shared[ref] = load_shared_ref(ref, repo_root)

    # Load stacks if stack-aware
    stacks = {}
    if intent.stack_aware:
        stacks_dir = repo_root / paths.get("stacks", "stacks")
        for hint in intent.stack_hints:
            stacks[hint] = resolve_stack(hint, stacks_dir)

    # Determine platforms
    platforms_dir = repo_root / paths.get("platforms", "platforms")
    if platforms is None:
        platforms = [p.name for p in platforms_dir.iterdir() if p.is_dir()]

    results = {}
    for platform_name in platforms:
        try:
            platform = load_platform(platforms_dir / platform_name)
        except ResolveError as e:
            results[platform_name] = {"status": "error", "error": str(e)}
            continue

        # DECIDE
        plan = decide(intent, platform, stacks, shared)

        if dry_run:
            results[platform_name] = {
                "status": "dry_run",
                "plan": {
                    "emitted": [c.id for c in plan.emitted],
                    "skipped": [c.id for c in plan.skipped],
                },
            }
            continue

        # EMIT
        working_dir = repo_root / paths.get("working", "working") / platform_name
        emitter = EMITTERS.get(platform_name)
        if not emitter:
            results[platform_name] = {"status": "error", "error": f"No emitter for {platform_name}"}
            continue

        start = time.monotonic()
        files = emitter.emit(intent, plan, shared, stacks, working_dir)
        duration_ms = int((time.monotonic() - start) * 1000)

        # RECORD (best-effort)
        try:
            from compiler.db import FactoryDB
            db = FactoryDB(repo_root / ".factory" / "state.db")
            db.register_intent(
                intent.name, intent.version, str(intent_name),
                len(intent.components), len(intent.shared_refs), intent.stack_aware,
            )
            db.record_compilation(
                intent_name=intent.name,
                intent_version=intent.version,
                platform=platform_name,
                caps_version=platform.version,
                rules_version=platform.version,
                status="success",
                components_emitted=[c.id for c in plan.emitted],
                components_skipped=[c.id for c in plan.skipped],
                warnings=[],
                duration_ms=duration_ms,
            )
            db.close()
        except Exception:
            pass  # SQLite recording is best-effort per spec

        results[platform_name] = {
            "status": "success",
            "files": [str(f) for f in files],
            "emitted": [c.id for c in plan.emitted],
            "skipped": [c.id for c in plan.skipped],
            "duration_ms": duration_ms,
        }

    return results


def compile_all(
    platforms: list[str] | None = None,
    repo_root: Path | None = None,
    dry_run: bool = False,
) -> dict:
    repo_root = repo_root or Path.cwd()
    config = _load_config(repo_root)
    intents_dir = repo_root / config.get("paths", {}).get("intents", "intents")

    results = {}
    for intent_dir in sorted(intents_dir.iterdir()):
        if intent_dir.is_dir() and (intent_dir / "intent.md").exists():
            try:
                results[intent_dir.name] = compile_intent(
                    intent_dir.name, platforms=platforms,
                    repo_root=repo_root, dry_run=dry_run,
                )
            except Exception as e:
                results[intent_dir.name] = {"error": str(e)}

    return results


def _cli():
    parser = argparse.ArgumentParser(description="Skill factory compiler")
    parser.add_argument("intent", nargs="?", help="Intent name to compile")
    parser.add_argument("--all", action="store_true", help="Compile all intents")
    parser.add_argument("--platform", help="Compile for a single platform")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without writing")

    args = parser.parse_args()

    if not args.intent and not args.all:
        parser.print_help()
        sys.exit(1)

    platforms = [args.platform] if args.platform else None

    if args.all:
        results = compile_all(platforms=platforms, dry_run=args.dry_run)
    else:
        results = {args.intent: compile_intent(
            args.intent, platforms=platforms, dry_run=args.dry_run,
        )}

    # Print results
    import json
    for name, result in results.items():
        if args.dry_run:
            print(f"[DRY RUN] {name}:")
            for platform, data in result.items():
                plan = data.get("plan", {})
                print(f"  {platform}: emit={plan.get('emitted', [])}, skip={plan.get('skipped', [])}")
        else:
            for platform, data in (result.items() if isinstance(result, dict) and "status" not in result else [(name, result)]):
                status = data.get("status", "unknown") if isinstance(data, dict) else "error"
                files_count = len(data.get("files", [])) if isinstance(data, dict) else 0
                print(f"  {platform}: {status} ({files_count} files)")


if __name__ == "__main__":
    _cli()
```

- [ ] **Step 4: Run all tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/ -v
```

Expected: all tests across all test files pass.

- [ ] **Step 5: Commit**

```bash
git add compiler/compile.py tests/test_compile.py
git commit -m "feat: implement compiler orchestrator with CLI"
```

---

### Task 7: Clean up working/ artifacts and tag

- [ ] **Step 1: Run full test suite**

```bash
cd ~/repos/skill-factory && uv run pytest tests/ -v --tb=short
```

Report total test count and any failures.

- [ ] **Step 2: Run a real compilation**

```bash
cd ~/repos/skill-factory
python compiler/compile.py _example
```

Verify output files exist in `working/claude/`, `working/vscode/`, `working/copilot-native/`.

- [ ] **Step 3: Run dry-run mode**

```bash
python compiler/compile.py _example --dry-run
```

Verify it prints the plan without writing files.

- [ ] **Step 4: Clean working/ and .factory/ artifacts**

```bash
rm -rf working/claude/_example working/vscode/prompts working/vscode/skills
rm -rf working/copilot-native/prompts working/copilot-native/skills
rm -f .factory/state.db .factory/state-export.json
```

- [ ] **Step 5: Commit and tag**

```bash
git add -A
git status
git commit -m "chore: complete compiler core implementation" --allow-empty
git tag v0.3.0-compiler -m "Compiler core (resolve, decide, emit, record) complete"
```
