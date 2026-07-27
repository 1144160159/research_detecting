from __future__ import annotations

import unittest
from pathlib import Path


class VGRFSelectedSystemExecutionWatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "wait_and_run_strict_v4_vgrf_selected_system_execution.sh"
        ).read_text(encoding="utf-8")

    def test_pairwise_path_exits_without_system_execution(self) -> None:
        self.assertIn('if [[ "$selected" == "caeos_pairwise" ]]', self.text)
        self.assertIn(
            "Pairwise selected; VGRF system execution not required",
            self.text,
        )

    def test_execution_protocol_binds_corruption_protocol(self) -> None:
        self.assertIn("--corruption-protocol", self.text)
        self.assertIn("--implementation summarize_strict_v4", self.text)
        self.assertIn("--implementation caeos/opendetect_deployment.py", self.text)

    def test_execution_order_is_frozen(self) -> None:
        commands = (
            "run_strict_v4_vgrf_selected_system_seed317.py",
            "run_strict_v4_vgrf_selected_system_capture.py",
            "run_strict_v4_vgrf_selected_system_training_efficiency.py",
            "benchmark_strict_v4_vgrf_selected_system.py",
            "run_strict_v4_vgrf_selected_system_corruption.py",
            "summarize_strict_v4_vgrf_selected_system.py",
        )
        offsets = [self.text.rindex(command) for command in commands]
        self.assertEqual(offsets, sorted(offsets))

    def test_idle_and_low_priority_gates_are_present(self) -> None:
        self.assertIn('while [[ "$idle_samples" -lt 5 ]]', self.text)
        self.assertIn("nvidia-smi --query-compute-apps=pid", self.text)
        self.assertIn("nice -n 15 ionice -c 3", self.text)


if __name__ == "__main__":
    unittest.main()
