# Review Engine — Domain-Based Prompts

Adversarial, domain-based review prompts organized by lens. Each domain is a
**separate pass with its own context window**. The combined-prompt failure mode
is shallow bullet-per-domain output; separate passes force depth.

This tree supports two related review modes built from the same domain library:

- **Code review** — concrete code defects, correctness bugs, missing async,
  test gaps, contract mistakes, and direct implementation issues. Start with
  `profile: code-default` or `code-comprehensive`.
- **Professional review** — senior engineering judgment about scale, failure
  behavior, operability, maintainability, and whether the choices are
  professional-grade. Start with `profile: professional-default` or
  `professional-pre-production`.

Advanced profiles (`competence`, `comprehensive`, `pre-merge`,
`pre-production`, `security-focused`) still exist for users who want finer
control. Add your own profiles freely — they're one YAML file each and touch
nothing else.

## Convention

Domains are layered across three axes, each a separate folder:

- **`concept/`** — language- and platform-agnostic lenses. Describe the shape of the problem and universal smells. Never mention a specific language or library. These own the output format, severity scale, and anti-confirmatory instructions.
- **`dialect/`** — language-specific overlays that *extend* a concept domain. Short. Additive only. Add smells the concept domain can't see because they're specific to how the language expresses the concept.
- **`platform/`** — framework-, service-, or library-specific overlays. Same idea as dialects but for platforms with non-obvious failure modes. Bar for inclusion: does this platform have failure modes a generically-competent reviewer would miss?

Overlays are concatenated onto concept domains at dispatch time by the controller. A single worker invocation may receive one concept + zero or more dialects + zero or more platforms, depending on what the files under review touch and what the active profile permits.

## Profiles

A **profile** is a YAML file in `profiles/` that names a set of domains and their selection modes. The controller reads a profile to decide what to run. Profiles are how you scale the same domain library to different review situations without forking domain files.

Each domain in a profile has a `mode`:

- `always` — run on every invocation of this profile, regardless of diff content.
- `conditional` — run only if the domain's own frontmatter triggers match the diff.

Profiles may also specify:

- `overlays` — which overlays are allowed to apply in this profile. Overlays outside the profile's list do not fire even if their triggers match.
- `severity_bump` — optional map that escalates findings at the merge stage (e.g., `minor: major` in `pre-production`).

### Current profiles

- `profiles/code-default.yaml` — default defect-focused code review
- `profiles/code-comprehensive.yaml` — broader implementation review
- `profiles/professional-default.yaml` — default senior-engineering judgment pass
- `profiles/professional-pre-production.yaml` — high-paranoia professional bar before shipping
- `profiles/competence.yaml` — the six always-on concept defaults plus conditional async/data-integrity/api-contract.
- `profiles/comprehensive.yaml` — strict superset of competence, adds correctness, tests, architecture, documentation, style, commits, requirements, plus conditional dependencies.
- `profiles/pre-merge.yaml` — lighter fast-feedback profile. Correctness, tests, maintainability, style, security, plus conditional async/data-integrity/api-contract.
- `profiles/pre-production.yaml` — paranoid pre-release profile. Security, resilience, operability, performance, concurrency, correctness, plus conditionals. Bumps `minor` findings to `major`.
- `profiles/security-focused.yaml` — narrow profile for auth/crypto/public-surface changes. Security, correctness, resilience, operability, tests, plus conditional api-contract/dependencies.

### Adding a profile

1. Copy the nearest existing profile.
2. List the domains you want and their modes.
3. List the overlays in scope.
4. Add an optional `severity_bump` if this profile has a stricter bar.
5. Document the profile's intended use in its `description` field — this is what the controller surfaces in the report header.

Profiles are composition, not duplication. Do not copy domain content into a profile. Do not write a new domain to achieve what a profile re-combination would achieve.

## Frontmatter

Every domain file starts with a YAML frontmatter block:

```yaml
---
id: concept/async
type: concept            # concept | dialect | platform | controller
title: Async & Concurrency Patterns
extends: null            # concept id, or null for concept domains
triggers:
  paths: []              # glob patterns
  imports: []            # import/using patterns
  always: false          # true for domains that always run regardless of profile
  profiles: []           # profiles in which this domain is always active
  conditional: ""        # prose description for judgment-based triggers
severity_owner: true     # true if this domain defines the severity scale and output format
---
```

- `concept/` domains set `severity_owner: true` and `extends: null`.
- `dialect/` and `platform/` overlays set `severity_owner: false` and name their concept parent in `extends`.
- `triggers.always: true` marks domains that run in every profile. Most domains leave this false and let the profile decide; the always-on competence defaults (performance, resilience, concurrency, operability, security, maintainability) use `always: true` as a convenience because they run in every profile that includes them.
- `triggers.profiles: [...]` is a hint the profile writer uses — it declares which profiles this domain is intended for. The profile file is the authoritative source for what runs; frontmatter is documentation.

## Severity scale

Shared across all domains so findings merge cleanly:

