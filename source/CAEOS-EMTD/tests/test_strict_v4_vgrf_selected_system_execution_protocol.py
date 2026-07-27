from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_vgrf_selected_system_execution_protocol import (
    VGRF,
    create_execution_protocol,
)


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, dict):
        path.write_text(json.dumps(value), encoding="utf-8")
    else:
        path.write_bytes(bytes(value))
    return file_hash(path)


def fixtures(root: Path, scenario_count: int = 102) -> dict:
    project = root / "project"
    project.mkdir()
    scenarios = [f"scenario_{index:03d}" for index in range(scenario_count)]
    design = canonical(
        {
            "schema_version": (
                "strict_v4_vgrf_selected_system_confirmation_design_v1"
            ),
            "runtime_equivalence_and_efficiency": {"expected_blocks": 204},
            "training_calibration_efficiency": {"expected_pairs": 14},
            "comparative_corruption": {
                "source_pair_count": 306,
                "expected_paired_condition_evaluations": 1530,
            },
            "required_output": {"required_system_gates": ["efficiency"]},
            "claim_boundary": {"no_splicing": True},
            "input_manifest_sha256": {
                "coverage": "c" * 64,
                "corruption": "pending",
            },
        }
    )
    preparation = canonical(
        {
            "schema_version": (
                "strict_v4_vgrf_selected_system_preparation_protocol_v1"
            ),
            "design_manifest_sha256": design["manifest_sha256"],
        }
    )
    inputs = []
    source_registry = []
    comparator_root = project / "runs/opendetect"
    split = "same-split"
    csv = project / "data.csv"
    config = project / "config.yaml"
    provenance_source = project / "seed7_provenance.json"
    csv_sha = write(csv, b"csv")
    config_sha = write(config, b"config")
    provenance_sha = write(provenance_source, {"command": []})
    for scenario in scenarios:
        for seed in (311, 313):
            inputs.append(
                {
                    "suite": "suite",
                    "scenario": scenario,
                    "training_seed": seed,
                    "csv": str(csv),
                    "csv_sha256": csv_sha,
                    "config": str(config.relative_to(project)),
                    "config_sha256": config_sha,
                    "unknown_classes": "unknown",
                    "source_provenance": str(
                        provenance_source.relative_to(project)
                    ),
                    "source_provenance_sha256": provenance_sha,
                    "source_parameter_fingerprint": "fingerprint",
                }
            )
            candidate = (
                project / "runs/vgrf" / "suite" / f"{scenario}_seed{seed}"
            )
            reference = (
                project
                / "runs/pairwise"
                / "suite"
                / f"{scenario}_seed{seed}"
            )
            source_hashes = {
                "candidate_metrics": write(
                    candidate / "metrics.json",
                    {
                        "protocol_manifest_sha256": "pending",
                        "input_sha256": {
                            "scores": "pending",
                            "evidence_package": "pending",
                        },
                        "diagnostics": {
                            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False
                        },
                    },
                ),
                "candidate_scores": write(
                    candidate / "scores.npz", b"candidate"
                ),
                "reference_metrics": write(
                    reference / "metrics.json",
                    {
                        "split_metadata": {
                            "split_fingerprint": {"combined": split}
                        }
                    },
                ),
                "reference_scores": write(
                    reference / "scores.npz", b"reference"
                ),
                "reference_evidence_package": write(
                    reference / "evidence_package.npz", b"evidence"
                ),
                "reference_provenance": write(
                    reference / "provenance.json", {"command": []}
                ),
            }
            comparator = (
                comparator_root
                / "suite"
                / f"{scenario}_seed{seed}_opendetect"
            )
            write(
                comparator / "metrics.json",
                {
                    "model": "opendetect",
                    "selection_evidence": {
                        "unknown_or_test_labels_used_for_fitting_or_selection": False
                    },
                    "split_metadata": {
                        "split_fingerprint": {"combined": split}
                    },
                },
            )
            write(comparator / "scores.npz", b"opendetect")
            write(comparator / "provenance.json", {"command": []})
            write(comparator / "model.pt", b"model")
            source_registry.append(
                {
                    "suite": "suite",
                    "scenario": scenario,
                    "seed": seed,
                    "candidate_root": str(candidate),
                    "reference_root": str(reference),
                    "source_file_sha256": source_hashes,
                }
            )
    vgrf_protocol = canonical(
        {
            "schema_version": "strict_v4_vgrf_confirmation_protocol_v1",
            "confirmation": {"inputs": inputs},
            "known_only_parameters": {
                "empirical_bayes_shrinkage": 20.0,
                "minimum_reliability": 0.05,
                "risk_blend": 0.25,
                "known_rejection_quantile": 0.95,
                "minimum_f1_gain": -0.002,
                "maximum_correct_risk_increase": 0.01,
                "minimum_auc_gain": 0.0,
                "minimum_separation_gain": 0.0,
                "minimum_strict_proxy_gain": 0.005,
            },
        }
    )
    for source in source_registry:
        path = Path(source["candidate_root"]) / "metrics.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["protocol_manifest_sha256"] = vgrf_protocol[
            "manifest_sha256"
        ]
        value["input_sha256"] = {
            "scores": source["source_file_sha256"]["reference_scores"],
            "evidence_package": source["source_file_sha256"][
                "reference_evidence_package"
            ],
        }
        source["source_file_sha256"]["candidate_metrics"] = write(path, value)
    vgrf_summary = canonical(
        {
            "schema_version": "strict_v4_vgrf_confirmation_summary_v1",
            "selected_algorithm": VGRF,
            "passes": True,
            "protocol_manifest_sha256": vgrf_protocol["manifest_sha256"],
        }
    )
    selection = canonical(
        {
            "schema_version": (
                "strict_v4_final_self_algorithm_selection_v1"
            ),
            "selected_algorithm": VGRF,
            "vgrf_confirmation_passes": True,
            "confirmation_summary_manifest_sha256": vgrf_summary[
                "manifest_sha256"
            ],
        }
    )
    reconfirmation_protocol = canonical(
        {
            "schema_version": (
                "strict_v4_selected_external_reconfirmation_protocol_v1"
            ),
            "selected_algorithm": VGRF,
            "source_registry": source_registry,
            "input_manifest_sha256": {
                "final_selection": selection["manifest_sha256"],
                "vgrf_protocol": vgrf_protocol["manifest_sha256"],
                "vgrf_summary": vgrf_summary["manifest_sha256"],
            },
        }
    )
    reconfirmation_summary = canonical(
        {
            "schema_version": (
                "strict_v4_selected_external_reconfirmation_summary_v1"
            ),
            "protocol_manifest_sha256": reconfirmation_protocol[
                "manifest_sha256"
            ],
            "selected_algorithm": VGRF,
            "validation": {"passes": True},
            "decision": {"passes": True},
        }
    )
    corruption_protocol = canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_protocol_v1"
            ),
            "confirmatory_graceful_degradation_gate": {
                "maximum_mean_degradation": {
                    "known_macro_f1": 0.10,
                    "unknown_auroc": 0.15,
                    "unknown_aupr": 0.15,
                    "unknown_fpr95": 0.20,
                    "oscr": 0.15,
                }
            },
        }
    )
    design["input_manifest_sha256"]["corruption"] = (
        corruption_protocol["manifest_sha256"]
    )
    design["manifest_sha256"] = canonical_hash(design)
    preparation["design_manifest_sha256"] = design["manifest_sha256"]
    preparation["manifest_sha256"] = canonical_hash(preparation)
    return {
        "project_root": project,
        "design": design,
        "preparation": preparation,
        "selection": selection,
        "vgrf_protocol": vgrf_protocol,
        "vgrf_summary": vgrf_summary,
        "reconfirmation_protocol": reconfirmation_protocol,
        "reconfirmation_summary": reconfirmation_summary,
        "corruption_protocol": corruption_protocol,
        "comparator_root": comparator_root,
        "source_run_root": project / "runs/seed317",
        "deployment_root": project / "runs/deployments",
        "source_file_sha256": {"input": "a" * 64},
        "implementation_sha256": {"runner": "b" * 64},
        "observed_system_outputs": 0,
    }


