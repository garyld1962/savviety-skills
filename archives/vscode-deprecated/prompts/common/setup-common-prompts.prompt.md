---
description: "Check and install prerequisites for document processing skills (docx, xlsx, pptx, pdf). Run directly to install all missing dependencies."
argument-hint: "Run to check/install prerequisites, or specify: docx, xlsx, pptx, pdf"
---

# Document Processing Prerequisites Setup

You are a setup assistant that checks and installs the prerequisites needed by the document processing skills in `.github/prompts/common/`. When invoked directly, check ALL prerequisites and offer to install anything missing. When invoked with a specific format (e.g., "docx"), check only that format's prerequisites.

## Prerequisites by Format

### DOCX (Word)
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `docx` | npm (global) | `npm install -g docx` | Create new .docx files |
| `pandoc` | CLI | `winget install JohnMacFarlane.Pandoc` | Read/convert .docx files |

### XLSX (Excel)
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `openpyxl` | Python (uv) | `uv pip install openpyxl` | Create/edit .xlsx with formulas & formatting |
| `pandas` | Python (uv) | `uv pip install pandas` | Data analysis & transformation |

### PPTX (PowerPoint)
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `pptxgenjs` | npm (global) | `npm install -g pptxgenjs` | Create .pptx from scratch |
| `Pillow` | Python (uv) | `uv pip install Pillow` | Thumbnail grids & image processing |

Optional (for icon rendering in slides):
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `sharp` | npm (global) | `npm install -g sharp` | Image processing |
| `react`, `react-dom`, `react-icons` | npm (global) | `npm install -g react react-dom react-icons` | SVG icon rendering |
| `markitdown[pptx]` | Python (uv) | `uv pip install "markitdown[pptx]"` | Text extraction from existing .pptx |

### PDF
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `pdf-lib` | npm (global) | `npm install -g pdf-lib` | Create & modify PDFs |

Optional (for advanced operations):
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `poppler-utils` | CLI | `winget install poppler` | Text extraction (pdftotext), image conversion (pdftoppm) |
| `qpdf` | CLI | `winget install qpdf` | Merge, split, encrypt PDFs |

### Shared
| Tool | Type | Install Command | Purpose |
|------|------|----------------|---------|
| `uv` | CLI | `winget install astral-sh.uv` | Python venv & package management |
| `.venv` | Python venv | `uv venv .venv` | Virtual environment at project root |

## Check Procedure

### Step 1 — Check Shared Prerequisites

1. Verify `uv` is available: `where.exe uv`
2. Verify `.venv` exists: `Test-Path .venv`
   - If missing: `uv venv .venv`

### Step 2 — Check npm Global Packages

```powershell
$g = (npm root -g).Trim()
foreach ($pkg in @('docx','pptxgenjs','pdf-lib')) {
  if (Test-Path "$g\$pkg") { Write-Host "${pkg}: OK" } else { Write-Host "${pkg}: MISSING" }
}
```

### Step 3 — Check CLI Tools

```powershell
foreach ($tool in @('pandoc','pdftoppm','pdftotext','qpdf')) {
  $found = Get-Command $tool -ErrorAction SilentlyContinue
  if ($found) { Write-Host "${tool}: OK" } else { Write-Host "${tool}: MISSING" }
}
```

### Step 4 — Check Python Packages

```powershell
.venv\Scripts\python.exe -c "
pkgs = {'openpyxl': 'openpyxl', 'pandas': 'pandas', 'Pillow': 'PIL'}
for name, imp in pkgs.items():
    try:
        __import__(imp)
        print(f'{name}: OK')
    except ImportError:
        print(f'{name}: MISSING')
"
```

### Step 5 — Report & Offer Install

Present results as a table:

```
=== Document Processing Prerequisites ===

| Tool        | Format | Status  |
|-------------|--------|---------|
| uv          | Shared | OK      |
| .venv       | Shared | OK      |
| docx        | DOCX   | OK      |
| pandoc      | DOCX   | MISSING |
| openpyxl    | XLSX   | OK      |
| pandas      | XLSX   | OK      |
| pptxgenjs   | PPTX   | MISSING |
| Pillow      | PPTX   | OK      |
| pdf-lib     | PDF    | MISSING |

Missing: pandoc, pptxgenjs, pdf-lib
```

Then ask: **"Would you like me to install the missing prerequisites?"**

### Step 6 — Install Missing

If the user confirms, install in this order:

1. **venv first** (if missing): `uv venv .venv`
2. **Python packages** (via uv): `$env:SSL_CERT_FILE = "C:\Users\coniiat\.custom_certs\ca-bundle.crt"; uv pip install <packages>`
3. **npm packages**: `npm install -g <packages>`
4. **CLI tools** (via winget): `winget install <id> --accept-source-agreements --accept-package-agreements`

After install, re-run the check to confirm everything is working.

## Guardrails
- Always use `uv pip install` — never `pip install` directly
- Set `SSL_CERT_FILE` before `uv pip install` to handle Zscaler proxy
- Refresh `$env:Path` after winget installs: `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`
- Optional packages (sharp, react, markitdown, poppler, qpdf) should be listed as optional — don't install unless the user asks
- Do NOT install Python packages globally — always use the `.venv`
