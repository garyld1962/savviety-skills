---
name: feature-sweep
description: "Audit installed skills against verified current platform releases and propose or apply targeted improvements. Use after a Codex or Copilot release, or to find useful new integrations; use a skill quality audit for ordinary wording and trigger problems."
---

# Feature sweep

Options: --skill <name>, --feature <capability>, --since <date>, --apply.

## Workflow
1. Identify the actual host, installed skill roots, version and exposed tools from
   local context. Read names/descriptions first; filter by the requested scope.
2. Check current official release notes and documentation for that host. Record the
   date checked, release/version, source URL, availability and prerequisites for
   each relevant feature. For OpenAI behavior check local version/configuration first
   and use official OpenAI documentation as fallback. Use official GitHub/Microsoft
   sources for Copilot. Treat unavailable browsing as an explicit research limitation.
3. Map verified capabilities to concrete workflow steps: judgment, implementation,
   context retrieval, review or repeated work. Read full instructions only for
   candidates. Larger advertised context is not a reason to read unrelated files.
4. Propose each change with skill/path, feature, before/after excerpt, expected benefit,
   prerequisites, validation and risk. Distinguish released, preview and unavailable
   features. Do not prescribe a model, tool or scheduler without verification.
5. Default to a review report. --apply or a request to update skills authorizes the
   scoped edits; apply relevant changes and validate metadata, references, scripts
   and representative behavior. Preserve existing contracts and user configuration.
   Stop only for material choices outside that authorization.
6. Report applied, skipped and deferred opportunities with sources. Persist changes
   through the owning repository's workflow. Create schedules only if explicitly
   requested; an opportunity to automate is not authorization to register a job.

## Example
"Check our review skills against the latest Copilot release" → date-stamped proposals
with official sources; no changes unless application was requested.

## Closed decisions and open decisions
Preserve configured model, permissions and delivery choices. List uncertain capability
availability as open; do not silently turn a preview feature into a required dependency.

## Do not
Do not use a hardcoded feature wish list as evidence, promise automatic runtime behavior
from prose alone, or apply speculative changes when sources cannot be checked.

## Copilot integration
This skill is the durable entrypoint for Copilot hosts that load agent skills.
The matching prompt file is an optional VS Code shortcut. Read repository instructions
before edits; use the tools actually exposed by the host, including connected GitHub
access when available. A prompt or skill does not itself grant additional permissions.
