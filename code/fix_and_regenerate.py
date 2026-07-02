#!/usr/bin/env python3
"""
Fix metadata for papers missing from CrossRef (arXiv, etc.)
Then regenerate 文献.md with clean IEEE citations.
"""

import json
import re
import sys
import time
import requests
import html

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

METADATA_FILE = "papers_metadata.json"
OUTPUT_MD = "文献.md"

def fix_arxiv_metadata(paper):
    """Try to get metadata from arXiv API."""
    filename = paper.get('_filename', '')
    doi = paper.get('doi', '')

    # Extract arXiv ID from DOI or filename
    arxiv_id = None
    m = re.search(r'arxiv[./](\d+\.\d+)', doi, re.IGNORECASE)
    if not m:
        m = re.search(r'arxiv[./](\d+\.\d+)', filename, re.IGNORECASE)

    if m:
        arxiv_id = m.group(1)
    else:
        return paper

    print(f"  Fetching arXiv: {arxiv_id}")
    try:
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1"
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return paper

        text = resp.text

        # Extract title from <entry> section (not the feed <title>)
        entry_m = re.search(r'<entry>(.*?)</entry>', text, re.DOTALL)
        entry_text = entry_m.group(1) if entry_m else text

        title_m = re.search(r'<title>(.*?)</title>', entry_text, re.DOTALL)
        if title_m:
            title = title_m.group(1).strip()
            title = re.sub(r'\s+', ' ', title)
            # Skip if it's the feed title
            if title and 'Query:' not in title and len(title) > 10:
                paper['title'] = title

        # Extract authors from <entry>
        authors = re.findall(r'<author>.*?<name>(.*?)</name>.*?</author>', entry_text, re.DOTALL)
        if authors:
            paper['authors'] = []
            for a in authors:
                parts = a.strip().rsplit(' ', 1)
                if len(parts) == 2:
                    paper['authors'].append({'given': parts[0], 'family': parts[1]})
                else:
                    paper['authors'].append({'given': '', 'family': a.strip()})

        # Extract year from <published>
        pub_m = re.search(r'<published>(\d{4})', entry_text)
        if pub_m and not paper.get('year'):
            paper['year'] = int(pub_m.group(1))

        # Journal
        journal_m = re.search(r'<journal_ref>(.*?)</journal_ref>', entry_text, re.DOTALL)
        if journal_m and not paper.get('journal'):
            paper['journal'] = journal_m.group(1).strip()
        elif not paper.get('journal'):
            paper['journal'] = 'arXiv preprint'

    except Exception as e:
        print(f"  arXiv error: {e}")

    return paper

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

    # If title is just a DOI/filename, clean it up
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

def main():
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Fix arXiv papers
    arxiv_fixed = 0
    for fn, paper in data.items():
        if 'arXiv' in fn and not paper.get('authors'):
            fix_arxiv_metadata(paper)
            arxiv_fixed += 1
            time.sleep(0.5)

    if arxiv_fixed:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Fixed {arxiv_fixed} arXiv papers")

    # Generate citations
    print(f"\nGenerating {len(data)} IEEE citations...")

    sorted_papers = sorted(data.items(), key=lambda x: (
        str(x[1].get('year', '9999')),
        str(x[1].get('authors', [{}])[0].get('family', 'zzz') if x[1].get('authors') else 'zzz'),
    ))

    lines = []
    lines.append("# 参考文献列表 (IEEE格式)")
    lines.append("")
    lines.append(f"**总计**: {len(data)} 篇文献")
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

        if (idx % 200) == 0:
            print(f"  Generated {idx} citations...")

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\nDone! {len(data)} references written to {OUTPUT_MD}")

if __name__ == '__main__':
    main()
