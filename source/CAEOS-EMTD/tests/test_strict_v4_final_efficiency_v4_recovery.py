import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EfficiencyV4RecoveryTests(unittest.TestCase):
    def test_recovery_uses_fresh_roots_and_consecutive_idle_samples(self) -> None:
        text = (ROOT / "scripts" / "run_strict_v4_final_efficiency_v4_recovery.sh").read_text(
            encoding="utf-8"
        )
        for suffix in (
            "protocol_v4",
            "execution_plan_v4",
            "final_efficiency_v4",
        ):
            self.assertIn(suffix, text)
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', text)
        self.assertIn("sleep 30", text)
        self.assertLess(
            text.index('while [[ "$idle_samples" -lt 5 ]]'),
            text.index('"$PYTHON" execute_strict_v4_final_efficiency_plan_v2.py'),
        )


if __name__ == "__main__":
    unittest.main()
