from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import load


def revise_protocol(
    prior: Dict[str, Any],
    *,
    prior_protocol_file_sha256: str,
    failure_log_path: str,
    failure_log_sha256: str,
    implementation: Dict[str, str],
    implementation_sha256: Dict[str, str],
    observed_counts: Dict[str, int],
) -> Dict[str, Any]:
    if (
        prior.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v1"
        or prior.get("manifest_sha256") != canonical_hash(prior)
    ):
        raise ValueError("canonical MDR pilot v1 protocol required")
    if any(int(value) != 0 for value in observed_counts.values()):
        raise ValueError("MDR pilot v2 requires a fresh zero-output root")
    if set(implementation) != set(implementation_sha256):
        raise ValueError("MDR pilot v2 implementation path/hash keys differ")
    value = {
        key: entry
        for key, entry in prior.items()
        if key not in {"manifest_sha256", "status", "implementation",
                       "implementation_sha256", "output_counts_at_freeze"}
    }
    value.update(
        {
            "schema_version": (
                "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
            ),
            "status": "revised_before_any_complete_pilot_result",
            "implementation": implementation,
            "implementation_sha256": implementation_sha256,
            "output_counts_at_freeze": observed_counts,
            "protocol_revision": {
                "supersedes_schema_version": prior["schema_version"],
                "supersedes_manifest_sha256": prior["manifest_sha256"],
                "supersedes_protocol_file_sha256": (
                    prior_protocol_file_sha256
                ),
                "reason": (
                    "v1 dynamic runpy module name was not importable during "
                    "joblib runtime serialization"
                ),
                "failure_log_path": failure_log_path,
                "failure_log_sha256": failure_log_sha256,
                "complete_capture_count_before_revision": 0,
                "evaluation_count_before_revision": 0,
                "algorithm_formula_changed": False,
                "dataset_split_changed": False,
                "selection_rule_changed": False,
                "fresh_run_and_result_roots_required": True,
            },
        }
    )
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-protocol", type=Path, required=True)
    parser.add_argument("--failure-log", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    prior_path = args.prior_protocol.resolve()
    failure_log = args.failure_log.resolve()
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    implementation = {}
    implementation_sha256 = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementation[name] = relative
        implementation_sha256[name] = file_hash(project_root / relative)
    observed = {
        "capture_manifests": (
            sum(1 for _ in run_root.rglob("capture_manifest.json"))
            if run_root.exists()
            else 0
        ),
        "evaluations": (
            sum(1 for _ in run_root.rglob("evaluation.json"))
            if run_root.exists()
            else 0
        ),
        "weight_selection": int(
            (result_root / "weight_selection.json").exists()
        ),
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
    }
    value = revise_protocol(
        load(prior_path),
        prior_protocol_file_sha256=file_hash(prior_path),
        failure_log_path=str(failure_log.relative_to(project_root)),
        failure_log_sha256=file_hash(failure_log),
        implementation=implementation,
        implementation_sha256=implementation_sha256,
        observed_counts=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
