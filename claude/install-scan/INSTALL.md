# install-scan — Installation

## What it does

A `PostToolUse` hook that intercepts `Bash` calls matching package install commands (`brew install`, `pip install`, `npm install`, `dotnet tool install`, `gh extension install`, `cargo install`, `gem install`, `apt install`) and scans the named packages against [OSV.dev](https://osv.dev) — Google's federated vulnerability database covering NVD + GHSA + ecosystem advisories.

Findings (CVE-IDs, severity, summary, fix version) print inline so the user sees them in chat without opening a log file.

**Behavior:** detect + report. Never silent on findings. Never blocks (always exits 0). Pair with a `PreToolUse` hook for blocking.

## Why this control exists

AI coding agents (Claude Code, Copilot, Cursor) install packages on the developer's behalf. Traditional dev-tool security (EDR, SCA at PR time, container scanners) doesn't intercept the moment-of-install when an AI agent is the one running the package manager. This hook plugs that gap.

## Coverage matrix

| Ecosystem | Detected commands |
|---|---|
| Homebrew | `brew install`, `brew upgrade` |
| PyPI | `pip install`, `pip3 install`, `python3 -m pip install` |
| npm | `npm install`, `npm i`, `npm add`, `yarn add`, `pnpm add`, `pnpm install` |
| NuGet | `dotnet tool install`, `dotnet add package` |
| crates.io | `cargo install`, `cargo add` |
| RubyGems | `gem install` |
| GitHub CLI | `gh extension install` |
| Debian | `apt install`, `apt-get install` |

## Prerequisites

- `jq` and `curl` (almost always already present on dev machines)
- Network access to `https://api.osv.dev`

For richer scanning of source directories and container images via the companion `scan-now.sh`:
- `osv-scanner` (Go) — `brew install osv-scanner` or download from <https://github.com/google/osv-scanner/releases>
- `grype` (Go) — `brew install grype` or download from <https://github.com/anchore/grype/releases>

## Install

Two install models — pick one.

### Option A · Per-project (recommended; matches `settings.template.json`)

Copy `install-scan/` into the project at `.claude/install-scan/`, then add this to the project's `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.claude/install-scan/install-scan.sh",
            "timeout": 30,
            "statusMessage": "Scanning installed packages..."
          }
        ]
      }
    ]
  }
}
```

### Option B · Global (`~/.claude/`)

Copy `install-scan/` to `~/.claude/install-scan/` and add the same `PostToolUse` block to `~/.claude/settings.json`, with the absolute path to the script.

## Verify

After installing, simulate a known-vulnerable install:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"pip install requests==2.31.0"}}' | bash .claude/install-scan/install-scan.sh
```

You should see 3 GHSAs (the `requests<2.32.0` advisories) listed inline, with severity, fix version, and summary.

## On-demand scanning (`scan-now.sh`)

Use the companion script anytime you want to scan something without an install trigger:

```bash
# Single package against OSV.dev API
.claude/install-scan/scan-now.sh pkg PyPI requests@2.31.0
.claude/install-scan/scan-now.sh pkg npm lodash@4.17.20

# Source directory (uses osv-scanner)
.claude/install-scan/scan-now.sh dir ./

# Container image (uses grype — broader DB)
.claude/install-scan/scan-now.sh image myregistry.azurecr.io/myapp:v1
```

## CISA KEV overlay

