from __future__ import annotations

import numpy as np

from evaluate_strict_v4_family_heldout_meta_pilot_v2 import fixed_evaluation


def test_v2_adds_research_contract_without_changing_operational_gate() -> None:
    metrics = {
        "model": {
            "name": "FHMM-CAEOS family-held-out malicious-boundary meta learner"
        },
        "training": {"meta_heldout_loss_weight": 1.0},
        "benign_index": 0,
    }
    arrays = {
        "validation_labels": np.asarray([0] * 100 + [1] * 20),
        "validation_attack_head_attack_probability": np.asarray(
            [0.01] * 100 + [0.99] * 20
        ),
        "validation_open_max": np.linspace(0.0, 1.0, 120),
        "test_attack_head_attack_probability": np.asarray(
            [0.01, 0.99, 0.99, 0.99]
        ),
        "test_open_max": np.asarray([0.01, 0.01, 0.99, 0.99]),
        "test_type_prediction": np.asarray([0, 1, 1, 1]),
        "test_labels": np.asarray([0, 1, -1, -1]),
        "test_unknown": np.asarray([False, False, True, True]),
        "known_class_names": np.asarray(["Benign", "Attack"]),
    }
    result = fixed_evaluation(metrics, arrays)
    assert result["metrics"]["benign_fpr"] == 0.0
    contract = result["research_metric_contract"]
    assert contract["closed_set_known"]["known_macro_f1"] == 1.0
    assert (
        contract["positive_class_convention"]["unknown_detection"]
        == "unknown_is_positive"
    )
    assert contract["calibration"]["available"] is False
