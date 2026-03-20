---
description: >-
  Audit project dependencies: check for vulnerabilities, outdated packages,
  unused deps, and license compliance. Adapts to pnpm/npm/yarn/cargo/pip.
argument-hint: '[--security-only] [--check outdated|unused|licenses] [--fix]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Dependency Health Check

Comprehensive audit of project dependencies — security vulnerabilities, outdated packages, unused dependencies, and license compliance.

## When to Use

- Before cutting a release
- Periodically (monthly) for hygiene
- After adding new dependencies
- When investigating supply chain concerns
- When a CVE advisory drops for a dependency you might use

## Arguments

- `--security-only` — run only the vulnerability audit (fastest)
- `--check <type>` — run a specific check: `outdated`, `unused`, `licenses`, `security`
- `--fix` — auto-update patch-level vulnerable dependencies (security only)

---

## CRITICAL: Do Not Guess

- **Package manager**: DETECT which package manager is in use. Do NOT assume npm or pnpm. Check for lock files first (Step 1).
- **Audit command syntax**: Different package managers have different audit commands and flags. Verify the correct syntax for the detected manager.
- **"Unused" detection**: Build tools, PostCSS plugins, Babel plugins, type-only packages (`@types/*`), and CLI tools used in `scripts` fields are easily missed by import scanning. Do NOT flag a dependency as unused unless you have checked ALL of these locations.
- **License classification**: Do NOT classify licenses you don't recognize. Report them as "Unknown" for human review.
- **Vulnerability severity**: Report the ACTUAL severity from the audit tool output. Do NOT re-classify severities based on your own judgment.

---

## Step 1: Detect Package Manager

Check the project root for lock files IN THIS ORDER:

| File Found | Manager | Lock File |
|------------|---------|-----------|
| `pnpm-workspace.yaml` OR `pnpm-lock.yaml` | pnpm | `pnpm-lock.yaml` |
| `package-lock.json` | npm | `package-lock.json` |
| `yarn.lock` | yarn | `yarn.lock` |
| `bun.lock` | bun | `bun.lock` |
| `Cargo.toml` | cargo | `Cargo.lock` |
| `requirements.txt` OR `pyproject.toml` | pip/uv | varies |

```bash
# Check which lock files exist
ls pnpm-lock.yaml pnpm-workspace.yaml package-lock.json yarn.lock bun.lock Cargo.toml Cargo.lock requirements.txt pyproject.toml 2>/dev/null
```

If monorepo, identify workspace packages:

```bash
# pnpm
cat pnpm-workspace.yaml

# npm/yarn
cat package.json | grep -A 10 '"workspaces"'
```

### Example: Correct detection

```
Found: pnpm-lock.yaml, pnpm-workspace.yaml
Manager: pnpm (monorepo with 6 workspaces)
```

### Example: INCORRECT

```
# WRONG: Running npm commands in a pnpm project
npm audit  # ← will give incomplete/wrong results
```

---

## Step 2: Security Vulnerabilities

### Node.js (pnpm/npm/yarn)

```bash
pnpm audit --json 2>/dev/null || npm audit --json 2>/dev/null
```

Parse results and classify:

| Severity | Action |
|----------|--------|
| Critical | **FAIL** — must fix before release |
| High | **WARN** — should fix; check if exploitable in your context |
| Moderate | **INFO** — note for backlog |
| Low | **INFO** — note only |

For EACH vulnerability, report:

1. Package name and installed version
2. Vulnerability ID (CVE or GHSA number)
3. Severity and CVSS score (from the audit output — do NOT make up scores)
4. Whether a fix is available (patched version number)
5. Whether it is a **direct** dependency (you can fix it) or **transitive** (parent must update)

### Example: Vulnerability finding

```
CRITICAL: lodash@4.17.20
  CVE-2021-23337 — Prototype Pollution
  CVSS: 7.2 (from audit output)
  Fix: Upgrade to lodash@4.17.21
  Type: Direct dependency (in package.json)
```

### Rust (cargo)

```bash
cargo audit 2>/dev/null
```

If `cargo-audit` is not installed, report: "cargo-audit not installed. Run `cargo install cargo-audit` to enable." Do NOT fail the audit.

### Python (pip)

```bash
pip-audit --format json 2>/dev/null || safety check --json 2>/dev/null
```

---

## Step 3: Outdated Packages

### Node.js

```bash
pnpm outdated --json 2>/dev/null || npm outdated --json 2>/dev/null
```

Classify each update:

| Update Type | Risk | Example |
|-------------|------|---------|
| Patch | Low — bug fixes only | 1.2.3 → 1.2.4 |
| Minor | Medium — new features, backward compatible | 1.2.3 → 1.3.0 |
| Major | **High — breaking changes possible** | 1.2.3 → 2.0.0 |

**Report:**
- Total outdated count
- Major updates listed individually (these need migration plans)
- Minor/patch update counts

### Example: Outdated report

