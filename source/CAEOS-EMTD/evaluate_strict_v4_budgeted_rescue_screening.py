from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from evaluate_strict_v4_class_conditional_tail_development import (
    evaluate_scenario,
)
from evaluate_strict_v4_hybrid_self_algorithm_development import mean_metrics
from evaluate_strict_v4_neural_empirical_tail_hybrid_qualification import (
    verify_xgboost_source,
)
from evaluate_strict_v4_neural_empirical_tail_hybrid_screening import (
    prepare_scenario,
)
from project_contract import evaluate_delivery_line
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
)


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    metrics = result["overall"]["metrics"]
    return (
        result["all_seed_engineering_passed"],
        result["scenario_pass_counts"]["engineering"],
        result["overall"]["engineering"]["passed"],
        metrics["unknown_attack_alert_recall"],
        metrics["attack_recall"],
        metrics["alert_accuracy"],
        metrics["known_attack_type_accuracy"],
        -metrics["benign_fpr"],
        metrics["unknown_label_recall"],
    )


def evaluate_candidate(
    prepared: dict[str, dict[str, dict[str, Any]]],
    method: dict[str, Any],
) -> dict[str, Any]:
    per_seed = {}
    all_metrics = []
    engineering_count = 0
    paper_count = 0
    for seed, scenarios in prepared.items():
        scenario_contract = {}
        seed_metrics = []
        for scenario, arrays in scenarios.items():
            result = evaluate_scenario(arrays, method)
            scenario_contract[scenario] = result
            seed_metrics.append(result["metrics"])
            all_metrics.append(result["metrics"])
            engineering_count += int(result["engineering"]["passed"])
            paper_count += int(result["paper"]["passed"])
        macro = mean_metrics(seed_metrics)
        per_seed[seed] = {
            "metrics": macro,
            "engineering": evaluate_delivery_line(macro, "engineering"),
            "paper": evaluate_delivery_line(macro, "paper"),
            "scenario_contract": scenario_contract,
        }
    overall = mean_metrics(all_metrics)
    return {
        "method": method,
        "per_seed": per_seed,
        "overall": {
            "metrics": overall,
            "engineering": evaluate_delivery_line(overall, "engineering"),
            "paper": evaluate_delivery_line(overall, "paper"),
        },
        "all_seed_engineering_passed": all(
            value["engineering"]["passed"] for value in per_seed.values()
        ),
        "all_seed_paper_passed": all(
            value["paper"]["passed"] for value in per_seed.values()
        ),
        "scenario_pass_counts": {
            "engineering": engineering_count,
            "paper": paper_count,
            "total": sum(len(value) for value in prepared.values()),
        },
    }


def build_screening(protocol_path: Path) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "screening protocol")
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

    risk_names = tuple(protocol["grid"]["risk_names"])
    prepared = {}
    source_sha256 = {}
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
                neural_dir, xgboost_dir, risk_names
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

    results = []
    for risk_name in risk_names:
        for budgets in protocol["grid"]["budget_pairs"]:
            method = {
                "algorithm": "caeos_budgeted_rescue_alert",
                "alert_score": "budgeted_xgboost_or_knn_rescue",
                "alert_budget": 0.04,
                "primary_alert_budget": budgets["primary_alert_budget"],
                "rescue_alert_budget": budgets["rescue_alert_budget"],
                "risk_name": risk_name,
                "open_risk_name": protocol["grid"]["open_risk_name"],
                "open_score": protocol["grid"]["open_score"],
                "open_budget": protocol["grid"]["open_budget"],
                "condition": "none",
                "minimum_local_reference": 32,
                "local_shrinkage": 64.0,
            }
            results.append(evaluate_candidate(prepared, method))
    selected = max(results, key=selection_key)
    sorted_results = sorted(results, key=selection_key, reverse=True)
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_budgeted_rescue_screening_v1",
        "state": "complete_adaptive_development_screening",
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
        },
        "candidate_count": len(results),
        "selected": selected,
        "top_candidates": [
            {
                key: value[key]
                for key in (
                    "method",
                    "overall",
                    "all_seed_engineering_passed",
                    "all_seed_paper_passed",
                    "scenario_pass_counts",
                )
            }
            for value in sorted_results[:20]
        ],
        "source_sha256": source_sha256,
        "claim_boundary": protocol["claim_boundary"],
    }
    payload["trigger_fresh_unseen_seed_confirmation"] = bool(
        selected["overall"]["engineering"]["passed"]
        and selected["all_seed_engineering_passed"]
    )
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_canonical(args.protocol, "screening protocol")
    if args.output.resolve() != Path(protocol["result_path"]):
        raise ValueError("output does not match frozen result path")
    payload = build_screening(args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "candidate_count": payload["candidate_count"],
                "manifest_sha256": payload["manifest_sha256"],
                "selected_method": payload["selected"]["method"],
                "selected_metrics": payload["selected"]["overall"]["metrics"],
                "trigger_fresh_unseen_seed_confirmation": payload[
                    "trigger_fresh_unseen_seed_confirmation"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
