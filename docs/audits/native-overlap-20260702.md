# Native-Overlap Audit — 2026-07-02

**Repo:** /path/to/repos/savviety-skills
**Custom skills audited:** 41 (all `claude/<name>/SKILL.md`, excluding skip list and `_internal/`)
**Overlap findings:** 14
**Native catalog:** read live from session at 2026-07-02 03:14

## Scope notes

- **`/goal` is not a native Claude Code feature.** It does not appear in this session's
  native catalog and has no directory under `claude/` on main. It is this repo's own
  custom skill, sitting in still-open **PR #31** (`feat/new-skills-and-feature-integrations`,
  opened 2026-05-19) along with `/feature-sweep` and other integrations. It is out of
  audit scope until merged. Recommendation: rebase/merge or close PR #31 before the next
  audit — a 6-week-old open PR of skill integrations is itself a process smell.
- The native built-ins that matter most this cycle: `/code-review` (with effort levels,
  `--fix`, and `ultra` multi-agent cloud mode), `/verify`, `/simplify`, `/run`, `/review`,
  `/security-review`, `/loop`, `/schedule`, `/remember` — plus the superpowers plugin
  process skills and the security plugins (supply-chain-risk-auditor, differential-review,
  static-analysis, insecure-defaults, variant-analysis).

## Summary

| Custom skill | Findings | Top verdict |
|---|---|---|
| `code-review` | 2 | **Tighten (name collision — consider rename)** |
| `checkpoint` | 2 | Integrate as sub-primitive |
| `review-adversarial` | 1 | Cross-reference |
| `review-gauntlet` | 1 | Cross-reference |
| `triage` | 1 | Tighten |
| `pr` | 2 | Integrate as sub-primitive |
| `ship` | 1 | Cross-reference |
| `test-plan` | 1 | Cross-reference |
| `ideate` | 1 | No change needed (already cross-referenced) |
| `dep-audit` | 1 | Integrate as sub-primitive |
| `find-skills` | 1 | Redundant (verify against upstream) |
| `execute-plan` | 1 | Integrate as sub-primitive |
| `parallel-optimization` | 1 | Cross-reference (low priority) |

## Findings

### `code-review` ⚠️ highest priority

**Description:** "Domain-based PR review controller. Use when you need a structured, multi-lens review of a pull request or code change. Supports two profiles: 'breakpoint' … and 'full' …" (abridged)

#### Overlap with native `code-review` (built-in)

- **Verdict:** Tighten — and consider renaming.
- **Reasoning:** This is a **direct name collision**, not just description overlap. The
  built-in `/code-review` reviews the current diff at selectable effort levels
  (low→max), supports `--fix`/`--comment`, and offers `ultra` — a multi-agent cloud
  review. In any consumer repo where the manifest installs `claude/code-review` →
  `.claude/skills/code-review`, the two skills fight over the same invocation name and
  every ambiguous phrase ("review this code", "review the diff"). Whichever wins,
  the user loses predictability.
- **Recommended action:** Rename the custom skill (e.g. `/domain-review` or
  `/review-domains`) and update the cross-references in `checkpoint`, `pr`, `ship`,
  `review-adversarial`, `review-gauntlet`, and `execute-plan` bodies. If renaming is
  too disruptive, at minimum rewrite the description to open with:
  `"Preferred over the built-in /code-review when you need the 11-domain
  controller/worker review with per-domain findings; use the built-in for a fast
  single-pass diff review or the ultra cloud review."`
  Also consider making the `breakpoint` profile delegate to the built-in at
  `low`/`medium` effort — the built-in now covers exactly that "light mid-flow
  review" territory, cheaper.

#### Overlap with native `review` (built-in)

- **Verdict:** Cross-reference.
- **Reasoning:** The built-in `/review` reviews a GitHub PR by number; the custom
  skill's `full` profile targets the same PR-boundary moment. Users saying "review
  PR 42" may get either.
