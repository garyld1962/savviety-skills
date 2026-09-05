---
slug: ontology-prerequisites-for-prd-create
intent: Prepare the downstream skills in claude/ to produce, consume, and enforce a domain ontology — including deliberately partial ones that extend feature by feature — so that a new /prd-create skill has somewhere to write its semantic output and something downstream that honours it. Does not build /prd-create itself.
type: enabling
---

# Prerequisite plan: semantic + ontology readiness for `/prd-create`

**Scope:** `claude/` only. Ten tasks across one new internal rubric and nine existing skills.

**Why this exists:** `/prd-create` will elicit a universe of discourse — entity types, reference schemes, fact types, constraints, lifecycle, temporality, modality. Today nothing in `claude/` can receive that. `_internal/aers-readiness` has no ontology section and no ontology ambiguity categories, so its automated score cannot see semantic defects. `/ubiquitous-language` is the only semantic skill and it is **orphaned** — a grep for `ubiquitous` across `claude/` returns only its own SKILL.md, the README index, MODEL-POLICY, and skill-help. No skill calls it. If `/prd-create` ships before this plan lands, its best output falls straight on the floor.

---

## Closed Decisions

Confirmed. These are load-bearing for every task below.

- **Rubric/interview split mirrors the existing AERS pattern.** `_internal/ontology-readiness/` holds the scorable rubric (`kind: reference`, `user-invocable: false`); `/prd-create` is the interactive remedy. This is the same shape as `_internal/aers-readiness` ↔ `/prd-validate`, and it is what makes the ontology gate-able from non-interactive contexts.
- **Artifact is `ONTOLOGY.md`, written to the working directory.** Fact types and constraints do not fit the glossary table format `UBIQUITOUS_LANGUAGE.md` uses. The glossary becomes a **derived view** of the ontology, not a second source of truth.
- **Notation is verbalized natural-language fact types in Markdown.** No OWL, RDF, or ORM diagram syntax. "A **Customer** places zero or more **Orders**" — readable by a stakeholder, checkable by an agent.
- **Skill directory is `claude/prd-create/`, invoked as `/prd-create`.** Matches `prd-validate` / `prd-acceptance`. The string "create a PRD" goes in the `description:` field for discoverability.
- **`/prd-create` absorbs `prd-validate --full-spec`.** The blank-start batched interview becomes `/prd-create`'s job. The flag is deprecated in Task 4 with a pointer; `/prd-validate` narrows to what its name says — validating and upgrading an artifact that already exists.
- **Ontology is not Data Models.** The ontology describes the world; `Data Models` describes the representation. The ontology *feeds* `Data Models` and `Closed Decisions`. The rubric must state this explicitly or the two sections will collapse into each other within a release.
- **A partial ontology is a first-class output, not a failure state.** Completeness is scoped to the universe of discourse of *this release*, and extended per feature. The rules that make this safe are specified in Task 1 under *Completeness and Extension* and are load-bearing for Tasks 2 and 8.

## Non-goals

- Writing `/prd-create` itself. That is the next plan.
- Porting any of this to `codex/`, `codex-new/`, `copilot/`, or `kimi/`. Parity is a follow-on (Task 11, deferred).
- Changing `manifest.json`. The installer copies `claude/` wholesale with a `skip` list; new directories are picked up without a manifest edit. Verify this during Task 10 rather than assuming it.
- Replacing or deprecating `Data Models` in the AERS.

---

## Task 1: Author `_internal/ontology-readiness`

```yaml
depends_on: []
write_scope:
  - claude/_internal/ontology-readiness/SKILL.md
  - claude/_internal/README.md
```

New reference rubric. Frontmatter per `_internal/README.md`: `user-invocable: false`, `internal: true`, `kind: reference`.

**Elicitation categories** (these are the questions `/prd-create` will ask):

