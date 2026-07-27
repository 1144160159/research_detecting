from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from external_dataset_protocol_utils import (
    canonical_hash,
    file_hash,
    load_json,
)


IMPLEMENTATION = (
    "create_strict_v4_krc_external_malicious_execution_protocol.py",
    "capture_krc_csr_confirmation_runtime.py",
    "evaluate_krc_external_runtime.py",
    "run_strict_v4_krc_external_malicious.py",
    "summarize_strict_v4_krc_external_malicious.py",
    "audit_strict_v4_krc_external_malicious.py",
    "train_hybrid_open_set.py",
    "train_mdr_caeos_open_set.py",
    "train_neural_open_set.py",
    "evaluate_mdr_external_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/csr_runtime.py",
    "caeos/structured_robust.py",
)


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def validate_positive_confirmation(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    audit: Dict[str, Any],
) -> None:
    require_canonical(
        protocol,
        "strict_v4_krc_csr_confirmation_protocol_v1",
        "KRC confirmation protocol",
    )
    require_canonical(
        summary,
        "strict_v4_krc_csr_confirmation_summary_v1",
        "KRC confirmation summary",
    )
    require_canonical(
        audit,
        "strict_v4_krc_csr_confirmation_audit_v1",
        "KRC confirmation audit",
    )
    if (
        summary.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or summary.get("passes") is not True
        or summary.get("authorize_external_safety_efficiency_confirmation")
        is not True
        or summary.get("selection") != "krc_csr_caeos_v1"
        or audit.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or audit.get("summary_manifest_sha256")
        != summary["manifest_sha256"]
        or audit.get("passes") is not True
        or audit.get("decision_matches_summary") is not True
    ):
        raise ValueError(
            "positive canonical KRC confirmation and matching audit required"
        )


def output_counts(result_root: Path) -> Dict[str, int]:
    counts = {
        "capture_manifest": len(
            list(result_root.glob("**/krc_capture/capture_manifest.json"))
        )
        if result_root.exists()
        else 0,
        "candidate_metrics": len(
            list(result_root.glob("**/krc_csr_caeos_v1/metrics.json"))
        )
        if result_root.exists()
        else 0,
        "opendetect_metrics": len(
            list(result_root.glob("**/opendetect/metrics.json"))
        )
        if result_root.exists()
        else 0,
        "summary": int((result_root / "summary.json").is_file()),
        "audit": int((result_root / "audit.json").is_file()),
        "completion": int((result_root / "execution_complete").is_file()),
    }
    if any(counts.values()):
        raise ValueError(
            "KRC external execution protocol requires a zero-result root"
        )
    return counts


