#!/usr/bin/env python3
"""Audit CICDDoS2019 capture markers against the currently frozen policy.

This is intentionally read-only.  It validates every referenced part before
reporting whether marker reuse can be recovered by a metadata-only migration.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from caeos_label_alignment import label_index_registry_sha256
from caeos_unified_dataset import canonical_json_hash, sha256_file
from prepare_caeos_splitpcap_class_csv_legacy_cicddos import (
    capture_identity,
    capture_member_allowlist,
    capture_processing_policy,
    dataset_pcap_repair_policy,
    load_json,
    load_pcap_repairs,
    processing_policy,
    select_capture_candidates,
    source_member_name,
)
from prepare_caeos_unified_multimodal_csv_legacy_cicddos import tshark_identity


def changed_paths(left: Any, right: Any, prefix: str = "") -> set[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        paths: set[str] = set()
        for key in sorted(set(left) | set(right)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in left or key not in right:
                paths.add(path)
            else:
                paths.update(changed_paths(left[key], right[key], path))
        return paths
    if isinstance(left, list) and isinstance(right, list):
        if left == right:
            return set()
        return {prefix}
    return set() if left == right else {prefix}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--label-index-manifest", required=True, type=Path)
    parser.add_argument("--pcap-repair-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--splitpcap-binary", required=True, type=Path)
    parser.add_argument("--splitpcap-commit", default="fca18e270fe4")
    parser.add_argument("--target-piece-bytes", type=int, default=128 * 1024 * 1024)
    parser.add_argument("--maximum-active-flows", type=int, default=6000)
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    parser.add_argument("--tshark-session-reset-packets", type=int, default=0)
    parser.add_argument("--frozen-repair-manifest-sha256")
    parser.add_argument("--find-capture-id")
    return parser.parse_args()


def build_expected(
    args: argparse.Namespace,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    list[tuple[dict[str, Any], str | None]],
    dict[str, dict[str, Any]],
]:
    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    source_manifest = load_json(args.source_manifest)
    label_manifest = load_json(args.label_index_manifest)
    repairs, repair_manifest_sha256 = load_pcap_repairs(args.pcap_repair_manifest)
    dataset = next(item for item in catalog["datasets"] if item["id"] == "cicddos2019")
    source_dataset = next(
        item for item in source_manifest["datasets"] if item["id"] == "cicddos2019"
    )
    alignment = next(
        item for item in label_manifest["datasets"] if item["id"] == "cicddos2019"
    )
    preprocessor = Path(__file__).resolve().parents[1] / "prepare_caeos_unified_multimodal_csv_legacy_cicddos.py"
    policy = processing_policy(
        catalog["feature_reservoir"],
        args.maximum_active_flows,
        "tshark",
        tshark_identity(args.tshark_binary),
        args.tshark_session_reset_packets,
        sha256_file(preprocessor),
        args.splitpcap_binary,
        args.splitpcap_commit,
        args.target_piece_bytes,
    )
    policy["pcap_repair_manifest_sha256"] = (
        args.frozen_repair_manifest_sha256 or repair_manifest_sha256
    )
    policy["label_alignment"] = {
        "path": str(Path(alignment["path"])),
        "sha256": alignment["sha256"],
        "record_count": int(alignment["record_count"]),
        "registry_sha256": label_index_registry_sha256(
            Path(alignment["path"]), "cicddos2019"
        ),
        "tolerance_ns": int(alignment.get("tolerance_ns", 0)),
        "conflict_policy": str(alignment.get("conflict_policy", "reject")),
        "time_nonoverlap_policy": str(
            alignment.get("time_nonoverlap_policy", "reject")
        ),
        "official_boundary_split": bool(
            alignment.get("official_boundary_split", False)
        ),
        "external_label_precedence": bool(
            alignment.get("external_label_precedence", False)
        ),
        "maximum_excluded_packet_fraction": float(
            alignment.get("maximum_excluded_packet_fraction", 1.0)
        ),
        "drop_unmatched_reasons": sorted(
            alignment.get("drop_unmatched_reasons", [])
        ),
        "label_exclusion_rule_version": "caeos_label_exclusion_v1",
        "required_status_prefix": "aligned_unique_",
        "unmatched_allowed": 0,
        "conflicts_allowed": 0,
    }
    allowlist = capture_member_allowlist(alignment, "cicddos2019")
    if allowlist is not None:
        policy["capture_member_inventory_scope"] = {
            "rule": "schedule_only_members_present_in_formal_capture_label_index",
            "source_member_count": len(allowlist),
            "source_member_sha256": canonical_json_hash(sorted(allowlist)),
        }
    _, dataset_repairs = dataset_pcap_repair_policy(repairs, "cicddos2019")
    selected, _ = select_capture_candidates(dataset, source_dataset, allowlist)
    return schema, policy, selected, dataset_repairs


def main() -> None:
    args = parse_args()
    schema, policy, selected, repairs = build_expected(args)
    schema_sha256 = canonical_json_hash(schema)
    marker_root = args.output_root / "_captures" / "cicddos2019"
    expected_ids = {
        capture_identity(source["path"], member): (source, member)
        for source, member in selected
    }
    if args.find_capture_id:
        source_member = expected_ids.get(args.find_capture_id)
        if source_member is None:
            raise ValueError(f"capture is not scheduled: {args.find_capture_id}")
        source, member = source_member
        print(
            json.dumps(
                {
                    "capture_id": args.find_capture_id,
                    "source": source,
                    "source_member": member,
                    "repair": repairs.get(args.find_capture_id),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return
    marker_paths = sorted(marker_root.glob("*.json"))
    marker_hashes: Counter[str] = Counter()
    expected_hashes: Counter[str] = Counter()
    policy_diff_paths: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []
    compatible = 0
    repaired = 0
    for marker_path in marker_paths:
        marker = load_json(marker_path)
        capture_id = marker_path.stem
        source_member = expected_ids.get(capture_id)
        if source_member is None:
            errors.append({"capture_id": capture_id, "reason": "not_in_current_schedule"})
            continue
        source, member = source_member
        repair = repairs.get(capture_id)
        effective_policy = capture_processing_policy(policy, repair)
        expected_hash = canonical_json_hash(effective_policy)
        expected_hashes[expected_hash] += 1
        parts = marker.get("parts", [])
        if not marker.get("complete") or not parts:
            errors.append({"capture_id": capture_id, "reason": "invalid_marker"})
            continue
        marker_policy_set = {
            str(part.get("processing_policy_sha256")) for part in parts
        }
        if len(marker_policy_set) != 1:
            errors.append({"capture_id": capture_id, "reason": "mixed_marker_policy"})
            continue
        marker_hash = next(iter(marker_policy_set))
        marker_hashes[marker_hash] += 1
        marker_error = None
        for part in parts:
            part_path = Path(part["part_path"])
            if not part_path.is_file():
                marker_error = f"missing_part:{part_path}"
                break
            if sha256_file(part_path) != part["part_sha256"]:
                marker_error = f"part_sha256_mismatch:{part_path}"
                break
            if part.get("schema_sha256") != schema_sha256:
                marker_error = "schema_sha256_mismatch"
                break
            embedded_policy = part.get("processing_policy")
            if not isinstance(embedded_policy, dict):
                marker_error = "embedded_processing_policy_missing"
                break
            if canonical_json_hash(embedded_policy) != marker_hash:
                marker_error = "embedded_processing_policy_hash_mismatch"
                break
            for path in changed_paths(embedded_policy, effective_policy):
                policy_diff_paths[path] += 1
        if marker_error:
            errors.append({"capture_id": capture_id, "reason": marker_error})
            continue
        marker_repair = marker.get("pcap_repair")
        if bool(marker_repair) != bool(repair):
            errors.append({"capture_id": capture_id, "reason": "repair_presence_mismatch"})
            continue
        if repair:
            repaired += 1
            repair_keys = (
                "source_path",
                "source_member",
                "original_sha256",
                "repaired_sha256",
                "repair_mode",
            )
            if any(marker_repair.get(key) != repair.get(key) for key in repair_keys):
                errors.append({"capture_id": capture_id, "reason": "repair_identity_mismatch"})
                continue
        compatible += 1
    report = {
        "schema_version": "caeos_cicddos2019_marker_compatibility_audit_v1",
        "dataset_id": "cicddos2019",
        "scheduled_capture_count": len(expected_ids),
        "marker_count": len(marker_paths),
        "verified_content_compatible_marker_count": compatible,
        "verified_repaired_marker_count": repaired,
        "marker_processing_policy_sha256_counts": dict(sorted(marker_hashes.items())),
        "current_expected_processing_policy_sha256_counts": dict(
            sorted(expected_hashes.items())
        ),
        "processing_policy_changed_path_part_counts": dict(
            sorted(policy_diff_paths.items())
        ),
        "base_policy": policy,
        "base_policy_sha256": canonical_json_hash(policy),
        "errors": errors,
        "error_count": len(errors),
        "metadata_only_policy_migration_candidate": (
            compatible == len(marker_paths) and not errors
        ),
    }
    report["report_sha256"] = canonical_json_hash(report)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
