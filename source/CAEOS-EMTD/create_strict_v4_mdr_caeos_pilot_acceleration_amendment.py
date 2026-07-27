from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import load


EXPECTED_FAILURE = "unexpected MDR pilot runner command"


def create_amendment(
    protocol: Dict[str, Any],
    *,
    protocol_file_sha256: str,
    failure_log_path: str,
    failure_log_sha256: str,
    completed_captures: list[Dict[str, str]],
    observed_counts: Dict[str, int],
    implementation: Dict[str, str],
    implementation_sha256: Dict[str, str],
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR pilot v2 protocol required")
    if not completed_captures or len(completed_captures) >= 42:
        raise ValueError("amendment requires a partial completed capture set")
    if int(observed_counts.get("capture_manifests", -1)) != len(
        completed_captures
    ):
        raise ValueError("completed capture registry/count mismatch")
    for key in ("evaluations", "weight_selection", "summary", "audit"):
        if int(observed_counts.get(key, -1)) != 0:
            raise ValueError("scheduler amendment requires zero effect outputs")
    if set(implementation) != set(implementation_sha256):
        raise ValueError("scheduler implementation keys differ")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_caeos_pilot_acceleration_amendment_v1"
        ),
        "state": "frozen_before_parallel_capture_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_protocol_file_sha256": protocol_file_sha256,
        "failure_evidence": {
            "path": failure_log_path,
            "sha256": failure_log_sha256,
            "expected_error": EXPECTED_FAILURE,
            "failure_is_scheduler_only": True,
        },
        "completed_captures_at_freeze": completed_captures,
        "observed_counts_at_freeze": observed_counts,
        "implementation": implementation,
        "implementation_sha256": implementation_sha256,
        "amendment_scope": {
            "runner_identity_accepts_exact_v2_filename": True,
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
    parser.add_argument("--failure-log", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    failure_log = args.failure_log.resolve()
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    capture_paths = sorted(run_root.rglob("capture_manifest.json"))
    completed = [
        {
            "path": str(path.relative_to(project_root)),
            "sha256": file_hash(path),
        }
        for path in capture_paths
    ]
    observed = {
        "capture_manifests": len(capture_paths),
        "evaluations": len(list(run_root.rglob("evaluation.json"))),
        "weight_selection": int(
            (result_root / "weight_selection.json").exists()
        ),
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
    }
    text = failure_log.read_text(encoding="utf-8")
    if EXPECTED_FAILURE not in text:
        raise ValueError("expected v2 scheduler failure is absent")
    implementation = {}
    implementation_sha256 = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementation[name] = relative
        implementation_sha256[name] = file_hash(project_root / relative)
    value = create_amendment(
        load(protocol_path),
        protocol_file_sha256=file_hash(protocol_path),
        failure_log_path=str(failure_log.relative_to(project_root)),
        failure_log_sha256=file_hash(failure_log),
        completed_captures=completed,
        observed_counts=observed,
        implementation=implementation,
        implementation_sha256=implementation_sha256,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