| Category | What it settles |
|---|---|
| UoD boundary | Which facts this system can represent at all. Distinct from Scope: Scope bounds the *work*, the UoD bounds *representable truth*. |
| Entity types + reference schemes | What counts as one X, and how an X is identified. Catches the classic `user` = auth identity vs billing party collision. |
| Fact types | Elementary predicates, verbalized. One relationship per statement. |
| Constraints | Mandatory/optional roles, uniqueness, frequency, subset/exclusion, ring, value domain. |
| Lifecycle totality | Legal states, legal transitions, and whether the transition table is **total** — every state has a defined exit or is explicitly terminal. |
| Temporality | Does a fact hold at an instant or over an interval? Is a correction distinguishable from a supersession? |
| Modality | **Alethic** (cannot be otherwise → type/schema constraint) vs **deontic** (must not be otherwise → validation rule or alert). Most PRD "shall" statements conflate these, and they compile to different code. |
| Homonyms/synonyms | One term, two meanings; two terms, one meaning. |

**Deterministic score.** Mirror the aers-readiness scoring shape exactly — present-and-substantive `0`, stub `1`, missing `2` — so callers can compose the two scores without learning a second scheme. Per Rule 3 below, an item marked `deferred` with its re-entry condition scores `0`; `unknown` scores `2`. Deferral is free; silence is not. A violation of the mandatory core (Rule 2) scores `2` regardless of how it is marked — those four cannot be deferred.

High-risk semantic ambiguity categories at `2` points each:

- entity with no reference scheme
- term used in a functional requirement but absent from the ontology
- non-total state machine
- fact type with no constraint and no explicit "unconstrained" marker
- alethic/deontic conflation on a load-bearing rule
- unstated temporality on a fact that visibly changes over time
- surviving homonym

**Also specify:** interaction rules (one question at a time; propose a default and confirm; challenge ambiguity rather than smoothing it) copied in spirit from aers-readiness; the `ONTOLOGY.md` output format; and a `## Contract` block with Inputs / Preconditions / Outputs / Postconditions / Failure modes.

### Completeness and Extension

A greenfield PRD is not expected to produce a complete ontology. It produces a *sufficient* one, extended feature by feature. These four rules make that safe; without them the second feature's extension is a migration rather than an append.

**Rule 1 — breadth is discretionary, depth is not.** Which entities and fact types appear at all is scoped to this release; adding entities later is purely additive. But for every entity that *does* appear in the PRD, depth is governed by Rule 2.

**Rule 2 — the mandatory core.** Four categories must be answered for every in-scope entity, because deferring them produces revisionary rather than monotonic growth:

| Must be settled | Why it cannot wait |
|---|---|
| Reference scheme | Changing how an X is identified breaks keys, foreign keys, integrations, and every cached identity assumption simultaneously. |
| Homonym resolution | Cheap now. If "account" ships as one table and later splits into billing entity and auth identity, it is a data migration. |
| Modality of each stated rule | It is a label today. Later it is the difference between a schema constraint, a validation rule, and an alert — and reclassifying means pulling a rule out of the schema. |
| Temporality declaration | Not implementation — *declaration*. "Price is point-in-time; historisation is out of scope this release" is a closed decision. Silence is a defect, because retrofitting history requires a backfill of data that was never recorded. |

Everything else is deferrable: frequency and subset/exclusion constraints, ring constraints, lifecycle totality for unreachable states, open value domains, and any fact type touching an out-of-scope entity.

**Rule 3 — three states per item, not two.** `settled`, `deferred` (with the condition that would bring it into scope), `unknown`. Deferred and unknown render identically as absence, and six months later nobody can tell which they are looking at. This mirrors the AERS `Closed Decisions` / `Open Decisions` split and its instruction not to hide open decisions in narrative prose — reuse that vocabulary. The UoD boundary is what licenses a deferral: it is the positive, checkable claim that these facts are not representable in this release.

**Rule 4 — additions append, revisions halt.** `/prd-create --extend` loads the existing `ONTOLOGY.md` and interrogates only the delta: new entities, plus any `deferred` item the new feature now touches. That short interview is what makes the front-loaded greenfield cost worth paying. But the extension pass must classify each change:

- **Addition** — new entity, new fact type, new optional role, a state appended to a lifecycle whose existing transitions were explicit, a loosened constraint. Appends freely.
- **Revision** — changed reference scheme, homonym split, tightened constraint, reclassified modality, retrofitted temporality. Every downstream artifact (data models, tests, code) is now stale. Halt and surface, per Task 8.

**Acceptance:** the rubric can be applied by hand to an existing PRD in `docs/` and produces a defensible score without the author needing to invent a scoring convention. A deliberately partial ontology — mandatory core settled, six items marked `deferred` — must score `Ready`.

