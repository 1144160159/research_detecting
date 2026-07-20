from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import numpy as np

from analyze_strict_v4_fusion_operators import (
    edl_evidence_sum,
    reliability_gate,
    standard_ds_fusion,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_fusion_operator_protocol import create_protocol


class FusionOperatorTests(unittest.TestCase):
    def test_edl_sum_is_normalized_and_uniform_for_zero_evidence(self) -> None:
        evidence = np.zeros((3, 2, 4), dtype=np.float64)
        probability = edl_evidence_sum(evidence)
        np.testing.assert_allclose(probability, 0.25)
        np.testing.assert_allclose(probability.sum(axis=1), 1.0)

    def test_reliability_gate_prefers_reliable_view(self) -> None:
        probability = np.asarray([[[0.9, 0.1], [0.1, 0.9]]])
        fused = reliability_gate(probability, np.asarray([[0.9, 0.1]]))
        self.assertGreater(fused[0, 0], fused[0, 1])
        np.testing.assert_allclose(fused.sum(axis=1), 1.0)

    def test_reliability_gate_does_not_pre_normalize_each_view(self) -> None:
        probability = np.asarray([[[0.9, 0.2], [0.1, 0.9]]])
        reliability = np.asarray([[0.8, 0.2]])
        raw_weighted = np.einsum("nm,nmk->nk", reliability, probability)
        expected = raw_weighted / raw_weighted.sum(axis=1, keepdims=True)
        np.testing.assert_allclose(
            reliability_gate(probability, reliability), expected, atol=1e-12
        )

    def test_standard_ds_is_commutative_for_two_views(self) -> None:
        evidence = np.asarray([[[4.0, 1.0], [1.0, 3.0]]])
        forward = standard_ds_fusion(evidence)
        reverse = standard_ds_fusion(evidence[:, ::-1])
        np.testing.assert_allclose(forward, reverse, atol=1e-12)
        np.testing.assert_allclose(forward.sum(axis=1), 1.0)

    def test_protocol_is_zero_result_frozen_and_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "create_strict_v4_fusion_operator_protocol.py",
                "analyze_strict_v4_fusion_operators.py",
                "analyze_strict_v4_attention_fusion.py",
                "scripts/run_strict_v4_fusion_operator_analysis.sh",
            ):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name + "\n", encoding="ascii")
            source = {
                "schema_version": "strict_v4_conflict_metric_protocol_v3",
                "expected_scenarios": 102,
                "source_manifest_sha256": "a" * 64,
            }
            source["manifest_sha256"] = canonical_hash(source)
            protocol = create_protocol(root, source, 0)
            self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
            with self.assertRaisesRegex(ValueError, "zero analyses"):
                create_protocol(root, source, 1)


if __name__ == "__main__":
    unittest.main()
