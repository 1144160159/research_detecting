import unittest

import numpy as np

from caeos.nnguide_posthoc import NNGuideCalibrator


class NNGuidePosthocTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(17)
        self.features = rng.normal(size=(20, 4))
        self.logits = rng.normal(loc=0.5, size=(20, 3))

    def test_formula_matches_official_pseudocode(self):
        calibrator = NNGuideCalibrator(bank_ratio=0.5, neighbor_count=3, bank_seed=0)
        calibrator.fit(self.features, self.logits)
        indices = np.arange(20)
        np.random.RandomState(0).shuffle(indices)
        indices = indices[:10]
        bank = self.features[indices]
        bank = bank / np.maximum(np.linalg.norm(bank, axis=1, keepdims=True), 1e-12)
        maximum = self.logits[indices].max(axis=1)
        confidence = maximum + np.log(np.exp(self.logits[indices] - maximum[:, None]).sum(axis=1))
        scaled_bank = bank * confidence[:, None]
        query = self.features[:5] / np.maximum(np.linalg.norm(self.features[:5], axis=1, keepdims=True), 1e-12)
        similarity = query @ scaled_bank.T
        expected = np.sort(similarity, axis=1)[:, -3:].mean(axis=1)
        np.testing.assert_array_equal(calibrator.bank_indices, indices)
        np.testing.assert_allclose(calibrator.scaled_bank, scaled_bank)
        np.testing.assert_allclose(calibrator.guidance(self.features[:5]), expected)

    def test_guided_risk_and_prediction(self):
        calibrator = NNGuideCalibrator(bank_ratio=0.5, neighbor_count=3, bank_seed=0)
        calibrator.fit(self.features, self.logits)
        output = calibrator.evaluate(self.features[:5], self.logits[:5])
        np.testing.assert_array_equal(output["prediction"], self.logits[:5].argmax(axis=1))
        np.testing.assert_allclose(output["guided_confidence"], output["base_confidence"] * output["guidance"])
        np.testing.assert_allclose(output["risk"], -output["guided_confidence"])

    def test_minimum_bank_adapter_preserves_topk_definition(self):
        calibrator = NNGuideCalibrator(bank_ratio=0.1, neighbor_count=5, bank_seed=0)
        calibrator.fit(self.features, self.logits)
        self.assertEqual(len(calibrator.bank_indices), 5)
        self.assertTrue(calibrator.evidence()["adaptation"]["minimum_bank_adapter_used"])


if __name__ == "__main__":
    unittest.main()
