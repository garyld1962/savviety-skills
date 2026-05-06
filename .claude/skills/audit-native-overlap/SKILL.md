---
name: audit-native-overlap
description: "Audit this repo's custom Claude Code skills for description-level overlap with native skills (superpowers, plugins, built-ins) using the current session's live skill list as the catalog. Identifies skills whose descriptions compete with natives and recommends per-skill verdicts: tighten, cross-reference, integrate as sub-primitive, hand off, or redundant. Trigger phrases: 'audit native skill overlap', 'check overlap with native skills', 'do my custom skills compete with natives', 'native skill audit', 'evaluate skills against natives'."
---

# /audit-native-overlap — Custom-vs-Native Skill Overlap Audit

**Purpose:** evaluate this repo's custom Claude Code skills against the native skill ecosystem (superpowers, plugins, built-ins) to find description-level overlaps that hurt skill triggering or could be sharpened by integration. Source-repo audit; not for project/ecosystem audits (use `/skill-audit` for that).

## When to Use

- Periodic health check on the dev repo's custom skills.
- After a major Claude Code or plugin update that introduces new natives.
- Before publishing a new custom skill, to see what it competes with.
- When a custom skill is mis-firing in tests and you suspect description overlap with a native.

## When NOT to Use

- Auditing a *consumer* project's installed plugins/skills — use `/skill-audit`.
- Creating or improving a single skill — use `/skill-creator` or `/skill-improver`.
- Structural lint (frontmatter, naming, cross-refs) — use `/validate-skills`.

## Prerequisites

Run this skill **inside Claude Code** so the current session's available-skills list is in the model context — that list IS the live native-skill catalog. The skill does not maintain a catalog file; staleness isn't possible because the list is read fresh each run.

If you are not in the savviety-skills source repo (no `manifest.json` at the cwd, no `claude/` directory), refuse with: `audit-native-overlap must run in the savviety-skills source repo.`

## Arguments

| Argument | Description |
|---|---|
| `[skill-name]` | Audit only the named custom skill. Default: all custom skills under `claude/`. |
| `--out=<path>` | Output path. Default: `docs/audits/native-overlap-<YYYYMMDD>.md`. |
| `--scope=<overlapping\|all>` | `overlapping` (default) reports only skills with at least one overlap finding; `all` includes "no overlap" verdicts. |
| `--apply` | After writing the report, draft edits to each affected SKILL.md (description tightening, cross-reference blocks, "When NOT to Use" handoffs). Disabled by default — review the report first. |

## Workflow

### Phase 1: Verify environment and enumerate custom skills

1. Confirm cwd contains `manifest.json` and `claude/`. If not, refuse (see Prerequisites).
2. Read `manifest.json` to extract `claude.skills.skip` (paths/names not to audit). Defaults if missing: `README.md`, `MODEL-POLICY.md`, `SESSION-CONTEXT.md`, `settings.template.json`, `infra`.
3. List entries under `claude/`. A custom skill is any directory `claude/<name>/` where `claude/<name>/SKILL.md` exists, EXCEPT:
   - Names in the skip list
   - The `_internal/` tree (contracts, not user-invocable — no trigger surface)
4. For each custom skill, read frontmatter (`name`, `description`) and the `## When to Use` and `## When NOT to Use` sections plus the first ~50 lines of body.
5. If `[skill-name]` was passed, restrict to that single skill.

### Phase 2: Identify the native catalog from the live session

Use the **current session's available-skills list** (visible in the system-reminder injected at session start) as the catalog. Treat as native any skill that:

- Has a plugin namespace prefix (e.g. `superpowers:`, `pr-review-toolkit:`, `claude-md-management:`, `hookify:`, `differential-review:`, `static-analysis:`, `variant-analysis:`, `codex:`, `skill-improver:`, `sourcegraph:`, `supply-chain-risk-auditor:`, `insecure-defaults:`), OR
- Has no prefix but does NOT correspond to a directory under this repo's `claude/` (e.g. built-ins like `init`, `review`, `security-review`, `simplify`, `loop`, `schedule`, `claude-api`, `update-config`).

**Do not invent natives.** If a skill isn't in the current session's listing, it's out of scope. If the listing is empty or unavailable, halt with: `Cannot read available-skills list from session — invoke this skill from inside Claude Code.`

Record the timestamp of the run. Note in the report: "native catalog read live from this session at `<timestamp>`."

