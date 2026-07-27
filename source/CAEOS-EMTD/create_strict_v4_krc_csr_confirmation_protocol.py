from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION = {
    "runtime": "caeos/krc_csr_runtime.py",
    "source_csr_runtime": "caeos/csr_runtime.py",
    "capture": "capture_krc_csr_confirmation_runtime.py",
    "source_csr_capture": "capture_csr_caeos_runtime.py",
    "evaluator": "evaluate_krc_csr_confirmation_runtime.py",
    "summarizer": "summarize_krc_csr_confirmation.py",
    "auditor": "audit_krc_csr_confirmation.py",
    "runner": "run_strict_v4_krc_csr_confirmation.py",
    "clean_trainer": "train_hybrid_open_set.py",
    "robust_trainer": "train_mdr_caeos_open_set.py",
}


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def output_counts(run_root: Path, result_root: Path) -> Dict[str, int]:
    return {
        "capture_manifest": len(
            list(run_root.rglob("capture_manifest.json"))
        )
        if run_root.exists()
        else 0,
        "evaluation": len(list(run_root.rglob("evaluation.json")))
        if run_root.exists()
        else 0,
        "summary": len(list(result_root.rglob("summary.json")))
        if result_root.exists()
        else 0,
        "audit": len(list(result_root.rglob("audit.json")))
        if result_root.exists()
        else 0,
    }


def create(
    design: Dict[str, Any],
    comparative: Dict[str, Any],
    project_root: Path,
    observed_counts: Dict[str, int],
    *,
    design_file_sha256: str,
    comparative_file_sha256: str,
) -> Dict[str, Any]:
    if (
        design.get("schema_version")
        != "strict_v4_krc_csr_confirmation_design_v1"
        or design.get("manifest_sha256") != canonical_hash(design)
        or design.get("execution_admitted") is not False
        or design.get("status")
        != "frozen_before_execution_implementation_and_results"
    ):
        raise ValueError("canonical frozen KRC confirmation design required")
    if (
        comparative.get("schema_version")
        != "strict_v4_comparative_corruption_protocol_v2"
        or comparative.get("manifest_sha256") != canonical_hash(comparative)
        or comparative["manifest_sha256"]
        != design["comparative_protocol_manifest_sha256"]
    ):
        raise ValueError("bound comparative corruption protocol required")
    if any(observed_counts.values()):
        raise ValueError(
            "KRC execution protocol must be frozen before any result exists"
        )
    implementation_sha256 = {}
    for name, relative in IMPLEMENTATION.items():
        path = project_root / relative
        if not path.is_file():
            raise ValueError(f"missing KRC implementation: {path}")
        implementation_sha256[name] = file_hash(path)
    confirmation = dict(design["confirmation"])
    confirmation.update(
        {
            "training_sample_fraction": 0.25,
            "health_quantile": 0.99,
            "fixed_severity": comparative["corruption_conditions"][
                "fixed_severity"
            ],
            "outer_workers": 4,
            "inner_jobs": 8,
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
        }
    )
    gate = dict(design["primary_gate"])
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
        "status": "admitted_before_first_result",
        "execution_admitted": True,
        "algorithm": "krc_csr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "design_file_sha256": design_file_sha256,
        "comparative_protocol_manifest_sha256": comparative[
            "manifest_sha256"
        ],
        "comparative_protocol_file_sha256": comparative_file_sha256,
        "development_protocol_manifest_sha256": design[
            "development_protocol_manifest_sha256"
        ],
        "development_summary_manifest_sha256": design[
            "development_summary_manifest_sha256"
        ],
        "development_audit_manifest_sha256": design[
            "development_audit_manifest_sha256"
        ],
        "coverage_manifest_sha256": design["coverage_manifest_sha256"],
        "source_registry": design["source_registry"],
        "source_registry_count": design["source_registry_count"],
        "development_scenario_identities": design[
            "development_scenario_identities"
        ],
        "primary_scenario_identities": design[
            "primary_scenario_identities"
        ],
        "confirmation": confirmation,
        "known_only_certificate": design["known_only_certificate"],
        "clean_safety_gate": {
            "partition": "odd_indices_existing_csr_calibration_partition",
            "nonmissing_activation_rate_one_sided_95pct_upper_maximum": (
                0.01
            ),
            "confidence": 0.95,
            "prediction_probability_exact_pairwise": True,
            "inactive_risk_max_absolute_difference": 1e-12,
            "test_arrays_read": [],
        },
        "primary_gate": gate,
        "aggregation_protocol": {
            "directed_metrics": [
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "lower_is_better": ["unknown_fpr95"],
            "scenario_enabled_only_if_all_three_training_seeds_certify": (
                True
            ),
            "metric_mean_order": (
                "evaluation_rows_then_seed_family_scenario_aggregation"
            ),
            "suite_gate_weighting": "within_suite_arithmetic_mean",
            "overall_metric_weighting": "equal_evaluation_rows",
            "bootstrap_unit": "scenario",
            "bootstrap_stratification": (
                "within_suite_then_equal_weight_seven_suites"
            ),
            "bootstrap_interval": "percentile_two_sided_95pct",
            "bootstrap_lower_quantile": 0.025,
            "no_seed_suite_metric_or_family_splicing": True,
        },
        "secondary_full102_report": design["secondary_full102_report"],
        "implementation": IMPLEMENTATION,
        "implementation_sha256": implementation_sha256,
        "resource_contract": {
            "outer_workers": 4,
            "inner_jobs_per_fit": 8,
            "maximum_concurrent_fit_processes": 4,
            "cpu_thread_budget": 32,
            "ionice_class": "idle",
            "nice_level": 19,
            "gpu_allocation": (
                "trainers_are_cpu_tree_ensembles_gpu_memory_not_reserved"
            ),
            "single_coordinator_process": True,
        },
        "output_counts_at_freeze": observed_counts,
        "finalization_order": [
            "306 canonical captures",
            "1836 canonical evaluations",
            "primary88 and secondary full102 summary",
            "independent audit",
            "document update only after audit",
        ],
        "selection_rule": design["selection_rule"],
        "claim_boundary": design["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    design_path = args.design.resolve()
    comparative_path = args.comparative_protocol.resolve()
    value = create(
        load_json(design_path),
        load_json(comparative_path),
        args.project_root.resolve(),
        output_counts(
            args.run_root.resolve(), args.result_root.resolve()
        ),
        design_file_sha256=file_hash(design_path),
        comparative_file_sha256=file_hash(comparative_path),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
