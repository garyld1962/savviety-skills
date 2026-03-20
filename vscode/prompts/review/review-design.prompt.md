---
description: >-
  Design system compliance check for UI code: color tokens, icon library,
  component states, accessibility, theming. Reads project design rules.
agent: 'ask'
tools:
  - read
  - search
  - codebase
---

# Design System Compliance Review

Quick review of UI code for design system compliance.

---

## CRITICAL: Do Not Guess

- **Design system**: DETECT which design system the project uses (Tailwind, MUI, Chakra, custom, etc.). Check `package.json` and config files.
- **Color tokens**: Read the actual theme/config file. Do NOT assume color names or values.
- **Component library**: Check what's imported in existing components. Do NOT recommend components from a library the project doesn't use.
- **Accessibility standards**: Check if the project documents a specific WCAG level. Default to WCAG 2.1 AA only if nothing is specified.

---

## Step 1: Detect Design System

```bash
# Check for design system packages
cat package.json | grep -E '"(tailwindcss|@mui|@chakra-ui|@radix-ui|@headlessui|antd|shadcn)"'

# Check for theme/token files
ls tailwind.config.* theme.ts tokens.ts design-tokens.* 2>/dev/null

# Read project docs for design rules
```

Read 2-3 existing UI components to learn the project's patterns.

---

## Step 2: Check Each Pattern

### 2a. Color Usage

| Check | Pass | Fail |
|-------|------|------|
| Colors use design tokens/theme variables | `text-primary`, `theme.colors.primary` | Hardcoded `#ff0000`, `rgb(255,0,0)` |
| No hardcoded color values | All from tokens | Raw hex/rgb values |
| Dark mode support (if applicable) | Theme-aware colors | Static colors that break in dark mode |

### 2b. Component States

| Check | Pass | Fail |
|-------|------|------|
| Interactive elements have hover state | `:hover` styled | No hover feedback |
| Interactive elements have focus state | `:focus-visible` styled | No focus indicator |
| Disabled state handled | `disabled` prop + visual treatment | Clickable when disabled |
| Loading state handled | Loading indicator | No loading feedback |
| Empty state handled | Empty state UI | Blank when no data |
| Error state handled | Error message UI | Silent failure |

### 2c. Accessibility

| Check | Pass | Fail |
|-------|------|------|
| Images have alt text | `alt` attribute present | Missing alt |
| Form inputs have labels | `<label>` or `aria-label` | Unlabeled inputs |
| Color contrast sufficient | 4.5:1 for normal text, 3:1 for large | Low contrast |
| Keyboard navigation works | Tab order logical, Enter/Space activate | Only mouse-accessible |
| ARIA attributes correct | Valid ARIA roles and properties | Invalid or missing ARIA |

### 2d. Icons

| Check | Pass | Fail |
|-------|------|------|
| Uses project's icon library | Icons from designated library | Mixed icon sources |
| Icons have accessible labels | `aria-label` on icon buttons | Decorative icons as interactive |

### 2e. Spacing & Layout

| Check | Pass | Fail |
|-------|------|------|
| Spacing uses design system values | `gap-4`, `p-6`, etc. | Arbitrary `margin: 13px` |
| Responsive behavior defined | Breakpoint-aware layout | Fixed-width only |

---

## Step 3: Report

```
## Design Review: <file(s)>

**Design System:** <detected>
**Theme:** <theme file location>

| Pattern | Verdict | Findings |
|---------|---------|----------|
| Colors | PASS/WARN/FAIL | N issues |
| Component States | PASS/WARN/FAIL | N issues |
| Accessibility | PASS/WARN/FAIL | N issues |
| Icons | PASS/WARN/FAIL | N issues |
| Spacing | PASS/WARN/FAIL | N issues |

### Findings
1. **[severity]** `file:line` — <description>
   - Convention: <project's design pattern>
   - Found: <what the code does>
   - Fix: <specific change>
```

---

## Rules

1. **Detect the design system first.** Reviewing UI code without knowing the design system produces wrong recommendations.
2. **Project tokens are the standard.** If the project uses `text-gray-600` from Tailwind, that's correct — do NOT recommend a different shade.
3. **Accessibility is non-negotiable.** Missing alt text and unlabeled inputs are always findings regardless of project conventions.
