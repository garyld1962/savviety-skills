---
slug: ontology-and-prd-create
source_prd: docs/handoffs/2026-09-01-ontology-prerequisites-for-prd-create.md
intent: Clean the review defects in claude/, make the requirements pipeline produce, consume, and gate on a domain ontology, and add the /prd-create interrogation skill as the single entrance for greenfield, feature, refresh, and rewrite work.
type: feature
---

# Ontology readiness and /prd-create

**Source:** docs/handoffs/2026-09-01-ontology-prerequisites-for-prd-create.md (Closed Decisions confirmed 2026-09-02) plus the 2026-09-02 review of `claude/` summarised in Context.

## Context

`/prd-create` will elicit a universe of discourse (entity types, reference schemes, fact types, constraints, lifecycle, temporality, modality) and write it somewhere downstream skills honour. Today nothing in `claude/` can receive that: `_internal/aers-readiness` has no ontology dimension, `/ubiquitous-language` is orphaned (no caller), and the pipeline's front is broken (`/goal` hands off to `/prd-validate`, which assumes an artifact already exists).

A full review of the 64 SKILL.md files under `claude/` on 2026-09-02 found the tree structurally sound (all `name:` fields match directories, no missing frontmatter) but with defects that later tasks would otherwise edit around:

- A `/plan` skill is referenced from 12 skills and does not exist. `/skill-improver` and `/new-skill` are referenced from feature-sweep and do not exist under `claude/`.
- Stale path roots (`dev/`, `claude-working/`, `claude-new/`, `copilot-native/`) survive in postmortem, process-tune, validate-plan, sync-main, code-review-professional, domain-review, configure, execute-plan tests, and a closed-decisions fragment. postmortem cites an execute-plan "Phase 5" heading that no longer exists.
- Four pipeline skills resolve "the requirements file" differently (`AERS.md`; `test_prd.md`; `prompt.md`/`docs/plans/PRD.md`; `docs/prds/`).
- aers-readiness names three different caller lists, scores 8 of its 9 ambiguity categories, and uses a finding name (`prd-not-ready`) that execute-prd does not (`requirements-incomplete`).
- execute-prd has no `## Arguments` or `## Contract`; execute-plan, spec-review-adversarial, thesis, and ubiquitous-language have no `## Contract`.
- Ten skills are absent from both `claude/README.md` and `skill-help`; MODEL-POLICY drifts from the actual `model:` pins (review-gauntlet is pinned despite the policy saying it must not be); `_internal/plan-format` lacks the mandatory `internal:`/`kind:` fields; README documents a nonexistent `execute-plan/agents/` directory.
- Smaller: prd-acceptance leaves exactly 70% undefined and claims to call `/prd-validate` but never does; integration-surface says router-only while the controller dispatches it for three layers; kickoff calls itself "Autonomous" while its Contract says interactive-by-design; goal's When-NOT-to-Use contradicts its own Step 7 handoff.

The user decided (2026-09-02): one comprehensive plan in plan-format; cleanup lands first; `/plan` references are rewritten to real targets; the PRD is the human-readable document and `AERS.md` remains the machine-translated execution-ready spec; related documents for one PRD live together in a per-PRD folder; brownfield modes read the codebase to seed the ontology.

