from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evaluate_strict_v4_hybrid_self_algorithm_development import (
    evaluate_configuration,
    file_hash,
    gates,
    mean_metrics,
    prepare_scenario,
)


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def load_canonical(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    declared = value.get("manifest_sha256")
    body = dict(value)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")
    return value


def build_confirmation(
    project_root: Path, protocol_path: Path
) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "confirmation protocol")
    for name, expected in protocol["implementation_sha256"].items():
        path = project_root / name
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"implementation hash drifted: {name}")
    selection_source = protocol["selection_source"]
    development_result_path = Path(
        selection_source["development_result_path"]
    )
    development_result = load_canonical(
        development_result_path, "development result"
    )
    if (
        file_hash(development_result_path)
        != selection_source["development_result_file_sha256"]
        or development_result["manifest_sha256"]
        != selection_source["development_result_manifest_sha256"]
        or development_result["selected"]["configuration"]
        != protocol["selected_configuration"]
    ):
        raise ValueError("frozen development selection binding differs")

    pairwise_root = Path(protocol["pairwise_root"])
    xgboost_root = Path(protocol["xgboost_root"])
    by_seed = {}
    all_metrics = []
    observed_sources = {}
    task_count = 0
    for seed in protocol["seeds"]:
        prepared = {}
        seed_sources = {}
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            arrays, sources = prepare_scenario(
                pairwise_root / identity, xgboost_root / identity
            )
            prepared[scenario] = arrays
            seed_sources[scenario] = sources
        if seed_sources != protocol["source_sha256"][str(seed)]:
            raise ValueError(f"fresh source hashes differ for seed {seed}")
        observed_sources[str(seed)] = seed_sources
        result = evaluate_configuration(
            prepared, protocol["selected_configuration"]
        )
        by_seed[str(seed)] = {
            "scenario_count": len(prepared),
            "macro_mean": result["macro_mean"],
            "gates": result["gates"],
            "scenario_basic_gate_pass_count": result[
                "scenario_basic_gate_pass_count"
            ],
            "scenario_full_gate_pass_count": result[
                "scenario_full_gate_pass_count"
            ],
            "per_scenario": result["per_scenario"],
        }
        all_metrics.extend(
            value["metrics"] for value in result["per_scenario"].values()
        )
        task_count += len(prepared)
    if task_count != protocol["expected_task_count"]:
        raise ValueError("fresh hybrid task coverage is incomplete")
    overall = mean_metrics(all_metrics)
    overall_gates = gates(overall)
    all_seed_basic = all(
        value["gates"]["basic_warning_95_5_gate"]
        for value in by_seed.values()
    )
    all_seed_full = all(
        value["gates"]["full_known_unknown_95_5_gate"]
        for value in by_seed.values()
    )
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_hybrid_self_algorithm_confirmation_v1",
        "state": "complete_fresh_read_only_confirmation",
        "algorithm": protocol["algorithm"],
        "selected_configuration": protocol["selected_configuration"],
        "task_count": task_count,
        "expected_task_count": protocol["expected_task_count"],
        "by_seed": by_seed,
        "overall_mean": overall,
        "overall_gates": overall_gates,
        "all_seed_basic_warning_95_5_gate": all_seed_basic,
        "all_seed_full_known_unknown_95_5_gate": all_seed_full,
        "eligible_self_algorithm_basic_claim": all_seed_basic,
        "eligible_self_algorithm_full_claim": all_seed_full,
        "source_sha256": observed_sources,
        "binding": {
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "development_result_manifest_sha256": development_result[
                "manifest_sha256"
            ],
        },
        "claim_boundary": {
            "configuration_was_selected_on_seed7_only": True,
            "fresh_results_selected_nothing": True,
            "single_suite_is_not_comprehensive_sota": True,
            "effect_failure_does_not_invalidate_execution_integrity": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_confirmation(args.project_root, args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": payload["manifest_sha256"],
                "task_count": payload["task_count"],
                "overall_mean": payload["overall_mean"],
                "overall_gates": payload["overall_gates"],
                "all_seed_basic_warning_95_5_gate": payload[
                    "all_seed_basic_warning_95_5_gate"
                ],
                "all_seed_full_known_unknown_95_5_gate": payload[
                    "all_seed_full_known_unknown_95_5_gate"
                ],
                "eligible_self_algorithm_full_claim": payload[
                    "eligible_self_algorithm_full_claim"
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
