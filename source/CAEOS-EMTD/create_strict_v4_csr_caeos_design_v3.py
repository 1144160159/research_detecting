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
    v2: Dict[str, Any],
    *,
    v2_file_sha256: str,
    implementation_sha256: Dict[str, str],
    capture_count: int,
    evaluation_count: int,
) -> Dict[str, Any]:
    if (
        v2.get("schema_version") != "strict_v4_csr_caeos_design_v2"
        or v2.get("manifest_sha256") != canonical_hash(v2)
        or v2.get("candidate_result_count_at_freeze") != 0
    ):
        raise ValueError("canonical zero-result CSR v2 design required")
    if int(capture_count) != 0 or int(evaluation_count) != 0:
        raise ValueError("CSR v3 requires zero capture and evaluation results")
    required = {
        "routing_module",
        "runtime_module",
        "capture",
        "evaluator",
        "design_creator_v3",
        "capture_test",
        "evaluator_test",
    }
    if set(implementation_sha256) != required:
        raise ValueError("complete CSR capture/evaluator binding required")
    value = {
        key: item
        for key, item in v2.items()
        if key not in {
            "schema_version",
            "manifest_sha256",
            "implementation_sha256",
            "execution_boundary",
            "revision",
        }
    }
    development = dict(value["development"])
    development["known_validation_partition"] = {
        "rule": "even_indices_calibration_odd_indices_safety",
        "partition_uses_labels": False,
        "calibration_fits_health_and_risk_maps": True,
        "safety_labels_used_for_clean_gate_only": True,
    }
    development["clean_gate"] = {
        "prediction_array_equal_pairwise": True,
        "probability_max_absolute_difference": 0.0,
        "inactive_nonmissing_risk_max_absolute_difference": 1e-12,
        "conflict_or_disagreement_activation_on_calibration": 0.0,
        "safety_nonmissing_activation_rate_one_sided_95pct_upper_maximum": (
            0.01
        ),
        "known_macro_f1_mean_degradation_maximum": 0.0,
        "known_macro_f1_worst_degradation_maximum": 0.0,
    }
    value["development"] = development
    value.update(
        {
            "schema_version": "strict_v4_csr_caeos_design_v3",
            "status": "frozen_before_candidate_results",
            "supersedes_design_manifest_sha256": v2["manifest_sha256"],
            "supersedes_design_file_sha256": v2_file_sha256,
            "revision": {
                "reason": (
                    "clarify the clean risk gate as inactive exact fallback "
                    "plus a finite-sample safety activation bound"
                ),
                "algorithm_formula_changed": False,
                "scenarios_seeds_weight_or_robustness_gate_changed": False,
                "clean_gate_semantics_changed_before_results": True,
                "capture_results_observed": 0,
                "evaluation_results_observed": 0,
            },
            "implementation_sha256": implementation_sha256,
            "execution_boundary": {
                "execution_admitted": False,
                "missing_before_execution": [
                    "canonical pilot execution protocol",
                    "resumable runner",
                    "independent summarizer and auditor",
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
    parser.add_argument("--v2-design", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
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
    implementations = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementations[name] = file_hash(project_root / relative)
    value = revise(
        load_json(args.v2_design),
        v2_file_sha256=file_hash(args.v2_design),
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
