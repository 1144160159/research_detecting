import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CounterfactualConflictGateQueueTests(unittest.TestCase):
    def test_self_algorithm_protocol_freezes_before_wait(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_mal_tls_counterfactual_conflict_gate.sh"
        ).read_text(encoding="utf-8")
        freeze = text.index("create_mal_tls_counterfactual_conflict_gate_protocol.py")
        wait = text.index('until [[ -f "$PREREQUISITE" ]]')
        run = text.index("run_mal_tls_counterfactual_conflict_gate.sh")
        self.assertLess(freeze, wait)
        self.assertLess(wait, run)
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', text)

    def test_grood_waits_for_self_algorithm_not_geometry_directly(self) -> None:
        text = (
            ROOT / "scripts" / "wait_and_run_strict_v4_grood_pilot.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("mal_tls_counterfactual_conflict_gate_seed201/pilot_complete", text)
        self.assertIn("CAEOS-EMTD-counterfactual-gate-20260721", text)
        self.assertNotIn("mal_tls_geometry_preserving_adapter_seed195/analysis.json", text)


if __name__ == "__main__":
    unittest.main()
