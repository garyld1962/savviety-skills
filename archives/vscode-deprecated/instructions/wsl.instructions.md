---
applyTo: "**/*.{sh,bash,zsh,ps1,cmd,bat,yml,yaml,json,toml,Dockerfile,Makefile}"
description: "Linux execution environment rules. The VS Code integrated terminal is already Linux (WSL2). No wsl prefix needed. Applies to shell scripts, config files, and build definitions."
---

# Linux Execution Environment

All terminal commands run in the **VS Code integrated terminal**, which is a Linux environment (WSL2 Ubuntu). Do NOT prefix commands with `wsl -d` — run them directly.

## The run.sh Pattern

If the project has `.scripts/run.sh`, it is the **single entrypoint** for all terminal operations:

```
bash .scripts/run.sh <command> [args...]
```

### Rules when run.sh exists

- **ALWAYS** route commands through `run.sh` — never run raw `pnpm`, `npm`, `dotnet`, `git`, or other CLI tools directly.
- **NEVER** create throwaway `.sh` scripts for one-off commands. Use `run.sh exec <command>` instead.
- If a command pattern is needed repeatedly, add it as a new `case` in `run.sh`.
- `run.sh` handles environment setup (nvm, PATH, working directory) — do not duplicate this in terminal commands.

### Rules when run.sh does NOT exist

- Run commands directly in the integrated terminal.
- The terminal has standard tools available: `dotnet`, `git`, `curl`, `ss`, `ps`, `kill`, `rg`, `pnpm`, etc.

## Path Handling

- **Always use forward slashes** (`/`) for all paths.
- **Native WSL paths** (`/home/gary/repos/...`) are fast. Prefer these for all project files.
- **Never use Windows-style paths** (`C:\Users\...`) in any config or script.

## Line Endings

- **All files must use LF** (Unix line endings), not CRLF.
- Git should be configured with `core.autocrlf=input`.

## Environment Considerations

- **Shell**: Bash is the default. Do not assume `zsh` features in scripts.
- **Docker**: Available via `docker` and `docker compose` if installed.
