from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def create_core_protocol(
    project_root: Path, design_path: Path, output_path: Path
) -> Dict[str, Any]:
    design = load_json(design_path)
    if (
        design.get("schema_version")
        != "strict_v4_rrc_csr_fallback_design_v1"
        or design.get("manifest_sha256") != canonical_hash(design)
        or design.get("execution_admitted") is not False
        or design.get("output_counts_at_freeze")
        != {
            "execution_protocol": 0,
            "captures": 0,
            "evaluations": 0,
            "summary": 0,
            "audit": 0,
        }
    ):
        raise ValueError("canonical zero-result RRC fallback design required")

    implementation_paths = [
        project_root / "caeos" / "rrc_csr_runtime.py",
        project_root / "certify_rrc_csr_scenario.py",
        project_root / "create_strict_v4_rrc_csr_core_protocol.py",
        project_root / "caeos" / "csr_runtime.py",
        project_root / "caeos" / "csr_exact_replay_runtime.py",
    ]
    implementation_sha256 = {
        path.relative_to(project_root).as_posix(): file_hash(path)
        for path in implementation_paths
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_core_protocol_v1",
        "state": "core_implemented_execution_chain_incomplete",
        "algorithm": "rrc_csr_caeos_v1",
        "execution_admitted": False,
        "design_manifest_sha256": design["manifest_sha256"],
        "design_file_sha256": file_hash(design_path),
        "implementation_sha256": implementation_sha256,
        "runtime_contract": {
            "prediction_probability_source": "clean_pairwise_exact",
            "enabled_risk_policy": (
                "csr_active_monotone_uplift_otherwise_clean_exact"
            ),
            "disabled_behavior": (
                "exact_pairwise_prediction_probability_risk"
            ),
            "scenario_certificate_shared_across_three_seeds": True,
            "absolute_known_macro_f1_threshold": None,
            "unknown_or_test_labels_used": False,
        },
        "certificate_contract": design["certificate"],
        "remaining_required_components": [
            "execution_protocol_creator",
            "three_seed_scenario_capture_coordinator",
            "runtime_materializer_and_roundtrip_capture",
            "six_condition_evaluator",
            "primary83_and_suite_balanced_summarizer",
            "independent_auditor",
            "resumable_runner_and_krc_negative_watcher",
        ],
        "output_counts_at_freeze": {
            "scenario_certificates": 0,
            "runtime_artifacts": 0,
            "captures": 0,
            "evaluations": 0,
            "summary": 0,
            "audit": 0,
        },
        "claim_boundary": {
            "core_protocol_is_not_execution_protocol": True,
            "core_implementation_is_not_effect_evidence": True,
            "current_krc_protocol_and_conclusion_unchanged": True,
            "rrc_activation_still_requires_terminal_negative_krc": True,
            "full_execution_chain_and_independent_audit_still_required": True,
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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_core_protocol(
        args.project_root.resolve(),
        args.design.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "manifest_sha256": value["manifest_sha256"],
                "file_sha256": file_hash(args.output.resolve()),
                "execution_admitted": value["execution_admitted"],
                "remaining_required_components": value[
                    "remaining_required_components"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
