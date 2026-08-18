from __future__ import annotations

from typing import Any, Sequence

import numpy as np


SCHEMA_VERSION = "strict_v4_open_set_metric_contract_v2"
TRAPEZOID = getattr(np, "trapezoid", np.trapz)


def _one_dimensional(name: str, values: np.ndarray, size: int | None = None) -> np.ndarray:
    array = np.asarray(values).reshape(-1)
    if size is not None and array.size != size:
        raise ValueError(f"{name} length {array.size} does not match {size}")
    if array.size == 0:
        raise ValueError(f"{name} must be nonempty")
    return array


def _binary_counts(
    target: np.ndarray,
    prediction: np.ndarray,
) -> tuple[int, int, int]:
    positive = np.asarray(target, dtype=bool)
    predicted_positive = np.asarray(prediction, dtype=bool)
    true_positive = int((positive & predicted_positive).sum())
    false_positive = int((~positive & predicted_positive).sum())
    false_negative = int((positive & ~predicted_positive).sum())
    return true_positive, false_positive, false_negative


def _binary_f1(target: np.ndarray, prediction: np.ndarray) -> float:
    true_positive, false_positive, false_negative = _binary_counts(
        target,
        prediction,
    )
    denominator = 2 * true_positive + false_positive + false_negative
    return float(2 * true_positive / denominator) if denominator else 0.0


