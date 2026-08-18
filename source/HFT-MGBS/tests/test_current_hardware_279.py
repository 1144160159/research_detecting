from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.current_hardware_279 import compose_current_hardware_audit


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "configs" / "current_hardware_2_79_release_profile_v1.json"
CURRENT = ROOT / "configs" / "current_hardware_2_79_current_evidence_v1.json"


def write_json(path: Path, value: object) -> str:
    data = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def histogram(kind: str):
    if kind == "capture":
        bounds = [50.0, 100.0, 500.0]
    elif kind == "internal":
        bounds = [1000.0, 5000.0, 50000.0]
    else:
        bounds = [5000.0, 10000.0, 50000.0]
    return {"upper_bounds_us": bounds, "bucket_counts": [990, 9, 1], "overflow_count": 0}


def quality_counts():
    confusion = {"tp": 900, "fp": 40, "fn": 100, "tn": 960}
    return {
        "group_confusions": [dict(confusion), dict(confusion)],
        "independent_confusion": dict(confusion),
        "score_buckets_descending": [
            {"score": 0.9, "positive_count": 900, "negative_count": 40},
            {"score": 0.1, "positive_count": 100, "negative_count": 960},
        ],
        "calibration_bins": [
            {"count": 1000, "confidence_sum": 900.0, "correct_count": 900},
            {"count": 1000, "confidence_sum": 950.0, "correct_count": 950},
        ],
        "events": {"matched": 80, "total": 100},
    }


