---
name: fin-extract
description: Extracts financial tables from large PDF reports (FIBRA quarterly/annual, 50-150 pages) with exact decimal precision. Scans the full document, identifies financial table pages, extracts targeted tables to CSV, and cross-validates numbers. Use when you need to pull financial data from PDFs for Excel models.
user-invocable: true
---

# Financial Table Extractor

Extracts financial tables from large PDF reports with exact decimal precision for use in Excel models. Built for Mexican FIBRA quarterly/annual reports (bilingual English/Spanish) but works on any financial PDF.

## When This Skill Is Invoked

User runs: `/fin-extract path/to/report.pdf`

Or Claude identifies a need to extract financial data from a PDF that's too large for the context window.

## Scripts

All scripts live in `~/.claude/skills/fin-extract/scripts/`:

- `scan_pdf.py` — Phase 1: lightweight page mapper (outputs JSON)
- `extract_tables.py` — Phase 2: precision table extraction (outputs CSV)
- `extract_text.py` — Phase 3: text extraction for cross-validation (outputs JSON)
- `batch_extract.py` — Batch pipeline: scan → select pages → extract → classify for all PDFs in a directory
- `build_workbook.py` — Aggregate all extracted CSVs into a multi-tab Excel workbook

## Workflow

### Step 0: Parse Arguments

The user provides a PDF path after `/fin-extract`. If no path is given, ask for one. Resolve relative paths against the current working directory.

### Step 1: Dependency Check

```bash
python -c "import pdfplumber" 2>/dev/null || pip install pdfplumber
```

If pip install fails, tell the user to install it manually.

### Step 2: Scan the Document

```bash
python ~/.claude/skills/fin-extract/scripts/scan_pdf.py "<pdf_path>"
```

This outputs JSON to stdout with per-page metadata: table count, text preview, and detected financial keywords. Progress goes to stderr. The JSON is small enough (~30KB for 150 pages) to fit in context.

Read the scan output and identify:
- Pages with `tables > 0` AND financial keywords
- Clusters of consecutive financial pages (likely multi-page financial statements)
- Page previews that suggest income statements, balance sheets, cash flow statements

### Step 3: Present Findings and Ask User

Show the user a summary like:

```
Found 142 pages. 23 pages have financial content:

Income Statement (Estado de Resultados):
  Pages 45-47 — revenue, operating expenses, net income, EBITDA

Balance Sheet (Estado de Posición Financiera):
  Pages 52-54 — total assets, total liabilities, equity

Cash Flow (Flujo de Efectivo):
  Pages 58-59 — cash flow

NOI / Property Metrics:
  Pages 72-75 — NOI, occupancy, GLA

Which pages should I extract? (all / specific pages / let me pick)
```

Group pages by detected statement type. Use financial keywords and previews to classify. If unsure, show the raw page list.

### Step 4: Extract Tables

Create an output directory next to the source PDF:

```bash
mkdir -p "<pdf_dir>/<pdf_stem>_tables/"
python ~/.claude/skills/fin-extract/scripts/extract_tables.py "<pdf_path>" "<pdf_dir>/<pdf_stem>_tables/" "<page_numbers>"
```

The script outputs:
- One CSV per detected table: `page_N_table_M.csv`
- `_metadata.json` with extraction details, detected number format, scale, currency, and row-total validation results

### Step 5: Cross-Validate

```bash
python ~/.claude/skills/fin-extract/scripts/extract_text.py "<pdf_path>" "<page_numbers>"
```

Compare numbers from the text extraction against the CSV tables. Report any discrepancies. Focus on:
- Total/subtotal rows (most likely to have validation data)
- Header row labels (confirm they match between methods)
- Number of data rows (should be consistent)

### Step 6: Read and Rename CSVs

After extraction, read each CSV's first few rows to identify what statement it contains. Rename or note each table with a human-readable name:
- `income_statement_3Q25.csv` instead of `page_25_table_1.csv`
- `balance_sheet_3Q25.csv` instead of `page_26_table_1.csv`
- `noi_ebitda_3Q25.csv`, `ffo_affo_3Q25.csv`, `cash_flow_3Q25.csv`, `key_indicators_3Q25.csv`

