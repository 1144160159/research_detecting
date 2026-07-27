from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.mdr_fusion import KnownOnlyHealthCalibration


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def load_run(
    path: Path,
) -> Tuple[Dict[str, Any], np.lib.npyio.NpzFile, np.lib.npyio.NpzFile]:
    return (
        load_json(path / "metrics.json"),
        np.load(path / "scores.npz", allow_pickle=False),
        np.load(path / "evidence_package.npz", allow_pickle=False),
    )


def scalar_text(value: np.ndarray) -> str:
    return str(np.asarray(value).reshape(()).item())


def evidence_view(archive: np.lib.npyio.NpzFile, prefix: str) -> Dict[str, np.ndarray]:
    return {
        "final_probability": np.asarray(
            archive[f"{prefix}_final_probability"], dtype=np.float64
        ),
        "local_conflict": np.asarray(
            archive[f"{prefix}_local_conflict"], dtype=np.float64
        ),
    }


def evaluate(clean_run: Path, robust_run: Path) -> Dict[str, Any]:
    clean_metrics, clean_scores, clean_evidence = load_run(clean_run)
    robust_metrics, robust_scores, robust_evidence = load_run(robust_run)
    for name in ("validation_labels", "test_labels", "test_unknown"):
        if not np.array_equal(clean_scores[name], robust_scores[name]):
            raise ValueError(f"clean and robust {name} arrays differ")
    if (
        clean_metrics.get("split_metadata", {}).get("split_fingerprint")
        != robust_metrics.get("split_metadata", {}).get("split_fingerprint")
    ):
        raise ValueError("clean and robust split fingerprints differ")
    if robust_metrics.get("model") != "mdr_caeos_structured_robust_pairwise_v1":
        raise ValueError("robust run has the wrong model identity")
    mdr = robust_metrics.get("mdr_candidate", {})
    if mdr.get("unknown_or_test_labels_used_for_training_or_selection") is not False:
        raise ValueError("robust run leakage guard failed")

    clean_risk_name = scalar_text(clean_evidence["selected_risk_name"])
    robust_risk_name = scalar_text(robust_evidence["selected_risk_name"])
    clean_validation_risk = np.asarray(
        clean_evidence["validation_selected_risk"], dtype=np.float64
    )
    robust_validation_risk = np.asarray(
        robust_evidence["validation_selected_risk"], dtype=np.float64
    )
    missing_validation_risk = np.asarray(
        robust_scores[
            "validation_missing_aware_cauchy_modality_support_union"
        ],
        dtype=np.float64,
    )
    calibration = KnownOnlyHealthCalibration.fit(
        evidence_view(clean_evidence, "validation"),
        evidence_view(robust_evidence, "validation"),
        clean_validation_risk,
        robust_validation_risk,
        missing_validation_risk,
        quantile=float(mdr["health_quantile"]),
    )
    output = calibration.apply(
        evidence_view(clean_evidence, "test"),
        evidence_view(robust_evidence, "test"),
        np.asarray(clean_evidence["test_selected_risk"], dtype=np.float64),
        np.asarray(robust_evidence["test_selected_risk"], dtype=np.float64),
        np.asarray(
            robust_scores[
                "test_missing_aware_cauchy_modality_support_union"
            ],
            dtype=np.float64,
        ),
        np.asarray(robust_scores["test_any_missing"], dtype=bool),
    )
    threshold = float(np.asarray(clean_evidence["selected_threshold"]).reshape(()))
    report = evaluate_hybrid_open_set(
        clean_scores["test_labels"],
        clean_scores["test_unknown"],
        output["prediction"],
        output["risk"],
        threshold,
    )
    clean_report = clean_metrics["reports"][clean_risk_name]
    return {
        "schema_version": "strict_v4_mdr_caeos_evaluation_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "clean_risk_name": clean_risk_name,
        "robust_risk_name": robust_risk_name,
        "threshold_source": "clean_pairwise_known_validation",
        "threshold": threshold,
        "health_calibration": calibration.evidence(),
        "routing": {
            "active_count": int(output["active"].sum()),
            "active_rate": float(output["active"].mean()),
            "missing_count": int(output["any_missing"].sum()),
            "missing_rate": float(output["any_missing"].mean()),
            "inactive_prediction_exactly_clean": bool(
                np.array_equal(
                    output["prediction"][~output["active"]],
                    output["clean_prediction"][~output["active"]],
                )
            ),
            "inactive_risk_exactly_clean": bool(
                np.array_equal(
                    output["risk"][~output["active"]],
                    np.asarray(clean_evidence["test_selected_risk"])[
                        ~output["active"]
                    ],
                )
            ),
            "unknown_or_test_labels_used_for_routing_or_calibration": False,
        },
        "clean_report": clean_report,
        "candidate_report": report,
        "test_labels_used_for_final_evaluation_only": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean-run", type=Path, required=True)
    parser.add_argument("--robust-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = evaluate(args.clean_run, args.robust_run)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value["candidate_report"], sort_keys=True))


if __name__ == "__main__":
    main()
