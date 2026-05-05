# Lean Skill — Checks

Organized by target file. Run all checks for a file in one pass after reading it.

Fix categories: **Auto** (apply immediately) | **Suggest** (show condensed version, apply if unambiguous) | **Flag** (report gap, do not create content)

---

## SKILL.md

### [Auto] Missing Silent Execution Directives

```bash
grep -c "Accumulate findings\|Do not emit\|Bail on empty\|no findings.*passed" SKILL.md
```

If count < 2 AND archetype is not Advisory: insert the three silent execution directives before the Token Economy section (or create one).

Directives to insert (see `directives.md` for exact wording):
- Do not emit text between tool calls
- Accumulate findings; report is the only output
- Bail on empty results — record as passed, move on

### [Flag] Missing Dispatcher Contract

```bash
grep -c "Dispatched as Sub-Agent\|base_ref\|merge-base" SKILL.md
```

If count = 0 AND archetype is Review Sub-agent: flag. Do not create — requires knowledge of the dispatch context.

### [Auto] HEAD~1 Instead of merge-base

```bash
grep -n "HEAD~1\|HEAD\^" SKILL.md
```

Replace `HEAD~1` with `$(git merge-base HEAD main 2>/dev/null || echo "HEAD~1")`.

### [Suggest] Persona Exceeds 5 Sentences

```bash
grep -c "\." SKILL.md | head -1
```

Count sentences in the identity/persona block. If >5: flag the excess; suggest trimming to contrarian insight + core principles only.

### [Flag] Missing Scope Limits

```bash
grep -c "Does not cover\|Does not own\|does not handle\|not cover" SKILL.md
```

If count = 0: flag. Advisory skills without scope limits cause invocation in situations they can't handle.

---

## references/checks.md

### [Auto] Unbounded Commands

```bash
grep -n "grep\|git log\|git diff\|find\|cat\|ls" references/checks.md \
  | grep -v "head -\|wc -l\|^\s*#" | head -20
```

For each match without `| head -N`: append `| head -10` (or appropriate N for the context).

### [Auto] Restating Comments in Bash Blocks

```bash
grep -B1 "grep\|git\|find\|cat" references/checks.md \
  | grep "^#" | grep -v "###\|!#" | head -10
```

Comments directly above commands that restate the section heading → remove.

### [Flag] Duplicate Extraction Command

```bash
grep -c "grep.*\^+\|merge-base\|git diff.*\^+" references/checks.md
```

If extraction command appears in both SKILL.md and checks.md: flag the duplicate in checks.md for removal.

### [Flag] Missing Tier Structure

```bash
grep -c "Tier 1\|Tier 2\|Tier 3\|Auto-Flag\|Judgment" references/checks.md
```

If count = 0 AND archetype is Review Sub-agent: flag. Checks without tiers have no confidence model — false positive rate will be high.

---

## references/report.md

### [Auto] Preamble Present

```bash
grep -in "i've completed\|here are\|after reviewing\|i have analyzed" references/report.md | head -5
```

Remove matching lines.

### [Auto] Command Echo Present

```bash
grep -n "Running:\|Executing:\|Command:" references/report.md | head -5
```

Remove matching lines from templates.

### [Flag] Missing Evidence Truncation Rule

```bash
grep -c "showing 3\|max 3\|3 lines" references/report.md
```

If count = 0: flag. Without a truncation rule, large findings flood the report.

### [Flag] Missing Collapse Rule

```bash
grep -c "remaining checks passed\|collapse\|All N" references/report.md
```

If count = 0: flag. Without a collapse rule, 20 passing checks each get a line.

### [Auto] Template Placeholder Lines

```bash
grep -n "\[repeat\|\[add more\|\[paste\|\[insert" references/report.md | head -5
```

Remove matching lines.

### [Suggest] Verbose Discussion Template

```bash
grep -A3 "Discussion\|Tradeoff" references/report.md | head -20
```

If Discussion template block exceeds 2 lines: suggest condensing to "**Tradeoff**: X vs Y. Worth it?"

---

## references/sharp-edges.md (Advisory)

### [Flag] Missing Severity Labels

```bash
grep -c "\*\*Severity\*\*" references/sharp-edges.md
grep -c "^## " references/sharp-edges.md
```

If severity count < heading count: flag edges missing severity labels.

### [Suggest] Edges Exceeding Format

```bash
grep -c "^## " references/sharp-edges.md
wc -l < references/sharp-edges.md
```

If average lines per edge > 20: flag for review. Sharp edges should be scannable warning cards, not essays. Suggest applying the format from `directives.md`.

### [Auto] Dangling Callout Lines

```bash
grep -n "^\*\*Remember\*\*:\|^\*\*Note\*\*:\|^\*\*Important\*\*:" references/sharp-edges.md | head -10
```

For each match: check if it restates the preceding code block. If so, fold the content into the block as a comment and remove the standalone line.

---

## references/patterns.md / decisions.md (Advisory)

### [Suggest] Short Bullet Lists (3+ items, all <6 words each)

```bash
grep -A4 "^- " references/patterns.md references/decisions.md 2>/dev/null \
  | grep -c "^- " | head -1
```

If 3+ consecutive bullets all under 6 words: suggest converting to inline `A, B, or C — pick one.`

### [Suggest] "If you see X, do Y" Closing Sentences

```bash
grep -n "^If you see\|^When you see\|^When this happens" references/patterns.md references/decisions.md 2>/dev/null | head -10
```

These restate the warning signs list above them. Suggest removing.

---

## references/criteria.md

### [Flag] Tier/Disposition Mismatch

```bash
# Collect Tier 1 checks
grep -A1 "### " references/checks.md | grep -v "^#\|--" | head -30
# Collect Blocking checks
grep -A1 "Blocking" references/criteria.md | head -20
```

Cross-reference: any check in Tier 1 that criteria.md marks as Non-blocking → flag for tier move.
Any check in Tier 2 that criteria.md marks as Blocking → flag for tier move.

### [Flag] Missing False Positive Exemptions

```bash
grep -c "skip if\|exempt\|not flag\|unless" references/criteria.md
```

If count = 0 AND skill has Tier 2 checks: flag. Tier 2 without exemptions has high false positive rate.

### [Suggest] Optional Scoring Section

```bash
grep -in "score\|penalty\|total.*points\|severity score" references/criteria.md | head -5
```

If scoring section present: flag as optional bloat unless dispatcher contract requires a score output.

---

## Missing File Checks (cross-file)

Run after inventorying all files present.

| Archetype | Required file | Missing action |
|-----------|--------------|----------------|
| Advisory | sharp-edges.md | **Flag** — most actionable advisory content |
| Advisory | patterns.md | **Flag** — advisory without patterns is an FAQ |
| Review Sub-agent | criteria.md | **Flag** — no disposition model |
| Review Sub-agent | report.md | **Flag** — no output format |
| Active Audit | criteria.md | **Flag** — no pass/fail thresholds |
| Any non-Advisory | Silent execution directives in SKILL.md | **Auto** — insert |
