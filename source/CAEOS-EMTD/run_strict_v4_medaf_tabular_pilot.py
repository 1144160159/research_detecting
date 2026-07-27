from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_medaf_tabular_pilot_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
)


SCHEMA = "strict_v4_medaf_tabular_run_manifest_v1"
REPORT_KEYS = {
    "medaf_tabular_adapter": "medaf_tabular_adapter",
    "mlp_energy": "energy",
    "opendetect": "opendetect",
}
REQUIRED_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def replace_option(
    arguments: List[str], option: str, value: str
) -> List[str]:
    result = list(arguments)
    found = False
    for index, item in enumerate(result[:-1]):
        if item == option:
            result[index + 1] = value
            found = True
    if not found:
        result.extend([option, value])
    return result


def selection_is_clean(metrics: Dict[str, Any]) -> bool:
    evidence = metrics.get("selection_evidence", {})
    return (
        evidence.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False
        and evidence.get("test_labels_used_for_final_metrics_only") is True
    )


def score_diagnostics(path: Path) -> Dict[str, Any]:
    with np.load(path, allow_pickle=False) as values:
        validation_risk = np.asarray(
            values["validation_medaf_tabular"], dtype=np.float64
        )
        test_risk = np.asarray(
            values["test_medaf_tabular"], dtype=np.float64
        )
        validation_gate = np.asarray(
            values["validation_gate_weights"], dtype=np.float64
        )
        test_gate = np.asarray(
            values["test_gate_weights"], dtype=np.float64
        )
    gate = np.concatenate((validation_gate, test_gate), axis=0)
    risk = np.concatenate((validation_risk, test_risk), axis=0)
    finite = bool(np.isfinite(risk).all() and np.isfinite(gate).all())
    gate_simplex_error = float(
        np.max(np.abs(gate.sum(axis=1) - 1.0))
    )
    result = {
        "finite": finite,
        "risk_standard_deviation": float(np.std(risk)),
        "gate_max_branch_standard_deviation": float(
            np.max(np.std(gate, axis=0))
        ),
        "gate_simplex_max_absolute_error": gate_simplex_error,
    }
    result["risk_non_degenerate"] = (
        finite and result["risk_standard_deviation"] > 1e-8
    )
    result["gate_non_degenerate"] = (
        finite
        and result["gate_max_branch_standard_deviation"] > 1e-8
        and gate_simplex_error <= 1e-5
    )
    return result


