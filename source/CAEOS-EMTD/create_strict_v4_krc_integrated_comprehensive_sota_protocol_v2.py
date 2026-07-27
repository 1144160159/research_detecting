from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_integrated_comprehensive_sota_protocol import (
    create as create_v1,
    verify_implementation as verify_v1_implementation,
)


IMPLEMENTATION = (
    "create_strict_v4_krc_integrated_comprehensive_sota_protocol_v2.py",
    "audit_strict_v4_krc_integrated_comprehensive_sota.py",
    "finalize_strict_v4_krc_downstream_decision_v2.py",
    "scripts/wait_and_run_strict_v4_krc_downstream.sh",
    "scripts/wait_and_run_parrot2025_full_no_decryption_features.sh",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_implementation(
    project_root: Path, relatives: Iterable[str] = IMPLEMENTATION
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC integrated v2 implementation: {relative}"
            )
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def create(
    *,
    project_root: Path,
    downstream_design: Dict[str, Any],
    downstream_design_file_sha256: str,
    observed_audits: int,
    implementation_sha256: Dict[str, str],
) -> Dict[str, Any]:
    compatibility_hashes = {
        **implementation_sha256,
        **verify_v1_implementation(project_root),
    }
    value = create_v1(
        project_root=project_root,
        downstream_design=downstream_design,
        downstream_design_file_sha256=downstream_design_file_sha256,
        observed_audits=observed_audits,
        implementation_sha256=compatibility_hashes,
    )
    value.update(
        {
            "protocol_revision": (
                "integrity_effect_separated_negative_branch_v2"
            ),
            "status": (
                "conditionally_frozen_v2_before_krc_and_branch_outputs"
            ),
            "implementation_sha256": implementation_sha256,
            "negative_branch": {
                "audit_integrity_must_pass": True,
                "effect_gate_may_fail": True,
                "when_krc_effect_gate_fails": (
                    "retain_pairwise_and_permit_only_preregistered_rrc"
                ),
                "krc_downstream_model_execution_required": False,
                "rrc_requires_new_seeds_execution_and_independent_audit": True,
                "does_not_erase_krc_exploration_evidence": True,
            },
            "decision_contract": {
                "audit_integrity_and_effect_are_separate": True,
                "negative_summary_requires_audit_overall_passes_false": True,
                "negative_branch_is_valid_when_structural_checks_all_true": True,
                "decision_schema_compatibility": (
                    "strict_v4_krc_downstream_decision_v1"
                ),
                "decision_revision_required": (
                    "integrity_effect_separated_negative_branch_v2"
                ),
            },
        }
    )
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create(
        project_root=args.project_root.resolve(),
        downstream_design=load(args.downstream_design),
        downstream_design_file_sha256=file_hash(args.downstream_design),
        observed_audits=int(args.output.is_file()),
        implementation_sha256=verify_implementation(
            args.project_root.resolve()
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
