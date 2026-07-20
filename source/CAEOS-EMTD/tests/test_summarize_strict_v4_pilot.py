from __future__ import annotations

from summarize_strict_v4_pilot import aggregate_table, build_budget_decision


def report(auroc: float, oscr: float, f1: float = 0.9) -> dict[str, float]:
    return {
        "known_macro_f1": f1,
        "unknown_auroc": auroc,
        "unknown_aupr": auroc - 0.1,
        "unknown_fpr95": 1.0 - auroc,
        "oscr": oscr,
    }


def test_budget_gate_expands_when_caeos_is_consistently_best() -> None:
    blocks = {
        "suite/a": {"caeos": report(0.9, 0.8), "baseline": report(0.8, 0.7)},
        "suite/b": {"caeos": report(0.85, 0.78), "baseline": report(0.8, 0.7)},
    }
    decision = build_budget_decision(blocks, aggregate_table(blocks))
    assert decision["state"] == "expand_multiseed"
    assert all(decision["gates"].values())


def test_budget_gate_holds_on_large_single_scenario_regression() -> None:
    blocks = {
        "suite/a": {"caeos": report(0.9, 0.8), "baseline": report(0.8, 0.7)},
        "suite/b": {"caeos": report(0.6, 0.7), "baseline": report(0.8, 0.7)},
    }
    decision = build_budget_decision(blocks, aggregate_table(blocks))
    assert decision["state"] == "hold_for_risk_adaptation"
    assert decision["gates"]["every_task_auroc_within_0_10"] is False
