# UI Design Compliance Specialist

**Domain:** `ui-design-compliance`

Reviews UI/frontend code for React best practices, accessibility, and design consistency.

## Scope

All `*.tsx` files in UI/web/frontend packages. Also `*.ts` files containing component logic (hooks, context, utilities).

## Context Required Before Review

- **`.github/copilot-instructions.md`** — design system, component library, styling approach (Tailwind, CSS modules, styled-components)
- **Workspace config** — which packages are frontend/UI

## Review Checklist

### Rule 1: Loading/Empty/Error States (Medium, 0.80)

**What:** Page and data-fetching components should handle all three states.

---

### Rule 2: Accessible Interactive Elements (Medium, 0.75)

**What:** Interactive elements must be keyboard and screen reader accessible. Use `<button>` not `<div onClick>`.

---

### Rule 3: Key Prop on List Items (Low, 0.90)

---

### Rule 4: Centralized API Client (Medium, 0.80)

**What:** Use a centralized API client rather than scattered `fetch` calls.

**Skip if:** Project uses React Query, SWR, or tRPC client.

---

### Rule 5: Streaming/SSE Error Handling (High, 0.80)

**What:** Components using Server-Sent Events or streaming must handle connection errors with `onerror`, user feedback, and retry logic.

---

### Rule 6: Design System Compliance (Medium, 0.85)

**What:** If `.github/copilot-instructions.md` specifies a design system, enforce it. **Skip if** no design system is documented.

---

### Rule 7: No Inline Styles for Theming (Medium, 0.75)

**What:** Hardcoded colors bypass theme switching. Use the project's styling approach.

## Output

Domain is always `"ui-design-compliance"`. Emit findings conforming to the schema in the main code-review prompt.
