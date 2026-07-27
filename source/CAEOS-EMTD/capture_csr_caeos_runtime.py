from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
from sklearn.metrics import f1_score

import capture_mdr_caeos_runtime as base
import capture_mdr_caeos_runtime_v2 as stable_capture
from caeos.conformal_safe_routing import (
    KnownValidationMaxRoutingCalibration,
)
from caeos.csr_runtime import CSRRuntime
from capture_pairwise_runtime import file_hash


ORIGINAL_CAPTURE = base.capture


def calibration_indices(count: int) -> np.ndarray:
    if count < 4:
        raise ValueError("CSR requires at least four known-validation rows")
    indices = np.arange(count, dtype=np.int64)[::2]
    if len(indices) < 2 or len(indices) >= count:
        raise ValueError("invalid CSR calibration partition")
    return indices


def safety_indices(count: int) -> np.ndarray:
    indices = np.arange(count, dtype=np.int64)[1::2]
    if len(indices) < 2:
        raise ValueError("invalid CSR safety partition")
    return indices


class SplitKnownValidationMaxCalibration:
    @classmethod
    def fit(
        cls,
        clean_validation_evidence: Dict[str, np.ndarray],
        robust_validation_evidence: Dict[str, np.ndarray],
        clean_validation_risk: np.ndarray,
        robust_validation_risk: np.ndarray,
        missing_validation_risk: np.ndarray,
        *,
        quantile: float = 0.99,
    ) -> KnownValidationMaxRoutingCalibration:
        del quantile
        count = len(clean_validation_risk)
        selected = calibration_indices(count)
        return KnownValidationMaxRoutingCalibration.fit(
            {
                name: np.asarray(value)[selected]
                for name, value in clean_validation_evidence.items()
            },
            {
                name: np.asarray(value)[selected]
                for name, value in robust_validation_evidence.items()
            },
            np.asarray(clean_validation_risk)[selected],
            np.asarray(robust_validation_risk)[selected],
            np.asarray(missing_validation_risk)[selected],
        )


def load_arrays(path: Path, names) -> Dict[str, np.ndarray]:
    if any(str(name).startswith("test_") for name in names):
        raise ValueError("CSR capture profile cannot read test arrays")
    with np.load(path, allow_pickle=False) as archive:
        missing = set(names) - set(archive.files)
        if missing:
            raise ValueError(f"missing CSR profile arrays: {sorted(missing)}")
        return {name: np.asarray(archive[name]) for name in names}


