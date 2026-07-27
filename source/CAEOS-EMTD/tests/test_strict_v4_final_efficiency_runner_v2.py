import tempfile
import unittest
from pathlib import Path

import numpy as np

from run_strict_v4_final_efficiency_v2 import (
    identical_views,
    method_order,
    require_equivalence,
    validate_active_implementation_hashes,
)


class StrictV4FinalEfficiencyRunnerV2Tests(unittest.TestCase):
    def test_method_order_alternates(self) -> None:
        self.assertEqual(method_order(0), ("candidate", "comparator"))
        self.assertEqual(method_order(1), ("comparator", "candidate"))
        self.assertEqual(method_order(2), ("candidate", "comparator"))

    def test_method_order_rejects_negative_repetition(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            method_order(-1)

    def test_identical_views_requires_array_identity(self) -> None:
        left = [np.asarray([[1.0], [2.0]]), np.asarray([[3.0], [4.0]])]
        right = [value.copy() for value in left]
        self.assertTrue(identical_views(left, right))
        right[1][0, 0] = 99.0
        self.assertFalse(identical_views(left, right))

    def test_active_implementation_hashes_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.py"
            path.write_text("stable\n", encoding="utf-8")
            protocol = {"implementation_sha256": {"candidate_pairwise_runtime": "0" * 64}}
            with self.assertRaisesRegex(ValueError, "candidate_pairwise_runtime"):
                validate_active_implementation_hashes(
                    protocol, {"candidate_pairwise_runtime": path}
                )

    def test_cross_device_diagnostic_cannot_enter_formal_runner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "equivalence.json"
            path.write_text(
                "{\n"
                '  "schema_version": "strict_v4_opendetect_runtime_equivalence_v1",\n'
                '  "passes": true,\n'
                '  "prediction_array_equal": true,\n'
                '  "risk_max_absolute_difference": 0.000016,\n'
                '  "absolute_tolerance": 0.00002,\n'
                '  "unknown_or_test_labels_used_for_runtime_fitting_or_selection": false\n'
                "}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "equivalence gate"):
                require_equivalence(
                    Path(directory),
                    "strict_v4_opendetect_runtime_equivalence_v1",
                    required_mode="runtime_vs_uninstrumented_same_device_shadow",
                )

    def test_wrong_equivalence_mode_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "equivalence.json"
            path.write_text(
                "{\n"
                '  "schema_version": "strict_v4_opendetect_runtime_equivalence_v1",\n'
                '  "passes": true,\n'
                '  "prediction_array_equal": true,\n'
                '  "risk_max_absolute_difference": 0.0,\n'
                '  "absolute_tolerance": 1e-12,\n'
                '  "equivalence_mode": "runtime_vs_source_score_archive",\n'
                '  "unknown_or_test_labels_used_for_runtime_fitting_or_selection": false\n'
                "}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "equivalence gate"):
                require_equivalence(
                    Path(directory),
                    "strict_v4_opendetect_runtime_equivalence_v1",
                    required_mode="runtime_vs_uninstrumented_same_device_shadow",
                )


if __name__ == "__main__":
    unittest.main()
