# Claude Code Skills
## A tour of the savviety-skills library

Organized by flow — top-level workflows first, one-off skills grouped by theme at the end.

---

# How to read this deck

Each **flow** is a top-level skill that composes several sub-skills into a repeatable workflow.

Sub-skills can also run standalone when you only need part of the flow.

One-off skills at the end are single-purpose tools grouped by theme.

> **Note:** deck reflects the target architecture after the consolidation plan lands (`/execute`, `/ship`, `/skills`). During the transition some slides show both old and new names.

---

# Flow 1 · Delivery
## From requirements to a merged PR

**Top-level entry points:** `/execute`, `/ship`

**Composes:** plan → execute-plan → checkpoint → ship

Pick your entry point by how much governance the work needs and how finished it is.

---

## /execute
**Autonomous start from a PRD or AERS**

- Readiness check → plan → implement → review, end-to-end
- Default: lightweight, no governance artifacts
- `--governed` flag: adds audit-grade artifacts (review-plan, disposition-log, execution-report)
- Replaces former `/kickoff` + `/execute-workflow`

---

## /plan
**Implementation planning only**

- Explores the codebase, estimates scope
- Writes a TDD-style task breakdown
- Use for the staged path when you want a checkpoint before execution

---

## /execute-plan
**Run a written plan**

- Reads a plan file, implements task-by-task
- Per-task build/test cycles + acceptance gate
- Pairs with `/plan` for the manual staged path

---

## /checkpoint
**Quality gate primitive**

- Discovers project tooling automatically
- Runs lint, typecheck/build, tests for changed packages
- Called internally by `/ship`; usable standalone

---

## /ship
**Unified delivery command**

- Default: PR lifecycle — branch → commit → checkpoint → push → PR → optional merge
- `--release`: adds repo-configured release steps (reads `ship.config.md`)
- `--fast`: emergency hot-fix mode, minimal gates
- Replaces former `/pr` + `/ship` + `/hotfix`

---

# Flow 2 · Requirements
## Shape, validate, verify

**Composes:** ideate → prd-validate → prd-acceptance

Upstream and downstream of code — shape requirements before, verify them after.

The AERS readiness **rubric** now lives in `_rubrics/` (referenced by `/prd-validate`, `/execute`).

---

## /ideate
**Shape a rough idea**

- Turns scattered docs or a vague ask into a clear direction
- Three modes: idea, ba, tech
- Sits upstream of brainstorming and `/plan`

---

## /prd-validate
**Make requirements implementation-ready**

- Interviews the author to close ambiguity
- Generates missing sections
- Use **before** `/plan` or `/execute`

---

## /prd-acceptance
**Verify delivery against the PRD**

- Reads the PRD, extracts checkboxes
- Verifies each criterion with evidence
- Produces a pass/fail scorecard

---

# Flow 3 · Review
## Multiple lenses, different stakes

**Composes:** code-review → review-adversarial → review-gauntlet

Plus `/ba-review-adversarial` for BA deliverables (not code).

---

## /code-review
**Domain-aware orchestrator**

- Runs specialist lenses per changed file
- Supports frontend, DB, API, design, security overlays
- Primary review command for any non-trivial PR

---

## /review-adversarial
**Cross-model challenge**

- Spawns reviewers on a **different** AI model (Codex/Gemini)
- Attacks work from distinct critical lenses
- Use on 200+ line diffs or high-risk code

---

## /review-gauntlet
**Meta-review**

- Challenges the review output itself
- Catches blind spots, overreach, missed issues in a review
- Use when a review's conclusions need scrutiny

---

## /ba-review-adversarial
**Adversarial review of BA deliverables**

- Targets requirements, stories, acceptance criteria — not code
- Spawns 1-3 reviewer lenses per phase
- Returns PASS / CONTESTED / REJECT verdict

---

# Flow 4 · Investigation
## Understand before you fix

**Composes:** triage → code-investigate → postmortem

---

## /triage
**Bug investigation & root cause**

- Reproduces the bug, traces cause
- Produces a structured report with risk assessment
- Investigates — does **not** write fixes

---

## /code-investigate
**Cross-repo pattern search**

- Literal, regex, or semantic (behavioral) search
- Versioned Markdown report with confidence scores
- Use when findings will be cited later

---

## /postmortem
**Governed run retrospective**

