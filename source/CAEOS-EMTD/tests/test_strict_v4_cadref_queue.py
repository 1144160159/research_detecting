from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StrictV4CADRefQueueTests(unittest.TestCase):
    def test_cadref_waits_for_actsub_and_freezes_before_running(self) -> None:
        watcher = (ROOT / "scripts" / "wait_and_run_strict_v4_cadref_pilot.sh").read_text(
            encoding="utf-8"
        )
        runner = (ROOT / "scripts" / "run_strict_v4_cadref_pilot.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("strict_v4_actsub_scale_fixed_pilot_seed7", watcher)
        self.assertIn("branch_complete", watcher)
        freeze = runner.index("--protocol-only")
        gate = runner.index("create_strict_v4_cadref_expansion_gate.py")
        execute = runner.index('> "$RESULT_ROOT/execution.log"')
        full_summary = runner.index("summarize_strict_v4_cadref_full.py")
        full_complete = runner.index('touch "$RESULT_ROOT/full102_complete"')
        self.assertLess(freeze, gate)
        self.assertLess(gate, execute)
        self.assertLess(full_summary, full_complete)

    def test_postefficiency_chain_waits_for_cadref(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("strict_v4_cadref_family_pilot_seed7", text)
        self.assertIn('CADREF_COMPLETE="$CADREF_ROOT/branch_complete"', text)
        self.assertIn("run_strict_v4_cadref", text)


if __name__ == "__main__":
    unittest.main()
