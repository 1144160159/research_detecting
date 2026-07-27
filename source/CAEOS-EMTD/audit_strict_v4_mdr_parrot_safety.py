from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_mdr_parrot_safety import aggregate, load


AGGREGATE_KEYS = (
    "model_pair_count",
    "capture_count",
    "application_count",
    "failure_count",
    "capture_blocks",
    "application_records",
    "applications_with_false_alert_rate_at_most_0_20_fraction",
    "capture_block_inference",
    "candidate_minus_source_benign_inference",
    "source_benign_model_reference_values",
    "confirmation_checks",
    "safety_gate_passes",
)


def evaluate_audit(
    *,
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    recomputed: Dict[str, Any],
    implementation_hashes_match: bool,
    metrics_hashes_match: bool,
    feature_shards_match: bool,
) -> Dict[str, Any]:
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version")
            == "strict_v4_mdr_parrot_safety_protocol_v1"
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version")
            == "strict_v4_mdr_parrot_safety_summary_v1"
            and summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "summary_binds_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "all_30_model_pair_metrics_bound_by_hash": metrics_hashes_match,
        "all_320_feature_shards_remain_hash_bound": feature_shards_match,
        "implementation_hashes_match": implementation_hashes_match,
        "independent_recomputation_exact": all(
            summary.get(key) == recomputed.get(key)
            for key in AGGREGATE_KEYS
        ),
        "parrot_not_used_for_fit_selection_calibration_or_threshold": all(
            item.get(
                "parrot_features_or_labels_used_for_fit_selection_"
                "calibration_or_threshold"
            )
            is False
            for item in recomputed.get("_records", [])
        ),
        "payload_decryption_not_used": all(
            item.get("payload_decryption_used") is False
            for item in recomputed.get("_records", [])
        ),
    }
    integrity = all(checks.values())
    safety = bool(recomputed.get("safety_gate_passes"))
    return {
        "checks": checks,
        "passes": integrity,
        "benign_domain_shift_safety_gate_passes": integrity and safety,
        "claim_boundary": {
            "cross_domain_benign_false_alert_safety_noninferiority_supported": (
                integrity and safety
            ),
            "malicious_detection_accuracy_claim_supported_by_this_audit": False,
            "parrot_accuracy_or_sota_claim_supported": False,
            "malicious_external_confirmation_still_required": True,
        },
    }


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    project_root: Path,
    run_root: Path,
) -> Dict[str, Any]:
    registry = {
        (str(item["scenario"]), int(item["training_seed"])): item
        for item in summary.get("model_pair_metrics_file_registry", [])
    }
    records = []
    metrics_hashes_match = True
    for source in protocol.get("source_model_pairs", []):
        identity = (
            str(source["scenario"]),
            int(source["training_seed"]),
        )
        path = (
            run_root
            / "evaluations"
            / identity[0]
            / f"seed{identity[1]}"
            / "model_pair_metrics.json"
        )
        if (
            not path.is_file()
            or identity not in registry
            or file_hash(path) != registry[identity].get("metrics_file_sha256")
        ):
            metrics_hashes_match = False
            continue
        records.append(load(path))
    implementation_hashes_match = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    feature_shards_match = True
    feature_root = Path(protocol.get("feature_root", ""))
    for capture in protocol.get("parrot_captures", []):
        capture_id = str(capture["capture_id"])
        path = feature_root / "shards" / capture_id / "manifest.json"
        if not path.is_file():
            feature_shards_match = False
            break
        value = load(path)
        if (
            value.get("manifest_sha256") != canonical_hash(value)
            or value.get("manifest_sha256")
            != protocol["feature_shard_manifest_sha256"].get(capture_id)
        ):
            feature_shards_match = False
            break
    try:
        recomputed = aggregate(records, protocol)
    except (KeyError, TypeError, ValueError):
        recomputed = {}
    recomputed["_records"] = records
    evaluated = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=implementation_hashes_match,
        metrics_hashes_match=(
            metrics_hashes_match
            and len(records) == 30
            and len(registry) == 30
        ),
        feature_shards_match=feature_shards_match,
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_parrot_safety_audit_v1",
        "protocol_manifest_sha256": protocol.get("manifest_sha256"),
        "summary_manifest_sha256": summary.get("manifest_sha256"),
        **evaluated,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol),
        load(args.summary),
        args.project_root,
        args.run_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