Use the header rows and the report's filename (e.g., `3Q25.pdf`) to determine the statement type and period.

### Step 7: Deliver Results

Present a summary:
- Number of tables extracted, with human-readable names
- Validation results (how many row totals checked out)
- Detected scale (e.g., "thousands of pesos") and currency
- Path to output directory with CSV files

Offer next steps:
- "Want me to combine these into an Excel workbook with tabs per statement?"
- "Want me to build a time-series workbook across multiple quarters?"
- "Want me to read specific values from these tables?"

### Step 8 (Optional): Build Excel Workbook

When the user wants an Excel workbook (single report or multi-quarter aggregate):

```python
import openpyxl
import pandas as pd

wb = openpyxl.Workbook()
# For each CSV, read as strings and write to a named tab
for csv_path, tab_name in tables:
    df = pd.read_csv(csv_path, dtype=str, header=None)
    ws = wb.create_sheet(title=tab_name)
    for row in df.itertuples(index=False):
        ws.append(list(row))

wb.remove(wb["Sheet"])  # remove default sheet
wb.save("output.xlsx")
```

For multi-quarter aggregation:
- Each statement type gets its own tab (e.g., "Income Statement")
- Quarters are stacked vertically with a blank row separator and period header
- Or quarters go in columns for time-series comparison — ask the user which layout they prefer

## Important Rules

### Presentation PDF Handling
The extraction script automatically handles presentation-style PDFs (investor decks exported from PowerPoint). These contain:
- **RGB color columns**: Decorative sidebars produce columns of small integers (0-255) that are color values, not data. The script auto-detects and strips these leading columns.
- **Split text labels**: Narrow column widths cause labels to split across cells (e.g., `"N"` | `"OI Margin"`). The script auto-merges single-letter fragments and word-wrap splits.
- **Narrative bullets**: Bullet-point commentary (`▪`, `•`) mixed into table areas is filtered out as footnotes.
- **Spacer rows**: Empty rows used for visual spacing are dropped.

After extraction, always spot-check the first few rows of the CSV to verify the label column reads correctly. Some labels may have missing spaces (e.g., `"ConsolidatedFFO"` instead of `"Consolidated FFO"`) — this reflects how the text is encoded in the PDF and is cosmetic, not a data error.

### Number Precision
- NEVER convert financial numbers to Python floats. The CSV files contain string-typed numbers.
- When reading CSVs back, use `pandas.read_csv(path, dtype=str)` to prevent float conversion.
- If the user asks to combine into Excel, use openpyxl and write values as strings or use Decimal.

### Row-Total Validation
The script's validation checks whether the last numeric column in each row equals the sum of all other numeric columns. For financial statements with period columns (3Q25, 3Q24, YTD), this validation mostly applies to YTD = sum of quarterly figures. Mismatches on other rows (e.g., where columns represent different periods, not additive components) are expected and not errors.

### Scale
- The scripts detect scale indicators ("millones de pesos", "in thousands") but do NOT auto-scale the numbers.
- Always tell the user the detected scale so they know the unit.
- Let the user decide whether to scale — never multiply numbers silently.

### Multi-Page Tables
- If consecutive pages have tables with matching column counts, they may be one table split across pages.
- After extraction, check if merging makes sense (same headers, sequential row labels).
- Offer to merge if detected, but don't do it automatically.

### Error Handling
- If scan finds zero financial pages: suggest the PDF may be image-based (scanned) and recommend OCR.
- If table extraction returns empty: try the text extraction path instead and parse numbers from layout-preserved text.
- If the PDF is password-protected: the scan will report this clearly. Ask the user for the password or an unlocked copy.

## Example Session (FIBRA Soma Quarterly Report)

