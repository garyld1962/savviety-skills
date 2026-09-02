---
name: prd-validate
description: "Turn an existing story, BRD, PRD, or AERS draft into an implementation-ready AERS. Interviews the author, closes structural and semantic ambiguity against the AERS and ontology rubrics, generates missing sections. Use before planning, /kickoff, or /execute-prd. When NOT to Use: vague intent without a problem statement yet (use /goal first to validate the outcome before writing requirements); no artifact at all (use /prd-create, which owns the blank start and writes the PRD folder)."
model: opus
---

# /prd-validate — AERS Readiness Gate

**Purpose:** Take a requirements artifact (story, BRD, PRD, partial AERS, or plain-language ask) and turn it into an implementation-ready AERS through focused interview. Complements `/prd-acceptance` (post-implementation validation).

**Use before planning, `/kickoff`, or `/execute-prd`** when the requirements are still ambiguous.

## When to Use

- Requirements have ambiguity, missing sections, or unclear acceptance criteria
- A BRD, story, or partial AERS needs to be made implementation-ready
- An artifact's terms are load-bearing but undefined, and its sibling `ONTOLOGY.md` is missing, stubbed, or out of step with the requirements
- Before planning, `/kickoff`, or `/execute-prd` on a new feature

## When NOT to Use

- Requirements are already implementation-ready — skip to `/execute-prd` or `/kickoff`
- You have only an idea and no artifact yet — use `/prd-create`, which owns the blank-start interview and writes the PRD folder (`docs/prds/<slug>/`, including its `ONTOLOGY.md`)
- You want to build or extend an ontology interactively — use `/prd-create` or `/prd-create --extend`
- Verifying completed work — use `/prd-acceptance`
- You need the rubrics themselves — see `_internal/aers-readiness/SKILL.md` and `_internal/ontology-readiness/SKILL.md`

## Arguments

- `<path>` — path to the requirements artifact. If not provided, resolve it by the order below.
- `--refine-problem` — focus on problem refinement mode (vague problem → precise statement)
- `--full-spec` — **deprecated.** Recognised for one release; prints a pointer to `/prd-create` and does not run. See **Full spec mode** below.

Resolution order — first match wins:

1. The explicit `<path>` argument, if one was supplied.
2. The most recently modified `docs/prds/*/AERS.md`.
3. `./AERS.md` (legacy root location).
4. The most recently modified `docs/prds/*/PRD.md`.
5. `./PRD.md`.
6. `./prompt.md`.

If two or more candidates tie within the same tier, do not guess: ask the
operator which is canonical (interactive) or emit a `plan-ambiguity` finding
and stop (autonomous).

Sibling artifacts — `ONTOLOGY.md`, `UBIQUITOUS_LANGUAGE.md`, and `PRD.md` —
resolve relative to the directory of the resolved requirements file, not the
repo root.

## Rubric

Two rubrics govern this skill. Neither is restated here.

- `_internal/aers-readiness/SKILL.md` — the **structural** half: the full AERS
  checklist, required sections (including `Domain Ontology`), closed-decision
  categories, ambiguity priorities, engineering hardening rules, the structural
  score, and the composite the verdict thresholds are read against.
- `_internal/ontology-readiness/SKILL.md` — the **semantic** half: the eight
  elicitation categories, the item states, the mandatory core, the `ONTOLOGY.md`
  format, the semantic ambiguity categories, the mode-aware delta rule, and the
  `Ontology:` verdict with its capped composite contribution.

Never restate a scoring number, a band, or an item-state definition — in this
skill or in its output. Cite `_internal/ontology-readiness` for both the scoring
and the meaning of `settled` / `deferred` / `unknown`.

The ontology under test is the sibling `ONTOLOGY.md`, located by the
sibling-artifact rule in `## Arguments`: it lives beside the resolved artifact,
in that artifact's `docs/prds/<slug>/` folder. There is no inline alternative —
an inlined ontology reads as a missing one.

## Workflow

### Step 1: Read the Artifact

Read the provided file, or resolve one by the order under `## Arguments`. Read
the sibling `ONTOLOGY.md` in the same folder if one exists, and note its `mode:`,
`scope:`, and `extends:` header fields — Step 5 needs them.

If nothing is found and nothing was pasted into the conversation, stop and say:
> "No requirements artifact found. `/prd-create` owns the blank start — it runs
> the interview and writes `docs/prds/<slug>/` including `ONTOLOGY.md`. Run that
> first, then `/prd-validate` on what it produces."

Do not open a blank-start interview here.

### Step 2: Assess Current State

Scan the artifact against the AERS required sections (from
`_internal/aers-readiness/SKILL.md`):
- Which sections exist and are complete?
- Which sections are missing?
- Which contain blocking ambiguity?

Then score the sibling `ONTOLOGY.md` against
`_internal/ontology-readiness/SKILL.md`:
- Which of the eight elicitation categories are substantive, stubbed, or absent?
- Is the mandatory core complete?
- Which load-bearing terms in the artifact resolve to no ontology entry?

