"""
Extract financial data from PDF statements.
Handles both table-based and text-based PDF layouts.
"""

import re
import unicodedata
import os
import pdfplumber
from pathlib import Path
from config import BALANCE_SHEET_ITEMS, INCOME_STATEMENT_ITEMS


_AZ_TRANSLATION = str.maketrans(
    {
        "ə": "e",
        "ı": "i",
        "ş": "s",
        "ç": "c",
        "ö": "o",
        "ü": "u",
        "ğ": "g",
        "Ə": "e",
        "I": "i",
        "Ş": "s",
        "Ç": "c",
        "Ö": "o",
        "Ü": "u",
        "Ğ": "g",
    }
)


def _norm_text(s: str) -> str:
    """
    Normalize text for robust matching across English/Azerbaijani/OCR artifacts.
    - lowercases
    - removes diacritics (unicode)
    - maps Azerbaijani-specific letters to latin approximations
    - removes punctuation / extra whitespace
    """
    if s is None:
        return ""
    s = str(s)
    s = s.translate(_AZ_TRANSLATION)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    # Keep letters/numbers/spaces only
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _configure_tesseract(pytesseract_module) -> None:
    """
    Configure Tesseract path on Windows if it's not on PATH.
    You can also set an explicit path using environment variable:
      TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    """
    explicit = os.environ.get("TESSERACT_CMD")
    if explicit and Path(explicit).exists():
        pytesseract_module.pytesseract.tesseract_cmd = explicit
        return

    # Common Windows install locations
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / r"AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for c in candidates:
        if Path(c).exists():
            pytesseract_module.pytesseract.tesseract_cmd = c
            return


def _parse_number(s: str) -> float | None:
    """Parse number from string, handling (1,234.56) and 1,234.56 formats."""
    if s is None:
        return None
    # pdfplumber sometimes returns numeric cells as int/float already
    if isinstance(s, (int, float)):
        return float(s)
    if not isinstance(s, str):
        return None
    s = str(s).strip()
    s = s.replace("\u00a0", " ").replace("\u202f", " ")  # NBSP / narrow NBSP
    s = s.replace(" ", "")
    # Handle parentheses for negative numbers
    if re.match(r"^\s*\([^)]+\)\s*$", s):
        s = "-" + s.replace("(", "").replace(")", "")
    # Handle curly braces sometimes used instead of parentheses
    if re.match(r"^\s*\{[^}]+\}\s*$", s):
        s = "-" + s.replace("{", "").replace("}", "")
    # If comma appears to be decimal separator (e.g. 1234,56), convert to dot.
    if "," in s and "." not in s:
        if re.search(r",\d{1,2}$", s):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        s = s.replace(",", "")
    try:
        return float(re.sub(r"[^\d.\-]", "", s))
    except ValueError:
        return None


def _collect_numbers_from_row(row: list, col_idx: int = -1) -> list[float]:
    """Extract numeric values from a table row (often last column = current period)."""
    nums = []
    for i, cell in enumerate(row):
        if col_idx >= 0 and i != col_idx:
            continue
        val = _parse_number(cell)
        if val is not None:
            nums.append(val)
    # Heuristic: many statements have a small "Note" number column (e.g., 9, 11, 23)
    # plus 1-2 large amount columns. If we see both small and large values,
    # drop the small ones.
    if len(nums) >= 2:
        abs_nums = [abs(x) for x in nums]
        max_abs = max(abs_nums)
        if max_abs >= 10_000:  # amounts are usually larger than this in statements
            nums = [n for n in nums if abs(n) >= 1_000]
    return nums


def _label_match(normalized_row_label: str, normalized_query: str) -> bool:
    """
    Token-based matching to avoid false positives like matching 'assets' inside 'intangible assets'.
    Requires all query tokens to be present in the row label.
    """
    if not normalized_row_label or not normalized_query:
        return False
    row_tokens = set(normalized_row_label.split())
    q_tokens = [t for t in normalized_query.split() if t]
    return all(t in row_tokens for t in q_tokens)


def _label_score(normalized_row_label: str, normalized_query: str) -> int:
    """
    Score match quality so we can prefer exact totals over subtotals like
    'total non-current assets' vs 'total assets'.
    """
    if not normalized_row_label or not normalized_query:
        return 0
    if normalized_row_label == normalized_query:
        return 3
    if normalized_row_label.endswith(normalized_query):
        return 2
    if _label_match(normalized_row_label, normalized_query):
        return 1
    return 0


