from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from evaluate_strict_v4_budgeted_rescue_screening import evaluate_candidate
from evaluate_strict_v4_neural_empirical_tail_hybrid_qualification import (
    verify_xgboost_source,
)
from evaluate_strict_v4_neural_empirical_tail_hybrid_screening import (
    prepare_scenario,
)
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
)


def build_frontier(protocol_path: Path) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "frontier protocol")
    parent_path = Path(protocol["parent_protocol"]["path"])
    completion_path = Path(protocol["source_completion"]["path"])
    parent = load_canonical(parent_path, "parent protocol")
    completion = load_canonical(completion_path, "source completion")
    if file_hash(parent_path) != protocol["parent_protocol"]["file_sha256"]:
        raise ValueError("parent protocol hash mismatch")
    if (
        file_hash(completion_path)
        != protocol["source_completion"]["file_sha256"]
    ):
        raise ValueError("source completion hash mismatch")
    project_root = Path(__file__).resolve().parent
    for name, expected_hash in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected_hash:
            raise ValueError(f"implementation hash mismatch: {name}")

    prepared = {}
    source_sha256 = {}
    risk_name = protocol["frontier"]["open_risk_name"]
    for seed in protocol["seeds"]:
        seed_prepared = {}
        seed_sources = {}
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            neural_artifact = completion["neural_task_artifacts"][identity]
            neural_dir = Path(neural_artifact["task_dir"])
            xgboost_dir = Path(parent["xgboost_root"]) / identity
            verify_xgboost_source(
                completion,
                identity=identity,
                task_dir=xgboost_dir,
            )
            arrays, hashes = prepare_scenario(
                neural_dir, xgboost_dir, (risk_name,)
            )
            if (
                file_hash(neural_dir / "metrics.json")
                != neural_artifact["metrics_sha256"]
                or file_hash(neural_dir / "scores.npz")
                != neural_artifact["scores_sha256"]
            ):
                raise ValueError(f"neural source hash mismatch: {identity}")
            seed_prepared[scenario] = arrays
            seed_sources[scenario] = hashes
        prepared[str(seed)] = seed_prepared
        source_sha256[str(seed)] = seed_sources

    records = []
    for alert_budget in protocol["frontier"]["alert_budgets"]:
        method = {
            "algorithm": "caeos_xgboost_alert_frontier",
            "alert_score": protocol["frontier"]["alert_score"],
            "alert_budget": alert_budget,
            "primary_alert_budget": None,
            "rescue_alert_budget": None,
            "risk_name": risk_name,
            "open_risk_name": risk_name,
            "open_score": protocol["frontier"]["open_score"],
            "open_budget": protocol["frontier"]["open_budget"],
            "condition": "none",
            "minimum_local_reference": 32,
            "local_shrinkage": 64.0,
        }
        records.append(evaluate_candidate(prepared, method))
    fpr_constraint = float(protocol["frontier"]["test_fpr_constraint"])
    feasible = [
        result
        for result in records
        if result["overall"]["metrics"]["benign_fpr"] < fpr_constraint
    ]
    best_feasible = (
        max(
            feasible,
            key=lambda result: (
                result["overall"]["metrics"][
                    "unknown_attack_alert_recall"
                ],
                result["scenario_pass_counts"]["engineering"],
                result["overall"]["metrics"]["attack_recall"],
            ),
        )
        if feasible
        else None
    )
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_alert_budget_frontier_v1",
        "state": "complete_adaptive_frontier_diagnostic",
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
        },
        "records": records,
        "feasible_budget_count": len(feasible),
        "best_feasible": best_feasible,
        "target_reachable_under_test_fpr_constraint": bool(
            best_feasible is not None
            and best_feasible["overall"]["metrics"][
                "unknown_attack_alert_recall"
            ]
            >= 0.95
        ),
        "source_sha256": source_sha256,
        "claim_boundary": protocol["claim_boundary"],
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_canonical(args.protocol, "frontier protocol")
    if args.output.resolve() != Path(protocol["result_path"]):
        raise ValueError("output does not match frozen result path")
    payload = build_frontier(args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "best_feasible_metrics": (
                    payload["best_feasible"]["overall"]["metrics"]
                    if payload["best_feasible"] is not None
                    else None
                ),
                "feasible_budget_count": payload["feasible_budget_count"],
                "manifest_sha256": payload["manifest_sha256"],
                "target_reachable_under_test_fpr_constraint": payload[
                    "target_reachable_under_test_fpr_constraint"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
