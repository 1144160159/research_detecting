from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake", required=True, type=Path)
    parser.add_argument("--flowmeter-jar", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def build(args: argparse.Namespace) -> dict[str, Any]:
    intake = json.loads(args.intake.read_text(encoding="utf-8"))
    record = next(
        item for item in intake["datasets"] if item["dataset_id"] == "cicids2018"
    )
    if record["label_intake_passed"] is not True:
        raise ValueError("CICIDS2018 intake gates did not pass")
    if not args.flowmeter_jar.is_file():
        raise FileNotFoundError(args.flowmeter_jar)
    payload: dict[str, Any] = {
        "schema_version": "caeos_cicids2018_label_regeneration_protocol_v1",
        "dataset_id": "cicids2018",
        "state": "queued_exact_flow_identity_regeneration",
        "source_intake": str(args.intake),
        "source_intake_manifest_sha256": intake["manifest_sha256"],
        "flowmeter_jar": str(args.flowmeter_jar),
        "flowmeter_jar_sha256": hashlib.sha256(args.flowmeter_jar.read_bytes()).hexdigest(),
        "input_pcap_archive_count": record["pcap_archive_count"],
        "input_pcap_archive_size_bytes": record["pcap_archive_size_bytes"],
        "official_flow_csv_count": record["official_flow_csv_count"],
        "official_flow_rows_including_repeated_headers": record[
            "official_flow_rows_including_repeated_headers"
        ],
        "timezone_contract": {
            "pcap_epoch": "UTC",
            "official_csv_and_attack_schedule": "fixed UTC-04:00",
            "flowmeter_jvm_option": "-Duser.timezone=Etc/GMT+4",
        },
        "join_contract": {
            "regenerate_identity_columns": [
                "Flow ID", "Src IP", "Src Port", "Dst IP", "Dst Port",
                "Protocol", "Timestamp", "Flow Duration",
            ],
            "official_dimensions": [
                "attack schedule", "attacker IP", "victim IP", "port", "protocol",
            ],
            "repeated_csv_header_rows": "exclude_with_explicit_counter",
            "ambiguous_or_unmatched_rows": "exclude_and_fail_formal_gate",
            "whole_attack_day_labeling": "forbidden",
            "whole_attack_time_window_without_endpoint_match": "forbidden",
        },
        "truncated_capture_policy": "exclude_only_truncated_boundary_flows_and_retain_complete_flows",
        "feature_extraction_started": False,
        "feature_admission": "blocked_until_regenerated_label_index_and_full_pcap_audit_pass",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["protocol_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    atomic_json(args.output, payload)
    return payload


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
