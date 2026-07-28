# Prompt for Copilot — skill consolidation analysis

Paste the block below into Copilot CLI when working in the `savviety-skills` repo. It instructs Copilot to run the same audit and consolidation exercise we ran on `claude/`, but against `copilot-native/`.

---

## Prompt

I need you to audit the skills in `copilot-native/` and produce a consolidation plan. We just did the same exercise for `claude/` — the outputs are at `docs/consolidation-plan.md` and `docs/skills-deck.md`. Read those first so your analysis has the same shape, but do **not** assume the claude decisions apply here — copilot-native has its own conventions (top-level `agents/` layer, different skill format, different invocation syntax).

### Phase 1 — Inventory

1. List every skill in `copilot-native/skills/` and every agent in `copilot-native/agents/` (if present). For each, capture:
   - Name
   - One-line purpose
   - Frontmatter description length and whether it leads with a trigger ("Use when…")
   - Whether it has "When to Use" / "When NOT to Use" sections
   - Top-level entry point vs sub-skill (is it invoked by users, or composed by another skill?)
2. Note structural inconsistencies: non-standard frontmatter, missing sections, oversized files.

### Phase 2 — Overlap analysis

Identify top-level skills whose use cases overlap. For each overlap:
- Name the skills involved
- Describe the shared use case in one sentence
- Identify the true differentiator (if any)
- Classify as: **clear overlap** (merge candidate), **borderline** (clarify descriptions), or **distinct** (leave alone)

Pay special attention to:
- Delivery/execution commands (anything that takes requirements → merged code)
- Review commands (multiple review styles or stages)
- Skill-meta commands (list / audit / find / help)
- Requirements-shaping commands
- Investigation commands (bug, pattern search, retrospective)

### Phase 3 — Consolidation plan

Write `docs/copilot-consolidation-plan.md` following the same structure as `docs/consolidation-plan.md`:
- One section per consolidation, ordered lowest-risk first
- For each: merged-from list, new surface (commands + flags), rationale, work items, risk level
- Explicit "Out of scope — deliberately keeping separate" section
- "Open questions" section at the end

Do **not** execute any merges. Plan only.

### Phase 4 — Slide deck

Write `docs/copilot-skills-deck.md` — a Gamma-ready markdown deck (slides separated by `---`) organizing copilot-native skills by flow, with one-off skills grouped by theme at the end. Mirror the structure of `docs/skills-deck.md` but use copilot-native's invocation syntax and reflect its agent-layer architecture. Add a "Consolidation in progress" slide with a before/after mapping table.

### Constraints

- **Don't modify any skill files** in this pass. Audit and plan only.
- **Don't assume claude's merges apply.** Copilot-native may have different overlaps or different best merges. Justify each recommendation from copilot-native's own skill set.
- **Flag genuine uncertainty.** If you can't tell whether two skills overlap without asking a human, list them under Open Questions rather than guessing.
- **Cite files by path** when recommending merges or moves.

### Deliverables

1. Summary in chat: inventory highlights + top 3–5 overlap findings + proposed merges
2. `docs/copilot-consolidation-plan.md`
3. `docs/copilot-skills-deck.md`

Start with Phase 1 and report inventory before proceeding to Phase 2.
