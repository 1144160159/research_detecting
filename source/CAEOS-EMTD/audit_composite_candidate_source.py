from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from confirm_cross_suite_fixed_risk import load_manifest
from summarize_paired_confirmation import METRICS, REQUIRED_ARTIFACTS, split_fingerprint


EXPECTED_SOURCE_COUNTS = {"edge_iiot": 70, "nf_cse": 70, "ustc_tfc2016": 50}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(source_root: Path, manifest_path: Path) -> dict[str, object]:
    manifest = load_manifest(manifest_path)
    selected = {
        str(suite): str(risk)
        for suite, risk in manifest["selected_suite_risks"].items()
    }
    expected_candidate_tasks = sum(EXPECTED_SOURCE_COUNTS[suite] for suite in selected)
    paths = sorted(source_root.glob("*/*/metrics.json"))
    counts: Counter[str] = Counter()
    candidate_checks = 0
    artifact_checks = 0
    fingerprint_checks = 0
    source_hashes: list[dict[str, str]] = []
    issues: list[str] = []
    for path in paths:
        suite = path.parent.parent.name
        counts[suite] += 1
        source_hashes.append(
            {"path": path.relative_to(source_root).as_posix(), "sha256": sha256(path)}
        )
        if suite not in selected:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        risk = selected[suite]
        reports = payload.get("reports")
        thresholds = payload.get("validation_thresholds")
        report = reports.get(risk) if isinstance(reports, dict) else None
        if not isinstance(report, dict) or any(
            metric not in report or not math.isfinite(float(report[metric]))
            for metric in METRICS
        ):
            issues.append(f"missing or non-finite report: {path}:{risk}")
        if not isinstance(thresholds, dict) or risk not in thresholds or not math.isfinite(
            float(thresholds[risk])
        ):
            issues.append(f"missing known-validation threshold: {path}:{risk}")
        candidate_checks += 1
        try:
            split_fingerprint(payload)
            fingerprint_checks += 1
        except ValueError as error:
            issues.append(f"split fingerprint: {path}:{error}")
        for name in REQUIRED_ARTIFACTS:
            artifact = path.parent / name
            if not artifact.is_file() or artifact.stat().st_size <= 0:
                issues.append(f"missing artifact: {artifact}")
            else:
                artifact_checks += 1

    if dict(counts) != EXPECTED_SOURCE_COUNTS:
        issues.append(
            f"source coverage mismatch: expected={EXPECTED_SOURCE_COUNTS} actual={dict(counts)}"
        )
    if candidate_checks != expected_candidate_tasks:
        issues.append(
            f"candidate task mismatch: expected={expected_candidate_tasks} actual={candidate_checks}"
        )
    report = {
        "schema_version": "composite_candidate_source_audit_v1",
        "state": "complete" if not issues else "invalid",
        "source_root": str(source_root.resolve()),
        "source_task_count": len(paths),
        "suite_task_counts": dict(counts),
        "selected_suite_risks": selected,
        "candidate_report_threshold_checks": candidate_checks,
        "split_fingerprint_checks": fingerprint_checks,
        "required_artifact_checks": artifact_checks,
        "runtime_selection_uses_unknown_or_test_labels": False,
        "selection_manifest_sha256": manifest["manifest_sha256"],
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest(),
        "issues": issues,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit frozen cross-suite reports before final gate materialization"
    )
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = audit(Path(args.source_root), Path(args.selection_manifest))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["state"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
