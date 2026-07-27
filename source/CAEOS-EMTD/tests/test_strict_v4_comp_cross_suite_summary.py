from __future__ import annotations

import copy

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_comp_cross_suite_confirmation import build_summary


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
            "strict_v4_comp_cross_suite_execution_protocol_v1"
        ),
        "state": "frozen_after_positive_pilot_before_cross_suite_execution",
        "execution_admitted": True,
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "paired_task_count": 306,
            "fresh_seeds": [269, 271, 277],
            "tasks": tasks,
        },
        "execution_controls": {
            "pairwise_policy_name": (
                "strict_v4_comp_cross_suite_pairwise_v1"
            )
        },
        "primary_statistics": {
            "bootstrap_repetitions": 100,
        },
        "admission_gate": {
            "candidate_vs_pairwise": {
                "equal_suite_mean_fpr95_oriented_improvement_minimum": 0.02,
                "equal_suite_mean_auroc_oriented_nonregression": -0.005,
                "equal_suite_mean_aupr_oriented_nonregression": -0.005,
                "equal_suite_mean_oscr_oriented_nonregression": -0.005,
                "known_macro_f1_absolute_tolerance": 1e-12,
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
    for index, task in enumerate(value["confirmation_universe"]["tasks"]):
        row = {
            **task,
            "group": "cross_suite",
            "pairwise": report(0.50),
            "caeos_comp": report(0.45),
            "opendetect": report(0.46),
        }
        record = {
            "schema_version": (
                "strict_v4_comp_cross_suite_task_evaluation_v1"
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


def test_summary_uses_equal_suite_aggregation_and_passes_positive_case() -> None:
    value = protocol()
    summary = summarize(value, records(value))

    assert summary["validation"]["task_record_count"] == 306
    assert summary["validation"]["scenario_count"] == 102
    assert summary["candidate_vs_pairwise"]["suite_count"] == 7
    assert (
        summary["candidate_vs_pairwise"]["metrics"]["unknown_fpr95"][
            "equal_suite_oriented_delta"
        ]
        > 0.049
    )
    assert summary["decision"]["passes"] is True
    assert summary["manifest_sha256"] == canonical_hash(summary)


def test_summary_rejects_single_task_fpr95_regression() -> None:
    value = protocol()
    rows = records(value)
    rows = copy.deepcopy(rows)
    rows[0]["evaluation"]["caeos_comp"]["unknown_fpr95"] = 0.60
    rows[0]["manifest_sha256"] = canonical_hash(rows[0])
    summary = summarize(value, rows)

    assert (
        summary["decision"]["checks"][
            "pairwise_per_task_fpr95_nonregression"
        ]
        is False
    )
    assert summary["decision"]["passes"] is False


def test_summary_rejects_opendetect_suite_breadth_failure() -> None:
    value = protocol()
    rows = records(value)
    rows = copy.deepcopy(rows)
    for row in rows:
        if row["task"]["suite"] in {"suite_0", "suite_1", "suite_2"}:
            row["evaluation"]["opendetect"]["unknown_auroc"] = 0.81
            row["manifest_sha256"] = canonical_hash(row)
    summary = summarize(value, rows)

    assert (
        summary["decision"]["checks"]["opendetect_suite_breadth_all_metrics"]
        is False
    )
    assert summary["decision"]["passes"] is False
