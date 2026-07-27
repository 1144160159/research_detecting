from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from summarize_strict_v4_mdr_evidence_reuse import (
    aggregate_captures,
    load,
)


def evaluate_audit(
    *,
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    recomputed: Dict[str, Any],
    implementation_hashes_match: bool,
    capture_hashes_match: bool,
    artifact_hashes_match: bool,
) -> Dict[str, Any]:
    aggregate_keys = (
        "capture_count",
        "scenario_block_count",
        "condition_count",
        "failure_count",
        "scenario_blocks",
        "raw_per_capture_ratios",
        "ratio_inference",
        "integrity_decision",
        "deployment_substitution_decision",
        "latency_improvement_over_original_decision",
        "strict_efficiency_vs_pairwise_diagnostic",
        "execution_context",
    )
    records = recomputed.get("_records", [])
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version")
            == "strict_v4_mdr_evidence_reuse_protocol_v1"
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version")
            == "strict_v4_mdr_evidence_reuse_summary_v1"
            and summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "summary_binds_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "all_306_captures_bound_by_hash": capture_hashes_match,
        "all_serialized_artifacts_bound_by_hash": artifact_hashes_match,
        "implementation_hashes_match": implementation_hashes_match,
        "independent_recomputation_exact": all(
            summary.get(key) == recomputed.get(key)
            for key in aggregate_keys
        ),
        "all_1836_conditions_pass_equivalence": (
            recomputed.get("condition_count") == 1836
            and all(
                record.get("equivalence", {}).get("all_direct_pass")
                is True
                and record.get("equivalence", {}).get(
                    "all_serialization_pass"
                )
                is True
                for record in records
            )
        ),
        "unknown_or_test_labels_not_used": all(
            record.get("unknown_or_test_labels_used") is False
            and record.get("equivalence", {}).get("labels_loaded") is False
            for record in records
        ),
        "fit_cost_not_claimed_reduced": all(
            record.get("fit_cost", {}).get(
                "unchanged_by_inference_optimization"
            )
            is True
            for record in records
        ),
    }
    audit_integrity = all(checks.values())
    recomputed_integrity = bool(
        recomputed.get("integrity_decision", {}).get("passes")
    )
    substitution = bool(
        recomputed.get("deployment_substitution_decision", {}).get(
            "passes"
        )
    )
    latency = bool(
        recomputed.get(
            "latency_improvement_over_original_decision", {}
        ).get("passes")
    )
    pairwise = bool(
        recomputed.get(
            "strict_efficiency_vs_pairwise_diagnostic", {}
        ).get("passes")
    )
    return {
        "checks": checks,
        "passes": audit_integrity and recomputed_integrity,
        "deployment_substitution_gate_passes": (
            audit_integrity and recomputed_integrity and substitution
        ),
        "latency_improvement_over_original_gate_passes": (
            audit_integrity
            and recomputed_integrity
            and substitution
            and latency
        ),
        "strict_efficiency_vs_pairwise_diagnostic_passes": (
            audit_integrity
            and recomputed_integrity
            and substitution
            and pairwise
        ),
        "claim_tiers": {
            "optimized_runtime_is_effect_equivalent_and_deployable": (
                audit_integrity and recomputed_integrity and substitution
            ),
            "optimized_runtime_improves_all_frozen_inference_axes": (
                audit_integrity
                and recomputed_integrity
                and substitution
                and latency
            ),
            "fit_cost_is_unchanged": True,
            "effectiveness_claims_must_come_from_mdr_confirmation": True,
            "optimization_cannot_override_failed_sota_efficiency_gate": True,
        },
    }


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    project_root: Path,
    run_root: Path,
) -> Dict[str, Any]:
    records = []
    capture_hashes_match = True
    artifact_hashes_match = True
    registry = {
        (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        ): item
        for item in summary.get("optimization_file_registry", [])
    }
    for source in protocol.get("sources", []):
        identity = (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        )
        path = (
            run_root
            / "captures"
            / identity[0]
            / identity[1]
            / f"seed{identity[2]}"
            / "optimization.json"
        )
        if (
            not path.is_file()
            or identity not in registry
            or file_hash(path)
            != registry[identity].get("optimization_file_sha256")
        ):
            capture_hashes_match = False
            continue
        record = load(path)
        optimized = path.parent / "mdr_evidence_reuse_runtime.joblib"
        pairwise = path.parent / "embedded_pairwise_runtime.joblib"
        artifact = record.get("artifact", {})
        if (
            not optimized.is_file()
            or not pairwise.is_file()
            or file_hash(optimized)
            != artifact.get("optimized_mdr_sha256")
            or file_hash(pairwise)
            != artifact.get("embedded_pairwise_sha256")
            or int(optimized.stat().st_size)
            != int(artifact.get("optimized_mdr_bytes", -1))
            or int(pairwise.stat().st_size)
            != int(artifact.get("embedded_pairwise_bytes", -1))
        ):
            artifact_hashes_match = False
        records.append(record)
    implementation_hashes_match = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    try:
        recomputed = aggregate_captures(records, protocol)
    except (KeyError, TypeError, ValueError):
        recomputed = {}
    recomputed["_records"] = records
    evaluated = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=implementation_hashes_match,
        capture_hashes_match=(
            capture_hashes_match
            and len(records) == 306
            and len(registry) == 306
        ),
        artifact_hashes_match=(
            artifact_hashes_match and len(records) == 306
        ),
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_evidence_reuse_audit_v1",
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
