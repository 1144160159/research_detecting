#!/usr/bin/env python3
"""
Comprehensive DOI verification and fix script.
- Extracts DOI from PDFs (improved: 5 pages, better patterns)
- Renames files to match actual DOI
- Handles duplicates, edge cases
- Updates papers_metadata.json
- Regenerates 文献.md

DOES NOT modify PDF file contents — only renames files.
"""

import os
import re
import sys
import json
import shutil
import subprocess
import html
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PAPER_DIR = "paper"
METADATA_FILE = "papers_metadata.json"
OUTPUT_MD = "文献.md"
PDFTOTEXT = r"D:\soft\Git\mingw64\bin\pdftotext.exe"
CROSSREF_URL = "https://api.crossref.org/works/{doi}"
HEADERS = {"User-Agent": "CitationGen/1.0 (mailto:research@example.com)"}


# ============================================================
# KNOWN FIXES (verified by web search)
# ============================================================
# Maps OLD filename -> NEW filename (None = delete duplicate)
KNOWN_FIXES = {
    # Garbled extraction: actual DOI is 10.1109/TCE.2026.3697692
    "10.1109_TCE.2025.[Your.pdf": "10.1109_TCE.2026.3697692.pdf",

    # Research Square preprint with version number
    "10.1038_s41598-025-01084-1.pdf": "10.21203_rs.3.rs-6201348_v1.pdf",

    # Zenodo code repo -> should use paper DOI (NDSS 2026)
    "10.5281_zenodo.17759516.pdf": "10.14722_ndss.2026.243241.pdf",

    # Duplicates: both have same internal DOI, keep the one with correct name
    # The old file is a duplicate from a different source
    "10.1093_oxfordhb_9780199314201.013.45.pdf": "10.1109_TDSC.2025.3621434_dup.pdf",
    "10.3403_30132534.pdf": "10.1109_TIFS.2026.3653575_dup.pdf",
}

# ============================================================
# DOI OVERRIDES (filename -> correct DOI)
# Used when PDF extraction may return wrong DOI (e.g., data repo vs paper DOI)
# ============================================================
DOI_OVERRIDES = {
    # TIPSO-GAN: PDF has both Zenodo code DOI and NDSS paper DOI.
    # Paper DOI takes precedence.
    "10.14722_ndss.2026.243241.pdf": "10.14722/ndss.2026.243241",

    # Garbled PDF: the internal DOI was a placeholder "[Your DOI Number]"
    # Real DOI confirmed by web search
    "10.1109_TCE.2026.3697692.pdf": "10.1109/TCE.2026.3697692",

    # Research Square preprint
    "10.21203_rs.3.rs-6201348_v1.pdf": "10.21203/rs.3.rs-6201348/v1",
}


# ============================================================
# DOI EXTRACTION
# ============================================================

def extract_text_bytes(filepath, pages=5):
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

