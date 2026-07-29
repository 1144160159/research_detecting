from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import joblib
import numpy as np
import pandas as pd

from caeos.pairwise_deployment import PairwiseDeploymentBundle
from caeos.selected_system_runtime import SelectedSystemRuntime
from capture_krc_parrot_deployment_bundle import trainer_namespace
from capture_mdr_parrot_deployment_bundle import source_benign_metrics
from capture_pairwise_runtime import file_hash
from certify_rrc_csr_scenario import (
    certify_seed_records,
    seed_record_from_capture,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_parrot_safety_protocol import build_model_pairs
from evaluate_mdr_parrot_capture import batched_predictions, benign_metrics
from materialize_rrc_csr_runtime import materialize
from run_strict_v4_selected_system_external_malicious import (
    ALGORITHMS,
    opendetect_policy,
    pairwise_policy,
    rrc_protocol,
)
from summarize_strict_v4_mdr_parrot_safety import aggregate as mdr_aggregate
import train_hybrid_open_set as trainer


PROTOCOL_SCHEMA = "strict_v4_selected_system_parrot_safety_protocol_v1"
DEPLOYMENT_SCHEMA = "strict_v4_selected_system_parrot_deployment_v1"
METRICS_SCHEMA = "strict_v4_selected_system_parrot_model_pair_metrics_v1"
SUMMARY_SCHEMA = "strict_v4_selected_system_parrot_safety_summary_v1"
AUDIT_SCHEMA = "strict_v4_selected_system_parrot_safety_audit_v1"
PAIRWISE_RISK = "missing_aware_cauchy_modality_support_union"
IMPLEMENTATION_FILES = (
    "run_strict_v4_selected_system_parrot_safety.py",
    "caeos/selected_system_runtime.py",
    "caeos/pairwise_deployment.py",
    "capture_pairwise_runtime.py",
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "materialize_rrc_csr_runtime.py",
    "summarize_strict_v4_mdr_parrot_safety.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def slug(value: str) -> str:
    output = "".join(
        character.lower() if character.isalnum() else "_"
        for character in str(value)
    ).strip("_")
    if not output:
        raise ValueError("empty scenario slug")
    return output


def identity(source: dict[str, Any]) -> tuple[str, int]:
    return str(source["scenario"]), int(source["training_seed"])


def block_path(run_root: Path, source: dict[str, Any]) -> Path:
    scenario, seed = identity(source)
    return (
        run_root
        / "model_pairs"
        / slug(str(source["suite"]))
        / slug(scenario)
        / f"seed{seed}"
    )


def output_counts(run_root: Path) -> dict[str, int]:
    return {
        "candidate_captures": (
            len(list(run_root.glob("model_pairs/**/candidate_capture/capture_manifest.json")))
            if run_root.exists()
            else 0
        ),
        "deployments": (
            len(list(run_root.glob("model_pairs/**/deployment/capture_manifest.json")))
            if run_root.exists()
            else 0
        ),
        "metrics": (
            len(list(run_root.glob("model_pairs/**/model_pair_metrics.json")))
            if run_root.exists()
            else 0
        ),
        "summary": int((run_root / "summary.json").is_file()),
        "audit": int((run_root / "audit.json").is_file()),
        "completion": int((run_root / "execution_complete.json").is_file()),
    }


def _corruption_seed_index(
    confirmation: dict[str, Any],
) -> dict[tuple[str, str, int], int]:
    return {
        (
            str(task["suite"]),
            str(task["scenario"]),
            int(task["training_seed"]),
        ): int(task["corruption_seed"])
        for task in confirmation["confirmation"]["tasks"]
    }


def create_protocol(
    *,
    project_root: Path,
    run_root: Path,
    activation_path: Path,
    adapter_design_path: Path,
    safety_design_path: Path,
    confirmation_protocol_path: Path,
    confirmation_capture_root: Path,
    comparative_protocol_path: Path,
    comparative_run_root: Path,
    feature_protocol_path: Path,
    feature_summary_path: Path,
) -> dict[str, Any]:
    activation = load(activation_path)
    design = load(adapter_design_path)
    safety_design = load(safety_design_path)
    confirmation = load(confirmation_protocol_path)
    comparative = load(comparative_protocol_path)
    feature_protocol = load(feature_protocol_path)
    feature_summary = load(feature_summary_path)
    require_canonical(
        activation,
        "strict_v4_selected_system_activation_v1",
        "selected-system activation",
    )
    require_canonical(
        design,
        "strict_v4_selected_system_downstream_adapter_design_v1",
        "selected-system adapter design",
    )
    require_canonical(
        safety_design,
        "parrot2025_external_benign_safety_design_v1",
        "PARROT external benign safety design",
    )
    require_canonical(
        confirmation,
        "strict_v4_krc_csr_confirmation_protocol_v1",
        "KRC confirmation source-task protocol",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "OpenDetect comparative source protocol",
    )
    require_canonical(
        feature_protocol,
        "parrot2025_full_no_decryption_feature_protocol_v1",
        "PARROT no-decryption feature protocol",
    )
    require_canonical(
        feature_summary,
        "parrot2025_full_no_decryption_feature_summary_v1",
        "PARROT no-decryption feature summary",
    )
    selected = activation.get("selected_algorithm")
    snapshot = activation.get("selection_snapshot", {})
    if (
        activation.get("execution_admitted") is not True
        or snapshot.get("final") is not True
        or snapshot.get("selected_algorithm") != selected
        or activation.get("selection_snapshot_sha256")
        != canonical_hash(snapshot)
        or selected not in ALGORITHMS
        or design.get("activation", {}).get("allowed_selected_algorithms")
        != list(ALGORITHMS)
        or safety_design.get("dataset_role")
        != "external_benign_mobile_application_domain_shift_safety_only"
        or safety_design.get("artifact_contract", {}).get(
            "parrot_used_for_training_validation_or_calibration"
        )
        is not False
        or activation.get("input_manifest_sha256", {}).get("adapter_design")
        != design["manifest_sha256"]
        or feature_summary.get("protocol_manifest_sha256")
        != feature_protocol["manifest_sha256"]
        or feature_summary.get("passed") is not True
        or not all(feature_summary.get("validation", {}).values())
        or int(feature_summary.get("capture_count", -1)) != 320
        or int(feature_summary.get("application_count", -1)) != 80
        or len(feature_protocol.get("feature_columns", [])) != 56
        or len(feature_protocol.get("captures", [])) != 320
    ):
        raise ValueError("selected-system PARROT activation/feature gate failed")
    sources = build_model_pairs(
        confirmation_protocol=confirmation,
        capture_root=confirmation_capture_root,
        comparative=comparative,
        project_root=project_root,
        comparative_run_root=comparative_run_root,
    )
    corruption = _corruption_seed_index(confirmation)
    normalized = []
    for source in sources:
        key = (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        )
        normalized.append(
            {
                **source,
                "corruption_seed": corruption[key],
                "augmentation_seed": int(source["training_seed"]),
                "fresh_candidate_refit_required": True,
                "candidate_refit_uses_parrot": False,
            }
        )
    identities = {identity(source) for source in normalized}
    if (
        len(normalized) != 30
        or len(identities) != 30
        or len({source["scenario"] for source in normalized}) != 10
    ):
        raise ValueError("PARROT source matrix must contain USTC 10x3")
    counts = output_counts(run_root)
    if any(counts.values()):
        raise ValueError("PARROT protocol requires a zero-result run root")
    implementation = {}
    for relative in IMPLEMENTATION_FILES:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        implementation[relative] = file_hash(path)
    feature_root = Path(feature_protocol["output_root"]).resolve()
    value: dict[str, Any] = {
        "schema_version": PROTOCOL_SCHEMA,
        "state": "admitted_after_final_selection_and_complete_features",
        "execution_admitted": True,
        "selected_algorithm": selected,
        "runtime_contract_schema": "strict_v4_selected_system_runtime_v1",
        "source_model_pairs": normalized,
        "source_model_pair_count": 30,
        "source_suite": "ustc_tfc2016",
        "candidate_training": {
            "fresh_refit_per_source_split": True,
            "parrot_excluded_from_fit_selection_calibration_and_threshold": True,
            "pairwise_runtime_policy": pairwise_policy(selected),
            "robust_runtime_policy": {
                "augmentation_weight": 0.5,
                "training_sample_fraction": 0.25,
                "health_quantile": 0.99,
            },
            "rrc_backend_protocol": (
                rrc_protocol(
                    [
                        {
                            "dataset": "ustc_tfc2016",
                            "unknown_attack_family": source["scenario"],
                            "training_seed": int(source["training_seed"]),
                            "validation_profile_seed": int(
                                source["corruption_seed"]
                            ),
                        }
                        for source in normalized
                    ]
                )
                if selected == "rrc_csr_caeos_v1"
                else None
            ),
        },
        "opendetect_policy": {
            **opendetect_policy(),
            "source": "frozen_comparative_runtime_with_paired_split",
            "fresh_refit_for_parrot": False,
        },
        "feature_root": feature_root.as_posix(),
        "feature_columns": list(feature_protocol["feature_columns"]),
        "metadata_columns": list(feature_protocol["metadata_columns"]),
        "feature_shard_manifest_sha256": feature_summary[
            "shard_manifest_sha256"
        ],
        "parrot_captures": list(feature_protocol["captures"]),
        "capture_count": 320,
        "application_count": 80,
        "aggregation": {
            "unit": "capture_after_averaging_30_model_pairs",
            "capture_block_bootstrap_repetitions": 10000,
            "capture_block_bootstrap_seed": 20260726,
            "application_has_four_capture_blocks": True,
        },
        "confirmation_gate": safety_design["confirmation_gate"],
        "resource_contract": {
            "requires_self_algorithm_confirmation_idle": True,
            "candidate_capture_outer_workers": 4,
            "candidate_fit_jobs_per_worker": 8,
            "capture_phase_precedes_parrot_inference": True,
            "subprocess_prefix": ["ionice", "-c", "3", "nice", "-n", "19"],
        },
        "run_root": run_root.resolve().as_posix(),
        "output_counts_at_freeze": counts,
        "input_manifest_sha256": {
            "activation": activation["manifest_sha256"],
            "adapter_design": design["manifest_sha256"],
            "parrot_safety_design": safety_design["manifest_sha256"],
            "confirmation_protocol": confirmation["manifest_sha256"],
            "comparative_protocol": comparative["manifest_sha256"],
            "feature_protocol": feature_protocol["manifest_sha256"],
            "feature_summary": feature_summary["manifest_sha256"],
        },
        "input_file_sha256": {
            "activation": file_hash(activation_path),
            "adapter_design": file_hash(adapter_design_path),
            "parrot_safety_design": file_hash(safety_design_path),
            "confirmation_protocol": file_hash(confirmation_protocol_path),
            "comparative_protocol": file_hash(comparative_protocol_path),
            "feature_protocol": file_hash(feature_protocol_path),
            "feature_summary": file_hash(feature_summary_path),
        },
        "implementation_sha256": dict(sorted(implementation.items())),
        "claim_boundary": {
            "parrot_is_external_benign_safety_only": True,
            "malicious_accuracy_or_parrot_sota_not_supported": True,
            "all_algorithms_use_same_ustc_source_matrix": True,
            "candidate_is_freshly_refit_without_parrot": True,
            "algorithm_renaming_or_result_splicing_forbidden": True,
            "payload_decryption_used": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def set_option(arguments: list[str], option: str, value: Any) -> None:
    if option in arguments:
        index = arguments.index(option)
        if index + 1 >= len(arguments):
            raise ValueError(f"option has no value: {option}")
        arguments[index + 1] = str(value)
    else:
        arguments.extend((option, str(value)))


def candidate_arguments(
    source: dict[str, Any],
    protocol: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    arguments = list(source["clean_trainer_arguments"])
    policy = protocol["candidate_training"]["pairwise_runtime_policy"]
    replacements = {
        "--seed": int(source["training_seed"]),
        "--output-dir": output_dir,
        "--jobs": protocol["resource_contract"]["candidate_fit_jobs_per_worker"],
        "--risk-selection": policy["risk_selection"],
        "--pseudo-unknown-max-alpha": policy["pseudo_unknown_max_alpha"],
        "--pseudo-unknown-min-fold-gain": policy[
            "pseudo_unknown_min_fold_gain"
        ],
        "--boundary-hard-pseudo-fraction": policy[
            "boundary_hard_pseudo_fraction"
        ],
        "--boundary-interpolation": policy["boundary_interpolation"],
        "--boundary-max-per-task": policy["boundary_max_per_task"],
        "--boundary-training-objective": policy[
            "boundary_training_objective"
        ],
        "--risk-policy-name": policy["risk_policy_name"],
    }
    for option, value in replacements.items():
        set_option(arguments, option, value)
    return arguments


def candidate_capture_command(
    *,
    python: str,
    project_root: Path,
    run_root: Path,
    protocol: dict[str, Any],
    source: dict[str, Any],
) -> list[str]:
    block = block_path(run_root, source)
    selected = protocol["selected_algorithm"]
    if selected in ("caeos_pairwise", "caeos_pug"):
        return [
            python,
            str(project_root / "capture_pairwise_runtime.py"),
            "--trainer",
            str(project_root / "train_hybrid_open_set.py"),
            "--capture-dir",
            str(block / "candidate_capture"),
            "--",
            *candidate_arguments(source, protocol, block / "source_train"),
        ]
    robust = protocol["candidate_training"]["robust_runtime_policy"]
    script = (
        "capture_krc_csr_confirmation_runtime.py"
        if selected == "krc_csr_caeos_v1"
        else "capture_csr_caeos_runtime.py"
    )
    capture_dir = (
        block / "candidate_capture"
        if selected == "krc_csr_caeos_v1"
        else block / "source_csr_capture"
    )
    return [
        python,
        str(project_root / script),
        "--clean-trainer",
        str(project_root / "train_hybrid_open_set.py"),
        "--robust-trainer",
        str(project_root / "train_mdr_caeos_open_set.py"),
        "--capture-dir",
        str(capture_dir),
        "--suite",
        str(source["suite"]),
        "--scenario",
        str(source["scenario"]),
        "--weight",
        str(robust["augmentation_weight"]),
        "--sample-fraction",
        str(robust["training_sample_fraction"]),
        "--training-seed",
        str(source["training_seed"]),
        "--augmentation-seed",
        str(source["augmentation_seed"]),
        "--health-quantile",
        str(robust["health_quantile"]),
        "--validation-corruption-seed",
        str(source["corruption_seed"]),
        "--",
        *candidate_arguments(
            source, protocol, capture_dir / "ignored_output"
        ),
    ]


def source_capture_dir(
    run_root: Path, source: dict[str, Any], selected: str
) -> Path:
    block = block_path(run_root, source)
    return (
        block / "source_csr_capture"
        if selected == "rrc_csr_caeos_v1"
        else block / "candidate_capture"
    )


def validate_source_capture(
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> bool:
    selected = protocol["selected_algorithm"]
    directory = source_capture_dir(run_root, source, selected)
    manifest_path = directory / "capture_manifest.json"
    if not manifest_path.is_file():
        return False
    value = load(manifest_path)
    expected_schema = {
        "caeos_pairwise": "strict_v4_pairwise_runtime_capture_v1",
        "caeos_pug": "strict_v4_pairwise_runtime_capture_v1",
        "krc_csr_caeos_v1": "strict_v4_krc_csr_runtime_capture_v1",
        "rrc_csr_caeos_v1": "strict_v4_csr_caeos_runtime_capture_v1",
    }[selected]
    artifact_name = (
        value.get("deployment_artifact")
        if selected in ("caeos_pairwise", "caeos_pug")
        else value.get("runtime_artifact")
    )
    input_name = (
        value.get("benchmark_inputs")
        if selected in ("caeos_pairwise", "caeos_pug")
        else value.get("evaluation_inputs")
    )
    artifact = directory / str(artifact_name or "")
    inputs = directory / str(input_name or "")
    expected_arguments = candidate_arguments(
        source,
        protocol,
        (
            block_path(run_root, source) / "source_train"
            if selected in ("caeos_pairwise", "caeos_pug")
            else directory / "ignored_output"
        ),
    )
    archived_arguments = (
        value.get("trainer_arguments")
        if selected in ("caeos_pairwise", "caeos_pug")
        else value.get("clean_trainer_arguments")
    )
    if (
        value.get("schema_version") != expected_schema
        or not artifact.is_file()
        or not inputs.is_file()
        or file_hash(artifact)
        != value.get(
            "deployment_artifact_sha256"
            if selected in ("caeos_pairwise", "caeos_pug")
            else "runtime_artifact_sha256"
        )
        or file_hash(inputs)
        != value.get(
            "benchmark_inputs_sha256"
            if selected in ("caeos_pairwise", "caeos_pug")
            else "evaluation_inputs_sha256"
        )
    ):
        raise ValueError(f"invalid selected-system source capture: {directory}")
    if selected in ("caeos_pairwise", "caeos_pug"):
        evidence = value.get("runtime_evidence", {})
        if (
            value.get("equivalence", {}).get("passes") is not True
            or archived_arguments != expected_arguments
            or evidence.get("selected_risk")
            != protocol["candidate_training"]["pairwise_runtime_policy"][
                "expected_runtime_selected_risk"
            ]
            or value.get("benchmark_inputs_contain_labels") is not False
        ):
            raise ValueError("invalid Pairwise-family capture evidence")
        metrics = load(
            block_path(run_root, source) / "source_train" / "metrics.json"
        )
        split = metrics.get("split_metadata", {}).get("split_fingerprint")
    else:
        requested_arguments = candidate_arguments(
            source, protocol, directory / "ignored_output"
        )
        required_options = {
            "--csv": requested_arguments[
                requested_arguments.index("--csv") + 1
            ],
            "--config": requested_arguments[
                requested_arguments.index("--config") + 1
            ],
            "--seed": str(source["training_seed"]),
            "--risk-selection": protocol["candidate_training"][
                "pairwise_runtime_policy"
            ]["risk_selection"],
        }
        option_values = {
            option: (
                archived_arguments[archived_arguments.index(option) + 1]
                if option in archived_arguments
                and archived_arguments.index(option) + 1
                < len(archived_arguments)
                else None
            )
            for option in required_options
        }
        if (
            value.get("state") != "complete"
            or value.get("task")
            != {"suite": source["suite"], "scenario": source["scenario"]}
            or int(value.get("training_seed", -1))
            != int(source["training_seed"])
            or value.get("roundtrip", {}).get("passes") is not True
            or value.get(
                "unknown_or_test_labels_used_for_training_selection_or_calibration"
            )
            is not False
            or option_values
            != {key: str(item) for key, item in required_options.items()}
        ):
            raise ValueError("invalid robust capture evidence")
        split = value.get("split_fingerprint")
    split_value = (
        split.get("combined") if isinstance(split, dict) else split
    )
    if str(split_value) != str(source["source_split_fingerprint"]):
        raise ValueError("fresh candidate source split fingerprint drifted")
    return True


def run_command(command: list[str], directory: Path, prefix: list[str]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / "execution.log"
    started = time.perf_counter()
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"command": command}) + "\n")
        handle.flush()
        completed = subprocess.run(
            [*prefix, *command],
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        failure = {
            "schema_version": "strict_v4_selected_system_parrot_failure_v1",
            "returncode": int(completed.returncode),
            "command": command,
            "wall_seconds": time.perf_counter() - started,
            "log_sha256": file_hash(log),
        }
        write_json(directory / "failure.json", failure)
        raise RuntimeError(f"PARROT source capture failed: {directory}")


def materialize_rrc(
    protocol: dict[str, Any], run_root: Path
) -> None:
    backend = protocol["candidate_training"].get("rrc_backend_protocol")
    require_canonical(
        backend,
        "strict_v4_rrc_csr_execution_protocol_v1",
        "RRC backend protocol",
    )
    sources = protocol.get("source_model_pairs", protocol.get("sources"))
    if not isinstance(sources, list) or not sources:
        raise ValueError("RRC source matrix is missing")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for source in sources:
        key = (str(source["suite"]), str(source["scenario"]))
        grouped.setdefault(key, []).append(source)
    for (suite, scenario), sources in sorted(grouped.items()):
        if len(sources) != 3:
            raise ValueError("RRC requires three source seeds per scenario")
        records = [
            seed_record_from_capture(
                block_path(run_root, source) / "source_csr_capture",
                suite=suite,
                scenario=scenario,
                training_seed=int(source["training_seed"]),
            )
            for source in sources
        ]
        certificate = certify_seed_records(
            records,
            protocol_manifest_sha256=backend["manifest_sha256"],
            suite=suite,
            scenario=scenario,
            expected_training_seeds=sorted(
                int(source["training_seed"]) for source in sources
            ),
        )
        certificate_path = (
            run_root
            / "_rrc_certificates"
            / slug(suite)
            / f"{slug(scenario)}.json"
        )
        if certificate_path.is_file():
            if load(certificate_path) != certificate:
                raise ValueError("RRC scenario certificate is immutable")
        else:
            write_json(certificate_path, certificate)
        for source in sources:
            block = block_path(run_root, source)
            output = block / "candidate_capture"
            manifest_path = output / "capture_manifest.json"
            if manifest_path.is_file():
                value = load(manifest_path)
                require_canonical(
                    value,
                    "strict_v4_rrc_csr_runtime_capture_v1",
                    "RRC candidate capture",
                )
                if (
                    value.get("scenario_certificate_manifest_sha256")
                    != certificate["manifest_sha256"]
                ):
                    raise ValueError("RRC materialization certificate drift")
                continue
            if output.exists() and any(output.iterdir()):
                raise ValueError(f"partial RRC materialization: {output}")
            materialize(
                backend,
                certificate,
                block / "source_csr_capture",
                output,
                suite=suite,
                scenario=scenario,
                training_seed=int(source["training_seed"]),
                corruption_seed=int(source["corruption_seed"]),
            )


def _runtime_context(
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> tuple[Any, Path, list[str], Path, float, list[np.ndarray], np.ndarray, np.ndarray]:
    selected = protocol["selected_algorithm"]
    block = block_path(run_root, source)
    candidate_dir = block / "candidate_capture"
    manifest = load(candidate_dir / "capture_manifest.json")
    if selected in ("caeos_pairwise", "caeos_pug"):
        runtime = joblib.load(candidate_dir / manifest["deployment_artifact"])
        arguments = list(manifest["trainer_arguments"])
        input_path = candidate_dir / manifest["benchmark_inputs"]
        with np.load(input_path, allow_pickle=False) as archive:
            views = [
                np.asarray(archive[name])
                for name in sorted(
                    archive.files,
                    key=lambda name: int(name.rsplit("_", 1)[1]),
                )
            ]
        metrics = load(block / "source_train" / "metrics.json")
        with np.load(
            block / "source_train" / "scores.npz", allow_pickle=False
        ) as scores:
            labels = np.asarray(scores["test_labels"], dtype=np.int64)
            unknown = np.asarray(scores["test_unknown"], dtype=bool)
        selected_risk = runtime.evidence()["selected_risk"]
        threshold = float(metrics["validation_thresholds"][selected_risk])
        return (
            runtime,
            candidate_dir,
            arguments,
            input_path,
            threshold,
            views,
            labels,
            unknown,
        )
    source_dir = (
        candidate_dir
        if selected == "krc_csr_caeos_v1"
        else block / "source_csr_capture"
    )
    source_manifest = load(source_dir / "capture_manifest.json")
    arguments = list(source_manifest["clean_trainer_arguments"])
    input_path = candidate_dir / manifest["evaluation_inputs"]
    runtime = joblib.load(candidate_dir / manifest["runtime_artifact"])
    with np.load(input_path, allow_pickle=False) as archive:
        modality_count = int(runtime.evidence()["modality_count"])
        views = [
            np.asarray(archive[f"view_{index}"])
            for index in range(modality_count)
        ]
        labels = np.asarray(archive["test_labels"], dtype=np.int64)
        unknown = np.asarray(archive["test_unknown"], dtype=bool)
    return (
        runtime,
        source_dir,
        arguments,
        input_path,
        float(runtime.clean_threshold),
        views,
        labels,
        unknown,
    )


def capture_deployment(
    *,
    protocol: dict[str, Any],
    project_root: Path,
    run_root: Path,
    source: dict[str, Any],
) -> dict[str, Any]:
    selected = protocol["selected_algorithm"]
    block = block_path(run_root, source)
    (
        runtime,
        source_dir,
        arguments,
        input_path,
        threshold,
        frozen_views,
        labels,
        unknown,
    ) = _runtime_context(protocol, run_root, source)
    args, config_path, data = trainer_namespace(arguments, project_root)
    prepared_views = [np.asarray(view) for view in trainer.views(data.test)]
    if (
        len(prepared_views) != len(frozen_views)
        or not all(
            np.array_equal(left, right)
            for left, right in zip(prepared_views, frozen_views)
        )
    ):
        raise ValueError("selected-system preprocessing replay failed")
    adapter = SelectedSystemRuntime(runtime, selected, threshold)
    preprocessing = data.preprocessing
    deployment = PairwiseDeploymentBundle(
        runtime=adapter,
        modality_names=tuple(data.modality_names),
        modalities={
            str(name): tuple(columns)
            for name, columns in preprocessing["modalities"].items()
        },
        processor_states={
            str(name): {
                key: list(values) for key, values in state.items()
            }
            for name, state in preprocessing["processors"].items()
        },
        class_names=tuple(data.class_names),
        benign_index=int(data.benign_index),
        selected_threshold=threshold,
        risk_policy_name=selected,
        source_config_sha256=file_hash(config_path),
    )
    evidence = deployment.evidence()
    if (
        evidence.get("feature_count") != 56
        or evidence.get("runtime_evidence", {}).get("selected_algorithm")
        != selected
    ):
        raise ValueError("selected-system deployment identity drift")
    output_dir = block / "deployment"
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / "selected_system_deployment.joblib"
    joblib.dump(deployment, artifact, compress=3)
    restored = joblib.load(artifact)
    before = adapter.predict(frozen_views)
    after = restored.predict_views(frozen_views)
    roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(before["prediction"], after["closed_set_index"])
        ),
        "risk_max_absolute_difference": float(
            np.max(np.abs(before["risk"] - after["risk"]))
        ),
        "probability_max_absolute_difference": float(
            np.max(np.abs(before["probability"] - after["probability"]))
        ),
    }
    roundtrip["passes"] = bool(
        roundtrip["prediction_array_equal"]
        and roundtrip["risk_max_absolute_difference"] <= 1e-12
        and roundtrip["probability_max_absolute_difference"] <= 1e-12
    )
    if not roundtrip["passes"]:
        raise ValueError("selected-system deployment roundtrip failed")
    benign = (~unknown) & (labels == deployment.benign_index)
    if not benign.any():
        raise ValueError("source benign reference is empty")
    benign_output = restored.predict_views(
        [view[benign] for view in frozen_views]
    )
    benign_output["prediction"] = benign_output["closed_set_index"]
    benign_output["threshold"] = np.full(
        int(benign.sum()), deployment.selected_threshold
    )
    source_manifest_path = source_dir / "capture_manifest.json"
    value: dict[str, Any] = {
        "schema_version": DEPLOYMENT_SCHEMA,
        "state": "complete",
        "selected_algorithm": selected,
        "scenario": source["scenario"],
        "training_seed": int(source["training_seed"]),
        "source_split_fingerprint": source["source_split_fingerprint"],
        "source_capture_manifest_file_sha256": file_hash(source_manifest_path),
        "source_runtime_input_sha256": file_hash(input_path),
        "source_config_sha256": file_hash(config_path),
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_evidence": evidence,
        "preprocessing_replay": {"all_view_arrays_equal": True},
        "serialization_roundtrip": roundtrip,
        "source_benign_reference": source_benign_metrics(
            benign_output, deployment.benign_index
        ),
        "source_benign_labels_used_for_final_reference_only": True,
        "fresh_candidate_refit_performed": True,
        "parrot_used_for_fit_selection_calibration_or_threshold": False,
        "payload_decryption_used": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    write_json(output_dir / "capture_manifest.json", value)
    return value


def evaluate_model_pair(
    *,
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> dict[str, Any]:
    block = block_path(run_root, source)
    deployment_dir = block / "deployment"
    manifest_path = deployment_dir / "capture_manifest.json"
    manifest = load(manifest_path)
    require_canonical(manifest, DEPLOYMENT_SCHEMA, "PARROT deployment")
    artifact = deployment_dir / manifest["deployment_artifact"]
    comparator_path = Path(source["opendetect_runtime"])
    if (
        manifest.get("selected_algorithm")
        != protocol["selected_algorithm"]
        or manifest.get("scenario") != source["scenario"]
        or int(manifest.get("training_seed", -1))
        != int(source["training_seed"])
        or manifest.get("source_split_fingerprint")
        != source["source_split_fingerprint"]
        or file_hash(artifact) != manifest["deployment_artifact_sha256"]
        or file_hash(comparator_path)
        != source["opendetect_runtime_sha256"]
    ):
        raise ValueError("PARROT model-pair identity drift")
    candidate = joblib.load(artifact)
    comparator = joblib.load(comparator_path)
    evidence = candidate.evidence()
    if (
        evidence.get("schema_version")
        != "strict_v4_pairwise_deployment_bundle_v2"
        or evidence.get("feature_count") != 56
        or list(candidate.feature_columns) != protocol["feature_columns"]
        or evidence.get("runtime_evidence", {}).get("selected_algorithm")
        != protocol["selected_algorithm"]
    ):
        raise ValueError("PARROT deployment feature/runtime contract drift")
    records = []
    feature_root = Path(protocol["feature_root"])
    for capture in protocol["parrot_captures"]:
        capture_id = str(capture["capture_id"])
        shard = feature_root / "shards" / capture_id
        shard_manifest = load(shard / "manifest.json")
        csv_path = shard / "features.csv"
        if (
            shard_manifest.get("schema_version")
            != "parrot2025_no_decryption_feature_shard_v1"
            or shard_manifest.get("manifest_sha256")
            != canonical_hash(shard_manifest)
            or shard_manifest.get("capture") != capture
            or shard_manifest.get("manifest_sha256")
            != protocol["feature_shard_manifest_sha256"][capture_id]
            or shard_manifest.get("features_csv_sha256")
            != file_hash(csv_path)
        ):
            raise ValueError(f"invalid PARROT feature shard: {capture_id}")
        frame = pd.read_csv(csv_path)
        if (
            list(frame.columns)
            != protocol["feature_columns"] + protocol["metadata_columns"]
            or len(frame) != int(shard_manifest["flow_row_count"])
            or not len(frame)
        ):
            raise ValueError(f"invalid PARROT feature frame: {capture_id}")
        views, quality = candidate.transform_frame(frame)
        candidate_output = batched_predictions(candidate.predict_views, views)
        comparator_output = batched_predictions(comparator.predict, views)
        records.append(
            {
                "capture_id": capture_id,
                "application": capture["application"],
                "flow_row_count": int(len(frame)),
                "feature_shard_manifest_sha256": shard_manifest[
                    "manifest_sha256"
                ],
                "feature_csv_sha256": shard_manifest["features_csv_sha256"],
                "input_quality_mean_by_modality": np.mean(
                    quality, axis=0
                ).tolist(),
                protocol["selected_algorithm"]: benign_metrics(
                    candidate_output["prediction"],
                    candidate_output["risk"],
                    candidate.selected_threshold,
                    candidate.benign_index,
                ),
                "opendetect": benign_metrics(
                    comparator_output["prediction"],
                    comparator_output["risk"],
                    float(source["opendetect_threshold"]),
                    candidate.benign_index,
                ),
            }
        )
    if len(records) != 320 or len(
        {record["capture_id"] for record in records}
    ) != 320:
        raise ValueError("PARROT capture coverage is incomplete")
    value: dict[str, Any] = {
        "schema_version": METRICS_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        "source": {
            "suite": "ustc_tfc2016",
            "scenario": source["scenario"],
            "training_seed": int(source["training_seed"]),
            "source_split_fingerprint": source["source_split_fingerprint"],
        },
        "deployment_manifest_file_sha256": file_hash(manifest_path),
        "deployment_artifact_sha256": manifest["deployment_artifact_sha256"],
        "opendetect_runtime_sha256": source["opendetect_runtime_sha256"],
        "opendetect_threshold": float(source["opendetect_threshold"]),
        "source_benign_reference": manifest["source_benign_reference"],
        "capture_count": len(records),
        "records": records,
        "failure_count": 0,
        "parrot_features_or_labels_used_for_fit_selection_calibration_or_threshold": False,
        "test_labels_used_for_final_benign_metrics_only": True,
        "fresh_candidate_refit_performed": True,
        "payload_decryption_used": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    write_json(block / "model_pair_metrics.json", value)
    return value


def aggregate(
    records: list[dict[str, Any]], protocol: dict[str, Any]
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "PARROT protocol")
    if len(records) != 30:
        raise ValueError("30 PARROT model pairs required")
    translated_protocol = deepcopy(protocol)
    translated_protocol["schema_version"] = (
        "strict_v4_mdr_parrot_safety_protocol_v1"
    )
    translated_protocol["selected_algorithm"] = "mdr_caeos_v1"
    translated_protocol["manifest_sha256"] = canonical_hash(
        translated_protocol
    )
    translated_records = []
    selected = protocol["selected_algorithm"]
    for record in records:
        require_canonical(record, METRICS_SCHEMA, "PARROT model-pair metrics")
        if (
            record.get("selected_algorithm") != selected
            or record.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or record.get("fresh_candidate_refit_performed") is not True
        ):
            raise ValueError("PARROT model-pair selected algorithm drift")
        translated = deepcopy(record)
        translated["schema_version"] = (
            "strict_v4_mdr_parrot_model_pair_metrics_v1"
        )
        translated["protocol_manifest_sha256"] = translated_protocol[
            "manifest_sha256"
        ]
        for capture in translated["records"]:
            capture["mdr_caeos_v1"] = capture.pop(selected)
        translated["manifest_sha256"] = canonical_hash(translated)
        translated_records.append(translated)
    result = mdr_aggregate(translated_records, translated_protocol)
    encoded = json.dumps(result)
    return json.loads(encoded.replace("mdr_caeos_v1", selected))


def summarize(
    protocol: dict[str, Any], run_root: Path
) -> dict[str, Any]:
    records = []
    registry = []
    for source in protocol["source_model_pairs"]:
        path = block_path(run_root, source) / "model_pair_metrics.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append(load(path))
        registry.append(
            {
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "metrics_file_sha256": file_hash(path),
            }
        )
    value: dict[str, Any] = {
        "schema_version": SUMMARY_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        **aggregate(records, protocol),
        "model_pair_metrics_file_registry": registry,
        "claim_boundary": {
            "successful_gate_allows": (
                "cross_domain_benign_false_alert_safety_noninferiority"
            ),
            "does_not_support_malicious_accuracy_or_parrot_sota": True,
            "does_not_replace_external_malicious_confirmation": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def audit(
    protocol: dict[str, Any],
    summary: dict[str, Any],
    project_root: Path,
    run_root: Path,
) -> dict[str, Any]:
    records = []
    registry = {
        (item["scenario"], int(item["training_seed"])): item
        for item in summary.get("model_pair_metrics_file_registry", [])
    }
    metric_hashes_match = True
    for source in protocol.get("source_model_pairs", []):
        key = identity(source)
        path = block_path(run_root, source) / "model_pair_metrics.json"
        if (
            not path.is_file()
            or key not in registry
            or file_hash(path)
            != registry[key].get("metrics_file_sha256")
        ):
            metric_hashes_match = False
            continue
        records.append(load(path))
    try:
        recomputed = aggregate(records, protocol)
    except (KeyError, TypeError, ValueError):
        recomputed = {}
    implementation_hashes_match = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    feature_hashes_match = True
    feature_root = Path(protocol.get("feature_root", ""))
    for capture in protocol.get("parrot_captures", []):
        capture_id = str(capture["capture_id"])
        path = feature_root / "shards" / capture_id / "manifest.json"
        if not path.is_file():
            feature_hashes_match = False
            break
        value = load(path)
        if (
            value.get("manifest_sha256") != canonical_hash(value)
            or value.get("manifest_sha256")
            != protocol["feature_shard_manifest_sha256"].get(capture_id)
        ):
            feature_hashes_match = False
            break
    recomputed_keys = (
        "model_pair_count",
        "capture_count",
        "application_count",
        "failure_count",
        "capture_blocks",
        "application_records",
        "applications_with_false_alert_rate_at_most_0_20_fraction",
        "capture_block_inference",
        "candidate_minus_source_benign_inference",
        "source_benign_model_reference_values",
        "confirmation_checks",
        "safety_gate_passes",
    )
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version") == PROTOCOL_SCHEMA
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version") == SUMMARY_SCHEMA
            and summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "selected_algorithm_bound_end_to_end": (
            summary.get("selected_algorithm")
            == protocol.get("selected_algorithm")
            and all(
                record.get("selected_algorithm")
                == protocol.get("selected_algorithm")
                for record in records
            )
        ),
        "all_30_metrics_bound_by_hash": (
            metric_hashes_match
            and len(records) == 30
            and len(registry) == 30
        ),
        "all_320_feature_shards_bound_by_hash": feature_hashes_match,
        "implementation_hashes_match": implementation_hashes_match,
        "independent_recomputation_exact": all(
            summary.get(key) == recomputed.get(key)
            for key in recomputed_keys
        ),
        "parrot_excluded_from_fit_selection_calibration_and_threshold": all(
            record.get(
                "parrot_features_or_labels_used_for_fit_selection_"
                "calibration_or_threshold"
            )
            is False
            for record in records
        ),
        "candidate_freshly_refit_without_parrot": all(
            record.get("fresh_candidate_refit_performed") is True
            for record in records
        ),
        "test_labels_used_for_final_metrics_only": all(
            record.get("test_labels_used_for_final_benign_metrics_only")
            is True
            for record in records
        ),
        "payload_decryption_not_used": all(
            record.get("payload_decryption_used") is False
            for record in records
        ),
    }
    integrity = all(checks.values())
    safety = bool(recomputed.get("safety_gate_passes"))
    value: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA,
        "protocol_manifest_sha256": protocol.get("manifest_sha256"),
        "summary_manifest_sha256": summary.get("manifest_sha256"),
        "selected_algorithm": protocol.get("selected_algorithm"),
        "checks": checks,
        "passes": integrity,
        "benign_domain_shift_safety_gate_passes": integrity and safety,
        "claim_boundary": {
            "cross_domain_benign_false_alert_safety_supported": (
                integrity and safety
            ),
            "malicious_detection_accuracy_claim_supported": False,
            "parrot_accuracy_or_sota_claim_supported": False,
            "external_malicious_confirmation_still_required": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def execute(
    *,
    protocol: dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    workers: int,
    python: str,
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "PARROT protocol")
    maximum = int(
        protocol["resource_contract"]["candidate_capture_outer_workers"]
    )
    if (
        protocol.get("execution_admitted") is not True
        or protocol.get("selected_algorithm") not in ALGORITHMS
        or protocol.get("run_root") != run_root.resolve().as_posix()
        or not 1 <= int(workers) <= maximum
    ):
        raise ValueError("invalid admitted PARROT execution")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    prefix = protocol["resource_contract"]["subprocess_prefix"]

    def capture_one(source: dict[str, Any]) -> str:
        selected = protocol["selected_algorithm"]
        directory = source_capture_dir(run_root, source, selected)
        if not validate_source_capture(protocol, run_root, source):
            if directory.exists() and any(directory.iterdir()):
                raise ValueError(f"partial source capture: {directory}")
            run_command(
                candidate_capture_command(
                    python=python,
                    project_root=project_root,
                    run_root=run_root,
                    protocol=protocol,
                    source=source,
                ),
                directory,
                prefix,
            )
            if not validate_source_capture(protocol, run_root, source):
                raise ValueError("candidate capture missing after command")
        return f"{source['scenario']}/seed{source['training_seed']}"

    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = [
            executor.submit(capture_one, source)
            for source in protocol["source_model_pairs"]
        ]
        for future in as_completed(futures):
            print(f"captured {future.result()}", flush=True)
    if protocol["selected_algorithm"] == "rrc_csr_caeos_v1":
        materialize_rrc(protocol, run_root)
    for source in protocol["source_model_pairs"]:
        block = block_path(run_root, source)
        deployment_manifest = block / "deployment" / "capture_manifest.json"
        if not deployment_manifest.is_file():
            capture_deployment(
                protocol=protocol,
                project_root=project_root,
                run_root=run_root,
                source=source,
            )
        else:
            value = load(deployment_manifest)
            require_canonical(value, DEPLOYMENT_SCHEMA, "PARROT deployment")
            if value.get("selected_algorithm") != protocol["selected_algorithm"]:
                raise ValueError("existing deployment algorithm drift")
        metrics_path = block / "model_pair_metrics.json"
        if not metrics_path.is_file():
            evaluate_model_pair(
                protocol=protocol,
                run_root=run_root,
                source=source,
            )
        else:
            value = load(metrics_path)
            require_canonical(value, METRICS_SCHEMA, "PARROT metrics")
            if value.get("selected_algorithm") != protocol["selected_algorithm"]:
                raise ValueError("existing metrics algorithm drift")
    summary = summarize(protocol, run_root)
    write_json(run_root / "summary.json", summary)
    audited = audit(protocol, summary, project_root, run_root)
    write_json(run_root / "audit.json", audited)
    completion: dict[str, Any] = {
        "schema_version": "strict_v4_selected_system_parrot_completion_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(run_root / "summary.json"),
        "audit_manifest_sha256": audited["manifest_sha256"],
        "audit_file_sha256": file_hash(run_root / "audit.json"),
        "selected_algorithm": protocol["selected_algorithm"],
        "integrity_passes": audited["passes"],
        "benign_domain_shift_safety_gate_passes": audited[
            "benign_domain_shift_safety_gate_passes"
        ],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    write_json(run_root / "execution_complete.json", completion)
    return completion


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--activation",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_v1/"
            "activation.json"
        ),
    )
    parser.add_argument(
        "--adapter-design",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--safety-design",
        type=Path,
        default=Path(
            "results/parrot2025_external_benign_safety_v1/"
            "design_protocol.json"
        ),
    )
    parser.add_argument(
        "--confirmation-protocol",
        type=Path,
        default=Path("results/strict_v4_krc_csr_confirmation_v1/protocol.json"),
    )
    parser.add_argument(
        "--confirmation-capture-root",
        type=Path,
        default=Path("runs/strict_v4_krc_csr_confirmation_v1/captures"),
    )
    parser.add_argument(
        "--comparative-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_comparative_corruption_protocol/"
            "protocol_manifest_v2.json"
        ),
    )
    parser.add_argument(
        "--comparative-run-root",
        type=Path,
        default=Path("runs/strict_v4_comparative_corruption"),
    )
    parser.add_argument(
        "--feature-protocol",
        type=Path,
        default=Path("results/parrot2025_full_no_decryption_features_v1/protocol.json"),
    )
    parser.add_argument(
        "--feature-summary",
        type=Path,
        default=Path(
            "results/parrot2025_full_no_decryption_features_v1/"
            "feature_shard_manifest.json"
        ),
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("results/strict_v4_selected_system_downstream_adapter_v1/parrot"),
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_v1/"
            "parrot_safety_protocol.json"
        ),
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--python", default=sys.executable)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    activation_path = resolve(root, args.activation)
    feature_summary_path = resolve(root, args.feature_summary)
    protocol_path = resolve(root, args.protocol)
    run_root = resolve(root, args.run_root)
    if not activation_path.is_file():
        print(
            json.dumps(
                {
                    "state": "pending_selected_system_activation",
                    "protocol_written": False,
                },
                sort_keys=True,
            )
        )
        return
    if not feature_summary_path.is_file():
        print(
            json.dumps(
                {
                    "state": "pending_parrot_feature_summary",
                    "protocol_written": False,
                },
                sort_keys=True,
            )
        )
        return
    if protocol_path.is_file():
        protocol = load(protocol_path)
        require_canonical(protocol, PROTOCOL_SCHEMA, "PARROT protocol")
    else:
        protocol = create_protocol(
            project_root=root,
            run_root=run_root,
            activation_path=activation_path,
            adapter_design_path=resolve(root, args.adapter_design),
            safety_design_path=resolve(root, args.safety_design),
            confirmation_protocol_path=resolve(
                root, args.confirmation_protocol
            ),
            confirmation_capture_root=resolve(
                root, args.confirmation_capture_root
            ),
            comparative_protocol_path=resolve(
                root, args.comparative_protocol
            ),
            comparative_run_root=resolve(root, args.comparative_run_root),
            feature_protocol_path=resolve(root, args.feature_protocol),
            feature_summary_path=feature_summary_path,
        )
        write_json(protocol_path, protocol)
    if not args.execute:
        print(
            json.dumps(
                {
                    "state": protocol["state"],
                    "selected_algorithm": protocol["selected_algorithm"],
                    "protocol_written": True,
                    "manifest_sha256": protocol["manifest_sha256"],
                },
                sort_keys=True,
            )
        )
        return
    completion = execute(
        protocol=protocol,
        protocol_path=protocol_path,
        project_root=root,
        run_root=run_root,
        workers=args.workers,
        python=args.python,
    )
    print(json.dumps(completion, sort_keys=True))


if __name__ == "__main__":
    main()
