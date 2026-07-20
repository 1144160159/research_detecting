from screen_strict_v4_risk_candidates_v2 import (
    NEXT_CONFIRMATION,
    REFERENCE,
    build_manifest,
    screen,
)


def _block(suite: str, scenario: str, good: float, unstable: float):
    return {
        "suite": suite,
        "scenario": scenario,
        "seed_count": 1,
        "deltas": {
            REFERENCE: {
                "unknown_auroc": 0.0,
                "unknown_aupr": 0.0,
                "unknown_fpr95": 0.0,
                "oscr": 0.0,
            },
            "robust": {
                "unknown_auroc": good,
                "unknown_aupr": good,
                "unknown_fpr95": good,
                "oscr": good,
            },
            "unstable": {
                "unknown_auroc": good,
                "unknown_aupr": unstable,
                "unknown_fpr95": good,
                "oscr": good,
            },
        },
    }


def test_screen_selects_uniform_loso_safe_candidate_and_freezes_boundary():
    blocks = [
        _block("cic_ton_iot", "a", 0.02, -0.02),
        _block("cic_ton_iot", "b", 0.03, 0.01),
        _block("cic_iot2023", "c", 0.01, -0.02),
        _block("cic_iot2023", "d", 0.02, 0.01),
    ]
    result = screen(blocks, [REFERENCE, "robust", "unstable"])
    assert result["selected_candidate"] == "robust"
    assert result["eligible_ranking"] == ["robust"]

    validation = {
        "run_count": 6,
        "scenario_count": 4,
        "fixed_risk_method_count": 3,
        "source_metrics_combined_sha256": "abc",
    }
    manifest = build_manifest(validation, result)
    assert manifest["status"] == "frozen_unconfirmed"
    assert set(manifest["selected_suite_risks"].values()) == {"robust"}
    assert manifest["confirmation"]["seeds"] == [23, 37]
    assert manifest["confirmation"]["expected_run_count"] == 12
    assert set(NEXT_CONFIRMATION["scenarios"]["cic_ton_iot"]).isdisjoint(
        {"ransomware", "scanning", "xss", "backdoor", "ddos", "password"}
    )
