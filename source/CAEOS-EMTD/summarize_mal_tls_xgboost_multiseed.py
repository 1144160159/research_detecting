from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = (
    "accuracy",
    "f1_macro",
    "f1_weighted",
    "balanced_accuracy",
    "ece",
    "nll",
    "training_seconds",
    "inference_samples_per_second",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object: %s" % path)
    return value


def stats(values: list[float]) -> dict[str, float]:
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("metric values must be finite and non-empty")
    return {
        "mean": mean(values),
        "std": pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def analyze(protocol: dict[str, Any], run_root: Path, mc7_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "mal_tls_xgboost_closed_set_protocol_v3":
        raise ValueError("unexpected XGBoost protocol schema")
    if protocol.get("benign_class") != "benign":
        raise ValueError("unexpected benign-class contract")
    if protocol.get("metrics_identity_field") != "seed":
        raise ValueError("unexpected metrics-identity contract")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("XGBoost protocol SHA mismatch")
    seeds = protocol.get("seeds")
    if seeds != [7, 11, 19, 23, 29] or protocol.get("expected_runs") != len(seeds):
        raise ValueError("unexpected seed or run-count contract")
    rows = []
    mc7_rows = []
    for seed in protocol["seeds"]:
        row = read_json(run_root / ("seed%d" % seed) / "metrics.json")
        if row.get("model") != "xgboost":
            raise ValueError("unexpected model for seed %s" % seed)
        if row.get("seed") != seed:
            raise ValueError("seed identity mismatch for seed %s" % seed)
        selection = row.get("selection_evidence", {})
        if selection.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            raise ValueError("test-label selection evidence failed for seed %s" % seed)
        rows.append(row)
        reference = read_json(mc7_root / ("mc5_seed%d" % seed) / "metrics.json")
        if reference.get("seed") not in (None, seed):
            raise ValueError("MC7 seed identity mismatch for seed %s" % seed)
        mc7_rows.append(reference)
    aggregate = {
        metric: stats([float(row[metric]) for row in rows]) for metric in METRICS
    }
    paired = {
        metric: stats(
            [float(row[metric]) - float(reference[metric]) for row, reference in zip(rows, mc7_rows)]
        )
        for metric in ("accuracy", "f1_macro", "f1_weighted", "balanced_accuracy", "ece", "nll")
    }
    return {
        "schema_version": "mal_tls_xgboost_closed_set_multiseed_summary_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "run_count": len(rows),
        "failure_count": len(list(run_root.glob("seed*/failure.json"))),
        "aggregate": aggregate,
        "paired_xgboost_minus_mc7_stable": paired,
        "selection_evidence_passes": True,
        "claim_scope": "closed_set_supporting_evidence_only",
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Mal_TLS2023 XGBoost closed-set baseline",
        "",
        "Five-seed row-stratified supporting evidence; not a strict-v4 open-set result.",
        "",
        "| Metric | Mean | Std | Min | Max | Mean delta vs MC7-Stable |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in ("accuracy", "f1_macro", "f1_weighted", "balanced_accuracy", "ece", "nll"):
        value = result["aggregate"][metric]
        delta = result["paired_xgboost_minus_mc7_stable"][metric]["mean"]
        lines.append(
            "| %s | %.6f | %.6f | %.6f | %.6f | %+.6f |"
            % (metric, value["mean"], value["std"], value["min"], value["max"], delta)
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--mc7-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(read_json(args.protocol), args.run_root, args.mc7_root)
    if result["run_count"] != 5 or result["failure_count"] != 0:
        raise ValueError("XGBoost multiseed baseline is incomplete")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    text = render(result)
    (args.output_dir / "summary.md").write_text(text, encoding="utf-8")
    (args.output_dir / "summary_complete").write_text(
        result["protocol_manifest_sha256"] + "\n", encoding="ascii"
    )
    print(text, end="")


if __name__ == "__main__":
    main()
