# Security Review — Criteria

---

## Disposition Table

| Tier | Disposition | Label | Definition |
|------|-------------|-------|------------|
| 1 | Blocking | Blocking | Correctness bug, security vulnerability, will cause a breach or production failure. Do not merge. |
| 2 | Non-blocking | Non-blocking | Security quality issue, should fix but doesn't stop merge if risk is understood. |
| 3 | Discussion | Discussion | Tradeoff or missing defense-in-depth. Author may have good reasons; warrants conversation. |
| — | Praise | Praise | Genuinely good security decision. Note sparingly. |

---

## Tier 1 — Blocking Findings

These are automatic flags. No false positive exemption unless the surrounding code clearly negates the risk.

| Check | Why Blocking |
|-------|-------------|
| Hardcoded secret / credential | Immediately exploitable; git history is permanent |
| SQL injection via string interpolation | Full database compromise possible |
| Shell command injection | Remote code execution |
| innerHTML / v-html with non-static input | XSS — session theft, account takeover |
| HTTP (non-HTTPS) external URL | Credentials and data transmitted in plaintext |
| Unvalidated redirect | Open redirect enables OAuth token theft and phishing |
| Path traversal | Arbitrary server file access |
| JWT none algorithm accepted | Complete auth bypass with zero crypto knowledge |
| Dynamic code execution | Arbitrary code execution from user input |
| Missing auth on sensitive routes | Unauthenticated access to protected resources |

---

## Tier 2 — Non-Blocking Findings

Flag these; they should be fixed before or soon after merge. Leave the merge decision to the author/reviewer.

| Check | Why Flag |
|-------|----------|
| Insecure cookie (missing httpOnly, Secure, SameSite) | Cookie theft via XSS or network interception |
| Verbose errors leaking stack traces | Reveals schema, paths, and framework version to attackers |
| Weak hash for passwords (MD5, SHA1, SHA256) | Brute-force in seconds on leaked DB |
| CORS wildcard (origin: '*') | Any site can make credentialed requests |
| Mass assignment (...req.body in DB op) | Attackers can set isAdmin: true, bypass email verification, etc. |
| Timing-unsafe secret comparison (===) | Timing oracle reveals valid tokens byte by byte |
| IDOR — resource fetch without ownership check | Any authenticated user can access any user's data |

---

## Tier 3 — Discussion Points

Note these; they are architecture or defense-in-depth concerns. The author may have valid reasons.

| Check | Discussion Point |
|-------|-----------------|
| Missing rate limiting on auth endpoints | Enables credential stuffing and brute force at scale |
| Logging sensitive fields | Logs are often less controlled than DB; indefinite retention |
| Missing CSP headers | CSP is defense-in-depth against XSS; missing it raises the blast radius |

---

## Scope Rules

- **Diff-only**: Only flag issues introduced in the PR diff. Pre-existing issues in untouched code are not in scope.
- **Test files**: Apply Tier 1 checks (especially hardcoded secrets). Skip Tier 2 and Tier 3. Hardcoded credentials in test files still end up in git history.
- **Generated / build files**: Skip entirely (dist/, build/, .next/, *.generated.*).
- **Config files** (package.json, next.config.*, server middleware): Apply Tier 1 + Tier 3 header checks.
- **False positive exception**: If innerHTML is clearly assigning a static string literal (not user input, not a variable), do not flag. Document the skip.

---

## Severity Escalation

If a single PR contains more than 3 Tier 1 findings, prepend the report header with:

> **Security Audit Required** — multiple critical findings suggest a systematic issue. Recommend a focused security review of the broader codebase before merge.
