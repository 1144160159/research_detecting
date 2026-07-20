from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


REPORTS = (
    "cauchy_modality_support_union",
    "missing_aware_cauchy_modality_support_union",
    "missing_aware_max_modality_knn",
)
METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)
ARTIFACTS = ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")


def canonical_manifest_hash(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    encoded = json.dumps(
        core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = payload.get("manifest_sha256")
    actual = canonical_manifest_hash(payload)
    if expected != actual:
        raise ValueError(f"manifest SHA mismatch: expected={expected} actual={actual}")
    conditions = payload.get("conditions", [])
    identifiers = [condition.get("id") for condition in conditions]
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise ValueError("manifest condition identifiers must be non-empty and unique")
    expected_runs = len(conditions) * len(payload.get("scenarios", [])) * len(
        payload.get("seeds", [])
    )
    if payload.get("expected_run_count") != expected_runs:
        raise ValueError("manifest expected_run_count is inconsistent")
    if tuple(payload.get("reports", ())) != REPORTS:
        raise ValueError("manifest report set is inconsistent with the frozen auditor")
    return payload


def _assert_close(left: float, right: float, label: str) -> None:
    if abs(float(left) - float(right)) > 1e-12:
        raise ValueError(f"{label} mismatch: {left} != {right}")


def _validate_corruption(
    protocol: dict[str, Any], condition: dict[str, Any], run_label: str
) -> None:
    test = protocol.get("test_corruption", {})
    _assert_close(
        protocol.get("train_label_noise_fraction", -1),
        condition["train_label_noise"],
        f"{run_label} train label noise",
    )
    if test.get("kind") != condition["test_corruption_kind"]:
        raise ValueError(f"{run_label} test corruption kind mismatch")
    expected_modality = condition.get("test_corruption_modality")
    if condition["test_corruption_kind"] == "none":
        expected_modality = None
    if test.get("modality") != expected_modality:
        raise ValueError(f"{run_label} test corruption modality mismatch")
    _assert_close(
        test.get("severity", -1),
        condition["test_corruption_severity"],
        f"{run_label} test corruption severity",
    )
    if test.get("seed") != condition["test_corruption_seed"]:
        raise ValueError(f"{run_label} test corruption seed mismatch")
    required_guards = {
        "train_only_label_corruption": True,
        "validation_is_clean": True,
        "test_only_feature_corruption": True,
        "unknown_or_test_labels_used_to_generate_corruption": False,
    }
    for key, expected in required_guards.items():
        if protocol.get(key) is not expected:
            raise ValueError(f"{run_label} corruption guard failed: {key}")


def _command_value(command: list[str], option: str) -> str:
    try:
        return command[command.index(option) + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"provenance command is missing {option}") from error


def _validate_provenance(
    payload: dict[str, Any], condition: dict[str, Any], scenario: str, seed: int
) -> None:
    command = payload.get("command", [])
    expected = {
        "--test-corruption-kind": condition["test_corruption_kind"],
        "--test-corruption-modality": str(condition["test_corruption_modality"]),
        "--test-corruption-severity": str(condition["test_corruption_severity"]),
        "--test-corruption-seed": str(condition["test_corruption_seed"]),
        "--train-label-noise": str(condition["train_label_noise"]),
    }
    for option, value in expected.items():
        if _command_value(command, option) != value:
            raise ValueError(f"provenance {option} mismatch")
    task = payload.get("task", {})
    if task.get("scenario") != scenario or task.get("seed") != seed:
        raise ValueError("provenance task identity mismatch")
    code = payload.get("code", {})
    if not isinstance(code.get("sha256"), str) or len(code["sha256"]) != 64:
        raise ValueError("provenance code identity is missing")


def load_and_audit(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    conditions = manifest["conditions"]
    scenarios = manifest["scenarios"]
    seeds = manifest["seeds"]
    rows: list[dict[str, Any]] = []
    failures = list(root.rglob("failure.json")) if root.exists() else []
    if failures:
        raise ValueError(f"corruption pilot contains {len(failures)} failure artifacts")
    fingerprints: dict[tuple[str, int], str] = {}
    clean_thresholds: dict[tuple[str, int], float] = {}
    for condition in conditions:
        condition_id = condition["id"]
        for scenario in scenarios:
            for seed in seeds:
                run = root / condition_id / "edge_iiot" / f"{scenario}_seed{seed}"
                missing = [name for name in ARTIFACTS if not (run / name).is_file()]
                if missing:
                    raise ValueError(f"missing artifacts for {run}: {missing}")
                metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
                provenance = json.loads(
                    (run / "provenance.json").read_text(encoding="utf-8")
                )
                label = f"{condition_id}/{scenario}/seed{seed}"
                _validate_corruption(metrics.get("corruption_protocol", {}), condition, label)
                _validate_provenance(provenance, condition, scenario, seed)
                reports = metrics.get("reports", {})
                if any(name not in reports for name in REPORTS):
                    raise ValueError(f"{label} is missing required reports")
                split = metrics.get("split_metadata", {}).get("split_fingerprint", {})
                combined = split.get("combined")
                if not isinstance(combined, str) or len(combined) != 64:
                    raise ValueError(f"{label} has no valid split fingerprint")
                key = (scenario, seed)
                if key in fingerprints and fingerprints[key] != combined:
                    raise ValueError(f"split fingerprint changed across conditions: {label}")
                fingerprints[key] = combined
                threshold = metrics.get("validation_thresholds", {}).get(
                    "cauchy_modality_support_union"
                )
                if threshold is None:
                    raise ValueError(f"{label} is missing the current-risk threshold")
                if condition_id == "clean":
                    clean_thresholds[key] = float(threshold)
                elif condition["train_label_noise"] == 0.0:
                    if key not in clean_thresholds:
                        raise ValueError("clean condition must precede test corruptions")
                    _assert_close(
                        threshold,
                        clean_thresholds[key],
                        f"{label} clean-validation threshold",
                    )
                rows.append(
                    {
                        "condition": condition_id,
                        "family": condition["family"],
                        "scenario": scenario,
                        "seed": seed,
                        "split_fingerprint": combined,
                        "reports": {name: reports[name] for name in REPORTS},
                    }
                )
    actual_metrics = len(list(root.rglob("metrics.json"))) if root.exists() else 0
    if actual_metrics != manifest["expected_run_count"]:
        raise ValueError(
            f"unexpected metrics count: {actual_metrics} != {manifest['expected_run_count']}"
        )
    return rows


def aggregate(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for report_name, report in row["reports"].items():
            grouped[(row["condition"], report_name)].append(report)
    table: list[dict[str, Any]] = []
    clean: dict[str, dict[str, float]] = {}
    for condition in manifest["conditions"]:
        condition_id = condition["id"]
        for report_name in REPORTS:
            reports = grouped[(condition_id, report_name)]
            values = {metric: mean(float(report[metric]) for report in reports) for metric in METRICS}
            if condition_id == "clean":
                clean[report_name] = values
            reference = clean[report_name]
            table.append(
                {
                    "condition": condition_id,
                    "family": condition["family"],
                    "report": report_name,
                    "scenario_count": len(reports),
                    "mean": values,
                    "delta_from_clean": {
                        metric: values[metric] - reference[metric] for metric in METRICS
                    },
                }
            )
    current_rows = [
        row for row in table if row["report"] == "cauchy_modality_support_union"
    ]
    worst = {
        metric: min(current_rows, key=lambda row: row["mean"][metric])[
            "condition"
        ]
        for metric in ("known_macro_f1", "unknown_auroc", "unknown_aupr", "oscr")
    }
    worst["unknown_fpr95"] = max(
        current_rows, key=lambda row: row["mean"]["unknown_fpr95"]
    )["condition"]
    return {
        "schema_version": "strict_v2_open_set_corruption_pilot_summary_v1",
        "state": "complete",
        "scope": "single-seed descriptive pilot; not a significance claim",
        "expected_runs": manifest["expected_run_count"],
        "completed_runs": len(rows),
        "failure_count": 0,
        "split_fingerprints_identical_across_conditions": True,
        "test_corruption_validation_thresholds_identical_to_clean": True,
        "unknown_or_test_labels_used_to_generate_corruption": False,
        "table": table,
        "current_risk_worst_condition": worst,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Strict-v2 Open-set Corruption Pilot",
        "",
        f"State: **{summary['state']}** ({summary['completed_runs']}/{summary['expected_runs']}, failures={summary['failure_count']})",
        "",
        "This is a single-seed descriptive pilot and is not a statistical significance claim.",
        "",
        "| Condition | Report | Known F1 | AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["table"]:
        values = row["mean"]
        lines.append(
            "| {condition} | {report} | {known_macro_f1:.4f} | {unknown_auroc:.4f} | "
            "{unknown_aupr:.4f} | {unknown_fpr95:.4f} | {oscr:.4f} | "
            "{known_acceptance_rate:.4f} | {unknown_rejection_rate:.4f} |".format(
                condition=row["condition"], report=row["report"], **values
            )
        )
    lines.extend(
        [
            "",
            "Audit guarantees: exact matrix, complete artifacts, zero failures, fixed split fingerprints, clean validation for test-only corruption, and no unknown/test-label use in corruption generation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit and summarize strict open-set corruption runs")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(args.manifest)
    rows = load_and_audit(args.root, manifest)
    summary = aggregate(rows, manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    args.markdown_output.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps({"state": summary["state"], "runs": len(rows)}))


if __name__ == "__main__":
    main()
