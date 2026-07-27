from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_protocol(protocol: dict[str, Any], project_root: Path) -> None:
    if (
        protocol.get("schema_version")
        != "parrot2025_full_no_decryption_feature_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("formal_model_metric_count_at_freeze") != 0
    ):
        raise ValueError("invalid PARROT full feature protocol")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(f"PARROT full implementation changed: {relative}")


def validate_shard(
    *,
    protocol: dict[str, Any],
    capture: dict[str, Any],
    shard_root: Path,
) -> dict[str, Any]:
    manifest_path = shard_root / "manifest.json"
    csv_path = shard_root / "features.csv"
    manifest = load_json(manifest_path)
    if (
        manifest.get("schema_version")
        != "parrot2025_no_decryption_feature_shard_v1"
        or manifest.get("manifest_sha256") != canonical_hash(manifest)
        or manifest.get("protocol_manifest_sha256") != protocol["manifest_sha256"]
        or manifest.get("capture") != capture
        or manifest.get("features_csv_sha256") != file_hash(csv_path)
    ):
        raise ValueError(f"invalid PARROT feature shard: {shard_root}")
    frame = pd.read_csv(csv_path)
    expected_columns = protocol["feature_columns"] + protocol["metadata_columns"]
    if list(frame.columns) != expected_columns:
        raise ValueError(f"PARROT shard column contract failed: {shard_root}")
    if len(frame) != int(manifest["flow_row_count"]) or len(frame) == 0:
        raise ValueError(f"PARROT shard row count failed: {shard_root}")
    if set(frame[protocol["metadata_columns"][0]]) != {capture["member"]}:
        raise ValueError(f"PARROT capture group metadata failed: {shard_root}")
    if set(frame[protocol["metadata_columns"][1]]) != {capture["application"]}:
        raise ValueError(f"PARROT application metadata failed: {shard_root}")
    if set(frame[protocol["metadata_columns"][2]]) != {
        "benign_external_safety_only"
    }:
        raise ValueError(f"PARROT role metadata failed: {shard_root}")
    values = frame.loc[:, protocol["feature_columns"]].to_numpy(dtype=float)
    if any(not math.isfinite(float(value)) for value in values.ravel()):
        raise ValueError(f"PARROT non-finite feature failed: {shard_root}")
    return manifest


def summarize(
    *,
    protocol_path: Path,
    project_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    verify_protocol(protocol, project_root)
    expected = {capture["capture_id"]: capture for capture in protocol["captures"]}
    shards_root = output_root / "shards"
    observed = {
        path.parent.name: path.parent
        for path in shards_root.glob("*/manifest.json")
    }
    if set(observed) != set(expected):
        raise ValueError(
            "PARROT shard inventory mismatch: missing=%s extra=%s"
            % (sorted(set(expected) - set(observed)), sorted(set(observed) - set(expected)))
        )
    manifests = []
    for capture_id in sorted(expected):
        manifests.append(
            validate_shard(
                protocol=protocol,
                capture=expected[capture_id],
                shard_root=observed[capture_id],
            )
        )
    app_counts = Counter(item["capture"]["application"] for item in manifests)
    if len(app_counts) != 80 or set(app_counts.values()) != {4}:
        raise ValueError("PARROT validated shard application coverage failed")
    result: dict[str, Any] = {
        "schema_version": "parrot2025_full_no_decryption_feature_summary_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "capture_count": len(manifests),
        "application_count": len(app_counts),
        "flow_row_count": sum(int(item["flow_row_count"]) for item in manifests),
        "input_packet_count": sum(
            int(item["packet_accounting"]["input_packets"]) for item in manifests
        ),
        "converted_ip_packet_count": sum(
            int(item["packet_accounting"]["converted_ip_packets"])
            for item in manifests
        ),
        "skipped_non_ip_packet_count": sum(
            int(item["packet_accounting"]["skipped_non_ip_packets"])
            for item in manifests
        ),
        "malformed_packet_count": sum(
            int(item["packet_accounting"]["malformed_packets"]) for item in manifests
        ),
        "feature_count": protocol["feature_count"],
        "shard_manifest_sha256": {
            item["capture"]["capture_id"]: item["manifest_sha256"]
            for item in manifests
        },
        "safety_audit": protocol["safety_policy"],
        "validation": {
            "all_320_captures_present": len(manifests) == 320,
            "all_80_applications_have_four_captures": (
                len(app_counts) == 80 and set(app_counts.values()) == {4}
            ),
            "all_shards_canonical_and_hash_bound": True,
            "all_rows_match_exact_56_feature_contract": (
                protocol["feature_count"] == 56
            ),
            "all_feature_values_finite": True,
            "malformed_packet_count_zero": all(
                int(item["packet_accounting"]["malformed_packets"]) == 0
                for item in manifests
            ),
            "no_forbidden_data_or_model_use": all(
                value is False or (key == "ssl_key_members_read" and value == 0)
                for key, value in protocol["safety_policy"].items()
            ),
        },
        "claim_boundary": protocol["claim_boundary"],
    }
    result["passed"] = all(result["validation"].values())
    result["manifest_sha256"] = canonical_hash(result)
    output_path = output_root / "feature_shard_manifest.json"
    temporary = output_root / f".feature_shard_manifest.json.{os.getpid()}.tmp"
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(output_path)
    if result["passed"]:
        (output_root / "full_feature_extraction_complete").touch()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(
        protocol_path=args.protocol,
        project_root=args.project_root,
        output_root=args.output_root,
    )
    print(
        json.dumps(
            {
                "passed": result["passed"],
                "captures": result["capture_count"],
                "rows": result["flow_row_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
