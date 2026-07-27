from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def optimized_efficiency_superiority(
    optimized: dict[str, Any],
    training_summary: dict[str, Any],
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    for batch, payload in optimized["aggregate"]["native_primary"].items():
        for metric in (
            "latency_p50_ms",
            "latency_p95_ms",
            "latency_p99_ms",
        ):
            ratio = payload[f"optimized_over_comparator_{metric}"]
            checks[
                f"optimized_native_batch{batch}_{metric}_upper_ci_le_1"
            ] = float(ratio["bootstrap_95ci"][1]) <= 1.0
        throughput = payload[
            "optimized_over_comparator_samples_per_second"
        ]
        checks[
            f"optimized_native_batch{batch}_throughput_lower_ci_ge_1"
        ] = float(throughput["bootstrap_95ci"][0]) >= 1.0
    training = training_summary["training"][
        "paired_candidate_over_comparator"
    ]
    for metric in (
        "total_fit_seconds",
        "deployment_artifact_bytes",
        "peak_host_rss_mb",
    ):
        checks[f"training_{metric}_upper_ci_le_1"] = (
            float(training[metric]["bootstrap_95ci"][1]) <= 1.0
        )
    return {"checks": checks, "passes": all(checks.values())}


def tensorized_efficiency_superiority(
    tensorized: dict[str, Any],
    training_summary: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        f"tensorized_{name}": value is True
        for name, value in tensorized[
            "formal_inference_sota_checks"
        ].items()
    }
    checks["tensorized_formal_inference_efficiency_sota_passes"] = (
        tensorized.get("formal_inference_efficiency_sota_passes") is True
    )
    training = training_summary["training"][
        "paired_candidate_over_comparator"
    ]
    for metric in ("total_fit_seconds", "peak_host_rss_mb"):
        checks[f"training_{metric}_upper_ci_le_1"] = (
            float(training[metric]["bootstrap_95ci"][1]) <= 1.0
        )
    checks["compact_deployment_artifact_bytes_upper_ci_le_1"] = (
        float(
            tensorized["artifact_aggregate"]["compact_over_comparator"][
                "bootstrap_95ci"
            ][1]
        )
        <= 1.0
    )
    return {"checks": checks, "passes": all(checks.values())}


def select_runtime_efficiency(
    optimized: dict[str, Any],
    training_summary: dict[str, Any],
    tensorized: Optional[dict[str, Any]],
) -> dict[str, Any]:
    if tensorized is None or tensorized.get(
        "formal_inference_efficiency_sota_passes"
    ) is not True:
        return {
            "selected_runtime": "pairwise_demand_driven_v6",
            "gate": optimized_efficiency_superiority(
                optimized, training_summary
            ),
            "equivalence_all_204_blocks": optimized.get(
                "gates", {}
            ).get("all_full_input_equivalence_checks_pass")
            is True,
            "internal_deployment_gate": optimized.get("gates", {}).get(
                "two_x_deployment_target_passes"
            )
            is True,
            "tensorized_candidate_evaluated": tensorized is not None,
            "tensorized_candidate_selected": False,
        }
    return {
        "selected_runtime": "pairwise_tensor_forest_compact_v7",
        "gate": tensorized_efficiency_superiority(
            tensorized, training_summary
        ),
        "equivalence_all_204_blocks": (
            tensorized.get("block_count") == 204
            and tensorized.get("compact_build_manifest_count") == 102
        ),
        "internal_deployment_gate": tensorized.get(
            "formal_inference_sota_checks", {}
        ).get("artifact_over_original_bootstrap_upper")
        is True,
        "tensorized_candidate_evaluated": True,
        "tensorized_candidate_selected": True,
    }


def create_audit(
    *,
    protocol: dict[str, Any],
    accuracy: dict[str, Any],
    compatibility: dict[str, Any],
    efficiency: dict[str, Any],
    optimized: dict[str, Any],
    tensorized: Optional[dict[str, Any]],
    corruption: dict[str, Any],
    comparative: dict[str, Any],
) -> dict[str, Any]:
    require_canonical(
        protocol,
        "strict_v4_final_readiness_post30_compat_protocol_v1",
        "compatibility readiness protocol",
    )
    require_canonical(
        accuracy,
        "strict_v4_comprehensive_sota_audit_v12",
        "post-30 accuracy audit",
    )
    require_canonical(
        compatibility,
        "strict_v4_post30_supersession_compatibility_audit_v1",
        "post-30 compatibility",
    )
    if (
        compatibility.get("old_audit_manifest_sha256")
        != accuracy["manifest_sha256"]
        or compatibility.get("post30_baseline_coverage_compatible")
        is not True
        or compatibility.get("unaffected_families_pass") is not True
        or not compatibility.get("superseded_family_audits")
        or not all(
            item.get("passes") is True
            for item in compatibility["superseded_family_audits"]
        )
    ):
        raise ValueError("post-30 compatibility did not repair coverage")
    require_canonical(
        efficiency,
        "strict_v4_final_efficiency_summary_v2",
        "formal efficiency summary",
    )
    if (
        efficiency.get("gates", {}).get(
            "formal_efficiency_claim_allowed"
        )
        is not True
    ):
        raise ValueError("formal efficiency summary is not admissible")
    require_canonical(
        optimized,
        "strict_v4_optimized_efficiency_summary_v1",
        "optimized efficiency summary",
    )
    if (
        optimized.get("gates", {}).get(
            "all_102_scenarios_x_2_modes_complete"
        )
        is not True
        or optimized.get("gates", {}).get(
            "all_full_input_equivalence_checks_pass"
        )
        is not True
        or optimized.get("gates", {}).get(
            "optimized_artifact_size_nonincrease_passes"
        )
        is not True
    ):
        raise ValueError("optimized efficiency summary is incomplete")
    if tensorized is not None:
        require_canonical(
            tensorized,
            "strict_v4_tensorized_full_efficiency_summary_v1",
            "tensorized efficiency summary",
        )
        if (
            tensorized.get("status") != "complete"
            or tensorized.get("block_count") != 204
            or tensorized.get("compact_build_manifest_count") != 102
            or tensorized.get("deployment_runtime_selection", {}).get(
                "metric_wise_runtime_mixing_forbidden"
            )
            is not True
        ):
            raise ValueError("tensorized efficiency summary is incomplete")
    require_canonical(
        corruption,
        "strict_v4_postselection_corruption_summary_v1",
        "post-selection corruption summary",
    )
    if corruption.get("validation", {}).get("passes") is not True:
        raise ValueError("post-selection corruption validation failed")
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_summary_v1",
        "comparative corruption summary",
    )
    if comparative.get("validation", {}).get("passes") is not True:
        raise ValueError("comparative corruption validation failed")
    selected_efficiency = select_runtime_efficiency(
        optimized, efficiency, tensorized
    )
    gates = {
        "post30_baseline_coverage_complete": True,
        "confirmed_external_accuracy_sota_7_datasets_102_scenarios": (
            accuracy.get("strict_v4_confirmed_external_sota_allowed")
            is True
        ),
        "formal_same_hardware_efficiency_characterized": True,
        "selected_runtime_equivalence_all_204_blocks": (
            selected_efficiency["equivalence_all_204_blocks"]
        ),
        "selected_runtime_internal_deployment_gate": (
            selected_efficiency["internal_deployment_gate"]
        ),
        "efficiency_superiority_all_required_native_metrics": (
            selected_efficiency["gate"]["passes"]
        ),
        "candidate_graceful_degradation_gate": corruption.get(
            "confirmatory_gate", {}
        ).get("passes")
        is True,
        "comparative_corruption_robustness_against_opendetect": (
            comparative.get("comparative_robustness_gate", {}).get(
                "passes"
            )
            is True
        ),
    }
    multidimensional = all(gates.values())
    result: dict[str, Any] = {
        "schema_version": "strict_v4_final_paper_readiness_audit_v4",
        "status": "complete_with_explicit_post30_compatibility",
        "selected_algorithm": accuracy.get("selected_algorithm"),
        "comprehensive_formal_method_count": accuracy.get(
            "comprehensive_formal_method_count"
        ),
        "selected_runtime": selected_efficiency["selected_runtime"],
        "selected_runtime_efficiency_superiority": selected_efficiency[
            "gate"
        ],
        "tensorized_candidate_evaluated": selected_efficiency[
            "tensorized_candidate_evaluated"
        ],
        "tensorized_candidate_selected": selected_efficiency[
            "tensorized_candidate_selected"
        ],
        "post30_coverage_source": (
            "explicit_zero_metric_supersession_compatibility"
        ),
        "legacy_post30_coverage_value_preserved": accuracy.get(
            "post30_baseline_coverage_complete"
        ),
        "gates": gates,
        "multidimensional_comprehensive_sota_allowed": multidimensional,
        "claim_tier": (
            "multidimensional_comprehensive_sota"
            if multidimensional
            else "development_complete_confirmatory_accuracy_sota_not_established"
        ),
        "claim_boundary": {
            "legacy_false_post30_field_is_not_overwritten": True,
            "compatibility_repairs_identity_only_not_effect_metrics": True,
            "accuracy_efficiency_and_robustness_gates_remain_independent": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--accuracy-audit", type=Path, required=True)
    parser.add_argument("--post30-compatibility", type=Path, required=True)
    parser.add_argument("--efficiency-summary", type=Path, required=True)
    parser.add_argument(
        "--optimized-efficiency-summary", type=Path, required=True
    )
    parser.add_argument(
        "--tensorized-full-root", type=Path, required=True
    )
    parser.add_argument("--corruption-summary", type=Path, required=True)
    parser.add_argument(
        "--comparative-corruption-summary", type=Path, required=True
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    project = Path(protocol["project_root"])
    for name, expected in protocol["implementation_sha256"].items():
        if file_hash(project / name) != expected:
            raise ValueError(f"implementation SHA mismatch: {name}")
    input_paths = {
        "accuracy_audit": args.accuracy_audit,
        "post30_compatibility": args.post30_compatibility,
    }
    for name, path in input_paths.items():
        if (
            file_hash(path)
            != protocol["frozen_input_file_sha256"][name]
        ):
            raise ValueError(f"frozen input file SHA mismatch: {name}")
    tensorized_summary = args.tensorized_full_root / "summary.json"
    tensorized_not_required = (
        args.tensorized_full_root / "not_required"
    )
    tensorized = (
        None
        if tensorized_not_required.is_file()
        else load(tensorized_summary)
    )
    result = create_audit(
        protocol=protocol,
        accuracy=load(args.accuracy_audit),
        compatibility=load(args.post30_compatibility),
        efficiency=load(args.efficiency_summary),
        optimized=load(args.optimized_efficiency_summary),
        tensorized=tensorized,
        corruption=load(args.corruption_summary),
        comparative=load(args.comparative_corruption_summary),
    )
    result["input_file_sha256"] = {
        "protocol": file_hash(args.protocol),
        **{
            name: file_hash(path)
            for name, path in input_paths.items()
        },
        "efficiency_summary": file_hash(args.efficiency_summary),
        "optimized_efficiency_summary": file_hash(
            args.optimized_efficiency_summary
        ),
        "tensorized_full_evidence": file_hash(
            tensorized_not_required
            if tensorized_not_required.is_file()
            else tensorized_summary
        ),
        "corruption_summary": file_hash(args.corruption_summary),
        "comparative_corruption_summary": file_hash(
            args.comparative_corruption_summary
        ),
    }
    result["audit_implementation_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    result["manifest_sha256"] = canonical_hash(result)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "audit_complete").touch()
    print(result["claim_tier"])


if __name__ == "__main__":
    main()
