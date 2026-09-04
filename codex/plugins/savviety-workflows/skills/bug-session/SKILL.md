---
name: bug-session
description: "Capture several reported bugs, inspect relevant code, and turn them into distinct actionable GitHub issues. Use for a bug intake session; use triage to diagnose one existing bug and execute-plan to implement fixes."
---

# Bug session

## Workflow
1. Confirm the target repository from context and run gh-readiness before remote work.
   Capture each symptom separately, including actual/expected behavior and available
   reproduction steps. Ask at most two or three focused questions per unclear bug.
2. Read the relevant code, tests, domain vocabulary and existing issues. Distinguish
   confirmed behavior from a hypothesis; do not invent a root cause. Investigate
   locally unless delegated investigation is already authorized and available.
3. Group duplicates; separate independently fixable bugs and order dependent fixes.
   Search open/recent issues before creating anything. Reuse an existing issue only
   when its scope matches, and report the match.
4. Draft a portable issue for each bug: descriptive title, user impact, actual versus
   expected behavior, reproduction, relevant environment, acceptance and dependencies.
   Keep implementation file/module guesses out of the problem statement; put verified
   technical evidence in a clearly marked investigation note when useful.
5. A request to file/create the issues authorizes creation once the repository and
   scope are clear. Otherwise return drafts. Use connected GitHub tools first or a
   configured CLI; pass multiline bodies as structured data or through --body-file.
6. Create dependencies first, use returned issue numbers in later bodies, and return
   links plus any remaining uncertainties. On partial failure, preserve a creation
   ledger and check it before retrying so issues are not duplicated.

## Examples
- "File issues for these three mobile bugs" → investigate, separate, deduplicate,
  create in the named repository, and return the real links.
- "Help me describe this crash" → return a supported issue draft.

## Closed decisions and open decisions
The user's expected behavior is authoritative unless conflicting evidence needs
clarification. Ask only about unresolved behavior or issue grouping that changes scope.

## Do not
Do not fix code during intake, invent issue IDs, report creation without a successful
response, or make a separate approval round for issue creation already requested.

## Codex integration
Use `$bug-session` explicitly or let its description match the request. Resolve sibling
skills inside this plugin. Read AGENTS.md before repository edits; honor the current
host's tool access and delegation rules. Do not require another platform's runtime.