def validate_metrics(
    path: Path, method: str
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    metrics = load(path)
    report_key = REPORT_KEYS[method]
    report = metrics.get("reports", {}).get(report_key)
    if not isinstance(report, dict):
        raise ValueError(f"{method} lacks report={report_key}")
    for metric in REQUIRED_METRICS:
        value = report.get(metric)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(f"{method} invalid metric={metric}")
    if not isinstance(metrics.get("split_metadata"), dict):
        raise ValueError(f"{method} lacks split metadata")
    if not selection_is_clean(metrics):
        raise ValueError(f"{method} violates known-only selection")
    diagnostics: Dict[str, Any] = {}
    if method == "medaf_tabular_adapter":
        scores_path = path.parent / "scores.npz"
        if not scores_path.is_file():
            raise ValueError("MEDAF scores.npz missing")
        diagnostics = score_diagnostics(scores_path)
    return metrics, diagnostics


def medaf_arguments(
    record: Dict[str, Any],
    design: Dict[str, Any],
    output_dir: Path,
) -> List[str]:
    shared = record["shared_arguments"]
    arguments: List[str] = []
    for option in (
        "--csv",
        "--config",
        "--unknown-classes",
        "--benign-class",
        "--split-strategy",
        "--max-per-class",
    ):
        arguments.extend([option, str(shared[option])])
    mechanism = design["mechanism"]
    arguments.extend(
        [
            "--epochs",
            str(mechanism["training_epochs"]),
            "--milestone",
            str(mechanism["learning_rate_milestone"]),
            "--learning-rate",
            str(mechanism["learning_rate"]),
            "--momentum",
            str(mechanism["momentum"]),
            "--weight-decay",
            str(mechanism["weight_decay"]),
            "--gate-temperature",
            str(mechanism["gate_temperature"]),
            "--logit-temperature",
            str(mechanism["logit_temperature"]),
            "--known-acceptance",
            str(design["leakage_policy"]["known_acceptance_quantile"]),
            "--batch-size",
            "128",
            "--num-workers",
            "4",
            "--seed",
            str(design["pilot"]["training_seed"]),
            "--output-dir",
            str(output_dir),
        ]
    )
    return arguments


def neural_arguments(
    record: Dict[str, Any],
    design: Dict[str, Any],
    method: str,
    output_dir: Path,
) -> List[str]:
    arguments = list(record["trainer_arguments"][method])
    arguments = replace_option(
        arguments, "--seed", str(design["pilot"]["training_seed"])
    )
    arguments = replace_option(
        arguments, "--output-dir", str(output_dir)
    )
    return arguments


def validate_existing_manifest(
    path: Path,
    *,
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    suite: str,
    scenario: str,
    method: str,
) -> bool:
    if not path.is_file():
        return False
    value = load(path)
    if (
        value.get("schema_version") != SCHEMA
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or value.get("task")
        != {"suite": suite, "scenario": scenario, "method": method}
    ):
        raise ValueError(f"invalid existing MEDAF run manifest: {path}")
    metrics_path = path.parent / "metrics.json"
    if file_hash(metrics_path) != value["metrics_file_sha256"]:
        raise ValueError(f"MEDAF metrics hash mismatch: {path}")
    metrics, diagnostics = validate_metrics(metrics_path, method)
    if canonical_hash(metrics["split_metadata"]) != value[
        "split_fingerprint"
    ]:
        raise ValueError(f"MEDAF split fingerprint mismatch: {path}")
    if diagnostics != value.get("score_diagnostics", {}):
        raise ValueError(f"MEDAF score diagnostics mismatch: {path}")
    return True


def run(
    protocol_path: Path,
    run_root: Path,
    project_root: Path,
) -> Dict[str, int]:
    protocol = load(protocol_path)
    if (
        protocol.get("schema_version") != PROTOCOL_SCHEMA
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("invalid MEDAF pilot protocol")
    design = load(project_root / protocol["design_path"])
    if (
        design.get("manifest_sha256")
        != protocol["design_manifest_sha256"]
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("MEDAF protocol/design binding mismatch")
    methods = list(design["pilot"]["methods"])
    completed = 0
    for record in protocol["source_registry"]:
        suite = record["suite"]
        scenario = record["scenario"]
        for method in methods:
            output_dir = run_root / suite / scenario / method
            manifest_path = output_dir / "run_manifest.json"
            if not validate_existing_manifest(
                manifest_path,
                protocol=protocol,
                design=design,
                suite=suite,
                scenario=scenario,
                method=method,
            ):
                output_dir.mkdir(parents=True, exist_ok=True)
                if method == "medaf_tabular_adapter":
                    trainer = project_root / protocol["implementation"][
                        "medaf_trainer"
                    ]
                    arguments = medaf_arguments(
                        record, design, output_dir
                    )
                else:
                    trainer = project_root / protocol["implementation"][
                        "neural_trainer"
                    ]
                    arguments = neural_arguments(
                        record, design, method, output_dir
                    )
                command = [sys.executable, str(trainer), *arguments]
                try:
                    subprocess.run(command, cwd=project_root, check=True)
                    metrics, diagnostics = validate_metrics(
                        output_dir / "metrics.json", method
                    )
                    value: Dict[str, Any] = {
                        "schema_version": SCHEMA,
                        "state": "complete",
                        "protocol_manifest_sha256": protocol[
                            "manifest_sha256"
                        ],
                        "design_manifest_sha256": design[
                            "manifest_sha256"
                        ],
                        "task": {
                            "suite": suite,
                            "scenario": scenario,
                            "method": method,
                        },
                        "training_seed": design["pilot"][
                            "training_seed"
                        ],
                        "report_key": REPORT_KEYS[method],
                        "command": command,
                        "metrics_file_sha256": file_hash(
                            output_dir / "metrics.json"
                        ),
                        "split_fingerprint": canonical_hash(
                            metrics["split_metadata"]
                        ),
                        "known_only_selection_verified": True,
                        "score_diagnostics": diagnostics,
                    }
                    value["manifest_sha256"] = canonical_hash(value)
                    manifest_path.write_text(
                        json.dumps(value, indent=2, sort_keys=True)
                        + "\n",
                        encoding="utf-8",
                    )
                    (output_dir / "failure.json").unlink(missing_ok=True)
                except Exception as error:
                    failure: Dict[str, Any] = {
                        "schema_version": (
                            "strict_v4_medaf_tabular_failure_v1"
                        ),
                        "state": "failed",
                        "protocol_manifest_sha256": protocol[
                            "manifest_sha256"
                        ],
                        "task": {
                            "suite": suite,
                            "scenario": scenario,
                            "method": method,
                        },
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                    failure["manifest_sha256"] = canonical_hash(failure)
                    (output_dir / "failure.json").write_text(
                        json.dumps(failure, indent=2, sort_keys=True)
                        + "\n",
                        encoding="utf-8",
                    )
                    raise
                validate_existing_manifest(
                    manifest_path,
                    protocol=protocol,
                    design=design,
                    suite=suite,
                    scenario=scenario,
                    method=method,
                )
            completed += 1
            print(
                f"report={completed}/{design['pilot']['expected_reports']} "
                f"suite={suite} scenario={scenario} method={method}",
                flush=True,
            )
    return {"run_manifest_count": completed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.protocol.resolve(),
        args.run_root.resolve(),
        args.project_root.resolve(),
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
