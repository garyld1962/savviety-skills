---
name: spec-review-adversarial
description: "Adversarially review PRDs, requirements, user stories, or acceptance criteria using 1–4 lens reviewers (Skeptic, Coherence, Semantic, Devil's Advocate). The Semantic lens checks the deliverable against its sibling ONTOLOGY.md. Returns PASS/CONTESTED/REJECT."
model: opus
---

# /spec-review-adversarial — Adversarial Review of Specifications

**Purpose:** Stress-test business analysis work products (requirements, user stories, acceptance criteria, process flows) by applying adversarial reviewer lenses. Finds gaps, contradictions, and ambiguities BEFORE they become code defects. This skill reviews BA deliverables, not code -- use /domain-review for code.

## When to Use

- A BA has produced requirements, user stories, or acceptance criteria for review
- You want to validate a PRD or feature specification before implementation begins
- A work item's acceptance criteria need a quality check
- You are about to start a sprint and want to catch ambiguity early

## When NOT to Use

- You need to review code -- use /domain-review
- You need to review a code review -- use /review-gauntlet
- The deliverable is purely technical (architecture doc, API spec) -- use /domain-review or a technical review

## Usage

```
/spec-review-adversarial <file-or-text>
/spec-review-adversarial docs/requirements/auth-flow.md
/spec-review-adversarial --ado 12345
/spec-review-adversarial --linear BF-42
/spec-review-adversarial --phase discovery
/spec-review-adversarial docs/prds/order-capture/PRD.md --ontology docs/prds/order-capture/ONTOLOGY.md
```

## Arguments

- `<file-or-text>` -- path to the BA deliverable or inline text to review
- `--ado <item-id>` -- fetch the work item from ADO and review its description + acceptance criteria
- `--linear <issue-id>` -- fetch the issue from Linear and review its description + acceptance criteria
- `--phase <phase>` -- override automatic phase detection (discovery, analysis, specification, validation)
- `--ontology <path>` -- path to the `ONTOLOGY.md` the Semantic lens checks against. Defaults to the deliverable's sibling `ONTOLOGY.md` (`docs/prds/<slug>/ONTOLOGY.md` when the deliverable lives in that folder). A legacy bare `.md` deliverable has no sibling, so the default resolves to nothing and the Semantic lens runs in inference mode.

## Step 1: Load the Deliverable

Obtain the BA work product:

1. If a file path is provided, read the file
2. If `--ado` or `--linear` is provided, use /work-item to fetch it
3. If inline text is provided, use that directly

Identify the deliverable type:
- **Requirements document** -- contains "shall", "must", "requirement", numbered items
- **User stories** -- contains "As a ... I want ... so that"
- **Acceptance criteria** -- contains "Given/When/Then" or checkbox lists
- **Process flow** -- contains sequential steps, decision points, swim lanes
- **PRD** -- contains sections like Overview, Goals, User Personas, Features

## Step 2: Detect Phase

Determine the BA phase to select appropriate lenses. Auto-detect from deliverable type, or use `--phase` override:

| Phase | Typical Deliverables | Lenses |
|-------|---------------------|--------|
| **Discovery** | Problem statement, stakeholder needs, market context | Skeptic, Devil's Advocate |
| **Analysis** | Requirements, process flows, gap analysis | Skeptic, Coherence, Semantic, Devil's Advocate |
| **Specification** | User stories, acceptance criteria, detailed requirements | Skeptic, Coherence, Semantic |
| **Validation** | Test plans mapped to requirements, traceability matrix | Coherence, Devil's Advocate |

## Step 3: Apply Reviewer Lenses

### Skeptic Lens

The Skeptic questions every assumption and asks "how do you know?"

Checks for:
- **Unsupported claims.** "Users prefer X" -- based on what evidence?
- **Vague quantifiers.** "Fast", "easy", "most users", "seamless" -- define the threshold
- **Missing metrics.** Success criteria without measurable targets
- **Assumed context.** References to systems, processes, or terms not defined in the document. Vocabulary gaps belong to the **Semantic Lens** -- raise them there as `[ONTOLOGY-<N>]`, not here
- **Happy path bias.** Only describes what happens when everything works. What about errors, edge cases, timeouts, partial failures?
- **Missing personas.** Who is "the user"? Are there different user types with different needs?

