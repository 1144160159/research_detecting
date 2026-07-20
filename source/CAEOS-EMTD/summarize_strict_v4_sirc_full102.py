from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Optional

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash


METHOD = "sirc_msp_residual"
METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def rank_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for row in rows:
        row.pop("metric_ranks", None)
        row.pop("mean_unknown_metric_rank", None)
    for metric in UNKNOWN_METRICS:
        values = [float(row[metric]) for row in rows]
        ranked = rankdata(values if metric == "unknown_fpr95" else [-value for value in values], method="average")
        for row, rank in zip(rows, ranked):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in rows:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / len(UNKNOWN_METRICS)
    return sorted(rows, key=lambda row: (row["mean_unknown_metric_rank"], -row["unknown_auroc"], row["method"]))


def _mean_report(reports: list[dict[str, float]], method: str) -> dict[str, Any]:
    row: dict[str, Any] = {"method": method}
    for metric in METRICS:
        row[metric] = sum(report[metric] for report in reports) / len(reports)
    return row


def _oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(full_root: Path, source_root: Path, existing_summary_path: Path) -> dict[str, Any]:
    protocol = _read(full_root / "protocol_manifest.json")
    matrix = _read(full_root / "matrix_summary.json")
    existing = _read(existing_summary_path)
    if protocol.get("schema_version") != "strict_v4_mlp_sirc_msp_fixed_protocol_v1":
        raise ValueError("unexpected SIRC full protocol schema")
    if protocol.get("mode") != "full" or protocol.get("expected_runs") != 102:
        raise ValueError("SIRC full protocol must cover 102 scenarios")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("SIRC full protocol SHA mismatch")
    if protocol.get("expansion_evidence", {}).get("gate_selected_expanded_methods") != [METHOD]:
        raise ValueError("SIRC full protocol did not select only the residual variant")
    if matrix.get("completed_runs") != 102 or matrix.get("failures") != 0:
        raise ValueError("SIRC full matrix is incomplete")
    if matrix.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
        raise ValueError("SIRC matrix is not bound to the full protocol")
    if existing.get("status") != "complete" or existing.get("method_count") != 25:
        raise ValueError("existing 25-method summary is not complete")

    candidate_reports: list[dict[str, float]] = []
    source_reports: list[dict[str, float]] = []
    by_suite_candidate: dict[str, list[dict[str, float]]] = {}
    split_checks = 0
    provenance_checks = 0
    no_leak_checks = 0
    failures = list(full_root.glob("**/failure.json"))
    for suite, scenarios in protocol["selected_scenarios"].items():
        by_suite_candidate[suite] = []
        for scenario in scenarios:
            output_path = full_root / suite / (scenario + "_seed7") / "metrics.json"
            provenance_path = output_path.parent / "provenance.json"
            source_path = source_root / suite / (scenario + "_seed7_mlp") / "metrics.json"
            output, provenance, source = _read(output_path), _read(provenance_path), _read(source_path)
            fingerprints = [_fingerprint(output), _fingerprint(source)]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError("split fingerprint mismatch for %s/%s" % (suite, scenario))
            split_checks += 1
            relative_source = "%s/%s_seed7_mlp" % (suite, scenario)
            expected_hashes = protocol["source_artifact_sha256"][relative_source]
            if provenance.get("source_artifact_sha256") != expected_hashes:
                raise ValueError("source artifact binding mismatch for %s/%s" % (suite, scenario))
            if provenance.get("methods") != ["sirc_msp_l1", "sirc_msp_residual"]:
                raise ValueError("unexpected SIRC provenance methods for %s/%s" % (suite, scenario))
            provenance_checks += 1
            evidence = output.get("selection_evidence", {})
            if evidence.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
                raise ValueError("SIRC leak guard failed for %s/%s" % (suite, scenario))
            if evidence.get("postprocessor", {}).get("official_code_commit") != "0b492695d5bf34942cd8b333d10a998f763c3eff":
                raise ValueError("SIRC official commit mismatch for %s/%s" % (suite, scenario))
            no_leak_checks += 1
            candidate_report = _report(output, METHOD, output_path)
            source_report = _report(source, "msp", source_path)
            candidate_reports.append(candidate_report)
            source_reports.append(source_report)
            by_suite_candidate[suite].append(candidate_report)
    if len(candidate_reports) != 102 or failures:
        raise ValueError("SIRC full analysis expected 102 reports and zero failures")

    sirc_overall = _mean_report(candidate_reports, METHOD)
    msp_overall = _mean_report(source_reports, "mlp_msp")
    overall_rows = [dict(row) for row in existing["overall"]]
    if any(row["method"] == METHOD for row in overall_rows):
        raise ValueError("SIRC residual already exists in the 25-method summary")
    overall = rank_rows(overall_rows + [sirc_overall])

    by_suite: dict[str, list[dict[str, Any]]] = {}
    for suite, rows in existing["by_suite"].items():
        suite_row = _mean_report(by_suite_candidate[suite], METHOD)
        by_suite[suite] = rank_rows([dict(row) for row in rows] + [suite_row])

    non_caeos = [row for row in overall if not str(row["method"]).startswith("caeos_")]
    selected = min(non_caeos, key=lambda row: (row["mean_unknown_metric_rank"], -row["unknown_auroc"], row["method"]))
    opendetect = next(row for row in overall if row["method"] == "opendetect")
    gains_vs_msp = {
        metric: _oriented_gain(sirc_overall[metric], msp_overall[metric], metric)
        for metric in UNKNOWN_METRICS
    }
    gains_vs_opendetect = {
        metric: _oriented_gain(sirc_overall[metric], opendetect[metric], metric)
        for metric in UNKNOWN_METRICS
    }
    return {
        "schema_version": "strict_v4_sirc_residual_26method_screen_v1",
        "status": "complete", "method_count": 26, "added_method": METHOD,
        "overall": overall, "by_suite": by_suite,
        "sirc_msp_residual_vs_mlp_msp_oriented_mean_gains": gains_vs_msp,
        "sirc_msp_residual_vs_opendetect_oriented_mean_gains": gains_vs_opendetect,
        "validation": {
            "passes": True, "scenario_count": 102, "report_count": 102,
            "failure_count": len(failures), "split_fingerprint_pair_checks": split_checks,
            "source_provenance_checks": provenance_checks, "no_leak_checks": no_leak_checks,
            "expanded_method": METHOD,
            "incidental_method_excluded_from_26method_table": "sirc_msp_l1",
        },
        "comparator_decision": {
            "selection_rule": "minimum four-unknown-metric mean rank, then higher AUROC",
            "selected_comparator": selected["method"],
            "selected_metrics": {metric: selected[metric] for metric in METRICS},
            "selected_mean_unknown_metric_rank": selected["mean_unknown_metric_rank"],
            "previous_comparator": "opendetect",
            "comparator_changed": selected["method"] != "opendetect",
            "next_action": "freeze independent new-seed confirmation for the selected comparator",
        },
        "full_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_expansion_gate_manifest_sha256": protocol["expansion_evidence"]["pilot_expansion_gate_manifest_sha256"],
        "pilot_analysis_sha256": protocol["expansion_evidence"]["pilot_analysis_sha256"],
        "existing_25method_summary_sha256": sha256_file(existing_summary_path),
        "analysis_implementation_sha256": sha256_file(Path(__file__).resolve()),
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 SIRC-Residual full102 and 26-method screen", "",
        "Selected strongest non-CAEOS comparator: `%s`." % result["comparator_decision"]["selected_comparator"], "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append("| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | {unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | {mean_unknown_metric_rank:.2f} |".format(**row))
    lines.extend(["", "Validation: `PASS` (102 scenarios, 0 failures, 102 split/provenance/no-leak checks).", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--existing-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.full_root, args.source_root, args.existing_summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rendered = render(result)
    (args.output_dir / "summary.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
