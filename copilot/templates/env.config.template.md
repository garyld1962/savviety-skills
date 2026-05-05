# Shell Environment Config (Copilot)

This file defines your shell environment for cross-platform command routing.
Fill in the sections below, then save to one of:
- `$HOME/.copilot/env.config.md` (user-level, applies to all repos)
- `<project>/.github/instructions/env.config.md` (project-level override)

## Shells

List the shells you actively use.

```yaml
shells:
  - name: <FILL IN: e.g., zsh>
    os: <FILL IN: e.g., macOS, Linux, Windows>
    notes: <OPTIONAL>
  # Add more shells as needed:
  # - name: bash
  #   os: Linux
  #   notes: WSL2 on Windows host
  # - name: pwsh
  #   os: Windows
  #   notes: PowerShell 7
```

## Routing Rules

Define how commands should be routed when a shell/project mismatch is detected.

```yaml
routing_rules:
  default_action: <FILL IN: direct | switch-terminal | warn>

  # Per-shell overrides (optional):
  # overrides:
  #   - when_shell: pwsh
  #     project_expects: bash
  #     action: switch-terminal
  #     message: "This project expects a Unix shell. Switch to a Linux terminal."
```

## Hosts

<OPTIONAL> Map specific hosts to their default shells.

```yaml
# hosts:
#   - name: my-workstation
#     default_shell: zsh
#     os: macOS
```

## Terminal Switching

<OPTIONAL> Rules for when to recommend switching terminals vs wrapping commands.

```yaml
# terminal_switching:
#   prefer_switch_over_wrap: true
#   wrap_only_when: "user explicitly requests a bridge command"
```
