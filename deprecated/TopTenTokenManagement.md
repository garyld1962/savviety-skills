# Top Ten Token Management Features

Sourced from `~/.claude/CLAUDE.md`, `claude/MODEL-POLICY.md`, and the `claude/` skills tree.

---

## 1. Context Budget Management

Rules and mechanisms that govern how much context is consumed and when to discard it.

**Three-Axis Token Budget (CLAUDE.md §2)**
Input, output, and context are each governed by explicit rules. Read targeted line ranges, not whole files. Write no preamble or recap. Never re-emit unchanged code — use targeted edits. If removing a sentence wouldn't change what the user can act on, remove it.

**Context Window Phase Clearing (CLAUDE.md §10)**
At natural phase boundaries — plan → execute, research → implement, review → fix, long debugging → clean attempt — prior tool outputs become dead weight. Suggest `/exit` and a fresh session so the next phase starts with only the artifact it needs, not the exploration that produced it.

**Cross-Session Memory Compression (`.remember/` + ccx)**
A rolling memory system (`now.md`, `today-*.md`, `recent.md`, `archive.md`) and a structured ccx event log (plan/intent/status) compress prior work into a digest. Fresh sessions read the digest instead of replaying raw tool output, eliminating the "reconstruct prior work" token cost at session start.

---

## 2. Cost-by-Capability Routing

Matching model tier to task complexity so expensive models are only used where they add value.

**Model Tier Pinning (MODEL-POLICY.md)**
Three tiers with explicit policy: `haiku` for dispatcher/lookup skills, `opus` for deep-reasoning skills, and unpinned (session-inherited) for everything else. Prevents over-using expensive models on cheap work and under-using capable models where reasoning headroom matters.

**Haiku-as-Router Pattern**
High-frequency routing skills (`find-skills`, `configure`, `repo-status`, `skill-help`, `env-check`) are pinned to Haiku specifically because they fire at the entry point of every skill invocation chain. Each invocation is cheap, but they run constantly — pinning here is the highest-ROI tier decision in the policy.

---

## 3. Tooling & Infrastructure

External tools and structural patterns that reduce token consumption at the infrastructure level.

**RTK — Rust Token Killer (RTK.md)**
A hook-based CLI proxy installed globally. Intercepts all shell commands and strips/compresses output before it reaches the context window, with claimed 60–90% savings on common dev operations. Transparent to the user — the hook rewrites `git status` → `rtk git status` automatically.

**Parallel Execution Lanes (`/parallel-optimization`)**
Replaces sequential back-and-forth with disjoint-write-scope lanes and milestone barriers. Each lane receives a narrow shared context packet instead of the full conversation history, and fewer coordination round-trips means fewer tokens spent re-stating context between steps.

**WSL/Bash over Windows/PowerShell**
Running in WSL with Bash produces significantly terser tool output than PowerShell. Unix commands (`git`, `rg`, `ls`, `grep`) emit compact, pipeable text. PowerShell serializes structured objects with verbose headers, type annotations, and formatting that inflate context with low-signal content. Shorter command output means less context consumed per tool call — compounding across a long session. Unix tools like `rg` and `fd` are also designed for minimal output by default, with no PowerShell equivalent as concise.

---

## 4. Guardrails Against Runaway Spending

Hard limits that stop token burn when a task loops or spirals.

**Token Guardrail in Scanning Skills**
Skills like `security-quick-check` and `modernization-rubric` embed a hard stop: halt file reading once cumulative reads consume ~30% of the available context window. The remaining 70% is reserved for synthesis phases. Prevents runaway scanning on large codebases from crowding out the work that actually produces output.

**Retry Budget Circuit Breaker (`/execute-plan`)**
A configurable `retry_budget` (default: 20 retries / 60 min) enforces CLAUDE.md §6 (impasse handling) as a hard limit. When exhausted, the executor surfaces the impasse rather than attempting another variant of the same broken fix. Prevents token burn on wrong-model-of-the-problem loops.

---

## 5. Review Quality vs. Token Tradeoff

Structuring review passes to maximize depth without inflating context.

**Separate-Pass Domain Reviews (`/code-review-professional`)**
Each review domain (security, performance, data integrity, concurrency, etc.) gets its own isolated context window pass. The explicit rationale: a combined prompt produces shallow bullet-per-domain output, while isolation forces depth per domain. The tradeoff is more total tokens spent, but higher signal per token — findings are actionable rather than superficial.
