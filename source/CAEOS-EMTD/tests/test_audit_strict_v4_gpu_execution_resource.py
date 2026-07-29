from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from audit_strict_v4_gpu_execution_resource import audit
from strict_v4_cicids2017_attack_family import canonical_hash


class GpuExecutionResourceAuditTests(unittest.TestCase):
    def write_evidence(self, root: Path, utilization: list[float]) -> Path:
        value = {
            "passes": True,
            "peak_gpu_memory_mib": 1000.0,
            "peak_gpu_utilization_percent": max(utilization),
            "torch_peak_memory_allocated_mib": 900.0,
            "torch_peak_memory_reserved_mib": 950.0,
            "sample_errors": [],
            "samples": [
                {"utilization_percent": item} for item in utilization
            ],
        }
        value["manifest_sha256"] = canonical_hash(value)
        path = root / "gpu_execution.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_passes_when_mean_and_memory_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_evidence(
                Path(directory), [40.0, 60.0, 80.0]
            )
            result = audit(
                path,
                minimum_mean_utilization=50.0,
                maximum_peak_memory_mib=45000.0,
            )
        self.assertEqual("pass", result["state"])
        self.assertEqual(60.0, result["observed"]["mean_gpu_utilization_percent"])

    def test_fails_low_mean_utilization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_evidence(Path(directory), [10.0, 20.0])
            result = audit(
                path,
                minimum_mean_utilization=50.0,
                maximum_peak_memory_mib=45000.0,
            )
        self.assertEqual("fail", result["state"])
        self.assertFalse(
            result["gates"]["mean_gpu_utilization_at_least_minimum"]
        )


if __name__ == "__main__":
    unittest.main()
