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


ALERT_BUDGETS = tuple(value / 1000.0 for value in range(40, 50))


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
    implementation_names = (
        "evaluate_strict_v4_neural_empirical_tail_hybrid_screening.py",
        "evaluate_strict_v4_class_conditional_tail_development.py",
        "evaluate_strict_v4_budgeted_rescue_screening.py",
        "evaluate_strict_v4_alert_budget_frontier.py",
    )
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_alert_budget_frontier_protocol_v1",
        "state": "frozen_frontier_before_effect",
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
        "frontier": {
            "alert_budgets": list(ALERT_BUDGETS),
            "alert_score": "xgboost_attack_probability",
            "open_risk_name": "knn",
            "open_score": "global_attack_tail_noisy_or",
            "open_budget": 0.04,
            "test_fpr_constraint": 0.05,
        },
        "implementation_sha256": {
            name: file_hash(project_root / name)
            for name in implementation_names
        },
        "result_path": str(output.parent / "frontier.json"),
        "claim_boundary": {
            "qualification_unknown_results_used_for_frontier_diagnosis": True,
            "frontier_is_adaptive_development_only": True,
            "thresholds_use_known_only_validation": True,
            "frontier_cannot_authorize_confirmation_claim": True,
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
                "budget_count": len(protocol["frontier"]["alert_budgets"]),
                "manifest_sha256": protocol["manifest_sha256"],
                "output": str(args.output.resolve()),
                "state": protocol["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
