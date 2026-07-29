from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold


ALERT_VARIANTS = ("xgb_attack", "tail_max", "tail_noisy_or")
OPEN_VARIANTS = ("risk_tail", "tail_max", "tail_noisy_or")
ALERT_BUDGETS = (0.01, 0.02, 0.03, 0.04)
OPEN_BUDGETS = (0.005, 0.01, 0.02, 0.03, 0.04)
TARGET = 0.95
FPR_LIMIT = 0.05


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any], label: str) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")


def empirical_cdf(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    reference = np.asarray(reference, dtype=np.float64).reshape(-1)
    values = np.asarray(values, dtype=np.float64)
    if reference.size == 0 or not np.isfinite(reference).all():
        raise ValueError("finite non-empty empirical reference is required")
    if not np.isfinite(values).all():
        raise ValueError("finite empirical values are required")
    ordered = np.sort(reference)
    return np.searchsorted(ordered, values, side="right") / ordered.size


def combine_tail(
    first: np.ndarray, second: np.ndarray, variant: str
) -> np.ndarray:
    if variant == "tail_max":
        return np.maximum(first, second)
    if variant == "tail_noisy_or":
        return 1.0 - (1.0 - first) * (1.0 - second)
    raise ValueError(f"unsupported tail combination: {variant}")


def upper_tail_threshold(scores: np.ndarray, budget: float) -> float:
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    labels = np.zeros(scores.shape, dtype=np.int64)
    calibration = calibrate_threshold(scores, labels, labels, 0, budget)
    if not calibration["feasible"]:
        raise ValueError("upper-tail calibration is infeasible")
    return float(calibration["threshold"])


def operational_metrics(
    *,
    predicted_alert: np.ndarray,
    predicted_unknown: np.ndarray,
    type_prediction: np.ndarray,
    test_labels: np.ndarray,
    test_unknown: np.ndarray,
    benign_index: int,
) -> dict[str, float]:
    actual_attack = test_unknown | (test_labels != benign_index)
    known_attack = (~test_unknown) & (test_labels != benign_index)
    true_positive = int((predicted_alert & actual_attack).sum())
    false_positive = int((predicted_alert & ~actual_attack).sum())
    true_negative = int((~predicted_alert & ~actual_attack).sum())
    false_negative = int((~predicted_alert & actual_attack).sum())
    correctly_typed_known = (
        known_attack
        & predicted_alert
        & ~predicted_unknown
        & (type_prediction == test_labels)
    )
    true_unknown = test_unknown & predicted_unknown
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    return {
        "alert_accuracy": float(
            (true_positive + true_negative) / test_labels.size
        ),
        "alert_precision": float(precision),
        "alert_recall": float(recall),
        "alert_f1": float(
            2.0 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        ),
        "benign_fpr": float(
            false_positive / (false_positive + true_negative)
            if false_positive + true_negative
            else 0.0
        ),
        "known_attack_type_accuracy": float(
            correctly_typed_known.sum() / known_attack.sum()
            if known_attack.sum()
            else 0.0
        ),
        "unknown_attack_alert_recall": float(
            (test_unknown & predicted_alert).sum() / test_unknown.sum()
            if test_unknown.sum()
            else 0.0
        ),
        "unknown_attack_recall": float(
            true_unknown.sum() / test_unknown.sum()
            if test_unknown.sum()
            else 0.0
        ),
        "unknown_label_precision": float(
            true_unknown.sum() / predicted_unknown.sum()
            if predicted_unknown.sum()
            else 0.0
        ),
    }


def gates(metrics: dict[str, float]) -> dict[str, bool]:
    value = {
        "alert_accuracy_at_least_95_percent": (
            metrics["alert_accuracy"] >= TARGET
        ),
        "alert_precision_at_least_95_percent": (
            metrics["alert_precision"] >= TARGET
        ),
        "alert_recall_at_least_95_percent": (
            metrics["alert_recall"] >= TARGET
        ),
        "benign_fpr_below_5_percent": metrics["benign_fpr"] < FPR_LIMIT,
        "known_attack_type_accuracy_at_least_95_percent": (
            metrics["known_attack_type_accuracy"] >= TARGET
        ),
        "unknown_attack_recall_at_least_95_percent": (
            metrics["unknown_attack_recall"] >= TARGET
        ),
    }
    value["basic_warning_95_5_gate"] = all(
        value[key]
        for key in (
            "alert_accuracy_at_least_95_percent",
            "alert_precision_at_least_95_percent",
            "alert_recall_at_least_95_percent",
            "benign_fpr_below_5_percent",
            "known_attack_type_accuracy_at_least_95_percent",
        )
    )
    value["full_known_unknown_95_5_gate"] = (
        value["basic_warning_95_5_gate"]
        and value["unknown_attack_recall_at_least_95_percent"]
    )
    return value


def configuration_key(configuration: dict[str, Any]) -> str:
    return (
        f"{configuration['alert_variant']}"
        f"__a{configuration['alert_budget']:.3f}"
        f"__{configuration['open_variant']}"
        f"__o{configuration['open_budget']:.3f}"
    )


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    metrics = result["macro_mean"]
    value_gates = result["gates"]
    deficits = (
        max(0.0, TARGET - metrics["alert_accuracy"])
        + max(0.0, TARGET - metrics["alert_precision"])
        + max(0.0, TARGET - metrics["alert_recall"])
        + max(0.0, metrics["benign_fpr"] - FPR_LIMIT)
        + max(0.0, TARGET - metrics["known_attack_type_accuracy"])
        + max(0.0, TARGET - metrics["unknown_attack_recall"])
    )
    minimum_margin = min(
        metrics["alert_accuracy"] - TARGET,
        metrics["alert_precision"] - TARGET,
        metrics["alert_recall"] - TARGET,
        FPR_LIMIT - metrics["benign_fpr"],
        metrics["known_attack_type_accuracy"] - TARGET,
        metrics["unknown_attack_recall"] - TARGET,
    )
    return (
        bool(value_gates["full_known_unknown_95_5_gate"]),
        bool(value_gates["basic_warning_95_5_gate"]),
        -deficits,
        minimum_margin,
        metrics["unknown_attack_recall"],
        metrics["known_attack_type_accuracy"],
        metrics["alert_accuracy"],
        -metrics["benign_fpr"],
    )


def mean_metrics(records: Iterable[dict[str, float]]) -> dict[str, float]:
    values = list(records)
    if not values:
        raise ValueError("records are required")
    return {
        key: float(np.mean([record[key] for record in values]))
        for key in values[0]
    }


def prepare_scenario(
    pairwise_dir: Path, xgboost_dir: Path
) -> tuple[dict[str, Any], dict[str, str]]:
    pairwise_metrics_path = pairwise_dir / "metrics.json"
    pairwise_scores_path = pairwise_dir / "scores.npz"
    evidence_path = pairwise_dir / "evidence_package.npz"
    xgboost_metrics_path = xgboost_dir / "metrics.json"
    xgboost_scores_path = xgboost_dir / "scores.npz"
    pairwise_metrics = load(pairwise_metrics_path)
    xgboost_metrics = load(xgboost_metrics_path)
    known_names = [str(value) for value in pairwise_metrics["known_class_names"]]
    if known_names != [
        str(value) for value in xgboost_metrics["known_class_names"]
    ]:
        raise ValueError("known class identity mismatch")
    benign_index = known_names.index("Benign")
    with np.load(pairwise_scores_path, allow_pickle=False) as scores:
        pairwise_validation_labels = np.asarray(
            scores["validation_labels"], dtype=np.int64
        )
        pairwise_test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
        pairwise_test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
    with np.load(evidence_path, allow_pickle=False) as evidence:
        validation_risk = np.asarray(
            evidence["validation_selected_risk"], dtype=np.float64
        )
        test_risk = np.asarray(
            evidence["test_selected_risk"], dtype=np.float64
        )
    with np.load(xgboost_scores_path, allow_pickle=False) as scores:
        validation_probability = np.asarray(
            scores["validation_probability"], dtype=np.float64
        )
        validation_labels = np.asarray(
            scores["validation_labels"], dtype=np.int64
        )
        test_probability = np.asarray(
            scores["test_probability"], dtype=np.float64
        )
        test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
        test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
    if not (
        np.array_equal(validation_labels, pairwise_validation_labels)
        and np.array_equal(test_labels, pairwise_test_labels)
        and np.array_equal(test_unknown, pairwise_test_unknown)
    ):
        raise ValueError("Pairwise and XGBoost split arrays differ")
    validation_benign = validation_labels == benign_index
    validation_attack = validation_labels != benign_index
    xgb_validation_attack = 1.0 - validation_probability[:, benign_index]
    xgb_test_attack = 1.0 - test_probability[:, benign_index]
    validation_attack_tail = empirical_cdf(
        xgb_validation_attack[validation_benign], xgb_validation_attack
    )
    test_attack_tail = empirical_cdf(
        xgb_validation_attack[validation_benign], xgb_test_attack
    )
    validation_risk_benign_tail = empirical_cdf(
        validation_risk[validation_benign], validation_risk
    )
    test_risk_benign_tail = empirical_cdf(
        validation_risk[validation_benign], test_risk
    )
    validation_uncertainty = 1.0 - validation_probability.max(axis=1)
    test_uncertainty = 1.0 - test_probability.max(axis=1)
    validation_risk_attack_tail = empirical_cdf(
        validation_risk[validation_attack], validation_risk
    )
    test_risk_attack_tail = empirical_cdf(
        validation_risk[validation_attack], test_risk
    )
    validation_uncertainty_tail = empirical_cdf(
        validation_uncertainty[validation_attack], validation_uncertainty
    )
    test_uncertainty_tail = empirical_cdf(
        validation_uncertainty[validation_attack], test_uncertainty
    )
    malicious_probability = test_probability.copy()
    malicious_probability[:, benign_index] = -np.inf
    arrays = {
        "benign_index": benign_index,
        "validation_labels": validation_labels,
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "type_prediction": malicious_probability.argmax(axis=1),
        "xgb_validation_attack": xgb_validation_attack,
        "xgb_test_attack": xgb_test_attack,
        "validation_attack_tail": validation_attack_tail,
        "test_attack_tail": test_attack_tail,
        "validation_risk_benign_tail": validation_risk_benign_tail,
        "test_risk_benign_tail": test_risk_benign_tail,
        "validation_risk_attack_tail": validation_risk_attack_tail,
        "test_risk_attack_tail": test_risk_attack_tail,
        "validation_uncertainty_tail": validation_uncertainty_tail,
        "test_uncertainty_tail": test_uncertainty_tail,
    }
    source_hashes = {
        "pairwise_metrics": file_hash(pairwise_metrics_path),
        "pairwise_scores": file_hash(pairwise_scores_path),
        "pairwise_evidence": file_hash(evidence_path),
        "xgboost_metrics": file_hash(xgboost_metrics_path),
        "xgboost_scores": file_hash(xgboost_scores_path),
    }
    return arrays, source_hashes


def alert_scores(
    arrays: dict[str, Any], variant: str
) -> tuple[np.ndarray, np.ndarray]:
    if variant == "xgb_attack":
        return arrays["xgb_validation_attack"], arrays["xgb_test_attack"]
    return (
        combine_tail(
            arrays["validation_attack_tail"],
            arrays["validation_risk_benign_tail"],
            variant,
        ),
        combine_tail(
            arrays["test_attack_tail"],
            arrays["test_risk_benign_tail"],
            variant,
        ),
    )


def open_scores(
    arrays: dict[str, Any], variant: str
) -> tuple[np.ndarray, np.ndarray]:
    if variant == "risk_tail":
        return (
            arrays["validation_risk_attack_tail"],
            arrays["test_risk_attack_tail"],
        )
    return (
        combine_tail(
            arrays["validation_risk_attack_tail"],
            arrays["validation_uncertainty_tail"],
            variant,
        ),
        combine_tail(
            arrays["test_risk_attack_tail"],
            arrays["test_uncertainty_tail"],
            variant,
        ),
    )


def evaluate_configuration(
    prepared: dict[str, dict[str, Any]], configuration: dict[str, Any]
) -> dict[str, Any]:
    per_scenario = {}
    for scenario, arrays in prepared.items():
        validation_alert_score, test_alert_score = alert_scores(
            arrays, configuration["alert_variant"]
        )
        validation_open_score, test_open_score = open_scores(
            arrays, configuration["open_variant"]
        )
        benign_index = int(arrays["benign_index"])
        validation_labels = arrays["validation_labels"]
        alert_calibration = calibrate_threshold(
            validation_alert_score,
            np.full(validation_labels.shape, benign_index, dtype=np.int64),
            validation_labels,
            benign_index,
            float(configuration["alert_budget"]),
        )
        open_threshold = upper_tail_threshold(
            validation_open_score[validation_labels != benign_index],
            float(configuration["open_budget"]),
        )
        predicted_alert = test_alert_score >= float(
            alert_calibration["threshold"]
        )
        predicted_unknown = predicted_alert & (
            test_open_score >= open_threshold
        )
        metrics = operational_metrics(
            predicted_alert=predicted_alert,
            predicted_unknown=predicted_unknown,
            type_prediction=arrays["type_prediction"],
            test_labels=arrays["test_labels"],
            test_unknown=arrays["test_unknown"],
            benign_index=benign_index,
        )
        per_scenario[scenario] = {
            "metrics": metrics,
            "gates": gates(metrics),
            "alert_threshold": float(alert_calibration["threshold"]),
            "open_threshold": open_threshold,
        }
    macro = mean_metrics(
        value["metrics"] for value in per_scenario.values()
    )
    return {
        "configuration": configuration,
        "macro_mean": macro,
        "gates": gates(macro),
        "scenario_basic_gate_pass_count": sum(
            value["gates"]["basic_warning_95_5_gate"]
            for value in per_scenario.values()
        ),
        "scenario_full_gate_pass_count": sum(
            value["gates"]["full_known_unknown_95_5_gate"]
            for value in per_scenario.values()
        ),
        "per_scenario": per_scenario,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = load(protocol_path)
    verify_canonical(protocol, "development protocol")
    expected_space = {
        "alert_variants": list(ALERT_VARIANTS),
        "alert_budgets": list(ALERT_BUDGETS),
        "open_variants": list(OPEN_VARIANTS),
        "open_budgets": list(OPEN_BUDGETS),
        "candidate_count": (
            len(ALERT_VARIANTS)
            * len(ALERT_BUDGETS)
            * len(OPEN_VARIANTS)
            * len(OPEN_BUDGETS)
        ),
    }
    if protocol.get("candidate_space") != expected_space:
        raise ValueError("development candidate space differs from protocol")
    implementation = Path(__file__).resolve()
    if protocol["implementation_sha256"].get(implementation.name) != file_hash(
        implementation
    ):
        raise ValueError("development evaluator hash drifted")
    pairwise_root = Path(protocol["pairwise_root"]).resolve()
    xgboost_root = Path(protocol["xgboost_root"]).resolve()
    pairwise_dirs = sorted(
        path.parent for path in pairwise_root.glob("*/metrics.json")
    )
    if len(pairwise_dirs) != 14:
        raise ValueError("exactly 14 seed7 Pairwise tasks are required")
    prepared = {}
    sources = {}
    for pairwise_dir in pairwise_dirs:
        scenario = pairwise_dir.name.removesuffix("_seed7")
        xgboost_dir = xgboost_root / f"{scenario}_seed7"
        prepared[scenario], sources[scenario] = prepare_scenario(
            pairwise_dir, xgboost_dir
        )
    if sources != protocol["source_sha256"]:
        raise ValueError("development source hashes differ from protocol")
    results = []
    for alert_variant, alert_budget, open_variant, open_budget in product(
        ALERT_VARIANTS, ALERT_BUDGETS, OPEN_VARIANTS, OPEN_BUDGETS
    ):
        configuration = {
            "alert_variant": alert_variant,
            "alert_budget": alert_budget,
            "open_variant": open_variant,
            "open_budget": open_budget,
        }
        results.append(evaluate_configuration(prepared, configuration))
    selected = max(results, key=selection_key)
    compact_candidates = {
        configuration_key(value["configuration"]): {
            "configuration": value["configuration"],
            "macro_mean": value["macro_mean"],
            "gates": value["gates"],
            "scenario_basic_gate_pass_count": value[
                "scenario_basic_gate_pass_count"
            ],
            "scenario_full_gate_pass_count": value[
                "scenario_full_gate_pass_count"
            ],
        }
        for value in results
    }
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_hybrid_self_algorithm_development_v1",
        "state": "complete_seed7_development_selection",
        "algorithm": (
            "Empirical-Tail Hybrid CAEOS: XGBoost known expert plus "
            "Pairwise-CAEOS conflict and uncertainty open-set head"
        ),
        "candidate_count": len(results),
        "selected": selected,
        "candidate_summary": compact_candidates,
        "source_sha256": sources,
        "binding": {
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "implementation_sha256": file_hash(Path(__file__).resolve()),
        },
        "selection_rule": {
            "order": [
                "full_known_unknown_95_5_gate",
                "basic_warning_95_5_gate",
                "minimum_total_target_deficit",
                "minimum_target_margin",
                "unknown_attack_recall",
                "known_attack_type_accuracy",
                "alert_accuracy",
                "lower_benign_fpr",
            ],
            "single_global_configuration_across_14_scenarios": True,
        },
        "claim_boundary": {
            "seed7_test_and_unknown_labels_used_for_development_selection": True,
            "development_result_is_not_confirmation": True,
            "fresh_907_911_919_results_were_not_read_by_this_script": True,
            "selected_configuration_must_be_frozen_before_fresh_evaluation": True,
            "xgboost_alone_is_a_baseline_not_the_self_algorithm": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": payload["manifest_sha256"],
                "candidate_count": payload["candidate_count"],
                "selected_configuration": selected["configuration"],
                "selected_macro_mean": selected["macro_mean"],
                "selected_gates": selected["gates"],
                "scenario_basic_gate_pass_count": selected[
                    "scenario_basic_gate_pass_count"
                ],
                "scenario_full_gate_pass_count": selected[
                    "scenario_full_gate_pass_count"
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
