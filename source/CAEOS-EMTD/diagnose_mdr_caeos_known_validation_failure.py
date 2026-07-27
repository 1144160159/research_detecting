from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import numpy as np
from sklearn.metrics import f1_score

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from caeos.mdr_fusion import js_divergence


EVIDENCE_ARRAYS = (
    "validation_final_probability",
    "validation_local_conflict",
)
SCORE_ARRAYS = (
    "validation_labels",
    "validation_any_missing",
)


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _load_allowlisted_arrays(
    path: Path, names: Iterable[str]
) -> Dict[str, np.ndarray]:
    requested = tuple(names)
    if any(name.startswith("test_") for name in requested):
        raise ValueError("known-validation diagnosis cannot read test arrays")
    with np.load(path, allow_pickle=False) as archive:
        missing = set(requested) - set(archive.files)
        if missing:
            raise ValueError(f"missing arrays in {path}: {sorted(missing)}")
        return {name: np.asarray(archive[name]) for name in requested}


def _macro_f1(labels: np.ndarray, prediction: np.ndarray) -> float:
    return float(
        f1_score(labels, prediction, average="macro", zero_division=0)
    )


def _validate_capture(
    capture: Mapping[str, Any],
    expected_design_sha256: str,
) -> None:
    if (
        capture.get("schema_version")
        != "strict_v4_mdr_caeos_runtime_capture_v1"
        or capture.get("state") != "complete"
        or capture.get("roundtrip", {}).get("passes") is not True
        or capture.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
    ):
        raise ValueError("complete leakage-free MDR capture required")
    runtime = capture.get("runtime_evidence", {})
    calibration = runtime.get("health_calibration", {})
    if (
        runtime.get("algorithm") != "mdr_caeos_v1"
        or runtime.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
        or runtime.get("contains_test_ground_truth") is not False
        or calibration.get("unknown_or_test_labels_used") is not False
    ):
        raise ValueError("invalid MDR runtime evidence")
    if capture.get("design_manifest_sha256") not in (
        None,
        expected_design_sha256,
    ):
        raise ValueError("capture design binding differs")


def diagnose_capture(
    capture_path: Path,
    expected_design_sha256: str,
) -> Dict[str, Any]:
    capture = load_json(capture_path)
    _validate_capture(capture, expected_design_sha256)
    clean_evidence = _load_allowlisted_arrays(
        capture_path.parent / "clean_run" / "evidence_package.npz",
        EVIDENCE_ARRAYS,
    )
    robust_evidence = _load_allowlisted_arrays(
        capture_path.parent / "robust_run" / "evidence_package.npz",
        ("validation_final_probability",),
    )
    scores = _load_allowlisted_arrays(
        capture_path.parent / "robust_run" / "scores.npz",
        SCORE_ARRAYS,
    )

    clean_probability = np.asarray(
        clean_evidence["validation_final_probability"], dtype=np.float64
    )
    robust_probability = np.asarray(
        robust_evidence["validation_final_probability"], dtype=np.float64
    )
    local_conflict = np.asarray(
        clean_evidence["validation_local_conflict"], dtype=np.float64
    )
    labels = np.asarray(scores["validation_labels"], dtype=np.int64)
    any_missing = np.asarray(
        scores["validation_any_missing"], dtype=bool
    )
    lengths = {
        len(clean_probability),
        len(robust_probability),
        len(local_conflict),
        len(labels),
        len(any_missing),
    }
    if len(lengths) != 1:
        raise ValueError("known-validation arrays are not aligned")
    if (
        clean_probability.ndim != 2
        or robust_probability.shape != clean_probability.shape
        or local_conflict.ndim != 2
        or not np.isfinite(clean_probability).all()
        or not np.isfinite(robust_probability).all()
        or not np.isfinite(local_conflict).all()
    ):
        raise ValueError("invalid known-validation evidence arrays")

    health = capture["runtime_evidence"]["health_calibration"]
    conflict = local_conflict.max(axis=1)
    disagreement = js_divergence(clean_probability, robust_probability)
    conflict_active = (
        conflict > float(health["conflict_threshold"]) + 1e-12
    )
    disagreement_active = (
        disagreement > float(health["disagreement_threshold"]) + 1e-12
    )
    active = any_missing | conflict_active | disagreement_active
    clean_prediction = clean_probability.argmax(axis=1)
    robust_prediction = robust_probability.argmax(axis=1)
    routed_prediction = np.where(
        active, robust_prediction, clean_prediction
    )
    changed = active & (clean_prediction != robust_prediction)
    clean_correct = clean_prediction == labels
    routed_correct = routed_prediction == labels
    corrected = (~clean_correct) & routed_correct
    harmed = clean_correct & (~routed_correct)

    clean_f1 = _macro_f1(labels, clean_prediction)
    robust_f1 = _macro_f1(labels, robust_prediction)
    routed_f1 = _macro_f1(labels, routed_prediction)
    profile = capture["known_validation_profile"]
    if abs(clean_f1 - float(profile["clean_pairwise_macro_f1"])) > 1e-12:
        raise ValueError("recomputed Pairwise validation F1 differs")
    if abs(robust_f1 - float(profile["robust_clean_macro_f1"])) > 1e-12:
        raise ValueError("recomputed robust validation F1 differs")

    count = len(labels)
    task = capture["task"]
    return {
        "suite": str(task["suite"]),
        "scenario": str(task["scenario"]),
        "weight": float(capture["weight"]),
        "sample_count": int(count),
        "clean_pairwise_macro_f1": clean_f1,
        "robust_clean_macro_f1": robust_f1,
        "routed_clean_macro_f1": routed_f1,
        "robust_clean_delta": robust_f1 - clean_f1,
        "routed_clean_delta": routed_f1 - clean_f1,
        "active_count": int(active.sum()),
        "active_rate": float(active.mean()),
        "missing_active_count": int(any_missing.sum()),
        "missing_active_rate": float(any_missing.mean()),
        "conflict_active_count": int(conflict_active.sum()),
        "conflict_active_rate": float(conflict_active.mean()),
        "disagreement_active_count": int(disagreement_active.sum()),
        "disagreement_active_rate": float(disagreement_active.mean()),
        "changed_prediction_count": int(changed.sum()),
        "changed_prediction_rate": float(changed.mean()),
        "corrected_count": int(corrected.sum()),
        "harmed_count": int(harmed.sum()),
        "net_correctness_change_count": int(corrected.sum() - harmed.sum()),
        "capture_manifest_file_sha256": file_hash(capture_path),
        "clean_evidence_file_sha256": file_hash(
            capture_path.parent / "clean_run" / "evidence_package.npz"
        ),
        "robust_evidence_file_sha256": file_hash(
            capture_path.parent / "robust_run" / "evidence_package.npz"
        ),
        "robust_scores_file_sha256": file_hash(
            capture_path.parent / "robust_run" / "scores.npz"
        ),
    }


