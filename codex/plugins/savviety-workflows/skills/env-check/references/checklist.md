# Environment Check Checklist

Use this to diagnose local shell and toolchain issues.

## Check

- Shell and PATH.
- Language runtimes.
- Package managers.
- Repo-local config.
- Codex config and hooks when relevant.
- Required env vars without printing secret values.
- Network or auth prerequisites for requested commands.

## Output

- `OK`: ready.
- `WARN`: usable with caveats.
- `FAIL`: missing required tool or config.

Never print secret values. Show names only.

