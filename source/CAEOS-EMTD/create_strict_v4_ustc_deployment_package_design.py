from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SEEDS = (311, 313)
SUITE = "ustc_tfc2016"
PAIRWISE = "caeos_pairwise"
VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def command_value(command: list[str], flag: str) -> str:
    index = command.index(flag)
    return command[index + 1]


def package_inputs(
    project_root: Path,
    coverage: dict[str, Any],
) -> list[dict[str, Any]]:
    registry = coverage["scenario_registry"][SUITE]
    scenarios = list(registry["scenarios"])
    if registry["count"] != 10 or len(scenarios) != 10:
        raise ValueError("USTC deployment requires exactly ten scenarios")
    source_root = (
        project_root / "runs/strict_v4_full103_pairwise_caeos_seed7"
    )
    records = []
    for scenario in scenarios:
        provenance_path = (
            source_root / SUITE / f"{scenario}_seed7" / "provenance.json"
        )
        provenance = load(provenance_path)
        command = provenance["command"]
        csv_path = Path(command_value(command, "--csv"))
        config_path = project_root / command_value(command, "--config")
        if file_hash(csv_path) != coverage["cache_artifacts"][SUITE]["sha256"]:
            raise ValueError(f"USTC cache SHA mismatch: {scenario}")
        for seed in SEEDS:
            package_id = f"{scenario}_seed{seed}"
            records.append(
                {
                    "package_id": package_id,
                    "suite": SUITE,
                    "scenario": scenario,
                    "unknown_classes": command_value(
                        command, "--unknown-classes"
                    ),
                    "training_seed": seed,
                    "source_seed": 7,
                    "source_provenance": provenance_path.relative_to(
                        project_root
                    ).as_posix(),
                    "source_provenance_sha256": file_hash(provenance_path),
                    "source_parameter_fingerprint": provenance[
                        "parameter_fingerprint"
                    ],
                    "csv": csv_path.as_posix(),
                    "csv_sha256": file_hash(csv_path),
                    "config": config_path.relative_to(
                        project_root
                    ).as_posix(),
                    "config_sha256": file_hash(config_path),
                    "pairwise_reference_run": (
                        f"runs/strict_v4_ustc_deployment_packages_v1/"
                        f"pairwise_reference/{package_id}"
                    ),
                    "package_root": (
                        f"results/strict_v4_ustc_deployment_packages_v1/"
                        f"packages/{package_id}"
                    ),
                }
            )
    if len(records) != 20:
        raise ValueError(f"expected 20 USTC packages, got {len(records)}")
    return records