Finding format:
```
[SKEPTIC-<N>] <severity> | Section: <reference>
  Claim: "<quoted text>"
  Challenge: <what is wrong or missing>
  Evidence needed: <what would resolve this>
```

### Coherence Lens

The Coherence reviewer checks internal consistency and completeness.

Checks for:
- **Contradictions.** Section A says X, Section B says not-X
- **Gaps in flow.** Step 3 produces output Y, but Step 4 expects input Z
- **Undefined terms.** A term is used but never defined, or defined differently in different places. When the Semantic Lens is active it owns term resolution and homonyms -- raise those as `[ONTOLOGY-<N>]`, not here
- **Orphaned requirements.** A requirement is stated but no acceptance criteria cover it
- **Orphaned acceptance criteria.** AC exists but traces to no requirement
- **Missing states.** A status field has values A, B, C but the flow only describes transitions for A and B
- **Boundary ambiguity.** "Up to 10 items" -- is 10 included? What happens at 11?
- **Implicit ordering.** Steps described without specifying whether they are sequential, parallel, or unordered
- **Missing required sections.** When the deliverable is a **PRD or AERS**, check it against the Required Sections list in `_internal/aers-readiness`. Report each absent or stub section as a Coherence finding naming the section. Do not restate that skill's scoring -- cite it and report the gap. `Domain Ontology` is the one section whose absence is a Semantic finding rather than a Coherence one, because it is scored by the ontology check

Finding format:
```
[COHERENCE-<N>] <severity> | Sections: <ref-A> vs <ref-B>
  Conflict: <what contradicts or is incomplete>
  Impact: <what goes wrong if this is not resolved>
  Suggestion: <how to fix>
```

### Semantic Lens

The Semantic reviewer checks that each term in the deliverable denotes exactly one thing, and that what the deliverable asserts about those things is identified, constrained, total, classified, and dated.

**Resolve the mode first.** Before running any check:

1. Use `--ontology <path>` if given.
2. Otherwise use the deliverable's sibling `ONTOLOGY.md` -- `docs/prds/<slug>/ONTOLOGY.md` when the deliverable lives in that folder. A legacy bare `.md` deliverable has no sibling.
3. If neither resolves to a readable file, run in **inference mode**.

In **ontology mode** every check below is a lookup against the ontology: term resolution, constraint presence, and lifecycle totality are decided by whether a row exists and what it says. In **inference mode** the same checks run against vocabulary inferred from the deliverable itself; the reviewer cannot distinguish "term missing from the ontology" from "no ontology exists", so inference-mode findings are capped at **Medium** and the report must state that the lens ran in inference mode. If the ontology resolves to a file that does not parse as the `ONTOLOGY.md` format, report that as a Blocker and stop the lens -- do not fall back to inference and do not guess at the intended rows.

The categories, the `ONTOLOGY.md` format, and the item-state vocabulary (`settled` / `deferred` / `unknown`) are defined in `_internal/ontology-readiness`. Read them there. This lens emits findings; it does not compute the `Ontology:` verdict or any score -- that belongs to the rubric and its callers.

Checks -- one per high-risk semantic ambiguity category in `_internal/ontology-readiness` § *Automated ontology check*, in that order:

