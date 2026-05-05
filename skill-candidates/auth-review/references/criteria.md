# Auth Review — Criteria

---

## Disposition Table

| Tier | Disposition | Label | Definition |
|------|-------------|-------|------------|
| 1 | Blocking | Blocking | Correctness bug or security vulnerability that directly enables account takeover, data theft, or auth bypass. Do not merge. |
| 2 | Non-blocking | Non-blocking | Auth implementation quality issue. Should fix; risk is real but not immediately catastrophic. |
| 3 | Discussion | Discussion | Missing defense layer or UX/policy tradeoff. Author may have good reasons. |
| — | Praise | Praise | Correct, non-obvious auth pattern. Note sparingly. |

---

## Tier 1 — Blocking Findings

| Check | Why Blocking |
|-------|-------------|
| JWT in localStorage | XSS steals tokens; all accounts compromised by one XSS |
| Token in URL param | Tokens logged by every proxy, CDN, and browser history |
| Plaintext password storage/comparison | Database breach = all passwords immediately usable |
| Weak hash for passwords (MD5/SHA1/SHA256) | GPU cracks billions/sec; DB breach = instant account compromise |
| jwt.decode() used for auth | Signature not verified; any payload can be forged |
| JWT verify without explicit algorithm | alg:none attack bypasses signature on vulnerable libraries |
| Hardcoded JWT secret | Anyone with repo access forges tokens for any user |
| OAuth state parameter missing | Login CSRF: attacker links their OAuth account to victim's session |
| IDOR — ID from params without ownership check | Any authenticated user accesses any other user's data |
| Missing auth middleware on sensitive routes | Unauthenticated access to protected operations |

---

## Tier 2 — Non-Blocking Findings

| Check | Why Flag |
|-------|----------|
| Session cookie missing httpOnly/Secure/SameSite | Session theft via XSS or network; severity depends on app sensitivity |
| JWT access token expiry too long (>1h) | Stolen tokens remain valid for extended window |
| Refresh token not rotated on use | Stolen refresh token grants indefinite access |
| Session not regenerated after login | Session fixation attack possible |
| bcrypt cost factor < 12 | Faster brute force on leaked DB; balance with login latency |
| Specific auth error messages | User enumeration enables targeted credential stuffing |
| Timing-unsafe comparison | Timing oracle for token/secret brute-force |

---

## Tier 3 — Discussion Points

| Check | Discussion Point |
|-------|-----------------|
| No MFA on high-risk operations | Credential theft = full account access without second factor |
| Overly broad OAuth scopes | Principle of least privilege; request only what's needed |
| No account lockout on failed attempts | Rate limiting alone doesn't prevent slow brute force over time |

---

## Scope Rules

- **Diff-only**: Only flag issues introduced in the PR diff.
- **Test files**: Apply Tier 1 checks. Plaintext passwords and hardcoded secrets in test fixtures are still in git history.
- **Generated / build files**: Skip entirely.
- **False positive guidance**:
  - `jwt.decode()` is acceptable when used only to read non-security payload fields (e.g., logging, display) after a separate `jwt.verify()` call is visible. Do not flag in that case.
  - Refresh token rotation absence: skip if the file is clearly a token generation utility and rotation is handled elsewhere (check imports/calls).
  - `===` comparison: only flag for secrets/tokens, not general string equality.

---

## Severity Escalation

If a PR touches auth code and has 2+ Tier 1 findings, prepend:

> **Auth Security Review Required** — multiple critical auth bugs found. Recommend a dedicated auth security review before merge.
