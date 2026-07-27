from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from caeos.budgeted_conformal_uplift import budgeted_conformal_uplift
from caeos.conflict_topology_copula import (
    FEATURE_NAMES,
    KnownOnlyCopulaRisk,
    conflict_topology_features,
)
from caeos.hybrid_open_set import evaluate_hybrid_open_set


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def higher_quantile(values: np.ndarray, quantile: float) -> float:
    try:
        return float(np.quantile(values, quantile, method="higher"))
    except TypeError:
        return float(np.quantile(values, quantile, interpolation="higher"))


def _features(package: Any, prefix: str) -> np.ndarray:
    return conflict_topology_features(
        view_probability=package[f"{prefix}_view_probability"],
        view_reliability=package[f"{prefix}_view_reliability"],
        pairwise_conflict=package[f"{prefix}_pairwise_conflict"],
        global_probability=package[f"{prefix}_global_probability"],
        view_fused_probability=package[f"{prefix}_view_fused_probability"],
    )


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    with np.load(args.evidence_package, allow_pickle=False) as package, np.load(
        args.scores, allow_pickle=False
    ) as scores:
        validation_features = _features(package, "validation")
        test_features = _features(package, "test")
        validation_labels = np.asarray(scores["validation_labels"], dtype=np.int64)
        test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
        test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
        test_prediction = np.asarray(scores["test_prediction"], dtype=np.int64)
        validation_incumbent = np.asarray(
            package["validation_selected_risk"], dtype=np.float64
        )
        test_incumbent = np.asarray(package["test_selected_risk"], dtype=np.float64)
        selected_risk_name = str(package["selected_risk_name"].item())

    if len(validation_features) != len(validation_labels):
        raise ValueError("validation evidence and labels are not aligned")
    if not (
        len(test_features)
        == len(test_labels)
        == len(test_unknown)
        == len(test_prediction)
        == len(test_incumbent)
    ):
        raise ValueError("test evidence and labels are not aligned")
    if len(validation_incumbent) != len(validation_features):
        raise ValueError("validation incumbent risk is not aligned")

    scorer = KnownOnlyCopulaRisk(
        calibration_fraction=args.calibration_fraction,
        split_seed=args.split_seed,
    ).fit(validation_features, validation_labels)
    validation_topology = scorer.score(validation_features)
    test_topology = scorer.score(test_features)
    calibration_indices = np.asarray(scorer.calibration_indices, dtype=np.int64)
    calibration_topology = validation_topology[calibration_indices]
    validation_candidate, validation_budget = budgeted_conformal_uplift(
        validation_incumbent,
        validation_topology,
        calibration_topology,
        args.tail_probability,
        args.alpha,
    )
    test_candidate, test_budget = budgeted_conformal_uplift(
        test_incumbent,
        test_topology,
        calibration_topology,
        args.tail_probability,
        args.alpha,
    )
    reference_threshold = higher_quantile(
        validation_incumbent[calibration_indices], args.known_rejection_quantile
    )
    candidate_threshold = higher_quantile(
        validation_candidate[calibration_indices], args.known_rejection_quantile
    )
    reference_report = evaluate_hybrid_open_set(
        test_labels, test_unknown, test_prediction, test_incumbent, reference_threshold
    )
    candidate_report = evaluate_hybrid_open_set(
        test_labels, test_unknown, test_prediction, test_candidate, candidate_threshold
    )
    validation_delta = validation_candidate - validation_incumbent
    test_delta = test_candidate - test_incumbent
    result = {
        "schema_version": "strict_v4_budgeted_conformal_uplift_metrics_v1",
        "protocol_manifest_sha256": args.protocol_manifest_sha256,
        "suite": args.suite,
        "scenario": args.scenario,
        "seed": args.seed,
        "reference_risk": selected_risk_name,
        "candidate_risk": "budgeted_conformal_conflict_uplift",
        "parameters": {
            "alpha": float(args.alpha),
            "tail_probability": float(args.tail_probability),
            "calibration_fraction": float(args.calibration_fraction),
            "split_seed": int(args.split_seed),
            "known_rejection_quantile": float(args.known_rejection_quantile),
            "feature_names": list(FEATURE_NAMES),
        },
        "thresholds": {
            "reference": reference_threshold,
            "candidate": candidate_threshold,
        },
        "reports": {"reference": reference_report, "candidate": candidate_report},
        "diagnostics": {
            "prediction_array_equal": True,
            "known_macro_f1_absolute_difference": abs(
                candidate_report["known_macro_f1"] - reference_report["known_macro_f1"]
            ),
            "candidate_non_decreasing_for_all_validation_samples": bool(
                np.all(validation_delta >= -1e-12)
            ),
            "candidate_non_decreasing_for_all_test_samples": bool(
                np.all(test_delta >= -1e-12)
            ),
            "validation_activation_rate": float(validation_budget["activation_rate"]),
            "test_activation_rate": float(test_budget["activation_rate"]),
            "activation_rate_absolute_gap": abs(
                float(validation_budget["activation_rate"])
                - float(test_budget["activation_rate"])
            ),
            "validation_budget": int(validation_budget["budget"]),
            "validation_selected_count": int(validation_budget["selected_count"]),
            "test_budget": int(test_budget["budget"]),
            "test_selected_count": int(test_budget["selected_count"]),
            "maximum_validation_uplift": float(np.max(validation_delta)),
            "maximum_test_uplift": float(np.max(test_delta)),
            "copula": scorer.evidence(),
            "unknown_or_test_labels_used_for_fit_threshold_activation_or_budget": False,
            "unlabeled_test_topology_used_for_deterministic_budget_ranking": True,
            "test_labels_used_for_final_metrics_only": True,
        },
        "input_sha256": {
            "evidence_package": file_hash(args.evidence_package),
            "scores": file_hash(args.scores),
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    np.savez_compressed(
        args.output_dir / "scores.npz",
        validation_incumbent_risk=validation_incumbent,
        validation_topology_risk=validation_topology,
        validation_candidate_risk=validation_candidate,
        validation_conformal_p_value=validation_budget["p_values"],
        validation_selected=validation_budget["selected"],
        calibration_indices=calibration_indices,
        test_incumbent_risk=test_incumbent,
        test_topology_risk=test_topology,
        test_candidate_risk=test_candidate,
        test_conformal_p_value=test_budget["p_values"],
        test_selected=test_budget["selected"],
        test_prediction=test_prediction,
        test_labels=test_labels,
        test_unknown=test_unknown,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-package", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--protocol-manifest-sha256", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--alpha", type=float, default=0.25)
    parser.add_argument("--tail-probability", type=float, default=0.05)
    parser.add_argument("--calibration-fraction", type=float, default=0.4)
    parser.add_argument("--split-seed", type=int, default=229)
    parser.add_argument("--known-rejection-quantile", type=float, default=0.95)
    evaluate(parser.parse_args())


if __name__ == "__main__":
    main()
