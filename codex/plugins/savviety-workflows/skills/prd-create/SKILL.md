---
name: prd-create
description: "Create a PRD, ONTOLOGY.md and AERS from an idea, goal, thesis or codebase via interview. Modes: greenfield, feature, refresh, rewrite. Not for an existing artifact (use /prd-validate)."
model: opus
---

# /prd-create — PRD, Ontology and AERS Authoring Interview

**Purpose:** Elicit a universe of discourse and a requirements set from a human,
seeded from the codebase when one exists, and write a per-PRD folder: the
human-readable `PRD.md`, the machine-facing `AERS.md`, the `ONTOLOGY.md` that
defines the domain, and the derived `UBIQUITOUS_LANGUAGE.md`. This is the
interactive front of the requirements pipeline; `/prd-validate` gates what it
produces.

Two rubrics own the standards this skill applies. Cite them; never restate them:

- `_internal/ontology-readiness` — elicitation categories, `### Item states`
  (`settled` / `deferred` / `unknown`), Rules 1–4 and the mandatory core, the
  `## ONTOLOGY.md format`, and the **Automated ontology check**.
- `_internal/aers-readiness` — Required Sections, Entry Modes, Interaction
  Rules, **Prioritize Ambiguity by Risk**, the **Automated readiness check**,
  and the Readiness Assessment template.

## When to Use

- An idea, a `/goal` statement, or a `/thesis` exists but no requirements artifact does
- A new feature must extend an existing `ONTOLOGY.md`
- A brownfield repo needs a PRD anchored to what the code already says
- You want the domain modelled before implementation planning starts

## When NOT to Use

- A requirements artifact already exists → `/prd-validate` (it hardens; this skill drafts)
- Only the goal is unclear → `/goal` first
- Scope is wobbly and there is no thesis → `/thesis` first (optional)
- Structural refactor with no user-visible behaviour change → `/modernize`
- You want tickets → `/issue-slices`, after this
- You want to build → `/execute-prd`, after this

## Arguments

- `<description>` — plain-language ask (optional; if omitted and no `--from`, ask).
- `--mode greenfield|feature|refresh|rewrite` — override auto-detection. Detection is otherwise confirmed with one question; this flag skips that question.
- `--extend <path-to-ONTOLOGY.md>` — load an existing ontology and interview only the delta. Implies `--mode feature` unless `--mode` says otherwise. If omitted in feature or rewrite mode and exactly one `docs/prds/*/ONTOLOGY.md` exists, propose it; if several exist, ask which.
- `--from <file>` — seed from a `/goal` statement, a `/thesis` artifact, or free notes; classified by content (see **Input Modes**).
- `--out <dir>` — output folder. Default `docs/prds/<slug>/`, slug = kebab-case of the goal title, confirmed in Step 0. Never overwrite an existing folder without showing the diff first.
- `--no-scan` — skip the Step 1 codebase seed. Refused in `refresh` (there is no baseline without a scan) and in `rewrite` unless `--extend` is given. Recorded in the ONTOLOGY.md header as `seeded-from-code: no (--no-scan)` and in AERS **Repo Starting State**.
- `--dry-run` — run Steps 0–1 only: print the detected mode with its evidence, the resolved output paths, and the seed proposal. Write nothing, ask no interview questions, invoke no sibling skill.
- `--full-spec` — accepted for one release as the blank-start batched alias absorbed from `/prd-validate`. Batching applies to Step 4 only.

## Input Modes

### Blank start

Ask the `_internal/aers-readiness` **Entry Modes** prompt verbatim:

> "Tell me what you want to achieve in plain language. You do not need to format it yet — I will help turn it into a structured, implementation-ready artifact."

Then run Steps 2–4 one question at a time.

**Blank start (batched)** — under `--full-spec` only, Step 4's requirements
interview may batch questions within one rubric category. Step 3's ontology
interview is never batched: the mandatory core is per entity, and each answer
changes the next question.

### From `/goal` or `/thesis` output (`--from`)

Classify the file by content, not by filename:

| Signal in the file | Classified as | Feeds |
|---|---|---|
| `Goal:` / `Success criteria:` / `Out of scope:` lines | goal | Problem Summary, success signals, Scope, Assumptions |
| `## Thesis` heading with In scope / Out of scope | thesis | Step 2 UoD boundary test, Scope, cut list |
| Neither | notes | Treated as an existing artifact per aers-readiness **Entry Modes**: preserve what is known, do not re-ask it |

### Existing notes or brownfield repo

Project shape is detected in the cwd via `_internal/modernization-rubric` §1.
The codebase is a source, not a substitute for the human: Step 1 proposes,
Step 3 confirms.

