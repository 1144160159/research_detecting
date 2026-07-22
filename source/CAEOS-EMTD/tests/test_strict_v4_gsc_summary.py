from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_gsc_expansion_gate import create_gate
from summarize_strict_v4_gsc_pilot import analyze


def report(shift: float = 0.0) -> dict[str, float]:
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8 + shift,
        "unknown_aupr": 0.75 + shift,
        "unknown_fpr95": 0.3 - shift,
        "oscr": 0.7 + shift,
    }


class StrictV4GSCSummaryTests(unittest.TestCase):
    def test_positive_formula_valid_pilot_expands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot = root / "pilot"
            source = root / "source"
            external = root / "external"
            selected = {f"suite_{index}": ["left", "right"] for index in range(7)}
            protocol = {
                "schema_version": "strict_v4_mlp_gsc_protocol_v1",
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
                    gsc_path = pilot / suite / f"{scenario}_seed7"
                    source_path = source / suite / f"{scenario}_seed7_mlp"
                    external_path = external / suite / f"{scenario}_seed7_opendetect"
                    for path in (gsc_path, source_path, external_path):
                        path.mkdir(parents=True, exist_ok=True)
                    gsc_payload = {
                        "schema_version": "strict_v4_mlp_gsc_v1",
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"gsc": report(0.02)},
                        "selection_evidence": {
                            "postprocessor": {
                                "method": "Gradient Short-Circuit",
                                "mask_ratio": 0.05,
                                "intervention": "zero_top_absolute_gradient_coordinates",
                            },
                            "validation_mask_diagnostics": {
                                "linear_head_degeneracy_observed": True
                            },
                            "test_mask_diagnostics": {
                                "linear_head_degeneracy_observed": True
                            },
                            "unknown_or_test_labels_used_for_fitting_or_selection": False,
                        },
                    }
                    source_payload = {
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"energy": report()},
                    }
                    external_payload = {
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"opendetect": report(-0.01)},
                    }
                    for path, payload in (
                        (gsc_path, gsc_payload),
                        (source_path, source_payload),
                        (external_path, external_payload),
                    ):
                        (path / "metrics.json").write_text(
                            json.dumps(payload), encoding="utf-8"
                        )
            result = analyze(pilot, source, external, gate)
            self.assertTrue(result["decision"]["expand_gsc_to_full102"])
            self.assertEqual(result["formula_integrity_count"], 14)


if __name__ == "__main__":
    unittest.main()
