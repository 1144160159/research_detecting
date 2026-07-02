#!/usr/bin/env python3
"""
Re-extract metadata and generate IEEE-format references (文献.md) for all papers.
Each reference links to the PDF file in the paper/ directory.
"""

import json
import os
import re
import sys
import time
import requests
import html

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PAPER_DIR = "paper"
OUTPUT_MD = "文献.md"
METADATA_FILE = "papers_metadata.json"
CROSSREF_URL = "https://api.crossref.org/works/{doi}"
HEADERS = {"User-Agent": "CitationGen/1.0 (mailto:research@example.com)"}
DELAY = 0.3

def filename_to_doi(filename):
    """Convert PDF filename to DOI."""
    name = filename.replace('.pdf', '')
    idx = name.find('_')
    if idx == -1:
        return name
    return name[:idx] + '/' + name[idx+1:]

def fetch_crossref(doi):
    """Fetch metadata from CrossRef API."""
    try:
        resp = requests.get(CROSSREF_URL.format(doi=doi), headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        msg = resp.json().get('message', {})
        info = {'doi': msg.get('DOI', doi)}

        title_list = msg.get('title', [])
        info['title'] = title_list[0] if title_list else ''

        abstract = msg.get('abstract', '')
        if abstract:
            abstract = re.sub(r'<[^>]+>', '', abstract)
            abstract = re.sub(r'&[a-z]+;', '', abstract)
            info['abstract'] = abstract.strip()[:3000]

        issued = msg.get('issued', {}).get('date-parts', [[None]])[0]
        info['year'] = issued[0] if issued and issued[0] else None

        info['publisher'] = msg.get('publisher', '')
        info['type'] = msg.get('type', '')

        container = msg.get('container-title', [])
        info['journal'] = container[0] if container else ''
        if not info['journal']:
            short = msg.get('short-container-title', [])
            info['journal'] = short[0] if short else ''

        # Volume, issue, pages
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

def format_author_ieee(authors):
    """Format author list in IEEE style: J. Smith, A. Johnson, and B. Lee"""
    if not authors:
        return ""
    formatted = []
    for a in authors:
        given = a.get('given', '')
        family = a.get('family', '')
        # IEEE: abbreviate given names to initials
        initials = ' '.join([g[0].upper() + '.' for g in given.split() if g])
        if not initials and family:
            formatted.append(family)
        else:
            formatted.append(f"{initials} {family}")
    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        # IEEE uses "and" before last author (for up to 3) or "et al."
        if len(formatted) <= 6:
            return ', '.join(formatted[:-1]) + ', and ' + formatted[-1]
        else:
            return ', '.join(formatted[:6]) + ', et al.'

def format_ieee_citation(paper):
    """Generate IEEE format citation string."""
    authors = format_author_ieee(paper.get('authors', []))
    title = paper.get('title', 'Untitled')
    title = html.unescape(title)
    title = re.sub(r'<[^>]+>', '', title)
    title = re.sub(r'\s+', ' ', title).strip()

    # Clean up math/code artifacts in title
    title = re.sub(r'<mml:math[^>]*>.*?</mml:math>', '', title, flags=re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title)
    title = title.strip()
    if not title or len(title) < 5:
        title = paper.get('_filename', 'Untitled').replace('.pdf', '').replace('_', ' ')

    # Ensure title is in quotes
    title = f'"{title}"'

    journal = paper.get('journal', '')
    year = paper.get('year', '')
    volume = paper.get('volume', '')
    issue = paper.get('issue', '')
    pages = paper.get('pages', '')
    doi = paper.get('doi', '')
    pub_type = paper.get('type', '')

    parts = [authors, title]

    # Journal/conference name
    if journal:
        parts.append(f"*{journal}*")
    else:
        parts.append("")

    # Vol, no, pp
    vol_info = []
    if volume:
        vol_info.append(f"vol. {volume}")
    if issue:
        vol_info.append(f"no. {issue}")
    if pages:
        vol_info.append(f"pp. {pages}")
    if vol_info:
        parts.append(', '.join(vol_info))

    # Year
    if year:
        parts.append(str(year))
    else:
        parts.append("")

    # DOI (optional for IEEE but useful)
    if doi and not doi.startswith('Contextual/') and not doi.startswith('A/'):
        parts.append(f"doi: {doi}")

    # Filter empty parts and join
    citation = ', '.join([p for p in parts if p])
    # Clean up any double commas or spaces
    citation = re.sub(r',\s*,', ',', citation)
    citation = re.sub(r'\s+', ' ', citation).strip()
    # Remove trailing comma
    citation = citation.rstrip(',')

    return citation

def main():
    # Load existing metadata if available
    results = {}
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"Loaded {len(results)} existing metadata entries")

    pdf_files = sorted([f for f in os.listdir(PAPER_DIR) if f.endswith('.pdf')])
    total = len(pdf_files)
    print(f"Processing {total} PDF files...")

    crossref_hits = 0
    crossref_misses = 0

    for i, filename in enumerate(pdf_files):
        if filename in results:
            continue

        doi = filename_to_doi(filename)
        info = {'_filename': filename, 'doi': doi}

        crossref_info = fetch_crossref(doi)
        if crossref_info:
            info.update(crossref_info)
            crossref_hits += 1
        else:
            # Use filename as fallback title
            title = filename.replace('.pdf', '').replace('_', ' ')
            # Check if it's a non-DOI descriptive filename
            if not re.match(r'^10\.\d+', doi):
                info['title'] = title
                info['year'] = None
            else:
                info['title'] = title
            crossref_misses += 1

        info['_filename'] = filename
        results[filename] = info

        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{total}] {crossref_hits} CrossRef hits, {crossref_misses} misses")
            # Save progress
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        time.sleep(DELAY)
        if (i + 1) % 150 == 0:
            time.sleep(3)

    # Final save
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nMetadata saved: {len(results)} papers (CrossRef: {crossref_hits}, Fallback: {crossref_misses})")

    # ============================================================
    # GENERATE IEEE CITATIONS (文献.md)
    # ============================================================
    print("\nGenerating IEEE citations...")

    # Sort: by domain category then year then first author
    sorted_papers = sorted(results.items(), key=lambda x: (
        str(x[1].get('year', '9999')),
        str(x[1].get('authors', [{}])[0].get('family', 'zzz') if x[1].get('authors') else 'zzz'),
    ))

    lines = []
    lines.append("# 参考文献列表 (IEEE格式)")
    lines.append("")
    lines.append(f"**总计**: {len(results)} 篇文献")
    lines.append(f"**生成日期**: 2026-06-12")
    lines.append("")
    lines.append("---")
    lines.append("")

    for idx, (filename, paper) in enumerate(sorted_papers, 1):
        citation = format_ieee_citation(paper)

        # Link to PDF
        pdf_path = f"paper/{filename}"
        doi = paper.get('doi', '')

        # Generate reference entry
        lines.append(f"**[{idx}]** {citation}")
        lines.append(f"")
        lines.append(f"> 📄 [PDF: `{filename}`]({pdf_path})")
        if doi and doi.startswith('10.'):
            lines.append(f"> 🔗 DOI: [{doi}](https://doi.org/{doi})")
        lines.append("")

        if idx % 200 == 0:
            print(f"  Generated {idx} citations...")

    # Write output
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\nDone! Written {len(results)} references to {OUTPUT_MD}")

if __name__ == '__main__':
    main()
