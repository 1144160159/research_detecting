from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from common import (
    clean_text,
    doi_from_filename,
    ensure_dir,
    keyword_groups,
    load_yaml,
    score_text,
    timestamp,
    write_csv,
    write_json,
)


def extract_pdf_text(path: Path, pages: int) -> tuple[str, str, int, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:
        return "", "", 0, f"pypdf unavailable: {exc}"

    try:
        reader = PdfReader(str(path), strict=False)
        metadata = reader.metadata or {}
        title = clean_text(getattr(metadata, "title", "") or metadata.get("/Title", ""))
        chunks: list[str] = []
        page_count = min(pages, len(reader.pages))
        for index in range(page_count):
            try:
                chunks.append(reader.pages[index].extract_text() or "")
            except Exception:
                chunks.append("")
        return title, "\n".join(chunks), page_count, ""
    except Exception as exc:
        return "", "", 0, f"{type(exc).__name__}: {exc}"


def title_guess(text: str, fallback: str) -> str:
    lines = [clean_text(line) for line in text.splitlines()]
    lines = [line for line in lines if 25 <= len(line) <= 220]
    blocked = ("abstract", "introduction", "copyright", "doi", "journal", "received")
    for line in lines[:30]:
        if not any(token in line.lower() for token in blocked):
            return line
    return clean_text(fallback)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--queries", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sources", default="")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workflow = workspace / "zotero-workflow"
    config = load_yaml(Path(args.config))
    queries_path = Path(args.queries) if args.queries else workflow / "config" / "queries.yml"
    queries_config = load_yaml(queries_path)

    corpus = config.get("local_corpus", {})
    paper_dir = workspace / str(corpus.get("path", "paper"))
    extract_pages = int(corpus.get("extract_pages", 3))
    configured_limit = int(corpus.get("max_pdfs_per_run", 0) or 0)
    limit = args.limit or configured_limit
    pdfs = sorted(paper_dir.rglob(str(corpus.get("file_glob", "*.pdf"))))
    if limit > 0:
        pdfs = pdfs[:limit]

    stamp = timestamp()
    output_dir = ensure_dir(workflow / "local-index")
    inventory_csv = output_dir / f"{stamp}_local_paper_inventory.csv"
    scores_csv = output_dir / f"{stamp}_local_relevance_scores.csv"
    summary_json = output_dir / f"{stamp}_local_index_summary.json"

    if args.dry_run:
        print(json.dumps({
            "stage": "local-index",
            "dry_run": True,
            "paper_dir": str(paper_dir),
            "pdf_count_seen": len(pdfs),
            "extract_pages": extract_pages,
            "would_write": [str(inventory_csv), str(scores_csv), str(summary_json)],
        }, ensure_ascii=False, indent=2))
        return 0

    groups = keyword_groups(queries_config)
    rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    for index, pdf in enumerate(pdfs, start=1):
        metadata_title, text, pages_seen, error = extract_pdf_text(pdf, extract_pages)
        guessed_title = metadata_title or title_guess(text, pdf.stem)
        doi_guess = doi_from_filename(pdf)
        combined = " ".join([pdf.name, doi_guess, metadata_title, guessed_title, text[:15000]])
        score, matched_groups, matched_terms = score_text(combined, groups)
        row = {
            "index": index,
            "file_path": str(pdf),
            "relative_path": str(pdf.relative_to(workspace)),
            "file_name": pdf.name,
            "size_bytes": pdf.stat().st_size,
            "doi_guess": doi_guess,
            "metadata_title": metadata_title,
            "title_guess": guessed_title,
            "pages_seen": pages_seen,
            "error": error,
        }
        score_row = {
            **row,
            "score": score,
            "matched_groups": ";".join(matched_groups),
            "matched_terms": ";".join(matched_terms),
        }
        rows.append(row)
        score_rows.append(score_row)
        if index % 100 == 0:
            print(f"indexed {index}/{len(pdfs)}", file=sys.stderr)

    inventory_fields = [
        "index", "file_path", "relative_path", "file_name", "size_bytes",
        "doi_guess", "metadata_title", "title_guess", "pages_seen", "error",
    ]
    score_fields = inventory_fields + ["score", "matched_groups", "matched_terms"]
    score_rows.sort(key=lambda row: int(row.get("score", 0)), reverse=True)
    write_csv(inventory_csv, rows, inventory_fields)
    write_csv(scores_csv, score_rows, score_fields)
    summary = {
        "stage": "local-index",
        "dry_run": False,
        "paper_dir": str(paper_dir),
        "pdf_count_indexed": len(rows),
        "inventory_csv": str(inventory_csv),
        "scores_csv": str(scores_csv),
        "top10": score_rows[:10],
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

