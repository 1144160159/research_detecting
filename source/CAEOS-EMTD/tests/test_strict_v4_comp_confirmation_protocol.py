from __future__ import annotations

from create_strict_v4_comp_confirmation_protocol import SCENARIOS, SEEDS
from evaluate_strict_v4_comp_confirmation import aggregate, gate_decision


def test_comp_confirmation_scope_is_frozen_and_unique() -> None:
    scenarios = SCENARIOS["stress"] + SCENARIOS["control"]

    assert SEEDS == [139, 149, 163]
    assert len(scenarios) == 6
    assert len(set(scenarios)) == 6
    assert len(scenarios) * len(SEEDS) == 18
    assert "recon_os_scan" in SCENARIOS["stress"]
    assert "ddos_slowloris" in SCENARIOS["control"]


def _protocol() -> dict:
    return {
        "admission_gate": {
            "candidate_vs_pairwise": {
                "mean_unknown_fpr95_oriented_improvement_minimum": 0.02,
                "mean_unknown_auroc_oriented_nonregression": -0.01,
                "mean_unknown_aupr_oriented_nonregression": -0.01,
                "mean_oscr_oriented_nonregression": -0.01,
                "known_macro_f1_absolute_tolerance": 1e-12,
                "per_task_unknown_fpr95_regression_tolerance": 0.02,
                "stress_group_fpr95_win_minimum": 5,
            },
            "candidate_vs_opendetect": {
                "mean_unknown_fpr95_noninferiority_margin": 0.01,
            },
        }
    }


def _rows() -> list[dict]:
    rows = []
    for index in range(18):
        shared = {
            "known_macro_f1": 0.8,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "oscr": 0.7,
        }
        rows.append(
            {
                "group": "stress" if index < 9 else "control",
                "pairwise": {**shared, "unknown_fpr95": 0.50},
                "caeos_comp": {**shared, "unknown_fpr95": 0.45},
                "opendetect": {**shared, "unknown_fpr95": 0.445},
            }
        )
    return rows


def _decision(rows: list[dict]) -> dict:
    vs_pairwise = aggregate(rows, "caeos_comp", "pairwise")
    vs_opendetect = aggregate(rows, "caeos_comp", "opendetect")
    return gate_decision(_protocol(), rows, vs_pairwise, vs_opendetect)


def test_comp_gate_treats_lower_fpr95_as_improvement() -> None:
    decision = _decision(_rows())

    assert decision["checks"]["mean_fpr95_improvement"] is True
    assert decision["checks"]["opendetect_fpr95_noninferiority"] is True
    assert decision["passes"] is True


def test_comp_gate_rejects_one_large_task_regression() -> None:
    rows = _rows()
    rows[9]["caeos_comp"]["unknown_fpr95"] = 0.53

    decision = _decision(rows)

    assert decision["checks"]["mean_fpr95_improvement"] is True
    assert decision["checks"]["per_task_fpr95_nonregression"] is False
    assert decision["passes"] is False


def test_comp_gate_rejects_opendetect_fpr95_inferiority() -> None:
    rows = _rows()
    for row in rows:
        row["opendetect"]["unknown_fpr95"] = 0.43

    decision = _decision(rows)

    assert decision["checks"]["opendetect_fpr95_noninferiority"] is False
    assert decision["passes"] is False