def _binary_ranking_points(
    target: np.ndarray,
    score: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    positive = np.asarray(target, dtype=bool)
    values = np.asarray(score, dtype=np.float64)
    positive_count = int(positive.sum())
    negative_count = int((~positive).sum())
    if positive_count == 0 or negative_count == 0:
        raise ValueError("ranking metrics require both target classes")
    order = np.argsort(-values, kind="mergesort")
    ordered_score = values[order]
    ordered_positive = positive[order]
    true_positive = 0
    false_positive = 0
    true_positive_rates = [0.0]
    false_positive_rates = [0.0]
    start = 0
    while start < order.size:
        end = start + 1
        while (
            end < order.size
            and ordered_score[end] == ordered_score[start]
        ):
            end += 1
        true_positive += int(ordered_positive[start:end].sum())
        false_positive += int((~ordered_positive[start:end]).sum())
        true_positive_rates.append(true_positive / positive_count)
        false_positive_rates.append(false_positive / negative_count)
        start = end
    return (
        np.asarray(false_positive_rates, dtype=np.float64),
        np.asarray(true_positive_rates, dtype=np.float64),
    )


def _binary_auroc(target: np.ndarray, score: np.ndarray) -> float:
    false_positive_rate, true_positive_rate = _binary_ranking_points(
        target,
        score,
    )
    return float(TRAPEZOID(true_positive_rate, false_positive_rate))


def _average_precision(target: np.ndarray, score: np.ndarray) -> float:
    positive = np.asarray(target, dtype=bool)
    values = np.asarray(score, dtype=np.float64)
    positive_count = int(positive.sum())
    negative_count = int((~positive).sum())
    if positive_count == 0 or negative_count == 0:
        raise ValueError("average precision requires both target classes")
    order = np.argsort(-values, kind="mergesort")
    ordered_score = values[order]
    ordered_positive = positive[order]
    cumulative_positive = 0
    cumulative_count = 0
    previous_recall = 0.0
    average_precision = 0.0
    start = 0
    while start < order.size:
        end = start + 1
        while (
            end < order.size
            and ordered_score[end] == ordered_score[start]
        ):
            end += 1
        cumulative_positive += int(ordered_positive[start:end].sum())
        cumulative_count += end - start
        recall = cumulative_positive / positive_count
        precision = cumulative_positive / cumulative_count
        average_precision += (recall - previous_recall) * precision
        previous_recall = recall
        start = end
    return float(average_precision)


def _per_class_recall_and_f1(
    labels: np.ndarray,
    prediction: np.ndarray,
    class_indices: Sequence[int],
) -> tuple[np.ndarray, np.ndarray]:
    recalls = []
    f1_values = []
    for class_index in class_indices:
        target = labels == class_index
        predicted = prediction == class_index
        true_positive = int((target & predicted).sum())
        false_positive = int((~target & predicted).sum())
        false_negative = int((target & ~predicted).sum())
        recalls.append(
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        denominator = 2 * true_positive + false_positive + false_negative
        f1_values.append(
            2 * true_positive / denominator if denominator else 0.0
        )
    return (
        np.asarray(recalls, dtype=np.float64),
        np.asarray(f1_values, dtype=np.float64),
    )


def fpr_known_at_95_unknown_tpr(
    is_unknown: np.ndarray,
    unknown_risk: np.ndarray,
) -> float:
    """Known-sample rejection rate at at least 95% unknown recall."""

    target = _one_dimensional("is_unknown", is_unknown).astype(bool)
    risk = _one_dimensional("unknown_risk", unknown_risk, target.size).astype(
        np.float64
    )
    if np.unique(target).size != 2:
        raise ValueError("FPR95 requires both known and unknown test samples")
    false_positive_rate, true_positive_rate = _binary_ranking_points(
        target,
        risk,
    )
    eligible = np.flatnonzero(true_positive_rate >= 0.95)
    return float(false_positive_rate[eligible[0]]) if eligible.size else 1.0


def exact_oscr_area(
    labels: np.ndarray,
    known_prediction: np.ndarray,
    is_unknown: np.ndarray,
    unknown_risk: np.ndarray,
) -> float:
    """Exact area under CCR versus unknown-as-known FPR.

    Lower risk means that a sample is accepted as one of the known classes.
    Tied risk values enter the curve together.
    """

    labels_array = _one_dimensional("labels", labels)
    prediction = _one_dimensional(
        "known_prediction", known_prediction, labels_array.size
    )
    unknown = _one_dimensional(
        "is_unknown", is_unknown, labels_array.size
    ).astype(bool)
    risk = _one_dimensional(
        "unknown_risk", unknown_risk, labels_array.size
    ).astype(np.float64)
    known = ~unknown
    if not known.any() or not unknown.any():
        raise ValueError("OSCR requires both known and unknown test samples")
    if not np.isfinite(risk).all():
        raise ValueError("unknown_risk contains non-finite values")

    correct_known = known & (prediction == labels_array)
    order = np.argsort(risk, kind="mergesort")
    ordered_risk = risk[order]
    ordered_unknown = unknown[order]
    ordered_correct = correct_known[order]

    false_positive_rate = [0.0]
    correct_classification_rate = [0.0]
    accepted_unknown = 0
    accepted_correct_known = 0
    start = 0
    while start < order.size:
        end = start + 1
        while (
            end < order.size
            and ordered_risk[end] == ordered_risk[start]
        ):
            end += 1
        accepted_unknown += int(ordered_unknown[start:end].sum())
        accepted_correct_known += int(ordered_correct[start:end].sum())
        false_positive_rate.append(accepted_unknown / int(unknown.sum()))
        correct_classification_rate.append(
            accepted_correct_known / int(known.sum())
        )
        start = end

    return float(
        TRAPEZOID(
            np.asarray(correct_classification_rate, dtype=np.float64),
            np.asarray(false_positive_rate, dtype=np.float64),
        )
    )


def known_probability_calibration(
    probabilities: np.ndarray,
    labels: np.ndarray,
    is_unknown: np.ndarray,
    *,
    bins: int = 15,
) -> dict[str, Any]:
    probability = np.asarray(probabilities, dtype=np.float64)
    labels_array = _one_dimensional("labels", labels)
    unknown = _one_dimensional(
        "is_unknown", is_unknown, labels_array.size
    ).astype(bool)
    if probability.ndim != 2 or probability.shape[0] != labels_array.size:
        raise ValueError("probabilities must have shape [samples, known_classes]")
    if bins <= 0:
        raise ValueError("bins must be positive")
    if not np.isfinite(probability).all():
        raise ValueError("probabilities contain non-finite values")
    if np.any(probability < 0.0):
        raise ValueError("probabilities contain negative values")
    row_sum = probability.sum(axis=1)
    if not np.allclose(row_sum, 1.0, atol=1e-6, rtol=0.0):
        raise ValueError("probability rows must sum to one")

    known = ~unknown
    known_probability = probability[known]
    known_labels = labels_array[known].astype(np.int64)
    if (
        np.any(known_labels < 0)
        or np.any(known_labels >= known_probability.shape[1])
    ):
        raise ValueError("known labels are outside the probability columns")

    confidence = known_probability.max(axis=1)
    prediction = known_probability.argmax(axis=1)
    correctness = prediction == known_labels
    boundaries = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for index, (lower, upper) in enumerate(
        zip(boundaries[:-1], boundaries[1:])
    ):
        selected = (confidence >= lower) & (
            confidence <= upper if index == bins - 1 else confidence < upper
        )
        if selected.any():
            ece += float(selected.mean()) * abs(
                float(correctness[selected].mean())
                - float(confidence[selected].mean())
            )

    one_hot = np.eye(known_probability.shape[1], dtype=np.float64)[
        known_labels
    ]
    clipped_true_probability = np.clip(
        known_probability[np.arange(known_labels.size), known_labels],
        1e-12,
        1.0,
    )
    return {
        "available": True,
        "scope": "known_test_only",
        "probability_space": "known_classes_only",
        "ece_bins": int(bins),
        "ece": float(ece),
        "brier_score": float(
            np.mean(np.sum((known_probability - one_hot) ** 2, axis=1))
        ),
        "negative_log_likelihood": float(
            -np.mean(np.log(clipped_true_probability))
        ),
    }


def evaluate_open_set_metric_contract(
    *,
    labels: np.ndarray,
    known_prediction: np.ndarray,
    is_unknown: np.ndarray,
    unknown_risk: np.ndarray,
    rejected_as_unknown: np.ndarray,
    class_names: Sequence[str] | None = None,
    known_class_probabilities: np.ndarray | None = None,
) -> dict[str, Any]:
    labels_array = _one_dimensional("labels", labels)
    prediction = _one_dimensional(
        "known_prediction", known_prediction, labels_array.size
    ).astype(np.int64)
    unknown = _one_dimensional(
        "is_unknown", is_unknown, labels_array.size
    ).astype(bool)
    risk = _one_dimensional(
        "unknown_risk", unknown_risk, labels_array.size
    ).astype(np.float64)
    rejected = _one_dimensional(
        "rejected_as_unknown", rejected_as_unknown, labels_array.size
    ).astype(bool)
    known = ~unknown
    if not known.any() or not unknown.any():
        raise ValueError("metric contract requires known and unknown samples")
    if not np.isfinite(risk).all():
        raise ValueError("unknown_risk contains non-finite values")

    known_labels = labels_array[known].astype(np.int64)
    known_prediction_values = prediction[known]
    class_indices = sorted(int(value) for value in np.unique(known_labels))
    if class_names is not None:
        names = [str(value) for value in class_names]
        if class_indices and max(class_indices) >= len(names):
            raise ValueError("class_names do not cover the known labels")
        class_label = {index: names[index] for index in class_indices}
    else:
        class_label = {index: str(index) for index in class_indices}

    per_class_recall, per_class_f1 = _per_class_recall_and_f1(
        known_labels,
        known_prediction_values,
        class_indices,
    )
    unknown_target = unknown.astype(np.int64)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "positive_class_convention": {
            "unknown_detection": "unknown_is_positive",
            "unknown_risk": "higher_means_more_unknown",
            "fpr95": (
                "known_sample_rejection_rate_at_first_test_curve_point_"
                "with_unknown_tpr_at_least_0.95"
            ),
        },
        "closed_set_known": {
            "population": "benign_plus_known_attack_families",
            "known_macro_f1": float(per_class_f1.mean()),
            "known_balanced_accuracy": float(per_class_recall.mean()),
            "per_class_recall": {
                class_label[index]: float(value)
                for index, value in zip(class_indices, per_class_recall)
            },
        },
        "unknown_detection": {
            "unknown_auroc_out": _binary_auroc(unknown_target, risk),
            "unknown_aupr_out": _average_precision(
                unknown_target,
                risk,
            ),
            "fpr_known_at_95_unknown_tpr": (
                fpr_known_at_95_unknown_tpr(unknown, risk)
            ),
            "unknown_f1_at_frozen_threshold": _binary_f1(
                unknown_target,
                rejected,
            ),
        },
        "joint_open_set": {
            "oscr_exact_v2": exact_oscr_area(
                labels_array,
                prediction,
                unknown,
                risk,
            ),
            "known_acceptance_rate_at_frozen_threshold": float(
                (~rejected[known]).mean()
            ),
            "unknown_rejection_rate_at_frozen_threshold": float(
                rejected[unknown].mean()
            ),
        },
    }
    report["unknown_detection"]["unknown_auroc"] = report[
        "unknown_detection"
    ]["unknown_auroc_out"]
    report["compatibility_aliases"] = {
        "unknown_detection.unknown_auroc": (
            report["unknown_detection"]["unknown_auroc_out"]
        ),
        "policy": "read_only_legacy_alias_do_not_use_in_new_reports",
    }
    if known_class_probabilities is None:
        report["calibration"] = {
            "available": False,
            "scope": "known_test_only",
            "reason": "known_class_probability_matrix_not_recorded",
        }
    else:
        report["calibration"] = known_probability_calibration(
            known_class_probabilities,
            labels_array,
            unknown,
        )
    return report
