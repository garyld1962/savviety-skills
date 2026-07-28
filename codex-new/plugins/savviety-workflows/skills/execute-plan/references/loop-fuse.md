# Execute Plan Loop Fuse

Use this gate before rerunning verification, restarting dev servers, changing ports,
or trying alternate tools for the same failed check.

## Hard Stop Rules

Stop and report instead of continuing when any condition is true:

- The same command, endpoint, test, or UI route fails twice with the same signature.
- Two different tools fail against the same target without adding new evidence.
- A verification command is discovered to be wrong, racy, or malformed.
- A dev server start fails once because of port/process state and cleanup is not obvious.
- A mutation check uses the same record in parallel, or would mix create/update/delete concurrently.
- More than 10 minutes or 3 verification attempts have been spent after implementation is otherwise complete.

## Failure Signature

Record a compact signature before deciding to retry:

- command or route
- status code or exit code
- first relevant error line
- whether the failure is app behavior, environment, permissions, or verification-procedure error

If the next attempt has the same signature, do not keep varying tools or flags.

## Required Stop Report

When the fuse trips, stop active dev servers you started and report:

- exact command or route
- exact status/exit code and error text
- what already passed
- likely class: app bug, environment blocker, permission blocker, or bad verification procedure
- remediation plan with the next single command or code change

Do not continue into broader acceptance, browser checks, alternate ports, or cleanup beyond stopping your own running processes.

## Serial Mutation Rule

For CRUD acceptance checks:

1. Create a fresh record.
2. Save its ID and timestamps.
3. Patch that exact record.
4. Verify immutable/mutable fields.
5. Delete or soft-delete that record.

Never run update and delete probes for the same record in parallel.
