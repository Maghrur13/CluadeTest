# Financial Statement Analysis Tool

Extract balances from PDF financial statements, calculate liquidity/solvency/profitability ratios, and export to **Excel** or **Word**.

## Setup

```bash
cd financial_analysis
python -m pip install -r requirements.txt
```

## Offline OCR (for scanned/image PDFs)

Some PDFs (like scans) have **no selectable text**, so extraction will be blank unless OCR is enabled.

### 1) Install Tesseract OCR (Windows)

Install Tesseract OCR, then install language packs:
- **English**: `eng`
- **Azerbaijani**: `aze`

### 2) If Tesseract is not on PATH (recommended fix)

Set an environment variable so the script can find `tesseract.exe`:

```bat
setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Close and re-open Command Prompt after running `setx`.

### 3) Verify OCR works (optional)

```bat
python -c "import pytesseract; print('OK')"
```

## Usage

### Single PDF → Excel

```bash
python main.py path/to/statement.pdf
```

Output: `statement_analysis.xlsx` in the same folder.

### Single PDF → Excel + Word

```bash
python main.py path/to/statement.pdf --word
```

Example (AzerGold):

```bat
cd /d "C:\Users\User\Desktop\CluadeTest\financial_analysis"
python main.py "C:\Users\User\Desktop\CluadeTest\statements\2024-cü il hesabat.pdf" --word
```

### Multiple PDFs (folder) → Comparison Excel

```bash
python main.py path/to/pdf_folder/
```

Output: `multi_company_analysis.xlsx` with all companies' ratios side-by-side.

## Excel Output

- **Sheet 1 – Extracted Data**: Raw line items (current assets, total liabilities, net income, etc.)
- **Sheet 2 – Financial Analysis**: Ratios with short interpretations

### Using the Excel File

1. Open the `.xlsx` file in Excel.
2. Add your own formulas in new columns (e.g. year-over-year change).
3. Create charts from the ratio data.
4. Use **Data → From Table/Range** for PivotTables.
5. Copy sheets into other workbooks or reports.

## Customizing Line Item Labels

PDF formats differ. Edit `config.py` and add your statement’s labels:

```python
BALANCE_SHEET_ITEMS = {
    "current_assets": [
        "current assets", "total current assets", "your custom label"
    ],
    # ...
}
```

## Ratios Calculated

| Category    | Ratios                                                                 |
|------------|-----------------------------------------------------------------------|
| Liquidity  | Current Ratio, Quick Ratio, Cash Ratio                               |
| Solvency   | Debt-to-Equity, Debt-to-Assets, Interest Coverage                    |
| Profitability | Net Margin, ROA, ROE, Gross Margin, Operating Margin             |

## Limitations

- Works best with **digital PDFs** (not scanned images). For scanned PDFs, consider OCR preprocessing.
- Line item names must match (or be added to) `config.py`.
- Multi-year statements: the tool uses the **last numeric column** as the current period.
