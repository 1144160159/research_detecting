from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any, Optional

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_external_training_pilot_protocol import METHODS


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
REPORT_ALIASES = {"palm": "palm_ssd_plus"}


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root is not an object: %s" % path)
    return payload


def report(payload: dict[str, Any], method: str, path: Path) -> dict[str, float]:
    value = payload.get("reports", {}).get(method)
    if value is None and method in REPORT_ALIASES:
        value = payload.get("reports", {}).get(REPORT_ALIASES[method])
    if not isinstance(value, dict):
        raise ValueError("missing report %s: %s" % (method, path))
    result = {metric: float(value[metric]) for metric in METRICS}
    if not all(math.isfinite(item) for item in result.values()):
        raise ValueError("non-finite report %s: %s" % (method, path))
    return result


def fingerprint(payload: dict[str, Any]) -> Optional[str]:
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def no_test_label_fit(
    payload: dict[str, Any], method: str, protocol: dict[str, Any]
) -> bool:
    selection = payload.get("selection_evidence", {})
    value = selection.get("unknown_or_test_labels_used_for_fitting_or_selection")
    if value is None:
        value = payload.get("unknown_or_test_labels_used_for_fitting_or_selection")
    if value is not None:
        return value is False
    if method != "sieve":
        return False
    repairs = set(payload.get("source_reference", {}).get("adapter_repairs", []))
    implementation = payload.get("implementation", "")
    return (
        protocol.get("fit_data") == "known_training_only"
        and protocol.get("checkpoint_and_threshold_data") == "known_validation_only"
        and protocol.get("unknown_or_test_labels_used_for_fitting_or_selection")
        is False
        and "select checkpoints on known validation instead of the test set" in repairs
        and "fit preprocessing on training data only" in repairs
        and "checkpoint selection use training statistics and known validation only"
        in implementation
        and set(payload.get("reports", {})) == {"sieve"}
        and set(payload.get("validation_thresholds", {})) == {"sieve"}
    )


