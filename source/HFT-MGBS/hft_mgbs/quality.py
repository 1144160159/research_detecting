"""Quality-protocol helpers that do not depend on a specific classifier."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, Iterable, Mapping, Sequence, Tuple


QUALITY_RESULT_NAME = re.compile(r"^(normal|fallback)_repeat(\d+)\.json$")


def expected_calibration_error(
    labels: Sequence[int], probabilities: Sequence[float], bins: int = 10
) -> float:
    if len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must have equal length")
    if bins <= 0:
        raise ValueError("bins must be positive")
    if not labels:
        return 0.0
    total = len(labels)
    error = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            position
            for position, probability in enumerate(probabilities)
            if lower <= probability < upper
            or (index == bins - 1 and probability == 1.0)
        ]
        if not members:
            continue
        confidence = sum(probabilities[position] for position in members) / len(members)
        accuracy = sum(labels[position] for position in members) / len(members)
        error += len(members) / total * abs(accuracy - confidence)
    return error


def binary_prediction_metrics(labels, probabilities, threshold):
    """Recompute all binary metrics from addressable label/probability evidence."""

    if len(labels) != len(probabilities) or not labels:
        raise ValueError("labels/probabilities must align and be non-empty")
    if any(type(value) is not int or value not in (0, 1) for value in labels):
        raise ValueError("labels must be binary integers")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0.0 <= float(value) <= 1.0
        for value in probabilities
    ):
        raise ValueError("probabilities must be in [0, 1]")
    clean_probabilities = [float(value) for value in probabilities]
    sentinel = max(clean_probabilities) + 1e-12
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or float(threshold) < 0.0
        or (
            float(threshold) > 1.0
            and float(threshold) != sentinel
        )
    ):
        raise ValueError("threshold is neither a probability nor the exact all-negative sentinel")
    predicted = [int(value >= float(threshold)) for value in clean_probabilities]
    tp = sum(label == 1 and guess == 1 for label, guess in zip(labels, predicted))
    tn = sum(label == 0 and guess == 0 for label, guess in zip(labels, predicted))
    fp = sum(label == 0 and guess == 1 for label, guess in zip(labels, predicted))
    fn = sum(label == 1 and guess == 0 for label, guess in zip(labels, predicted))
    attack_total = tp + fn
    benign_total = tn + fp
    if attack_total == 0 or benign_total == 0:
        raise ValueError("both classes are required")
    attack_recall = tp / attack_total
    benign_recall = tn / benign_total
    attack_denominator = 2 * tp + fp + fn
    benign_denominator = 2 * tn + fp + fn
    attack_f1 = 0.0 if attack_denominator == 0 else 2.0 * tp / attack_denominator
    benign_f1 = 0.0 if benign_denominator == 0 else 2.0 * tn / benign_denominator

    ranked = sorted(zip(clean_probabilities, labels), key=lambda item: item[0])
    positive_rank_sum = 0.0
    index = 0
    while index < len(ranked):
        stop = index + 1
        while stop < len(ranked) and ranked[stop][0] == ranked[index][0]:
            stop += 1
        average_rank = ((index + 1) + stop) / 2.0
        positive_rank_sum += average_rank * sum(item[1] for item in ranked[index:stop])
        index = stop
    auroc = (
        positive_rank_sum - attack_total * (attack_total + 1) / 2.0
    ) / (attack_total * benign_total)

    descending = sorted(
        zip(clean_probabilities, labels), key=lambda item: item[0], reverse=True
    )
    true_positive = false_positive = previous_true_positive = 0
    auprc = 0.0
    index = 0
    while index < len(descending):
        stop = index + 1
        while stop < len(descending) and descending[stop][0] == descending[index][0]:
            stop += 1
        positives = sum(item[1] for item in descending[index:stop])
        true_positive += positives
        false_positive += stop - index - positives
        precision = true_positive / (true_positive + false_positive)
        auprc += ((true_positive - previous_true_positive) / attack_total) * precision
        previous_true_positive = true_positive
        index = stop
    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "macro_f1": (attack_f1 + benign_f1) / 2.0,
        "balanced_accuracy": (attack_recall + benign_recall) / 2.0,
        "auroc": auroc,
        "auprc": auprc,
        "benign_recall": benign_recall,
        "attack_recall": attack_recall,
        "ece": expected_calibration_error(labels, clean_probabilities),
        "predicted_attack_ratio": (tp + fp) / len(labels),
    }


def select_macro_f1_threshold(labels, probabilities, min_attack_recall=0.0):
    """Select in O(N log N), retaining the exact all-negative sentinel."""

    if not 0.0 <= float(min_attack_recall) <= 1.0:
        raise ValueError("minimum attack recall must be in [0, 1]")
    if len(labels) != len(probabilities) or not labels:
        raise ValueError("labels/probabilities must align and be non-empty")
    if any(type(value) is not int or value not in (0, 1) for value in labels):
        raise ValueError("labels must be binary integers")
    clean_probabilities = [float(value) for value in probabilities]
    if any(not 0.0 <= value <= 1.0 for value in clean_probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    attack_total = sum(labels)
    benign_total = len(labels) - attack_total
    if attack_total == 0 or benign_total == 0:
        raise ValueError("both classes are required")
    ranked = sorted(
        zip(clean_probabilities, labels), key=lambda item: item[0], reverse=True
    )
    candidates = []
    tp = fp = 0
    fn = attack_total
    tn = benign_total

    def append_candidate(threshold):
        attack_recall = tp / attack_total
        benign_recall = tn / benign_total
        attack_denominator = 2 * tp + fp + fn
        benign_denominator = 2 * tn + fp + fn
        attack_f1 = 0.0 if attack_denominator == 0 else 2.0 * tp / attack_denominator
        benign_f1 = 0.0 if benign_denominator == 0 else 2.0 * tn / benign_denominator
        if attack_recall >= min_attack_recall:
            candidates.append(
                {
                    "threshold": threshold,
                    "macro_f1": (attack_f1 + benign_f1) / 2.0,
                    "balanced_accuracy": (attack_recall + benign_recall) / 2.0,
                    "attack_recall": attack_recall,
                    "benign_recall": benign_recall,
                    "predicted_attack_ratio": (tp + fp) / len(labels),
                }
            )

    append_candidate(max(clean_probabilities) + 1e-12)
    index = 0
    while index < len(ranked):
        threshold = ranked[index][0]
        stop = index + 1
        while stop < len(ranked) and ranked[stop][0] == threshold:
            stop += 1
        positives = sum(item[1] for item in ranked[index:stop])
        negatives = stop - index - positives
        tp += positives
        fn -= positives
        fp += negatives
        tn -= negatives
        append_candidate(threshold)
        index = stop
    if not candidates:
        raise ValueError("no threshold satisfies the minimum attack recall")
    selected = max(
        candidates,
        key=lambda item: (
            item["macro_f1"],
            item["balanced_accuracy"],
            -abs(item["threshold"] - 0.5),
            -item["threshold"],
        ),
    )
    selected["minimum_attack_recall_constraint"] = min_attack_recall
    replayed = binary_prediction_metrics(
        labels, clean_probabilities, selected["threshold"]
    )
    replayed["threshold"] = selected["threshold"]
    replayed["minimum_attack_recall_constraint"] = min_attack_recall
    return replayed


def minimum_metric(records: Iterable[dict], name: str):
    values = [record[name] for record in records if record.get(name) is not None]
    return None if not values else min(values)


def summarize_quality_runs(
    named_runs: Iterable[Tuple[str, Mapping[str, object]]],
    minimum_repeats: int = 3,
    max_budget_overrun_count: int = 0,
    min_key_flow_coverage: float = 0.99,
) -> Dict[str, object]:
    if minimum_repeats <= 0:
        raise ValueError("minimum_repeats must be positive")
    grouped = defaultdict(list)
    rejected = []
    for name, payload in named_runs:
        match = QUALITY_RESULT_NAME.match(name)
        if match is None:
            rejected.append(name)
            continue
        mode, repeat = match.groups()
        grouped[mode].append((int(repeat), payload))
    candidates = []
    for mode, runs in sorted(grouped.items()):
        runs.sort(key=lambda item: item[0])
        payloads = [item[1] for item in runs]
        safety_ratios = {
            float(
                payload["candidate"].get(
                    "execution_budget_safety_ratio", 0.75
                )
            )
            for payload in payloads
        }
        metrics = [item["quality"]["conservative"] for item in payloads]
        audits = [
            item.get("candidate_constraint_audit") for item in payloads
        ]
        missing_audit = any(audit is None for audit in audits)
        valid_audits = [audit for audit in audits if audit is not None]
        budget_overrun_count_max = (
            None
            if not valid_audits
            else max(
                int(audit["budget_overrun_count"])
                for audit in valid_audits
            )
        )
        key_flow_coverage_min = (
            None
            if not valid_audits
            else min(
                float(audit["key_flow_coverage_min"])
                for audit in valid_audits
            )
        )
        hard_constraint_violations = []
        if missing_audit:
            hard_constraint_violations.append(
                "missing_candidate_constraint_audit"
            )
        if (
            budget_overrun_count_max is not None
            and budget_overrun_count_max > max_budget_overrun_count
        ):
            hard_constraint_violations.append("budget_overrun")
        if (
            key_flow_coverage_min is not None
            and key_flow_coverage_min < min_key_flow_coverage
        ):
            hard_constraint_violations.append("key_flow_coverage")
        if len(safety_ratios) != 1:
            hard_constraint_violations.append(
                "execution_budget_safety_ratio_inconsistent"
            )
        candidate = {
            "mode": mode,
            "repeat_ids": [item[0] for item in runs],
            "repeat_count": len(runs),
            "repeat_gate_passed": len(runs) >= minimum_repeats,
            "budget_overrun_count_max": budget_overrun_count_max,
            "key_flow_coverage_min": key_flow_coverage_min,
            "hard_constraint_violations": hard_constraint_violations,
            "hard_constraints_passed": not hard_constraint_violations,
            "batch_size": payloads[0]["candidate"]["batch_size"],
            "budget_us": payloads[0]["candidate"]["budget_us"],
            "execution_budget_safety_ratio": (
                next(iter(safety_ratios))
                if len(safety_ratios) == 1
                else None
            ),
            "flow_sample_count_min": min(
                item["quality"]["flow_sample_count"] for item in payloads
            ),
            "feature_count_min": min(
                item["quality"]["feature_count"] for item in payloads
            ),
            "macro_f1_min": min(item["macro_f1_min"] for item in metrics),
            "balanced_accuracy_min": min(
                item["balanced_accuracy_min"] for item in metrics
            ),
            "capture_balanced_accuracy_min": min(
                item["capture_balanced_accuracy_min"] for item in metrics
            ),
            "auroc_min": min(item["auroc_min"] for item in metrics),
            "auprc_min": min(item["auprc_min"] for item in metrics),
            "ece_max": max(item["ece_max"] for item in metrics),
            "final_quality_eligible": False,
            "missing_final_evidence": sorted(
                {
                    evidence
                    for payload in payloads
                    for evidence in payload.get("missing_final_evidence", [])
                }
            ),
        }
        candidates.append(candidate)
    return {
        "schema_version": 1,
        "scope": "offline_grouped_quality_summary",
        "aggregation_policy": "worst_case_across_full_extraction_repeats",
        "minimum_repeats": minimum_repeats,
        "candidate_count": len(candidates),
        "feasible_candidate_count": sum(
            candidate["repeat_gate_passed"]
            and candidate["hard_constraints_passed"]
            for candidate in candidates
        ),
        "rejected_files": sorted(rejected),
        "candidates": candidates,
        "final_quality_eligible": False,
    }
