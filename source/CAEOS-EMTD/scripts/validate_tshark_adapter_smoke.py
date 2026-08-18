from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from caeos_unified_dataset import canonical_json_hash, sha256_file
from prepare_caeos_unified_multimodal_csv import process_capture, tshark_identity


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    parser.add_argument("--tshark-session-reset-packets", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    columns = [item["name"] for item in schema["columns"]]
    identity = tshark_identity(args.tshark_binary)
    part = args.output_root / "real_fragment_sample.part"
    metadata = process_capture(
        {
            "dataset": {
                "id": "ciciot2023",
                "priority": "P0",
                "role": "main_development_and_known_classification",
                "source_root": str(args.capture.parent),
                "label_policy": "relative_attack_directory",
                "label_binding": "capture_path",
            },
            "path": str(args.capture),
            "member": None,
            "source_member_override": (
                "DDoS-ICMP_Fragmentation/real_fragment_sample.pcap"
            ),
            "capture_id": "tshark-real-fragment-smoke",
            "source_sha256": sha256_file(args.capture),
            "part_path": str(part),
            "schema_sha256": canonical_json_hash(schema),
            "columns": columns,
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 1000,
            "packet_decoder": "tshark",
            "tshark_binary": args.tshark_binary,
            "packet_decoder_identity": identity,
            "tshark_session_reset_packets": args.tshark_session_reset_packets,
        }
    )
    matched = []
    with part.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, fieldnames=columns):
            offsets = [int(value) for value in row["ip_fragment_offset_seq"].split(";")]
            headers = [
                int(value) for value in row["transport_header_length_seq"].split(";")
            ]
            payloads = [
                int(value) for value in row["packet_payload_length_seq"].split(";")
            ]
            for offset, header, payload in zip(offsets, headers, payloads):
                if offset == 1480:
                    matched.append(
                        {"offset_bytes": offset, "l4_header_bytes": header, "payload_bytes": payload}
                    )
    assert matched, "real sample contains no decoded 1480-byte fragment offset"
    assert any(
        item["l4_header_bytes"] == 0 and item["payload_bytes"] == 328
        for item in matched
    ), matched
    assert metadata["packet_decoder_identity"] == identity
    assert metadata["processing_policy_sha256"]
    print(
        json.dumps(
            {
                "status": "passed",
                "packet_decoder_identity": identity,
                "part_sha256": metadata["part_sha256"],
                "rows": metadata["counters"]["rows"],
                "matched_fragments": matched,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
