from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from certify_krc_csr import load
from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION = {
    "certifier": "certify_krc_csr.py",
    "selector": "evaluate_krc_csr_selection.py",
    "summarizer": "summarize_krc_csr_pilot.py",
    "runner": "run_strict_v4_krc_csr_pilot.py",
    "auditor": "audit_krc_csr_pilot.py",
    "creator": "create_strict_v4_krc_csr_protocol.py",
}


def counts(run_root: Path, result_root: Path) -> Dict[str, int]:
    return {
        "certificate": len(list(run_root.rglob("certificate.json")))
        if run_root.exists()
        else 0,
        "evaluation": len(list(run_root.rglob("evaluation.json")))
        if run_root.exists()
        else 0,
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
        "completion": int((result_root / "pilot_complete").exists()),
    }


def create(
    project_root: Path,
    design: Dict[str, Any],
    admission: Dict[str, Any],
    source_protocol: Dict[str, Any],
    source_summary: Dict[str, Any],
    source_audit: Dict[str, Any],
    source_capture_root: Path,
    source_evaluation_root: Path,
    run_root: Path,
    result_root: Path,
) -> Dict[str, Any]:
    if (
        design.get("manifest_sha256") != canonical_hash(design)
        or admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("passes") is not True
        or source_protocol.get("manifest_sha256")
        != canonical_hash(source_protocol)
        or source_summary.get("manifest_sha256")
        != canonical_hash(source_summary)
        or source_summary.get("passes") is not False
        or source_summary.get("checks", {}).get(
            "at_least_5_of_7_suites_nonnegative_each_metric"
        )
        is not False
        or source_audit.get("manifest_sha256")
        != canonical_hash(source_audit)
        or source_audit.get("passes") is not True
    ):
        raise ValueError("canonical negative source CSR evidence required")
    frozen_counts = counts(run_root, result_root)
    if any(frozen_counts.values()):
        raise ValueError("KRC protocol must freeze before candidate outputs")
    capture_hashes = {}
    for path in sorted(source_capture_root.rglob("capture_manifest.json")):
        value = load(path)
        key = f"{value['task']['suite']}/{value['task']['scenario']}"
        capture_hashes[key] = file_hash(path)
    evaluation_hashes = {}
    for path in sorted(source_evaluation_root.rglob("evaluation.json")):
        value = load(path)
        key = f"{value['suite']}/{value['scenario']}/{value['condition']}"
        evaluation_hashes[key] = file_hash(path)
    if len(capture_hashes) != 14 or len(evaluation_hashes) != 84:
        raise ValueError("14 source captures and 84 evaluations required")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_development_protocol_v1",
        "status": "frozen_before_candidate_outputs",
        "algorithm": "krc_csr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "source_exact_replay_protocol_manifest_sha256": source_protocol[
            "manifest_sha256"
        ],
        "source_exact_replay_summary_manifest_sha256": source_summary[
            "manifest_sha256"
        ],
        "source_exact_replay_audit_manifest_sha256": source_audit[
            "manifest_sha256"
        ],
        "source_capture_manifest_file_sha256": dict(
            sorted(capture_hashes.items())
        ),
        "source_evaluation_file_sha256": dict(
            sorted(evaluation_hashes.items())
        ),
        "known_only_certificate": {
            "partition": "even_indices_existing_csr_calibration_partition",
            "calibration_known_macro_f1_minimum": 0.9,
            "calibration_error_detection_auroc_minimum": 0.7,
            "degenerate_error_labels_enable_routing": False,
            "disabled_behavior": "exact_pairwise_prediction_probability_risk",
            "unknown_or_test_labels_used": False,
        },
        "development_gate": {
            "enabled_scenario_count_minimum": 4,
            "enabled_suite_count_minimum": 2,
            "inherits_csr_effect_gates": True,
        },
        "reserved_confirmation": {
            "training_seeds": [647, 653, 659],
            "corruption_seeds": [661, 673, 677],
            "primary_scenario_rule": (
                "full102 minus the 14 development scenario identities"
            ),
            "primary_scenario_count": 88,
            "enabled_scenario_count_minimum": 18,
            "enabled_suite_count_minimum": 4,
            "same_effect_gates_as_development": True,
            "real_runtime_execution_required": True,
            "no_automatic_sota_claim": True,
        },
        "implementation": IMPLEMENTATION,
        "implementation_sha256": {
            name: file_hash(project_root / relative)
            for name, relative in IMPLEMENTATION.items()
        },
        "output_counts_at_freeze": frozen_counts,
        "effect_metrics_used_for": (
            "development-only algorithm design; prohibited for confirmation "
            "threshold changes"
        ),
        "claim_boundary": {
            "development_pass_only_authorizes_confirmation": True,
            "report_materialization_is_not_runtime_confirmation": True,
            "full102_external_safety_efficiency_still_required": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--source-protocol", type=Path, required=True)
    parser.add_argument("--source-summary", type=Path, required=True)
    parser.add_argument("--source-audit", type=Path, required=True)
    parser.add_argument("--source-capture-root", type=Path, required=True)
    parser.add_argument("--source-evaluation-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create(
        args.project_root.resolve(),
        load(args.design),
        load(args.admission),
        load(args.source_protocol),
        load(args.source_summary),
        load(args.source_audit),
        args.source_capture_root.resolve(),
        args.source_evaluation_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
