from __future__ import annotations

import argparse
import json
import os
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
        != "strict_v4_mdr_evidence_reuse_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("selected_algorithm") != "mdr_caeos_v1"
        or int(protocol.get("source_count", -1)) != 306
        or int(protocol.get("expected_condition_count", -1)) != 1836
        or len(protocol.get("sources", [])) != 306
        or len(identities) != 306
    ):
        raise ValueError("invalid MDR evidence-reuse protocol")


def expected_source(source: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "suite": str(source["suite"]),
        "scenario": str(source["scenario"]),
        "training_seed": int(source["training_seed"]),
        "corruption_seed": int(source["corruption_seed"]),
        "capture_manifest_file_sha256": source[
            "capture_manifest_file_sha256"
        ],
        "runtime_artifact_sha256": source["runtime_artifact_sha256"],
        "evaluation_inputs_sha256": source["evaluation_inputs_sha256"],
    }


def validate_capture(
    path: Path, protocol: Dict[str, Any], source: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    condition_records = value.get("equivalence", {}).get("conditions", [])
    if (
        value.get("schema_version")
        != "strict_v4_mdr_evidence_reuse_capture_v1"
        or value.get("state") != "complete"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("source") != expected_source(source)
        or value.get("equivalence", {}).get("condition_count") != 6
        or len(condition_records) != 6
        or {
            str(item.get("condition")) for item in condition_records
        }
        != set(map(str, protocol["conditions"]))
        or not all(
            item.get("direct_equivalence", {}).get("passes") is True
            and item.get("serialization_equivalence", {}).get("passes")
            is True
            for item in condition_records
        )
        or value.get("equivalence", {}).get("all_direct_pass") is not True
        or value.get("equivalence", {}).get("all_serialization_pass")
        is not True
        or value.get("equivalence", {}).get("labels_loaded") is not False
        or value.get("fit_cost", {}).get(
            "unchanged_by_inference_optimization"
        )
        is not True
        or value.get("exclusive_machine_preflight_marker") != "passed"
        or value.get("unknown_or_test_labels_used") is not False
    ):
        raise ValueError(f"invalid existing MDR optimization capture: {path}")
    artifacts = value.get("artifact", {})
    optimized = path.parent / "mdr_evidence_reuse_runtime.joblib"
    pairwise = path.parent / "embedded_pairwise_runtime.joblib"
    if (
        not optimized.is_file()
        or not pairwise.is_file()
        or file_hash(optimized) != artifacts.get("optimized_mdr_sha256")
        or file_hash(pairwise) != artifacts.get("embedded_pairwise_sha256")
        or int(optimized.stat().st_size)
        != int(artifacts.get("optimized_mdr_bytes", -1))
        or int(pairwise.stat().st_size)
        != int(artifacts.get("embedded_pairwise_bytes", -1))
    ):
        raise ValueError(f"optimization artifact hash mismatch: {path.parent}")
    return True


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
) -> None:
    validate_protocol(protocol)
    if os.environ.get("MDR_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError(
            "external exclusive-machine preflight marker is required"
        )
    for relative, expected in protocol["implementation_sha256"].items():
        actual = file_hash(project_root / relative)
        if actual != expected:
            raise ValueError(
                f"MDR evidence-reuse implementation SHA mismatch: {relative}"
            )
    environment = dict(os.environ)
    for index, source in enumerate(protocol["sources"], start=1):
        output = (
            run_root
            / "captures"
            / str(source["suite"])
            / str(source["scenario"])
            / f"seed{int(source['training_seed'])}"
            / "optimization.json"
        )
        if validate_capture(output, protocol, source):
            print(
                f"retained {index}/306 {source['suite']}/"
                f"{source['scenario']}/seed{source['training_seed']}",
                flush=True,
            )
            continue
        if output.parent.exists() and any(output.parent.iterdir()):
            raise ValueError(
                f"partial MDR optimization output exists: {output.parent}"
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        log_path = output.with_suffix(".log")
        command = [
            sys.executable,
            str(project_root / "evaluate_mdr_evidence_reuse.py"),
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
                env=environment,
            )
        validate_capture(output, protocol, source)
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
