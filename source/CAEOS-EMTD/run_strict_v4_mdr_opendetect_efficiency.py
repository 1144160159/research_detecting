from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
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
        != "strict_v4_mdr_opendetect_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("selected_algorithm") != "mdr_caeos_v1"
        or int(protocol.get("source_count", -1)) != 306
        or len(protocol.get("sources", [])) != 306
        or len(identities) != 306
    ):
        raise ValueError("invalid MDR-OpenDetect efficiency protocol")


def expected_source(source: Dict[str, Any]) -> Dict[str, Any]:
    candidate = source["candidate"]
    comparator = source["comparator"]
    return {
        "suite": source["suite"],
        "scenario": source["scenario"],
        "training_seed": int(source["training_seed"]),
        "candidate_capture_manifest_file_sha256": candidate[
            "capture_manifest_file_sha256"
        ],
        "candidate_capture_execution_file_sha256": candidate[
            "capture_execution_file_sha256"
        ],
        "candidate_runtime_artifact_sha256": candidate[
            "runtime_artifact_sha256"
        ],
        "evaluation_inputs_sha256": candidate["evaluation_inputs_sha256"],
        "comparator_seed": int(comparator["comparator_seed"]),
        "comparator_capture_manifest_file_sha256": comparator[
            "capture_manifest_file_sha256"
        ],
        "comparator_runtime_artifact_sha256": comparator[
            "runtime_artifact_sha256"
        ],
        "comparator_source_metrics_file_sha256": comparator[
            "source_metrics_file_sha256"
        ],
    }


def validate_benchmark(
    path: Path, protocol: Dict[str, Any], source: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_mdr_opendetect_efficiency_benchmark_v1"
        or value.get("state") != "complete"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("source") != expected_source(source)
        or value.get("same_input_evidence", {}).get(
            "candidate_and_comparator_received_same_arrays"
        )
        is not True
        or value.get("same_input_evidence", {}).get("labels_loaded")
        is not False
        or value.get("exclusive_machine_preflight_marker") != "passed"
        or value.get(
            "unknown_or_test_labels_used_for_benchmark_selection"
        )
        is not False
        or value.get("comparator_seed_reuse_supports_effectiveness_claim")
        is not False
    ):
        raise ValueError(f"invalid existing efficiency benchmark: {path}")
    return True


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
) -> None:
    validate_protocol(protocol)
    for relative, expected in protocol["implementation_sha256"].items():
        actual = file_hash(project_root / relative)
        if actual != expected:
            raise ValueError(
                "MDR-OpenDetect efficiency implementation SHA mismatch: "
                f"{relative}"
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
            raise ValueError(f"partial efficiency output exists: {output.parent}")
        output.parent.mkdir(parents=True, exist_ok=True)
        log_path = output.with_suffix(".log")
        command = [
            sys.executable,
            str(project_root / "benchmark_mdr_opendetect_runtime.py"),
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
        with log_path.open("w", encoding="utf-8") as log:
            subprocess.run(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        validate_benchmark(output, protocol, source)
        print(
            f"completed {index}/306 {source['suite']}/"
            f"{source['scenario']}/seed{source['training_seed']}",
            flush=True,
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
