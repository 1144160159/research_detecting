import json
import tempfile
import unittest
from pathlib import Path

from create_mal_tls_conservative_residual_pilot_protocol import create_protocol
from diagnose_mal_tls_conservative_residual_components import (
    COMPONENT_METRICS,
    diagnose,
)


class ConservativeResidualComponentDiagnosticTests(unittest.TestCase):
    def test_reports_paired_component_gains_without_selection_claim(self) -> None:
        protocol = create_protocol(
            dataset_sha256="a" * 64,
            implementation_sha256={"train.py": "b" * 64},
            observed_metrics=0,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed = protocol["training"]["development_seed"]
            for scenario in protocol["dataset"]["scenarios"]:
                for role, value in (("reference", 0.8), ("candidate", 0.7)):
                    profile = protocol["paired_methods"][role]["encoder_profile"]
                    run = root / profile / f"{scenario}_seed{seed}"
                    run.mkdir(parents=True)
                    (run / "metrics.json").write_text(
                        json.dumps({name: value for name in COMPONENT_METRICS}),
                        encoding="utf-8",
                    )
            result = diagnose(protocol, root)
            self.assertEqual(result["paired_scenario_count"], 6)
            self.assertFalse(result["formal_selection_evidence"])
            for name in COMPONENT_METRICS:
                self.assertAlmostEqual(result["mean_component_auroc_gains"][name], -0.1)
                self.assertEqual(result["negative_scenario_counts"][name], 6)


if __name__ == "__main__":
    unittest.main()
