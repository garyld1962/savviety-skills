# Gamma Brief
## Copilot-native skills, prompts, and agents deck for engineers

Use this document as the direct source for a slide deck in Gamma.

The goal is to explain the **Copilot-native workspace** in `savviety-skills` to
engineers: how the major workflow **flows** fit together, where **built-in
Copilot features** should be used first, and which **targeted prompts/agents**
act like ad-hoc tools when a full flow is not needed.

---

## What Gamma should produce

- **Audience:** software engineers, tech leads, staff engineers, engineering managers
- **Tone:** technical, practical, architecture-oriented
- **Style:** engineering workflow deck, not a marketing deck
- **Deck length:** 12-14 slides
- **Visual bias:** workflow diagrams, layered architecture maps, command/prompt maps, decision trees
- **Avoid:** hype language, abstract AI messaging, stock-photo aesthetics, or generic productivity claims

---

## Core message

The Copilot-native library is built around a simple idea:

1. **Use Copilot built-ins first**
2. **Add custom prompts only where they add real workflow leverage**
3. **Keep durable knowledge in skills**
4. **Keep passive rules in instructions**
5. **Use agents for bounded specialist roles**

This is not a flat list of prompts.

It is a layered engineering system with:

- **native built-ins** for planning, review, research, tasks, diff/PR inspection, and session control
- **prompt-led flows** for requirements shaping, governed execution, investigation, and deeper review
- **specialist agents** for bounded analysis and artifact writing
- **skills** that hold rubrics, heuristics, and domain knowledge
- **instructions** that hold always-on constraints

---

## Important context for the deck

- This deck is about **Copilot Native**, not the Claude skill library
- It reflects the **current `copilot-native/` workspace**
- This workspace is still a **proposal/staging area**, not yet the final deployed `.github/` set
- The deck should explain both:
  - the **workflow clusters**
  - the **built-in-first design philosophy**

---

## Recommended framing for Gamma

Use this mental model early in the deck:

### Layer 1 — Built-ins
- `/plan`
- `/review`
- `/research`
- `/fleet`
- `/tasks`
- `/diff`
- `/pr`
- `/env`
- `/context`
- `/compact`
- `/share`
- `/model`

### Layer 2 — Custom prompts
- user-facing workflow entry points
- thin orchestration where built-ins are not enough

### Layer 3 — Agents
- bounded specialist workers
- review, investigation, ideation, orchestration, report writing

### Layer 4 — Skills
- durable knowledge
- rubrics, heuristics, contracts, decision rules

### Layer 5 — Instructions
- always-on constraints
- authoring discipline
- environment rules

---

## Slide plan

### Slide 1 — Title
**Title:** Copilot-native engineering workflows  
**Subtitle:** Built-ins first, custom assets where they add leverage

**Content:**
- Introduce the `copilot-native/` workspace
- Position it as an engineering workflow system for GitHub Copilot
- Emphasize that this is about practical delivery, review, investigation, and requirements shaping

**Visual direction:**
- Clean title slide
- Small layered architecture visual in the corner: built-ins -> prompts -> agents -> skills -> instructions

---

### Slide 2 — The operating model
**Title:** How the Copilot-native workspace is designed

**Content:**
- Built-ins handle the default path
- Prompts provide workflow entry points
- Agents provide bounded specialist execution
- Skills hold durable logic
- Instructions hold passive always-on rules

**Suggested layout:**
- Five-layer stack diagram

**Engineer takeaway:**
- The system is intentionally **not** trying to recreate the entire platform in custom prompts

---

### Slide 3 — What built-ins are expected to do
**Title:** Start with native Copilot features

**Content:**

**Default built-in roles**
- `/plan` = planning
- `/review` = default quick review
- `/research` = broad repo/web investigation
- `/fleet` + `/tasks` = parallel specialist work and background visibility
- `/diff` = changed-scope inspection
- `/pr` = PR state, checks, and merge readiness
- `/env` = environment snapshot
- `/context` + `/compact` = context management for long runs
- `/share` = export when repo persistence is not needed
- `/model` = deliberate second-opinion or adversarial passes

**Suggested visual:**
- Two-column table:
  - built-in
  - preferred role in the workspace

**Engineer takeaway:**
- Custom assets are justified only when built-ins are insufficient

---

### Slide 4 — Flow 1 · Requirements and BA shaping
**Title:** Turn rough business input into executable engineering input

**Prompts to show:**
- `ideate`
- `prd-validator`
- `ba-problem-refiner`
- `ba-spec-engineer`
- `ba-context-builder`
- `ba-eval-harness`
- `ba-knowledge-capture`
- `ubiquitous-language`

