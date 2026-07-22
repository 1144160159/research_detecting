import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SelfAlgorithmBranchQueueTests(unittest.TestCase):
    def test_positive_geometry_branch_freezes_before_confirmation_run(self) -> None:
        text = (
            ROOT
            / "scripts"
            / "wait_and_run_mal_tls_geometry_adapter_confirmation_branch.sh"
        ).read_text(encoding="utf-8")
        decision = text.index("freeze_for_reserved_seed_confirmation")
        freeze = text.index("create_mal_tls_geometry_adapter_confirmation_protocol.py")
        run = text.index("run_mal_tls_geometry_adapter_confirmation.sh")
        complete = text.index('touch "$BRANCH_ROOT/branch_complete"')
        self.assertLess(decision, freeze)
        self.assertLess(freeze, run)
        self.assertLess(run, complete)
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', text)

    def test_next_candidate_waits_for_confirmation_branch(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_mal_tls_counterfactual_conflict_gate.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("mal_tls_geometry_adapter_confirmation_branch/branch_complete", text)
        self.assertNotIn(
            "mal_tls_geometry_preserving_adapter_seed195/pilot_complete", text
        )


if __name__ == "__main__":
    unittest.main()
