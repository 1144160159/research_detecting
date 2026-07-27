from __future__ import annotations

import unittest

from scripts.merge_offline_candidate_evidence import (
    combine_operating_modes,
    dominates,
    summarize_recovery_runs,
)


class JointMergeTest(unittest.TestCase):
    def candidate(self, **overrides):
        candidate = {
            "throughput_mpps_min": 1.0,
            "p99_latency_us_max": 100.0,
            "resource_pressure_max": 0.5,
            "macro_f1_min": 0.9,
            "ece_max": 0.1,
            "independent_macro_f1_min": 0.5,
            "independent_attack_recall_min": 0.7,
            "ground_truth_event_recall_min": 0.8,
        }
        candidate.update(overrides)
        return candidate

    def test_independent_holdout_prevents_false_dominance(self):
        faster_but_worse_holdout = self.candidate(
            throughput_mpps_min=2.0,
            independent_macro_f1_min=0.4,
        )
        reference = self.candidate()

        self.assertFalse(
            dominates(faster_but_worse_holdout, reference)
        )

    def test_attack_recall_tradeoff_prevents_false_dominance(self):
        higher_macro_lower_attack_recall = self.candidate(
            independent_macro_f1_min=0.6,
            independent_attack_recall_min=0.6,
        )

        self.assertFalse(
            dominates(higher_macro_lower_attack_recall, self.candidate())
        )

    def test_candidate_must_be_no_worse_on_all_joint_objectives(self):
        better = self.candidate(
            throughput_mpps_min=2.0,
            p99_latency_us_max=90.0,
            macro_f1_min=0.95,
            independent_macro_f1_min=0.55,
        )

        self.assertTrue(dominates(better, self.candidate()))

    def recovery_run(self, recovery_s=0.27, coverage=1.0, overruns=0):
        return {
            "candidate": {
                "batch_size": 512,
                "budget_us": 5000.0,
                "execution_budget_safety_ratio": 0.5,
            },
            "status": "complete",
            "fallback_recovery_s": recovery_s,
            "hard_constraint_observations": {
                "budget_overrun_count": overruns,
                "minimum_key_flow_coverage": coverage,
            },
            "evidence_scope": {
                "fallback_activation_verified": True,
                "fallback_recovery_verified": True,
                "fallback_real_pcap_processing_verified": True,
                "same_candidate_pipeline_instance_verified": True,
                "application_budget_verified": overruns == 0,
                "key_flow_coverage_verified": coverage == 1.0,
            },
        }

    def test_recovery_summary_uses_worst_repeat_and_hard_gates(self):
        named = [
            ("repeat1.json", self.recovery_run(0.25)),
            ("repeat2.json", self.recovery_run(0.27)),
            ("repeat3.json", self.recovery_run(0.26)),
        ]

        summary = summarize_recovery_runs(
            named, max_fallback_recovery_s=0.30
        )
        candidate = summary["candidates"][0]

        self.assertEqual(candidate["fallback_recovery_s_max"], 0.27)
        self.assertTrue(candidate["hard_constraints_passed"])

    def test_recovery_threshold_violation_is_not_hidden(self):
        named = [
            ("repeat1.json", self.recovery_run(0.25)),
            ("repeat2.json", self.recovery_run(0.31)),
            ("repeat3.json", self.recovery_run(0.26)),
        ]

        candidate = summarize_recovery_runs(
            named, max_fallback_recovery_s=0.30
        )["candidates"][0]

        self.assertFalse(candidate["hard_constraints_passed"])
        self.assertIn(
            "fallback_recovery_s_max",
            candidate["hard_constraint_violations"],
        )

    def mode_profile(self, mode, **overrides):
        profile = self.candidate()
        profile.update(
            {
                "name": "{}_batch512_budget5000".format(mode),
                "mode": mode,
                "batch_size": 512,
                "budget_us": 5000,
                "execution_budget_safety_ratio": 0.5,
                "p999_latency_us_max": 120.0,
                "budget_overrun_count_max": 0,
                "key_flow_coverage_min": 1.0,
                "recovery_fallback_recovery_s_max": 0.27,
                "independent_decision_policy": {
                    "feature_profile": "invariant_no_ports_v1",
                    "classifier": "extra_trees",
                    "threshold_policy": "calibration_macro_f1",
                    "calibration_attack_recall_floor": 0.8,
                    "calibration_groups": ["unsw_january"],
                    "evaluation_groups": ["unsw_february"],
                },
                "joint_gate_violations": [],
            }
        )
        profile.update(overrides)
        return profile

    def test_normal_and_fallback_are_paired_as_one_configuration(self):
        normal = self.mode_profile(
            "normal", throughput_mpps_min=1.0, macro_f1_min=0.95
        )
        fallback = self.mode_profile(
            "fallback", throughput_mpps_min=1.2, macro_f1_min=0.90
        )

        configurations = combine_operating_modes([normal, fallback])

        self.assertEqual(len(configurations), 1)
        self.assertEqual(
            configurations[0]["mode_profiles"],
            [
                "fallback_batch512_budget5000",
                "normal_batch512_budget5000",
            ],
        )
        self.assertEqual(
            configurations[0]["throughput_mpps_min"], 1.0
        )
        self.assertEqual(configurations[0]["macro_f1_min"], 0.90)
        self.assertTrue(
            configurations[0]["offline_joint_gate_passed"]
        )
        self.assertEqual(
            configurations[0]["independent_attack_recall_min"], 0.7
        )

    def test_missing_fallback_mode_blocks_deployable_configuration(self):
        configuration = combine_operating_modes(
            [self.mode_profile("normal")]
        )[0]

        self.assertFalse(configuration["offline_joint_gate_passed"])
        self.assertIn(
            "mode_evidence.fallback.missing",
            configuration["joint_gate_violations"],
        )

    def test_mixed_mode_decision_policies_are_rejected(self):
        normal = self.mode_profile("normal")
        fallback = self.mode_profile("fallback")
        fallback["independent_decision_policy"] = dict(
            fallback["independent_decision_policy"],
            calibration_attack_recall_floor=0.9,
        )

        configurations = combine_operating_modes([normal, fallback])

        self.assertEqual(len(configurations), 2)
        self.assertTrue(
            all(
                not item["offline_joint_gate_passed"]
                for item in configurations
            )
        )
        self.assertTrue(
            all(
                any(
                    violation.startswith("mode_evidence.")
                    and violation.endswith(".missing")
                    for violation in item["joint_gate_violations"]
                )
                for item in configurations
            )
        )


if __name__ == "__main__":
    unittest.main()
