from __future__ import annotations

from evaluate_strict_v4_fhmm_calibrated_aggregation_development_v2 import (
    augmented_worst_case,
    selection_key,
    threshold_unknown_f1,
)


def candidate(
    *,
    known_type: float,
    unknown_recall: float,
    oscr: float,
) -> dict:
    repeat = {
        "operational": {
            "unknown_attack_recall": unknown_recall,
            "unknown_label_precision": 0.8,
        }
    }
    return {
        "gates": {
            "all_repeats_typed_known_unknown_95_5": False,
            "all_repeats_user_warning_95_5": True,
            "all_repeats_legacy_botnet_expansion": True,
            "repeat_pass_count_typed_known_unknown_95_5": 1,
            "repeat_pass_count_user_warning_95_5": 2,
            "repeat_pass_count_legacy_botnet_expansion": 2,
        },
        "worst_case": {
            "alert_accuracy": 0.97,
            "benign_fpr": 0.04,
            "known_attack_type_accuracy": known_type,
            "unknown_attack_alert_recall": 0.90,
            "unknown_auroc": 0.88,
            "oscr_exact_v2": oscr,
        },
        "per_repeat": {"37": repeat, "41": repeat},
    }


def test_threshold_unknown_f1() -> None:
    value = {
        "operational": {
            "unknown_attack_recall": 0.5,
            "unknown_label_precision": 0.75,
        }
    }
    assert threshold_unknown_f1(value) == 0.6


def test_augmented_worst_case_adds_threshold_metrics() -> None:
    value = candidate(known_type=0.96, unknown_recall=0.4, oscr=0.85)
    worst = augmented_worst_case(value)
    assert worst["unknown_attack_recall"] == 0.4
    assert worst["unknown_label_precision"] == 0.8


def test_selection_prefers_unknown_rejection_after_hard_floors() -> None:
    lower_rejection = candidate(
        known_type=0.98,
        unknown_recall=0.1,
        oscr=0.90,
    )
    higher_rejection = candidate(
        known_type=0.96,
        unknown_recall=0.4,
        oscr=0.88,
    )
    assert selection_key(higher_rejection) > selection_key(lower_rejection)

