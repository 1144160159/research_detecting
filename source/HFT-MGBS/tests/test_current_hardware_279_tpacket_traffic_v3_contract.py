import json
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_traffic_v3_contract.sh"
CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_traffic_v3_contract.json"
RUST_BIN = ROOT / "rust" / "hft-capture" / "src" / "bin" / "tpacket_v3_full_pipeline.rs"


class CurrentHardware279TpacketRunnerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = RUNNER.read_text(encoding="utf-8")
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.rust_bin = RUST_BIN.read_text(encoding="utf-8")

    def test_config_freezes_traffic_v3_and_qm_runtime_affinity_full_pipeline(self):
        self.assertEqual(self.config["interfaces"]["capture"], "ens8f0")
        self.assertEqual(
            self.config["candidate_id"],
            "TPACKET_QM_RUNTIME_AFFINITY_MULTIFLOW_V3_FLOW_CHURN_DIAGNOSTIC",
        )
        self.assertEqual(self.config["interfaces"]["replay"], "ens8f1")
        self.assertEqual(self.config["interfaces"]["hardware_queues"], 8)
        self.assertEqual(self.config["traffic"]["packet_size_l2_bytes"], 64)
        self.assertEqual(self.config["traffic"]["generator_queues"], 8)
        self.assertEqual(self.config["traffic"]["clone_skb"], 64)
        self.assertEqual(self.config["traffic"]["burst"], 8)
        self.assertEqual(self.config["traffic"]["rx_usecs"], 24)
        self.assertEqual(self.config["pipeline"]["fanout_mode"], "qm")
        self.assertEqual(
            self.config["pipeline"]["binary_sha256"],
            "499b0b8e9abc14877d85fa0009489ffdf2e7f8d9527986e6cd1993008c2589fe",
        )
        self.assertTrue(self.config["pipeline"]["allow_qm_override"])
        self.assertTrue(self.config["pipeline"]["require_runtime_flow_affinity_evidence"])
        self.assertEqual(self.config["pipeline"]["flow_affinity_hash_algorithm"], "dual_fnv1a64_v1")
        self.assertEqual(self.config["pipeline"]["flow_affinity_cross_worker_collision_max"], 0)
        self.assertEqual(self.config["pipeline"]["active_timeout_seconds"], 1)
        self.assertEqual(self.config["pipeline"]["batch_size"], 8)
        self.assertGreaterEqual(self.config["traffic"]["generator_duration_seconds"], 19)
        self.assertGreaterEqual(self.config["pipeline"]["minimum_required_full_windows"], 15)
        self.assertTrue(self.config["preflight"]["include_smt_siblings"])
        self.assertEqual(self.config["preflight"]["cpu_sample_count"], 5)
        self.assertEqual(self.config["preflight"]["reserved_cpu_average_busy_fraction_max"], 0.85)
        self.assertEqual(self.config["preflight"]["reserved_cpu_single_sample_busy_fraction_block"], 0.98)
        self.assertTrue(self.config["preflight"]["require_complete_cpu_evidence"])
        self.assertEqual(self.config["pipeline"]["pktgen_cpus"], [44,45,46,47,48,49,50,52])
        self.assertEqual(self.config["pipeline"]["scheduler_cpu"], 53)
        self.assertEqual(self.config["pipeline"]["generator_control_cpu"], 54)
        self.assertEqual(
            self.config["preflight"]["irqbalance_active_mode"],
            "explicitly_authorized_stop_then_fixed_irq_then_restore_service",
        )
        self.assertTrue(self.config["preflight"]["irqbalance_service_stop_start_authorization_required"])
        self.assertEqual(self.config["preflight"]["irqbalance_service_stop_timeout_seconds"], 15)
        self.assertEqual(self.config["preflight"]["irqbalance_service_start_timeout_seconds"], 15)
        self.assertTrue(self.config["pipeline"]["dual_port_same_queue_irq_mapping"])
        self.assertEqual(self.config["pipeline"]["start_delay_ms"], 13000)
        self.assertEqual(self.config["runtime_hard_gates"]["capture_nic_rx_discards_delta_max"], 0)

    def test_deterministic_multiflow_v3_is_frozen_and_read_back(self):
        traffic = self.config["traffic"]
        self.assertEqual(traffic["profile_id"], "deterministic_multiflow_v3_flowlen1")
        self.assertEqual(traffic["flows_per_queue"], 145)
        self.assertEqual(traffic["flowlen_packets"], 1)
        self.assertEqual(traffic["destination_range_semantics"], "inclusive_on_observed_linux_5_10_pktgen")
        self.assertEqual(traffic["expected_global_distinct_flows"], 1160)
        self.assertEqual(traffic["expected_revisit_cycle_packets_per_queue"], 9280)
        self.assertEqual(traffic["expected_active_timeout_closures_per_second"], 1160)
        self.assertEqual(traffic["flow_sequence_flag"], "FLOW_SEQ")
        self.assertEqual(traffic["udp_destination_port"], 53)
        for token in (
            'pgset "${control}" flows 145',
            'pgset "${control}" flowlen 1',
            'pgset "${control}" flag FLOW_SEQ',
            'pgset "${control}" udp_dst_min 53',
            'pgset "${control}" udp_dst_max 53',
            'dst_max "11.${index}.0.145"',
            "pktgen_configured_${index}.txt",
            "pktgen_params_validation.txt",
            "pktgen_current_validation.txt",
            "range_semantics=inclusive",
            "aggregate closed-flow density is below 1000 per full window",
        ):
            self.assertIn(token, self.script)

    def test_traffic_v3_is_blocked_before_mutation_until_real_prerequisites_exist(self):
        blockers = self.config["execution_blockers"]
        self.assertTrue(blockers["generator_tail_2_79_requalification_required"])
        self.assertTrue(blockers["per_flow_end_to_end_receipt_not_implemented_in_frozen_binary"])
        self.assertTrue(blockers["fail_before_host_mutation"])
        blocker = self.script.index("traffic-v3 blocked before host mutation")
        mutation = self.script.index('ethtool -G "${capture_nic}" rx 4078')
        self.assertLess(blocker, mutation)
        self.assertIn("exit 86", self.script[blocker:blocker + 300])
        self.assertNotIn("flow_kernel_receive_to_remote_score_end_to_end", self.rust_bin)

    def test_per_full_window_real_receipt_gate_is_strict_and_non_synthetic(self):
        minimums = self.config["runtime_hard_gates"]["per_full_window_latency_receipt_minimums"]
        self.assertEqual(minimums["flow_materialization_to_feature_enqueue"], 1000)
        self.assertEqual(minimums["kernel_receive_to_feature_enqueue"], 1000)
        self.assertEqual(minimums["flow_kernel_receive_to_remote_score_end_to_end"], 1000)
        self.assertEqual(minimums["gpu_batch_round_trip"], 100)
        for token in (
            "per_window_latency_receipt_gate.json",
            'full_window_ids = epoch_seconds[1:-1]',
            'receipt.get("window_id")',
            'receipt.get("metric")',
            'len(set(source_ids)) != len(source_ids)',
            'raw_latency_sample_receipts_truncated") != 0',
            '"synthetic_or_duplicated_receipts_allowed": False',
            "per-full-window real latency receipt minimum failed",
        ):
            self.assertIn(token, self.script)

    def test_runner_requires_all_authorizations_lock_and_three_hash_roots(self):
        required = [
            "HFT_CURRENT_279_MUTATION_AUTHORIZATION",
            "I_AUTHORIZE_CURRENT_279_TPACKET_MUTATION",
            "HFT_CURRENT_279_RESTORATION_AUTHORIZATION",
            "I_AUTHORIZE_CURRENT_279_TPACKET_RESTORATION",
            "HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION",
            "I_AUTHORIZE_IRQBALANCE_STOP_START_FOR_CURRENT_279",
            "HFT_CURRENT_279_CHANGE_TICKET",
            "HFT_CURRENT_279_RUNNER_SHA256",
            "HFT_CURRENT_279_CONFIG_SHA256",
            "HFT_CURRENT_279_BINARY_SHA256",
            "flock -n 9",
            "verify_frozen",
            "trusted_artifacts.sha256",
        ]
        for token in required:
            self.assertIn(token, self.script)
        self.assertLess(self.script.index("exact current-2.79 mutation authorization"),
                        self.script.index("mkdir -m 0700 -- \"${requested_evidence_dir}\""))
        self.assertLess(self.script.index("flock -n 9"),
                        self.script.index("mutations_started=true"))

    def test_runner_uses_qm_with_runtime_affinity_evidence_and_eight_worker_arguments(self):
        self.assertIn("--fanout-mode qm", self.script)
        self.assertIn("--allow-qm-with-verified-flow-affinity", self.script)
        self.assertIn("--flow-affinity-evidence-max-distinct-per-worker 65536", self.script)
        self.assertIn("--worker-cpus 36 37 38 39 40 41 42 43", self.script)
        for token in (
            'v.get("qm_flow_affinity_evidence")',
            '"schema_version": 2',
            '"hash_algorithm": "dual_fnv1a64_v1"',
            '"evidence_complete": True',
            '"runtime_verified": True',
            '"cross_worker_collision_count": 0',
            'affinity.get("closed_flow_observations") != v.get("flows_closed")',
        ):
            self.assertIn(token, self.script)
        self.assertNotIn("--allow-unready-gpu-diagnostic", self.script)

    def test_rust_qm_gate_is_derived_from_closed_flow_worker_ownership(self):
        for token in (
            "flow_affinity_hash_counts: BTreeMap<String, u64>",
            "stable_flow_id_hash(&flow.flow_id)",
            "build_flow_affinity_evidence(&workers)",
            "cross_worker_collision_count",
            "closed_flow_observations == total_flows_closed",
            "owners.values().all(|ids| ids.len() == 1)",
            "QM runtime flow-affinity evidence is incomplete or has cross-worker collisions",
            "qm_runtime_affinity_rejects_one_flow_seen_by_two_workers",
            "qm_runtime_affinity_rejects_bounded_evidence_overflow",
        ):
            self.assertIn(token, self.rust_bin)
        self.assertNotIn("qm_flow_affinity_asserted", self.rust_bin)

    def test_rust_hotpath_v1_and_low_rate_expiry_evidence_are_present(self):
        flow = (ROOT / "rust" / "hft-capture" / "src" / "flow.rs").read_text(encoding="utf-8")
        for token in (
            "if tcp_flags == 0",
            "remaining.trailing_zeros()",
            "sparse_flag_update_matches_fixed_eight_bit_reference_exhaustively",
        ):
            self.assertIn(token, flow)
        for token in (
            "EpochSecondAccumulator",
            "epoch_out_of_order_packets",
            "expire_scan_calls",
            "expire_scan_closed_total",
            "expire_scan_event_time_delta_us_min",
            "expire_scan_event_time_delta_us_max",
            "expire_scan_event_time_delta_samples",
            "expire_scan_first_delta_omitted",
            "record_expire_event_time_delta",
            "expiry_delta_observation_omits_epoch_sized_first_sample_without_changing_scan_count",
            "flush_closed",
            "epoch_accumulator_matches_per_packet_btree_for_monotonic_and_disordered_input",
        ):
            self.assertIn(token, self.rust_bin)

    def test_udp_worker_local_fast_path_has_equivalence_and_lifecycle_fixtures(self):
        flow = (ROOT / "rust" / "hft-capture" / "src" / "flow.rs").read_text(encoding="utf-8")
        for token in (
            "LocalUdpFlowState",
            "udp: HashMap<FlowKey, LocalUdpFlowState>",
            "if parsed.protocol == 17",
            "materialize_udp",
            "udp_local_fast_path_matches_generic_features_for_fixed_bidirectional_sequence",
            "udp_local_fast_path_matches_generic_features_for_randomized_sequences",
            "udp_local_fast_path_matches_active_idle_expiry_and_flush",
            "udp_local_fast_path_canonicalizes_both_directions_and_keeps_udp_flags_zero",
            "HighestDscp TOS must match",
            "microbench_udp_local_state_against_generic_partitioned_table",
        ):
            self.assertIn(token, flow)

    def test_gpu_ready_gate_precedes_generator_start(self):
        ready = self.script.index('v.get("gpu_ready_at_start") is True')
        generator = self.script.index("echo start >/proc/net/pktgen/pgctrl")
        self.assertLess(ready, generator)
        self.assertIn('[[ "${ready}" == true ]]', self.script)
        self.assertIn("pipeline exited before GPU reverse ready", self.script)

    def test_preflight_is_exact_and_service_stop_is_post_gate_only(self):
        required = [
            'basename "$(readlink -f "/sys/class/net/${nic}/device/driver")"',
            '"$(<"/sys/class/net/${nic}/operstate")" == up',
            '"$(<"/sys/class/net/${nic}/carrier")" == 1',
            '[[ -z "$(ip -o addr show dev "${nic}")" ]]',
            "expected exactly eight queue IRQs per interface",
            "cpu_preflight.json",
            "reserved CPU idle preflight failed",
            "process_threads_preflight.txt",
            "listening_tcp_preflight.txt",
            "irqbalance_systemd_show.txt",
            "irqbalance_systemd_config.txt",
            "irqbalance_enabled_state.txt",
            "irqbalance_process_identity.env",
            "thread_siblings_list",
            "range(5)",
            "average_busy_fraction_max",
            "single_sample_busy_fraction_block",
            "evidence_complete",
            "find_competing_pipeline",
            "competing_pipeline_pre_mutation.tsv",
            "competing_pipeline_final_pre_mutation.tsv",
            "reverse GPU port became occupied during preflight",
            "pktgen appeared during preflight",
            "mpstat -P ALL 1 21",
        ]
        for token in required:
            self.assertIn(token, self.script)
        self.assertNotIn("systemctl restart", self.script)
        final_gate = self.script.index("verify_frozen || { echo \"frozen artifacts drifted before mutation\"")
        stop_service = self.script.index("timeout 15 systemctl stop irqbalance")
        self.assertLess(final_gate, stop_service)

    def test_irqbalance_active_service_stop_start_is_bounded_and_transactional(self):
        for token in (
            "monitor_target_irq_affinity",
            "verify_target_irq_affinity",
            "verify_irqbalance_identity",
            "verify_irqbalance_inactive",
            "irqbalance_target_irqs.txt",
            "timeout 15 systemctl stop irqbalance",
            "timeout 15 systemctl start irqbalance",
            "irqbalance_systemd_show_stopped.txt",
            "irqbalance_systemd_config_pre_restore.txt",
            "irqbalance_process_identity_restored.env",
            "irqbalance_enabled_state_restored.txt",
            "irqbalance_unit_config verify true drifted",
            "restored_active_new_identity",
            "irqbalance_unexpectedly_active",
            "sleep 0.1",
            "sleep 11",
            "irq_affinity_drift.tsv",
            "irq_affinity_generator_start_check.tsv",
            "IRQ affinity monitor exited before generator start",
            "kill -TERM -- \"-${capture_pgid}\"",
        ):
            self.assertIn(token, self.script)
        for forbidden in (
            "SCM_CREDENTIALS", "settings ban irqs", "irqbalance_socket_request",
            "/run/irqbalance/irqbalance3649.sock", "systemctl restart irqbalance",
        ):
            self.assertNotIn(forbidden, self.script)
        self.assertNotIn("kill ${irqbalance_pid}", self.script)
        self.assertNotIn("pkill irqbalance", self.script)
        self.assertIn('if [[ "${irq_affinity_managed}" == true ]]', self.script)
        cleanup = self.script.index("# Stop the generator and every child")
        restore_irq = self.script.index('>"/proc/irq/${irq}/smp_affinity_list"', cleanup)
        restore_service = self.script.index("timeout 15 systemctl start irqbalance", cleanup)
        self.assertLess(restore_irq, restore_service)

    def test_nic_rx_discards_is_an_independent_zero_delta_gate(self):
        for token in (
            "nic_rx_discards_gate.json",
            "unique total rx_discards counter missing",
            "per-queue rx_discards evidence incomplete",
            '"maximum_allowed_delta": 0',
            "capture NIC rx_discards delta is nonzero",
        ):
            self.assertIn(token, self.script)

    def test_service_restore_requires_active_new_identity_and_same_executable(self):
        for token in (
            '"${restored_irqbalance_exe}" == "${irqbalance_exe}"',
            '"${restored_irqbalance_pid}:${restored_irqbalance_ticks}"',
            '!= "${irqbalance_pid}:${irqbalance_start_ticks}"',
            "irqbalance_service restore true identity_mismatch",
            "irqbalance_service restore true start_failed",
        ):
            self.assertIn(token, self.script)

    def test_complete_state_snapshot_and_restoration_ledger_are_sealed(self):
        for token in (
            "_interface.txt", "_addresses.txt", "_driver.txt", "_link.txt",
            "_ring.txt", "_coalesce.txt", "_features.txt", "_channels.txt",
            "_xdp.txt", "_qdisc.txt", "_qdisc_statistics.txt",
            "_irq_affinity.tsv", "_pktgen_module.txt", "_pktgen_pgctrl.txt",
            "restoration_ledger.tsv", "evidence.sha256", "evidence.sha256.check",
        ):
            self.assertIn(token, self.script)
        stop = self.script.index("# Stop the generator and every child")
        restore_irq = self.script.index('printf \'%s\\n\' "${affinity}"', stop)
        restore_ring = self.script.index('ethtool -G "${capture_nic}" rx "${original_rx_ring}"', stop)
        self.assertLess(stop, restore_irq)
        self.assertLess(stop, restore_ring)
        self.assertIn("trap '' HUP INT TERM", self.script)
        self.assertIn('setsid "${frozen_binary}"', self.script)
        self.assertIn('kill -TERM -- "-${capture_pgid}"', self.script)
        self.assertIn('kill -KILL -- "-${capture_pgid}"', self.script)
        self.assertIn("SECONDS + 5", self.script)

    def test_raw_receipts_can_never_claim_qualification(self):
        q = self.config["qualification"]
        self.assertTrue(q["raw_diagnostic_only"])
        self.assertFalse(q["runtime_identity_verified"])
        self.assertFalse(q["full_pipeline_qualified"])
        self.assertFalse(q["final_pareto_ingestion_allowed"])
        for token in (
            '"runtime_identity_verified": False',
            '"full_pipeline_qualified": False',
            '"final_pareto_ingestion_allowed": False',
        ):
            self.assertIn(token, self.script)

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
                env=env, capture_output=True, text=True,
            )
        self.assertEqual(denied.returncode, 74)
        self.assertIn("mutation authorization", denied.stderr)

    @unittest.skipUnless(os.name == "posix" and shutil.which("bash"), "requires POSIX bash")
    def test_traffic_v3_prerequisites_fail_before_evidence_or_host_mutation(self):
        binary = ROOT / "rust" / "hft-capture" / "target" / "release" / "tpacket_v3_full_pipeline"
        if not binary.is_file():
            self.skipTest("formal binary unavailable")
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "hft_current_279_tpacket_v3_blocked"
            env = os.environ.copy()
            env.update({
                "HFT_CURRENT_279_MUTATION_AUTHORIZATION": "I_AUTHORIZE_CURRENT_279_TPACKET_MUTATION",
                "HFT_CURRENT_279_RESTORATION_AUTHORIZATION": "I_AUTHORIZE_CURRENT_279_TPACKET_RESTORATION",
                "HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION": "I_AUTHORIZE_IRQBALANCE_STOP_START_FOR_CURRENT_279",
                "HFT_CURRENT_279_CHANGE_TICKET": "HFT-279-TRAFFIC-V3-TDD",
                "HFT_CURRENT_279_RUNNER_SHA256": digest(RUNNER),
                "HFT_CURRENT_279_CONFIG_SHA256": digest(CONFIG),
                "HFT_CURRENT_279_BINARY_SHA256": digest(binary),
            })
            blocked = subprocess.run(
                ["bash", str(RUNNER), str(evidence)], env=env, capture_output=True, text=True,
            )
            self.assertEqual(blocked.returncode, 86, blocked.stderr)
            self.assertIn("traffic-v3 blocked before host mutation", blocked.stderr)
            self.assertFalse(evidence.exists())


if __name__ == "__main__":
    unittest.main()
