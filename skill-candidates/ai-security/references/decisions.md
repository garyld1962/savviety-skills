# AI Security — Decisions

## When to Use LLM Output for Security-Sensitive Operations

| Operation | Use LLM output directly? | Safe approach |
|-----------|--------------------------|---------------|
| Authorization decision ("is user allowed?") | Never | Use deterministic auth logic; LLM advises, code decides |
| Input classification ("is this safe?") | Never as sole gate | Use as one signal; combine with pattern matching and behavioral rules |
| Data extraction (parse structured data) | With schema validation | Validate output against Zod/JSON Schema before use |
| Content generation (text, summaries) | Yes, with output sanitization | Sanitize for XSS, redact PII before storing/rendering |
| Code generation | Yes, with sandbox + static analysis | Never execute LLM-generated code without scanning and sandboxing |
| SQL/query generation | Avoid if possible | If used: parse and validate query structure; never use string interpolation |

**Rule**: LLM output is a suggestion. Any security-relevant decision must be made by deterministic code that does not trust the model's text output. "The LLM said the user is authorized" is not authorization.

---

## System Prompt Confidentiality

**System prompts are not secrets.** Treat them as obfuscated, not secret. A determined user can extract a system prompt through instruction-override attacks, model verbosity, or jailbreaks. Design accordingly.

| Assumption | Reality |
|------------|---------|
| "Users can't see my system prompt" | Can be extracted via injection in most models |
| "My prompt is too complex to extract" | Multi-turn attacks work on long prompts too |
| "Instruction hierarchy prevents leakage" | Reduces risk; does not eliminate it |

**Implications**:
- Never put secrets (API keys, passwords) in the system prompt
- Never put information in the system prompt that you'd be embarrassed to see leaked (internal business rules, unannounced product plans)
- Design your application so a fully leaked system prompt does not create a security vulnerability — the security controls must be in code, not prompts

---

## Tool / Function Calling Permission Model

```
Question: What should my LLM agent be able to do?
Answer: Only what it absolutely needs for the specific task.
```

| Tool Category | Permission Gate | Reversible? | Recommendation |
|---------------|----------------|------------|----------------|
| Read-only queries (search, lookup) | Automatic | Yes | Allow freely with input validation |
| Write operations (create, update) | Validate intent + log | Yes (with effort) | Allow with audit trail and schema validation |
| Destructive operations (delete, archive) | Human confirmation | No | Require explicit user approval per action |
| External network calls | Allowlist only | Depends | Only to pre-approved domains |
| Code execution | Sandbox + human review | No | Avoid in production; require code review if used |
| Financial operations | Human confirmation + 2FA | No | Never automate without human-in-the-loop |

**Key principle**: if a prompt injection attack compromises your LLM, the attacker gains exactly the permissions you granted the model. Minimize tool access to minimize blast radius.

---

## Model Choice and Trust Level

| Deployment model | Audit capability | Data leaves your infra? | Recommended for |
|-----------------|-----------------|------------------------|----------------|
| Hosted API (Anthropic, OpenAI) | Provider logs; your logs | Yes | Most applications |
| Hosted API with zero data retention | Provider policy; your logs | Depends on provider | PII-sensitive apps |
| Self-hosted open model (vLLM, Ollama) | Full control | No | Regulated industries, highest sensitivity |
| Fine-tuned model (third-party) | Limited | Depends | Only with supply chain verification |

**Self-hosted does not mean more secure by default**. A self-hosted model with fewer safety guardrails is often easier to inject than a hosted model with constitutional AI training. Choose based on data residency requirements, not security theater.

For fine-tuned or third-party models: verify the model hash against a known-good manifest before deployment. An unverified model is an unverified binary running in your infrastructure.

---

## When Compliance Is Not Enough

Standard frameworks (SOC2, ISO 27001, NIST AI RMF) have weak or no LLM-specific controls. Verified compliant systems can still be:

- Trivially prompt-injected (no control maps to injection defense)
- System-prompt-extractable (confidentiality controls don't cover prompt leakage)
- Vulnerable to indirect injection via RAG (data integrity controls don't cover this)
- Missing rate limits on LLM endpoints (availability controls focus on infrastructure, not AI cost)

**Minimum additional controls for any LLM application** regardless of compliance framework:
1. Input validation with multi-layer injection detection
2. Output sanitization before rendering or storage
3. Rate limiting on LLM endpoints (both request rate and token budget)
4. Audit logging (hashed inputs/outputs, tools called, user ID)
5. Least-privilege tool access with server-side validation
6. Human-in-the-loop for irreversible agent actions
