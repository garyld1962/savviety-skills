# Claude review and native workflow update

Reviewed the 48 public Claude entrypoints at commit
`c95088fdb443676d8ec7cfadbfbe60bbc825e3d6`, with deeper inspection of execution,
requirements readiness, acceptance, platform adaptation and installation. This is
a source review with isolated script/installer tests, not live model certification.

## Recommendations for Claude

| Priority | Finding and evidence | Recommended change |
|---|---|---|
| High | [run-plan.mjs](../../claude/execute-plan/workflows/run-plan.mjs) uses `review?.findings ?? []` in reviewGate; missing review output becomes no findings. | Require a completed, schema-valid review with scope and revision evidence. Missing/null output must block. |
| High | The alignment schema includes `allTasksImplemented`, but execution never checks that boolean before deriving the verdict. | Require true and evidence covering every planned task and acceptance criterion. |
| High | The fix loop closes findings from the fixer's `status: fixed`; integration asks to resolve conflicts favoring already-merged lanes. | Recheck each fix, verify integrated behavior and final code head, and resolve conflicts semantically without discarding either side. |
| High | [prd-acceptance](../../claude/prd-acceptance/SKILL.md) explicitly counts MANUAL checks as pass. | Keep manual/unavailable behavior unproved. Require actual observations before acceptance or release. |
| Medium | [drawio](../../claude/drawio/SKILL.md) references missing vendor/shared resources and instructs deletion of editable source after export. | Package required references/helpers, retain source and verify exports independently of XML syntax. |
| Medium | [vault](../../claude/vault/SKILL.md) embeds `/data/obsidian`. | Resolve an explicit/configured vault, preserve conventions and enforce its filesystem boundary. |
| Medium | [feature-sweep](../../claude/feature-sweep/SKILL.md) mixes release research with a hardcoded feature/model opportunity list. | Require dated official sources and actual host capability checks before proposing changes. |
| Medium | Workflow failures can throw before the final report is written; the runtime and prose disagree on terminal finding statuses. | Write reports on all exits; define one disposition vocabulary and test failed/missing-review, partial-task and resume paths. |

These Claude runtime findings are recommendations; this update changes the requested
Codex/Copilot assets and shared installation/validation support. It deliberately does
not regenerate the unrelated Kimi distribution or change the Claude runtime.

## Implemented native changes

- Added nine workflows to both platforms: bug-session, design-twice, drawio,
  feature-sweep, gh-readiness, goal, issue-slices, refactor-brief and vault.
- Preserved Codex consolidations for delivery, kickoff, domain review and skill
  management. [The coverage map](../parity/claude-native.md) records all 48 source
  workflows against 44 Codex entrypoints and Copilot skills/prompt shortcuts.
- Replaced the conflicting wave/lane plan formats with dependency graphs and explicit
  write ownership, automated readiness scoring, optional design comparison, bounded
  repair loops, resume checks and final-head review/proof contracts.
- Added deterministic graph and execution-report validators, a local draw.io URL
  helper, self-contained packaged references and drift detection. Native report
  version 2 is explicitly distinct from Claude's existing version 1.
- Made acceptance checks distinguish manual/unavailable evidence from success.
  Native host capabilities and existing authorization control delegation; there is
  no dependency on Claude's Workflow runtime or invented Copilot commands.
- Fixed installer paths from removed `copilot-native/` to `copilot/`, shipped missing
  governed process/templates, and fail before writes when a manifest source is absent.
  Existing Codex config/hooks/marketplace settings are now user-owned on update.
- Added behavioral tests and CI gates covering coverage, source drift, metadata,
  missing references, installation/update and false-success failure cases.

## Compatibility and remaining work

Older wave/lane plans need an explicit migration to task metadata; they are rejected
with a diagnostic, not silently reinterpreted. The shared validators need Python 3
and PyYAML. They verify structure and declared evidence, not the truth of fabricated
evidence; agents must inspect actual check output and repository state.

Skill coverage does not imply identical orchestration internals. New workflows and
core execution paths are durable Copilot skills; some existing workflow mappings
remain prompt-only and require a prompt-capable host. Current [GitHub skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
and [VS Code prompt documentation](https://code.visualstudio.com/docs/agent-customization/prompt-files)
describe this distinction. Prompt category directories may require explicit workspace
locations. Live host discovery and desktop draw.io export remain integration checks.

Installer tree updates still manage the shared destination namespaces. Custom assets
inside those trees need explicit preservation rules; a future ownership inventory
would be safer than expanding ad hoc path exceptions. Keep historical source copies
out of active navigation and make platform coverage checks part of every skill change.

Version 2 success reports certify committed code. Explicit no-commit requests return
draft verification evidence without attributing uncommitted edits to an older SHA.

## Validation

Run the repository's existing Workflow syntax/JSON/shell checks and Kimi drift check,
plus `python3 codex/scripts/validate_codex_assets.py`,
`bin/sync-native-contracts --check`, `python3 bin/validate-native-parity`, and
`python3 -m unittest discover -s tests -v`.

The behavioral suite covers dependency cycles, unknown/duplicate IDs, overlapping
future globs, traversal, malformed YAML/headings, JSON date metadata, source fences,
missing/stale review output, false alignment, manual/boolean proof, malformed SHAs,
retry exhaustion, risk dispositions, Unicode diagram round-tripping, invalid diagram
graphs, both installers and update preservation. An independent forward pass found
parser/type edge cases; those cases were reproduced and added to the fixes/tests.
