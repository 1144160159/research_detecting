from __future__ import annotations

from copy import deepcopy

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_protocol import SCHEMA
from summarize_strict_v4_selected_system_preconfirmation import (
    summarize_records,
)


METHODS = [
    "mlp_msp",
    "mlp_energy",
    "mlp_openmax",
    "mlp_knn",
    "mlp_vim",
    "mahalanobis_pp",
    "opendetect",
]
FAMILIES = [
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
]
METRICS = [
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
]


def report(value: float, fpr95: float) -> dict[str, float]:
    return {
        "known_macro_f1": value,
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": fpr95,
        "oscr": value,
    }


def fixture() -> tuple[dict, list[dict]]:
    sources = []
    records = []
    suite_counts = {
        **{f"suite{index}": 15 for index in range(6)},
        "suite6": 12,
    }
    for suite, count in suite_counts.items():
        for scenario_index in range(count):
            scenario = f"scenario{scenario_index}"
            for seed in (647, 653, 659):
                source = {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "corruption_seed": seed + 100,
                    "source_split_fingerprint": "a" * 64,
                }
                sources.append(source)
                conditions = []
                for family in FAMILIES:
                    conditions.append(
                        {
                            "family": family,
                            "candidate_degradation": {
                                **{metric: 0.02 for metric in METRICS},
                                "ece": 0.02,
                            },
                            "opendetect_degradation": {
                                **{metric: 0.10 for metric in METRICS},
                                "ece": 0.10,
                            },
                            "candidate_robustness_advantage": {
                                **{metric: 0.08 for metric in METRICS},
                                "ece": 0.08,
                            },
                        }
                    )
                records.append(
                    {
                        "source": source,
                        "candidate_clean_report": report(0.90, 0.10),
                        "classic_main_reports": {
                            method: report(0.80, 0.20)
                            for method in METHODS
                        },
                        "conditions": conditions,
                    }
                )
    protocol = {
        "schema_version": SCHEMA,
        "selected_algorithm": "krc_csr_caeos_v1",
        "sources": sources,
        "training_seeds": [647, 653, 659],
        "classic_main_gate": {
            "methods": METHODS,
        },
        "selective_sota_claim_ladder": {
            "unknown_detection": {
                "metrics": [
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                ],
                "comparators": METHODS,
                "known_macro_f1_maximum_degradation": 0.01,
            },
        },
        "corruption": {
            "families": FAMILIES,
            "absolute_maximum_mean_degradation": {
                "known_macro_f1": 0.10,
                "unknown_auroc": 0.15,
                "unknown_aupr": 0.15,
                "unknown_fpr95": 0.20,
                "oscr": 0.15,
            },
        },
        "aggregation": {
            "bootstrap_seed": 20260728,
            "bootstrap_repetitions": 50,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol, records


def test_all_three_preconfirmation_gates_cover_full_matrix() -> None:
    protocol, records = fixture()
    result = summarize_records(records, protocol)

    assert result["validation"] == {
        "task_record_count": 306,
        "scenario_count": 102,
        "suite_count": 7,
        "training_seeds": [647, 653, 659],
        "paired_corruption_condition_count": 1530,
        "all_records_canonical_and_bound": True,
        "passes": True,
    }
    classic = result["classic_main_gate"]
    assert classic["strict_five_metric_dominance_count"] == 7
    assert classic["passes"] is True
    assert len(classic["scenario_blocks"]) == 102
    assert len(classic["by_suite"]) == 7
    assert all(
        comparison["strictly_dominates_all_five_metrics"]
        for comparison in classic["comparisons"].values()
    )
    assert classic["selective_unknown_detection_sota_passes"] is True

    absolute = result["absolute_corruption_gate"]
    assert absolute["suite_threshold_check_count"] == 175
    assert absolute["all_175_suite_threshold_checks_pass"] is True
    assert absolute["passes"] is True

    comparative = result["comparative_corruption_gate"]
    assert comparative["all_five_families_pass"] is True
    assert comparative["passes"] is True
    assert result["selective_sota_claims"][
        "any_selective_sota_authorized"
    ] is True
    assert all(
        family["checks"][
            "all_six_metric_bootstrap_lower_bounds_strictly_positive"
        ]
        for family in comparative["by_family"].values()
    )


def test_each_effect_gate_fails_closed_on_bound_negative_evidence() -> None:
    protocol, records = fixture()
    negative = deepcopy(records)
    for record in negative:
        record["candidate_clean_report"] = report(0.70, 0.30)
    negative[0]["conditions"][0]["candidate_degradation"][
        "known_macro_f1"
    ] = 100.0
    negative[0]["conditions"][0]["candidate_robustness_advantage"][
        "known_macro_f1"
    ] = -100.0

    result = summarize_records(negative, protocol)

    assert result["classic_main_gate"]["passes"] is False
    assert result["absolute_corruption_gate"]["passes"] is False
    assert result["comparative_corruption_gate"]["passes"] is False
    assert result["selective_sota_claims"][
        "any_selective_sota_authorized"
    ] is False


def test_selective_unknown_sota_is_predeclared_without_five_metric_claim() -> None:
    protocol, records = fixture()
    selective = deepcopy(records)
    for record in selective:
        record["candidate_clean_report"] = {
            "known_macro_f1": 0.795,
            "unknown_auroc": 0.90,
            "unknown_aupr": 0.90,
            "unknown_fpr95": 0.10,
            "oscr": 0.70,
        }

    result = summarize_records(selective, protocol)

    assert result["classic_main_gate"]["passes"] is False
    assert result["classic_main_gate"][
        "selective_unknown_detection_sota_passes"
    ] is True
    claims = result["selective_sota_claims"]
    assert claims["unknown_detection"]["passes"] is True
    assert claims["comprehensive_sota_authorized"] is False
