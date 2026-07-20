from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_training_full102_expansion_protocol import file_hash, read_json
from summarize_strict_v4_external_training_pilot import (
    METRICS,
    UNKNOWN_METRICS,
    fingerprint,
    no_test_label_fit,
    report,
)


def analyze(
    expansion_root: Path,
    source_root: Path,
    opendetect_root: Path,
) -> dict[str, Any]:
    protocol_path = expansion_root / "protocol_manifest.json"
    protocol = read_json(protocol_path)
    if protocol.get("schema_version") != "strict_v4_training_full102_expansion_protocol_v1":
        raise ValueError("unexpected full102 expansion protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("full102 expansion protocol SHA mismatch")
    methods = tuple(protocol.get("methods", []))
    registry = protocol.get("scenario_registry", {})
    if not methods or sum(len(items) for items in registry.values()) != 102:
        raise ValueError("invalid full102 expansion scope")

    blocks: list[dict[str, Any]] = []
    split_checks = 0
    no_leak_checks = 0
    for suite, scenarios in registry.items():
        for scenario in scenarios:
            source_path = source_root / suite / (scenario + "_seed7_mlp") / "metrics.json"
            external_path = (
                opendetect_root / suite / (scenario + "_seed7_opendetect") / "metrics.json"
            )
            source = read_json(source_path)
            external = read_json(external_path)
            candidates = {}
            for method in methods:
                path = expansion_root / suite / (scenario + "_seed7_" + method) / "metrics.json"
                candidates[method] = (read_json(path), path)
            fingerprints = [fingerprint(source), fingerprint(external)] + [
                fingerprint(candidates[method][0]) for method in methods
            ]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError("split fingerprint mismatch: %s/%s" % (suite, scenario))
            split_checks += 1
            if not all(no_test_label_fit(candidates[method][0], method, protocol) for method in methods):
                raise ValueError("unknown/test label fitting detected: %s/%s" % (suite, scenario))
            no_leak_checks += 1
            reports = {"opendetect": report(external, "opendetect", external_path)}
            for method in methods:
                payload, path = candidates[method]
                reports[method] = report(payload, method, path)
            blocks.append({"suite": suite, "scenario": scenario, "reports": reports})

    failures = sorted(str(path) for path in expansion_root.glob("*/*/failure.json"))
    overall = []
    for method in ("opendetect",) + methods:
        row: dict[str, Any] = {"method": method}
        for metric in METRICS:
            value = sum(block["reports"][method][metric] for block in blocks) / len(blocks)
            if not math.isfinite(value):
                raise ValueError("non-finite aggregate metric: %s/%s" % (method, metric))
            row[metric] = value
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranked = rankdata(
            values if metric == "unknown_fpr95" else [-value for value in values],
            method="average",
        )
        for row, rank in zip(overall, ranked):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / len(
            UNKNOWN_METRICS
        )
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))

    expected_runs = 102 * len(methods)
    passes = (
        len(blocks) == 102
        and not failures
        and split_checks == 102
        and no_leak_checks == 102
    )
    return {
        "schema_version": "strict_v4_training_full102_expansion_analysis_v1",
        "status": "complete" if passes else "failed",
        "group": protocol["group"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "methods": list(methods),
        "scenario_count": len(blocks),
        "method_run_count": len(blocks) * len(methods),
        "failure_count": len(failures),
        "overall": overall,
        "validation": {
            "passes": passes,
            "scenario_count": len(blocks),
            "method_run_count": len(blocks) * len(methods),
            "expected_method_run_count": expected_runs,
            "split_fingerprint_checks": split_checks,
            "no_leak_checks": no_leak_checks,
            "failure_count": len(failures),
        },
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 training baseline full102 expansion",
        "",
        "Group: `%s`; methods: `%s`." % (result["group"], ", ".join(result["methods"])),
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | {unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | {mean_unknown_metric_rank:.2f} |".format(
                **row
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expansion-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pilot-result-root", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.expansion_root, args.source_root, args.opendetect_root)
    if not result["validation"]["passes"]:
        raise ValueError("full102 expansion validation failed")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    analysis_path = args.output_dir / "analysis.json"
    analysis_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    args.pilot_result_root.mkdir(parents=True, exist_ok=True)
    (args.pilot_result_root / "full102_expansion_complete").write_text(
        file_hash(analysis_path) + "\n", encoding="ascii"
    )
    print(render(result), end="")


if __name__ == "__main__":
    main()
