from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

from evaluate_strict_v4_cicids2017_attack_family_gpu_hybrid import (
    prepare_by_seed,
    verify_chain,
)
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    ALERT_VARIANTS,
    OPEN_BUDGETS,
    OPEN_VARIANTS,
    evaluate_configuration,
    selection_key,
)
from strict_v4_cicids2017_attack_family import atomic_json, canonical_hash


ALERT_BUDGETS = (0.04, 0.045, 0.049)


def compact(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "configuration": result["configuration"],
        "macro_mean": result["macro_mean"],
        "gates": result["gates"],
        "scenario_basic_gate_pass_count": result[
            "scenario_basic_gate_pass_count"
        ],
        "scenario_full_gate_pass_count": result[
            "scenario_full_gate_pass_count"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    completion_path = args.completion.resolve()
    protocol, completion = verify_chain(
        args.project_root.resolve(), protocol_path, completion_path
    )
    if protocol["stage"] != "development":
        raise ValueError("alert-budget exploration is development-only")
    prepared_by_seed, source_hashes = prepare_by_seed(protocol, completion)
    development_seed = int(protocol["development_seed"])
    prepared = prepared_by_seed[development_seed]
    candidates = [
        evaluate_configuration(
            prepared,
            {
                "alert_variant": alert_variant,
                "alert_budget": alert_budget,
                "open_variant": open_variant,
                "open_budget": open_budget,
            },
        )
        for alert_variant, alert_budget, open_variant, open_budget in product(
            ALERT_VARIANTS, ALERT_BUDGETS, OPEN_VARIANTS, OPEN_BUDGETS
        )
    ]
    selected = max(candidates, key=selection_key)
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_gpu_alert_budget_exploration_v1",
        "state": "complete_development_only",
        "development_seed": development_seed,
        "candidate_count": len(candidates),
        "alert_budgets": list(ALERT_BUDGETS),
        "selected": selected,
        "macro_basic_gate_candidate_count": sum(
            value["gates"]["basic_warning_95_5_gate"] for value in candidates
        ),
        "macro_full_gate_candidate_count": sum(
            value["gates"]["full_known_unknown_95_5_gate"]
            for value in candidates
        ),
        "best_macro_alert_recall_with_fpr_and_known_gates": compact(
            max(
                (
                    value
                    for value in candidates
                    if value["macro_mean"]["benign_fpr"] < 0.05
                    and value["macro_mean"]["known_attack_type_accuracy"] >= 0.95
                ),
                key=lambda value: (
                    value["macro_mean"]["alert_recall"],
                    value["macro_mean"]["alert_accuracy"],
                ),
            )
        ),
        "best_unknown_alert_recall_with_fpr_and_known_gates": compact(
            max(
                (
                    value
                    for value in candidates
                    if value["macro_mean"]["benign_fpr"] < 0.05
                    and value["macro_mean"]["known_attack_type_accuracy"] >= 0.95
                ),
                key=lambda value: (
                    value["macro_mean"]["unknown_attack_alert_recall"],
                    value["macro_mean"]["alert_recall"],
                ),
            )
        ),
        "source_sha256": source_hashes,
        "binding": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "completion_manifest_sha256": completion["manifest_sha256"],
        },
        "claim_boundary": {
            "development_labels_used_for_exploration": True,
            "fresh_confirmation_results_read": False,
            "not_a_confirmation_result": True,
            "no_new_model_training": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    atomic_json(args.output.resolve(), payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
