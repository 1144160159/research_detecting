from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_doh_temporal_external_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "doh_temporal_external_protocol_v1":
        raise ValueError("unexpected temporal protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("temporal protocol SHA mismatch")
    rows = []
    for seed in protocol["experiment"]["seeds"]:
        pairwise = load_json(run_root / f"seed{seed}_pairwise" / "metrics.json")
        comparator = load_json(run_root / f"seed{seed}_opendetect" / "metrics.json")
        if pairwise.get("seed") != seed or comparator.get("seed") != seed:
            raise ValueError(f"seed mismatch for {seed}")
        left_split = pairwise.get("split_metadata", {})
        right_split = comparator.get("split_metadata", {})
        if left_split != right_split:
            raise ValueError(f"candidate/comparator split mismatch for seed {seed}")
        if left_split.get("strategy") != "temporal_capture_grouped":
            raise ValueError(f"non-temporal split for seed {seed}")
        if any(left_split.get("group_overlap", {}).values()):
            raise ValueError(f"capture overlap for seed {seed}")
        for ranges in left_split.get("per_class_time_ranges", {}).values():
            if not (
                ranges["train"]["maximum"] <= ranges["validation"]["minimum"]
                <= ranges["test"]["minimum"]
            ):
                raise ValueError(f"unordered time ranges for seed {seed}")
        candidate_report = pairwise["selected_report"]
        comparator_report = comparator["reports"]["opendetect"]
        difference = {
            metric: float(candidate_report[metric] - comparator_report[metric])
            for metric in METRICS
        }
        difference["unknown_fpr95"] *= -1.0
        rows.append({
            "seed": seed,
            "split_fingerprint": left_split["split_fingerprint"]["combined"],
            "candidate": {metric: float(candidate_report[metric]) for metric in METRICS},
            "comparator": {metric: float(comparator_report[metric]) for metric in METRICS},
            "oriented_difference": difference,
        })
    means = {
        metric: float(np.mean([row["oriented_difference"][metric] for row in rows]))
        for metric in METRICS
    }
    nonnegative = sum(value >= 0.0 for value in means.values())
    required = int(protocol["pilot_gate"]["minimum_nonnegative_mean_metric_count"])
    return {
        "schema_version": "doh_temporal_external_summary_v1",
        "protocol_sha256": protocol["manifest_sha256"],
        "run_count": len(rows) * 2,
        "failure_count": 0,
        "paired_rows": rows,
        "mean_oriented_difference": means,
        "nonnegative_mean_metric_count": nonnegative,
        "pilot_gate_passes": nonnegative >= required,
        "claim_tier": "temporal_capture_generalization_pilot",
        "claim_boundary": protocol["claim_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(load_json(args.protocol), args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
