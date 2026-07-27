from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def revise(
    v3: Dict[str, Any],
    *,
    v3_file_sha256: str,
    implementation_sha256: Dict[str, str],
    capture_count: int,
    evaluation_count: int,
) -> Dict[str, Any]:
    if (
        v3.get("schema_version") != "strict_v4_csr_caeos_design_v3"
        or v3.get("manifest_sha256") != canonical_hash(v3)
    ):
        raise ValueError("canonical CSR v3 design required")
    if int(capture_count) != 0 or int(evaluation_count) != 0:
        raise ValueError("CSR v4 requires zero capture and evaluation results")
    required = {
        "capture",
        "evaluator",
        "summarizer",
        "auditor",
        "design_creator_v4",
        "summary_test",
    }
    if set(implementation_sha256) != required:
        raise ValueError("complete CSR pilot analysis binding required")
    value = {
        key: item
        for key, item in v3.items()
        if key not in {
            "schema_version",
            "manifest_sha256",
            "implementation_sha256",
            "execution_boundary",
            "revision",
        }
    }
    mechanism = dict(value["mechanism"])
    mechanism.update(
        {
            "training_sample_fraction": 0.25,
            "structured_family_severities": {
                "modality_missing": 1.0,
                "field_missing": 0.3,
                "row_missing": 0.3,
                "feature_shuffle": 0.3,
                "gaussian_drift": 0.5,
            },
            "legacy_health_quantile_argument": {
                "value": 0.99,
                "used_by_csr_calibration": False,
                "reason": (
                    "trainer wrapper compatibility only; CSR uses the "
                    "calibration-partition maximum"
                ),
            },
        }
    )
    value["mechanism"] = mechanism
    value.update(
        {
            "schema_version": "strict_v4_csr_caeos_design_v4",
            "status": "frozen_before_candidate_results",
            "supersedes_design_manifest_sha256": v3["manifest_sha256"],
            "supersedes_design_file_sha256": v3_file_sha256,
            "revision": {
                "reason": (
                    "freeze the structured sample fraction and bind pilot "
                    "summary and audit implementations"
                ),
                "algorithm_equations_changed": False,
                "scenarios_seeds_weight_gates_or_corruption_changed": False,
                "training_configuration_completed_before_results": True,
                "capture_results_observed": 0,
                "evaluation_results_observed": 0,
            },
            "implementation_sha256": implementation_sha256,
            "execution_boundary": {
                "execution_admitted": False,
                "missing_before_execution": [
                    "canonical pilot execution protocol",
                    "resumable runner",
                    "resource-idle watcher",
                ],
                "no_training_started_by_design_freeze": True,
            },
            "candidate_result_count_at_freeze": 0,
        }
    )
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v3-design", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    captures = (
        sum(1 for _ in run_root.rglob("capture_manifest.json"))
        if run_root.exists()
        else 0
    )
    evaluations = (
        sum(1 for _ in run_root.rglob("evaluation.json"))
        if run_root.exists()
        else 0
    ) + (
        sum(1 for _ in result_root.rglob("evaluation.json"))
        if result_root.exists()
        else 0
    )
    project_root = args.project_root.resolve()
    implementations = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementations[name] = file_hash(project_root / relative)
    value = revise(
        load_json(args.v3_design),
        v3_file_sha256=file_hash(args.v3_design),
        implementation_sha256=implementations,
        capture_count=captures,
        evaluation_count=evaluations,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
