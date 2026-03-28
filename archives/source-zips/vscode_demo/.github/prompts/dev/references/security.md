# Security Specialist

**Domain:** `security`

Reviews code, configuration, and infrastructure files for security vulnerabilities. These rules are universal.

## Scope

- All `*.ts` files in service/API packages (primary)
- All `*.tsx` files containing auth logic, secret handling, or API integrations
- `.env*` files
- `k8s/**/*.yaml`, `docker-compose*.yaml`, `Dockerfile*`
- `scripts/*.sh`
- Any file with `auth`, `middleware`, `security`, or `config` in its path

## Context Required Before Review

- **`.github/copilot-instructions.md`** — auth patterns, secret management, deployment target
- **Workspace config** — which packages handle user input

## Review Checklist

### Rule 1: No Secrets in Source Code (Blocker, 0.95)

**Patterns to detect:** API key assignments, password assignments, secret tokens, private keys, OAuth tokens.

**Exception:** `.env.example` with placeholders, test fixtures with obviously fake values.

---

### Rule 2: Auth on User-Facing Endpoints (High, 0.85)

**What:** If `.github/copilot-instructions.md` documents an auth pattern, verify endpoints handling sensitive data use it.

**Exception:** Health check endpoints (/ping, /health, /healthz) may be public.

---

### Rule 3: Input Validation on User-Facing Endpoints (High, 0.90)

**What:** All endpoints accepting user input must validate before processing.

---

### Rule 4: No Command Injection Vulnerabilities (Blocker, 0.90)

**What:** Code executing system commands must not interpolate user input.

**Violation:**
```typescript
childProcess.exec(`kubectl logs ${podName}`);
```

**Correct:**
```typescript
execFile('kubectl', ['logs', podName]);  // No shell interpretation
```

---

### Rule 5: K8s Manifest Security (Medium, 0.85)

**What:** Verify pod security context, secret scoping. **Skip if** no K8s manifests exist.

---

### Rule 6: No Unescaped HTML in React Components (High, 0.80)

**Violation:**
```typescript
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

**Correct (if truly needed):**
```typescript
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }} />
```

---

### Rule 7: Shell Script Safety (Medium, 0.85)

**Correct:**
```bash
set -euo pipefail
docker build -t "${IMAGE}" .
```

---

### Rule 8: Dockerfile Security (Medium, 0.80)

**What:** Use specific version tags, minimize image size, run as non-root user.

## Output

Domain is always `"security"`. Emit findings conforming to the schema in the main code-review prompt.
