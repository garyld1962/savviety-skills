# Dependency Audit Reporting

Use this for dependency health checks.

## Check

- Package manager and lockfile state.
- Outdated direct dependencies.
- Known vulnerabilities from available audit tooling.
- Deprecated packages.
- Runtime or framework compatibility risks.
- Transitive risk only when it has a concrete impact.

## Report

- `Critical`: exploitable security or broken runtime compatibility.
- `Major`: upgrade needed soon or blocks supported platform.
- `Minor`: stale but low-risk.
- `Notes`: informational updates.

Include exact package names, current versions, target versions when known, and verification commands.

