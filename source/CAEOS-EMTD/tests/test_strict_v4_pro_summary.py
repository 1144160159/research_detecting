from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from caeos.pro_posthoc import OFFICIAL_COMMIT
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_pro_expansion_gate import create_gate
from summarize_strict_v4_pro_pilot import analyze


def report(shift: float = 0.0) -> dict[str, float]:
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8 + shift,
        "unknown_aupr": 0.75 + shift,
        "unknown_fpr95": 0.3 - shift,
        "oscr": 0.7 + shift,
    }


class StrictV4PROSummaryTests(unittest.TestCase):
    def test_positive_formula_valid_pilot_expands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot = root / "pilot"
            source = root / "source"
            external = root / "external"
            selected = {f"suite_{index}": ["left", "right"] for index in range(7)}
            protocol = {
                "schema_version": "strict_v4_mlp_pro_msp_fixed_protocol_v1",
                "mode": "pilot",
                "expected_runs": 14,
                "selected_scenarios": selected,
            }
            protocol["manifest_sha256"] = canonical_hash(protocol)
            pilot.mkdir()
            (pilot / "protocol_manifest.json").write_text(
                json.dumps(protocol), encoding="utf-8"
            )
            gate = create_gate(protocol, 0)
            fingerprint = {"train": "a", "validation": "b", "test": "c"}
            for suite, scenarios in selected.items():
                for scenario in scenarios:
                    pro_path = pilot / suite / f"{scenario}_seed7"
                    source_path = source / suite / f"{scenario}_seed7_mlp"
                    external_path = external / suite / f"{scenario}_seed7_opendetect"
                    for path in (pro_path, source_path, external_path):
                        path.mkdir(parents=True, exist_ok=True)
                    pro_payload = {
                        "schema_version": "strict_v4_mlp_pro_msp_fixed_v1",
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"pro_msp_fixed": report(0.02)},
                        "selection_evidence": {
                            "postprocessor": {
                                "method": "PRO-MSP-Fixed",
                                "official_commit": OFFICIAL_COMMIT,
                                "official_class": "PROv2_MSP_Postprocessor",
                                "step_size": 0.003,
                                "steps": 1,
                                "temperature": 1.0,
                                "score": "minimum MSP over original and sign-gradient descent path",
                            },
                            "validation_diagnostics": {
                                "all_risks_finite": True,
                                "mean_confidence_drop": 0.01,
                            },
                            "test_diagnostics": {
                                "all_risks_finite": True,
                                "mean_confidence_drop": 0.02,
                            },
                            "prediction_uses_unperturbed_model": True,
                            "unknown_or_test_labels_used_for_fitting_or_selection": False,
                        },
                    }
                    source_payload = {
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"msp": report(), "energy": report(-0.005)},
                    }
                    external_payload = {
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"opendetect": report(-0.01)},
                    }
                    for path, payload in (
                        (pro_path, pro_payload),
                        (source_path, source_payload),
                        (external_path, external_payload),
                    ):
                        (path / "metrics.json").write_text(
                            json.dumps(payload), encoding="utf-8"
                        )
            result = analyze(pilot, source, external, gate)
            self.assertTrue(result["decision"]["expand_pro_to_full102"])
            self.assertEqual(result["formula_integrity_count"], 14)


if __name__ == "__main__":
    unittest.main()
