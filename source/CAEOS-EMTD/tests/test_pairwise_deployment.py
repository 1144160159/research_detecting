from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from caeos.pairwise_deployment import (
    UNKNOWN_CLASS_NAME,
    PairwiseDeploymentBundle,
    feature_schema_hash,
)


class DummyRuntime:
    def predict(self, views):
        joined = np.concatenate(views, axis=1)
        score = joined.sum(axis=1)
        probability = np.column_stack(
            [1.0 / (1.0 + np.exp(score)), 1.0 / (1.0 + np.exp(-score))]
        )
        return {
            "prediction": probability.argmax(axis=1),
            "probability": probability,
            "risk": np.abs(score),
        }

    def evidence(self):
        return {
            "contains_training_or_test_labels": False,
            "contains_test_ground_truth": False,
        }


def make_bundle(threshold: float = 2.0) -> PairwiseDeploymentBundle:
    modalities = {"flow": ("a", "b"), "time": ("c",)}
    processor_states = {
        "flow": {
            "median": [1.0, 2.0],
            "mean": [1.0, 2.0],
            "std": [1.0, 2.0],
        },
        "time": {
            "median": [3.0],
            "mean": [3.0],
            "std": [1.0],
        },
    }
    return PairwiseDeploymentBundle(
        runtime=DummyRuntime(),
        modality_names=("flow", "time"),
        modalities=modalities,
        processor_states=processor_states,
        class_names=("Benign", "Attack"),
        benign_index=0,
        selected_threshold=threshold,
        risk_policy_name="test_pairwise_v1",
        source_config_sha256="a" * 64,
    )


class PairwiseDeploymentTests(unittest.TestCase):
    def test_schema_hash_is_order_sensitive(self) -> None:
        modalities = {"flow": ("a", "b"), "time": ("c",)}
        first = feature_schema_hash(("flow", "time"), modalities)
        second = feature_schema_hash(("time", "flow"), modalities)
        self.assertNotEqual(first, second)

    def test_raw_frame_transform_and_rejection(self) -> None:
        bundle = make_bundle(threshold=2.0)
        frame = pd.DataFrame(
            {
                "a": [1.0, 5.0],
                "b": [2.0, 2.0],
                "c": [3.0, 3.0],
                "ignored_metadata": ["x", "y"],
            }
        )
        output = bundle.predict_frame(frame)
        np.testing.assert_array_equal(output["rejected"], [False, True])
        np.testing.assert_array_equal(output["open_set_index"], [0, -1])
        np.testing.assert_array_equal(
            output["open_set_name"], ["Benign", UNKNOWN_CLASS_NAME]
        )
        self.assertEqual(output["modality_quality"].shape, (2, 2))

    def test_non_numeric_values_use_frozen_training_median(self) -> None:
        bundle = make_bundle()
        frame = pd.DataFrame({"a": ["bad"], "b": [2.0], "c": [np.nan]})
        views, quality = bundle.transform_frame(frame)
        np.testing.assert_array_equal(views[0], [[0.0, 0.0]])
        np.testing.assert_array_equal(views[1], [[0.0]])
        np.testing.assert_array_equal(quality, [[0.5, 0.0]])

    def test_missing_feature_fails_closed(self) -> None:
        bundle = make_bundle()
        with self.assertRaisesRegex(ValueError, "missing columns"):
            bundle.predict_frame(pd.DataFrame({"a": [1.0], "b": [2.0]}))

    def test_invalid_processor_state_fails_closed(self) -> None:
        bundle = make_bundle()
        state = bundle.processor_states.copy()
        state["flow"] = dict(state["flow"])
        state["flow"]["std"] = [1.0, 0.0]
        with self.assertRaisesRegex(ValueError, "std must be positive"):
            PairwiseDeploymentBundle(
                runtime=DummyRuntime(),
                modality_names=bundle.modality_names,
                modalities=bundle.modalities,
                processor_states=state,
                class_names=bundle.class_names,
                benign_index=bundle.benign_index,
                selected_threshold=bundle.selected_threshold,
                risk_policy_name=bundle.risk_policy_name,
                source_config_sha256=bundle.source_config_sha256,
            )

    def test_serialization_roundtrip_is_exact(self) -> None:
        bundle = make_bundle()
        frame = pd.DataFrame({"a": [1.0], "b": [2.0], "c": [3.0]})
        expected = bundle.predict_frame(frame)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.joblib"
            joblib.dump(bundle, path)
            restored = joblib.load(path)
            actual = restored.predict_frame(frame)
        for name in (
            "closed_set_index",
            "open_set_index",
            "open_set_name",
            "probability",
            "risk",
            "rejected",
            "modality_quality",
        ):
            np.testing.assert_array_equal(actual[name], expected[name])

    def test_evidence_discloses_fitted_reference_state(self) -> None:
        evidence = make_bundle().evidence()
        self.assertFalse(evidence["contains_raw_input_rows"])
        self.assertTrue(
            evidence["contains_fitted_nonparametric_reference_vectors"]
        )
        self.assertTrue(evidence["contains_fitted_class_conditional_state"])
        self.assertFalse(evidence["contains_validation_labels"])
        self.assertFalse(evidence["contains_test_labels"])
        self.assertEqual(evidence["storage_policy"], "gpu_private_do_not_publish")
        self.assertFalse(
            evidence[
                "unknown_or_test_labels_used_for_preprocessing_selection_or_threshold"
            ]
        )


if __name__ == "__main__":
    unittest.main()
