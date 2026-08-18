from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.runtime_identity import load_runtime_identity, validate_runtime_identity


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "docs" / "experiments" / "current_runtime_identity_v1.json"
SHA = "a" * 64


def valid_receipt() -> dict:
    return {
        "schema_version": 1,
        "scope": "hft_mgbs_split_runtime_identity",
        "read_only": True,
        "verified": True,
        "runtime_manifest": {
            "path": "/opt/project/runs/split_deployment/runtime_manifest.json",
            "expected_sha256": SHA,
            "actual_sha256": SHA,
            "declared_pid": 1888,
        },
        "gpu_process": {
            "pid": 1888,
            "alive": True,
            "cmdline": "python -m hft_mgbs.gpu_service",
            "exe": "/usr/bin/python3",
            "cwd": "/opt/project",
        },
        "gpu_listener_50051": {"endpoint": "0.0.0.0:50051", "owner_pid": 1888},
        "gpu_localhost_health": {"ok": True, "failures": []},
        "physical_to_gpu_50051": {"reachable": True, "failure": None},
        "physical_reverse_50052": {"listener": True, "established": True},
    }


class RuntimeIdentityTest(unittest.TestCase):
    def test_valid_identity(self):
        self.assertEqual(validate_runtime_identity(valid_receipt()), {"verified": True, "errors": []})

    def test_current_fact_is_explicitly_unverified(self):
        receipt = load_runtime_identity(CURRENT)
        result = validate_runtime_identity(receipt)
        self.assertFalse(result["verified"])
        self.assertIn("runtime_manifest.sha256_mismatch", result["errors"])
        self.assertIn("runtime_manifest.listener_pid_mismatch", result["errors"])
        self.assertIn("physical_to_gpu_50051.reachable", result["errors"])
        self.assertIn("physical_reverse_50052.listener", result["errors"])
        self.assertIn("physical_reverse_50052.established", result["errors"])

    def test_listener_must_belong_to_bound_process(self):
        receipt = valid_receipt()
        receipt["gpu_listener_50051"]["owner_pid"] = 9
        receipt["verified"] = False
        self.assertIn("gpu_listener_50051.owner_process_mismatch", validate_runtime_identity(receipt)["errors"])

    def test_process_identity_fields_are_mandatory(self):
        receipt = valid_receipt()
        receipt["gpu_process"]["exe"] = None
        receipt["verified"] = False
        self.assertIn("gpu_process.exe", validate_runtime_identity(receipt)["errors"])

    def test_health_failures_fail_closed(self):
        receipt = valid_receipt()
        receipt["gpu_localhost_health"]["failures"] = ["timeout"]
        receipt["verified"] = False
        self.assertIn("gpu_localhost_health.failures", validate_runtime_identity(receipt)["errors"])

    def test_claim_cannot_override_recomputation(self):
        receipt = valid_receipt()
        receipt["verified"] = False
        result = validate_runtime_identity(receipt)
        self.assertFalse(result["verified"])
        self.assertEqual(result["errors"], ["verified.claim_mismatch"])

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_runtime_identity(path)


if __name__ == "__main__":
    unittest.main()
