import unittest

from create_mal_tls_geometry_adapter_confirmation_protocol import create_protocol
from create_strict_v4_external_confirmation_protocol import canonical_hash
from analyze_mal_tls_geometry_adapter_confirmation import bootstrap_summary


def pilot_fixture():
    pilot = {
        "schema_version": "mal_tls_geometry_preserving_adapter_protocol_v1",
        "paired_methods": {
            "reference": {"encoder_profile": "uniform_mlp"},
            "candidate": {"encoder_profile": "mal_tls_geometry_preserving_adapter"},
        },
        "dataset": {"scenarios": {"a": ["x"]}},
        "training": {"development_seed": 195, "expected_development_runs": 2},
        "hard_invariants": {"invariant_metrics": ["distance_auroc"]},
        "reserved_confirmation": {"seeds": [197, 199, 211]},
    }
    pilot["manifest_sha256"] = canonical_hash(pilot)
    analysis = {
        "schema_version": "mal_tls_geometry_preserving_adapter_analysis_v1",
        "protocol_manifest_sha256": pilot["manifest_sha256"],
        "passes": True,
        "decision": "freeze_for_reserved_seed_confirmation",
    }
    return pilot, analysis


class GeometryAdapterConfirmationTests(unittest.TestCase):
    def test_bootstrap_summary_preserves_positive_constant_gain(self) -> None:
        summary = bootstrap_summary([0.02] * 18, seed=7, repetitions=100)
        self.assertAlmostEqual(summary["mean"], 0.02)
        self.assertGreater(summary["bootstrap_95ci"][0], 0.0)

    def test_positive_pilot_freezes_reserved_seed_confirmation(self) -> None:
        pilot, analysis = pilot_fixture()
        protocol = create_protocol(
            pilot,
            analysis,
            pilot_protocol_file_sha256="a" * 64,
            pilot_analysis_file_sha256="b" * 64,
            implementation_sha256={"train.py": "c" * 64},
            observed_metrics=0,
        )
        self.assertEqual(protocol["training"]["confirmation_seeds"], [197, 199, 211])
        self.assertEqual(protocol["training"]["expected_confirmation_runs"], 36)
        self.assertEqual(protocol["confirmation_metrics_observed_at_freeze"], 0)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))

    def test_negative_pilot_cannot_freeze_confirmation(self) -> None:
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

    def test_existing_results_block_confirmation_freeze(self) -> None:
        pilot, analysis = pilot_fixture()
        with self.assertRaisesRegex(ValueError, "before results"):
            create_protocol(
                pilot,
                analysis,
                pilot_protocol_file_sha256="a" * 64,
                pilot_analysis_file_sha256="b" * 64,
                implementation_sha256={},
                observed_metrics=1,
            )


if __name__ == "__main__":
    unittest.main()
