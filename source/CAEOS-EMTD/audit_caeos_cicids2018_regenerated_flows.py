from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json, sha256_file


ALIASES = {
    "src_ip": {"srcip", "sourceip"},
    "dst_ip": {"dstip", "destinationip"},
    "protocol": {"protocol"},
    "timestamp": {"timestamp"},
    "duration": {"flowduration"},
}


def token(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def indices(header: list[str]) -> dict[str, int]:
    result = {}
    for position, name in enumerate(header):
        normalized = token(name)
        for field, aliases in ALIASES.items():
            if normalized in aliases:
                result[field] = position
    missing = sorted(set(ALIASES) - set(result))
    if missing:
        raise ValueError(f"missing regenerated flow columns: {missing}")
    return result


def local_time(value: str) -> datetime:
    cleaned = " ".join(value.strip().split())
    for pattern in ("%d/%m/%Y %I:%M:%S %p", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(cleaned, pattern)
        except ValueError:
            pass
    raise ValueError(f"unsupported timestamp: {value!r}")


def prepared_events(schedule: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for event_index, event in enumerate(schedule["events"]):
        result.append(
            {
                "event_index": event_index,
                "fine_label": event["fine_label"],
                "family_label": event["family_label"],
                "start": datetime.strptime(event["start"], "%Y-%m-%d %H:%M"),
                "end": datetime.strptime(event["end"], "%Y-%m-%d %H:%M"),
                "endpoint_pairs": {
                    frozenset((attacker, victim))
                    for attacker in event["attackers"]
                    for victim in event["victims"]
                },
            }
        )
    return result


def audit_day(arguments: tuple[str, list[dict[str, Any]], str]) -> dict[str, Any]:
    day_path_text, events, output_text = arguments
    day_path = Path(day_path_text)
    counters: Counter[str] = Counter()
    fine_counts: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    files = sorted(day_path.glob("*Flow.csv"))
    for path in files:
        try:
            with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as handle:
                reader = csv.reader(handle)
                field_index = indices(next(reader))
                for row in reader:
                    counters["total_flows"] += 1
                    try:
                        protocol = int(float(row[field_index["protocol"]]))
                        if protocol not in {6, 17}:
                            counters["excluded_protocol_outside_official_tcp_udp"] += 1
                            continue
                        start = local_time(row[field_index["timestamp"]])
                        duration_us = max(0, int(float(row[field_index["duration"]])))
                        end = start + timedelta(microseconds=duration_us)
                        endpoints = frozenset(
                            (row[field_index["src_ip"]].strip(), row[field_index["dst_ip"]].strip())
                        )
                        if len(endpoints) != 2 or "" in endpoints:
                            counters["excluded_missing_five_tuple"] += 1
                            continue
                    except (IndexError, ValueError, OverflowError, OSError):
                        counters["excluded_invalid_flow_identity"] += 1
                        continue
                    matches = [
                        event
                        for event in events
                        if endpoints in event["endpoint_pairs"]
                        and event["start"] <= end
                        and event["end"] >= start
                    ]
                    if len(matches) > 1:
                        counters["conflicting_flows"] += 1
                        continue
                    counters["matched_flows"] += 1
                    if matches:
                        event = matches[0]
                        counters["malicious_flows"] += 1
                        fine_counts[event["fine_label"]] += 1
                        event_counts[str(event["event_index"])] += 1
                    else:
                        counters["benign_flows"] += 1
                        fine_counts["Benign"] += 1
        except Exception as error:
            counters["source_read_failures"] += 1
            counters[f"source_read_failure::{type(error).__name__}"] += 1
    payload = {
        "day": day_path.name,
        "generated_file_count": len(files),
        "counters": dict(sorted(counters.items())),
        "fine_label_counts": dict(sorted(fine_counts.items())),
        "event_match_counts": dict(sorted(event_counts.items(), key=lambda item: int(item[0]))),
    }
    atomic_json(Path(output_text), payload)
    return payload


def marker_values(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True, type=Path)
    parser.add_argument("--generated-root", required=True, type=Path)
    parser.add_argument("--archive-markers", required=True, type=Path)
    parser.add_argument("--per-day-dir", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    events = prepared_events(schedule)
    args.per_day_dir.mkdir(parents=True, exist_ok=True)
    days = sorted(path for path in args.generated_root.iterdir() if path.is_dir())
    tasks = [
        (str(day), events, str(args.per_day_dir / f"{day.name}.json")) for day in days
    ]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(audit_day, task) for task in tasks]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["day"])
    counters: Counter[str] = Counter()
    fine_counts: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    for result in results:
        counters.update(result["counters"])
        fine_counts.update(result["fine_label_counts"])
        event_counts.update(result["event_match_counts"])
    marker_audit = []
    for path in sorted(args.archive_markers.glob("*.complete")):
        values = marker_values(path)
        actual = next((item["generated_file_count"] for item in results if item["day"] == path.stem), -1)
        marker_audit.append(
            {
                "day": path.stem,
                "marker": str(path),
                "marker_sha256": sha256_file(path),
                "capture_members": int(values["capture_members"]),
                "flow_csvs": int(values["flow_csvs"]),
                "actual_flow_csvs": actual,
                "complete": int(values["capture_members"]) == int(values["flow_csvs"]) == actual,
                "archive": values["archive"],
            }
        )
    excluded = sum(value for key, value in counters.items() if key.startswith("excluded_"))
    retained = counters["total_flows"] - excluded - counters["conflicting_flows"]
    missing_events = [index for index in range(len(events)) if event_counts[str(index)] == 0]
    formal_gate = bool(
        len(marker_audit) == len(days) == 10
        and all(item["complete"] for item in marker_audit)
        and counters["source_read_failures"] == 0
        and counters["conflicting_flows"] == 0
        and counters["matched_flows"] == retained
        and not missing_events
    )
    summary = {
        "schema_version": "caeos_cicids2018_regenerated_full_capture_audit_v1",
        "dataset_id": "cicids2018",
        "scope": "full_frozen_capture_inventory_via_completed_cicflowmeter_member_replay",
        "authority_granularity": "official_endpoint_pair_and_attack_time_window",
        "schedule_path": str(args.schedule),
        "schedule_sha256": sha256_file(args.schedule),
        "processed_source_count": len(marker_audit),
        "source_count": len(days),
        "all_sources_complete": all(item["complete"] for item in marker_audit),
        "generated_file_count": sum(item["generated_file_count"] for item in results),
        "total_flows": counters["total_flows"],
        "matched_flows": counters["matched_flows"],
        "unmatched_flows": excluded,
        "conflicting_flows": counters["conflicting_flows"],
        "excluded_flows": excluded,
        "raw_coverage_fraction": counters["matched_flows"] / counters["total_flows"],
        "effective_coverage_fraction": counters["matched_flows"] / retained if retained else 0.0,
        "formal_label_gate_passed": formal_gate,
        "formal_label_gate_reason": None if formal_gate else "incomplete replay, conflict, read failure, or official event without a matching flow",
        "missing_event_indices": missing_events,
        "counters": dict(sorted(counters.items())),
        "fine_label_counts": dict(sorted(fine_counts.items())),
        "event_match_counts": dict(sorted(event_counts.items(), key=lambda item: int(item[0]))),
        "label_exclusion_summary": {
            "total_finalized_flows": counters["total_flows"],
            "excluded_flows": excluded,
            "excluded_flow_fraction": excluded / counters["total_flows"],
            "reason_counts": {
                key.removeprefix("excluded_"): value
                for key, value in sorted(counters.items())
                if key.startswith("excluded_")
            },
        },
        "archive_replay_markers": marker_audit,
        "per_day_audits": [str(args.per_day_dir / f"{item['day']}.json") for item in results],
    }
    atomic_json(args.summary_output, summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