def create_design(
    project_root: Path,
    coverage_path: Path,
    parrot_protocol_path: Path,
    vgrf_pilot_protocol_path: Path,
    result_root: Path,
    run_root: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    coverage = load(coverage_path)
    parrot = load(parrot_protocol_path)
    vgrf_pilot = load(vgrf_pilot_protocol_path)
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    if parrot.get("manifest_sha256") != canonical_hash(parrot):
        raise ValueError("PARROT feature protocol SHA mismatch")
    if vgrf_pilot.get("manifest_sha256") != canonical_hash(vgrf_pilot):
        raise ValueError("VGRF pilot protocol SHA mismatch")
    observed_records = (
        len(list(result_root.rglob("package_record.json")))
        if result_root.exists()
        else 0
    )
    observed_artifacts = (
        len(list(result_root.rglob("*deployment_bundle.joblib")))
        if result_root.exists()
        else 0
    )
    if observed_records or observed_artifacts:
        raise ValueError("deployment design must freeze before package artifacts")

    config_path = project_root / "configs/ustc_tfc2016_nfstream.json"
    config = load(config_path)
    config_columns = [
        column
        for name in config["modalities"]
        for column in config["modalities"][name]
    ]
    if config_columns != parrot["feature_columns"]:
        raise ValueError("USTC config and PARROT ordered features differ")
    names = (
        "create_strict_v4_ustc_deployment_package_design.py",
        "create_strict_v4_ustc_deployment_package_protocol.py",
        "run_strict_v4_ustc_deployment_packages.py",
        "summarize_strict_v4_ustc_deployment_packages.py",
        "capture_pairwise_deployment_bundle.py",
        "audit_pairwise_deployment_bundle.py",
        "audit_pairwise_parrot_feature_contract.py",
        "caeos/pairwise_deployment.py",
        "caeos/vgrf_deployment.py",
        "caeos/class_conditional_reliability_fusion.py",
        "caeos/validation_gated_reliability_fusion.py",
        "build_vgrf_deployment_bundle.py",
        "audit_vgrf_deployment_bundle.py",
        "scripts/wait_and_run_strict_v4_ustc_deployment_packages.sh",
    )
    design: dict[str, Any] = {
        "schema_version": "strict_v4_ustc_deployment_package_design_v1",
        "status": "frozen_before_final_selection_and_package_artifacts",
        "purpose": (
            "build twenty GPU-private USTC source-domain deployment packages "
            "for the final Pairwise-or-VGRF algorithm"
        ),
        "selection_source": {
            "path": (
                "results/strict_v4_vgrf_confirmation_seed311_313/"
                "final_selection.json"
            ),
            "completion_marker": (
                "results/strict_v4_vgrf_confirmation_seed311_313/"
                "branch_complete"
            ),
            "schema_version": "strict_v4_final_self_algorithm_selection_v1",
            "allowed_algorithms": [PAIRWISE, VGRF],
            "selection_must_exist_before_execution_protocol_freeze": True,
        },
        "package_matrix": {
            "suite": SUITE,
            "scenario_count": 10,
            "seeds": list(SEEDS),
            "package_count": 20,
            "inputs": package_inputs(project_root, coverage),
            "reuse_seed7_sample_cache": True,
            "change_only_training_seed_output_dir_and_risk_policy": True,
            "estimators_and_maximum_per_class_inherited_from_source_provenance": True,
        },
        "pairwise_policy": {
            "capture_schema": "strict_v4_pairwise_deployment_capture_v3",
            "test_and_label_free_validation_exact_replay_required": True,
        },
        "vgrf_policy": {
            "pilot_protocol_manifest_sha256": vgrf_pilot[
                "manifest_sha256"
            ],
            "pilot_protocol_file_sha256": file_hash(
                vgrf_pilot_protocol_path
            ),
            "known_only_parameters": vgrf_pilot[
                "known_only_parameters"
            ],
            "full102_confirmation_required_if_selected": True,
            "source_and_runtime_gate_probability_threshold_must_match": True,
            "stable_runtime_risk_difference_must_be_reported": True,
        },
        "parrot_feature_contract": {
            "protocol_path": parrot_protocol_path.resolve().relative_to(
                project_root
            ).as_posix(),
            "protocol_manifest_sha256": parrot["manifest_sha256"],
            "protocol_file_sha256": file_hash(parrot_protocol_path),
            "feature_count": parrot["feature_count"],
            "feature_columns": parrot["feature_columns"],
            "ustc_config": config_path.relative_to(project_root).as_posix(),
            "ustc_config_sha256": file_hash(config_path),
            "ordered_feature_contract_must_match_for_every_package": True,
        },
        "output_policy": {
            "result_root": result_root.resolve().as_posix(),
            "run_root": run_root.resolve().as_posix(),
            "storage_policy": "gpu_private_do_not_publish",
            "raw_or_processed_training_rows_must_not_be_published": True,
            "formal_model_metrics_admitted": 0,
            "external_execution_admitted_before_all_packages_pass": False,
        },
        "execution_policy": {
            "sequential_packages": True,
            "resume_only_from_hash_validated_package_record": True,
            "five_consecutive_idle_samples_before_start": True,
            "unknown_or_test_labels_used_for_fit_selection_or_threshold": False,
        },
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_file_sha256": file_hash(coverage_path),
        "package_records_observed_at_freeze": observed_records,
        "deployment_artifacts_observed_at_freeze": observed_artifacts,
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in names
        },
        "claim_boundary": {
            "design_or_package_replay_does_not_establish_external_sota": True,
            "parrot_metrics_require_separate_frozen_read_only_execution": True,
            "all_twenty_packages_required_before_external_admission": True,
        },
    }
    design["manifest_sha256"] = canonical_hash(design)
    return design


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--parrot-protocol", type=Path, required=True)
    parser.add_argument("--vgrf-pilot-protocol", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    design = create_design(
        args.project_root,
        args.coverage,
        args.parrot_protocol,
        args.vgrf_pilot_protocol,
        args.result_root,
        args.run_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(design, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(design["manifest_sha256"])


if __name__ == "__main__":
    main()
