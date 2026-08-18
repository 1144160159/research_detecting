from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_dpdk_bnx2x_validation.sh"
RUST_MAIN = ROOT / "rust" / "hft-dpdk" / "src" / "main.rs"
RELEASE_CONFIG = (
    ROOT / "configs" / "r0_dpdk_probe_1mpps_b128_release_gate_v2.json"
)


class DpdkRunnerContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = RUNNER.read_text(encoding="utf-8")
        cls.rust = RUST_MAIN.read_text(encoding="utf-8")
        cls.config = json.loads(RELEASE_CONFIG.read_text(encoding="utf-8"))

    def test_release_candidate_is_frozen_single_queue_and_not_final_pareto(self):
        self.assertEqual(self.config["schema_version"], 2)
        self.assertEqual(self.config["qualification_mode"], "release_gate_v2")
        self.assertTrue(self.config["frozen"])
        self.assertEqual(self.config["queue_count"], 1)
        self.assertEqual(
            self.config["expected_backend"], "dpdk_bnx2x_single_queue"
        )
        self.assertFalse(self.config["binary_freeze_pending"])
        self.assertRegex(
            self.config["expected_binary_sha256"], re.compile(r"^[0-9a-f]{64}$")
        )
        for field in (
            "expected_runner_sha256",
            "expected_validator_sha256",
            "expected_composer_sha256",
            "expected_cpu_preflight_sha256",
            "expected_dpdk_preflight_sha256",
            "expected_dpdk_build_manifest_sha256",
        ):
            self.assertRegex(self.config[field], re.compile(r"^[0-9a-f]{64}$"))
        self.assertFalse(self.config["final_pareto_ingestion_allowed"])
        self.assertEqual(
            self.config["hugepage_count"] * self.config["hugepage_size_bytes"],
            self.config["resource_max"]["hugepage_reserved_bytes"],
        )

    def test_internal_lock_and_identity_checks_precede_mutation(self):
        lock = self.runner.index("flock -n 9")
        mapping = self.runner.index("interface-to-PCI mapping")
        preflight_only = self.runner.index(
            'if [[ "${HFT_DPDK_PREFLIGHT_ONLY:-}" == "YES" ]]'
        )
        cpu_preflight = self.runner.index(
            'python3 "${run_dir}/preflight_dpdk_cpu_idle.py"'
        )
        mutation = self.runner.index("mutation_started=1")
        self.assertLess(lock, mapping)
        self.assertLess(mapping, mutation)
        self.assertLess(preflight_only, mutation)
        self.assertLess(cpu_preflight, mutation)
        self.assertIn("table all dev", self.runner)
        self.assertIn("/master", self.runner)
        self.assertIn("upper_*", self.runner)
        self.assertIn(".iif == $interface", self.runner)
        self.assertIn(".oif == $interface", self.runner)
        self.assertIn('.dst == "ff00::/8"', self.runner)

    def test_signal_cleanup_is_fail_closed(self):
        self.assertIn("trap 'on_signal HUP 129' HUP", self.runner)
        self.assertIn("trap 'on_signal INT 130' INT", self.runner)
        self.assertIn("trap 'on_signal TERM 143' TERM", self.runner)
        self.assertIn("trap finalize EXIT", self.runner)
        self.assertIn("trap '' HUP INT TERM", self.runner)
        self.assertIn("timeout --signal=TERM --kill-after=5s", self.runner)
        self.assertIn("restore_attempted", self.runner)
        self.assertNotIn("restore_host || true", self.runner)
        self.assertNotIn("rm -rf", self.runner)
        self.assertNotIn("/new_id", self.runner)

    def test_evidence_empty_arrays_and_cleanup_fatal_errors_are_fail_closed(self):
        self.assertIn(
            "local -a required_files=() present_files=() missing_files=() empty_files=()",
            self.runner,
        )
        self.assertIn("local -a snapshot_suffixes=()", self.runner)
        self.assertIn("trap 'trap - EXIT; exit 99' EXIT", self.runner)
        self.assertIn('build_status="$?"', self.runner)
        self.assertIn("final_status=17", self.runner)

    def test_result_resources_restoration_and_hashes_are_required_evidence(self):
        for name in (
            "result.json",
            "process_time.txt",
            "preflight.stdout.json",
            "restoration_ledger.json",
            "acceptance.json",
            "evidence_inventory.json",
            "evidence_sha256_complete.txt",
            "evidence_sha256_complete_check.txt",
        ):
            self.assertIn(name, self.runner)
        self.assertIn("validate_dpdk_run.py", self.runner)
        self.assertIn("compose_dpdk_run_acceptance.py", self.runner)
        self.assertIn("standalone_receipt_trusted", (
            ROOT / "scripts" / "compose_dpdk_run_acceptance.py"
        ).read_text(encoding="utf-8"))
        self.assertIn("sha256sum -c evidence_sha256_complete.txt", self.runner)

    def test_all_numa_hugepages_and_frozen_interface_baseline_are_required(self):
        self.assertIn("HUGEPAGE_NODE_GLOB", self.runner)
        self.assertIn("hugepage_nodes_before_json", self.runner)
        self.assertIn("hugepages_global_during", self.runner)
        self.assertIn("dedicated_bnx2x_kernel_default_v1", self.runner)
        self.assertIn("baseline_features_sha256", self.runner)
        self.assertIn("baseline_qdisc_sha256", self.runner)
        self.assertIn("capture_mtu_before", self.runner)
        self.assertIn("capture_txqlen_before", self.runner)

    def test_schema_five_separates_raw_data_plane_from_wrapper_acceptance(self):
        self.assertIn("schema_version: 5", self.rust)
        self.assertIn('errors.push("tx_target_load")', self.rust)
        self.assertIn('errors.push("rx_target_load")', self.rust)
        self.assertIn('errors.push("replay_tx_error")', self.rust)
        self.assertIn("data_plane_qualified", self.rust)
        self.assertIn("resource_gate_evaluated: false", self.rust)
        self.assertIn("r0_capture_only_qualified: false", self.rust)
        self.assertIn("final_pareto_ingestion_allowed: false", self.rust)


if __name__ == "__main__":
    unittest.main()
