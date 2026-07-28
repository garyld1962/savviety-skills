---
name: security-quick-check
description: "Reusable 7-point security review for diffs. Embedded by ship fast mode, ship PR mode, checkpoint, and code-review when a fast security pass is warranted. Not user-invokable."
user-invocable: false
internal: true
---

# Security Quick Check

A focused, low-cost security pass over the current diff. Designed to catch the OWASP-flavored mistakes that a hurried implementer most commonly introduces. **Not** a substitute for full threat modeling or a security review on architecturally significant changes.

## When to Use

Embed this rubric in any workflow that ships code without going through full `code-review`:

- `ship --fast` — mandatory; the one review step you never skip on an expedited fix.
- `ship` PR and release modes — recommended on diffs that touch auth, input handling, rendering, or persistence.
- `checkpoint` — optional gate before opening a PR.

Skip when the diff is purely cosmetic (formatting, comments, docs, type-only changes with no runtime behavior).

## The 7 Points

For the current diff, verify each:

1. **No new secrets or credentials committed.**
   - No API keys, tokens, passwords, connection strings, or private keys in source, configs, or fixtures.
   - No `.env`, `.pem`, `.key`, or credential JSON files added.
   - Check both added lines and any new files.

2. **No injection vulnerabilities introduced.**
   - SQL: no string concatenation or interpolation building queries — parameterized queries only.
   - Shell: no unescaped user input passed to `exec`, `system`, `child_process.exec`, `os.system`, etc.
   - LDAP, NoSQL, XPath, command injection: same rule.

3. **No auth or authorization bypasses.**
   - New routes, handlers, or RPC methods enforce authentication where peers do.
   - Authorization checks (role, ownership, tenant) preserved on modified handlers.
   - No `// TODO: add auth` left in production paths.

4. **Input validation remains intact.**
   - Removed validation must be replaced, not silently dropped.
   - New inputs validated at the trust boundary (size, type, range, allowed values).
   - Trust-boundary fields (IDs, paths, URLs, redirects) cannot be attacker-controlled without checks.

5. **No unsafe dynamic code execution.**
   - No new `eval`, `Function(...)`, `exec`, `vm.runInThisContext`, or equivalent.
   - No dynamic `require`/`import` of attacker-controllable paths.
   - No deserialization of untrusted data with formats that allow code execution (pickle, Java serialization, YAML `!!python/object`).

6. **No unescaped user content rendered as HTML.**
   - Templating uses auto-escaping; raw/`unsafe`/`{{{...}}}` blocks are explicitly safe.
   - No `innerHTML = userInput` or React `dangerouslySetInnerHTML` with non-sanitized data.
   - URLs in `href`/`src` validated against `javascript:` and `data:` schemes where relevant.

7. **No raw SQL string interpolation.**
   - Even when input "looks safe," all SQL goes through parameterized queries or a query builder.
   - Dynamic identifiers (table/column names) come from an allow-list, never user input.

## Output Format

When invoked, produce one of:

- **PASS:** "Security quick check: 7/7 clear." — no findings, proceed.
- **FAIL:** Bulleted list of findings with file/line and which point failed:

  ```
  Security quick check: 2 findings.
  - [#2 injection] src/api/users.ts:48 — query built via template string with `name` from req body
  - [#6 unescaped HTML] src/views/profile.tsx:22 — dangerouslySetInnerHTML on `bio` without sanitizer
  ```

Findings block the calling workflow until resolved. The user may override (`--security-override <reason>`) only on hotfix when explicitly justified.

## Rules

- **Diff-scoped, not codebase-scoped.** Only review what changed. A pre-existing issue in untouched code is out of scope here — surface it as a separate note.
- **No false-positive theater.** If a flagged pattern is provably safe in context (constant input, internal-only path, escaped by a verified helper), say so and pass. Do not pad findings.
- **One screen.** Default output fits on a screen. Cite the rule number so the caller can trace.
- **Not a replacement for full review.** This is the fast path. Architecturally significant changes still need `code-review` or `code-review-professional`.
