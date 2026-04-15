# Gamma Brief
## Claude Code skills deck for engineers

Use this document as the direct source for a slide deck in Gamma.

The goal is to explain the **major flows** and **ad-hoc skills** in the
`savviety-skills` Claude library to a technical audience. Keep it practical,
specific, and engineering-oriented.

---

## What Gamma should produce

- **Audience:** software engineers, tech leads, staff engineers, and engineering managers
- **Tone:** technical, credible, operational
- **Style:** architecture deck, not marketing deck
- **Deck length:** 12-14 slides
- **Visual bias:** workflow diagrams, grouped capability maps, command examples, and "when to use it" framing
- **Avoid:** hype language, generic AI claims, stock-photo style visuals, or slides that read like product marketing

---

## Core message

This library is not just a bag of prompts.

It is organized around:

1. **Flows** — repeatable, multi-step workflows that combine several skills into a reliable engineering path
2. **Ad-hoc skills** — focused one-off tools used when you need a specific capability without entering a full workflow

The engineering value is:

- less reinvention of process
- more consistent execution
- clearer entry points for planning, delivery, review, investigation, and requirements work
- better composition between skills

---

## Important context for the deck

- The deck should reflect the **target architecture after consolidation**
- During the transition, some old names still appear in the repo and docs
- The consolidated target names to emphasize are:
  - `/execute`
  - `/ship`
  - `/skills`
- The deck should explain the target shape first, then mention legacy names only as transition notes

---

## Slide plan

### Slide 1 — Title
**Title:** Claude Code Skills  
**Subtitle:** Flows and ad-hoc tools for engineering work

**Content:**
- Explain that this is a tour of the `savviety-skills` library for Claude Code
- Position it as a working library for real software delivery, not a demo

**Visual direction:**
- Clean title slide
- Small capability map in the corner showing: delivery, requirements, review, investigation, TDD, session context

---

### Slide 2 — Mental model
**Title:** Two ways to use the library

**Content:**
- **Flows** = top-level workflows that compose multiple skills
- **Ad-hoc skills** = single-purpose tools used on demand
- Engineers should pick a flow when the work spans multiple stages
- Engineers should pick an ad-hoc skill when they need one focused capability

**Suggested layout:**
- Two-column comparison
  - Left: Flows
  - Right: Ad-hoc skills

**Key point to show:**
- Flows reduce process overhead
- Ad-hoc skills reduce search cost for targeted tasks

---

### Slide 3 — Delivery flow
**Title:** Flow 1 · Delivery
**Subtitle:** From requirements to a merged PR

**Skills to show:**
- `/execute`
- `/plan`
- `/execute-plan`
- `/checkpoint`
- `/ship`

**Narrative:**
- `/execute` is the autonomous entry point from a PRD or AERS
- `/plan` + `/execute-plan` is the staged/manual path
- `/checkpoint` is the reusable quality gate
- `/ship` handles PR lifecycle and release/hot-fix variants

**Suggested visual:**
- Main pipeline diagram:
  `requirements -> /execute -> /checkpoint -> /ship`
- Secondary branch:
  `requirements -> /plan -> /execute-plan -> /checkpoint -> /ship`

**Engineer takeaway:**
- Choose the path based on governance needs and how much control you want between stages

---

### Slide 4 — Requirements flow
**Title:** Flow 2 · Requirements
**Subtitle:** Shape, validate, verify

**Skills to show:**
- `/ideate`
- `/prd-validate`
- `/prd-acceptance`

**Narrative:**
- `/ideate` shapes unclear ideas before implementation
- `/prd-validate` turns a rough PRD or story into an implementation-ready AERS
- `/prd-acceptance` checks delivery against the original requirements

**Suggested visual:**
- Left-to-right lifecycle:
  `rough idea -> validated AERS -> delivered work -> acceptance check`

**Engineer takeaway:**
- Requirements work is not just pre-coding documentation; it also closes the loop after delivery

---

### Slide 5 — Review flow
**Title:** Flow 3 · Review
**Subtitle:** Multiple lenses, different stakes

**Skills to show:**
- `/code-review`
- `/review-adversarial`
- `/review-gauntlet`
- `/ba-review-adversarial`

**Narrative:**
- `/code-review` is the main engineering review orchestrator
- `/review-adversarial` uses a different model and more skeptical lenses for high-risk changes
- `/review-gauntlet` challenges the review itself
- `/ba-review-adversarial` applies similar pressure to BA artifacts rather than code

**Suggested visual:**
- Layered pyramid:
  - base = `/code-review`
  - middle = `/review-adversarial`
  - top = `/review-gauntlet`
- Side lane for `/ba-review-adversarial`

**Engineer takeaway:**
- These are not redundant reviews; each exists for a different failure mode

---

### Slide 6 — Investigation flow
**Title:** Flow 4 · Investigation
**Subtitle:** Understand before you fix

**Skills to show:**
- `/triage`
- `/code-investigate`
- `/postmortem`

**Narrative:**
- `/triage` is for bug investigation and root cause
- `/code-investigate` is for evidence-backed codebase or multi-repo search
- `/postmortem` analyzes workflow/process after governed work

**Suggested visual:**
- Investigation timeline:
  `problem observed -> triage -> code-investigate -> fix/workflow -> postmortem`

**Engineer takeaway:**
- The library separates diagnosis, search, and retrospective analysis instead of blending them together

---

### Slide 7 — TDD flow
**Title:** Flow 5 · TDD
**Subtitle:** Tests before code

