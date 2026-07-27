from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--v1-design", type=Path, required=True)
    parser.add_argument(
        "--readiness-compat-protocol", type=Path, required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    v1 = load(args.v1_design)
    readiness = load(args.readiness_compat_protocol)
    if (
        v1.get("schema_version")
        != "strict_v4_integrated_comprehensive_sota_design_v1"
        or v1.get("manifest_sha256") != canonical_hash(v1)
    ):
        raise ValueError("invalid integrated v1 design")
    if (
        readiness.get("schema_version")
        != "strict_v4_final_readiness_post30_compat_protocol_v1"
        or readiness.get("manifest_sha256")
        != canonical_hash(readiness)
    ):
        raise ValueError("invalid readiness compatibility protocol")
    output_root = (
        project / "results/strict_v4_integrated_comprehensive_sota_v2"
    )
    if (output_root / "audit.json").exists():
        raise ValueError("integrated v2 design must freeze before output")
    names = (
        "create_strict_v4_integrated_comprehensive_sota_design_v2.py",
        "audit_strict_v4_integrated_comprehensive_sota_v2.py",
        "audit_strict_v4_integrated_comprehensive_sota.py",
        "scripts/wait_and_audit_strict_v4_integrated_comprehensive_sota_v2.sh",
    )
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_integrated_comprehensive_sota_design_v2"
        ),
        "status": (
            "frozen_before_final_selection_external_results_and_v2_audit"
        ),
        "project_root": str(project),
        "supersedes_design_manifest_sha256": v1["manifest_sha256"],
        "supersedes_design_file_sha256": file_hash(args.v1_design),
        "readiness_compatibility_protocol_manifest_sha256": readiness[
            "manifest_sha256"
        ],
        "readiness_compatibility_protocol_file_sha256": file_hash(
            args.readiness_compat_protocol
        ),
        "allowed_selected_algorithms": [
            "caeos_pairwise",
            (
                "caeos_validation_gated_class_conditional_"
                "reliability_fusion"
            ),
        ],
        "selected_system_evidence_contract": {
            "pairwise": (
                "base readiness selected_algorithm must equal caeos_pairwise"
            ),
            "vgrf_schema": (
                "strict_v4_vgrf_selected_system_confirmation_summary_v1"
            ),
            "vgrf_equivalence_block_count": 204,
            "vgrf_comparative_corruption_pair_count": 1530,
            "required_system_gates": list(
                (
                    "formal_same_hardware_efficiency_characterized",
                    "selected_runtime_equivalence_all_204_blocks",
                    "selected_runtime_internal_deployment_gate",
                    (
                        "efficiency_superiority_all_required_native_"
                        "metrics"
                    ),
                    "candidate_graceful_degradation_gate",
                    (
                        "comparative_corruption_robustness_against_"
                        "opendetect"
                    ),
                )
            ),
        },
        "implementation_sha256": {
            name: file_hash(project / name) for name in names
        },
        "audit_output_count_at_freeze": 0,
        "claim_boundary": {
            "integrated_v1_cannot_authorize_final_claims": True,
            "selected_algorithm_must_own_system_evidence": True,
            "pairwise_evidence_cannot_be_substituted_for_vgrf": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
