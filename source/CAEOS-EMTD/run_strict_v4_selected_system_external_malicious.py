from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Iterable

import joblib
import numpy as np

from caeos.pseudo_unknown_gated_continuous import PUG_RISK_NAME
from caeos.selected_system_runtime import SelectedSystemRuntime
from capture_pairwise_runtime import file_hash
from certify_rrc_csr_scenario import (
    certify_seed_records,
    seed_record_from_capture,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_external_runtime import report
from materialize_rrc_csr_runtime import materialize
from summarize_strict_v4_krc_external_malicious import comparator_checks
from summarize_strict_v4_mdr_external_malicious import (
    aggregate,
    metric_report,
    split_integrity,
)


ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)
PAIRWISE_RISK = "cauchy_modality_support_union"
PAIRWISE_SELECTION = "nested_boundary_pairwise_pseudo_unknown_blend"
PUG_SELECTION = "nested_pug_continuous_outer_min_p"
PROTOCOL_SCHEMA = "strict_v4_selected_system_external_malicious_protocol_v1"
METRICS_SCHEMA = "strict_v4_selected_system_external_runtime_metrics_v1"
PROVENANCE_SCHEMA = (
    "strict_v4_selected_system_external_malicious_provenance_v1"
)
IMPLEMENTATION_FILES = (
    "run_strict_v4_selected_system_external_malicious.py",
    "capture_pairwise_runtime.py",
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "certify_rrc_csr_scenario.py",
    "materialize_rrc_csr_runtime.py",
    "train_hybrid_open_set.py",
    "train_mdr_caeos_open_set.py",
    "train_neural_open_set.py",
    "evaluate_mdr_external_runtime.py",
    "summarize_strict_v4_mdr_external_malicious.py",
    "caeos/pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/rrc_csr_runtime.py",
    "caeos/selected_system_runtime.py",
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
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_") or (
        "unnamed"
    )


def task_identity(task: dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(task["dataset"]),
        str(task["unknown_attack_family"]),
        int(task["training_seed"]),
    )


def task_block(run_root: Path, task: dict[str, Any]) -> Path:
    return (
        run_root
        / task["dataset"]
        / (
            f"{slug(task['unknown_attack_family'])}_"
            f"seed{int(task['training_seed'])}"
        )
    )


def pairwise_policy(selected_algorithm: str) -> dict[str, Any]:
    if selected_algorithm not in ALGORITHMS:
        raise ValueError("unsupported selected algorithm")
    return {
        "estimators": 80,
        "jobs": 8,
        "known_acceptance": 0.95,
        "risk_selection": (
            PUG_SELECTION
            if selected_algorithm == "caeos_pug"
            else PAIRWISE_SELECTION
        ),
        "expected_runtime_selected_risk": (
            PUG_RISK_NAME
            if selected_algorithm == "caeos_pug"
            else PAIRWISE_RISK
        ),
        "pseudo_unknown_max_alpha": 0.5,
        "pseudo_unknown_min_fold_gain": -0.05,
        "boundary_hard_pseudo_fraction": 0.5,
        "boundary_interpolation": 0.5,
        "boundary_max_per_task": 512,
        "boundary_training_objective": "pairwise",
        "risk_policy_name": (
            "strict_v4_selected_system_external_pug_v1"
            if selected_algorithm == "caeos_pug"
            else "strict_v4_selected_system_external_pairwise_v1"
        ),
        "parameters_fixed_before_external_test_evaluation": True,
    }


def opendetect_policy() -> dict[str, Any]:
    return {
        "epochs": 100,
        "patience": 100,
        "hidden_dim": 128,
        "embedding_dim": 64,
        "known_acceptance": 0.95,
        "parameters_fixed_before_external_test_evaluation": True,
    }


