from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import numpy as np

from analyze_strict_v4_attention_fusion import (
    attention_fusion,
    evaluate,
    fit_attention,
)
from create_strict_v4_attention_fusion_protocol import create_protocol
from create_strict_v4_external_confirmation_protocol import canonical_hash


class AttentionFusionTests(unittest.TestCase):
    def test_attention_weights_are_normalized(self) -> None:
        probability = np.asarray(
            [
                [[0.9, 0.1], [0.5, 0.5]],
                [[0.2, 0.8], [0.6, 0.4]],
            ]
        )
        fused, weights = attention_fusion(probability, np.asarray([0.2, -0.2, 1.0]))
        np.testing.assert_allclose(weights.sum(axis=1), 1.0)
        np.testing.assert_allclose(fused.sum(axis=1), 1.0)

    def test_fit_attention_improves_validation_nll(self) -> None:
        labels = np.asarray([0, 1] * 50)
        strong = np.stack([1 - 0.9 * labels, 0.1 + 0.8 * labels], axis=1)
        weak = np.full_like(strong, 0.5, dtype=np.float64)
        probability = np.stack([strong, weak], axis=1)
        result = fit_attention(probability, labels)
        self.assertLess(result["validation_nll"], result["uniform_validation_nll"])
        self.assertGreater(result["mean_validation_weights"][0], 0.5)

    def test_evaluate_rewards_separated_unknown_risk(self) -> None:
        probability = np.asarray(
            [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5], [0.52, 0.48]]
        )
        labels = np.asarray([0, 1, -1, -1])
        unknown = np.asarray([False, False, True, True])
        result = evaluate(probability, labels, unknown)
        self.assertEqual(result["known_macro_f1"], 1.0)
        self.assertEqual(result["unknown_auroc"], 1.0)

    def test_protocol_is_zero_result_frozen_and_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "create_strict_v4_attention_fusion_protocol.py",
                "analyze_strict_v4_attention_fusion.py",
                "scripts/run_strict_v4_attention_fusion_analysis.sh",
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
            self.assertEqual(
                protocol["source_protocol_manifest_sha256"],
                source["manifest_sha256"],
            )
            with self.assertRaisesRegex(ValueError, "zero analyses"):
                create_protocol(root, source, 1)


if __name__ == "__main__":
    unittest.main()
