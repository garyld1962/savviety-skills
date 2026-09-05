---
name: gh-readiness
description: "Check GitHub access, target repository and required capabilities before creating issues, PRs, releases or other GitHub changes. Use when access is unknown or changed; avoid repeated probes once this session established the needed capability."
---

# GitHub readiness

This is a read-only capability check; do not create a test issue or PR.

## Checks
1. Identify the intended host and owner/repository from the request and local remote
   configuration. Report a sanitized repository URL, not credentials embedded in a
   remote. Do not assume github.com when an enterprise host is configured.
2. Prefer an available GitHub connection. Read the target repository and relevant
   resource to verify access; inspect callable capabilities and repository permissions
   for the upcoming operation. Missing CLI is not failure when the connection suffices.
3. When CLI is required, use command -v gh, gh auth status --hostname <host>, and a
   read-only API call to the intended repository. Do not use auth token, --show-token,
   dump environment variables, or start login/refresh as a side effect of this check.
4. Report the identity/host when available, repository match, read access and write
   permission evidence. Classic OAuth scopes are only one credential model: a
   fine-grained or GitHub App token cannot be judged from a missing "repo" scope.
   A readable repository alone does not prove permission to create a release or PR.
5. Reuse the successful check during this session unless account, host, repository,
   operation or an authentication failure changes the evidence.

## Result
- PASS: the selected path supports the requested operation, with evidence.
- PARTIAL: reading works but required write capability or repository selection is
  unverified; name the uncertainty and the narrow next check.
- FAIL: no usable path reaches the intended resource; report the actual failure and
  recovery step. Do not claim access was restored until a subsequent read succeeds.

## Example
"File a bug using our GitHub connection" → check that repository and issue creation
capability; do not require installing gh when the connection already supports it.

## Closed decisions and open decisions
The target repository/host is a closed decision when specified. Resolve conflicting
remotes or missing operation permissions before a write.

## Do not
Do not print tokens, request broader access speculatively, mutate authentication,
or conflate a missing tool with a missing GitHub capability.

## Codex integration
Use `$gh-readiness` explicitly or let its description match the request. Resolve sibling
skills inside this plugin. Read AGENTS.md before repository edits; honor the current
host's tool access and delegation rules. Do not require another platform's runtime.
