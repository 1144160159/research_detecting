from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from audit_strict_v4_conflict_metric_fdr import (
    benjamini_hochberg,
    bootstrap_mean_interval,
)
from create_strict_v4_conflict_fdr_audit_protocol import create_protocol
from create_strict_v4_external_confirmation_protocol import canonical_hash


class ConflictFdrAuditTests(unittest.TestCase):
    def test_benjamini_hochberg_is_monotone_in_rank(self) -> None:
        pvalues = [0.01, 0.04, 0.03, 0.002]
        qvalues = benjamini_hochberg(pvalues)
        ordered = sorted(zip(pvalues, qvalues))
        self.assertEqual([round(value, 3) for value in qvalues], [0.02, 0.04, 0.04, 0.008])
        self.assertTrue(
            all(left[1] <= right[1] for left, right in zip(ordered, ordered[1:]))
        )

    def test_bootstrap_interval_is_reproducible_and_positive(self) -> None:
        first = bootstrap_mean_interval([0.1, 0.2, 0.3], 2000, 7, 0.95)
        second = bootstrap_mean_interval([0.1, 0.2, 0.3], 2000, 7, 0.95)
        self.assertEqual(first, second)
        self.assertGreater(first["lower"], 0)

    def test_protocol_is_bound_and_zero_result_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "create_strict_v4_conflict_fdr_audit_protocol.py",
                "audit_strict_v4_conflict_metric_fdr.py",
                "scripts/run_strict_v4_conflict_fdr_audit.sh",
            ):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name + "\n", encoding="ascii")
            parent = {
                "schema_version": "strict_v4_conflict_metric_protocol_v3",
                "expected_scenarios": 102,
            }
            parent["manifest_sha256"] = canonical_hash(parent)
            protocol = create_protocol(root, parent, 0)
            self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
            self.assertEqual(
                protocol["parent_protocol_manifest_sha256"],
                parent["manifest_sha256"],
            )
            with self.assertRaisesRegex(ValueError, "zero audit"):
                create_protocol(root, parent, 1)


if __name__ == "__main__":
    unittest.main()
