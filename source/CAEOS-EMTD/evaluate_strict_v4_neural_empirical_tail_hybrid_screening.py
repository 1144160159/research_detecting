from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_hybrid_self_algorithm_development import (
    ALERT_BUDGETS,
    ALERT_VARIANTS,
    OPEN_BUDGETS,
    OPEN_VARIANTS,
    canonical_hash,
    combine_tail,
    empirical_cdf,
    file_hash,
    gates,
    mean_metrics,
    operational_metrics,
    upper_tail_threshold,
)
from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold


DEFAULT_RISK_NAMES = (
    "msp",
    "energy",
    "max_logit",
    "mahalanobis",
    "relative_mahalanobis",
    "knn",
    "vim",
    "nci",
    "energy_cea",
    "nci_cea",
    "scale",
    "openmax",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def prepare_scenario(
    neural_dir: Path,
    xgboost_dir: Path,
    risk_names: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, str]]:
    neural_metrics_path = neural_dir / "metrics.json"
    neural_scores_path = neural_dir / "scores.npz"
    xgboost_metrics_path = xgboost_dir / "metrics.json"
    xgboost_scores_path = xgboost_dir / "scores.npz"
    neural_metrics = load_json(neural_metrics_path)
    xgboost_metrics = load_json(xgboost_metrics_path)
    known_names = [str(value) for value in neural_metrics["known_class_names"]]
    if known_names != [
        str(value) for value in xgboost_metrics["known_class_names"]
    ]:
        raise ValueError("known class identity mismatch")
    benign_index = known_names.index("Benign")
    with np.load(neural_scores_path, allow_pickle=False) as neural_scores:
        neural_validation_labels = np.asarray(
            neural_scores["validation_labels"], dtype=np.int64
        )
        neural_test_labels = np.asarray(
            neural_scores["test_labels"], dtype=np.int64
        )
        neural_test_unknown = np.asarray(
            neural_scores["test_unknown"], dtype=bool
        )
        neural_risks = {
            risk_name: (
                np.asarray(
                    neural_scores[f"validation_{risk_name}"],
                    dtype=np.float64,
                ),
                np.asarray(
                    neural_scores[f"test_{risk_name}"], dtype=np.float64
                ),
            )
            for risk_name in risk_names
        }
    with np.load(xgboost_scores_path, allow_pickle=False) as xgboost_scores:
        validation_probability = np.asarray(
            xgboost_scores["validation_probability"], dtype=np.float64
        )
        validation_labels = np.asarray(
            xgboost_scores["validation_labels"], dtype=np.int64
        )
        test_probability = np.asarray(
            xgboost_scores["test_probability"], dtype=np.float64
        )
        test_labels = np.asarray(
            xgboost_scores["test_labels"], dtype=np.int64
        )
        test_unknown = np.asarray(
            xgboost_scores["test_unknown"], dtype=bool
        )
    if not (
        np.array_equal(validation_labels, neural_validation_labels)
        and np.array_equal(test_labels, neural_test_labels)
        and np.array_equal(test_unknown, neural_test_unknown)
    ):
        raise ValueError("Neural and XGBoost split arrays differ")
    validation_benign = validation_labels == benign_index
    validation_attack = ~validation_benign
    xgboost_validation_attack = 1.0 - validation_probability[:, benign_index]
    xgboost_test_attack = 1.0 - test_probability[:, benign_index]
    validation_attack_tail = empirical_cdf(
        xgboost_validation_attack[validation_benign],
        xgboost_validation_attack,
    )
    test_attack_tail = empirical_cdf(
        xgboost_validation_attack[validation_benign], xgboost_test_attack
    )
    validation_uncertainty = 1.0 - validation_probability.max(axis=1)
    test_uncertainty = 1.0 - test_probability.max(axis=1)
    validation_uncertainty_tail = empirical_cdf(
        validation_uncertainty[validation_attack], validation_uncertainty
    )
    test_uncertainty_tail = empirical_cdf(
        validation_uncertainty[validation_attack], test_uncertainty
    )
    risk_tails = {}
    for risk_name, (validation_risk, test_risk) in neural_risks.items():
        if not (
            np.isfinite(validation_risk).all()
            and np.isfinite(test_risk).all()
        ):
            raise ValueError(f"non-finite neural risk: {risk_name}")
        risk_tails[risk_name] = {
            "validation_benign": empirical_cdf(
                validation_risk[validation_benign], validation_risk
            ),
            "test_benign": empirical_cdf(
                validation_risk[validation_benign], test_risk
            ),
            "validation_attack": empirical_cdf(
                validation_risk[validation_attack], validation_risk
            ),
            "test_attack": empirical_cdf(
                validation_risk[validation_attack], test_risk
            ),
        }
    malicious_probability = test_probability.copy()
    malicious_probability[:, benign_index] = -np.inf
    validation_malicious_probability = validation_probability.copy()
    validation_malicious_probability[:, benign_index] = -np.inf
    arrays = {
        "benign_index": benign_index,
        "validation_labels": validation_labels,
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "validation_type_prediction": (
            validation_malicious_probability.argmax(axis=1)
        ),
        "type_prediction": malicious_probability.argmax(axis=1),
        "xgboost_validation_attack": xgboost_validation_attack,
        "xgboost_test_attack": xgboost_test_attack,
        "validation_attack_tail": validation_attack_tail,
        "test_attack_tail": test_attack_tail,
        "validation_uncertainty_tail": validation_uncertainty_tail,
        "test_uncertainty_tail": test_uncertainty_tail,
        "validation_uncertainty": validation_uncertainty,
        "test_uncertainty": test_uncertainty,
        "risk_values": {
            risk_name: {
                "validation": values[0],
                "test": values[1],
            }
            for risk_name, values in neural_risks.items()
        },
        "risk_tails": risk_tails,
    }
    hashes = {
        "neural_metrics": file_hash(neural_metrics_path),
        "neural_scores": file_hash(neural_scores_path),
        "xgboost_metrics": file_hash(xgboost_metrics_path),
        "xgboost_scores": file_hash(xgboost_scores_path),
    }
    return arrays, hashes