def _aggregate(
    records: List[Dict[str, Any]],
    mean_limit: float,
    worst_limit: float,
) -> List[Dict[str, Any]]:
    rows = []
    for weight in sorted({float(record["weight"]) for record in records}):
        selected = [
            record for record in records if float(record["weight"]) == weight
        ]
        robust_delta = np.asarray(
            [record["robust_clean_delta"] for record in selected],
            dtype=np.float64,
        )
        routed_delta = np.asarray(
            [record["routed_clean_delta"] for record in selected],
            dtype=np.float64,
        )
        active_rate = np.asarray(
            [record["active_rate"] for record in selected], dtype=np.float64
        )
        changed_rate = np.asarray(
            [record["changed_prediction_rate"] for record in selected],
            dtype=np.float64,
        )
        worst = min(selected, key=lambda record: record["routed_clean_delta"])
        rows.append(
            {
                "weight": weight,
                "scenario_count": len(selected),
                "robust_clean_delta_mean": float(robust_delta.mean()),
                "robust_clean_delta_minimum": float(robust_delta.min()),
                "routed_clean_delta_mean": float(routed_delta.mean()),
                "routed_clean_delta_minimum": float(routed_delta.min()),
                "active_rate_mean": float(active_rate.mean()),
                "active_rate_maximum": float(active_rate.max()),
                "changed_prediction_rate_mean": float(changed_rate.mean()),
                "changed_prediction_rate_maximum": float(
                    changed_rate.max()
                ),
                "routed_clean_tolerance_passes": bool(
                    routed_delta.mean() >= mean_limit - 1e-12
                    and routed_delta.min() >= worst_limit - 1e-12
                ),
                "worst_routed_scenario": {
                    "suite": worst["suite"],
                    "scenario": worst["scenario"],
                    "routed_clean_delta": worst["routed_clean_delta"],
                    "active_rate": worst["active_rate"],
                    "changed_prediction_rate": worst[
                        "changed_prediction_rate"
                    ],
                    "corrected_count": worst["corrected_count"],
                    "harmed_count": worst["harmed_count"],
                },
            }
        )
    return rows


def diagnose(
    design: Dict[str, Any],
    rejection: Dict[str, Any],
    capture_paths: List[Path],
) -> Dict[str, Any]:
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical MDR v2 design required")
    if (
        rejection.get("schema_version")
        != "strict_v4_mdr_caeos_weight_rejection_v1"
        or rejection.get("manifest_sha256") != canonical_hash(rejection)
        or rejection.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or rejection.get("state") != "rejected_on_known_validation_only"
        or rejection.get("test_evaluations_generated") != 0
        or rejection.get("unknown_or_test_labels_used") is not False
    ):
        raise ValueError("canonical MDR weight rejection required")
    records = [
        diagnose_capture(path, design["manifest_sha256"])
        for path in capture_paths
    ]
    expected = {
        (str(row["suite"]), str(row["scenario"]), float(row["weight"]))
        for row in records
    }
    if len(expected) != len(records) or len(records) != 42:
        raise ValueError("exactly 42 unique MDR captures required")
    mean_limit = -float(
        design["pilot"]["expansion_gate"][
            "clean_known_macro_f1_mean_degradation_maximum"
        ]
    )
    worst_limit = -float(
        design["pilot"]["expansion_gate"][
            "clean_known_macro_f1_worst_degradation_maximum"
        ]
    )
    aggregate = _aggregate(records, mean_limit, worst_limit)
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_caeos_known_validation_failure_diagnosis_v1"
        ),
        "state": "complete_known_validation_only",
        "design_manifest_sha256": design["manifest_sha256"],
        "weight_rejection_manifest_sha256": rejection["manifest_sha256"],
        "capture_count": len(records),
        "weights": aggregate,
        "records": sorted(
            records,
            key=lambda row: (
                row["weight"],
                row["suite"],
                row["scenario"],
            ),
        ),
        "interpretation_boundary": {
            "mdr_rejection_remains_final": True,
            "diagnosis_can_revive_or_reselect_mdr": False,
            "test_arrays_read": [],
            "unknown_or_test_labels_used": False,
            "allowed_use": (
                "mechanism diagnosis and preregistration of a new candidate"
            ),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--rejection", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = diagnose(
        load_json(args.design),
        load_json(args.rejection),
        sorted(args.capture_root.rglob("capture_manifest.json")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
