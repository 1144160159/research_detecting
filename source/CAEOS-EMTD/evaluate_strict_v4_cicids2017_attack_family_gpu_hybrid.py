from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

from create_strict_v4_cicids2017_attack_family_gpu_protocol import (
    DEVELOPMENT_STATE,
)
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    ALERT_BUDGETS,
    ALERT_VARIANTS,
    OPEN_BUDGETS,
    OPEN_VARIANTS,
    configuration_key,
    evaluate_configuration,
    gates,
    mean_metrics,
    prepare_scenario,
    selection_key,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def verify_chain(
    project_root: Path,
    protocol_path: Path,
    completion_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = load_canonical(protocol_path, "GPU attack-family protocol")
    completion = load_canonical(
        completion_path, "GPU attack-family matrix completion"
    )
    if (
        completion.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or completion.get("state")
        != "complete_heterogeneous_gpu_execution"
        or completion.get("complete_task_count")
        != protocol["expected_task_count"]
        or not completion.get("gpu_execution", {}).get("all_tasks_passed")
        or completion.get("gpu_execution", {}).get("passing_task_count")
        != protocol["expected_task_count"]
    ):
        raise ValueError("GPU matrix completion does not bind the protocol")
    expected = protocol["implementation_sha256"][
        "evaluate_strict_v4_cicids2017_attack_family_gpu_hybrid.py"
    ]
    if file_hash(Path(__file__).resolve()) != expected:
        raise ValueError("GPU attack-family evaluator hash drifted")
    for identity, task in completion["task_artifacts"].items():
        for name, expected_hash in task["pairwise_sha256"].items():
            if file_hash(Path(task["pairwise_dir"]) / name) != expected_hash:
                raise ValueError(f"Pairwise artifact drifted: {identity}/{name}")
        for name, expected_hash in task["xgboost_sha256"].items():
            if file_hash(Path(task["xgboost_dir"]) / name) != expected_hash:
                raise ValueError(f"XGBoost artifact drifted: {identity}/{name}")
        evidence = load_canonical(
            Path(task["xgboost_dir"]) / "gpu_execution.json",
            f"GPU execution evidence {identity}",
        )
        if (
            evidence["manifest_sha256"]
            != task["gpu_execution"]["manifest_sha256"]
            or not evidence.get("passes")
            or evidence.get("gpu_identity", {}).get("uuid")
            != protocol["xgboost_known_expert"]["required_gpu_uuid"]
        ):
            raise ValueError(f"GPU execution evidence drifted: {identity}")
    return protocol, completion


def prepare_by_seed(
    protocol: dict[str, Any], completion: dict[str, Any]
) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    prepared_by_seed: dict[int, dict[str, Any]] = {}
    source_hashes: dict[str, Any] = {}
    for seed in protocol["seeds"]:
        prepared: dict[str, Any] = {}
        seed_sources: dict[str, Any] = {}
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            task = completion["task_artifacts"][identity]
            arrays, sources = prepare_scenario(
                Path(task["pairwise_dir"]), Path(task["xgboost_dir"])
            )
            prepared[scenario] = arrays
            seed_sources[scenario] = sources
        prepared_by_seed[int(seed)] = prepared
        source_hashes[str(seed)] = seed_sources
    return prepared_by_seed, source_hashes


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
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


def gpu_summary(completion: dict[str, Any]) -> dict[str, Any]:
    task_evidence = {
        identity: task["gpu_execution"]
        for identity, task in completion["task_artifacts"].items()
    }
    return {
        **completion["gpu_execution"],
        "all_tasks_passed": all(
            bool(value["passes"]) for value in task_evidence.values()
        ),
        "task_evidence": dict(sorted(task_evidence.items())),
    }


def evaluate_development(
    protocol: dict[str, Any],
    completion: dict[str, Any],
    prepared_by_seed: dict[int, dict[str, Any]],
    source_hashes: dict[str, Any],
    protocol_path: Path,
    completion_path: Path,
) -> dict[str, Any]:
    development_seed = int(protocol["development_seed"])
    if set(prepared_by_seed) != {development_seed}:
        raise ValueError("development must use the frozen development seed only")
    candidates = []
    for alert_variant, alert_budget, open_variant, open_budget in product(
        ALERT_VARIANTS, ALERT_BUDGETS, OPEN_VARIANTS, OPEN_BUDGETS
    ):
        candidates.append(
            evaluate_configuration(
                prepared_by_seed[development_seed],
                {
                    "alert_variant": alert_variant,
                    "alert_budget": alert_budget,
                    "open_variant": open_variant,
                    "open_budget": open_budget,
                },
            )
        )
    if len(candidates) != protocol["hybrid_candidate_space"]["candidate_count"]:
        raise ValueError("candidate count differs from frozen protocol")
    selected = max(candidates, key=selection_key)
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_gpu_hybrid_development_v1",
        "state": DEVELOPMENT_STATE,
        "algorithm": (
            "GPU Attack-Family Empirical-Tail Hybrid CAEOS: CUDA XGBoost "
            "known-family expert plus CPU Pairwise-CAEOS conflict and "
            "uncertainty open-set head"
        ),
        "development_seed": development_seed,
        "selected": selected,
        "candidate_count": len(candidates),
        "candidate_summary": {
            configuration_key(value["configuration"]): compact_result(value)
            for value in candidates
        },
        "gpu_execution": gpu_summary(completion),
        "source_sha256": source_hashes,
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "completion_path": str(completion_path),
            "completion_file_sha256": file_hash(completion_path),
            "completion_manifest_sha256": completion["manifest_sha256"],
        },
        "selection_rule": {
            "single_global_configuration_across_7_attack_families": True,
            "order": [
                "full_known_unknown_95_5_gate",
                "basic_warning_95_5_gate",
                "minimum_total_target_deficit",
                "minimum_target_margin",
                "unknown_attack_family_recall",
                "known_attack_family_accuracy",
                "alert_accuracy",
                "lower_benign_fpr",
            ],
        },
        "claim_boundary": {
            **protocol["claim_boundary"],
            "authorized_level": "attack_family",
            "development_labels_used_for_selection": True,
            "development_result_is_not_confirmation": True,
            "fresh_confirmation_results_were_not_read": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def evaluate_confirmation(
    protocol: dict[str, Any],
    completion: dict[str, Any],
    prepared_by_seed: dict[int, dict[str, Any]],
    source_hashes: dict[str, Any],
    protocol_path: Path,
    completion_path: Path,
) -> dict[str, Any]:
    configuration = protocol.get("selected_configuration")
    if not isinstance(configuration, dict):
        raise ValueError("confirmation configuration was not frozen")
    per_seed: dict[str, Any] = {}
    for seed, prepared in sorted(prepared_by_seed.items()):
        per_seed[str(seed)] = evaluate_configuration(prepared, configuration)
    aggregate_metrics = mean_metrics(
        value["macro_mean"] for value in per_seed.values()
    )
    aggregate_gates = gates(aggregate_metrics)
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_gpu_hybrid_confirmation_v1",
        "state": "complete_fresh_attack_family_gpu_confirmation",
        "algorithm": (
            "GPU Attack-Family Empirical-Tail Hybrid CAEOS: CUDA XGBoost "
            "known-family expert plus CPU Pairwise-CAEOS conflict and "
            "uncertainty open-set head"
        ),
        "selected_configuration": configuration,
        "seeds": list(protocol["seeds"]),
        "per_seed": per_seed,
        "aggregate_macro_mean": aggregate_metrics,
        "aggregate_gates": aggregate_gates,
        "all_seed_basic_warning_95_5_gate": all(
            value["gates"]["basic_warning_95_5_gate"]
            for value in per_seed.values()
        ),
        "all_seed_full_known_unknown_95_5_gate": all(
            value["gates"]["full_known_unknown_95_5_gate"]
            for value in per_seed.values()
        ),
        "gpu_execution": gpu_summary(completion),
        "source_sha256": source_hashes,
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "completion_path": str(completion_path),
            "completion_file_sha256": file_hash(completion_path),
            "completion_manifest_sha256": completion["manifest_sha256"],
            "selection_source": protocol["selection_source"],
        },
        "claim_boundary": {
            **protocol["claim_boundary"],
            "authorized_level": "attack_family",
            "fresh_test_or_unknown_labels_used_for_selection": False,
            "full_self_algorithm_claim_requires_all_seed_full_gate": True,
        },
    }
    payload["eligible_self_algorithm_attack_family_claim"] = payload[
        "all_seed_full_known_unknown_95_5_gate"
    ]
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    completion_path = args.completion.resolve()
    protocol, completion = verify_chain(
        project_root, protocol_path, completion_path
    )
    prepared_by_seed, source_hashes = prepare_by_seed(protocol, completion)
    if protocol["stage"] == "development":
        payload = evaluate_development(
            protocol,
            completion,
            prepared_by_seed,
            source_hashes,
            protocol_path,
            completion_path,
        )
    else:
        payload = evaluate_confirmation(
            protocol,
            completion,
            prepared_by_seed,
            source_hashes,
            protocol_path,
            completion_path,
        )
    atomic_json(args.output.resolve(), payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
