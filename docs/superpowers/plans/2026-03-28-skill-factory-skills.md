# Skill Factory Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the 5 factory skills that power the skill factory: intent-author, skill-discovery, verify-platform, reconcile, and compile-review. These are Claude Code SKILL.md files invoked as `/name` commands.

**Architecture:** Each skill is a markdown SKILL.md file in `factory-skills/<name>/`. These are hand-authored (never compiled from intents). They use the existing compiler, publish, and db tooling from Plans 2-4.

**Tech Stack:** Markdown with YAML frontmatter (Claude Code skill format)

**Spec:** `~/repos/skills/docs/superpowers/specs/2026-03-25-skill-factory-design.md` (section: Factory Skills)

**Depends on:** Plans 1-4 (scaffolding + state DB + compiler + publish)

---

## File Structure

```
~/repos/skill-factory/
└── factory-skills/
    ├── intent-author/
    │   └── SKILL.md          # Interview skill — writes intent documents
    ├── skill-discovery/
    │   └── SKILL.md          # Helps decide what type of intent to create
    ├── verify-platform/
    │   └── SKILL.md          # Update platform capabilities from vendor changelog
    ├── reconcile/
    │   └── SKILL.md          # Detect drift between working dirs and published repo
    └── compile-review/
        └── SKILL.md          # Quality gate on compiled output
```

---

### Task 1: Write intent-author skill

**Files:**
- Create: `factory-skills/intent-author/SKILL.md`

This is the most complex factory skill — it interviews the user, produces two documents, gets approval, and merges into a final intent.

- [ ] **Step 1: Write the skill**

The skill must cover:

1. **Frontmatter**: name, description
2. **Purpose**: Interview user to create an intent document
3. **Arguments**: `<name>` (intent name), `--edit` (modify existing intent)
4. **Workflow** (9 steps from spec):
   - Ask about the goal
   - Write Doc 1 (Goal & Constraints) — tell user to keep visible on side screen
   - Work through constraints, inputs, outputs, error cases
   - Determine components (prompt/skill/agent sub-structures)
   - Build Doc 2 (Component Spec) — flag platform deviations as they emerge
   - Identify shared references and stack awareness
   - User approves both docs
   - Merge into `intents/<name>/intent.md` with proper frontmatter
   - Record in SQLite via `python compiler/db.py` or direct FactoryDB
5. **Doc 1 format** (from spec):
   ```markdown
   # <Name> — Goal & Constraints
   ## Goal
   ## Constraints
   ## Success Criteria
   ```
6. **Doc 2 format** (from spec):
   ```markdown
   # <Name> — Component Spec
   ## Components
   ## Shared References
   ## Platform Notes
   ## Stack Awareness
   ```
7. **Merge rules**: Doc 1 → Goal/Constraints body sections. Doc 2 → frontmatter (components, shared_refs, platform_notes, stack_aware) + per-component body sections
8. **Platform deviation detection**: Read `platforms/*/capabilities.yml` and check if each component is covered by a built-in or extension. Alert the user: "For Copilot Native, /plan covers this — emit thin wrapper or skip?"
9. **Guardrails**: Don't assume component types. Don't hardcode platform assumptions. Ask one question at a time. Flag deviations explicitly.

- [ ] **Step 2: Verify the skill loads in Claude Code format**

Check that the YAML frontmatter is valid:
```bash
cd ~/repos/skill-factory && python -c "
import frontmatter
post = frontmatter.load('factory-skills/intent-author/SKILL.md')
print(f'name: {post[\"name\"]}')
print(f'description: {post[\"description\"]}')
print('OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add factory-skills/intent-author/SKILL.md
git commit -m "feat: add intent-author factory skill"
```

---

### Task 2: Write skill-discovery skill

**Files:**
- Create: `factory-skills/skill-discovery/SKILL.md`

- [ ] **Step 1: Write the skill**

The skill must cover:

1. **Frontmatter**: name, description
2. **Purpose**: Help user decide what to build before invoking intent-author
3. **Workflow**:
   - Ask: "What problem are you running into repeatedly?" or "What workflow do you keep doing manually?"
   - Scan existing intents in `intents/` — is this already covered?
   - Read platform capabilities — does a built-in already solve this?
   - Check extensions — does superpowers or another plugin handle this?
   - If gap found: recommend intent type (workflow, standalone skill, agent) and hand off to `/intent-author`
   - If already covered: show the user where and how to use the existing solution
4. **Decision tree**: When is a new intent needed vs. modifying an existing one vs. using a built-in?
5. **Guardrails**: Don't create intents for things built-ins already handle. Don't duplicate existing intents. Always check before recommending creation.

- [ ] **Step 2: Validate frontmatter**
- [ ] **Step 3: Commit**

```bash
git add factory-skills/skill-discovery/SKILL.md
git commit -m "feat: add skill-discovery factory skill"
```

---

### Task 3: Write verify-platform skill

