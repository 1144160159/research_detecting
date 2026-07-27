from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from audit_strict_v4_krc_parrot_safety import audit
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_krc_parrot_safety import summarize


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_protocol(protocol: Dict[str, Any]) -> None:
    identities = {
        (str(item["scenario"]), int(item["training_seed"]))
        for item in protocol.get("source_model_pairs", [])
    }
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_parrot_safety_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("selected_algorithm") != "krc_csr_caeos_v1"
        or protocol.get("execution_admitted") is not True
        or int(protocol.get("source_model_pair_count", -1)) != 30
        or len(identities) != 30
        or int(protocol.get("capture_count", -1)) != 320
    ):
        raise ValueError("invalid KRC PARROT protocol")


def validate_deployment(
    path: Path, source: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    artifact = path.parent / str(value.get("deployment_artifact", ""))
    if (
        value.get("schema_version")
        != "strict_v4_krc_parrot_deployment_capture_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("scenario") != source["scenario"]
        or int(value.get("training_seed", -1))
        != int(source["training_seed"])
        or value.get("source_split_fingerprint")
        != source["source_split_fingerprint"]
        or value.get("source_capture_manifest_file_sha256")
        != source["capture_manifest_file_sha256"]
        or value.get("preprocessing_replay", {}).get(
            "all_view_arrays_equal"
        )
        is not True
        or value.get("serialization_roundtrip", {}).get("passes")
        is not True
        or value.get("model_refit_performed") is not False
        or not artifact.is_file()
        or file_hash(artifact) != value.get("deployment_artifact_sha256")
    ):
        raise ValueError(f"invalid existing KRC PARROT deployment: {path}")
    return True


def validate_metrics(
    path: Path, source: Dict[str, Any], protocol: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_krc_parrot_model_pair_metrics_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("source", {}).get("scenario") != source["scenario"]
        or int(value.get("source", {}).get("training_seed", -1))
        != int(source["training_seed"])
        or int(value.get("capture_count", -1)) != 320
        or int(value.get("failure_count", -1)) != 0
        or value.get(
            "parrot_features_or_labels_used_for_fit_selection_calibration_"
            "or_threshold"
        )
        is not False
        or value.get("candidate_model_refit_for_parrot") is not False
    ):
        raise ValueError(f"invalid existing KRC PARROT metrics: {path}")
    return True


def run_command(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    workers: int,
) -> None:
    validate_protocol(protocol)
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(
                f"KRC PARROT implementation SHA mismatch: {relative}"
            )
    if int(workers) < 1:
        raise ValueError("KRC PARROT workers must be positive")

    def frozen_sources_match(source: Dict[str, Any]) -> None:
        capture_dir = Path(source["capture_dir"])
        if (
            file_hash(capture_dir / "capture_manifest.json")
            != source["capture_manifest_file_sha256"]
            or file_hash(capture_dir / "capture_execution.json")
            != source["capture_execution_file_sha256"]
            or file_hash(
                capture_dir
                / load(capture_dir / "capture_manifest.json")[
                    "runtime_artifact"
                ]
            )
            != source["krc_runtime_sha256"]
            or file_hash(Path(source["csv"])) != source["csv_sha256"]
            or file_hash(Path(source["config"])) != source["config_sha256"]
            or file_hash(Path(source["opendetect_runtime"]))
            != source["opendetect_runtime_sha256"]
            or file_hash(Path(source["opendetect_csv"]))
            != source["opendetect_csv_sha256"]
            or file_hash(Path(source["opendetect_config"]))
            != source["opendetect_config_sha256"]
            or file_hash(Path(source["opendetect_benchmark_inputs"]))
            != source["opendetect_benchmark_inputs_sha256"]
        ):
            raise ValueError("KRC PARROT frozen source identity drifted")

    def capture_source(index: int, source: Dict[str, Any]) -> str:
        frozen_sources_match(source)
        deployment_dir = (
            run_root
            / "deployments"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
        )
        manifest_path = deployment_dir / "capture_manifest.json"
        if validate_deployment(manifest_path, source):
            return (
                f"retained deployment {index}/30 {source['scenario']}/"
                f"seed{source['training_seed']}"
            )
        if deployment_dir.exists() and any(deployment_dir.iterdir()):
            raise ValueError(
                f"partial KRC PARROT deployment exists: {deployment_dir}"
            )
        run_command(
            [
                sys.executable,
                str(project_root / "capture_krc_parrot_deployment_bundle.py"),
                "--source-capture-dir",
                str(source["capture_dir"]),
                "--project-root",
                str(project_root),
                "--output-dir",
                str(deployment_dir),
            ],
            deployment_dir / "capture.log",
        )
        validate_deployment(manifest_path, source)
        return (
            f"completed deployment {index}/30 {source['scenario']}/"
            f"seed{source['training_seed']}"
        )

    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = {
            executor.submit(capture_source, index, source): index
            for index, source in enumerate(
                protocol["source_model_pairs"], start=1
            )
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)

    def evaluate_source(index: int, source: Dict[str, Any]) -> str:
        deployment_dir = (
            run_root
            / "deployments"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
        )
        output = (
            run_root
            / "evaluations"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
            / "model_pair_metrics.json"
        )
        if validate_metrics(output, source, protocol):
            return (
                f"retained evaluation {index}/30 {source['scenario']}/"
                f"seed{source['training_seed']}"
            )
        if output.parent.exists() and any(output.parent.iterdir()):
            raise ValueError(
                f"partial KRC PARROT evaluation exists: {output.parent}"
            )
        run_command(
            [
                sys.executable,
                str(project_root / "evaluate_krc_parrot_capture.py"),
                "--protocol",
                str(protocol_path),
                "--scenario",
                str(source["scenario"]),
                "--training-seed",
                str(source["training_seed"]),
                "--deployment-dir",
                str(deployment_dir),
                "--output",
                str(output),
            ],
            output.with_suffix(".log"),
        )
        validate_metrics(output, source, protocol)
        return (
            f"completed evaluation {index}/30 {source['scenario']}/"
            f"seed{source['training_seed']}"
        )

    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = {
            executor.submit(evaluate_source, index, source): index
            for index, source in enumerate(
                protocol["source_model_pairs"], start=1
            )
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)
    result_root.mkdir(parents=True, exist_ok=True)
    summary_path = result_root / "summary.json"
    audit_path = result_root / "audit.json"
    summary = summarize(protocol, run_root)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    audited = audit(protocol, summary, project_root, run_root)
    audit_path.write_text(
        json.dumps(audited, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if audited.get("passes") is not True:
        raise ValueError("KRC PARROT independent audit failed")
    completion = {
        "schema_version": "strict_v4_krc_parrot_execution_complete_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "audit_manifest_sha256": audited["manifest_sha256"],
        "benign_domain_shift_safety_gate_passes": audited[
            "benign_domain_shift_safety_gate_passes"
        ],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    (result_root / "execution_complete").write_text(
        json.dumps(completion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    run(
        load(protocol_path),
        protocol_path,
        args.project_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        args.workers,
    )


if __name__ == "__main__":
    main()
