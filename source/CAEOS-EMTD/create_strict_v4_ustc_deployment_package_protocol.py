from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_ustc_deployment_package_design import (
    PAIRWISE,
    VGRF,
    load,
)


def create_protocol(
    design_path: Path,
    selection_path: Path,
    project_root: Path,
    vgrf_confirmation_protocol_path: Path,
    vgrf_confirmation_summary_path: Path,
) -> dict[str, Any]:
    design = load(design_path)
    selection = load(selection_path)
    if (
        design.get("schema_version")
        != "strict_v4_ustc_deployment_package_design_v1"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("invalid USTC deployment design")
    if (
        selection.get("schema_version")
        != design["selection_source"]["schema_version"]
        or selection.get("manifest_sha256") != canonical_hash(selection)
    ):
        raise ValueError("invalid final self-algorithm selection")
    selected = selection.get("selected_algorithm")
    if selected not in design["selection_source"]["allowed_algorithms"]:
        raise ValueError(f"unsupported selected algorithm: {selected}")
    for name, expected in design["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"deployment implementation drift: {name}")

    result_root = Path(design["output_policy"]["result_root"])
    observed = (
        len(list(result_root.rglob("package_record.json")))
        if result_root.exists()
        else 0
    )
    if observed:
        raise ValueError("execution protocol must freeze before package records")

    vgrf_binding = None
    if selected == VGRF:
        confirmation_protocol = load(vgrf_confirmation_protocol_path)
        confirmation_summary = load(vgrf_confirmation_summary_path)
        if (
            confirmation_protocol.get("schema_version")
            != "strict_v4_vgrf_confirmation_protocol_v1"
            or confirmation_protocol.get("manifest_sha256")
            != canonical_hash(confirmation_protocol)
        ):
            raise ValueError("invalid VGRF confirmation protocol")
        if (
            confirmation_summary.get("schema_version")
            != "strict_v4_vgrf_confirmation_summary_v1"
            or confirmation_summary.get("manifest_sha256")
            != canonical_hash(confirmation_summary)
            or confirmation_summary.get("passes") is not True
            or confirmation_summary.get("selected_algorithm") != VGRF
        ):
            raise ValueError("VGRF selection lacks passed full102 confirmation")
        if selection.get("confirmation_summary_manifest_sha256") != (
            confirmation_summary["manifest_sha256"]
        ):
            raise ValueError("selection and VGRF summary binding mismatch")
        if confirmation_protocol["known_only_parameters"] != (
            design["vgrf_policy"]["known_only_parameters"]
        ):
            raise ValueError("VGRF known-only parameters drifted")
        vgrf_binding = {
            "confirmation_protocol_manifest_sha256": confirmation_protocol[
                "manifest_sha256"
            ],
            "confirmation_protocol_file_sha256": file_hash(
                vgrf_confirmation_protocol_path
            ),
            "confirmation_summary_manifest_sha256": confirmation_summary[
                "manifest_sha256"
            ],
            "confirmation_summary_file_sha256": file_hash(
                vgrf_confirmation_summary_path
            ),
            "known_only_parameters": confirmation_protocol[
                "known_only_parameters"
            ],
        }
    elif (
        selected != PAIRWISE
        or selection.get("vgrf_confirmation_passes") is not False
    ):
        raise ValueError("Pairwise selection is inconsistent with VGRF status")

    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_ustc_deployment_package_protocol_v1",
        "status": "frozen_after_final_selection_before_package_artifacts",
        "design_manifest_sha256": design["manifest_sha256"],
        "design_file_sha256": file_hash(design_path),
        "selection": {
            "selected_algorithm": selected,
            "selection_manifest_sha256": selection["manifest_sha256"],
            "selection_file_sha256": file_hash(selection_path),
            "vgrf_confirmation_passes": selection[
                "vgrf_confirmation_passes"
            ],
        },
        "vgrf_binding": vgrf_binding,
        "package_matrix": design["package_matrix"],
        "pairwise_policy": design["pairwise_policy"],
        "parrot_feature_contract": design["parrot_feature_contract"],
        "output_policy": design["output_policy"],
        "execution_policy": design["execution_policy"],
        "implementation_sha256": design["implementation_sha256"],
        "package_records_observed_at_freeze": observed,
        "formal_model_metrics_admitted": 0,
        "external_execution_admitted": False,
        "claim_boundary": design["claim_boundary"],
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument(
        "--vgrf-confirmation-protocol", type=Path, required=True
    )
    parser.add_argument(
        "--vgrf-confirmation-summary", type=Path, required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        args.design,
        args.selection,
        args.project_root,
        args.vgrf_confirmation_protocol,
        args.vgrf_confirmation_summary,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
