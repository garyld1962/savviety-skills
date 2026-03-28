---
name: agent-browser
description: >-
  Browser automation for AI agents using agent-browser CLI. Use when you need to
  interact with websites: navigate, fill forms, click buttons, take screenshots,
  extract data, scrape content, or test web apps.
mode: agent
tools:
  - terminal
---

# Browser Automation with agent-browser

You have access to `agent-browser`, a CLI tool for browser automation. Use it via the terminal.

## Core Workflow

Every browser task follows this pattern:

1. **Navigate**: `agent-browser open <url>`
2. **Snapshot**: `agent-browser snapshot -i` (get element refs like `@e1`, `@e2`)
3. **Interact**: Use refs to click, fill, select
4. **Re-snapshot**: After navigation or DOM changes, get fresh refs

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # Check result
```

## Essential Commands

**Navigation:**
- `agent-browser open <url>` — Navigate to page
- `agent-browser close` — Close browser session
- `agent-browser wait --load networkidle` — Wait for network to settle

**Snapshots:**
- `agent-browser snapshot -i` — Interactive elements with refs (@e1, @e2...)
- `agent-browser snapshot -i -C` — Include cursor-interactive elements
- `agent-browser snapshot -s "#selector"` — Scope to CSS selector

**Interactions:**
- `agent-browser click @e1` — Click element
- `agent-browser fill @e2 "text"` — Clear and type
- `agent-browser type @e2 "text"` — Type without clearing
- `agent-browser select @e1 "option"` — Dropdown selection
- `agent-browser check @e1` — Toggle checkbox
- `agent-browser scroll down 500` — Scroll page

**Data Extraction:**
- `agent-browser get text @e1` — Get element text
- `agent-browser get url` — Current URL
- `agent-browser get title` — Page title

**Screenshots:**
- `agent-browser screenshot` — Screenshot to temp dir
- `agent-browser screenshot --full` — Full page screenshot
- `agent-browser screenshot --annotate` — Numbered interactive elements
- `agent-browser pdf output.pdf` — Save as PDF

**Diffs:**
- `agent-browser diff snapshot` — Compare current vs last snapshot
- `agent-browser diff screenshot --baseline before.png` — Visual diff

## Command Chaining

Chain with `&&` when you don't need intermediate output:

```bash
agent-browser open https://example.com && \
  agent-browser wait --load networkidle && \
  agent-browser screenshot page.png
```

Run separately when you need to parse output (e.g., snapshot to discover refs, then interact).

## Authentication

**Import from running browser:**
```bash
agent-browser --auto-connect state save ./auth.json
agent-browser --state ./auth.json open https://app.example.com
```

**Persistent profile (stays logged in):**
```bash
agent-browser --profile ~/.myapp open https://app.example.com/login
# Future runs already authenticated
agent-browser --profile ~/.myapp open https://app.example.com/dashboard
```

**Named sessions (multi-agent safe):**
```bash
agent-browser --session myapp open https://app.example.com/login
# ... login flow ...
agent-browser close  # Auto-saves
```

## Device Emulation

```bash
agent-browser set device "iPhone 14"
agent-browser set viewport 1920 1080
```

## Key Rules

- **Refs expire** after navigation, form submission, or dynamic content. Always re-snapshot.
- **Default timeout** is 25 seconds. Use explicit waits for slow pages.
- **Always close** sessions when done: `agent-browser close`
- **Use named sessions** when running multiple agents to avoid conflicts.
- **Chain commands** for efficiency when intermediate output isn't needed.

## JavaScript Evaluation

```bash
agent-browser eval 'document.title'
agent-browser eval --stdin <<'EVALEOF'
Array.from(document.querySelectorAll("img"))
  .filter(i => !i.alt)
  .map(i => ({ src: i.src, width: i.width }))
EVALEOF
```
