from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.algorithm_optimality import audit_algorithm_search
from scripts.audit_algorithm_search import load_strict_json


ROOT = Path(__file__).resolve().parents[1]


def metric_row(**overrides):
    row = {
        "macro_f1_min": 0.75,
        "attack_recall_min": 0.76,
        "benign_recall_min": 0.95,
        "auprc_min": 0.52,
        "ece_max": 0.03,
        "ground_truth_event_recall_min": 0.74,
        "key_flow_coverage_min": 1.0,
        "budget_overrun_count_max": 0,
        "budget_us_max": 5000,
    }
    row.update(overrides)
    return row


def complete_search():
    candidates = []
    for candidate_id, macro_f1 in (("A1", 0.74), ("A2", 0.76)):
        normal = metric_row(macro_f1_min=macro_f1)
        fallback = metric_row(macro_f1_min=macro_f1 + 0.01)
        worst = dict(normal)
        candidates.append(
            {
                "id": candidate_id,
                "feature_profile": candidate_id,
                "classifier": "extra_trees",
                "threshold_policy": "floor080",
                "adaptation_policy": "none",
                "stage": "fresh_confirmatory",
                "evidence": "/remote/{}.json".format(candidate_id),
                "evidence_sha256": candidate_id.lower()[0] * 64,
                "mode_contract": {
                    "repeat_count_by_mode": {"normal": 3, "fallback": 3},
                    "input_hash_manifest_sha256": "f" * 64,
                },
                "mode_metrics": {"normal": normal, "fallback": fallback},
                "reported_worst_case_metrics": worst,
            }
        )
    return {
        "schema_version": 2,
        "search_id": "test",
        "exploration_budget": {
            "minimum_candidates": 2,
            "maximum_candidates": 2,
            "hard_cap_candidates": 12,
            "actual_candidates": 2,
        },
        "selection_protocol": {
            "hard_constraints_before_pareto": True,
            "normal_and_fallback_must_be_paired": True,
            "measured_repeats_per_mode_for_finalists": 3,
            "minimum_material_improvement": 0.01,
            "pareto_objectives": [
                "macro_f1_min:max",
                "attack_recall_min:max",
                "benign_recall_min:max",
                "auprc_min:max",
                "ece_max:min",
            ],
        },
        "hard_constraints": {
            "min_macro_f1_min": 0.7,
            "min_attack_recall_min": 0.72,
            "min_benign_recall_min": 0.93,
            "min_auprc_min": 0.45,
            "min_ground_truth_event_recall_min": 0.7,
            "min_key_flow_coverage_min": 0.99,
            "max_ece_max": 0.05,
            "max_budget_overrun_count_max": 0,
            "max_budget_us": 5000,
        },
        "resource_budget": {
            "expected_batch_size": 512,
            "max_budget_us": 5000,
            "execution_budget_safety_ratio": 0.5,
            "production_joint_comparison_required_metrics": [
                "throughput_mpps",
                "packet_drop_count",
                "end_to_end_p99_us",
                "cpu_utilization",
                "gpu_utilization",
                "memory_utilization",
                "key_flow_coverage",
                "fallback_recovery_s",
            ],
        },
        "candidates": candidates,
        "strict_pareto_front": ["A2"],
        "practical_front": ["A2"],
        "selected_candidate": "A2",
    }


class AlgorithmOptimalityTest(unittest.TestCase):
    def test_current_search_fails_closed_but_recomputes_a09_a10(self):
        search = load_strict_json(ROOT / "configs" / "algorithm_search_rc1.json")
        result = audit_algorithm_search(search)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["actual_candidate_count"], 10)
        self.assertEqual(result["paired_metric_complete_candidate_count"], 2)
        self.assertEqual(result["confirmatory_strict_pareto_front"], ["A09", "A10"])
        self.assertEqual(result["confirmatory_practical_front"], ["A09"])
        self.assertEqual(result["confirmatory_practical_winner"], "A09")
        self.assertFalse(result["algorithm_only_practical_optimum_proven"])
        self.assertFalse(result["production_joint_optimum_proven"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_complete_bounded_search_can_prove_algorithm_only_optimum(self):
        result = audit_algorithm_search(complete_search())
        self.assertTrue(result["accepted"], result["errors"])
        self.assertTrue(result["algorithm_only_practical_optimum_proven"])
        self.assertEqual(result["practical_front_recomputed_from_available_metrics"], ["A2"])
        self.assertFalse(result["production_joint_optimum_proven"])

    def test_reported_front_and_selected_candidate_are_not_trusted(self):
        search = complete_search()
        search["strict_pareto_front"] = ["A1"]
        search["practical_front"] = ["A1"]
        search["selected_candidate"] = "A1"
        result = audit_algorithm_search(search)
        self.assertFalse(result["accepted"])
        self.assertIn("search.reported_strict_pareto_front", result["errors"])
        self.assertIn("search.selected_candidate.finalist_comparison", result["errors"])

    def test_missing_hash_or_mode_repeats_rejects_optimality(self):
        search = complete_search()
        search["candidates"][0]["evidence_sha256"] = None
        search["candidates"][1]["mode_contract"]["repeat_count_by_mode"]["fallback"] = 2
        result = audit_algorithm_search(search)
        self.assertFalse(result["accepted"])
        self.assertIn("A1.evidence_sha256", result["errors"])
        self.assertIn("A2.repeat_count_by_mode", result["errors"])

    def test_tampered_worst_case_metric_is_rejected(self):
        search = complete_search()
        search["candidates"][1]["reported_worst_case_metrics"]["macro_f1_min"] = 0.99
        result = audit_algorithm_search(search)
        self.assertFalse(result["accepted"])
        self.assertIn("A2.reported_worst_case_metrics", result["errors"])

    def test_evidence_path_must_not_contain_a_physical_newline(self):
        search = complete_search()
        search["candidates"][0]["evidence"] = "/remote/summary.jso\nn"
        result = audit_algorithm_search(search)
        self.assertFalse(result["accepted"])
        self.assertIn("A1.evidence_path", result["errors"])

    def test_strict_json_rejects_duplicate_keys_and_non_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / "duplicate.json"
            duplicate.write_bytes(b'{"schema_version":1,"schema_version":2}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_strict_json(duplicate)
            invalid = Path(directory) / "invalid.json"
            invalid.write_bytes(b'{"reason":"\xff"}')
            with self.assertRaises(UnicodeDecodeError):
                load_strict_json(invalid)

    def test_cli_runs_directly_and_current_search_fails_closed(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "audit_algorithm_search.py"),
                str(ROOT / "configs" / "algorithm_search_rc1.json"),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["confirmatory_practical_winner"], "A09")


if __name__ == "__main__":
    unittest.main()
