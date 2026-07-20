from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Optional

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash


METHODS = ("shannon_entropy", "prototype_distance")
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
        ranks = rankdata(values if metric == "unknown_fpr95" else [-value for value in values], method="average")
        for row, rank in zip(rows, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in rows:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / len(UNKNOWN_METRICS)
    return sorted(rows, key=lambda row: (row["mean_unknown_metric_rank"], -row["unknown_auroc"], row["method"]))


def _mean_report(reports: list[dict[str, float]], method: str) -> dict[str, Any]:
    return {"method": method, **{metric: sum(report[metric] for report in reports) / len(reports) for metric in METRICS}}


def analyze(full_root: Path, source_root: Path, existing_summary_path: Path) -> dict[str, Any]:
    protocol = _read(full_root / "protocol_manifest.json")
    matrix = _read(full_root / "matrix_summary.json")
    existing = _read(existing_summary_path)
    if protocol.get("schema_version") != "strict_v4_mlp_mandatory_scores_protocol_v1":
        raise ValueError("unexpected mandatory score protocol schema")
    if protocol.get("mode") != "full" or protocol.get("expected_runs") != 102:
        raise ValueError("mandatory score protocol must cover full102")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("mandatory score protocol SHA mismatch")
    if protocol.get("methods") != list(METHODS) or protocol.get("ood_parameter_sweep") is not False:
        raise ValueError("mandatory score protocol methods or tuning policy changed")
    if matrix.get("completed_runs") != 102 or matrix.get("failures") != 0 or matrix.get("report_count") != 204:
        raise ValueError("mandatory score matrix is incomplete")
    if matrix.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
        raise ValueError("mandatory score matrix protocol binding mismatch")
    if existing.get("schema_version") != "strict_v4_sirc_residual_26method_screen_v1" or existing.get("method_count") != 26:
        raise ValueError("existing 26-method summary is incomplete")

    reports = {method: [] for method in METHODS}
    by_suite_reports = {suite: {method: [] for method in METHODS} for suite in protocol["selected_scenarios"]}
    split_checks = provenance_checks = no_leak_checks = score_checks = 0
    failures = list(full_root.glob("**/failure.json"))
    for suite, scenarios in protocol["selected_scenarios"].items():
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
            if provenance.get("source_artifact_sha256") != protocol["source_artifact_sha256"][relative_source]:
                raise ValueError("source artifact binding mismatch for %s/%s" % (suite, scenario))
            if provenance.get("methods") != list(METHODS):
                raise ValueError("mandatory score provenance methods differ for %s/%s" % (suite, scenario))
            provenance_checks += 1
            evidence = output.get("selection_evidence", {})
            if evidence.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
                raise ValueError("mandatory score leak guard failed for %s/%s" % (suite, scenario))
            no_leak_checks += 1
            diagnostics = output.get("diagnostics", {})
            if not all(
                float(diagnostics.get(method, {}).get(name, 0.0)) > 1e-12
                for method in METHODS for name in ("validation_risk_std", "test_risk_std")
            ):
                raise ValueError("mandatory score is degenerate for %s/%s" % (suite, scenario))
            score_checks += 1
            for method in METHODS:
                report = _report(output, method, output_path)
                reports[method].append(report)
                by_suite_reports[suite][method].append(report)
    if any(len(items) != 102 for items in reports.values()) or failures:
        raise ValueError("mandatory full102 analysis expected 204 reports and zero failures")

    added_rows = [_mean_report(reports[method], method) for method in METHODS]
    existing_rows = [dict(row) for row in existing["overall"]]
    if set(METHODS) & {row["method"] for row in existing_rows}:
        raise ValueError("mandatory methods already exist in the 26-method summary")
    overall = rank_rows(existing_rows + added_rows)
    by_suite = {}
    for suite, rows in existing["by_suite"].items():
        additions = [_mean_report(by_suite_reports[suite][method], method) for method in METHODS]
        by_suite[suite] = rank_rows([dict(row) for row in rows] + additions)
    non_caeos = [row for row in overall if not str(row["method"]).startswith("caeos_")]
    selected = min(non_caeos, key=lambda row: (row["mean_unknown_metric_rank"], -row["unknown_auroc"], row["method"]))
    previous = existing["comparator_decision"]["selected_comparator"]
    return {
        "schema_version": "strict_v4_mandatory_scores_28method_screen_v1",
        "status": "complete", "method_count": 28, "added_methods": list(METHODS),
        "overall": overall, "by_suite": by_suite,
        "validation": {
            "passes": True, "scenario_count": 102, "report_count": 204,
            "failure_count": len(failures), "split_fingerprint_pair_checks": split_checks,
            "source_provenance_checks": provenance_checks, "no_leak_checks": no_leak_checks,
            "nondegenerate_score_checks": score_checks,
        },
        "comparator_decision": {
            "selection_rule": "minimum four-unknown-metric mean rank, then higher AUROC",
            "selected_comparator": selected["method"],
            "selected_metrics": {metric: selected[metric] for metric in METRICS},
            "selected_mean_unknown_metric_rank": selected["mean_unknown_metric_rank"],
            "previous_comparator": previous,
            "comparator_changed": selected["method"] != previous,
            "next_action": "retain existing external protocol only when comparator_changed is false",
        },
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "existing_26method_summary_sha256": sha256_file(existing_summary_path),
        "analysis_implementation_sha256": sha256_file(Path(__file__).resolve()),
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 mandatory Entropy/Prototype full102 and 28-method screen", "",
        "Selected strongest non-CAEOS comparator: `%s`." % result["comparator_decision"]["selected_comparator"], "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append("| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | {unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | {mean_unknown_metric_rank:.2f} |".format(**row))
    lines.extend(["", "Validation: `PASS` (102 scenarios, 204 reports, 0 failures).", ""])
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
