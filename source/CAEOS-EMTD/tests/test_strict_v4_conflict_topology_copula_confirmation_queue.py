from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ConflictTopologyConfirmationQueueTests(unittest.TestCase):
    def test_positive_branch_freezes_before_confirmation_run(self) -> None:
        text = (
            ROOT
            / "scripts"
            / "wait_and_run_strict_v4_conflict_topology_copula_confirmation_branch.sh"
        ).read_text(encoding="utf-8")
        decision = text.index("freeze_for_reserved_seed_confirmation")
        freeze = text.index(
            "create_strict_v4_conflict_topology_copula_confirmation_protocol.py"
        )
        run = text.index("run_strict_v4_conflict_topology_copula_confirmation.sh")
        complete = text.index('touch "$BRANCH_ROOT/branch_complete"')
        self.assertLess(decision, freeze)
        self.assertLess(freeze, run)
        self.assertLess(run, complete)

    def test_wdiscood_waits_for_confirmation_branch(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_strict_v4_wdiscood_pilot.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "strict_v4_conflict_topology_copula_confirmation_branch/branch_complete",
            text,
        )
        self.assertNotIn(
            "strict_v4_conflict_topology_copula_pilot_seed7/pilot_complete", text
        )


if __name__ == "__main__":
    unittest.main()
