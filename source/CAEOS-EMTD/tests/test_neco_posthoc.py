import unittest

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from caeos.neco_posthoc import NECOID90Calibrator


class NECOPosthocTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(37)
        self.train = rng.normal(size=(50, 8)) * np.arange(1, 9)
        self.features = rng.normal(size=(9, 8)) * np.arange(1, 9)
        self.logits = rng.normal(size=(9, 4))

    def test_matches_official_scaler_pca_ratio_with_id90_dimension(self):
        scaler = StandardScaler().fit(self.train)
        standardized = scaler.transform(self.train)
        pca = PCA().fit(standardized)
        dimension = int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_), 0.90) + 1)
        expected_values = scaler.transform(self.features)
        expected_projection = expected_values @ pca.components_[:dimension].T
        expected = np.linalg.norm(expected_projection, axis=1) / np.linalg.norm(expected_values, axis=1)
        calibrator = NECOID90Calibrator()
        calibrator.fit(self.train)
        output = calibrator.evaluate(self.features, self.logits)
        self.assertEqual(calibrator.evidence()["selected_dimension"], dimension)
        np.testing.assert_allclose(output["confidence"], expected, rtol=1e-10, atol=1e-12)

    def test_prediction_is_unmodified(self):
        calibrator = NECOID90Calibrator()
        calibrator.fit(self.train)
        output = calibrator.evaluate(self.features, self.logits)
        np.testing.assert_array_equal(output["prediction"], self.logits.argmax(axis=1))

    def test_constant_dimension_uses_standard_scaler_adapter(self):
        train = self.train.copy()
        train[:, 0] = 3.0
        features = self.features.copy()
        features[:, 0] = 3.0
        calibrator = NECOID90Calibrator()
        calibrator.fit(train)
        self.assertEqual(calibrator.evidence()["zero_scale_dimension_count"], 1)
        self.assertTrue(np.isfinite(calibrator.evaluate(features, self.logits)["risk"]).all())


if __name__ == "__main__":
    unittest.main()
