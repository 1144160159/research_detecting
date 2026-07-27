from __future__ import annotations

import numpy as np

from summarize_krc_csr_confirmation import (
    DIRECTED_METRICS,
    FAMILIES,
    aggregate,
    bootstrap_primary,
    directed_delta,
)


def test_directed_delta_orients_all_metrics_as_improvement() -> None:
    pairwise = {
        "unknown_auroc": 0.70,
        "unknown_aupr": 0.60,
        "unknown_fpr95": 0.30,
        "oscr": 0.50,
    }
    candidate = {
        "unknown_auroc": 0.72,
        "unknown_aupr": 0.63,
        "unknown_fpr95": 0.26,
        "oscr": 0.51,
    }
    assert np.isclose(
        directed_delta(candidate, pairwise, "unknown_auroc"), 0.02
    )
    assert np.isclose(
        directed_delta(candidate, pairwise, "unknown_aupr"), 0.03
    )
    assert np.isclose(
        directed_delta(candidate, pairwise, "unknown_fpr95"), 0.04
    )
    assert np.isclose(directed_delta(candidate, pairwise, "oscr"), 0.01)


def test_primary_aggregation_and_bootstrap_use_scenario_units() -> None:
    scenario_counts = [13, 13, 13, 13, 12, 12, 12]
    identities = []
    rows = []
    for suite_index, count in enumerate(scenario_counts):
        suite = f"suite_{suite_index}"
        for scenario_index in range(count):
            scenario = f"scenario_{scenario_index}"
            identities.append((suite, scenario))
            value = 0.01 + suite_index * 0.001
            for seed in (647, 653, 659):
                for family in FAMILIES:
                    for metric in DIRECTED_METRICS:
                        rows.append(
                            {
                                "suite": suite,
                                "scenario": scenario,
                                "training_seed": seed,
                                "family": family,
                                "metric": metric,
                                "directed_delta": value,
                            }
                        )
    result = aggregate(rows, identities)
    assert result["scenario_count"] == 88
    assert all(
        count == 7
        for count in result["suite_nonnegative_count"].values()
    )
    bootstrap = bootstrap_primary(
        result["scenario_composite_directed_mean"],
        replicates=200,
        seed=20260726,
    )
    assert bootstrap["unit"] == "scenario"
    assert bootstrap["lower_95"] > 0.0
    assert np.isclose(bootstrap["point_estimate"], 0.013)
