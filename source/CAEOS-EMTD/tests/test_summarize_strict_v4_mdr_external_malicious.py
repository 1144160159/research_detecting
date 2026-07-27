import numpy as np

from summarize_strict_v4_mdr_external_malicious import (
    aggregate,
    holm_adjust,
    metric_report,
    oriented,
)


def report(value):
    return {
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
        "known_macro_f1": value,
    }


def test_oriented_metrics_use_correct_direction():
    candidate, comparator = report(0.8), report(0.6)
    assert oriented(candidate, comparator, "unknown_auroc") > 0
    assert oriented(candidate, comparator, "unknown_fpr95") > 0


def test_aggregate_averages_three_seeds_before_statistics():
    records = []
    for dataset in ("LSNM2024", "CICDDoS2019"):
        for attack in ("a", "b"):
            for seed in (223, 227, 229):
                records.append(
                    {
                        "dataset": dataset,
                        "unknown_attack_family": attack,
                        "seed": seed,
                        "candidate": report(0.8),
                        "comparator": report(0.6),
                    }
                )
    result = aggregate(records, repetitions=100, bootstrap_seed=7)
    assert result["label_block_count"] == 4
    assert np.isclose(
        result["metrics"]["unknown_auroc"]["oriented_mean_gain"], 0.2
    )


def test_aggregate_rejects_missing_seed():
    import pytest

    records = [
        {
            "dataset": "LSNM2024",
            "unknown_attack_family": "a",
            "seed": seed,
            "candidate": report(0.8),
            "comparator": report(0.6),
        }
        for seed in (223, 227)
    ]
    with pytest.raises(ValueError, match="three seed"):
        aggregate(records, repetitions=10, bootstrap_seed=7)


def test_holm_adjustment_is_monotone_in_sorted_order():
    adjusted = holm_adjust({"a": 0.01, "b": 0.02, "c": 0.5})
    assert adjusted["a"] <= adjusted["b"] <= adjusted["c"]


def test_mdr_report_rejects_external_weight_reselection():
    import pytest

    metrics = {
        "schema_version": "strict_v4_mdr_external_runtime_metrics_v1",
        "diagnostics": {
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing": False,
            "test_labels_used_for_final_metrics_only": True,
            "external_weight_reselected": True,
        },
        "routing": {
            "inactive_prediction_exactly_pairwise": True,
            "inactive_risk_exactly_pairwise": True,
            "inactive_probability_exactly_pairwise": True,
        },
        "reports": {"candidate": report(0.8)},
    }
    with pytest.raises(ValueError, match="leakage or fallback"):
        metric_report(metrics, "mdr_caeos_v1")