def create_protocol(
    *,
    project_root: Path,
    result_root: Path,
    input_protocol_path: Path,
    downstream_design_path: Path,
    external_design_path: Path,
    confirmation_protocol_path: Path,
    confirmation_summary_path: Path,
    confirmation_audit_path: Path,
) -> Dict[str, Any]:
    input_protocol = load_json(input_protocol_path)
    downstream = load_json(downstream_design_path)
    external = load_json(external_design_path)
    confirmation_protocol = load_json(confirmation_protocol_path)
    confirmation_summary = load_json(confirmation_summary_path)
    confirmation_audit = load_json(confirmation_audit_path)
    require_canonical(
        input_protocol,
        "strict_v4_krc_external_malicious_input_protocol_v2",
        "KRC external input protocol",
    )
    require_canonical(
        downstream,
        "strict_v4_krc_downstream_sota_design_v1",
        "KRC downstream design",
    )
    require_canonical(
        external,
        "gpu_external_dataset_evaluation_design_protocol_v1",
        "external evaluation design",
    )
    validate_positive_confirmation(
        confirmation_protocol,
        confirmation_summary,
        confirmation_audit,
    )
    if (
        input_protocol.get("execution_admitted") is not False
        or input_protocol["input_manifest_sha256"]["downstream_design"]
        != downstream["manifest_sha256"]
        or input_protocol["input_manifest_sha256"][
            "krc_confirmation_protocol"
        ]
        != confirmation_protocol["manifest_sha256"]
        or downstream["input_manifest_sha256"]["external_malicious_design"]
        != external["manifest_sha256"]
        or downstream["activation_gate"]["confirmation_selection"]
        != "krc_csr_caeos_v1"
        or len(input_protocol["tasks"]) != 96
        or input_protocol["task_counts"]["attack_families"] != 32
    ):
        raise ValueError("KRC external input/design binding mismatch")

    implementation_sha256 = {}
    for relative in IMPLEMENTATION:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC external implementation: {relative}"
            )
        implementation_sha256[relative] = file_hash(path)
    confirmation = confirmation_protocol["confirmation"]
    zero_counts = output_counts(result_root)
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_external_malicious_execution_protocol_v1"
        ),
        "status": "admitted_after_positive_krc_confirmation_before_results",
        "execution_admitted": True,
        "algorithm": "krc_csr_caeos_v1",
        "comparators": ["embedded_pairwise", "opendetect"],
        "tasks": input_protocol["tasks"],
        "task_counts": input_protocol["task_counts"],
        "dataset_registry": input_protocol["dataset_registry"],
        "krc_policy": {
            "augmentation_weight": float(
                confirmation["fixed_augmentation_weight"]
            ),
            "sample_fraction": float(
                confirmation["training_sample_fraction"]
            ),
            "health_quantile": float(confirmation["health_quantile"]),
            "certificate_known_macro_f1_minimum": 0.9,
            "certificate_error_detection_auroc_minimum": 0.7,
            "prediction_probability_policy": "exact_embedded_pairwise",
            "risk_policy": (
                "known_only_certified_monotone_uplift_otherwise_exact"
            ),
        },
        "pairwise_runtime_policy": external["pairwise_runtime_policy"],
        "opendetect_policy": external["opendetect_policy"],
        "statistics": {
            "bootstrap_unit": (
                "attack_family_after_averaging_three_training_seeds"
            ),
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260726,
            "wilcoxon_alternative": "greater",
            "multiple_testing": "holm_across_four_unknown_metrics",
            "comparators_evaluated_independently_without_splicing": True,
        },
        "confirmation_gate": {
            "against_each_comparator": input_protocol[
                "confirmation_gate"
            ],
            "both_comparators_must_pass": True,
            "coverage_complete_and_failure_count_zero": True,
            "unknown_or_test_labels_excluded_from_fit_selection_threshold_"
            "and_routing": True,
        },
        "expected_outputs": {
            "candidate_capture_count": 96,
            "candidate_metric_count": 96,
            "embedded_pairwise_report_count": 96,
            "opendetect_metric_count": 96,
            "total_metric_report_count": 288,
            "summary_count": 1,
            "audit_count": 1,
        },
        "resource_contract": {
            "must_not_overlap_krc_accuracy_confirmation": True,
            "candidate_capture_outer_workers": 4,
            "candidate_fit_jobs_per_worker": 8,
            "opendetect_gpu_workers": 1,
            "capture_phase_precedes_opendetect_phase": True,
            "nice": 19,
            "ionice": "idle",
        },
        "result_root": result_root.resolve().as_posix(),
        "output_counts_at_freeze": zero_counts,
        "input_manifest_sha256": {
            "input_protocol": input_protocol["manifest_sha256"],
            "downstream_design": downstream["manifest_sha256"],
            "external_design": external["manifest_sha256"],
            "confirmation_protocol": confirmation_protocol[
                "manifest_sha256"
            ],
            "confirmation_summary": confirmation_summary["manifest_sha256"],
            "confirmation_audit": confirmation_audit["manifest_sha256"],
        },
        "input_file_sha256": {
            "input_protocol": file_hash(input_protocol_path),
            "downstream_design": file_hash(downstream_design_path),
            "external_design": file_hash(external_design_path),
            "confirmation_protocol": file_hash(confirmation_protocol_path),
            "confirmation_summary": file_hash(confirmation_summary_path),
            "confirmation_audit": file_hash(confirmation_audit_path),
        },
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
        "claim_boundary": {
            "external_success_is_required_but_not_sufficient_for_tier1": True,
            "integrity_audit_pass_does_not_imply_effect_gate_pass": True,
            "pairwise_and_opendetect_gates_cannot_be_spliced": True,
            "candidate_is_retrained_for_every_external_split": True,
            "parrot_benign_safety_is_separate": True,
            "efficiency_is_separate": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--input-protocol", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument("--external-design", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root.resolve(),
        result_root=args.result_root.resolve(),
        input_protocol_path=args.input_protocol.resolve(),
        downstream_design_path=args.downstream_design.resolve(),
        external_design_path=args.external_design.resolve(),
        confirmation_protocol_path=args.confirmation_protocol.resolve(),
        confirmation_summary_path=args.confirmation_summary.resolve(),
        confirmation_audit_path=args.confirmation_audit.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
