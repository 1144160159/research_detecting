import unittest

from analyze_mal_tls_counterfactual_conflict_gate_confirmation import bootstrap_summary
from create_mal_tls_counterfactual_conflict_gate_confirmation_protocol import (
    create_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def pilot_fixture():
    pilot = {
        "schema_version": "mal_tls_counterfactual_conflict_gate_protocol_v1",
        "paired_methods": {
            "reference": {"encoder_profile": "uniform_mlp"},
            "candidate": {
                "encoder_profile": "mal_tls_counterfactual_conflict_gate"
            },
        },
        "dataset": {"scenarios": {"a": ["x"]}},
        "known_only_counterfactual_training": {"counterfactual_weight": 1.0},
        "training": {"development_seed": 201, "expected_development_runs": 2},
        "hard_invariants": {"invariant_metrics": ["distance_auroc"]},
        "reserved_confirmation": {"seeds": [203, 205, 207]},
    }
    pilot["manifest_sha256"] = canonical_hash(pilot)
    analysis = {
        "schema_version": "mal_tls_counterfactual_conflict_gate_analysis_v1",
        "protocol_manifest_sha256": pilot["manifest_sha256"],
        "passes": True,
        "decision": "freeze_for_reserved_seed_confirmation",
    }
    return pilot, analysis


class CounterfactualConfirmationTests(unittest.TestCase):
    def test_positive_pilot_freezes_reserved_confirmation(self) -> None:
        pilot, analysis = pilot_fixture()
        protocol = create_protocol(
            pilot,
            analysis,
            pilot_protocol_file_sha256="a" * 64,
            pilot_analysis_file_sha256="b" * 64,
            implementation_sha256={"train.py": "c" * 64},
            observed_metrics=0,
        )
        self.assertEqual(protocol["training"]["confirmation_seeds"], [203, 205, 207])
        self.assertEqual(protocol["training"]["expected_confirmation_runs"], 36)
        self.assertEqual(protocol["confirmation_metrics_observed_at_freeze"], 0)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))

    def test_negative_pilot_and_existing_results_block_freeze(self) -> None:
        pilot, analysis = pilot_fixture()
        analysis["passes"] = False
        with self.assertRaisesRegex(ValueError, "authorize"):
            create_protocol(
                pilot,
                analysis,
                pilot_protocol_file_sha256="a" * 64,
                pilot_analysis_file_sha256="b" * 64,
                implementation_sha256={},
                observed_metrics=0,
            )
        analysis["passes"] = True
        with self.assertRaisesRegex(ValueError, "before results"):
            create_protocol(
                pilot,
                analysis,
                pilot_protocol_file_sha256="a" * 64,
                pilot_analysis_file_sha256="b" * 64,
                implementation_sha256={},
                observed_metrics=1,
            )

    def test_bootstrap_summary_preserves_positive_constant_gain(self) -> None:
        summary = bootstrap_summary([0.03] * 18, seed=9, repetitions=100)
        self.assertAlmostEqual(summary["mean"], 0.03)
        self.assertGreater(summary["bootstrap_95ci"][0], 0.0)


if __name__ == "__main__":
    unittest.main()
