from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable

import numpy as np
from scipy.stats import beta
from sklearn.metrics import f1_score, roc_auc_score

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


TRAINING_SEEDS = (647, 653, 659)
MACRO_F1_MINIMUM = 0.9
ERROR_AUROC_MINIMUM = 0.7
RRC_SCENARIO_MEAN_AUROC_MINIMUM = 0.7
RRC_SEED_AUROC_MINIMUM = 0.68
SAFETY_ACTIVE_RATE_UPPER_MAXIMUM = 0.01


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(value: Dict[str, Any], path: Path) -> None:
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"non-canonical manifest: {path}")


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def clopper_pearson_upper(
    successes: int, trials: int, confidence: float = 0.95
) -> float:
    if trials <= 0 or successes < 0 or successes > trials:
        raise ValueError("valid non-empty binomial counts required")
    if successes == trials:
        return 1.0
    return float(beta.ppf(confidence, successes + 1, trials - successes))


def summarize_records(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(records)
    if not rows:
        raise ValueError("at least one diagnostic record is required")
    grouped: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["identity"]].append(row)

    scenario_records = []
    for identity, members in sorted(grouped.items()):
        seeds = sorted(int(row["training_seed"]) for row in members)
        complete = seeds == list(TRAINING_SEEDS)
        aurocs = [
            float(row["calibration_error_detection_auroc"])
            for row in members
        ]
        safety_passes = all(
            float(row["source_safety_active_rate_upper_95pct"])
            <= SAFETY_ACTIVE_RATE_UPPER_MAXIMUM
            and close(float(row["source_safety_clean_delta"]), 0.0)
            and row["source_prediction_array_equal_pairwise"] is True
            and close(
                float(row["source_probability_max_absolute_difference"]),
                0.0,
            )
            and close(
                float(row["source_inactive_risk_max_absolute_difference"]),
                0.0,
            )
            for row in members
        )
        eligible = bool(
            complete
            and mean(aurocs) >= RRC_SCENARIO_MEAN_AUROC_MINIMUM
            and min(aurocs) >= RRC_SEED_AUROC_MINIMUM
            and safety_passes
        )
        scenario_records.append(
            {
                "identity": identity,
                "observed_training_seeds": seeds,
                "complete_three_seed_scenario": complete,
                "mean_calibration_error_detection_auroc": mean(aurocs),
                "minimum_calibration_error_detection_auroc": min(aurocs),
                "maximum_source_safety_active_rate_upper_95pct": max(
                    float(row["source_safety_active_rate_upper_95pct"])
                    for row in members
                ),
                "all_source_safety_checks_pass": safety_passes,
                "rrc_diagnostic_eligible": eligible,
            }
        )

    macro_f1 = [float(row["calibration_known_macro_f1"]) for row in rows]
    error_auroc = [
        float(row["calibration_error_detection_auroc"]) for row in rows
    ]
    active_rates = [float(row["source_safety_active_rate"]) for row in rows]
    return {
        "observed_capture_count": len(rows),
        "observed_identity_count": len(grouped),
        "complete_three_seed_scenario_count": sum(
            int(row["complete_three_seed_scenario"])
            for row in scenario_records
        ),
        "class_count_values": sorted(
            {int(row["known_class_count"]) for row in rows}
        ),
        "calibration_known_macro_f1": {
            "minimum": min(macro_f1),
            "mean": mean(macro_f1),
            "maximum": max(macro_f1),
            "passes_absolute_0_9_count": sum(
                value >= MACRO_F1_MINIMUM for value in macro_f1
            ),
        },
        "calibration_error_detection_auroc": {
            "minimum": min(error_auroc),
            "mean": mean(error_auroc),
            "maximum": max(error_auroc),
            "passes_absolute_0_7_count": sum(
                value >= ERROR_AUROC_MINIMUM for value in error_auroc
            ),
        },
        "source_safety_active_rate": {
            "minimum": min(active_rates),
            "mean": mean(active_rates),
            "maximum": max(active_rates),
        },
        "source_safety_clean_delta_maximum_absolute": max(
            abs(float(row["source_safety_clean_delta"])) for row in rows
        ),
        "rrc_diagnostic_eligible_scenario_count": sum(
            int(row["rrc_diagnostic_eligible"])
            for row in scenario_records
        ),
        "rrc_diagnostic_eligible_identities": [
            row["identity"]
            for row in scenario_records
            if row["rrc_diagnostic_eligible"]
        ],
        "scenario_records": scenario_records,
    }


