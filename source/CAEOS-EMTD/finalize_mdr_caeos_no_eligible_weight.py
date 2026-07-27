from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import select


Identity = Tuple[str, str, float]


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def rejection_rows(
    design: Dict[str, Any],
    manifests: Iterable[Dict[str, Any]],
) -> Tuple[list[Dict[str, Any]], set[Identity]]:
    weights = {
        float(value)
        for value in design["mechanism"]["training_augmentation_weight_grid"]
    }
    expected = {
        (str(suite), str(scenario), weight)
        for suite, scenarios in design["pilot"]["scenarios"].items()
        for scenario in scenarios
        for weight in weights
    }
    observed: set[Identity] = set()
    by_weight = {weight: [] for weight in weights}
    for manifest in manifests:
        task = manifest.get("task", {})
        identity = (
            str(task.get("suite")),
            str(task.get("scenario")),
            float(manifest.get("weight", -1.0)),
        )
        profile = manifest.get("known_validation_profile", {})
        if (
            manifest.get("schema_version")
            != "strict_v4_mdr_caeos_runtime_capture_v1"
            or manifest.get("state") != "complete"
            or manifest.get("roundtrip", {}).get("passes") is not True
            or profile.get("schema_version")
            != "strict_v4_mdr_known_validation_profile_v1"
            or profile.get("record_count") != 15
            or profile.get("known_validation_labels_used") is not True
            or profile.get("unknown_or_test_labels_used") is not False
            or identity in observed
            or identity not in expected
        ):
            raise ValueError("invalid capture for MDR weight rejection")
        observed.add(identity)
        by_weight[identity[2]].append(
            (
                float(profile["clean_delta"]),
                float(profile["corrupted_minimax_macro_f1"]),
            )
        )
    if observed != expected:
        raise ValueError("incomplete MDR capture universe")

    gate = design["pilot"]["expansion_gate"]
    mean_limit = -float(
        gate["clean_known_macro_f1_mean_degradation_maximum"]
    )
    worst_limit = -float(
        gate["clean_known_macro_f1_worst_degradation_maximum"]
    )
    rows = []
    for weight in sorted(weights):
        values = by_weight[weight]
        clean = np.asarray([value[0] for value in values])
        robust = np.asarray([value[1] for value in values])
        row: Dict[str, Any] = {
            "weight": weight,
            "scenario_count": len(values),
            "clean_delta_mean": float(clean.mean()),
            "clean_delta_minimum": float(clean.min()),
            "corrupted_minimax_mean": float(robust.mean()),
            "corrupted_minimax_minimum": float(robust.min()),
        }
        row["eligible"] = bool(
            row["clean_delta_mean"] >= mean_limit - 1e-12
            and row["clean_delta_minimum"] >= worst_limit - 1e-12
        )
        rows.append(row)
    return rows, observed


def finalize(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    integrity: Dict[str, Any],
    manifests: list[Dict[str, Any]],
    manifest_file_sha256: list[str],
    *,
    selector_file_sha256: str,
    finalizer_file_sha256: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR pilot v2 protocol required")
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
        or design.get("manifest_sha256")
        != protocol.get("design_manifest_sha256")
    ):
        raise ValueError("canonical protocol-bound MDR design required")
    if (
        integrity.get("schema_version")
        != "strict_v4_mdr_caeos_capture_integrity_audit_v1"
        or integrity.get("manifest_sha256") != canonical_hash(integrity)
        or integrity.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or integrity.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or integrity.get("observed_capture_count") != 42
        or integrity.get("passes") is not True
    ):
        raise ValueError("complete passing capture integrity audit required")

    rows, observed = rejection_rows(design, manifests)
    if any(row["eligible"] for row in rows):
        raise ValueError("MDR rejection branch requires zero eligible weights")
    try:
        select(design, manifests, manifest_file_sha256)
    except ValueError as error:
        if str(error) != "no MDR weight satisfies the frozen clean tolerance":
            raise
    else:
        raise ValueError("frozen selector did not reject all weights")

    rejection: Dict[str, Any] = {
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
    rejection["manifest_sha256"] = canonical_hash(rejection)

    summary: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_pilot_summary_v1",
        "state": "complete_after_known_validation_weight_rejection",
        "algorithm": "mdr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "weight_rejection_manifest_sha256": rejection["manifest_sha256"],
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
    summary["manifest_sha256"] = canonical_hash(summary)
    return rejection, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--integrity", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--selector", type=Path, required=True)
    parser.add_argument("--rejection-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()
    evaluation_paths = list(args.evaluation_root.rglob("evaluation.json"))
    if evaluation_paths:
        raise ValueError("weight rejection branch requires zero evaluations")
    paths = sorted(args.capture_root.rglob("capture_manifest.json"))
    rejection, summary = finalize(
        load(args.protocol),
        load(args.design),
        load(args.integrity),
        [load(path) for path in paths],
        [file_hash(path) for path in paths],
        selector_file_sha256=file_hash(args.selector),
        finalizer_file_sha256=file_hash(Path(__file__).resolve()),
    )
    args.rejection_output.parent.mkdir(parents=True, exist_ok=True)
    args.rejection_output.write_text(
        json.dumps(rejection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.summary_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(summary["manifest_sha256"])


if __name__ == "__main__":
    main()