- **Recommended action:** Add to "When NOT to Use": "Reviewing a GitHub PR by number
  where you just want a standard pass — the built-in `/review` handles that; use this
  skill when you need the domain-worker structure."

### `checkpoint`

**Description:** "Quality gate: discovers project tooling, runs linter, typecheck/build, and tests for changed packages. Use before pushing or creating PRs."

#### Overlap with native `verify` (built-in)

- **Verdict:** Integrate as sub-primitive.
- **Reasoning:** Checkpoint proves the code compiles and tests pass; native `/verify`
  proves the change actually works by exercising the affected flow end-to-end. They're
  adjacent, not duplicative — checkpoint's gate is exactly where an end-to-end
  verification belongs for nontrivial product-source diffs.
- **Recommended action:** Add an optional final step: "If the diff touches product
  source (not just tests/docs/config), invoke the built-in `/verify` to exercise the
  changed flow before reporting green." Seam-specific — flag for human review rather
  than auto-apply.

#### Overlap with `superpowers:verification-before-completion`

- **Verdict:** Cross-reference.
- **Reasoning:** Both fire at the "about to claim done" stage. The superpowers skill is
  a discipline (evidence before assertions); checkpoint is the mechanical gate. In a
  session with superpowers installed, ambiguous "make sure it's done" phrasing can route
  to either.
- **Recommended action:** Add a `## Relationship to native skills` note: checkpoint is
  the concrete command-runner that satisfies verification-before-completion's
  evidence requirement; the two compose rather than compete.

### `review-adversarial`

**Description:** "Cross-model adversarial code review via Codex/Gemini. Use for high-stakes diffs (auth, payments, migrations) or diffs over 200 lines after code-review passes."

#### Overlap with native `code-review` `ultra` mode

- **Verdict:** Cross-reference.
- **Reasoning:** `/code-review ultra` launches a multi-agent cloud review — same
  outcome territory (deep scrutiny of a high-stakes diff). The custom skill's genuine
  value-add is **cross-model** review (Codex/Gemini CLIs), which ultra does not provide;
  but ultra is the better answer when those CLIs aren't installed or the user wants
  depth without model diversity.
- **Recommended action:** Add to "When NOT to Use": "Codex/Gemini CLIs unavailable, or
  you want depth rather than model diversity — use `/code-review ultra` (multi-agent
  cloud review) instead." Keep the cross-model claim front and center in the
  description; it's the differentiator.

### `review-gauntlet`

**Description:** "Use when a code review's conclusions need scrutiny. Reviews THE REVIEW via 3 lenses (Skeptic, Architect, Pragmatist). Returns SOLID / MIXED / UNRELIABLE."

#### Overlap with `superpowers:receiving-code-review`

- **Verdict:** Cross-reference.
- **Reasoning:** Both interpose between "review received" and "implementing its
  feedback," demanding verification instead of blind compliance. The superpowers skill
  is a behavioral discipline; gauntlet is a structured multi-lens verdict.
- **Recommended action:** Add a relationship note: "For a lightweight
  verify-before-implementing discipline, `superpowers:receiving-code-review` suffices;
  use this skill when the review is large (5+ findings) or would trigger significant
  rework and you want a formal SOLID/MIXED/UNRELIABLE verdict."

### `triage`

**Description:** "Investigate a bug from reproduction through root cause analysis. Produces a structured triage report with classification, risk assessment, and recommended next step. Does NOT write fixes."

#### Overlap with `superpowers:systematic-debugging`

- **Verdict:** Tighten.
- **Reasoning:** systematic-debugging triggers on "any bug, test failure, or unexpected
  behavior, before proposing fixes" — with superpowers' process-skill-first rule, it
  will win nearly every ambiguous bug phrasing. Triage's niche (investigation → report
  → handoff, no fix) is real but the description doesn't claim it against the native.
