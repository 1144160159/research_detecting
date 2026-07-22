import tempfile
import unittest
from pathlib import Path

from analyze_mal_tls_heterogeneous_pilot import analyze
from create_mal_tls_heterogeneous_pilot_protocol import create_protocol


class MalTlsHeterogeneousPilotTests(unittest.TestCase):
    def test_protocol_is_result_free_and_disjoint(self) -> None:
        protocol = create_protocol(
            dataset_sha256="a" * 64,
            implementation_sha256={"train.py": "b" * 64},
            observed_metrics=0,
        )
        self.assertEqual(protocol["training"]["development_seed"], 191)
        self.assertEqual(protocol["reserved_confirmation"]["seeds"], [197, 199, 211])
        self.assertEqual(protocol["training"]["expected_development_runs"], 12)

    def test_protocol_rejects_observed_results(self) -> None:
        with self.assertRaisesRegex(ValueError, "before results"):
            create_protocol(
                dataset_sha256="a" * 64,
                implementation_sha256={},
                observed_metrics=1,
            )

    def test_analysis_requires_paired_split_fingerprints(self) -> None:
        protocol = create_protocol(
            dataset_sha256="a" * 64,
            implementation_sha256={},
            observed_metrics=0,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for profile, kinds in (
                ("uniform_mlp", ["mlp", "mlp", "mlp", "mlp"]),
                ("mal_tls_heterogeneous", ["tls_gated", "mlp", "mlp", "sequence_tcn"]),
            ):
                for scenario in protocol["dataset"]["scenarios"]:
                    run = root / profile / f"{scenario}_seed191"
                    run.mkdir(parents=True)
                    values = {
                        "unknown_auroc": 0.8 + (profile != "uniform_mlp") * 0.01,
                        "unknown_aupr": 0.7 + (profile != "uniform_mlp") * 0.01,
                        "unknown_fpr95": 0.3 - (profile != "uniform_mlp") * 0.01,
                        "oscr": 0.6 + (profile != "uniform_mlp") * 0.01,
                        "known_macro_f1": 0.75,
                        "ece": 0.05,
                        "encoder_profile": profile,
                    }
                    (run / "metrics.json").write_text(__import__("json").dumps(values))
                    metadata = {
                        "encoder_kinds": kinds,
                        "split_metadata": {"split_fingerprint": {"combined": scenario}},
                    }
                    (run / "data_metadata.json").write_text(
                        __import__("json").dumps(metadata)
                    )
            result = analyze(protocol, root)
            self.assertTrue(result["passes"])
            self.assertEqual(result["paired_scenario_count"], 6)


if __name__ == "__main__":
    unittest.main()
