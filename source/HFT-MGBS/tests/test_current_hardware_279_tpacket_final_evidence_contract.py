import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_final_evidence.sh"
CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_final_evidence_contract.json"
RUST_BIN = ROOT / "rust" / "hft-capture" / "src" / "bin" / "tpacket_v3_full_pipeline.rs"
METRICS = ROOT / "rust" / "hft-capture" / "src" / "metrics.rs"
FLOW = ROOT / "rust" / "hft-capture" / "src" / "flow.rs"


class CurrentHardware279FinalEvidenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = RUNNER.read_text(encoding="utf-8")
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.rust_bin = RUST_BIN.read_text(encoding="utf-8")
        cls.metrics = METRICS.read_text(encoding="utf-8")
        cls.flow = FLOW.read_text(encoding="utf-8")

    def test_candidate_and_formal_binary_are_single_frozen_identity(self):
        candidate = "TPACKET_QM_FIXED64_GROUP512_A09_FINAL_EVIDENCE_CONTRACT"
        binary = "9c4e6cfab251b1d595dc9366f77752f8c333f9e2b2fd1092f2f1ebc7aa557255"
        self.assertEqual(self.config["candidate_id"], candidate)
        self.assertEqual(self.config["pipeline"]["binary_sha256"], binary)
        self.assertGreaterEqual(self.script.count(candidate), 2)
        self.assertGreaterEqual(self.script.count(binary), 2)
        self.assertNotIn(
            "TPACKET_QM_RUNTIME_AFFINITY_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC",
            self.script,
        )

    def test_group512_semantics_and_raw_continuity_gate_are_explicit(self):
        traffic = self.config["traffic"]
        self.assertEqual(traffic["clone_skb"], 64)
        self.assertEqual(traffic["burst"], 8)
        self.assertEqual(traffic["observed_group_packets"], 512)
        self.assertEqual(traffic["sequence_step"], 512)
        self.assertEqual(traffic["sequence_residue"], 1)
        for token in (
            '"profile_id": "linux_pktgen_ipv4_udp_be_header_clone64_burst8_group512_v2"',
            '"observed_group_packets": 512',
            '"sequence_step": 512',
            '"packet_gap": 0',
            '"input_conservation_ok": True',
            '"ownership_merge_conservation_ok": True',
            'continuity = v.get("packet_continuity")',
            'continuity_windows = v.get("packet_continuity_windows")',
        ):
            self.assertIn(token, self.script)

    def test_a09_health_cli_and_raw_identity_must_match(self):
        expected = self.config["expected_gpu_identity"]
        self.assertEqual(expected["candidate_id"], "A09")
        self.assertEqual(expected["schema_version"], 1)
        self.assertEqual(expected["inference_engine"], "numpy_exact")
        self.assertEqual(
            expected["model_sha256"],
            "fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2",
        )
        for token in (
            "--expected-gpu-candidate A09",
            "--expected-gpu-schema 1",
            "--expected-gpu-model-sha256 fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2",
            "--expected-gpu-inference-engine numpy_exact",
            '"backend_identity") != "A09/schema_v1/ordered_v1"',
        ):
            self.assertIn(token, self.script)

    def test_raw_field_paths_match_actual_serialized_metrics(self):
        for token in (
            'metrics = v.get("pipeline_metrics")',
            'metrics.get("flow_completion_receipts")',
            'metrics.get("flow_completion_conservation")',
            'metrics.get("gpu_batch_evidence")',
            'zero_metrics = ("gpu_queue_full", "gpu_batches_failed", "gpu_backend_identity_failures"',
            'if metrics.get(name) != 0',
        ):
            self.assertIn(token, self.script)
        for field in (
            "pub flow_completion_receipts: Vec<FlowCompletionReceipt>",
            "pub flow_completion_conservation: FlowCompletionConservation",
            "pub gpu_batch_evidence: Vec<GpuBatchEvidence>",
            "pub gpu_queue_full: u64",
            "pub gpu_batches_failed: u64",
        ):
            self.assertIn(field, self.metrics)
        self.assertIn("pipeline_metrics: MetricsReport", self.rust_bin)

    def test_loss_capacity_receipts_and_conservation_are_zero_or_per_window_gates(self):
        gates = self.config["runtime_hard_gates"]
        for name in (
            "feature_queue_drops_max",
            "key_feature_queue_drops_max",
            "gpu_queue_full_max",
            "gpu_batches_failed_max",
            "gpu_backend_identity_failures_max",
            "gpu_worker_join_failures_max",
            "key_flows_enqueue_failed_max",
            "key_flows_inference_failed_max",
            "key_flows_terminal_unresolved_max",
            "key_flows_recovery_pending_max",
            "flow_completion_receipts_truncated_max",
        ):
            self.assertEqual(gates[name], 0)
        self.assertEqual(gates["per_full_window_minimums"]["flow_completion_receipts"], 1000)
        self.assertEqual(gates["per_full_window_minimums"]["gpu_batch_evidence"], 100)
        self.assertTrue(gates["require_flow_completion_conservation"])

    def test_unproved_flow_churn_is_a_static_pre_mutation_block(self):
        execution = self.config["execution"]
        self.assertFalse(execution["flow_completion_density_precondition_proved"])
        self.assertTrue(execution["static_block_before_evidence_or_host_mutation"])
        self.assertEqual(execution["static_block_exit_code"], 86)
        blocker = self.script.index("final-evidence blocked before evidence or host mutation")
        self.assertLess(blocker, self.script.index('mkdir -m 0700 -- "${requested_evidence_dir}"'))
        self.assertLess(blocker, self.script.index('ethtool -G "${capture_nic}" rx 4078'))
        self.assertIn("last_ts_us.saturating_sub(value.first_ts_us) >= self.active_timeout_us", self.flow)
        self.assertIn("now_us.saturating_sub(value.last_ts_us) >= self.idle_timeout_us", self.flow)

    @unittest.skipUnless(os.name == "posix" and shutil.which("bash"), "requires POSIX bash")
    def test_bash_syntax_and_missing_authorization_fail_closed(self):
        syntax = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
        self.assertEqual(syntax.returncode, 0, syntax.stderr)
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ.copy()
            for name in tuple(env):
                if name.startswith("HFT_CURRENT_279_"):
                    env.pop(name)
            denied = subprocess.run(
                ["bash", str(RUNNER), str(Path(directory) / "hft_current_279_tpacket_denied")],
                env=env,
                capture_output=True,
                text=True,
            )
        self.assertEqual(denied.returncode, 74)
        self.assertIn("mutation authorization", denied.stderr)

    @unittest.skipUnless(os.name == "posix" and shutil.which("bash"), "requires POSIX bash")
    def test_exact_hash_roots_still_stop_at_static_block_without_creating_evidence(self):
        binary = ROOT / "rust" / "hft-capture" / "target" / "release" / "tpacket_v3_full_pipeline"
        if not binary.is_file():
            self.skipTest("formal binary unavailable")
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "hft_current_279_tpacket_final_blocked"
            env = os.environ.copy()
            env.update(
                {
                    "HFT_CURRENT_279_MUTATION_AUTHORIZATION": "I_AUTHORIZE_CURRENT_279_TPACKET_MUTATION",
                    "HFT_CURRENT_279_RESTORATION_AUTHORIZATION": "I_AUTHORIZE_CURRENT_279_TPACKET_RESTORATION",
                    "HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION": "I_AUTHORIZE_IRQBALANCE_STOP_START_FOR_CURRENT_279",
                    "HFT_CURRENT_279_CHANGE_TICKET": "HFT-279-FINAL-EVIDENCE-TDD",
                    "HFT_CURRENT_279_CONFIG": str(CONFIG),
                    "HFT_CURRENT_279_BINARY": str(binary.resolve()),
                    "HFT_CURRENT_279_RUNNER_SHA256": digest(RUNNER),
                    "HFT_CURRENT_279_CONFIG_SHA256": digest(CONFIG),
                    "HFT_CURRENT_279_BINARY_SHA256": digest(binary),
                }
            )
            blocked = subprocess.run(
                ["bash", str(RUNNER), str(evidence)], env=env, capture_output=True, text=True
            )
            self.assertEqual(blocked.returncode, 86, blocked.stderr)
            self.assertIn("flow completion density", blocked.stderr)
            self.assertFalse(evidence.exists())


if __name__ == "__main__":
    unittest.main()
