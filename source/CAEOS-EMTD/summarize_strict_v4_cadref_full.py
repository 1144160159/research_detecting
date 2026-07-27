from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_klm_matrix import sha256_file
from summarize_strict_v4_cadref_pilot import (
    CANDIDATES,
    METHODS,
    METRICS,
    UNKNOWN_METRICS,
    _fingerprint,
    _formula_integrity,
    _oriented,
    _read,
    _report,
)


def analyze(full_root, source_root, opendetect_root, pilot_analysis):
    protocol = _read(full_root / "protocol_manifest.json")
    matrix = _read(full_root / "matrix_summary.json")
    if protocol.get("schema_version") != "strict_v4_mlp_cadref_family_protocol_v1":
        raise ValueError("unexpected CADRef full protocol schema")
    if protocol.get("mode") != "full" or protocol.get("expected_runs") != 102:
        raise ValueError("CADRef full analysis requires 102 scenarios")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("CADRef full protocol SHA mismatch")
    if (
        matrix.get("schema_version") != "strict_v4_mlp_cadref_family_matrix_v1"
        or matrix.get("status") != "complete"
        or matrix.get("completed_runs") != 102
        or matrix.get("failures") != 0
        or matrix.get("protocol_manifest_sha256") != protocol["manifest_sha256"]
    ):
        raise ValueError("CADRef full matrix summary is incomplete")
    if pilot_analysis.get("schema_version") != "strict_v4_mlp_cadref_family_pilot_analysis_v1":
        raise ValueError("unexpected CADRef pilot analysis schema")
    expanded = pilot_analysis.get("decision", {}).get("expand_methods_to_full102", [])
    if not expanded or not set(expanded).issubset(CANDIDATES):
        raise ValueError("CADRef full matrix lacks an eligible pilot method")

    blocks = []
    formula_count = 0
    nonconstant = {method: 0 for method in CANDIDATES}
    failures = list(full_root.glob("**/failure.json"))
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            paths = {
                "new": full_root / suite / f"{scenario}_seed7" / "metrics.json",
                "source": source_root / suite / f"{scenario}_seed7_mlp" / "metrics.json",
                "external": opendetect_root
                / suite
                / f"{scenario}_seed7_opendetect"
                / "metrics.json",
            }
            payloads = {name: _read(path) for name, path in paths.items()}
            fingerprints = [_fingerprint(payloads[name]) for name in ("new", "source", "external")]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError(f"split mismatch for {suite}/{scenario}")
            _, item_nonconstant = _formula_integrity(payloads["new"], paths["new"])
            formula_count += 1
            for method in CANDIDATES:
                nonconstant[method] += int(item_nonconstant[method])
            blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "reports": {
                        "caref": _report(payloads["new"], "caref", paths["new"]),
                        "cadref_energy_fixed": _report(
                            payloads["new"], "cadref_energy_fixed", paths["new"]
                        ),
                        "mlp_energy": _report(payloads["source"], "energy", paths["source"]),
                        "opendetect": _report(
                            payloads["external"], "opendetect", paths["external"]
                        ),
                    },
                }
            )
    if len(blocks) != 102 or failures or formula_count != 102:
        raise ValueError("CADRef full artifact coverage is incomplete")

    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / 102.0
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-v for v in values])
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / 4.0
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))

    candidates = {}
    for method in CANDIDATES:
        gains = {
            metric: sum(
                _oriented(
                    block["reports"][method][metric],
                    block["reports"]["mlp_energy"][metric],
                    metric,
                )
                for block in blocks
            )
            / 102.0
            for metric in UNKNOWN_METRICS
        }
        by_suite = defaultdict(list)
        for block in blocks:
            by_suite[block["suite"]].append(
                sum(
                    _oriented(
                        block["reports"][method][metric],
                        block["reports"]["mlp_energy"][metric],
                        metric,
                    )
                    for metric in UNKNOWN_METRICS
                )
                / 4.0
            )
        candidates[method] = {
            "vs_mlp_energy_oriented_mean_gains": gains,
            "vs_mlp_energy_four_metric_mean_gain": sum(gains.values()) / 4.0,
            "vs_mlp_energy_suite_mean_gains": {
                suite: sum(values) / len(values)
                for suite, values in sorted(by_suite.items())
            },
            "known_f1_max_absolute_difference": max(
                abs(
                    block["reports"][method]["known_macro_f1"]
                    - block["reports"]["mlp_energy"]["known_macro_f1"]
                )
                for block in blocks
            ),
        }
    result = {
        "schema_version": "strict_v4_mlp_cadref_family_full_analysis_v1",
        "status": "complete",
        "full_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_protocol_manifest_sha256": pilot_analysis["pilot_protocol_manifest_sha256"],
        "pilot_gate_manifest_sha256": pilot_analysis["expansion_gate_manifest_sha256"],
        "pilot_expanded_methods": expanded,
        "scenario_count": 102,
        "failure_count": 0,
        "formula_integrity_count": formula_count,
        "nonconstant_score_counts": nonconstant,
        "overall": overall,
        "candidates": candidates,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "test_labels_used_for_full_development_metrics_only": True,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render(result):
    lines = [
        "# Strict-v4 CARef/CADRef full102 analysis",
        "",
        "Full coverage: `102/102`, failures: `0`.",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | "
            "{unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | "
            "{mean_unknown_metric_rank:.2f} |".format(**row)
        )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(
        args.full_root,
        args.source_root,
        args.opendetect_root,
        _read(args.pilot_analysis),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "full_analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render(result)
    (args.output_dir / "full_analysis.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