## Workflow

### Step 0: Preflight

1. **Interactive check.** This is an interview. In a non-interactive context (CI,
   autonomous run, scheduled agent), refuse to start with the same shape as
   `/prd-validate`'s non-interactive failure mode: say so, and point at
   `_internal/aers-readiness` and `_internal/ontology-readiness` for a
   deterministic score of an existing artifact instead. Never start a partial
   interview and fill the rest in.
2. **Resolve mode** — first match wins; then confirm with one question whose
   default is the detected mode. `--mode` skips the question.

   | Detect | Evidence |
   |---|---|
   | greenfield | no manifest (`_internal/modernization-rubric` §1) in cwd and no `--extend` |
   | rewrite | project shape detected AND the ask contains rewrite verbs (rewrite, replace, port to, migrate from X to Y, re-platform, v2 from scratch) |
   | refresh | project shape detected AND the ask contains modernize triggers (modernize, refresh, bring up to date, upgrade the stack) |
   | feature | project shape detected (brownfield default), or `--extend` given |

   Tie-break refresh versus rewrite with one question: "May the public API or
   stack change? No → refresh. Yes → rewrite." If refresh turns out to carry no
   user-visible behaviour change, say so and offer `/modernize` — link it, do
   not invoke it.
3. **Locate the ontology for `--extend`.** Read its header. If it has no `uod:`
   field, halt: an ontology without a UoD boundary cannot license a deferral, so
   the delta cannot be classified. Say that, and point at `/prd-validate`.
4. **Resolve slug and `--out`.** May share the mode confirmation message when
   both are defaults. If the folder exists, show the diff before writing.
5. **Extended-thinking gate** (as `/goal` Step 2). Before asking anything, reason
   privately about which rubric categories the inputs already answer, which
   entities are actually in this release, and where the expensive mistakes are.
   Produce a per-entity question budget: the 4 mandatory-core categories, plus at
   most 2 discretionary questions before offering deferral.

Under `--dry-run`, print the resolved mode with its evidence and the resolved
output paths here. In brownfield modes continue to Step 1 and stop after the seed
proposal; in `greenfield` stop here. Either way write nothing and ask nothing.

### Step 1: Codebase seed (brownfield only; skipped by `--no-scan` where permitted)

Compose existing scanners. Never invent a new one.

- `/audit-existing` → `## Existing State` feeds AERS **Repo Starting State**,
  **Tooling Assumptions** and **Execution Preflight**;
  `## Duplicated Or Divergent Contracts` is the strongest homonym signal;
  `## Missing Or Partial` feeds PRD **Current State**; `## Test And Verification
  Gaps` and `## Planning Implications` feed the AERS Verification Matrix.
- Domain-entity discovery, the ubiquitous-language codebase-scan idea applied to
  the ontology categories: read `references/codebase-seed.md` for the full
  code-signal → ontology-category table (models and exported domain types →
  entities; PK and unique indexes → reference schemes; FKs and relations → fact
  types with cardinality; status enums plus transition code → lifecycles with a
  totality check; NOT NULL and check constraints → alethic candidates; validators
  and guards → deontic candidates; timestamps, history tables and soft delete →
  temporality; the same name in two packages → homonym).
- `refresh` only: `_internal/modernization-rubric` §1 shape detection (language,
  type, size class, test signal, patterns) feeds the PRD **Current State** header
  and AERS **Repo Starting State**. Sample-read per its §3 and stop at the 30%
  context guardrail. Do not run `/modernize`: it produces a refactor plan, not a PRD.

Emit a **seed proposal** and print it. Every seeded item enters `ONTOLOGY.md` as
`unknown` with a `code:<file:line>` source until a human confirms it in Step 3.
Nothing seeded is ever written `settled` without a human answer — a scan reports
what the code does, which is not evidence of what the domain requires.

Under `--dry-run`, the seed proposal is the last thing printed: stop here, write
no files, and do not enter Step 2.

### Step 2: UoD boundary and thesis anchoring

Use the thesis (from `--from`, or stated in the ask) as the UoD boundary test.
Otherwise ask for one sentence. If the user cannot give one and scope is wobbly,
offer `/thesis` — link it, do not run it inline.

Propose the boundary as two lists — representable this release, and not
representable this release — and distinguish UoD from Scope in the rubric's own
words: Scope bounds the *work*, the UoD bounds *representable truth*. Ask one
confirm-or-amend question.

Brownfield: seeded entities outside this release's ask are proposed as out of the
UoD. That is what licenses deferring their fact types.

**`rewrite` only — agree the permitted-change list here**, alongside the UoD
boundary, with one question:

