import unittest

import numpy as np

from caeos.foss import FOSSForest, FOSSTree


class FOSSTest(unittest.TestCase):
    def test_weighted_entropy_prefers_finite_variable_dimension(self):
        constant = FOSSTree._weighted_entropy(np.ones(10))
        variable = FOSSTree._weighted_entropy(np.arange(10, dtype=np.float64))
        self.assertTrue(np.isinf(constant))
        self.assertTrue(np.isfinite(variable))

    def test_forest_predicts_finite_risk_and_known_class(self):
        rng = np.random.RandomState(7)
        first = rng.normal(loc=-2.0, scale=0.15, size=(80, 3))
        second = rng.normal(loc=2.0, scale=0.15, size=(80, 3))
        values = np.vstack([first, second])
        labels = np.asarray([0] * len(first) + [1] * len(second))
        model = FOSSForest(num_trees=20, subsample_size=60, seed=7)
        model.fit(values, labels)

        query = np.vstack([first[:5], second[:5], np.full((2, 3), 9.0)])
        prediction, risk, probability = model.predict(query)
        self.assertEqual(prediction.shape, (12,))
        self.assertEqual(probability.shape, (12, 2))
        self.assertTrue(np.isfinite(risk).all())
        self.assertTrue(np.all((risk >= 0.0) & (risk <= 1.0)))
        self.assertGreater(float(risk[-2:].mean()), float(risk[:10].mean()))

    def test_constant_features_do_not_crash(self):
        values = np.ones((20, 4), dtype=np.float64)
        labels = np.asarray([0] * 10 + [1] * 10)
        model = FOSSForest(num_trees=3, subsample_size=10, seed=11)
        model.fit(values, labels)
        prediction, risk, _ = model.predict(values[:3])
        self.assertEqual(prediction.shape, (3,))
        self.assertTrue(np.isfinite(risk).all())

    def test_structural_transform_is_finite_and_retains_tree_coordinates(self):
        values = np.concatenate(
            [np.linspace(0.0, 0.2, 20), np.linspace(1.0, 1.2, 20)]
        ).reshape(-1, 1)
        labels = np.asarray([0] * 20 + [1] * 20, dtype=np.int64)
        model = FOSSForest(
            num_trees=8, subsample_size=30, min_samples=5, seed=13
        )
        model.fit(values, labels)
        transformed = model.transform(np.asarray([[0.05], [5.0]]))
        self.assertEqual(transformed.shape, (2, 2 * 8 + 1))
        self.assertTrue(np.isfinite(transformed).all())
        near_cloud = transformed[0, 1:-1:2].mean()
        far_cloud = transformed[1, 1:-1:2].mean()
        self.assertGreater(far_cloud, near_cloud)
        aggregated = model.transform_aggregated(np.asarray([[0.05], [5.0]]))
        self.assertEqual(aggregated.shape, (2, 8))
        self.assertTrue(np.isfinite(aggregated).all())
        self.assertGreater(aggregated[1, 4], aggregated[0, 4])


if __name__ == "__main__":
    unittest.main()
