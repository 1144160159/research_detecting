import json
import tempfile
import unittest
from pathlib import Path

from analyze_mal_tls_conservative_residual_pilot import analyze
from create_mal_tls_conservative_residual_pilot_protocol import create_protocol


class ConservativeResidualPilotTests(unittest.TestCase):
    def protocol(self):
        return create_protocol(
            dataset_sha256="a" * 64,
            implementation_sha256={"train.py": "b" * 64},
            observed_metrics=0,
        )

    def test_protocol_is_result_free_and_uses_disjoint_seed(self) -> None:
        protocol = self.protocol()
        self.assertEqual(protocol["training"]["development_seed"], 193)
        self.assertEqual(protocol["metrics_observed_at_freeze"], 0)
        self.assertEqual(protocol["reserved_confirmation"]["seeds"], [197, 199, 211])
        self.assertTrue(
            protocol["paired_methods"][
                "known_validation_evidence_temperature_calibration_for_both"
            ]
        )

    def test_analyzer_requires_paired_temperature_evidence(self) -> None:
        protocol = self.protocol()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed = protocol["training"]["development_seed"]
            for scenario in protocol["dataset"]["scenarios"]:
                for role in ("reference", "candidate"):
                    method = protocol["paired_methods"][role]
                    run = root / method["encoder_profile"] / f"{scenario}_seed{seed}"
                    run.mkdir(parents=True)
                    gain = 0.01 if role == "candidate" else 0.0
                    metrics = {
                        "encoder_profile": method["encoder_profile"],
                        "encoder_kinds": method["encoder_kinds"],
                        "evidence_temperature_calibration": True,
                        "evidence_temperature": 1.0,
                        "known_macro_f1": 0.8 + gain,
                        "ece": 0.1 - gain,
                        "unknown_auroc": 0.8 + gain,
                        "unknown_aupr": 0.7 + gain,
                        "unknown_fpr95": 0.3 - gain,
                        "oscr": 0.6 + gain,
                    }
                    metadata = {
                        "encoder_kinds": method["encoder_kinds"],
                        "split_metadata": {
                            "split_fingerprint": {"combined": scenario + "-fp"}
                        },
                    }
                    temperature = {
                        "enabled": True,
                        "temperature": 1.0,
                        "fit_split": "known_only_validation",
                        "unknown_or_test_labels_used": False,
                    }
                    (run / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
                    (run / "data_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
                    (run / "evidence_temperature.json").write_text(
                        json.dumps(temperature), encoding="utf-8"
                    )
            result = analyze(protocol, root)
            self.assertTrue(result["passes"])
            self.assertEqual(result["paired_scenario_count"], 6)


if __name__ == "__main__":
    unittest.main()