---

## Task 2: Extend `_internal/aers-readiness` with the ontology dimension

```yaml
depends_on: [1]
write_scope:
  - claude/_internal/aers-readiness/SKILL.md
```

- Add **`Domain Ontology`** to *Required Sections in an Execution-Ready AERS*. It points at `ONTOLOGY.md` or inlines the fact types when the domain is small.
- Under *Domain and workflow* in *What to Extract or Create*, replace the current bullet list with a reference to the ontology rubric so the categories are defined in exactly one place.
- Add a sentence under *Data Models* distinguishing ontology from representation (per Closed Decisions).
- Add the semantic ambiguity categories from Task 1 to *Prioritize Ambiguity by Risk*.
- Extend the **Automated readiness check** to fold in the ontology score, including its `settled` / `deferred` / `unknown` handling. A PRD whose ontology is deliberately partial but fully marked must be able to reach `Ready` — otherwise the deferral mechanism is decorative.

**Compatibility risk — handle explicitly.** Every existing artifact in every consumer repo currently scores with no ontology section. Adding one required section (`+2`) plus up to seven ambiguity categories (`+14`) would flip essentially every artifact in existence to `Not ready` (7+), which halts `/execute-prd` and `/kickoff`. Mitigation to specify in the rubric: **cap the ontology contribution at 4 points** in the composite score, and route ontology gaps to a separate `Ontology: Ready / Partial / Absent` line in the verdict rather than letting them dominate the structural score. The structural thresholds (`0–2` / `3–6` / `7+`) stay as they are.

**Acceptance:** re-score `docs/plans/2026-07-08-execute-plan-checkpoint-adversarial-gating.md`'s source PRD under old and new rules. The verdict must not move by more than one band.

---

## Task 3: Rework `/ubiquitous-language` from extractive to derivable

```yaml
depends_on: [1]
write_scope:
  - claude/ubiquitous-language/SKILL.md
```

Current Step 1 is "scan the conversation for domain-relevant nouns" — it harvests terms that were already used, after the fact. That is the wrong end of the pipeline for `/prd-create`, and it is why the skill has no callers.

- Add **`--from-ontology`**: read `ONTOLOGY.md` and generate the glossary as a derived view. Definitions come from the ontology's entity types; the *Relationships* section is generated from fact types with real cardinality instead of "cardinality where obvious"; *Flagged ambiguities* is generated from the rubric's homonym/synonym findings.
- Keep the conversation-scanning mode for legacy use, but retitle it so the derived path is the default reading.
- Add a `## Contract` block. This skill currently has none — verified by grep against `## Contract` across the requirements skills.
- State the source-of-truth rule in the Rules section: when `ONTOLOGY.md` exists, it wins; the glossary is regenerated, never hand-edited.

**Acceptance:** given a hand-written `ONTOLOGY.md`, running the derived mode produces a `UBIQUITOUS_LANGUAGE.md` with no terms absent from the ontology and no ontology entity types missing from the glossary.

---

## Task 4: `/prd-validate` embeds the ontology rubric

```yaml
depends_on: [1, 2]
write_scope:
  - claude/prd-validate/SKILL.md
```

Today this skill scores *structure* — are the thirteen sections present and substantive. It cannot score whether the requirements are semantically well-formed, because there is nothing to check against. Task 1 gives it that.

- **Step 2 (Assess Current State):** add an ontology line to the readiness snapshot.
- **Step 2.5 (Risk-Rank the Gaps):** semantic gaps enter the same risk ranking as structural ones. An undefined load-bearing term outranks a missing Tooling Assumptions section.
- **New Step 3.5 — closure pass.** Run *after* the interview and *after* Step 4 drafts sections, not before. This is the mechanical half of the ontology work and it is where the interrogation gets sharp, because it checks the draft against itself rather than asking modelling questions cold:
  - every noun and verb in Functional Requirements resolves to an ontology term
  - every fact type carries at least one constraint or an explicit unconstrained marker
  - every state has a defined exit or is marked terminal
  - no homonym survives
  - every "shall" is classified alethic or deontic