| Category | Look at | Fires when |
|---|---|---|
| **entity with no reference scheme** | Each entity the deliverable defines or changes | Ontology mode: the entity's row has no reference scheme, or its reference scheme is `deferred`/`unknown`. Inference mode: the deliverable names the entity and never says what makes two mentions the same one |
| **term used in a functional requirement but absent from the ontology** | Every distinct noun and verb phrase in Functional Requirements | Ontology mode: the term matches no entity, fact type, or state name. Inference mode: the term is used in a requirement and defined nowhere in the deliverable |
| **non-total state machine** | Each state or status field, and its transitions | A listed state has no defined exit transition and is not marked terminal |
| **fact type with no constraint and no explicit `[unconstrained]` marker** | The Constraints cell of each fact type; in inference mode, each asserted relationship | The cell is blank or absent. `[unconstrained]` does not fire it, and neither does generic-but-present text such as "standard validation" -- that is a stub for the rubric to charge, not an ambiguity finding here |
| **alethic/deontic conflation on a load-bearing rule** | Each "shall" / "must" / "must not" the implementation has to enforce | The rule carries no classification as alethic (cannot be otherwise -> schema constraint) or deontic (must not be otherwise -> validation rule or alert), and the two would compile to different code. If the classification does not change the code, the rule is not load-bearing -- do not report it |
| **unstated temporality on a fact that visibly changes over time** | Facts the deliverable itself shows changing: price, status, assignment, address, role | Neither the ontology nor the deliverable states whether the fact holds at an instant or over an interval, nor whether historisation is in scope this release |
| **surviving homonym** | Terms used in more than one section | Two usages resolve to different entities or different reference schemes and no split is recorded. The mirror case -- two terms, one meaning -- is reported under this category as a synonym |

Finding format:
```
[ONTOLOGY-<N>] <severity> | Category: <one of the seven above> | Section: <reference>
  Term: "<the term, fact type, or rule as written>"
  Ambiguity: <the competing readings, or the declaration that is missing>
  Resolves to: <the ontology row or declaration that would close it>
  Mode: <ontology: <path> | inference (no ontology found)>
```

Severity: in ontology mode, an unresolved **entity with no reference scheme**, **surviving homonym**, **alethic/deontic conflation**, or **unstated temporality** is a Blocker -- these four are the mandatory core, and each is a data migration once code exists. The other three are High or below unless the ambiguity would demonstrably produce wrong code. In inference mode nothing exceeds Medium.

### Devil's Advocate Lens

The Devil's Advocate argues the opposite position and stress-tests decisions.

Checks for:
- **Alternative approaches.** "We chose X" -- why not Y? What was the trade-off analysis?
- **Worst-case scenarios.** What if this feature is used maliciously? At 100x expected scale? By a confused user?
- **Stakeholder conflicts.** Does this serve all stakeholders, or does it optimize for one at the expense of another?
- **Future fragility.** This design works now, but what known upcoming changes would break it?
- **Reversibility.** If this decision is wrong, how hard is it to undo?
- **Second-order effects.** If we do X, what does that imply for Y and Z?

Finding format:
```
[DEVIL-<N>] <severity> | Section: <reference>
  Position: "<the decision or claim being challenged>"
  Counter: <the opposing argument>
  Risk if ignored: <what could go wrong>
```

## Step 4: Severity Classification

Each finding is classified:

| Severity | Meaning |
|----------|---------|
| **Blocker** | Cannot proceed to implementation. Ambiguity or contradiction will cause incorrect code. |
| **High** | Significant gap that will likely cause rework or defects if not addressed. |
| **Medium** | Unclear area that could lead to misinterpretation. Should be clarified. |
| **Low** | Minor improvement. Nice to have but not blocking. |

## Step 5: Lead Judgment (Filter False Positives)

Before filtering, engage extended thinking to reason privately:
- Which findings would concretely cause wrong code to be written if left unresolved?
- Which Blockers can be safely downgraded without any implementation risk?
- Did the lenses miss anything by focusing on individual sections rather than the whole artifact?
- Do the Medium findings form a pattern that collectively deserves a High?
- Is the current Blocker count calibrated to genuine implementation risk, or to adversarial thoroughness?

Use that reasoning to guide the filter pass.

After thinking, apply lead judgment to filter results:

