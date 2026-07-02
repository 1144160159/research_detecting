#!/usr/bin/env python3
"""
Verify PDF filenames match actual DOIs inside each paper.
Uses bytes-mode subprocess to avoid Windows encoding issues.
"""

import os
import re
import sys
import subprocess
import json
import shutil

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PAPER_DIR = "paper"
REPORT_FILE = "doi_verification_report.txt"

PDFTOTEXT = r"D:\soft\Git\mingw64\bin\pdftotext.exe"

def extract_text_bytes(filepath, pages=2):
    """Extract first N pages as bytes."""
    try:
        result = subprocess.run(
            [PDFTOTEXT, "-l", str(pages), filepath, "-"],
            capture_output=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass
    return b""

def extract_doi_from_bytes(data):
    """Extract DOI from PDF bytes content."""
    if not data:
        return None

    patterns = [
        rb'https?://doi\.org/(10\.[^/\s]+/[^\s\)\]<>]+)',
        rb'Digital Object Identifier\s+(10\.[^\s]+)',
        rb'[Dd][Oo][Ii]:\s*(10\.[^\s]+)',
        rb'doi:\s*(10\.[^\s]+)',
        rb'doi[./]\s*(10\.\d{4,}[^\s]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, data)
        if match:
            doi = match.group(1).decode('ascii', errors='replace')
            doi = doi.strip('.,;:)]}>"\'')
            if doi.endswith('.'):
                doi = doi[:-1]
            if doi.startswith('10.') and '/' in doi:
                return doi

    # Try arXiv pattern
    arxiv_match = re.search(rb'ar[xX]iv:(\d{4}\.\d{4,5})', data)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1).decode('ascii')
        return f"10.48550/arXiv.{arxiv_id}"

    return None

def filename_to_doi(filename):
    """PDF filename -> expected DOI."""
    name = filename.replace('.pdf', '')
    idx = name.find('_')
    if idx == -1:
        return name
    return name[:idx] + '/' + name[idx+1:]

def doi_to_filename(doi):
    """DOI -> expected PDF filename."""
    match = re.match(r'(10\.\d{4,})/(.+)', doi)
    if match:
        return match.group(1) + '_' + match.group(2) + '.pdf'
    return doi.replace('/', '_') + '.pdf'

def normalize_doi(doi):
    """Lowercase and strip URL prefix."""
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
    return doi

def main():
    if not os.path.exists(PDFTOTEXT):
        print(f"ERROR: pdftotext not found at {PDFTOTEXT}")
        return

    pdf_files = sorted([f for f in os.listdir(PAPER_DIR) if f.endswith('.pdf')])
    total = len(pdf_files)
    print(f"Verifying {total} PDF files with {PDFTOTEXT}\n")

    matched = []
    mismatched = []
    no_doi = []
    errors = []

    for i, filename in enumerate(pdf_files):
        filepath = os.path.join(PAPER_DIR, filename)
        expected_doi = normalize_doi(filename_to_doi(filename))

        try:
            data = extract_text_bytes(filepath, pages=2)
            found_doi = extract_doi_from_bytes(data)
        except Exception as e:
            errors.append((filename, str(e)))
            continue

        found_norm = normalize_doi(found_doi) if found_doi else None

        if found_norm and expected_doi:
            if found_norm == expected_doi:
                matched.append(filename)
            else:
                correct_name = doi_to_filename(found_doi)
                mismatched.append((filename, expected_doi, found_doi, correct_name))
        elif found_norm and not expected_doi:
            correct_name = doi_to_filename(found_doi)
            mismatched.append((filename, '(non-DOI filename)', found_doi, correct_name))
        else:
            no_doi.append(filename)

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{total}] ✓{len(matched)} ✗{len(mismatched)} ?{len(no_doi)}")

    # ===================== REPORT =====================
    lines = []
    lines.append("=" * 70)
    lines.append("DOI VERIFICATION REPORT")
    lines.append(f"Total PDFs: {total}")
    lines.append(f"Matched (✓): {len(matched)}")
    lines.append(f"Mismatched (✗): {len(mismatched)}")
    lines.append(f"No DOI found (?): {len(no_doi)}")
    lines.append(f"Errors: {len(errors)}")
    lines.append("=" * 70)
    lines.append("")

    if mismatched:
        lines.append(f"--- MISMATCHED ({len(mismatched)}) ---")
        lines.append("")
        for fn, exp, found, correct in mismatched:
            lines.append(f"  FILE:     {fn}")
            lines.append(f"  EXPECTED: {exp}")
            lines.append(f"  ACTUAL:   {found}")
            lines.append(f"  CORRECT:  {correct}")
            lines.append("")
    else:
        lines.append("✓ ALL DOIs MATCH!")
        lines.append("")

    if no_doi:
        lines.append(f"--- NO DOI FOUND IN PDF ({len(no_doi)}) ---")
        lines.append("(These may be scanned PDFs, standards, or non-standard formats)")
        lines.append("")
        for fn in no_doi:
            lines.append(f"  {fn}")
        lines.append("")

    if errors:
        lines.append(f"--- ERRORS ({len(errors)}) ---")
        for fn, e in errors:
            lines.append(f"  {fn}: {e}")
        lines.append("")

    report = '\n'.join(lines)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n{'='*70}")
    print(f"VERIFICATION COMPLETE")
    print(f"  Matched:    {len(matched)} ✓")
    print(f"  Mismatched: {len(mismatched)} ✗")
    print(f"  No DOI:     {len(no_doi)} ?")
    print(f"  Errors:     {len(errors)}")
    print(f"\n  Report: {REPORT_FILE}")

    if mismatched:
        print(f"\n⚠ MISMATCHES ({len(mismatched)}):")
        for fn, exp, found, correct in mismatched:
            print(f"  {fn}")
            print(f"    Expected: {exp}")
            print(f"    Actual:   {found}")
            print(f"    Correct filename: {correct}")
            print()

    # ===================== FIX =====================
    if mismatched:
        print("\n" + "=" * 70)
        print("RENAMING MISMATCHED FILES...")
        for fn, exp, found, correct in mismatched:
            old_path = os.path.join(PAPER_DIR, fn)
            new_path = os.path.join(PAPER_DIR, correct)
            if os.path.exists(new_path):
                print(f"  SKIP (target exists): {fn} -> {correct}")
            else:
                try:
                    shutil.move(old_path, new_path)
                    print(f"  RENAMED: {fn} -> {correct}")
                except Exception as e:
                    print(f"  ERROR: {fn} -> {correct}: {e}")

    return mismatched, no_doi, matched

if __name__ == '__main__':
    main()