**Files:**
- Create: `factory-skills/verify-platform/SKILL.md`

- [ ] **Step 1: Write the skill**

The skill must cover:

1. **Frontmatter**: name, description
2. **Purpose**: Update platform capability definitions when vendors ship changes
3. **Arguments**: `<platform-name>` (claude, vscode, copilot-native)
4. **Workflow**:
   - Read current `platforms/<name>/capabilities.yml` and `last_verified` date
   - Fetch vendor changelog (URL from capabilities file) using web search or web fetch
   - Show what's new since last verification
   - Propose capability additions, changes, or deprecations
   - User approves changes
   - Update capabilities.yml: bump version, update `last_verified`, add/modify capabilities
   - Record in SQLite via FactoryDB `record_platform_check()`
   - Query SQLite: which intents were compiled against the old version?
   - Report: "N intents may need recompilation"
5. **Staleness warning**: If `last_verified` > 30 days, note urgency
6. **Guardrails**: Don't auto-update without approval. Don't remove capabilities without explicit confirmation. Always show the diff before writing.

- [ ] **Step 2: Validate frontmatter**
- [ ] **Step 3: Commit**

```bash
git add factory-skills/verify-platform/SKILL.md
git commit -m "feat: add verify-platform factory skill"
```

---

### Task 4: Write reconcile skill

**Files:**
- Create: `factory-skills/reconcile/SKILL.md`

- [ ] **Step 1: Write the skill**

The skill must cover:

1. **Frontmatter**: name, description
2. **Purpose**: Detect drift between factory working dirs and the published repo
3. **Workflow**:
   - Read publish config from `compiler/config.yml` to find published repo path
   - Run `git diff` or file comparison between `working/` and published repo's platform dirs
   - Classify drift:
     - **Outbound**: working has changes not yet published (normal — compile happened, publish hasn't)
     - **Inbound**: published repo has changes not in working (someone edited published skills directly)
   - For inbound drift, per file:
     - Show the diff
     - Identify which intent produced the file (query SQLite compilations table)
     - Options: (a) backport — user edits the intent, then recompiles; (b) discard — next publish overwrites
   - Record decisions in SQLite via `record_reconciliation()`
4. **Guardrails**: Don't auto-discard changes. Always show diffs. The backport is manual — guide the user to the right intent but don't rewrite it.

- [ ] **Step 2: Validate frontmatter**
- [ ] **Step 3: Commit**

```bash
git add factory-skills/reconcile/SKILL.md
git commit -m "feat: add reconcile factory skill"
```

---

### Task 5: Write compile-review skill

**Files:**
- Create: `factory-skills/compile-review/SKILL.md`

- [ ] **Step 1: Write the skill**

The skill must cover:

1. **Frontmatter**: name, description
2. **Purpose**: Quality gate on compiled output before publish
3. **Arguments**: `[--platform <name>]` (optional, defaults to all)
4. **Workflow** (7 checks from spec):
   - **Frontmatter validation**: Read platform rules, check all required fields present in compiled artifacts
   - **Structural compliance**: Check required sections exist (e.g., "CRITICAL: Do Not Guess" for VS Code/Copilot Native prompts)
   - **Shared reference resolution**: Check all `@skill:` or `foundations/` references point to actual files
   - **Context budget**: Check file sizes against platform `context_budget_kb` limit
   - **Diff review**: Compare against previous compilation (if available in SQLite) — flag new/deleted/large-diff files
   - **Cross-platform consistency**: Verify same intent produced output for all expected platforms
   - **Empty artifact check**: No zero-content or stub-only files
5. **Report format**: Pass/fail per platform with specific issues
6. **SQLite integration**: Record the review result. Publish.py checks for a recent passing review before allowing publish.
7. **Guardrails**: Don't auto-fix issues (report only). Don't skip any check. Always show the full report.

- [ ] **Step 2: Validate frontmatter**
- [ ] **Step 3: Commit**

```bash
git add factory-skills/compile-review/SKILL.md
git commit -m "feat: add compile-review factory skill"
```

---

### Task 6: Validate all skills and tag

- [ ] **Step 1: Validate all 5 skill frontmatters**

```bash
cd ~/repos/skill-factory
for skill in intent-author skill-discovery verify-platform reconcile compile-review; do
    python -c "
import frontmatter
post = frontmatter.load('factory-skills/$skill/SKILL.md')
print(f'  {skill}: name={post[\"name\"]}, desc={post[\"description\"][:50]}...')
" || echo "  FAIL: $skill"
done
```

All 5 should print name and description.

- [ ] **Step 2: Run full test suite to verify no regressions**

```bash
uv run pytest tests/ -v --tb=short
```

- [ ] **Step 3: Show git log**

```bash
git log --oneline
```

- [ ] **Step 4: Tag**

```bash
git tag v0.5.0-factory-skills -m "Factory skills (intent-author, skill-discovery, verify-platform, reconcile, compile-review) complete"
```
