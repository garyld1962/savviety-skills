---
name: ubiquitous-language
description: "Use when you need a domain glossary. Derives UBIQUITOUS_LANGUAGE.md from the PRD's ONTOLOGY.md; falls back to extracting terms from conversation when no ontology exists."
---

# /ubiquitous-language — Domain Terminology Glossary

**Purpose:** Produce `UBIQUITOUS_LANGUAGE.md`, the stakeholder-readable view of
the domain vocabulary. The default path **derives** it from
`docs/prds/<slug>/ONTOLOGY.md` — entity types become terms, fact types become
relationships, homonym resolutions become flagged ambiguities. Where no ontology
exists, the legacy path extracts terms from conversation and codebase instead.

The ontology is the source of truth; this glossary is a view of it. Called by
`/prd-create` Step 8 once the ontology is written.

## When to Use

- After `/prd-create` or `/prd-validate` has produced a `docs/prds/<slug>/ONTOLOGY.md` and you want the readable glossary
- When onboarding to a project that has an ontology and you need the vocabulary without reading the rubric
- Before writing requirements, when the same concept is being called different things across the team
- Legacy mode only: after a BA interview where domain terms were discussed but no ontology exists yet

## When NOT to Use

- You want to *build* or *extend* the ontology — that is an interview, use `/prd-create`
- You want the ontology rubric itself (item states, format, scoring) — see `claude/_internal/ontology-readiness/SKILL.md`
- You want the closure pass over the PRD's nouns and verbs — use `/prd-validate`

## Arguments

- `--from-ontology [path]` — **default mode.** Derive the glossary from an `ONTOLOGY.md`. With no `[path]`, use the sibling `ONTOLOGY.md` of the resolved requirements artifact — `docs/prds/<slug>/ONTOLOGY.md`. Artifact resolution order is defined once, in `/prd-validate` § *Arguments*; follow it there rather than restating it.
- _(none)_ — if an `ONTOLOGY.md` resolves, behave as `--from-ontology`. Otherwise fall through to **Legacy: extract from conversation**.
- `--scan` — legacy mode only: also scan the codebase for domain terms (type names, enum values, table names).
- `--update` — legacy mode only: read the existing `UBIQUITOUS_LANGUAGE.md` and merge new terms. **Refuses** when an `ONTOLOGY.md` exists; see **Re-running** below.

**Output location.** In derived mode the glossary is written beside the ontology
it reads: `docs/prds/<slug>/UBIQUITOUS_LANGUAGE.md`. In legacy mode it is
written to `UBIQUITOUS_LANGUAGE.md` in the working directory.

## Workflow

### Step 1: Read the ontology

1. Resolve the ontology: the `--from-ontology [path]` argument if given, else the sibling `ONTOLOGY.md` of the resolved requirements artifact.
2. If none resolves, say so and switch to **Legacy: extract from conversation**. Do not invent an ontology.
3. Read the header fields (`mode`, `scope`, `uod`, `status`) and every table named in `_internal/ontology-readiness` § *ONTOLOGY.md format*: Entity Types, Fact Types, Lifecycles, Temporality, Deferred, Unknown, Extension Log.
4. Note the `Status` cell (`settled` / `deferred` / `unknown`) on every row. Those three states are defined once, in `_internal/ontology-readiness` § *Item states* — read them there, do not redefine them here.

### Step 2: Derive terms from Entity Types

One Entity Types row → one glossary term. For each row:

- **Term** is the entity name, verbatim. Do not rename, pluralize, or prettify — the ontology's spelling is the canonical one.
- **Definition** is one sentence built from two inputs: the entity's role across the Fact Types rows that mention it, and its **Reference scheme**. State the reference scheme in the definition — "…identified by its `sku`" — because "what counts as one of these" is half of what a reader needs.
- **Aliases to avoid** come from the row's **Homonym resolution** cell plus any synonym the ontology rejected. Empty is allowed; a guess is not.
- Group terms by domain cluster only if natural groupings emerge. One cohesive domain → one table.

Carry `deferred` and `unknown` entity rows into the glossary **marked as such** —
prefix the definition with `*(deferred — <re-entry condition>)*` or
`*(unknown — <why>)*`, taken from the Deferred and Unknown tables. Never drop
them silently: a term absent from the glossary reads as a term nobody needed.

### Step 3: Derive relationships from Fact Types

One Fact Types row → one Relationships bullet. Use the verbalized fact type as
written, and take the cardinality from the row's **Constraints** column —
`mandatory:` and `unique:` are the cardinality, not decoration. Never write
cardinality "where obvious"; if the Constraints cell reads `[unconstrained]` or
the row is `unknown`, say so in the bullet rather than assuming a number.

Carry each row's **Modality** where it changes what a reader should expect: an
`alethic` fact cannot be otherwise, a `deontic` one must not be — flag deontic
rows as validation rules, not structure. `deferred` and `unknown` fact types get
a bullet marked with their state, same as terms. An entity carried as
`deferred` with no fact types at all gets one bullet saying exactly that —
otherwise its absence from Relationships reads as an oversight.

### Step 4: Write the example dialogue

Write 3–5 exchanges between a dev and a domain expert that demonstrate:

- Terms used precisely, in the ontology's spelling
- Boundaries between related concepts — especially the ones a homonym resolution split apart
- A lifecycle transition or a deontic rule in natural use

### Step 5: Flag ambiguities

Two sources, both mechanical:

1. The Entity Types **Homonym resolution** column — every non-empty cell becomes a flagged ambiguity with the ontology's resolution as the recommendation.
2. The rubric's homonym/synonym findings — `_internal/ontology-readiness` § *Elicitation Categories* (Homonyms/synonyms) and its high-risk ambiguity categories, as reported by `/prd-validate` or the rubric's automated check.

