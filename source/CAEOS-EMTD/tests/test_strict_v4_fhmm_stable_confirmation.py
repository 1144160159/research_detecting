from __future__ import annotations

import complete_strict_v4_fhmm_stable_confirmation as completion
import evaluate_strict_v4_fhmm_stable_confirmation as evaluation


def operational(**overrides: float) -> dict[str, float]:
    values = {
        "alert_accuracy": 0.96,
        "benign_fpr": 0.04,
        "known_attack_type_accuracy": 0.96,
        "unknown_attack_alert_recall": 0.90,
        "unknown_attack_recall": 0.35,
    }
    values.update(overrides)
    return values


def targets() -> dict[str, float]:
    return {
        "alert_accuracy_minimum": 0.95,
        "benign_fpr_strictly_below": 0.05,
        "known_attack_type_accuracy_minimum": 0.95,
        "unknown_attack_alert_recall_minimum": 0.85,
        "unknown_attack_rejection_recall_minimum": 0.30,
        "unknown_auroc_minimum": 0.88,
        "oscr_minimum": 0.87,
    }


def test_repeat_gates_separate_primary_and_full_typed_claims() -> None:
    gates = evaluation.repeat_gates(
        operational(),
        {"unknown_auroc": 0.89, "oscr_exact_v2": 0.88},
        targets(),
    )
    assert gates["user_warning_95_5"]
    assert gates["primary_known_unknown_confirmation"]
    assert not gates["full_typed_known_unknown_95_5"]


def test_repeat_gates_require_strictly_sub_five_percent_fpr() -> None:
    gates = evaluation.repeat_gates(
        operational(benign_fpr=0.05),
        {"unknown_auroc": 0.89, "oscr_exact_v2": 0.88},
        targets(),
    )
    assert not gates["user_warning_95_5"]
    assert not gates["primary_known_unknown_confirmation"]


def test_finite_history_requires_all_three_losses() -> None:
    valid = {
        "training": {
            "history": [
                {
                    "epoch": 0,
                    "training_loss": 1.0,
                    "validation_loss": 0.8,
                    "meta_outer_loss": 0.5,
                }
            ]
        }
    }
    invalid = {
        "training": {
            "history": [
                {
                    "epoch": 0,
                    "training_loss": 1.0,
                    "validation_loss": 0.8,
                    "meta_outer_loss": float("nan"),
                }
            ]
        }
    }
    assert completion.finite_history(valid)
    assert not completion.finite_history(invalid)
