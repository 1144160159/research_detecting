from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_caeos_runtime import report, selected_modality


PROTOCOL_SCHEMA = "strict_v4_self_algorithm_direct_tournament_protocol_v1"
RECORD_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_task_evaluation_v1"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def select_task(
    protocol: dict[str, Any], suite: str, scenario: str, seed: int
) -> dict[str, Any]:
    matches = [
        task
        for task in protocol["confirmation_universe"]["tasks"]
        if task["suite"] == suite
        and task["scenario"] == scenario
        and int(task["training_seed"]) == int(seed)
    ]
    if len(matches) != 1:
        raise ValueError("exactly one frozen tournament task required")
    return matches[0]


def split_fingerprint(value: Any) -> str:
    output = value.get("combined") if isinstance(value, dict) else value
    if not isinstance(output, str) or len(output) != 64:
        raise ValueError("valid split fingerprint required")
    return output


def frozen_challenger_risk(
    protocol: dict[str, Any], runtime: Any
) -> str:
    expected = protocol["candidate_training"]["pug_execution_controls"][
        "candidate_risk_selection"
    ]
    observed = runtime.evidence().get("selected_risk")
    if observed != expected:
        raise ValueError(
            "challenger runtime did not use the frozen PUG risk: "
            f"{observed!r} != {expected!r}"
        )
    return str(observed)


def load_incumbent(
    protocol: dict[str, Any], directory: Path
) -> tuple[Any, list[np.ndarray], np.ndarray, np.ndarray, dict[str, Any]]:
    manifest_path = directory / "capture_manifest.json"
    manifest = load(manifest_path)
    schema = (
        "strict_v4_krc_csr_runtime_capture_v1"
        if protocol["incumbent_algorithm"] == "krc_csr_caeos_v1"
        else "strict_v4_rrc_csr_runtime_capture_v1"
    )
    require_canonical(manifest, schema, "incumbent capture")
    artifact = directory / manifest["runtime_artifact"]
    inputs = directory / manifest["evaluation_inputs"]
    if (
        file_hash(artifact) != manifest["runtime_artifact_sha256"]
        or file_hash(inputs) != manifest["evaluation_inputs_sha256"]
    ):
        raise ValueError("incumbent capture artifact drift")
    runtime = joblib.load(artifact)
    evidence = runtime.evidence()
    with np.load(inputs, allow_pickle=False) as archive:
        views = [
            np.asarray(archive[f"view_{index}"])
            for index in range(int(evidence["modality_count"]))
        ]
        labels = np.asarray(archive["test_labels"], dtype=np.int64)
        unknown = np.asarray(archive["test_unknown"], dtype=bool)
    return runtime, views, labels, unknown, {
        "manifest": manifest,
        "manifest_path": manifest_path,
        "artifact": artifact,
        "inputs": inputs,
    }


