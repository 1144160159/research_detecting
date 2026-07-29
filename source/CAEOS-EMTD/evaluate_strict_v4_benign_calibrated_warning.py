#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


REPORT_METRICS = (
    "alert_accuracy",
    "alert_precision",
    "alert_recall",
    "alert_f1",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
    "unknown_attack_recall",
    "unknown_label_precision",
    "three_level_accuracy",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(payload: Dict[str, Any]) -> str:
    canonical = dict(payload)
    canonical.pop("manifest_sha256", None)
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _ratio(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return (
        float(2.0 * precision * recall / (precision + recall))
        if precision + recall
        else 0.0
    )


def calibrate_threshold(
    validation_risk: np.ndarray,
    validation_prediction: np.ndarray,
    validation_labels: np.ndarray,
    benign_index: int,
    benign_fpr_budget: float,
) -> Dict[str, Any]:
    benign = validation_labels == benign_index
    benign_count = int(benign.sum())
    if benign_count == 0:
        raise ValueError("validation split has no benign samples")
    base_false_alert = benign & (validation_prediction != benign_index)
    base_false_alert_count = int(base_false_alert.sum())
    maximum_false_alert_count = int(np.floor(benign_fpr_budget * benign_count))
    allowed_rejections = maximum_false_alert_count - base_false_alert_count
    if allowed_rejections < 0:
        return {
            "feasible": False,
            "threshold": float("inf"),
            "benign_count": benign_count,
            "base_false_alert_count": base_false_alert_count,
            "allowed_risk_rejection_count": 0,
            "achieved_validation_benign_fpr": _ratio(
                base_false_alert_count, benign_count
            ),
        }

    eligible_risk = validation_risk[benign & ~base_false_alert]
    if allowed_rejections >= eligible_risk.size:
        threshold = float("-inf")
    elif allowed_rejections == 0:
        threshold = float(np.nextafter(np.max(eligible_risk), np.inf))
    else:
        unique_values = np.unique(eligible_risk)
        feasible_values = [
            float(value)
            for value in unique_values
            if int((eligible_risk >= value).sum()) <= allowed_rejections
        ]
        threshold = min(feasible_values) if feasible_values else float(
            np.nextafter(np.max(eligible_risk), np.inf)
        )

    rejected = eligible_risk >= threshold
    achieved_count = base_false_alert_count + int(rejected.sum())
    return {
        "feasible": True,
        "threshold": threshold,
        "benign_count": benign_count,
        "base_false_alert_count": base_false_alert_count,
        "allowed_risk_rejection_count": max(0, allowed_rejections),
        "achieved_validation_benign_fpr": _ratio(achieved_count, benign_count),
    }


def evaluate_task(
    task_dir: Path, benign_fpr_budget: float, alert_mode: str
) -> Dict[str, Any]:
    paths = {
        "metrics": task_dir / "metrics.json",
        "scores": task_dir / "scores.npz",
        "evidence": task_dir / "evidence_package.npz",
        "provenance": task_dir / "provenance.json",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{task_dir}: missing {missing}")

    with paths["metrics"].open("r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    with paths["provenance"].open("r", encoding="utf-8") as handle:
        provenance = json.load(handle)
    with np.load(paths["scores"], allow_pickle=False) as scores:
        validation_labels = np.asarray(scores["validation_labels"], dtype=np.int64)
        test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
        test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
        score_test_prediction = np.asarray(
            scores["test_prediction"], dtype=np.int64
        )
    with np.load(paths["evidence"], allow_pickle=False) as evidence:
        selected_risk_name = str(evidence["selected_risk_name"].item())
        validation_risk = np.asarray(
            evidence["validation_selected_risk"], dtype=np.float64
        )
        test_risk = np.asarray(evidence["test_selected_risk"], dtype=np.float64)
        validation_probability = np.asarray(
            evidence["validation_final_probability"], dtype=np.float64
        )
        test_probability = np.asarray(
            evidence["test_final_probability"], dtype=np.float64
        )
        evidence_prediction = np.asarray(
            evidence["test_known_prediction"], dtype=np.int64
        )
        evidence_known_classes = [
            str(value) for value in evidence["known_class_names"].tolist()
        ]

    known_class_names = [str(value) for value in metrics["known_class_names"]]
    if evidence_known_classes != known_class_names:
        raise ValueError(f"{task_dir}: known class identity mismatch")
    if selected_risk_name != str(metrics["selected_risk"]):
        raise ValueError(f"{task_dir}: selected risk identity mismatch")
    if not np.array_equal(evidence_prediction, score_test_prediction):
        raise ValueError(f"{task_dir}: test prediction mismatch")
    if validation_probability.shape[0] != validation_labels.size:
        raise ValueError(f"{task_dir}: validation shape mismatch")
    if not (
        test_probability.shape[0]
        == test_labels.size
        == test_unknown.size
        == test_risk.size
    ):
        raise ValueError(f"{task_dir}: test shape mismatch")
    if not (
        np.isfinite(validation_risk).all()
        and np.isfinite(test_risk).all()
        and np.isfinite(validation_probability).all()
        and np.isfinite(test_probability).all()
    ):
        raise ValueError(f"{task_dir}: non-finite evidence")

    benign_name = str(metrics["arguments"]["benign_class"])
    benign_index = known_class_names.index(benign_name)
    validation_prediction = validation_probability.argmax(axis=1)
    test_prediction = test_probability.argmax(axis=1)
    if not np.array_equal(test_prediction, score_test_prediction):
        raise ValueError(f"{task_dir}: probability argmax mismatch")

    known = ~test_unknown
    actual_attack = test_unknown | (test_labels != benign_index)
    if alert_mode == "legacy_union":
        calibration = calibrate_threshold(
            validation_risk,
            validation_prediction,
            validation_labels,
            benign_index,
            benign_fpr_budget,
        )
        alert_threshold = float(calibration["threshold"])
        open_set_threshold = alert_threshold
        open_rejected = test_risk >= open_set_threshold
        predicted_alert = open_rejected | (test_prediction != benign_index)
        predicted_unknown = open_rejected
        type_prediction = test_prediction
    elif alert_mode == "hierarchical_probability":
        validation_attack_score = 1.0 - validation_probability[:, benign_index]
        test_attack_score = 1.0 - test_probability[:, benign_index]
        all_benign_prediction = np.full(
            validation_labels.shape, benign_index, dtype=np.int64
        )
        calibration = calibrate_threshold(
            validation_attack_score,
            all_benign_prediction,
            validation_labels,
            benign_index,
            benign_fpr_budget,
        )
        alert_threshold = float(calibration["threshold"])
        open_set_threshold = float(metrics["validation_thresholds"][selected_risk_name])
        open_rejected = test_risk >= open_set_threshold
        predicted_alert = test_attack_score >= alert_threshold
        predicted_unknown = predicted_alert & open_rejected
        malicious_probability = test_probability.copy()
        malicious_probability[:, benign_index] = -np.inf
        type_prediction = malicious_probability.argmax(axis=1)
    else:
        raise ValueError(f"unsupported alert mode: {alert_mode}")

    true_positive = int((predicted_alert & actual_attack).sum())
    false_positive = int((predicted_alert & ~actual_attack).sum())
    true_negative = int((~predicted_alert & ~actual_attack).sum())
    false_negative = int((~predicted_alert & actual_attack).sum())
    alert_precision = _ratio(true_positive, true_positive + false_positive)
    alert_recall = _ratio(true_positive, true_positive + false_negative)

    known_attack = known & (test_labels != benign_index)
    correctly_typed_known_attack = (
        known_attack
        & predicted_alert
        & ~predicted_unknown
        & (type_prediction == test_labels)
    )
    three_level_correct = (
        (~actual_attack & ~predicted_alert)
        | correctly_typed_known_attack
        | (test_unknown & predicted_unknown)
    )
    operational_metrics = {
        "alert_accuracy": _ratio(true_positive + true_negative, test_labels.size),
        "alert_precision": alert_precision,
        "alert_recall": alert_recall,
        "alert_f1": _f1(alert_precision, alert_recall),
        "benign_fpr": _ratio(false_positive, false_positive + true_negative),
        "known_attack_type_accuracy": _ratio(
            int(correctly_typed_known_attack.sum()), int(known_attack.sum())
        ),
        "unknown_attack_alert_recall": _ratio(
            int((test_unknown & predicted_alert).sum()), int(test_unknown.sum())
        ),
        "unknown_attack_recall": _ratio(
            int((test_unknown & predicted_unknown).sum()), int(test_unknown.sum())
        ),
        "unknown_label_precision": _ratio(
            int((test_unknown & predicted_unknown).sum()), int(predicted_unknown.sum())
        ),
        "three_level_accuracy": _ratio(
            int(three_level_correct.sum()), test_labels.size
        ),
    }
    gates = {
        "alert_accuracy_at_least_95_percent": (
            operational_metrics["alert_accuracy"] >= 0.95
        ),
        "alert_precision_at_least_95_percent": (
            operational_metrics["alert_precision"] >= 0.95
        ),
        "alert_recall_at_least_95_percent": (
            operational_metrics["alert_recall"] >= 0.95
        ),
        "benign_fpr_below_5_percent": operational_metrics["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            operational_metrics["known_attack_type_accuracy"] >= 0.95
        ),
        "unknown_attack_recall_at_least_95_percent": (
            operational_metrics["unknown_attack_recall"] >= 0.95
        ),
    }
    gates["basic_warning_95_5_gate"] = bool(
        gates["alert_accuracy_at_least_95_percent"]
        and gates["alert_precision_at_least_95_percent"]
        and gates["alert_recall_at_least_95_percent"]
        and gates["benign_fpr_below_5_percent"]
        and gates["known_attack_type_accuracy_at_least_95_percent"]
    )
    gates["full_known_unknown_95_5_gate"] = bool(
        gates["basic_warning_95_5_gate"]
        and gates["unknown_attack_recall_at_least_95_percent"]
    )

    task = provenance["task"]
    return {
        "suite": str(task["suite"]),
        "scenario": str(task["scenario"]),
        "seed": int(task["seed"]),
        "selected_risk": selected_risk_name,
        "alert_mode": alert_mode,
        "alert_threshold": alert_threshold,
        "open_set_threshold": open_set_threshold,
        "calibration": calibration,
        "operational_metrics": operational_metrics,
        "gates": gates,
        "source_sha256": {name: _sha256(path) for name, path in paths.items()},
    }


def _aggregate_gates(mean: Dict[str, float]) -> Dict[str, bool]:
    gates = {
        "alert_accuracy_at_least_95_percent": mean["alert_accuracy"] >= 0.95,
        "alert_precision_at_least_95_percent": mean["alert_precision"] >= 0.95,
        "alert_recall_at_least_95_percent": mean["alert_recall"] >= 0.95,
        "benign_fpr_below_5_percent": mean["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            mean["known_attack_type_accuracy"] >= 0.95
        ),
        "unknown_attack_recall_at_least_95_percent": (
            mean["unknown_attack_recall"] >= 0.95
        ),
    }
    gates["basic_warning_95_5_gate"] = bool(
        gates["alert_accuracy_at_least_95_percent"]
        and gates["alert_precision_at_least_95_percent"]
        and gates["alert_recall_at_least_95_percent"]
        and gates["benign_fpr_below_5_percent"]
        and gates["known_attack_type_accuracy_at_least_95_percent"]
    )
    gates["full_known_unknown_95_5_gate"] = bool(
        gates["basic_warning_95_5_gate"]
        and gates["unknown_attack_recall_at_least_95_percent"]
    )
    return gates


def _mean_metrics(records: List[Dict[str, Any]]) -> Dict[str, float]:
    if not records:
        raise ValueError("cannot aggregate empty records")
    return {
        key: float(
            np.mean(
                [record["operational_metrics"][key] for record in records]
            )
        )
        for key in REPORT_METRICS
    }


def build_evaluation(
    run_root: Path,
    suites: List[str],
    benign_fpr_budget: float,
    alert_mode: str,
    seeds: List[int] | None = None,
) -> Dict[str, Any]:
    records = []
    seed_filter = None if seeds is None else set(seeds)
    if seed_filter is not None and len(seed_filter) != len(seeds):
        raise ValueError("seed filter contains duplicates")
    for suite in suites:
        suite_dir = run_root / suite
        if not suite_dir.is_dir():
            raise FileNotFoundError(f"missing suite directory: {suite_dir}")
        for task_dir in sorted(suite_dir.iterdir()):
            if not task_dir.is_dir() or not (task_dir / "metrics.json").is_file():
                continue
            record = evaluate_task(task_dir, benign_fpr_budget, alert_mode)
            if seed_filter is None or record["seed"] in seed_filter:
                records.append(record)
    if not records:
        raise ValueError("no complete tasks")
    observed_seeds = sorted({int(record["seed"]) for record in records})
    if seed_filter is not None and observed_seeds != sorted(seed_filter):
        raise ValueError(
            f"requested seeds do not match observed seeds: "
            f"{sorted(seed_filter)} != {observed_seeds}"
        )

    by_suite: Dict[str, Any] = {}
    for suite in suites:
        suite_records = [record for record in records if record["suite"] == suite]
        if not suite_records:
            raise ValueError(f"no records for requested suite: {suite}")
        by_suite[suite] = {
            "scenario_count": len(suite_records),
            "calibration_feasible_count": sum(
                bool(record["calibration"]["feasible"]) for record in suite_records
            ),
            "mean": _mean_metrics(suite_records),
            "basic_warning_95_5_pass_count": sum(
                bool(record["gates"]["basic_warning_95_5_gate"])
                for record in suite_records
            ),
            "full_known_unknown_95_5_pass_count": sum(
                bool(record["gates"]["full_known_unknown_95_5_gate"])
                for record in suite_records
            ),
        }
    suite_equal_mean = {
        key: float(np.mean([by_suite[suite]["mean"][key] for suite in suites]))
        for key in REPORT_METRICS
    }
    aggregate_gates = _aggregate_gates(suite_equal_mean)
    by_seed: Dict[str, Any] = {}
    for seed in observed_seeds:
        seed_records = [record for record in records if record["seed"] == seed]
        mean = _mean_metrics(seed_records)
        by_seed[str(seed)] = {
            "scenario_count": len(seed_records),
            "suite_count": len({record["suite"] for record in seed_records}),
            "mean": mean,
            "gates": _aggregate_gates(mean),
        }

    payload: Dict[str, Any] = {
        "schema_version": "strict_v4_benign_calibrated_warning_evaluation_v1",
        "state": "complete_read_only_recalibration",
        "claim_boundary": {
            "threshold_uses_validation_benign_only": True,
            "unknown_or_test_labels_used_for_threshold": False,
            "selected_risk_identity_is_inherited_without_reselection": True,
            "this_is_a_seed7_diagnostic_not_multiseed_confirmation": (
                observed_seeds == [7]
            ),
            "seed_scope_is_explicitly_reported": True,
            "suite_scope_was_fixed_by_command_before_metric_computation": True,
        },
        "run_root": str(run_root.resolve()),
        "suites": suites,
        "requested_seeds": None if seeds is None else sorted(seeds),
        "observed_seeds": observed_seeds,
        "alert_mode": alert_mode,
        "validation_benign_fpr_budget": benign_fpr_budget,
        "scenario_count": len(records),
        "by_suite": by_suite,
        "by_seed": by_seed,
        "suite_equal_mean": suite_equal_mean,
        "aggregate_gates": aggregate_gates,
        "all_seed_basic_warning_95_5_gate": all(
            value["gates"]["basic_warning_95_5_gate"]
            for value in by_seed.values()
        ),
        "all_seed_full_known_unknown_95_5_gate": all(
            value["gates"]["full_known_unknown_95_5_gate"]
            for value in by_seed.values()
        ),
        "records": records,
    }
    payload["manifest_sha256"] = _canonical_sha256(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--suites", nargs="+", required=True)
    parser.add_argument(
        "--validation-benign-fpr-budget", type=float, default=0.01
    )
    parser.add_argument(
        "--alert-mode",
        choices=("legacy_union", "hierarchical_probability"),
        default="legacy_union",
    )
    parser.add_argument(
        "--seeds",
        default="",
        help="Optional comma-separated seed filter with exact coverage checks",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 0.0 < args.validation_benign_fpr_budget < 0.05:
        raise ValueError("validation benign FPR budget must be in (0, 0.05)")

    seeds = (
        None
        if not args.seeds.strip()
        else [int(value) for value in args.seeds.split(",") if value.strip()]
    )
    payload = build_evaluation(
        args.run_root,
        [str(value) for value in args.suites],
        float(args.validation_benign_fpr_budget),
        str(args.alert_mode),
        seeds,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": payload["manifest_sha256"],
                "scenario_count": payload["scenario_count"],
                "suite_equal_mean": payload["suite_equal_mean"],
                "aggregate_gates": payload["aggregate_gates"],
                "all_seed_basic_warning_95_5_gate": payload[
                    "all_seed_basic_warning_95_5_gate"
                ],
                "all_seed_full_known_unknown_95_5_gate": payload[
                    "all_seed_full_known_unknown_95_5_gate"
                ],
                "output": str(args.output.resolve()),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
