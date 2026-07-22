import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_vos_pilot_protocol import create_gate
from run_strict_v4_vos_matrix import command_for


class VOSProtocolTests(unittest.TestCase):
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
            "epochs": 35,
            "start_epoch": 10,
            "batch_size": 128,
            "hidden_dim": 256,
            "embedding_dim": 128,
            "dropout": 0.1,
            "learning_rate": 0.001,
            "weight_decay": 0.0001,
            "queue_size": 128,
            "sample_from": 1000,
            "select": 1,
            "covariance_ridge": 0.0001,
            "outlier_loss_weight": 0.1,
            "known_acceptance": 0.95,
            "sampling": "natural",
        }
        source = {
            "seed": 7,
            "training_source": {
                "csv": "data.csv",
                "config": "config.json",
                "unknown_classes": "Attack",
                "benign_class": "Benign",
                "split_strategy": "fingerprint_grouped",
                "max_per_class": 5000,
                "chunksize": 100000,
            },
        }
        command = command_for(
            {"frozen_hyperparameters": frozen}, source, Path("out")
        )
        self.assertIn("--sample-from", command)
        self.assertIn("1000", command)
        self.assertNotIn("test", command)

    def test_watcher_freezes_before_wait_and_runs_after_doh(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "wait_and_run_strict_v4_vos_pilot.sh"
        ).read_text(encoding="utf-8")
        self.assertLess(
            script.index("create_strict_v4_vos_pilot_protocol.py"),
            script.index('until [[ -f "$PREREQUISITE" ]]'),
        )
        self.assertLess(
            script.index("doh_temporal_external/execution_complete"),
            script.index("run_strict_v4_vos_matrix.py"),
        )
        self.assertIn("nvidia-smi --query-compute-apps=pid", script)
        self.assertIn("--mlp-root runs/strict_v4_full103_mlp_seed7", script)
        self.assertIn(
            "--comparator-root runs/strict_v4_full103_independent_baselines_seed7",
            script,
        )

    def test_doh_watcher_waits_for_actual_wdiscood_marker(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "wait_and_run_doh_temporal_external.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "runs/strict_v4_wdiscood_pilot_seed7/pilot_complete", script
        )


if __name__ == "__main__":
    unittest.main()
