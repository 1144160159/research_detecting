from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from evaluate_strict_v4_neural_empirical_tail_hybrid_screening import (
    DEFAULT_RISK_NAMES,
)
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
)


BUDGET_PAIRS = (
    (0.035, 0.005),
    (0.030, 0.010),
    (0.025, 0.015),
    (0.020, 0.020),
    (0.015, 0.025),
    (0.010, 0.030),
)


def build_protocol(
    *,
    project_root: Path,
    parent_protocol_path: Path,
    completion_path: Path,
    output: Path,
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
    if any(abs(primary + rescue - 0.04) > 1e-12 for primary, rescue in BUDGET_PAIRS):
        raise ValueError("all budget pairs must sum to 0.04")
    implementation_names = (
        "evaluate_strict_v4_neural_empirical_tail_hybrid_screening.py",
        "evaluate_strict_v4_class_conditional_tail_development.py",
        "evaluate_strict_v4_budgeted_rescue_screening.py",
    )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_budgeted_rescue_screening_protocol_v1"
        ),
        "state": "frozen_development_grid_before_effect",
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
        "grid": {
            "risk_names": list(DEFAULT_RISK_NAMES),
            "budget_pairs": [
                {
                    "primary_alert_budget": primary,
                    "rescue_alert_budget": rescue,
                }
                for primary, rescue in BUDGET_PAIRS
            ],
            "candidate_count": len(DEFAULT_RISK_NAMES) * len(BUDGET_PAIRS),
            "open_risk_name": "knn",
            "open_score": "global_attack_tail_noisy_or",
            "open_budget": 0.04,
        },
        "implementation_sha256": {
            name: file_hash(project_root / name)
            for name in implementation_names
        },
        "result_path": str(output.parent / "screening.json"),
        "claim_boundary": {
            "qualification_unknown_results_used_for_development_selection": True,
            "current_seeds_are_adaptive_development_only": True,
            "fresh_unseen_seeds_required_for_confirmation": True,
            "thresholds_use_known_only_validation_within_each_candidate": True,
            "candidate_budget_union_upper_bound": 0.04,
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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        project_root=args.project_root,
        parent_protocol_path=args.parent_protocol,
        completion_path=args.completion,
        output=args.output,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "candidate_count": protocol["grid"]["candidate_count"],
                "manifest_sha256": protocol["manifest_sha256"],
                "output": str(args.output.resolve()),
                "state": protocol["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
