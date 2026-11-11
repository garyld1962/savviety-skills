---
name: jev-gate
description: "Local System-1 Jev-class decision-model control plane (vllm-sr/Decision-1.0-Nox-4B or jaredpalmer/kev-4b on local RTX 5090 /v1/systemone via FastMCP jev-gate). Defines the 4 core contracts: cascading configuration, smart_search, triage_coding_task, and verify_code_invariants + gate_shell_command. Not user-invokable."
user-invocable: false
internal: true
kind: embedded
---

# `jev-gate` — Local System-1 Decision Control Plane

All code and prose synthesis stays on frontier cloud models (Claude, Gemini, OpenAI). The local Jev-class decision model (`vllm-sr/Decision-1.0-Nox-4B` or `jaredpalmer/kev-4b`) hosted on the local RTX 5090 (`/v1/systemone` endpoint, ~15ms latency) and exposed via the `jev-gate` FastMCP server acts strictly as a **single-pass probability control plane** (`choice`, `noul` yes/no, and `score`) before and after cloud actions.

---

## Contract 1: Cascading Configuration Hierarchy

All skills, hooks, and MCP tool calls must resolve configuration in this strict 3-tier precedence order:

```
Runtime Tool Args > Project-Local (./.jev-gate.toml) > User-Global (~/.config/jev-gate/config.toml)
```

1. **User-Global Config (`~/.config/jev-gate/config.toml`):**
   - Template: `templates/jev-gate.global.toml` (configure via `/configure jev-gate-global`).
   - Holds the RTX 5090 `/v1/systemone` endpoint URL, active decision model ID, default cloud model lane mappings (`fast_lane` vs. `deep_lane`), global search blocklists (`-site:linkedin.com`, `-site:pinterest.com`, `-site:quora.com`, `-site:medium.com`), and baseline confidence thresholds.
2. **Project-Local Config (`./.jev-gate.toml`):**
   - Template: `templates/jev-gate.project.toml` (configure via `/configure jev-gate`).
   - Overrides domain-specific search allowlists (e.g., `3d_printing`, `rust_cad`, `software_arch`), project-specific architectural invariants (`[[invariants]]` evaluated as `noul` booleans against `git diff`s), and per-project lane routing thresholds.
3. **Runtime Tool Args:**
   - Explicit arguments passed to `smart_search`, `triage_coding_task`, `verify_code_invariants`, or `gate_shell_command` override both files for that call.

---

## Contract 2: Pre-Search Hygiene (`smart_search`)

- **Rule:** Never execute a raw web search for technical settings, hardware parameters, CAD/slicer profiles, or SDK/library documentation directly.
- **Procedure:**
  1. Call the `jev-gate` MCP tool `smart_search(query, force_backend="auto")` first.
  2. In a single ~15ms forward pass on the RTX 5090, `smart_search`:
     - Classifies the query domain (`3d_printing`, `rust_cad`, `software_arch`, `general_dev`, etc.).
     - Strips social/SEO spam by appending `global_blocklist` (`-site:linkedin.com -site:pinterest.com -site:quora.com -site:medium.com`).
     - Injects matching `domain_allowlists` from `.jev-gate.toml` (e.g., `site:printables.com`, `site:docs.rs`, `site:github.com`).
     - Evaluates `needs_perplexity_synthesis` (`noul`):
       - `< 0.80` → executes a fast filtered search for exact parameters/docs.
       - `>= 0.80` → escalates to Perplexity MCP for multi-source synthesis.
- **Graceful Fallback (when `jev-gate` is unreachable):**
  - Append the static `global_blocklist` (`-site:linkedin.com -site:pinterest.com -site:quora.com -site:medium.com`) to the query manually before calling the host's native web search tool, and log `[jev-gate: offline — applied static search blocklist]`.

---

## Contract 3: Pre-Coding Triage & Context Pruning (`triage_coding_task`)

