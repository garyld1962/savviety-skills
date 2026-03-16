# BA Skills — Presenter Guide

## What This Is

A collection of 14 VS Code prompt files (`.prompt.md`) that turn GitHub Copilot into a structured business analysis partner. They fall into two categories:

1. **The Pipeline** — a 6-phase structured analysis workflow with an orchestrator
2. **Standalone Skills** — individual tools for specific BA tasks

All skills are invoked from VS Code Chat using `/ba-<skillname>`.

---

## Skill Inventory

### Pipeline Skills

These run in sequence (Phase 1 → 6), managed by the orchestrator. Each phase fills one section of a growing **Project Brief** document. A **thesis thread** (root cause hypothesis) runs through the entire pipeline — formed in Phase 1, checked in Phase 3, validated in Phase 5, referenced in Phase 6.

| Skill | Phase | What It Does |
|-------|-------|-------------|
| `/ba-init` | Orchestrator | Starts/resumes a project, manages phase transitions, tracks state in `.ba-project/` |
| `/ba-problem-thesis` | 1 | Transforms a vague problem into a precise statement + testable root cause hypothesis |
| `/ba-stakeholder` | 2 | Maps stakeholders, power dynamics, domain terminology, dependencies |
| `/ba-current-state` | 3 | Documents as-is process, identifies gaps, **checkpoints the thesis** |
| `/ba-requirements` | 4 | Translates gaps into formal, testable, traceable requirements (MoSCoW priority) |
| `/ba-validation` | 5 | Stress-tests requirements with failure modes, edge cases, constraint architecture, **validates the thesis** |
| `/ba-solution` | 6 | Evaluates options (always includes "do nothing"), recommends, builds measurement plan |

### Standalone Skills

These work independently — no pipeline state required. Use them for quick, focused tasks.

| Skill | What It Does |
|-------|-------------|
| `/ba-preflight` | 9-question thinking exercise before drafting any significant deliverable |
| `/ba-context-builder` | Interviews you to build a reusable project context document |
| `/ba-problem-refiner` | Takes vague business problems → precise problem statements with gap analysis |
| `/ba-spec-engineer` | Deep interview → complete requirements specification document |
| `/ba-knowledge-capture` | 8 templates for capturing decisions, meeting debriefs, stakeholder intel, etc. |
| `/ba-eval-harness` | Creates evaluation frameworks for scoring AI-generated BA deliverables |
| `/ba-constraint-architecture` | Designs four-quadrant constraint architectures (Must Do / Must Not / Prefer / Escalate) |

### Adversarial Review Skills

These critique BA work products from different critical perspectives. **Switch to a different model** in the Copilot model picker before running — the point is cross-model scrutiny.

| Skill | Lens | What It Challenges |
|-------|------|-------------------|
| `/ba-adversarial-review` | Orchestrator | Selects 1-3 lenses based on phase, produces combined PASS/CONTESTED/REJECT verdict |
| `/ba-adversarial-skeptic` | Skeptic | Evidence quality, hidden assumptions, claims stated as facts |
| `/ba-adversarial-coherence` | Coherence | Thesis thread integrity, traceability, logical flow between sections |
| `/ba-adversarial-advocate` | Devil's Advocate | Stakeholder pushback, political realism, adoption risk |

**Lens selection by phase** (mirrors how the dev adversarial review scales):

| Phase | Lenses Applied |
|-------|---------------|
| 1-2 (early analysis) | Skeptic only |
| 3-4 (middle analysis) | Skeptic + Coherence |
| 5-6 or full brief | Skeptic + Coherence + Devil's Advocate |

### Pipeline vs. Standalone — When to Use Which

