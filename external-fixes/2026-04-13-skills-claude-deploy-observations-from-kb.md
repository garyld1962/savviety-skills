# Observations: ~/repos/skills/claude deploy-UX issues surfaced while bootstrapping `kb`

| Field | Value |
|-------|-------|
| **Date** | 2026-04-13T04:50:00Z |
| **Source repo** | `~/repos/skills` (internal, no version tag) |
| **Related upstream issue** | None filed |
| **Applied in** | `~/repos/kb/.claude/` (new project bootstrap, not plugin cache) |
| **Nature** | Structural / deploy-UX observations, not in-place file edits |

## Reason

While bootstrapping a new project (`~/repos/kb`) and asked to "copy the claude skills and related files from `~/repos/skills/claude` to `.claude` in the kb repo," I hit three friction points that suggest the source layout in `~/repos/skills/claude/` does not match the destination layout expected in a project's `.claude/` folder. This doc records what I had to adjust so the skills repo can decide whether to change its source layout or ship a deploy script.

## Source layout (today)

```
~/repos/skills/claude/
├── README.md                  # Skill catalog (doc)
├── SESSION-CONTEXT.md          # Per-session Claude context (config)
├── _rubrics/                  # Shared rubric data (used by skills)
├── changelog/                 # Skill folder
├── checkpoint/                # Skill folder
├── plan/                      # Skill folder
└── ... (38 more skill folders)
```

## Destination layout (what Claude Code actually expects)

Based on `~/repos/bakerst/baker-street/.claude/`:

```
<project>/.claude/
├── README.md                  # Top-level (not inside skills/)
├── SESSION-CONTEXT.md          # Top-level (not inside skills/)
├── settings.json              # Project permissions + hooks
├── agents/                    # Project-specific agents (often empty)
└── skills/                    # <- skill folders go HERE
    ├── _rubrics/
    ├── changelog/
    ├── checkpoint/
    └── ...
```

## Friction points

### 1. Naive copy puts top-level files in the wrong place

`cp -r ~/repos/skills/claude/. .claude/skills/` places `README.md` and `SESSION-CONTEXT.md` **inside** `.claude/skills/`, not at `.claude/` root. Claude Code auto-loads `SESSION-CONTEXT.md` only when it's at `.claude/` root, so the naive copy silently breaks auto-context. I had to `mv` them up one level after copying.

**Suggested fix upstream**: either (a) restructure `~/repos/skills/claude/` so top-level files live in a sibling folder (`~/repos/skills/claude-root-files/`), or (b) ship a deploy script (`deploy-skills claude <target>`) that knows the correct mapping. The README already references `deploy-skills claude` but no such script exists in the repo today — `archives/deploy-deprecated.sh` is the only match.

### 2. `settings.json` has no canonical template in `~/repos/skills/claude/`

Every project's `.claude/` needs a `settings.json` for permissions and hooks. There's no template in the skills repo, so I copied from `~/repos/bakerst/baker-street/.claude/settings.json` as a starting point.

**Suggested fix upstream**: add `~/repos/skills/claude/settings.template.json` with language-agnostic defaults (permissions + pr-guardrail + post-commit hook only), so new projects have a known starting point.

### 3. Baker-street's `settings.json` has a language-specific pre-commit hook

The `settings.json` I copied has this `PreToolUse` hook:

```json
{
  "matcher": "Bash(git commit:*)",
  "hooks": [
    { "type": "command",
      "command": "pnpm -r build --reporter=silent 2>&1 | tail -30",
      "timeout": 60000 }
  ]
}
```

This hardcodes a TypeScript/pnpm workflow. `kb` is a Python repo (uv + pyproject.toml), so this hook would fail on every commit if copied verbatim. I removed it.

**Suggested fix upstream**: when a template `settings.json` ships in the skills repo (per observation #2), leave the `PreToolUse` build hook empty or provide language variants (`settings.template.ts.json`, `settings.template.py.json`, `settings.template.rs.json`).

## Changes applied in the target repo

For the record, the end state in `~/repos/kb/.claude/`:

- `skills/` — all 39 skill folders + `_rubrics` + `changelog` (copied verbatim)
- `README.md` — moved up from `skills/`
- `SESSION-CONTEXT.md` — moved up from `skills/`
- `agents/` — created empty
- `settings.json` — copied from baker-street, `pnpm -r build` PreToolUse hook removed

No skill content was modified.

## Re-application

N/A — no plugin cache files were touched. These observations exist so `~/repos/skills` can decide whether to restructure or ship a deploy script. If the repo evolves, the `~/repos/kb` project will want to re-sync by `rsync`-ing updated skill folders from `~/repos/skills/claude/` into `~/repos/kb/.claude/skills/` (careful: exclude `README.md` and `SESSION-CONTEXT.md` from the rsync, or they'll land in the wrong place again).
