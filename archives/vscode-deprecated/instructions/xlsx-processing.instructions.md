---
applyTo: "**"
description: "Excel/spreadsheet (.xlsx, .xlsm, .csv, .tsv) creation, editing, analysis, formulas, formatting, financial models"
---

# Excel/Spreadsheet Processing

> **Prerequisites:** This skill requires `openpyxl` and `pandas` (Python/uv). Run `/setup-common-prompts` to check and install missing dependencies.

Use these instructions when working with spreadsheet files (.xlsx, .xlsm, .csv, .tsv) — creating, reading, editing, fixing, formatting, charting, cleaning data, or converting between formats. The deliverable must be a spreadsheet file. Do NOT use for Word documents, HTML reports, or database pipelines.

## Requirements for Outputs

### All Excel Files

- **Professional Font**: Use Arial or Times New Roman unless otherwise instructed
- **Zero Formula Errors**: Every Excel file MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- **Preserve Existing Templates**: When updating templates, EXACTLY match existing format, style, and conventions. Existing template conventions ALWAYS override these guidelines

### Financial Models

#### Color Coding Standards (unless overridden by existing template)

| Color | Usage |
|-------|-------|
| **Blue text** (0,0,255) | Hardcoded inputs, scenario-changeable numbers |
| **Black text** (0,0,0) | ALL formulas and calculations |
| **Green text** (0,128,0) | Links from other worksheets in same workbook |
| **Red text** (255,0,0) | External links to other files |
| **Yellow background** (255,255,0) | Key assumptions needing attention |

#### Number Formatting Standards

- **Years**: Format as text strings ("2024" not "2,024")
- **Currency**: Use $#,##0; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Format all zeros as "-" including percentages ($#,##0;($#,##0);-)
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

#### Formula Rules

- Place ALL assumptions in separate cells, use cell references (not hardcoded values)
- Use `=B5*(1+$B$6)` instead of `=B5*1.05`
- Document hardcodes: "Source: [System/Document], [Date], [Reference], [URL]"

---

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.** The spreadsheet must remain dynamic and updateable.

```python
# WRONG - Hardcoding calculated values
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000

# CORRECT - Using Excel formulas
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to ALL calculations — totals, percentages, ratios, differences, etc.

---

## Reading and Analyzing Data

### With pandas

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                           # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
df.head()       # Preview
df.info()       # Column info
df.describe()   # Statistics
df.to_excel('output.xlsx', index=False)
```

---

## Common Workflow

1. **Choose tool**: pandas for data analysis, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**:
   ```bash
   python scripts/recalc.py output.xlsx
   ```
6. **Verify and fix errors**: Check `error_summary` in JSON output, fix, and recalculate again

### Creating New Excel Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])
sheet['B2'] = '=SUM(A1:A10)'

sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### Editing Existing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']

for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]

sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)

new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

---

## Recalculating Formulas

Excel files created/modified by openpyxl contain formulas as strings but not calculated values. Use the recalc script:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors
- Returns JSON with detailed error locations and counts

### Interpreting Output

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

---

## Formula Verification Checklist

### Essential Verification
- Test 2-3 sample references before building full model
- Confirm Excel columns match (column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

### Common Pitfalls
- Handle NaN with `pd.notna()`
- FY data often in columns 50+
- Search all occurrences, not just first
- Check denominators before division formulas (#DIV/0!)
- Verify all cell references point to intended cells (#REF!)
- Cross-sheet references: use `Sheet1!A1` format

### Formula Testing Strategy
- Start small: test on 2-3 cells before applying broadly
- Verify all referenced cells exist
- Test edge cases: zero, negative, and very large values

---

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- `data_only=True` reads calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently replaced with values
- Large files: `read_only=True` for reading, `write_only=True` for writing

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

### Code Style
- Write minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- For Excel files: add comments to cells with complex formulas, document data sources
