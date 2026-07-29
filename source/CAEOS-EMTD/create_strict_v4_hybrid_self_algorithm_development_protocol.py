from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evaluate_strict_v4_hybrid_self_algorithm_development import (
    ALERT_BUDGETS,
    ALERT_VARIANTS,
    OPEN_BUDGETS,
    OPEN_VARIANTS,
)


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_protocol(
    project_root: Path, pairwise_root: Path, xgboost_root: Path
) -> dict[str, Any]:
    project_root = project_root.resolve()
    pairwise_root = pairwise_root.resolve()
    xgboost_root = xgboost_root.resolve()
    pairwise_dirs = sorted(
        path.parent for path in pairwise_root.glob("*/metrics.json")
    )
    scenarios = [
        path.name.removesuffix("_seed7") for path in pairwise_dirs
    ]
    if len(scenarios) != 14 or len(set(scenarios)) != 14:
        raise ValueError("exactly 14 unique seed7 scenarios are required")
    source_sha256 = {}
    for scenario, pairwise_dir in zip(scenarios, pairwise_dirs):
        xgboost_dir = xgboost_root / f"{scenario}_seed7"
        paths = {
            "pairwise_metrics": pairwise_dir / "metrics.json",
            "pairwise_scores": pairwise_dir / "scores.npz",
            "pairwise_evidence": pairwise_dir / "evidence_package.npz",
            "xgboost_metrics": xgboost_dir / "metrics.json",
            "xgboost_scores": xgboost_dir / "scores.npz",
        }
        for path in paths.values():
            if not path.is_file():
                raise FileNotFoundError(path)
        source_sha256[scenario] = {
            name: file_hash(path) for name, path in paths.items()
        }
    evaluator = (
        project_root / "evaluate_strict_v4_hybrid_self_algorithm_development.py"
    )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_hybrid_self_algorithm_development_protocol_v1"
        ),
        "state": "frozen_zero_result_seed7_development",
        "algorithm": (
            "Empirical-Tail Hybrid CAEOS: XGBoost known expert plus "
            "Pairwise-CAEOS conflict and uncertainty open-set head"
        ),
        "seed": 7,
        "scenarios": scenarios,
        "expected_scenario_count": 14,
        "pairwise_root": str(pairwise_root),
        "xgboost_root": str(xgboost_root),
        "candidate_space": {
            "alert_variants": list(ALERT_VARIANTS),
            "alert_budgets": list(ALERT_BUDGETS),
            "open_variants": list(OPEN_VARIANTS),
            "open_budgets": list(OPEN_BUDGETS),
            "candidate_count": (
                len(ALERT_VARIANTS)
                * len(ALERT_BUDGETS)
                * len(OPEN_VARIANTS)
                * len(OPEN_BUDGETS)
            ),
        },
        "selection_rule": [
            "full_known_unknown_95_5_gate",
            "basic_warning_95_5_gate",
            "minimum_total_target_deficit",
            "minimum_target_margin",
            "unknown_attack_recall",
            "known_attack_type_accuracy",
            "alert_accuracy",
            "lower_benign_fpr",
        ],
        "source_sha256": source_sha256,
        "implementation_sha256": {
            evaluator.name: file_hash(evaluator),
        },
        "claim_boundary": {
            "seed7_test_and_unknown_labels_may_select_development_configuration": True,
            "fresh_907_911_919_may_select_nothing": True,
            "development_result_cannot_establish_target_or_sota": True,
            "one_global_configuration_for_all_scenarios": True,
        },
        "formal_output_counts_at_freeze": {
            "development_result": 0,
            "fresh_confirmation": 0,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--pairwise-root", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        args.project_root, args.pairwise_root, args.xgboost_root
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
