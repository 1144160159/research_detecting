from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


PAIRWISE = "caeos_pairwise"
VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"
SYSTEM_GATES = (
    "formal_same_hardware_efficiency_characterized",
    "selected_runtime_equivalence_all_204_blocks",
    "selected_runtime_internal_deployment_gate",
    "efficiency_superiority_all_required_native_metrics",
    "candidate_graceful_degradation_gate",
    "comparative_corruption_robustness_against_opendetect",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def selected_system_gates(
    *,
    selected: str,
    base: dict[str, Any],
    selected_system: Optional[dict[str, Any]],
) -> tuple[dict[str, bool], str]:
    if selected == PAIRWISE:
        if selected_system is not None:
            raise ValueError(
                "Pairwise path must not substitute a selected-system summary"
            )
        if base.get("selected_algorithm") != PAIRWISE:
            raise ValueError("Pairwise base readiness identity mismatch")
        return (
            {
                name: base.get("gates", {}).get(name) is True
                for name in SYSTEM_GATES
            },
            "pairwise_base_readiness",
        )
    if selected != VGRF:
        raise ValueError(f"unsupported selected algorithm: {selected}")
    if selected_system is None:
        raise ValueError("VGRF selected-system evidence is required")
    require_canonical(
        selected_system,
        "strict_v4_vgrf_selected_system_confirmation_summary_v1",
        "VGRF selected-system summary",
    )
    if (
        selected_system.get("selected_algorithm") != VGRF
        or selected_system.get("validation", {}).get("passes") is not True
        or selected_system.get("equivalence_block_count") != 204
        or selected_system.get("comparative_corruption_pair_count")
        != 1530
    ):
        raise ValueError("VGRF selected-system evidence is incomplete")
    return (
        {
            name: selected_system.get("gates", {}).get(name) is True
            for name in SYSTEM_GATES
        },
        "vgrf_selected_system_confirmation",
    )


def create_audit(
    *,
    protocol: dict[str, Any],
    base: dict[str, Any],
    compatibility: dict[str, Any],
    selection: dict[str, Any],
    reconfirmation: Optional[dict[str, Any]],
    not_required: Optional[dict[str, Any]],
    external: dict[str, Any],
    selected_system: Optional[dict[str, Any]],
) -> dict[str, Any]:
    require_canonical(
        protocol,
        "strict_v4_integrated_comprehensive_sota_design_v2",
        "integrated SOTA v2 design",
    )
    require_canonical(
        base, "strict_v4_final_paper_readiness_audit_v4", "base readiness"
    )
    require_canonical(
        compatibility,
        "strict_v4_post30_supersession_compatibility_audit_v1",
        "post-30 compatibility",
    )
    require_canonical(
        selection,
        "strict_v4_final_self_algorithm_selection_v1",
        "final self-algorithm selection",
    )
    require_canonical(
        external,
        "gpu_external_dataset_evaluation_summary_v1",
        "external summary",
    )
    if (
        compatibility.get("post30_baseline_coverage_compatible")
        is not True
        or base.get("gates", {}).get(
            "post30_baseline_coverage_complete"
        )
        is not True
    ):
        raise ValueError("post-30 baseline coverage is not admissible")
    selected = selection["selected_algorithm"]
    if reconfirmation is not None:
        require_canonical(
            reconfirmation,
            "strict_v4_selected_external_reconfirmation_summary_v1",
            "selected external reconfirmation",
        )
        seven_suite = (
            reconfirmation.get(
                "strict_seven_suite_accuracy_sota_allowed"
            )
            is True
            and reconfirmation.get("decision", {}).get("passes") is True
            and reconfirmation.get("validation", {}).get("passes") is True
            and reconfirmation.get("selected_algorithm") == selected
        )
        reconfirmation_status = "completed"
    else:
        if not_required is None:
            raise ValueError(
                "reconfirmation result or not-required record is required"
            )
        require_canonical(
            not_required,
            "strict_v4_selected_external_reconfirmation_not_required_v1",
            "selected external reconfirmation not-required record",
        )
        seven_suite = False
        reconfirmation_status = "not_required_without_claim_upgrade"
    system, system_source = selected_system_gates(
        selected=selected,
        base=base,
        selected_system=selected_system,
    )
    gates = {
        "post30_baseline_coverage_complete": True,
        "selected_algorithm_consistent_across_new_confirmations": (
            external.get("selected_algorithm") == selected
            and (
                reconfirmation is None
                or reconfirmation.get("selected_algorithm") == selected
            )
        ),
        "strict_seven_suite_accuracy_sota_reconfirmed": seven_suite,
        "two_external_dataset_confirmation_passes": (
            external.get("expanded_external_accuracy_confirmation_passes")
            is True
            and external.get("validation", {}).get("passes") is True
        ),
        "selected_algorithm_system_evidence_consistent": all(
            system.values()
        ),
        **system,
    }
    passes = all(gates.values())
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_integrated_comprehensive_sota_audit_v2"
        ),
        "status": "complete",
        "selected_algorithm": selected,
        "selected_system_evidence_source": system_source,
        "reconfirmation_status": reconfirmation_status,
        "gates": gates,
        "multidimensional_comprehensive_sota_allowed": passes,
        "claim_tier": (
            "multidimensional_comprehensive_sota_with_algorithm_"
            "consistent_system_evidence"
            if passes
            else "comprehensive_sota_not_established"
        ),
        "claim_boundary": {
            "integrated_v1_is_superseded_for_final_claims": True,
            "pairwise_system_evidence_cannot_be_inherited_by_vgrf": True,
            "all_required_gates_must_pass_without_dimension_substitution": True,
        },
        "required_follow_up": [
            name for name, passed in gates.items() if not passed
        ],
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--base-readiness", type=Path, required=True)
    parser.add_argument("--post30-compatibility", type=Path, required=True)
    parser.add_argument("--final-selection", type=Path, required=True)
    parser.add_argument("--reconfirmation-root", type=Path, required=True)
    parser.add_argument("--external-summary", type=Path, required=True)
    parser.add_argument("--selected-system-summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    design = load(args.design)
    project = Path(design["project_root"])
    for name, expected in design["implementation_sha256"].items():
        if file_hash(project / name) != expected:
            raise ValueError(f"implementation SHA mismatch: {name}")
    summary_path = args.reconfirmation_root / "summary.json"
    not_required_path = args.reconfirmation_root / "not_required.json"
    reconfirmation = load(summary_path) if summary_path.is_file() else None
    not_required = (
        load(not_required_path) if not_required_path.is_file() else None
    )
    selected_system = (
        load(args.selected_system_summary)
        if args.selected_system_summary is not None
        else None
    )
    value = create_audit(
        protocol=design,
        base=load(args.base_readiness),
        compatibility=load(args.post30_compatibility),
        selection=load(args.final_selection),
        reconfirmation=reconfirmation,
        not_required=not_required,
        external=load(args.external_summary),
        selected_system=selected_system,
    )
    value["input_file_sha256"] = {
        "design": file_hash(args.design),
        "base_readiness": file_hash(args.base_readiness),
        "post30_compatibility": file_hash(args.post30_compatibility),
        "final_selection": file_hash(args.final_selection),
        "selected_external_reconfirmation": file_hash(
            summary_path if summary_path.is_file() else not_required_path
        ),
        "external_summary": file_hash(args.external_summary),
        "selected_system_summary": (
            file_hash(args.selected_system_summary)
            if args.selected_system_summary is not None
            else None
        ),
    }
    value["audit_implementation_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output.parent / "audit_complete").touch()
    print(value["claim_tier"])


if __name__ == "__main__":
    main()