- **Recommended action:** Description before/after —
  Before: "Investigate a bug from reproduction through root cause analysis. …"
  After: "Investigate a bug from reproduction through root cause analysis and produce
  a structured triage report (classification, risk, recommended next step) — the
  deliverable is the report, not a fix. Preferred over
  superpowers:systematic-debugging when the goal is a handoff document for /hotfix,
  /plan, or a human decision rather than an in-session fix."

### `pr`

**Description:** "Full PR lifecycle: branch, commit, checkpoint, push, create PR, and optionally squash-merge. Automates the entire pull request workflow with quality gates."

#### Overlap with `superpowers:finishing-a-development-branch`

- **Verdict:** Cross-reference.
- **Reasoning:** Both fire when implementation is complete; the superpowers skill
  presents merge/PR/cleanup options interactively, while `/pr` executes the automated
  flow. Ambiguous "I'm done, wrap this up" phrasing can route to either.
- **Recommended action:** Add to "When NOT to Use": "You want to be walked through
  integration options (merge vs PR vs discard) rather than the automated PR flow —
  use superpowers:finishing-a-development-branch."

#### Overlap with native `security-review` (built-in)

- **Verdict:** Integrate as sub-primitive.
- **Reasoning:** `/pr` is the last gate before code leaves the machine; the built-in
  `/security-review` reviews pending changes on the current branch — exactly the right
  seam for auth/payment/input-handling diffs.
- **Recommended action:** In the checkpoint step of `/pr`, add a conditional: "If the
  diff touches auth, secrets, payments, or input parsing, run the built-in
  `/security-review` before pushing." Seam-specific — flag for human review.

### `ship`

**Description:** "Ship completed work through the repo's actual delivery flow: checkpoint, commit, push, PR, and release steps. Reads project-specific delivery commands from config."

#### Overlap with `superpowers:finishing-a-development-branch`

- **Verdict:** Cross-reference.
- **Reasoning:** Same workflow stage as `/pr` above, weaker overlap because ship
  requires explicit config and covers release steps beyond the PR.
- **Recommended action:** Mirror the `/pr` handoff line in "When NOT to Use."

### `test-plan`

**Description:** "Use before implementing a feature to generate it.todo() stubs from requirements (TDD-first). Supports plan, validate, and refresh modes. TypeScript monorepos."

#### Overlap with `superpowers:test-driven-development`

