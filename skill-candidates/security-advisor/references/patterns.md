# Security Advisor — Patterns

Proven security engineering patterns for building secure systems.

---

## Pattern 1: STRIDE Threat Modeling

**When**: Designing a new feature, API, or system; evaluating security of a proposed architecture.

**The Pattern**:

STRIDE is a checklist of threat categories. Walk through each for every trust boundary — the edges where data crosses from one component to another (user → API, API → DB, service → service).

| Threat | Question to ask | Example mitigation |
|--------|----------------|-------------------|
| **S**poofing | Can an attacker impersonate a user or service? | Strong auth, mutual TLS |
| **T**ampering | Can data be modified in transit or at rest? | HTTPS, signatures, HMAC |
| **R**epudiation | Can a user deny performing an action? | Immutable audit logs |
| **I**nformation Disclosure | What sensitive data could leak? | Encryption, least privilege, error handling |
| **D**enial of Service | Can the system be made unavailable? | Rate limiting, circuit breakers |
| **E**levation of Privilege | Can a user gain higher permissions than intended? | RBAC, authorization checks on every request |

**Practical process**:
1. Draw a simple data flow diagram — boxes for components, arrows for data flows
2. Mark trust boundaries (where untrusted input enters, where privilege changes)
3. Apply STRIDE to each trust boundary
4. For each identified threat, decide: accept / mitigate / transfer / eliminate
5. Document decisions — "We accepted this risk because X" is a valid outcome

---

## Pattern 2: Defense in Depth

**When**: Designing any security architecture. The single-control failure mode is the most common cause of breaches.

**The Pattern**:

```
Layer 1: Network
  WAF, DDoS protection, firewall rules, rate limiting

Layer 2: Transport
  TLS/HTTPS everywhere, HSTS headers, certificate validation

Layer 3: Application boundary
  Input validation, schema enforcement, output encoding

Layer 4: Authentication
  Strong auth, MFA, session management

Layer 5: Authorization
  Permission checks on every request, RBAC/ABAC, ownership verification

Layer 6: Data
  Encryption at rest, field-level encryption for PII, parameterized queries

Layer 7: Detection
  Audit logging, anomaly detection, alerting on security events
```

Each layer catches what others miss. Design so that the failure of any single layer does not cause a catastrophic breach — only a degradation.

**Common violation**: Relying on the firewall as the only protection. If the firewall is misconfigured or an insider threat exists, nothing else catches it.

---

## Pattern 3: Least Privilege

**When**: Designing permissions, roles, database access, service accounts, API scopes.

**The Pattern**:

Grant the minimum access required for a task, at the appropriate scope, for the minimum duration.

```
// BAD: One admin role for everything
user.role = 'admin'

// GOOD: Granular permissions scoped to need
user.permissions = ['orders:read', 'orders:create']

// Database: App user cannot DROP or GRANT
GRANT SELECT, INSERT, UPDATE ON app.* TO 'app_user';

// OAuth: Request only what's needed
scope: 'openid email'   // not scope: 'admin:all'

// Service accounts: one per service, no shared credentials
```

Practical questions to ask:
- Does this service/user need write access, or just read?
- Does this API key need all endpoints, or just one?
- Does the DB user need to drop tables?

---

## Pattern 4: Secure by Default

**When**: Designing APIs, configuration systems, middleware, or any system with defaults.

**The Pattern**:

Systems should be secure out of the box. Insecurity requires explicit opt-in.

```
// WRONG: Security is opt-in
app.get('/data', (req, res) => { ... })        // Open
app.get('/admin', requireAuth, (req, res) => { ... })  // Protected

// RIGHT: Security is the default
app.use(requireAuth)          // All routes protected
app.get('/public/*', allowPublic)  // Explicit exceptions

// Cookie defaults: always secure
res.cookie('session', token, {
  httpOnly: true,   // Default
  secure: true,     // Default in prod
  sameSite: 'lax'   // Default
})
```

Test the default: what happens when a developer adds a new route without thinking about security? The default should be safe.

---

## Pattern 5: Secrets Management

**When**: Handling API keys, passwords, tokens, encryption keys, OAuth secrets.

**The Pattern**:

```
DEVELOPMENT:   .env file (git-ignored), local secrets
STAGING/PROD:  Platform env vars or secrets manager
ENTERPRISE:    HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager

Hierarchy:
  Hardcoded (never) → .env file → Platform env → Secrets manager → HSM
```

Key requirements:
- Never commit secrets to git (use pre-commit hooks: gitleaks, git-secrets)
- Rotate secrets without requiring a deploy
- Audit who accessed what secret
- Different secrets per environment — prod secrets never on dev machines

**If a secret is leaked**: Rotate immediately. History cleanup is not sufficient. Assume the secret is compromised.

---

## Pattern 6: Security Logging

**When**: Building any system that handles authentication, authorization, or sensitive data.

**What to log** (always):
- Auth attempts: login success/failure, password changes, MFA events
- Auth decisions: permission grants and denials
- Admin operations: role changes, privilege escalation
- Security events: rate limit hits, validation failures, anomalous patterns

**What not to log**: passwords, tokens, API keys, raw session content, credit card numbers, SSNs.

**Log format**: structured JSON with timestamp, event type, user ID, IP, request ID. Never raw request bodies.

**Detection rules to consider**:
- 5+ failed logins in 10 minutes → lock account, alert
- Login from new geography after recent login → flag for MFA
- Bulk data access (10x normal) → alert for exfiltration risk

**Retention**: security logs 1 year minimum; audit logs 7 years for regulated industries.

---

## Pattern 7: Zero Trust Architecture

**When**: Designing internal service-to-service communication, remote access, or multi-tenant systems.

**The Pattern**:

"Never trust, always verify" — even for internal systems.

- Don't trust the internal network. Compromise travels laterally.
- Verify identity on every request, not just at the perimeter.
- Assume breach: design for detection and containment, not just prevention.
- Micro-segment: service A should not be able to reach service C if it doesn't need to.

**Practical minimum**:
```
Every request:
  1. Verify identity (JWT, mTLS, service account token)
  2. Verify specific permission for this action
  3. Log the decision

Don't: "It's an internal service, so trust it"
Do:    Verify even internal services have the right to perform the action
```