def scores_for(
    arrays: dict[str, Any], configuration: dict[str, Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    risk_tail = arrays["risk_tails"][configuration["risk_name"]]
    alert_variant = configuration["alert_variant"]
    if alert_variant == "xgb_attack":
        validation_alert = arrays["xgboost_validation_attack"]
        test_alert = arrays["xgboost_test_attack"]
    else:
        validation_alert = combine_tail(
            arrays["validation_attack_tail"],
            risk_tail["validation_benign"],
            alert_variant,
        )
        test_alert = combine_tail(
            arrays["test_attack_tail"],
            risk_tail["test_benign"],
            alert_variant,
        )
    open_variant = configuration["open_variant"]
    if open_variant == "risk_tail":
        validation_open = risk_tail["validation_attack"]
        test_open = risk_tail["test_attack"]
    else:
        validation_open = combine_tail(
            risk_tail["validation_attack"],
            arrays["validation_uncertainty_tail"],
            open_variant,
        )
        test_open = combine_tail(
            risk_tail["test_attack"],
            arrays["test_uncertainty_tail"],
            open_variant,
        )
    return validation_alert, test_alert, validation_open, test_open


def evaluate_configuration(
    prepared: dict[str, dict[str, Any]], configuration: dict[str, Any]
) -> dict[str, Any]:
    per_scenario = {}
    for scenario, arrays in prepared.items():
        (
            validation_alert,
            test_alert,
            validation_open,
            test_open,
        ) = scores_for(arrays, configuration)
        benign_index = int(arrays["benign_index"])
        validation_labels = arrays["validation_labels"]
        calibration = calibrate_threshold(
            validation_alert,
            np.full(validation_labels.shape, benign_index, dtype=np.int64),
            validation_labels,
            benign_index,
            float(configuration["alert_budget"]),
        )
        if not calibration["feasible"]:
            raise ValueError(f"infeasible alert calibration: {scenario}")
        open_threshold = upper_tail_threshold(
            validation_open[validation_labels != benign_index],
            float(configuration["open_budget"]),
        )
        predicted_alert = test_alert >= float(calibration["threshold"])
        predicted_unknown = predicted_alert & (test_open >= open_threshold)
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
            "alert_threshold": float(calibration["threshold"]),
            "open_threshold": float(open_threshold),
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


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    metrics = result["macro_mean"]
    scenario_count = len(result["per_scenario"])
    return (
        result["scenario_full_gate_pass_count"] == scenario_count,
        result["scenario_basic_gate_pass_count"] == scenario_count,
        result["scenario_full_gate_pass_count"],
        result["scenario_basic_gate_pass_count"],
        result["gates"]["full_known_unknown_95_5_gate"],
        result["gates"]["basic_warning_95_5_gate"],
        metrics["unknown_attack_recall"],
        metrics["unknown_attack_alert_recall"],
        metrics["known_attack_type_accuracy"],
        metrics["alert_accuracy"],
        -metrics["benign_fpr"],
    )


def scenario_name(path: Path, suffix: str) -> str:
    if not path.name.endswith(suffix):
        raise ValueError(f"unexpected task directory: {path.name}")
    return path.name[: -len(suffix)]


def run_screening(
    neural_root: Path,
    xgboost_root: Path,
    risk_names: tuple[str, ...],
    alert_budgets: tuple[float, ...] = ALERT_BUDGETS,
    open_budgets: tuple[float, ...] = OPEN_BUDGETS,
) -> dict[str, Any]:
    neural_dirs = sorted(
        path.parent for path in neural_root.glob("*_seed7_mlp/metrics.json")
    )
    if len(neural_dirs) != 14:
        raise ValueError("exactly 14 seed7 neural tasks are required")
    prepared = {}
    sources = {}
    for neural_dir in neural_dirs:
        scenario = scenario_name(neural_dir, "_seed7_mlp")
        prepared[scenario], sources[scenario] = prepare_scenario(
            neural_dir,
            xgboost_root / f"{scenario}_seed7",
            risk_names,
        )
    results = []
    for (
        risk_name,
        alert_variant,
        alert_budget,
        open_variant,
        open_budget,
    ) in product(
        risk_names,
        ALERT_VARIANTS,
        alert_budgets,
        OPEN_VARIANTS,
        open_budgets,
    ):
        results.append(
            evaluate_configuration(
                prepared,
                {
                    "risk_name": risk_name,
                    "alert_variant": alert_variant,
                    "alert_budget": alert_budget,
                    "open_variant": open_variant,
                    "open_budget": open_budget,
                },
            )
        )
    selected = max(results, key=selection_key)
    payload: dict[str, Any] = {
        "schema_version": (
            "strict_v4_neural_empirical_tail_hybrid_screening_v1"
        ),
        "state": "complete_architecture_screening_diagnostic",
        "candidate_count": len(results),
        "risk_names": list(risk_names),
        "alert_budgets": list(alert_budgets),
        "open_budgets": list(open_budgets),
        "selected": selected,
        "source_sha256": sources,
        "top_candidates": [
            {
                key: value[key]
                for key in (
                    "configuration",
                    "macro_mean",
                    "gates",
                    "scenario_basic_gate_pass_count",
                    "scenario_full_gate_pass_count",
                )
            }
            for value in sorted(results, key=selection_key, reverse=True)[:20]
        ],
        "claim_boundary": {
            "read_only_architecture_screening": True,
            "seed7_unknown_test_labels_used_for_selection": True,
            "legacy_neural_and_cpu_xgboost_artifacts_are_not_gpu_confirmation": (
                True
            ),
            "eligible_to_trigger_fresh_gpu_training": bool(
                selected["gates"]["basic_warning_95_5_gate"]
            ),
            "eligible_for_paper_effect_claim": False,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--neural-root", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--risk-names", default=",".join(DEFAULT_RISK_NAMES)
    )
    parser.add_argument("--alert-budgets", default="0.01,0.02,0.03,0.04")
    parser.add_argument("--open-budgets", default="0.005,0.01,0.02,0.03,0.04")
    args = parser.parse_args()
    risk_names = tuple(
        value.strip()
        for value in args.risk_names.split(",")
        if value.strip()
    )
    if not risk_names or len(risk_names) != len(set(risk_names)):
        raise ValueError("risk names must be non-empty and unique")
    alert_budgets = tuple(
        float(value)
        for value in args.alert_budgets.split(",")
        if value.strip()
    )
    open_budgets = tuple(
        float(value)
        for value in args.open_budgets.split(",")
        if value.strip()
    )
    for label, budgets in (
        ("alert", alert_budgets),
        ("open", open_budgets),
    ):
        if (
            not budgets
            or len(budgets) != len(set(budgets))
            or any(value <= 0.0 or value >= 0.05 for value in budgets)
        ):
            raise ValueError(
                f"{label} budgets must be unique values in (0, 0.05)"
            )
    payload = run_screening(
        args.neural_root.resolve(),
        args.xgboost_root.resolve(),
        risk_names,
        alert_budgets,
        open_budgets,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": payload["manifest_sha256"],
                "candidate_count": payload["candidate_count"],
                "selected": payload["selected"],
                "claim_boundary": payload["claim_boundary"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
