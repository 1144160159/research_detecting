import unittest

from hft_mgbs.evidence import REQUIRED_EVIDENCE, CandidateEvidenceEnvelope, audit_candidate_evidence
from hft_mgbs.optimization import CandidateMetrics


def metrics():
    return CandidateMetrics(
        name="candidate",
        quality=0.9,
        gain_per_cost=1.0,
        throughput_mpps=1.0,
        packet_drop_count=0,
        p99_latency_us=100.0,
        p999_latency_us=200.0,
        cpu_utilization=0.5,
        gpu_utilization=0.5,
        memory_utilization=0.5,
        gpu_memory_utilization=0.5,
        budget_overrun_count=0,
        key_flow_coverage=0.99,
        fallback_recovery_s=1.0,
        complexity=0.2,
    )


class EvidenceGateTests(unittest.TestCase):
    def test_offline_partial_evidence_is_rejected(self):
        envelope = CandidateEvidenceEnvelope(
            metrics(),
            {name: name in {"budget_overrun", "key_flow_coverage"} for name in REQUIRED_EVIDENCE},
            "complete",
            3,
            "a" * 64,
            "b" * 64,
        )
        audit = audit_candidate_evidence(envelope)
        self.assertFalse(audit.accepted)
        self.assertIn("nic_packet_drop", audit.errors[0])
        self.assertIn("end_to_end_p99", audit.errors[0])

    def test_complete_live_evidence_is_accepted(self):
        envelope = CandidateEvidenceEnvelope(
            metrics(),
            {name: True for name in REQUIRED_EVIDENCE},
            "complete",
            3,
            "a" * 64,
            "b" * 64,
        )
        self.assertTrue(audit_candidate_evidence(envelope).accepted)

    def test_incomplete_manifest_and_repeats_are_rejected(self):
        envelope = CandidateEvidenceEnvelope(
            metrics(),
            {name: True for name in REQUIRED_EVIDENCE},
            "running",
            1,
            "bad",
            "bad",
        )
        errors = audit_candidate_evidence(envelope).errors
        self.assertIn("manifest_not_complete", errors)
        self.assertIn("measured_repeats_below_3", errors)
        self.assertIn("invalid_code_sha256", errors)


if __name__ == "__main__":
    unittest.main()
