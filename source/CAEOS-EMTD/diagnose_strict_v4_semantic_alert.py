from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def alert_metrics(
    alert: np.ndarray,
    labels: np.ndarray,
    is_unknown: np.ndarray,
) -> dict[str, float]:
    unknown = is_unknown.astype(bool)
    benign = (~unknown) & (labels == 0)
    known_attack = (~unknown) & (labels != 0)
    actual_attack = ~benign
    true_positive = int(np.sum(alert & actual_attack))
    predicted_positive = int(np.sum(alert))
    actual_positive = int(np.sum(actual_attack))
    return {
        "alert_accuracy": float(np.mean(alert == actual_attack)),
        "alert_precision": (
            float(true_positive / predicted_positive)
            if predicted_positive
            else 0.0
        ),
        "attack_recall": (
            float(true_positive / actual_positive)
            if actual_positive
            else 0.0
        ),
        "benign_fpr": float(alert[benign].mean()),
        "known_attack_alert_recall": float(alert[known_attack].mean()),
        "unknown_attack_alert_recall": float(alert[unknown].mean()),
    }


def diagnose_scores(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as arrays:
        labels = arrays["label"].astype(np.int64)
        is_unknown = arrays["is_unknown"].astype(bool)
        current = arrays["alert"].astype(bool)
        predicted_attack = arrays["known_prediction"].astype(np.int64) != 0
        rejected_unknown = arrays["unknown_prediction"].astype(bool)
    rules = {
        "current_operational_alert": current,
        "predicted_non_benign_class": predicted_attack,
        "rejected_as_unknown": rejected_unknown,
        "categorical_semantic_union": (
            predicted_attack | rejected_unknown
        ),
        "full_semantic_union": (
            current | predicted_attack | rejected_unknown
        ),
    }
    return {
        "scores_path": str(path.resolve()),
        "scores_sha256": file_hash(path),
        "sample_count": int(len(labels)),
        "rule_metrics": {
            name: alert_metrics(rule, labels, is_unknown)
            for name, rule in rules.items()
        },
    }


def aggregate(
    scenarios: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rule_names = next(
        iter(scenarios.values())
    )["rule_metrics"].keys()
    metric_names = next(
        iter(next(iter(scenarios.values()))["rule_metrics"].values())
    ).keys()
    result = {}
    for rule_name in rule_names:
        result[rule_name] = {}
        for metric_name in metric_names:
            values = [
                scenario["rule_metrics"][rule_name][metric_name]
                for scenario in scenarios.values()
            ]
            result[rule_name][metric_name] = {
                "mean": float(np.mean(values)),
                "worst": (
                    float(np.max(values))
                    if metric_name == "benign_fpr"
                    else float(np.min(values))
                ),
            }
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result_dir = args.result_dir.resolve()
    scenarios = {
        family: diagnose_scores(
            result_dir / f"{family.lower()}_scores.npz"
        )
        for family in ("DDoS", "DoS", "Mirai")
    }
    report = {
        "schema_version": "strict_v4_semantic_alert_diagnostic_v1",
        "state": "posthoc_read_only_diagnostic",
        "decision_contract": {
            "predicted_non_benign_class": "known_prediction != Benign",
            "rejected_as_unknown": "open_set_rejection == True",
            "categorical_semantic_union": (
                "predicted_non_benign_class OR rejected_as_unknown"
            ),
            "full_semantic_union": (
                "current_operational_alert OR "
                "predicted_non_benign_class OR rejected_as_unknown"
            ),
            "true_unknown_labels_used_to_fit_rule_or_threshold": False,
            "true_labels_used_for_posthoc_scoring_only": True,
        },
        "scenarios": scenarios,
        "aggregate": aggregate(scenarios),
    }
    rendered = json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite diagnostic: {output}")
    output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
