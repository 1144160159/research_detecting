from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


METHODS = (
    "isolation_forest",
    "one_class_svm",
    "local_outlier_factor",
    "pca_reconstruction",
)
REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def finite_nonnegative(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


def finite_scalar(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def audit_run(metrics_path: Path) -> list[str]:
    issues: list[str] = []
    try:
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"cannot read {metrics_path}: {error}"]
    if not isinstance(payload, dict):
        return [f"metrics root is not an object: {metrics_path}"]
    if payload.get("model") != "classical_ood":
        issues.append(f"model mismatch: {metrics_path}")

    reports = payload.get("reports")
    if not isinstance(reports, dict) or set(reports) != set(METHODS):
        issues.append(f"report set mismatch: {metrics_path}")
    else:
        for method, report in reports.items():
            if not isinstance(report, dict):
                issues.append(f"invalid report {method}: {metrics_path}")
                continue
            for metric in REPORT_METRICS:
                value = report.get(metric)
                if not finite_nonnegative(value) or float(value) > 1.0:
                    issues.append(
                        f"invalid {method}.{metric}={value!r}: {metrics_path}"
                    )

    thresholds = payload.get("validation_thresholds")
    if not isinstance(thresholds, dict) or set(thresholds) != set(METHODS):
        issues.append(f"threshold set mismatch: {metrics_path}")
    elif any(not finite_scalar(value) for value in thresholds.values()):
        issues.append(f"invalid validation threshold: {metrics_path}")

    selection = payload.get("selection_evidence")
    expected_selection = {
        "unknown_or_test_labels_used_for_training": False,
        "unknown_or_test_labels_used_for_thresholds": False,
        "detector_subsample_is_class_balanced": True,
    }
    if not isinstance(selection, dict) or any(
        selection.get(key) is not expected
        for key, expected in expected_selection.items()
    ):
        issues.append(f"selection/leakage guard mismatch: {metrics_path}")

    if not finite_nonnegative(payload.get("training_seconds")):
        issues.append(f"training_seconds is not a non-negative scalar: {metrics_path}")
    components = payload.get("training_seconds_by_component")
    expected_components = {"known_classifier", *METHODS}
    if not isinstance(components, dict) or set(components) != expected_components:
        issues.append(f"training component set mismatch: {metrics_path}")
    elif any(not finite_nonnegative(value) for value in components.values()):
        issues.append(f"invalid component training time: {metrics_path}")
    by_report = payload.get("resource_usage_by_report")
    if not isinstance(by_report, dict) or set(by_report) != set(METHODS):
        issues.append(f"report resource set mismatch: {metrics_path}")
    else:
        for method, resource in by_report.items():
            if not isinstance(resource, dict) or not finite_nonnegative(
                resource.get("training_seconds")
            ):
                issues.append(f"invalid report resource {method}: {metrics_path}")

    run_dir = metrics_path.parent
    for artifact in ("provenance.json", "scores.npz", "model.pkl"):
        path = run_dir / artifact
        if not path.is_file() or path.stat().st_size <= 0:
            issues.append(f"missing or empty {artifact}: {run_dir}")
    scores_path = run_dir / "scores.npz"
    if scores_path.is_file() and scores_path.stat().st_size > 0:
        try:
            with np.load(scores_path, allow_pickle=False) as scores:
                required = {
                    "validation_labels",
                    "test_labels",
                    "test_unknown",
                    "test_prediction",
                    *{f"validation_{method}" for method in METHODS},
                    *{f"test_{method}" for method in METHODS},
                }
                if not required.issubset(scores.files):
                    issues.append(f"score key set incomplete: {scores_path}")
                else:
                    validation_size = len(scores["validation_labels"])
                    test_size = len(scores["test_labels"])
                    if len(scores["test_unknown"]) != test_size or len(
                        scores["test_prediction"]
                    ) != test_size:
                        issues.append(f"test score length mismatch: {scores_path}")
                    for method in METHODS:
                        validation = scores[f"validation_{method}"]
                        test = scores[f"test_{method}"]
                        if len(validation) != validation_size or len(test) != test_size:
                            issues.append(f"risk length mismatch {method}: {scores_path}")
                        if not np.isfinite(validation).all() or not np.isfinite(test).all():
                            issues.append(f"non-finite risk {method}: {scores_path}")
        except (OSError, ValueError, EOFError) as error:
            issues.append(f"cannot validate scores {scores_path}: {error}")
    return issues


def build_audit(root: Path, expected_runs: int) -> dict[str, object]:
    metrics_paths = sorted(root.glob("*/*/metrics.json"))
    failure_paths = sorted(root.glob("**/failure.json"))
    issues = [f"failure marker: {path}" for path in failure_paths]
    for path in metrics_paths:
        issues.extend(audit_run(path))
    if issues:
        state = "invalid"
    elif len(metrics_paths) == expected_runs:
        state = "complete"
    else:
        state = "incomplete"
    return {
        "schema_version": "classical_ood_report_audit_v1",
        "state": state,
        "root": str(root),
        "expected_runs": expected_runs,
        "observed_runs": len(metrics_paths),
        "method_count": len(METHODS),
        "expected_method_evaluations": expected_runs * len(METHODS),
        "failure_count": len(failure_paths),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit classical OOD reports")
    parser.add_argument("--root", required=True)
    parser.add_argument("--expected-runs", type=int, default=190)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = build_audit(Path(args.root), args.expected_runs)
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
