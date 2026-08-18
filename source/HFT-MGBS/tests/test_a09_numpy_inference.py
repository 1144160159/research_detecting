import copy
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier

from hft_mgbs.a09_numpy_inference import A09NumpyExactPredictor
from hft_mgbs.gpu_service import A09BundleBackend


class _TestVectorizer:
    def transform(self, rows):
        matrix = np.zeros((len(rows), 11), dtype=np.float32)
        for row_index in range(len(rows)):
            matrix[row_index] = np.arange(11, dtype=np.float32) * 0.1 + row_index
        return matrix


class A09NumpyInferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.RandomState(20260813)
        cls.training_matrix = rng.normal(size=(640, 11)).astype(np.float32)
        cls.training_labels = (
            cls.training_matrix[:, 0]
            + 0.4 * cls.training_matrix[:, 3]
            - 0.2 * cls.training_matrix[:, 7]
            > 0.0
        ).astype(np.int8)
        cls.models = [
            ExtraTreesClassifier(
                n_estimators=37,
                min_samples_leaf=2,
                random_state=seed,
                n_jobs=1,
            ).fit(cls.training_matrix, cls.training_labels)
            for seed in (7, 11, 19)
        ]
        cls.predictor = A09NumpyExactPredictor(cls.models, [1, 1, 1])

    def sklearn_probability(self, matrix):
        return np.mean(
            [model.predict_proba(matrix)[:, 1] for model in self.models], axis=0
        )

    def test_golden_probabilities_are_bit_exact(self):
        matrix = np.asarray(
            [
                [0.0] * 11,
                [1.0, -1.0, 0.5, 0.25, 0.0, 0.0, 0.0, -0.5, 0.0, 0.0, 0.0],
                [-2.0, 1.0, 0.0, -1.5, 0.2, 0.0, 0.1, 0.5, 0.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        )
        expected = self.sklearn_probability(matrix)
        actual = self.predictor.predict_positive_probability(matrix)

        self.assertTrue(np.array_equal(actual, expected))
        self.assertEqual((actual >= 0.5).tolist(), (expected >= 0.5).tolist())

    def test_seeded_random_batches_are_bit_exact(self):
        rng = np.random.RandomState(91)
        for batch_size in (1, 8, 64, 512):
            with self.subTest(batch_size=batch_size):
                matrix = rng.normal(size=(batch_size, 11)).astype(np.float32)
                expected = self.sklearn_probability(matrix)
                actual = self.predictor.predict_positive_probability(matrix)
                self.assertTrue(np.array_equal(actual, expected))

    def test_float64_input_follows_sklearn_float32_conversion(self):
        rng = np.random.RandomState(101)
        matrix = rng.normal(size=(32, 11))
        expected = self.sklearn_probability(matrix.astype(np.float32))
        actual = self.predictor.predict_positive_probability(matrix)
        self.assertTrue(np.array_equal(actual, expected))

    def test_exact_and_adjacent_float32_split_values_are_bit_exact(self):
        tree = self.models[0].estimators_[0].tree_
        node = int(np.flatnonzero(tree.children_left != -1)[0])
        feature = int(tree.feature[node])
        value = np.float32(tree.threshold[node])
        matrix = np.zeros((3, 11), dtype=np.float32)
        matrix[:, feature] = [
            np.nextafter(value, np.float32(-np.inf), dtype=np.float32),
            value,
            np.nextafter(value, np.float32(np.inf), dtype=np.float32),
        ]
        expected = self.sklearn_probability(matrix)
        actual = self.predictor.predict_positive_probability(matrix)
        self.assertTrue(np.array_equal(actual, expected))

    def test_rejects_wrong_member_count_and_positive_class(self):
        with self.assertRaisesRegex(ValueError, "exactly three"):
            A09NumpyExactPredictor(self.models[:2], [1, 1])
        with self.assertRaisesRegex(ValueError, "positive class"):
            A09NumpyExactPredictor(self.models, [0, 1, 1])

    def test_rejects_corrupted_tree_child_index(self):
        corrupted = copy.deepcopy(self.models)
        corrupted[0].estimators_[0].tree_.children_left[0] = 999999
        with self.assertRaisesRegex(ValueError, "child index"):
            A09NumpyExactPredictor(corrupted, [1, 1, 1])

    def test_rejects_wrong_shape_and_nonfinite_input(self):
        with self.assertRaisesRegex(ValueError, "feature count"):
            self.predictor.predict_positive_probability(np.zeros((8, 10)))
        matrix = np.zeros((8, 11), dtype=np.float32)
        matrix[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, "non-finite"):
            self.predictor.predict_positive_probability(matrix)

    def test_compiled_arrays_are_read_only_and_models_remain_unchanged(self):
        original_threshold = self.models[0].estimators_[0].tree_.threshold.copy()
        forest = self.predictor._forests[0]
        self.assertFalse(forest.threshold.flags.writeable)
        with self.assertRaises(ValueError):
            forest.threshold[0, 0] = 123.0
        self.assertTrue(
            np.array_equal(
                self.models[0].estimators_[0].tree_.threshold,
                original_threshold,
            )
        )

    def test_gpu_service_opt_in_matches_default_and_reports_health(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle_path = Path(temporary) / "a09_bundle.joblib"
            joblib.dump(
                {
                    "candidate_id": "A09",
                    "feature_profile": "invariant_no_ports_v1",
                    "vectorizer": _TestVectorizer(),
                    "models": self.models,
                    "thresholds": [0.41, 0.42, 0.43],
                    "positive_indices": [1, 1, 1],
                },
                bundle_path,
            )
            reference = A09BundleBackend(bundle_path, inference_engine="sklearn")
            exact = A09BundleBackend(bundle_path, inference_engine="numpy_exact")
            flows = [
                {"flow_id": str(index), "features": {"flow_packets": index + 1}}
                for index in range(8)
            ]
            expected = reference.predict(flows, ordered_response=True)
            actual = exact.predict(flows, ordered_response=True)

            self.assertEqual(actual, expected)
            self.assertEqual(exact.thresholds, [0.41, 0.42, 0.43])
            self.assertEqual(exact.threshold, 0.42)
            self.assertEqual(exact.health()["inference_engine"], "numpy_exact")
            self.assertEqual(exact.health()["algorithm_device"], "cpu")


if __name__ == "__main__":
    unittest.main()