> "Which ontology items may this rewrite revise? Everything not on this list is
> preserved as-is."

Record the answer as a confirmed closed decision. Step 3 gates every `revision`
against this list, and Step 5 records it as the PRD's `What May Change`. Agreeing
it in Step 2 is what makes the Step 3 gate checkable — the PRD does not exist
until Step 5.

### Step 3: Ontology interview

Ask in this order: entities and reference schemes → homonyms and synonyms → fact types →
constraints → modality → lifecycle totality → temporality. Per entity, the
mandatory core first.

- One question at a time. Propose a default, explain why the question matters,
  challenge ambiguity — "both, probably" is a homonym, not an answer. "You
  choose" → propose a default and ask for confirmation.
- **Explore before asking** (`/grill-me`): if the Step 1 seed already answers a
  question, show the `code:<file:line>` evidence and ask only for confirmation.
- **Mandatory core cannot be deferred.** Refuse with the Rule 2 rationale from
  `_internal/ontology-readiness`. The only two exits are `settled`, or removing
  the entity from this release's UoD.
- A deferral requires a **re-entry condition**. Without one it is `unknown`, and
  scores per `_internal/ontology-readiness` § *Item states*. Say so at the time.
- One elementary predicate per fact type; bold the entity names; split compound
  statements. Every fact type gets a constraint or the explicit `[unconstrained]`
  marker — blank is an omission. Constraint cells use the `unique:`,
  `mandatory:` and `value domain:` prefixes.
- Every "shall" or "must" is classified alethic or deontic before it is written.
- Say the cost of deferral out loud: only `settled` rows are consumed downstream
  by `/prd-acceptance` and `/test-plan`.

**Under `--extend`:** interview only new entities plus `deferred` items this
feature now touches — exactly the delta declared by `scope:` and `extends:`.

**Classify every change** as an `addition` (appends freely) or a `revision` (one
of the five kinds in Rule 4). Revision handling is per mode:

- `feature` — a `revision` **halts**. List the stale downstream artifacts (PRD,
  AERS, data models, tests, code) and write nothing.
- `refresh` — same rule as `feature`: a `revision` **halts** with the same stale
  artifact list. Add to the halt message that a change of this class means the
  ask is really a rewrite, and offer re-running in `--mode rewrite`. Refresh has
  no permitted-change list of its own.
- `rewrite` — a `revision` is allowed only when the item appears in the
  permitted-change list agreed in Step 2, and is confirmed there as a closed
  decision. Log it as `revision` in the Extension Log, citing that decision.
  Anything outside the Step 2 list **halts**. Do not consult the PRD's
  `What May Change`: Step 5 writes that section *from* the Step 2 agreement, so
  it does not exist yet when this gate runs.
- `greenfield` — no baseline exists; every change is an `addition`.

### Step 4: Requirements interview (aers-readiness risk order)

Under `--full-spec`, print once before asking anything:
`--full-spec` is a one-release alias; it will be removed.

Second extended-thinking gate — the `/prd-validate` Step 2.5 questions: which
gaps cause the most expensive mistake, which small-looking ambiguities hide a
load-bearing decision, what breaks first if implementation started today. Then
ask in **Prioritize Ambiguity by Risk** order, semantic and structural gaps in
one list.

- Stack, runtime and tooling come from the Step 1 audit. Never ask what the
  audit already answered.
- Draft Functional Requirements as `FR-n`, with **bold** ontology terms and a
  modality tag on each rule.
- **Closure check:** every noun and verb in the FRs resolves to an ontology term.
  Unresolved terms go back to Step 3 as additions, not into the PRD as prose.
- Acceptance criteria are `- [ ]` checkboxes carrying the load-bearing ontology
  constraints (a uniqueness constraint becomes a duplicate-insert criterion, a
  mandatory role a null-rejection criterion, a total lifecycle an exhaustive
  transition criterion) so `/prd-acceptance` and `/test-plan` can find them.

Batching is permitted here, within one rubric category, only under `--full-spec`.

### Step 5: Write PRD.md

Write `<out>/PRD.md` from `references/prd-template.md`. Sections: header (title,
date, status, owner, **Mode**, thesis, links to the three siblings); Summary;
Problem and Outcome; Thesis and UoD Boundary; Users and Actors; Scope (in / out /
later); **Current State → Target State** (brownfield only; delta table
`| Aspect | Current | Target | Change class |`); Functional Requirements;
Non-functional Requirements; Acceptance Criteria; Closed Decisions and Open
Decisions (product-level only — engineering decisions live in the AERS); Risks
and Assumptions; Non-goals; **What May Change** (rewrite only).