The hook also cross-checks every CVE alias of an OSV finding against [CISA's Known Exploited Vulnerabilities catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog). If a finding is actively being exploited in the wild per CISA, the line is flagged with `🔥 ACTIVELY EXPLOITED (CISA KEV: CVE-...)`.

The KEV catalog JSON feed is cached locally for 6 hours under `/tmp/cisa-kev-cache.json`; the overlay degrades gracefully (skips flagging) if the feed can't be fetched.

This signal matters because CISA KEV findings are not theoretical — they're CVEs with confirmed active exploitation, often required to be patched within 21 days under [BOD 22-01](https://www.cisa.gov/news-events/directives/binding-operational-directive-22-01) for federal agencies and used as a benchmark for everyone else.

## SBOM generation (`sbom-now.sh`)

Companion script that wraps `syft` to generate CycloneDX or SPDX Software Bills of Materials. SBOMs are a standardized inventory of every component and version in a build — required by US Executive Order 14028 for federal contractors, and coming under the EU Cyber Resilience Act.

```bash
# Source directory
.claude/install-scan/sbom-now.sh dir ./

# Container image
.claude/install-scan/sbom-now.sh image myregistry.azurecr.io/myapp:v1

# SPDX format (default is CycloneDX JSON)
SBOM_FORMAT=spdx-json .claude/install-scan/sbom-now.sh dir ./
```

**Why generate SBOMs at install time:**
- Re-scan stored SBOMs against future CVEs without rebuilding
- Diff across builds to catch unexpected dep additions ("why did 47 new transitives land in this release?")
- Feed downstream tools: Dependency-Track, Grype, Snyk, OSV-Scanner

Requires `syft` (Anchore): `brew install syft` or [download](https://github.com/anchore/syft/releases).

## Pattern scanning for LLM-flavored code smells (`pattern-scan.sh`)

Companion script that wraps **Semgrep** with a curated ruleset (`llm-patterns.semgrep.yml`) targeting patterns disproportionately produced by LLMs. The ruleset focuses on tutorial-era patterns the model copies from training data without considering modern best practice or current security guidance.

```bash
# Scan a directory
.claude/install-scan/pattern-scan.sh dir ./src

# Scan a single file
.claude/install-scan/pattern-scan.sh file ./api/handler.ts

# Scan files staged for the next git commit (good as a pre-commit hook)
.claude/install-scan/pattern-scan.sh staged

# Add upstream Semgrep packs alongside the LLM-specific rules
.claude/install-scan/pattern-scan.sh --extras dir ./
```

**What's in the ruleset (`llm-patterns.semgrep.yml`):**

| Language | LLM-flavored pattern detected |
|---|---|
| Python | `eval` / `exec`, `pickle.load`, `yaml.load` (vs safe_load), `verify=False`, `subprocess shell=True`, f-string SQL |
| JS / TS | `eval` / `Function(...)` constructor, CORS `'*'`, `rejectUnauthorized: false`, JWT `algorithm: 'none'`, `localStorage` for tokens, `Math.random()` for tokens |
| React / JSX | `dangerouslySetInnerHTML` |
| HTML | inline `<script>` tags, inline `onclick` / `onload` / `onerror` |
| Java | MD5 / SHA-1 in `MessageDigest`, `Runtime.exec()` with concat |
| Bash | `curl URL \| bash`, `eval $VAR` |
| Dockerfile | missing `USER` directive (image runs as root), `ADD https://...` |

Each rule's message explains *why it's an LLM-flavored smell*, not just the underlying security issue. That phrasing helps in code review — the reviewer sees "this is a classic 'quick LLM fix' pattern" and knows to push back specifically on AI-generated diffs.

**Requires Semgrep:** `brew install semgrep` (macOS) or `pip3 install semgrep` (Linux). Free OSS edition is sufficient.

**Add JMA-specific rules** by extending `llm-patterns.semgrep.yml` — Semgrep YAML rules are quick to author. Examples of additions worth considering:
- Banned domains in URL strings (e.g., reject `pastebin.com`, `requestbin.com`, `webhook.site`)
- Hardcoded JMA tenant IDs / subscription IDs (sign of prompt-leakage)
- Detection of imported packages outside an internal allowlist

## Limitations

- **Detection only, not blocking.** A malicious or vulnerable package gets installed before the scan runs. The hook surfaces the finding so the developer sees it; doesn't undo the install. For prevention, add a parallel `PreToolUse` allowlist hook.
- **Coverage gaps.** OSV.dev coverage of Homebrew is thinner than PyPI / npm / Go / NuGet. Many `brew install` packages will return clean even if their underlying components have CVEs at the binary level. Treat `brew` results as a floor, not a ceiling.
- **No transitive dep analysis.** Only the direct packages named on the command line are scanned. For full dep graph analysis, use `scan-now.sh dir <project>` against a manifest.
- **Network dependency.** Each install triggers an HTTPS call to `https://api.osv.dev`. Hook returns "scan failed" but exits 0 if offline.

## License

Same as savviety-skills repo.
