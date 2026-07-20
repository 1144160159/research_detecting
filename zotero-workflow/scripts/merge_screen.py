from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from common import (
    clean_text,
    ensure_dir,
    latest_file,
    load_yaml,
    normalize_title,
    read_csv,
    stable_id,
    timestamp,
    write_csv,
    write_json,
)


def load_external_records(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records


def iter_external_papers(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    papers: list[dict[str, Any]] = []
    for record in records:
        parsed = record.get("parsed")
        if not isinstance(parsed, dict):
            continue
        candidates = parsed.get("papers") or parsed.get("results") or parsed.get("data") or []
        if isinstance(candidates, dict):
            candidates = candidates.get("papers") or candidates.get("results") or []
        if not isinstance(candidates, list):
            continue
        for item in candidates:
            if not isinstance(item, dict):
                continue
            title = clean_text(item.get("title") or item.get("name") or "")
            if not title:
                continue
            papers.append({
                "source_type": "external",
                "source": record.get("source", ""),
                "query": record.get("query", ""),
                "title": title,
                "year": item.get("year", ""),
                "doi": item.get("doi") or item.get("DOI") or "",
                "url": item.get("url") or item.get("paper_url") or "",
                "abstract": clean_text(item.get("abstract", "")),
                "score": item.get("score", ""),
                "file_path": "",
                "matched_groups": "",
                "matched_terms": "",
            })
    return papers


def decision_for(row: dict[str, Any], keep_threshold: int, maybe_threshold: int) -> str:
    try:
        score = int(float(row.get("score") or 0))
    except Exception:
        score = 0
    groups = set(str(row.get("matched_groups", "")).split(";"))
    if score >= keep_threshold:
        return "keep"
    if {"open_set", "encrypted_traffic"} <= groups and ("malicious" in groups or "anomaly_detection" in groups):
        return "keep"
    if score >= maybe_threshold:
        return "maybe"
    if row.get("source_type") == "external":
        return "maybe"
    return "reject"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--queries", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sources", default="")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workflow = workspace / "zotero-workflow"
    config = load_yaml(Path(args.config))
    screening_config = config.get("screening", {})
    keep_threshold = int(screening_config.get("keep_threshold", 28))
    maybe_threshold = int(screening_config.get("maybe_threshold", 12))

    local_scores = latest_file(workflow / "local-index", "*_local_relevance_scores.csv")
    external_jsonl = latest_file(workflow / "exports", "*_external_search_results.jsonl")
    if not external_jsonl:
        external_jsonl = latest_file(workflow / "external-search", "*_external_search_results.jsonl")

    stamp = timestamp()
    merged_dir = ensure_dir(workflow / "merged")
    screening_dir = ensure_dir(workflow / "screening")
    candidates_csv = merged_dir / f"{stamp}_candidates_ranked.csv"
    screening_csv = screening_dir / f"{stamp}_screening_batch_auto.csv"
    summary_json = merged_dir / f"{stamp}_merge_screen_summary.json"

    if args.dry_run:
        print(json.dumps({
            "stage": "merge-screen",
            "dry_run": True,
            "local_scores": str(local_scores) if local_scores else None,
            "external_jsonl": str(external_jsonl) if external_jsonl else None,
            "would_write": [str(candidates_csv), str(screening_csv), str(summary_json)],
        }, ensure_ascii=False, indent=2))
        return 0

    candidates: list[dict[str, Any]] = []
    if local_scores:
        for row in read_csv(local_scores):
            candidates.append({
                "source_type": "local_pdf",
                "source": "paper",
                "query": "",
                "title": row.get("title_guess") or row.get("metadata_title") or row.get("file_name", ""),
                "year": "",
                "doi": row.get("doi_guess", ""),
                "url": "",
                "abstract": "",
                "score": row.get("score", ""),
                "file_path": row.get("file_path", ""),
                "matched_groups": row.get("matched_groups", ""),
                "matched_terms": row.get("matched_terms", ""),
            })

    candidates.extend(iter_external_papers(load_external_records(external_jsonl)))
    if args.limit > 0:
        candidates = candidates[: args.limit]

    deduped: dict[str, dict[str, Any]] = {}
    for row in candidates:
        key = clean_text(row.get("doi", "")).lower() or normalize_title(str(row.get("title", ""))) or stable_id(str(row))
        if key not in deduped:
            row["candidate_id"] = stable_id(key)
            deduped[key] = row
            continue
        existing = deduped[key]
        if not existing.get("file_path") and row.get("file_path"):
            existing["file_path"] = row.get("file_path")
        existing["source"] = ";".join(sorted(set(str(existing.get("source", "")).split(";") + [str(row.get("source", ""))])))

    ranked = list(deduped.values())
    ranked.sort(key=lambda row: int(float(row.get("score") or 0)), reverse=True)

    candidate_fields = [
        "candidate_id", "source_type", "source", "query", "title", "year", "doi",
        "url", "score", "file_path", "matched_groups", "matched_terms", "abstract",
    ]
    write_csv(candidates_csv, ranked, candidate_fields)

    screening_rows: list[dict[str, Any]] = []
    for index, row in enumerate(ranked, start=1):
        decision = decision_for(row, keep_threshold, maybe_threshold)
        groups = [g for g in str(row.get("matched_groups", "")).split(";") if g]
        reason = "keyword score and topic match" if groups else "external search candidate; needs title/abstract review"
        screening_rows.append({
            "rank": index,
            "candidate_id": row.get("candidate_id", ""),
            "decision_initial": decision,
            "title": row.get("title", ""),
            "year": row.get("year", ""),
            "doi": row.get("doi", ""),
            "source": row.get("source", ""),
            "score": row.get("score", ""),
            "file_path": row.get("file_path", ""),
            "reason_initial": reason,
            "matched_groups": row.get("matched_groups", ""),
            "matched_terms": row.get("matched_terms", ""),
            "zotero_action": "import_or_link" if decision in {"keep", "maybe"} else "do_not_import_yet",
            "human_decision": "",
            "human_note": "",
        })

    screening_fields = [
        "rank", "candidate_id", "decision_initial", "title", "year", "doi", "source",
        "score", "file_path", "reason_initial", "matched_groups", "matched_terms",
        "zotero_action", "human_decision", "human_note",
    ]
    write_csv(screening_csv, screening_rows, screening_fields)
    summary = {
        "stage": "merge-screen",
        "dry_run": False,
        "local_scores": str(local_scores) if local_scores else None,
        "external_jsonl": str(external_jsonl) if external_jsonl else None,
        "candidates": len(ranked),
        "screening_csv": str(screening_csv),
        "candidates_csv": str(candidates_csv),
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
