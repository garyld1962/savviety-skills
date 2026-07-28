# Skill Consolidation Plan

Reduces top-level skill count and eliminates overlapping entry points. Four consolidations, ordered lowest-risk first.

---

## 1. `/skills` — unified skill-management command

**Merges:** `skill-help` + `skill-audit` + `find-skills`

**New surface:**

```
/skills                     # list all available skills (was /skill-help)
/skills <name>              # detailed help on one skill (was /skill-help <name>)
/skills --audit             # audit skill/plugin/agent ecosystem (was /skill-audit)
/skills --find <query>      # discover installable skills (was /find-skills)
```

**Rationale:** Three separate skill-meta commands confuse users. One command with flags is the conventional CLI pattern.

**Work:**
- Create `claude/skills/SKILL.md` as the dispatcher
- Move body of `skill-help/` to a default (no-flag) mode
- Move body of `skill-audit/` under `--audit` branch (keep sub-files if any)
- Move body of `find-skills/` under `--find` branch
- Delete old three directories
- Update `claude/README.md` skill catalog table
- Add deprecation note in SKILL.md pointing to new command
- Grep for `/skill-help`, `/skill-audit`, `/find-skills` references across repo; update

**Risk:** Low — these are meta skills, no workflow depends on them.

---

## 2. `/execute` — unified autonomous execution

**Merges:** `kickoff` + `execute-workflow`

**New surface:**

```
/execute <path>             # lightweight autonomous flow (was /kickoff)
/execute <path> --governed  # with audit artifacts (was /execute-workflow)
/execute <path> --skip-readiness
```

**Rationale:** Same shape (requirements → merged). The only real difference is whether governance artifacts are produced. A flag communicates this more clearly than two commands whose names don't hint at the difference.

**Unchanged:** `/plan` and `/execute-plan` stay separate — they serve the manual staged path where the user wants a checkpoint between planning and execution.

**Work:**
- Create `claude/execute/SKILL.md` merging both flows
- Default path = kickoff behavior
- `--governed` branch = execute-workflow behavior (pre-flight config check, artifact folder, disposition loop)
- Preserve config file expected by execute-workflow
- Delete `claude/kickoff/` and `claude/execute-workflow/`
- Update `/postmortem` skill — it references `/execute-workflow` runs by folder convention; verify the artifact path is the same
- Update `claude/README.md` catalog + "Starting execution from a PRD or AERS" section
- Update the skills-deck.md Delivery flow slides

**Risk:** Medium — `/postmortem` reads run artifacts produced by the governed path; make sure folder layout is preserved exactly.

---

## 3. `/ship` — unified delivery command

**Merges:** `pr` + `ship` + `hotfix`

**New surface:**

```
/ship              # PR lifecycle (was /pr)
/ship --release    # PR + configured release steps (was /ship)
/ship --fast       # emergency fast-path, minimal gates (was /hotfix)
/ship --draft      # create as draft
/ship --no-merge   # leave PR open
```

**Rationale:** Three commands for "get this merged" is one too many. `/ship` is the most evocative name and already exists as the release-aware variant — promoting it to the general delivery command makes sense.

**Semantics:**
- Default: checkpoint → branch → commit → push → PR → optional merge (today's `/pr`)
- `--release`: same + runs `ship.config.md` or `CLAUDE.md` Ship-section release steps (today's `/ship`)
- `--fast`: skip non-critical gates, single-commit, auto-merge prompt (today's `/hotfix`)

**Work:**
- Rewrite `claude/ship/SKILL.md` to be the dispatcher with three modes
- Default mode = today's `/pr` body
- `--release` mode = today's `/ship` body
- `--fast` mode = today's `/hotfix` body
- Delete `claude/pr/` and `claude/hotfix/`
- Update `claude/README.md`
- Search for `/pr` and `/hotfix` usage in other SKILL.md files; replace

**Risk:** Medium — hotfix semantics (skip gates, single commit) must not accidentally apply to default mode. Write test cases for the flag router in the SKILL instructions.

---

## 4. Move `/prd-readiness` out of the command surface

**Change:** `claude/prd-readiness/` → `claude/_rubrics/prd-readiness.md` (or `claude/_rubrics/aers-readiness.md`)

**Rationale:** Today it's listed as a slash command but its body is reference material (the AERS rubric). Other skills reference it — that's a library role, not a command role. `_rubrics/` already exists for this exact purpose.

**Work:**
- Move file, drop the `name:` + `description:` frontmatter (rubrics don't need it) or keep as plain markdown
- Update `/prd-validate`, `/kickoff`/`/execute` (post-merge), `/execute-workflow` (post-merge) references from `/prd-readiness` → relative path to `_rubrics/aers-readiness.md`
- Update `claude/README.md` — remove from Requirements skills table, mention under "Referenced rubrics"
- Remove from skills-deck.md Requirements flow; add a brief mention that the rubric lives in `_rubrics/`

**Risk:** Low — no behavior change, just a relocation.

---

## Ordering & suggested commits

Each consolidation can ship as its own PR:

1. **PR A — `/skills` merge** (smallest blast radius, warm-up)
2. **PR B — `/prd-readiness` → `_rubrics/`** (pure move)
3. **PR C — `/ship` merge** (deletes two skills)
4. **PR D — `/execute` merge** (highest-risk, depends on artifact layout)

Do A + B in parallel; then C; then D last so postmortem coupling gets the most thought.

---

## Out of scope (deliberately keeping separate)

- `/plan` + `/execute-plan` — the staged path is a legitimate mode; don't collapse
- `/checkpoint` — primitive; stays standalone and as a callee from `/ship`
- Review suite (`code-review` / `review-adversarial` / `review-gauntlet` / `ba-review-adversarial`) — genuinely distinct lenses
- `/triage` vs `/code-investigate` — different inputs and outputs
- `/whereami` ↔ `/session-save` — paired primitives, not overlapping

---

## Open questions before starting

1. For `/execute --governed`, should existing `/execute-workflow <path>` invocations keep working as an alias for a deprecation window? Or hard-cut?
2. For `/ship --fast`, should it skip the checkpoint entirely, or run a fast subset (lint only, skip tests)?
3. Any external docs or team runbooks that reference `/kickoff`, `/pr`, `/hotfix`, `/skill-help` and need updating?
4. Config file shape: `/execute-workflow` has pre-flight config today. After the merge, is that config required only when `--governed` is passed, or always checked?