1. **Remove pedantic findings.** If a finding is technically correct but practically irrelevant (e.g., "you said 'fast' but in context the SLA is clearly defined elsewhere"), discard it.
2. **Merge duplicates.** If two lenses flag the same issue, keep the one with the better explanation. When one of them is the Semantic lens and the issue is a vocabulary defect, keep the `[ONTOLOGY-<N>]` finding.
3. **Downgrade over-severity.** If a finding is marked Blocker but the impact is actually limited, downgrade it.
4. **Preserve genuine issues.** Do not filter findings just because they are uncomfortable. The point is to find real problems.

Mark filtered findings with a note: `[Filtered: <reason>]`

## Step 6: Verdict

Calculate the verdict from unfiltered findings:

| Verdict | Criteria |
|---------|----------|
| **PASS** | 0 Blockers, 0 High. Deliverable is ready for implementation. |
| **CONTESTED** | 0 Blockers, >=1 High. Deliverable needs targeted revisions. |
| **REJECT** | >=1 Blocker. Deliverable has fundamental issues that must be resolved before implementation. |

## Step 7: Report

```
BA Adversarial Review: <deliverable title or file>

  Phase:    <Discovery | Analysis | Specification | Validation>
  Lenses:   <list of lenses applied>
  Ontology: <path to the ONTOLOGY.md checked against | none -- Semantic lens ran in inference mode>
  Verdict:  <PASS | CONTESTED | REJECT>

Findings: <total> (<N> Blocker, <N> High, <N> Medium, <N> Low)
Filtered: <N> findings removed by lead judgment

---

<findings grouped by lens, ordered by severity>

---

Summary
  <2-3 sentence overall assessment>

Recommended Actions
  1. <most critical action>
  2. <next action>
  ...

Tracking: <ADO/Linear reference if provided>
```

## Key Rules

1. **BA deliverables, not code.** This skill reviews requirements, stories, and criteria. For code, use /domain-review.
2. **Specific, evidence-based findings.** Every finding must cite a specific section, quote the relevant text, and explain the issue concretely. "This could be clearer" is not a finding.
3. **Lead judgment is mandatory.** Raw adversarial output is noisy. The filtering step separates signal from pedantry.
4. **"I would have written it differently" is NOT a finding.** Style preferences are not defects. Only flag issues that would cause implementation problems.
5. **Respect the phase.** Discovery deliverables are intentionally less precise than specifications. Apply phase-appropriate standards.
6. **Severity must be justified.** A Blocker must explain what specific implementation harm results. If you cannot articulate the harm, it is not a Blocker.

## Contract

- **Inputs:** a BA deliverable as a file path, inline text, or `--ado <id>` / `--linear <id>` (delegates to `/work-item`); optional `--phase <phase>`; optional `--ontology <path>`, defaulting to the deliverable's sibling `docs/prds/<slug>/ONTOLOGY.md`. Reads `_internal/ontology-readiness` for the semantic ambiguity categories and the `ONTOLOGY.md` format, and `_internal/aers-readiness` for the Required Sections list when the deliverable is a PRD or AERS.
- **Preconditions:** the deliverable is readable text; tracker auth if `--ado`/`--linear`. No ontology is required -- its absence selects inference mode, it does not block the review.
- **Outputs:** a report per Step 7 carrying the phase, the lenses applied, the ontology path or `none`, a verdict of `PASS` / `CONTESTED` / `REJECT`, and findings in the `[SKEPTIC-<N>]`, `[COHERENCE-<N>]`, `[ONTOLOGY-<N>]`, and `[DEVIL-<N>]` formats, each with a severity and a cited section.
- **Postconditions:** the deliverable is not modified; findings are advisory. Filtered findings are shown with `[Filtered: <reason>]` rather than deleted. The verdict follows Step 6 from the unfiltered findings only.
- **Failure modes:** deliverable unreadable → halt and report the file-access error, do not review from the filename. Ontology absent (no `--ontology`, no sibling `ONTOLOGY.md`) → the Semantic lens runs in inference mode, caps its findings at Medium, and the report states it. Ontology present but unparseable → report it as a Blocker and say the Semantic lens could not run; do not fall back to inference and do not guess at the intended rows. No ontology verdict or score is computed here -- that is `_internal/ontology-readiness`' job.