- **Rule:** Before starting a multi-file task or loading large repository contexts into the cloud LLM, call `triage_coding_task(task_prompt, candidate_files)`.
- **Who calls it:** the lane choice only takes effect if it is made *before* the coding agent is spawned, because an agent's model is fixed at spawn time. Orchestrators (e.g. `execute-plan`'s `run-plan.mjs`) call it per task and pass the lane's model to the agent they spawn. An agent that calls it for itself can only use the abstention and context-pruning outputs.
- **Outputs & Required Agent Actions:**
  1. **Model Lane Selection (`fast_lane` vs. `deep_lane`):**
     - `fast_lane` (e.g., Claude Sonnet/Haiku, Gemini Flash) for single-file edits, boilerplate, unit tests, and syntax fixes.
     - `deep_lane` (e.g., Claude Opus, Gemini Pro, OpenAI frontier reasoning) for multi-file refactors, concurrency, and architecture.
     - **Confidence Floor:** If lane confidence is `< 0.65`, automatically fall back to `deep_lane`.
  2. **Abstention Gate (`insufficient_context`):**
     - If `insufficient_context` scores highest among triage outcomes, **halt immediately** and ask the user for clarification (or emit a `plan-ambiguity` / `blocked` status in autonomous runs) before generating code.
  3. **Context Pruning (`keep_full` | `keep_signatures_only` | `drop`):**
     - Scores all `candidate_files` in parallel:
       - `keep_full`: Read the full file into context.
       - `keep_signatures_only`: Read only exported interfaces/signatures (via `jev-gate` skeleton output or `ast-grep`), never the full implementation body.
       - `drop`: Do not read into the cloud context window.
- **Graceful Fallback (when `jev-gate` is unreachable):**
  - Default to `deep_lane`, log `[jev-gate: offline — defaulting to deep_lane]`, and use standard repo-scoped file reading.

---

## Contract 4: Post-Generation Invariant & Tool-Safety (`verify_code_invariants` & `gate_shell_command`)

### 4A. Diff Auditing (`verify_code_invariants`)

- **Rule:** After generating a code patch (and before running slow builds/tests or committing), pass the `git diff` to `verify_code_invariants(git_diff)`.
- **What it does:** Evaluates all project architectural invariants defined under `[[invariants]]` in `.jev-gate.toml` in a single parallel forward pass (`noul` boolean probabilities).
- **Required Action:**
  - If any invariant exceeds its failure threshold (default `>= 0.80`), fix the architectural violation immediately before running build/test or presenting the code.
  - Record invariant check status in checkpoint and execution reports.
- **Graceful Fallback (when `jev-gate` is unreachable):**
  - Log `[jev-gate: offline — verify_code_invariants skipped]` in the checkpoint/execution report; never claim that semantic invariants passed when the endpoint was unreachable.

### 4B. Shell Gating (`gate_shell_command`)

- **Rule:** Before running non-trivial shell commands (mutations, git history changes, package operations, database scripts, file deletions), evaluate `(command, working_dir)` via `gate_shell_command(command, working_dir)` (either via the MCP tool or automatically via the `PreToolUse` hook script `bin/jev-shell-hook`).
- **Decision Classes (`choice`):**
  - `safe_auto_execute` (`probability >= 0.85`): Execute immediately without prompting.
  - `requires_user_confirmation` (`safe_auto_execute < 0.85` and not destructive): Pause and ask the user for confirmation.
  - `blocked_destructive`: Refuse execution immediately and explain the risk dimension (`modifies_git_history`, `destroys_uncommitted_work`, `touches_outside_workspace`, `exfiltrates_secrets`).
- **Graceful Fallback (when `jev-gate` is unreachable):**
  - Enforce the static destructive deny list (`git reset --hard`, `git push --force`, `git clean -f`, `git branch -D`, `rm -rf`) as hard blocks, and route non-trivial mutating commands to `requires_user_confirmation` (`ask`).

---

## Contract Summary

- **Inputs:**
  - `smart_search(query, force_backend="auto")`
  - `triage_coding_task(task_prompt, candidate_files)`
  - `verify_code_invariants(git_diff)`
  - `gate_shell_command(command, working_dir)`
- **Preconditions:** Cascading config loaded from `./.jev-gate.toml` and `~/.config/jev-gate/config.toml` when present.
- **Outputs:** Calibrated `choice`, `noul`, and `score` decisions governing search routing, model lane selection, context pruning, semantic diff invariants, and shell safety.
- **Failure modes:** When the local RTX 5090 `/v1/systemone` endpoint is unreachable, skills degrade gracefully per the fallback rules above (`deep_lane` + static search blocklist + logged invariant skip + `requires_user_confirmation` shell gate).
