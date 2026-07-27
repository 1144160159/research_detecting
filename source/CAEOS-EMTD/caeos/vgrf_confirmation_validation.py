from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _replace_value(command: list[str], flag: str, value: str) -> None:
    index = command.index(flag)
    command[index + 1] = value


def validate_reference_result(
    reference: Path,
    record: dict,
    protocol: dict,
    project_root: Path,
) -> None:
    required = (
        "metrics.json",
        "provenance.json",
        "evidence_package.npz",
        "scores.npz",
    )
    if any(not (reference / name).is_file() for name in required):
        raise ValueError("reference result is incomplete")
    source_path = project_root / record["source_provenance"]
    if file_sha(source_path) != record["source_provenance_sha256"]:
        raise ValueError("reference source provenance SHA mismatch")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    provenance = json.loads(
        (reference / "provenance.json").read_text(encoding="utf-8")
    )
    expected_task = {
        "suite": record["suite"],
        "scenario": record["scenario"],
        "unknown_classes": record["unknown_classes"],
        "seed": record["training_seed"],
    }
    if provenance.get("schema_version") != 1:
        raise ValueError("reference provenance schema mismatch")
    if provenance.get("task") != expected_task:
        raise ValueError("reference task identity mismatch")
    expected_command = list(source["command"][1:])
    _replace_value(
        expected_command, "--seed", str(record["training_seed"])
    )
    _replace_value(
        expected_command, "--output-dir", str(reference.resolve())
    )
    _replace_value(
        expected_command,
        "--risk-policy-name",
        "strict_v4_vgrf_confirmation_reference_v1",
    )
    observed_command = provenance.get("command")
    if (
        not isinstance(observed_command, list)
        or observed_command[1:] != expected_command
    ):
        raise ValueError("reference training command mismatch")
    if (
        file_sha(Path(record["csv"])) != record["csv_sha256"]
        or file_sha(project_root / record["config"])
        != record["config_sha256"]
    ):
        raise ValueError("reference source input SHA mismatch")
    inputs = provenance.get("inputs", {})
    if (
        inputs.get("csv", {}).get("path") != record["csv"]
        or inputs.get("config", {}).get("sha256")
        != record["config_sha256"]
    ):
        raise ValueError("reference provenance input mismatch")
    trainer_sha = protocol["implementation_sha256"][
        "train_hybrid_open_set.py"
    ]
    code_files = provenance.get("code", {}).get("files", {})
    observed_trainer_shas = [
        value
        for name, value in code_files.items()
        if Path(name).name == "train_hybrid_open_set.py"
    ]
    if observed_trainer_shas != [trainer_sha]:
        raise ValueError("reference trainer implementation mismatch")


def validate_candidate_result(
    payload: dict,
    record: dict,
    protocol: dict,
    reference: Path,
) -> None:
    if payload.get("schema_version") != (
        "strict_v4_validation_gated_reliability_fusion_metrics_v1"
    ):
        raise ValueError("candidate result schema mismatch")
    expected_identity = {
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": record["training_seed"],
    }
    for key, expected in expected_identity.items():
        if payload.get(key) != expected:
            raise ValueError(f"candidate result {key} mismatch")
    parameter_map = {
        "shrinkage": "empirical_bayes_shrinkage",
        "minimum_reliability": "minimum_reliability",
        "risk_blend": "risk_blend",
        "known_rejection_quantile": "known_rejection_quantile",
        "minimum_f1_gain": "minimum_f1_gain",
        "maximum_correct_risk_increase": "maximum_correct_risk_increase",
        "minimum_auc_gain": "minimum_auc_gain",
        "minimum_separation_gain": "minimum_separation_gain",
        "minimum_strict_proxy_gain": "minimum_strict_proxy_gain",
    }
    parameters = payload.get("parameters", {})
    frozen = protocol["known_only_parameters"]
    for observed_name, frozen_name in parameter_map.items():
        if parameters.get(observed_name) != frozen[frozen_name]:
            raise ValueError(
                f"candidate result parameter mismatch: {observed_name}"
            )
    inputs = payload.get("input_sha256", {})
    expected_inputs = {
        "evidence_package": file_sha(reference / "evidence_package.npz"),
        "scores": file_sha(reference / "scores.npz"),
    }
    if inputs != expected_inputs:
        raise ValueError("candidate result input SHA mismatch")
    diagnostics = payload.get("diagnostics", {})
    if type(diagnostics.get("enabled")) is not bool:
        raise ValueError("candidate enabled diagnostic is not boolean")
    if type(diagnostics.get("exact_fallback")) is not bool:
        raise ValueError("candidate fallback diagnostic is not boolean")
    if (
        diagnostics.get(
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
        )
        is not False
        or diagnostics.get("test_labels_used_for_final_metrics_only") is not True
    ):
        raise ValueError("candidate no-leak diagnostics failed")
    gate = payload.get("validation_gate", {})
    if gate.get("enabled") is not diagnostics["enabled"]:
        raise ValueError("candidate gate decision mismatch")
    if not diagnostics["enabled"] and not diagnostics["exact_fallback"]:
        raise ValueError("disabled candidate is not an exact fallback")
    finite_values = []
    for report_name in ("reference", "candidate"):
        report = payload.get("reports", {}).get(report_name, {})
        for metric in (
            "known_macro_f1",
            "unknown_auroc",
            "unknown_aupr",
            "unknown_fpr95",
            "oscr",
        ):
            finite_values.append(float(report[metric]))
    for name in ("reference", "candidate"):
        finite_values.append(float(payload.get("thresholds", {})[name]))
    if not np.isfinite(np.asarray(finite_values, dtype=np.float64)).all():
        raise ValueError("candidate result contains non-finite values")