- **critical** — will cause incident, data loss, or security breach in production. Blocks.
- **major** — meaningful degradation under load, real maintenance burden, or latent bug. Revise before merge.
- **minor** — worth fixing but not blocking. Leave a note.
- **nit** — style or taste. Mention once, don't belabor.

Profiles may apply a `severity_bump` at merge time (e.g., `pre-production` bumps `minor → major`). The bump is applied *after* workers report, so the bump is visible in the merged report.

## Output format (all domains)

```
## Findings
[severity] [file:line] — [problem] — [fix]

## Questions
[things the reviewer needs to know to finalize]

## Verdict
[block | revise | accept-with-notes | accept]
```

Some domains extend this format slightly (correctness includes an adversarial input/scenario field; tests include a "how a real bug would slip past" field). The severity and verdict vocabulary is identical across all domains.

## How to run

1. Choose a profile. When in doubt: `code-default` for defect-focused review,
   `professional-default` for engineering-choice review, and
   `professional-pre-production` before releases.
2. Invoke the controller (`SKILL.md`) with `profile: {id}` and the diff.
3. Controller loads the profile, triages the diff, selects domains, dispatches workers in parallel.
4. Each worker runs with its own context window scoped to the files it needs.
5. Controller merges findings, applies any profile-level severity bump, and emits a single report.

The controller does **not** review. It dispatches and merges. Producing findings from the controller collapses back into the shallow-review failure mode.

## Current domains

### Concept — always in competence profile

- `concept/performance.md` — CPU, memory, allocations, I/O patterns
- `concept/resilience.md` — error handling, timeouts, retries, blast radius
- `concept/concurrency.md` — shared state, locking, ordering, lifetimes
- `concept/operability.md` — logging, metrics, tracing, 3am debuggability
- `concept/security.md` — input validation, authz, secrets, trust boundaries
- `concept/maintainability.md` — readability, naming, structure, future-reader pain

### Concept — conditional in competence profile

- `concept/async.md` — async execution structure (fanout, cancellation, backpressure)
- `concept/data-integrity.md` — transactions, idempotency, migration safety
- `concept/api-contract.md` — interface design, versioning, coupling

### Concept — added by comprehensive profile

- `concept/correctness.md` — "assume tests pass, what bugs remain"
- `concept/tests.md` — test quality, would they catch a real regression
- `concept/architecture.md` — design fit, coupling, layering, simpler alternatives
- `concept/documentation.md` — docs that will serve future readers and operators
- `concept/style.md` — beyond-linter conventions, codebase consistency
- `concept/commits.md` — atomicity, bisectability, message quality
- `concept/dependencies.md` — supply chain, justification, version pins (conditional)
- `concept/requirements.md` — PR-vs-code alignment, simpler solutions, unstated assumptions
- `concept/ui-design.md` — component states, accessibility, design system compliance (conditional)

### Dialects

- `dialect/csharp-async.md` — extends `concept/async`
- `dialect/typescript-async.md` — extends `concept/async`
- `dialect/python-async.md` — extends `concept/async`
- `dialect/typescript-types.md` — extends `concept/style` (type safety, strict mode, import hygiene)

### Platforms

- `platform/azure-service-bus.md` — extends `concept/resilience`
- `platform/nats-jetstream.md` — extends `concept/resilience`
- `platform/postgres.md` — extends `concept/data-integrity` (migration safety, ORM patterns, indexing, connection management)

### Profiles

- `profiles/competence.yaml`
- `profiles/comprehensive.yaml`
- `profiles/pre-merge.yaml`
- `profiles/pre-production.yaml`
- `profiles/security-focused.yaml`

### Controller

- `SKILL.md` — dispatcher and merger. Takes `profile` as input.

## Adding a new domain

1. Decide the axis: concept, dialect, or platform. When in doubt, prefer concept — dialects and platforms are for smells the concept genuinely can't express.
2. Copy the nearest existing file as a template. Fill in frontmatter first; the triggers are the part that matters most for the controller.
3. For overlays: keep to a smell list and an "actively hunt for" section. Do not restate output format or severity. Do not repeat the concept's hunt list.
4. Decide which profile(s) the domain belongs to and update those YAML files to include it.
5. Add the file to the "Current domains" list in this README.
6. Run the controller against a known-bad diff and verify the new domain fires when expected.

## Comprehensive quality bar

A note on the comprehensive profile specifically: every domain in it — not just the competence ones — retains adversarial, bar-raising framing. The new concept domains are *not* checklists. Correctness review is not "did you test it," it's "assume the tests pass, what bugs remain." Test review is not "did you write tests," it's "would these tests catch a real regression." Architecture review is not "does it compile," it's "is this the simplest design that solves the problem."

If a domain's output reads like a box being ticked, the prompt is not doing its job. Every concept file ends with an explicit anti-confirmatory instruction that names the specific work the reviewer must perform before being allowed to say "looks good." Do not remove those instructions when editing domains. They are the single highest-leverage line in each prompt.
