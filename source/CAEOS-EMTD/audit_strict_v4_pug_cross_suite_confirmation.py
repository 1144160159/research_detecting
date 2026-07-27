from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from evaluate_strict_v4_pug_cross_suite_confirmation import (
    METRICS,
    load,
    validate_protocol,
)


METHODS = ("pairwise", "caeos_pug", "opendetect")
DIRECTIONS = {
    "known_macro_f1": "higher",
    "unknown_auroc": "higher",
    "unknown_aupr": "higher",
    "unknown_fpr95": "lower",
    "oscr": "higher",
}


def close(left: Any, right: Any, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def oriented_delta(
    candidate: float, reference: float, direction: str
) -> float:
    return (
        float(candidate) - float(reference)
        if direction == "higher"
        else float(reference) - float(candidate)
    )


def independently_recompute(
    records: list[dict[str, Any]],
    candidate: str,
    reference: str,
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        row = record["evaluation"]
        grouped[(row["suite"], row["scenario"])].append(row)
    if len(grouped) != 102:
        raise ValueError("audit requires 102 scenario identities")
    scenario_means = {}
    for identity, rows in grouped.items():
        if sorted(int(row["seed"]) for row in rows) != [269, 271, 277]:
            raise ValueError("audit requires three frozen seeds per scenario")
        scenario_means[identity] = {
            method: {
                metric: float(
                    np.mean([row[method][metric] for row in rows])
                )
                for metric in METRICS
            }
            for method in METHODS
        }
    suites = sorted({suite for suite, _scenario in scenario_means})
    if len(suites) != 7:
        raise ValueError("audit requires seven suites")

    metrics = {}
    for metric in METRICS:
        direction = DIRECTIONS[metric]
        by_suite = {}
        scenario_deltas = []
        for suite in suites:
            values = [
                reports
                for (row_suite, _scenario), reports in scenario_means.items()
                if row_suite == suite
            ]
            candidate_mean = float(
                np.mean([value[candidate][metric] for value in values])
            )
            reference_mean = float(
                np.mean([value[reference][metric] for value in values])
            )
            suite_delta = oriented_delta(
                candidate_mean, reference_mean, direction
            )
            by_suite[suite] = {
                "candidate_mean": candidate_mean,
                "reference_mean": reference_mean,
                "oriented_delta": float(suite_delta),
                "scenario_count": len(values),
            }
            scenario_deltas.extend(
                oriented_delta(
                    value[candidate][metric],
                    value[reference][metric],
                    direction,
                )
                for value in values
            )
        suite_deltas = np.asarray(
            [value["oriented_delta"] for value in by_suite.values()],
            dtype=np.float64,
        )
        metrics[metric] = {
            "direction": direction,
            "candidate_equal_suite_mean": float(
                np.mean(
                    [value["candidate_mean"] for value in by_suite.values()]
                )
            ),
            "reference_equal_suite_mean": float(
                np.mean(
                    [value["reference_mean"] for value in by_suite.values()]
                )
            ),
            "equal_suite_oriented_delta": float(suite_deltas.mean()),
            "nonnegative_suite_count": int((suite_deltas >= -1e-12).sum()),
            "positive_suite_count": int((suite_deltas > 1e-12).sum()),
            "minimum_suite_oriented_delta": float(suite_deltas.min()),
            "maximum_suite_oriented_delta": float(suite_deltas.max()),
            "minimum_scenario_oriented_delta": float(
                np.min(scenario_deltas)
            ),
            "by_suite": by_suite,
        }
    return metrics


def compare_metric_tree(
    expected: dict[str, Any], observed: dict[str, Any]
) -> bool:
    if set(expected) != set(observed):
        return False
    for metric, expected_metric in expected.items():
        observed_metric = observed.get(metric)
        if not isinstance(observed_metric, dict):
            return False
        if (
            expected_metric["direction"] != observed_metric.get("direction")
            or expected_metric["nonnegative_suite_count"]
            != observed_metric.get("nonnegative_suite_count")
            or expected_metric["positive_suite_count"]
            != observed_metric.get("positive_suite_count")
        ):
            return False
        for name in (
            "candidate_equal_suite_mean",
            "reference_equal_suite_mean",
            "equal_suite_oriented_delta",
            "minimum_suite_oriented_delta",
            "maximum_suite_oriented_delta",
            "minimum_scenario_oriented_delta",
        ):
            if not close(expected_metric[name], observed_metric.get(name)):
                return False
        if set(expected_metric["by_suite"]) != set(
            observed_metric.get("by_suite", {})
        ):
            return False
        for suite, expected_suite in expected_metric["by_suite"].items():
            observed_suite = observed_metric["by_suite"][suite]
            if expected_suite["scenario_count"] != observed_suite.get(
                "scenario_count"
            ):
                return False
            for name in (
                "candidate_mean",
                "reference_mean",
                "oriented_delta",
            ):
                if not close(
                    expected_suite[name], observed_suite.get(name)
                ):
                    return False
    return True


def independently_recompute_route_coverage(
    protocol: dict[str, Any], records: list[dict[str, Any]]
) -> dict[str, Any]:
    contract = protocol["route_coverage_contract"]
    grouped: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for record in records:
        row = record["evaluation"]
        grouped[(row["suite"], row["scenario"])].append(
            bool(row["pug_selected"])
        )
    stable = sorted(
        f"{suite}/{scenario}"
        for (suite, scenario), selections in grouped.items()
        if len(selections) == int(contract["seed_count_per_scenario"])
        and sum(selections)
        >= int(contract["scenario_selected_seed_count_minimum"])
    )
    suites = sorted({identity.split("/", 1)[0] for identity in stable})
    return {
        "definition": "at_least_two_of_three_fresh_seeds",
        "pug_selected_scenario_count": len(stable),
        "pug_selected_suite_count": len(suites),
        "pug_selected_scenarios": stable,
        "pug_selected_suites": suites,
    }


def independently_recompute_checks(
    protocol: dict[str, Any],
    records: list[dict[str, Any]],
    pairwise: dict[str, Any],
    opendetect: dict[str, Any],
) -> tuple[dict[str, bool], dict[str, Any]]:
    gates = protocol["admission_gate"]
    pair_gate = gates["candidate_vs_pairwise"]
    open_gate = gates["candidate_vs_opendetect"]
    coverage_gate = gates["route_coverage"]
    coverage = independently_recompute_route_coverage(protocol, records)
    task_fpr95 = [
        record["evaluation"]["pairwise"]["unknown_fpr95"]
        - record["evaluation"]["caeos_pug"]["unknown_fpr95"]
        for record in records
    ]
    task_aupr = [
        record["evaluation"]["caeos_pug"]["unknown_aupr"]
        - record["evaluation"]["pairwise"]["unknown_aupr"]
        for record in records
    ]
    known_f1 = [
        abs(
            record["evaluation"]["pairwise"]["known_macro_f1"]
            - record["evaluation"]["caeos_pug"]["known_macro_f1"]
        )
        for record in records
    ]
    minimum = open_gate["per_metric_nonnegative_suite_count_minimum"]
    checks = {
        "route_scenario_coverage": coverage[
            "pug_selected_scenario_count"
        ]
        >= coverage_gate["pug_selected_scenario_count_minimum"],
        "route_suite_coverage": coverage["pug_selected_suite_count"]
        >= coverage_gate["pug_selected_suite_count_minimum"],
        "pairwise_fpr95_equal_suite_improvement": pairwise[
            "unknown_fpr95"
        ]["equal_suite_oriented_delta"]
        >= pair_gate[
            "equal_suite_mean_fpr95_oriented_improvement_minimum"
        ],
        "pairwise_auroc_nonregression": pairwise["unknown_auroc"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate["equal_suite_mean_auroc_oriented_nonregression"],
        "pairwise_aupr_nonregression": pairwise["unknown_aupr"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate["equal_suite_mean_aupr_oriented_nonregression"],
        "pairwise_oscr_nonregression": pairwise["oscr"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate["equal_suite_mean_oscr_oriented_nonregression"],
        "pairwise_known_f1_invariant": max(known_f1)
        <= pair_gate["known_macro_f1_absolute_tolerance"],
        "pairwise_per_task_fpr95_nonregression": min(task_fpr95)
        >= -pair_gate["per_task_fpr95_regression_tolerance"],
        "pairwise_per_task_aupr_nonregression": min(task_aupr)
        >= -pair_gate["per_task_aupr_regression_tolerance"],
        "pairwise_fpr95_suite_breadth": pairwise["unknown_fpr95"][
            "positive_suite_count"
        ]
        >= pair_gate["suite_fpr95_positive_count_minimum"],
        "pairwise_worst_suite_fpr95_nonregression": pairwise[
            "unknown_fpr95"
        ]["minimum_suite_oriented_delta"]
        >= -pair_gate["worst_suite_fpr95_oriented_regression_tolerance"],
        "opendetect_fpr95_noninferiority": opendetect["unknown_fpr95"][
            "equal_suite_oriented_delta"
        ]
        >= -open_gate["equal_suite_mean_fpr95_noninferiority_margin"],
        "opendetect_auroc_nonregression": opendetect["unknown_auroc"][
            "equal_suite_oriented_delta"
        ]
        >= open_gate["equal_suite_mean_auroc_oriented_nonregression"],
        "opendetect_aupr_nonregression": opendetect["unknown_aupr"][
            "equal_suite_oriented_delta"
        ]
        >= open_gate["equal_suite_mean_aupr_oriented_nonregression"],
        "opendetect_oscr_nonregression": opendetect["oscr"][
            "equal_suite_oriented_delta"
        ]
        >= open_gate["equal_suite_mean_oscr_oriented_nonregression"],
        "opendetect_known_f1_nonregression": opendetect[
            "known_macro_f1"
        ]["equal_suite_oriented_delta"]
        >= open_gate["equal_suite_mean_known_f1_oriented_nonregression"],
        "opendetect_suite_breadth_all_metrics": all(
            metric["nonnegative_suite_count"] >= minimum
            for metric in opendetect.values()
        ),
    }
    return checks, coverage


def build_audit(
    *,
    protocol: dict[str, Any],
    summary: dict[str, Any],
    records: list[dict[str, Any]],
    task_record_sha256: dict[str, str],
    input_file_sha256: dict[str, str],
    auditor_sha256: str,
) -> dict[str, Any]:
    validate_protocol(protocol, check_implementation=False)
    if (
        summary.get("schema_version")
        != "strict_v4_pug_cross_suite_confirmation_summary_v1"
        or summary.get("state")
        != "cross_suite_confirmation_summary_complete"
        or summary.get("manifest_sha256") != canonical_hash(summary)
    ):
        raise ValueError("canonical PUG cross-suite summary required")
    expected_tasks = {
        (task["suite"], task["scenario"], int(task["seed"]))
        for task in protocol["confirmation_universe"]["tasks"]
    }
    observed_tasks = []
    records_canonical = True
    protocol_binding = True
    selection_isolation = True
    for record in records:
        records_canonical &= (
            record.get("manifest_sha256") == canonical_hash(record)
        )
        protocol_binding &= (
            record.get("input_evidence", {}).get(
                "protocol_manifest_sha256"
            )
            == protocol["manifest_sha256"]
        )
        selection_isolation &= (
            record.get("evaluation", {}).get(
                "unknown_or_test_labels_used_for_selection"
            )
            is False
        )
        task = record.get("task", {})
        observed_tasks.append(
            (task.get("suite"), task.get("scenario"), task.get("seed"))
        )
    task_universe = (
        len(records) == 306
        and len(set(observed_tasks)) == 306
        and set(observed_tasks) == expected_tasks
    )
    hash_binding = (
        summary.get("input_evidence", {}).get("task_record_sha256")
        == dict(sorted(task_record_sha256.items()))
    )
    pairwise = independently_recompute(records, "caeos_pug", "pairwise")
    opendetect = independently_recompute(
        records, "caeos_pug", "opendetect"
    )
    pairwise_reconciles = compare_metric_tree(
        pairwise, summary["candidate_vs_pairwise"]["metrics"]
    )
    opendetect_reconciles = compare_metric_tree(
        opendetect, summary["candidate_vs_opendetect"]["metrics"]
    )
    checks, coverage = independently_recompute_checks(
        protocol, records, pairwise, opendetect
    )
    decision_reconciles = (
        summary.get("decision", {}).get("checks") == checks
        and summary.get("decision", {}).get("route_coverage") == coverage
        and summary.get("decision", {}).get("passes") == all(checks.values())
    )
    bootstrap = summary.get("bootstrap_reporting", {})
    bootstrap_metadata = True
    for offset, name in enumerate(
        ("candidate_vs_pairwise", "candidate_vs_opendetect")
    ):
        value = bootstrap.get(name, {})
        bootstrap_metadata &= (
            value.get("repetitions")
            == protocol["primary_statistics"]["bootstrap_repetitions"]
            and value.get("seed")
            == int(protocol["manifest_sha256"][:8], 16) + offset
            and value.get("blocks") == "suite_then_scenario"
            and value.get("reporting_only_not_an_admission_gate") is True
        )
        for metric in METRICS:
            interval = value.get("metrics", {}).get(metric, {})
            numbers = [
                interval.get("lower_95"),
                interval.get("median"),
                interval.get("upper_95"),
            ]
            bootstrap_metadata &= all(
                isinstance(number, (int, float)) and np.isfinite(number)
                for number in numbers
            ) and numbers[0] <= numbers[1] <= numbers[2]

    integrity_checks = {
        "summary_canonical": True,
        "task_record_count_and_universe": task_universe,
        "task_records_canonical": records_canonical,
        "task_protocol_binding": protocol_binding,
        "task_selection_isolation": selection_isolation,
        "task_file_sha_binding": hash_binding,
        "pairwise_point_metrics_independently_reconcile": (
            pairwise_reconciles
        ),
        "opendetect_point_metrics_independently_reconcile": (
            opendetect_reconciles
        ),
        "decision_and_route_independently_reconcile": decision_reconciles,
        "bootstrap_metadata_and_intervals_valid": bootstrap_metadata,
    }
    integrity_passes = all(integrity_checks.values())
    effect_passes = bool(summary["decision"]["passes"])
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pug_cross_suite_confirmation_audit_v1"
        ),
        "state": "cross_suite_confirmation_independent_audit_complete",
        "integrity": {
            "passes": integrity_passes,
            "checks": integrity_checks,
        },
        "effect": {
            "passes": effect_passes,
            "checks": checks,
            "route_coverage": coverage,
            "negative_effect_is_a_valid_audited_outcome": True,
        },
        "selection": {
            "candidate_selected": integrity_passes and effect_passes,
            "selected_algorithm": (
                "caeos_pug"
                if integrity_passes and effect_passes
                else "upstream_incumbent"
            ),
        },
        "input_manifest_sha256": {
            "protocol": protocol["manifest_sha256"],
            "summary": summary["manifest_sha256"],
        },
        "input_file_sha256": dict(sorted(input_file_sha256.items())),
        "implementation_sha256": {
            "audit_strict_v4_pug_cross_suite_confirmation.py": auditor_sha256
        },
        "claim_boundary": {
            "selection_is_limited_to_frozen_strict_v4_scope": True,
            "external_malicious_parrot_deployment_and_efficiency_required": True,
            "bootstrap_values_are_checked_not_independently_resampled": True,
            "no_comprehensive_sota_claim_is_authorized_here": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/summary.json"
        ),
    )
    parser.add_argument(
        "--task-root",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/tasks"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/audit.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    summary_path = resolve(args.summary)
    task_root = resolve(args.task_root)
    output_path = resolve(args.output)
    if not protocol_path.is_file() or not summary_path.is_file():
        if output_path.exists():
            raise ValueError("pending summary must not retain an audit")
        print("state=pending_summary")
        return
    protocol = load(protocol_path)
    validate_protocol(protocol)
    paths = sorted(task_root.rglob("*.json")) if task_root.is_dir() else []
    if len(paths) != 306:
        raise ValueError("complete task universe required before audit")
    summary = load(summary_path)
    records = [load(path) for path in paths]
    auditor_path = Path(__file__).resolve()
    audit = build_audit(
        protocol=protocol,
        summary=summary,
        records=records,
        task_record_sha256={
            path.relative_to(root).as_posix(): file_hash(path)
            for path in paths
        },
        input_file_sha256={
            protocol_path.relative_to(root).as_posix(): file_hash(
                protocol_path
            ),
            summary_path.relative_to(root).as_posix(): file_hash(
                summary_path
            ),
        },
        auditor_sha256=file_hash(auditor_path),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        if load(output_path) != audit:
            raise ValueError("existing audit is immutable")
    else:
        temporary = output_path.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(audit, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output_path)
    print(f"integrity_passes={audit['integrity']['passes']}")
    print(f"effect_passes={audit['effect']['passes']}")
    print(f"manifest_sha256={audit['manifest_sha256']}")
    print(f"file_sha256={file_hash(output_path)}")


if __name__ == "__main__":
    main()
