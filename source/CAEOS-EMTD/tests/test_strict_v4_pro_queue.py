from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StrictV4PROQueueTests(unittest.TestCase):
    def test_pro_waits_for_gsc_and_freezes_before_running(self) -> None:
        watcher = (ROOT / "scripts" / "wait_and_run_strict_v4_pro_pilot.sh").read_text(
            encoding="utf-8"
        )
        runner = (ROOT / "scripts" / "run_strict_v4_pro_pilot.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("strict_v4_gsc_pilot_seed7", watcher)
        self.assertIn("pilot_complete", watcher)
        freeze = runner.index("--protocol-only")
        gate = runner.index("create_strict_v4_pro_expansion_gate.py")
        execute = runner.index('> "$RESULT_ROOT/execution.log"')
        self.assertLess(freeze, gate)
        self.assertLess(gate, execute)

    def test_postefficiency_claim_chain_waits_for_pro_branch(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("strict_v4_pro_msp_fixed_pilot_seed7", text)
        self.assertIn('PRO_COMPLETE="$PRO_ROOT/branch_complete"', text)
        self.assertIn("run_strict_v4_pro", text)


if __name__ == "__main__":
    unittest.main()
