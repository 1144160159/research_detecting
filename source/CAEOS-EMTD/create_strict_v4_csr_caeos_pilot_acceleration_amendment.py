from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_csr_caeos_pilot import (
    load_json,
    validate_capture,
    validate_protocol,
)


EXPECTED_CAPTURE_COUNT = 14


def create_amendment(
    protocol: dict[str, Any],
    *,
    protocol_file_sha256: str,
    completed_captures: list[dict[str, Any]],
    observed_counts: dict[str, int],
    implementation: dict[str, str],
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    validate_protocol(protocol)
    capture_count = int(observed_counts.get("capture_manifests", -1))
    if (
        capture_count != len(completed_captures)
        or not 1 <= capture_count < EXPECTED_CAPTURE_COUNT
    ):
        raise ValueError(
            "CSR amendment requires a partial validated capture set"
        )
    for key in ("evaluations", "clean_admission", "summary", "audit", "completion"):
        if int(observed_counts.get(key, -1)) != 0:
            raise ValueError(
                "CSR scheduler amendment requires zero effect outputs"
            )
    if set(implementation) != set(implementation_sha256):
        raise ValueError("CSR scheduler implementation keys differ")
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_csr_caeos_pilot_acceleration_amendment_v1"
        ),
        "state": "frozen_before_parallel_capture_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_protocol_file_sha256": protocol_file_sha256,
        "completed_captures_at_freeze": completed_captures,
        "observed_counts_at_freeze": observed_counts,
        "implementation": implementation,
        "implementation_sha256": implementation_sha256,
        "superseded_resource_policy_only": {
            "outer_workers": 1,
            "no_parallel_csr_training": True,
        },
        "replacement_resource_policy": {
            "maximum_outer_workers": 4,
            "per_capture_trainer_jobs": 8,
            "serial_runner_must_be_stopped": True,
            "resume_canonical_runner_after_capture_completion": True,
        },
        "amendment_scope": {
            "task_matrix_changed": False,
            "capture_command_changed": False,
            "algorithm_or_hyperparameters_changed": False,
            "dataset_or_split_changed": False,
            "selection_or_effect_gate_changed": False,
            "effect_metrics_read": False,
            "maximum_outer_workers": 4,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    protocol = load_json(protocol_path)
    validate_protocol(protocol)
    weight = 0.5
    completed: list[dict[str, Any]] = []
    for manifest_path in sorted(run_root.rglob("capture_manifest.json")):
        manifest = load_json(manifest_path)
        suite = str(manifest.get("task", {}).get("suite", ""))
        scenario = str(manifest.get("task", {}).get("scenario", ""))
        validate_capture(manifest_path, suite, scenario, weight)
        completed.append(
            {
                "path": str(manifest_path.relative_to(project_root)),
                "sha256": file_hash(manifest_path),
                "task": {"suite": suite, "scenario": scenario},
            }
        )
    observed = {
        "capture_manifests": len(completed),
        "evaluations": len(list(run_root.rglob("evaluation.json"))),
        "clean_admission": int(
            (result_root / "clean_admission.json").exists()
        ),
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
        "completion": int(
            (result_root / "pilot_complete").exists()
            or (result_root / "branch_complete").exists()
        ),
    }
    implementation: dict[str, str] = {}
    implementation_sha256: dict[str, str] = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementation[name] = relative
        implementation_sha256[name] = file_hash(project_root / relative)
    value = create_amendment(
        protocol,
        protocol_file_sha256=file_hash(protocol_path),
        completed_captures=completed,
        observed_counts=observed,
        implementation=implementation,
        implementation_sha256=implementation_sha256,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        existing = load_json(args.output)
        if existing != value:
            raise ValueError("existing CSR acceleration amendment differs")
    else:
        args.output.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
