from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION = {
    "runtime": "caeos/rrc_csr_runtime.py",
    "source_runtime": "caeos/csr_runtime.py",
    "source_capture": "capture_csr_caeos_runtime.py",
    "scenario_certifier": "certify_rrc_csr_scenario.py",
    "materializer": "materialize_rrc_csr_runtime.py",
    "evaluator": "evaluate_rrc_csr_runtime.py",
    "capture_pipeline": "run_strict_v4_rrc_csr_capture_pipeline.py",
    "summarizer": "summarize_rrc_csr_confirmation.py",
    "auditor": "audit_rrc_csr_confirmation.py",
    "runner": "run_strict_v4_rrc_csr_confirmation.py",
    "protocol_creator": "create_strict_v4_rrc_csr_execution_protocol.py",
    "clean_trainer": "train_hybrid_open_set.py",
    "robust_trainer": "train_mdr_caeos_open_set.py",
}


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical(value: Dict[str, Any], schema: str) -> bool:
    return bool(
        value.get("schema_version") == schema
        and value.get("manifest_sha256") == canonical_hash(value)
    )


def output_counts(run_root: Path, result_root: Path) -> Dict[str, int]:
    patterns = {
        "base_csr_captures": (
            run_root / "base_csr_captures",
            "capture_manifest.json",
        ),
        "scenario_certificates": (
            run_root / "scenario_certificates",
            "certificate.json",
        ),
        "rrc_runtime_captures": (
            run_root / "rrc_runtime_captures",
            "capture_manifest.json",
        ),
        "evaluations": (run_root / "evaluations", "evaluation.json"),
        "capture_pipeline_inventory": (
            result_root,
            "capture_pipeline_inventory.json",
        ),
        "summary": (result_root, "summary.json"),
        "audit": (result_root, "audit.json"),
    }
    return {
        name: len(list(root.rglob(pattern))) if root.exists() else 0
        for name, (root, pattern) in patterns.items()
    }


