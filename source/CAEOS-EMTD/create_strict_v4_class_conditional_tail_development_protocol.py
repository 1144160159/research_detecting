from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
)


def build_protocol(
    *,
    project_root: Path,
    parent_protocol_path: Path,
    completion_path: Path,
    output: Path,
    candidate: str = "conditional_open",
) -> dict[str, Any]:
    project_root = project_root.resolve()
    parent_protocol_path = parent_protocol_path.resolve()
    completion_path = completion_path.resolve()
    output = output.resolve()
    parent = load_canonical(parent_protocol_path, "parent protocol")
    completion = load_canonical(completion_path, "completion")
    expected = int(parent["expected_task_count"])
    if (
        completion.get("task_coverage", {}).get("complete") is not True
        or len(completion.get("neural_task_artifacts", {})) != expected
        or len(completion.get("xgboost_task_artifacts", {})) != expected
        or completion.get("all_tasks_confirmed_cuda", {}).get("neural")
        is not True
        or completion.get("all_tasks_confirmed_cuda", {}).get("xgboost")
        is not True
    ):
        raise ValueError("complete CUDA source artifacts are required")
    if (
        completion.get("protocol", {}).get("manifest_sha256")
        != parent["manifest_sha256"]
    ):
        raise ValueError("completion is not bound to parent protocol")
    if candidate not in {
        "conditional_open",
        "conditional_alert",
        "budgeted_dual_alert",
    }:
        raise ValueError(f"unsupported candidate: {candidate}")
    if candidate == "conditional_open":
        algorithm = "caeos_class_conditional_tail"
        alert_score = "xgboost_attack_probability"
        open_score = "class_conditional_tail_noisy_or"
    elif candidate == "conditional_alert":
        algorithm = "caeos_class_conditional_alert_tail"
        alert_score = "class_conditional_benign_tail_noisy_or"
        open_score = "global_attack_tail_noisy_or"
    else:
        algorithm = "caeos_budgeted_dual_alert"
        alert_score = "budgeted_xgboost_or_knn_rescue"
        open_score = "global_attack_tail_noisy_or"
    implementation_names = (
        "evaluate_strict_v4_neural_empirical_tail_hybrid_screening.py",
        "evaluate_strict_v4_class_conditional_tail_development.py",
    )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_class_conditional_tail_development_protocol_v1"
        ),
        "state": "frozen_single_candidate_before_development_effect",
        "parent_protocol": {
            "path": str(parent_protocol_path),
            "file_sha256": file_hash(parent_protocol_path),
            "manifest_sha256": parent["manifest_sha256"],
        },
        "source_completion": {
            "path": str(completion_path),
            "file_sha256": file_hash(completion_path),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "seeds": parent["seeds"],
        "scenarios": parent["scenarios"],
        "expected_task_count": expected,
        "method": {
            "algorithm": algorithm,
            "alert_score": alert_score,
            "alert_budget": 0.04,
            "primary_alert_budget": (
                0.03 if candidate == "budgeted_dual_alert" else None
            ),
            "rescue_alert_budget": (
                0.01 if candidate == "budgeted_dual_alert" else None
            ),
            "risk_name": "knn",
            "open_score": open_score,
            "open_budget": 0.04,
            "condition": "xgboost_predicted_attack_class",
            "minimum_local_reference": 32,
            "local_shrinkage": 64.0,
            "fallback": "global_known_attack_empirical_cdf",
        },
        "implementation_sha256": {
            name: file_hash(project_root / name)
            for name in implementation_names
        },
        "result_path": str(
            output.parent / "class_conditional_tail_development.json"
        ),
        "claim_boundary": {
            "single_candidate_no_grid_search": True,
            "thresholds_use_known_only_validation": True,
            "qualification_unknown_results_informed_method_design": True,
            "current_seeds_are_adaptive_development_only": True,
            "fresh_unseen_seeds_required_for_confirmation": True,
            "eligible_for_paper_effect_claim": False,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument(
        "--candidate",
        choices=(
            "conditional_open",
            "conditional_alert",
            "budgeted_dual_alert",
        ),
        default="conditional_open",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        project_root=args.project_root,
        parent_protocol_path=args.parent_protocol,
        completion_path=args.completion,
        output=args.output,
        candidate=args.candidate,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": protocol["manifest_sha256"],
                "output": str(args.output.resolve()),
                "state": protocol["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
