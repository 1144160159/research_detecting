from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}
ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")
ANALYSIS_IMPLEMENTATION = (
    "summarize_strict_v4_ronetc_full102.py",
    "audit_strict_v4_ronetc_full102.py",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(payload: dict[str, Any], field: str = "manifest_sha256") -> str:
    value = dict(payload)
    value.pop(field, None)
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def normalize_unknown(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise ValueError(f"invalid unknown class value: {value!r}")


def report(payload: dict[str, Any], method: str, path: Path) -> dict[str, float]:
    reports = payload.get("reports", {})
    if set(reports) != {method}:
        raise ValueError(f"{path} must contain only report {method!r}")
    result = {}
    for metric in METRICS:
        value = float(reports[method][metric])
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"invalid {metric} in {path}: {value}")
        result[metric] = value
    return result


def mean_report(rows: list[dict[str, float]]) -> dict[str, float]:
    if not rows:
        raise ValueError("cannot aggregate an empty report collection")
    return {
        metric: sum(row[metric] for row in rows) / len(rows)
        for metric in METRICS
    }


def comparison(
    candidate: list[dict[str, float]], reference: list[dict[str, float]]
) -> dict[str, Any]:
    if len(candidate) != len(reference) or not candidate:
        raise ValueError("paired reports must be non-empty and equally sized")
    output = {}
    for metric in METRICS:
        deltas = []
        for left, right in zip(candidate, reference):
            raw = left[metric] - right[metric]
            deltas.append(-raw if metric in LOWER_IS_BETTER else raw)
        output[metric] = {
            "direction": (
                "lower_is_better"
                if metric in LOWER_IS_BETTER
                else "higher_is_better"
            ),
            "oriented_mean_delta": sum(deltas) / len(deltas),
            "wins": sum(delta > 1e-12 for delta in deltas),
            "ties": sum(abs(delta) <= 1e-12 for delta in deltas),
            "losses": sum(delta < -1e-12 for delta in deltas),
        }
    return output


def validate_inputs(
    protocol_path: Path,
    protocol_audit_path: Path,
    baseline_manifest_path: Path,
    full_summary_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = load_json(protocol_path)
    if (
        protocol.get("schema_version")
        != "strict_v4_ronetc_full102_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("state") != "frozen_zero_result"
    ):
        raise ValueError("invalid frozen RoNeTC protocol")
    protocol_audit = load_json(protocol_audit_path)
    if (
        protocol_audit.get("audit_manifest_sha256")
        != canonical_hash(protocol_audit, "audit_manifest_sha256")
        or protocol_audit.get("passed") is not True
        or not all(protocol_audit.get("checks", {}).values())
    ):
        raise ValueError("invalid RoNeTC protocol audit")
    baseline_manifest = load_json(baseline_manifest_path)
    if (
        baseline_manifest.get("schema_version")
        != "strict_v4_baseline_manifest_v2"
        or baseline_manifest.get("manifest_sha256")
        != canonical_hash(baseline_manifest)
        or baseline_manifest.get("scenario_inference_units") != 102
        or baseline_manifest.get("seed") != 7
        or "opendetect" not in baseline_manifest.get("reported_methods", [])
    ):
        raise ValueError("invalid bound OpenDetect baseline manifest")
    full_summary = load_json(full_summary_path)
    if (
        full_summary.get("schema_version")
        != "strict_v4_full103_coverage_summary_v1"
        or full_summary.get("baseline_manifest_sha256")
        != baseline_manifest["manifest_sha256"]
        or full_summary.get("validation", {}).get("passes") is not True
        or full_summary.get("validation", {}).get("scenario_count") != 102
    ):
        raise ValueError("full103 summary does not bind the baseline manifest")
    source_hashes = protocol.get("source_evidence_sha256", {})
    if (
        source_hashes.get("strict_v4_full102_summary")
        != file_hash(full_summary_path)
        or source_hashes.get("strict_v4_baseline_manifest_v2")
        != file_hash(baseline_manifest_path)
    ):
        raise ValueError("protocol/source evidence hash mismatch")
    return protocol, baseline_manifest


def build_summary(
    protocol_path: Path,
    protocol_audit_path: Path,
    result_root: Path,
    opendetect_root: Path,
    baseline_manifest_path: Path,
    full_summary_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    protocol, baseline_manifest = validate_inputs(
        protocol_path,
        protocol_audit_path,
        baseline_manifest_path,
        full_summary_path,
    )
    tasks = protocol.get("tasks", [])
    if len(tasks) != 102:
        raise ValueError("RoNeTC full102 summary requires 102 tasks")

    records = []
    identities = set()
    for task in tasks:
        suite = task["suite"]
        scenario = task["scenario"]
        seed = int(task["seed"])
        identity = (suite, scenario, seed)
        if identity in identities:
            raise ValueError(f"duplicate task identity: {identity}")
        identities.add(identity)
        candidate_dir = result_root / suite / f"{scenario}_seed{seed}_ronetc"
        reference_dir = (
            opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
        )
        artifact_hashes = {}
        for label, directory in (
            ("ronetc", candidate_dir),
            ("opendetect", reference_dir),
        ):
            for artifact in ARTIFACTS:
                path = directory / artifact
                if not path.is_file():
                    raise ValueError(f"missing {label} artifact: {path}")
                artifact_hashes[f"{label}/{artifact}"] = file_hash(path)

        candidate_metrics_path = candidate_dir / "metrics.json"
        reference_metrics_path = reference_dir / "metrics.json"
        candidate_metrics = load_json(candidate_metrics_path)
        reference_metrics = load_json(reference_metrics_path)
        candidate_provenance = load_json(candidate_dir / "provenance.json")
        reference_provenance = load_json(reference_dir / "provenance.json")
        expected_unknown = normalize_unknown(task["unknown_classes"])
        for label, metrics, provenance, method in (
            (
                "ronetc",
                candidate_metrics,
                candidate_provenance,
                "ronetc",
            ),
            (
                "opendetect",
                reference_metrics,
                reference_provenance,
                "opendetect",
            ),
        ):
            if metrics.get("model") != method or metrics.get("seed") != seed:
                raise ValueError(f"{label} model/seed mismatch for {identity}")
            if normalize_unknown(metrics.get("unknown_classes")) != expected_unknown:
                raise ValueError(f"{label} unknown classes mismatch for {identity}")
            selection = metrics.get("selection_evidence", {})
            if not (
                selection.get(
                    "unknown_or_test_labels_used_for_fitting_or_selection"
                )
                is False
                and selection.get("test_labels_used_for_final_metrics_only")
                is True
            ):
                raise ValueError(f"{label} leakage guard failed for {identity}")
            provenance_task = provenance.get("task", {})
            if (
                provenance_task.get("suite") != suite
                or provenance_task.get("scenario") != scenario
                or provenance_task.get("model") != method
                or provenance_task.get("seed") != seed
            ):
                raise ValueError(f"{label} provenance mismatch for {identity}")
        candidate_split = candidate_metrics["split_metadata"][
            "split_fingerprint"
        ]["combined"]
        reference_split = reference_metrics["split_metadata"][
            "split_fingerprint"
        ]["combined"]
        if (
            candidate_split != reference_split
            or candidate_metrics.get("sample_counts")
            != reference_metrics.get("sample_counts")
        ):
            raise ValueError(f"paired split mismatch for {identity}")
        records.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "unknown_classes": expected_unknown,
                "split_fingerprint": candidate_split,
                "reports": {
                    "ronetc": report(
                        candidate_metrics, "ronetc", candidate_metrics_path
                    ),
                    "opendetect": report(
                        reference_metrics,
                        "opendetect",
                        reference_metrics_path,
                    ),
                },
                "artifact_sha256": artifact_hashes,
            }
        )

    suite_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        suite_records[record["suite"]].append(record)
    by_suite = {}
    for suite, rows in sorted(suite_records.items()):
        candidate = [row["reports"]["ronetc"] for row in rows]
        reference = [row["reports"]["opendetect"] for row in rows]
        by_suite[suite] = {
            "scenario_count": len(rows),
            "ronetc": mean_report(candidate),
            "opendetect": mean_report(reference),
            "ronetc_vs_opendetect": comparison(candidate, reference),
        }
    candidate = [record["reports"]["ronetc"] for record in records]
    reference = [record["reports"]["opendetect"] for record in records]
    summary: dict[str, Any] = {
        "schema_version": "strict_v4_ronetc_full102_summary_v1",
        "state": "full102_development_summary_complete",
        "input_evidence": {
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "protocol_audit_file_sha256": file_hash(protocol_audit_path),
            "protocol_audit_manifest_sha256": load_json(
                protocol_audit_path
            )["audit_manifest_sha256"],
            "baseline_manifest_file_sha256": file_hash(
                baseline_manifest_path
            ),
            "baseline_manifest_sha256": baseline_manifest["manifest_sha256"],
            "full103_summary_file_sha256": file_hash(full_summary_path),
        },
        "analysis_implementation_sha256": {
            name: file_hash(project_root / name)
            for name in ANALYSIS_IMPLEMENTATION
        },
        "validation": {
            "passes": True,
            "suite_count": len(by_suite),
            "scenario_count": len(records),
            "task_identity_count": len(identities),
            "paired_split_fingerprint_checks": len(records),
            "artifact_checks": len(records) * len(ARTIFACTS) * 2,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "overall": {
            "ronetc": mean_report(candidate),
            "opendetect": mean_report(reference),
            "ronetc_vs_opendetect": comparison(candidate, reference),
        },
        "by_suite": by_suite,
        "task_records": records,
        "claim_boundary": {
            "seed7_is_development_screen": True,
            "comparison_is_same_split_and_paired": True,
            "effect_sign_does_not_control_integrity_pass": True,
            "authorizes_algorithm_selection": False,
            "authorizes_comprehensive_sota": False,
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# RoNeTC strict-v4 full102 development summary",
        "",
        "| Suite | Scenarios | RoNeTC F1 | RoNeTC AUROC | RoNeTC AUPR | RoNeTC FPR95 | RoNeTC OSCR |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for suite, row in summary["by_suite"].items():
        report = row["ronetc"]
        lines.append(
            f"| {suite} | {row['scenario_count']} | "
            f"{report['known_macro_f1']:.6f} | "
            f"{report['unknown_auroc']:.6f} | "
            f"{report['unknown_aupr']:.6f} | "
            f"{report['unknown_fpr95']:.6f} | {report['oscr']:.6f} |"
        )
    lines.extend(
        [
            "",
            "This is a paired seed-7 development comparison with OpenDetect. "
            "It does not authorize algorithm selection or comprehensive SOTA.",
            "",
            f"Manifest: `{summary['manifest_sha256']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--protocol-audit", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    summary = build_summary(
        args.protocol.resolve(),
        args.protocol_audit.resolve(),
        args.result_root.resolve(),
        args.opendetect_root.resolve(),
        args.baseline_manifest.resolve(),
        args.full_summary.resolve(),
        args.project_root.resolve(),
    )
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
                "output": str(args.output_json),
                "scenario_count": len(summary["task_records"]),
                "manifest_sha256": summary["manifest_sha256"],
            }
        )
    )


if __name__ == "__main__":
    main()
