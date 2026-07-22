from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StrictV4UnifiedSelfAlgorithmQueueTests(unittest.TestCase):
    def test_selector_waits_for_both_component_and_ctc_branches(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_select_strict_v4_unified_self_algorithm.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("mal_tls_self_algorithm_selection/audit_complete", text)
        self.assertIn("strict_v4_conflict_topology_copula_confirmation_branch", text)
        self.assertIn("branch_complete", text)
        self.assertIn("select_strict_v4_unified_self_algorithm.py", text)

    def test_downstream_claim_chains_require_unified_decision(self) -> None:
        wdisc = (
            ROOT / "scripts" / "wait_and_run_strict_v4_wdiscood_pilot.sh"
        ).read_text(encoding="utf-8")
        post = (
            ROOT / "scripts" / "wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh"
        ).read_text(encoding="utf-8")
        marker = "strict_v4_unified_self_algorithm_selection/accuracy_decision_complete"
        self.assertIn(marker, wdisc)
        self.assertIn("UNIFIED_SELF_COMPLETE", post)
        self.assertIn("UNIFIED_SELF_DECISION", post)


if __name__ == "__main__":
    unittest.main()
