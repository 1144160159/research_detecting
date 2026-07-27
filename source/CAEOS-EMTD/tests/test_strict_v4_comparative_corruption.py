import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from evaluate_strict_v4_comparative_corruption import degradation, risk_ece
from create_strict_v4_comparative_corruption_protocol import (
    candidate_selection_is_label_free,
)
from create_strict_v4_comparative_corruption_protocol_v2 import (
    create_protocol_v2,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_comparative_corruption import provenance_arguments
from summarize_strict_v4_comparative_corruption import holm_adjust


ROOT = Path(__file__).resolve().parents[1]


class ComparativeCorruptionTests(unittest.TestCase):
    def test_v2_schema_revision_requires_zero_paired_results(self) -> None:
        v1 = {
            "schema_version": (
                "strict_v4_comparative_corruption_protocol_v1"
            ),
            "implementation_sha256": {
                "evaluator": "1" * 64,
                "runner": "2" * 64,
                "summarizer": "3" * 64,
            },
            "source_registry": [],
            "corruption_conditions": {"families": []},
            "seeds": [137, 139, 149],
        }
        v1["manifest_sha256"] = canonical_hash(v1)
        with self.assertRaisesRegex(ValueError, "zero paired"):
            create_protocol_v2(
                v1,
                v1_file_sha256="0" * 64,
                evaluator_sha256="4" * 64,
                runner_sha256="5" * 64,
                summarizer_sha256="6" * 64,
                revision_creator_sha256="7" * 64,
                failed_evaluation_log_sha256="8" * 64,
                paired_results_observed_at_revision=1,
                runtime_capture_pairs_observed_at_revision=1,
            )

    def test_evaluator_uses_public_is_unknown_dataset_field(self) -> None:
        source = (
            ROOT / "evaluate_strict_v4_comparative_corruption.py"
        ).read_text(encoding="utf-8")
        self.assertIn("bundle.test.is_unknown.numpy()", source)
        self.assertNotIn("bundle.test.unknown.numpy()", source)

    def test_fixed_risk_branch_uses_overall_selection_leakage_audit(self) -> None:
        metrics = {
            "selected_risk": "cauchy_modality_support_union",
            "risk_selection_details": {
                "unknown_or_test_labels_used_for_selection": False,
                "pseudo_unknown_learned_blend": {
                    "unknown_or_test_labels_used": False
                },
            },
        }
        self.assertTrue(candidate_selection_is_label_free(metrics))
        metrics["risk_selection_details"][
            "unknown_or_test_labels_used_for_selection"
        ] = True
        self.assertFalse(candidate_selection_is_label_free(metrics))

    def test_risk_ece_and_degradation_orientation(self) -> None:
        self.assertEqual(
            risk_ece(
                np.asarray([0.0, 0.0, 1.0, 1.0]),
                np.asarray([False, False, True, True]),
            ),
            0.0,
        )
        clean = {"unknown_auroc": 0.9, "unknown_fpr95": 0.2, "ece": 0.1}
        corrupt = {"unknown_auroc": 0.8, "unknown_fpr95": 0.3, "ece": 0.15}
        self.assertAlmostEqual(degradation(clean, corrupt, "unknown_auroc"), 0.1)
        self.assertAlmostEqual(degradation(clean, corrupt, "unknown_fpr95"), 0.1)
        self.assertAlmostEqual(degradation(clean, corrupt, "ece"), 0.05)

    def test_holm_adjustment_is_monotone_in_sorted_order(self) -> None:
        adjusted = holm_adjust({"a": 0.001, "b": 0.01, "c": 0.04})
        self.assertAlmostEqual(adjusted["a"], 0.003)
        self.assertAlmostEqual(adjusted["b"], 0.02)
        self.assertAlmostEqual(adjusted["c"], 0.04)

    def test_candidate_provenance_is_identity_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "provenance.json"
            path.write_text(
                json.dumps(
                    {
                        "task": {"suite": "suite", "scenario": "attack", "seed": 137},
                        "command": ["python", "train_hybrid_open_set.py", "--seed", "137"],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                provenance_arguments(path, "suite", "attack", 137),
                ["--seed", "137"],
            )
            with self.assertRaisesRegex(ValueError, "identity"):
                provenance_arguments(path, "suite", "attack", 139)

    def test_serial_chain_places_comparative_corruption_before_final_audit(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_prepare_strict_v4_final_efficiency_seed191_caches.sh"
        ).read_text(encoding="utf-8")
        candidate = text.index("summarize_strict_v4_postselection_corruption.py")
        comparative = text.index("run_strict_v4_comparative_corruption.py")
        final_audit = text.index("audit_strict_v4_final_paper_readiness.py")
        self.assertLess(candidate, comparative)
        self.assertLess(comparative, final_audit)
        self.assertIn("--comparative-corruption-summary", text)
        active_chain = (
            ROOT
            / "scripts"
            / "wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "strict_v4_comparative_corruption_protocol_v2",
            active_chain,
        )

    def test_cross_device_archival_metrics_are_diagnostic_only(self) -> None:
        source = (ROOT / "evaluate_strict_v4_comparative_corruption.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("degradation_uses_same_device_runtime_clean_anchors", source)
        self.assertIn(
            "archival_clean_metric_absolute_differences_diagnostic_only", source
        )
        self.assertNotIn("require_clean_equivalence", source)


if __name__ == "__main__":
    unittest.main()
