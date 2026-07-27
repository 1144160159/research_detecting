from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score, roc_auc_score


def validation_safety_gate(
    *,
    labels: np.ndarray,
    incumbent_probability: np.ndarray,
    candidate_probability: np.ndarray,
    incumbent_risk: np.ndarray,
    candidate_risk: np.ndarray,
    minimum_f1_gain: float = -0.002,
    maximum_correct_risk_increase: float = 0.01,
    minimum_auc_gain: float = 0.0,
    minimum_separation_gain: float = 0.0,
    minimum_strict_proxy_gain: float = 0.005,
) -> dict[str, float | int | bool | str]:
    """Choose candidate or exact fallback using known validation labels only."""
    labels = np.asarray(labels, dtype=np.int64)
    incumbent_probability = np.asarray(incumbent_probability, dtype=np.float64)
    candidate_probability = np.asarray(candidate_probability, dtype=np.float64)
    incumbent_risk = np.asarray(incumbent_risk, dtype=np.float64).reshape(-1)
    candidate_risk = np.asarray(candidate_risk, dtype=np.float64).reshape(-1)
    count = len(labels)
    if not (
        incumbent_probability.shape == candidate_probability.shape
        and incumbent_probability.ndim == 2
        and len(incumbent_probability) == count
        and len(incumbent_risk) == count
        and len(candidate_risk) == count
    ):
        raise ValueError("validation gate inputs are not aligned")
    if count == 0 or not all(
        np.isfinite(values).all()
        for values in (
            incumbent_probability,
            candidate_probability,
            incumbent_risk,
            candidate_risk,
        )
    ):
        raise ValueError("validation gate inputs must be nonempty and finite")

    incumbent_prediction = incumbent_probability.argmax(axis=1)
    candidate_prediction = candidate_probability.argmax(axis=1)
    incumbent_f1 = float(
        f1_score(labels, incumbent_prediction, average="macro", zero_division=0)
    )
    candidate_f1 = float(
        f1_score(labels, candidate_prediction, average="macro", zero_division=0)
    )
    error = incumbent_prediction != labels
    error_count = int(error.sum())
    correct_count = int((~error).sum())
    if error_count == 0 or correct_count == 0:
        return {
            "enabled": False,
            "reason": "incumbent_validation_error_target_is_degenerate",
            "incumbent_macro_f1": incumbent_f1,
            "candidate_macro_f1": candidate_f1,
            "macro_f1_gain": candidate_f1 - incumbent_f1,
            "incumbent_error_detection_auroc": float("nan"),
            "candidate_error_detection_auroc": float("nan"),
            "error_detection_auroc_gain": float("nan"),
            "incumbent_error_correct_separation": float("nan"),
            "candidate_error_correct_separation": float("nan"),
            "separation_gain": float("nan"),
            "correct_risk_increase": float(np.mean(candidate_risk - incumbent_risk)),
            "error_count": error_count,
            "correct_count": correct_count,
        }
    incumbent_auc = float(roc_auc_score(error.astype(np.int64), incumbent_risk))
    candidate_auc = float(roc_auc_score(error.astype(np.int64), candidate_risk))
    incumbent_separation = float(
        incumbent_risk[error].mean() - incumbent_risk[~error].mean()
    )
    candidate_separation = float(
        candidate_risk[error].mean() - candidate_risk[~error].mean()
    )
    f1_gain = candidate_f1 - incumbent_f1
    auc_gain = candidate_auc - incumbent_auc
    separation_gain = candidate_separation - incumbent_separation
    correct_risk_increase = float(
        candidate_risk[~error].mean() - incumbent_risk[~error].mean()
    )
    checks = {
        "macro_f1": f1_gain >= minimum_f1_gain,
        "correct_risk": correct_risk_increase <= maximum_correct_risk_increase,
        "error_detection_auroc": auc_gain >= minimum_auc_gain,
        "error_correct_separation": separation_gain >= minimum_separation_gain,
        "strict_proxy_gain": max(auc_gain, separation_gain) >= minimum_strict_proxy_gain,
    }
    enabled = all(checks.values())
    return {
        "enabled": enabled,
        "reason": "all_known_validation_safety_checks_pass" if enabled else "known_validation_safety_check_failed",
        "incumbent_macro_f1": incumbent_f1,
        "candidate_macro_f1": candidate_f1,
        "macro_f1_gain": f1_gain,
        "incumbent_error_detection_auroc": incumbent_auc,
        "candidate_error_detection_auroc": candidate_auc,
        "error_detection_auroc_gain": auc_gain,
        "incumbent_error_correct_separation": incumbent_separation,
        "candidate_error_correct_separation": candidate_separation,
        "separation_gain": separation_gain,
        "correct_risk_increase": correct_risk_increase,
        "error_count": error_count,
        "correct_count": correct_count,
        "checks": checks,
    }


def apply_validation_gate(
    *,
    gate: dict[str, object],
    incumbent_probability: np.ndarray,
    candidate_probability: np.ndarray,
    incumbent_risk: np.ndarray,
    candidate_risk: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if gate.get("enabled") is True:
        return (
            np.asarray(candidate_probability, dtype=np.float64),
            np.asarray(candidate_risk, dtype=np.float64),
        )
    return (
        np.asarray(incumbent_probability, dtype=np.float64),
        np.asarray(incumbent_risk, dtype=np.float64),
    )
