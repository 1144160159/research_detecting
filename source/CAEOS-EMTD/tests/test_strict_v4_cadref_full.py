from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from caeos.cadref_posthoc import OFFICIAL_COMMIT
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_cadref_full import analyze


def report(shift=0.0):
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8 + shift,
        "unknown_aupr": 0.75 + shift,
        "unknown_fpr95": 0.3 - shift,
        "oscr": 0.7 + shift,
    }


def candidate_payload(fingerprint):
    return {
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


class StrictV4CADRefFullTests(unittest.TestCase):
    def test_full_analysis_requires_and_binds_all_102_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            full = root / "full"
            source = root / "source"
            external = root / "external"
            counts = [15, 15, 15, 15, 14, 14, 14]
            selected = {
                f"suite_{index}": [f"scenario_{item}" for item in range(count)]
                for index, count in enumerate(counts)
            }
            protocol = {
                "schema_version": "strict_v4_mlp_cadref_family_protocol_v1",
                "mode": "full",
                "expected_runs": 102,
                "selected_scenarios": selected,
            }
            protocol["manifest_sha256"] = canonical_hash(protocol)
            full.mkdir()
            (full / "protocol_manifest.json").write_text(
                json.dumps(protocol), encoding="utf-8"
            )
            matrix = {
                "schema_version": "strict_v4_mlp_cadref_family_matrix_v1",
                "status": "complete",
                "completed_runs": 102,
                "failures": 0,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
            }
            (full / "matrix_summary.json").write_text(
                json.dumps(matrix), encoding="utf-8"
            )
            fingerprint = {"train": "a", "validation": "b", "test": "c"}
            for suite, scenarios in selected.items():
                for scenario in scenarios:
                    paths = (
                        full / suite / f"{scenario}_seed7",
                        source / suite / f"{scenario}_seed7_mlp",
                        external / suite / f"{scenario}_seed7_opendetect",
                    )
                    for path in paths:
                        path.mkdir(parents=True, exist_ok=True)
                    payloads = (
                        candidate_payload(fingerprint),
                        {
                            "split_metadata": {"split_fingerprint": fingerprint},
                            "reports": {"energy": report()},
                        },
                        {
                            "split_metadata": {"split_fingerprint": fingerprint},
                            "reports": {"opendetect": report(-0.01)},
                        },
                    )
                    for path, payload in zip(paths, payloads):
                        (path / "metrics.json").write_text(
                            json.dumps(payload), encoding="utf-8"
                        )
            pilot = {
                "schema_version": "strict_v4_mlp_cadref_family_pilot_analysis_v1",
                "pilot_protocol_manifest_sha256": "pilot",
                "expansion_gate_manifest_sha256": "gate",
                "decision": {"expand_methods_to_full102": ["cadref_energy_fixed"]},
            }
            result = analyze(full, source, external, pilot)
            self.assertEqual(result["scenario_count"], 102)
            self.assertEqual(result["formula_integrity_count"], 102)
            self.assertEqual(result["manifest_sha256"], canonical_hash(result))


if __name__ == "__main__":
    unittest.main()
