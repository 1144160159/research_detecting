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


def minimum_metric(records: Iterable[dict], name: str):
    values = [record[name] for record in records if record.get(name) is not None]
    return None if not values else min(values)


def summarize_quality_runs(
    named_runs: Iterable[Tuple[str, Mapping[str, object]]],
    minimum_repeats: int = 3,
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
        metrics = [item["quality"]["conservative"] for item in payloads]
        candidate = {
            "mode": mode,
            "repeat_ids": [item[0] for item in runs],
            "repeat_count": len(runs),
            "repeat_gate_passed": len(runs) >= minimum_repeats,
            "batch_size": payloads[0]["candidate"]["batch_size"],
            "budget_us": payloads[0]["candidate"]["budget_us"],
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
        "rejected_files": sorted(rejected),
        "candidates": candidates,
        "final_quality_eligible": False,
    }
