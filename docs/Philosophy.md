# Philosophy

> Working draft. This is a place to record my reasons, goals, and beliefs about
> using AI in software development. It is intentionally editable and incomplete.

## Why I care about this

I do not want AI to become a novelty layer on top of software development. I
want it to become a serious engineering tool: something that improves clarity,
speed, judgment, and consistency without lowering standards.

I am not interested in using AI to bypass thinking. I am interested in using it
to make good thinking more scalable.

## Core belief

AI is most valuable when it acts as a force multiplier for professional
engineering judgment, not as a substitute for it.

That means:

- AI should help surface options, risks, gaps, and contradictions.
- AI should help turn vague intent into executable artifacts.
- AI should help review work from multiple lenses.
- AI should reduce mechanical overhead.
- AI should not silently make important decisions on my behalf.

## My goals for AI in software development

### 1. Reduce wasted reasoning

If something is already known, it should be written down so the model does not
have to rediscover it every time.

This is why I care about:

- source-of-truth documents
- reusable skills
- explicit instructions
- closed decisions
- structured specifications

I want AI effort spent on the still-open parts of the problem, not on
re-deriving settled facts.

### 2. Increase precision before execution

A lot of software waste comes from starting implementation too early with fuzzy
requirements, hidden assumptions, and unmade decisions.

I want AI to help sharpen the work before coding starts:

- clarify the problem
- separate open decisions from closed decisions
- define the intended interfaces and behaviors
- expose ambiguity instead of smoothing it over
- create artifacts that an engineer or agent can actually execute

### 3. Raise the engineering bar, not just the output volume

I am not trying to maximize how much code AI can produce. I am trying to
maximize how often the result reflects good engineering choices.

For me, that includes:

- scale awareness
- operational awareness
- explicit failure thinking
- maintainability
- evidence-backed review
- respect for real constraints

Code that merely "works" is not the standard I am aiming for.

### 4. Preserve human control over consequential decisions

I want humans to remain responsible for:

- what problem is actually worth solving
- what tradeoffs are acceptable
- what risks can be accepted
- when disagreement requires arbitration
- what quality bar matters in a given context

AI can assist heavily, but it should not quietly absorb that authority.

## What I seem to believe about good AI systems

### AI works better with structure than with freedom

Left unconstrained, models often revisit settled choices, guess missing facts,
or produce plausible but shallow work.

So I prefer systems that provide:

- explicit examples
- explicit do-nots
- explicit closed decisions
- fixed output shapes where useful
- clear separation of responsibilities

I do not see this as making AI weaker. I see it as making it more reliable.

### Durable knowledge should live separately from orchestration

I keep coming back to a layered model:

- prompts for workflow orchestration
- skills for durable knowledge, rubrics, and heuristics
- instructions for passive always-on constraints
- agents for bounded specialist roles

This separation matters because it reduces duplication and drift. It also makes
the system easier to reason about and improve over time.

### Source of truth matters

I prefer one canonical place for important truth and then compilation,
projection, or adaptation outward from that source.

I distrust ecosystems where the same rules are copied into many places and then
quietly diverge.

This is true for:

- skill definitions
- conventions
- configuration
- workflow expectations
- requirements artifacts

The more AI is involved, the more important this becomes.

### Built-ins first, custom only when there is real leverage

I do not want custom AI assets just because the platform allows them.

If a platform already has a strong built-in for planning, review, research, or
task management, I would rather use that than recreate it badly.

Custom assets are worth it when they add something the platform does not
already provide well:

- domain knowledge
- better review lenses
- structured requirements refinement
- repo-specific orchestration
- durable organizational memory

### Good review is more than defect detection

I care about two different review questions:

1. Does this contain concrete bugs, correctness issues, or risk?
2. Even if it works, were the right engineering choices made?

That second question matters a lot to me.

I want AI to help identify not only broken code, but amateur choices that will
fail under scale, complexity, or operational pressure.

### Green checks are not proof

Passing tests, clean lint, or successful builds are useful signals, but they are
not the same thing as confidence.

I want AI workflows that distinguish between:

- what has been proved
- what has only been partially proved
- what still rests on assumption

I care about evidence, not just clean status indicators.

### Independence improves review quality

I believe challenge systems work better when the challenger is meaningfully
independent from the original implementation path.

That is why I value:

- adversarial review
- different models or model families
- separate review passes
- explicit disposition of disagreements

I do not want a review system that merely restates the author's intent in
slightly different words.

## What I do not want AI to become

- a generator of large amounts of shallow code
- a confidence theater machine
- a replacement for explicit requirements
- a system that hides uncertainty behind fluent prose
- a reason to lower engineering standards
- a source of copied prompt clutter and duplicated rules
- a workflow that makes humans less thoughtful

## What I value in AI-assisted workflows

### Explicitness

I would rather the system say:

- "this is known"
- "this is assumed"
- "this is still open"
- "this is blocked"
- "this is accepted risk"

than blur those categories together.

### Configurability without hardcoding

Good AI systems should adapt to different environments without embedding local
assumptions into shared assets.

That is why I prefer:

- environment-neutral assets
- blank templates for local configuration
- shared vs local separation
- pre-flight checks before execution

### Artifacts over chat residue

I want important work to leave behind durable artifacts:

- executable specs
- plans
- review reports
- disposition logs
- context documents
- runbooks

Good AI collaboration should improve institutional memory, not just produce
useful chat in the moment.

### Simplicity with discipline

I am not looking for maximal complexity in the AI layer.

I would rather have:

- fewer assets
- clearer responsibilities
- stronger guardrails
- more reusable patterns

than a sprawling collection of partially overlapping commands and prompts.

## Tensions I expect to keep managing

These are tradeoffs I do not think go away:

### Speed vs rigor

AI can move fast, but speed without clear decisions and review discipline
usually creates downstream cost.

### Autonomy vs control

More autonomy is useful only when the rails are strong enough that the system
does not drift into confident nonsense.

### Flexibility vs consistency

Overly rigid systems become annoying. Overly flexible systems become noisy and
unreliable. I want the middle ground: adaptable workflows with stable patterns.

### Reuse vs local reality

Shared assets are valuable, but they must leave room for project-specific and
personal context. I care about preserving both.

## Principles I want to keep testing

These are the ideas I most want to keep refining:

- make known facts explicit
- separate closed decisions from open decisions
- prefer evidence over confidence
- use built-ins before custom assets
- keep durable knowledge separate from orchestration
- design review systems that challenge, not flatter
- use AI to raise the professional standard, not to mass-produce output
- preserve human ownership of meaningful tradeoffs
- create source-of-truth systems instead of duplicated prompt sprawl
- optimize for long-term quality, not short-term impressiveness

## Notes to future me

- Keep asking whether a new AI workflow actually adds leverage or just adds
  ceremony.
- Keep watching for places where the model is being asked to reason about things
  that should have been made explicit earlier.
- Keep distinguishing "technically correct" from "professionally good."
- Keep designing systems that help good engineers think better.

## Additions / edits

Questions I may want to expand later:

- What kinds of work should remain deeply human even if AI gets much better?
- Where do I want hard governance versus lightweight guidance?
- What does "professional review" mean in my own words?
- What are my non-negotiable quality bars for AI-generated change?
- What failure modes have I personally seen often enough to design around?