def create(
    *,
    project_root: Path,
    design: Dict[str, Any],
    input_protocol: Dict[str, Any],
    implementation_protocol: Dict[str, Any],
    krc_protocol: Dict[str, Any],
    observed_counts: Dict[str, int],
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    if (
        not canonical(design, "strict_v4_rrc_csr_fallback_design_v1")
        or not canonical(
            input_protocol,
            "strict_v4_rrc_csr_execution_input_protocol_v1",
        )
        or not canonical(
            implementation_protocol,
            "strict_v4_rrc_csr_execution_implementation_protocol_v1",
        )
        or not canonical(
            krc_protocol, "strict_v4_krc_csr_confirmation_protocol_v1"
        )
        or input_protocol.get("activation_gate_satisfied") is not True
        or input_protocol.get("execution_admitted") is not False
        or input_protocol.get("rrc_design_manifest_sha256")
        != design["manifest_sha256"]
        or input_protocol.get("krc_protocol_manifest_sha256")
        != krc_protocol["manifest_sha256"]
        or implementation_protocol.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or implementation_protocol.get("execution_admitted") is not False
        or implementation_protocol.get("state")
        != "full_execution_chain_implemented_waiting_terminal_krc_decision"
        or implementation_protocol.get("remaining_required_components") != []
    ):
        raise ValueError("canonical terminal-negative RRC inputs required")
    if any(int(value) != 0 for value in observed_counts.values()):
        raise ValueError(
            "RRC execution protocol must be frozen before every result"
        )
    tasks = input_protocol["tasks"]
    source_registry = input_protocol["source_registry"]
    if (
        len(tasks) != 249
        or len(source_registry) != 83
        or input_protocol["task_counts"]
        != {
            "scenarios": 83,
            "training_seeds": 3,
            "base_csr_captures": 249,
            "scenario_certificates": 83,
            "rrc_runtime_captures": 249,
            "conditions_per_runtime": 6,
            "evaluations": 1494,
        }
    ):
        raise ValueError("exact RRC 83x3x6 task universe required")

    implementation_sha256 = {}
    for name, relative in IMPLEMENTATION.items():
        path = project_root / relative
        if not path.is_file():
            raise ValueError(f"missing RRC implementation: {path}")
        implementation_sha256[name] = file_hash(path)

    confirmation = design["confirmation"]
    conditions = list(krc_protocol["confirmation"]["conditions"])
    if conditions != [
        "clean",
        "modality_missing",
        "field_missing",
        "row_missing",
        "feature_shuffle",
        "gaussian_drift",
    ]:
        raise ValueError("frozen six-condition contract drifted")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
        "state": "admitted_after_terminal_negative_krc_before_results",
        "execution_admitted": True,
        "algorithm": "rrc_csr_caeos_v1",
        "rrc_design_manifest_sha256": design["manifest_sha256"],
        "rrc_input_protocol_manifest_sha256": input_protocol[
            "manifest_sha256"
        ],
        "rrc_implementation_protocol_manifest_sha256": (
            implementation_protocol["manifest_sha256"]
        ),
        "krc_protocol_manifest_sha256": krc_protocol["manifest_sha256"],
        "krc_downstream_decision_manifest_sha256": input_protocol[
            "downstream_decision_manifest_sha256"
        ],
        "coverage_manifest_sha256": krc_protocol[
            "coverage_manifest_sha256"
        ],
        "comparative_protocol_manifest_sha256": krc_protocol[
            "comparative_protocol_manifest_sha256"
        ],
        "source_registry": source_registry,
        "source_registry_count": len(source_registry),
        "tasks": tasks,
        "task_counts": input_protocol["task_counts"],
        "training_seeds": input_protocol["training_seeds"],
        "corruption_seeds": input_protocol["corruption_seeds"],
        "conditions": conditions,
        "fixed_severity": krc_protocol["confirmation"]["fixed_severity"],
        "fixed_augmentation_weight": krc_protocol["confirmation"][
            "fixed_augmentation_weight"
        ],
        "training_sample_fraction": krc_protocol["confirmation"][
            "training_sample_fraction"
        ],
        "health_quantile": krc_protocol["confirmation"]["health_quantile"],
        "certificate_gate": design["certificate"],
        "effect_gate": {
            "primary_enabled_scenario_count_minimum": confirmation[
                "primary_enabled_scenario_count_minimum"
            ],
            "primary_enabled_suite_count_minimum": confirmation[
                "primary_enabled_suite_count_minimum"
            ],
            "overall_directed_means_strictly_positive": confirmation[
                "overall_directed_means_strictly_positive"
            ],
            "suite_nonnegative_count_minimum_each_metric": confirmation[
                "suite_nonnegative_count_minimum_each_metric"
            ],
            "each_family_metric_regression_maximum": confirmation[
                "each_family_metric_regression_maximum"
            ],
            "modality_missing_composite_improves": confirmation[
                "modality_missing_composite_improves"
            ],
            "gaussian_drift_composite_improves": confirmation[
                "gaussian_drift_composite_improves"
            ],
        },
        "aggregation_protocol": {
            "directed_metrics": [
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "lower_is_better": ["unknown_fpr95"],
            "scenario_enabled_only_if_three_seed_certificate_passes": True,
            "seed_then_scenario_then_suite_aggregation": True,
            "suite_balanced_overall": True,
            "bootstrap_unit": "scenario",
            "bootstrap_stratification": "within_suite_equal_suite_weight",
            "bootstrap_replicates": confirmation["bootstrap_replicates"],
            "bootstrap_seed": confirmation["bootstrap_seed"],
            "no_seed_suite_metric_or_family_splicing": True,
        },
        "implementation": IMPLEMENTATION,
        "implementation_sha256": implementation_sha256,
        "resource_contract": {
            "outer_workers": 4,
            "inner_jobs_per_fit": 8,
            "maximum_concurrent_fit_processes": 4,
            "cpu_thread_budget": 32,
            "subprocess_resource_prefix": [
                "ionice",
                "-c",
                "3",
                "nice",
                "-n",
                "19",
            ],
            "resume_policy": (
                "reuse_only_canonical_complete_hash_valid_outputs"
            ),
            "partial_output_policy": (
                "stop_without_overwrite_and_require_manual_quarantine"
            ),
        },
        "output_counts_at_freeze": observed_counts,
        "finalization_order": [
            "249 base CSR captures",
            "83 three-seed known-only scenario certificates",
            "249 serialized RRC runtime captures",
            "1494 six-condition evaluations",
            "primary83 suite-balanced summary",
            "independent audit",
            "document update only after audit",
        ],
        "claim_boundary": {
            "terminal_negative_krc_is_only_activation_not_rrc_effect": True,
            "test_labels_used_for_final_evaluation_only": True,
            "rrc_success_does_not_alone_establish_external_sota": True,
            "full_sota_requires_pre_registered_external_and_system_gates": True,
        },
        "input_file_sha256": input_file_sha256,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--rrc-design", type=Path, required=True)
    parser.add_argument("--rrc-input-protocol", type=Path, required=True)
    parser.add_argument(
        "--rrc-implementation-protocol", type=Path, required=True
    )
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "rrc_design": args.rrc_design.resolve(),
        "rrc_input_protocol": args.rrc_input_protocol.resolve(),
        "rrc_implementation_protocol": (
            args.rrc_implementation_protocol.resolve()
        ),
        "krc_protocol": args.krc_protocol.resolve(),
    }
    value = create(
        project_root=args.project_root.resolve(),
        design=load_json(paths["rrc_design"]),
        input_protocol=load_json(paths["rrc_input_protocol"]),
        implementation_protocol=load_json(
            paths["rrc_implementation_protocol"]
        ),
        krc_protocol=load_json(paths["krc_protocol"]),
        observed_counts=output_counts(
            args.run_root.resolve(), args.result_root.resolve()
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
