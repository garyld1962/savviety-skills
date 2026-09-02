---
name: ontology-readiness
description: "Reusable rubric defining ontology readiness for a requirements artifact — elicitation categories, item states, completeness and extension rules, the ONTOLOGY.md format, and a deterministic ontology score. Composed into _internal/aers-readiness; remedied interactively by /prd-create; consumed by /prd-validate, /ubiquitous-language --from-ontology, /prd-acceptance, /test-plan, and /spec-review-adversarial. Not user-invokable."
user-invocable: false
internal: true
kind: reference
---

# Ontology Readiness Rubric

Use this skill to evaluate or shape the **semantic** half of a requirements
artifact: what exists in the world the system is about, how it is identified,
what may be said about it, and what may not.

**Artifact:** `docs/prds/<slug>/ONTOLOGY.md`, beside the PRD it describes.

**Notation:** verbalized natural-language fact types in Markdown. No OWL, no
RDF, no ORM diagram syntax. "A **Customer** places zero or more **Orders**" —
readable by a stakeholder, checkable by an agent.

## When to Use

- Scoring the semantic readiness of a PRD or an `ONTOLOGY.md`
- Composing the `Ontology:` verdict line into `_internal/aers-readiness`
- You need the authoritative definition of settled / deferred / unknown
- You need the authoritative `ONTOLOGY.md` format

## When NOT to Use

- You want an interactive interview to build or extend an ontology — use `/prd-create`
- You want to score the artifact's *structure* — use `_internal/aers-readiness`
- You want a glossary — use `/ubiquitous-language --from-ontology`, which derives one
- The domain is trivial by the test in **Automated ontology check** — do not manufacture modelling work

## Relationship to Other Skills

- Composes into `_internal/aers-readiness`: this rubric produces the `Ontology:` line and a capped composite contribution; aers-readiness owns the structural score.
- `/prd-create` is the interactive remedy — it runs this rubric's elicitation categories as an interview and writes the `ONTOLOGY.md`. It is an interview: never auto-invoke it.
- `/prd-validate` runs the closure pass (every noun and verb in Functional Requirements resolves to an ontology term; every fact type constrained or explicitly marked; every state has an exit; no surviving homonym; every "shall" classified).
- `/ubiquitous-language --from-ontology` derives `UBIQUITOUS_LANGUAGE.md` as a view. When `ONTOLOGY.md` exists it wins; the glossary is regenerated, never hand-edited.
- `/prd-acceptance` and `/test-plan` consume the constraints: a uniqueness constraint is a duplicate-insert test, a mandatory role is a null-rejection test, a total lifecycle is an exhaustive transition test.
- `/spec-review-adversarial` uses the ambiguity categories below as a semantic lens.
- `/kickoff` and `/execute-prd` gate on the verdict, reached through aers-readiness.

## Interaction Rules

Applied by `/prd-create`, not by this rubric (a rubric asks nothing):

- Ask one question at a time.
- Prefer multiple-choice with a recommended default; explain why the question matters.
- Challenge ambiguity instead of smoothing over it. "Both, probably" is a homonym, not an answer.
- If the user says "you choose", propose a default and ask for confirmation.
- Never invent a reference scheme, a modality, or a temporality to close a gap. `unknown` is an honest answer; a fabricated one is not.

## Elicitation Categories

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

**Ontology is not Data Models.** The ontology describes the world; `Data Models`
describes the representation. The ontology *feeds* `Data Models` and
`Closed Decisions`. Keep them separate or they collapse into each other within
a release, and the world becomes whatever the current schema happens to be.

### Item states

Every elicited item carries exactly one of three states. This is the single
definition of these words in this repo; other skills cite it rather than
redefining it.

| State | Meaning | Renders as | Score |
|---|---|---|---|
| `settled` | Decided. Maps to the AERS **Closed Decisions** section. | A row with an answer. | 0 |
| `deferred` | Out of the UoD this release, **plus the re-entry condition** that would bring it in. Maps to AERS **Open Decisions**. | A row in `## Deferred` with its condition. | 0 |
| `unknown` | Nobody has decided, or nobody knows. Also maps to **Open Decisions**. | A row in `## Unknown` with why. | 2 |

