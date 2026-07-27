from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"


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


def validate_summary(
    *,
    design: dict[str, Any],
    preparation: dict[str, Any],
    selection: dict[str, Any],
    confirmation: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_vgrf_selected_system_confirmation_design_v1",
        "VGRF system design",
    )
    require_canonical(
        preparation,
        "strict_v4_vgrf_selected_system_preparation_protocol_v1",
        "VGRF system preparation",
    )
    require_canonical(
        selection,
        "strict_v4_final_self_algorithm_selection_v1",
        "final selection",
    )
    require_canonical(
        confirmation,
        "strict_v4_vgrf_confirmation_summary_v1",
        "VGRF confirmation",
    )
    require_canonical(
        summary,
        "strict_v4_vgrf_selected_system_confirmation_summary_v1",
        "VGRF system summary",
    )
    if (
        preparation.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("preparation-to-design binding mismatch")
    if (
        selection.get("selected_algorithm") != VGRF
        or selection.get("vgrf_confirmation_passes") is not True
        or confirmation.get("passes") is not True
        or confirmation.get("selected_algorithm") != VGRF
        or selection.get("confirmation_summary_manifest_sha256")
        != confirmation["manifest_sha256"]
    ):
        raise ValueError("positive VGRF selection binding mismatch")
    bindings = {
        "design_manifest_sha256": design["manifest_sha256"],
        "preparation_protocol_manifest_sha256": preparation[
            "manifest_sha256"
        ],
        "final_selection_manifest_sha256": selection["manifest_sha256"],
        "vgrf_confirmation_summary_manifest_sha256": confirmation[
            "manifest_sha256"
        ],
    }
    for name, expected in bindings.items():
        if summary.get(name) != expected:
            raise ValueError(f"system summary binding mismatch: {name}")
    required = design["required_output"]
    if (
        summary.get("selected_algorithm") != VGRF
        or summary.get("equivalence_block_count")
        != required["equivalence_block_count"]
        or summary.get("comparative_corruption_pair_count")
        != required["comparative_corruption_pair_count"]
        or summary.get("validation", {}).get("passes") is not True
        or summary.get("metric_wise_or_suite_wise_splicing_used")
        is not False
    ):
        raise ValueError("system summary completeness validation failed")
    leakage = summary.get("leakage_validation", {})
    if (
        leakage.get(
            "unknown_or_test_labels_used_for_fitting_selection_"
            "threshold_or_corruption_generation"
        )
        is not False
        or leakage.get("test_labels_used_for_final_metrics_only")
        is not True
    ):
        raise ValueError("system summary leakage validation failed")
    gates = summary.get("gates", {})
    expected_names = set(required["required_system_gates"])
    if set(gates) != expected_names or any(
        type(value) is not bool for value in gates.values()
    ):
        raise ValueError("system summary gate universe mismatch")
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_validation_v1"
        ),
        "status": "complete",
        "selected_algorithm": VGRF,
        "bindings": bindings,
        "equivalence_block_count": summary["equivalence_block_count"],
        "comparative_corruption_pair_count": summary[
            "comparative_corruption_pair_count"
        ],
        "system_gates": gates,
        "all_system_gates_pass": all(gates.values()),
        "summary_is_structurally_admissible": True,
        "claim_boundary": (
            "a structurally valid negative summary completes the branch "
            "but does not authorize comprehensive SOTA"
        ),
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--final-selection", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--system-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    preparation = load(args.preparation)
    project = Path(preparation["project_root"])
    for name, expected in preparation["implementation_sha256"].items():
        if file_hash(project / name) != expected:
            raise ValueError(f"implementation SHA mismatch: {name}")
    result = validate_summary(
        design=load(args.design),
        preparation=preparation,
        selection=load(args.final_selection),
        confirmation=load(args.confirmation_summary),
        summary=load(args.system_summary),
    )
    result["input_file_sha256"] = {
        "design": file_hash(args.design),
        "preparation": file_hash(args.preparation),
        "final_selection": file_hash(args.final_selection),
        "confirmation_summary": file_hash(args.confirmation_summary),
        "system_summary": file_hash(args.system_summary),
    }
    result["validator_implementation_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    result["manifest_sha256"] = canonical_hash(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["all_system_gates_pass"])


if __name__ == "__main__":
    main()
