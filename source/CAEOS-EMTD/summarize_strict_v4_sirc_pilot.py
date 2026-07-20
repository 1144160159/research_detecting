from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any, Optional

from scipy.stats import rankdata

from caeos.sirc_posthoc import METHODS as CANDIDATES
from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
METHODS = CANDIDATES + ("mlp_msp", "opendetect")


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root is not an object: %s" % path)
    return payload


def _report(payload: dict[str, Any], method: str, path: Path) -> dict[str, float]:
    report = payload.get("reports", {}).get(method)
    if not isinstance(report, dict):
        raise ValueError("missing report %s: %s" % (method, path))
    result = {metric: float(report[metric]) for metric in METRICS}
    if not all(math.isfinite(value) for value in result.values()):
        raise ValueError("non-finite report %s: %s" % (method, path))
    return result


def _fingerprint(payload: dict[str, Any]) -> Optional[str]:
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    return None if value is None else json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(pilot_root: Path, source_root: Path, opendetect_root: Path, gate: dict[str, Any]) -> dict[str, Any]:
    protocol = _read(pilot_root / "protocol_manifest.json")
    if gate.get("schema_version") != "strict_v4_mlp_sirc_msp_fixed_expansion_gate_v1":
        raise ValueError("unexpected SIRC expansion gate schema")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("SIRC expansion gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("SIRC expansion gate protocol binding mismatch")
    blocks = []
    failures = list(pilot_root.glob("**/failure.json"))
    diagnostics: dict[str, Any] = {}
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            candidate_path = pilot_root / suite / (scenario + "_seed7") / "metrics.json"
            source_path = source_root / suite / (scenario + "_seed7_mlp") / "metrics.json"
            external_path = opendetect_root / suite / (scenario + "_seed7_opendetect") / "metrics.json"
            candidate, source, external = _read(candidate_path), _read(source_path), _read(external_path)
            fingerprints = [_fingerprint(item) for item in (candidate, source, external)]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError("split fingerprint mismatch for %s/%s" % (suite, scenario))
            identity = "%s/%s" % (suite, scenario)
            diagnostics[identity] = candidate["diagnostics"]
            reports = {
                method: _report(candidate, method, candidate_path) for method in CANDIDATES
            }
            reports["mlp_msp"] = _report(source, "msp", source_path)
            reports["opendetect"] = _report(external, "opendetect", external_path)
            blocks.append({"suite": suite, "scenario": scenario, "reports": reports})
    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / len(blocks)
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-value for value in values], method="average")
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / len(UNKNOWN_METRICS)
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))

    gains_by_candidate: dict[str, Any] = {}
    checks_by_candidate: dict[str, Any] = {}
    for candidate_method in CANDIDATES:
        oriented_gains = {
            metric: sum(
                _oriented_gain(block["reports"][candidate_method][metric], block["reports"]["mlp_msp"][metric], metric)
                for block in blocks
            ) / len(blocks)
            for metric in UNKNOWN_METRICS
        }
        suite_values: dict[str, list[float]] = defaultdict(list)
        for block in blocks:
            suite_values[block["suite"]].append(sum(
                _oriented_gain(block["reports"][candidate_method][metric], block["reports"]["mlp_msp"][metric], metric)
                for metric in UNKNOWN_METRICS
            ) / len(UNKNOWN_METRICS))
        suite_gains = {suite: sum(values) / len(values) for suite, values in sorted(suite_values.items())}
        candidate_row = next(row for row in overall if row["method"] == candidate_method)
        known_f1_max_difference = max(
            abs(block["reports"][candidate_method]["known_macro_f1"] - block["reports"]["mlp_msp"]["known_macro_f1"])
            for block in blocks
        )
        nondegenerate = all(
            float(item[candidate_method][key]) > 1e-12
            for item in diagnostics.values()
            for key in ("validation_risk_std", "test_risk_std", "validation_auxiliary_std", "test_auxiliary_std")
        )
        checks = {
            "pilot_runs_complete": len(blocks) == 14 and not failures,
            "split_integrity": True,
            "known_f1_nonregression": known_f1_max_difference <= 1e-12,
            "nondegenerate_score": nondegenerate,
            "top_two_rank": candidate_row["mean_unknown_metric_rank"] <= 2.0,
            "metric_breadth": sum(value > 0.0 for value in oriented_gains.values()) >= 2,
            "overall_gain": sum(oriented_gains.values()) / len(oriented_gains) > 0.0,
            "oscr_gain": oriented_gains["oscr"] > 0.0,
            "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 4 and min(suite_gains.values()) >= -0.05,
        }
        gains_by_candidate[candidate_method] = {
            "oriented_mean_gains_vs_mlp_msp": oriented_gains,
            "four_metric_mean_gain_vs_mlp_msp": sum(oriented_gains.values()) / len(oriented_gains),
            "suite_mean_gains_vs_mlp_msp": suite_gains,
            "known_f1_max_absolute_difference": known_f1_max_difference,
        }
        checks_by_candidate[candidate_method] = checks
    passing = [method for method in CANDIDATES if all(checks_by_candidate[method].values())]
    return {
        "schema_version": "strict_v4_mlp_sirc_msp_fixed_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks), "failure_count": len(failures), "overall": overall,
        "score_diagnostics": diagnostics, "candidate_gains": gains_by_candidate,
        "expansion_checks": checks_by_candidate,
        "decision": {"expand_sirc_to_full102": bool(passing), "expand_methods": passing},
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 SIRC-MSP-Fixed pilot analysis", "",
        "Expand any SIRC variant to full 102: `%s`." % ("YES" if result["decision"]["expand_sirc_to_full102"] else "NO"),
        "Passing variants: `%s`." % (", ".join(result["decision"]["expand_methods"]) or "none"), "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append("| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | {unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | {mean_unknown_metric_rank:.2f} |".format(**row))
    for method in CANDIDATES:
        lines.extend(["", "## %s expansion gate" % method, ""])
        for name, passed in result["expansion_checks"][method].items():
            lines.append("- `%s`: %s" % (name, "PASS" if passed else "FAIL"))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.pilot_root, args.source_root, args.opendetect_root, _read(args.gate))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rendered = render(result)
    (args.output_dir / "analysis.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
