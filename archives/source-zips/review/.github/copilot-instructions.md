# Project Instructions

> **This file is the single source of truth for project conventions.**
> All skills (code-review, architecture-map, etc.) read this file for configuration.
> Update this file as the project evolves.

## Project Overview

Port of a legacy Java pricing precalculation engine to C#/.NET 10.
Imports dealer pricing data from Oracle (SYSPDB2 schema) into a local SQLite
cache, then serves a web UI for browsing deal structures (dealers → products →
buckets → add-ons → rules).

## Tech Stack

- **Language:** C# 13 / .NET 10 (preview)
- **Projects:** `PricingPrecalc` (console importer), `PricingWeb` (minimal-API web app)
- **Databases:** Oracle (source, read-only) → SQLite (local cache, WAL mode)
- **NuGet packages:** `Microsoft.Data.Sqlite`, `Oracle.ManagedDataAccess.Core`, `Microsoft.Extensions.Configuration.*`
- **Frontend:** Static HTML served from `PricingWeb/wwwroot/`
- **Target runtime:** Linux container

## Build & Test Commands

This project lives on the WSL filesystem. **Always use `.scripts/run.sh`** for terminal commands:

```powershell
# All commands go through the runner:
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh <command> [args]

# Examples:
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh restore
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh build
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh test
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh run web
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh run precalc
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh watch web
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh commit "feat(scope): message"
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh status
wsl -d Ubuntu-24.04 -e bash .scripts/run.sh exec <any command>
```

**IMPORTANT — Terminal rules:**
- NEVER create throwaway `.sh` scripts — use `run.sh exec` for one-off commands
- NEVER run raw `dotnet`, `git` etc. directly — always go through `run.sh`
- If a new command pattern is needed repeatedly, add it to `run.sh` as a new case
- The runner handles PATH/env setup automatically

## Project Structure

```
.github/
  copilot-instructions.md  # This file
  agents/                  # Agent definitions (code review, architecture mapper)
  skills/                  # Skill definitions (review domains, architecture mapping)
  prompts/                 # Prompt files (BA, dev, review workflows)
.scripts/
  run.sh                   # WSL command router — ALL terminal commands go through here
.vscode/
  settings.json            # VS Code settings + auto-approve rules
  tasks.json               # Build/test/run tasks via run.sh
PricingPrecalc/            # Console app — Oracle → SQLite data importer
  Program.cs               # Entry point: config, SQLite init, Oracle connect, import
  DataImporter.cs          # Bulk data importer: 7-phase relationship chain import
  schema.sql               # SQLite schema definition
  appsettings.json         # Config (SQLite path, Oracle conn string placeholder)
PricingWeb/                # Minimal-API web app — browsing the imported data
  Program.cs               # Minimal-API setup, endpoints, static files
  ImportService.cs         # Oracle import trigger from web UI
  DealSummaryService.cs    # Query engine: dealer → products → buckets → add-ons
  wwwroot/index.html       # Static HTML frontend
  appsettings.json         # ASP.NET Core logging config
  Properties/launchSettings.json
```

## Coding Conventions

### General
- Use **nullable reference types** (`<Nullable>enable</Nullable>`)
- Prefer top-level statements for console apps
- Prefer minimal APIs over MVC controllers
- Use `record` for DTOs and value objects
- Use `using` declarations (not `using` blocks) where scope allows

### Naming
- **Files:** PascalCase (`DataImporter.cs`)
- **Types/Interfaces:** PascalCase (`DealSummaryService`)
- **Methods:** PascalCase (`GetOwnerChain`)
- **Local variables:** camelCase (`dealerCode`)
- **Constants:** PascalCase (`Schema`) for private, UPPER_SNAKE for public configs

### Error Handling
- Always handle async errors — no unhandled promise rejections
- Validate user input at system boundaries (API endpoints)
- Return `Results.Json(new { error = ... }, statusCode: 500)` for API errors

### Git & Commits
- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(scope): description`
- One logical change per commit

### Security
- No secrets in source code — use User Secrets (`dotnet user-secrets`)
- Oracle connection string stored in User Secrets (ID: `36720d48-d363-481f-999c-e48ecda79775`)
- All SQL queries use parameterized queries (no string concatenation)

## Known Issues

- `ImportRequest` record in `ImportService.cs` has `FromDate`/`ToDate` but `ImportDealerAsync` only accepts a single `effectiveDate`
- `CheckOverridden` in `DealSummaryService.cs` is stubbed (always returns `false`)
- No Dockerfile yet — deployment model is linux container but not containerized
- No test project exists
- `GetBaseBuckets` builds secondary bucket nesting but only returns primary buckets (secondary nesting incomplete)
