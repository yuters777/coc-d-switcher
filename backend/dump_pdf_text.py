#!/usr/bin/env python3
"""
Dump raw text from PDF to understand structure
"""
import sys
import pdfplumber
from pathlib import Path

def dump_pdf_text(pdf_path: str):
    """Dump all text from PDF for analysis"""

    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return

    print("=" * 80)
    print(f"PDF TEXT DUMP: {Path(pdf_path).name}")
    print("=" * 80)

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"\n{'='*80}")
            print(f"PAGE {i+1}")
            print(f"{'='*80}")
            text = page.extract_text()
            print(text)
            print(f"\n{'='*80}")
            print(f"CHARACTER COUNT: {len(text)}")
            print(f"LINE COUNT: {len(text.splitlines())}")
            print(f"{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dump_pdf_text.py <pdf_path>")
        sys.exit(1)

    dump_pdf_text(sys.argv[1])