def build_safety_profile(
    runtime: CSRRuntime,
    capture_dir: Path,
) -> Dict[str, Any]:
    clean_evidence = load_arrays(
        capture_dir / "clean_run" / "evidence_package.npz",
        (
            "validation_final_probability",
            "validation_local_conflict",
            "validation_selected_risk",
        ),
    )
    robust_evidence = load_arrays(
        capture_dir / "robust_run" / "evidence_package.npz",
        (
            "validation_final_probability",
            "validation_selected_risk",
        ),
    )
    robust_scores = load_arrays(
        capture_dir / "robust_run" / "scores.npz",
        (
            "validation_labels",
            "validation_any_missing",
            "validation_missing_aware_cauchy_modality_support_union",
        ),
    )
    count = len(robust_scores["validation_labels"])
    selected = safety_indices(count)
    clean_probability = np.asarray(
        clean_evidence["validation_final_probability"], dtype=np.float64
    )[selected]
    robust_probability = np.asarray(
        robust_evidence["validation_final_probability"], dtype=np.float64
    )[selected]
    routed = runtime.health_calibration.apply(
        {
            "final_probability": clean_probability,
            "local_conflict": np.asarray(
                clean_evidence["validation_local_conflict"],
                dtype=np.float64,
            )[selected],
        },
        {"final_probability": robust_probability},
        np.asarray(
            clean_evidence["validation_selected_risk"], dtype=np.float64
        )[selected],
        np.asarray(
            robust_evidence["validation_selected_risk"], dtype=np.float64
        )[selected],
        np.asarray(
            robust_scores[
                "validation_missing_aware_cauchy_modality_support_union"
            ],
            dtype=np.float64,
        )[selected],
        np.asarray(
            robust_scores["validation_any_missing"], dtype=bool
        )[selected],
    )
    labels = np.asarray(
        robust_scores["validation_labels"], dtype=np.int64
    )[selected]
    clean_prediction = clean_probability.argmax(axis=1)
    clean_f1 = float(
        f1_score(
            labels, clean_prediction, average="macro", zero_division=0
        )
    )
    routed_f1 = float(
        f1_score(
            labels,
            routed["prediction"],
            average="macro",
            zero_division=0,
        )
    )
    inactive = ~np.asarray(routed["active"], dtype=bool)
    inactive_risk_difference = (
        float(
            np.max(
                np.abs(
                    routed["risk"][inactive]
                    - routed["clean_risk"][inactive]
                )
            )
        )
        if inactive.any()
        else 0.0
    )
    return {
        "schema_version": "strict_v4_csr_known_validation_safety_profile_v1",
        "partition": {
            "rule": "even_indices_calibration_odd_indices_safety",
            "total_count": int(count),
            "calibration_count": int(len(calibration_indices(count))),
            "safety_count": int(len(selected)),
        },
        "clean_pairwise_macro_f1": clean_f1,
        "routed_clean_macro_f1": routed_f1,
        "clean_delta": routed_f1 - clean_f1,
        "prediction_array_equal_pairwise": bool(
            np.array_equal(routed["prediction"], clean_prediction)
        ),
        "probability_max_absolute_difference": float(
            np.max(np.abs(routed["probability"] - clean_probability))
        ),
        "inactive_risk_max_absolute_difference": (
            inactive_risk_difference
        ),
        "active_count": int(routed["active"].sum()),
        "active_rate": float(routed["active"].mean()),
        "missing_active_count": int(routed["any_missing"].sum()),
        "conflict_active_count": int(
            routed["conflict_active"].sum()
        ),
        "disagreement_active_count": int(
            routed["disagreement_active"].sum()
        ),
        "test_arrays_read": [],
        "unknown_or_test_labels_used_for_calibration": False,
        "known_validation_labels_used_for_safety_gate_only": True,
    }


def capture_csr(*args, **kwargs) -> Dict[str, Any]:
    if float(kwargs["weight"]) != 0.5:
        raise ValueError("CSR v1 requires fixed augmentation weight 0.5")
    base.KnownOnlyHealthCalibration = SplitKnownValidationMaxCalibration
    base.MDRRuntime = CSRRuntime
    base.run_nested_base_capture = stable_capture.run_nested_base_capture
    manifest = ORIGINAL_CAPTURE(*args, **kwargs)
    capture_dir = Path(args[2])
    runtime = joblib.load(capture_dir / manifest["runtime_artifact"])
    if not isinstance(runtime, CSRRuntime):
        raise TypeError("captured runtime is not CSRRuntime")
    manifest.pop("known_validation_profile", None)
    manifest.update(
        {
            "schema_version": "strict_v4_csr_caeos_runtime_capture_v1",
            "algorithm": "csr_caeos_v1",
            "health_boundary": (
                "known-validation calibration-partition maximum"
            ),
            "safety_profile": build_safety_profile(runtime, capture_dir),
            "clean_evidence_file_sha256": file_hash(
                capture_dir / "clean_run" / "evidence_package.npz"
            ),
            "robust_evidence_file_sha256": file_hash(
                capture_dir / "robust_run" / "evidence_package.npz"
            ),
            "robust_scores_file_sha256": file_hash(
                capture_dir / "robust_run" / "scores.npz"
            ),
            "test_effect_metrics_computed": False,
            "test_labels_read_for_roundtrip_or_selection": False,
        }
    )
    (capture_dir / "capture_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    base.capture = capture_csr
    base.main()


if __name__ == "__main__":
    main()
