#!/usr/bin/env bash
# Structural validation tests for the domain-based code review system.
# Run from the repo root: bash claude/domain-review/tests/validate-structure.sh

set -uo pipefail

REVIEW_DIR="claude/domain-review"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

echo "=== Code Review Structure Validation ==="
echo ""

# --- 1. Required directories exist ---
echo "1. Directory structure"
for dir in concept dialect platform profiles; do
  if [ -d "$REVIEW_DIR/$dir" ]; then
    pass "$dir/ exists"
  else
    fail "$dir/ missing"
  fi
done

# --- 2. SKILL.md exists and has frontmatter ---
echo ""
echo "2. Controller (SKILL.md)"
if [ -f "$REVIEW_DIR/SKILL.md" ]; then
  pass "SKILL.md exists"
  if head -1 "$REVIEW_DIR/SKILL.md" | grep -q '^---'; then
    pass "SKILL.md has frontmatter"
  else
    fail "SKILL.md missing frontmatter"
  fi
  if grep -q '^name:' "$REVIEW_DIR/SKILL.md"; then
    pass "SKILL.md has name field"
  else
    fail "SKILL.md missing name field"
  fi
else
  fail "SKILL.md missing"
fi

# --- 3. Every concept domain has required frontmatter fields ---
echo ""
echo "3. Concept domain frontmatter"
for f in "$REVIEW_DIR"/concept/*.md; do
  name=$(basename "$f")
  # Check required fields
  for field in "id:" "type:" "title:" "severity_owner:"; do
    if grep -q "^$field" "$f"; then
      pass "$name has $field"
    else
      fail "$name missing $field"
    fi
  done
  # Check type is concept
  if grep -q "^type: concept" "$f"; then
    pass "$name type is concept"
  else
    fail "$name type is not concept"
  fi
  # Check severity_owner is true
  if grep -q "^severity_owner: true" "$f"; then
    pass "$name owns severity scale"
  else
    fail "$name does not own severity scale (expected true for concepts)"
  fi
done

# --- 4. Every dialect/platform overlay has required frontmatter ---
echo ""
echo "4. Overlay frontmatter"
for f in "$REVIEW_DIR"/dialect/*.md "$REVIEW_DIR"/platform/*.md; do
  name=$(basename "$f")
  for field in "id:" "type:" "title:" "extends:"; do
    if grep -q "^$field" "$f"; then
      pass "$name has $field"
    else
      fail "$name missing $field"
    fi
  done
  # Check severity_owner is false
  if grep -q "^severity_owner: false" "$f"; then
    pass "$name severity_owner is false"
  else
    fail "$name severity_owner should be false for overlays"
  fi
  # Check extends points to a real concept
  extends_target=$(grep "^extends:" "$f" | sed 's/^extends: *//')
  if [ -f "$REVIEW_DIR/${extends_target}.md" ]; then
    pass "$name extends $extends_target (file exists)"
  else
    fail "$name extends $extends_target (FILE NOT FOUND)"
  fi
done

# --- 5. Every profile references only existing domains ---
echo ""
echo "5. Profile domain references"
for f in "$REVIEW_DIR"/profiles/*.yaml; do
  pname=$(basename "$f")
  # Extract domain IDs from profile (indented id: lines under domains:, not the top-level id:)
  grep "^    *- *id:" "$f" | sed 's/.*id: *//' | while read -r domain_id; do
    if [ -f "$REVIEW_DIR/${domain_id}.md" ]; then
      pass "$pname references $domain_id (exists)"
    else
      fail "$pname references $domain_id (FILE NOT FOUND)"
    fi
  done
done

