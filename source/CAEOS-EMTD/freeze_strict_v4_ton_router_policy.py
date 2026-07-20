from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_strict_v4_validation_router import REFERENCE, UNKNOWN_METRICS, canonical_hash


def build_manifest(
    source_manifest: dict[str, Any],
    source_confirmation: dict[str, Any],
    source_manifest_sha256: str,
    source_confirmation_sha256: str,
) -> dict[str, Any]:
    if source_manifest.get("schema_version") != "strict_v4_validation_suite_router_candidate_v1":
        raise ValueError("unexpected source suite-router manifest")
    if source_manifest.get("manifest_sha256") != canonical_hash(source_manifest):
        raise ValueError("source suite-router manifest hash mismatch")
    if source_confirmation.get("manifest_sha256") != source_manifest["manifest_sha256"]:
        raise ValueError("source confirmation does not match source manifest")
    ton = source_confirmation.get("by_suite", {}).get("cic_ton_iot", {})
    metrics = ton.get("metrics", {})
    if not all(
        metrics.get(metric, {}).get("oriented_mean_improvement", 0.0) > 0.0
        for metric in UNKNOWN_METRICS
    ):
        raise ValueError("source ToN router did not improve all four unknown metrics")
    ton_rule = source_manifest["candidate"]["selected_rules"]["cic_ton_iot"]
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_ton_router_partial_policy_candidate_v1",
        "status": "frozen_unconfirmed",
        "frozen_before_confirmation": True,
        "candidate": {
            "name": "strict_v4_ton_validation_router_cic_fallback_v1",
            "suite_policy": {
                "cic_ton_iot": {"kind": "validation_router", "rule": ton_rule},
                "cic_iot2023": {"kind": "fixed_fallback", "risk": REFERENCE},
            },
            "runtime_features_use_known_validation_only": True,
            "runtime_routing_uses_known_suite_identity": True,
            "router_implementation_sha256": source_manifest["candidate"][
                "implementation_sha256"
            ],
        },
        "development": {
            "source_suite_router_manifest_file_sha256": source_manifest_sha256,
            "source_suite_router_manifest_internal_sha256": source_manifest[
                "manifest_sha256"
            ],
            "source_suite_router_confirmation_sha256": source_confirmation_sha256,
            "partial_policy_selection_uses_opened_confirmation_labels": True,
            "source_overall_gate_passed": source_confirmation["decision"]["passes"],
            "source_ton_all_four_means_positive": True,
            "cic_iot2023_forced_exact_fallback": True,
        },
        "confirmation": {
            "seeds": [67, 71],
            "scenarios": {
                "cic_ton_iot": [
                    "backdoor",
                    "ddos",
                    "dos",
                    "injection",
                    "mitm",
                    "password",
                    "ransomware",
                    "scanning",
                    "xss",
                ]
            },
            "expected_run_count": 18,
            "seed_disjoint": True,
            "scenario_boundary": "all ToN-IoT attack scenarios cross-seed replication",
        },
        "confirmation_gate": {
            "unit": "scenario mean across confirmation seeds",
            "all_four_unknown_metric_means_positive": True,
            "unknown_auroc_bootstrap_ci_lower_gt_zero": True,
            "unknown_aupr_nonregression_tolerance": 0.01,
            "unknown_fpr95_oriented_nonregression_tolerance": 0.01,
            "oscr_nonregression_tolerance": 0.01,
            "both_endpoints_must_be_exercised": True,
            "fallback": REFERENCE,
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze ToN-only router with exact CIC fallback")
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--source-confirmation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_raw = args.source_manifest.read_bytes()
    confirmation_raw = args.source_confirmation.read_bytes()
    manifest = build_manifest(
        json.loads(manifest_raw.decode("utf-8")),
        json.loads(confirmation_raw.decode("utf-8")),
        hashlib.sha256(manifest_raw).hexdigest(),
        hashlib.sha256(confirmation_raw).hexdigest(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest_sha256": manifest["manifest_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
