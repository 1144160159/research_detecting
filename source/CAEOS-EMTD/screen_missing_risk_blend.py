from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set


def screen(
    detector_scores: np.lib.npyio.NpzFile,
    classifier_scores: np.lib.npyio.NpzFile,
    threshold: float,
    steps: int,
) -> list[dict[str, object]]:
    if steps < 2:
        raise ValueError("blend screening requires at least two steps")
    for key in (
        "test_labels",
        "test_unknown",
        "test_cauchy_modality_support_union",
        "test_missing_aware_max_modality_knn",
    ):
        if key not in detector_scores:
            raise ValueError(f"detector scores are missing {key}")
    if not np.array_equal(
        detector_scores["test_labels"], classifier_scores["test_labels"]
    ) or not np.array_equal(
        detector_scores["test_unknown"], classifier_scores["test_unknown"]
    ):
        raise ValueError("detector and classifier evaluation arrays differ")
    rows = []
    current = detector_scores["test_cauchy_modality_support_union"]
    missing = detector_scores["test_missing_aware_max_modality_knn"]
    prediction = classifier_scores["test_prediction"]
    for alpha in np.linspace(0.0, 1.0, steps):
        risk = float(alpha) * current + (1.0 - float(alpha)) * missing
        report = evaluate_hybrid_open_set(
            detector_scores["test_labels"],
            detector_scores["test_unknown"],
            prediction,
            risk,
            threshold,
        )
        rows.append(
            {
                "current_risk_weight": float(alpha),
                "missing_aware_risk_weight": float(1.0 - alpha),
                "report": report,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Development-only missing-risk blend frontier")
    parser.add_argument("--detector-run", type=Path, required=True)
    parser.add_argument("--classifier-run", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=21)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    detector_metrics = json.loads(
        (args.detector_run / "metrics.json").read_text(encoding="utf-8")
    )
    detector_scores = np.load(args.detector_run / "scores.npz", allow_pickle=False)
    classifier_scores = np.load(
        args.classifier_run / "scores.npz", allow_pickle=False
    )
    threshold = float(
        detector_metrics["validation_thresholds"][
            "cauchy_modality_support_union"
        ]
    )
    rows = screen(detector_scores, classifier_scores, threshold, args.steps)
    result = {
        "schema_version": "missing_risk_blend_development_screen_v1",
        "state": "development_diagnostic_only",
        "selection_prohibited": True,
        "reason": "test labels are used only to characterize the frontier; a frozen validation-only selector is required",
        "threshold_source": "clean known validation of the detector model",
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in rows:
        report = row["report"]
        print(
            "alpha={:.2f} f1={:.4f} auroc={:.4f} fpr95={:.4f} oscr={:.4f} ka={:.4f} ur={:.4f}".format(
                row["current_risk_weight"],
                report["known_macro_f1"],
                report["unknown_auroc"],
                report["unknown_fpr95"],
                report["oscr"],
                report["known_acceptance_rate"],
                report["unknown_rejection_rate"],
            )
        )


if __name__ == "__main__":
    main()