- **Step 5 (Readiness Verdict):** add the `Ontology:` line from Task 2.
- Update `## Contract` — new embedded rubric, new output artifact (`ONTOLOGY.md` may be written or updated), new failure mode (ontology absent and the domain is non-trivial → report, do not fabricate one).
- **Deprecate `--full-spec`.** It today claims "build a complete AERS through batched interview" from a blank start; per Closed Decisions that is now `/prd-create`'s job. Leave the flag recognised for one release, emitting a pointer rather than running, then remove. Update *When to Use* / *When NOT to Use* and the blank-start entry so `/prd-validate` no longer advertises a blank-start path — including in `_internal/aers-readiness`'s *Entry Modes*, whose "Blank start" prompt should redirect to `/prd-create` (fold this into Task 2's edit).
- Add `--extend` awareness: when the artifact under validation has an `ONTOLOGY.md` marked partial, validate against the marked scope rather than reporting every `deferred` item as a gap.

---

## Task 5: `/spec-review-adversarial` gains a semantic lens

```yaml
depends_on: [1]
write_scope:
  - claude/spec-review-adversarial/SKILL.md
  - claude/spec-review-adversarial/references/ (if reviewer lenses are externalised there)
```

This skill already has the seed: it looks for *Assumed context* ("references to systems, processes, or terms not defined in the document") and *Undefined terms* ("a term is used but never defined, or defined differently in different places"). Promote those two bullets into a first-class lens driven by the Task 1 rubric, covering homonym, synonym, unstated cardinality, non-total state machine, and modality conflation.

Add `ONTOLOGY.md` as an optional input: when present, the lens checks the spec *against* it rather than inferring the vocabulary from the spec alone. Add a `## Contract` block — this skill also lacks one.

---

## Task 6: `/prd-acceptance` verifies ontology invariants

```yaml
depends_on: [1]
write_scope:
  - claude/prd-acceptance/SKILL.md
```

Every constraint in `ONTOLOGY.md` is a testable assertion about the delivered system: a uniqueness constraint is a duplicate-insert test, a mandatory role is a null-rejection test, a total state machine is an exhaustive transition test. Today acceptance only walks the PRD's acceptance criteria, which routinely omit these because they felt too obvious to write down.

Add a step after the criteria walk: verify ontology constraints as first-class acceptance items, reported in the same pass/fail-with-evidence format.

---

## Task 7: Feed the ontology into `/test-plan`'s analysts

```yaml
depends_on: [1]
write_scope:
  - claude/test-plan/SKILL.md
  - claude/test-plan/analysts/boundary-validation/SKILL.md
  - claude/test-plan/analysts/state-lifecycle/SKILL.md
  - claude/test-plan/analysts/contract-compliance/SKILL.md
```

The analyst set already maps onto the constraint taxonomy almost one-to-one — this is the highest-leverage task in the plan and it needs the least invention:

| Ontology output | Analyst |
|---|---|
| Value domains | `boundary-validation` |
| Lifecycle totality, state transitions | `state-lifecycle` |
| Uniqueness, mandatory roles, fact-type arity | `contract-compliance` |
| Fact types crossing a system edge | `integration-surface` |

Add `ONTOLOGY.md` as an optional input to the controller and pass the relevant slice to each analyst, so test cases are *derived* from constraints instead of re-derived from prose by each analyst independently.

---

## Task 8: Rewire the autonomous gates

```yaml
depends_on: [2]
write_scope:
  - claude/kickoff/SKILL.md
  - claude/execute-prd/SKILL.md
  - claude/execute-plan/SKILL.md
```

All three reference `_internal/aers-readiness`. Once Task 2 changes the score they need updating:

- `/kickoff` step 3 and `/execute-prd` step 4: handle the new `Ontology:` verdict line alongside the structural verdict.
- Decide autonomous-mode behaviour. Recommended, consistent with the existing "suggest, don't auto-invoke" doctrine: ontology `Absent` on a non-trivial domain logs a known risk and proceeds; ontology `Absent` **plus** structural `Partially ready` halts. Never auto-invoke `/prd-create` — it is an interview, same interaction boundary as `/prd-validate`.
- **Extend the reopened-decision halt to ontology revisions.** `/kickoff`'s failure modes already include "any closed decision in the artifact reopened → halt and surface the conflict." An ontology revision in the Rule 4 sense — changed reference scheme, homonym split, tightened constraint, reclassified modality, retrofitted temporality — is exactly that, and must route through the same halt. Ontology *additions* pass through untouched. State the addition/revision distinction in the failure-mode line so it is checkable rather than a judgement call.
- Update the `## Contract` lines in all three to name the new rubric.
- `/postmortem` also references aers-readiness; check whether it needs the same edit or is only citing the term.

---

## Task 9: Front-of-pipeline handoffs

```yaml
depends_on: [1]
write_scope:
  - claude/goal/SKILL.md
  - claude/thesis/SKILL.md
```

Light touch, but the chain is currently broken at the top — `/goal`'s "When NOT to Use" sends the user to `/prd-validate`, which assumes an artifact already exists.

- `/goal`: point the completed outcome statement at `/prd-create`, not `/prd-validate`.
- `/thesis`: add one line noting that the thesis sentence functions as the UoD boundary test — it is what lets you say "that entity isn't in this world." Add a `## Contract` block (also missing).

---

## Task 10: Index, policy, and installer

```yaml
depends_on: [1, 2, 3, 4, 5, 6, 7, 8, 9]
write_scope:
  - claude/README.md
  - claude/_internal/README.md
  - claude/skill-help/SKILL.md
  - claude/MODEL-POLICY.md
```

- `claude/README.md`: add `prd-create` and the ontology rubric to the *Requirements, Design & BA* table. Rewrite the *Typical flow* section, which currently starts at "read the artifact" and has no upstream at all — it should read `/goal` → `/thesis` (optional) → `/prd-create` → `/prd-validate` → plan → execute.
- `_internal/README.md`: add `ontology-readiness` to the `kind: reference` example list.
- `skill-help`: it already indexes both `aers-readiness` and `ubiquitous-language`; add the new entries.
- `MODEL-POLICY.md`: `/prd-create` is a once-per-task, deep-reasoning, structured-artifact skill — the exact profile the doc describes for `model: opus`. Add it to the pinned list when the skill lands.
- Confirm no `manifest.json` change is needed (see Non-goals).

---

## Deferred: Task 11 — cross-platform parity

`codex/plugins/savviety-workflows/skills/` carries mirrors of `prd-validate`, `prd-acceptance`, `spec-review-adversarial`, `ubiquitous-language`, and `test-plan`, each with an `aers-readiness.md` reference copy. `copilot/` and `kimi/` have their own. Port after `/prd-create` ships and the shape has settled, using `.claude/skills/port-skill`. Porting now means porting twice.

---

## Sequencing

```
1 ──┬── 2 ──── 8
    ├── 3
    ├── 4  (also needs 2)
    ├── 5
    ├── 6
    ├── 7
    └── 9
              └── 10 (last)
```

Task 1 is the only true blocker. Tasks 3, 5, 6, 7, 9 are independent of each other and parallelisable. Task 10 is the closing pass.

## Risks

- **Score inflation.** Task 2's mitigation is the load-bearing part of this plan. If the composite score is not capped, every existing artifact flips to `Not ready` and the autonomous gates jam. Test this before merging Task 2, not after.
- **Modelling theatre.** A full ORM-style fact-type decomposition is overkill for a CRUD feature. Task 1's Rule 3 is the mitigation: proportionality comes from *auditable deferral*, not from skipping. Watch for the failure where `deferred` becomes a reflex — if a review shows most deferrals carry no re-entry condition, the marker has degraded into a synonym for `unknown` and the scoring incentive has inverted.
- **Mandatory-core erosion.** Rule 2's four categories are the entire load-bearing content of the deferral scheme. The first time someone defers a reference scheme "just for the spike," the extension path stops being additive. This needs to be a hard failure in the rubric, not a warning.
- **Two sources of truth.** If `UBIQUITOUS_LANGUAGE.md` stays hand-editable after Task 3, it will drift from `ONTOLOGY.md` within a release and nobody will know which one the requirements were written against. The regenerate-only rule needs to be stated as a rule, not a convention.
- **Boundary creep between `/prd-create` and `/prd-validate`.** Task 4's `--full-spec` resolution is the seam. Leave it unresolved and both skills will grow toward each other.