- **Verdict:** Cross-reference.
- **Reasoning:** The superpowers skill owns the TDD process trigger ("implementing any
  feature or bugfix, before writing implementation code"); test-plan is the concrete
  stub generator for TypeScript monorepos. Complementary, but nothing in either doc
  says so, so "TDD" phrasing routes unpredictably.
- **Recommended action:** Add a relationship note: "This skill generates the stubs
  that superpowers:test-driven-development's red phase consumes; invoke it from within
  that process, not instead of it."

### `ideate`

**Description:** "Use before /plan or brainstorming to shape a rough ask, doc, or folder into a direction. Three modes: idea (general), ba (business-analysis), tech (technical options)."

#### Overlap with `superpowers:brainstorming`

- **Verdict:** No change needed.
- **Reasoning:** The body's "When to Use / When NOT to Use" already positions ideate
  upstream of brainstorming and hands off cleanly ("Direction is already clear — jump
  to superpowers:brainstorming"). This is the pattern the other findings should copy.
- **Recommended action:** None.

### `dep-audit`

**Description:** "Audit project dependencies: check for vulnerabilities, outdated packages, unused deps, and license compliance. Use periodically or before releases."

#### Overlap with `supply-chain-risk-auditor` plugin

- **Verdict:** Integrate as sub-primitive.
- **Reasoning:** The plugin identifies dependencies at heightened risk of exploitation
  or takeover — a dimension dep-audit's CVE/outdated/unused/license checks don't cover.
  Same trigger surface ("supply chain concerns" appears verbatim in dep-audit's When
  to Use).
- **Recommended action:** Add a step or "When to escalate" note: "For
  takeover/maintainer-risk analysis beyond CVEs, run
  supply-chain-risk-auditor:supply-chain-risk-auditor and merge its findings into the
  report." Seam-specific — flag for human review.

### `find-skills`

**Description:** "Use when user asks 'how do I do X', 'is there a skill for X', or wants to extend capabilities. Discovers and installs agent skills from available marketplaces."

#### Overlap with the marketplace `find-skills` skill

- **Verdict:** Redundant (verify before removing).
- **Reasoning:** The session catalog contains a `find-skills` whose description is
  functionally identical. This looks like a vendored copy of the upstream skill. If the
  diff against upstream is nil or trivial, the repo is maintaining a fork for no gain
  and consumer repos get two skills competing for the same triggers.
- **Recommended action:** Diff `claude/find-skills/` against the upstream/marketplace
  version. If no meaningful delta, remove it from `claude/` and let consumers install
  the upstream; if there is a delta, document it in the description ("differs from
  upstream by …").

### `execute-plan`

**Description:** (abridged) "Execute an existing written implementation plan end-to-end with staged reviews … Preferred over superpowers:executing-plans whenever the plan follows this skill's wave/team/closed-decisions format."

#### Overlap with native `verify` / `code-review` at internal seams

- **Verdict:** Integrate as sub-primitive.
- **Reasoning:** The description-level positioning against superpowers:executing-plans
  is already done (this is the model the other skills should follow). What's new since
  that positioning: built-in `/verify` (end-to-end exercise) and `/code-review` effort
  levels fit execute-plan's milestone breakpoints and staged-review steps better than
  bespoke instructions.
- **Recommended action:** At milestone breakpoints, offer the built-in `/verify` on the
  wave's diff; at staged-review steps, consider the built-in `/code-review` at
  `medium` effort for breakpoint-grade passes, reserving the domain controller for the
  PR boundary. Seam-specific — human review required (note: `execute-plan/SKILL.md`
  has uncommitted edits in the working tree; coordinate with that work).

### `parallel-optimization`

**Description:** (abridged) "Analyze a PRD or plan and produce a parallel-agent execution map with dependency barriers, write scopes, and task ownership …"

#### Overlap with `superpowers:dispatching-parallel-agents`

- **Verdict:** Cross-reference (low priority).
- **Reasoning:** The superpowers skill governs *running* independent parallel tasks;
  parallel-optimization *produces the map* those runs consume. Trigger collision is
  limited ("parallel" phrasings), and parallel-optimization is mostly auto-invoked by
  /execute-prd.
- **Recommended action:** One line in the body noting the relationship. Low priority.

## New-native integration opportunities (beyond overlap verdicts)

Requested in this run's arguments — where new built-ins could slot into the existing
process rather than compete with it:

| Native | Where it fits |
|---|---|
| `/verify` | Final step of `checkpoint`; milestone gates in `execute-plan`; post-fix proof in `hotfix` |
| `/code-review` effort levels | `breakpoint`-profile replacement inside the custom review controller; staged reviews in `execute-plan` |
| `/code-review ultra` | Alternative escalation path documented in `review-adversarial` |
| `/security-review` | Conditional step in `/pr` and `/ship` for sensitive diffs |
| `/simplify` | Optional post-implementation pass in `execute-plan` / `kickoff` before the craft grade |
| `/run` | Deploy/verify steps where the app must be observed working (complements `k8s-verify` for non-K8s apps) |
| `/loop`, `/schedule` | Babysitting long `execute-plan` runs or recurring `dep-audit` / `skill-audit` cadences |
| `/remember` | Session-continuity replacement for the deleted `handoff.md` / `handoff-events.md` pattern |

## Caveats

Findings are description-level recommendations, not verdicts to apply mechanically.
The model can miss subtle overlaps and over-call borderline ones — treat this as the
starting point for human judgment. No edits were applied (`--apply` not passed).
