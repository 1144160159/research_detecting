from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_test_corruption(payload: dict[str, Any]) -> dict[str, Any]:
    corruption = payload.get("corruption_protocol", {}).get("test_corruption")
    if not corruption or corruption.get("kind") == "none":
        return {"kind": "none", "modality": None, "severity": 0.0}
    return corruption


def audit_pair(
    detector_run: Path,
    classifier_run: Path,
    risk_name: str,
) -> tuple[dict[str, Any], dict[str, Any], np.lib.npyio.NpzFile, np.lib.npyio.NpzFile]:
    detector = load_json(detector_run / "metrics.json")
    classifier = load_json(classifier_run / "metrics.json")
    detector_fingerprint = detector.get("split_metadata", {}).get("split_fingerprint")
    classifier_fingerprint = classifier.get("split_metadata", {}).get("split_fingerprint")
    if detector_fingerprint != classifier_fingerprint:
        raise ValueError("detector and classifier split fingerprints differ")
    detector_corruption = normalized_test_corruption(detector)
    classifier_corruption = normalized_test_corruption(classifier)
    if detector_corruption != classifier_corruption:
        raise ValueError("detector and classifier test corruptions differ")
    augmentation = classifier.get("training_augmentation", {})
    if augmentation.get("enabled") is not True:
        raise ValueError("classifier run is not a modality-dropout model")
    if augmentation.get("unknown_or_test_labels_used") is not False:
        raise ValueError("classifier augmentation leakage guard failed")
    threshold = detector.get("validation_thresholds", {}).get(risk_name)
    if threshold is None:
        raise ValueError(f"detector run has no threshold for {risk_name}")
    detector_scores = np.load(detector_run / "scores.npz", allow_pickle=False)
    classifier_scores = np.load(classifier_run / "scores.npz", allow_pickle=False)
    for name in ("test_labels", "test_unknown"):
        if not np.array_equal(detector_scores[name], classifier_scores[name]):
            raise ValueError(f"detector and classifier {name} arrays differ")
    risk_key = f"test_{risk_name}"
    if risk_key not in detector_scores:
        raise ValueError(f"detector score archive has no {risk_key}")
    if "test_prediction" not in classifier_scores:
        raise ValueError("classifier score archive has no test_prediction")
    return detector, classifier, detector_scores, classifier_scores


def evaluate_pair(
    detector_run: Path,
    classifier_run: Path,
    risk_name: str = "cauchy_modality_support_union",
    prediction_routing: str = "always_robust",
    routing_modalities: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    detector, classifier, detector_scores, classifier_scores = audit_pair(
        detector_run, classifier_run, risk_name
    )
    threshold = float(detector["validation_thresholds"][risk_name])
    if prediction_routing == "always_robust":
        if routing_modalities is not None:
            raise ValueError("routing_modalities requires missingness routing")
        prediction = classifier_scores["test_prediction"]
        routed_count = len(prediction)
    elif prediction_routing == "missingness":
        if routing_modalities is not None:
            if not routing_modalities or len(set(routing_modalities)) != len(
                routing_modalities
            ):
                raise ValueError("routing_modalities must be non-empty and unique")
            if "test_view_missing" not in classifier_scores:
                raise ValueError(
                    "selective missingness routing requires test_view_missing evidence"
                )
            view_missing = np.asarray(
                classifier_scores["test_view_missing"], dtype=bool
            )
            if view_missing.ndim != 2 or any(
                modality < 0 or modality >= view_missing.shape[1]
                for modality in routing_modalities
            ):
                raise ValueError("routing modality index is out of range")
            missing = view_missing[:, routing_modalities].any(axis=1)
        elif "test_any_missing" in classifier_scores:
            missing = np.asarray(classifier_scores["test_any_missing"], dtype=bool)
        elif normalized_test_corruption(classifier)["kind"] == "none":
            missing = np.zeros(len(classifier_scores["test_prediction"]), dtype=bool)
        else:
            raise ValueError("missingness routing requires test_any_missing evidence")
        prediction = np.where(
            missing,
            classifier_scores["test_prediction"],
            detector_scores["test_prediction"],
        )
        routed_count = int(missing.sum())
    else:
        raise ValueError("prediction_routing must be always_robust or missingness")
    report = evaluate_hybrid_open_set(
        detector_scores["test_labels"],
        detector_scores["test_unknown"],
        prediction,
        detector_scores[f"test_{risk_name}"],
        threshold,
    )
    detector_report = detector["reports"][risk_name]
    invariant_metrics = ("unknown_auroc", "unknown_aupr", "unknown_fpr95")
    for metric in invariant_metrics:
        if abs(float(report[metric]) - float(detector_report[metric])) > 1e-12:
            raise ValueError(f"dual-path detector invariant failed: {metric}")
    return {
        "schema_version": "dual_path_modality_dropout_evaluation_v1",
        "state": "complete",
        "risk_name": risk_name,
        "decision_architecture": {
            "unknown_risk_and_threshold": "clean detector run",
            "known_class_prediction": (
                "modality-dropout classifier run"
                if prediction_routing == "always_robust"
                else "clean classifier unless validation-calibrated feature missingness is detected"
            ),
            "prediction_routing": prediction_routing,
            "routing_modalities": (
                list(routing_modalities) if routing_modalities is not None else "all"
            ),
            "routed_sample_count": int(routed_count),
            "routed_sample_rate": float(routed_count / len(prediction)),
            "unknown_or_test_labels_used_for_training_selection_or_threshold": False,
        },
        "split_fingerprint": detector["split_metadata"]["split_fingerprint"],
        "test_corruption": normalized_test_corruption(detector),
        "detector_model": detector["model"],
        "classifier_model": classifier["model"],
        "classifier_training_augmentation": classifier["training_augmentation"],
        "detector_report": detector_report,
        "classifier_native_report": classifier["reports"][risk_name],
        "dual_path_report": report,
        "detector_ranking_metrics_exactly_preserved": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate clean-risk plus robust-classifier dual path")
    parser.add_argument("--detector-run", type=Path, required=True)
    parser.add_argument("--classifier-run", type=Path, required=True)
    parser.add_argument("--risk-name", default="cauchy_modality_support_union")
    parser.add_argument(
        "--prediction-routing",
        choices=("always_robust", "missingness"),
        default="always_robust",
    )
    parser.add_argument(
        "--routing-modalities",
        default="",
        help="Comma-separated modality indices; empty routes any detected modality",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    routing_modalities = (
        tuple(int(value) for value in args.routing_modalities.split(",") if value.strip())
        if args.routing_modalities.strip()
        else None
    )
    result = evaluate_pair(
        args.detector_run,
        args.classifier_run,
        args.risk_name,
        args.prediction_routing,
        routing_modalities,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["dual_path_report"], sort_keys=True))


if __name__ == "__main__":
    main()
