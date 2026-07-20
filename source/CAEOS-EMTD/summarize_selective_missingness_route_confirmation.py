from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from summarize_missingness_routed_expansion import validate_manifest
from summarize_selective_missingness_route import aggregate, load_pairs


def summarize_confirmation(
    root: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    if manifest.get("evaluation_role") != "frozen_disjoint_confirmation":
        raise ValueError("manifest is not a frozen disjoint confirmation")
    result = aggregate(load_pairs(root, manifest), manifest)
    passed = bool(
        result["gate_results"]["active_modalities_passed"]
        and result["gate_results"]["inactive_modalities_exactly_preserved"]
    )
    result.update(
        {
            "schema_version": "selective_missingness_route_confirmation_summary_v1",
            "state": "confirmed" if passed else "rejected",
            "confirmation_status": "passed" if passed else "failed",
            "development_source_summary_sha256": manifest[
                "development_source_summary_sha256"
            ],
            "confirmation_boundary": {
                "scenarios": manifest["scenarios"],
                "seeds": manifest["seeds"],
                "modalities": manifest["modalities"],
            },
        }
    )
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Selective Missingness Route Frozen Confirmation",
        "",
        f"State: **{result['state']}**. Confirmation: **{result['confirmation_status']}**.",
        "",
        "| Modality | Active | Pairs | Mean F1 gain | Minimum F1 gain | Mean OSCR gain | Minimum OSCR gain | Route range |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for modality, values in result["by_modality"].items():
        lines.append(
            f"| {modality} | {values['active']} | {values['pair_count']} | "
            f"{values['mean_known_macro_f1_gain']:+.4f} | "
            f"{values['minimum_known_macro_f1_gain']:+.4f} | "
            f"{values['mean_oscr_gain']:+.4f} | "
            f"{values['minimum_oscr_gain']:+.4f} | "
            f"{values['minimum_routed_sample_rate']:.4f}-"
            f"{values['maximum_routed_sample_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "The policy and gates were frozen after development and evaluated on disjoint scenarios and seeds.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize the frozen selective missingness route confirmation"
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(args.manifest)
    result = summarize_confirmation(args.root, manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"state": result["state"]}, sort_keys=True))


if __name__ == "__main__":
    main()
