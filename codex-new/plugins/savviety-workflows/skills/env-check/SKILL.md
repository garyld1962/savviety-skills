---
name: env-check
description: "Detect shell, OS, repo root, package manager, path, and command-routing constraints before giving commands across local, WSL, remote, or container environments."
---

# Env Check

Use this before environment-sensitive commands.

Read `references/checklist.md` for Codex-native checks. `references/legacy/` is archival only.

Return the detected environment, safe command style, missing tools, and any commands that need user approval.
