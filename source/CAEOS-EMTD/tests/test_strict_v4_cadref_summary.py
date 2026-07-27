from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from caeos.cadref_posthoc import OFFICIAL_COMMIT
from create_strict_v4_cadref_expansion_gate import create_gate
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_cadref_pilot import analyze


def report(shift: float = 0.0) -> dict[str, float]:
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8 + shift,
        "unknown_aupr": 0.75 + shift,
        "unknown_fpr95": 0.3 - shift,
        "oscr": 0.7 + shift,
    }


class StrictV4CADRefSummaryTests(unittest.TestCase):
    def test_positive_formula_valid_family_expands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot = root / "pilot"
            source = root / "source"
            external = root / "external"
            selected = {f"suite_{index}": ["left", "right"] for index in range(7)}
            protocol = {
                "schema_version": "strict_v4_mlp_cadref_family_protocol_v1",
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
                        "schema_version": "strict_v4_mlp_cadref_family_v1",
                        "split_metadata": {"split_fingerprint": fingerprint},
                        "reports": {
                            "caref": report(0.02),
                            "cadref_energy_fixed": report(0.03),
                        },
                        "selection_evidence": {
                            "postprocessor": {
                                "family": "CARef-and-CADRef-Energy-Fixed",
                                "official_commit": OFFICIAL_COMMIT,
                                "caref_formula": "Eq.6 negative normalized L1 relative feature error",
                                "cadref_formula": "Eq.10 negative(Ep/Energy(x)+En/mean_train_Energy)",
                                "logit_method": "Energy",
                                "hyperparameter_policy": "official_default_Energy_without_OOD_sweep",
                                "fit_split": "known_training_embeddings_and_logits_only",
                            },
                            "fit_diagnostics": {
                                "known_training_sample_count": 100,
                                "supported_predicted_class_count": 3,
                                "global_mean_energy": 2.0,
                            },
                            "validation_diagnostics": {
                                "all_scores_finite": True,
                                "minimum_absolute_energy": 0.5,
                                "caref_score_standard_deviation": 0.1,
                                "cadref_score_standard_deviation": 0.1,
                            },
                            "test_diagnostics": {
                                "all_scores_finite": True,
                                "minimum_absolute_energy": 0.4,
                                "caref_score_standard_deviation": 0.2,
                                "cadref_score_standard_deviation": 0.2,
                            },
                            "prediction_uses_unmodified_frozen_model": True,
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
                        (candidate_path, candidate_payload),
                        (source_path, source_payload),
                        (external_path, external_payload),
                    ):
                        (path / "metrics.json").write_text(
                            json.dumps(payload), encoding="utf-8"
                        )
            result = analyze(pilot, source, external, gate)
            self.assertTrue(result["decision"]["expand_family_to_full102"])
            self.assertEqual(
                result["decision"]["expand_methods_to_full102"],
                ["caref", "cadref_energy_fixed"],
            )
            self.assertEqual(result["formula_integrity_count"], 14)


if __name__ == "__main__":
    unittest.main()
