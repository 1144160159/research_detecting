import argparse
import json

import numpy as np

from evaluate_validation_gated_reliability_fusion import evaluate
from caeos.validation_gated_reliability_fusion import (
    apply_validation_gate,
    validation_safety_gate,
)


def test_gate_enables_when_all_known_proxies_improve():
    labels = np.array([0, 0, 0, 1, 1, 1])
    incumbent_probability = np.array([
        [0.9, 0.1], [0.8, 0.2], [0.4, 0.6], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]
    ])
    candidate_probability = incumbent_probability.copy()
    incumbent_risk = np.array([0.1, 0.2, 0.3, 0.1, 0.2, 0.3])
    candidate_risk = np.array([0.05, 0.1, 0.9, 0.05, 0.1, 0.9])
    gate = validation_safety_gate(
        labels=labels, incumbent_probability=incumbent_probability,
        candidate_probability=candidate_probability, incumbent_risk=incumbent_risk,
        candidate_risk=candidate_risk,
    )
    assert gate["enabled"] is True


def test_gate_falls_back_on_known_proxy_regression():
    labels = np.array([0, 0, 1, 1])
    incumbent_probability = np.array([[0.9, 0.1], [0.4, 0.6], [0.1, 0.9], [0.6, 0.4]])
    candidate_probability = incumbent_probability.copy()
    incumbent_risk = np.array([0.1, 0.8, 0.1, 0.8])
    candidate_risk = np.array([0.9, 0.1, 0.9, 0.1])
    gate = validation_safety_gate(
        labels=labels, incumbent_probability=incumbent_probability,
        candidate_probability=candidate_probability, incumbent_risk=incumbent_risk,
        candidate_risk=candidate_risk,
    )
    assert gate["enabled"] is False
    probability, risk = apply_validation_gate(
        gate=gate, incumbent_probability=incumbent_probability,
        candidate_probability=candidate_probability[:, ::-1], incumbent_risk=incumbent_risk,
        candidate_risk=candidate_risk,
    )
    assert np.array_equal(probability, incumbent_probability)
    assert np.array_equal(risk, incumbent_risk)


def test_degenerate_error_target_fails_closed():
    labels = np.array([0, 1])
    probability = np.array([[0.9, 0.1], [0.1, 0.9]])
    risk = np.array([0.1, 0.2])
    gate = validation_safety_gate(
        labels=labels, incumbent_probability=probability,
        candidate_probability=probability, incumbent_risk=risk, candidate_risk=risk,
    )
    assert gate["enabled"] is False
    assert "degenerate" in gate["reason"]


def test_test_label_and_unknown_perturbation_cannot_change_selection(tmp_path):
    validation_labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    validation_probability = np.array([
        [0.90, 0.10], [0.80, 0.20], [0.40, 0.60], [0.70, 0.30],
        [0.10, 0.90], [0.20, 0.80], [0.60, 0.40], [0.30, 0.70],
    ])
    test_probability = np.array([
        [0.85, 0.15], [0.65, 0.35], [0.25, 0.75], [0.45, 0.55],
        [0.75, 0.25], [0.35, 0.65], [0.55, 0.45], [0.15, 0.85],
    ])

    def view_stack(probability):
        softened = 0.8 * probability + 0.1
        sharpened = probability**2
        sharpened /= sharpened.sum(axis=1, keepdims=True)
        return np.stack([softened, sharpened], axis=1)

    evidence_path = tmp_path / "evidence.npz"
    np.savez_compressed(
        evidence_path,
        validation_view_probability=view_stack(validation_probability),
        validation_global_probability=validation_probability,
        validation_view_fused_probability=validation_probability,
        validation_gate=np.full(len(validation_probability), 0.5),
        validation_final_probability=validation_probability,
        validation_selected_risk=np.array(
            [0.10, 0.20, 0.65, 0.15, 0.10, 0.20, 0.70, 0.15]
        ),
        test_view_probability=view_stack(test_probability),
        test_global_probability=test_probability,
        test_view_fused_probability=test_probability,
        test_gate=np.full(len(test_probability), 0.5),
        test_final_probability=test_probability,
        test_selected_risk=np.array(
            [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
        ),
    )
    score_variants = (
        (
            np.array([0, 0, 1, 1, 0, 1, 0, 1]),
            np.array([False, False, False, False, True, True, True, True]),
        ),
        (
            np.array([1, 1, 0, 0, 1, 0, 1, 0]),
            np.array([True, False, True, False, False, True, False, True]),
        ),
    )
    outputs = []
    for index, (test_labels, test_unknown) in enumerate(score_variants):
        scores_path = tmp_path / f"scores_{index}.npz"
        output_dir = tmp_path / f"output_{index}"
        np.savez_compressed(
            scores_path,
            validation_labels=validation_labels,
            test_labels=test_labels,
            test_unknown=test_unknown,
            test_prediction=test_probability.argmax(axis=1),
        )
        result = evaluate(
            argparse.Namespace(
                evidence_package=evidence_path,
                scores=scores_path,
                output_dir=output_dir,
                protocol_manifest_sha256="synthetic-invariance-test",
                suite="synthetic",
                scenario="test-label-perturbation",
                seed=307,
                shrinkage=20.0,
                minimum_reliability=0.05,
                risk_blend=0.25,
                known_rejection_quantile=0.95,
                minimum_f1_gain=-0.002,
                maximum_correct_risk_increase=0.01,
                minimum_auc_gain=0.0,
                minimum_separation_gain=0.0,
                minimum_strict_proxy_gain=0.005,
            )
        )
        with np.load(output_dir / "scores.npz", allow_pickle=False) as selected:
            outputs.append(
                {
                    "gate": result["validation_gate"],
                    "thresholds": result["thresholds"],
                    "gate_enabled": selected["validation_gate_enabled"].copy(),
                    "validation_risk": selected["validation_selected_risk"].copy(),
                    "test_risk": selected["test_selected_risk"].copy(),
                    "test_prediction": selected["test_selected_prediction"].copy(),
                    "stored_test_labels": selected["test_labels"].copy(),
                    "stored_test_unknown": selected["test_unknown"].copy(),
                }
            )

    assert json.dumps(outputs[0]["gate"], sort_keys=True) == json.dumps(
        outputs[1]["gate"], sort_keys=True
    )
    assert outputs[0]["thresholds"] == outputs[1]["thresholds"]
    for key in (
        "gate_enabled",
        "validation_risk",
        "test_risk",
        "test_prediction",
    ):
        assert np.array_equal(outputs[0][key], outputs[1][key])
    assert not np.array_equal(
        outputs[0]["stored_test_labels"], outputs[1]["stored_test_labels"]
    )
    assert not np.array_equal(
        outputs[0]["stored_test_unknown"], outputs[1]["stored_test_unknown"]
    )


if __name__ == "__main__":
    tests = [
        test_gate_enables_when_all_known_proxies_improve,
        test_gate_falls_back_on_known_proxy_regression,
        test_degenerate_error_target_fails_closed,
    ]
    for test in tests:
        test()
    print(f"{len(tests)}/{len(tests)} PASS")
