from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any


AUDIT_SCHEMA = "strict_v4_krc_certificate_bottleneck_audit_v1"
PROGRESS_SCHEMA = "strict_v4_krc_csr_confirmation_progress_audit_v1"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def metric_summary(values: list[float], threshold: float) -> dict[str, Any]:
    return {
        "minimum": min(values),
        "mean": fmean(values),
        "maximum": max(values),
        "passes_absolute_threshold_count": sum(value >= threshold for value in values),
        "absolute_threshold": threshold,
    }


def validate_inputs(
    audit: dict[str, Any],
    progress: dict[str, Any],
    audit_path: Path,
    progress_path: Path,
) -> None:
    if audit.get("schema_version") != AUDIT_SCHEMA:
        raise ValueError("unexpected KRC bottleneck audit schema")
    if progress.get("schema_version") != PROGRESS_SCHEMA:
        raise ValueError("unexpected KRC progress schema")
    if audit.get("passes") is not True:
        raise ValueError("KRC bottleneck audit did not pass integrity checks")
    if audit.get("progress_manifest_sha256") != progress.get("manifest_sha256"):
        raise ValueError("audit/progress canonical manifest mismatch")
    if audit.get("progress_file_sha256") != file_hash(progress_path):
        raise ValueError("audit/progress file SHA256 mismatch")
    observed = progress.get("observed_totals", {}).get("captures")
    if observed != len(audit.get("records", [])):
        raise ValueError("audit record count does not match progress captures")
    identities = {
        (row["suite"], row["scenario"], int(row["training_seed"]))
        for row in audit["records"]
    }
    if len(identities) != len(audit["records"]):
        raise ValueError("duplicate suite/scenario/training-seed records")
    if not audit_path.is_file():
        raise FileNotFoundError(audit_path)


def build_summary(
    audit: dict[str, Any],
    progress: dict[str, Any],
    audit_path: Path,
    progress_path: Path,
) -> dict[str, Any]:
    validate_inputs(audit, progress, audit_path, progress_path)
    by_suite: dict[str, list[dict[str, Any]]] = defaultdict(list)
    scenarios_by_suite: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in audit["records"]:
        by_suite[record["suite"]].append(record)
    for record in audit["diagnostics"]["scenario_records"]:
        scenarios_by_suite[record["identity"].split("/", 1)[0]].append(record)

    suites: dict[str, Any] = {}
    for suite in sorted(by_suite):
        records = by_suite[suite]
        scenarios = scenarios_by_suite[suite]
        known_f1 = [float(row["calibration_known_macro_f1"]) for row in records]
        error_auroc = [
            float(row["calibration_error_detection_auroc"]) for row in records
        ]
        complete = [
            row for row in scenarios if row["complete_three_seed_scenario"] is True
        ]
        suites[suite] = {
            "observed_capture_count": len(records),
            "observed_scenario_count": len(scenarios),
            "complete_three_seed_scenario_count": len(complete),
            "known_class_count_values": sorted(
                {int(row["known_class_count"]) for row in records}
            ),
            "calibration_known_macro_f1": metric_summary(known_f1, 0.9),
            "calibration_error_detection_auroc": metric_summary(error_auroc, 0.7),
            "source_safety": {
                "active_capture_count": sum(
                    int(row["source_safety_active_count"]) > 0 for row in records
                ),
                "maximum_active_rate": max(
                    float(row["source_safety_active_rate"]) for row in records
                ),
                "maximum_active_rate_upper_95pct": max(
                    float(row["source_safety_active_rate_upper_95pct"])
                    for row in records
                ),
                "complete_scenario_failure_count": sum(
                    row["all_source_safety_checks_pass"] is not True
                    for row in complete
                ),
            },
            "rrc_diagnostic_eligible_complete_scenario_count": sum(
                row["rrc_diagnostic_eligible"] is True for row in complete
            ),
        }

    output: dict[str, Any] = {
        "schema_version": "strict_v4_krc_cross_suite_diagnostic_v1",
        "state": "valid_partial_diagnostic",
        "input_sha256": {
            "progress_file": file_hash(progress_path),
            "progress_manifest": progress["manifest_sha256"],
            "bottleneck_audit_file": file_hash(audit_path),
            "bottleneck_audit_manifest": audit["manifest_sha256"],
        },
        "observed_totals": progress["observed_totals"],
        "suite_summaries": suites,
        "claim_boundary": {
            "uses_known_validation_diagnostics_only": True,
            "uses_outer_unknown_test_labels": False,
            "authorizes_algorithm_selection": False,
            "authorizes_gate_changes": False,
            "authorizes_comprehensive_sota": False,
            "partial_results_must_not_be_pooled_as_terminal_effect": True,
        },
    }
    output["manifest_sha256"] = canonical_hash(output)
    return output


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# KRC cross-suite known-certificate diagnostic",
        "",
        f"State: **{summary['state']}**.",
        "",
        "| Suite | Captures | Complete scenarios | Known classes | Known F1 mean (>=0.9) | Error AUROC mean (>=0.7) | Source-safety failed scenarios | RRC eligible |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for suite, row in summary["suite_summaries"].items():
        f1 = row["calibration_known_macro_f1"]
        auroc = row["calibration_error_detection_auroc"]
        safety = row["source_safety"]
        lines.append(
            f"| {suite} | {row['observed_capture_count']} | "
            f"{row['complete_three_seed_scenario_count']} | "
            f"{','.join(map(str, row['known_class_count_values']))} | "
            f"{f1['mean']:.6f} ({f1['passes_absolute_threshold_count']}) | "
            f"{auroc['mean']:.6f} ({auroc['passes_absolute_threshold_count']}) | "
            f"{safety['complete_scenario_failure_count']} | "
            f"{row['rrc_diagnostic_eligible_complete_scenario_count']} |"
        )
    lines.extend(
        [
            "",
            "This report uses known-validation diagnostics only. It cannot select an",
            "algorithm, change a frozen gate, pool partial results as terminal effect,",
            "or authorize comprehensive SOTA.",
            "",
            f"Manifest: `{summary['manifest_sha256']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize protocol-bound KRC diagnostics by suite."
    )
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    audit = load_json(args.audit)
    progress = load_json(args.progress)
    summary = build_summary(audit, progress, args.audit, args.progress)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.output_md.write_text(render_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "output_md": str(args.output_md),
                "manifest_sha256": summary["manifest_sha256"],
            }
        )
    )


if __name__ == "__main__":
    main()