def audit(
    protocol_path: Path,
    progress_path: Path,
    capture_root: Path,
    output_path: Path,
) -> Dict[str, Any]:
    protocol = load_json(protocol_path)
    progress = load_json(progress_path)
    require_canonical(protocol, protocol_path)
    require_canonical(progress, progress_path)
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_csr_confirmation_protocol_v1"
        or progress.get("schema_version")
        != "strict_v4_krc_csr_confirmation_progress_audit_v1"
        or progress.get("passes") is not True
        or progress.get("protocol", {}).get("manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("canonical KRC protocol and passing progress required")

    progress_records = list(progress.get("records", []))
    if len(progress_records) != int(
        progress["observed_totals"]["captures"]
    ):
        raise ValueError("progress record count mismatch")

    records = []
    input_inventory = []
    for progress_record in progress_records:
        suite = progress_record["suite"]
        scenario = progress_record["scenario"]
        training_seed = int(progress_record["training_seed"])
        capture_dir = (
            capture_root / suite / scenario / f"seed{training_seed}"
        )
        capture_path = capture_dir / "capture_manifest.json"
        source_path = capture_dir / "csr_capture_manifest.json"
        clean_path = capture_dir / "clean_run" / "evidence_package.npz"
        robust_path = capture_dir / "robust_run" / "scores.npz"
        capture = load_json(capture_path)
        source = load_json(source_path)
        require_canonical(capture, capture_path)
        if (
            file_hash(capture_path)
            != progress_record["capture_manifest_file_sha256"]
            or file_hash(source_path)
            != capture["source_csr_capture_manifest_file_sha256"]
            or source.get("schema_version")
            != "strict_v4_csr_caeos_runtime_capture_v1"
            or source.get("state") != "complete"
            or source.get("algorithm") != "csr_caeos_v1"
            or capture["task"] != source["task"]
            or int(capture["training_seed"]) != training_seed
            or int(source["training_seed"]) != training_seed
        ):
            raise ValueError(
                f"capture/source binding mismatch: "
                f"{suite}/{scenario}/seed{training_seed}"
            )

        with np.load(clean_path, allow_pickle=False) as archive:
            probability = np.asarray(
                archive["validation_final_probability"], dtype=np.float64
            )
            risk = np.asarray(
                archive["validation_selected_risk"], dtype=np.float64
            )
        with np.load(robust_path, allow_pickle=False) as archive:
            labels = np.asarray(
                archive["validation_labels"], dtype=np.int64
            )
        if not (len(probability) == len(risk) == len(labels)):
            raise ValueError("known-validation arrays are not aligned")
        selected = np.arange(len(labels), dtype=np.int64)[::2]
        prediction = probability[selected].argmax(axis=1)
        errors = prediction != labels[selected]
        if len(np.unique(errors)) != 2:
            raise ValueError("both correct and incorrect calibration rows required")
        macro_f1 = float(
            f1_score(
                labels[selected],
                prediction,
                average="macro",
                zero_division=0,
            )
        )
        error_auroc = float(
            roc_auc_score(errors.astype(np.int64), risk[selected])
        )
        certificate = capture["known_only_certificate"]
        if (
            not close(
                macro_f1, certificate["calibration_known_macro_f1"]
            )
            or not close(
                error_auroc,
                certificate["calibration_error_detection_auroc"],
            )
        ):
            raise ValueError("known-only certificate recomputation mismatch")

        safety = source["safety_profile"]
        safety_count = int(safety["partition"]["safety_count"])
        active_count = int(safety["active_count"])
        record = {
            "identity": f"{suite}/{scenario}",
            "suite": suite,
            "scenario": scenario,
            "training_seed": training_seed,
            "known_class_count": int(probability.shape[1]),
            "calibration_count": int(len(selected)),
            "calibration_known_macro_f1": macro_f1,
            "calibration_error_detection_auroc": error_auroc,
            "current_krc_routing_enabled": bool(
                certificate["routing_enabled"]
            ),
            "source_safety_count": safety_count,
            "source_safety_active_count": active_count,
            "source_safety_active_rate": float(safety["active_rate"]),
            "source_safety_active_rate_upper_95pct": (
                clopper_pearson_upper(active_count, safety_count)
            ),
            "source_safety_clean_delta": float(safety["clean_delta"]),
            "source_prediction_array_equal_pairwise": bool(
                safety["prediction_array_equal_pairwise"]
            ),
            "source_probability_max_absolute_difference": float(
                safety["probability_max_absolute_difference"]
            ),
            "source_inactive_risk_max_absolute_difference": float(
                safety["inactive_risk_max_absolute_difference"]
            ),
        }
        records.append(record)
        input_inventory.append(
            {
                "identity": record["identity"],
                "training_seed": training_seed,
                "capture_manifest_file_sha256": file_hash(capture_path),
                "source_csr_capture_manifest_file_sha256": file_hash(
                    source_path
                ),
                "clean_known_validation_file_sha256": file_hash(clean_path),
                "robust_known_validation_file_sha256": file_hash(robust_path),
            }
        )

    diagnostics = summarize_records(records)
    evidence: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_certificate_bottleneck_audit_v1",
        "state": "known_validation_only_diagnostic_complete",
        "passes": True,
        "algorithm_under_diagnosis": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "progress_manifest_sha256": progress["manifest_sha256"],
        "progress_file_sha256": file_hash(progress_path),
        "input_inventory": input_inventory,
        "records": records,
        "diagnostics": diagnostics,
        "current_gate_diagnosis": {
            "absolute_macro_f1_gate_is_binding_all_observed_captures": (
                diagnostics["calibration_known_macro_f1"][
                    "passes_absolute_0_9_count"
                ]
                == 0
            ),
            "risk_separability_gate_passes_some_observed_captures": (
                diagnostics["calibration_error_detection_auroc"][
                    "passes_absolute_0_7_count"
                ]
                > 0
            ),
            "source_routing_preserves_known_classification": (
                diagnostics[
                    "source_safety_clean_delta_maximum_absolute"
                ]
                == 0.0
            ),
            "diagnosis_does_not_modify_frozen_krc_protocol": True,
        },
        "rrc_fallback_hypothesis": {
            "algorithm": "rrc_csr_caeos_v1",
            "certificate_unit": "scenario_pooled_across_three_seeds",
            "scenario_mean_error_auroc_minimum": (
                RRC_SCENARIO_MEAN_AUROC_MINIMUM
            ),
            "per_seed_error_auroc_minimum": RRC_SEED_AUROC_MINIMUM,
            "per_seed_safety_active_rate_upper_95pct_maximum": (
                SAFETY_ACTIVE_RATE_UPPER_MAXIMUM
            ),
            "prediction_probability_exact_pairwise_required": True,
            "clean_macro_f1_delta_exact_zero_required": True,
            "inactive_risk_exact_pairwise_required": True,
            "absolute_known_macro_f1_threshold_used": False,
            "reason": (
                "replace a task-difficulty surrogate with direct known-only "
                "risk-separability and routing-safety evidence"
            ),
        },
        "data_use_boundary": {
            "known_validation_arrays_read": True,
            "test_arrays_read": False,
            "evaluation_files_read": [],
            "test_effect_metrics_read": False,
            "observed_identities_become_development_only_for_rrc": sorted(
                {record["identity"] for record in records}
            ),
            "current_krc_confirmation_remains_authoritative_and_unchanged": True,
        },
        "output_path": output_path.resolve().as_posix(),
    }
    evidence["manifest_sha256"] = canonical_hash(evidence)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = audit(
        args.protocol.resolve(),
        args.progress.resolve(),
        args.capture_root.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "passes": evidence["passes"],
                "diagnostics": evidence["diagnostics"],
                "manifest_sha256": evidence["manifest_sha256"],
                "file_sha256": file_hash(args.output.resolve()),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
