from __future__ import annotations

import copy

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_pug_cross_suite_confirmation import build_summary


SUITE_COUNTS = [15, 15, 15, 15, 14, 14, 14]


def protocol():
    tasks = [
        {
            "suite": f"suite_{suite}",
            "scenario": f"scenario_{suite}_{scenario:02d}",
            "seed": seed,
        }
        for suite, count in enumerate(SUITE_COUNTS)
        for scenario in range(count)
        for seed in [269, 271, 277]
    ]
    value = {
        "schema_version": (
            "strict_v4_pug_cross_suite_execution_protocol_v1"
        ),
        "state": "frozen_after_positive_pilot_before_cross_suite_execution",
        "execution_admitted": True,
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "paired_task_count": 306,
            "expected_pairwise_pug_runs": 306,
            "expected_fresh_opendetect_runs": 306,
            "fresh_seeds": [269, 271, 277],
            "tasks": tasks,
        },
        "execution_controls": {
            "candidate_policy_name": "strict_v4_pug_confirmation_v1",
            "candidate_risk_selection": (
                "nested_pug_continuous_outer_min_p"
            ),
        },
        "route_coverage_contract": {
            "seed_count_per_scenario": 3,
            "scenario_selected_seed_count_minimum": 2,
            "suite_selected_scenario_count_minimum": 1,
        },
        "primary_statistics": {"bootstrap_repetitions": 20},
        "admission_gate": {
            "candidate_vs_pairwise": {
                "equal_suite_mean_fpr95_oriented_improvement_minimum": 0.02,
                "equal_suite_mean_auroc_oriented_nonregression": 0.0,
                "equal_suite_mean_aupr_oriented_nonregression": 0.0,
                "equal_suite_mean_oscr_oriented_nonregression": 0.0,
                "known_macro_f1_absolute_tolerance": 1e-12,
                "per_task_aupr_regression_tolerance": 0.02,
                "per_task_fpr95_regression_tolerance": 0.02,
                "suite_fpr95_positive_count_minimum": 5,
                "worst_suite_fpr95_oriented_regression_tolerance": 0.01,
            },
            "candidate_vs_opendetect": {
                "equal_suite_mean_fpr95_noninferiority_margin": 0.01,
                "equal_suite_mean_auroc_oriented_nonregression": 0.0,
                "equal_suite_mean_aupr_oriented_nonregression": 0.0,
                "equal_suite_mean_oscr_oriented_nonregression": 0.0,
                "equal_suite_mean_known_f1_oriented_nonregression": 0.0,
                "per_metric_nonnegative_suite_count_minimum": 5,
            },
            "route_coverage": {
                "pug_selected_scenario_count_minimum": 18,
                "pug_selected_suite_count_minimum": 4,
            },
        },
        "output_contract": {
            "partial_metrics_must_not_be_aggregated": True,
        },
        "implementation_sha256": {},
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def report(fpr95: float):
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8,
        "unknown_aupr": 0.7,
        "unknown_fpr95": fpr95,
        "oscr": 0.7,
    }


def records(value):
    output = []
    for task in value["confirmation_universe"]["tasks"]:
        row = {
            **task,
            "group": "cross_suite",
            "pug_selected": True,
            "unknown_or_test_labels_used_for_selection": False,
            "pairwise": report(0.50),
            "caeos_pug": report(0.45),
            "opendetect": report(0.46),
        }
        record = {
            "schema_version": (
                "strict_v4_pug_cross_suite_task_evaluation_v1"
            ),
            "state": "single_paired_task_evaluation_complete",
            "task": task,
            "evaluation": row,
            "input_evidence": {
                "protocol_manifest_sha256": value["manifest_sha256"],
            },
        }
        record["manifest_sha256"] = canonical_hash(record)
        output.append(record)
    return output


def summarize(value, rows):
    return build_summary(
        protocol=value,
        records=rows,
        task_record_sha256={
            f"task_{index}": f"{index + 1:064x}"
            for index in range(len(rows))
        },
        protocol_file_sha256="a" * 64,
        summarizer_sha256="b" * 64,
    )


def test_summary_passes_equal_suite_and_route_coverage_case() -> None:
    value = protocol()
    summary = summarize(value, records(value))

    assert summary["validation"]["task_record_count"] == 306
    assert summary["candidate_vs_pairwise"]["suite_count"] == 7
    assert (
        summary["decision"]["route_coverage"][
            "pug_selected_scenario_count"
        ]
        == 102
    )
    assert summary["decision"]["passes"] is True
    assert summary["manifest_sha256"] == canonical_hash(summary)


def test_summary_rejects_unstable_route_coverage() -> None:
    value = protocol()
    rows = copy.deepcopy(records(value))
    for row in rows:
        if row["task"]["scenario"] >= "scenario_1_00":
            row["evaluation"]["pug_selected"] = False
            row["manifest_sha256"] = canonical_hash(row)
    summary = summarize(value, rows)

    assert summary["decision"]["checks"]["route_suite_coverage"] is False
    assert summary["decision"]["passes"] is False


def test_summary_rejects_single_task_aupr_regression() -> None:
    value = protocol()
    rows = copy.deepcopy(records(value))
    rows[0]["evaluation"]["caeos_pug"]["unknown_aupr"] = 0.60
    rows[0]["manifest_sha256"] = canonical_hash(rows[0])
    summary = summarize(value, rows)

    assert (
        summary["decision"]["checks"][
            "pairwise_per_task_aupr_nonregression"
        ]
        is False
    )