class CurrentHardware279Test(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.profile_sha = hashlib.sha256(PROFILE.read_bytes()).hexdigest()
        self.campaign_id = "current-hardware-positive-v1"

    def tearDown(self):
        self.temporary.cleanup()

    def probe(self, available=False):
        payload = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_xdp_probe_v1",
            "campaign_id": self.campaign_id,
            "profile_sha256": self.profile_sha,
            "attempted_backend": "xdp_skb",
            "attach_exit_status": 0 if available else 95,
            "capture_probe_exit_status": 0 if available else 95,
            "packets_observed": 1000 if available else 0,
            "interface_state_before_sha256": "a" * 64,
            "interface_state_after_sha256": "a" * 64,
            "xdp_program_ids_before": [],
            "xdp_program_ids_after": [],
        }
        path = self.root / "xdp_probe.json"
        return {"path": path.name, "sha256": write_json(path, payload)}

    def raw_run(self, candidate_id, backend, mode, repeat, mpps):
        windows = []
        packets = int(mpps * 1_000_000)
        for index in range(15):
            windows.append(
                {
                    "window_index": index,
                    "duration_s": 1.0,
                    "packets_offered": packets,
                    "packets_received": packets,
                    "nic_rx_missed": 0,
                    "nic_rx_errors": 0,
                    "socket_drops": 0,
                    "sequence_gaps": 0,
                    "parse_rejected": 0,
                    "feature_update_rejected": 0,
                    "budget_overrun_count": 0,
                    "key_flow_eligible": 100,
                    "key_flow_completed": 100,
                    "key_flow_skipped_due_budget": 0,
                    "gpu_queue_full_count": 0,
                    "inference_batch_failure_count": 0,
                    "kernel_entry_to_shard": histogram("capture"),
                    "kernel_entry_to_feature_enqueue": histogram("feature"),
                    "internal_feature_enqueue": histogram("internal"),
                    "end_to_end": histogram("e2e"),
                    "resource_sample": {
                        "host_cpu_fraction": 0.5,
                        "host_memory_fraction": 0.4,
                        "service_gpu_fraction": 0.0,
                        "service_gpu_memory_fraction": 0.0,
                    },
                }
            )
        fallback = None
        if mode == "fallback":
            start = repeat * 1_000_000_000
            fallback = {
                "trial_id": f"{candidate_id}-fault-{repeat}",
                "start_monotonic_ns": start,
                "end_monotonic_ns": start + 100_000_000,
                "steps": [
                    "fault_injection_observed",
                    "local_fallback_activated",
                    "post_switch_traffic_observed",
                    "primary_recovered",
                    "fallback_state_cleared",
                    "capture_backend_restored",
                    "interfaces_restored",
                    "final_state_verification",
                ],
                "recovery_ms": 100.0,
                "transition_packet_gap": 0,
                "capture_drop_during_fallback": 0,
                "primary_restored": True,
                "host_restored": True,
            }
        payload = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_raw_run_v1",
            "campaign_id": self.campaign_id,
            "profile_sha256": self.profile_sha,
            "candidate_id": candidate_id,
            "backend": backend,
            "mode": mode,
            "repeat_index": repeat,
            "pair_id": f"{candidate_id}-pair-{repeat}",
            "run_id": f"{candidate_id}-{mode}-{repeat}",
            "generator_run_id": f"generator-{candidate_id}-{mode}-{repeat}",
            "hardware_identity_sha256": "1" * 64,
            "code_sha256": "2" * 64,
            "input_sha256": "3" * 64,
            "runtime_manifest_sha256": "4" * 64,
            "capture_binary_sha256": "5" * 64,
            "windows": windows,
            "quality_counts": quality_counts(),
            "fallback_trial": fallback,
        }
        path = self.root / "runs" / f"{candidate_id}-{mode}-{repeat}.json"
        return {"mode": mode, "repeat_index": repeat, "path": str(path.relative_to(self.root)), "sha256": write_json(path, payload)}

    def candidate(self, candidate_id, backend, mpps):
        return {
            "candidate_id": candidate_id,
            "backend": backend,
            "raw_runs": [
                self.raw_run(candidate_id, backend, mode, repeat, mpps)
                for mode in ("normal", "fallback")
                for repeat in (1, 2, 3)
            ],
        }

    def manifest(self, candidates, *, xdp_available=False, claims=True):
        return {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_evidence_manifest_v1",
            "campaign_id": self.campaign_id,
            "profile_sha256": self.profile_sha,
            "evidence_root": ".",
            "xdp_probe": self.probe(xdp_available),
            "candidates": candidates,
            "legacy_discovery": [],
            "claimed_state": {
                "candidate_evidence_qualified": claims,
                "full_pipeline_qualified": claims,
                "production_release_accepted": False,
                "final_pareto_ingestion_allowed": False,
            },
        }

    def compose(self, manifest):
        path = self.root / "evidence_manifest.json"
        write_json(path, manifest)
        return compose_current_hardware_audit(PROFILE, path)

    def test_current_pending_and_legacy_b2_are_fail_closed(self):
        result = compose_current_hardware_audit(PROFILE, CURRENT)
        self.assertTrue(result["audit_complete"])
        self.assertEqual(result["legacy_discovery_count"], 1)
        self.assertEqual(result["legacy_qualification_count"], 0)
        self.assertFalse(result["candidate_evidence_qualified"])
        self.assertFalse(result["full_pipeline_qualified"])
        self.assertFalse(result["production_release_accepted"])

    def test_tpacket_can_win_only_after_xdp_probe_and_two_non_xdp_evaluations(self):
        result = self.compose(
            self.manifest(
                [
                    self.candidate("tpacket-qualified", "tpacket_v3", 2.80),
                    self.candidate("dpdk-below-target", "dpdk", 2.60),
                ]
            )
        )
        self.assertTrue(result["candidate_evidence_qualified"], result["errors"])
        self.assertTrue(result["full_pipeline_qualified"])
        self.assertEqual(result["selected_candidate"], "tpacket-qualified")
        self.assertFalse(result["production_release_accepted"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_xdp_priority_applies_only_after_full_pipeline_qualification(self):
        result = self.compose(
            self.manifest(
                [
                    self.candidate("xdp-qualified", "xdp_skb", 2.79),
                    self.candidate("tpacket-faster", "tpacket_v3", 3.00),
                    self.candidate("dpdk-qualified", "dpdk", 2.90),
                ],
                xdp_available=True,
            )
        )
        self.assertTrue(result["candidate_evidence_qualified"], result["errors"])
        self.assertEqual(result["selected_candidate"], "xdp-qualified")

    def test_one_historical_or_formal_repeat_cannot_count_as_three(self):
        candidate = self.candidate("tpacket-incomplete", "tpacket_v3", 2.80)
        candidate["raw_runs"] = candidate["raw_runs"][:2]
        result = self.compose(self.manifest([candidate], claims=False))
        audit = next(item for item in result["candidate_audits"] if item["candidate_id"] == "tpacket-incomplete")
        self.assertFalse(audit["evaluation_complete"])
        self.assertIn("candidate.repeat_matrix", audit["errors"])
        self.assertFalse(result["candidate_evidence_qualified"])

    def test_raw_hash_drift_and_self_reported_acceptance_fail_closed(self):
        candidate = self.candidate("tpacket-tamper", "tpacket_v3", 2.80)
        first = self.root / candidate["raw_runs"][0]["path"]
        payload = json.loads(first.read_text("utf-8"))
        payload["accepted"] = True
        first.write_text(json.dumps(payload), encoding="utf-8")
        result = self.compose(self.manifest([candidate], claims=False))
        audit = next(item for item in result["candidate_audits"] if item["candidate_id"] == "tpacket-tamper")
        self.assertIn("candidate.raw_runs.0.sha256", audit["errors"])
        self.assertFalse(result["candidate_evidence_qualified"])

        candidate["raw_runs"][0]["sha256"] = hashlib.sha256(first.read_bytes()).hexdigest()
        result = self.compose(self.manifest([candidate], claims=False))
        audit = next(item for item in result["candidate_audits"] if item["candidate_id"] == "tpacket-tamper")
        self.assertIn("candidate.raw_runs.0.self_reported_state", audit["errors"])
        self.assertFalse(result["candidate_evidence_qualified"])

    def test_per_window_rate_gate_cannot_be_replaced_by_an_average(self):
        candidate = self.candidate("tpacket-average-bypass", "tpacket_v3", 3.00)
        reference = candidate["raw_runs"][0]
        path = self.root / reference["path"]
        payload = json.loads(path.read_text("utf-8"))
        payload["windows"][0]["packets_offered"] = 2_780_000
        payload["windows"][0]["packets_received"] = 2_780_000
        reference["sha256"] = write_json(path, payload)
        result = self.compose(self.manifest([candidate], claims=False))
        audit = next(item for item in result["candidate_audits"] if item["candidate_id"] == "tpacket-average-bypass")
        self.assertIn("candidate.raw_runs.0.windows.0.throughput", audit["errors"])
        self.assertFalse(audit["qualified"])

    def test_duplicate_identities_and_overlapping_faults_fail_closed(self):
        candidate = self.candidate("tpacket-identity-bypass", "tpacket_v3", 2.80)
        first = self.root / candidate["raw_runs"][0]["path"]
        second_reference = candidate["raw_runs"][1]
        second = self.root / second_reference["path"]
        first_payload = json.loads(first.read_text("utf-8"))
        second_payload = json.loads(second.read_text("utf-8"))
        second_payload["run_id"] = first_payload["run_id"]
        second_reference["sha256"] = write_json(second, second_payload)
        fallback_refs = [item for item in candidate["raw_runs"] if item["mode"] == "fallback"]
        first_fallback = self.root / fallback_refs[0]["path"]
        second_fallback = self.root / fallback_refs[1]["path"]
        left = json.loads(first_fallback.read_text("utf-8"))
        right = json.loads(second_fallback.read_text("utf-8"))
        right["fallback_trial"]["start_monotonic_ns"] = left["fallback_trial"]["end_monotonic_ns"]
        fallback_refs[1]["sha256"] = write_json(second_fallback, right)
        result = self.compose(self.manifest([candidate], claims=False))
        audit = next(item for item in result["candidate_audits"] if item["candidate_id"] == "tpacket-identity-bypass")
        self.assertTrue(any(error.endswith(".run_id") for error in audit["errors"]))
        self.assertIn("candidate.fallback_trials", audit["errors"])
        self.assertFalse(audit["qualified"])

    def test_lowered_profile_cannot_create_a_new_acceptance_scope(self):
        profile = json.loads(PROFILE.read_text("utf-8"))
        profile["traffic_contract"]["nominal_mpps"] = 2.0
        path = self.root / "lowered-profile.json"
        write_json(path, profile)
        result = compose_current_hardware_audit(path, CURRENT)
        self.assertFalse(result["audit_complete"])
        self.assertFalse(result["candidate_evidence_qualified"])

    def test_cli_current_pending_returns_two_without_pythonpath(self):
        output = self.root / "audit.json"
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/compose_current_hardware_279.py",
                "--profile",
                str(PROFILE),
                "--evidence",
                str(CURRENT),
                "--output",
                str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            env={key: value for key, value in __import__("os").environ.items() if key != "PYTHONPATH"},
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertFalse(json.loads(output.read_text("utf-8"))["candidate_evidence_qualified"])


if __name__ == "__main__":
    unittest.main()