```
Outdated: 12 packages
  Major (need migration):
    - typescript 5.3.3 → 5.7.2
    - vitest 1.6.0 → 2.1.0
  Minor: 5 packages
  Patch: 5 packages
```

### Rust

```bash
cargo outdated 2>/dev/null
```

---

## Step 4: Unused Dependencies

### Node.js

For each dependency in `package.json` (both `dependencies` and `devDependencies`):

1. Search source tree for imports:

   ```bash
   grep -r "from ['\"]<package>" src/ --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx'
   grep -r "require(['\"]<package>" src/ --include='*.ts' --include='*.js'
   ```

2. **ALSO check these locations before flagging as unused:**
   - `scripts` field in `package.json` (CLI tools like vitest, eslint, tsc)
   - Config files (`.eslintrc*`, `vite.config.*`, `postcss.config.*`, `tailwind.config.*`, `jest.config.*`, `vitest.config.*`)
   - Type packages (`@types/*`) — check if the corresponding package is used
   - Babel/PostCSS/Vite plugins — referenced in config, not imported in source
   - Peer dependencies of other installed packages

**Classification:**

| Category | Confidence | Action |
|----------|------------|--------|
| No imports found anywhere (source + config + scripts) | Definitely unused | Safe to remove |
| Only imported in one place | Possibly unused | Flag for review |
| Used only in scripts/config | Build tool | Do NOT flag as unused |
| `@types/*` package | Type dependency | Check if base package is used |

### Example: CORRECT unused detection

```
Definitely unused:
  - chalk (no imports in source, config, or scripts)

Possibly unused:
  - lodash (imported in 1 file — verify if still needed)

NOT flagged (build tools):
  - vitest (used in scripts.test)
  - @types/node (type dependency for Node.js)
  - postcss (referenced in postcss.config.js)
```

### Example: INCORRECT

```
# WRONG: Flagging vitest as unused because it's not imported in src/
Unused: vitest  # ← It's a test runner invoked via scripts, not imported
```

---

## Step 5: License Compliance

### Node.js

```bash
npx license-checker --json --production 2>/dev/null
```

Or manually check `license` fields in `node_modules/*/package.json`.

Classify licenses:

| Category | Licenses | Risk |
|----------|----------|------|
| Permissive | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD | **PASS** |
| Weak Copyleft | LGPL-2.1, LGPL-3.0, MPL-2.0 | **WARN** — review usage context |
| Strong Copyleft | GPL-2.0, GPL-3.0, AGPL-3.0 | **FAIL** — may require your code to be open source |
| Unknown | UNLICENSED, missing, custom, or anything you don't recognize | **WARN** — review manually |

**Do NOT provide legal advice.** Flag potential issues and recommend consulting the organization's open source policy.

---

## Step 6: Auto-Fix (only with `--fix`)

Only for security vulnerabilities with available patch-level fixes:

```bash
pnpm audit --fix 2>/dev/null || npm audit fix 2>/dev/null
```

**Only apply patch-level fixes.** For minor/major version bumps, report as manual actions.

After fixing:

```bash
pnpm install     # Regenerate lock file
pnpm -r build    # Verify build still works
```

**If build breaks after auto-fix:** Revert immediately:

```bash
git checkout -- pnpm-lock.yaml
pnpm install
```

Report which fixes were applied and which broke the build.

---

## Step 7: Report

```
## Dependency Audit

**Manager:** pnpm | **Workspaces:** N | **Total deps:** N

### Security
| Severity | Count | Fixable |
|----------|-------|---------|
| Critical | N | N |
| High | N | N |
| Moderate | N | N |
| Low | N | N |

[List critical/high vulnerabilities with CVE IDs and fix versions]

### Outdated
- Major updates available: N [list each]
- Minor updates available: N
- Patch updates available: N

### Unused (suspected)
- Definitely unused: [list]
- Possibly unused: [list]

### Licenses
- Permissive: N
- Weak copyleft: N [list]
- Strong copyleft: N [list — REVIEW REQUIRED]
- Unknown: N [list]

### Verdict: CLEAN / NEEDS ATTENTION / CRITICAL

[CLEAN: no critical/high vulns, no copyleft concerns]
[NEEDS ATTENTION: has high vulns or copyleft deps]
[CRITICAL: has critical vulns or AGPL/GPL deps in production]
```

---

## Rules

1. **Read-only by default.** Only `--fix` makes changes, and only patch-level security fixes.
2. **Context matters.** A critical vulnerability in a dev-only tool is less urgent than a moderate vulnerability in a production HTTP parser. Note whether vulnerable packages are in `dependencies` vs `devDependencies`.
3. **Don't cry wolf.** Only flag unused deps you are confident about. Build tools are NOT unused just because they aren't imported in source code.
4. **License is not legal advice.** Flag potential issues but recommend consulting the organization's open source policy for copyleft questions.
5. **Transitive vs direct.** ALWAYS note whether a vulnerable package is a direct dependency (fixable by you) or transitive (requires the parent package to update).
