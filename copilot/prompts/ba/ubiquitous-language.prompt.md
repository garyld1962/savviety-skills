---
description: >-
  Extract a DDD-style ubiquitous language glossary from conversation and
  codebase — a semantic concern focused on precise, unambiguous domain
  vocabulary. Flags ambiguities, proposes canonical terms.
argument-hint: '[--scan] [--update]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
  - edit
---

# Ubiquitous Language

Extract domain terminology from the current conversation into a consistent glossary saved to `UBIQUITOUS_LANGUAGE.md`.

## Steps

1. **Gather** — scan conversation for domain nouns, verbs, concepts. If `--scan`, also search codebase for types, enums, table names.
2. **Classify** — identify ambiguities (same word, different meanings), synonyms (different words, same concept), vague terms.
3. **Propose** — pick canonical terms (be opinionated), write one-sentence definitions, list aliases to avoid, group by domain cluster.
4. **Relate** — map relationships with cardinality using bold term names.
5. **Dialogue** — write 3-5 dev/domain-expert exchanges showing precise term usage.
6. **Flag** — list unresolved ambiguities with recommendations.
7. **Save** — write `UBIQUITOUS_LANGUAGE.md`. If `--update`, read existing file first and merge.

## Rules

- Domain terms only — skip programming concepts
- One sentence per definition — what it IS, not what it does
- Be opinionated — pick the best word
- Flag conflicts explicitly
