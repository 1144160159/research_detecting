from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_nested_gate_matrix import (
    Experiment as PairwiseExperiment,
    build_run_provenance,
    freeze_or_validate_provenance,
)
from run_neural_baseline_matrix import Experiment as NeuralExperiment


VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"
RISK_POLICY = "strict_v4_vgrf_confirmation_reference_v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def replace_value(command: list[str], flag: str, value: str) -> None:
    try:
        index = command.index(flag)
        command[index + 1] = value
    except (ValueError, IndexError) as error:
        raise ValueError(f"source command lacks {flag}") from error


def replay_command(
    source_provenance: dict[str, Any],
    *,
    seed: int,
    output_dir: Path,
    risk_policy: str | None = None,
) -> list[str]:
    source = source_provenance.get("command")
    if not isinstance(source, list) or len(source) < 2:
        raise ValueError("source provenance command is invalid")
    command = [str(value) for value in source]
    command[0] = sys.executable
    replace_value(command, "--seed", str(seed))
    replace_value(command, "--output-dir", str(output_dir.resolve()))
    if risk_policy is not None:
        replace_value(command, "--risk-policy-name", risk_policy)
    return command


def seed317_records(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid VGRF selected-system execution protocol")
    if protocol.get("selected_algorithm") != VGRF:
        raise ValueError("execution protocol does not select VGRF")
    records = [
        item
        for item in protocol.get("source_registry", [])
        if int(item.get("seed", -1)) == 317
    ]
    identities = {
        (str(item["suite"]), str(item["scenario"]), int(item["seed"]))
        for item in records
    }
    if (
        len(records) != 102
        or len(identities) != 102
        or any(
            item.get("source_mode")
            != "preregistered_seed317_execution"
            for item in records
        )
    ):
        raise ValueError("execution protocol lacks 102 unique seed-317 records")
    return sorted(
        records, key=lambda item: (item["suite"], item["scenario"])
    )


def resolve_project_input(project: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project / path


def validate_source_inputs(
    project: Path, record: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = record["source_inputs"]
    paths = {
        "csv": resolve_project_input(project, inputs["csv"]),
        "config": resolve_project_input(project, inputs["config"]),
        "source_provenance": resolve_project_input(
            project, inputs["source_provenance"]
        ),
        "opendetect_source_provenance": resolve_project_input(
            project, inputs["opendetect_source_provenance"]
        ),
    }
    expected = {
        "csv": inputs["csv_sha256"],
        "config": inputs["config_sha256"],
        "source_provenance": inputs["source_provenance_sha256"],
        "opendetect_source_provenance": inputs[
            "opendetect_source_provenance_sha256"
        ],
    }
    for name, path in paths.items():
        if not path.is_file() or file_hash(path) != expected[name]:
            raise ValueError(f"seed-317 source input SHA mismatch: {name}")
    return load(paths["source_provenance"]), load(
        paths["opendetect_source_provenance"]
    )


def reference_record(record: dict[str, Any]) -> dict[str, Any]:
    inputs = record["source_inputs"]
    return {
        "suite": record["suite"],
        "scenario": record["scenario"],
        "training_seed": 317,
        "unknown_classes": inputs["unknown_classes"],
        "csv": inputs["csv"],
        "csv_sha256": inputs["csv_sha256"],
        "config": inputs["config"],
        "config_sha256": inputs["config_sha256"],
        "source_provenance": inputs["source_provenance"],
        "source_provenance_sha256": inputs[
            "source_provenance_sha256"
        ],
    }


def run_logged(
    command: list[str], *, project: Path, log_path: Path
) -> float:
    started = time.perf_counter()
    with log_path.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            command,
            cwd=project,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed with exit {completed.returncode}: {log_path}"
        )
    return elapsed


def run_pairwise(
    *,
    project: Path,
    record: dict[str, Any],
    source_provenance: dict[str, Any],
    protocol: dict[str, Any],
) -> float:
    from caeos.vgrf_confirmation_validation import (
        validate_reference_result,
    )

    output = Path(record["run_output_roots"]["pairwise"])
    output.mkdir(parents=True, exist_ok=True)
    required = (
        output / "metrics.json",
        output / "provenance.json",
        output / "evidence_package.npz",
        output / "scores.npz",
    )
    command = replay_command(
        source_provenance,
        seed=317,
        output_dir=output,
        risk_policy=RISK_POLICY,
    )
    expected_provenance = build_run_provenance(
        PairwiseExperiment(
            suite=str(record["suite"]),
            scenario=str(record["scenario"]),
            unknown_classes=str(
                record["source_inputs"]["unknown_classes"]
            ),
            seed=317,
            output_dir=str(output.resolve()),
        ),
        command,
    )
    complete = freeze_or_validate_provenance(
        output,
        expected_provenance,
        (required[0], required[2], required[3]),
    )
    elapsed = 0.0
    if not complete:
        elapsed = run_logged(
            command, project=project, log_path=output / "training.log"
        )
    validator_protocol = {
        "implementation_sha256": {
            "train_hybrid_open_set.py": protocol[
                "implementation_sha256"
            ]["train_hybrid_open_set.py"]
        }
    }
    validate_reference_result(
        output,
        reference_record(record),
        validator_protocol,
        project,
    )
    return elapsed


def validate_vgrf_result(
    result: dict[str, Any],
    *,
    record: dict[str, Any],
    protocol: dict[str, Any],
    reference: Path,
) -> None:
    expected = {
        "schema_version": (
            "strict_v4_validation_gated_reliability_fusion_metrics_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": 317,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise ValueError(f"seed-317 VGRF {key} mismatch")
    if result.get("input_sha256") != {
        "evidence_package": file_hash(reference / "evidence_package.npz"),
        "scores": file_hash(reference / "scores.npz"),
    }:
        raise ValueError("seed-317 VGRF input binding mismatch")
    diagnostics = result.get("diagnostics", {})
    if (
        diagnostics.get(
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
        )
        is not False
        or diagnostics.get("test_labels_used_for_final_metrics_only")
        is not True
    ):
        raise ValueError("seed-317 VGRF leakage declaration failed")


def run_vgrf(
    *,
    record: dict[str, Any],
    protocol: dict[str, Any],
) -> float:
    from evaluate_validation_gated_reliability_fusion import evaluate

    reference = Path(record["run_output_roots"]["pairwise"])
    output = Path(record["run_output_roots"]["vgrf"])
    output.mkdir(parents=True, exist_ok=True)
    metrics_path = output / "metrics.json"
    if metrics_path.is_file():
        result = load(metrics_path)
        elapsed = 0.0
    else:
        parameters = protocol["vgrf_known_only_parameters"]
        started = time.perf_counter()
        result = evaluate(
            argparse.Namespace(
                evidence_package=reference / "evidence_package.npz",
                scores=reference / "scores.npz",
                output_dir=output,
                protocol_manifest_sha256=protocol["manifest_sha256"],
                suite=record["suite"],
                scenario=record["scenario"],
                seed=317,
                shrinkage=parameters["empirical_bayes_shrinkage"],
                minimum_reliability=parameters["minimum_reliability"],
                risk_blend=parameters["risk_blend"],
                known_rejection_quantile=parameters[
                    "known_rejection_quantile"
                ],
                minimum_f1_gain=parameters["minimum_f1_gain"],
                maximum_correct_risk_increase=parameters[
                    "maximum_correct_risk_increase"
                ],
                minimum_auc_gain=parameters["minimum_auc_gain"],
                minimum_separation_gain=parameters[
                    "minimum_separation_gain"
                ],
                minimum_strict_proxy_gain=parameters[
                    "minimum_strict_proxy_gain"
                ],
            )
        )
        elapsed = time.perf_counter() - started
    validate_vgrf_result(
        result, record=record, protocol=protocol, reference=reference
    )
    return elapsed


def validate_opendetect(
    *,
    output: Path,
    expected_provenance: dict[str, Any],
    pairwise_metrics: dict[str, Any],
) -> None:
    required = (
        output / "metrics.json",
        output / "scores.npz",
        output / "provenance.json",
        output / "model.pt",
    )
    if any(not path.is_file() for path in required):
        raise ValueError("seed-317 OpenDetect output is incomplete")
    if load(output / "provenance.json") != expected_provenance:
        raise ValueError("seed-317 OpenDetect provenance mismatch")
    metrics = load(output / "metrics.json")
    if (
        metrics.get("model") != "opendetect"
        or "opendetect" not in metrics.get("reports", {})
        or metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError("seed-317 OpenDetect identity or leakage failure")
    expected_split = pairwise_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    observed_split = metrics["split_metadata"]["split_fingerprint"][
        "combined"
    ]
    if observed_split != expected_split:
        raise ValueError("seed-317 OpenDetect split fingerprint mismatch")


def run_opendetect(
    *,
    project: Path,
    record: dict[str, Any],
    source_provenance: dict[str, Any],
) -> float:
    output = Path(record["run_output_roots"]["opendetect"])
    output.mkdir(parents=True, exist_ok=True)
    command = replay_command(
        source_provenance, seed=317, output_dir=output
    )
    experiment = NeuralExperiment(
        suite=str(record["suite"]),
        scenario=str(record["scenario"]),
        unknown_classes=str(record["source_inputs"]["unknown_classes"]),
        model="opendetect",
        seed=317,
        output_dir=str(output.resolve()),
    )
    provenance = build_run_provenance(experiment, command)
    metrics_path = output / "metrics.json"
    scores_path = output / "scores.npz"
    complete = freeze_or_validate_provenance(
        output, provenance, (metrics_path, scores_path, output / "model.pt")
    )
    elapsed = 0.0
    if not complete:
        elapsed = run_logged(
            command, project=project, log_path=output / "run.log"
        )
    validate_opendetect(
        output=output,
        expected_provenance=provenance,
        pairwise_metrics=load(
            Path(record["run_output_roots"]["pairwise"]) / "metrics.json"
        ),
    )
    return elapsed


def write_state(
    path: Path,
    *,
    protocol: dict[str, Any],
    results: list[dict[str, Any]],
    state: str,
) -> None:
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_seed317_execution_state_v1"
        ),
        "state": state,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_source_pairs": 102,
        "reported_source_pairs": len(results),
        "results": sorted(
            results, key=lambda item: (item["suite"], item["scenario"])
        ),
    }
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    protocol = load(args.protocol)
    records = seed317_records(protocol)
    active_runner = Path(__file__).resolve()
    expected_runner_sha = protocol.get("implementation_sha256", {}).get(
        active_runner.name
    )
    if expected_runner_sha != file_hash(active_runner):
        raise ValueError("active seed-317 runner implementation SHA mismatch")
    results: list[dict[str, Any]] = []
    args.state.parent.mkdir(parents=True, exist_ok=True)
    write_state(
        args.state, protocol=protocol, results=results, state="running"
    )
    for record in records:
        pairwise_source, opendetect_source = validate_source_inputs(
            project, record
        )
        timings = {
            "pairwise_seconds": run_pairwise(
                project=project,
                record=record,
                source_provenance=pairwise_source,
                protocol=protocol,
            ),
            "vgrf_seconds": run_vgrf(record=record, protocol=protocol),
            "opendetect_seconds": run_opendetect(
                project=project,
                record=record,
                source_provenance=opendetect_source,
            ),
        }
        results.append(
            {
                "suite": record["suite"],
                "scenario": record["scenario"],
                "seed": 317,
                "timings": timings,
                "run_output_roots": record["run_output_roots"],
            }
        )
        write_state(
            args.state,
            protocol=protocol,
            results=results,
            state="running",
        )
        print(
            f"completed {record['suite']}/{record['scenario']}_seed317",
            flush=True,
        )
    write_state(
        args.state, protocol=protocol, results=results, state="complete"
    )
    (args.state.parent / "seed317_execution_complete").touch()


if __name__ == "__main__":
    main()
