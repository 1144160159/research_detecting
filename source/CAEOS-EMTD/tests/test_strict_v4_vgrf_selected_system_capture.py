from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np


TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is required")
class VGRFSelectedSystemCaptureTests(unittest.TestCase):
    def test_pairwise_frozen_source_equivalence(self) -> None:
        import json

        from run_strict_v4_vgrf_selected_system_capture import (
            source_pairwise_equivalence,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            capture = root / "capture"
            source.mkdir()
            capture.mkdir()
            prediction = np.asarray([0, 1], dtype=np.int64)
            probability = np.asarray(
                [[0.8, 0.2], [0.1, 0.9]], dtype=np.float64
            )
            risk = np.asarray([0.2, 0.9], dtype=np.float64)
            rejected = np.asarray([False, True])
            np.savez_compressed(
                source / "scores.npz", test_prediction=prediction
            )
            np.savez_compressed(
                source / "evidence_package.npz",
                test_final_probability=probability,
                test_selected_risk=risk,
                test_rejected=rejected,
            )
            expected = capture / "expected.npz"
            np.savez_compressed(
                expected,
                closed_set_index=prediction,
                probability=probability,
                risk=risk,
                rejected=rejected,
            )
            (capture / "capture_manifest.json").write_text(
                json.dumps(
                    {
                        "processed_benchmark_expected_outputs": (
                            expected.name
                        )
                    }
                ),
                encoding="utf-8",
            )
            result = source_pairwise_equivalence(source, capture)
        self.assertTrue(result["passes"])

    def test_pairwise_source_difference_fails_closed(self) -> None:
        import json

        from run_strict_v4_vgrf_selected_system_capture import (
            source_pairwise_equivalence,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            capture = root / "capture"
            source.mkdir()
            capture.mkdir()
            np.savez_compressed(
                source / "scores.npz",
                test_prediction=np.asarray([0], dtype=np.int64),
            )
            np.savez_compressed(
                source / "evidence_package.npz",
                test_final_probability=np.asarray([[1.0, 0.0]]),
                test_selected_risk=np.asarray([0.1]),
                test_rejected=np.asarray([False]),
            )
            expected = capture / "expected.npz"
            np.savez_compressed(
                expected,
                closed_set_index=np.asarray([1], dtype=np.int64),
                probability=np.asarray([[1.0, 0.0]]),
                risk=np.asarray([0.1]),
                rejected=np.asarray([False]),
            )
            (capture / "capture_manifest.json").write_text(
                json.dumps(
                    {
                        "processed_benchmark_expected_outputs": (
                            expected.name
                        )
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "differs"):
                source_pairwise_equivalence(source, capture)


if __name__ == "__main__":
    unittest.main()
