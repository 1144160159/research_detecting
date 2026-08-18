"""Constraint-first selection for a bounded inference runtime search."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping


COMMON_IDENTITY_FIELDS = (
    "candidate_id",
    "config_version",
    "input_sha256",
    "thresholds_sha256",
)

MAX_METRICS = (
    "pipeline_drop_rate_max",
    "parse_reject_rate_max",
    "end_to_end_p99_us_max",
    "end_to_end_p999_us_max",
    "internal_feature_p99_us_max",
    "inference_batch_p99_us_max",
    "budget_overrun_count_max",
)

MIN_METRICS = (
    "observed_mpps_min",
    "key_flow_coverage_min",
)

OBJECTIVES = (
    "inference_batch_p99_us_max",
    "internal_feature_p99_us_max",
    "end_to_end_p99_us_max",
    "eligible_cpu_count",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _number(mapping, key, errors, prefix):
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append("{}.{}.missing_or_invalid".format(prefix, key))
        return None
    return float(value)


def _dominates(left, right):
    left_values = left["objective_values"]
    right_values = right["objective_values"]
    no_worse = all(
        left_values[name] <= right_values[name] for name in OBJECTIVES
    )
    strictly_better = any(
        left_values[name] < right_values[name] for name in OBJECTIVES
    )
    return no_worse and strictly_better


def _campaigns(value):
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, list):
        return value
    return []


def select_runtime_candidate(
    config: Mapping[str, object],
    evidence_by_candidate: Mapping[
        str, Mapping[str, object] | list[Mapping[str, object]]
    ],
):
    """Return a cross-campaign constraint audit and bounded Pareto selection."""

    errors = []
    candidates = config.get("candidates")
    if not isinstance(candidates, list):
        return {
            "schema_version": 2,
            "scope": "runtime_candidate_constraint_first_selection",
            "accepted": False,
            "errors": ["config.candidates.missing_or_invalid"],
            "selected_candidate": None,
        }
    budget = config.get("search_budget") or {}
    minimum = budget.get("minimum_candidates")
    maximum = budget.get("maximum_candidates")
    if not isinstance(minimum, int) or not isinstance(maximum, int):
        errors.append("config.search_budget.missing_or_invalid")
    elif not minimum <= len(candidates) <= maximum:
        errors.append("candidate_count_outside_search_budget")

    thresholds = config.get("hard_thresholds") or {}
    required_repeats = thresholds.get("minimum_repeats")
    if not isinstance(required_repeats, int) or required_repeats < 1:
        errors.append("config.hard_thresholds.minimum_repeats")
        required_repeats = 3
    minimum_campaigns = thresholds.get("minimum_campaigns", 1)
    if not isinstance(minimum_campaigns, int) or minimum_campaigns < 1:
        errors.append("config.hard_thresholds.minimum_campaigns")
        minimum_campaigns = 1
    minimum_total_repeats = thresholds.get(
        "minimum_total_repeats",
        required_repeats * minimum_campaigns,
    )
    if (
        not isinstance(minimum_total_repeats, int)
        or minimum_total_repeats < required_repeats * minimum_campaigns
    ):
        errors.append("config.hard_thresholds.minimum_total_repeats")
        minimum_total_repeats = required_repeats * minimum_campaigns

    results = []
    reference_identity = None
    reference_code_sha256s = None
    seen_ids = set()
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            errors.append("config.candidate.missing_or_invalid")
            continue
        candidate_id = candidate.get("candidate_id")
        prefix = "candidate.{}".format(candidate_id)
        if not isinstance(candidate_id, str) or not candidate_id:
            errors.append("config.candidate_id.missing_or_invalid")
            continue
        if candidate_id in seen_ids:
            errors.append("config.candidate_id.duplicate.{}".format(candidate_id))
            continue
        seen_ids.add(candidate_id)
        candidate_errors = []
        campaign_evidence = _campaigns(
            evidence_by_candidate.get(candidate_id)
        )
        if not campaign_evidence:
            candidate_errors.append("evidence.missing")
        if len(campaign_evidence) < minimum_campaigns:
            candidate_errors.append("evidence.campaign_count")

        campaign_metrics = []
        campaign_summaries = []
        candidate_identity = None
        code_sha256s = set()
        total_run_count = 0
        for index, evidence in enumerate(campaign_evidence, start=1):
            campaign_prefix = "{}.campaign{}".format(prefix, index)
            if not isinstance(evidence, Mapping):
                candidate_errors.append(
                    "evidence.campaign{}.missing_or_invalid".format(index)
                )
                continue
            identity = evidence.get("identity") or {}
            normalized_identity = {
                field: identity.get(field)
                for field in COMMON_IDENTITY_FIELDS
            }
            if candidate_identity is None:
                candidate_identity = normalized_identity
            elif normalized_identity != candidate_identity:
                candidate_errors.append(
                    "evidence.campaign_identity_inconsistent"
                )
            code_sha256 = identity.get("code_sha256")
            if (
                not isinstance(code_sha256, str)
                or len(code_sha256) != 64
                or any(
                    character not in "0123456789abcdef"
                    for character in code_sha256.lower()
                )
            ):
                candidate_errors.append(
                    "evidence.campaign{}.code_sha256".format(index)
                )
            else:
                code_sha256s.add(code_sha256.lower())

            if (
                evidence.get("scope")
                != "virtual_link_live_diagnostic_repeat_audit"
            ):
                candidate_errors.append(
                    "evidence.campaign{}.scope".format(index)
                )
            run_count = evidence.get("run_count")
            if run_count != required_repeats:
                candidate_errors.append(
                    "evidence.campaign{}.repeat_count".format(index)
                )
            if isinstance(run_count, int) and not isinstance(run_count, bool):
                total_run_count += run_count
            if evidence.get("final_pareto_ingestion_allowed") is not False:
                candidate_errors.append(
                    "evidence.campaign{}.final_pareto_marker".format(index)
                )
            if evidence.get("accepted") is not True:
                candidate_errors.append(
                    "evidence.campaign{}.repeat_audit_failed".format(index)
                )

            observed = evidence.get("observed_worst_case") or {}
            observed_metrics = {}
            for name in MAX_METRICS + MIN_METRICS:
                observed_metrics[name] = _number(
                    observed,
                    name,
                    candidate_errors,
                    campaign_prefix + ".observed",
                )
            campaign_metrics.append(observed_metrics)
            campaign_summaries.append(
                {
                    "campaign_index": index,
                    "run_count": run_count,
                    "accepted": evidence.get("accepted") is True,
                    "code_sha256": code_sha256,
                    "metrics": observed_metrics,
                }
            )

        if total_run_count < minimum_total_repeats:
            candidate_errors.append("evidence.total_repeat_count")
        if candidate_identity is not None:
            if reference_identity is None:
                reference_identity = candidate_identity
            elif candidate_identity != reference_identity:
                candidate_errors.append("evidence.identity_inconsistent")
        normalized_code_sha256s = sorted(code_sha256s)
        if reference_code_sha256s is None and normalized_code_sha256s:
            reference_code_sha256s = normalized_code_sha256s
        elif (
            normalized_code_sha256s
            and normalized_code_sha256s != reference_code_sha256s
        ):
            candidate_errors.append(
                "evidence.capture_code_campaigns_inconsistent"
            )

        metrics = {}
        for name in MAX_METRICS:
            values = [
                campaign[name]
                for campaign in campaign_metrics
                if campaign[name] is not None
            ]
            metrics[name] = max(values) if values else None
        for name in MIN_METRICS:
            values = [
                campaign[name]
                for campaign in campaign_metrics
                if campaign[name] is not None
            ]
            metrics[name] = min(values) if values else None
        cpu_count = candidate.get("eligible_cpu_count")
        if (
            isinstance(cpu_count, bool)
            or not isinstance(cpu_count, int)
            or cpu_count < 1
        ):
            candidate_errors.append("config.eligible_cpu_count")
            cpu_count = None
        metrics["eligible_cpu_count"] = cpu_count

        checks = (
            ("pipeline_drop_rate_max", "<=", "max_pipeline_drop_rate"),
            ("parse_reject_rate_max", "<=", "max_parse_reject_rate"),
            ("observed_mpps_min", ">=", "min_observed_mpps"),
            ("end_to_end_p99_us_max", "<=", "max_end_to_end_p99_us"),
            ("end_to_end_p999_us_max", "<=", "max_end_to_end_p999_us"),
            (
                "internal_feature_p99_us_max",
                "<=",
                "max_internal_feature_p99_us",
            ),
            (
                "inference_batch_p99_us_max",
                "<=",
                "max_inference_batch_p99_us",
            ),
            ("key_flow_coverage_min", ">=", "min_key_flow_coverage"),
            ("budget_overrun_count_max", "<=", "max_budget_overrun_count"),
        )
        for metric_name, operator, threshold_name in checks:
            threshold = thresholds.get(threshold_name)
            value = metrics.get(metric_name)
            if (
                isinstance(threshold, bool)
                or not isinstance(threshold, (int, float))
            ):
                errors.append(
                    "config.hard_thresholds.{}".format(threshold_name)
                )
                continue
            if value is None:
                continue
            passed = (
                value <= threshold
                if operator == "<="
                else value >= threshold
            )
            if not passed:
                candidate_errors.append(
                    "hard_gate.{}.{}{}".format(
                        metric_name, operator, threshold
                    )
                )

        objective_values = {
            name: metrics.get(name) for name in OBJECTIVES
        }
        if any(value is None for value in objective_values.values()):
            candidate_errors.append("objective.missing")
        results.append(
            {
                "candidate_id": candidate_id,
                "prediction_execution": candidate.get(
                    "prediction_execution"
                ),
                "cpu_set": candidate.get("cpu_set"),
                "campaign_count": len(campaign_evidence),
                "total_run_count": total_run_count,
                "capture_code_sha256s": normalized_code_sha256s,
                "campaigns": campaign_summaries,
                "hard_pass": not candidate_errors,
                "errors": sorted(set(candidate_errors)),
                "metrics": metrics,
                "objective_values": objective_values,
            }
        )

    passing = [result for result in results if result["hard_pass"]]
    pareto = []
    for result in passing:
        if not any(
            other is not result and _dominates(other, result)
            for other in passing
        ):
            pareto.append(result)
    pareto.sort(
        key=lambda result: tuple(
            result["objective_values"][name] for name in OBJECTIVES
        )
    )
    selected = pareto[0]["candidate_id"] if pareto else None
    if not passing:
        errors.append("no_candidate_passed_hard_constraints")
    if selected is None:
        errors.append("no_pareto_candidate_selected")

    return {
        "schema_version": 2,
        "scope": "runtime_candidate_constraint_first_selection",
        "accepted": not errors and selected is not None,
        "errors": sorted(set(errors)),
        "candidate_count": len(candidates),
        "passing_candidate_count": len(passing),
        "identity": {
            **(reference_identity or {}),
            "capture_code_sha256s": reference_code_sha256s or [],
        },
        "hard_thresholds": thresholds,
        "objectives_minimize": list(OBJECTIVES),
        "selection_rule": (
            "all_campaigns_hard_constraints_then_worst_case_pareto_then_"
            "lexicographic_objectives"
        ),
        "candidates": results,
        "pareto_front": [result["candidate_id"] for result in pareto],
        "selected_candidate": selected,
        "final_pareto_ingestion_allowed": False,
    }


def load_evidence_assignments(
    assignments: Iterable[str],
) -> tuple[dict[str, list[object]], list[dict[str, str]]]:
    evidence = {}
    provenance = []
    seen_paths = set()
    for assignment in assignments:
        candidate_id, separator, raw_path = assignment.partition("=")
        if not separator or not candidate_id or not raw_path:
            raise ValueError(
                "evidence must use CANDIDATE_ID=/absolute/path.json"
            )
        path = Path(raw_path)
        resolved_path = path.resolve()
        if resolved_path in seen_paths:
            raise ValueError(
                "duplicate evidence path: {}".format(path)
            )
        seen_paths.add(resolved_path)
        evidence.setdefault(candidate_id, []).append(
            json.loads(path.read_text(encoding="utf-8"))
        )
        provenance.append(
            {
                "candidate_id": candidate_id,
                "path": str(path),
                "sha256": sha256_file(path),
            }
        )
    return evidence, provenance