Scope is `claude/` only. Nothing under `.claude/`, `codex/`, `copilot/`, or `kimi/` is touched (parity is the handoff's deferred Task 11). `manifest.json` copies `claude/` wholesale, so new directories need no manifest edit; the closing task asserts that.

## Closed Decisions

- Rubric/interview split: `_internal/ontology-readiness` (kind reference, not user-invocable) is the scorable rubric and `/prd-create` is the interactive remedy, mirroring `_internal/aers-readiness` and `/prd-validate`.
- Artifact layout: `docs/prds/<slug>/PRD.md` (human-readable), `AERS.md` (execution-ready translation), `ONTOLOGY.md` (semantic source of truth), `UBIQUITOUS_LANGUAGE.md` (derived view); root `AERS.md` stays a legacy location.
- Sibling artifacts resolve relative to the directory of the resolved requirements file.
- Requirements-file resolution order, used verbatim in prd-validate, prd-acceptance, execute-prd, kickoff: explicit path, then most recently modified `docs/prds/*/AERS.md`, then `./AERS.md`, then most recent `docs/prds/*/PRD.md`, then `./PRD.md`, then `./prompt.md`; ties within a tier ask (interactive) or emit `plan-ambiguity` (autonomous).
- `/execute-prd` persists fetched work items to `docs/prds/<source-slug>/PRD.md` instead of `docs/plans/PRD-<slug>.md`.
- `/plan` references become `/execute-prd` where the context is compiling a requirements source into a plan and `superpowers:writing-plans` for generic planning; `/skill-improver` and `/new-skill` become `superpowers:writing-skills`.
- The autonomous not-ready finding is named `requirements-incomplete` everywhere.
- Notation is verbalized natural-language fact types in Markdown, one relationship per statement, no OWL, RDF, or ORM diagram syntax.
- Ontology is not Data Models: the ontology describes the world, Data Models describes representation, and the rubric states this explicitly.
- Item states `settled`, `deferred` (must carry a re-entry condition), and `unknown` are defined once in `_internal/ontology-readiness` and cited everywhere else; `settled` maps to Closed Decisions and `deferred` to Open Decisions.
- Mandatory core per in-scope entity (reference scheme, homonym resolution, modality of each stated rule, temporality declaration) cannot be deferred; a deferred core item scores 2 and caps the ontology verdict at Partial.
- Ontology contribution to the composite readiness score is capped: Ready adds 0, Partial adds 2, Absent adds 4; the structural thresholds 0–2, 3–6, 7+ are unchanged and the `Domain Ontology` required section is excluded from the per-section 0/1/2 tally.
- The verdict carries a separate `Ontology: Ready / Partial / Absent` line.
- Trivial domain rule: fewer than three distinct entity types across Functional Requirements and Data Models and no state or status field means a missing ontology reports `Ontology: Absent (trivial domain)` and contributes 0.
- `ONTOLOGY.md` carries a header declaring `mode: greenfield | feature | refresh | rewrite`, `scope:`, `extends:` (feature and rewrite), `uod:`, and `seeded-from-code:`, plus an append-only Extension Log whose entries are classed `addition:` or `revision:`.
- Additions append; revisions (changed reference scheme, homonym split, tightened constraint, reclassified modality, retrofitted temporality) halt and surface, except in rewrite mode where each revision must be listed in the PRD's `What May Change` section and confirmed as a closed decision.
- `/prd-create` absorbs `prd-validate --full-spec`; the flag stays recognised for one release and prints a pointer instead of running.
- `/prd-create` writes `AERS.md` itself by applying the aers-readiness transformation and automated check at the end of the interview, and recommends `/prd-validate` only when the verdict is not Ready.
- `/prd-create` supports four modes (greenfield, feature, refresh, rewrite) and in brownfield modes seeds the ontology from the codebase via `/audit-existing`, the ubiquitous-language codebase-scan idea, and modernization-rubric project-shape detection, never inventing a new scanner.
- `/prd-create` is pinned `model: opus` and is never auto-invoked from a non-interactive context, the same boundary as `/prd-validate`.
- `/ubiquitous-language --from-ontology` writes the glossary beside the ontology it reads, and the glossary is regenerated, never hand-edited.

## Task 0: Rewrite dangling cross-references and stale path roots

```yaml
depends_on: []
write_scope:
  - claude/grill-me/SKILL.md
  - claude/ideate/SKILL.md
  - claude/bug-session/SKILL.md
  - claude/design-twice/SKILL.md
  - claude/triage/SKILL.md
  - claude/hotfix/SKILL.md
  - claude/feature-sweep/SKILL.md
  - claude/process-tune/SKILL.md
  - claude/postmortem/SKILL.md
  - claude/validate-plan/**
  - claude/code-review-professional/SKILL.md
  - claude/sync-main/SKILL.md
  - claude/_internal/closed-decisions/git/lockfile-conflicts.md
  - claude/domain-review/references/controller-guide.md
  - claude/configure/registry.md
  - claude/execute-plan/tests/**
  - claude/_internal/plan-format/SKILL.md
  - claude/_internal/dependency-classification/SKILL.md
  - claude/review-gauntlet/SKILL.md
  - claude/test-plan/analysts/integration-surface/SKILL.md
milestone_end: false
```

Files that no later task edits. Files prd-validate, kickoff, work-item, execute-prd, execute-plan/SKILL.md, and aers-readiness are fixed by Tasks 2 and 4 instead.

- `/plan` → `superpowers:writing-plans` in grill-me, ideate (description and body), design-twice (description and body); `/plan` → `/execute-prd` in triage (description and body), bug-session (description and body), hotfix, validate-plan (`/plan`-authored plans are "authored by `/execute-prd`"; "the sibling `/plan` skill" wording removed); process-tune "`/plan`-shaped" → "`_internal/plan-format`-shaped".
- feature-sweep: `/skill-improver` and `/new-skill` → `superpowers:writing-skills` (description and body).
- Stale roots: `dev/execute-plan/SKILL.md` → `claude/execute-plan/SKILL.md` (postmortem, process-tune); `dev/review-gauntlet` → `claude/review-gauntlet/SKILL.md` (code-review-professional); `dev/{sync-main,pr,ship,execute-plan}` in lockfile-conflicts.md → `/sync-main`, `/pr`, `/ship`, `/execute-plan`; `dev/closed-decisions/...` in sync-main → `_internal/closed-decisions/git/lockfile-conflicts.md`; `claude-working/...` and `<claude-working-root>` → `claude/...` and `_internal/closed-decisions/` in validate-plan SKILL.md, both test samples, and domain-review controller-guide; `claude-new/` → `claude/` in execute-plan/tests/smoke.md; configure/registry.md `copilot-native/templates/env.config.template.md` → `copilot/templates/env.config.template.md`.
- postmortem and process-tune: every "Phase 5" reference → "the `## Postmortem` section of `claude/execute-plan/SKILL.md`" (index schema → its `### Cross-run aggregation` subsection).
- plan-format: "execute-prd step 5" → "step 7", "step 7 checks it" → "step 8"; frontmatter gains `internal: true` and `kind: reference`.
- dependency-classification frontmatter `kind: reference` → `kind: embedded` (it returns a classification, the README's own embedded example). review-gauntlet: delete the `model: opus` line per MODEL-POLICY.
- integration-surface banner and Contract precondition: "only when the target layer is `router`" → "when the target layer is `service`, `router`, or `component`; not selected for `schema`".

**Acceptance:** all of the following shell checks exit 0.
- `! rg -q --pcre2 '(?<![\w/-])/plan(?![\w-])' claude --glob '!claude/prd-validate/**' --glob '!claude/kickoff/**' --glob '!claude/work-item/**' --glob '!claude/_internal/aers-readiness/**' --glob '!claude/execute-plan/SKILL.md' --glob '!claude/execute-prd/**'`
- `! rg -q '/skill-improver|/new-skill' claude/feature-sweep/SKILL.md`
- `! rg -q 'dev/(execute-plan|review-gauntlet|closed-decisions|sync-main|pr|ship)|claude-working|claude-new|copilot-native/' claude`
- `! rg -q 'Phase 5' claude/postmortem/SKILL.md claude/process-tune/SKILL.md && rg -q 'claude/execute-plan/SKILL.md' claude/postmortem/SKILL.md`
- `rg -q 'execute-prd step 7' claude/_internal/plan-format/SKILL.md && rg -q 'execute-prd step 8' claude/_internal/plan-format/SKILL.md`
- `rg -q '^internal: true' claude/_internal/plan-format/SKILL.md && rg -q '^kind: reference' claude/_internal/plan-format/SKILL.md`
- `rg -q '^kind: embedded' claude/_internal/dependency-classification/SKILL.md`
- `! rg -q '^model:' claude/review-gauntlet/SKILL.md`
- `rg -q 'service.*router.*component' claude/test-plan/analysts/integration-surface/SKILL.md && ! rg -q 'only when the target layer is .router.' claude/test-plan/analysts/integration-surface/SKILL.md`
- `rg -q 'copilot/templates/env.config.template.md' claude/configure/registry.md`
- `find claude -name "*.mjs" -print0 | xargs -0 bin/check-workflow-syntax`

## Task 1: Repair the skill indexes and model policy

```yaml
depends_on: []
write_scope:
  - claude/README.md
  - claude/skill-help/SKILL.md
  - claude/MODEL-POLICY.md
  - claude/CLAUDE.md
milestone_end: false
```

- README catalog tables: add bug-session, design-twice, drawio, feature-sweep, gh-readiness, goal, issue-slices, modernize, refactor-brief, vault under the category each fits (goal, design-twice, refactor-brief → Requirements, Design & BA; the rest by purpose). Reword the kickoff row to "Interactive readiness → plan → implement → review".
- README structure section: execute-plan tree → `SKILL.md`, `workflows/run-plan.mjs`, `tests/` (remove `agents/implementer.md` etc.); list all 11 `_internal` skills plus the `closed-decisions/` fragment store; `review-tests` attribution → "external skill (not shipped from this repo)"; `install-scan` lives at `claude/install-scan/` (fix README and `claude/CLAUDE.md`).
- skill-help category table: add the same 10 skills; drop `(rubric: aers-readiness)` from the Specs & Requirements row (contradicts the no-`_internal` rule in the same file).
- MODEL-POLICY: add design-twice, feature-sweep, goal to the opus list; review-gauntlet remains in the unpinned list (Task 0 removed the file pin). Leave prd-create and ontology entries to Task 13.

**Acceptance:** all of the following shell checks exit 0.
- `for s in bug-session design-twice drawio feature-sweep gh-readiness goal issue-slices modernize refactor-brief vault; do rg -q "/$s" claude/README.md && rg -q "\b$s\b" claude/skill-help/SKILL.md || exit 1; done`
- `! rg -q 'aers-readiness' claude/skill-help/SKILL.md`
- `! rg -q 'implementer.md' claude/README.md && rg -q 'run-plan.mjs' claude/README.md`
- `for s in aers-readiness decision-record dependency-classification diff-manifest disposition modernization-rubric plan-format pre-flight-check professional-rubric repo-delivery security-quick-check; do rg -q "$s" claude/README.md || exit 1; done`
- `! rg -q 'review-tests.*superpowers' claude/README.md`
- `! rg -q 'infra/.*install-scan' claude/CLAUDE.md claude/README.md`
- `for f in $(rg -l '^model: opus' claude --glob 'SKILL.md'); do s=$(basename $(dirname $f)); rg -q "^- .$s.\$" claude/MODEL-POLICY.md || exit 1; done`

## Task 2: Unify requirements-artifact resolution and add missing pipeline contracts

```yaml
depends_on: []
write_scope:
  - claude/execute-prd/SKILL.md
  - claude/execute-plan/SKILL.md
  - claude/prd-validate/SKILL.md
  - claude/prd-acceptance/SKILL.md
  - claude/kickoff/SKILL.md
  - claude/work-item/SKILL.md
milestone_end: true
```

- Write the canonical resolution order (Closed Decisions) verbatim into prd-validate `## Arguments`, prd-acceptance Step 1, execute-prd step 2, and kickoff `## Arguments` plus step 1. Add the sibling-artifact rule (`ONTOLOGY.md`, `UBIQUITOUS_LANGUAGE.md`, `PRD.md` resolve relative to the chosen file's directory) so the ontology tasks can cite it.
- execute-prd: add `## Arguments` (`<path>`, `--ado <id>`, `--linear <id>`, `--type`, pass-through flags to `/execute-plan`) and `## Contract` (Inputs, Preconditions, Outputs, Postconditions, Failure modes naming `plan-ambiguity` and `requirements-incomplete`). Work-item persistence path → `docs/prds/<source-slug>/PRD.md`. work-item: `/plan` → `/execute-prd`; path examples updated.
- execute-plan: add `## Contract`; the taxonomy row "drives `/plan` and `/execute-prd` step 5" → "drives `/execute-prd` step 7".
- prd-validate: `/plan` → `/execute-prd` (When NOT to Use, Step 5 next step, Contract); Outputs: a non-file start writes `docs/prds/<slug>/AERS.md`.
- prd-acceptance: remove `test_prd.md`; Result Logic → PASS when all pass, PARTIAL when ≥70% pass, FAIL when <70% pass; Contract "Calls `/prd-validate`" → "does not call `/prd-validate`; an artifact with no acceptance criteria halts with `no-acceptance-criteria` and suggests `/prd-validate`"; `**Arguments:**` becomes a `## Arguments` heading.
- kickoff: title `# /kickoff — Interactive Development Start`; description reworded (operator-supervised; unattended → `/execute-prd`); `/plan` → `superpowers:writing-plans`.

**Acceptance:** all of the following shell checks exit 0.
- `for f in claude/prd-validate/SKILL.md claude/prd-acceptance/SKILL.md claude/execute-prd/SKILL.md claude/kickoff/SKILL.md; do rg -q 'docs/prds/\*/AERS\.md' "$f" || exit 1; done`
- `! rg -q 'test_prd' claude/prd-acceptance/SKILL.md && ! rg -q 'docs/plans/PRD-' claude/execute-prd/SKILL.md claude/work-item/SKILL.md`
- `rg -q '^## Arguments' claude/execute-prd/SKILL.md && rg -q '^## Contract' claude/execute-prd/SKILL.md && rg -q '^## Contract' claude/execute-plan/SKILL.md && rg -q '^## Arguments' claude/prd-acceptance/SKILL.md`
- `rg -q '≥70%' claude/prd-acceptance/SKILL.md && rg -q '<70%' claude/prd-acceptance/SKILL.md && ! rg -q 'Calls ./prd-validate.' claude/prd-acceptance/SKILL.md`
- `rg -q '^# /kickoff — Interactive Development Start' claude/kickoff/SKILL.md && ! rg -qi 'autonomous development start|autonomously ship' claude/kickoff/SKILL.md`
- `! rg -q --pcre2 '(?<![\w/-])/plan(?![\w-])' claude/prd-validate/SKILL.md claude/kickoff/SKILL.md claude/execute-plan/SKILL.md claude/work-item/SKILL.md claude/execute-prd/SKILL.md`
- `rg -q 'execute-prd. step 7' claude/execute-plan/SKILL.md`

## Task 3: Author `_internal/ontology-readiness`

```yaml
depends_on: [0, 1, 2]
write_scope:
  - claude/_internal/ontology-readiness/**
milestone_end: false
```

New reference rubric. Frontmatter per `claude/_internal/README.md`: `name`, quoted `description` naming consumers and ending "Not user-invokable.", `user-invocable: false`, `internal: true`, `kind: reference`, no `model:`.

- Sections: When to Use / When NOT to Use; Relationship to Other Skills (composes into `_internal/aers-readiness`; `/prd-create` is the interactive remedy; `/prd-validate` runs the closure pass; `/ubiquitous-language --from-ontology` derives the glossary; `/prd-acceptance` and `/test-plan` consume constraints); Interaction Rules copied in spirit from aers-readiness (one question at a time, propose a default, challenge ambiguity).
- Elicitation categories table with the handoff's eight rows (UoD boundary, entity types + reference schemes, fact types, constraints, lifecycle totality, temporality, modality, homonyms/synonyms) and the ontology-versus-Data-Models statement.
- `### Item states`: the single definition of `settled`, `deferred` (with re-entry condition, licensed by the UoD boundary), `unknown`, mapped to AERS Closed/Open Decisions.
- `## Completeness and Extension`: the handoff's Rules 1–4 verbatim, the mandatory-core table, the hard-failure rule for deferred core items, the five revision kinds, and how `extends:` drives a delta interview.
- `## ONTOLOGY.md format`: header (`mode: greenfield | feature | refresh | rewrite`, `scope:`, `extends:`, `uod:`, `seeded-from-code:`, status summary); location `docs/prds/<slug>/ONTOLOGY.md`; sections Entity Types (reference scheme, homonym resolution, status, source), Fact Types (verbalized, constraints or `[unconstrained]`, modality, status, source), Lifecycles (transition table, terminal marks, totality flag), Temporality, Deferred (with re-entry condition), Unknown, Extension Log (`addition:` / `revision:`).
- `## Automated ontology check`: per-category 0/1/2 (deferred with condition scores 0, unknown scores 2, deferred core item scores 2 and caps at Partial); seven ambiguity categories at 2 each; mode-aware scoring (feature and rewrite score the delta and flag `revision:` entries); trivial-domain rule; verdict `Ontology: Ready 0–2 / Partial 3–6 / Absent 7+ or file missing`; literal line `Composite contribution: Ready → 0, Partial → +2, Absent → +4 (cap 4)`.
- `## Worked example`: a deliberately partial ontology (core settled, six deferred items with re-entry conditions) with its computed score showing `Ontology: Ready`. `## Contract` block.

**Acceptance:** all of the following shell checks exit 0.
- `f=claude/_internal/ontology-readiness/SKILL.md; test -f $f && rg -q '^name: ontology-readiness' $f && rg -q '^user-invocable: false' $f && rg -q '^internal: true' $f && rg -q '^kind: reference' $f && ! rg -q '^model:' $f`
- `test "$(rg -c '^### Item states' claude/_internal/ontology-readiness/SKILL.md)" = 1`
- `for k in 'UoD boundary' 'Reference scheme' 'Fact type' 'Constraint' 'Lifecycle' 'Temporality' 'Modality' 'Homonym' 'mandatory core' 're-entry condition'; do rg -qi "$k" claude/_internal/ontology-readiness/SKILL.md || exit 1; done`
- `rg -q 'mode: greenfield \| feature \| refresh \| rewrite' claude/_internal/ontology-readiness/SKILL.md && rg -q '^extends:' claude/_internal/ontology-readiness/SKILL.md && rg -q '^seeded-from-code:' claude/_internal/ontology-readiness/SKILL.md`
- `rg -q 'Ontology: Ready / Partial / Absent' claude/_internal/ontology-readiness/SKILL.md && rg -qF 'Ready → 0, Partial → +2, Absent → +4' claude/_internal/ontology-readiness/SKILL.md`
- `rg -q 'trivial domain' claude/_internal/ontology-readiness/SKILL.md && rg -q 'Extension Log' claude/_internal/ontology-readiness/SKILL.md && rg -q '^## Contract' claude/_internal/ontology-readiness/SKILL.md && rg -q '^## Worked example' claude/_internal/ontology-readiness/SKILL.md`
- `rg -q 'docs/prds/<slug>/ONTOLOGY.md' claude/_internal/ontology-readiness/SKILL.md`
- Hand-applying the check to `docs/prds/2026-08-11-local-first-agent-runner.md` (no `ONTOLOGY.md`, ≥3 entity types) yields the line `Ontology: Absent`; applying it to `docs/superpowers/specs/2026-07-07-execute-plan-runtime-fixes.md` yields the line `Ontology: Absent (trivial domain)`; both lines recorded in the task completion note.

## Task 4: Extend `_internal/aers-readiness` with the ontology dimension

```yaml
depends_on: [3]
write_scope:
  - claude/_internal/aers-readiness/SKILL.md
milestone_end: true
```

- Required Sections gains `Domain Ontology` (points at the sibling `ONTOLOGY.md` or inlines fact types for a small domain), explicitly excluded from the per-section tally. Data Models gains the ontology-versus-representation sentence. The *Domain and workflow* bullets become a pointer to the rubric's elicitation categories so they are defined once.
- *Prioritize Ambiguity by Risk* gains the seven semantic categories (cited, not redefined). The scored list gains "unclear workflow/business rules" so both structural lists have nine entries.
- Automated readiness check: composite = structural points + ontology contribution per `_internal/ontology-readiness` (Ready 0, Partial +2, Absent +4); thresholds unchanged; the Readiness Assessment template and verdict table gain the `Ontology:` line and a place for the numeric score.
- Folded fixes: `prd-not-ready` → `requirements-incomplete`; the three caller lists (description, When to Use, Contract) unified to `/prd-validate`, `/kickoff`, `/execute-prd`, `/spec-review-adversarial`; the `/plan` mention dropped; Entry Modes "Blank start" and When NOT to Use "drafting from scratch" redirect to `/prd-create`.

**Acceptance:** all of the following shell checks exit 0.
- `f=claude/_internal/aers-readiness/SKILL.md; rg -q 'Domain Ontology' $f && rg -q 'ontology-readiness' $f && rg -q 'Ontology: Ready / Partial / Absent' $f && rg -qF 'Absent → +4' $f`
- `test "$(rg -c 'unclear workflow/business rules' claude/_internal/aers-readiness/SKILL.md)" = 2`
- `rg -q 'requirements-incomplete' claude/_internal/aers-readiness/SKILL.md && ! rg -q 'prd-not-ready' claude/_internal/aers-readiness/SKILL.md`
- `! rg -q --pcre2 '(?<![\w/-])/plan(?![\w-])' claude/_internal/aers-readiness/SKILL.md && rg -q '/prd-create' claude/_internal/aers-readiness/SKILL.md`
- `! rg -q '^#+ Item states' claude/_internal/aers-readiness/SKILL.md`
- Re-score `docs/superpowers/specs/2026-07-07-execute-plan-runtime-fixes.md` and `docs/prds/2026-08-11-local-first-agent-runner.md` under the pre-task and post-task rules: structural points are identical before and after for both; composite delta is exactly 0 for the first (trivial domain) and exactly +4 for the second; neither verdict moves more than one band; the four totals are recorded in the task completion note.

## Task 5: Rework `/ubiquitous-language` from extractive to derivable

```yaml
depends_on: [3]
write_scope:
  - claude/ubiquitous-language/**
milestone_end: false
```

- Add `--from-ontology [path]` (default: the sibling `ONTOLOGY.md` of the resolved requirements artifact). Output `UBIQUITOUS_LANGUAGE.md` beside the ontology. Definitions come from entity types; Relationships are generated from fact types with real cardinality; Flagged ambiguities come from the rubric's homonym/synonym findings.
- Retitle the workflow so the derived path is the default reading; keep conversation scanning as "Legacy: extract from conversation".
- Rules: when `ONTOLOGY.md` exists it wins; the glossary is regenerated, never hand-edited; `--update` refuses when an ontology exists and points at `--from-ontology`.
- Add `## Contract` (failure mode: ontology term without a definition → report, do not invent). Update the description to mention ontology derivation.
- Add fixtures `tests/ontology-sample.md` (a hand-written ontology in the Task 3 format) and `tests/expected-glossary.md` for the harness smoke test.

**Acceptance:** all of the following shell checks exit 0.
- `f=claude/ubiquitous-language/SKILL.md; rg -q -- '--from-ontology' $f && rg -q 'ONTOLOGY.md' $f && rg -q 'ontology-readiness' $f && rg -q '^## Contract' $f`
- `rg -qi 'never hand-edited' claude/ubiquitous-language/SKILL.md && rg -q 'docs/prds/' claude/ubiquitous-language/SKILL.md`
- `test -f claude/ubiquitous-language/tests/ontology-sample.md && test -f claude/ubiquitous-language/tests/expected-glossary.md`
- `diff <(rg -oP '^\| \*\*\K[^*]+' claude/ubiquitous-language/tests/ontology-sample.md | sort -u) <(rg -oP '^\| \*\*\K[^*]+' claude/ubiquitous-language/tests/expected-glossary.md | sort -u)`

## Task 6: Embed the ontology rubric in `/prd-validate`

```yaml
depends_on: [2, 3, 4]
write_scope:
  - claude/prd-validate/SKILL.md
milestone_end: false
```

- Rubric section cites both `_internal/aers-readiness` and `_internal/ontology-readiness`. Step 2 snapshot adds an `Ontology:` line; Step 2.5 ranks semantic gaps alongside structural ones (an undefined load-bearing term outranks a missing Tooling Assumptions section).
- New `### Step 3.5: Closure Pass`, run after Step 4 drafting: every noun and verb in Functional Requirements resolves to an ontology term; every fact type has a constraint or `[unconstrained]`; every state has an exit or is terminal; no homonym survives; every "shall" is alethic or deontic.
- Step 5 verdict adds the `Ontology:` line. `--extend` awareness: when `ONTOLOGY.md` declares `mode: feature` or `rewrite`, validate against `scope:` and do not report `deferred` items as gaps.
- Deprecate `--full-spec`: recognised, prints a pointer to `/prd-create`, does not run; the Full spec mode body becomes the deprecation note; When to Use / When NOT to Use no longer advertise a blank start.
- Contract: both rubrics embedded; `ONTOLOGY.md` may be written to the artifact's directory; failure mode "ontology absent on a non-trivial domain → report, do not fabricate".

**Acceptance:** all of the following shell checks exit 0.
- `f=claude/prd-validate/SKILL.md; rg -q '^### Step 3.5' $f && rg -q 'ontology-readiness' $f && rg -q 'Ontology:' $f && rg -q -- '--extend' $f`
- `rg -q -- '--full-spec' claude/prd-validate/SKILL.md && rg -qi 'deprecated' claude/prd-validate/SKILL.md && rg -q '/prd-create' claude/prd-validate/SKILL.md && ! rg -q 'building a complete AERS through batched interview' claude/prd-validate/SKILL.md`
- `for k in 'alethic' 'terminal' 'homonym' 'unconstrained' 'do not fabricate'; do rg -qi "$k" claude/prd-validate/SKILL.md || exit 1; done`
- `rg -q 'docs/prds/\*/AERS\.md' claude/prd-validate/SKILL.md`

## Task 7: Add a semantic lens to `/spec-review-adversarial`

```yaml
depends_on: [3]
write_scope:
  - claude/spec-review-adversarial/**
milestone_end: false
```

- New `### Semantic Lens` driven by the rubric's seven ambiguity categories (homonym, synonym, unstated cardinality, non-total state machine, modality conflation, missing reference scheme, unstated temporality); finding format `[ONTOLOGY-<N>]`; phase table marks Semantic for Analysis and Specification.
- Promote the existing *Assumed context* and *Undefined terms* bullets to pointers at the Semantic lens.
- `--ontology <path>` optional argument (default: sibling `ONTOLOGY.md`); when present, check the spec against it instead of inferring vocabulary.
- Coherence lens: when the deliverable is a PRD or AERS, check the `_internal/aers-readiness` Required Sections (makes the rubric's caller list true).
- Add `## Contract`.

**Acceptance:** all of the following shell checks exit 0.
- `f=claude/spec-review-adversarial/SKILL.md; rg -q '^### Semantic Lens' $f && rg -q 'ONTOLOGY-<N>' $f && rg -q 'ontology-readiness' $f && rg -q 'aers-readiness' $f`
- `rg -q '^## Contract' claude/spec-review-adversarial/SKILL.md && rg -q -- '--ontology' claude/spec-review-adversarial/SKILL.md`

## Task 8: Verify ontology invariants in `/prd-acceptance`

```yaml
depends_on: [2, 3]
write_scope:
  - claude/prd-acceptance/SKILL.md
milestone_end: false
```

- New Step 2.5 "Extract Ontology Constraints": load the sibling `ONTOLOGY.md`; only `settled` constraints become items `OC-01..`; `deferred` items are listed SKIPPED with their re-entry condition; a missing file skips the step with a note.
- Mapping table: uniqueness → duplicate-insert test; mandatory role → null-rejection test; total state machine → exhaustive transition test; value domain → boundary test; alethic rule → schema or type-level check; deontic rule → validation or alert check.
- Step 4 gains "Phase 3b: Ontology constraints"; the summary table gains an `Ontology` row; report and response carry `OC-` results in the same pass/fail-with-evidence format. Contract cites `_internal/ontology-readiness`.

**Acceptance:** all of the following shell checks exit 0.
- `f=claude/prd-acceptance/SKILL.md; rg -q 'OC-01' $f && rg -q 'ONTOLOGY.md' $f && rg -q 'ontology-readiness' $f && rg -q '\| Ontology \|' $f`
- `rg -qi 'duplicate-insert|duplicate insert' claude/prd-acceptance/SKILL.md && rg -qi 'null-rejection|null rejection' claude/prd-acceptance/SKILL.md && rg -q 'deferred' claude/prd-acceptance/SKILL.md`

## Task 9: Feed the ontology into `/test-plan` analysts

```yaml
depends_on: [0, 3]
write_scope:
  - claude/test-plan/SKILL.md
  - claude/test-plan/analysts/boundary-validation/SKILL.md
  - claude/test-plan/analysts/state-lifecycle/SKILL.md
  - claude/test-plan/analysts/contract-compliance/SKILL.md
  - claude/test-plan/analysts/integration-surface/SKILL.md
milestone_end: false
```

- Controller: `--ontology <path>` (default: sibling of the requirements artifact, else most recent `docs/prds/*/ONTOLOGY.md`); State 2 reads it first; slicing table (value domains → boundary-validation; lifecycle → state-lifecycle; uniqueness, mandatory roles, arity → contract-compliance; edge-crossing fact types → integration-surface); State 4 passes each analyst its slice; the State 3 state-lifecycle exception also triggers when the ontology declares a lifecycle for the entity.
- Each analyst: Contract Inputs gains "ontology slice (optional)"; a "Derive from ontology" subsection states specs are derived from constraints when the slice exists and re-derived from prose only when it does not; state-lifecycle emits a P1 spec for any non-total lifecycle. Controller Contract cites `_internal/ontology-readiness`.

**Acceptance:** all of the following shell checks exit 0.
- `rg -q 'ONTOLOGY.md' claude/test-plan/SKILL.md && rg -q -- '--ontology' claude/test-plan/SKILL.md && rg -q 'ontology-readiness' claude/test-plan/SKILL.md`
- `for a in boundary-validation state-lifecycle contract-compliance integration-surface; do rg -qi 'ontology' claude/test-plan/analysts/$a/SKILL.md || exit 1; done`
- `rg -qi 'non-total' claude/test-plan/analysts/state-lifecycle/SKILL.md`

## Task 10: Rewire the readiness gates for the ontology verdict

```yaml
depends_on: [2, 4]
write_scope:
  - claude/kickoff/SKILL.md
  - claude/execute-prd/SKILL.md
  - claude/execute-plan/SKILL.md
milestone_end: false
```

- kickoff step 2 and execute-prd step 4: compute the composite per `_internal/aers-readiness` (ontology contribution included) and report both the structural verdict and the `Ontology:` line.
- Behaviour: `Ontology: Absent` on a non-trivial domain logs a known risk and proceeds; `Absent` plus structural `Partially ready` halts with `requirements-incomplete`; never auto-invoke `/prd-create` (same boundary as `/prd-validate`).
- Reopened-decision halt extended: an ontology revision (the five kinds) halts with `ontology-revision`; additions pass. Stated in kickoff and execute-prd Failure modes and in execute-plan preflight (a plan contradicting an `ONTOLOGY.md` entry without a matching `revision:` log entry).
- execute-plan: recommendation taxonomy gains an `ontology-readiness` row; the requirements-fit postmortem lens mentions ontology items the source missed. All three Contracts name `_internal/ontology-readiness`. `/postmortem` needs no edit (its only aers-readiness mention is an example string); record that in the task note.

**Acceptance:** all of the following shell checks exit 0.
- `for f in kickoff execute-prd execute-plan; do rg -q 'ontology-readiness' claude/$f/SKILL.md && rg -q 'ontology-revision' claude/$f/SKILL.md || exit 1; done`
- `rg -q 'Ontology:' claude/kickoff/SKILL.md && rg -q 'Ontology:' claude/execute-prd/SKILL.md && rg -q 'Absent' claude/execute-prd/SKILL.md`
- `rg -q 'auto-invoke ./prd-create.' claude/kickoff/SKILL.md && rg -q 'auto-invoke ./prd-create.' claude/execute-prd/SKILL.md`
- `rg -q '\| .ontology-readiness. \|' claude/execute-plan/SKILL.md`
- `! rg -q 'ontology' claude/postmortem/SKILL.md`

## Task 11: Point the front of the pipeline at `/prd-create`

```yaml
depends_on: [3]
write_scope:
  - claude/goal/SKILL.md
  - claude/thesis/SKILL.md
milestone_end: false
```

- goal: "requirements already written → `/prd-validate`" stays; "goal clear, ready to write requirements → `/prd-create`"; Step 7 handoff lists `/prd-create` first and `/prd-validate` only for an existing artifact; CRITICAL "Do NOT write requirements — that belongs in `/prd-create`"; the description's When NOT to Use updated the same way.
- thesis: one line in the Output section stating the thesis sentence is the UoD boundary test used by `_internal/ontology-readiness` (it is what lets you say "that entity isn't in this world"); add `## Contract`.

**Acceptance:** all of the following shell checks exit 0.
- `rg -q '/prd-create' claude/goal/SKILL.md && ! rg -q 'skip to ./prd-validate.' claude/goal/SKILL.md && ! rg -q 'that belongs in ./prd-validate.' claude/goal/SKILL.md`
- `rg -q '^## Contract' claude/thesis/SKILL.md && rg -q 'ontology-readiness' claude/thesis/SKILL.md && rg -qi 'universe of discourse|UoD' claude/thesis/SKILL.md`

## Task 12: Author the `/prd-create` interrogation skill

```yaml
depends_on: [4, 5, 6, 10, 11]
write_scope:
  - claude/prd-create/**
milestone_end: true
```

Layout: `claude/prd-create/SKILL.md` (target ≤ 400 lines) plus `references/codebase-seed.md` (code-signal → ontology-category table) and `references/prd-template.md` (PRD.md skeleton with per-mode conditional sections). The `ONTOLOGY.md` format is owned by the Task 3 rubric and cited, not duplicated.

- Frontmatter: `name: prd-create`; quoted description under 200 chars that contains "create a PRD", names the four modes, and defers existing artifacts to `/prd-validate`; `model: opus` last.
- Header `# /prd-create — PRD, Ontology and AERS Authoring Interview`, `**Purpose:**`, `## When to Use`, `## When NOT to Use` (existing artifact → `/prd-validate`; goal unclear → `/goal`; scope wobbly → `/thesis`; refactor with no behaviour change → `/modernize`; tickets → `/issue-slices`; build → `/execute-prd`).
- `## Arguments` (bullet convention): `<description>`; `--mode greenfield|feature|refresh|rewrite` (auto-detected and confirmed with one question unless given); `--extend <ONTOLOGY.md>` (implies feature; default proposed when exactly one `docs/prds/*/ONTOLOGY.md` exists); `--from <file>` (goal statement, thesis artifact, or notes, classified by content); `--out <dir>` (default `docs/prds/<slug>/`; never overwrite without showing the diff); `--no-scan` (refused in refresh, and in rewrite without `--extend`; recorded in headers); `--dry-run` (Steps 0–1 only, writes nothing); `--full-spec` (legacy alias: blank start with batched requirements pass).
- `## Input Modes`: blank start (aers-readiness prompt verbatim, then one question at a time; batched only under `--full-spec`, and never in the ontology interview); from `/goal` or `/thesis` output (classification table: goal lines → Problem Summary and Scope; thesis → UoD boundary test and cut list; neither → notes treated as an existing artifact); existing notes or brownfield repo.
- `## Workflow` with `### Step 0` to `### Step 9`:
  - Step 0 Preflight: interactive check (refuse otherwise, pointing at both rubrics); mode detection table (greenfield when no project shape and no `--extend`; rewrite on rewrite verbs; refresh on modernize triggers; feature as the brownfield default) with one confirmation question and the refresh-versus-rewrite tie-break "may the public API or stack change?"; refresh with no behaviour change → offer `/modernize`; locate the ontology for `--extend` and halt if it has no `uod:` header; resolve slug and `--out`; extended-thinking gate producing a per-entity question budget (four mandatory-core plus at most two discretionary before offering deferral).
  - Step 1 Codebase seed (brownfield only): compose `/audit-existing` (Existing State → Repo Starting State, Tooling Assumptions, Execution Preflight; Duplicated Or Divergent Contracts → homonym candidates; Missing Or Partial → Current State), the ubiquitous-language codebase-scan idea via `references/codebase-seed.md` (models and exported domain types → entities; PK and unique indexes → reference schemes; FKs and relations → fact types with cardinality; status enums plus transition code → lifecycles with totality check; NOT NULL and check constraints → alethic candidates; validators and guards → deontic candidates; timestamps, history tables, soft delete → temporality; same name in two packages → homonym), and for refresh the modernization-rubric §1 shape detection with its §3 sampling guardrail. Every seeded item enters as `unknown` with a `code:<file:line>` source; nothing is written `settled` without a human answer. The seed proposal is the last thing printed under `--dry-run`.
  - Step 2 UoD boundary and thesis anchoring: use or elicit one thesis sentence (offer `/thesis`, do not run it inline); propose representable versus not-representable lists; distinguish UoD from Scope using the rubric's wording; brownfield entities outside this release's ask are proposed as out of UoD, which licenses deferring their fact types.
  - Step 3 Ontology interview in rubric order (entities and reference schemes → homonyms and synonyms → fact types → constraints → modality → lifecycle totality → temporality), mandatory core first per entity; explore-before-asking with evidence; refuse mandatory-core deferral; deferral requires a re-entry condition or becomes `unknown`; one elementary predicate per fact type; every fact type constrained or `[unconstrained]`; every rule alethic or deontic; under `--extend` interview only new entities plus touched deferrals, classify addition versus revision, and halt on revision listing the stale downstream artifacts (rewrite mode: revision allowed only when listed in `What May Change` and confirmed).
  - Step 4 Requirements interview in aers-readiness risk order after a second extended-thinking gate; stack and tooling answered from the audit, never asked; Functional Requirements as `FR-n` with bold ontology terms and modality tags; closure check sends unresolved terms back to Step 3 as additions; acceptance criteria as `- [ ]` checkboxes carrying load-bearing ontology constraints.
  - Step 5 Write `PRD.md` from `references/prd-template.md`: header (title, date, status, owner, Mode, thesis, links to the three siblings), Summary, Problem and Outcome, Thesis and UoD Boundary, Users and Actors, Scope, Current State → Target State (brownfield only, delta table with change class), Functional Requirements, Non-functional Requirements, Acceptance Criteria, Closed and Open Decisions (product-level), Risks and Assumptions, Non-goals, What May Change (rewrite only). State that PRD content flows to AERS, never the reverse.
  - Step 6 Write `ONTOLOGY.md` in the rubric's format with the header fields and status summary; mandatory-core rows can only be `settled`.
  - Step 7 Translate to `AERS.md`: map PRD sections to the 13 Required Sections plus `Domain Ontology`; generate Public API, Data Models (citing the ontology as source), Verification Matrix, Repo Starting State, Tooling Assumptions, Execution Preflight, Definition of Done; compute structural score plus capped ontology contribution; write the Readiness Assessment with both lines.
  - Step 8 Derived glossary: invoke `/ubiquitous-language --from-ontology <out>/ONTOLOGY.md`; never hand-write it.
  - Step 9 Report: folder path, four files, mode, seeded-from-code, `Readiness:` with points, `Ontology:` with settled/deferred/unknown counts, blocking gaps, next step (`/prd-validate` if not Ready or unknown rows remain; `/execute-prd` if Ready; `/issue-slices` for tickets).
- `## Per-mode differences` table with the row header `| Aspect | greenfield | feature | refresh | rewrite |` covering seed, baseline ontology, change classification, PRD-specific sections, AERS Repo Starting State, `--no-scan`, Extension Log.
- `## Rules`, `## CRITICAL: Do Not` (no fabricated facts; never non-interactive or auto-invoked; never defer mandatory core or accept deferral without a re-entry condition; never hand-edit the glossary; never write a revised ontology on a revision finding; never overwrite a folder without a diff; never drift into `/execute-prd` or `/modernize` work; never batch outside `--full-spec`; never mark Ready with a missing core row or unresolved high-risk ambiguity), and `## Contract` with the five lines.

**Acceptance:** all of the following shell checks exit 0.
- `test -f claude/prd-create/SKILL.md && test -f claude/prd-create/references/codebase-seed.md && test -f claude/prd-create/references/prd-template.md`
- `f=claude/prd-create/SKILL.md; head -1 $f | rg -qx -- '---' && rg -q '^name: prd-create$' $f && rg -q '^model: opus$' $f && rg -q '^description: ".*"$' $f && rg -qi 'create a PRD' $f`
- `awk -F'"' '/^description:/{exit (length($2) < 200) ? 0 : 1}' claude/prd-create/SKILL.md`
- `for h in '## When NOT to Use' '## Arguments' '## Input Modes' '## Workflow' '## Per-mode differences' '## Rules' '## CRITICAL: Do Not' '## Contract'; do rg -q "^$h" claude/prd-create/SKILL.md || exit 1; done`
- `for s in 0 1 2 3 4 5 6 7 8 9; do rg -q "^### Step $s" claude/prd-create/SKILL.md || exit 1; done`
- `for k in '--mode greenfield|feature|refresh|rewrite' '--extend <' '--from <' '--out <' '--no-scan' '--dry-run' '--full-spec'; do rg -qF -- "$k" claude/prd-create/SKILL.md || exit 1; done`
- `for k in '_internal/ontology-readiness' '_internal/aers-readiness' '_internal/modernization-rubric' '/audit-existing' '--from-ontology' 'docs/prds/<slug>/' 'PRD.md' 'AERS.md' 'ONTOLOGY.md' 'UBIQUITOUS_LANGUAGE.md' 'references/codebase-seed.md' 'references/prd-template.md'; do rg -qF -- "$k" claude/prd-create/SKILL.md || exit 1; done`
- `for k in 'mandatory core' 're-entry condition' 'settled' 'deferred' 'unknown' 'addition' 'revision' 'halt' 'non-interactive' 'What May Change'; do rg -qi -- "$k" claude/prd-create/SKILL.md || exit 1; done`
- `rg -qF '| Aspect | greenfield | feature | refresh | rewrite |' claude/prd-create/SKILL.md`
- `test "$(wc -l < claude/prd-create/SKILL.md)" -le 400`
- `rg -q 'What May Change' claude/prd-create/references/prd-template.md && rg -q 'Current State' claude/prd-create/references/prd-template.md`
- `for k in 'reference scheme' 'fact type' 'lifecycle' 'alethic' 'deontic' 'temporality' 'homonym'; do rg -qi "$k" claude/prd-create/references/codebase-seed.md || exit 1; done`
- `test -d claude/prd-create && test -f claude/prd-create/SKILL.md && ! ls claude/prd-create | rg -qv '^(SKILL.md|references)$'`

## Task 13: Index, policy, front-door handoffs, and installer confirmation

```yaml
depends_on: [1, 7, 8, 9, 12]
write_scope:
  - claude/README.md
  - claude/_internal/README.md
  - claude/skill-help/SKILL.md
  - claude/CLAUDE.md
  - claude/MODEL-POLICY.md
  - claude/ideate/SKILL.md
  - claude/issue-slices/SKILL.md
milestone_end: true
```

- README: add the `prd-create` row to Requirements, Design & BA ("Interview to a PRD folder: PRD.md, ONTOLOGY.md, AERS.md, derived glossary; rubric: `_internal/ontology-readiness/`"); prd-validate row names both rubrics; ubiquitous-language row → "Derive the domain glossary from `ONTOLOGY.md` (legacy: extract from conversation)"; `_internal` tree adds `ontology-readiness/SKILL.md`; new "Artifact layout" paragraph for `docs/prds/<slug>/`; Typical flow rewritten as `/goal` → `/thesis` (optional) → `/prd-create` → `/prd-validate` (if not Ready) → `/execute-prd` or `/kickoff` → `/execute-plan`.
- `_internal/README.md`: add `ontology-readiness` to the `reference` examples sentence.
- skill-help: add `prd-create` to Specs & Requirements (rubrics stay unlisted per the file's own rule).
- `claude/CLAUDE.md`: dev-flow chain includes `prd-create`.
- MODEL-POLICY: add `prd-create` to the opus list.
- ideate and issue-slices handoff text: "write a PRD → `/prd-create`; upgrade an existing one → `/prd-validate`".
- Closing checks: no `/plan` anywhere in `claude/`; no `prd-not-ready`; every aers-readiness caller references it; `manifest.json` unchanged and `_internal` not in its skip list.

**Acceptance:** all of the following shell checks exit 0.
- `rg -q 'ontology-readiness' claude/README.md && rg -q 'ontology-readiness' claude/_internal/README.md && rg -q 'docs/prds/<slug>/' claude/README.md`
- `rg -q '/prd-create' claude/README.md && rg -q 'prd-create' claude/CLAUDE.md && rg -q 'prd-create' claude/skill-help/SKILL.md && rg -q '^- .prd-create.$' claude/MODEL-POLICY.md`
- `rg -q '/prd-create' claude/ideate/SKILL.md && rg -q '/prd-create' claude/issue-slices/SKILL.md`
- `! rg -q 'aers-readiness' claude/skill-help/SKILL.md`
- `jq empty manifest.json && jq -e '.claude.skills.skip | index("_internal") == null' manifest.json >/dev/null && git diff --quiet -- manifest.json`
- `! rg -q --pcre2 '(?<![\w/-])/plan(?![\w-])' claude && ! rg -q 'prd-not-ready' claude`
- `for f in prd-validate kickoff execute-prd spec-review-adversarial; do rg -q 'aers-readiness' claude/$f/SKILL.md || exit 1; done`
- `find claude -name "*.mjs" -print0 | xargs -0 bin/check-workflow-syntax && jq empty claude/settings.template.json`
- `for d in claude/*/ claude/_internal/*/; do case $d in claude/infra/|claude/_internal/|claude/install-scan/|claude/_internal/closed-decisions/) continue;; esac; test -f "$d/SKILL.md" && n=$(rg -o '^name: .*' "$d/SKILL.md" | cut -d' ' -f2) && test "$n" = "$(basename $d)" || exit 1; done`

## Sequencing

```
0 ─┐
1 ─┼─ 3 ──┬─ 4 ──┬─ 6 (also 2)
2 ─┘      │      └─ 10 (also 2)
          ├─ 5
          ├─ 7
          ├─ 8 (also 2)
          ├─ 9 (also 0)
          └─ 11
    4,5,6,10,11 ── 12 (prd-create; gate)
    1,7,8,9,12  ── 13 (closing; gate)
```

Tasks 0, 1, 2 run as one parallel group with a review gate after Task 2. Task 3 is the only blocker for the ontology phase; 5, 7, 8, 9, 11 are mutually independent. Task 4 gates on the score-cap re-score before 6 and 10. Task 12 gates before the closing index pass.

## Verification

Structural gate after every task: `find claude -name "*.mjs" -print0 | xargs -0 bin/check-workflow-syntax && jq empty manifest.json` (the repo's lint command) plus the task's own acceptance bullets. Run `/validate-plan` on this file before execution; run `/validate-skills` (repo dev skill, read-only) after Task 13.

End-to-end smoke, manual, after the branch is installed into `~/repos/skills-test-harness/claude-test` via `cli/skill.sh --claude --update`:

1. Greenfield dry run: `/prd-create --dry-run --mode greenfield "A todo list for one person"` prints `Mode: greenfield` and a `docs/prds/` path; `test ! -d docs/prds` exits 0 afterwards.
2. Brownfield dry run in a repo with a `package.json`: `/prd-create --dry-run "add tags to todos"` prints `Detected mode: feature` and a seed proposal with at least one entity carrying a `code:` citation; no files written.
3. Full greenfield run on the todo example produces `docs/prds/<slug>/{PRD,AERS,ONTOLOGY,UBIQUITOUS_LANGUAGE}.md`; the ontology's mandatory core is fully `settled`; `/prd-validate docs/prds/<slug>/AERS.md` reports an `Ontology:` line and does not re-ask settled items.
4. Extension run: `/prd-create --extend docs/prds/<slug>/ONTOLOGY.md "add due dates"` interviews only the delta and appends an `addition:` entry; changing a reference scheme in the answers produces a halt naming the stale artifacts.
5. Glossary: `/ubiquitous-language --from-ontology claude/ubiquitous-language/tests/ontology-sample.md` output matches `tests/expected-glossary.md` on entity names.
6. Gate: `/execute-prd docs/prds/<slug>/AERS.md` in autonomous mode with the ontology removed logs `Ontology: Absent` as a known risk and proceeds when the structural verdict is Ready.

## Out of scope, noted for later

- `bin/build-kimi-plugin --check` will report `kimi/skills/` out of sync after these edits; regeneration writes outside `claude/` and belongs with the handoff's deferred cross-platform parity task.
- Root `manifest.json`'s copilot block references a nonexistent `copilot-native/` tree.
- `.claude/skills/validate-skills/SKILL.md` references a stale `_rubrics/` path (overlay, not edited here per standing instruction).
- `_internal/pre-flight-check` has no callers; left as-is.
