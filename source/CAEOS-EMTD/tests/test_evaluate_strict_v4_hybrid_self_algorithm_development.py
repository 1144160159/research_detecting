import numpy as np

from evaluate_strict_v4_hybrid_self_algorithm_development import (
    combine_tail,
    empirical_cdf,
    gates,
    selection_key,
)


def test_empirical_cdf_and_tail_combinations() -> None:
    reference = np.array([0.1, 0.2, 0.4])
    values = np.array([0.05, 0.2, 0.5])
    np.testing.assert_allclose(
        empirical_cdf(reference, values), [0.0, 2.0 / 3.0, 1.0]
    )
    first = np.array([0.2, 0.8])
    second = np.array([0.5, 0.4])
    np.testing.assert_allclose(
        combine_tail(first, second, "tail_max"), [0.5, 0.8]
    )
    np.testing.assert_allclose(
        combine_tail(first, second, "tail_noisy_or"), [0.6, 0.88]
    )


def test_full_gate_and_selection_prefer_feasible_candidate() -> None:
    passing_metrics = {
        "alert_accuracy": 0.96,
        "alert_precision": 0.98,
        "alert_recall": 0.96,
        "benign_fpr": 0.04,
        "known_attack_type_accuracy": 0.96,
        "unknown_attack_recall": 0.96,
    }
    failing_metrics = dict(passing_metrics)
    failing_metrics["unknown_attack_recall"] = 0.94
    passing = {
        "macro_mean": passing_metrics,
        "gates": gates(passing_metrics),
    }
    failing = {
        "macro_mean": failing_metrics,
        "gates": gates(failing_metrics),
    }
    assert passing["gates"]["full_known_unknown_95_5_gate"]
    assert selection_key(passing) > selection_key(failing)