# --- 6. Every profile overlay references only existing overlays ---
echo ""
echo "6. Profile overlay references"
for f in "$REVIEW_DIR"/profiles/*.yaml; do
  pname=$(basename "$f")
  # Extract overlay IDs (lines under overlays: that start with - )
  in_overlays=false
  while IFS= read -r line; do
    if echo "$line" | grep -q "^overlays:"; then
      in_overlays=true
      continue
    fi
    if $in_overlays; then
      if echo "$line" | grep -q "^  - "; then
        overlay_id=$(echo "$line" | sed 's/^  - *//')
        if [ -f "$REVIEW_DIR/${overlay_id}.md" ]; then
          pass "$pname overlay $overlay_id (exists)"
        else
          fail "$pname overlay $overlay_id (FILE NOT FOUND)"
        fi
      elif echo "$line" | grep -qv "^$\|^#"; then
        in_overlays=false
      fi
    fi
  done < "$f"
done

# --- 7. Severity scale consistency ---
echo ""
echo "7. Severity scale in concept domains"
for f in "$REVIEW_DIR"/concept/*.md; do
  name=$(basename "$f")
  if grep -q "critical.*major.*minor.*nit" "$f" 2>/dev/null || \
     (grep -q "critical" "$f" && grep -q "major" "$f" && grep -q "minor" "$f" && grep -q "nit" "$f"); then
    pass "$name has all four severity levels"
  else
    fail "$name missing severity levels (expected: critical, major, minor, nit)"
  fi
done

# --- 8. Anti-confirmatory instruction ---
echo ""
echo "8. Anti-confirmatory instructions in concept domains"
for f in "$REVIEW_DIR"/concept/*.md; do
  name=$(basename "$f")
  if grep -qi "bar-raising instruction\|do not say " "$f"; then
    pass "$name has anti-confirmatory instruction"
  else
    fail "$name missing anti-confirmatory instruction"
  fi
done

# --- 9. Output format section ---
echo ""
echo "9. Output format in concept domains"
for f in "$REVIEW_DIR"/concept/*.md; do
  name=$(basename "$f")
  if grep -q "## Output format" "$f"; then
    pass "$name has output format section"
  else
    fail "$name missing output format section"
  fi
done

# --- 10. Profile has required fields ---
echo ""
echo "10. Profile schema"
for f in "$REVIEW_DIR"/profiles/*.yaml; do
  pname=$(basename "$f")
  for field in "id:" "title:" "description:"; do
    if grep -q "^$field" "$f"; then
      pass "$pname has $field"
    else
      fail "$pname missing $field"
    fi
  done
  if grep -q "^domains:" "$f"; then
    pass "$pname has domains list"
  else
    fail "$pname missing domains list"
  fi
  if grep -q "^overlays:" "$f"; then
    pass "$pname has overlays list"
  else
    fail "$pname missing overlays list"
  fi
done

# --- 11. Domain count ---
echo ""
echo "11. Domain counts"
concept_count=$(ls "$REVIEW_DIR"/concept/*.md 2>/dev/null | wc -l)
dialect_count=$(ls "$REVIEW_DIR"/dialect/*.md 2>/dev/null | wc -l)
platform_count=$(ls "$REVIEW_DIR"/platform/*.md 2>/dev/null | wc -l)
profile_count=$(ls "$REVIEW_DIR"/profiles/*.yaml 2>/dev/null | wc -l)
echo "  Concepts: $concept_count"
echo "  Dialects: $dialect_count"
echo "  Platforms: $platform_count"
echo "  Profiles: $profile_count"
if [ "$concept_count" -ge 17 ]; then pass ">=17 concept domains"; else fail "Expected >=17 concepts, got $concept_count"; fi
if [ "$dialect_count" -ge 4 ]; then pass ">=4 dialect overlays"; else fail "Expected >=4 dialects, got $dialect_count"; fi
if [ "$platform_count" -ge 3 ]; then pass ">=3 platform overlays"; else fail "Expected >=3 platforms, got $platform_count"; fi
if [ "$profile_count" -ge 5 ]; then pass ">=5 profiles"; else fail "Expected >=5 profiles, got $profile_count"; fi

# --- Summary ---
echo ""
echo "=== Results ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo ""
if [ "$FAIL" -gt 0 ]; then
  echo "VALIDATION FAILED"
  exit 1
else
  echo "ALL TESTS PASSED"
  exit 0
fi
