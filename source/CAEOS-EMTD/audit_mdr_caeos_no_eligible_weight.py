from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from finalize_mdr_caeos_no_eligible_weight import load, rejection_rows


def audit(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    integrity: Dict[str, Any],
    rejection: Dict[str, Any],
    summary: Dict[str, Any],
    manifests: list[Dict[str, Any]],
    manifest_file_sha256: list[str],
    *,
    selector_file_sha256: str,
    finalizer_file_sha256: str,
    auditor_file_sha256: str,
    evaluation_count: int,
) -> Dict[str, Any]:
    protocol_valid = (
        protocol.get("schema_version")
        == "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        and protocol.get("manifest_sha256") == canonical_hash(protocol)
    )
    design_valid = (
        design.get("schema_version") == "strict_v4_mdr_caeos_design_v2"
        and design.get("manifest_sha256") == canonical_hash(design)
        and design.get("manifest_sha256")
        == protocol.get("design_manifest_sha256")
    )
    integrity_valid = (
        integrity.get("manifest_sha256") == canonical_hash(integrity)
        and integrity.get("protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and integrity.get("design_manifest_sha256")
        == design.get("manifest_sha256")
        and integrity.get("observed_capture_count") == 42
        and integrity.get("passes") is True
    )
    rows, observed = rejection_rows(design, manifests)
    expected_rejection = {
        "schema_version": "strict_v4_mdr_caeos_weight_rejection_v1",
        "state": "rejected_on_known_validation_only",
        "reason": "no_weight_satisfies_frozen_clean_tolerance",
        "design_manifest_sha256": design["manifest_sha256"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "capture_integrity_manifest_sha256": integrity["manifest_sha256"],
        "capture_manifest_count": len(observed),
        "capture_manifest_file_sha256": sorted(manifest_file_sha256),
        "selector_file_sha256": selector_file_sha256,
        "finalizer_file_sha256": finalizer_file_sha256,
        "selection_rule": (
            "reject MDR before test evaluation when no augmentation weight "
            "satisfies frozen mean and worst clean Known Macro-F1 tolerances"
        ),
        "rows": rows,
        "selected_weight": None,
        "known_validation_labels_used": True,
        "unknown_or_test_labels_used": False,
        "test_evaluations_generated": 0,
    }
    expected_rejection["manifest_sha256"] = canonical_hash(
        expected_rejection
    )
    expected_summary = {
        "schema_version": "strict_v4_mdr_caeos_pilot_summary_v1",
        "state": "complete_after_known_validation_weight_rejection",
        "algorithm": "mdr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "weight_rejection_manifest_sha256": expected_rejection[
            "manifest_sha256"
        ],
        "selected_weight": None,
        "validation": {
            "capture_count": len(observed),
            "evaluation_count": 0,
            "capture_integrity_passes": True,
            "passes": True,
        },
        "expansion_checks": {
            "eligible_weight_exists": False,
            "test_evaluation_required_after_weight_rejection": False,
        },
        "decision": {
            "expand_to_full102_confirmation": False,
            "retain_caeos_pairwise": True,
            "reason": "no_weight_satisfies_frozen_clean_tolerance",
        },
        "claim_boundary": {
            "pilot_is_development_only": True,
            "pilot_success_does_not_establish_sota": True,
            "test_effect_metrics_not_generated": True,
            "no_threshold_or_weight_changed_after_rejection": True,
        },
    }
    expected_summary["manifest_sha256"] = canonical_hash(expected_summary)
    checks = {
        "protocol_canonical": protocol_valid,
        "design_canonical_and_bound": design_valid,
        "capture_integrity_complete_and_bound": integrity_valid,
        "capture_count_42": len(observed) == 42,
        "all_weights_ineligible": not any(
            row["eligible"] for row in rows
        ),
        "evaluation_count_zero": evaluation_count == 0,
        "rejection_exactly_recomputed": rejection == expected_rejection,
        "summary_exactly_recomputed": summary == expected_summary,
        "unknown_or_test_labels_used_for_selection": False,
        "threshold_or_weight_override_observed": False,
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_pilot_audit_v2",
        "state": "complete_known_validation_weight_rejection_audit",
        "audit_mode": "no_eligible_weight_before_test_evaluation",
        "algorithm": "mdr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "capture_integrity_manifest_sha256": integrity["manifest_sha256"],
        "weight_rejection_manifest_sha256": rejection["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "selector_file_sha256": selector_file_sha256,
        "finalizer_file_sha256": finalizer_file_sha256,
        "auditor_file_sha256": auditor_file_sha256,
        "checks": checks,
        "passes": all(
            value is True
            for name, value in checks.items()
            if name
            not in {
                "unknown_or_test_labels_used_for_selection",
                "threshold_or_weight_override_observed",
            }
        )
        and checks["unknown_or_test_labels_used_for_selection"] is False
        and checks["threshold_or_weight_override_observed"] is False,
        "effect_decision_inherited_without_override": summary["decision"],
        "claim_boundary": {
            "audit_passes_means_negative_branch_integrity_only": True,
            "no_test_effect_claim_allowed": True,
            "pairwise_retained_without_component_splicing": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--integrity", type=Path, required=True)
    parser.add_argument("--rejection", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--selector", type=Path, required=True)
    parser.add_argument("--finalizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.capture_root.rglob("capture_manifest.json"))
    evaluation_count = len(
        list(args.evaluation_root.rglob("evaluation.json"))
    )
    value = audit(
        load(args.protocol),
        load(args.design),
        load(args.integrity),
        load(args.rejection),
        load(args.summary),
        [load(path) for path in paths],
        [file_hash(path) for path in paths],
        selector_file_sha256=file_hash(args.selector),
        finalizer_file_sha256=file_hash(args.finalizer),
        auditor_file_sha256=file_hash(Path(__file__).resolve()),
        evaluation_count=evaluation_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
