from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


def canonical_manifest_hash(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    encoded = json.dumps(
        core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("manifest_sha256") != canonical_manifest_hash(payload):
        raise ValueError("expansion manifest internal SHA mismatch")
    expected = (
        len(payload["scenarios"])
        * len(payload["seeds"])
        * len(payload["modalities"])
    )
    if payload.get("expected_pair_count") != expected:
        raise ValueError("expansion expected_pair_count is inconsistent")
    return payload


def load_pairs(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = []
    for scenario in manifest["scenarios"]:
        for seed in manifest["seeds"]:
            for modality in manifest["modalities"]:
                path = root / f"{scenario}_seed{seed}_m{modality}.json"
                if not path.is_file():
                    raise ValueError(f"missing routed evaluation: {path}")
                payload = json.loads(path.read_text(encoding="utf-8"))
                architecture = payload.get("decision_architecture", {})
                if architecture.get("prediction_routing") != "missingness":
                    raise ValueError(f"invalid prediction routing: {path}")
                if payload.get("detector_ranking_metrics_exactly_preserved") is not True:
                    raise ValueError(f"detector ranking invariant failed: {path}")
                corruption = payload.get("test_corruption", {})
                if (
                    corruption.get("kind") != "field_missing"
                    or int(corruption.get("modality")) != int(modality)
                    or abs(float(corruption.get("severity")) - 0.5) > 1e-12
                ):
                    raise ValueError(f"corruption identity mismatch: {path}")
                pairs.append(
                    {
                        "scenario": scenario,
                        "seed": int(seed),
                        "modality": int(modality),
                        "routed_sample_rate": float(
                            architecture["routed_sample_rate"]
                        ),
                        "known_macro_f1_gain": float(
                            payload["dual_path_report"]["known_macro_f1"]
                            - payload["detector_report"]["known_macro_f1"]
                        ),
                        "oscr_gain": float(
                            payload["dual_path_report"]["oscr"]
                            - payload["detector_report"]["oscr"]
                        ),
                        "detector_report": payload["detector_report"],
                        "dual_path_report": payload["dual_path_report"],
                    }
                )
    extras = list(root.glob("*.json"))
    if len(extras) != manifest["expected_pair_count"]:
        raise ValueError(
            f"unexpected evaluation count: {len(extras)} != {manifest['expected_pair_count']}"
        )
    return pairs


def aggregate(pairs: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        grouped[pair["modality"]].append(pair)

    def summary(rows: list[dict[str, Any]]) -> dict[str, float]:
        f1 = [row["known_macro_f1_gain"] for row in rows]
        oscr = [row["oscr_gain"] for row in rows]
        routing = [row["routed_sample_rate"] for row in rows]
        return {
            "pair_count": len(rows),
            "mean_known_macro_f1_gain": mean(f1),
            "median_known_macro_f1_gain": median(f1),
            "minimum_known_macro_f1_gain": min(f1),
            "mean_oscr_gain": mean(oscr),
            "median_oscr_gain": median(oscr),
            "minimum_oscr_gain": min(oscr),
            "mean_routed_sample_rate": mean(routing),
            "minimum_routed_sample_rate": min(routing),
        }

    overall = summary(pairs)
    by_modality = {
        str(modality): summary(rows) for modality, rows in sorted(grouped.items())
    }
    gates = manifest["gates"]
    pair_pass = all(
        pair["known_macro_f1_gain"]
        >= float(gates["per_pair_gain_minimum"]) - 1e-12
        and pair["oscr_gain"] >= float(gates["per_pair_gain_minimum"]) - 1e-12
        and pair["routed_sample_rate"]
        >= float(gates["routed_sample_rate_minimum"]) - 1e-12
        for pair in pairs
    )
    mean_pass = (
        overall["mean_known_macro_f1_gain"]
        >= float(gates["overall_mean_gain_minimum"]) - 1e-12
        and overall["mean_oscr_gain"]
        >= float(gates["overall_mean_gain_minimum"]) - 1e-12
    )
    modality_pass = all(
        values["mean_known_macro_f1_gain"]
        >= float(gates["per_modality_mean_gain_minimum"]) - 1e-12
        and values["mean_oscr_gain"]
        >= float(gates["per_modality_mean_gain_minimum"]) - 1e-12
        for values in by_modality.values()
    )
    confirmed = pair_pass and mean_pass and modality_pass
    return {
        "schema_version": "missingness_routed_expansion_summary_v1",
        "state": "confirmed" if confirmed else "rejected",
        "scope": "three scenarios by three seeds by three field-missing modalities",
        "expected_pair_count": manifest["expected_pair_count"],
        "completed_pair_count": len(pairs),
        "failure_count": 0,
        "unknown_or_test_labels_used_for_training_selection_or_threshold": False,
        "unknown_test_labels_used_for_confirmation_evaluation_only": True,
        "overall": overall,
        "by_modality": by_modality,
        "gate_results": {
            "all_pairs_passed": pair_pass,
            "overall_mean_passed": mean_pass,
            "all_modality_means_passed": modality_pass,
            "confirmed": confirmed,
        },
        "pairs": pairs,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Missingness-routed Dual-path Expansion",
        "",
        f"State: **{result['state']}** ({result['completed_pair_count']}/{result['expected_pair_count']})",
        "",
        "| Modality | Pairs | Mean F1 gain | Minimum F1 gain | Mean OSCR gain | Minimum OSCR gain | Minimum routed rate |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for modality, values in result["by_modality"].items():
        lines.append(
            "| {m} | {n} | {f1:+.4f} | {minf1:+.4f} | {oscr:+.4f} | {minoscr:+.4f} | {route:.4f} |".format(
                m=modality,
                n=values["pair_count"],
                f1=values["mean_known_macro_f1_gain"],
                minf1=values["minimum_known_macro_f1_gain"],
                oscr=values["mean_oscr_gain"],
                minoscr=values["minimum_oscr_gain"],
                route=values["minimum_routed_sample_rate"],
            )
        )
    lines.extend(
        [
            "",
            "This confirmation uses test labels only for frozen post-hoc evaluation; training, routing, risk selection and thresholds remain label-isolated.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the routed robustness expansion")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(args.manifest)
    result = aggregate(load_pairs(args.root, manifest), manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    args.markdown_output.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"state": result["state"], **result["overall"]}, sort_keys=True))


if __name__ == "__main__":
    main()
