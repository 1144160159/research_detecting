import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OptimizedEfficiencyQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.watcher = (
            ROOT / "scripts" / "wait_and_run_strict_v4_optimized_efficiency_v6.sh"
        ).read_text(encoding="utf-8")
        cls.wdisc = (
            ROOT / "scripts" / "wait_and_run_strict_v4_wdiscood_pilot.sh"
        ).read_text(encoding="utf-8")

    def test_protocol_freezes_before_waiting_and_execution(self) -> None:
        freeze = self.watcher.index("create_strict_v4_optimized_efficiency_protocol.py")
        wait = self.watcher.index('until [[ -f "$V5_COMPLETE"')
        execute = self.watcher.index(
            '\n"$PYTHON" run_strict_v4_optimized_efficiency_matrix.py'
        )
        self.assertLess(freeze, wait)
        self.assertLess(wait, execute)

    def test_waits_for_v5_and_ctc_confirmation(self) -> None:
        self.assertIn("strict_v4_final_efficiency_v5/recovery_complete", self.watcher)
        self.assertIn(
            "strict_v4_conflict_topology_copula_confirmation_branch/branch_complete",
            self.watcher,
        )

    def test_requires_five_sample_idle_window(self) -> None:
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', self.watcher)
        self.assertIn("nvidia-smi --query-compute-apps=pid,process_name", self.watcher)
        self.assertIn("pgrep -af", self.watcher)
        self.assertIn("sleep 30", self.watcher)

    def test_wdiscood_waits_for_optimized_branch(self) -> None:
        self.assertIn(
            "results/strict_v4_optimized_efficiency_v6/branch_complete", self.wdisc
        )
        self.assertIn('&& -f "$OPTIMIZED_EFFICIENCY_COMPLETE"', self.wdisc)


if __name__ == "__main__":
    unittest.main()