def rrc_protocol(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    mapped = [
        {
            "suite": task["dataset"],
            "scenario": task["unknown_attack_family"],
            "training_seed": int(task["training_seed"]),
            "corruption_seed": int(task["validation_profile_seed"]),
        }
        for task in tasks
    ]
    value: dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
        "state": "admitted_as_selected_system_external_backend",
        "execution_admitted": True,
        "algorithm": "rrc_csr_caeos_v1",
        "tasks": mapped,
        "task_count": len(mapped),
        "certificate_policy": {
            "unit": "dataset_attack_family_three_training_seeds",
            "known_validation_only": True,
            "test_arrays_read": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def output_counts(run_root: Path) -> dict[str, int]:
    return {
        "candidate_capture": (
            len(list(run_root.glob("**/candidate_capture/capture_manifest.json")))
            if run_root.exists()
            else 0
        ),
        "candidate_metrics": (
            len(list(run_root.glob("**/candidate/metrics.json")))
            if run_root.exists()
            else 0
        ),
        "opendetect_metrics": (
            len(list(run_root.glob("**/opendetect/metrics.json")))
            if run_root.exists()
            else 0
        ),
        "summary": int((run_root / "summary.json").is_file()),
        "audit": int((run_root / "audit.json").is_file()),
        "completion": int((run_root / "execution_complete.json").is_file()),
    }


def create_protocol(
    *,
    project_root: Path,
    run_root: Path,
    activation_path: Path,
    adapter_design_path: Path,
    input_protocol_path: Path,
) -> dict[str, Any]:
    activation = load(activation_path)
    design = load(adapter_design_path)
    inputs = load(input_protocol_path)
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
        inputs,
        "strict_v4_krc_external_malicious_input_protocol_v2",
        "external malicious input protocol",
    )
    selected = activation.get("selected_algorithm")
    selection_snapshot = activation.get("selection_snapshot", {})
    allowed = design.get("activation", {}).get(
        "allowed_selected_algorithms", []
    )
    tasks = inputs.get("tasks")
    counts = inputs.get("task_counts", {})
    if (
        activation.get("execution_admitted") is not True
        or selection_snapshot.get("final") is not True
        or selection_snapshot.get("selected_algorithm") != selected
        or activation.get("selection_snapshot_sha256")
        != canonical_hash(selection_snapshot)
        or selected not in ALGORITHMS
        or allowed != list(ALGORITHMS)
        or activation.get("input_manifest_sha256", {}).get("adapter_design")
        != design["manifest_sha256"]
        or inputs.get("execution_admitted") is not False
        or not isinstance(tasks, list)
        or len(tasks) != 96
        or int(counts.get("attack_families", -1)) != 32
        or int(counts.get("datasets", -1)) != 2
        or int(counts.get("training_seeds", -1)) != 3
    ):
        raise ValueError("selected-system external activation/input mismatch")
    identities = [task_identity(task) for task in tasks]
    if len(identities) != len(set(identities)):
        raise ValueError("external malicious task identities are not unique")
    counts_at_freeze = output_counts(run_root)
    if any(counts_at_freeze.values()):
        raise ValueError("external protocol requires a zero-result run root")
    implementation = {}
    for relative in IMPLEMENTATION_FILES:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing implementation: {relative}")
        implementation[relative] = file_hash(path)

    comparators = (
        ["opendetect"]
        if selected == "caeos_pairwise"
        else ["embedded_pairwise", "opendetect"]
    )
    value: dict[str, Any] = {
        "schema_version": PROTOCOL_SCHEMA,
        "state": "admitted_after_final_selection_before_external_results",
        "execution_admitted": True,
        "selected_algorithm": selected,
        "runtime_contract_schema": "strict_v4_selected_system_runtime_v1",
        "backend": {
            "caeos_pairwise": "pairwise_family_capture",
            "caeos_pug": "pairwise_family_capture",
            "krc_csr_caeos_v1": "krc_known_only_seed_capture",
            "rrc_csr_caeos_v1": (
                "rrc_three_seed_known_only_scenario_certificate"
            ),
        }[selected],
        "comparators": comparators,
        "tasks": tasks,
        "task_counts": counts,
        "dataset_registry": inputs["dataset_registry"],
        "pairwise_runtime_policy": pairwise_policy(selected),
        "robust_runtime_policy": {
            "augmentation_weight": 0.5,
            "training_sample_fraction": 0.25,
            "health_quantile": 0.99,
            "unknown_or_test_labels_used_for_certificate": False,
        },
        "opendetect_policy": opendetect_policy(),
        "rrc_backend_protocol": (
            rrc_protocol(tasks)
            if selected == "rrc_csr_caeos_v1"
            else None
        ),
        "statistics": {
            "bootstrap_unit": (
                "attack_family_after_averaging_three_training_seeds"
            ),
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260727,
            "wilcoxon_alternative": "greater",
            "multiple_testing": "holm_across_four_unknown_metrics",
            "comparators_evaluated_independently_without_splicing": True,
        },
        "confirmation_gate": {
            "against_each_comparator": inputs["confirmation_gate"],
            "all_required_comparators_must_pass": True,
            "coverage_complete_and_failure_count_zero": True,
            "unknown_or_test_labels_excluded_from_fit_selection_threshold_"
            "and_routing": True,
        },
        "expected_outputs": {
            "candidate_capture_count": 96,
            "candidate_metric_count": 96,
            "opendetect_metric_count": 96,
            "candidate_report_count": 96,
            "embedded_pairwise_report_count": (
                0 if selected == "caeos_pairwise" else 96
            ),
            "opendetect_report_count": 96,
            "summary_count": 1,
            "audit_count": 1,
        },
        "resource_contract": {
            "requires_self_algorithm_confirmation_idle": True,
            "candidate_capture_outer_workers": 4,
            "candidate_fit_jobs_per_worker": 8,
            "opendetect_gpu_workers": 1,
            "capture_phase_precedes_opendetect_phase": True,
            "nice": 19,
            "ionice": "idle",
        },
        "run_root": run_root.resolve().as_posix(),
        "output_counts_at_freeze": counts_at_freeze,
        "input_manifest_sha256": {
            "activation": activation["manifest_sha256"],
            "adapter_design": design["manifest_sha256"],
            "external_input_protocol": inputs["manifest_sha256"],
        },
        "input_file_sha256": {
            "activation": file_hash(activation_path),
            "adapter_design": file_hash(adapter_design_path),
            "external_input_protocol": file_hash(input_protocol_path),
        },
        "implementation_sha256": dict(sorted(implementation.items())),
        "claim_boundary": {
            "external_success_is_required_but_not_sufficient_for_sota": True,
            "pairwise_selected_system_is_not_compared_against_itself": True,
            "candidate_is_retrained_for_every_external_split": True,
            "algorithm_directory_renaming_or_result_splicing_forbidden": True,
            "parrot_benign_safety_and_efficiency_are_separate": True,
            "integrity_pass_is_separate_from_effect_pass": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def verify_protocol(
    protocol: dict[str, Any],
    project_root: Path,
    run_root: Path,
    workers: int,
) -> None:
    require_canonical(protocol, PROTOCOL_SCHEMA, "external protocol")
    selected = protocol.get("selected_algorithm")
    maximum = int(
        protocol.get("resource_contract", {}).get(
            "candidate_capture_outer_workers", 0
        )
    )
    if (
        protocol.get("execution_admitted") is not True
        or selected not in ALGORITHMS
        or run_root.resolve().as_posix() != protocol.get("run_root")
        or not 1 <= int(workers) <= maximum
        or len(protocol.get("tasks", [])) != 96
    ):
        raise ValueError("invalid admitted selected-system external protocol")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    blocks = [task_block(run_root, task) for task in protocol["tasks"]]
    if len(blocks) != len(set(blocks)):
        raise ValueError("external task paths collide")


def verify_task_inputs(task: dict[str, Any]) -> None:
    if (
        file_hash(Path(task["csv"])) != task["csv_sha256"]
        or file_hash(Path(task["sidecar"]))
        != task["sidecar_file_sha256"]
        or file_hash(Path(task["config"])) != task["config_sha256"]
        or int(task["prepared_seed"]) != int(task["training_seed"])
        or int(task["split_seed"]) != int(task["training_seed"])
        or int(task["opendetect_seed"]) != int(task["training_seed"])
    ):
        raise ValueError("external task input or seed contract drift")


def base_arguments(
    task: dict[str, Any],
    policy: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    return [
        "--csv",
        task["csv"],
        "--config",
        task["config"],
        "--unknown-classes",
        task["unknown_attack_family"],
        "--benign-class",
        task["benign_label"],
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        "4000",
        "--estimators",
        str(policy["estimators"]),
        "--jobs",
        str(policy["jobs"]),
        "--known-acceptance",
        str(policy["known_acceptance"]),
        "--risk-selection",
        str(policy["risk_selection"]),
        "--pseudo-unknown-max-alpha",
        str(policy["pseudo_unknown_max_alpha"]),
        "--pseudo-unknown-min-fold-gain",
        str(policy["pseudo_unknown_min_fold_gain"]),
        "--boundary-hard-pseudo-fraction",
        str(policy["boundary_hard_pseudo_fraction"]),
        "--boundary-interpolation",
        str(policy["boundary_interpolation"]),
        "--boundary-max-per-task",
        str(policy["boundary_max_per_task"]),
        "--boundary-training-objective",
        str(policy["boundary_training_objective"]),
        "--risk-policy-name",
        str(policy["risk_policy_name"]),
        "--seed",
        str(task["training_seed"]),
        "--output-dir",
        str(output_dir),
    ]


def pairwise_capture_command(
    *,
    python: str,
    project_root: Path,
    block: Path,
    task: dict[str, Any],
    protocol: dict[str, Any],
) -> list[str]:
    return [
        python,
        str(project_root / "capture_pairwise_runtime.py"),
        "--trainer",
        str(project_root / "train_hybrid_open_set.py"),
        "--capture-dir",
        str(block / "candidate_capture"),
        "--",
        *base_arguments(
            task,
            protocol["pairwise_runtime_policy"],
            block / "source_train",
        ),
    ]


def robust_capture_command(
    *,
    python: str,
    project_root: Path,
    block: Path,
    task: dict[str, Any],
    protocol: dict[str, Any],
) -> list[str]:
    selected = protocol["selected_algorithm"]
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
    robust = protocol["robust_runtime_policy"]
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
        task["dataset"],
        "--scenario",
        task["unknown_attack_family"],
        "--weight",
        str(robust["augmentation_weight"]),
        "--sample-fraction",
        str(robust["training_sample_fraction"]),
        "--training-seed",
        str(task["training_seed"]),
        "--augmentation-seed",
        str(task["augmentation_seed"]),
        "--health-quantile",
        str(robust["health_quantile"]),
        "--validation-corruption-seed",
        str(task["validation_profile_seed"]),
        "--",
        *base_arguments(
            task,
            protocol["pairwise_runtime_policy"],
            capture_dir / "ignored_by_robust_capture",
        ),
    ]


def opendetect_command(
    *,
    python: str,
    project_root: Path,
    output: Path,
    task: dict[str, Any],
    policy: dict[str, Any],
) -> list[str]:
    return [
        python,
        str(project_root / "train_neural_open_set.py"),
        "--dataset",
        "tabular",
        "--csv",
        task["csv"],
        "--config",
        task["config"],
        "--unknown-classes",
        task["unknown_attack_family"],
        "--benign-class",
        task["benign_label"],
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        "4000",
        "--model",
        "opendetect",
        "--epochs",
        str(policy["epochs"]),
        "--patience",
        str(policy["patience"]),
        "--hidden-dim",
        str(policy["hidden_dim"]),
        "--embedding-dim",
        str(policy["embedding_dim"]),
        "--known-acceptance",
        str(policy["known_acceptance"]),
        "--seed",
        str(task["opendetect_seed"]),
        "--device",
        "auto",
        "--output-dir",
        str(output),
    ]


def run_command(
    command: list[str],
    directory: Path,
    resource_prefix: list[str],
) -> float:
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / "execution.log"
    started = time.perf_counter()
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"command": command}) + "\n")
        handle.flush()
        completed = subprocess.run(
            [*resource_prefix, *command],
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        failure = {
            "schema_version": (
                "strict_v4_selected_system_external_execution_failure_v1"
            ),
            "returncode": int(completed.returncode),
            "command": command,
            "log_sha256": file_hash(log),
            "wall_seconds": float(elapsed),
        }
        write_json(directory / "failure.json", failure)
        raise RuntimeError(f"external command failed: {directory}")
    return float(elapsed)


def capture_directory(
    block: Path, selected_algorithm: str
) -> Path:
    return (
        block / "source_csr_capture"
        if selected_algorithm == "rrc_csr_caeos_v1"
        else block / "candidate_capture"
    )


def validate_source_capture(
    block: Path,
    task: dict[str, Any],
    protocol: dict[str, Any],
) -> bool:
    selected = protocol["selected_algorithm"]
    capture_dir = capture_directory(block, selected)
    manifest_path = capture_dir / "capture_manifest.json"
    if not manifest_path.is_file():
        return False
    value = load(manifest_path)
    expected_schema = {
        "caeos_pairwise": "strict_v4_pairwise_runtime_capture_v1",
        "caeos_pug": "strict_v4_pairwise_runtime_capture_v1",
        "krc_csr_caeos_v1": "strict_v4_krc_csr_runtime_capture_v1",
        "rrc_csr_caeos_v1": "strict_v4_csr_caeos_runtime_capture_v1",
    }[selected]
    if value.get("schema_version") != expected_schema:
        raise ValueError(f"capture schema mismatch: {capture_dir}")
    if selected in ("caeos_pairwise", "caeos_pug"):
        artifact = capture_dir / value.get("deployment_artifact", "")
        inputs = capture_dir / value.get("benchmark_inputs", "")
        evidence = value.get("runtime_evidence", {})
        expected_arguments = base_arguments(
            task,
            protocol["pairwise_runtime_policy"],
            block / "source_train",
        )
        if (
            value.get("equivalence", {}).get("passes") is not True
            or value.get("benchmark_inputs_contain_labels") is not False
            or value.get("trainer_arguments") != expected_arguments
            or evidence.get("selected_risk")
            != protocol["pairwise_runtime_policy"][
                "expected_runtime_selected_risk"
            ]
            or evidence.get("contains_test_ground_truth") is not False
            or evidence.get("contains_training_or_test_labels") is not False
            or file_hash(artifact)
            != value.get("deployment_artifact_sha256")
            or file_hash(inputs) != value.get("benchmark_inputs_sha256")
        ):
            raise ValueError(f"invalid Pairwise-family capture: {capture_dir}")
        for path in (
            block / "source_train" / "metrics.json",
            block / "source_train" / "scores.npz",
        ):
            if not path.is_file():
                raise ValueError(f"missing Pairwise source output: {path}")
        return True

    expected_algorithm = (
        "krc_csr_caeos_v1"
        if selected == "krc_csr_caeos_v1"
        else "csr_caeos_v1"
    )
    artifact = capture_dir / value.get("runtime_artifact", "")
    inputs = capture_dir / value.get("evaluation_inputs", "")
    if (
        value.get("state") != "complete"
        or value.get("algorithm") != expected_algorithm
        or value.get("task")
        != {
            "suite": task["dataset"],
            "scenario": task["unknown_attack_family"],
        }
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or float(value.get("weight", -1.0))
        != float(
            protocol["robust_runtime_policy"]["augmentation_weight"]
        )
        or file_hash(artifact) != value.get("runtime_artifact_sha256")
        or file_hash(inputs) != value.get("evaluation_inputs_sha256")
        or value.get("roundtrip", {}).get("passes") is not True
        or value.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
        or (
            selected == "krc_csr_caeos_v1"
            and value.get("test_labels_read_for_certificate_or_roundtrip")
            is not False
        )
        or (
            selected == "rrc_csr_caeos_v1"
            and value.get("test_labels_read_for_roundtrip_or_selection")
            is not False
        )
    ):
        raise ValueError(f"invalid robust source capture: {capture_dir}")
    if selected == "krc_csr_caeos_v1":
        require_canonical(
            value,
            "strict_v4_krc_csr_runtime_capture_v1",
            "KRC external capture",
        )
    return True


def validate_candidate_capture(
    block: Path,
    task: dict[str, Any],
    protocol: dict[str, Any],
) -> None:
    selected = protocol["selected_algorithm"]
    if selected != "rrc_csr_caeos_v1":
        if not validate_source_capture(block, task, protocol):
            raise ValueError("selected runtime capture is absent")
        return
    backend = protocol.get("rrc_backend_protocol")
    capture_dir = block / "candidate_capture"
    manifest_path = capture_dir / "capture_manifest.json"
    if not isinstance(backend, dict) or not manifest_path.is_file():
        raise ValueError("RRC selected runtime capture is absent")
    value = load(manifest_path)
    require_canonical(
        value,
        "strict_v4_rrc_csr_runtime_capture_v1",
        "RRC selected runtime capture",
    )
    artifact = capture_dir / value.get("runtime_artifact", "")
    inputs = capture_dir / value.get("evaluation_inputs", "")
    if (
        value.get("state") != "complete"
        or value.get("algorithm") != selected
        or value.get("protocol_manifest_sha256")
        != backend.get("manifest_sha256")
        or value.get("task")
        != {
            "suite": task["dataset"],
            "scenario": task["unknown_attack_family"],
        }
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or int(value.get("corruption_seed", -1))
        != int(task["validation_profile_seed"])
        or value.get("roundtrip", {}).get("passes") is not True
        or file_hash(artifact) != value.get("runtime_artifact_sha256")
        or file_hash(inputs) != value.get("evaluation_inputs_sha256")
        or value.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
        or value.get("test_labels_read_for_materialization_or_roundtrip")
        is not False
    ):
        raise ValueError("RRC selected runtime capture identity drifted")


def execute_capture_task(
    *,
    python: str,
    project_root: Path,
    protocol: dict[str, Any],
    run_root: Path,
    task: dict[str, Any],
    resource_prefix: list[str],
) -> str:
    verify_task_inputs(task)
    block = task_block(run_root, task)
    selected = protocol["selected_algorithm"]
    capture_dir = capture_directory(block, selected)
    if not validate_source_capture(block, task, protocol):
        if capture_dir.exists() and any(capture_dir.iterdir()):
            raise ValueError(
                f"partial capture requires quarantine: {capture_dir}"
            )
        command = (
            pairwise_capture_command(
                python=python,
                project_root=project_root,
                block=block,
                task=task,
                protocol=protocol,
            )
            if selected in ("caeos_pairwise", "caeos_pug")
            else robust_capture_command(
                python=python,
                project_root=project_root,
                block=block,
                task=task,
                protocol=protocol,
            )
        )
        run_command(command, capture_dir, resource_prefix)
        if not validate_source_capture(block, task, protocol):
            raise ValueError("capture missing after successful command")
    return "/".join(map(str, task_identity(task)))


def materialize_rrc_tasks(
    protocol: dict[str, Any], run_root: Path
) -> None:
    backend = protocol.get("rrc_backend_protocol")
    if not isinstance(backend, dict):
        raise ValueError("RRC backend protocol is absent")
    require_canonical(
        backend,
        "strict_v4_rrc_csr_execution_protocol_v1",
        "RRC backend protocol",
    )
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for task in protocol["tasks"]:
        grouped.setdefault(
            (task["dataset"], task["unknown_attack_family"]), []
        ).append(task)
    for (dataset, scenario), tasks in sorted(grouped.items()):
        if len(tasks) != 3:
            raise ValueError("RRC requires three tasks per attack family")
        records = [
            seed_record_from_capture(
                task_block(run_root, task) / "source_csr_capture",
                suite=dataset,
                scenario=scenario,
                training_seed=int(task["training_seed"]),
            )
            for task in tasks
        ]
        certificate = certify_seed_records(
            records,
            protocol_manifest_sha256=backend["manifest_sha256"],
            suite=dataset,
            scenario=scenario,
            expected_training_seeds=[
                int(task["training_seed"]) for task in tasks
            ],
        )
        certificate_path = (
            run_root
            / "_rrc_certificates"
            / dataset
            / f"{slug(scenario)}.json"
        )
        if certificate_path.is_file():
            if load(certificate_path) != certificate:
                raise ValueError("existing RRC certificate is immutable")
        else:
            write_json(certificate_path, certificate)
        for task in tasks:
            block = task_block(run_root, task)
            output = block / "candidate_capture"
            manifest_path = output / "capture_manifest.json"
            if manifest_path.is_file():
                validate_candidate_capture(block, task, protocol)
                if load(manifest_path).get(
                    "scenario_certificate_manifest_sha256"
                ) != certificate["manifest_sha256"]:
                    raise ValueError("existing RRC materialization drifted")
                continue
            if output.exists() and any(output.iterdir()):
                raise ValueError(
                    f"partial RRC materialization requires quarantine: {output}"
                )
            materialize(
                backend,
                certificate,
                block / "source_csr_capture",
                output,
                suite=dataset,
                scenario=scenario,
                training_seed=int(task["training_seed"]),
                corruption_seed=int(task["validation_profile_seed"]),
            )
            validate_candidate_capture(block, task, protocol)


def runtime_bundle(
    block: Path,
    selected_algorithm: str,
) -> tuple[Any, list[np.ndarray], np.ndarray, np.ndarray, float, dict[str, Any]]:
    capture_dir = block / "candidate_capture"
    capture = load(capture_dir / "capture_manifest.json")
    if selected_algorithm in ("caeos_pairwise", "caeos_pug"):
        runtime = joblib.load(capture_dir / capture["deployment_artifact"])
        with np.load(
            capture_dir / capture["benchmark_inputs"], allow_pickle=False
        ) as archive:
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
            pairwise_prediction = np.asarray(
                scores["test_prediction"], dtype=np.int64
            )
            pairwise_risk = np.asarray(
                scores[f"test_{PAIRWISE_RISK}"], dtype=np.float64
            )
        selected_risk = runtime.evidence()["selected_risk"]
        threshold = float(metrics["validation_thresholds"][selected_risk])
        comparator_threshold = float(
            metrics["validation_thresholds"][PAIRWISE_RISK]
        )
        auxiliary = {
            "split_metadata": metrics["split_metadata"],
            "pairwise_prediction": pairwise_prediction,
            "pairwise_risk": pairwise_risk,
            "pairwise_threshold": comparator_threshold,
            "capture_manifest_file_sha256": file_hash(
                capture_dir / "capture_manifest.json"
            ),
            "runtime_artifact_sha256": capture[
                "deployment_artifact_sha256"
            ],
            "evaluation_inputs_sha256": capture["benchmark_inputs_sha256"],
            "source_metrics_sha256": file_hash(
                block / "source_train" / "metrics.json"
            ),
            "source_scores_sha256": file_hash(
                block / "source_train" / "scores.npz"
            ),
        }
        return runtime, views, labels, unknown, threshold, auxiliary

    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    runtime = joblib.load(artifact)
    evidence = runtime.evidence()
    with np.load(inputs_path, allow_pickle=False) as archive:
        views = [
            np.asarray(archive[f"view_{index}"])
            for index in range(int(evidence["modality_count"]))
        ]
        labels = np.asarray(archive["test_labels"], dtype=np.int64)
        unknown = np.asarray(archive["test_unknown"], dtype=bool)
    source = (
        capture_dir
        if selected_algorithm == "krc_csr_caeos_v1"
        else block / "source_csr_capture"
    )
    metrics = load(source / "robust_run" / "metrics.json")
    auxiliary = {
        "split_metadata": metrics["split_metadata"],
        "capture_manifest_file_sha256": file_hash(
            capture_dir / "capture_manifest.json"
        ),
        "runtime_artifact_sha256": capture["runtime_artifact_sha256"],
        "evaluation_inputs_sha256": capture["evaluation_inputs_sha256"],
        "source_metrics_sha256": file_hash(
            source / "robust_run" / "metrics.json"
        ),
    }
    return (
        runtime,
        views,
        labels,
        unknown,
        float(runtime.clean_threshold),
        auxiliary,
    )


def evaluate_candidate(
    *,
    protocol: dict[str, Any],
    run_root: Path,
    task: dict[str, Any],
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "external protocol")
    expected = {
        task_identity(record): record for record in protocol["tasks"]
    }
    if expected.get(task_identity(task)) != task:
        raise ValueError("external task is outside the frozen protocol")
    selected = protocol["selected_algorithm"]
    block = task_block(run_root, task)
    validate_candidate_capture(block, task, protocol)
    runtime, views, labels, unknown, threshold, auxiliary = runtime_bundle(
        block, selected
    )
    adapter = SelectedSystemRuntime(runtime, selected, threshold)
    inference = adapter.predict(views)
    reports = {
        "candidate": report(
            labels,
            unknown,
            inference["prediction"],
            inference["risk"],
            threshold,
        )
    }
    routing: dict[str, Any] = {
        "unknown_or_test_labels_used": False,
    }
    if selected == "caeos_pug":
        reports["embedded_pairwise"] = report(
            labels,
            unknown,
            auxiliary["pairwise_prediction"],
            auxiliary["pairwise_risk"],
            auxiliary["pairwise_threshold"],
        )
        routing.update(
            {
                "prediction_exactly_pairwise_all_rows": bool(
                    np.array_equal(
                        inference["prediction"],
                        auxiliary["pairwise_prediction"],
                    )
                ),
                "probability_source_exactly_pairwise": True,
            }
        )
    elif selected in ("krc_csr_caeos_v1", "rrc_csr_caeos_v1"):
        raw = runtime.predict(views)
        clean_probability = np.asarray(raw["clean_probability"])
        clean_prediction = clean_probability.argmax(axis=1)
        clean_risk = np.asarray(raw["clean_risk"])
        active = np.asarray(raw["active"], dtype=bool)
        reports["embedded_pairwise"] = report(
            labels,
            unknown,
            clean_prediction,
            clean_risk,
            threshold,
        )
        routing.update(
            {
                "active_count": int(active.sum()),
                "active_rate": float(active.mean()),
                "prediction_exactly_pairwise_all_rows": bool(
                    np.array_equal(inference["prediction"], clean_prediction)
                ),
                "probability_exactly_pairwise_all_rows": bool(
                    np.array_equal(
                        inference["probability"], clean_probability
                    )
                ),
                "risk_monotone_not_below_pairwise": bool(
                    np.all(inference["risk"] >= clean_risk - 1e-12)
                ),
                "inactive_risk_exactly_pairwise": bool(
                    np.array_equal(
                        inference["risk"][~active], clean_risk[~active]
                    )
                ),
            }
        )
        required = (
            "prediction_exactly_pairwise_all_rows",
            "probability_exactly_pairwise_all_rows",
            "risk_monotone_not_below_pairwise",
            "inactive_risk_exactly_pairwise",
        )
        if not all(routing[name] for name in required):
            raise ValueError("robust selected runtime routing contract failed")

    split = auxiliary["split_metadata"]
    if (
        not isinstance(split, dict)
        or any(
            int(value) != 0
            for value in split.get("fingerprint_overlap", {}).values()
        )
        or split.get("cross_label_fingerprint_filter", {}).get(
            "unknown_labels_used"
        )
        is not False
    ):
        raise ValueError("external split integrity failed")
    value: dict[str, Any] = {
        "schema_version": METRICS_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": selected,
        "dataset": task["dataset"],
        "unknown_attack_family": task["unknown_attack_family"],
        "training_seed": int(task["training_seed"]),
        "split_metadata": split,
        "capture": {
            "manifest_file_sha256": auxiliary[
                "capture_manifest_file_sha256"
            ],
            "runtime_artifact_sha256": auxiliary[
                "runtime_artifact_sha256"
            ],
            "evaluation_inputs_sha256": auxiliary[
                "evaluation_inputs_sha256"
            ],
            "source_metrics_sha256": auxiliary["source_metrics_sha256"],
            "source_scores_sha256": auxiliary.get(
                "source_scores_sha256"
            ),
        },
        "runtime_evidence": adapter.evidence(),
        "reports": reports,
        "routing": routing,
        "diagnostics": {
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing": False,
            "test_labels_used_for_final_metrics_only": True,
            "external_parameters_reselected": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    output = block / "candidate" / "metrics.json"
    write_json(output, value)
    write_provenance(
        output=output.parent,
        protocol=protocol,
        task=task,
        method=selected,
        command=["in_process_selected_system_runtime_evaluation"],
    )
    return value


def write_provenance(
    *,
    output: Path,
    protocol: dict[str, Any],
    task: dict[str, Any],
    method: str,
    command: list[str],
) -> None:
    metrics = output / "metrics.json"
    value: dict[str, Any] = {
        "schema_version": PROVENANCE_SCHEMA,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        "dataset": task["dataset"],
        "unknown_attack_family": task["unknown_attack_family"],
        "training_seed": int(task["training_seed"]),
        "method": method,
        "csv_sha256": task["csv_sha256"],
        "sidecar_file_sha256": task["sidecar_file_sha256"],
        "config_sha256": task["config_sha256"],
        "metrics_sha256": file_hash(metrics),
        "command": command,
        "unknown_or_test_metrics_used_for_configuration": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    write_json(output / "provenance.json", value)


def validate_bound_metrics(
    output: Path,
    protocol: dict[str, Any],
    task: dict[str, Any],
    method: str,
) -> bool:
    metrics_path = output / "metrics.json"
    provenance_path = output / "provenance.json"
    if not metrics_path.is_file() and not provenance_path.is_file():
        return False
    if not metrics_path.is_file() or not provenance_path.is_file():
        raise ValueError(f"partial external metrics: {output}")
    provenance = load(provenance_path)
    require_canonical(provenance, PROVENANCE_SCHEMA, "provenance")
    if (
        provenance.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or provenance.get("selected_algorithm")
        != protocol["selected_algorithm"]
        or provenance.get("metrics_sha256") != file_hash(metrics_path)
        or provenance.get("method") != method
        or task_identity(provenance) != task_identity(task)
        or provenance.get("csv_sha256") != task["csv_sha256"]
        or provenance.get("sidecar_file_sha256")
        != task["sidecar_file_sha256"]
        or provenance.get("config_sha256") != task["config_sha256"]
        or provenance.get(
            "unknown_or_test_metrics_used_for_configuration"
        )
        is not False
    ):
        raise ValueError(f"external provenance mismatch: {output}")
    return True


def execute_candidate_evaluation(
    protocol: dict[str, Any],
    run_root: Path,
    task: dict[str, Any],
) -> str:
    output = task_block(run_root, task) / "candidate"
    if not validate_bound_metrics(
        output, protocol, task, protocol["selected_algorithm"]
    ):
        if output.exists() and any(output.iterdir()):
            raise ValueError(
                f"partial candidate metrics require quarantine: {output}"
            )
        evaluate_candidate(protocol=protocol, run_root=run_root, task=task)
        validate_bound_metrics(
            output, protocol, task, protocol["selected_algorithm"]
        )
    return "/".join(map(str, task_identity(task)))


def execute_opendetect(
    *,
    python: str,
    project_root: Path,
    protocol: dict[str, Any],
    run_root: Path,
    task: dict[str, Any],
    resource_prefix: list[str],
) -> str:
    verify_task_inputs(task)
    output = task_block(run_root, task) / "opendetect"
    if not validate_bound_metrics(
        output, protocol, task, "opendetect"
    ):
        if output.exists() and any(output.iterdir()):
            raise ValueError(
                f"partial OpenDetect metrics require quarantine: {output}"
            )
        command = opendetect_command(
            python=python,
            project_root=project_root,
            output=output,
            task=task,
            policy=protocol["opendetect_policy"],
        )
        run_command(command, output, resource_prefix)
        write_provenance(
            output=output,
            protocol=protocol,
            task=task,
            method="opendetect",
            command=command,
        )
        validate_bound_metrics(output, protocol, task, "opendetect")
    return "/".join(map(str, task_identity(task)))


def candidate_metric_report(
    metrics: dict[str, Any], name: str
) -> dict[str, float]:
    require_canonical(metrics, METRICS_SCHEMA, "candidate metrics")
    diagnostics = metrics.get("diagnostics", {})
    if (
        metrics.get("state") != "complete"
        or diagnostics.get(
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing"
        )
        is not False
        or diagnostics.get("test_labels_used_for_final_metrics_only")
        is not True
        or diagnostics.get("external_parameters_reselected") is not False
    ):
        raise ValueError("candidate metrics leakage gate failed")
    value = metrics.get("reports", {}).get(name)
    if not isinstance(value, dict):
        raise ValueError(f"candidate report is absent: {name}")
    names = (
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
        "known_macro_f1",
    )
    return {metric: float(value[metric]) for metric in names}


def summarize(
    protocol: dict[str, Any], run_root: Path
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "external protocol")
    comparators = list(protocol["comparators"])
    records: dict[str, list[dict[str, Any]]] = {
        name: [] for name in comparators
    }
    metric_files = []
    for task in protocol["tasks"]:
        block = task_block(run_root, task)
        candidate_path = block / "candidate"
        opendetect_path = block / "opendetect"
        if not validate_bound_metrics(
            candidate_path,
            protocol,
            task,
            protocol["selected_algorithm"],
        ) or not validate_bound_metrics(
            opendetect_path, protocol, task, "opendetect"
        ):
            raise ValueError(f"external metrics coverage is incomplete: {block}")
        candidate_metrics = load(candidate_path / "metrics.json")
        opendetect_metrics = load(opendetect_path / "metrics.json")
        if (
            not split_integrity(candidate_metrics)
            or not split_integrity(opendetect_metrics)
            or candidate_metrics["split_metadata"]["split_fingerprint"]
            != opendetect_metrics["split_metadata"]["split_fingerprint"]
        ):
            raise ValueError(f"external split binding failed: {block}")
        candidate = candidate_metric_report(
            candidate_metrics, "candidate"
        )
        base = {
            "dataset": task["dataset"],
            "unknown_attack_family": task["unknown_attack_family"],
            "seed": int(task["training_seed"]),
            "candidate": candidate,
        }
        if "embedded_pairwise" in comparators:
            records["embedded_pairwise"].append(
                {
                    **base,
                    "comparator": candidate_metric_report(
                        candidate_metrics, "embedded_pairwise"
                    ),
                }
            )
        records["opendetect"].append(
            {
                **base,
                "comparator": metric_report(
                    opendetect_metrics, "opendetect"
                ),
            }
        )
        metric_files.extend(
            [
                candidate_path / "metrics.json",
                opendetect_path / "metrics.json",
            ]
        )
    statistics = protocol["statistics"]
    repetitions = int(statistics["bootstrap_repetitions"])
    seed = int(statistics["bootstrap_seed"])
    aggregations = {
        name: aggregate(
            rows,
            repetitions=repetitions,
            bootstrap_seed=seed + 1000 * index,
        )
        for index, (name, rows) in enumerate(records.items())
    }
    gates = protocol["confirmation_gate"]["against_each_comparator"]
    checks = {
        name: comparator_checks(value, gates)
        for name, value in aggregations.items()
    }
    expected = int(
        protocol["task_counts"]["total_scenarios_per_algorithm"]
    )
    failures = list(run_root.rglob("failure.json"))
    coverage = {
        "coverage_complete_and_failure_count_zero": bool(
            all(len(rows) == expected for rows in records.values())
            and len(metric_files) == 2 * expected
            and not failures
        ),
        "all_metric_files_remain_hash_bound": all(
            path.is_file() for path in metric_files
        ),
        "unknown_or_test_labels_excluded_from_fit_selection_threshold_"
        "and_routing": True,
        "all_required_comparators_pass_without_splicing": all(
            all(value.values()) for value in checks.values()
        ),
    }
    effect_passes = bool(
        coverage["coverage_complete_and_failure_count_zero"]
        and coverage[
            "unknown_or_test_labels_excluded_from_fit_selection_threshold_"
            "and_routing"
        ]
        and coverage["all_required_comparators_pass_without_splicing"]
    )
    integrity_passes = bool(
        coverage["coverage_complete_and_failure_count_zero"]
        and coverage["all_metric_files_remain_hash_bound"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_selected_system_external_malicious_summary_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        "comparators": comparators,
        "scenario_count": expected,
        "failure_count": len(failures),
        "metric_file_sha256": {
            path.relative_to(run_root).as_posix(): file_hash(path)
            for path in sorted(metric_files)
        },
        "aggregations": aggregations,
        "checks_by_comparator": checks,
        "validation": {
            "checks": coverage,
            "integrity_passes": integrity_passes,
            "effect_passes": effect_passes,
        },
        "external_malicious_confirmation_passes": effect_passes,
        "claim_boundary": {
            **protocol["claim_boundary"],
            "summary_integrity_does_not_override_failed_effect_gate": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def audit_summary(
    protocol: dict[str, Any],
    summary: dict[str, Any],
    run_root: Path,
) -> dict[str, Any]:
    require_canonical(
        summary,
        "strict_v4_selected_system_external_malicious_summary_v1",
        "external summary",
    )
    recomputed = summarize(protocol, run_root)
    summary_matches = summary == recomputed
    integrity = bool(
        summary_matches
        and summary.get("validation", {}).get("integrity_passes") is True
    )
    effect = bool(
        integrity
        and summary.get("validation", {}).get("effect_passes") is True
    )
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_selected_system_external_malicious_audit_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        "summary_recomputation_matches": summary_matches,
        "integrity_passes": integrity,
        "effect_passes": effect,
        "comprehensive_sota_authorized": False,
        "claim_boundary": {
            "external_effect_is_only_one_required_comprehensive_gate": True,
            "parrot_benign_safety_efficiency_and_integrated_audit_pending": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def execute(
    *,
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    python: str,
    workers: int,
    resource_prefix: list[str],
) -> None:
    protocol = load(protocol_path)
    verify_protocol(protocol, project_root, run_root, workers)
    tasks = protocol["tasks"]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                execute_capture_task,
                python=python,
                project_root=project_root,
                protocol=protocol,
                run_root=run_root,
                task=task,
                resource_prefix=resource_prefix,
            )
            for task in tasks
        ]
        for index, future in enumerate(as_completed(futures), start=1):
            print(
                f"capture {index}/{len(futures)} {future.result()}",
                flush=True,
            )
    if protocol["selected_algorithm"] == "rrc_csr_caeos_v1":
        materialize_rrc_tasks(protocol, run_root)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                execute_candidate_evaluation, protocol, run_root, task
            )
            for task in tasks
        ]
        for index, future in enumerate(as_completed(futures), start=1):
            print(
                f"candidate {index}/{len(futures)} {future.result()}",
                flush=True,
            )
    for index, task in enumerate(tasks, start=1):
        value = execute_opendetect(
            python=python,
            project_root=project_root,
            protocol=protocol,
            run_root=run_root,
            task=task,
            resource_prefix=resource_prefix,
        )
        print(f"opendetect {index}/{len(tasks)} {value}", flush=True)

    summary = summarize(protocol, run_root)
    write_json(run_root / "summary.json", summary)
    audit = audit_summary(protocol, summary, run_root)
    write_json(run_root / "audit.json", audit)
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_selected_system_external_execution_complete_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "audit_manifest_sha256": audit["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        "task_count": len(tasks),
        "integrity_passes": audit["integrity_passes"],
        "effect_passes": audit["effect_passes"],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    write_json(run_root / "execution_complete.json", completion)


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("prepare", "run"), default="prepare")
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
        "--input-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_krc_external_malicious_input_protocol_v2/"
            "protocol.json"
        ),
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_v1/"
            "external_malicious_protocol.json"
        ),
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_external_malicious_v1"
        ),
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--capture-workers", type=int, default=4)
    parser.add_argument(
        "--resource-prefix",
        nargs="*",
        default=["ionice", "-c3", "nice", "-n19"],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    activation = resolve(root, args.activation)
    design = resolve(root, args.adapter_design)
    inputs = resolve(root, args.input_protocol)
    protocol_path = resolve(root, args.protocol)
    run_root = resolve(root, args.run_root)
    if args.mode == "prepare":
        if not activation.is_file():
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
        value = create_protocol(
            project_root=root,
            run_root=run_root,
            activation_path=activation,
            adapter_design_path=design,
            input_protocol_path=inputs,
        )
        if protocol_path.is_file():
            existing = load(protocol_path)
            if existing != value:
                raise ValueError("existing external protocol is immutable")
        else:
            write_json(protocol_path, value)
        print(
            json.dumps(
                {
                    "state": value["state"],
                    "selected_algorithm": value["selected_algorithm"],
                    "manifest_sha256": value["manifest_sha256"],
                    "file_sha256": file_hash(protocol_path),
                },
                sort_keys=True,
            )
        )
        return
    if not protocol_path.is_file():
        raise FileNotFoundError("selected-system external protocol is absent")
    execute(
        protocol_path=protocol_path,
        project_root=root,
        run_root=run_root,
        python=args.python,
        workers=int(args.capture_workers),
        resource_prefix=list(args.resource_prefix),
    )


if __name__ == "__main__":
    main()
