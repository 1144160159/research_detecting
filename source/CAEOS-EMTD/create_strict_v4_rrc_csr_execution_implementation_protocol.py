from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION = (
    "caeos/rrc_csr_runtime.py",
    "certify_rrc_csr_scenario.py",
    "create_strict_v4_rrc_csr_execution_input_protocol.py",
    "materialize_rrc_csr_runtime.py",
    "evaluate_rrc_csr_runtime.py",
    "create_strict_v4_rrc_csr_execution_protocol.py",
    "run_strict_v4_rrc_csr_capture_pipeline.py",
    "summarize_rrc_csr_confirmation.py",
    "audit_rrc_csr_confirmation.py",
    "run_strict_v4_rrc_csr_confirmation.py",
    "classify_strict_v4_rrc_terminal_decision.py",
    "scripts/wait_and_run_strict_v4_rrc_csr_confirmation.sh",
    "create_strict_v4_rrc_csr_execution_implementation_protocol.py",
)


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def create(
    project_root: Path,
    design_path: Path,
    core_protocol_path: Path,
    output_path: Path,
) -> Dict[str, Any]:
    design = load_json(design_path)
    core = load_json(core_protocol_path)
    if (
        design.get("schema_version")
        != "strict_v4_rrc_csr_fallback_design_v1"
        or design.get("manifest_sha256") != canonical_hash(design)
        or core.get("schema_version")
        != "strict_v4_rrc_csr_core_protocol_v1"
        or core.get("manifest_sha256") != canonical_hash(core)
        or core.get("design_manifest_sha256") != design["manifest_sha256"]
        or design.get("execution_admitted") is not False
        or core.get("execution_admitted") is not False
    ):
        raise ValueError("canonical zero-result RRC design/core required")
    implementation_sha256 = {
        relative: file_hash(project_root / relative)
        for relative in IMPLEMENTATION
    }
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_rrc_csr_execution_implementation_protocol_v1"
        ),
        "state": "full_execution_chain_implemented_waiting_terminal_krc_decision",
        "algorithm": "rrc_csr_caeos_v1",
        "execution_admitted": False,
        "design_manifest_sha256": design["manifest_sha256"],
        "core_protocol_manifest_sha256": core["manifest_sha256"],
        "implementation_sha256": implementation_sha256,
        "implemented_components": [
            "scenario_pooled_runtime",
            "three_seed_known_only_certifier",
            "conditional_input_protocol_creator",
            "runtime_materializer_and_serialization_roundtrip",
            "six_condition_evaluator",
            "full_execution_protocol_creator",
            "base_csr_capture_and_scenario_coordinator",
            "primary83_and_suite_balanced_summarizer",
            "independent_auditor",
            "resumable_final_runner",
            "terminal_krc_decision_watcher",
        ],
        "remaining_required_components": [],
        "materialization_contract": {
            "source_csr_manifest_artifact_and_input_sha_required": True,
            "scenario_certificate_and_seed_record_required": True,
            "test_features_used_for_roundtrip_only": True,
            "test_labels_used_for_roundtrip": False,
            "prediction_probability_risk_active_roundtrip_exact": True,
        },
        "evaluation_contract": {
            "conditions": [
                "clean",
                "modality_missing",
                "field_missing",
                "row_missing",
                "feature_shuffle",
                "gaussian_drift",
            ],
            "metrics_and_corruption_selector_reused_from_krc": True,
            "test_labels_used_for_final_evaluation_only": True,
            "candidate_and_embedded_pairwise_reported_together": True,
        },
        "output_counts_at_freeze": {
            "execution_protocol": 0,
            "base_csr_captures": 0,
            "scenario_certificates": 0,
            "rrc_runtime_captures": 0,
            "evaluations": 0,
            "summary": 0,
            "audit": 0,
        },
        "claim_boundary": {
            "implementation_protocol_is_not_execution_protocol": True,
            "no_rrc_effect_or_sota_claim_supported": True,
            "terminal_negative_krc_still_required": True,
            "all_components_bound_before_execution_protocol": True,
        },
        "output_path": output_path.resolve().as_posix(),
    }
    value["manifest_sha256"] = canonical_hash(value)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--core-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create(
        args.project_root.resolve(),
        args.design.resolve(),
        args.core_protocol.resolve(),
        args.output.resolve(),
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
