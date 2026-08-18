from __future__ import annotations

import unittest

from run_strict_v4_fine_binary_warning_development import REQUIRED_ARTIFACTS


class FineBinaryWarningDevelopmentTest(unittest.TestCase):
    def test_binary_completion_requires_effect_and_cuda_artifacts(self) -> None:
        self.assertEqual(
            set(REQUIRED_ARTIFACTS),
            {
                "metrics.json",
                "scores.npz",
                "model.ubj",
                "gpu_execution.json",
                "provenance.json",
            },
        )


if __name__ == "__main__":
    unittest.main()
