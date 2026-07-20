from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import ensure_dir, latest_file, load_yaml, read_csv, timestamp, write_csv, write_json


def tag_for_group(group: str, tag_config: dict[str, Any]) -> str:
    topic_tags = tag_config.get("topic_tags", {})
    if isinstance(topic_tags, dict):
        return str(topic_tags.get(group, ""))
    return ""


def confirmed_decision(row: dict[str, str], use_human_only: bool = False) -> str:
    human = (row.get("human_decision") or "").strip().lower()
    if human:
        return human
    if use_human_only:
        return ""
    return (row.get("decision_initial") or "").strip().lower()


def build_tags(row: dict[str, str], tag_config: dict[str, Any], use_human_only: bool = False) -> str:
    tags: list[str] = []
    status_tags = tag_config.get("status_tags", {}) if isinstance(tag_config.get("status_tags", {}), dict) else {}
    evidence_tags = tag_config.get("evidence_tags", {}) if isinstance(tag_config.get("evidence_tags", {}), dict) else {}
    decision = confirmed_decision(row, use_human_only=use_human_only)
    if decision in status_tags:
        tags.append(str(status_tags[decision]))
    else:
        tags.append(str(status_tags.get("inbox", "ad/status/inbox")))

    groups = [g for g in str(row.get("matched_groups", "")).split(";") if g]
    for group in groups:
        tag = tag_for_group(group, tag_config)
        if tag:
            tags.append(tag)

    try:
        rank = int(row.get("rank", "999999") or "999999")
    except Exception:
        rank = 999999
    if decision == "keep" and rank <= 10:
        tags.append(str(evidence_tags.get("must_cite", "ad/evidence/must-cite")))
    elif decision == "keep":
        tags.append(str(evidence_tags.get("support", "ad/evidence/support")))

    return ";".join(sorted(set(t for t in tags if t)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sources", default="")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workflow = workspace / "zotero-workflow"
    tag_config_path = workflow / "config" / "zotero-tags.yml"
    tag_config = load_yaml(tag_config_path)
    screening_file = latest_file(workflow / "screening", "*_screening_batch_auto.csv")
    if not screening_file:
        raise FileNotFoundError("No screening batch found under zotero-workflow/screening")

    rows = read_csv(screening_file)
    use_human_only = any((row.get("human_decision") or "").strip() for row in rows)
    confirmed_keep = [row for row in rows if confirmed_decision(row, use_human_only=use_human_only) == "keep"]
    if args.limit > 0:
        confirmed_keep = confirmed_keep[: args.limit]

    stamp = timestamp()
    output_dir = ensure_dir(workflow / "zotero-import")
    manifest_csv = output_dir / f"{stamp}_confirmed_keep_zotero_manifest.csv"
    mineru_queue_csv = output_dir / f"{stamp}_confirmed_keep_mineru_queue.csv"
    instructions_md = output_dir / f"{stamp}_zotero_import_instructions.md"
    summary_json = output_dir / f"{stamp}_zotero_batch_summary.json"

    if args.dry_run:
        print(json.dumps({
            "stage": "zotero-batch",
            "dry_run": True,
            "screening_file": str(screening_file),
            "use_human_only": use_human_only,
            "confirmed_keep": len(confirmed_keep),
            "would_write": [str(manifest_csv), str(mineru_queue_csv), str(instructions_md), str(summary_json)],
        }, ensure_ascii=False, indent=2))
        return 0

    collection = tag_config.get("collections", {}).get("core", "异常检测/01_Core_核心证据")
    manifest_rows: list[dict[str, Any]] = []
    queue_rows: list[dict[str, Any]] = []
    for row in confirmed_keep:
        tags = build_tags(row, tag_config, use_human_only=use_human_only)
        manifest_rows.append({
            "rank": row.get("rank", ""),
            "candidate_id": row.get("candidate_id", ""),
            "title": row.get("title", ""),
            "year": row.get("year", ""),
            "doi": row.get("doi", ""),
            "source": row.get("source", ""),
            "file_path": row.get("file_path", ""),
            "zotero_collection": collection,
            "zotero_tags": tags,
            "import_mode": "linked_pdf_if_local_else_metadata",
            "confirmed_decision": confirmed_decision(row, use_human_only=use_human_only),
            "reason": row.get("reason_initial", ""),
        })
        if row.get("file_path"):
            queue_rows.append({
                "priority": row.get("rank", ""),
                "title": row.get("title", ""),
                "doi": row.get("doi", ""),
                "file_path": row.get("file_path", ""),
                "mineru_action": "parse_pdf_to_zotero_note",
                "note_title_prefix": "MinerU Parse",
                "evidence_card_target": f"zotero-workflow/evidence-cards/{row.get('candidate_id', row.get('rank', 'paper'))}_evidence.md",
            })

    manifest_fields = [
        "rank", "candidate_id", "title", "year", "doi", "source", "file_path",
        "zotero_collection", "zotero_tags", "import_mode", "confirmed_decision", "reason",
    ]
    queue_fields = [
        "priority", "title", "doi", "file_path", "mineru_action",
        "note_title_prefix", "evidence_card_target",
    ]
    write_csv(manifest_csv, manifest_rows, manifest_fields)
    write_csv(mineru_queue_csv, queue_rows, queue_fields)

    instructions = [
        "# Zotero Import Batch",
        "",
        f"Screening source: `{screening_file}`",
        f"Confirmed keep items: {len(manifest_rows)}",
        f"Local PDF items queued for MinerU: {len(queue_rows)}",
        "",
        "## Zotero 操作",
        "",
        "1. 在 Zotero 中确认集合存在：`异常检测/01_Core_核心证据`。",
        "2. 对 manifest 中有 `file_path` 的本地 PDF，优先以链接附件方式导入或拖入核心集合。",
        "3. 导入后补齐 DOI/标题，并写入 `zotero_tags` 字段中的标签。",
        "4. 外部检索但无本地 PDF 的条目先建元数据条目，后续再补 PDF。",
        "",
        "## MinerU 操作",
        "",
        "1. 按 `confirmed_keep_mineru_queue.csv` 的 priority 顺序解析 PDF。",
        "2. 每篇解析结果回写 Zotero 子笔记。",
        "3. 关键结论再整理到 `zotero-workflow/evidence-cards/`。",
        "",
        "## Files",
        "",
        f"- Manifest: `{manifest_csv}`",
        f"- MinerU queue: `{mineru_queue_csv}`",
    ]
    instructions_md.write_text("\n".join(instructions) + "\n", encoding="utf-8")
    summary = {
        "stage": "zotero-batch",
        "screening_file": str(screening_file),
        "use_human_only": use_human_only,
        "confirmed_keep": len(manifest_rows),
        "local_pdf_mineru_queue": len(queue_rows),
        "manifest_csv": str(manifest_csv),
        "mineru_queue_csv": str(mineru_queue_csv),
        "instructions_md": str(instructions_md),
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