| Situation | Use |
|-----------|-----|
| Full structured analysis from scratch | Pipeline (`/ba-init`) |
| Quick problem statement cleanup | `/ba-problem-refiner` |
| Need a spec for a well-understood feature | `/ba-spec-engineer` |
| Preparing to draft something with AI | `/ba-preflight` |
| Starting a new project and creating reusable context | `/ba-context-builder` |
| Just left a meeting and need to capture notes | `/ba-knowledge-capture` |
| Want to quality-check your AI BA workflow | `/ba-eval-harness` |
| Need to prevent "technically correct but wrong" failures | `/ba-constraint-architecture` |
| Adversarial critique of any BA work product | `/ba-adversarial-review` (switch model first) |

---

## Demo Flow — Suggested Script

### Option A: Pipeline Demo (15-20 min)

Shows the structured 6-phase workflow and thesis thread.

1. **Start** — Run `/ba-init` and choose "single-session mode"
2. **Phase 1** — Present a business problem (example below). Watch it get refined into a problem statement with a testable thesis.
3. **Phase 3** — Skip to current state/gap analysis. Show the thesis checkpoint ("does the evidence still support our hypothesis?").
4. **Phase 5** — Skip to validation. Show the constraint architecture and final thesis validation.
5. **Wrap up** — Show the `.ba-project/` folder with `state.json`, `log.md`, and the growing `brief.md`.

**Key talking points:**
- The thesis thread is the analytical backbone — it's formed, tested, and validated
- Each phase produces a handoff package with exactly what the next phase needs
- State is persisted — you can resume across sessions
- Cross-phase impacts are tracked (scope changes, challenged assumptions)

### Option B: Standalone Skills Demo (10-15 min)

Shows the practical day-to-day tools.

1. **Pre-flight** — Run `/ba-preflight` before drafting a BRD. Walk through 2-3 of the 9 questions to show how it sharpens thinking.
2. **Problem Refiner** — Paste a vague stakeholder request. Watch it get gap-analyzed and rewritten.
3. **Knowledge Capture** — Show a meeting debrief or decision capture template.
4. **Constraint Architecture** — Show the four-quadrant framework with a quick example.

**Key talking points:**
- These are fast, focused — no pipeline setup required
- Pre-flight prevents the #1 AI failure: jumping to drafting without clear thinking
- Knowledge capture fights the "it's all in my head" problem
- Constraint architecture prevents "technically correct but wrong"

### Option C: Combined Demo (25-30 min)

1. Start with `/ba-preflight` (2 min) — show thinking-before-doing
2. Run `/ba-init` → Phase 1 problem thesis (8 min) — show the pipeline
3. Show `/ba-problem-refiner` on the same problem (3 min) — compare standalone vs. pipeline
4. Jump to Phase 5 validation (5 min) — show constraint architecture and thesis validation
5. Show `/ba-knowledge-capture` for a decision capture (3 min) — show day-to-day utility
6. Show `/ba-eval-harness` concept (2 min) — show quality assurance

### Option D: Adversarial Review Demo (10-15 min)

Shows the cross-model critique workflow.

1. **Setup** — Take a completed Phase 1 or Phase 3 output. Switch to a different model in the Copilot model picker.
2. **Run `/ba-adversarial-review`** — Paste the work product. Show lens selection based on phase.
3. **Walk through findings** — Show severity ratings, specific section references, and the difference between a real finding and noise.
4. **Lead Judgment** — Show how the orchestrator accepts/rejects its own findings.
5. **Individual lens** — Run `/ba-adversarial-skeptic` standalone on a Phase 1 problem statement to show the focused lens.

