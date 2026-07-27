from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


LATENCY_METRICS = (
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
)
METHODS = (
    "original_mdr_caeos_v1",
    "mdr_evidence_reuse_v1",
    "embedded_caeos_pairwise",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def bootstrap_mean(
    values: Iterable[float], *, seed: int, repetitions: int
) -> Dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if (
        array.ndim != 1
        or not len(array)
        or not np.isfinite(array).all()
        or int(repetitions) < 1
    ):
        raise ValueError("finite nonempty bootstrap values required")
    rng = np.random.default_rng(int(seed))
    sampled = array[
        rng.integers(0, len(array), size=(int(repetitions), len(array)))
    ].mean(axis=1)
    return {
        "n": int(len(array)),
        "mean": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(sampled, 0.025)),
            float(np.quantile(sampled, 0.975)),
        ],
    }


def positive_ratio(numerator: float, denominator: float) -> float:
    numerator = float(numerator)
    denominator = float(denominator)
    if (
        not np.isfinite(numerator)
        or not np.isfinite(denominator)
        or numerator <= 0.0
        or denominator <= 0.0
    ):
        raise ValueError("positive finite ratio operands required")
    return numerator / denominator


def source_identity(record: Dict[str, Any]) -> tuple[str, str, int]:
    source = record["source"]
    return (
        str(source["suite"]),
        str(source["scenario"]),
        int(source["training_seed"]),
    )


def expected_source(source: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "suite": str(source["suite"]),
        "scenario": str(source["scenario"]),
        "training_seed": int(source["training_seed"]),
        "corruption_seed": int(source["corruption_seed"]),
        "capture_manifest_file_sha256": source[
            "capture_manifest_file_sha256"
        ],
        "runtime_artifact_sha256": source["runtime_artifact_sha256"],
        "evaluation_inputs_sha256": source["evaluation_inputs_sha256"],
    }


def validate_equivalence(
    record: Dict[str, Any], protocol: Dict[str, Any]
) -> int:
    block = record.get("equivalence", {})
    conditions = block.get("conditions", [])
    expected = set(map(str, protocol["conditions"]))
    tolerance = float(
        protocol["equivalence"][
            "probability_risk_and_diagnostics_max_absolute_tolerance"
        ]
    )
    if (
        int(block.get("condition_count", -1)) != len(expected)
        or len(conditions) != len(expected)
        or {str(item.get("condition")) for item in conditions} != expected
        or block.get("all_direct_pass") is not True
        or block.get("all_serialization_pass") is not True
        or block.get("labels_loaded") is not False
    ):
        raise ValueError("condition equivalence coverage mismatch")
    for item in conditions:
        for name in ("direct_equivalence", "serialization_equivalence"):
            comparison = item.get(name, {})
            discrete = comparison.get("discrete_array_equal", {})
            numeric = comparison.get(
                "numeric_max_absolute_difference", {}
            )
            if (
                comparison.get("passes") is not True
                or not discrete
                or not all(value is True for value in discrete.values())
                or not numeric
                or not all(
                    np.isfinite(float(value))
                    and float(value) <= tolerance
                    for value in numeric.values()
                )
                or float(comparison.get("absolute_tolerance", -1.0))
                != tolerance
            ):
                raise ValueError("formal MDR equivalence check failed")
    return len(conditions)


