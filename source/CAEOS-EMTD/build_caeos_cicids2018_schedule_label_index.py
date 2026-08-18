from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file


def timestamp_ns(value: str, timezone: ZoneInfo) -> int:
    parsed = datetime.strptime(value, "%Y-%m-%d %H:%M").replace(tzinfo=timezone)
    return int(parsed.timestamp() * 1_000_000_000)


def build(schedule_path: Path, registry: Path, output_index: Path, audit: Path) -> dict:
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    timezone = ZoneInfo(schedule["timezone"])
    records = []
    for event_index, event in enumerate(schedule["events"]):
        start_ns = timestamp_ns(event["start"], timezone)
        end_ns = timestamp_ns(event["end"], timezone)
        for attacker in event["attackers"]:
            for victim in event["victims"]:
                for protocol in (6, 17):
                    record_id = hashlib.sha256(
                        f"{event_index}\0{attacker}\0{victim}\0{protocol}".encode("ascii")
                    ).hexdigest()
                    records.append(
                        {
                            "record_id": record_id,
                            "src_ip": attacker,
                            "dst_ip": victim,
                            "src_port": None,
                            "dst_port": None,
                            "protocol": protocol,
                            "start_ns": start_ns,
                            "end_ns": end_ns,
                            "fine_label": event["fine_label"],
                            "family_label": event["family_label"],
                            "binary_label": 1,
                            "label_source": f"{schedule['authority_url']}#table-2-event-{event_index + 1}",
                        }
                    )
    for protocol in (6, 17):
        records.append(
            {
                "record_id": f"official-schedule-benign-fallback-{protocol}",
                "source_member": None,
                "protocol": protocol,
                "start_ns": timestamp_ns(schedule["benign_start"], timezone),
                "end_ns": timestamp_ns(schedule["benign_end"], timezone),
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": f"{schedule['authority_url']}#non-attack-schedule-traffic",
            }
        )
    label_index = create_label_index(
        output_index, "cicids2018", records, sha256_file(registry)
    )
    payload = {
        "schema_version": "caeos_cicids2018_schedule_label_index_audit_v1",
        "dataset_id": "cicids2018",
        "authority": "official_attack_schedule_endpoint_and_time_rules",
        "authority_url": schedule["authority_url"],
        "schedule_path": str(schedule_path),
        "schedule_sha256": sha256_file(schedule_path),
        "timezone": schedule["timezone"],
        "event_count": len(schedule["events"]),
        "endpoint_time_rule_count": len(records) - 2,
        "admitted_protocols": [6, 17],
        "fine_label_counts": dict(sorted(Counter(x["fine_label"] for x in records).items())),
        "family_label_counts": dict(sorted(Counter(x["family_label"] for x in records).items())),
        "benign_fallback_scope": [schedule["benign_start"], schedule["benign_end"]],
        "label_index": label_index,
    }
    atomic_json(audit, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.schedule, args.registry, args.output_index, args.audit_output), sort_keys=True))


if __name__ == "__main__":
    main()
