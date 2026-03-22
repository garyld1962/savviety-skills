---
applyTo: "**/*.{sh,bash,zsh,ps1,cmd,bat,yml,yaml,json,toml,Dockerfile,Makefile}"
description: "WSL2/Linux execution environment rules. The repository lives in WSL2 Linux; VS Code runs on Windows. All terminal commands must execute inside WSL. Applies to shell scripts, config files, and build definitions."
---

# WSL2 / Linux Execution Environment

This repository lives inside **WSL2 Linux** (Ubuntu). VS Code runs on **Windows** and connects to WSL via the Remote - WSL extension. All terminal commands must execute inside the WSL Linux environment, not Windows.

## The run.sh Pattern

If the project has `.scripts/run.sh`, it is the **single entrypoint** for all terminal operations:

```
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh <command> [args...]
```

### Rules when run.sh exists

- **ALWAYS** route commands through `run.sh` — never run raw `pnpm`, `npm`, `dotnet`, `git`, or other CLI tools directly in a Windows terminal.
- **NEVER** create throwaway `.sh` scripts for one-off commands. Use `run.sh exec <command>` instead.
- If a command pattern is needed repeatedly, add it as a new `case` in `run.sh`.
- `run.sh` handles environment setup (nvm, PATH, working directory) — do not duplicate this in terminal commands.

### Rules when run.sh does NOT exist

- Use the VS Code integrated terminal (which connects to WSL automatically).
- Run commands as normal Linux commands — the terminal is already inside WSL.

## Path Handling

- **Always use forward slashes** (`/`) for all paths in scripts, configs, and code.
- **Native WSL paths** (`/home/gary/repos/...`) are fast. Prefer these for all project files.
- **Mounted Windows paths** (`/mnt/c/...`, `/mnt/d/...`) have slower I/O and permission quirks. Avoid for build artifacts, `node_modules`, or anything performance-sensitive.
- **Never use Windows-style paths** (`C:\Users\...`) in any Linux-executed script or config. They don't resolve inside WSL.
- When a tool outputs a Windows path (e.g., from a VS Code extension), convert it: `C:\Users\sql_1\source` → `/mnt/c/Users/sql_1/source`.

## Line Endings

- **All files must use LF** (Unix line endings), not CRLF.
- Git should be configured with `core.autocrlf=input` to prevent CRLF from creeping in.
- If a file has CRLF and a script fails with `\r: command not found`, the line endings are wrong.

## Environment Considerations

- **Shell**: Bash is the safe default. Do not assume `zsh` features in scripts.
- **Node.js / nvm**: If the project uses nvm, `run.sh` sources it. Raw terminal sessions may not have nvm loaded — use `run.sh` or source nvm manually.
- **Docker**: Docker Desktop runs via WSL2 backend. `docker` and `docker compose` commands work natively in the WSL terminal.
- **GPU workloads**: NVIDIA CUDA is available inside WSL2. GPU containers need `runtime: nvidia` or `deploy.resources.reservations.devices` in compose files.
- **File permissions**: Files on native WSL paths (`/home/...`) have proper Linux permissions. Files on `/mnt/c/...` may show `777` — don't rely on permissions for mounted Windows drives.