def _find_value_for_label(tables: list, label_mappings: dict) -> dict[str, float]:
    """Search tables for rows matching label mappings and extract values."""
    result = {}
    best_scores: dict[str, int] = {}
    for table in tables:
        for row in table:
            if not row or len(row) < 2:
                continue
            # Some PDFs have label in col 0 or 1; join first two cells for robustness.
            label_text = " ".join(str(c) for c in row[:2] if c)
            label_cell = _norm_text(label_text)
            for key, labels in label_mappings.items():
                for lbl in labels:
                    nlbl = _norm_text(lbl)
                    if not nlbl:
                        continue
                    score = _label_score(label_cell, nlbl)
                    if score <= 0:
                        continue
                    prev = best_scores.get(key, 0)
                    if score < prev:
                        continue
                    nums = _collect_numbers_from_row(row)
                    if nums:
                        # Most statements list current year first (left-to-right): 2024 then 2023.
                        # After dropping note numbers, prefer the first amount.
                        result[key] = nums[0]
                        best_scores[key] = score
                        break
    return result


def _extract_from_text(text: str, label_mappings: dict) -> dict[str, float]:
    """Fallback: extract values from raw text using regex patterns."""
    result = {}
    lines = text.split("\n")
    for line in lines:
        nline = _norm_text(line)
        for key, labels in label_mappings.items():
            if key in result:
                continue
            for lbl in labels:
                nlbl = _norm_text(lbl)
                if nlbl and _label_match(nline, nlbl):
                    # Extract all numeric-looking chunks from the line.
                    # Many financial statement lines look like:
                    #   Label [Note] 2024_amount 2023_amount
                    # We:
                    # - parse all numbers
                    # - drop small note numbers when big amounts exist
                    # - then take the last two amounts and pick the first (current year)
                    raw_chunks = re.findall(r"[\(\{]?-?[\d\s.,!]+[\)\}]?", line)
                    parsed = []
                    for ch in raw_chunks:
                        val = _parse_number(ch)
                        if val is None:
                            continue
                        if abs(val) >= 1e15:
                            continue
                        parsed.append(val)

                    if not parsed:
                        break

                    # Reuse row-style filtering for note numbers
                    filtered = _collect_numbers_from_row(parsed)
                    if len(filtered) >= 2:
                        last_two = filtered[-2:]
                        result[key] = last_two[0]  # current year column (usually first of the last two)
                    else:
                        result[key] = filtered[0]
                    break
    return result


def extract_financial_data(pdf_path: str | Path) -> dict[str, float]:
    """
    Extract balance sheet and income statement figures from a PDF.
    Returns a dict like: current_assets, total_assets, net_income, etc.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    all_tables = []
    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)
            text = page.extract_text()
            if text:
                all_text.append(text)

    full_text = "\n".join(all_text)
    merged = {**BALANCE_SHEET_ITEMS, **INCOME_STATEMENT_ITEMS}

    # If PDF is scanned/image-only, text can be empty -> OCR fallback
    if not all_tables and not full_text.strip():
        try:
            import pytesseract  # type: ignore
            import pypdfium2 as pdfium  # type: ignore
        except Exception:
            return {
                "_error": (
                    "This PDF appears to be scanned (no selectable text). "
                    "Install OCR dependencies: `python -m pip install pytesseract pypdfium2` "
                    "and install Tesseract OCR (Windows). Then re-run."
                )
            }

        try:
            _configure_tesseract(pytesseract)
            pdf = pdfium.PdfDocument(str(pdf_path))
            ocr_pages = []
            for i in range(len(pdf)):
                page = pdf[i]
                bitmap = page.render(scale=2.5)  # higher = better OCR, slower
                pil_img = bitmap.to_pil()
                # Requires Tesseract language packs: aze + eng
                ocr_text = pytesseract.image_to_string(pil_img, lang="aze+eng")
                if ocr_text:
                    ocr_pages.append(ocr_text)
            full_text = "\n".join(ocr_pages)
        except Exception as e:
            return {
                "_error": (
                    "OCR failed. Make sure Tesseract is installed and available. "
                    "If Tesseract is installed but not on PATH, set TESSERACT_CMD env var. "
                    f"Details: {e}"
                )
            }

    # Prefer table extraction
    data = _find_value_for_label(all_tables, merged)

    # Fill gaps from text
    for key, labels in merged.items():
        if key not in data:
            text_data = _extract_from_text(full_text, {key: labels})
            if key in text_data:
                data[key] = text_data[key]

    return data


def extract_from_folder(folder: str | Path, pattern: str = "*.pdf") -> dict[str, dict]:
    """Extract from all PDFs in a folder. Returns {filename: {line_item: value}}."""
    folder = Path(folder)
    results = {}
    used_names: dict[str, int] = {}
    for f in folder.glob(pattern):
        try:
            name = f.stem.strip()
            # Make names less ambiguous for Excel headers (avoid huge titles / duplicates)
            name = re.sub(r"\s+", " ", name)
            if len(name) > 45:
                name = name[:42].rstrip() + "..."
            if name in used_names:
                used_names[name] += 1
                name = f"{name} ({used_names[name]})"
            else:
                used_names[name] = 1
            results[name] = extract_financial_data(f)
        except Exception as e:
            results[f.stem] = {"_error": str(e)}
    return results
