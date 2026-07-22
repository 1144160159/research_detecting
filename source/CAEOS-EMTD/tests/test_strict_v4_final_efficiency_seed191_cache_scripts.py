from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FinalEfficiencySeed191CacheScriptTests(unittest.TestCase):
    def test_preparation_is_gated_and_result_free(self) -> None:
        text = (
            ROOT / "scripts" / "prepare_strict_v4_final_efficiency_seed191_caches.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('test -f "$EXTERNAL_MARKER"', text)
        self.assertIn("SEED=191", text)
        self.assertIn("formal_timing_allowed", text)
        self.assertNotIn("train_hybrid_open_set.py", text)
        self.assertNotIn("train_neural_open_set.py", text)
        self.assertNotIn("metrics.json", text)

    def test_watcher_waits_for_external_completion(self) -> None:
        text = (
            ROOT
            / "scripts"
            / "wait_and_prepare_strict_v4_final_efficiency_seed191_caches.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('until [[ -f "$EXTERNAL_MARKER" ]]', text)
        freeze_position = text.index("freeze_strict_v4_final_efficiency_protocol_v2.sh")
        prepare_position = text.index(
            "prepare_strict_v4_final_efficiency_seed191_caches.sh"
        )
        plan_position = text.index(
            "create_strict_v4_final_efficiency_execution_plan_v2.py"
        )
        execute_position = text.index(
            "execute_strict_v4_final_efficiency_plan_v2.py"
        )
        summary_position = text.index("summarize_strict_v4_final_efficiency_v2.py")
        corruption_position = text.index("run_strict_v4_postselection_corruption.py")
        self.assertLess(freeze_position, prepare_position)
        self.assertLess(prepare_position, plan_position)
        self.assertLess(plan_position, execute_position)
        self.assertLess(execute_position, summary_position)
        self.assertLess(summary_position, corruption_position)
        self.assertIn("prepare_strict_v4_final_efficiency_seed191_caches.sh", text)
        self.assertIn("--query-compute-apps=pid", text)
        self.assertIn("runs/strict_v4_final_efficiency_v2", text)

    def test_protocol_freeze_binds_all_runtime_implementations(self) -> None:
        text = (
            ROOT / "scripts" / "freeze_strict_v4_final_efficiency_protocol_v2.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('test -f "$EXTERNAL_MARKER"', text)
        self.assertIn("--candidate-runtime", text)
        self.assertIn("--candidate-capture", text)
        self.assertIn("--candidate-benchmark", text)
        self.assertIn("--comparator-runtime", text)
        self.assertIn("--comparator-capture", text)
        self.assertIn("--comparator-training-capture", text)
        self.assertIn("--comparator-benchmark", text)
        self.assertIn("--paired-runner", text)
        self.assertIn("--execution-plan-creator", text)
        self.assertIn("--execution-plan-executor", text)
        self.assertIn("--efficiency-summarizer", text)
        self.assertIn("efficiency_metrics_observed_at_freeze", text)


if __name__ == "__main__":
    unittest.main()
