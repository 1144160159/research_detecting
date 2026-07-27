from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any, Optional

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
UNKNOWN_METRICS = METRICS[1:]
CANDIDATES = ("klnd1", "klnd2", "klnd3")
METHODS = CANDIDATES + ("mlp_msp", "mlp_energy", "opendetect")


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root is not an object: %s" % path)
    return payload


def _report(
    payload: dict[str, Any], method: str, path: Path
) -> dict[str, float]:
    report = payload.get("reports", {}).get(method)
    if not isinstance(report, dict):
        raise ValueError("missing report %s: %s" % (method, path))
    result = {metric: float(report[metric]) for metric in METRICS}
    if not all(math.isfinite(value) for value in result.values()):
        raise ValueError("non-finite report %s: %s" % (method, path))
    return result


def _fingerprint(payload: dict[str, Any]) -> Optional[str]:
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    return (
        None
        if value is None
        else json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    )


def _oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return (
        reference - candidate
        if metric == "unknown_fpr95"
        else candidate - reference
    )


def analyze(
    pilot_root: Path,
    source_root: Path,
    opendetect_root: Path,
    gate: dict[str, Any],
) -> dict[str, Any]:
    protocol = _read(pilot_root / "protocol_manifest.json")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("k-LND pilot protocol SHA mismatch")
    if gate.get("schema_version") != "strict_v4_mlp_klnd_expansion_gate_v1":
        raise ValueError("unexpected k-LND expansion gate schema")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("k-LND expansion gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get(
        "manifest_sha256"
    ):
        raise ValueError("k-LND expansion gate protocol binding mismatch")
    blocks = []
    failures = list(pilot_root.glob("**/failure.json"))
    support_checks = {}
    diagnostics = {}
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            candidate_path = (
                pilot_root / suite / (scenario + "_seed7") / "metrics.json"
            )
            source_path = (
                source_root
                / suite
                / (scenario + "_seed7_mlp")
                / "metrics.json"
            )
            external_path = (
                opendetect_root
                / suite
                / (scenario + "_seed7_opendetect")
                / "metrics.json"
            )
            candidate = _read(candidate_path)
            source = _read(source_path)
            external = _read(external_path)
            if candidate.get("selection_evidence", {}).get(
                "unknown_or_test_labels_used_for_fitting_or_selection"
            ) is not False:
                raise ValueError(
                    "k-LND leakage invariant failed for %s/%s"
                    % (suite, scenario)
                )
            fingerprints = [
                _fingerprint(item) for item in (candidate, source, external)
            ]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError(
                    "split fingerprint mismatch for %s/%s" % (suite, scenario)
                )
            evidence = candidate["selection_evidence"]["klnd"]
            identity = "%s/%s" % (suite, scenario)
            support_checks[identity] = {
                "train_correct_min": min(evidence["train_correct_counts"]),
                "validation_correct_min": min(
                    evidence["validation_correct_counts"]
                ),
                "class_count": evidence["class_count"],
            }
            diagnostics[identity] = {
                method: {
                    "validation_risk_std": float(
                        candidate["diagnostics"][method]["validation_risk_std"]
                    ),
                    "test_risk_std": float(
                        candidate["diagnostics"][method]["test_risk_std"]
                    ),
                }
                for method in CANDIDATES
            }
            reports = {
                method: _report(candidate, method, candidate_path)
                for method in CANDIDATES
            }
            reports.update(
                {
                    "mlp_msp": _report(source, "msp", source_path),
                    "mlp_energy": _report(source, "energy", source_path),
                    "opendetect": _report(
                        external, "opendetect", external_path
                    ),
                }
            )
            blocks.append(
                {"suite": suite, "scenario": scenario, "reports": reports}
            )
    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(
                block["reports"][method][metric] for block in blocks
            ) / len(blocks)
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(
            values if metric == "unknown_fpr95" else [-value for value in values],
            method="average",
        )
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(
            row["metric_ranks"].values()
        ) / len(UNKNOWN_METRICS)
    overall.sort(
        key=lambda row: (row["mean_unknown_metric_rank"], row["method"])
    )
    selected = min(
        (row for row in overall if row["method"] in CANDIDATES),
        key=lambda row: (row["mean_unknown_metric_rank"], row["method"]),
    )["method"]
    oriented_gains = {}
    for metric in UNKNOWN_METRICS:
        gains = [
            _oriented_gain(
                block["reports"][selected][metric],
                block["reports"]["mlp_energy"][metric],
                metric,
            )
            for block in blocks
        ]
        oriented_gains[metric] = sum(gains) / len(gains)
    by_suite = defaultdict(list)
    for block in blocks:
        gains = [
            _oriented_gain(
                block["reports"][selected][metric],
                block["reports"]["mlp_energy"][metric],
                metric,
            )
            for metric in UNKNOWN_METRICS
        ]
        by_suite[block["suite"]].append(sum(gains) / len(gains))
    suite_gains = {
        suite: sum(values) / len(values)
        for suite, values in sorted(by_suite.items())
    }
    known_f1_differences = [
        block["reports"][selected]["known_macro_f1"]
        - block["reports"]["mlp_msp"]["known_macro_f1"]
        for block in blocks
    ]
    selected_row = next(row for row in overall if row["method"] == selected)
    checks = {
        "pilot_runs_complete": len(blocks) == 14 and not failures,
        "split_integrity": True,
        "known_only_fit": all(
            item["train_correct_min"] > 0
            and item["validation_correct_min"] > 0
            and item["class_count"] >= 2
            for item in support_checks.values()
        ),
        "nondegenerate_score": all(
            method_values["validation_risk_std"] > 1e-12
            and method_values["test_risk_std"] > 1e-12
            for item in diagnostics.values()
            for method_values in item.values()
        ),
        "known_f1_tolerance": (
            sum(known_f1_differences) / len(known_f1_differences) >= -0.01
            and min(known_f1_differences) >= -0.05
        ),
        "top_half_rank": selected_row["mean_unknown_metric_rank"] <= 3.0,
        "metric_breadth": (
            sum(value > 0.0 for value in oriented_gains.values()) >= 2
        ),
        "overall_gain": (
            sum(oriented_gains.values()) / len(oriented_gains) > 0.0
        ),
        "suite_robustness": (
            sum(value >= 0.0 for value in suite_gains.values()) >= 4
            and min(suite_gains.values()) >= -0.05
        ),
    }
    validation = {
        "passes": (
            checks["pilot_runs_complete"]
            and checks["split_integrity"]
            and checks["known_only_fit"]
            and checks["nondegenerate_score"]
        ),
        "scenario_count": len(blocks),
        "report_count": len(blocks) * len(CANDIDATES),
        "failure_count": len(failures),
        "split_fingerprint_checks": len(blocks),
        "no_leak_checks": len(blocks),
        "known_support_checks": len(support_checks),
        "score_checks": len(diagnostics) * len(CANDIDATES),
    }
    return {
        "schema_version": "strict_v4_mlp_klnd_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks),
        "failure_count": len(failures),
        "overall": overall,
        "selected_variant": selected,
        "variant_selection_rule": gate["variant_selection_rule"],
        "score_diagnostics": diagnostics,
        "known_support": support_checks,
        "selected_vs_mlp_energy_oriented_mean_gains": oriented_gains,
        "selected_vs_mlp_energy_four_metric_mean_gain": (
            sum(oriented_gains.values()) / len(oriented_gains)
        ),
        "selected_vs_mlp_energy_suite_mean_gains": suite_gains,
        "known_f1_mean_difference": (
            sum(known_f1_differences) / len(known_f1_differences)
        ),
        "known_f1_worst_scenario_difference": min(known_f1_differences),
        "validation": validation,
        "expansion_checks": checks,
        "decision": {"expand_selected_klnd_to_full102": all(checks.values())},
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 k-LND pilot analysis",
        "",
        "Selected variant: `%s`." % result["selected_variant"],
        "Expand selected k-LND to full 102: `%s`."
        % (
            "YES"
            if result["decision"]["expand_selected_klnd_to_full102"]
            else "NO"
        ),
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
    result = analyze(
        args.pilot_root,
        args.source_root,
        args.opendetect_root,
        _read(args.gate),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render(result)
    (args.output_dir / "analysis.md").write_text(
        rendered, encoding="utf-8"
    )
    print(rendered, end="")


if __name__ == "__main__":
    main()
