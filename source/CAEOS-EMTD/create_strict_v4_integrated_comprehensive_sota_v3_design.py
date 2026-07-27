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


def create_design(
    v2_design: dict[str, Any],
    suite_protocol: dict[str, Any],
    *,
    project_root: str,
    v2_design_file_sha256: str,
    suite_protocol_file_sha256: str,
    auditor_sha256: str,
    v2_audit_count_at_freeze: int,
    suite_audit_count_at_freeze: int,
    v3_audit_count_at_freeze: int,
) -> dict[str, Any]:
    if (
        v2_design.get("schema_version")
        != "strict_v4_integrated_comprehensive_sota_design_v2"
        or v2_design.get("manifest_sha256") != canonical_hash(v2_design)
    ):
        raise ValueError("invalid integrated comprehensive SOTA v2 design")
    if (
        suite_protocol.get("schema_version")
        != "strict_v4_postselection_corruption_suite_gate_protocol_v1"
        or suite_protocol.get("manifest_sha256")
        != canonical_hash(suite_protocol)
    ):
        raise ValueError("invalid corruption suite-gate protocol")
    if any(
        int(count) != 0
        for count in (
            v2_audit_count_at_freeze,
            suite_audit_count_at_freeze,
            v3_audit_count_at_freeze,
        )
    ):
        raise ValueError("integrated v3 design must freeze before all audits")
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_integrated_comprehensive_sota_design_v3"
        ),
        "status": (
            "frozen_before_v2_suite_gate_and_v3_audit_without_effect_read"
        ),
        "project_root": project_root,
        "effect_results_read": False,
        "supersedes_design_manifest_sha256": v2_design["manifest_sha256"],
        "corruption_suite_gate_protocol_manifest_sha256": suite_protocol[
            "manifest_sha256"
        ],
        "input_file_sha256": {
            "v2_design": v2_design_file_sha256,
            "corruption_suite_gate_protocol": suite_protocol_file_sha256,
        },
        "implementation_sha256": {
            "integrated_v3_auditor": auditor_sha256
        },
        "output_count_at_freeze": {
            "integrated_v2_audit": 0,
            "corruption_suite_gate_audit": 0,
            "integrated_v3_audit": 0,
        },
        "required_predecessor_gates": {
            "integrated_v2_multidimensional_comprehensive_sota": True,
            "postselection_anchor_aggregate_corruption_gate": True,
            "postselection_anchor_all_175_suite_threshold_checks": True,
            "postselection_anchor_suite_gate_validation": True,
        },
        "claim_boundary": {
            "integrated_v2_is_superseded_for_final_claims": True,
            "v2_cannot_substitute_for_suite_stratified_robustness": True,
            "suite_gate_is_pairwise_anchor_evidence_not_vgrf_substitution": True,
            "ece_remains_descriptive_without_frozen_threshold": True,
            "all_required_gates_must_pass_without_dimension_substitution": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--v2-design", type=Path, required=True)
    parser.add_argument("--suite-gate-protocol", type=Path, required=True)
    parser.add_argument("--auditor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    v2_audit = (
        project
        / "results/strict_v4_integrated_comprehensive_sota_v2/audit.json"
    )
    suite_audit = (
        project
        / "results/strict_v4_postselection_corruption_suite_gate_seed7/audit.json"
    )
    value = create_design(
        load(args.v2_design),
        load(args.suite_gate_protocol),
        project_root=str(project),
        v2_design_file_sha256=file_hash(args.v2_design),
        suite_protocol_file_sha256=file_hash(args.suite_gate_protocol),
        auditor_sha256=file_hash(args.auditor),
        v2_audit_count_at_freeze=int(v2_audit.exists()),
        suite_audit_count_at_freeze=int(suite_audit.exists()),
        v3_audit_count_at_freeze=int(args.output.with_name("audit.json").exists()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
