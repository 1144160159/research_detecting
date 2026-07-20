import unittest

import numpy as np

from caeos.mandatory_scores import PrototypeDistanceCalibrator, shannon_entropy_risk


class MandatoryScoreTests(unittest.TestCase):
    def test_entropy_matches_uniform_and_confident_limits(self):
        uniform = shannon_entropy_risk(np.zeros((1, 4), dtype=np.float64))[0]
        confident = shannon_entropy_risk(np.array([[20.0, -20.0, -20.0, -20.0]]))[0]
        self.assertAlmostEqual(uniform, np.log(4.0), places=12)
        self.assertLess(confident, 1e-12)

    def test_prototype_centers_and_squared_distance(self):
        embeddings = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 2.0], [0.0, 4.0]])
        labels = np.array([0, 0, 1, 1])
        scorer = PrototypeDistanceCalibrator().fit(embeddings, labels)
        np.testing.assert_allclose(scorer.prototypes_, np.array([[1.0, 0.0], [0.0, 3.0]]))
        np.testing.assert_allclose(scorer.score(np.array([[1.0, 1.0], [0.0, 3.0]])), np.array([1.0, 0.0]))

    def test_prototype_fit_rejects_missing_class_index(self):
        with self.assertRaises(ValueError):
            PrototypeDistanceCalibrator().fit(np.eye(2), np.array([0, 2]))


if __name__ == "__main__":
    unittest.main()
