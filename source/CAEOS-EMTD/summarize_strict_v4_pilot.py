from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import rankdata


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
UNKNOWN_METRICS = METRICS[1:]
LOWER_IS_BETTER = {"unknown_fpr95"}
EXPECTED_SCENARIOS = {
    "cic_ton_iot": {"xss", "scanning", "ransomware"},
    "cic_iot2023": {
        "command_injection",
        "ddos_icmp_flood",
        "mirai_udpplain",
    },
}
EXPECTED_MODELS = {"mlp", "opendetect", "ronetc"}
EXPECTED_POLICY = "strict_v4_pilot_fixed_cauchy_modality_union_v1"
EXPECTED_RISK = "cauchy_modality_support_union"
CAEOS_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
NEURAL_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def report_metrics(report: object, label: str) -> dict[str, float]:
    if not isinstance(report, dict):
        raise ValueError(f"missing report for {label}")
    missing = [metric for metric in METRICS if metric not in report]
    if missing:
        raise ValueError(f"report for {label} misses {missing}")
    values = {metric: float(report[metric]) for metric in METRICS}
    if not all(np.isfinite(value) for value in values.values()):
        raise ValueError(f"non-finite report for {label}")
    return values


def split_fingerprint(metrics: dict[str, Any], label: str) -> str:
    value = (
        metrics.get("split_metadata", {})
        .get("split_fingerprint", {})
        .get("combined")
    )
    if not value:
        raise ValueError(f"missing split fingerprint for {label}")
    return str(value)


def check_artifacts(directory: Path, names: tuple[str, ...]) -> int:
    missing = [name for name in names if not (directory / name).is_file()]
    if missing:
        raise ValueError(f"missing artifacts under {directory}: {missing}")
    return len(names)


def expected_tasks() -> set[tuple[str, str]]:
    return {
        (suite, scenario)
        for suite, scenarios in EXPECTED_SCENARIOS.items()
        for scenario in scenarios
    }


def parse_caeos_task(directory: Path, seed: int) -> tuple[str, str]:
    suffix = f"_seed{seed}"
    if not directory.name.endswith(suffix):
        raise ValueError(f"unexpected CAEOS directory: {directory}")
    return directory.parent.name, directory.name[: -len(suffix)]


def parse_neural_task(directory: Path, seed: int) -> tuple[str, str, str]:
    marker = f"_seed{seed}_"
    if marker not in directory.name:
        raise ValueError(f"unexpected neural directory: {directory}")
    scenario, model = directory.name.rsplit(marker, 1)
    return directory.parent.name, scenario, model


def aggregate_table(
    blocks: dict[str, dict[str, dict[str, float]]]
) -> list[dict[str, Any]]:
    if not blocks:
        raise ValueError("no pilot blocks")
    methods = sorted(next(iter(blocks.values())))
    if any(sorted(value) != methods for value in blocks.values()):
        raise ValueError("method coverage differs across pilot blocks")
    means = {
        method: {
            metric: float(np.mean([block[method][metric] for block in blocks.values()]))
            for metric in METRICS
        }
        for method in methods
    }
    ranks = {method: {} for method in methods}
    for metric in UNKNOWN_METRICS:
        values = np.asarray([means[method][metric] for method in methods])
        ranked = rankdata(values if metric in LOWER_IS_BETTER else -values)
        for method, value in zip(methods, ranked):
            ranks[method][metric] = float(value)
    table = []
    for method in methods:
        table.append(
            {
                "method": method,
                **means[method],
                "metric_ranks": ranks[method],
                "mean_unknown_metric_rank": float(
                    np.mean([ranks[method][metric] for metric in UNKNOWN_METRICS])
                ),
            }
        )
    return sorted(
        table,
        key=lambda row: (
            row["mean_unknown_metric_rank"],
            -row["unknown_auroc"],
            row["method"],
        ),
    )


