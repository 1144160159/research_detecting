from __future__ import annotations

import evaluate_strict_v4_fhmm_attack_routing_development_v3 as routing


def candidate(
    *,
    alert_accuracy: float,
    benign_fpr: float,
    known_type: float,
    unknown_alert: float,
) -> dict:
    repeat = {
        "operational": {
            "alert_accuracy": alert_accuracy,
            "benign_fpr": benign_fpr,
            "known_attack_type_accuracy": known_type,
            "unknown_attack_alert_recall": unknown_alert,
            "unknown_attack_recall": 0.4,
        },
        "research_main": {
            "known_macro_f1": 0.96,
            "known_balanced_accuracy": 0.97,
            "unknown_auroc": 0.90,
            "unknown_aupr_out": 0.70,
            "fpr_known_at_95_unknown_tpr": 0.20,
            "oscr_exact_v2": 0.89,
        },
        "gates": {
            "user_warning_95_5": (
                alert_accuracy >= 0.95 and benign_fpr < 0.05
            ),
            "typed_known_unknown_95_5": (
                alert_accuracy >= 0.95
                and benign_fpr < 0.05
                and known_type >= 0.95
                and unknown_alert >= 0.95
            ),
        },
    }
    return {
        "configuration": {},
        "per_repeat": {"43": repeat, "47": repeat},
        "macro_mean": {},
    }


def test_configuration_space_is_bounded() -> None:
    values = routing.configurations()
    assert len(values) == 36
    assert {value["open_budget"] for value in values} == {0.04}
    assert {value["type_rule"] for value in values} == {
        "validation_best_macro_f1_member"
    }


def test_selection_prioritizes_dual_split_full_gate() -> None:
    near = candidate(
        alert_accuracy=0.99,
        benign_fpr=0.01,
        known_type=0.99,
        unknown_alert=0.94,
    )
    passing = candidate(
        alert_accuracy=0.95,
        benign_fpr=0.049,
        known_type=0.95,
        unknown_alert=0.95,
    )
    assert routing.selection_key(passing) > routing.selection_key(near)


def test_strict_fpr_boundary_does_not_pass() -> None:
    value = candidate(
        alert_accuracy=0.99,
        benign_fpr=0.05,
        known_type=0.99,
        unknown_alert=0.99,
    )
    assert not routing.development_gates(value)[
        "all_repeats_user_warning_95_5"
    ]