def aggregate_captures(
    records: list[Dict[str, Any]], protocol: Dict[str, Any]
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_evidence_reuse_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(records) != 306
    ):
        raise ValueError("canonical protocol and 306 captures required")
    expected = {
        (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        ): source
        for source in protocol["sources"]
    }
    if len(expected) != 306:
        raise ValueError("protocol source identity coverage mismatch")
    by_scenario: Dict[tuple[str, str], list[Dict[str, Any]]] = defaultdict(
        list
    )
    capture_ratios = []
    contexts = []
    seen = set()
    condition_count = 0
    for record in records:
        if (
            record.get("schema_version")
            != "strict_v4_mdr_evidence_reuse_capture_v1"
            or record.get("state") != "complete"
            or record.get("manifest_sha256") != canonical_hash(record)
            or record.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or record.get("exclusive_machine_preflight_marker") != "passed"
            or record.get("unknown_or_test_labels_used") is not False
            or record.get("fit_cost", {}).get(
                "unchanged_by_inference_optimization"
            )
            is not True
        ):
            raise ValueError("invalid MDR evidence-reuse capture")
        identity = source_identity(record)
        if identity in seen or identity not in expected:
            raise ValueError("duplicate or unexpected optimization identity")
        if record["source"] != expected_source(expected[identity]):
            raise ValueError("optimization source hash binding mismatch")
        seen.add(identity)
        condition_count += validate_equivalence(record, protocol)
        runtime_optimization = (
            record.get("runtime_evidence", {})
            .get("deployment_optimization", {})
        )
        if (
            runtime_optimization.get("schema_version")
            != "mdr_evidence_reuse_v1"
            or runtime_optimization.get("effect_semantics_changed")
            is not False
            or int(
                runtime_optimization.get(
                    "clean_model_evidence_passes_per_batch", -1
                )
            )
            != 1
            or int(
                runtime_optimization.get(
                    "robust_model_evidence_passes_per_batch", -1
                )
            )
            != 1
            or int(
                runtime_optimization.get(
                    "original_clean_model_evidence_passes_per_batch", -1
                )
            )
            != 2
            or int(
                runtime_optimization.get(
                    "original_robust_model_evidence_passes_per_batch", -1
                )
            )
            != 3
        ):
            raise ValueError("runtime evidence-reuse contract mismatch")
        batches = {}
        for batch in protocol["benchmark"]["batch_sizes"]:
            block = record.get("benchmark", {}).get(str(batch))
            if set(block or {}) != set(METHODS):
                raise ValueError("optimization method coverage mismatch")
            batches[str(batch)] = {}
            for comparator in (
                "original_mdr_caeos_v1",
                "embedded_caeos_pairwise",
            ):
                ratios = {
                    metric: positive_ratio(
                        block["mdr_evidence_reuse_v1"][metric],
                        block[comparator][metric],
                    )
                    for metric in LATENCY_METRICS
                }
                ratios["samples_per_second"] = positive_ratio(
                    block["mdr_evidence_reuse_v1"][
                        "samples_per_second"
                    ],
                    block[comparator]["samples_per_second"],
                )
                batches[str(batch)][f"optimized_vs_{comparator}"] = ratios
        artifact = record.get("artifact", {})
        ratios = {
            "suite": identity[0],
            "scenario": identity[1],
            "training_seed": identity[2],
            "batches": batches,
            "optimized_vs_original_artifact_ratio": positive_ratio(
                artifact["optimized_mdr_bytes"],
                artifact["original_mdr_bytes"],
            ),
            "optimized_vs_pairwise_artifact_ratio": positive_ratio(
                artifact["optimized_mdr_bytes"],
                artifact["embedded_pairwise_bytes"],
            ),
        }
        capture_ratios.append(ratios)
        by_scenario[(identity[0], identity[1])].append(ratios)
        contexts.append(record["execution_context"])
    if seen != set(expected) or condition_count != 1836:
        raise ValueError("optimization capture or condition coverage mismatch")
    expected_seeds = set(map(int, protocol["training_seeds"])) if (
        "training_seeds" in protocol
    ) else {
        int(source["training_seed"]) for source in protocol["sources"]
    }
    if len(expected_seeds) != 3:
        raise ValueError("three training seeds required")
    if (
        len(by_scenario) != 102
        or any(len(values) != 3 for values in by_scenario.values())
        or any(
            {int(value["training_seed"]) for value in values}
            != expected_seeds
            for values in by_scenario.values()
        )
    ):
        raise ValueError("three-seed scenario block coverage mismatch")

    scenario_blocks = []
    ratio_series: Dict[str, list[float]] = defaultdict(list)
    for (suite, scenario), values in sorted(by_scenario.items()):
        scenario_block: Dict[str, Any] = {
            "suite": suite,
            "scenario": scenario,
            "seed_count": 3,
            "batches": {},
        }
        for batch in protocol["benchmark"]["batch_sizes"]:
            batch_key = str(batch)
            scenario_block["batches"][batch_key] = {}
            for comparison in (
                "optimized_vs_original_mdr_caeos_v1",
                "optimized_vs_embedded_caeos_pairwise",
            ):
                scenario_block["batches"][batch_key][comparison] = {}
                for metric in (*LATENCY_METRICS, "samples_per_second"):
                    value = float(
                        np.mean(
                            [
                                item["batches"][batch_key][comparison][
                                    metric
                                ]
                                for item in values
                            ]
                        )
                    )
                    scenario_block["batches"][batch_key][comparison][
                        metric
                    ] = value
                    ratio_series[
                        f"{comparison}_batch{batch}_{metric}"
                    ].append(value)
        for key in (
            "optimized_vs_original_artifact_ratio",
            "optimized_vs_pairwise_artifact_ratio",
        ):
            value = float(np.mean([item[key] for item in values]))
            scenario_block[key] = value
            ratio_series[key].append(value)
        scenario_blocks.append(scenario_block)

    repetitions = int(
        protocol["benchmark"]["scenario_block_bootstrap_repetitions"]
    )
    base_seed = int(protocol["benchmark"]["bootstrap_seed"])
    inference = {
        key: bootstrap_mean(
            values,
            seed=base_seed + index,
            repetitions=repetitions,
        )
        for index, (key, values) in enumerate(sorted(ratio_series.items()))
    }
    original_checks = {
        key: (
            summary["bootstrap_95ci"][0] >= 1.0
            if key.endswith("samples_per_second")
            else summary["bootstrap_95ci"][1] <= 1.0
        )
        for key, summary in inference.items()
        if key.startswith("optimized_vs_original_mdr_caeos_v1_batch")
    }
    pairwise_checks = {
        key: (
            summary["bootstrap_95ci"][0] >= 1.0
            if key.endswith("samples_per_second")
            else summary["bootstrap_95ci"][1] <= 1.0
        )
        for key, summary in inference.items()
        if key.startswith("optimized_vs_embedded_caeos_pairwise_batch")
    }
    context_tokens = {json.dumps(value, sort_keys=True) for value in contexts}
    integrity_checks = {
        "capture_count_is_306": len(records) == 306,
        "scenario_block_count_is_102": len(scenario_blocks) == 102,
        "condition_count_is_1836": condition_count == 1836,
        "all_direct_and_serialization_equivalence_pass": True,
        "all_outputs_are_bound_to_source_hashes": True,
        "effect_semantics_unchanged": True,
        "model_evidence_passes_reduce_from_5_to_2": True,
        "fit_cost_declared_unchanged": True,
        "unknown_or_test_labels_not_used": True,
        "same_hardware_context_is_constant": len(context_tokens) == 1,
    }
    return {
        "capture_count": len(records),
        "scenario_block_count": len(scenario_blocks),
        "condition_count": condition_count,
        "failure_count": 0,
        "scenario_blocks": scenario_blocks,
        "raw_per_capture_ratios": capture_ratios,
        "ratio_inference": inference,
        "integrity_decision": {
            "checks": integrity_checks,
            "passes": all(integrity_checks.values()),
        },
        "deployment_substitution_decision": {
            "passes": all(integrity_checks.values()),
            "requires_latency_improvement": False,
            "preserves_effectiveness_selection": True,
        },
        "latency_improvement_over_original_decision": {
            "checks": original_checks,
            "passes": bool(original_checks) and all(original_checks.values()),
        },
        "strict_efficiency_vs_pairwise_diagnostic": {
            "checks": pairwise_checks,
            "passes": bool(pairwise_checks) and all(pairwise_checks.values()),
            "cannot_override_formal_selected_system_efficiency_gate": True,
        },
        "execution_context": contexts[0],
    }


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    records = []
    file_registry = []
    for source in protocol["sources"]:
        path = (
            run_root
            / "captures"
            / str(source["suite"])
            / str(source["scenario"])
            / f"seed{int(source['training_seed'])}"
            / "optimization.json"
        )
        if not path.is_file():
            raise FileNotFoundError(f"missing optimization capture: {path}")
        records.append(load(path))
        file_registry.append(
            {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "optimization_file_sha256": file_hash(path),
            }
        )
    aggregate = aggregate_captures(records, protocol)
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_evidence_reuse_summary_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate,
        "optimization_file_registry": file_registry,
        "claim_boundary": {
            "deployment_inference_optimization_only": True,
            "accuracy_and_robustness_are_unchanged_by_equivalence": True,
            "latency_improvement_is_empirical_not_assumed": True,
            "training_and_full_capture_fit_cost_are_unchanged": True,
            "dual_model_artifact_state_is_not_removed": True,
            "cannot_authorize_sota_by_itself": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(load(args.protocol), args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
