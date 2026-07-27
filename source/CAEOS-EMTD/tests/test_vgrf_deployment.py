from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from caeos.pairwise_deployment import PairwiseDeploymentBundle
from caeos.vgrf_deployment import VGRFDeploymentBundle


class DummyEvidenceModel:
    def predict_with_evidence(self, views):
        first = np.asarray(views[0], dtype=np.float64)[:, 0]
        second = np.asarray(views[1], dtype=np.float64)[:, 0]
        first_attack = 1.0 / (1.0 + np.exp(-first))
        second_attack = 1.0 / (1.0 + np.exp(-second))
        view_probability = np.stack(
            [
                np.column_stack([1.0 - first_attack, first_attack]),
                np.column_stack([1.0 - second_attack, second_attack]),
            ],
            axis=1,
        )
        global_probability = view_probability.mean(axis=1)
        view_fused_probability = (
            0.7 * view_probability[:, 0] + 0.3 * view_probability[:, 1]
        )
        gate = np.full(len(first), 0.5, dtype=np.float64)
        final_probability = (
            (1.0 - gate[:, None]) * global_probability
            + gate[:, None] * view_fused_probability
        )
        return {
            "view_probability": view_probability,
            "global_probability": global_probability,
            "view_fused_probability": view_fused_probability,
            "gate": gate,
            "final_probability": final_probability,
        }


class DummyVGRFRuntime:
    def __init__(self):
        self.model = DummyEvidenceModel()

    def _model_inputs(self, views):
        arrays = [np.asarray(view) for view in views]
        joined = np.concatenate(arrays, axis=1)
        return arrays, joined, joined

    def predict(self, views):
        evidence = self.model.predict_with_evidence(views)
        probability = evidence["final_probability"]
        risk = 1.0 - probability.max(axis=1)
        return {
            "prediction": probability.argmax(axis=1),
            "probability": probability,
            "risk": risk,
        }

    def evidence(self):
        return {
            "contains_training_or_test_labels": False,
            "contains_test_ground_truth": False,
        }


def make_pairwise() -> PairwiseDeploymentBundle:
    return PairwiseDeploymentBundle(
        runtime=DummyVGRFRuntime(),
        modality_names=("flow", "time"),
        modalities={"flow": ("a",), "time": ("b",)},
        processor_states={
            "flow": {"median": [0.0], "mean": [0.0], "std": [1.0]},
            "time": {"median": [0.0], "mean": [0.0], "std": [1.0]},
        },
        class_names=("Benign", "Attack"),
        benign_index=0,
        selected_threshold=0.5,
        risk_policy_name="dummy_pairwise",
        source_config_sha256="a" * 64,
    )


def make_vgrf(enabled: bool = True) -> VGRFDeploymentBundle:
    return VGRFDeploymentBundle(
        pairwise=make_pairwise(),
        class_reliability=np.asarray([[0.95, 0.40], [0.40, 0.95]]),
        validation_gate={"enabled": enabled, "reason": "unit_test"},
        selected_threshold=0.4,
        risk_blend=0.25,
        source_protocol_manifest_sha256="b" * 64,
    )


class VGRFDeploymentTests(unittest.TestCase):
    def test_enabled_gate_returns_finite_outputs(self) -> None:
        bundle = make_vgrf(True)
        output = bundle.predict_frame(
            pd.DataFrame({"a": [-2.0, 2.0], "b": [1.0, -1.0]})
        )
        self.assertEqual(output["probability"].shape, (2, 2))
        self.assertTrue(np.isfinite(output["probability"]).all())
        self.assertTrue(np.isfinite(output["risk"]).all())
        self.assertEqual(output["modality_quality"].shape, (2, 2))

    def test_disabled_gate_is_exact_pairwise_fallback(self) -> None:
        bundle = make_vgrf(False)
        views = [
            np.asarray([[-2.0], [2.0]], dtype=np.float32),
            np.asarray([[1.0], [-1.0]], dtype=np.float32),
        ]
        expected = bundle.pairwise.runtime.predict(views)
        actual = bundle.predict_views(views)
        np.testing.assert_array_equal(
            actual["probability"], expected["probability"]
        )
        np.testing.assert_array_equal(actual["risk"], expected["risk"])

    def test_invalid_reliability_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "class reliability"):
            VGRFDeploymentBundle(
                pairwise=make_pairwise(),
                class_reliability=np.asarray([[0.5, 0.5]]),
                validation_gate={"enabled": True},
                selected_threshold=0.5,
                risk_blend=0.25,
                source_protocol_manifest_sha256="b" * 64,
            )

    def test_serialization_roundtrip_is_exact(self) -> None:
        bundle = make_vgrf(True)
        views = [
            np.asarray([[-2.0], [2.0]], dtype=np.float32),
            np.asarray([[1.0], [-1.0]], dtype=np.float32),
        ]
        expected = bundle.predict_views(views)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "vgrf.joblib"
            joblib.dump(bundle, path)
            actual = joblib.load(path).predict_views(views)
        for name in (
            "closed_set_index",
            "probability",
            "risk",
            "rejected",
        ):
            np.testing.assert_array_equal(actual[name], expected[name])

    def test_evidence_discloses_validation_aggregates(self) -> None:
        evidence = make_vgrf().evidence()
        self.assertTrue(
            evidence["contains_known_validation_aggregate_statistics"]
        )
        self.assertFalse(evidence["contains_validation_labels"])
        self.assertFalse(evidence["contains_test_labels"])
        self.assertEqual(evidence["storage_policy"], "gpu_private_do_not_publish")


if __name__ == "__main__":
    unittest.main()
