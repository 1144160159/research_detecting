from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from caeos.actsub_posthoc import OFFICIAL_COMMIT
from create_strict_v4_actsub_expansion_gate import create_gate
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_actsub_pilot import analyze


def report(shift: float = 0.0) -> dict[str, float]:
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8 + shift,
        "unknown_aupr": 0.75 + shift,
        "unknown_fpr95": 0.3 - shift,
        "oscr": 0.7 + shift,
    }


class StrictV4ActSubSummaryTests(unittest.TestCase):
    def test_positive_formula_valid_pilot_expands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot = root / "pilot"
            source = root / "source"
            external = root / "external"
            selected = {f"suite_{index}": ["left", "right"] for index in range(7)}
            protocol = {
                "schema_version": "strict_v4_mlp_actsub_scale_fixed_protocol_v1",
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
                    candidate_path = pilot / suite / f"{scenario}_seed7"
                    source_path = source / suite / f"{scenario}_seed7_mlp"
                    external_path = external / suite / f"{scenario}_seed7_opendetect"
                    for path in (candidate_path, source_path, external_path):
                        path.mkdir(parents=True, exist_ok=True)
                    candidate_payload = {
                        "schema_version": "strict_v4_mlp_actsub_scale_fixed_v1",
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {"actsub_scale_fixed": report(0.02)},
                        "selection_evidence": {
                            "postprocessor": {
                                "method": "ActSub-SCALE-Fixed",
                                "official_commit": OFFICIAL_COMMIT,
                                "official_formula": "Eq. 10 decisive_energy_times_insignificant_score_power_lambda",
                                "scale_percentile": 95.0,
                                "lambda": 2.0,
                                "neighbors": 10,
                                "hyperparameter_policy": "official_ResNet_defaults_without_APS_OOD_sweep",
                                "fit_split": "known_training_embeddings_only",
                            },
                            "fit_diagnostics": {
                                "balance_index": 20,
                                "embedding_dimension": 64,
                                "known_training_sample_count": 100,
                            },
                            "validation_diagnostics": {
                                "all_scores_finite": True,
                                "score_standard_deviation": 0.1,
                            },
                            "test_diagnostics": {
                                "all_scores_finite": True,
                                "score_standard_deviation": 0.2,
                            },
                            "prediction_uses_unmodified_frozen_model": True,
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
                        (candidate_path, candidate_payload),
                        (source_path, source_payload),
                        (external_path, external_payload),
                    ):
                        (path / "metrics.json").write_text(
                            json.dumps(payload), encoding="utf-8"
                        )
            result = analyze(pilot, source, external, gate)
            self.assertTrue(result["decision"]["expand_actsub_to_full102"])
            self.assertEqual(result["formula_integrity_count"], 14)
            self.assertEqual(result["nonconstant_score_count"], 14)


if __name__ == "__main__":
    unittest.main()
