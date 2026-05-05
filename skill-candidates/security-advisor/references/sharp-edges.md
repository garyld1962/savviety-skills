# Security Advisor — Sharp Edges

Critical security thinking mistakes and architectural traps.

---

## Security Theater (Compliance ≠ Security)

**Severity**: High
**Situation**: Team believes passing a SOC 2 audit, completing GDPR questionnaires, or having a documented security policy means the system is secure.

Compliance is a point-in-time snapshot of whether you meet a minimum bar. It tells you what you had when the auditor visited, not whether you're secure now. A documented password policy that nobody enforces, annual security training that nobody applies, and encryption "mentioned in the policy" that uses MD5 — all pass audits. None protect users.

```
Compliant but not secure:
  Password policy: documented ✓
  Actual passwords: "Password123!" ✓
  Audit result: PASS

Secure but not compliant:
  Password enforcement: strict ✓
  Documentation: missing ✗
  Audit result: FAIL (fix the docs)

Goal:
  Both — but build the security first.
  Compliance is evidence of security, not a substitute.
```

**Fix**: Use compliance frameworks as a checklist for security work, not as a destination. Continuously validate — automated scanning daily, not just at audit time. Policies must be technically enforced, not just documented.

---

## Security by Obscurity

**Severity**: High
**Situation**: Relying on hidden admin URLs, obfuscated endpoints, non-standard ports, or undocumented APIs as a security control.

Attackers scan everything. Automated tools find hidden paths in seconds. Frontend JavaScript bundles reveal API endpoints. Decompilation reveals custom algorithms. Obscurity buys you minutes, not security. When it's discovered (and it will be), there is no protection underneath.

```
What attackers do in minutes:
  Directory brute force: ffuf -w wordlist.txt -u https://target.com/FUZZ
  Port scanning: nmap -p- target.com
  Bundle analysis: grep -r "api/" bundle.js
```

**Fix**: Obscurity is acceptable as a bonus layer (harder to find = slightly less attacked) but not as a foundation. Every endpoint must require authentication and authorization regardless of how discoverable it is. Assume attackers have your source code.

---

## Premature Security Hardening

**Severity**: Medium
**Situation**: Spending significant engineering effort on security measures for threats that don't match your actual risk profile.

A solo developer's side project does not need HSM key storage, mutual TLS between services, and a custom SIEM. A healthcare startup processing PHI absolutely does. Security investment should be proportional to risk: threat likelihood × data sensitivity × regulatory exposure.

```
Common premature hardening traps:
  - Building custom crypto instead of using bcrypt
  - Complex RBAC for an app with two roles
  - Air-gapping a system whose main threat is SQL injection
  - Security review process so heavy it blocks all shipping

What to do instead:
  1. Identify your actual threats (use STRIDE)
  2. Fix the OWASP Top 10 first — these are cheap and cover most real attacks
  3. Add layers proportional to sensitivity
  4. Don't optimize for attacks that require nation-state resources if you're a startup
```

**Fix**: Apply the Pareto principle. OWASP Top 10 prevention, secure defaults, dependency patching, and good secrets management cover 80% of real-world risk for most applications. Get those right before building an elaborate custom security system.

---

## Neglecting the Human Layer

**Severity**: High
**Situation**: Building technically excellent security controls while ignoring that users, developers, and administrators are the most exploited attack surface.

The most sophisticated SQL injection prevention means nothing if a developer commits a database credential to GitHub. MFA protects accounts until an administrator gets phished and approves a fake login request. Defense in depth covers systems but systems are operated by people.

```
Human-layer attack vectors:
  - Developers committing secrets (most common breach vector)
  - Phishing: users or admins clicking credential-stealing links
  - MFA fatigue: push-notification bombing until user approves
  - Social engineering: "Hi, I'm IT support, I need your password"
  - Insider threat: legitimate access used maliciously

Technical controls that help:
  - Pre-commit hooks blocking secret commits (gitleaks)
  - Phishing-resistant MFA (FIDO2/passkeys — not SMS, not push)
  - Short MFA approval windows and rate limiting push attempts
  - Least privilege (limits damage from insider threat)
  - Audit logs (detects and attributes insider activity)
```

**Fix**: Security training is not enough on its own. Make the secure path the easy path. Pre-commit hooks catch secrets before developers make mistakes. FIDO2/passkeys are phishing-resistant by design, not by training. Assume some percentage of your developers will be phished — design controls that limit the blast radius.

---

## The One-Time Security Fix

**Severity**: Medium
**Situation**: Treating security as a project with a completion state: "We did a security audit last year and fixed everything."

New code introduces new vulnerabilities. Dependencies gain new CVEs daily. Attack techniques evolve. A system that was secure 18 months ago may have a critical dependency vulnerability today. Security is a process, not a state.

```
What changes constantly:
  - Codebase: new features, new attack surface
  - Dependencies: new CVEs, abandoned libraries
  - Team: knowledge loss as people leave
  - Attack techniques: new exploits for old patterns
  - Infrastructure: new services, new configs
```

**Fix**: Automate the repeatable parts. Dependency scanning runs daily (Dependabot, Snyk). SAST runs on every PR. Secret scanning runs pre-commit. Penetration tests happen annually — not as a replacement for continuous automated scanning, but as a different category of validation that finds what automation misses.

---

## The False MFA Sense of Security

**Severity**: Medium
**Situation**: Implementing MFA and considering account security solved, especially when the second factor is SMS.

Not all MFA is equal. SMS is vulnerable to SIM swapping (attacker convinces carrier to transfer victim's number) and SS7 protocol attacks. Email-as-second-factor is not MFA — it's the same factor (knowledge) as a password. "Remember this device for 30 days" means 30 days of effective single-factor. Optional MFA means most users won't enable it.

```
MFA strength ladder (weakest to strongest):
  Email codes       — same channel as password reset, not meaningfully "second factor"
  SMS codes         — SIM swap, SS7 interception
  Push notifications — MFA fatigue attacks (user approves to stop the spam)
  TOTP apps         — good; phishable (user types code into fake site)
  FIDO2/Passkeys    — phishing-resistant; strongest practical option

Deployment traps:
  - Optional MFA: most users won't enable it for accounts they consider low-value
  - "Remember for 30 days": nearly defeats the purpose
  - SMS-only MFA: security theater for high-value accounts
```

**Fix**: Use TOTP as the minimum standard for anything beyond low-risk apps. Offer FIDO2/passkeys for high-security users. Make MFA mandatory for admin accounts — no exceptions. Keep "remember device" periods short (7 days max). For consumer apps, consider passkeys as a replacement for passwords, not just an add-on.
