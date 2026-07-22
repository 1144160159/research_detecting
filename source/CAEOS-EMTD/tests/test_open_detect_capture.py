from __future__ import annotations

import unittest

import numpy as np
import torch

from caeos.open_detect import OpenDetectClassifier
from caeos.open_detect_runtime import OpenDetectRuntime
from capture_opendetect_runtime import same_device_shadow


class OpenDetectCaptureTests(unittest.TestCase):
    def test_same_device_shadow_matches_runtime_exactly_on_cpu(self) -> None:
        torch.manual_seed(17)
        model = OpenDetectClassifier(
            [3, 2],
            4,
            hidden_dim=8,
            latent_dim=5,
            dropout=0.0,
            temperature=1.0,
            generative_weight=0.005,
        )
        checkpoint = {
            "arguments": {
                "model": "opendetect",
                "hidden_dim": 8,
                "embedding_dim": 5,
                "dropout": 0.0,
                "temperature": 1.0,
                "open_detect_generative_weight": 0.005,
            },
            "input_dims": [3, 2],
            "class_names": ["a", "b", "c", "d"],
            "model_state": model.state_dict(),
        }
        views = [
            np.arange(18, dtype=np.float32).reshape(6, 3) / 10.0,
            np.arange(12, dtype=np.float32).reshape(6, 2) / 7.0,
        ]
        shadow = same_device_shadow(checkpoint, views, "cpu")
        runtime = OpenDetectRuntime.from_checkpoint(checkpoint, "cpu")
        observed = runtime.predict(views)
        np.testing.assert_array_equal(observed["prediction"], shadow["prediction"])
        np.testing.assert_array_equal(observed["risk"], shadow["risk"])


if __name__ == "__main__":
    unittest.main()
