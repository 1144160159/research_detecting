from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
from scipy.special import logsumexp
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    roc_auc_score,
)

from caeos.metrics import fpr_at_95_tpr, open_set_classification_rate
from caeos.neural_open_set import OpenMaxCalibrator, RelativeMahalanobis
from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


SCENARIOS = ("DDoS", "DoS", "Mirai")
METRICS = (
    "known_accuracy",
    "known_macro_f1",
    "known_balanced_accuracy",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "unknown_f1",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)


def known_only_threshold(
    validation_risk: np.ndarray, known_acceptance: float = 0.95
) -> float:
    risk = np.asarray(validation_risk, dtype=np.float64)
    if risk.ndim != 1 or len(risk) == 0 or not np.isfinite(risk).all():
        raise ValueError("validation risk must be a finite non-empty vector")
    if not 0.0 < known_acceptance < 1.0:
        raise ValueError("known acceptance must be strictly between zero and one")
    return float(np.quantile(risk, known_acceptance, method="higher"))


def evaluate_risk(
    *,
    validation_risk: np.ndarray,
    test_risk: np.ndarray,
    test_prediction: np.ndarray,
    test_labels: np.ndarray,
    is_unknown: np.ndarray,
) -> dict[str, float]:
    risk = np.asarray(test_risk, dtype=np.float64)
    prediction = np.asarray(test_prediction, dtype=np.int64)
    labels = np.asarray(test_labels, dtype=np.int64)
    unknown = np.asarray(is_unknown, dtype=bool)
    if not (
        risk.shape == prediction.shape == labels.shape == unknown.shape
    ):
        raise ValueError("test baseline arrays have incompatible shapes")
    if not np.isfinite(risk).all():
        raise ValueError("test baseline risk contains non-finite values")
    known = ~unknown
    if not known.any() or not unknown.any():
        raise ValueError("test split must contain known and unknown samples")
    threshold = known_only_threshold(validation_risk)
    rejection = risk > threshold
    target = unknown.astype(np.int64)
    return {
        "known_accuracy": float(
            accuracy_score(labels[known], prediction[known])
        ),
        "known_macro_f1": float(
            f1_score(labels[known], prediction[known], average="macro")
        ),
        "known_balanced_accuracy": float(
            balanced_accuracy_score(labels[known], prediction[known])
        ),
        "unknown_auroc": float(roc_auc_score(target, risk)),
        "unknown_aupr": float(average_precision_score(target, risk)),
        "unknown_fpr95": float(fpr_at_95_tpr(target, risk)),
        "unknown_f1": float(f1_score(target, rejection.astype(np.int64))),
        "oscr": float(
            open_set_classification_rate(
                labels, prediction, unknown, risk
            )
        ),
        "known_acceptance_rate": float((~rejection[known]).mean()),
        "unknown_rejection_rate": float(rejection[unknown].mean()),
        "risk_threshold": threshold,
    }


def baseline_records(
    arrays: dict[str, np.ndarray],
) -> dict[str, dict[str, float]]:
    train_embedding = arrays["baseline_train_embedding"]
    train_logits = arrays["baseline_train_log_evidence"]
    train_labels = arrays["baseline_train_label"]
    validation_embedding = arrays["baseline_validation_embedding"]
    validation_logits = arrays["baseline_validation_log_evidence"]
    validation_belief = arrays["baseline_validation_belief"]
    validation_labels = arrays["baseline_validation_label"]
    test_embedding = arrays["baseline_test_embedding"]
    test_logits = arrays["baseline_test_log_evidence"]
    test_belief = arrays["baseline_test_belief"]
    test_labels = arrays["baseline_test_label"]
    is_unknown = arrays["baseline_test_is_unknown"]
    if np.any(validation_labels < 0):
        raise ValueError("validation split is not known-only")

    belief_prediction = np.asarray(test_belief).argmax(axis=1)
    risks: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {
        "MSP": (
            1.0 - np.asarray(validation_belief).max(axis=1),
            1.0 - np.asarray(test_belief).max(axis=1),
            belief_prediction,
        ),
        "Energy": (
            -logsumexp(np.asarray(validation_logits), axis=1),
            -logsumexp(np.asarray(test_logits), axis=1),
            belief_prediction,
        ),
    }

    openmax = OpenMaxCalibrator(tail_size=20, alpha=10)
    openmax.fit(train_logits, train_labels)
    validation_openmax, _ = openmax.predict(validation_logits)
    test_openmax, openmax_prediction = openmax.predict(test_logits)
    risks["OpenMax"] = (
        validation_openmax,
        test_openmax,
        openmax_prediction,
    )

    relative_mahalanobis = RelativeMahalanobis()
    relative_mahalanobis.fit(train_embedding, train_labels)
    risks["Mahalanobis++"] = (
        relative_mahalanobis.score(validation_embedding),
        relative_mahalanobis.score(test_embedding),
        belief_prediction,
    )

    return {
        name: evaluate_risk(
            validation_risk=validation_risk,
            test_risk=test_risk,
            test_prediction=prediction,
            test_labels=test_labels,
            is_unknown=is_unknown,
        )
        for name, (validation_risk, test_risk, prediction) in risks.items()
    }


