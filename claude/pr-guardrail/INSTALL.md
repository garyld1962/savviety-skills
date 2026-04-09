# PR Guardrail — Installation

## What it does

A PreToolUse hook that intercepts `gh pr create` commands and checks for existing open PRs before allowing the command. If open PRs are found (especially on the current branch), it blocks the command and asks the user how to proceed.

**Behavior:** warn + prompt. Never silent, never hard-blocking without giving options.

## Install

Add this to your **global** `~/.claude/settings.json` (so it applies across all repos):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "if": "Bash(gh pr create:*)",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/repos/skills/claude/pr-guardrail/pr-guardrail.sh",
            "timeout": 15,
            "statusMessage": "Checking for existing PRs..."
          }
        ]
      }
    ]
  }
}
```

**Important:** Merge this into your existing `hooks` section — don't replace the whole file. See the `update-config` skill for safe merging.

## How it works

1. The hook fires on any Bash tool call matching `gh pr create`
2. It runs `gh pr list --author @me --state open` to find your open PRs
3. It runs `gh pr view` to check if the current branch already has a PR
4. If **any** open PRs exist, it blocks and shows the list with options
5. The agent surfaces the options to you and waits for your decision

## Options when blocked

- **[1] Push to existing PR's branch** — just push your commits to the existing PR
- **[2] Stack a new branch** — create a new branch from current, then PR that
- **[3] Close the existing PR first** — close the old one, then create new
- **[4] Override** — create the new PR anyway (for legitimate cases)

## Uninstall

Remove the `PreToolUse` entry with matcher `Bash` and `if: "Bash(gh pr create:*)"` from `~/.claude/settings.json`.