Add every `unknown` row that touches vocabulary, marked `unknown`, with no
recommendation attached — an unknown with a recommendation is a settled item
in disguise.

### Step 6: Write the glossary

Write to `docs/prds/<slug>/UBIQUITOUS_LANGUAGE.md` (derived mode) using this format:

```markdown
# Ubiquitous Language

Derived from `ONTOLOGY.md` — regenerated, never hand-edited.

## [Domain cluster name]

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Term** | One-sentence definition (what it IS), stating the reference scheme | alias1, alias2 |

## Relationships

- A **Term** places zero or more **OtherTerms** (mandatory: OtherTerm→Term)
- A **Term** contains one or more **AnotherTerms**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No — an **Invoice** is only generated once a **Fulfillment** is confirmed."

## Flagged ambiguities

- "account" meant both the billing party and the auth identity — resolved: use **Customer** for the billing party.
```

Output a brief inline summary after saving: term count, and how many rows were
carried as `deferred` or `unknown`.

## Legacy: extract from conversation

Use this mode **only** when no `ONTOLOGY.md` resolves. It produces a glossary
with no ontology behind it, so it is a draft, not a contract.

1. Scan the conversation for domain-relevant nouns, verbs, and concepts.
2. Note where the same word is used for different things (ambiguity), where different words are used for the same thing (synonyms), and which terms are vague or overloaded.
3. If `--scan`: search the codebase for domain entities — exported types, interfaces, enums, DB table/model names — and flag divergences from the conversation terms.
4. For each concept: pick a canonical term, write a one-sentence definition of what it IS, list aliases to avoid, group by domain cluster only if groupings emerge.
5. Express relationships with cardinality where the conversation established one; say "cardinality not established" where it did not.
6. Write the example dialogue and the flagged ambiguities as in Steps 4–5 above.
7. Write `UBIQUITOUS_LANGUAGE.md` in the working directory, in the same format.

Close the summary by suggesting `/prd-create` if the domain warrants an
ontology — the glossary derived from one is the artifact that survives.

## Rules

- **The ontology wins.** When `ONTOLOGY.md` exists, it is the source of truth: derive, do not re-elicit, and do not contradict it. If a term in conversation disagrees with the ontology, that is a finding for `/prd-create --extend`, not an edit here.
- **The glossary is regenerated, never hand-edited.** It is a view. Fixes go into `ONTOLOGY.md` and the glossary is rebuilt; an edit made here is lost on the next run and, worse, silently diverges from the ontology until then.
- **Never invent a definition.** An ontology term with too little information to define is reported, not filled in — see **Contract** § *Failure modes*.
- **Carry the open items.** `deferred` and `unknown` rows appear in the glossary marked with their state. Dropping them makes an open decision look closed.
- **Real cardinality only.** Take it from the Constraints column. "Where obvious" is how a one-to-many quietly becomes a many-to-many.
- **Domain terms only.** Skip module names, class names, and generic programming concepts (array, endpoint, middleware) unless they have domain-specific meaning.
- **Write the example dialogue.** It is the most valuable part — it shows the vocabulary in natural use.

## Re-running

**Derived mode:** re-run `--from-ontology`. The glossary is regenerated from the
current ontology; there is no merge step, because there is nothing in the
glossary that did not come from the ontology.

**`--update` (legacy only):** if an `ONTOLOGY.md` resolves, `--update` **refuses**
and says so:

> "`ONTOLOGY.md` exists at `docs/prds/<slug>/ONTOLOGY.md`. The glossary is derived from it and is never hand-edited — re-run with `--from-ontology`. To change a definition, change the ontology (`/prd-create --extend`)."

With no ontology present, `--update` reads the existing
`UBIQUITOUS_LANGUAGE.md`, incorporates new terms from subsequent discussion,
updates definitions if understanding has evolved, re-flags new ambiguities, and
rewrites the example dialogue.

## Contract

- **Inputs:** in derived mode, an `ONTOLOGY.md` — the `--from-ontology [path]` argument, or the sibling of the requirements artifact resolved per `/prd-validate` § *Arguments*. In legacy mode, the conversation, plus the codebase under `--scan` and an existing `UBIQUITOUS_LANGUAGE.md` under `--update`.
- **Preconditions:** the ontology is readable and in the format defined by `_internal/ontology-readiness` § *ONTOLOGY.md format*. `--update` requires that no `ONTOLOGY.md` resolves.
- **Outputs:** `docs/prds/<slug>/UBIQUITOUS_LANGUAGE.md` beside the ontology (derived mode) or `./UBIQUITOUS_LANGUAGE.md` (legacy mode), containing the domain cluster table(s), Relationships, Example dialogue, and Flagged ambiguities; plus an inline summary.
- **Postconditions:** every Entity Types row appears as exactly one term; every Fact Types row appears as exactly one relationship bullet; every `deferred` and `unknown` row is present and marked; the ontology is unmodified.
- **Failure modes:** no ontology resolves → say so and fall through to legacy mode, never fabricate one. An ontology term without enough information to define — no reference scheme, no fact type mentioning it — → **report it and stop defining it**; emit the term marked *(insufficient information — settle its reference scheme in `/prd-create`)* and never invent a definition. Ontology unreadable or malformed → report the file and the offending section; do not partially derive. `--update` with an ontology present → refuse, per **Re-running**.

## Fixtures

`tests/ontology-sample.md` is a small hand-written ontology in the rubric's
format; `tests/expected-glossary.md` is the glossary derived mode must produce
from it. Following Steps 1–6 against the sample should reproduce the expected
glossary's terms, relationships, and flagged ambiguities.
