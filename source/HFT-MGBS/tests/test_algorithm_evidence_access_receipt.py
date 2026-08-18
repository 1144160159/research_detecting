from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = (
    ROOT
    / "docs"
    / "experiments"
    / "2026-08-13-algorithm-evidence-access-three-route.json"
)


class AlgorithmEvidenceAccessReceiptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RECEIPT.read_text(encoding="utf-8"))

    def test_three_access_routes_are_explicit_and_read_only(self):
        self.assertTrue(self.value["read_only"])
        self.assertEqual(len(self.value["routes"]), 3)
        self.assertEqual(
            [route["route_id"] for route in self.value["routes"]],
            [
                "local_direct_gpu_mapped_ssh",
                "physical_host_to_gpu",
                "local_workspace_and_archives",
            ],
        )

    def test_internal_22_is_not_promoted_to_the_gpu_endpoint(self):
        route = self.value["routes"][1]
        internal = route["internal_port_22"]
        self.assertFalse(internal["same_ssh_endpoint_as_mapped_gpu"])
        self.assertFalse(internal["accepted_as_gpu_evidence_source"])
        self.assertNotEqual(
            internal["ed25519_sha256_fingerprint"],
            internal["trusted_mapped_gpu_ed25519_sha256_fingerprint"],
        )

    def test_missing_remote_bytes_remain_null_and_fail_closed(self):
        candidates = self.value["candidate_evidence_status"]
        self.assertEqual(len(candidates), 10)
        self.assertTrue(all(item["size_bytes"] is None for item in candidates))
        self.assertTrue(all(item["sha256"] is None for item in candidates))
        self.assertEqual(self.value["retrieved_size_sha_schema_count"], 0)
        self.assertEqual(self.value["retrieved_paired_metric_count"], 2)
        self.assertFalse(self.value["full_ten_candidate_evidence_complete"])
        self.assertFalse(self.value["algorithm_only_practical_optimum_proven"])
        self.assertFalse(self.value["production_joint_optimum_proven"])
        self.assertFalse(self.value["final_pareto_ingestion_allowed"])


if __name__ == "__main__":
    unittest.main()
