import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "dpdk_stock_tcp_rss_q2_diagnostic_v1.json"
RUNNER_PATH = ROOT / "scripts" / "run_dpdk_tcp_rss_diagnostic.sh"
VALIDATOR_PATH = ROOT / "scripts" / "validate_dpdk_tcp_rss_diagnostic.py"

SPEC = importlib.util.spec_from_file_location("tcp_rss_validator", VALIDATOR_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class DpdkTcpRssDiagnosticTest(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.hashes = {
            "contract_sha256": "a" * 64,
            "runner_sha256": "b" * 64,
            "validator_sha256": "c" * 64,
            "binary_sha256": "d" * 64,
            "cpu_preflight_sha256": "1" * 64,
            "dpdk_preflight_sha256": "2" * 64,
            "cpu_preflight_result_sha256": "3" * 64,
            "dpdk_preflight_result_sha256": "4" * 64,
            "pre_mutation_gate_sha256": "5" * 64,
            "build_manifest_sha256": "e" * 64,
            "bnx2x_ethdev_sha256": "f" * 64,
        }
        self.contract.update(
            binary_freeze_pending=False,
            expected_runner_sha256=self.hashes["runner_sha256"],
            expected_validator_sha256=self.hashes["validator_sha256"],
            expected_binary_sha256=self.hashes["binary_sha256"],
            expected_cpu_preflight_sha256=self.hashes["cpu_preflight_sha256"],
            expected_dpdk_preflight_sha256=self.hashes["dpdk_preflight_sha256"],
            expected_dpdk_build_manifest_sha256=self.hashes[
                "build_manifest_sha256"
            ],
            expected_bnx2x_ethdev_sha256=self.hashes["bnx2x_ethdev_sha256"],
        )
        self.result = {
            "schema_version": 5,
            "scope": "r0_dpdk_bnx2x_capture_only",
            "backend": "dpdk_bnx2x_stock_tcp_rss_diagnostic",
            "candidate_id": self.contract["candidate_id"],
            "frozen_thresholds_sha256": self.hashes["contract_sha256"],
            "capture_pci": self.contract["capture_pci"],
            "replay_pci": self.contract["replay_pci"],
            "queue_count": 2,
            "realtime_priority": self.contract["realtime_priority"],
            "main_cpu": self.contract["main_cpu"],
            "rx_cpus": self.contract["rx_cpus"],
            "tx_cpus": self.contract["tx_cpus"],
            "traffic_profile": "tcp_rss_diagnostic",
            "synthetic_flow_count": 256,
            "ip_protocol": 6,
            "timestamp_offset_bytes": 54,
            "port_configuration": "stock_bnx2x_implicit_tcp_rss_mq_none_hf_zero",
            "target_mpps": 1.0,
            "frame_size_bytes": 64,
            "burst_size": 128,
            "max_end_to_end_p99_us": 100.0,
            "max_end_to_end_p999_us": 500.0,
            "duration_s": 15.1,
            "offered_packets": 15_100_000,
            "received_packets": 15_100_000,
            "offered_received_gap": 0,
            "observed_tx_mpps_min_1s": 1.0,
            "observed_rx_mpps_min_1s": 1.0,
            "rate_window_alignment": "shared_monotonic_epoch_fixed_1s_v1",
            "tx_rate_full_windows": 15,
            "rx_rate_full_windows": 15,
            "achieved_tx_mpps": 1.0,
            "achieved_rx_mpps": 1.0,
            "tx_queue_packets": [7_550_000, 7_550_000],
            "rx_queue_packets": [7_550_000, 7_550_000],
            "capture_stats_delta": {
                "ipackets": 15_100_000,
                "imissed": 0,
                "ierrors": 0,
                "rx_nombuf": 0,
            },
            "replay_stats_delta": {"opackets": 15_100_000, "oerrors": 0},
            "latency_sample_stride": 1024,
            "latency_timestamp_source": "dpdk_tsc_embedded_tx_rx_v1",
            "end_to_end_latency_us": {
                "samples": 14_746,
                "p99": 80.0,
                "p999": 400.0,
            },
            "data_plane_qualified": True,
            "hard_gate_errors": [],
            "r0_capture_only_qualified": False,
            "full_pipeline_qualified": False,
            "final_pareto_ingestion_allowed": False,
        }
        requested = sorted(
            [self.contract["main_cpu"]]
            + self.contract["rx_cpus"]
            + self.contract["tx_cpus"]
        )
        self.cpu_preflight = {
            "scope": "non_mutating_dpdk_cpu_idle_preflight",
            "passed": True,
            "evidence_complete": True,
            "mutations_performed": False,
            "requested_cpus": requested,
            "include_smt_siblings": True,
            "effective_cpus": requested + [92, 93, 104, 109, 111],
            "max_utilization_threshold": 0.05,
            "sample_seconds": 1.0,
            "samples": 5,
            "observations": [{"sample": value} for value in range(1, 6)],
            "max_observed_utilization": {
                str(cpu): 0.01 for cpu in requested + [92, 93, 104, 109, 111]
            },
        }
        self.dpdk_preflight = {
            "scope": "read_only_dpdk_bnx2x_preflight",
            "ready_for_disruptive_validation": True,
            "mutations_performed": False,
            "blockers": [],
            "explicit_approval_required": True,
            "requires_all_pf_unbind": True,
            "dpdk_build_manifest_present": True,
            "uio_pci_generic_available": True,
            "rss_supported_by_bnx2x_pmd": False,
            "ports": [
                {
                    "interface": self.contract["capture_interface"],
                    "pci_address": self.contract["capture_pci"],
                    "driver": "bnx2x",
                    "carrier": 1,
                    "speed_mbps": 10_000,
                },
                {
                    "interface": self.contract["replay_interface"],
                    "pci_address": self.contract["replay_pci"],
                    "driver": "bnx2x",
                    "carrier": 1,
                    "speed_mbps": 10_000,
                },
            ],
        }
        self.restoration_ledger = [
            {"step": name, "status": 0, "ok": True}
            for name in (
                "child_stopped",
                f"bind_{self.contract['capture_pci']}_bnx2x",
                f"bind_{self.contract['replay_pci']}_bnx2x",
                "netdevs_reappeared",
                f"restore_{self.contract['capture_interface']}",
                f"restore_{self.contract['replay_interface']}",
                "runtime_prefix_removed",
                "hugepage_count_restored",
                "hugetlb_unmounted",
                "uio_pci_generic_unloaded",
                "uio_unloaded",
                "restored_snapshot_collection",
                "final_state_verification",
            )
        ]
        self.pre_mutation_gate = {
            "scope": "dpdk_stock_bnx2x_tcp_rss_q2_pre_mutation_gate",
            "mutations_performed": False,
            "exact_dpdk_process_gate_clear": True,
            "exact_dpdk_runtime_gate_clear": True,
            "frozen_and_source_artifact_rehash_verified": True,
            "passed": True,
            "frozen_artifact_sha256": {
                "contract": self.hashes["contract_sha256"],
                "runner": self.hashes["runner_sha256"],
                "validator": self.hashes["validator_sha256"],
                "binary": self.hashes["binary_sha256"],
                "cpu_preflight_script": self.hashes["cpu_preflight_sha256"],
                "dpdk_preflight_script": self.hashes["dpdk_preflight_sha256"],
                "dpdk_build_manifest": self.hashes["build_manifest_sha256"],
                "bnx2x_ethdev": self.hashes["bnx2x_ethdev_sha256"],
            },
        }

    def validate(
        self,
        result=None,
        manifest=None,
        *,
        cpu_preflight=None,
        dpdk_preflight=None,
        restoration_ledger=None,
        pre_mutation_gate=None,
        restoration_claim=True,
        original_exit_status=0,
        hashes=None,
    ):
        return MODULE.validate(
            self.contract,
            self.result if result is None else result,
            **(self.hashes if hashes is None else hashes),
            build_manifest_text=manifest
            or "experimental_bnx2x_rss=NO\n"
            + f"bnx2x_ethdev_sha256={self.hashes['bnx2x_ethdev_sha256']}\n",
            cpu_preflight=(
                self.cpu_preflight if cpu_preflight is None else cpu_preflight
            ),
            dpdk_preflight=(
                self.dpdk_preflight if dpdk_preflight is None else dpdk_preflight
            ),
            pre_mutation_gate=(
                self.pre_mutation_gate
                if pre_mutation_gate is None
                else pre_mutation_gate
            ),
            restoration_ledger=(
                self.restoration_ledger
                if restoration_ledger is None
                else restoration_ledger
            ),
            original_exit_status=original_exit_status,
            restoration_claim=restoration_claim,
        )

    def test_valid_q2_is_diagnostic_only(self):
        acceptance = self.validate()
        self.assertTrue(acceptance["diagnostic_passed"])
        self.assertTrue(acceptance["q2_5m_unlocked"])
        self.assertFalse(acceptance["q4_unlocked"])
        self.assertFalse(acceptance["resource_gate_evaluated"])
        self.assertFalse(acceptance["final_pareto_ingestion_allowed"])
        self.assertTrue(acceptance["rate_alignment_verified"])
        self.assertTrue(acceptance["nic_packet_counters_verified"])

    def test_each_queue_must_reach_frozen_forty_percent(self):
        passing = copy.deepcopy(self.result)
        passing["tx_queue_packets"] = [6_040_000, 9_060_000]
        passing["rx_queue_packets"] = [6_040_000, 9_060_000]
        self.assertTrue(self.validate(passing)["diagnostic_passed"])

        failing = copy.deepcopy(self.result)
        failing["tx_queue_packets"] = [6_039_999, 9_060_001]
        failing["rx_queue_packets"] = [6_039_999, 9_060_001]
        acceptance = self.validate(failing)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("tx_software_queue_coverage", acceptance["errors"])
        self.assertIn("rx_software_queue_coverage", acceptance["errors"])

    def test_both_software_queues_are_mandatory(self):
        result = copy.deepcopy(self.result)
        result["rx_queue_packets"] = [15_100_000, 0]
        acceptance = self.validate(result)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("rx_software_queue_coverage", acceptance["errors"])
        self.assertTrue(acceptance["q2_failure_stops_branch"])

    def test_pending_binary_original_status_and_preflight_fail_closed(self):
        self.contract["binary_freeze_pending"] = True
        acceptance = self.validate(
            cpu_preflight={"passed": False},
            dpdk_preflight={"ready_for_disruptive_validation": False},
            original_exit_status=1,
        )
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("binary_freeze_pending", acceptance["errors"])
        self.assertIn("original_exit_status", acceptance["errors"])
        self.assertIn("cpu_preflight", acceptance["errors"])
        self.assertIn("dpdk_preflight", acceptance["errors"])

    def test_preflight_script_hashes_are_bound(self):
        hashes = copy.deepcopy(self.hashes)
        hashes["cpu_preflight_sha256"] = "9" * 64
        hashes["dpdk_preflight_sha256"] = "8" * 64
        acceptance = self.validate(hashes=hashes)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("identity.cpu_preflight", acceptance["errors"])
        self.assertIn("identity.dpdk_preflight", acceptance["errors"])

    def test_pre_mutation_gate_receipt_is_a_hard_gate(self):
        gate = copy.deepcopy(self.pre_mutation_gate)
        gate["exact_dpdk_process_gate_clear"] = False
        gate["passed"] = False
        acceptance = self.validate(pre_mutation_gate=gate)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("pre_mutation_gate", acceptance["errors"])

    def test_restoration_is_recomputed_from_complete_ledger(self):
        ledger = copy.deepcopy(self.restoration_ledger)
        ledger[4]["status"] = 1
        ledger[4]["ok"] = False
        acceptance = self.validate(
            restoration_ledger=ledger, restoration_claim=True
        )
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertFalse(acceptance["restoration_verified"])
        self.assertIn("restoration_ledger", acceptance["errors"])
        self.assertIn("restoration_claim", acceptance["errors"])

    def test_rate_alignment_and_nic_counts_are_independent_gates(self):
        result = copy.deepcopy(self.result)
        result["rate_window_alignment"] = "unaligned"
        result["capture_stats_delta"]["ipackets"] -= 1
        acceptance = self.validate(result)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("rate_windows", acceptance["errors"])
        self.assertIn("nic_packet_counters", acceptance["errors"])

    def test_rx_drain_elapsed_average_does_not_reject_full_windows(self):
        result = copy.deepcopy(self.result)
        # Rust RX elapsed includes the bounded drain interval, while the formal
        # rate gate is based on the 15 shared complete one-second windows.
        result["achieved_rx_mpps"] = 0.9967
        acceptance = self.validate(result)
        self.assertTrue(acceptance["diagnostic_passed"])
        self.assertEqual(acceptance["reported_achieved_rx_mpps"], 0.9967)
        self.assertGreaterEqual(
            acceptance["derived_rx_contract_window_mpps"], 1.0
        )

    def test_rx_contract_window_packet_total_is_still_a_gate(self):
        result = copy.deepcopy(self.result)
        result["offered_packets"] = 14_999_999
        result["received_packets"] = 14_999_999
        result["tx_queue_packets"] = [7_499_999, 7_500_000]
        result["rx_queue_packets"] = [7_499_999, 7_500_000]
        result["capture_stats_delta"]["ipackets"] = 14_999_999
        result["replay_stats_delta"]["opackets"] = 14_999_999
        result["achieved_tx_mpps"] = 14_999_999 / 15.1 / 1_000_000
        acceptance = self.validate(result)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("rate_windows", acceptance["errors"])

    def test_latency_is_recomputed_from_report(self):
        result = copy.deepcopy(self.result)
        result["end_to_end_latency_us"]["p999"] = 501.0
        result["data_plane_qualified"] = True
        acceptance = self.validate(result)
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("end_to_end_p999", acceptance["errors"])

    def test_stock_manifest_is_a_hard_gate(self):
        acceptance = self.validate(manifest="experimental_bnx2x_rss=YES\n")
        self.assertFalse(acceptance["diagnostic_passed"])
        self.assertIn("stock_manifest.experimental_bnx2x_rss", acceptance["errors"])

    def test_runner_is_independent_q2_tcp_and_fail_closed(self):
        runner = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertIn("--traffic-profile tcp-rss-diagnostic", runner)
        self.assertIn(".queue_count == 2", runner)
        self.assertIn(".min_per_queue_packet_fraction == 0.40", runner)
        self.assertIn(".q4_allowed == false", runner)
        self.assertIn("experimental_bnx2x_rss=NO", runner)
        self.assertIn("validate_dpdk_tcp_rss_diagnostic.py", runner)
        self.assertIn("--restoration-ledger", runner)
        self.assertIn("verify_run_dir_frozen_artifacts", runner)
        self.assertIn("exact_dpdk_process_gate", runner)
        self.assertIn("exact_dpdk_runtime_gate", runner)
        self.assertNotIn("compose_dpdk_run_acceptance.py", runner)
        self.assertNotIn("run_dpdk_bnx2x_validation.sh", runner)
        wait_tail = runner[runner.rindex('wait "${child_pid}"') :]
        self.assertNotIn('child_pid=""', wait_tail)
        self.assertNotIn('child_pgid=""', wait_tail)
        self.assertNotIn('child_pgid="${observed_child_pgid}"', runner)
        self.assertIn(
            '[[ "${observed_child_pgid}" == "${child_pid}" ]] && break', runner
        )
        ownership_check = runner.index('previous == "--file-prefix"')
        group_signal = runner.index('kill -TERM -- "-${child_pgid}"')
        self.assertLess(ownership_check, group_signal)
        self.assertLess(
            runner.index("preflight_dpdk_cpu_idle.py"),
            runner.index("mutation_started=1"),
        )
        self.assertLess(
            runner.rindex("verify_run_dir_frozen_artifacts &&"),
            runner.index("mutation_started=1"),
        )

    def test_interface_restoration_is_best_effort(self):
        runner = RUNNER_PATH.read_text(encoding="utf-8")
        start = runner.index("restore_interface_settings()")
        end = runner.index("remove_runtime_prefix()", start)
        function = runner[start:end]
        self.assertGreaterEqual(function.count("|| status=1"), 6)
        self.assertNotIn("|| return", function)
        self.assertIn('return "${status}"', function)


if __name__ == "__main__":
    unittest.main()
