import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SelfAlgorithmFinalQueueTests(unittest.TestCase):
    def test_counterfactual_confirmation_freezes_before_run(self) -> None:
        text = (
            ROOT
            / "scripts"
            / "wait_and_run_mal_tls_counterfactual_conflict_gate_confirmation_branch.sh"
        ).read_text(encoding="utf-8")
        decision = text.index("freeze_for_reserved_seed_confirmation")
        freeze = text.index(
            "create_mal_tls_counterfactual_conflict_gate_confirmation_protocol.py"
        )
        run = text.index("run_mal_tls_counterfactual_conflict_gate_confirmation.sh")
        complete = text.index('touch "$BRANCH_ROOT/branch_complete"')
        self.assertLess(decision, freeze)
        self.assertLess(freeze, run)
        self.assertLess(run, complete)
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', text)

    def test_selection_waits_for_both_confirmation_branches(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_audit_mal_tls_self_algorithm_selection.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('"$GEOMETRY_BRANCH/branch_complete"', text)
        self.assertIn('"$COUNTERFACTUAL_BRANCH/branch_complete"', text)
        self.assertIn("audit_mal_tls_self_algorithm_selection.py", text)

    def test_grood_waits_for_selection_audit(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_strict_v4_grood_pilot.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("mal_tls_self_algorithm_selection/audit_complete", text)
        self.assertNotIn(
            "mal_tls_counterfactual_conflict_gate_seed201/pilot_complete", text
        )


if __name__ == "__main__":
    unittest.main()
