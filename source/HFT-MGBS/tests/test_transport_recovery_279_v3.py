import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.transport_recovery_279 import compose_transport_recovery_campaign_v3


PROJECT = Path(__file__).resolve().parents[1]
PROFILE = PROJECT / "configs/current_hardware_2_79_release_profile_v3_transport_recovery.json"


def dump(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


class TransportRecoveryV3Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        identity = {name: (str(i) * 64)[:64] for i, name in enumerate(
            ("model", "runtime_manifest", "service_source", "engine_source", "service_launcher"), 1)}
        self.receipts = []
        for index in range(3):
            run, trial = f"run-{index}", f"trial-{index}"
            start = 1_000_000_000 + index * 1_000_000_000
            fault = {"schema_version": 1, "scope": "hft_mgbs_external_transport_fault_injection_receipt_v1",
                     "run_id": run, "trial_id": trial, "controller_id": f"external-{index}",
                     "action": "disconnect_reverse_tcp", "target_listener": "127.0.0.1:50052",
                     "injected_monotonic_ns": start + 10}
            fp = self.root / f"fault-{index}.json"
            fsha = dump(fp, fault)
            receipt = {
                "schema_version": 3, "scope": "hft_mgbs_current_hardware_2_79_transport_recovery_receipt_v3",
                "campaign_id": "campaign", "candidate_id": "candidate", "run_id": run, "trial_id": trial,
                "start_monotonic_ns": start, "end_monotonic_ns": start + 100_000_000, "recovery_ms": 250.0,
                "external_fault_receipt": {"path": fp.name, "sha256": fsha}, "fault_detected": True,
                "counters": {"eligible_key_flows": 5, "cached": 5, "retried": 5, "recovery_remote_scored": 5,
                             "pending": 0, "unresolved": 0, "terminal_failed": 0, "local_fallback_completed": 0},
                "transport_observations": {"bounded_buffer_capacity": 128, "bounded_buffer_high_watermark": 5,
                    "circuit_open_delta": 1, "reverse_tcp_disconnect_delta": 1,
                    "reverse_tcp_reconnect_success_delta": 1},
                "a09_identity_before": identity, "a09_identity_after": identity,
                "windows": [{"window_index": index, "packet_gap": 0, "capture_drop": 0}],
                "restoration": {"primary_service_restored": True, "pf_restored": True, "host_restored": True},
            }
            rp = self.root / f"receipt-{index}.json"
            self.receipts.append((rp, receipt))
        self._write_input()

    def tearDown(self):
        self.tmp.cleanup()

    def _write_input(self):
        refs = [{"path": path.name, "sha256": dump(path, value)} for path, value in self.receipts]
        self.input = self.root / "input.json"
        dump(self.input, {"schema_version": 3,
             "scope": "hft_mgbs_current_hardware_2_79_transport_recovery_campaign_input_v3",
             "profile_sha256": hashlib.sha256(PROFILE.read_bytes()).hexdigest(), "evidence_root": ".",
             "campaign_id": "campaign", "candidate_id": "candidate", "receipts": refs})

    def audit(self):
        return compose_transport_recovery_campaign_v3(PROFILE, self.input)

    def mutate(self, key, value, index=0):
        target = self.receipts[index][1]
        target[key] = value
        self._write_input()

    def test_positive_is_transport_only(self):
        result = self.audit()
        self.assertTrue(result["transport_recovery_qualified"])
        self.assertEqual(result["local_fallback_completed"], 0)
        self.assertFalse(result["local_quality_qualified"])
        self.assertFalse(result["production_high_availability_qualified"])

    def test_rejects_self_reported_steps(self):
        self.mutate("steps", ["fault_detected"])
        self.assertIn("receipts.0.self_reported_or_local_fallback_fields", self.audit()["errors"])

    def test_rejects_duplicate_trial(self):
        self.mutate("trial_id", "trial-0", 1)
        self.assertIn("campaign.unique_trials", self.audit()["errors"])

    def test_rejects_a09_identity_drift(self):
        changed = dict(self.receipts[0][1]["a09_identity_after"]); changed["model"] = "f" * 64
        self.mutate("a09_identity_after", changed)
        self.assertIn("receipts.0.a09_identity_drift", self.audit()["errors"])

    def test_rejects_over_300ms_and_unresolved(self):
        self.mutate("recovery_ms", 300.01)
        counters = dict(self.receipts[0][1]["counters"]); counters["unresolved"] = 1
        self.mutate("counters", counters)
        errors = self.audit()["errors"]
        self.assertIn("receipts.0.recovery_ms", errors)
        self.assertIn("receipts.0.unresolved_or_local_completion", errors)

    def test_rejects_packet_gap(self):
        self.mutate("windows", [{"window_index": 0, "packet_gap": 1, "capture_drop": 0}])
        self.assertIn("receipts.0.packet_continuity", self.audit()["errors"])

    def test_rejects_missing_external_injection_hash(self):
        self.mutate("external_fault_receipt", {"path": "fault-0.json"})
        self.assertIn("receipts.0.external_fault_receipt", self.audit()["errors"])

    def test_rejects_local_field_forgery(self):
        counters = dict(self.receipts[0][1]["counters"]); counters["local_fallback_completed"] = 5
        self.mutate("counters", counters)
        self.assertIn("receipts.0.unresolved_or_local_completion", self.audit()["errors"])


if __name__ == "__main__":
    unittest.main()