```
User: /fin-extract ~/OneDrive/Documents/emlc/fibrasoma_reports/3Q25.pdf

Claude: Let me check dependencies and scan the document.
[runs dependency check]
[runs scan_pdf.py]

Found 46 pages. Key financial content:

Key Financial Indicators (p11): 8 tables — revenue, income, EBITDA, NOI, FFO, AFFO, CBFIs
NOI & EBITDA Breakdown (p15): 5 tables — revenue, income, EBITDA, NOI, operating expenses
FFO/AFFO Reconciliation (p16): 7 tables — income, amortization, FFO, AFFO, CBFIs
Credit Profile (p17-18): 8+4 tables — debt, EBITDA, total assets, LTV, leverage
Income Statement (p25): 7 tables — revenue, income, operating expenses, net income, interest, fair value
Balance Sheet (p26): 2 tables — total assets, total liabilities, investment properties
Cash Flow (p27): 8 tables — cash flow, equity, net income, interest, debt, fair value

Which pages should I extract?

User: Income statement and balance sheet

Claude: Extracting pages 25-27...
[runs extract_tables.py — auto-strips presentation color columns, merges split labels]
[runs extract_text.py for cross-validation]

Extracted 3 tables:
  page_25_table_1.csv — 33 rows × 5 cols (Income Statement: ThousandPesos, 3Q25, 3Q24, 2025 YTD)
  page_26_table_1.csv — 38 rows × 5 cols (Balance Sheet)
  page_27_table_1.csv — 47 rows × 5 cols (Cash Flow)

Number format: English (1,234.56)
Scale: thousands (ThousandPesos)
Currency: MXN

Note: some labels have missing spaces (e.g., "Rentalincome") — this is how the text
is encoded in the presentation PDF, not a data error. Numbers are accurate.

Files saved to: ~/OneDrive/Documents/emlc/fibrasoma_reports/3Q25_tables/

Want me to combine these into an Excel workbook?
```

## Batch Processing Multiple Reports

Two scripts automate multi-report extraction and aggregation.

### `batch_extract.py`

Processes all PDFs in a directory through the full pipeline: scan → page selection → table extraction → statement classification and renaming.

```bash
python ~/.claude/skills/fin-extract/scripts/batch_extract.py <pdf_directory> [--output-dir <dir>]
```

- PDFs must be named with a period prefix like `3Q25.pdf` — the period is derived from the filename
- For each PDF, scans pages, selects those with 2+ financial keywords and at least one table (capped at 15 pages), extracts tables, then classifies CSVs by statement type using regex matching on headers
- Output per PDF: `<period>_tables/` directory containing named CSVs (`income_statement_3Q25.csv`, `balance_sheet_3Q25.csv`, etc.) plus `_metadata.json`
- Duplicates get `_2`, `_3` suffixes (e.g., `noi_ebitda_2_3Q25.csv`) — these are secondary tables on the same topic, usually breakdowns or supporting detail
- Unclassified tables keep their `page_N_table_M` names
- Outputs JSON summary to stdout; progress and diagnostics go to stderr
- Uses `sys.stdout.buffer.write()` for JSON output to avoid Windows cp1252 encoding errors

Statement types detected: `income_statement`, `balance_sheet`, `cash_flow`, `noi_ebitda`, `ffo_affo`, `key_indicators`, `credit_profile`.

### `build_workbook.py`

Reads all `*_tables/` directories and creates a single Excel workbook with one tab per statement type.

```bash
python ~/.claude/skills/fin-extract/scripts/build_workbook.py <tables_parent_dir> [--output <path.xlsx>]
```

- Default output: `fibrasoma_aggregate.xlsx` in the parent directory
- By default, includes only the 7 primary statement types (skips duplicates and unclassified pages). Pass `--all` to include everything.
- Quarters are stacked vertically within each tab, sorted chronologically (1Q21 → 3Q25), separated by blue period header rows
- Formatting: bold column headers, blue merged period header rows with white text, auto-width columns, frozen panes at row 3

### Typical batch workflow

```bash
# Extract all 19 quarterly PDFs
python ~/.claude/skills/fin-extract/scripts/batch_extract.py ~/fibrasoma_reports/

# Build aggregate workbook (primary statement types only)
python ~/.claude/skills/fin-extract/scripts/build_workbook.py ~/fibrasoma_reports/

# Build workbook including all tables
python ~/.claude/skills/fin-extract/scripts/build_workbook.py ~/fibrasoma_reports/ --all
```

### Windows notes

- All subprocess calls use `encoding="utf-8", errors="replace"` to handle non-ASCII chars from pdfplumber
- File renames use explicit delete-then-rename (`safe_rename`) because `Path.rename()` doesn't overwrite on Windows
- Page numbers vary between quarters as report formats evolve — the scanner handles this automatically
