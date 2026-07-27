import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh"


class PostEfficiencyClaimChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SCRIPT.read_text(encoding="utf-8")

    def test_waits_for_efficiency_v5_and_last_self_algorithm_candidate(self) -> None:
        self.assertIn("strict_v4_final_efficiency_v5", self.text)
        self.assertIn("recovery_complete", self.text)
        self.assertIn("strict_v4_grood_pilot_seed7", self.text)
        self.assertIn("GROOD_COMPLETE", self.text)
        self.assertNotIn("strict_v4_final_efficiency_v2/summary.json", self.text)

    def test_frozen_candidate_corruption_protocol_is_not_recreated(self) -> None:
        self.assertIn(
            "83415875d1f26c8f1c948dac65f498110a5f3a6080e2aba4fd4407aa05eea4f4",
            self.text,
        )
        self.assertNotIn("create_strict_v4_postselection_corruption_protocol.py", self.text)
        self.assertIn("frozen manifest hash mismatch", self.text)

    def test_chain_order_is_serial_and_final_audit_uses_v5(self) -> None:
        candidate = self.text.index("run_strict_v4_postselection_corruption.py")
        comparative_freeze = self.text.index(
            "create_strict_v4_comparative_corruption_protocol.py"
        )
        comparative_run = self.text.index("run_strict_v4_comparative_corruption.py")
        final_audit = self.text.index("audit_strict_v4_final_paper_readiness.py")
        self.assertLess(candidate, comparative_freeze)
        self.assertLess(comparative_freeze, comparative_run)
        self.assertLess(comparative_run, final_audit)
        self.assertIn('--efficiency-summary "$EFFICIENCY_SUMMARY"', self.text)

    def test_requires_stable_gpu_and_experiment_process_idle_window(self) -> None:
        self.assertIn("nvidia-smi --query-compute-apps=pid,process_name", self.text)
        self.assertIn("pgrep -af", self.text)
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', self.text)
        self.assertIn("sleep 30", self.text)

    def test_refuses_late_comparative_protocol_freeze(self) -> None:
        self.assertIn("find \"$COMPARATIVE_RUN_ROOT\" -name paired_corruption.json", self.text)
        self.assertIn(
            "refusing to freeze comparative protocol after paired results exist",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
