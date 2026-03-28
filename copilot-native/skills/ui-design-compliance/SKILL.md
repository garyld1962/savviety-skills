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
