from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from summarize_missingness_routed_expansion import validate_manifest


def load_pairs(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = []
    selected = set(int(value) for value in manifest["selected_routing_modalities"])
    for scenario in manifest["scenarios"]:
        for seed in manifest["seeds"]:
            for modality in manifest["modalities"]:
                path = root / f"{scenario}_seed{seed}_m{modality}.json"
                payload = json.loads(path.read_text(encoding="utf-8"))
                architecture = payload["decision_architecture"]
                if architecture.get("routing_modalities") != sorted(selected):
                    raise ValueError(f"routing modality mismatch: {path}")
                corruption = payload["test_corruption"]
                if (
                    corruption.get("kind") != "field_missing"
                    or int(corruption.get("modality")) != int(modality)
                ):
                    raise ValueError(f"corruption mismatch: {path}")
                pairs.append(
                    {
                        "scenario": scenario,
                        "seed": int(seed),
                        "modality": int(modality),
                        "active": int(modality) in selected,
                        "routed_sample_rate": float(architecture["routed_sample_rate"]),
                        "known_macro_f1_gain": float(
                            payload["dual_path_report"]["known_macro_f1"]
                            - payload["detector_report"]["known_macro_f1"]
                        ),
                        "oscr_gain": float(
                            payload["dual_path_report"]["oscr"]
                            - payload["detector_report"]["oscr"]
                        ),
                    }
                )
    if len(list(root.glob("*.json"))) != manifest["expected_pair_count"]:
        raise ValueError("unexpected selective replay evaluation count")
    return pairs


def aggregate(pairs: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        grouped[pair["modality"]].append(pair)
    by_modality = {
        str(modality): {
            "pair_count": len(rows),
            "active": bool(rows[0]["active"]),
            "mean_known_macro_f1_gain": mean(
                row["known_macro_f1_gain"] for row in rows
            ),
            "minimum_known_macro_f1_gain": min(
                row["known_macro_f1_gain"] for row in rows
            ),
            "mean_oscr_gain": mean(row["oscr_gain"] for row in rows),
            "minimum_oscr_gain": min(row["oscr_gain"] for row in rows),
            "minimum_routed_sample_rate": min(
                row["routed_sample_rate"] for row in rows
            ),
            "maximum_routed_sample_rate": max(
                row["routed_sample_rate"] for row in rows
            ),
        }
        for modality, rows in sorted(grouped.items())
    }
    gates = manifest["gates"]
    active_pass = all(
        values["mean_known_macro_f1_gain"] >= gates["active_mean_gain_minimum"]
        and values["mean_oscr_gain"] >= gates["active_mean_gain_minimum"]
        and values["minimum_known_macro_f1_gain"]
        >= gates["active_per_pair_gain_minimum"]
        and values["minimum_oscr_gain"] >= gates["active_per_pair_gain_minimum"]
        and values["minimum_routed_sample_rate"]
        >= gates["active_routed_sample_rate_minimum"]
        for values in by_modality.values()
        if values["active"]
    )
    tolerance = float(gates["inactive_gain_absolute_tolerance"])
    inactive_pass = all(
        abs(values["mean_known_macro_f1_gain"]) <= tolerance
        and abs(values["minimum_known_macro_f1_gain"]) <= tolerance
        and abs(values["mean_oscr_gain"]) <= tolerance
        and abs(values["minimum_oscr_gain"]) <= tolerance
        and values["maximum_routed_sample_rate"]
        <= gates["inactive_routed_sample_rate_maximum"]
        for values in by_modality.values()
        if not values["active"]
    )
    selected = active_pass and inactive_pass
    return {
        "schema_version": "selective_missingness_route_development_summary_v1",
        "state": "development_candidate_selected" if selected else "rejected",
        "confirmation_status": "not_run",
        "completed_pair_count": len(pairs),
        "expected_pair_count": manifest["expected_pair_count"],
        "selected_routing_modalities": manifest["selected_routing_modalities"],
        "by_modality": by_modality,
        "gate_results": {
            "active_modalities_passed": active_pass,
            "inactive_modalities_exactly_preserved": inactive_pass,
            "development_candidate_selected": selected,
        },
        "confirmation_boundary": manifest.get("confirmation_boundary"),
        "pairs": pairs,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Selective Missingness Route Development Replay",
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
            "This is development reuse after the all-modality candidate was rejected. It cannot support a robustness claim until the frozen disjoint confirmation boundary is run.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize selective missingness routing development replay"
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(args.manifest)
    result = aggregate(load_pairs(args.root, manifest), manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"state": result["state"]}, sort_keys=True))


if __name__ == "__main__":
    main()
