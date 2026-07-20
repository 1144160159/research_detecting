from screen_cross_suite_risk_candidates_v2 import REFERENCE, robust_screen


def metrics(auroc: float, aupr: float = 0.7, fpr95: float = 0.4, oscr: float = 0.7):
    return {
        "known_macro_f1": 0.9,
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


def test_robust_screen_uses_minimum_leave_one_seed_out_gain() -> None:
    seed_blocks = {}
    for seed, stable_gain, fragile_gain in ((7, 0.03, 0.10), (11, 0.03, -0.02), (19, 0.03, -0.02)):
        seed_blocks[seed] = {
            "suite/scenario_a": {
                REFERENCE: metrics(0.7),
                "stable": metrics(0.7 + stable_gain),
                "fragile": metrics(0.7 + fragile_gain),
            },
            "suite/scenario_b": {
                REFERENCE: metrics(0.6),
                "stable": metrics(0.6 + stable_gain),
                "fragile": metrics(0.6 + fragile_gain),
            },
        }
    result = robust_screen(seed_blocks, 0.01)
    assert result["selected_candidate"] == "stable"
    assert "fragile" not in result["robust_eligible_methods"]


def test_robust_screen_falls_back_when_no_gain_is_seed_stable() -> None:
    seed_blocks = {
        7: {"suite/scenario": {REFERENCE: metrics(0.7), "candidate": metrics(0.8)}},
        11: {"suite/scenario": {REFERENCE: metrics(0.7), "candidate": metrics(0.6)}},
    }
    result = robust_screen(seed_blocks, 0.01)
    assert result["selected_candidate"] == REFERENCE