class VGRFSelectedSystemExecutionProtocolTests(unittest.TestCase):
    def test_positive_plan_has_exact_306_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            result = create_execution_protocol(**values)
        self.assertEqual(result["source_pair_count"], 306)
        self.assertEqual(
            sum(
                item["source_mode"]
                == "preregistered_seed317_execution"
                for item in result["source_registry"]
            ),
            102,
        )
        self.assertEqual(result["system_outputs_observed_at_freeze"], 0)

    def test_duplicate_source_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            records = values["reconfirmation_protocol"]["source_registry"]
            records[1] = dict(records[0])
            values["reconfirmation_protocol"]["manifest_sha256"] = (
                canonical_hash(values["reconfirmation_protocol"])
            )
            values["reconfirmation_summary"][
                "protocol_manifest_sha256"
            ] = values["reconfirmation_protocol"]["manifest_sha256"]
            values["reconfirmation_summary"]["manifest_sha256"] = (
                canonical_hash(values["reconfirmation_summary"])
            )
            with self.assertRaisesRegex(ValueError, "duplicate"):
                create_execution_protocol(**values)

    def test_missing_source_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            values["reconfirmation_protocol"]["source_registry"].pop()
            values["reconfirmation_protocol"]["manifest_sha256"] = (
                canonical_hash(values["reconfirmation_protocol"])
            )
            values["reconfirmation_summary"][
                "protocol_manifest_sha256"
            ] = values["reconfirmation_protocol"]["manifest_sha256"]
            values["reconfirmation_summary"]["manifest_sha256"] = (
                canonical_hash(values["reconfirmation_summary"])
            )
            with self.assertRaisesRegex(ValueError, "coverage mismatch"):
                create_execution_protocol(**values)

    def test_existing_system_output_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            values["observed_system_outputs"] = 1
            with self.assertRaisesRegex(ValueError, "before system"):
                create_execution_protocol(**values)

    def test_negative_external_effect_is_preserved_and_admissible(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            summary = values["reconfirmation_summary"]
            summary["decision"]["passes"] = False
            summary["manifest_sha256"] = canonical_hash(summary)
            result = create_execution_protocol(**values)
        self.assertFalse(
            result["claim_boundary"][
                "external_accuracy_reconfirmation_passed_before_system_work"
            ]
        )

    def test_non_vgrf_selection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            values["selection"]["selected_algorithm"] = "caeos_pairwise"
            values["selection"]["manifest_sha256"] = canonical_hash(
                values["selection"]
            )
            with self.assertRaisesRegex(ValueError, "VGRF selection"):
                create_execution_protocol(**values)

    def test_source_sha_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            source = values["reconfirmation_protocol"]["source_registry"][0]
            path = Path(source["candidate_root"]) / "scores.npz"
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                create_execution_protocol(**values)

    def test_vgrf_leakage_declaration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            source = values["reconfirmation_protocol"]["source_registry"][0]
            path = Path(source["candidate_root"]) / "metrics.json"
            metric = json.loads(path.read_text(encoding="utf-8"))
            metric["diagnostics"][
                "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
            ] = True
            source["source_file_sha256"]["candidate_metrics"] = write(
                path, metric
            )
            values["reconfirmation_protocol"]["manifest_sha256"] = (
                canonical_hash(values["reconfirmation_protocol"])
            )
            values["reconfirmation_summary"][
                "protocol_manifest_sha256"
            ] = values["reconfirmation_protocol"]["manifest_sha256"]
            values["reconfirmation_summary"]["manifest_sha256"] = (
                canonical_hash(values["reconfirmation_summary"])
            )
            with self.assertRaisesRegex(ValueError, "leakage"):
                create_execution_protocol(**values)


if __name__ == "__main__":
    unittest.main()