Report a quick readiness snapshot:
```
Current readiness: Partially ready
Ontology: Partial

Present: Problem Summary, Scope, Functional Requirements
Missing: Closed Decisions, Data Models, Verification Matrix, Execution Preflight
Ambiguous: scope boundary (is X in or out?), delete semantics
Undefined terms: "account" (two meanings), "archive" (no lifecycle exit)
```

Always emit the `Ontology:` line, including when it reads `Ready` or
`Absent (trivial domain)` — a silent line is indistinguishable from a check that
was never run. When no sibling `ONTOLOGY.md` exists, apply the trivial-domain
test from `_internal/ontology-readiness` before reporting a bare `Absent`, and
report the gap: do not fabricate an ontology to fill the line.

### Step 2.5: Risk-Rank the Gaps (Extended Thinking)

Before asking any questions, engage extended thinking to reason privately:
- Which gaps, if left unresolved, would cause the most expensive implementation mistake?
- Are there ambiguities that look small but hide a load-bearing architectural decision?
- What is the most likely way this artifact gets misinterpreted by an engineer who doesn't ask questions?
- If implementation started today from this artifact, what would break first?

Rank **semantic** gaps in the same ordering as structural ones — one list, not
two. Semantic gaps usually win, because a wrong section is rewritten while a
wrong term is migrated: an undefined load-bearing term, an unresolved homonym,
or a missing reference scheme outranks a missing **Tooling Assumptions**
section. The mandatory-core items in `_internal/ontology-readiness` are the
highest-cost gaps in either list, for exactly the reasons that rubric gives.

Use this to order the Step 3 interview by actual risk, not by section order or
by which rubric raised the gap. Ask the most dangerous gap first.

### Step 3: Interview

Follow the interaction rules from `_internal/aers-readiness/SKILL.md` (and, for
ontology questions, the matching rules in `_internal/ontology-readiness/SKILL.md`):
- One question at a time
- Prefer multiple-choice with recommended default
- Prioritize by the single risk ordering from Step 2.5
- Challenge ambiguity instead of smoothing over it — "both, probably" is a homonym, not an answer

### Step 4: Generate Missing Sections

As answers come in, produce the lightest useful version of:
- gap report
- Closed Decisions section
- Open Decisions section
- Public API / interface section (when relevant)
- Data Models section (when relevant)
- example JSON or contract snippets where ambiguity exists
- Execution Preflight
- Verification Matrix
- UI Behavior Matrix (when UI work is involved)
- `ONTOLOGY.md` rows for every term settled during the interview, in the format
  owned by `_internal/ontology-readiness` (never a variant of it)

**Where the output lands.** Write the enriched artifact back to the resolved
artifact path. When the run started from a non-file source — an artifact pasted
into the conversation — write a new `docs/prds/<slug>/AERS.md`, per the
Contract. Either way, `ONTOLOGY.md` may be written or updated beside it in the
same folder: created when the domain is non-trivial and none exists and the
interview settled enough to write one, appended to otherwise. Never rewrite an
existing `ONTOLOGY.md` wholesale — its Extension Log is append-only, and its
already-`settled` rows are not yours to reopen.

### Step 3.5: Closure Pass

Numbered 3.5 because it closes the Step 3 interview, but placed after Step 4
because it runs against drafted text — there is nothing to close until the
sections and the ontology rows exist.

Mechanical. Tick every box against the drafted artifact and its sibling
`ONTOLOGY.md`:

- [ ] **Every noun and verb in Functional Requirements resolves to an ontology term.** Each one names an entity type, a role in a fact type, an event in a lifecycle, or a defined term. A word used in a requirement and absent from the ontology is a gap, not a synonym.
- [ ] **Every fact type carries a constraint or the literal marker `[unconstrained]`.** A blank Constraints cell is an omission; `[unconstrained]` is a decision.
- [ ] **Every state has a defined exit or is marked terminal.** Walk each lifecycle table state by state. A state with neither an outbound transition nor a terminal marker makes the state machine non-total.
- [ ] **No homonym survives.** No term carries two meanings; no two terms carry one meaning. Check the artifact and the ontology together — a split resolved in one and not the other is still a surviving homonym.
- [ ] **Every "shall" is alethic or deontic.** Every "shall" / "must" / "will" statement carries a modality label: alethic (cannot be otherwise → schema or type constraint) or deontic (must not be otherwise → validation rule or alert). Unlabelled is a conflation, and the two compile to different code.

Each unticked box yields items, and every item takes exactly one of two exits:

1. **The user answers** → record it in `ONTOLOGY.md` as a `settled` row, or as a `deferred` row *with* its re-entry condition, and reflect it in the artifact.
2. **The user does not know** → record an `unknown` row naming why, and carry it into the Step 5 blocking-gap list.

There is no third exit. Do not fabricate a reference scheme, a constraint, a
modality, or a temporality to make a box tick — a fabricated answer is
indistinguishable from a settled one six months later, which is the whole reason
the item states exist.

### Step 5: Readiness Verdict