**Agents and skills behind the flow:**
- `ba-ideation`
- `tech-ideation`
- `prd-quality-gate`
- `prd-readiness`
- `project-context`
- `ba-knowledge-ops`

**Narrative:**
- Shape ideas before planning
- Convert business-facing input into an **AERS**
- Capture reusable context and terminology
- Use `ubiquitous-language` when shared domain vocabulary is still fuzzy

**Suggested visual:**
- Left-to-right flow:
  `rough ask -> ideation -> readiness validation -> reusable context/glossary -> /plan`

**Engineer takeaway:**
- This flow reduces ambiguity before coding starts

---

### Slide 5 — Flow 2 · Autonomous execution and governed delivery
**Title:** From accepted requirements to implementation and release

**Prompts to show:**
- `autonomous-development-kickoff`
- `execute-plan`
- `execute-workflow`
- `checkpoint`
- `ship`
- `hotfix`

**Agents and skills behind the flow:**
- `execute-orchestrator`
- `plan-reviewer`
- `code-reviewer`
- `disposition-coordinator`
- `repo-delivery`
- `review-disposition-governance`
- `execution-environment`

**Narrative:**
- `autonomous-development-kickoff` is the thin built-in-first entry path
- `execute-plan` is the staged/manual execution path
- `execute-workflow` is the governed path with artifacts and gates
- `checkpoint`, `ship`, and `hotfix` handle repo-specific delivery behavior

**Suggested visual:**
- Branching diagram:
  - fast path = `requirements -> /plan -> implement -> /review -> ship`
  - governed path = `requirements -> execute-workflow -> gated execution -> review/disposition -> postmortem`

**Engineer takeaway:**
- The delivery model separates normal execution from explicitly governed execution

---

### Slide 6 — Flow 3 · Review
**Title:** Review is layered, not one-size-fits-all

**Built-in + custom review model**
- built-in `/review` = quick/default path
- `code-review` = structured defect-focused review
- `professional-review` = senior-bar engineering judgment
- `review-api`, `review-db`, `review-design`, `review-tests` = narrow compliance checks
- `adversarial-review` = deliberate second-opinion challenge
- `adversarial-review-gauntlet` = challenge the review output itself

**Skills and agents behind the flow:**
- `review-engine`
- `review-foundations`
- `api-patterns`
- `db-schema-review`
- `ui-design-compliance`
- `test-quality`
- `adversarial-reviewer`

**Suggested visual:**
- Review ladder:
  - `/review`
  - `code-review`
  - `professional-review`
  - `adversarial-review`
  - `adversarial-review-gauntlet`

**Engineer takeaway:**
- Each review lane exists for a different failure mode

---

### Slide 7 — Flow 4 · Investigation
**Title:** Evidence-backed investigation across one repo or many

**Prompts and agents to show:**
- `investigate-code`
- `orchestrator-code-investigation`
- `specialist-code-investigation-search`
- `writer-investigation-report`

**Skills behind the flow:**
- `code-investigation-orchestrator`
- `code-investigation-search`
- `investigation-report-writer`

**Narrative:**
- Use built-in `/research` for broad exploration
- Use `investigate-code` when you need a structured, versioned, evidence-backed report
- This flow is designed for cross-repo search and durable artifacts

**Suggested visual:**
- Flow:
  `request -> orchestrator -> parallel search workers -> reduced results -> written report`

**Engineer takeaway:**
- Investigation here is a repeatable reporting workflow, not just an interactive search

---

### Slide 8 — Flow 5 · Post-run learning and governance
**Title:** Close the loop after high-governance work

**Prompt to show:**
- `postmortem`

**Agent and skills behind it:**
- `postmortem-analyst`
- `review-disposition-governance`
- `copilot-platform-playbook`

**Narrative:**
- Postmortem is for workflow/process analysis, not code review
- It makes the governed execution path auditable and improvable
- It belongs after a completed run, especially one with formal gates and artifacts

**Suggested visual:**
- Loop:
  `governed execution -> review/disposition artifacts -> postmortem -> better future runs`

**Engineer takeaway:**
- This workspace treats engineering process quality as a first-class concern

---

### Slide 9 — Ad-hoc prompts by theme
**Title:** Targeted prompts engineers can use without entering a full flow

**Group 1 — Configuration and environment**
- `configure`
- `environment-check`

**Group 2 — Ops and change support**
- `dependency-audit`
- `migration-guide`
- `k8s-deploy-verify`
- `ado-item`

