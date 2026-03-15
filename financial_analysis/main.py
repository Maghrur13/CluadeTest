"""
Financial Statement Analysis - Main Entry Point

Reads PDF financial statements, extracts balances, calculates ratios,
and exports to Excel (and optionally Word).

Usage:
    python main.py path/to/statement.pdf
    python main.py path/to/folder/  # Process all PDFs in folder
"""

import sys
from pathlib import Path

from extract_pdf import extract_financial_data, extract_from_folder
from ratios import calculate_all_ratios
from export_excel import export_to_excel, export_multi_to_excel
from export_word import export_to_word


def analyze_single_pdf(
    pdf_path: Path,
    output_dir: Path | None = None,
    export_excel: bool = True,
    export_word: bool = False,
) -> list[Path]:
    """Analyze one PDF and save Excel (and optionally Word) report."""
    data = extract_financial_data(pdf_path)
    if "_error" in data:
        raise ValueError(data["_error"])

    ratios = calculate_all_ratios(data)
    out_dir = output_dir or pdf_path.parent
    name = pdf_path.stem
    outputs = []
    if export_excel:
        xlsx = out_dir / f"{name}_analysis.xlsx"
        export_to_excel(data, ratios, xlsx, company_name=name)
        outputs.append(xlsx)
    if export_word:
        docx = out_dir / f"{name}_analysis.docx"
        export_to_word(data, ratios, docx, company_name=name)
        outputs.append(docx)
    return outputs


def analyze_folder(folder_path: Path, output_path: Path | None = None) -> Path:
    """Analyze all PDFs in folder and create comparison Excel."""
    results = extract_from_folder(folder_path)
    companies_data = {}
    for name, data in results.items():
        if "_error" in data:
            print(f"  Skipping {name}: {data['_error']}")
            continue
        ratios = calculate_all_ratios(data)
        companies_data[name] = (data, ratios)

    if not companies_data:
        raise ValueError("No valid PDFs could be processed.")

    out = output_path or folder_path / "multi_company_analysis.xlsx"
    return export_multi_to_excel(companies_data, out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExamples:")
        print("  python main.py statement.pdf")
        print("  python main.py ./pdf_folder/")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: Path not found: {path}")
        sys.exit(1)

    export_word_flag = "--word" in sys.argv

    try:
        if path.is_file() and path.suffix.lower() == ".pdf":
            outs = analyze_single_pdf(path, export_word=export_word_flag)
            for o in outs:
                print(f"Report saved: {o}")
        elif path.is_dir():
            out = analyze_folder(path)
            print(f"Comparison report saved: {out}")
        else:
            print("Provide a .pdf file or a folder containing PDFs.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
