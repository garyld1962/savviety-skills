---
description: >-
  Implement a feature, change, or addition. Reads existing code patterns first,
  then writes code that matches the project's style. Use for any "add X" or
  "create Y" task.
argument-hint: '<what to implement>'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
---

# Implement — Guided Code Generation

Write code that fits the project. Read first, write second, verify third.

## When to Use

- "Add a new endpoint / service / component / utility"
- "Create a new file that does X"
- "Implement this feature / story / ticket"
- Any task where you need to write new code or significantly modify existing code

---

## CRITICAL: Do Not Guess

- **File paths**: SEARCH the codebase before creating or referencing files. Do NOT invent paths.
- **Imports**: READ existing files to find import patterns. Do NOT guess at package names, aliases (`@/`, `~/`, `#`), or barrel exports.
- **APIs and methods**: READ the source or type definitions before calling a function. Do NOT hallucinate method signatures, parameters, or return types.
- **Dependencies**: Check `package.json` (or `.csproj`) before importing a library. If the package isn't installed, ASK before adding it. Do NOT assume.
- **Naming conventions**: READ 2-3 existing files in the same area. Match their naming (camelCase vs PascalCase, file naming, export patterns).
- **Error handling patterns**: READ how existing code handles errors. Do NOT add try-catch, Result types, or error middleware that the project doesn't use.
- **Test patterns**: If you need to add tests, READ an existing test file first. Match the framework, assertion style, and structure.

---

## Step 1: Understand the Request

Parse what the user wants. If unclear, ask ONE clarifying question. Do NOT proceed with assumptions.

State explicitly:
```
Task: <what I'm implementing>
Affected area: <which package/directory/module>
```

---

## Step 2: Read Before Writing

**This step is NOT optional.** You MUST read existing code before writing anything.

### 2a. Read project conventions

```
Read: .github/copilot-instructions.md
```

### 2b. Read the affected area

For EACH file you plan to create or modify:
1. If modifying: read the ENTIRE file first
2. If creating: read 2-3 sibling files in the same directory to learn the patterns
3. Read the relevant types/interfaces your code will use

### 2c. Map the pattern

Before writing, explicitly note:
```
Pattern observed:
- File naming: <e.g., kebab-case.ts, PascalCase.cs>
- Export style: <e.g., named exports, default export, barrel index>
- Import aliases: <e.g., @/lib, ~/utils, relative paths>
- Error handling: <e.g., try-catch with logger, Result<T>, middleware>
- Logging: <e.g., pino, console, ILogger, none>
```

---

## Step 3: Write Code

Now implement. Follow these rules:

### Match, don't innovate
- Use the SAME patterns as existing code. If the project uses `function` declarations, don't switch to arrow functions. If it uses classes, don't introduce functional style.
- Use the SAME level of abstraction. If nearby code is simple and direct, don't add layers of indirection.

### Minimal scope
- Implement ONLY what was requested. No bonus features, no "while I'm here" refactors.
- No comments explaining obvious code. Only add comments where the logic is non-obvious.
- No extra error handling beyond what existing code does.

### Real imports only
- Every import must reference a file or package that EXISTS. Search to verify.
- Copy import patterns from sibling files.

---

## Step 4: Verify

After writing, verify your changes:

### 4a. Check imports resolve

For each new import you added, verify the target exists:
```bash
# For relative imports — verify the file exists
ls <import-target-path>

# For package imports — verify it's installed
cat package.json | grep '<package-name>'
```

### 4b. Build

Run the project's build command (detect from `package.json` scripts or project docs):
```bash
<detected-build-command>
```

If build fails:
1. Read the error — it's usually a missing import, type mismatch, or syntax error
2. Fix minimally
3. Retry (max 3 attempts)
4. If still failing: STOP and show the error

### 4c. Test (if tests exist for this area)

```bash
<detected-test-command>
```

---

## Step 5: Report

```
## Implementation Complete

**Task:** <what was implemented>
**Files changed:**
- <path> — <what changed>

**Verified:**
- Imports resolve: YES/NO
- Build passes: YES/NO
- Tests pass: YES/NO/N/A

**Pattern notes:** <any deviations from existing patterns and why>
```

---

## Rules

1. **Read before write.** NEVER create a file without first reading its siblings. NEVER modify a file without reading it entirely.
2. **Match the project.** Your code should be indistinguishable from existing code. Same patterns, same style, same level of abstraction.
3. **No hallucinated imports.** If you can't find it in the codebase or package.json, it doesn't exist. ASK before adding dependencies.
4. **Minimal changes.** Implement what was asked. Nothing more.
5. **Verify or report failure.** Always try to build. If you can't verify, say so — don't claim it works.
6. **Stop after 3 failures.** If build or tests fail 3 times, STOP. Show the error. Do NOT spiral.