**Group 3 — Prompt discovery and asset authoring**
- `skill-help`
- `copilot-asset-audit`

**Suggested layout:**
- Three-column grouped map

**Engineer takeaway:**
- These are the Copilot-native equivalent of ad-hoc tools: focused entry points for one specific problem

---

### Slide 10 — What the ad-hoc prompts actually do
**Title:** Ad-hoc capabilities in practice

**Configuration and environment**
- `configure` = fill config templates and write them to the right place
- `environment-check` = resolve shell-routing ambiguity when `/env` is not enough

**Ops and change support**
- `dependency-audit` = dependency health and risk review
- `migration-guide` = repo-specific major-version upgrade planning
- `k8s-deploy-verify` = post-deploy Kubernetes verification
- `ado-item` = retrieve Azure DevOps work items for downstream flows

**Prompt and asset ergonomics**
- `skill-help` = browse the custom prompt surface
- `copilot-asset-audit` = review a Copilot asset set for duplication, missing guardrails, and modernization opportunities

**Engineer takeaway:**
- The ad-hoc layer is a toolbox of reusable engineering primitives

---

### Slide 11 — Specialist agents
**Title:** Where agents fit in

**Agents to highlight:**
- `execute-orchestrator`
- `code-reviewer`
- `adversarial-reviewer`
- `prd-quality-gate`
- `ba-ideation`
- `tech-ideation`
- `orchestrator-code-investigation`
- `writer-investigation-report`

**Narrative:**
- Agents should have bounded roles
- They are not meant to replace the base Copilot experience
- They are the place for specialist execution, formatting, or orchestration work with a clear contract

**Suggested visual:**
- Prompt -> agent -> artifact/output map

**Engineer takeaway:**
- Prompts are entry points; agents are specialist workers

---

### Slide 12 — The durable logic lives in skills
**Title:** Skills are the knowledge layer

**Examples to show:**
- `prd-readiness`
- `review-engine`
- `repo-delivery`
- `execution-environment`
- `dependency-change-management`
- `api-patterns`
- `db-schema-review`
- `ui-design-compliance`
- `test-quality`
- `copilot-platform-playbook`

**Narrative:**
- Skills hold rubrics, heuristics, and decision logic
- Prompts should remain thin by pointing to these skills
- This is what makes the workspace scalable and maintainable

**Suggested visual:**
- Hub-and-spoke:
  - prompts and agents on the outside
  - skills as the shared center

**Engineer takeaway:**
- Reuse and consistency depend on keeping the durable rules in skills

---

### Slide 13 — What engineers should remember
**Title:** How to use the Copilot-native library well

**Content:**
- Start with the **built-in** when it already solves the problem well
- Use a **custom prompt** when you need repeatable workflow leverage
- Use an **agent** when you need a bounded specialist
- Use a **skill** when you need the durable rubric or contract
- Use **instructions** for always-on rules
- Prefer the layered model over giant all-in-one prompts

**Suggested closing message:**
- The system is designed to reduce duplication and increase leverage, not to add more surface area than engineers need

---

## Design guidance for Gamma

- Use **workflow diagrams** and **layered architecture visuals**
- Use monospace for built-ins (`/plan`) and prompt/agent names (`code-review`, `@execute-orchestrator`)
- Keep prompt descriptions short and practical
- Emphasize where built-ins stop and custom assets begin
- Show the distinction between **flow entry points** and **targeted/ad-hoc prompts**

---

## Content rules for Gamma

- Do **not** turn this into a generic "Copilot can do everything" deck
- Do **not** flatten built-ins, prompts, agents, skills, and instructions into one list
- Do **not** describe every prompt as equally important
- Do **not** ignore the built-in-first philosophy
- Do **not** imply the workspace is already the final deployed production asset set

---

## Source material

Primary sources:
- `copilot-native/README.md`
- `copilot-native/asset-catalog.md`

Supporting sources:
- `copilot-native/platform-review.md`
- `copilot-native/skills/README.md`

---

## One-line prompt for Gamma

Create a technical slide deck for engineers that explains the Copilot-native workspace as a built-in-first engineering system. Show how native Copilot commands (`/plan`, `/review`, `/research`, `/fleet`, `/tasks`, `/diff`, `/pr`, `/env`, `/share`) combine with custom prompts, specialist agents, reusable skills, and instructions. Organize the deck around the main workflow flows (requirements shaping, execution and delivery, review, investigation, post-run learning) and then explain the targeted/ad-hoc prompts by theme. Keep the tone practical, architectural, and grounded in real engineering workflows.
