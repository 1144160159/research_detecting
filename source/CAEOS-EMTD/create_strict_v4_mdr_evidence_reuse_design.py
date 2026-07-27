from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def create_design(
    *,
    project_root: Path,
    mdr_design: Dict[str, Any],
    selected_system_design: Dict[str, Any],
    opendetect_efficiency_design: Dict[str, Any],
    input_file_sha256: Dict[str, str],
    implementation_sha256: Dict[str, str],
    observed_outputs: int,
) -> Dict[str, Any]:
    require_canonical(
        mdr_design,
        "strict_v4_mdr_caeos_design_v2",
        "MDR design",
    )
    require_canonical(
        selected_system_design,
        "strict_v4_mdr_selected_system_design_v1",
        "MDR selected-system design",
    )
    require_canonical(
        opendetect_efficiency_design,
        "strict_v4_mdr_opendetect_efficiency_design_v1",
        "MDR-OpenDetect efficiency design",
    )
    if int(observed_outputs) != 0:
        raise ValueError("evidence-reuse design requires zero formal outputs")
    required = {
        "create_strict_v4_mdr_evidence_reuse_design.py",
        "caeos/mdr_evidence_reuse_runtime.py",
        "caeos/mdr_runtime.py",
        "caeos/mdr_fusion.py",
        "caeos/pairwise_runtime.py",
        "caeos/hybrid_open_set.py",
        "tests/test_mdr_evidence_reuse_runtime.py",
    }
    if not required.issubset(implementation_sha256):
        raise ValueError("evidence-reuse implementation hashes incomplete")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_evidence_reuse_design_v1",
        "status": (
            "conditionally_frozen_before_mdr_selection_and_optimization_outputs"
        ),
        "activation_gate": {
            "selected_algorithm_must_equal": "mdr_caeos_v1",
            "mdr_full102_confirmation_must_pass": True,
            "source_runtime_schema": (
                "strict_v4_mdr_caeos_runtime_capture_v1"
            ),
        },
        "optimization": {
            "name": "mdr_evidence_reuse_v1",
            "scope": "deployment_inference_only",
            "effect_semantics_changed": False,
            "original_model_evidence_passes_per_batch": {
                "clean": 2,
                "robust": 3,
                "total": 5,
            },
            "optimized_model_evidence_passes_per_batch": {
                "clean": 1,
                "robust": 1,
                "total": 2,
            },
            "reuse": [
                "clean_final_probability_and_local_conflict",
                "robust_final_probability_and_local_conflict",
                "robust_component_values_for_missing_aware_risk",
            ],
        },
        "formal_equivalence": {
            "capture_count": 306,
            "scenario_count": 102,
            "condition_count": 1836,
            "conditions": [
                "clean",
                "modality_missing",
                "field_missing",
                "row_missing",
                "feature_shuffle",
                "gaussian_drift",
            ],
            "prediction_active_and_missing_arrays_exact": True,
            "probability_risk_and_diagnostics_max_absolute_tolerance": 1e-12,
            "serialization_roundtrip_required": True,
            "all_source_artifact_and_input_hashes_required": True,
            "unknown_or_test_labels_used": False,
        },
        "benchmark": {
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "method_order": "alternate_by_timed_repetition",
            "methods": [
                "original_mdr_caeos_v1",
                "mdr_evidence_reuse_v1",
                "embedded_caeos_pairwise",
            ],
            "same_process_inputs_threads_and_affinity": True,
            "scenario_block_bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260724,
        },
        "decision": {
            "deployment_substitution_requires_all_equivalence_checks": True,
            "latency_improvement_is_reported_not_assumed": True,
            "artifact_and_full_capture_fit_cost_remain_separate": True,
            "optimization_cannot_change_accuracy_or_robustness_selection": True,
            "optimization_cannot_override_failed_efficiency_gate": True,
        },
        "claim_boundary": {
            "not_a_new_effectiveness_algorithm": True,
            "does_not_authorize_sota_by_itself": True,
            "does_not_reduce_dual_model_training_cost_by_construction": True,
            "does_not_remove_dual_model_artifact_state_by_construction": True,
            "formal_results_must_wait_for_positive_mdr_selection": True,
        },
        "expected_output": {
            "schema_version": (
                "strict_v4_mdr_evidence_reuse_summary_v1"
            ),
            "capture_count": 306,
            "condition_count": 1836,
        },
        "formal_output_count_at_freeze": 0,
        "paths": {"project_root": str(project_root.resolve())},
        "input_manifest_sha256": {
            "mdr_design": mdr_design["manifest_sha256"],
            "selected_system_design": selected_system_design[
                "manifest_sha256"
            ],
            "opendetect_efficiency_design": (
                opendetect_efficiency_design["manifest_sha256"]
            ),
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--mdr-design", type=Path, required=True)
    parser.add_argument("--selected-system-design", type=Path, required=True)
    parser.add_argument(
        "--opendetect-efficiency-design", type=Path, required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "mdr_design": args.mdr_design,
        "selected_system_design": args.selected_system_design,
        "opendetect_efficiency_design": (
            args.opendetect_efficiency_design
        ),
    }
    relatives = [
        "create_strict_v4_mdr_evidence_reuse_design.py",
        "caeos/mdr_evidence_reuse_runtime.py",
        "caeos/mdr_runtime.py",
        "caeos/mdr_fusion.py",
        "caeos/pairwise_runtime.py",
        "caeos/hybrid_open_set.py",
        "tests/test_mdr_evidence_reuse_runtime.py",
    ]
    observed = int(args.output.exists())
    value = create_design(
        project_root=args.project_root,
        mdr_design=load(args.mdr_design),
        selected_system_design=load(args.selected_system_design),
        opendetect_efficiency_design=load(
            args.opendetect_efficiency_design
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        implementation_sha256={
            relative: file_hash(args.project_root / relative)
            for relative in relatives
        },
        observed_outputs=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