**Skill to show:**
- `/test-plan`

**Narrative:**
- Focused flow with one entry point
- Generates test specs and `it.todo()` scaffolding before implementation
- Best fit when teams want behavior-first implementation

**Suggested visual:**
- Simple loop:
  `requirements -> /test-plan -> implementation -> validation`

**Engineer takeaway:**
- Even a one-command flow can still be a repeatable engineering pattern

---

### Slide 8 — Session flow
**Title:** Flow 6 · Session context
**Subtitle:** Persist state across long-running work

**Skills to show:**
- `/whereami`
- `/session-save`

**Narrative:**
- `/whereami` restores working context at the start of a session
- `/session-save` captures in-flight state at the end
- Useful for long-running features, incidents, and handoffs

**Suggested visual:**
- Circular loop:
  `/whereami -> do work -> /session-save -> next session -> /whereami`

**Engineer takeaway:**
- Session continuity is treated as a first-class engineering concern

---

### Slide 9 — Ad-hoc skills by theme
**Title:** Ad-hoc skills
**Subtitle:** Single-purpose tools grouped by theme

**Groups to show:**
- **Skill meta:** `/skills`, `/configure`
- **Ops:** `/env-check`, `/k8s-verify`, `/dep-audit`, `/dep-migrate`, `/sync-main`, `/changelog`
- **Collaboration:** `/work-item`, `/teams`, `/grill-me`, `/ubiquitous-language`

**Suggested layout:**
- Three-column grouped capability map

**Narrative:**
- These are not part of one big flow
- They are pulled in when a specific need appears
- Some are utilities, some are decision-support tools, some are coordination tools

---

### Slide 10 — What the ad-hoc skills actually do
**Title:** Ad-hoc skills in practice

**Content:**

**Skill meta**
- `/skills` = discover, audit, and find skills
- `/configure` = fill required config templates interactively

**Ops**
- `/env-check` = route commands safely across environments
- `/k8s-verify` = verify cluster-level rollout health
- `/dep-audit` = audit dependency health and risk
- `/dep-migrate` = plan big version upgrades
- `/sync-main` = safely sync with main
- `/changelog` = generate release notes/changelog updates

**Collaboration**
- `/work-item` = fetch ticket context from ADO or Linear
- `/teams` = parallelize independent implementation streams
- `/grill-me` = pressure-test assumptions and design branches
- `/ubiquitous-language` = build shared business/domain terminology

**Engineer takeaway:**
- Ad-hoc skills are best understood as reusable engineering primitives

---

### Slide 11 — How engineers compose the skills
**Title:** Common usage patterns

**Content:**
- **Standard work:** `/whereami -> /execute <path> -> /ship -> /session-save`
- **Risk-bearing work:** `/whereami -> /prd-validate -> /execute --governed -> /review-adversarial -> /ship --release -> /postmortem`
- **Emergency:** `/whereami -> /triage -> /ship --fast`
- **Investigation-heavy work:** `/whereami -> /triage -> /code-investigate`

**Suggested visual:**
- Four horizontal swimlanes with commands as labeled blocks

**Engineer takeaway:**
- The real value comes from composition patterns, not isolated commands

---

### Slide 12 — Why the consolidation matters
**Title:** Simplifying the top-level surface

**Content:**
- The library is consolidating overlapping commands into clearer entry points

**Show this mapping:**
- `/kickoff` + `/execute-workflow` -> `/execute`
- `/pr` + `/ship` + `/hotfix` -> `/ship`
- `/skill-help` + `/skill-audit` + `/find-skills` -> `/skills`
- `/prd-readiness` (command) -> `_rubrics/aers-readiness`

**Narrative:**
- Fewer top-level commands
- Clearer decision-making at the point of entry
- Better mental model for engineers new to the library

**Suggested visual:**
- Before/after consolidation table

---

### Slide 13 — Practical guidance
**Title:** How engineers should think about the library

**Content:**
- Start with the workflow, not the command catalog
- Pick a flow when work spans multiple stages
- Use ad-hoc skills when you need one focused capability
- Prefer the consolidated target commands in docs and onboarding
- Treat rubrics as library material, not user-facing entry points

**Suggested closing message:**
- The library is most useful when it reduces cognitive load, not when it exposes every internal building block

---

## Design guidance for Gamma

- Use **architecture-diagram visuals**, not abstract illustrations
- Favor **grouped command cards**, **workflow arrows**, and **before/after consolidation tables**
- Use monospace styling for slash commands
- Keep command descriptions short and concrete
- Show transitions and relationships between commands clearly
- Include light speaker-note style phrasing in the slides if Gamma supports it

---

## Content rules for Gamma

- Do **not** turn this into a generic "AI productivity" presentation
- Do **not** describe every skill as equally important
- Do **not** flatten flows and ad-hoc skills into one undifferentiated list
- Do **not** remove the consolidation context
- Do **not** invent capabilities not present in the source material

---

## Source material

Primary source:
- `docs/skills-deck.md`

Supporting source:
- `claude/README.md`
- `docs/consolidation-plan.md`

---

## One-line prompt for Gamma

Create a technical slide deck for engineers that explains the Claude Code skills library as a set of reusable engineering workflows and ad-hoc tools. Organize the deck around the six major flows (delivery, requirements, review, investigation, TDD, session context), then explain the ad-hoc skills grouped by theme. Keep the tone practical and architecture-oriented, use diagrams and command maps, and emphasize the target consolidated command surface (`/execute`, `/ship`, `/skills`) over legacy names.
