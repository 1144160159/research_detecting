from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_dpdk_testpmd_capacity.sh"
SUMMARY = ROOT / "scripts" / "summarize_dpdk_testpmd_capacity.py"
Q1 = ROOT / "configs" / "dpdk_testpmd_capacity_10mpps_v1.json"
Q4 = ROOT / "configs" / "dpdk_testpmd_capacity_q4_10mpps_v1.json"
Q4_V2 = ROOT / "configs" / "dpdk_testpmd_capacity_q4_10mpps_v2.json"
SPEC = importlib.util.spec_from_file_location("capacity_summary", SUMMARY)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def testpmd_log(direction: str, rates: list[int]) -> str:
    rate_name = "Rx-pps" if direction == "rx" else "Tx-pps"
    packet_name = "RX-packets" if direction == "rx" else "TX-packets"
    lines = [f"{rate_name}: {rate}" for rate in rates]
    lines += [
        f"{packet_name}: 150000000",
        "RX-missed: 0",
        "RX-errors: 0",
        "RX-nombuf: 0",
        "TX-errors: 0",
        "###### NIC extended statistics for port 0",
        "rx_errors: 0",
        "rx_missed_errors: 0",
        "tx_errors: 0",
    ]
    return "\n".join(lines)


class DpdkTestpmdCapacityTest(unittest.TestCase):
    def setUp(self):
        self.q1 = json.loads(Q1.read_text(encoding="utf-8"))

    def summarize(self, rx_rates, tx_rates):
        return MODULE.summarize(
            self.q1,
            testpmd_log("rx", rx_rates),
            testpmd_log("tx", tx_rates),
            contract_sha256="1" * 64,
            rx_log_sha256="2" * 64,
            tx_log_sha256="3" * 64,
        )

    def test_q1_is_diagnostic_only_and_has_distinct_workers(self):
        for path, rx_queues, tx_queues in ((Q1, 1, 1),):
            config = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(config["diagnostic_only"])
            self.assertFalse(config["final_pareto_ingestion_allowed"])
            self.assertEqual(config["rx_queue_count"], rx_queues)
            self.assertEqual(config["tx_queue_count"], tx_queues)
            cpus = [config["rx_main_cpu"], config["tx_main_cpu"]]
            cpus += config["rx_worker_cpus"] + config["tx_worker_cpus"]
            self.assertEqual(len(cpus), len(set(cpus)))
            self.assertEqual(config["numa_node"], 1)
            self.assertTrue(all(28 <= cpu <= 55 for cpu in cpus))
            self.assertEqual(len(config["rx_worker_cpus"]), rx_queues)
            self.assertEqual(len(config["tx_worker_cpus"]), tx_queues)

    def test_asymmetric_q4_contracts_are_retained_only_as_rejected_evidence(self):
        runner = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("and .rx_queue_count == 1", runner)
        self.assertIn("and .tx_queue_count == 1", runner)
        self.assertNotIn(".tx_queue_count == 1 or .tx_queue_count == 4", runner)
        for path in (Q4, Q4_V2):
            config = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(config["rx_queue_count"], 1)
            self.assertEqual(config["tx_queue_count"], 4)
            self.assertTrue(config["diagnostic_only"])
            self.assertFalse(config["final_pareto_ingestion_allowed"])

    def test_q4_v2_is_a_single_cpu_only_adaptation(self):
        q4_v1 = json.loads(Q4.read_text(encoding="utf-8"))
        q4_v2 = json.loads(Q4_V2.read_text(encoding="utf-8"))
        allowed_changes = {
            "candidate_id",
            "rx_main_cpu",
            "rx_worker_cpus",
            "tx_main_cpu",
            "tx_worker_cpus",
            "cpu_selection_evidence",
            "notes",
        }
        differing = {key for key in q4_v1.keys() | q4_v2.keys() if q4_v1.get(key) != q4_v2.get(key)}
        self.assertLessEqual(differing, allowed_changes)
        self.assertEqual(q4_v2["rx_main_cpu"], 45)
        self.assertEqual(q4_v2["rx_worker_cpus"], [46])
        self.assertEqual(q4_v2["tx_main_cpu"], 51)
        self.assertEqual(q4_v2["tx_worker_cpus"], [30, 31, 32, 37])
        self.assertTrue(q4_v2["frozen"])

    def test_summary_passes_twelve_post_warmup_windows(self):
        rx_rates = [1, 2, 3, 4] + [10_100_000] * 12
        tx_rates = [1, 2] + [10_100_000] * 12
        result = self.summarize(rx_rates, tx_rates)
        self.assertTrue(result["capacity_qualified"])
        self.assertFalse(result["r0_capture_only_qualified"])
        self.assertFalse(result["full_pipeline_qualified"])

    def test_summary_rejects_low_rate_or_missing_xstats(self):
        rx_rates = [1, 2, 3, 4] + [10_100_000] * 11 + [9_900_000]
        tx_rates = [1, 2] + [10_100_000] * 11 + [9_900_000]
        result = self.summarize(rx_rates, tx_rates)
        self.assertFalse(result["capacity_qualified"])
        self.assertIn("rx_target_capacity", result["errors"])
        result = MODULE.summarize(
            self.q1,
            "Rx-pps: 10100000\n" * 14,
            "Tx-pps: 10100000\n" * 14,
            contract_sha256="1" * 64,
            rx_log_sha256="2" * 64,
            tx_log_sha256="3" * 64,
        )
        self.assertIn("rx_xstats_missing", result["errors"])

    def test_summary_rejects_nonzero_standard_error_counters(self):
        rx_rates = [1, 2, 3, 4] + [10_100_000] * 12
        tx_rates = [1, 2] + [10_100_000] * 12
        rx_log = testpmd_log("rx", rx_rates).replace("RX-missed: 0", "RX-missed: 1")
        result = MODULE.summarize(
            self.q1,
            rx_log,
            testpmd_log("tx", tx_rates),
            contract_sha256="1" * 64,
            rx_log_sha256="2" * 64,
            tx_log_sha256="3" * 64,
        )
        self.assertFalse(result["capacity_qualified"])
        self.assertIn("nonzero_standard_error_counters", result["errors"])

    def test_runner_contract_is_fail_closed_and_restores_host(self):
        runner = SCRIPT.read_text(encoding="utf-8")
        for token in (
            "flock -n 9",
            "preflight_dpdk_cpu_idle.py",
            "--include-smt-siblings",
            "show port xstats all",
            'printf "show port stats all',
            "trap '' HUP INT TERM",
            "restoration_ledger.json",
            "evidence_sha256_complete.txt",
            "qdisc_sha256",
            "hugepage_nodes_json",
            "runtime_prefixes_removed",
            "final_state_verification",
            "mkfifo",
            "process_dir in /proc/[0-9]*",
            "rx_ready.marker",
            "tx_ready.marker",
            "--burst=256",
            "--mbcache=512",
            "--total-num-mbufs=32768",
            "--record-burst-stats",
            "--socket-mem 0,256",
            "HFT_PREFLIGHT_ONLY",
            "mutation_started:false",
        ):
            self.assertIn(token, runner)
        self.assertNotIn("rm -rf", runner)
        self.assertNotIn("pgrep -af '[h]ft-dpdk|[t]estpmd", runner)
        self.assertIn(".rx_queue_count as $queues", runner)
        self.assertIn(".tx_queue_count as $queues", runner)
        self.assertIn("and .tx_queue_count == 1", runner)
        self.assertIn('sleep 2; printf "start', runner)
        self.assertNotIn('--stats-period "${STATS_PERIOD}"', runner)
        self.assertLess(runner.index("mkfifo"), runner.index("dpdk-testpmd.bin"))


if __name__ == "__main__":
    unittest.main()
