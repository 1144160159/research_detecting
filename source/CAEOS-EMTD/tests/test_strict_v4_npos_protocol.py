import unittest
from pathlib import Path

from create_strict_v4_npos_pilot_protocol import create_gate
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_npos_matrix import command_for
from summarize_strict_v4_npos_full102 import rerank


class NPOSProtocolTests(unittest.TestCase):
    def test_gate_is_frozen_before_results(self) -> None:
        protocol = {
            "manifest_sha256": "placeholder",
            "pilot_metrics_observed_at_freeze": 0,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol)
        self.assertEqual(gate["pilot_metrics_observed_at_freeze"], 0)
        self.assertIn("full102", gate["pass_action"])
        self.assertTrue(gate["test_labels_used_for_development_gate"])

    def test_runner_command_uses_only_frozen_hyperparameters(self) -> None:
        frozen = {
            "epochs": 35, "start_epoch": 10, "batch_size": 128,
            "hidden_dim": 256, "embedding_dim": 128, "dropout": 0.1,
            "learning_rate": 0.001, "weight_decay": 0.0001,
            "queue_size": 128, "minimum_queue": 20,
            "synthesis_neighbors": 20, "boundary_count": 20,
            "noise_count": 64, "outliers_per_class": 2,
            "covariance_scale": 0.1, "outlier_loss_weight": 0.1,
            "evaluation_neighbors": 100, "known_acceptance": 0.95,
            "sampling": "natural",
        }
        source = {
            "seed": 7,
            "training_source": {
                "csv": "data.csv", "config": "config.json",
                "unknown_classes": "Attack", "benign_class": "Benign",
                "split_strategy": "fingerprint_grouped", "max_per_class": 5000,
                "chunksize": 100000,
            },
        }
        command = command_for({"frozen_hyperparameters": frozen}, source, __import__("pathlib").Path("out"))
        self.assertIn("--evaluation-neighbors", command)
        self.assertIn("100", command)
        self.assertNotIn("test", command)

    def test_extension_waits_for_current_final_audit_and_respects_gate(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "wait_and_run_strict_v4_npos_extension.sh"
        ).read_text(encoding="utf-8")
        self.assertLess(
            script.index("strict_v4_final_paper_readiness/audit_complete"),
            script.index("run_strict_v4_npos_matrix.py"),
        )
        self.assertLess(
            script.index("expand_to_full102"),
            script.index("create_strict_v4_npos_full102_protocol.py"),
        )
        self.assertIn("nvidia-smi --query-compute-apps=pid", script)

    def test_full102_ranking_orients_fpr95_downward(self) -> None:
        records = [
            {"method": "a", "unknown_auroc": 0.8, "unknown_aupr": 0.8, "unknown_fpr95": 0.2, "oscr": 0.8},
            {"method": "b", "unknown_auroc": 0.7, "unknown_aupr": 0.7, "unknown_fpr95": 0.4, "oscr": 0.7},
        ]
        ranked = rerank(records)
        self.assertEqual(ranked[0]["method"], "a")
        self.assertEqual(ranked[0]["metric_ranks"]["unknown_fpr95"], 1.0)


if __name__ == "__main__":
    unittest.main()