### Phase 3: Compare each custom skill against the catalog

For each custom skill, identify candidate natives whose descriptions overlap on:

- **Trigger phrases** — same verbs/nouns ("execute", "plan", "review", "spec", "PRD", "requirements", "audit")
- **Outcome territory** — same kind of output (a plan, a review verdict, a refactor, a report)
- **Workflow stage** — same point in the dev flow (planning, executing, reviewing, committing, debugging)

Rank candidates by overlap strength. A custom skill may have zero, one, or several native counterparts.

### Phase 4: Verdict per overlap pair

For each `(custom skill, native)` pair with non-trivial overlap, assign exactly one verdict:

| Verdict | When | Recommended action |
|---|---|---|
| **Tighten** | Custom skill loses its own trigger surface to a native (the native is winning ambiguous user phrases) | Sharpen the custom skill's `description:` with explicit trigger phrases and a "Preferred over `<native>` when..." claim |
| **Cross-reference** | Custom is the project-tailored version of a native — same job, stricter contracts | Add a `## Relationship to native skills` block citing the native and stating when to defer |
| **Integrate as sub-primitive** | A specific seam (failure path, isolation, verification) where the custom skill could call the native | Identify the seam in the body and add the call/cross-reference at that location |
| **Hand off** | Custom is heavier than the native; some user phrasings should defer | Add the native to "When NOT to Use" with the deferring condition |
| **Redundant** | Custom duplicates a native with no value-add | Recommend deprecation/removal |

If a custom skill has no overlap candidates, verdict is **No overlap** — report only when `--scope=all`.

### Phase 5: Write the report

Write to the `--out` path (default: `docs/audits/native-overlap-<YYYYMMDD>.md`). Create the directory if missing.

Format:

```
# Native-Overlap Audit — <YYYY-MM-DD>

**Repo:** <repo-root>
**Custom skills audited:** <N>
**Overlap findings:** <M>
**Native catalog:** read live from session at <timestamp>

## Summary

| Custom skill | Findings | Top verdict |
|---|---|---|
| <name> | N | Tighten / Cross-reference / ... |

## Findings

### `<custom-skill-name>`

**Description:** <current `description:` value, verbatim>

#### Overlap with `<native-skill>`

- **Verdict:** <Tighten | Cross-reference | Integrate as sub-primitive | Hand off | Redundant>
- **Reasoning:** <2–3 sentences naming the specific overlap>
- **Recommended action:** <concrete edit, ideally with before/after snippets>

(repeat per native overlap; repeat per custom skill)

## Skills with no overlap

(only when --scope=all)

- `<name>` — <one-line note on what the skill does that natives don't>
```

### Phase 6: Apply (only if `--apply` was passed)

After the report is written, draft and apply the recommended edits to each affected `claude/<name>/SKILL.md`:

- **Description tightenings** — `Edit` the frontmatter `description:` line
- **Cross-reference blocks** — insert `## Relationship to native skills` after the intro and before `## When to Use`
- **"When NOT to Use" handoffs** — extend the existing section with the deferring condition
- **Sub-primitive integrations** — these are seam-specific; flag for human review, do NOT auto-apply

Pre-conditions for `--apply`:

1. Working tree must be clean OR already on a feature branch. If the tree has uncommitted changes on `main`, halt and ask the operator to branch or stash first.
2. After applying, do not commit. Leave changes staged for human review.
3. After applying, run `/validate-skills` (if available) to catch any structural breakage from the edits.

## Key Rules

1. **The catalog is the live session.** Do not maintain a catalog file. Do not invent natives the session can't see. If the listing isn't available, halt — do not guess.
2. **Source-repo only.** This audit is meaningful only in the savviety-skills source repo. Refuse cleanly elsewhere.
3. **Report first, edit second.** `--apply` is opt-in. Default is read-only.
4. **One verdict per overlap pair.** A custom skill overlapping three natives produces three findings, not one merged verdict.
5. **Skip `_internal/`.** Internal contracts have no triggering surface to overlap.
6. **Acknowledge model limits.** The model can miss subtle overlaps and hallucinate borderline ones. Findings are recommendations to review, not verdicts to mechanically apply. The report should treat itself as a starting point for human judgment.
7. **Don't recommend changes to native skills.** This audit only proposes edits to *this repo's* custom skills.