In `rewrite` mode, `What May Change` is not elicited here: it records the
permitted-change list agreed in Step 2, together with the preserved list that is
its complement. Every Extension Log `revision` written in Step 3 must appear in
it.

The PRD carries no Public API, Data Models, Verification Matrix, Repo Starting
State, Tooling Assumptions, Execution Preflight or Readiness Assessment. PRD
content flows into `AERS.md` in Step 7, never the reverse.

### Step 6: Write ONTOLOGY.md

Write `<out>/ONTOLOGY.md` in the `## ONTOLOGY.md format` owned by
`_internal/ontology-readiness`. Do not reproduce that format here; read it there
and follow it exactly, including the header fields (`mode`, `extends`, `scope`,
`uod`, `seeded-from-code`, `thesis`, `status`) and the status summary line.

Mandatory-core rows can only be `settled`. The Extension Log is created empty in
greenfield and appended in every other mode; it is append-only.

### Step 7: Translate to AERS.md and score

This skill writes `<out>/AERS.md` itself, by applying the
`_internal/aers-readiness` transformation to the PRD:

- Map PRD sections onto the **Required Sections**, one of which is
  `Domain Ontology` — a pointer to the sibling `ONTOLOGY.md`, never an inline
  copy.
- Generate the sections the PRD does not carry: Public API or Public Interface;
  Data Models (citing `ONTOLOGY.md` as the source and naming which entity each
  structure represents); Verification Matrix; Repo Starting State; Tooling
  Assumptions; Execution Preflight; Definition of Done.
- Apply both automated checks: the **Automated readiness check** for the
  structural score, and the **Automated ontology check** for the `Ontology:`
  line and its capped composite contribution.
- Write the **Readiness Assessment** in the rubric's template, with both verdict
  lines, the structural score, the ontology contribution, the composite, the
  blocking gaps and the recommended follow-ups.

Recommend `/prd-validate` only when the verdict is not `Ready`, or when
`unknown` rows remain in the ontology. A `Ready` artifact with no `unknown` rows
does not need the hardening interview.

### Step 8: Derived glossary

Invoke `/ubiquitous-language --from-ontology <out>/ONTOLOGY.md`, which writes
`<out>/UBIQUITOUS_LANGUAGE.md`. The glossary is a view of the ontology: never
hand-write it, never hand-edit it, and never let it disagree with the ontology.

### Step 9: Report and handoff

Print this to the console. It is the run report, **not** the AERS
**Readiness Assessment** section — that one is written into `AERS.md` in Step 7,
in the `_internal/aers-readiness` template, and is not restated here.

```
PRD folder: docs/prds/<slug>/
  PRD.md · AERS.md · ONTOLOGY.md · UBIQUITOUS_LANGUAGE.md
Mode: <mode>   Seeded from code: yes @ <sha> | no (--no-scan) | n/a (greenfield)
Readiness: Ready | Partially ready | Not ready   (structural <n>, ontology +<c>, composite <n>)
Ontology: Ready / Partial / Absent   (settled <n> · deferred <n> · unknown <n>; mandatory core complete | INCOMPLETE)
Blocking gaps:
- ...
Next step:
  /prd-validate docs/prds/<slug>/AERS.md   (if not Ready, or unknown rows remain)
  /execute-prd docs/prds/<slug>/AERS.md    (if Ready)
  /issue-slices                            (tickets first)
```

## Per-mode differences

| Aspect | greenfield | feature | refresh | rewrite |
|---|---|---|---|---|
| Step 1 seed | skipped | audit + entity scan | audit + entity scan + modernization-rubric §1 shape | audit + entity scan (or `--extend` in lieu) |
| Baseline ontology | none | existing via `--extend` (delta) or seeded | current-state facts from code are the baseline, confirmed before any target-state change | the existing ontology is the contract to preserve |
| Change classification | all additions | addition appends; revision halts | additions append; revision halts, offering `--mode rewrite` | additions append; revision only if in the Step 2 permitted-change list, confirmed as a closed decision; outside it halts |
| PRD-specific sections | — | Current State → Target State | Current State → Target State with shape header; redirect to `/modernize` when no behaviour changes | Current State → Target State, plus `What May Change` and the preserved list, both recording the Step 2 agreement |
| AERS Repo Starting State | "empty repo" | from audit | from audit + shape | from audit; replacement strategy recorded as a decision |
| `--no-scan` | n/a | allowed (recorded) | refused | only with `--extend` |
| Extension Log | created empty | appended | appended | appended; revisions cite the Step 2 decision that permitted them |

## Rules

