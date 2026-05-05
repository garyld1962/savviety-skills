# Lean Skill — Report Format

---

## Template

```
## Lean Audit — [skill-name] ([archetype])
[N files audited · N violations found: N auto-fixed, N suggested, N flagged]

---

### SKILL.md
- ✅ Silent execution directives present
- ✅ Scope limits defined
- ⚠️ [Auto] HEAD~1 replaced with git merge-base
- ⚠️ [Flag] Missing dispatcher contract — add "When Dispatched as Sub-Agent" table

### references/checks.md
- ✅ All commands capped with | head -N
- ✅ No duplicate extraction commands
- ⚠️ [Auto] 3 restating comments removed from bash blocks
- ⚠️ [Suggest] 2 sequential grep calls combined into one

### references/report.md
- ✅ No preamble
- ✅ Evidence truncation rule present
- ⚠️ [Auto] 2 template placeholder lines removed
- ⚠️ [Flag] Missing collapse rule for passed checks

### references/sharp-edges.md
- ✅ All edges have severity labels
- ⚠️ [Suggest] "If you see X, do Y" closer on edge 3 removed
- ⚠️ [Suggest] Dangling **Remember** callout on edge 5 folded into code block

### references/criteria.md
- ⚠️ [Flag] Tier mismatch: "sequential await" is Blocking in criteria.md but in Tier 2 — move to Tier 1
- ⚠️ [Flag] No false positive exemptions for Tier 2 checks

---

[All N remaining file checks passed.]
```

---

## Formatting Rules

**Header line**: `[skill-name]` from the `id:` field in SKILL.md frontmatter. `[archetype]` from detection in Step 2.

**Summary line**: counts of violations by action category. Auto-fixed = edits already applied. Suggested = shown for review. Flagged = reported but not acted on.

**Per-file sections**: only include files that exist. If a file has no violations, include one line: `✅ [filename] — clean`.

**Violation format**:
- Prefix with category tag: `[Auto]`, `[Suggest]`, `[Flag]`
- State what was found and what was done (or what needs to be done)
- One line per violation where possible

**Collapse clean files**: if more than 4 files are completely clean, collapse to: `All N remaining files clean.`

**Missing files**: list at the end, separately:
```
### Missing Files
- references/criteria.md — required for Review Sub-agent (Flag: needs disposition content)
```

**No preamble**: report starts with `## Lean Audit —`. Not "I've completed the lean audit of..." or "Here is a summary of findings...".

**Suggestion display**: when a Suggest fix is applied, show old → new inline in the report only if the change is under 3 lines. For longer changes, describe the transformation ("bullet list condensed to inline form").

---

## After Report

If any `[Flag]` items require new content (missing criteria.md, missing dispatcher contract): list them as a numbered action list at the end of the report.

```
### Action Required
1. Add dispatcher contract to SKILL.md (see references/archetypes.md for template)
2. Move "sequential await" check from Tier 2 to Tier 1 in checks.md
3. Add false positive exemptions to criteria.md Tier 2 section
```

If all violations were Auto-fixed or all Suggested fixes accepted: `No action required — skill is lean.`