def extract_text_bytes_range(filepath, first_page, last_page):
    """Extract pages from first_page to last_page as bytes."""
    try:
        result = subprocess.run(
            [PDFTOTEXT, "-f", str(first_page), "-l", str(last_page), filepath, "-"],
            capture_output=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass
    return b""

def is_valid_doi(doi):
    """Validate that a DOI looks complete and real."""
    if not doi:
        return False
    if not doi.startswith('10.'):
        return False
    if '/' not in doi:
        return False
    # Must have a suffix after the last /
    parts = doi.split('/')
    if len(parts) < 2:
        return False
    suffix = parts[-1]
    # Suffix must be at least 4 characters (not empty or just a space)
    if len(suffix.strip()) < 4:
        return False
    # Filter garbage
    if '[Your' in doi or '[your' in doi:
        return False
    # Filter incomplete DOIs that end with just a slash
    if doi.endswith('/'):
        return False
    return True

def extract_doi_from_bytes(data):
    """Extract DOI from PDF bytes content with improved patterns.
    Only returns the FIRST valid DOI found (assuming it's the paper's own DOI).
    """
    if not data:
        return None

    # Ordered by reliability - most specific/reliable patterns first
    patterns = [
        # "Digital Object Identifier 10.XXX/YYY" - most reliable
        rb'Digital\s+Object\s+Identifier\s+(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # "DOI. No. 10.XXX/YYY"
        rb'DOI\.\s*No\.\s*(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # "Citation information: DOI 10.XXX/YYY" (IEEE author preprint style)
        # Must come BEFORE generic "DOI:" to ensure primary journal DOI is found
        rb'Citation\s+information:\s*DOI\s+(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # "DOI: 10.XXX/YYY" (with colon)
        rb'DOI:\s*(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # "doi: 10.XXX/YYY" (lowercase with colon)
        rb'doi:\s*(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # "DOI. No. 10.XXX/YYY" (period + No., no colon)
        rb'DOI\.\s*No\.\s*(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # "DOI 10.XXX/YYY" (no colon, space-separated) - less reliable, try later
        rb'DOI\s+(10\.\d{4,}/[^\s\)\]<>\"\']+)',
        # Standard DOI URL (https://doi.org/10.XXX/YYY)
        rb'https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s\)\]<>\"\']+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, data)
        for match in matches:
            doi = match.decode('ascii', errors='replace').strip()
            # Clean up trailing punctuation
            doi = doi.rstrip('.,;:)]}>\"\'')
            if doi.endswith('.'):
                doi = doi[:-1]
            if is_valid_doi(doi):
                doi = re.sub(r'/+', '/', doi)  # Fix double slashes
                return doi

    return None

def extract_paper_doi(filepath):
    """Extract the paper's own DOI, trying progressively larger page ranges.
    Uses safe patterns that avoid bibliography DOIs."""

    # Try first 2 pages (where paper DOI usually is)
    data = extract_text_bytes_range(filepath, 1, 2)
    doi = extract_doi_from_bytes(data)
    if doi:
        return doi

    # Try page 1 only
    data = extract_text_bytes_range(filepath, 1, 1)
    doi = extract_doi_from_bytes(data)
    if doi:
        return doi

    # Try first 3 pages
    data = extract_text_bytes(filepath, pages=3)
    doi = extract_doi_from_bytes(data)
    if doi:
        return doi

    # Try first 5 pages as last resort
    data = extract_text_bytes(filepath, pages=5)
    doi = extract_doi_from_bytes(data)
    if doi:
        return doi

    # Try arXiv ID
    try:
        data = extract_text_bytes(filepath, pages=3)
    except Exception:
        data = b""
    arxiv_match = re.search(rb'ar[xX]iv:(\d{4}\.\d{4,5})', data)
    if arxiv_match:
        return f"10.48550/arXiv.{arxiv_match.group(1).decode('ascii')}"

    return None


# ============================================================
# FILENAME <-> DOI CONVERSION
# ============================================================

def filename_to_doi(filename):
    """PDF filename -> DOI (replace first _ with /)."""
    name = filename.replace('.pdf', '')
    idx = name.find('_')
    if idx == -1:
        return name
    return name[:idx] + '/' + name[idx+1:]

def doi_to_filename(doi):
    """DOI -> safe PDF filename, handling version suffixes like /v1."""
    # Handle version suffixes: 10.21203/rs.3.rs-6201348/v1 -> 10.21203_rs.3.rs-6201348_v1.pdf
    # Replace / with _ but keep the structure
    parts = doi.split('/')
    # First part (registrant) + underscore + rest joined by underscores
    if len(parts) >= 2:
        # Format: 10.REGISTRANT_SUFFIX_PARTS.pdf
        return parts[0] + '_' + '_'.join(parts[1:]) + '.pdf'
    return doi.replace('/', '_') + '.pdf'

def normalize_doi(doi):
    """Lowercase and strip URL prefix."""
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
    doi = re.sub(r'/+', '/', doi)  # Fix double slashes
    return doi


# ============================================================
# CROSSREF METADATA
# ============================================================

def fetch_crossref(doi):
    """Fetch metadata from CrossRef API."""
    if not HAS_REQUESTS:
        return None
    try:
        resp = requests.get(CROSSREF_URL.format(doi=doi), headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        msg = resp.json().get('message', {})
        info = {'doi': msg.get('DOI', doi)}

        title_list = msg.get('title', [])
        info['title'] = title_list[0] if title_list else ''

        issued = msg.get('issued', {}).get('date-parts', [[None]])[0]
        info['year'] = issued[0] if issued and issued[0] else None

        info['publisher'] = msg.get('publisher', '')
        info['type'] = msg.get('type', '')

        container = msg.get('container-title', [])
        info['journal'] = container[0] if container else ''

        info['volume'] = msg.get('volume', '')
        info['issue'] = msg.get('issue', '')
        info['pages'] = msg.get('page', '')

        authors = msg.get('author', [])
        info['authors'] = []
        for a in authors[:20]:
            family = a.get('family', '')
            given = a.get('given', '')
            if family or given:
                info['authors'].append({'given': given, 'family': family})

        return info
    except Exception:
        return None


# ============================================================
# IEEE FORMATTING
# ============================================================

def format_author_ieee(authors):
    if not authors:
        return ""
    formatted = []
    for a in authors:
        given = a.get('given', '')
        family = a.get('family', '')
        initials = ' '.join([g[0].upper() + '.' for g in given.split() if g])
        if initials and family:
            formatted.append(f"{initials} {family}")
        elif family:
            formatted.append(family)
    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        if len(formatted) <= 6:
            return ', '.join(formatted[:-1]) + ', and ' + formatted[-1]
        else:
            return ', '.join(formatted[:6]) + ', et al.'

def format_ieee_citation(paper):
    authors = format_author_ieee(paper.get('authors', []))

    title = paper.get('title', 'Untitled')
    title = html.unescape(title)
    title = re.sub(r'<[^>]+>', '', title)
    title = re.sub(r'<mml:math[^>]*>.*?</mml:math>', '', title, flags=re.DOTALL)
    title = re.sub(r'\s+', ' ', title).strip()

    if not title or re.match(r'^10\.\d+[/.\s]', title):
        title = paper.get('_filename', 'Untitled')
        title = title.replace('.pdf', '').replace('_', ' ')
        title = re.sub(r'^10\.\d+[\s/]', '', title)
        title = title.strip()

    title = f'"{title}"'

    journal = paper.get('journal', '')
    year = paper.get('year', '')
    volume = paper.get('volume', '')
    issue = paper.get('issue', '')
    pages = paper.get('pages', '')
    doi = paper.get('doi', '')

    parts = []
    if authors:
        parts.append(authors)
    parts.append(title)

    if journal:
        parts.append(f"*{journal}*")

    vol_info = []
    if volume:
        vol_info.append(f"vol. {volume}")
    if issue:
        vol_info.append(f"no. {issue}")
    if pages:
        vol_info.append(f"pp. {pages}")
    if vol_info:
        parts.append(', '.join(vol_info))

    if year:
        parts.append(str(year))

    if doi and doi.startswith('10.'):
        parts.append(f"doi: {doi}")

    citation = ', '.join([p for p in parts if p])
    citation = re.sub(r',\s*,', ',', citation)
    citation = re.sub(r'\s+', ' ', citation).strip()
    citation = citation.rstrip(',')

    return citation


# ============================================================
# MAIN
# ============================================================

def main():
    if not os.path.exists(PDFTOTEXT):
        print(f"ERROR: pdftotext not found at {PDFTOTEXT}")
        print("Will proceed with filename-based DOI only.")
        pdf_to_text_available = False
    else:
        pdf_to_text_available = True

    print("=" * 70)
    print("COMPREHENSIVE DOI VERIFICATION AND FIX")
    print("=" * 70)

    # Step 1: Apply known fixes first
    print("\n[1/5] Applying known fixes...")
    for old_name, new_name in KNOWN_FIXES.items():
        old_path = os.path.join(PAPER_DIR, old_name)
        new_path = os.path.join(PAPER_DIR, new_name)
        if os.path.exists(old_path):
            if new_name is None:
                print(f"  DELETE (duplicate): {old_name}")
            elif os.path.exists(new_path):
                print(f"  SKIP (target exists): {old_name} -> {new_name}")
            else:
                shutil.move(old_path, new_path)
                print(f"  RENAMED: {old_name} -> {new_name}")
        else:
            print(f"  NOT FOUND: {old_name}")

    # Step 2: Extract DOI from all PDFs
    print("\n[2/5] Extracting DOIs from all PDFs...")
    pdf_files = sorted([f for f in os.listdir(PAPER_DIR) if f.endswith('.pdf')])
    total = len(pdf_files)

    verified_ok = []
    to_rename = []
    extraction_failed = []
    conflicts = []

    for i, filename in enumerate(pdf_files):
        filepath = os.path.join(PAPER_DIR, filename)
        filename_doi = normalize_doi(filename_to_doi(filename))

        if pdf_to_text_available:
            try:
                found_doi = extract_paper_doi(filepath)
            except Exception as e:
                found_doi = None
        else:
            found_doi = None

        found_norm = normalize_doi(found_doi) if found_doi else None

        # Apply DOI overrides for known cases (e.g., prefer paper DOI over data repo DOI)
        if filename in DOI_OVERRIDES:
            override_doi = DOI_OVERRIDES[filename]
            override_norm = normalize_doi(override_doi)
            if found_norm and found_norm != override_norm:
                print(f"  OVERRIDE: {filename}: extracted={found_norm}, using={override_norm}")
            found_doi = override_doi
            found_norm = override_norm

        if found_norm and filename_doi:
            if found_norm == filename_doi:
                verified_ok.append(filename)
            else:
                correct_name = doi_to_filename(found_doi)
                if correct_name != filename:
                    if correct_name in pdf_files or os.path.exists(os.path.join(PAPER_DIR, correct_name)):
                        conflicts.append((filename, filename_doi, found_doi, correct_name))
                    else:
                        to_rename.append((filename, filename_doi, found_doi, correct_name))
        elif found_norm and not filename_doi:
            correct_name = doi_to_filename(found_doi)
            to_rename.append((filename, '(non-DOI name)', found_doi, correct_name))
        else:
            extraction_failed.append(filename)

        if (i + 1) % 100 == 0:
            print(f"  [{i+1}/{total}] ✓{len(verified_ok)} ✗{len(to_rename)} ?{len(extraction_failed)}")

    print(f"\n  Results: ✓{len(verified_ok)} matched, {len(to_rename)} to rename, "
          f"{len(conflicts)} conflicts, {len(extraction_failed)} no extraction")

    # Step 3: Rename files
    print("\n[3/5] Renaming files to match actual DOI...")
    renamed = 0
    for fn, exp, found, correct in to_rename:
        old_path = os.path.join(PAPER_DIR, fn)
        new_path = os.path.join(PAPER_DIR, correct)
        if os.path.exists(new_path):
            print(f"  SKIP (target exists): {fn}")
            conflicts.append((fn, exp, found, correct))
        else:
            try:
                shutil.move(old_path, new_path)
                print(f"  RENAMED: {fn} -> {correct}")
                renamed += 1
            except Exception as e:
                print(f"  ERROR: {fn}: {e}")

    if conflicts:
        print(f"\n  ⚠ {len(conflicts)} conflicts (target file already exists):")
        for fn, exp, found, correct in conflicts:
            old_path = os.path.join(PAPER_DIR, fn)
            new_path = os.path.join(PAPER_DIR, correct)
            old_size = os.path.getsize(old_path) if os.path.exists(old_path) else 0
            new_size = os.path.getsize(new_path) if os.path.exists(new_path) else 0
            print(f"    {fn} ({old_size} bytes)")
            print(f"    -> {correct} ({new_size} bytes) - TARGET EXISTS")
            if old_size == new_size:
                print(f"       Same size - likely exact duplicate. Old file kept as-is.")
            else:
                print(f"       Different sizes - may be different version. Old file kept as-is.")
            print()

    print(f"\n  Total renamed: {renamed}")

    # Step 4: Update metadata JSON
    print("\n[4/5] Updating papers_metadata.json...")
    current_files = sorted([f for f in os.listdir(PAPER_DIR) if f.endswith('.pdf')])

    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            old_metadata = json.load(f)
        print(f"  Loaded {len(old_metadata)} old metadata entries")
    else:
        old_metadata = {}

    new_metadata = {}
    crossref_hits = 0
    crossref_misses = 0

    for i, filename in enumerate(current_files):
        # Check if we have old metadata under old filename or by searching
        old_entry = None
        if filename in old_metadata:
            old_entry = old_metadata[filename]
        else:
            # Try to find by DOI match
            doi = filename_to_doi(filename)
            for old_fn, entry in old_metadata.items():
                if entry.get('doi', '') == doi:
                    old_entry = entry
                    old_entry['_filename'] = filename
                    break

        if old_entry:
            old_entry['_filename'] = filename
            new_metadata[filename] = old_entry
        else:
            doi = filename_to_doi(filename)
            info = {'_filename': filename, 'doi': doi}

            if HAS_REQUESTS and doi.startswith('10.'):
                crossref_info = fetch_crossref(doi)
                if crossref_info:
                    info.update(crossref_info)
                    crossref_hits += 1
                else:
                    crossref_misses += 1
                    title = filename.replace('.pdf', '').replace('_', ' ')
                    info['title'] = title
            else:
                title = filename.replace('.pdf', '').replace('_', ' ')
                info['title'] = title

            new_metadata[filename] = info

        if (i + 1) % 100 == 0:
            print(f"  [{i+1}/{len(current_files)}] processed")
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_metadata, f, ensure_ascii=False, indent=2)

        if HAS_REQUESTS and (i + 1) % 20 == 0:
            time.sleep(0.3)

    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_metadata, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(new_metadata)} entries (CrossRef: {crossref_hits}, Fallback: {crossref_misses})")

    # Step 5: Regenerate 文献.md
    print("\n[5/5] Regenerating 文献.md...")

    sorted_papers = sorted(new_metadata.items(), key=lambda x: (
        str(x[1].get('year', '9999')),
        str(x[1].get('authors', [{}])[0].get('family', 'zzz') if x[1].get('authors') else 'zzz'),
    ))

    lines = []
    lines.append("# 参考文献列表 (IEEE格式)")
    lines.append("")
    lines.append(f"**总计**: {len(new_metadata)} 篇文献")
    lines.append(f"**生成日期**: 2026-06-12")
    lines.append("")
    lines.append("---")
    lines.append("")

    for idx, (filename, paper) in enumerate(sorted_papers, 1):
        citation = format_ieee_citation(paper)
        pdf_path = f"paper/{filename}"
        doi = paper.get('doi', '')

        lines.append(f"**[{idx}]** {citation}")
        lines.append("")
        lines.append(f"> 📄 [PDF: `{filename}`]({pdf_path})")
        if doi and doi.startswith('10.'):
            lines.append(f"> 🔗 DOI: [{doi}](https://doi.org/{doi})")
        lines.append("")

        if idx % 200 == 0:
            print(f"  Generated {idx} citations...")

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"  Done! {len(sorted_papers)} references written to {OUTPUT_MD}")

    # Final report
    print("\n" + "=" * 70)
    print("FIX SUMMARY")
    print("=" * 70)
    print(f"  Known fixes applied:    {sum(1 for old in KNOWN_FIXES if os.path.exists(os.path.join(PAPER_DIR, old)))}")
    print(f"  DOI-based renames:      {renamed}")
    print(f"  Conflicts (kept old):   {len(conflicts)}")
    print(f"  Extraction failed:      {len(extraction_failed)}")
    print(f"  Total PDFs:             {len(current_files)}")
    print(f"\n  Metadata:  {METADATA_FILE} ({len(new_metadata)} entries)")
    print(f"  References: {OUTPUT_MD} ({len(sorted_papers)} citations)")
    print()

    if conflicts:
        print("⚠ NOTE: Some conflicts exist where target filename already exists.")
        print("  The old file was kept. These may be duplicates (same paper from different sources).")
        print("  Review these files manually if needed.")
        for fn, exp, found, correct in conflicts:
            print(f"    {fn}")

    if extraction_failed:
        print(f"\n⚠ {len(extraction_failed)} files - DOI could not be extracted from PDF.")
        print("  These keep their current filenames. Verify manually if needed.")
        for fn in extraction_failed:
            print(f"    {fn}")

    return new_metadata


if __name__ == '__main__':
    main()