- Analyzes workflow, review quality, tool usage
- Writes `postmortem.md` in the run folder
- Reviews the process, not the code (runs after `/execute --governed`)

---

# Flow 5 · TDD
## Tests before code

**Entry point:** `/test-plan`

---

## /test-plan
**Generate test specs before implementation**

- Produces `it.todo()` stubs from requirements
- Plan / validate / refresh modes
- TypeScript monorepos; designed for iterative team-agent use

---

# Flow 6 · Session
## Persist context across sessions

**Composes:** whereami ↔ session-save

---

## /whereami
**Session-start briefing**

- Reads SESSION.md + git state + open PRs
- The single command to run first in every new session

---

## /session-save
**Session-end state capture**

- Writes `.claude/SESSION.md` with in-flight context
- Counterpart to /whereami (where it reads, this writes)
- Run before ending a long session

---

# One-off skills
## Grouped by theme

The following skills aren't part of a multi-step flow — they're single-purpose tools.

---

## Skill meta · /skills
**Unified skill-management command**

- `/skills` — list all available skills
- `/skills <name>` — detailed help on one skill
- `/skills --audit` — audit ecosystem, recommend gaps
- `/skills --find <query>` — discover installable skills
- Replaces former `/skill-help` + `/skill-audit` + `/find-skills`

---

## Skill meta · /configure
**Fill in blank config templates**

- Interviews the user, writes completed config
- Called when a skill's pre-flight says config is missing

---

## Ops · /env-check
**Detect shell/environment routing**

- Runs before giving commands
- Prevents "works on my machine" surprises

---

## Ops · /k8s-verify
**Post-deploy Kubernetes verification**

- Confirms resources rolled out correctly
- Use after cluster-level changes

---

## Ops · /dep-audit
**Dependency health & risk audit**

- Outdated, vulnerable, or unsupported packages
- Produces a prioritized action list

---

## Ops · /dep-migrate
**Major-version dependency migration**

- Plans and scripts the upgrade path
- Breaks large upgrades into reviewable steps

---

## Ops · /sync-main
**Safely sync branch with main**

- Detects conflicts early
- Preserves in-progress work

---

## Ops · /changelog
**Generate or update changelog**

- From commit history or PR notes
- Keeps release notes consistent

---

## Collab · /work-item
**Fetch an ADO or Linear ticket**

- Clean markdown summary of title, description, AC
- Used by /triage, /plan, and `/ship --fast` as input

---

## Collab · /teams
**Parallel implementation streams**

- Spawns 2-4 worker roles on independent scopes
- Nested implementer / reviewer / fixer roles
- Use for features that split cleanly across packages

---

## Collab · /grill-me
**Stress-test a plan or design**

- Relentless one-question-at-a-time interview
- Walks every branch of the decision tree
- Use when assumptions need pressure

---

## Collab · /ubiquitous-language
**Build a shared domain glossary**

- DDD-style ubiquitous language extraction
- Flags ambiguity, proposes canonical terms
- Saves `UBIQUITOUS_LANGUAGE.md`

---

# Referenced rubrics (not commands)

Library material lives under `claude/_rubrics/` — referenced by skills but not invokable directly.

- **aers-readiness** — the rubric that defines "implementation-ready" for a requirements artifact. Used by `/prd-validate` and `/execute`.

---

# Using the skills together

**Standard work:** `/whereami` → `/execute <path>` → `/ship` → `/session-save`

**Risk-bearing work:** `/whereami` → `/prd-validate` → `/execute --governed` → `/review-adversarial` → `/ship --release` → `/postmortem`

**Emergency:** `/whereami` → `/triage` → `/ship --fast`

**Investigation:** `/whereami` → `/triage` → `/code-investigate`

---

# Consolidation in progress

Four merges are being rolled out:

| Before | After |
|---|---|
| `/kickoff` + `/execute-workflow` | `/execute` (+ `--governed`) |
| `/pr` + `/ship` + `/hotfix` | `/ship` (+ `--release`, `--fast`) |
| `/skill-help` + `/skill-audit` + `/find-skills` | `/skills` (+ `--audit`, `--find`) |
| `/prd-readiness` (as command) | `_rubrics/aers-readiness.md` |

Full plan: `docs/consolidation-plan.md`.

---

# Thank you

Questions? Improvements? Start with `/skills --audit`.
