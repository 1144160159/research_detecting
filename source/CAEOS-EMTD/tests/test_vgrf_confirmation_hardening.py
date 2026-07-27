from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_vgrf_confirmation_protocol import (
    validate_pilot_analysis,
)
from caeos.vgrf_confirmation_validation import (
    file_sha,
    validate_candidate_result,
    validate_reference_result,
)
from summarize_strict_v4_vgrf_confirmation import analyze, write_outputs


PARAMETERS = {
    "empirical_bayes_shrinkage": 20.0,
    "minimum_reliability": 0.05,
    "risk_blend": 0.25,
    "known_rejection_quantile": 0.95,
    "minimum_f1_gain": -0.002,
    "maximum_correct_risk_increase": 0.01,
    "minimum_auc_gain": 0.0,
    "minimum_separation_gain": 0.0,
    "minimum_strict_proxy_gain": 0.005,
}


def build_protocol(root: Path) -> dict:
    csv_path = root / "input.csv"
    config_path = root / "config.json"
    csv_path.write_text("feature,label\n1,known\n", encoding="utf-8")
    config_path.write_text("{}\n", encoding="utf-8")
    inputs = []
    for seed in (311, 313):
        for index in range(102):
            suite = f"suite_{index % 7}"
            scenario = f"scenario_{index}"
            source_path = (
                root
                / "source"
                / suite
                / f"{scenario}_seed7"
                / "provenance.json"
            )
            if not source_path.exists():
                source_path.parent.mkdir(parents=True, exist_ok=True)
                source_path.write_text(
                    json.dumps(
                        {
                            "command": [
                                "python",
                                "train_hybrid_open_set.py",
                                "--csv",
                                str(csv_path),
                                "--config",
                                "config.json",
                                "--unknown-classes",
                                scenario,
                                "--risk-policy-name",
                                "source_policy",
                                "--seed",
                                "7",
                                "--output-dir",
                                "source-output",
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
            inputs.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "unknown_classes": scenario,
                    "csv": str(csv_path),
                    "csv_sha256": file_sha(csv_path),
                    "config": "config.json",
                    "config_sha256": file_sha(config_path),
                    "source_provenance": source_path.relative_to(
                        root
                    ).as_posix(),
                    "source_provenance_sha256": file_sha(source_path),
                }
            )
    protocol = {
        "schema_version": "strict_v4_vgrf_confirmation_protocol_v1",
        "status": (
            "frozen_after_positive_seed307_pilot_before_seed311_313_"
            "full102_metrics"
        ),
        "known_only_parameters": PARAMETERS,
        "implementation_sha256": {
            "train_hybrid_open_set.py": "a" * 64
        },
        "confirmation": {
            "inputs": inputs,
            "bootstrap": {"replicates": 30, "seed": 20260723},
            "gate": {
                "minimum_fully_nonregressing_suite_count": 6,
                "minimum_suite_metric_gain": -0.005,
                "minimum_enabled_scenarios": 20,
                "minimum_positive_scenario_composite_count": 120,
                "minimum_mean_known_macro_f1_gain": -0.002,
                "minimum_scenario_known_macro_f1_gain": -0.01,
                "maximum_temperature_reconstruction_error": 1e-10,
            },
        },
        "claim_boundary": {
            "confirmation_does_not_replace_external_gates": True
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def payload_for(
    protocol: dict,
    record: dict,
    reference: Path,
) -> dict:
    parameters = {
        "shrinkage": PARAMETERS["empirical_bayes_shrinkage"],
        "minimum_reliability": PARAMETERS["minimum_reliability"],
        "risk_blend": PARAMETERS["risk_blend"],
        "known_rejection_quantile": PARAMETERS[
            "known_rejection_quantile"
        ],
        "minimum_f1_gain": PARAMETERS["minimum_f1_gain"],
        "maximum_correct_risk_increase": PARAMETERS[
            "maximum_correct_risk_increase"
        ],
        "minimum_auc_gain": PARAMETERS["minimum_auc_gain"],
        "minimum_separation_gain": PARAMETERS[
            "minimum_separation_gain"
        ],
        "minimum_strict_proxy_gain": PARAMETERS[
            "minimum_strict_proxy_gain"
        ],
    }
    return {
        "schema_version": (
            "strict_v4_validation_gated_reliability_fusion_metrics_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": record["training_seed"],
        "parameters": parameters,
        "validation_gate": {"enabled": True},
        "thresholds": {"reference": 0.5, "candidate": 0.5},
        "reports": {
            "reference": {
                "known_macro_f1": 0.80,
                "unknown_auroc": 0.60,
                "unknown_aupr": 0.50,
                "unknown_fpr95": 0.40,
                "oscr": 0.55,
            },
            "candidate": {
                "known_macro_f1": 0.81,
                "unknown_auroc": 0.70,
                "unknown_aupr": 0.60,
                "unknown_fpr95": 0.30,
                "oscr": 0.65,
            },
        },
        "diagnostics": {
            "enabled": True,
            "exact_fallback": False,
            "validation_temperature_reconstruction_max_abs_error": 0.0,
            "test_temperature_reconstruction_max_abs_error": 0.0,
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": (
                False
            ),
            "test_labels_used_for_final_metrics_only": True,
        },
        "input_sha256": {
            "evidence_package": file_sha(
                reference / "evidence_package.npz"
            ),
            "scores": file_sha(reference / "scores.npz"),
        },
    }


def materialize(
    root: Path,
    protocol: dict,
) -> tuple[Path, Path]:
    run_root = root / "candidate"
    reference_root = root / "reference"
    for record in protocol["confirmation"]["inputs"]:
        suffix = f'{record["scenario"]}_seed{record["training_seed"]}'
        reference = reference_root / record["suite"] / suffix
        candidate = run_root / record["suite"] / suffix
        reference.mkdir(parents=True, exist_ok=True)
        candidate.mkdir(parents=True, exist_ok=True)
        (reference / "evidence_package.npz").write_bytes(b"evidence")
        (reference / "scores.npz").write_bytes(b"scores")
        (reference / "metrics.json").write_text(
            "{}\n", encoding="utf-8"
        )
        source = json.loads(
            (root / record["source_provenance"]).read_text(
                encoding="utf-8"
            )
        )
        command = list(source["command"])
        command[command.index("--seed") + 1] = str(
            record["training_seed"]
        )
        command[command.index("--output-dir") + 1] = str(
            reference.resolve()
        )
        command[command.index("--risk-policy-name") + 1] = (
            "strict_v4_vgrf_confirmation_reference_v1"
        )
        provenance = {
            "schema_version": 1,
            "task": {
                "suite": record["suite"],
                "scenario": record["scenario"],
                "unknown_classes": record["unknown_classes"],
                "seed": record["training_seed"],
            },
            "command": command,
            "inputs": {
                "csv": {"path": record["csv"]},
                "config": {"sha256": record["config_sha256"]},
            },
            "code": {
                "files": {
                    str(root / "train_hybrid_open_set.py"): "a" * 64
                }
            },
        }
        (reference / "provenance.json").write_text(
            json.dumps(provenance), encoding="utf-8"
        )
        payload = payload_for(protocol, record, reference)
        (candidate / "metrics.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
    return run_root, reference_root


class VGRFConfirmationHardeningTests(unittest.TestCase):
    def test_confirmation_requires_deterministic_pilot_recomputation(
        self,
    ) -> None:
        pilot_protocol = {"manifest_sha256": "a" * 64}
        pilot_analysis = {
            "protocol_manifest_sha256": "a" * 64,
            "passes": True,
            "decision": "freeze_seed311_313_full102_confirmation",
        }
        with patch(
            "create_strict_v4_vgrf_confirmation_protocol.analyze_pilot",
            return_value=dict(pilot_analysis),
        ):
            validate_pilot_analysis(
                pilot_protocol, pilot_analysis, Path("unused")
            )
        with patch(
            "create_strict_v4_vgrf_confirmation_protocol.analyze_pilot",
            return_value={**pilot_analysis, "passes": False},
        ):
            with self.assertRaisesRegex(ValueError, "recomputation"):
                validate_pilot_analysis(
                    pilot_protocol, pilot_analysis, Path("unused")
                )

    def test_all_204_valid_results_select_vgrf_as_one_algorithm(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = build_protocol(root)
            run_root, reference_root = materialize(root, protocol)
            result = analyze(protocol, run_root, reference_root, root)
            output = root / "output"
            write_outputs(result, output)
            selection = json.loads(
                (output / "final_selection.json").read_text()
            )
        self.assertTrue(result["passes"])
        self.assertEqual(result["paired_result_count"], 204)
        self.assertEqual(
            result["selected_algorithm"],
            "caeos_validation_gated_class_conditional_reliability_fusion",
        )
        self.assertEqual(
            selection["manifest_sha256"], canonical_hash(selection)
        )

    def test_tampered_input_sha_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = build_protocol(root)
            run_root, reference_root = materialize(root, protocol)
            record = protocol["confirmation"]["inputs"][0]
            suffix = f'{record["scenario"]}_seed{record["training_seed"]}'
            path = run_root / record["suite"] / suffix / "metrics.json"
            payload = json.loads(path.read_text())
            payload["input_sha256"]["scores"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "input SHA"):
                validate_candidate_result(
                    payload,
                    record,
                    protocol,
                    reference_root / record["suite"] / suffix,
                )

    def test_unknown_label_use_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = build_protocol(root)
            run_root, reference_root = materialize(root, protocol)
            record = protocol["confirmation"]["inputs"][0]
            suffix = f'{record["scenario"]}_seed{record["training_seed"]}'
            path = run_root / record["suite"] / suffix / "metrics.json"
            payload = json.loads(path.read_text())
            payload["diagnostics"][
                "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
            ] = True
            with self.assertRaisesRegex(ValueError, "no-leak"):
                validate_candidate_result(
                    payload,
                    record,
                    protocol,
                    reference_root / record["suite"] / suffix,
                )

    def test_duplicate_protocol_input_fails_before_aggregation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = build_protocol(root)
            protocol["confirmation"]["inputs"][-1] = dict(
                protocol["confirmation"]["inputs"][0]
            )
            protocol["manifest_sha256"] = canonical_hash(protocol)
            with self.assertRaisesRegex(ValueError, "204 unique"):
                analyze(
                    protocol,
                    root / "candidate",
                    root / "reference",
                    root,
                )

    def test_stale_reference_training_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = build_protocol(root)
            _, reference_root = materialize(root, protocol)
            record = protocol["confirmation"]["inputs"][0]
            suffix = f'{record["scenario"]}_seed{record["training_seed"]}'
            reference = reference_root / record["suite"] / suffix
            provenance_path = reference / "provenance.json"
            provenance = json.loads(provenance_path.read_text())
            provenance["task"]["seed"] = 7
            provenance_path.write_text(json.dumps(provenance))
            with self.assertRaisesRegex(ValueError, "task identity"):
                validate_reference_result(
                    reference, record, protocol, root
                )


if __name__ == "__main__":
    unittest.main()