def aggregate(
    per_scenario: dict[str, dict[str, float]]
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for metric in METRICS:
        values = np.asarray(
            [record[metric] for record in per_scenario.values()],
            dtype=np.float64,
        )
        result[metric] = {
            "mean": float(values.mean()),
            "worst": float(
                values.max() if metric == "unknown_fpr95" else values.min()
            ),
        }
    return result


def load_arrays(path: Path) -> dict[str, np.ndarray]:
    required = {
        f"baseline_{split}_{name}"
        for split in ("train", "validation", "test")
        for name in ("embedding", "log_evidence", "belief", "label")
    } | {"baseline_test_is_unknown"}
    with np.load(path, allow_pickle=False) as payload:
        missing = sorted(required - set(payload.files))
        if missing:
            raise ValueError(f"baseline score arrays are missing: {missing}")
        return {name: np.asarray(payload[name]) for name in required}


def build_evaluation(
    protocol_path: Path, completion_path: Path
) -> dict[str, Any]:
    protocol = load_canonical(protocol_path.resolve(), "protocol")
    completion = load_canonical(completion_path.resolve(), "completion")
    if (
        completion.get("state") != "completed"
        or completion.get("task_count") != len(SCENARIOS)
        or completion.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("PCAP development run is incomplete or mismatched")

    run_root = Path(protocol["paths"]["run_root"])
    by_method: dict[str, dict[str, dict[str, float]]] = {}
    self_records: dict[str, dict[str, float]] = {}
    artifacts: dict[str, dict[str, str]] = {}
    for scenario in SCENARIOS:
        task_root = run_root / scenario.lower()
        metrics_path = task_root / "metrics.json"
        scores_path = task_root / "scores.npz"
        if (
            file_hash(metrics_path)
            != completion["task_metric_sha256"][scenario]
        ):
            raise ValueError(f"{scenario} task metrics differ from completion")
        metrics = load_canonical(metrics_path, f"{scenario} task metrics")
        records = baseline_records(load_arrays(scores_path))
        for method, record in records.items():
            by_method.setdefault(method, {})[scenario] = record
        self_records[scenario] = {
            metric: float(metrics["three_layer_metrics"][metric])
            for metric in METRICS
        }
        artifacts[scenario] = {
            "metrics_sha256": file_hash(metrics_path),
            "scores_sha256": file_hash(scores_path),
            "model_sha256": file_hash(task_root / "model.pt"),
        }

    by_method["CAEOS-EMTD"] = self_records
    summaries = {
        method: aggregate(records) for method, records in by_method.items()
    }
    baseline_names = tuple(
        name for name in summaries if name != "CAEOS-EMTD"
    )
    best_baseline = max(
        baseline_names, key=lambda name: summaries[name]["oscr"]["mean"]
    )
    self_summary = summaries["CAEOS-EMTD"]
    baseline_summary = summaries[best_baseline]
    comparison = {
        "reference_baseline": best_baseline,
        "known_macro_f1_delta": (
            self_summary["known_macro_f1"]["mean"]
            - baseline_summary["known_macro_f1"]["mean"]
        ),
        "unknown_auroc_delta": (
            self_summary["unknown_auroc"]["mean"]
            - baseline_summary["unknown_auroc"]["mean"]
        ),
        "unknown_aupr_delta": (
            self_summary["unknown_aupr"]["mean"]
            - baseline_summary["unknown_aupr"]["mean"]
        ),
        "unknown_fpr95_reduction": (
            baseline_summary["unknown_fpr95"]["mean"]
            - self_summary["unknown_fpr95"]["mean"]
        ),
        "oscr_delta": (
            self_summary["oscr"]["mean"]
            - baseline_summary["oscr"]["mean"]
        ),
    }
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_classical_baseline_evaluation_v1"
        ),
        "state": "complete_development_baseline_evaluation",
        "protocol": {
            "path": str(protocol_path.resolve()),
            "file_sha256": file_hash(protocol_path.resolve()),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "completion": {
            "path": str(completion_path.resolve()),
            "file_sha256": file_hash(completion_path.resolve()),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "implementation_sha256": {
            Path(__file__).name: file_hash(Path(__file__).resolve()),
            "caeos/metrics.py": file_hash(
                Path(__file__).resolve().parent / "caeos" / "metrics.py"
            ),
            "caeos/neural_open_set.py": file_hash(
                Path(__file__).resolve().parent
                / "caeos"
                / "neural_open_set.py"
            ),
        },
        "methods": {
            "MSP": "one minus maximum fused evidential belief",
            "Energy": "negative log-sum-exp of fused log evidence",
            "OpenMax": "Weibull recalibration fitted on known training logits",
            "Mahalanobis++": (
                "relative class-conditional Mahalanobis risk fitted on "
                "known training embeddings"
            ),
            "CAEOS-EMTD": "frozen conflict-aware composite risk",
        },
        "main_metrics": [
            "known_macro_f1",
            "known_balanced_accuracy",
            "unknown_auroc",
            "unknown_aupr",
            "unknown_fpr95",
            "oscr",
        ],
        "per_scenario": by_method,
        "summary": summaries,
        "self_vs_best_oscr_baseline": comparison,
        "artifacts": artifacts,
        "claim_boundary": {
            "same_native_three_modal_backbone": True,
            "same_capture_grouped_family_held_out_split": True,
            "baseline_fit_uses_known_training_only": True,
            "thresholds_use_known_only_validation": True,
            "unknown_test_used_for_evaluation_only": True,
            "development_seed_only": True,
            "confirmation_claim_permitted": False,
            "sota_claim_permitted": False,
            "vim_excluded_reason": (
                "the conflict-fused evidence has no single linear classifier "
                "mapping from the fused embedding, violating ViM assumptions"
            ),
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_evaluation(args.protocol, args.completion)
    atomic_json(args.output.resolve(), report)
    print(
        {
            "output": str(args.output.resolve()),
            "manifest_sha256": report["manifest_sha256"],
            "self_vs_best_oscr_baseline": report[
                "self_vs_best_oscr_baseline"
            ],
        }
    )


if __name__ == "__main__":
    main()
