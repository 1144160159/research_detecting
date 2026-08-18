"""Fail-closed audit for the bounded offline algorithm search.

This module deliberately does not make a production deployment decision.  It
only checks whether the algorithm-only search record is sufficient to prove a
winner, recomputes the paired normal/fallback metrics, and derives strict and
material (epsilon) Pareto fronts.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Mapping, Optional, Sequence, Tuple


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MODES = ("normal", "fallback")
MAXIMIZE = (
    "macro_f1_min",
    "attack_recall_min",
    "benign_recall_min",
    "auprc_min",
)
MINIMIZE = ("ece_max",)
OBJECTIVES = MAXIMIZE + MINIMIZE
MIN_CONSTRAINTS = {
    "macro_f1_min": "min_macro_f1_min",
    "attack_recall_min": "min_attack_recall_min",
    "benign_recall_min": "min_benign_recall_min",
    "auprc_min": "min_auprc_min",
    "ground_truth_event_recall_min": "min_ground_truth_event_recall_min",
    "key_flow_coverage_min": "min_key_flow_coverage_min",
}
MAX_CONSTRAINTS = {
    "ece_max": "max_ece_max",
    "budget_overrun_count_max": "max_budget_overrun_count_max",
    "budget_us_max": "max_budget_us",
}
METRIC_NAMES = tuple(MIN_CONSTRAINTS) + tuple(MAX_CONSTRAINTS)


def _number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _append(errors: List[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def _path_is_clean(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value.startswith("/")
        and not any(character in value for character in "\r\n\x00")
    )


def _aggregate_modes(
    mode_metrics: Mapping[str, object],
) -> Optional[Dict[str, float]]:
    if set(mode_metrics) != set(MODES):
        return None
    rows = [mode_metrics[mode] for mode in MODES]
    if not all(isinstance(row, Mapping) for row in rows):
        return None
    if any(not all(_number(row.get(name)) for name in METRIC_NAMES) for row in rows):
        return None
    aggregated: Dict[str, float] = {}
    for name in MIN_CONSTRAINTS:
        aggregated[name] = min(float(row[name]) for row in rows)
    for name in MAX_CONSTRAINTS:
        aggregated[name] = max(float(row[name]) for row in rows)
    return aggregated


def _dominates(
    left: Mapping[str, float], right: Mapping[str, float]
) -> bool:
    no_worse = all(left[name] >= right[name] for name in MAXIMIZE)
    no_worse = no_worse and all(left[name] <= right[name] for name in MINIMIZE)
    strictly_better = any(left[name] > right[name] for name in MAXIMIZE)
    strictly_better = strictly_better or any(
        left[name] < right[name] for name in MINIMIZE
    )
    return no_worse and strictly_better


def _materially_dominates(
    left: Mapping[str, float],
    right: Mapping[str, float],
    epsilon: float,
) -> bool:
    """Return true for epsilon dominance without hiding a material regression."""

    benefits = [left[name] - right[name] for name in MAXIMIZE]
    benefits.extend(right[name] - left[name] for name in MINIMIZE)
    return all(value >= -epsilon for value in benefits) and any(
        value > epsilon for value in benefits
    )


def _front(
    metrics: Mapping[str, Mapping[str, float]],
    dominance,
) -> List[str]:
    names = sorted(metrics)
    return [
        name
        for name in names
        if not any(
            dominance(metrics[other], metrics[name])
            for other in names
            if other != name
        )
    ]


def _same_metrics(
    left: object, right: Mapping[str, float], tolerance: float = 1e-12
) -> bool:
    return isinstance(left, Mapping) and set(left) == set(right) and all(
        _number(left.get(name))
        and abs(float(left[name]) - float(value)) <= tolerance
        for name, value in right.items()
    )


def audit_algorithm_search(search: Mapping[str, object]) -> Dict[str, object]:
    """Recompute algorithm search eligibility and optimality.

    ``accepted`` means that the full bounded search, not merely its finalists,
    has complete hash-bound paired evidence.  A finalist comparison may still
    be computed when the full proof is incomplete, but cannot be promoted to a
    global or production optimum.
    """

    errors: List[str] = []
    if search.get("schema_version") != 2:
        _append(errors, "search.schema_version")

    budget = search.get("exploration_budget")
    if not isinstance(budget, Mapping):
        budget = {}
        _append(errors, "search.exploration_budget")
    candidates = search.get("candidates")
    if not isinstance(candidates, list):
        candidates = []
        _append(errors, "search.candidates")
    minimum = budget.get("minimum_candidates")
    maximum = budget.get("maximum_candidates")
    hard_cap = budget.get("hard_cap_candidates")
    actual = budget.get("actual_candidates")
    if not all(isinstance(value, int) and not isinstance(value, bool) for value in (
        minimum,
        maximum,
        hard_cap,
        actual,
    )):
        _append(errors, "search.exploration_budget.types")
    elif not (
        1 <= minimum <= actual == len(candidates) <= maximum <= hard_cap <= 12
    ):
        _append(errors, "search.exploration_budget.bounds")

    protocol = search.get("selection_protocol")
    if not isinstance(protocol, Mapping):
        protocol = {}
        _append(errors, "search.selection_protocol")
    if protocol.get("hard_constraints_before_pareto") is not True:
        _append(errors, "search.protocol.hard_constraints_before_pareto")
    if protocol.get("normal_and_fallback_must_be_paired") is not True:
        _append(errors, "search.protocol.normal_fallback_pair")
    repeats_required = protocol.get("measured_repeats_per_mode_for_finalists")
    if not isinstance(repeats_required, int) or repeats_required < 3:
        _append(errors, "search.protocol.measured_repeats")
    epsilon = protocol.get("minimum_material_improvement")
    if not _number(epsilon) or not 0 <= float(epsilon) < 1:
        epsilon = 0.0
        _append(errors, "search.protocol.minimum_material_improvement")
    expected_objectives = [
        "macro_f1_min:max",
        "attack_recall_min:max",
        "benign_recall_min:max",
        "auprc_min:max",
        "ece_max:min",
    ]
    if protocol.get("pareto_objectives") != expected_objectives:
        _append(errors, "search.protocol.pareto_objectives")

    constraints = search.get("hard_constraints")
    if not isinstance(constraints, Mapping):
        constraints = {}
        _append(errors, "search.hard_constraints")
    for gate_name in tuple(MIN_CONSTRAINTS.values()) + tuple(
        MAX_CONSTRAINTS.values()
    ):
        if not _number(constraints.get(gate_name)):
            _append(errors, "search.hard_constraints.{}".format(gate_name))

    resource_budget = search.get("resource_budget")
    if not isinstance(resource_budget, Mapping):
        resource_budget = {}
        _append(errors, "search.resource_budget")
    if resource_budget.get("expected_batch_size") != 512:
        _append(errors, "search.resource_budget.expected_batch_size")
    if resource_budget.get("max_budget_us") != constraints.get("max_budget_us"):
        _append(errors, "search.resource_budget.max_budget_us")
    if not _number(resource_budget.get("execution_budget_safety_ratio")):
        _append(errors, "search.resource_budget.execution_budget_safety_ratio")
    required_joint_resources = resource_budget.get(
        "production_joint_comparison_required_metrics"
    )
    if required_joint_resources != [
        "throughput_mpps",
        "packet_drop_count",
        "end_to_end_p99_us",
        "cpu_utilization",
        "gpu_utilization",
        "memory_utilization",
        "key_flow_coverage",
        "fallback_recovery_s",
    ]:
        _append(errors, "search.resource_budget.production_joint_metrics")

    candidate_ids: List[str] = []
    parameter_tuples: List[Tuple[object, ...]] = []
    candidate_audits: List[Dict[str, object]] = []
    complete_metrics: Dict[str, Mapping[str, float]] = {}
    feasible_metrics: Dict[str, Mapping[str, float]] = {}
    hash_complete_count = 0
    metric_complete_count = 0
    for index, candidate in enumerate(candidates):
        prefix = "candidate.{}".format(index)
        if not isinstance(candidate, Mapping):
            _append(errors, prefix + ".mapping")
            continue
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not candidate_id:
            _append(errors, prefix + ".id")
            candidate_id = "<invalid-{}>".format(index)
        candidate_ids.append(candidate_id)
        parameter_tuples.append(
            tuple(
                candidate.get(name)
                for name in (
                    "feature_profile",
                    "classifier",
                    "threshold_policy",
                    "adaptation_policy",
                )
            )
        )
        candidate_errors: List[str] = []
        evidence_path = candidate.get("evidence")
        if not _path_is_clean(evidence_path):
            candidate_errors.append("evidence_path")
            _append(errors, "{}.evidence_path".format(candidate_id))
        evidence_sha256 = candidate.get("evidence_sha256")
        hash_complete = isinstance(evidence_sha256, str) and bool(
            SHA256_PATTERN.fullmatch(evidence_sha256)
        )
        if hash_complete:
            hash_complete_count += 1
        else:
            candidate_errors.append("evidence_sha256")
            _append(errors, "{}.evidence_sha256".format(candidate_id))

        mode_metrics = candidate.get("mode_metrics")
        aggregated = (
            _aggregate_modes(mode_metrics)
            if isinstance(mode_metrics, Mapping)
            else None
        )
        if aggregated is None:
            candidate_errors.append("paired_mode_metrics")
            _append(errors, "{}.paired_mode_metrics".format(candidate_id))
        else:
            metric_complete_count += 1
            complete_metrics[candidate_id] = aggregated
            if not _same_metrics(
                candidate.get("reported_worst_case_metrics"), aggregated
            ):
                candidate_errors.append("reported_worst_case_metrics")
                _append(
                    errors,
                    "{}.reported_worst_case_metrics".format(candidate_id),
                )
            mode_contract = candidate.get("mode_contract")
            if not isinstance(mode_contract, Mapping):
                candidate_errors.append("mode_contract")
                _append(errors, "{}.mode_contract".format(candidate_id))
            else:
                if set(mode_contract.get("repeat_count_by_mode") or {}) != set(
                    MODES
                ) or any(
                    mode_contract["repeat_count_by_mode"].get(mode, 0)
                    < repeats_required
                    for mode in MODES
                ):
                    candidate_errors.append("repeat_count_by_mode")
                    _append(
                        errors,
                        "{}.repeat_count_by_mode".format(candidate_id),
                    )
                manifest_hash = mode_contract.get("input_hash_manifest_sha256")
                if not isinstance(manifest_hash, str) or not SHA256_PATTERN.fullmatch(
                    manifest_hash
                ):
                    candidate_errors.append("input_hash_manifest_sha256")
                    _append(
                        errors,
                        "{}.input_hash_manifest_sha256".format(candidate_id),
                    )

            violations: List[str] = []
            for metric_name, gate_name in MIN_CONSTRAINTS.items():
                gate = constraints.get(gate_name)
                if not _number(gate) or aggregated[metric_name] < float(gate):
                    violations.append(gate_name)
            for metric_name, gate_name in MAX_CONSTRAINTS.items():
                gate = constraints.get(gate_name)
                if not _number(gate) or aggregated[metric_name] > float(gate):
                    violations.append(gate_name)
            if not violations:
                feasible_metrics[candidate_id] = aggregated
        candidate_audits.append(
            {
                "candidate_id": candidate_id,
                "stage": candidate.get("stage"),
                "evidence_hash_complete": hash_complete,
                "paired_metrics_complete": aggregated is not None,
                "recomputed_worst_case_metrics": aggregated,
                "hard_constraint_violations": (
                    []
                    if aggregated is not None
                    and candidate_id in feasible_metrics
                    else None
                ),
                "auditable": not candidate_errors,
                "errors": candidate_errors,
            }
        )

    if len(candidate_ids) != len(set(candidate_ids)):
        _append(errors, "search.duplicate_candidate_id")
    if len(parameter_tuples) != len(set(parameter_tuples)):
        _append(errors, "search.duplicate_parameter_candidate")

    strict_front = _front(feasible_metrics, _dominates)
    practical_front = _front(
        {name: feasible_metrics[name] for name in strict_front},
        lambda left, right: _materially_dominates(
            left, right, float(epsilon)
        ),
    )

    finalist_ids = sorted(
        candidate.get("id")
        for candidate in candidates
        if isinstance(candidate, Mapping)
        and candidate.get("stage") == "fresh_confirmatory"
        and isinstance(candidate.get("id"), str)
    )
    finalist_metrics = {
        name: feasible_metrics[name]
        for name in finalist_ids
        if name in feasible_metrics
    }
    finalist_strict_front = _front(finalist_metrics, _dominates)
    finalist_practical_front = _front(
        {
            name: finalist_metrics[name]
            for name in finalist_strict_front
        },
        lambda left, right: _materially_dominates(
            left, right, float(epsilon)
        ),
    )
    finalist_winner = (
        finalist_practical_front[0]
        if len(finalist_practical_front) == 1
        else None
    )
    selected = search.get("selected_candidate")
    if finalist_winner is not None and selected != finalist_winner:
        _append(errors, "search.selected_candidate.finalist_comparison")
    if search.get("strict_pareto_front") != finalist_strict_front:
        _append(errors, "search.reported_strict_pareto_front")
    if search.get("practical_front") != finalist_practical_front:
        _append(errors, "search.reported_practical_front")

    all_candidates_complete = (
        len(candidates) > 0
        and metric_complete_count == len(candidates)
        and hash_complete_count == len(candidates)
    )
    full_search_front_matches = (
        search.get("strict_pareto_front") == strict_front
        and search.get("practical_front") == practical_front
    )
    algorithm_only_optimum_proven = (
        all_candidates_complete
        and full_search_front_matches
        and len(practical_front) == 1
        and selected == practical_front[0]
        and not errors
    )
    production_joint_optimum_proven = False
    return {
        "schema_version": 1,
        "scope": "bounded_offline_algorithm_optimality_audit",
        "accepted": algorithm_only_optimum_proven,
        "search_id": search.get("search_id"),
        "candidate_hard_cap": hard_cap,
        "declared_candidate_count": actual,
        "actual_candidate_count": len(candidates),
        "paired_metric_complete_candidate_count": metric_complete_count,
        "evidence_hash_complete_candidate_count": hash_complete_count,
        "feasible_metric_complete_candidate_count": len(feasible_metrics),
        "strict_pareto_front_recomputed_from_available_metrics": strict_front,
        "practical_front_recomputed_from_available_metrics": practical_front,
        "confirmatory_finalist_ids": finalist_ids,
        "confirmatory_strict_pareto_front": finalist_strict_front,
        "confirmatory_practical_front": finalist_practical_front,
        "confirmatory_practical_winner": finalist_winner,
        "confirmatory_metric_comparison_complete": (
            len(finalist_ids) >= 2
            and len(finalist_metrics) == len(finalist_ids)
        ),
        "confirmatory_evidence_hash_complete": all(
            next(
                audit["evidence_hash_complete"]
                for audit in candidate_audits
                if audit["candidate_id"] == name
            )
            for name in finalist_ids
        ) if finalist_ids else False,
        "algorithm_only_practical_optimum_proven": (
            algorithm_only_optimum_proven
        ),
        "production_joint_optimum_proven": production_joint_optimum_proven,
        "production_joint_optimum_reason": (
            "offline quality candidates do not contain comparable physical "
            "capture throughput, drop, tail latency, attributed resources, "
            "key-flow coverage, and fallback evidence"
        ),
        "final_pareto_ingestion_allowed": False,
        "candidate_audits": candidate_audits,
        "errors": sorted(errors),
    }