def analyze(
    pilot_root: Path,
    source_root: Path,
    opendetect_root: Path,
    methods: tuple[str, ...] = METHODS,
    analysis_schema: str = "strict_v4_external_training_pilot_analysis_v1",
) -> dict[str, Any]:
    protocol = read_json(pilot_root / "protocol_manifest.json")
    gate = read_json(pilot_root / "expansion_gate.json")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("external training pilot protocol SHA mismatch")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("external training pilot gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("external training pilot protocol/gate binding mismatch")
    blocks = []
    split_checks = 0
    no_leak_checks = 0
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            source_path = source_root / suite / (scenario + "_seed7_mlp") / "metrics.json"
            external_path = opendetect_root / suite / (scenario + "_seed7_opendetect") / "metrics.json"
            source = read_json(source_path)
            external = read_json(external_path)
            candidate_payloads = {}
            for method in methods:
                path = pilot_root / suite / (scenario + "_seed7_" + method) / "metrics.json"
                candidate_payloads[method] = (read_json(path), path)
            fingerprints = [fingerprint(source), fingerprint(external)] + [
                fingerprint(candidate_payloads[method][0]) for method in methods
            ]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError("split fingerprint mismatch: %s/%s" % (suite, scenario))
            split_checks += 1
            if not all(
                no_test_label_fit(candidate_payloads[method][0], method, protocol)
                for method in methods
            ):
                raise ValueError("unknown/test label fitting detected: %s/%s" % (suite, scenario))
            no_leak_checks += 1
            reports = {"opendetect": report(external, "opendetect", external_path)}
            for method in methods:
                payload, path = candidate_payloads[method]
                reports[method] = report(payload, method, path)
            blocks.append({"suite": suite, "scenario": scenario, "reports": reports})
    failures = sorted(str(path) for path in pilot_root.glob("*/*/failure.json"))
    method_order = ("opendetect",) + methods
    overall = []
    for method in method_order:
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
    decisions = {}
    for method in methods:
        oriented = {}
        for metric in UNKNOWN_METRICS:
            gains = []
            for block in blocks:
                candidate = block["reports"][method][metric]
                reference = block["reports"]["opendetect"][metric]
                gains.append(reference - candidate if metric == "unknown_fpr95" else candidate - reference)
            oriented[metric] = sum(gains) / len(gains)
        by_suite = defaultdict(list)
        for block in blocks:
            gains = []
            for metric in UNKNOWN_METRICS:
                candidate = block["reports"][method][metric]
                reference = block["reports"]["opendetect"][metric]
                gains.append(reference - candidate if metric == "unknown_fpr95" else candidate - reference)
            by_suite[block["suite"]].append(sum(gains) / len(gains))
        suite_gains = {suite: sum(values) / len(values) for suite, values in sorted(by_suite.items())}
        known_deltas = [
            block["reports"][method]["known_macro_f1"]
            - block["reports"]["opendetect"]["known_macro_f1"]
            for block in blocks
        ]
        row = next(item for item in overall if item["method"] == method)
        checks = {
            "pilot_runs_complete": len(blocks) == 14 and not failures,
            "split_and_leakage_integrity": split_checks == 14 and no_leak_checks == 14,
            "known_f1_tolerance": sum(known_deltas) / len(known_deltas) >= -0.03 and min(known_deltas) >= -0.10,
            "top_two_rank": row["mean_unknown_metric_rank"] <= 2.0,
            "metric_breadth": sum(value > 0.0 for value in oriented.values()) >= 2,
            "overall_gain": sum(oriented.values()) / len(oriented) > 0.0,
            "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 4 and min(suite_gains.values()) >= -0.05,
        }
        decisions[method] = {
            "oriented_mean_gains_vs_opendetect": oriented,
            "four_metric_mean_gain_vs_opendetect": sum(oriented.values()) / len(oriented),
            "suite_mean_gains_vs_opendetect": suite_gains,
            "known_f1_mean_difference_vs_opendetect": sum(known_deltas) / len(known_deltas),
            "known_f1_worst_difference_vs_opendetect": min(known_deltas),
            "checks": checks,
            "expand_to_full102": all(checks.values()),
        }
    expanded = [method for method in methods if decisions[method]["expand_to_full102"]]
    return {
        "schema_version": analysis_schema,
        "status": "complete",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks),
        "method_run_count": len(blocks) * len(methods),
        "failure_count": len(failures),
        "overall": overall,
        "candidate_decisions": decisions,
        "expand_to_full102": expanded,
        "validation": {
            "passes": len(blocks) == 14 and not failures and split_checks == 14 and no_leak_checks == 14,
            "scenario_count": len(blocks),
            "method_run_count": len(blocks) * len(methods),
            "split_fingerprint_checks": split_checks,
            "no_leak_checks": no_leak_checks,
            "failure_count": len(failures),
        },
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 external training baseline pilot",
        "",
        "Expand to full102: `%s`." % (", ".join(result["expand_to_full102"]) or "NONE"),
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | {unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | {mean_unknown_metric_rank:.2f} |".format(**row)
        )
    for method, decision in result["candidate_decisions"].items():
        lines.extend(["", "## %s expansion gate" % method, ""])
        for name, passed in decision["checks"].items():
            lines.append("- `%s`: %s" % (name, "PASS" if passed else "FAIL"))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.pilot_root, args.source_root, args.opendetect_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    text = render(result)
    (args.output_dir / "analysis.md").write_text(text, encoding="utf-8")
    (args.output_dir / "pilot_complete").write_text(
        result["pilot_protocol_manifest_sha256"] + "\n", encoding="ascii"
    )
    if result["expand_to_full102"]:
        (args.output_dir / "full102_expansion_required").write_text(
            "\n".join(result["expand_to_full102"]) + "\n", encoding="ascii"
        )
    print(text, end="")


if __name__ == "__main__":
    main()
