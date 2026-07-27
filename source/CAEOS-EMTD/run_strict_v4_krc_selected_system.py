from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_protocol(protocol: Dict[str, Any]) -> None:
    identities = {
        (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        )
        for item in protocol.get("sources", [])
    }
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_selected_system_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or protocol.get("selected_algorithm") != "krc_csr_caeos_v1"
        or int(protocol.get("source_count", -1)) != 306
        or len(protocol.get("sources", [])) != 306
        or len(identities) != 306
    ):
        raise ValueError("invalid KRC selected-system protocol")


def validate_benchmark(
    path: Path, protocol: Dict[str, Any], source: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    expected_source = {
        key: source[key]
        for key in (
            "suite",
            "scenario",
            "training_seed",
            "capture_manifest_file_sha256",
            "capture_execution_file_sha256",
            "krc_runtime_sha256",
            "evaluation_inputs_sha256",
            "total_capture_wall_seconds",
        )
    }
    artifact = path.parent / "embedded_pairwise_runtime.joblib"
    if (
        value.get("schema_version")
        != "strict_v4_krc_selected_system_benchmark_v1"
        or value.get("state") != "complete"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("source") != expected_source
        or value.get("roundtrip", {}).get("krc_capture", {}).get("passes")
        is not True
        or value.get("roundtrip", {})
        .get("embedded_pairwise", {})
        .get("passes")
        is not True
        or not artifact.is_file()
        or file_hash(artifact)
        != value.get("cost", {}).get("pairwise_artifact_sha256")
    ):
        raise ValueError(f"invalid existing KRC system benchmark: {path}")
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


def validate_completion(
    protocol: Dict[str, Any],
    summary: Path,
    audit: Path,
    completion: Path,
) -> bool:
    if not completion.exists():
        return False
    if not summary.is_file() or not audit.is_file():
        raise ValueError("completion exists without summary and audit")
    audit_value = load(audit)
    completion_value = load(completion)
    if (
        audit_value.get("schema_version")
        != "strict_v4_krc_selected_system_audit_v1"
        or audit_value.get("manifest_sha256") != canonical_hash(audit_value)
        or audit_value.get("passes") is not True
        or completion_value
        != {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "summary_file_sha256": file_hash(summary),
            "audit_file_sha256": file_hash(audit),
        }
    ):
        raise ValueError("invalid KRC selected-system completion")
    return True


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
) -> None:
    validate_protocol(protocol)
    if os.environ.get("KRC_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError("exclusive-machine preflight marker is required")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(
                f"KRC selected-system implementation SHA mismatch: {relative}"
            )
    for index, source in enumerate(protocol["sources"], start=1):
        output = (
            run_root
            / "benchmarks"
            / str(source["suite"])
            / str(source["scenario"])
            / f"seed{int(source['training_seed'])}"
            / "benchmark.json"
        )
        if validate_benchmark(output, protocol, source):
            print(
                f"retained {index}/306 {source['suite']}/"
                f"{source['scenario']}/seed{source['training_seed']}",
                flush=True,
            )
            continue
        if output.parent.exists() and any(output.parent.iterdir()):
            raise ValueError(
                f"partial KRC selected-system output exists: {output.parent}"
            )
        command = [
            sys.executable,
            str(project_root / "benchmark_krc_selected_system_runtime.py"),
            "--capture-dir",
            str(source["capture_dir"]),
            "--protocol",
            str(protocol_path),
            "--suite",
            str(source["suite"]),
            "--scenario",
            str(source["scenario"]),
            "--training-seed",
            str(source["training_seed"]),
            "--output",
            str(output),
        ]
        run_command(command, output.with_suffix(".log"))
        validate_benchmark(output, protocol, source)
        print(
            f"completed {index}/306 {source['suite']}/"
            f"{source['scenario']}/seed{source['training_seed']}",
            flush=True,
        )
    summary = run_root / "summary.json"
    audit = run_root / "audit.json"
    completion = run_root / "execution_complete"
    if validate_completion(protocol, summary, audit, completion):
        print("retained complete KRC selected-system finalization", flush=True)
        return
    if summary.exists() or audit.exists():
        raise ValueError("partial KRC selected-system finalization exists")
    run_command(
        [
            sys.executable,
            str(project_root / "summarize_strict_v4_krc_selected_system.py"),
            "--protocol",
            str(protocol_path),
            "--run-root",
            str(run_root),
            "--output",
            str(summary),
        ],
        run_root / "summary.log",
    )
    run_command(
        [
            sys.executable,
            str(project_root / "audit_strict_v4_krc_selected_system.py"),
            "--protocol",
            str(protocol_path),
            "--summary",
            str(summary),
            "--run-root",
            str(run_root),
            "--output",
            str(audit),
        ],
        run_root / "audit.log",
    )
    audit_value = load(audit)
    if audit_value.get("passes") is not True:
        raise ValueError("KRC selected-system final audit failed")
    completion.write_text(
        json.dumps(
            {
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "summary_file_sha256": file_hash(summary),
                "audit_file_sha256": file_hash(audit),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    run_root = args.run_root.resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    run(
        load(protocol_path),
        protocol_path,
        args.project_root.resolve(),
        run_root,
    )


if __name__ == "__main__":
    main()
