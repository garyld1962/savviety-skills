# Model Pinning Policy

Some shared Claude skills pin a specific model via the `model:` frontmatter
field. Most don't. This doc explains the policy so future skill authors know
when to pin and when to leave it alone.

## The rule

**Pin only when there's a clear case. Default is unpinned.**

Over-pinning creates friction: a session intentionally running on `opus` loses
its context when a `sonnet`-pinned skill fires mid-chain. Under-pinning
creates waste: a `sonnet` session that invokes a deep-reasoning skill misses
the reasoning headroom.

The answer is to pin skills that have a **clear match** to a model tier and
leave everything else to inherit the session's model.

## Tiers

### `model: opus` — deep reasoning, high-stakes, low frequency

Pin to `opus` when the skill has to *think* and the output shapes downstream
work. These skills typically run once per task, produce structured artifacts,
and benefit from reasoning headroom more than from speed.

Currently pinned to `opus`:

- `thesis`
- `kickoff`
- `grill-me`
- `ideate`
- `prd-validate`
- `spec-review-adversarial`
- `triage`
- `dep-migrate`
- `code-investigate`
- `design-twice`
- `feature-sweep`
- `goal`

### `model: haiku` — lookup, routing, high frequency

Pin to `haiku` when the skill is essentially a dispatcher, formatter, or
lookup. No deep reasoning needed; speed and cost matter more than capability.

Currently pinned to `haiku`:

- `skill-help`
- `repo-status`
- `configure`
- `env-check`

### Unpinned — inherits session

Leave the `model:` field off entirely when:

- The skill should match whatever model the user is currently running on.
- The skill is an **orchestrator** that dispatches specialists (the
  specialists should pick their own tier).
- The skill's whole point is to be **different** from the caller — e.g.,
  `review-adversarial` and `review-gauntlet` exist to challenge the original
  implementer. Static pinning would defeat the purpose; the skill itself
  should pick a model that contrasts with what ran the original work.

Currently unpinned:

- `audit-existing`, `checkpoint`, `changelog`, `execute-plan`, `execute-prd`,
  `hotfix`, `parallel-optimization`, `pr`, `process-tune`, `ship`, `sync-main`,
  `test-plan`, `validate-plan`
- `domain-review`, `review-adversarial`, `review-gauntlet`
- `code-review-professional`, `postmortem`, `prd-acceptance`,
  `ubiquitous-language`, `what-is-it-about`, `work-item`, `k8s-verify`,
  `dep-audit`, `skill-audit`
- `_internal/*` contracts and rubrics unless a specific model pin is added

## How to add a skill

When adding a new skill to `claude/`:

1. Decide which tier it fits by asking: does this skill need to *reason* (opus),
   *dispatch/lookup* (haiku), or *match the session* (unpinned)?
2. If pinning, add `model: opus` or `model: haiku` as the last field in the
   frontmatter block, before the closing `---`.
3. If the case isn't clear, leave it unpinned. A user can always override by
   invoking the skill from a session running the tier they want.

## How to change an existing skill's tier

Changing a skill's `model:` pin is a semi-visible behavioral change — users
who invoke the skill will get a different model than before, which can
affect output quality, token cost, and latency. Treat it as:

- a single-commit change touching just the frontmatter line,
- with a commit message that names the *reason* ("pin to opus — plan output
  was thin on sonnet for large codebases"),
- ideally informed by actual usage evidence, not guesswork.

## Reference

- Claude Code skills frontmatter reference: https://code.claude.com/docs/en/skills.md
- Valid model values: https://code.claude.com/docs/en/model-config.md