**Key talking points:**
- Cross-model review catches blind spots the authoring model won't find in its own work
- Three lenses map to real BA failure modes: bad evidence (Skeptic), broken logic (Coherence), political naivety (Devil's Advocate)
- Findings only — the reviewer doesn't rewrite, just like a real code review
- Severity is tied to decision risk, not document polish

---

## Sample Problem for Demo

Use this as starter input for Phase 1 or the Problem Refiner:

> "Our sales team keeps complaining that it takes too long to get quotes out to customers. They say the system is slow and they're losing deals. The VP of Sales wants us to buy a new CRM."

This is a good demo problem because:
- It's a **solution disguised as a problem** ("buy a new CRM") — the skills will push back
- It has **vague impact** ("too long", "losing deals") — the skills will probe for specifics
- It has a **symptom vs. root cause** issue — system speed may not be the real problem
- It has **unstated assumptions** — that a CRM is the solution, that the system is actually the bottleneck

---

## Architecture At a Glance

```
.github/prompts/ba/
├── ba-init.prompt.md              # Orchestrator
├── ba-problem-thesis.prompt.md    # Phase 1
├── ba-stakeholder.prompt.md       # Phase 2
├── ba-current-state.prompt.md     # Phase 3
├── ba-requirements.prompt.md      # Phase 4
├── ba-validation.prompt.md        # Phase 5
├── ba-solution.prompt.md          # Phase 6
├── ba-preflight.prompt.md         # Standalone
├── ba-context-builder.prompt.md   # Standalone
├── ba-problem-refiner.prompt.md   # Standalone
├── ba-spec-engineer.prompt.md     # Standalone
├── ba-knowledge-capture.prompt.md # Standalone
├── ba-eval-harness.prompt.md      # Standalone
├── ba-constraint-architecture.prompt.md  # Standalone
├── ba-adversarial-review.prompt.md       # Adversarial orchestrator
├── ba-adversarial-skeptic.prompt.md      # Adversarial lens: evidence
├── ba-adversarial-coherence.prompt.md    # Adversarial lens: structure
└── ba-adversarial-advocate.prompt.md     # Adversarial lens: politics

.github/skills/ba-templates/
├── project-brief-template.md  # Template used by pipeline
└── guide.md                   # This file
```

**Pipeline state** is stored per-project:
```
.ba-project/
├── state.json    # Current phase, thesis status, progress
├── log.md        # Append-only audit trail
└── brief.md      # The Project Brief — grows with each phase
```

---

## Key Design Principles

1. **Interview, don't generate** — Every skill conducts a structured interview before producing output. No hallucinated context.
2. **Thesis thread** — The root cause hypothesis is the analytical backbone of the pipeline. Formed → Checked → Validated → Referenced.
3. **Evidence typing** — Claims are tagged as Data, Observation, Stakeholder Report, or Assumption. No upgrading assumptions to facts.
4. **Solution-neutral** — Skills stay solution-neutral until Phase 6. Problem statements describe WHAT, not HOW.
5. **Constraint architecture** — The four-quadrant model (Must Do / Must Not / Prefer / Escalate) prevents "technically correct but wrong" failures.
6. **Traceability** — Requirements trace to gaps, gaps trace to pain points, success metrics trace to objectives.
7. **Guardrails** — Every skill has explicit guardrails at the end defining what it must and must not do.

---

## Common Questions

**Q: Do I have to use the full pipeline?**
No. Standalone skills work independently. Use the pipeline when you want full structured analysis; use standalone skills for targeted tasks.

**Q: Can I jump between phases?**
Phase 1 is always first. After that, the standard sequence is 1→2→3→4→5→6, but Phase 2 can be abbreviated, Phase 3 adapts for greenfield, and any phase can send you back to Phase 1 if the thesis is challenged.

**Q: What's the difference between `/ba-problem-refiner` and Phase 1?**
`/ba-problem-refiner` produces a clean problem statement with gap analysis. Phase 1 (`/ba-problem-thesis`) does that AND formulates a testable root cause hypothesis, alternative hypotheses, and success metrics — feeding into the full pipeline.

**Q: What's the difference between `/ba-constraint-architecture` and Phase 5?**
`/ba-constraint-architecture` is a standalone tool for building constraint architectures on any requirements. Phase 5 does that AND validates the thesis, consolidates assumptions, and produces the full validation section of the Project Brief.

**Q: What if I'm analyzing a brand-new product (greenfield)?**
Phase 3 has a greenfield adaptation (Step 3-alt) that focuses on analogous processes, competitor analysis, and user expectations instead of current-state documentation.
