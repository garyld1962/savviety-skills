# Global Token Management Features

Summarized from `~/.claude/CLAUDE.md` — sections 2 and 10.

---

## Section 2 — Token Efficiency

Three dimensions:

### Input (what you read)
- Targeted reads over broad exploration — `rg` + line-range views, not `cat` on whole files
- Don't re-read files already in context this session
- Don't enumerate a directory tree when you need one file
- Sample, don't exhaust — 20 lines of a log usually tells you what 20,000 would
- Prefer `--help`/`man`/focused grep over reading a whole doc for a specific question

### Output (what you write)
- No preamble, no "I'll help you with that", no narration of routine actions
- No recap of the user's request back to them
- No closing reassurance
- Prose over bullets for continuous content; bullets only for genuinely enumerable items
- Match reply length to question weight — one-line questions get one-line answers

### Context (what you reuse)
- Don't re-emit unchanged code — use `str_replace` and targeted edits, not full-file rewrites
- Don't repeat the same caveat across multiple sections of a reply
- Don't restate the plan after executing it unless execution deviated
- Compress summaries of prior work aggressively

**Test:** if removing a sentence wouldn't change what the user can act on, remove it.

---

## Section 10 — Context Window Hygiene

Suggest a fresh session (`/exit`) at phase boundaries where prior context becomes ballast:

| Boundary | Why clear |
|---|---|
| Plan → Execute | Once written to a file, the exploration that produced it is dead weight |
| Research → Implement | Findings are captured; search queries don't help implementation |
| Review → Fix | Review context biases toward reviewer framing, not code reality |
| Long debugging → Clean attempt | 15+ turns pollutes context with wrong hypotheses |
| Multi-repo switch | Prior repo file contents waste context unless the dependency is the point |

Also flags **mid-session context drift** — when the current task has shifted far enough that most existing tool output is irrelevant to what's being worked on now.
