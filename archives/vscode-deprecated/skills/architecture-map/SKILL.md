---
name: architecture-map
description: >
  Map the overall architecture of this solution as a reference document.
  Produces a structured Markdown file at docs/architecture.md covering projects,
  data flow, domain model, API surface, and deployment target.
  Other review skills should read this document for context.
---

# Mission

Produce (or update) `docs/architecture.md` — a concise, structured reference
that describes how this solution is organized, how data flows through it, and
what domain concepts are involved.

This document is the **single source of truth** other review skills consult
before analysing code. Keep it factual and evidence-based — cite files and
line ranges.

# When to run

- Once at the start of a new assessment engagement.
- After significant structural changes (new projects, new data sources, API
  redesigns).
- On demand when the user asks for an architecture overview.

# Output location

`docs/architecture.md`

Create the `docs/` directory if it does not exist.

# Required sections

## 1. Solution overview

- Solution file and contained projects (`*.csproj`).
- Target framework, SDK version, key NuGet packages.
- One-paragraph summary of what the system does.

## 2. Project breakdown

For **each** project in the solution:

| Field | Detail |
|---|---|
| Name | Project name |
| SDK | e.g. `Microsoft.NET.Sdk`, `Microsoft.NET.Sdk.Web` |
| Role | Console app / Web API / Class library / Worker / Test |
| Entry point | `Program.cs` or equivalent |
| Key classes | Top 5 classes by importance, one-line purpose each |
| Dependencies | Other projects it references, major NuGet packages |

## 3. Data flow diagram

A **Mermaid** `flowchart LR` (or `TD`) showing:

- External data sources (Oracle, files, queues, etc.)
- Internal stores (SQLite, caches, etc.)
- Projects / services and how data moves between them
- API consumers (browser, CLI, other services)

Keep it to ≤15 nodes. Use subgraphs for logical grouping.

## 4. Domain model

A **Mermaid** `erDiagram` or a table listing the core domain entities
(tables, records, aggregates) and their relationships.

Focus on the top ~15 entities. Reference `schema.sql` or EF model files.

## 5. API surface

For Web / API projects, list every endpoint:

| Method | Route | Purpose | Request body | Response shape |
|---|---|---|---|---|

## 6. Configuration & secrets

- Where configuration is loaded (`appsettings.json`, User Secrets, env vars).
- Which settings are required vs. optional.
- How secrets are managed (User Secrets ID, Key Vault, etc.).

## 7. Build, run & deploy

- How to build, test, run locally (reference `.scripts/run.sh` commands).
- Target deployment model (Linux container, App Service, K8s, etc.).
- Any Dockerfile or CI pipeline present (or absent).

## 8. Key observations

Bullet list of notable architectural decisions, known gaps, or risks spotted
during the mapping. These become input for the review skills.

# Process

1. Parse the `.sln` to enumerate projects.
2. Read each `.csproj` for framework, SDK, package references, and project references.
3. Read `Program.cs` / `Startup.cs` of each project.
4. Read key service classes, entity definitions, schema files.
5. Read configuration files (`appsettings.json`, `launchSettings.json`).
6. Assemble the document following the template above.
7. Write to `docs/architecture.md`.

# Rules

- Do NOT modify any source code — this is a **read-only** analysis.
- Cite evidence: file paths and line ranges for every claim.
- Use Mermaid for diagrams (GitHub-rendered).
- Keep the document under ~400 lines — brevity over exhaustiveness.
- If information is uncertain, say so explicitly (e.g. "No Dockerfile found —
  deployment model is unclear").