Deferred and unknown otherwise render identically as absence, and six months
later nobody can tell which they are looking at. As in the AERS rubric, do not
hide open decisions in narrative prose — they go in the table.

A `deferred` item **without** a re-entry condition is not deferred. Score it as
`unknown`. If a review shows most deferrals carry no condition, the marker has
degraded into a synonym for `unknown` and the scoring incentive has inverted.

**Deferral is free; silence is not.**

## Completeness and Extension

A greenfield PRD is not expected to produce a complete ontology. It produces a
*sufficient* one, extended feature by feature. These four rules make that safe;
without them the second feature's extension is a migration rather than an append.

**Rule 1 — breadth is discretionary, depth is not.** Which entities and fact
types appear at all is scoped to this release; adding entities later is purely
additive. But for every entity that *does* appear in the PRD, depth is governed
by Rule 2.

**Rule 2 — the mandatory core.** Four categories must be answered for every
in-scope entity, because deferring them produces revisionary rather than
monotonic growth:

| Must be settled | Why it cannot wait |
|---|---|
| Reference scheme | Changing how an X is identified breaks keys, foreign keys, integrations, and every cached identity assumption simultaneously. |
| Homonym resolution | Cheap now. If "account" ships as one table and later splits into billing entity and auth identity, it is a data migration. |
| Modality of each stated rule | It is a label today. Later it is the difference between a schema constraint, a validation rule, and an alert — and reclassifying means pulling a rule out of the schema. |
| Temporality declaration | Not implementation — *declaration*. "Price is point-in-time; historisation is out of scope this release" is a closed decision. Silence is a defect, because retrofitting history requires a backfill of data that was never recorded. |

Everything else is deferrable: frequency and subset/exclusion constraints, ring
constraints, lifecycle totality for unreachable states, open value domains, and
any fact type touching an out-of-scope entity.

**Hard failure.** A mandatory-core item marked `deferred` or `unknown` scores
**2** regardless of how it is marked, and **caps the verdict at `Partial`** no
matter how low the total. These four are the entire load-bearing content of the
deferral scheme. The first time a reference scheme is deferred "just for the
spike", the extension path stops being additive. This is a failure, not a
warning.

**Rule 3 — three states per item, not two.** See **Item states** above. The UoD
boundary is what licenses a deferral: it is the positive, checkable claim that
these facts are not representable in this release. A deferral against a stub UoD
boundary is not licensed.

**Rule 4 — additions append, revisions halt.** `/prd-create --extend` loads the
existing `ONTOLOGY.md` and interrogates only the delta declared by `scope:` and
`extends:`: new entities, plus any `deferred` item the new feature now touches.
That short delta interview is what makes the front-loaded greenfield cost worth
paying. Every change is classified into exactly one of two classes, and the
class is recorded in the Extension Log:

- **`addition`** — new entity, new fact type, new optional role, a state appended to a lifecycle whose existing transitions were explicit, a loosened constraint. Appends freely.
- **`revision`** — one of exactly five kinds: changed reference scheme, homonym split, tightened constraint, reclassified modality, retrofitted temporality. Every downstream artifact (data models, tests, code) is now stale. Halt and surface.

## ONTOLOGY.md format

Location: `docs/prds/<slug>/ONTOLOGY.md`. Header field names are exact —
`/prd-create --extend` and `/prd-validate` read them.

```
# Ontology: <slug>
mode: greenfield | feature | refresh | rewrite
extends: docs/prds/<prev-slug>/ONTOLOGY.md | none
scope: <entities in this release>
uod: Representable: … / Not representable this release: …
seeded-from-code: yes @ <git sha> | no (--no-scan) | n/a (greenfield)
thesis: <one sentence>
status: settled N · deferred N · unknown N · mandatory core: complete | INCOMPLETE

## Entity Types
| Entity | Reference scheme | Homonym resolution | Status | Source |

## Fact Types
| # | Verbalized fact type | Constraints | Modality | Status | Source |
| F1 | A **Customer** places zero or more **Orders** | mandatory: Order→Customer; unique: Order.number | alethic | settled | interview |

## Lifecycles
### <Entity> — Total: yes | no (missing exits: …)
| From | Event | To | Guard | Status |
Terminal: …

## Temporality
| Fact / attribute | Instant or interval | Correction vs supersession distinguishable | Status |

## Deferred (with re-entry condition)
| Item | Category | Re-entry condition |

## Unknown
| Item | Category | Why unknown |

## Extension Log
| Date | Change | Class | Result |
```

