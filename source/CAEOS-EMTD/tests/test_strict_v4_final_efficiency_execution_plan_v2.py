from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_execution_plan_v2 import (
    create_plan,
    replace_option,
)
from create_strict_v4_final_efficiency_protocol_v2 import file_hash
from execute_strict_v4_final_efficiency_plan_v2 import step_complete


class FinalEfficiencyExecutionPlanV2Tests(unittest.TestCase):
    def test_replace_option_replaces_or_appends(self) -> None:
        self.assertEqual(replace_option(["--seed", "7"], "--seed", "191"), ["--seed", "191"])
        self.assertEqual(replace_option([], "--device", "cuda"), ["--device", "cuda"])

    def test_plan_has_21_training_and_102_inference_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_root = root / "candidate"
            comparator_root = root / "comparator"
            registry = {}
            sentinels = {}
            readiness_artifacts = {}
            remaining = 102
            for index in range(7):
                suite = f"suite_{index}"
                count = 15 if index < 4 else 14
                remaining -= count
                scenarios = [f"scenario_{index}_{item}" for item in range(count)]
                registry[suite] = {"count": count, "scenarios": scenarios}
                sentinels[suite] = scenarios[0]
                readiness_artifacts[suite] = [
                    {"path": str(root / suite / "seed191.csv"), "ready": True}
                ]
                for scenario in scenarios:
                    for source_root, suffix, trainer in (
                        (candidate_root, "", "train_hybrid_open_set.py"),
                        (comparator_root, "_opendetect", "train_neural_open_set.py"),
                    ):
                        run = source_root / suite / f"{scenario}_seed7{suffix}"
                        run.mkdir(parents=True)
                        payload = {
                            "task": {"suite": suite, "scenario": scenario, "seed": 7},
                            "command": [
                                "python",
                                trainer,
                                "--csv",
                                "seed7.csv",
                                "--seed",
                                "7",
                                "--output-dir",
                                str(run),
                            ],
                        }
                        (run / "provenance.json").write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(remaining, 0)
            coverage = {
                "schema_version": "strict_v4_coverage_manifest_v2",
                "scenario_registry": registry,
            }
            coverage["manifest_sha256"] = canonical_hash(coverage)
            protocol = {
                "schema_version": "strict_v4_final_efficiency_protocol_v2",
                "coverage_manifest_sha256": coverage["manifest_sha256"],
                "training_calibration_benchmark": {
                    "sentinel_scenarios": sentinels,
                    "clean_process_repetitions": 3,
                },
                "implementation_sha256": {
                    "efficiency_execution_plan_creator": file_hash(
                        Path(__file__).resolve().parents[1]
                        / "create_strict_v4_final_efficiency_execution_plan_v2.py"
                    ),
                    "efficiency_execution_plan_executor": file_hash(
                        Path(__file__).resolve().parents[1]
                        / "execute_strict_v4_final_efficiency_plan_v2.py"
                    ),
                    "efficiency_summarizer": file_hash(
                        Path(__file__).resolve().parents[1]
                        / "summarize_strict_v4_final_efficiency_v2.py"
                    ),
                },
            }
            protocol["manifest_sha256"] = canonical_hash(protocol)
            readiness = {
                "schema_version": "strict_v4_final_efficiency_cache_readiness_v1",
                "seed191_training_sentinels": {"artifacts": readiness_artifacts},
                "gates": {"formal_timing_allowed": True},
            }
            plan = create_plan(
                protocol,
                coverage,
                readiness,
                protocol_file_sha256="1" * 64,
                coverage_file_sha256="2" * 64,
                readiness_file_sha256="3" * 64,
                protocol_path=root / "protocol.json",
                candidate_source_root=candidate_root,
                comparator_source_root=comparator_root,
                output_root=root / "formal",
                python="python",
            )
            self.assertEqual(len(plan["training_blocks"]), 21)
            self.assertEqual(len(plan["inference_blocks"]), 102)
            self.assertEqual(len(plan["inference_blocks"][0]["steps"]), 8)
            self.assertEqual(plan["manifest_sha256"], canonical_hash(plan))
            self.assertEqual(
                plan["training_blocks"][0]["method_order"],
                ["candidate", "comparator"],
            )
            self.assertEqual(
                plan["training_blocks"][1]["method_order"],
                ["comparator", "candidate"],
            )
            self.assertEqual(
                plan["implementation_sha256"]["efficiency_summarizer"],
                protocol["implementation_sha256"]["efficiency_summarizer"],
            )

    def test_step_complete_requires_every_expected_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "a"
            second = Path(directory) / "b"
            first.touch()
            step = {"expected_files": [str(first), str(second)]}
            self.assertFalse(step_complete(step))
            second.touch()
            self.assertTrue(step_complete(step))


if __name__ == "__main__":
    unittest.main()
