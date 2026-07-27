"""Audit UNSW-NB15 flow/ground-truth alignment without training a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs import MultiGranularityExtractor, PcapFileReader
from hft_mgbs.unsw import UnswGroundTruth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap", type=Path)
    parser.add_argument("ground_truth_csv", type=Path)
    parser.add_argument("--max-packets", type=int, default=20000)
    parser.add_argument("--max-payload-bytes", type=int, default=256)
    parser.add_argument("--tolerance-s", type=float, default=0.0)
    args = parser.parse_args()
    truth = UnswGroundTruth.from_csv(args.ground_truth_csv)
    extractor = MultiGranularityExtractor(max_completed_flows=500_000)
    first_packet_timestamp = None
    last_packet_timestamp = None
    with PcapFileReader(
        str(args.pcap), max_payload_bytes=args.max_payload_bytes
    ) as reader:
        for index, packet in enumerate(reader, 1):
            if first_packet_timestamp is None:
                first_packet_timestamp = packet.timestamp
            last_packet_timestamp = packet.timestamp
            extractor.update(packet)
            if args.max_packets and index >= args.max_packets:
                break
        pcap_stats = reader.stats
    records = extractor.flow_records()
    labels = [
        truth.label_flow_record(record, tolerance_s=args.tolerance_s)
        for record in records
    ]
    output = {
        "schema_version": 1,
        "scope": "unsw_alignment_audit",
        "pcap": str(args.pcap),
        "ground_truth_csv": str(args.ground_truth_csv),
        "max_packets": args.max_packets,
        "tolerance_s": args.tolerance_s,
        "packet_time_range": {
            "first": first_packet_timestamp,
            "last": last_packet_timestamp,
        },
        "pcap_stats": {
            "total_records": pcap_stats.total_records,
            "parsed_packets": pcap_stats.parsed_packets,
            "rejected_records": pcap_stats.rejected_records,
            "skipped_non_ip": pcap_stats.skipped_non_ip,
            "skipped_unsupported": pcap_stats.skipped_unsupported,
            "malformed_packets": pcap_stats.malformed_packets,
        },
        "ground_truth": {
            **truth.parse_stats,
            "indexed_key_count": truth.indexed_key_count,
        },
        "flows": {
            "total": len(records),
            "attack": sum(labels),
            "benign_unmatched": len(labels) - sum(labels),
            "attack_ratio": 0.0 if not labels else sum(labels) / len(labels),
        },
        "final_quality_eligible": False,
        "missing_final_evidence": [
            "alignment_recall_against_ground_truth_events",
            "full_holdout_extraction",
            "trained_candidate_evaluation",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
