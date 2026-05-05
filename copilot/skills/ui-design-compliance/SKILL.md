---
name: ui-design-compliance
description: UI review rubric for design-system consistency, component states, accessibility, and theme-safe implementation.
---

# UI Design Compliance

Use this skill for frontend and component review passes.

## Review focus

- detect the actual design system or component library first
- use the project's tokens, theme files, and component patterns as the standard
- verify loading, empty, error, disabled, focus, and hover states where
  applicable
- check accessible interactive elements, labels, alt text, and keyboard support
- avoid hardcoded theming values that bypass the design system
- flag spacing, icon, or responsive behavior that clearly violates local
  patterns

## Guardrails

- Do not recommend components from libraries the project does not use.
- Default accessibility expectations to WCAG 2.1 AA only when the repo does not
  specify otherwise.

## Examples

- **Component review:** Compare a changed component to the repo's existing token
  and theme usage, then flag hardcoded colors or spacing only when they really
  bypass the local design system.
- **State review:** If a control has loading and error states in adjacent local
  components but the changed component omits them, flag the missing states as a
  concrete UX issue.

## Do Nots

- Do not recommend swapping in a new component library just because it would be
  cleaner in the abstract.
- Do not treat personal visual taste as a design-system defect.
- Do not skip keyboard, focus, and label checks just because the component looks
  correct visually.

## Closed Decisions

- The repo's existing design system, tokens, and component patterns are the
  standard.
- Accessibility expectations follow repo rules first, then WCAG 2.1 AA when the
  repo is silent.
- Theme-safe implementation is required; hardcoded theming values are not the
  default path.
