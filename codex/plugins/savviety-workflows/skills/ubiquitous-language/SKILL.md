---
name: ubiquitous-language
description: "Build or refresh a domain glossary from interviews, specs, code, and docs. Flags ambiguous terms and writes UBIQUITOUS_LANGUAGE.md when asked."
---

# Ubiquitous Language

Use this for domain onboarding, DDD glossary work, or terminology cleanup.

## Workflow

1. Read supplied docs, code, tickets, or interview notes.
2. Extract domain terms, aliases, definitions, examples, and boundary context.
3. Flag overloaded or ambiguous terms.
4. Identify terms that appear in code with a different meaning than business usage.
5. Produce a glossary. Write `UBIQUITOUS_LANGUAGE.md` only when the user asks for file edits.

## Output

Group terms by bounded context when possible and mark confidence for inferred definitions.
