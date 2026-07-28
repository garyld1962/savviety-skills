# Security Advisor — Decisions

Security architecture decisions with concrete frameworks for choosing.

---

## Decision 1: Authentication Mechanism

**When**: Choosing how users prove their identity.

| Method | Security | UX | Best For |
|--------|----------|-----|---------|
| Password only | Low | Simple | Low-risk internal tools |
| Password + TOTP MFA | High | Moderate | Most applications |
| Passwordless (magic link, passkey) | High | Good | Consumer apps |
| SSO / OAuth (Okta, Azure AD) | High | Seamless | Enterprise / B2B |

**Framework**:
1. What is the risk level of the data and actions? (financial, health, PII = higher bar)
2. What is the user's technical sophistication? (consumer = lower friction tolerance)
3. Are there compliance requirements? (PCI, HIPAA, SOC 2 have specific requirements)
4. Do users belong to organizations with existing identity providers?

**Recommendation**: Password + TOTP for most apps. Passkeys/WebAuthn for consumer apps building for the future. SSO if the users are enterprise and have IdPs. SMS as a fallback only — vulnerable to SIM swapping and SS7 attacks.

**Password policy**: 12+ characters minimum, breach-list checking (HIBP), allow paste, allow long passwords (password manager friendly). Drop complex character rules — they create predictable patterns.

---

## Decision 2: Session Management — JWT vs. Server Sessions vs. Hybrid

**When**: Deciding how to maintain authenticated state.

| Strategy | Statefulness | Scalability | Revocation | Best For |
|----------|-------------|-------------|------------|---------|
| Server sessions (Redis-backed) | Stateful | Moderate | Immediate | Traditional web apps |
| JWT (stateless) | Stateless | High | Hard | Microservices |
| Hybrid: short JWT + server refresh | Mixed | High | Via refresh token | Most modern apps |

**Framework**:

- **Can you afford a session store?** If yes, server sessions are simpler and offer immediate revocation.
- **Do you need to scale horizontally without shared state?** JWT is a good fit.
- **Do you need to revoke a specific session** (compromise detected, password change)? Pure JWT makes this hard — use hybrid.

**Hybrid (recommended)**:
- Access token: 15-minute JWT, stateless, fast
- Refresh token: 7-day server-stored hash, rotated on each use
- Revoke by deleting the refresh token from the store

**Token storage**:
- Access token: in-memory (JS variable), never localStorage
- Refresh token: httpOnly cookie with `Secure`, `SameSite=Lax`, path `/auth/refresh`
- Mobile: platform secure storage (Keychain, Keystore)

---

## Decision 3: Authorization Model

**When**: Designing who can access what.

| Model | Complexity | Granularity | Best For |
|-------|-----------|-------------|---------|
| RBAC (Role-Based) | Low | Role-level | Most applications |
| ABAC (Attribute-Based) | High | Context-aware | Complex compliance rules |
| ReBAC (Relationship-Based) | Medium | Graph-based | Collaborative / social apps |

**Framework**:
- Start with RBAC + ownership checks. This covers 90% of cases.
- Add ABAC when you need rules like "only during business hours" or "only from approved devices."
- Use ReBAC when access depends on relationships: "member of team that owns document."

**Non-negotiable**: ownership check on every resource-level operation. RBAC tells you what a user can do in general; ownership tells you whether they can do it to this specific resource.

---

## Decision 4: Encryption — At Rest vs. In Transit vs. Field-Level

**When**: Deciding what to encrypt and how.

| Level | What It Covers | When Required |
|-------|---------------|---------------|
| Transport (TLS) | Data in transit | Always — non-negotiable |
| Database at rest | Stored data | Strong default; required for PII regulations |
| Field-level encryption | Specific sensitive fields | PII, payment data, health data |
| End-to-end | Entire path, server can't read | Messaging apps, high-sensitivity docs |

**Framework**:
- TLS everywhere is non-negotiable. TLS 1.2 minimum; TLS 1.3 preferred.
- Database-level encryption (transparent) protects against physical disk theft — low cost, high value.
- Field-level encryption protects against DB breach and insider threat — higher cost, needed for PII.
- End-to-end is architecturally complex — only where the threat model requires it.

**Passwords**: always hashed (bcrypt/Argon2id), never encrypted. Encryption is reversible; hashing is not. If you can recover a password, you've done it wrong.

**Algorithm selection**:
- Symmetric encryption: AES-256-GCM
- Asymmetric: RSA-2048+, or Ed25519/X25519
- Hashing (non-password): SHA-256 or SHA-3
- Password hashing: Argon2id (preferred) or bcrypt with cost factor 12+

**Key management**: environment variables for dev; dedicated KMS (AWS KMS, GCP Cloud KMS, Azure Key Vault, HashiCorp Vault) for production. Rotate keys annually at minimum; automate rotation where possible.

---

## Decision 5: When to Bring in a Security Specialist

**When**: Deciding whether an issue exceeds internal capacity.

Bring in an external specialist when:
- **Building security-critical infrastructure**: custom auth systems, cryptographic protocols, PKI
- **Processing regulated data**: PCI DSS (card data), HIPAA (health data), preparing for SOC 2 audit
- **After a breach or suspected compromise**: incident response requires forensics expertise
- **Before major launch**: penetration test by external firm finds issues the team is too close to see
- **Expanding attack surface significantly**: new public API, new third-party integrations, new geography

Internal team handles:
- OWASP Top 10 prevention (documented, teachable)
- Dependency vulnerability management (automated tooling)
- Security reviews of standard application code
- Security monitoring and alerting setup

**What to look for in a specialist**: they should find real issues (zero findings = inadequate scope or time), provide clear reproduction steps, explain business impact, and give actionable remediation.

---

## Decision 6: Vulnerability Severity and Response Time

**When**: Triaging a discovered vulnerability or CVE.

| Severity | CVSS | Response | Examples |
|----------|------|----------|---------|
| Critical | 9.0–10.0 | Fix within 24 hours | RCE, auth bypass, data breach risk |
| High | 7.0–8.9 | Fix within 7 days | Privilege escalation, sensitive data exposure |
| Medium | 4.0–6.9 | Fix within 30 days | Limited impact, requires conditions |
| Low | 0.1–3.9 | Fix within 90 days | Info disclosure, hard to exploit |

If you can't meet the timeline: document the reason, implement mitigations (WAF rule, disable feature), get approval from the appropriate authority, set a new deadline.

Track mean time to remediate. Aging vulnerabilities and recurrence rate are the key metrics.

---

## Decision 7: How to Communicate Security Risk to Stakeholders

**When**: Explaining a security finding to non-technical leadership, product managers, or clients.

**Framework — translate to business terms**:
1. **What could happen**: "An attacker could read any user's private messages" — not "IDOR vulnerability present"
2. **Likelihood**: "This is trivially exploitable by anyone with a free account" — not "CVSS 8.5"
3. **Impact**: "This would expose ~50,000 user records and trigger GDPR breach notification" — not "data leakage"
4. **Cost of fix vs. cost of incident**: "2 days of engineering vs. $2M in regulatory fines and reputational damage"
5. **Urgency**: "Attackers actively look for this pattern; we have days, not weeks"

**What to avoid**: technical jargon without translation, severity scores without context, framing security as compliance (it's risk management). Never present security purely as a blocker — present it as risk the business is choosing to accept or mitigate.
