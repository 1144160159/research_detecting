"""Export bounded HFT-MGBS flow records for correctness-oracle comparison."""

from __future__ import annotations

import argparse
import json

from hft_mgbs import MultiGranularityExtractor, PcapFileReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    parser.add_argument("--max-packets", type=int, default=0)
    parser.add_argument("--max-payload-bytes", type=int, default=256)
    parser.add_argument("--activity-timeout-s", type=float, default=300.0)
    parser.add_argument("--max-flow-duration-s", type=float, default=120.0)
    args = parser.parse_args()
    extractor = MultiGranularityExtractor(
        activity_timeout_s=args.activity_timeout_s,
        max_flow_duration_s=args.max_flow_duration_s,
    )
    with PcapFileReader(args.pcap, max_payload_bytes=args.max_payload_bytes) as reader:
        for index, packet in enumerate(reader, 1):
            extractor.update(packet)
            if args.max_packets and index >= args.max_packets:
                break
        stats = reader.stats
    output = {
        "schema_version": 1,
        "source": args.pcap,
        "flow_semantics": {
            "direction": "first_packet_defines_forward",
            "activity_timeout_s": args.activity_timeout_s,
            "max_flow_duration_s": args.max_flow_duration_s,
            "close_policy": "two_sided_fin_or_rst_then_roll_on_next_packet",
        },
        "pcap": {
            "total_records": stats.total_records,
            "parsed_packets": stats.parsed_packets,
            "rejected_records": stats.rejected_records,
        },
        "flow_count": extractor.completed_flow_count + extractor.active_flow_count,
        "flows": extractor.flow_records(),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
