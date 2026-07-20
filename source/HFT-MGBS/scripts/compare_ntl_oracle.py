"""Compare HFT flow semantics with an isolated NTLFlowLyzer CSV oracle."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


PROTOCOLS = {"TCP": 6, "UDP": 17, "6": 6, "17": 17}
FIELDS = {
    "packets_count": ("flow_packets", 0.0),
    "fwd_packets_count": ("flow_fwd_packets", 0.0),
    "bwd_packets_count": ("flow_bwd_packets", 0.0),
    "total_payload_bytes": ("flow_payload_bytes", 0.0),
    "fwd_total_payload_bytes": ("flow_fwd_payload_bytes", 0.0),
    "bwd_total_payload_bytes": ("flow_bwd_payload_bytes", 0.0),
    "duration": ("flow_duration_s", 1e-6),
    "packets_IAT_mean": ("flow_mean_iat_s", 1e-6),
    "packet_IAT_std": ("flow_iat_std_s", 1e-6),
    "fwd_packets_IAT_mean": ("flow_fwd_mean_iat_s", 1e-6),
    "fwd_packets_IAT_std": ("flow_fwd_iat_std_s", 1e-6),
    "bwd_packets_IAT_mean": ("flow_bwd_mean_iat_s", 1e-6),
    "bwd_packets_IAT_std": ("flow_bwd_iat_std_s", 1e-6),
}
for _flag in ("fin", "psh", "urg", "ece", "syn", "ack", "cwr", "rst"):
    FIELDS["{}_flag_counts".format(_flag)] = (
        "flow_{}_flag_count".format(_flag), 0.0
    )
    FIELDS["fwd_{}_flag_counts".format(_flag)] = (
        "flow_fwd_{}_flag_count".format(_flag), 0.0
    )
    FIELDS["bwd_{}_flag_counts".format(_flag)] = (
        "flow_bwd_{}_flag_count".format(_flag), 0.0
    )


def ntl_key(row):
    protocol = PROTOCOLS.get(row["protocol"].upper())
    if protocol is None:
        raise ValueError("unsupported NTL protocol {}".format(row["protocol"]))
    return (
        row["src_ip"], row["dst_ip"], int(row["src_port"]), int(row["dst_port"]), protocol
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("hft_json", type=Path)
    parser.add_argument("ntl_csv", type=Path)
    parser.add_argument("--ntl-manifest", type=Path)
    args = parser.parse_args()
    with args.hft_json.open("r", encoding="utf-8") as handle:
        hft = json.load(handle)
    oracle_status = "unknown"
    if args.ntl_manifest:
        with args.ntl_manifest.open("r", encoding="utf-8") as handle:
            oracle_status = json.load(handle).get("status", "unknown")

    hft_groups = defaultdict(list)
    for record in hft["flows"]:
        hft_groups[tuple(record["forward_key"])].append(record)
    ntl_groups = defaultdict(list)
    with args.ntl_csv.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        for row in csv.DictReader(handle):
            ntl_groups[ntl_key(row)].append(row)

    all_keys = set(hft_groups) | set(ntl_groups)
    equal_count_keys = {
        key for key in all_keys if len(hft_groups[key]) == len(ntl_groups[key])
    }
    mismatched_keys = [
        {
            "key": list(key),
            "hft_flows": len(hft_groups[key]),
            "ntl_flows": len(ntl_groups[key]),
        }
        for key in sorted(all_keys)
        if key not in equal_count_keys
    ]
    field_stats = {
        name: {"compared": 0, "matched": 0, "max_abs_error": 0.0, "mismatch_samples": []}
        for name in FIELDS
    }
    for key in equal_count_keys:
        hft_rows = sorted(hft_groups[key], key=lambda item: item["start_timestamp"])
        ntl_rows = sorted(ntl_groups[key], key=lambda item: item["timestamp"])
        for hft_row, ntl_row in zip(hft_rows, ntl_rows):
            features = hft_row["features"]
            for ntl_name, (hft_name, tolerance) in FIELDS.items():
                if ntl_name not in ntl_row or ntl_row[ntl_name] == "":
                    continue
                left = float(ntl_row[ntl_name])
                right = float(features[hft_name])
                error = abs(left - right)
                stats = field_stats[ntl_name]
                stats["compared"] += 1
                stats["matched"] += int(error <= tolerance)
                stats["max_abs_error"] = max(stats["max_abs_error"], error)
                if error > tolerance and len(stats["mismatch_samples"]) < 5:
                    stats["mismatch_samples"].append(
                        {
                            "key": list(key),
                            "ntl": left,
                            "hft": right,
                            "start_timestamp": hft_row["start_timestamp"],
                        }
                    )

    for stats in field_stats.values():
        stats["match_ratio"] = (
            0.0 if stats["compared"] == 0 else stats["matched"] / stats["compared"]
        )
    flow_counts_equal = len(hft["flows"]) == sum(len(rows) for rows in ntl_groups.values())
    all_fields_exact = all(
        stats["compared"] > 0 and stats["matched"] == stats["compared"]
        for stats in field_stats.values()
    )
    output = {
        "schema_version": 1,
        "scope": "diagnostic_oracle_comparison",
        "oracle_status": oracle_status,
        "hft_flow_count": len(hft["flows"]),
        "ntl_flow_count": sum(len(rows) for rows in ntl_groups.values()),
        "flow_counts_equal": flow_counts_equal,
        "equal_count_key_groups": len(equal_count_keys),
        "mismatched_key_group_count": len(mismatched_keys),
        "mismatched_key_groups_sample": mismatched_keys[:20],
        "field_stats": field_stats,
        "accepted": oracle_status == "complete" and flow_counts_equal and all_fields_exact,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