Rules the format encodes:

- Every row carries `settled`, `deferred`, or `unknown`.
- Mandatory-core rows — reference scheme, homonym resolution, modality of each rule, temporality declaration — can only be `settled`.
- The Constraints column may read `[unconstrained]`. It may never be blank: blank is an omission, `[unconstrained]` is a decision.
- `Source` is `interview`, `code:<file:line>`, or a path to a prior ontology. Items seeded from a code scan enter as `unknown` with a `code:` source until a human settles them — a scan reports what the code does, which is not evidence of what the domain requires.
- The Extension Log is append-only. `Class` is `addition` (appended) or `revision` (halted, then confirmed or rejected).

## Automated ontology check

Deterministic. Do not invent a variant.

**Per-category score**, over the eight **Elicitation Categories**, mirroring
`_internal/aers-readiness` so the two scores compose without a second scheme:

- **Present and substantive** — at least one concrete row or sentence specific to this work → **0 points**.
- **Present but stub** — heading or column exists, body is "TBD" / empty / generic boilerplate → **1 point**.
- **Missing entirely** → **2 points**.

Then, per **Item states**: an item marked `deferred` with a re-entry condition
scores **0**; `unknown` scores **2**; a mandatory-core item that is not `settled`
scores **2** and caps the verdict at `Partial`.

**High-risk semantic ambiguity categories**, each unresolved one adds **2 points**:

- entity with no reference scheme
- term used in a functional requirement but absent from the ontology
- non-total state machine
- fact type with no constraint and no explicit `[unconstrained]` marker
- alethic/deontic conflation on a load-bearing rule
- unstated temporality on a fact that visibly changes over time
- surviving homonym

**Mode-aware scoring.** In `greenfield` and `refresh`, score the whole ontology.
In `feature` and `rewrite`, score only the delta declared by `scope:` and
`extends:` — pre-existing settled rows are not re-scored. Any `revision:` entry
in the Extension Log is flagged in the verdict: in `feature` mode it is a halt
condition for callers (`/kickoff` and `/execute-prd` route it through their
reopened-decision halt); in `rewrite` mode it must be matched by a confirmed
closed decision in the PRD, and is a halt if it is not.

**Trivial domain.** Count the distinct entity types the artifact requires the
system to represent, across its Functional Requirements and Data Models, within
the mode's scoring window — so a change spec against an existing codebase counts
only the entity types its delta introduces or redefines, not the ones it merely
edits around. If that count is fewer than three **and** the artifact declares no
state or status field, the domain is trivial: a missing `ONTOLOGY.md` reports
`Ontology: Absent (trivial domain)` and contributes **0** to the composite.
Modelling theatre is a real cost; proportionality comes from auditable deferral,
not from ceremony over a two-noun domain.

### Verdict

```
Ontology: Ready / Partial / Absent
```

| Total points | Verdict | Caller behavior |
|---|---|---|
| `0–2` | **Ready** | Proceed. |
| `3–6` | **Partial** | Suggest `/prd-create --extend` or `/prd-validate` to the operator; do not auto-invoke. In autonomous mode, log the gap list as a known risk and proceed. |
| `7+`, or `ONTOLOGY.md` missing on a non-trivial domain | **Absent** | Log a known risk. Combined with a structural verdict of `Partially ready` or worse, halt. |

```
Composite contribution: Ready → 0, Partial → +2, Absent → +4 (cap 4)
```

The cap is load-bearing. Uncapped, one required section (+2) plus seven
ambiguity categories (+14) flips every artifact written before this rubric
existed to `Not ready`, jamming `/kickoff` and `/execute-prd`. Ontology gaps get
their own verdict line; they do not dominate the structural score, whose
thresholds (`0–2` / `3–6` / `7+`) are unchanged.

### Why "suggest, don't auto-invoke"

`/prd-create` is an interview, not a gate. Auto-invoking it from a
non-interactive context (CI, autonomous run, scheduled agent) hangs waiting for
input. The score is the gate; the interview is the remedy.