End with the template from `_internal/aers-readiness/SKILL.md` §
*Readiness Assessment*, unchanged:
```
Readiness: Ready / Partially ready / Not ready
Ontology: Ready / Partial / Absent

Structural score: <n>
Ontology contribution: <0 | +2 | +4>
Composite: <n>

Blocking gaps:
- (list, or "None")

Recommended next step:
- /execute-prd <path>  (if ready)
- /prd-create --extend <path>  (if the ontology is Partial, or Absent on a non-trivial domain)
- Continue refining (if not ready)
```

`Ontology:` is copied verbatim from `_internal/ontology-readiness`, including
the `(trivial domain)` qualifier when that rule fires. The three numeric lines
come from those rubrics; do not compute a variant here.

**`--extend` awareness.** When the sibling `ONTOLOGY.md` header declares
`mode: feature` or `mode: rewrite`, validate against the delta its `scope:` and
`extends:` fields declare — the new entities plus any `deferred` item this
feature now touches — and score per category over the delta rows only, per the
mode-aware scoring rule in `_internal/ontology-readiness`. Pre-existing settled
rows are not re-scored, and a category with no delta rows is not a gap.

Under that rule, **do not report `deferred` items as gaps.** A deferral carrying
a re-entry condition is a recorded decision, not an omission; reporting it as a
gap punishes the honest marker and pushes the next author toward silence. The
exceptions are the ones the rubric already names: a `deferred` mandatory-core
item, a deferral with no re-entry condition, and any `revision` entry in the
Extension Log — surface all three, per that rubric.

## Modes

### Default mode

Upgrade an existing artifact into an AERS. Focus on closing ambiguity and adding missing sections.

### Problem refinement mode (`--refine-problem`)

Bias toward:
- turning solution-shaped requests back into problem statements
- surfacing stakeholder, scope, impact, root-cause, success, and assumption gaps
- producing a concise problem statement plus a gap map

### Full spec mode (`--full-spec`) — deprecated

**Deprecated.** The flag is still recognised for one release so that existing
invocations get a pointer rather than an unknown-flag error. It does not run.

On seeing `--full-spec`, print:

> `--full-spec` is deprecated. `/prd-create` owns the blank-start interview and
> writes the PRD folder — `docs/prds/<slug>/`, including its `ONTOLOGY.md`. Run
> `/prd-create` for a new spec, or `/prd-validate <path>` (no flag) to harden an
> existing one.

Then stop. Do not fall through to default mode with the flag silently ignored,
and do not start a batched interview.

## CRITICAL: Do Not Guess

- Do NOT invent settled facts. If the author knows something, ask them.
- Do NOT fabricate an ontology, a reference scheme, a constraint, a modality, or a temporality to close a Step 3.5 box. `unknown` is an honest row; an invented one is not.
- Do NOT reopen or overwrite `settled` rows in an existing `ONTOLOGY.md`, and do NOT convert a `deferred` row to `settled` without the author's answer.
- Do NOT silently choose architecture-impacting defaults when the choice is still open.
- Do NOT overwrite an existing artifact wholesale without showing proposed changes.
- Do NOT mark the artifact ready if blocking ambiguity remains.
- Do NOT stop at a business-oriented PRD if the user needs an engineering-executable output.
- Do NOT drift into implementation planning — that belongs in `/execute-prd`.

## Contract

- **Inputs:** `<path>` to a requirements artifact, OR the artifact pasted into the conversation; the sibling `ONTOLOGY.md` when one exists, plus the prior ontology named by its `extends:` in `feature` / `rewrite` mode. Optional flags: `--refine-problem`; `--full-spec` (deprecated — recognised, points at `/prd-create`, does not run). Embeds both rubrics: `_internal/aers-readiness` for structure and `_internal/ontology-readiness` for semantics.
- **Preconditions:** human operator is at the keyboard — this is an interactive interview, not a gate. Callers (`/kickoff`, `/execute-prd`) MUST NOT auto-invoke this skill from a non-interactive context. A requirements artifact exists; a blank start belongs to `/prd-create`.
- **Outputs:** an enriched AERS written back to the resolved artifact path (or, when started from a non-file source, a new `docs/prds/<slug>/AERS.md`); an `ONTOLOGY.md` written or updated beside it in the same folder; closed decisions inlined; a fresh composite score and `Ontology:` verdict line per the two rubrics' automated checks; a gap list for residual unresolved items, including `unknown` rows raised by the closure pass.
- **Postconditions:** artifact moves toward `Ready` — but does not require it (`Partially ready` is an acceptable exit when residual gaps are documented as open decisions); the Step 3.5 closure pass has run against the drafted output; `ONTOLOGY.md` keeps its existing `settled` rows and its append-only Extension Log; callers can re-score with `_internal/aers-readiness` to confirm.
- **Failure modes:** non-interactive context detected → refuse to start and suggest `_internal/aers-readiness` for a deterministic score instead; user says "you choose" on a non-default question → propose a default and ask for confirmation, do not silently pick; ontology absent on a non-trivial domain → report the gap and recommend `/prd-create`, **do not fabricate** an ontology to close it; `revision` entry in the Extension Log → surface it rather than scoring past it.
