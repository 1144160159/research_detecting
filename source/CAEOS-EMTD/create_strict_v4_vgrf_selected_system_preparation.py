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


def create_preparation(
    *,
    project_root: Path,
    design: dict[str, Any],
    design_file_sha256: str,
    implementation_sha256: dict[str, str],
    observed_outputs: int,
) -> dict[str, Any]:
    if (
        design.get("schema_version")
        != "strict_v4_vgrf_selected_system_confirmation_design_v1"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("invalid VGRF selected-system design")
    if observed_outputs != 0:
        raise ValueError("preparation must freeze before system outputs")
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_preparation_protocol_v1"
        ),
        "status": (
            "frozen_before_final_selection_execution_protocol_and_outputs"
        ),
        "project_root": str(project_root.resolve()),
        "design_manifest_sha256": design["manifest_sha256"],
        "design_file_sha256": design_file_sha256,
        "implementation_sha256": implementation_sha256,
        "branch_behavior": {
            "pairwise": "write_canonical_not_required_and_complete",
            "vgrf": (
                "write_execution_required_then_wait_for_design_bound_"
                "system_summary"
            ),
        },
        "required_future_execution_implementations": [
            "execution_protocol_creator",
            "seed317_source_runner",
            "vgrf_and_opendetect_runtime_capture",
            "same_hardware_benchmark_runner",
            "comparative_corruption_runner",
            "system_summarizer",
        ],
        "claim_boundary": {
            "preparation_does_not_create_effect_metrics": True,
            "branch_completion_accepts_structurally_valid_negative_results": True,
            "only_all_positive_system_gates_authorize_comprehensive_sota": True,
        },
        "system_outputs_observed_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    observed = len(
        [
            path
            for path in args.result_root.glob("*")
            if path.is_file()
            and path.name
            in {
                "summary.json",
                "validation.json",
                "execution_required.json",
                "not_required.json",
            }
        ]
    )
    names = (
        "create_strict_v4_vgrf_selected_system_preparation.py",
        "validate_strict_v4_vgrf_selected_system_summary.py",
        "scripts/wait_and_validate_strict_v4_vgrf_selected_system.sh",
        "create_strict_v4_vgrf_selected_system_design.py",
    )
    value = create_preparation(
        project_root=project,
        design=load(args.design),
        design_file_sha256=file_hash(args.design),
        implementation_sha256={
            name: file_hash(project / name) for name in names
        },
        observed_outputs=observed,
    )
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
