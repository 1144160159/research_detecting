from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
METHODS = ("gsc", "mlp_energy", "opendetect")


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _report(payload, method, path):
    report = payload.get("reports", {}).get(method)
    if not isinstance(report, dict):
        raise ValueError("missing report %s: %s" % (method, path))
    result = {metric: float(report[metric]) for metric in METRICS}
    if not all(math.isfinite(value) for value in result.values()):
        raise ValueError("non-finite report %s: %s" % (method, path))
    return result


def _fingerprint(payload):
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    return (
        None
        if value is None
        else json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def _formula_integrity(payload, path):
    if payload.get("schema_version") != "strict_v4_mlp_gsc_v1":
        raise ValueError("unexpected GSC metrics schema: %s" % path)
    selection = payload.get("selection_evidence", {})
    postprocessor = selection.get("postprocessor", {})
    validation = selection.get("validation_mask_diagnostics", {})
    test = selection.get("test_mask_diagnostics", {})
    checks = {
        "method": postprocessor.get("method") == "Gradient Short-Circuit",
        "mask_ratio": float(postprocessor.get("mask_ratio", -1.0)) == 0.05,
        "intervention": postprocessor.get("intervention")
        == "zero_top_absolute_gradient_coordinates",
        "validation_linear_head_diagnostic": validation.get(
            "linear_head_degeneracy_observed"
        )
        is True,
        "test_linear_head_diagnostic": test.get("linear_head_degeneracy_observed")
        is True,
        "label_integrity": selection.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False,
    }
    if not all(checks.values()):
        raise ValueError("GSC formula integrity failed for %s: %s" % (path, checks))
    return checks


def analyze(pilot_root, source_root, opendetect_root, gate):
    protocol = _read(pilot_root / "protocol_manifest.json")
    if gate.get("schema_version") != "strict_v4_mlp_gsc_expansion_gate_v1":
        raise ValueError("unexpected GSC gate schema")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("GSC gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("GSC gate protocol binding mismatch")
    blocks = []
    formula_checks = []
    failures = list(pilot_root.glob("**/failure.json"))
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            paths = {
                "new": pilot_root / suite / (scenario + "_seed7") / "metrics.json",
                "source": source_root / suite / (scenario + "_seed7_mlp") / "metrics.json",
                "external": opendetect_root
                / suite
                / (scenario + "_seed7_opendetect")
                / "metrics.json",
            }
            payloads = {name: _read(path) for name, path in paths.items()}
            fingerprints = [
                _fingerprint(payloads[name]) for name in ("new", "source", "external")
            ]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError("split mismatch for %s/%s" % (suite, scenario))
            formula_checks.append(_formula_integrity(payloads["new"], paths["new"]))
            blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "reports": {
                        "gsc": _report(payloads["new"], "gsc", paths["new"]),
                        "mlp_energy": _report(payloads["source"], "energy", paths["source"]),
                        "opendetect": _report(
                            payloads["external"], "opendetect", paths["external"]
                        ),
                    },
                }
            )
    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / len(
                blocks
            )
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-v for v in values])
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / 4.0
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))
    gains = {}
    for metric in UNKNOWN_METRICS:
        values = []
        for block in blocks:
            candidate = block["reports"]["gsc"][metric]
            reference = block["reports"]["mlp_energy"][metric]
            values.append(
                reference - candidate if metric == "unknown_fpr95" else candidate - reference
            )
        gains[metric] = sum(values) / len(values)
    by_suite = defaultdict(list)
    for block in blocks:
        values = []
        for metric in UNKNOWN_METRICS:
            candidate = block["reports"]["gsc"][metric]
            reference = block["reports"]["mlp_energy"][metric]
            values.append(
                reference - candidate if metric == "unknown_fpr95" else candidate - reference
            )
        by_suite[block["suite"]].append(sum(values) / 4.0)
    suite_gains = {suite: sum(values) / len(values) for suite, values in sorted(by_suite.items())}
    candidate_row = next(row for row in overall if row["method"] == "gsc")
    known_diff = max(
        abs(
            block["reports"]["gsc"]["known_macro_f1"]
            - block["reports"]["mlp_energy"]["known_macro_f1"]
        )
        for block in blocks
    )
    checks = {
        "pilot_runs_complete": len(blocks) == 14 and not failures,
        "split_integrity": True,
        "known_f1_nonregression": known_diff <= 1e-12,
        "formula_integrity": len(formula_checks) == 14,
        "top_two_rank": candidate_row["mean_unknown_metric_rank"] <= 2.0,
        "metric_breadth": sum(value > 0.0 for value in gains.values()) >= 2,
        "overall_gain": sum(gains.values()) / 4.0 > 0.0,
        "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 4
        and min(suite_gains.values()) >= -0.05,
    }
    return {
        "schema_version": "strict_v4_mlp_gsc_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks),
        "failure_count": len(failures),
        "formula_integrity_count": len(formula_checks),
        "linear_head_degeneracy_interpretation": (
            "mask_is_class_fixed_but_formula_faithful_and_first_order_exact"
        ),
        "overall": overall,
        "gsc_vs_mlp_energy_oriented_mean_gains": gains,
        "gsc_vs_mlp_energy_four_metric_mean_gain": sum(gains.values()) / 4.0,
        "gsc_vs_mlp_energy_suite_mean_gains": suite_gains,
        "known_f1_max_absolute_difference": known_diff,
        "expansion_checks": checks,
        "decision": {"expand_gsc_to_full102": all(checks.values())},
    }


def render(result):
    lines = [
        "# Strict-v4 GSC pilot analysis",
        "",
        "Expand GSC to full 102: `%s`."
        % ("YES" if result["decision"]["expand_gsc_to_full102"] else "NO"),
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
    lines.extend(["", "## Expansion gate", ""])
    for name, passed in result["expansion_checks"].items():
        lines.append("- `%s`: %s" % (name, "PASS" if passed else "FAIL"))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(
        args.pilot_root, args.source_root, args.opendetect_root, _read(args.gate)
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render(result)
    (args.output_dir / "analysis.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
