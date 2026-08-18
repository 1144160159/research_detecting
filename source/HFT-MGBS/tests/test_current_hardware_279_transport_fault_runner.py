import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile
import unittest


PROJECT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = PROJECT / "scripts/run_current_hardware_279_transport_fault_v1.sh"
CONFIG = PROJECT / "configs/current_hardware_2_79_transport_fault_runner_v1.json"
PROFILE = PROJECT / "configs/current_hardware_2_79_release_profile_v3_transport_recovery.json"
GPU_SOURCE = PROJECT / "rust/hft-capture/src/gpu.rs"
PIPELINE_SOURCE = PROJECT / "rust/hft-capture/src/bin/tpacket_v3_full_pipeline.rs"


class TransportFaultRunnerContractTest(unittest.TestCase):
    def setUp(self):
        self.text = RUNNER.read_text(encoding="utf-8")
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_shell_syntax(self):
        if os.name == "nt":
            self.skipTest("remote Linux bash -n gate covers shell syntax")
        result = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_is_independent_and_parent_is_frozen(self):
        self.assertNotEqual(RUNNER.name, "run_current_hardware_279_tpacket_diagnostic.sh")
        parent = PROJECT / "scripts" / pathlib.Path(self.config["parent_runner"]["path"]).name
        self.assertEqual(hashlib.sha256(parent.read_bytes()).hexdigest(), self.config["parent_runner"]["sha256"])
        self.assertEqual(hashlib.sha256(PROFILE.read_bytes()).hexdigest(), self.config["transport_profile"]["sha256"])
        self.assertEqual(hashlib.sha256(GPU_SOURCE.read_bytes()).hexdigest(), self.config["rust_recovery_source"]["sha256"])

    def test_current_budget_is_static_no_go(self):
        profile = json.loads(PROFILE.read_text())
        found = re.search(r"CIRCUIT_OPEN_DURATION:\s*Duration\s*=\s*Duration::from_millis\((\d+)\)", GPU_SOURCE.read_text())
        self.assertIsNotNone(found)
        self.assertGreaterEqual(int(found.group(1)), profile["transport_recovery"]["recovery_ms_max"])
        self.assertLess(self.text.index("NO-GO: circuit-open"), self.text.index("iptables -w 5 -I OUTPUT"))

    def test_current_pipeline_lacks_required_per_window_continuity(self):
        pipeline = PIPELINE_SOURCE.read_text()
        missing = [m for m in self.config["rust_pipeline_source"]["required_receipt_markers"] if m not in pipeline]
        self.assertEqual(missing, ["packet_continuity_windows", "packet_gap"])
        self.assertIn("NO-GO: raw pipeline lacks per-window continuity markers", self.text)

    def test_rule_is_exact_single_reverse_connection(self):
        for token in ('--sport "${reverse_port}"', '-d "${gpu_ip}"', '--dport "${peer_port}"',
                      '-m owner --uid-owner 0', '-m conntrack --ctstate ESTABLISHED',
                      '--comment "${rule_comment}"', '-j REJECT --reject-with tcp-reset'):
            self.assertIn(token, self.text)
        self.assertNotIn("--dport \"${health_port}\"", self.text)
        self.assertNotRegex(self.text, r"iptables\s+(?:-w\s+\d+\s+)?-(?:F|X)\b")

    def test_no_gpu_service_control_or_remote_kill(self):
        self.assertNotRegex(self.text, r"(?:systemctl|service)\s+.*gpu")
        self.assertNotRegex(self.text, r"\bkill(?:all)?\b.*(?:10\.0\.5\.103|gpu|50051)")
        self.assertNotIn("ssh ", self.text)

    def test_three_authorizations_lock_watchdog_and_trap(self):
        self.assertEqual(self.text.count("_AUTHORIZATION:-}"), 3)
        self.assertIn("flock -n 9", self.text)
        self.assertIn("setsid bash -c", self.text)
        self.assertIn("trap cleanup EXIT INT TERM HUP", self.text)
        self.assertIn("iptables-save", self.text)
        self.assertIn('after_rules_sha}" == "${before_rules_sha}', self.text)

    def test_external_receipt_is_hashed_and_events_are_monotonic(self):
        self.assertIn('"external_fault_receipt":{"path":faultp.name,"sha256":fsha}', self.text)
        self.assertIn("time.monotonic_ns()", self.text)
        self.assertIn('"injected_monotonic_ns":inj', self.text)
        self.assertIn('"removed_monotonic_ns":removed', self.text)

    def test_receipt_refuses_synthetic_window_zeros(self):
        self.assertIn('windows=raw.get("packet_continuity_windows")', self.text)
        self.assertIn('w.get("packet_gap")!=0 or w.get("capture_drop")!=0', self.text)
        self.assertNotIn('"packet_gap":0,"capture_drop":0', self.text)

    def test_profile_and_config_claim_only_transport_recovery(self):
        profile = json.loads(PROFILE.read_text())
        self.assertFalse(profile["claim_boundary"]["remote_retry_is_local_fallback"])
        self.assertFalse(profile["claim_boundary"]["production_high_availability_qualified"])
        self.assertTrue(self.config["safety"]["gpu_service_stop_or_kill_forbidden"])
        self.assertTrue(self.config["safety"]["ssh_and_port_50051_rules_forbidden"])

    def test_config_has_only_hash_identity_not_secret(self):
        raw = CONFIG.read_text()
        self.assertNotRegex(raw, r"(?i)password|private.?key|1qaz")
        for value in self.config["a09_identity"].values():
            self.assertRegex(value, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
