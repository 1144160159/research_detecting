from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StrictV4FisherRaoQueueTests(unittest.TestCase):
    def test_watcher_waits_for_cadref(self) -> None:
        watcher = (ROOT / "scripts" / "wait_and_run_strict_v4_fisher_rao_pilot.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("strict_v4_cadref_family_pilot_seed7", watcher)
        self.assertIn('CADREF_ROOT/analysis.json', watcher)
        self.assertIn('CADREF_ROOT/branch_complete', watcher)
        self.assertLess(watcher.index("until [["), watcher.index("run_strict_v4_fisher_rao_pilot.sh"))

    def test_runner_freezes_protocol_and_gate_before_execution(self) -> None:
        runner = (ROOT / "scripts" / "run_strict_v4_fisher_rao_pilot.sh").read_text(
            encoding="utf-8"
        )
        protocol = runner.index("--protocol-only")
        gate = runner.index("create_strict_v4_fisher_rao_expansion_gate.py")
        execution = runner.index('> "$RESULT_ROOT/execution.log"')
        self.assertLess(protocol, gate)
        self.assertLess(gate, execution)

    def test_postefficiency_chain_waits_for_fisher_rao(self) -> None:
        chain = (
            ROOT / "scripts" / "wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("strict_v4_fisher_rao_family_pilot_seed7", chain)
        self.assertIn('FISHER_RAO_ROOT/analysis.json', chain)
        self.assertIn('FISHER_RAO_ROOT/branch_complete', chain)
        self.assertIn("run_strict_v4_fisher_rao", chain)


if __name__ == "__main__":
    unittest.main()