## Worked example

`docs/prds/2026-09-02-order-capture/ONTOLOGY.md`, deliberately partial. Header:

```
mode: greenfield
extends: none
scope: Customer, Order, OrderLine, Product
uod: Representable: orders placed by one customer against catalogue products, and their fulfilment state. Not representable this release: partial shipments, returns, multi-currency pricing, customer merges.
seeded-from-code: n/a (greenfield)
status: settled 14 · deferred 6 · unknown 0 · mandatory core: complete
```

Mandatory core, all `settled`: reference schemes (`Customer.customer_number`
issued by the CRM; `Order.order_number`; `OrderLine` identified by
`(Order, line_no)`; `Product.sku`); homonym resolution ("account" split into
`Customer` and `LoginIdentity`, the latter out of the UoD); modality on all five
fact types (four alethic, one deontic — "an Order **must not** ship before
payment clears" is a validation rule, not a schema constraint); temporality
declared (`Product.price` is point-in-time, historisation out of scope, stated
as a closed decision).

Six deferred items, each with a re-entry condition:

| Item | Category | Re-entry condition |
|---|---|---|
| `Shipment` lifecycle | Lifecycle totality | When partial shipments enter scope |
| Subset constraint: OrderLine.discount ⊆ Product.eligible_discounts | Constraints | When promotional pricing ships |
| Ring constraint on Customer.referred_by | Constraints | When referrals ship |
| Currency value domain | Constraints | When a non-GBP market opens |
| Correction vs supersession on Order.total | Temporality | When finance requires a restatement audit trail |
| `Return` entity and its fact types | Entity types | When returns enter scope |

Score, line by line:

| Category | Finding | Points |
|---|---|---|
| UoD boundary | Both halves stated, names the excluded facts | 0 |
| Entity types + reference schemes | Four entities, each with a reference scheme | 0 |
| Fact types | Five verbalized, one predicate each | 0 |
| Constraints | Present, but three of five rows read "standard validation" rather than a named constraint kind — generic boilerplate | 1 |
| Lifecycle totality | `Order` table marked `Total: yes`, terminal states `Cancelled`, `Delivered`; `Shipment` deferred with condition | 0 |
| Temporality | Declared for `Product.price` and `Order.placed_at`; one row deferred with condition | 0 |
| Modality | All five rules labelled alethic or deontic | 0 |
| Homonyms/synonyms | "account" resolved; no survivor | 0 |
| Deferred items (6) | All carry a re-entry condition | 0 |
| Mandatory core | Complete — no cap applied | 0 |
| Ambiguity categories (7) | None fire | 0 |
| **Total** | | **1** |

```
Ontology: Ready
```

Total `1` is inside `0–2`. The margin is thin on purpose: one more stub, or any
single ambiguity category firing, moves this to `Partial`. Had any one of the
six deferrals lost its re-entry condition it would score `unknown` (2), and the
artifact would land at `3` — `Partial`. Had the `Customer` reference scheme been
among the deferrals, the mandatory-core cap would force `Partial` at any total.

## Contract

- **Inputs:** a requirements artifact (PRD, AERS, spec), and optionally `docs/prds/<slug>/ONTOLOGY.md`. For `feature` and `rewrite` modes, also the prior ontology named by `extends:`.
- **Preconditions:** the artifact is text and readable. This is a reference rubric, not an interview — `/prd-create` is the interactive remedy and requires a supervising human.
- **Outputs:** an `Ontology: Ready / Partial / Absent` verdict line; a capped composite contribution per **Automated ontology check**; a gap list keyed to the eight elicitation categories, the ambiguity categories, and any `revision:` entry in the Extension Log.
- **Postconditions:** callers act per the verdict thresholds; existing settled rows are preserved; the Extension Log stays append-only; no `deferred` item is silently converted to `settled`.
- **Failure modes:** artifact unreadable → `Ontology: Absent` with the file-access error in the gap list. `ONTOLOGY.md` missing on a non-trivial domain → report `Absent`, never fabricate an ontology to close the gap. Mandatory-core item not `settled` → `Partial` at best, regardless of total. `revision:` entry in `feature` mode → halt and surface, do not score past it. Code-seeded rows presented as `settled` without human confirmation → treat as `unknown`.
