from __future__ import annotations

from typing import Dict

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    roc_auc_score,
    roc_curve,
)

from .open_set import OpenSetCalibrator


def expected_calibration_error(probabilities: np.ndarray, labels: np.ndarray, bins: int = 15) -> float:
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    correctness = (prediction == labels).astype(np.float64)
    error = 0.0
    boundaries = np.linspace(0.0, 1.0, bins + 1)
    for lower, upper in zip(boundaries[:-1], boundaries[1:]):
        selected = (confidence > lower) & (confidence <= upper)
        if selected.any():
            error += selected.mean() * abs(correctness[selected].mean() - confidence[selected].mean())
    return float(error)


def fpr_at_95_tpr(target: np.ndarray, score: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(target, score)
    selected = np.where(tpr >= 0.95)[0]
    return float(fpr[selected[0]]) if len(selected) else 1.0


def open_set_classification_rate(
    labels: np.ndarray,
    prediction: np.ndarray,
    is_unknown: np.ndarray,
    risk: np.ndarray,
) -> float:
    known = ~is_unknown
    correct = prediction[known] == labels[known]
    thresholds = np.unique(np.quantile(risk, np.linspace(0.0, 1.0, 300)))
    false_positive_rates = []
    correct_classification_rates = []
    for threshold in thresholds:
        false_positive_rates.append(float((risk[is_unknown] <= threshold).mean()))
        correct_classification_rates.append(
            float((correct & (risk[known] <= threshold)).sum() / max(1, known.sum()))
        )
    order = np.argsort(false_positive_rates)
    return float(
        np.trapz(
            np.asarray(correct_classification_rates)[order],
            np.asarray(false_positive_rates)[order],
        )
    )


def evaluate_open_set(
    output: Dict[str, torch.Tensor],
    labels: torch.Tensor,
    is_unknown: torch.Tensor,
    calibrator: OpenSetCalibrator,
) -> Dict[str, float]:
    result = calibrator.predict(output)
    risk = result["risk"].detach().cpu().numpy()
    known_prediction = result["known_prediction"].detach().cpu().numpy()
    unknown_prediction = result["is_unknown"].detach().cpu().numpy()
    labels_np = labels.cpu().numpy()
    is_unknown_np = is_unknown.cpu().numpy().astype(bool)
    known = ~is_unknown_np
    probabilities = output["fused_probability"].detach().cpu().numpy()
    raw_components = calibrator.raw_components(output)

    unknown_target = is_unknown_np.astype(np.int64)
    report = {
        "known_accuracy": float(accuracy_score(labels_np[known], known_prediction[known])),
        "known_macro_f1": float(
            f1_score(labels_np[known], known_prediction[known], average="macro")
        ),
        "unknown_auroc": float(roc_auc_score(unknown_target, risk)),
        "unknown_aupr": float(average_precision_score(unknown_target, risk)),
        "unknown_fpr95": fpr_at_95_tpr(unknown_target, risk),
        "unknown_f1": float(f1_score(unknown_target, unknown_prediction.astype(np.int64))),
        "oscr": open_set_classification_rate(
            labels_np, known_prediction, is_unknown_np, risk
        ),
        "ece": expected_calibration_error(probabilities[known], labels_np[known]),
        "risk_threshold": float(calibrator.risk_threshold),
        "known_acceptance_rate": float((~unknown_prediction[known]).mean()),
        "unknown_rejection_rate": float(unknown_prediction[is_unknown_np].mean()),
        "mean_known_risk": float(risk[known].mean()),
        "mean_unknown_risk": float(risk[is_unknown_np].mean()),
        "mean_known_conflict": float(output["global_conflict"][known].mean()),
        "mean_unknown_conflict": float(output["global_conflict"][is_unknown_np].mean()),
    }
    for name, values in raw_components.items():
        values_np = values.detach().cpu().numpy()
        report["%s_auroc" % name] = float(roc_auc_score(unknown_target, values_np))
        report["mean_known_%s" % name] = float(values_np[known].mean())
        report["mean_unknown_%s" % name] = float(values_np[is_unknown_np].mean())

    num_modalities = output["raw_conflict"].shape[1]
    raw_global_conflict = output["raw_conflict"].sum(dim=(1, 2)) / max(
        1, num_modalities * (num_modalities - 1)
    )
    raw_global_np = raw_global_conflict.detach().cpu().numpy()
    report["raw_conflict_auroc"] = float(
        roc_auc_score(unknown_target, raw_global_np)
    )
    report["mean_known_raw_conflict"] = float(raw_global_np[known].mean())
    report["mean_unknown_raw_conflict"] = float(
        raw_global_np[is_unknown_np].mean()
    )

    for modality_index in range(num_modalities):
        reliability = output["reliability"][:, modality_index].detach().cpu().numpy()
        discount = output["discount"][:, modality_index].detach().cpu().numpy()
        report["mean_known_reliability_m%d" % modality_index] = float(
            reliability[known].mean()
        )
        report["mean_unknown_reliability_m%d" % modality_index] = float(
            reliability[is_unknown_np].mean()
        )
        report["mean_known_discount_m%d" % modality_index] = float(
            discount[known].mean()
        )
        report["mean_unknown_discount_m%d" % modality_index] = float(
            discount[is_unknown_np].mean()
        )
    one_hot = F.one_hot(labels[known], num_classes=probabilities.shape[1]).numpy()
    report["brier_score"] = float(np.mean(np.sum((probabilities[known] - one_hot) ** 2, axis=1)))
    return report