def load_challenger(
    directory: Path, train_directory: Path
) -> tuple[Any, list[np.ndarray], np.ndarray, np.ndarray, dict[str, Any]]:
    manifest_path = directory / "capture_manifest.json"
    manifest = load(manifest_path)
    if (
        manifest.get("schema_version")
        != "strict_v4_pairwise_runtime_capture_v1"
        or manifest.get("equivalence", {}).get("passes") is not True
        or manifest.get("benchmark_inputs_contain_labels") is not False
    ):
        raise ValueError("complete PUG challenger capture required")
    artifact = directory / manifest["deployment_artifact"]
    inputs = directory / manifest["benchmark_inputs"]
    metrics_path = train_directory / "metrics.json"
    scores_path = train_directory / "scores.npz"
    for path in (
        artifact,
        inputs,
        metrics_path,
        scores_path,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    if (
        file_hash(artifact) != manifest["deployment_artifact_sha256"]
        or file_hash(inputs) != manifest["benchmark_inputs_sha256"]
    ):
        raise ValueError("challenger capture artifact drift")
    runtime = joblib.load(artifact)
    with np.load(inputs, allow_pickle=False) as archive:
        views = [
            np.asarray(archive[name])
            for name in sorted(
                archive.files,
                key=lambda name: int(name.rsplit("_", 1)[1]),
            )
        ]
    with np.load(scores_path, allow_pickle=False) as scores:
        labels = np.asarray(scores["test_labels"], dtype=np.int64)
        unknown = np.asarray(scores["test_unknown"], dtype=bool)
    return runtime, views, labels, unknown, {
        "manifest": manifest,
        "manifest_path": manifest_path,
        "artifact": artifact,
        "inputs": inputs,
        "metrics_path": metrics_path,
        "scores_path": scores_path,
        "metrics": load(metrics_path),
    }


def evaluate_task(
    *,
    protocol: dict[str, Any],
    protocol_path: Path,
    task: dict[str, Any],
    task_root: Path,
    output: Path,
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "tournament protocol")
    if protocol.get("execution_admitted") is not True:
        raise ValueError("admitted tournament protocol required")
    incumbent, incumbent_views, labels, unknown, incumbent_files = (
        load_incumbent(protocol, task_root / "incumbent_capture")
    )
    challenger, challenger_views, challenger_labels, challenger_unknown, (
        challenger_files
    ) = load_challenger(
        task_root / "challenger_capture",
        task_root / "challenger_train",
    )
    observed_risk = frozen_challenger_risk(protocol, challenger)
    if (
        len(incumbent_views) != len(challenger_views)
        or not np.array_equal(labels, challenger_labels)
        or not np.array_equal(unknown, challenger_unknown)
        or any(
            not np.array_equal(left, right)
            for left, right in zip(incumbent_views, challenger_views)
        )
    ):
        raise ValueError("incumbent and challenger test split is not paired")
    incumbent_split = split_fingerprint(
        incumbent_files["manifest"].get("split_fingerprint")
    )
    challenger_split = split_fingerprint(
        challenger_files["metrics"]
        .get("split_metadata", {})
        .get("split_fingerprint")
    )
    if incumbent_split != challenger_split:
        raise ValueError("incumbent and challenger split fingerprints differ")
    records = []
    conditions = protocol["confirmation_universe"]["conditions"]
    for condition in conditions:
        if condition == "clean":
            modality = None
            severity = 0.0
            views = incumbent_views
        else:
            modality = selected_modality(
                protocol["manifest_sha256"],
                task["suite"],
                task["scenario"],
                condition,
                len(incumbent_views),
            )
            severity = float(
                protocol["confirmation_universe"]["fixed_severity"][
                    condition
                ]
            )
            views = incumbent.corrupt(
                incumbent_views,
                family=condition,
                modality=modality,
                severity=severity,
                seed=int(task["corruption_seed"]),
            )
        incumbent_output = incumbent.predict(views)
        challenger_output = challenger.predict(views)
        incumbent_report = report(
            labels,
            unknown,
            incumbent_output["prediction"],
            incumbent_output["risk"],
            float(incumbent.clean_threshold),
        )
        challenger_report = report(
            labels,
            unknown,
            challenger_output["prediction"],
            challenger_output["risk"],
            float(challenger.clean_threshold),
        )
        records.append(
            {
                "condition": condition,
                "corruption": {
                    "modality": modality,
                    "severity": severity,
                    "seed": int(task["corruption_seed"]),
                    "same_corrupted_arrays_for_both_algorithms": True,
                },
                "incumbent_report": incumbent_report,
                "challenger_report": challenger_report,
            }
        )
    artifacts = {
        "incumbent_manifest": file_hash(
            incumbent_files["manifest_path"]
        ),
        "incumbent_runtime": file_hash(incumbent_files["artifact"]),
        "incumbent_inputs": file_hash(incumbent_files["inputs"]),
        "challenger_manifest": file_hash(
            challenger_files["manifest_path"]
        ),
        "challenger_runtime": file_hash(challenger_files["artifact"]),
        "challenger_inputs": file_hash(challenger_files["inputs"]),
        "challenger_metrics": file_hash(challenger_files["metrics_path"]),
        "challenger_scores": file_hash(challenger_files["scores_path"]),
    }
    value: dict[str, Any] = {
        "schema_version": RECORD_SCHEMA,
        "state": "single_paired_task_evaluation_complete",
        "task": {
            "identity": task["identity"],
            "suite": task["suite"],
            "scenario": task["scenario"],
            "seed": int(task["training_seed"]),
            "corruption_seed": int(task["corruption_seed"]),
        },
        "incumbent_algorithm": protocol["incumbent_algorithm"],
        "challenger_algorithm": protocol["challenger_algorithm"],
        "challenger_selected_risk": observed_risk,
        "split_fingerprint": incumbent_split,
        "condition_evaluations": records,
        "input_evidence": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "protocol_file_sha256": file_hash(protocol_path),
            "artifact_sha256": artifacts,
        },
        "claim_boundary": {
            "single_task_record_cannot_select_candidate": True,
            "test_labels_used_only_for_frozen_final_evaluation": True,
            "unknown_or_test_labels_not_used_for_fit_selection_or_threshold": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    if output.is_file():
        if load(output) != value:
            raise ValueError("existing tournament task record is immutable")
        return value
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path(
            "runs/strict_v4_self_algorithm_direct_tournament_v1"
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    protocol = load(protocol_path)
    task = select_task(protocol, args.suite, args.scenario, args.seed)
    task_root = (
        resolve(args.run_root)
        / "task_runs"
        / task["suite"]
        / task["scenario"]
        / f"seed{int(task['training_seed'])}"
    )
    output = (
        resolve(args.output)
        if args.output is not None
        else (
            root
            / "results/strict_v4_self_algorithm_direct_tournament_v1/"
            "task_records"
            / task["suite"]
            / task["scenario"]
            / f"seed{int(task['training_seed'])}"
            / "evaluation.json"
        )
    )
    value = evaluate_task(
        protocol=protocol,
        protocol_path=protocol_path,
        task=task,
        task_root=task_root,
        output=output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
