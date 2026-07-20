from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from common import append_jsonl, ensure_dir, load_yaml, run_command, timestamp, write_json


def enabled_sources(config: dict[str, Any], requested: str) -> dict[str, dict[str, Any]]:
    sources = config.get("external_search", {}).get("sources", {})
    if requested:
        names = [name.strip() for name in re.split(r"[,\s]+", requested) if name.strip()]
        return {name: sources.get(name, {"enabled": True}) for name in names}
    return {
        name: cfg
        for name, cfg in sources.items()
        if isinstance(cfg, dict) and bool(cfg.get("enabled", False))
    }


def parse_json_output(stdout: str) -> Any:
    start = stdout.find("{")
    if start < 0:
        start = stdout.find("[")
    if start < 0:
        return None
    try:
        return json.loads(stdout[start:])
    except Exception:
        return None


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
    queries_config = load_yaml(Path(args.queries))
    queries = list(queries_config.get("primary_queries", []))
    if args.limit > 0:
        queries = queries[:args.limit]

    sources = enabled_sources(config, args.sources)
    stamp = timestamp()
    output_dir = ensure_dir(workflow / "exports")
    compatibility_dir = ensure_dir(workflow / "external-search")
    output_jsonl = output_dir / f"{stamp}_external_search_results.jsonl"
    compatibility_jsonl = compatibility_dir / f"{stamp}_external_search_results.jsonl"
    summary_json = output_dir / f"{stamp}_external_search_summary.json"
    compatibility_summary_json = compatibility_dir / f"{stamp}_external_search_summary.json"

    commands: list[list[str]] = []
    skipped_plan: list[dict[str, Any]] = []
    planned_semantic_requests = 0
    for query in queries:
        for source, source_config in sources.items():
            if source == "semantic":
                max_requests = int(source_config.get("max_requests_per_run", 1))
                if planned_semantic_requests >= max_requests:
                    skipped_plan.append({
                        "query": query,
                        "source": source,
                        "reason": f"semantic max_requests_per_run={max_requests}",
                    })
                    continue
                planned_semantic_requests += 1
            max_results = int(source_config.get("max_results", config.get("external_search", {}).get("default_max_results_per_source", 5)))
            commands.append(["paper-search", "search", str(query), "-n", str(max_results), "-s", source])

    if args.dry_run:
        print(json.dumps({
            "stage": "external-search",
            "dry_run": True,
            "queries": queries,
            "sources": list(sources.keys()),
            "command_count": len(commands),
            "skipped_by_rate_policy": skipped_plan,
            "would_write": [
                str(output_jsonl),
                str(summary_json),
                str(compatibility_jsonl),
                str(compatibility_summary_json),
            ],
            "commands": commands,
        }, ensure_ascii=False, indent=2))
        return 0

    records: list[dict[str, Any]] = []
    semantic_requests = 0
    for query in queries:
        for source, source_config in sources.items():
            if source == "semantic":
                max_requests = int(source_config.get("max_requests_per_run", 1))
                if semantic_requests >= max_requests:
                    records.append({
                        "query": query,
                        "source": source,
                        "skipped": True,
                        "reason": f"semantic max_requests_per_run={max_requests}",
                    })
                    continue
                wait_seconds = int(source_config.get("wait_seconds_between_requests", 60))
                if semantic_requests > 0 and wait_seconds > 0:
                    time.sleep(wait_seconds)
                semantic_requests += 1

            max_results = int(source_config.get("max_results", config.get("external_search", {}).get("default_max_results_per_source", 5)))
            cmd = ["paper-search", "search", str(query), "-n", str(max_results), "-s", source]
            started = time.strftime("%Y-%m-%dT%H:%M:%S")
            try:
                code, stdout, stderr = run_command(cmd, timeout=180)
            except Exception as exc:
                code, stdout, stderr = 999, "", f"{type(exc).__name__}: {exc}"
            parsed = parse_json_output(stdout)
            record = {
                "query": query,
                "source": source,
                "command": cmd,
                "exit_code": code,
                "started_at": started,
                "stderr_preview": stderr[:1200],
                "stdout_preview": stdout[:1200],
                "parsed": parsed,
            }
            records.append(record)
            append_jsonl(output_jsonl, [record])
            append_jsonl(compatibility_jsonl, [record])

    summary = {
        "stage": "external-search",
        "dry_run": False,
        "queries": queries,
        "sources": list(sources.keys()),
        "records": len(records),
        "output_jsonl": str(output_jsonl),
        "compatibility_jsonl": str(compatibility_jsonl),
    }
    write_json(summary_json, summary)
    write_json(compatibility_summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
