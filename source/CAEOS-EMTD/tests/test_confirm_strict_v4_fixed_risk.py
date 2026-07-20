from __future__ import annotations

from confirm_strict_v4_fixed_risk import decision


def aggregate(gain: float) -> dict:
    return {
        "metrics": {
            metric: {
                "oriented_mean_improvement": gain,
                "bootstrap_95_ci": {"lower": gain / 2, "upper": gain * 2},
            }
            for metric in ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
        }
    }


def test_confirmation_gate_requires_every_suite_positive() -> None:
    combined = aggregate(0.02)
    suites = {"a": aggregate(0.02), "b": aggregate(0.01)}
    assert decision(combined, suites, 0.01)["passes"] is True
    suites["b"]["metrics"]["oscr"]["oriented_mean_improvement"] = -0.001
    assert decision(combined, suites, 0.01)["passes"] is False