- Apply the **Interaction Rules** of both rubrics: one question at a time,
  multiple choice with a recommended default, explain why it matters, challenge
  ambiguity, "you choose" gets a proposal and a confirmation.
- Item states are `settled`, `deferred` (with a re-entry condition) and
  `unknown`, defined once in `_internal/ontology-readiness` § *Item states*.
  Use those words; do not redefine them.
- The mandatory core is Rule 2's four categories. It is never deferred, and a
  mandatory-core row that is not `settled` carries the mandatory-core cap defined
  in `_internal/ontology-readiness` Rule 2.
- Question budget per entity: 4 mandatory-core, then at most 2 discretionary
  before offering deferral. Deferral is free; silence is not.
- Every seeded row keeps its `code:<file:line>` source until a human settles it.
- Ontology describes the world; Data Models describe the representation. Keep
  them separate.
- Halt conditions surface and stop: `--extend` target without a `uod:` header,
  a `revision` in feature or refresh mode, a `revision` outside the Step 2
  permitted-change list in rewrite mode.
- Score with the rubrics' automated checks. Do not invent a variant.

## CRITICAL: Do Not

- Do NOT fabricate a fact, entity, reference scheme, constraint, modality or
  temporality to close a gap. `unknown` is an honest row; an invented one is not.
- Do NOT run from a **non-interactive** context, and do NOT let another skill
  auto-invoke this one. `/kickoff` and `/execute-prd` never auto-invoke it.
- Do NOT defer a mandatory core item, and do NOT accept any deferral without a
  re-entry condition — record it as `unknown` and say so.
- Do NOT write a `settled` row for anything a human has not answered, including
  every row the code scan proposed.
- Do NOT hand-write or hand-edit `UBIQUITOUS_LANGUAGE.md`; it is derived in Step 8.
- Do NOT write a revised ontology when Step 3 classifies a change as a
  `revision` — halt, list the stale artifacts, and let the human decide.
- Do NOT overwrite an existing `--out` folder without showing the diff first.
- Do NOT drift into `/execute-prd` planning or `/modernize` refactor work; this
  skill writes requirements, not plans.
- Do NOT batch questions outside `--full-spec`, and never batch Step 3.
- Do NOT report `Readiness: Ready` while a mandatory-core row is missing or a
  high-risk ambiguity category is unresolved.

## Contract

- **Inputs:** `<description>` and/or `--from <file>` (goal, thesis or notes); the repo in cwd; optionally an existing `ONTOLOGY.md` via `--extend <path>`. Flags: `--mode greenfield|feature|refresh|rewrite`, `--out <dir>`, `--no-scan`, `--dry-run`, `--full-spec`. Embeds `_internal/ontology-readiness` and `_internal/aers-readiness`; composes `/audit-existing` and `_internal/modernization-rubric`; reads `references/codebase-seed.md` and `references/prd-template.md`.
- **Preconditions:** a human operator is at the keyboard — this is an interview, never a gate and never auto-invoked. Write access to `--out` (default `docs/prds/<slug>/`). For `--extend`, the named ontology exists and its header carries `uod:`.
- **Outputs:** the folder `docs/prds/<slug>/` containing `PRD.md`, `ONTOLOGY.md`, `AERS.md` and the derived `UBIQUITOUS_LANGUAGE.md`, plus the Step 9 report with the `Readiness:` and `Ontology:` lines and a next step. Under `--dry-run`: the detected mode with evidence, the resolved paths and the seed proposal, and no files.
- **Postconditions:** every ontology row carries `settled`, `deferred` with a re-entry condition, or `unknown`; the mandatory core is complete or the report says `INCOMPLETE`; the Extension Log is append-only; pre-existing `settled` rows are unchanged; the glossary is derived, not authored.
- **Failure modes:** non-interactive context → refuse and point at the two rubrics for a deterministic score. `--extend` target with no `uod:` header → halt. `revision` classified in feature or refresh mode → halt with the stale-artifact list, write nothing (refresh additionally offers `--mode rewrite`). `revision` in rewrite mode outside the Step 2 permitted-change list → halt. `--no-scan` in refresh, or in rewrite without `--extend` → refuse and explain there is no baseline. Existing `--out` folder → show the diff and ask before overwriting. User asks to skip the mandatory core → refuse with Rule 2's rationale and offer to drop the entity from this release's UoD instead. User wants an existing artifact hardened rather than drafted → hand off to `/prd-validate`.

## Codex integration
Use `$prd-create` explicitly or let its description match the request. Resolve
sibling skills inside this plugin. Read AGENTS.md before repository edits; honor
the current host's tool access and delegation rules. Do not require another
platform's runtime.