def oriented_delta(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric in LOWER_IS_BETTER else candidate - reference


def build_budget_decision(
    blocks: dict[str, dict[str, dict[str, float]]],
    overall: list[dict[str, Any]],
) -> dict[str, Any]:
    caeos = next(row for row in overall if row["method"] == "caeos")
    competitors = [row for row in overall if row["method"] != "caeos"]
    strongest: dict[str, dict[str, Any]] = {}
    for metric in METRICS:
        best = min(competitors, key=lambda row: row[metric]) if metric in LOWER_IS_BETTER else max(
            competitors, key=lambda row: row[metric]
        )
        strongest[metric] = {
            "method": best["method"],
            "value": best[metric],
            "caeos_value": caeos[metric],
            "oriented_delta": oriented_delta(caeos[metric], best[metric], metric),
        }
    worst_task_auroc_delta = min(
        oriented_delta(
            methods["caeos"]["unknown_auroc"],
            max(
                report["unknown_auroc"]
                for method, report in methods.items()
                if method != "caeos"
            ),
            "unknown_auroc",
        )
        for methods in blocks.values()
    )
    gates = {
        "mean_unknown_rank_at_most_1_5": caeos["mean_unknown_metric_rank"] <= 1.5,
        "auroc_within_0_02_of_strongest": strongest["unknown_auroc"][
            "oriented_delta"
        ]
        >= -0.02,
        "oscr_within_0_02_of_strongest": strongest["oscr"]["oriented_delta"]
        >= -0.02,
        "known_f1_within_0_02_of_strongest": strongest["known_macro_f1"][
            "oriented_delta"
        ]
        >= -0.02,
        "every_task_auroc_within_0_10": worst_task_auroc_delta >= -0.10,
    }
    expand = all(gates.values())
    return {
        "state": "expand_multiseed" if expand else "hold_for_risk_adaptation",
        "gates": gates,
        "strongest_baselines": strongest,
        "worst_task_auroc_oriented_delta": worst_task_auroc_delta,
    }


def audit_group_cache(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    groups = {
        str(label): int(count)
        for label, count in payload.get("groups_per_class", {}).items()
    }
    eligible = {str(value) for value in payload.get("eligible_labels", [])}
    excluded = {str(value) for value in payload.get("excluded_labels", [])}
    minimum = int(payload.get("minimum_groups_per_class", -1))
    passes = (
        payload.get("schema_version") == "group_supported_cache_v1"
        and minimum == 3
        and excluded == {"Uploading_Attack"}
        and eligible
        and all(groups[label] >= minimum for label in eligible)
        and all(groups[label] < minimum for label in excluded)
        and int(payload.get("output_rows", -1)) == 33000
    )
    if not passes:
        raise ValueError("CICIoT2023 group-supported cache audit failed")
    return {
        "passes": True,
        "minimum_groups_per_class": minimum,
        "eligible_class_count": len(eligible),
        "excluded_labels": sorted(excluded),
        "output_rows": int(payload["output_rows"]),
        "output_sha256": payload["output_sha256"],
    }


def load_pilot(
    caeos_root: Path, neural_root: Path, seed: int
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    fingerprints: dict[str, str] = {}
    caeos_tasks: set[tuple[str, str]] = set()
    artifact_checks = 0
    for path in sorted(caeos_root.glob("*/*/metrics.json")):
        directory = path.parent
        suite, scenario = parse_caeos_task(directory, seed)
        task = (suite, scenario)
        if task in caeos_tasks:
            raise ValueError(f"duplicate CAEOS task: {task}")
        caeos_tasks.add(task)
        artifact_checks += check_artifacts(directory, CAEOS_ARTIFACTS)
        metrics = load_json(path)
        if int(metrics.get("seed", -1)) != seed:
            raise ValueError(f"CAEOS seed mismatch for {task}")
        if metrics.get("risk_policy") != EXPECTED_POLICY:
            raise ValueError(f"CAEOS risk policy mismatch for {task}")
        expected_risks = (
            {EXPECTED_RISK}
            if isinstance(EXPECTED_RISK, str)
            else set(EXPECTED_RISK)
        )
        if metrics.get("selected_risk") not in expected_risks:
            raise ValueError(f"CAEOS selected risk mismatch for {task}")
        key = f"{suite}/{scenario}"
        fingerprints[key] = split_fingerprint(metrics, key)
        blocks[key] = {
            "caeos": report_metrics(metrics.get("selected_report"), f"{key}/caeos")
        }
    if caeos_tasks != expected_tasks():
        raise ValueError(
            f"CAEOS coverage mismatch: missing={sorted(expected_tasks() - caeos_tasks)}, "
            f"extra={sorted(caeos_tasks - expected_tasks())}"
        )

    neural_tasks: set[tuple[str, str, str]] = set()
    split_checks = 0
    for path in sorted(neural_root.glob("*/*/metrics.json")):
        directory = path.parent
        suite, scenario, model = parse_neural_task(directory, seed)
        task = (suite, scenario, model)
        if task in neural_tasks or model not in EXPECTED_MODELS:
            raise ValueError(f"invalid neural task: {task}")
        neural_tasks.add(task)
        artifact_checks += check_artifacts(directory, NEURAL_ARTIFACTS)
        metrics = load_json(path)
        if int(metrics.get("seed", -1)) != seed or metrics.get("model") != model:
            raise ValueError(f"neural identity mismatch for {task}")
        key = f"{suite}/{scenario}"
        if split_fingerprint(metrics, f"{key}/{model}") != fingerprints[key]:
            raise ValueError(f"split fingerprint mismatch for {key}/{model}")
        split_checks += 1
        reports = metrics.get("reports", {})
        if not isinstance(reports, dict):
            raise ValueError(f"missing reports for {task}")
        if model == "mlp":
            for risk, report in reports.items():
                blocks[key][f"mlp_{risk}"] = report_metrics(
                    report, f"{key}/mlp_{risk}"
                )
        else:
            blocks[key][model] = report_metrics(reports.get(model), f"{key}/{model}")
    expected_neural = {
        (*task, model) for task in expected_tasks() for model in EXPECTED_MODELS
    }
    if neural_tasks != expected_neural:
        raise ValueError(
            f"neural coverage mismatch: missing={sorted(expected_neural - neural_tasks)}, "
            f"extra={sorted(neural_tasks - expected_neural)}"
        )
    first_methods = set(next(iter(blocks.values())))
    if any(set(methods) != first_methods for methods in blocks.values()):
        raise ValueError("method coverage differs across scenarios")
    return blocks, {
        "passes": True,
        "caeos_tasks": len(caeos_tasks),
        "neural_tasks": len(neural_tasks),
        "artifact_checks": artifact_checks,
        "split_fingerprint_pair_checks": split_checks,
        "split_fingerprints_identical": True,
        "method_count": len(first_methods),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 representative pilot",
        "",
        f"Validation: **PASS**; scenarios: {report['scenario_count']}; "
        f"methods: {report['validation']['method_count']}.",
        "This is a descriptive single-seed budget gate, not confirmatory inference.",
        "",
        "| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for index, row in enumerate(report["overall"], start=1):
        lines.append(
            f"| {index} | {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.2f} |"
        )
    decision = report["budget_decision"]
    lines.extend(
        [
            "",
            "## Budget decision",
            "",
            f"State: **{decision['state']}**.",
            f"Gates: `{decision['gates']}`.",
            f"Worst per-task AUROC oriented delta: "
            f"`{decision['worst_task_auroc_oriented_delta']:+.6f}`.",
            "",
            "## Group-cache audit",
            "",
            f"Eligible CICIoT2023 classes: {report['group_cache_audit']['eligible_class_count']}; "
            f"excluded: `{report['group_cache_audit']['excluded_labels']}`; "
            f"rows: {report['group_cache_audit']['output_rows']}.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit and summarize the strict-v4 representative pilot"
    )
    parser.add_argument("--caeos-root", type=Path, required=True)
    parser.add_argument("--neural-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--group-cache-sidecar", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    actual_manifest_sha = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    if actual_manifest_sha != args.expected_manifest_sha256:
        raise ValueError("strict-v4 candidate manifest SHA mismatch")
    blocks, validation = load_pilot(args.caeos_root, args.neural_root, args.seed)
    overall = aggregate_table(blocks)
    report = {
        "schema_version": "strict_v4_representative_pilot_summary_v1",
        "status": "descriptive_single_seed_budget_gate",
        "manifest": str(args.manifest),
        "manifest_sha256": actual_manifest_sha,
        "scenario_count": len(blocks),
        "validation": validation,
        "group_cache_audit": audit_group_cache(args.group_cache_sidecar),
        "overall": overall,
        "by_suite": {
            suite: aggregate_table(
                {
                    key: value
                    for key, value in blocks.items()
                    if key.startswith(f"{suite}/")
                }
            )
            for suite in sorted(EXPECTED_SCENARIOS)
        },
        "budget_decision": build_budget_decision(blocks, overall),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(
        render_markdown(report), encoding="utf-8"
    )
    print(json.dumps({"decision": report["budget_decision"]}, indent=2))


if __name__ == "__main__":
    main()
