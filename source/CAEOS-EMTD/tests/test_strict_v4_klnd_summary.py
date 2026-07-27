from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_klnd_expansion_gate import create_gate
from summarize_strict_v4_klnd_pilot import analyze


def report(
    known: float, auroc: float, aupr: float, fpr95: float, oscr: float
) -> dict[str, float]:
    return {
        "known_macro_f1": known,
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


class StrictV4KLNDSummaryTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def build_fixture(self, root: Path) -> tuple[Path, Path, Path, dict]:
        pilot = root / "pilot"
        source = root / "source"
        external = root / "external"
        selected = {
            "suite_%d" % index: ["unknown_a", "unknown_b"]
            for index in range(7)
        }
        protocol = {
            "schema_version": "strict_v4_mlp_klnd_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
            "selected_scenarios": selected,
            "class_center_data": (
                "correctly_classified_known_training_logits_only"
            ),
            "native_threshold_data": (
                "correctly_classified_known_validation_logits_only"
            ),
            "ood_parameter_sweep": False,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        self.write_json(pilot / "protocol_manifest.json", protocol)
        gate = create_gate(protocol, observed_metrics=0)
        fingerprint = {"digest": "same-split"}
        for suite, scenarios in selected.items():
            for scenario in scenarios:
                candidate = {
                    "split_metadata": {"split_fingerprint": fingerprint},
                    "reports": {
                        "klnd1": report(0.8, 0.70, 0.60, 0.40, 0.65),
                        "klnd2": report(0.8, 0.72, 0.62, 0.38, 0.67),
                        "klnd3": report(0.8, 0.80, 0.70, 0.25, 0.75),
                    },
                    "selection_evidence": {
                        "unknown_or_test_labels_used_for_fitting_or_selection": False,
                        "klnd": {
                            "class_count": 3,
                            "train_correct_counts": [10, 10, 10],
                            "validation_correct_counts": [5, 5, 5],
                        },
                    },
                    "diagnostics": {
                        method: {
                            "validation_risk_std": 0.2,
                            "test_risk_std": 0.3,
                        }
                        for method in ("klnd1", "klnd2", "klnd3")
                    },
                }
                source_value = {
                    "split_metadata": {"split_fingerprint": fingerprint},
                    "reports": {
                        "msp": report(0.8, 0.65, 0.55, 0.45, 0.60),
                        "energy": report(0.8, 0.70, 0.60, 0.35, 0.65),
                    },
                }
                external_value = {
                    "split_metadata": {"split_fingerprint": fingerprint},
                    "reports": {
                        "opendetect": report(
                            0.8, 0.75, 0.65, 0.30, 0.70
                        )
                    },
                }
                self.write_json(
                    pilot / suite / (scenario + "_seed7") / "metrics.json",
                    candidate,
                )
                self.write_json(
                    source
                    / suite
                    / (scenario + "_seed7_mlp")
                    / "metrics.json",
                    source_value,
                )
                self.write_json(
                    external
                    / suite
                    / (scenario + "_seed7_opendetect")
                    / "metrics.json",
                    external_value,
                )
        return pilot, source, external, gate

    def test_selects_best_variant_and_expands_when_all_gates_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pilot, source, external, gate = self.build_fixture(
                Path(temporary)
            )
            result = analyze(pilot, source, external, gate)
        self.assertEqual(result["selected_variant"], "klnd3")
        self.assertEqual(result["validation"]["report_count"], 42)
        self.assertTrue(result["validation"]["passes"])
        self.assertTrue(
            result["decision"]["expand_selected_klnd_to_full102"]
        )
        self.assertTrue(all(result["expansion_checks"].values()))

    def test_rejects_split_fingerprint_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pilot, source, external, gate = self.build_fixture(
                Path(temporary)
            )
            path = (
                pilot
                / "suite_0"
                / "unknown_a_seed7"
                / "metrics.json"
            )
            value = json.loads(path.read_text(encoding="utf-8"))
            value["split_metadata"]["split_fingerprint"] = {
                "digest": "different"
            }
            self.write_json(path, value)
            with self.assertRaisesRegex(ValueError, "split fingerprint"):
                analyze(pilot, source, external, gate)


if __name__ == "__main__":
    unittest.main()
