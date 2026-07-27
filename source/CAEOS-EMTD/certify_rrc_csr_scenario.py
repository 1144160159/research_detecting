from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, Sequence

import numpy as np
from scipy.stats import beta
from sklearn.metrics import f1_score, roc_auc_score

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


SCENARIO_MEAN_AUROC_MINIMUM = 0.7
PER_SEED_AUROC_MINIMUM = 0.68
SAFETY_ACTIVE_RATE_UPPER_MAXIMUM = 0.01


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


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


def seed_record_from_capture(
    capture_dir: Path,
    *,
    suite: str,
    scenario: str,
    training_seed: int,
) -> Dict[str, Any]:
    manifest_path = capture_dir / "capture_manifest.json"
    clean_path = capture_dir / "clean_run" / "evidence_package.npz"
    robust_path = capture_dir / "robust_run" / "scores.npz"
    manifest = load_json(manifest_path)
    if (
        manifest.get("schema_version")
        != "strict_v4_csr_caeos_runtime_capture_v1"
        or manifest.get("state") != "complete"
        or manifest.get("algorithm") != "csr_caeos_v1"
        or manifest.get("task")
        != {"suite": suite, "scenario": scenario}
        or int(manifest.get("training_seed", -1)) != int(training_seed)
        or manifest.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
        or manifest.get("test_labels_read_for_roundtrip_or_selection")
        is not False
        or manifest.get("test_effect_metrics_computed") is not False
        or file_hash(clean_path) != manifest["clean_evidence_file_sha256"]
        or file_hash(robust_path) != manifest["robust_scores_file_sha256"]
    ):
        raise ValueError("complete bound CSR capture required")

    with np.load(clean_path, allow_pickle=False) as archive:
        probability = np.asarray(
            archive["validation_final_probability"], dtype=np.float64
        )
        risk = np.asarray(
            archive["validation_selected_risk"], dtype=np.float64
        )
    with np.load(robust_path, allow_pickle=False) as archive:
        labels = np.asarray(archive["validation_labels"], dtype=np.int64)
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

    safety = manifest["safety_profile"]
    safety_count = int(safety["partition"]["safety_count"])
    active_count = int(safety["active_count"])
    safety_upper = clopper_pearson_upper(active_count, safety_count)
    structural_passes = bool(
        safety["prediction_array_equal_pairwise"] is True
        and close(safety["probability_max_absolute_difference"], 0.0)
        and close(safety["inactive_risk_max_absolute_difference"], 0.0)
        and close(safety["clean_delta"], 0.0)
    )
    return {
        "suite": suite,
        "scenario": scenario,
        "training_seed": int(training_seed),
        "known_class_count": int(probability.shape[1]),
        "calibration_count": int(len(selected)),
        "calibration_known_macro_f1_report_only": macro_f1,
        "calibration_error_detection_auroc": error_auroc,
        "safety_count": safety_count,
        "safety_active_count": active_count,
        "safety_active_rate": float(safety["active_rate"]),
        "safety_active_rate_upper_95pct": safety_upper,
        "structural_safety_passes": structural_passes,
        "source_capture_manifest_file_sha256": file_hash(manifest_path),
        "clean_known_validation_file_sha256": file_hash(clean_path),
        "robust_known_validation_file_sha256": file_hash(robust_path),
        "known_validation_labels_used": True,
        "unknown_or_test_labels_used": False,
        "test_arrays_read": False,
        "test_effect_metrics_read": False,
    }


def certify_seed_records(
    records: Iterable[Dict[str, Any]],
    *,
    protocol_manifest_sha256: str,
    suite: str,
    scenario: str,
    expected_training_seeds: Sequence[int],
) -> Dict[str, Any]:
    rows = sorted(records, key=lambda row: int(row["training_seed"]))
    seeds = [int(seed) for seed in expected_training_seeds]
    if (
        len(protocol_manifest_sha256) != 64
        or len(rows) != 3
        or len(seeds) != 3
        or len(set(seeds)) != 3
        or [int(row["training_seed"]) for row in rows] != sorted(seeds)
        or any(
            row["suite"] != suite
            or row["scenario"] != scenario
            or row.get("known_validation_labels_used") is not True
            or row.get("unknown_or_test_labels_used") is not False
            or row.get("test_arrays_read") is not False
            or row.get("test_effect_metrics_read") is not False
            for row in rows
        )
    ):
        raise ValueError("three exact known-only scenario seed records required")

    aurocs = [
        float(row["calibration_error_detection_auroc"]) for row in rows
    ]
    all_safety = all(
        row["structural_safety_passes"] is True
        and float(row["safety_active_rate_upper_95pct"])
        <= SAFETY_ACTIVE_RATE_UPPER_MAXIMUM
        for row in rows
    )
    routing_enabled = bool(
        mean(aurocs) >= SCENARIO_MEAN_AUROC_MINIMUM
        and min(aurocs) >= PER_SEED_AUROC_MINIMUM
        and all_safety
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_scenario_certificate_v1",
        "state": "complete_known_validation_only",
        "algorithm": "rrc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol_manifest_sha256,
        "suite": suite,
        "scenario": scenario,
        "training_seeds": sorted(seeds),
        "seed_records": rows,
        "scenario_aggregation": {
            "mean_calibration_error_detection_auroc": mean(aurocs),
            "minimum_calibration_error_detection_auroc": min(aurocs),
            "all_seed_safety_checks_pass": all_safety,
        },
        "thresholds": {
            "scenario_mean_error_detection_auroc_minimum": (
                SCENARIO_MEAN_AUROC_MINIMUM
            ),
            "per_seed_error_detection_auroc_minimum": (
                PER_SEED_AUROC_MINIMUM
            ),
            "per_seed_safety_active_rate_upper_95pct_maximum": (
                SAFETY_ACTIVE_RATE_UPPER_MAXIMUM
            ),
            "absolute_known_macro_f1_threshold": None,
        },
        "routing_enabled": routing_enabled,
        "known_validation_labels_used": True,
        "unknown_or_test_labels_used": False,
        "test_arrays_read": False,
        "test_effect_metrics_read": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value
