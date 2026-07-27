import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EfficiencyV5RecoveryScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (
            ROOT / "scripts" / "run_strict_v4_final_efficiency_v5_recovery.sh"
        ).read_text(encoding="utf-8")
        cls.reuse = (
            ROOT / "prepare_strict_v4_final_efficiency_v5_reuse.py"
        ).read_text(encoding="utf-8")

    def test_freezes_new_protocol_and_plan_before_reuse(self) -> None:
        self.assertLess(
            self.text.index("create_strict_v4_final_efficiency_protocol_v2.py"),
            self.text.index("prepare_strict_v4_final_efficiency_v5_reuse.py"),
        )
        self.assertLess(
            self.text.index("create_strict_v4_final_efficiency_execution_plan_v2.py"),
            self.text.index("prepare_strict_v4_final_efficiency_v5_reuse.py"),
        )

    def test_reuse_forbids_old_timings_and_learned_candidate_capture(self) -> None:
        self.assertIn('"learned_blend_candidate_capture_reuse_allowed": False', self.reuse)
        self.assertIn('"standalone_benchmark_reuse_allowed": False', self.reuse)
        self.assertIn('"paired_efficiency_metric_reuse_allowed": False', self.reuse)
        self.assertIn("selected == CAUCHY_RISK", self.reuse)

    def test_requires_failure_evidence_and_runtime_hash_change(self) -> None:
        self.assertIn("learned_tail_runtime_shadow_rank_instability", self.reuse)
        self.assertIn("archived runtime does not match old protocol", self.reuse)
        self.assertIn("active runtime does not match new protocol", self.reuse)
        self.assertIn("runtime fix did not change implementation hash", self.reuse)

    def test_waits_for_five_consecutive_idle_samples(self) -> None:
        self.assertIn('idle_samples=0', self.text)
        self.assertIn('idle_samples=$((idle_samples + 1))', self.text)
        self.assertIn('sleep 30', self.text)


if __name__ == "__main__":
    unittest.main()
