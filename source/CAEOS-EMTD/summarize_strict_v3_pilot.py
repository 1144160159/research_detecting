from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from analyze_entropy_cauchy_fusion import task_report as replay_caeos_fusions


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}
EXPECTED_SCENARIOS = {
    "nf_unsw": {"exploits", "fuzzers", "reconnaissance"},
    "cicids2017": {"ddos", "portscan", "web_bruteforce"},
}
EXPECTED_MODELS = {"mlp", "opendetect", "ronetc"}
CAEOS_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
NEURAL_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit and summarize the frozen strict-v3 representative pilot"
    )
    parser.add_argument("--caeos-root", required=True)
    parser.add_argument("--neural-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, object]:
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
    return {metric: float(report[metric]) for metric in METRICS}


def split_fingerprint(metrics: dict[str, object], label: str) -> str:
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


def parse_caeos_task(directory: Path, seed: int) -> tuple[str, str]:
    suite = directory.parent.name
    suffix = f"_seed{seed}"
    if not directory.name.endswith(suffix):
        raise ValueError(f"unexpected CAEOS task directory: {directory}")
    return suite, directory.name[: -len(suffix)]


def parse_neural_task(directory: Path, seed: int) -> tuple[str, str, str]:
    suite = directory.parent.name
    marker = f"_seed{seed}_"
    if marker not in directory.name:
        raise ValueError(f"unexpected neural task directory: {directory}")
    scenario, model = directory.name.rsplit(marker, 1)
    return suite, scenario, model


def validate_expected_tasks(observed: set[tuple[str, str]], label: str) -> None:
    expected = {
        (suite, scenario)
        for suite, scenarios in EXPECTED_SCENARIOS.items()
        for scenario in scenarios
    }
    if observed != expected:
        raise ValueError(
            f"{label} task coverage mismatch: "
            f"missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )


def aggregate_table(
    blocks: dict[str, dict[str, dict[str, float]]]
) -> list[dict[str, object]]:
    methods = sorted(next(iter(blocks.values())))
    means = {
        method: {
            metric: float(np.mean([blocks[key][method][metric] for key in blocks]))
            for metric in METRICS
        }
        for method in methods
    }
    ranks: dict[str, dict[str, float]] = {method: {} for method in methods}
    for metric in METRICS[1:]:
        values = np.asarray([means[method][metric] for method in methods])
        ranked = rankdata(values if metric in LOWER_IS_BETTER else -values)
        for method, rank_value in zip(methods, ranked):
            ranks[method][metric] = float(rank_value)
    table = [
        {
            "method": method,
            **means[method],
            "metric_ranks": ranks[method],
            "mean_unknown_metric_rank": float(
                np.mean([ranks[method][metric] for metric in METRICS[1:]])
            ),
        }
        for method in methods
    ]
    return sorted(
        table,
        key=lambda row: (
            row["mean_unknown_metric_rank"],
            -row["unknown_auroc"],
            row["method"],
        ),
    )


def build_summary(
    blocks: dict[str, dict[str, dict[str, float]]]
) -> dict[str, object]:
    overall = aggregate_table(blocks)
    by_suite = {
        suite: aggregate_table(
            {key: value for key, value in blocks.items() if key.startswith(f"{suite}/")}
        )
        for suite in sorted(EXPECTED_SCENARIOS)
    }
    lookup = {row["method"]: row for row in overall}
    reference = lookup["caeos_current"]
    candidate = lookup["caeos_rank_union"]
    deltas = {
        metric: (
            reference[metric] - candidate[metric]
            if metric in LOWER_IS_BETTER
            else candidate[metric] - reference[metric]
        )
        for metric in METRICS
    }
    gate = {
        "auroc_improves": deltas["unknown_auroc"] > 0.0,
        "aupr_nonregression": deltas["unknown_aupr"] >= -0.01,
        "fpr95_nonregression": deltas["unknown_fpr95"] >= -0.01,
        "oscr_nonregression": deltas["oscr"] >= -0.01,
    }
    gate["passes"] = all(gate.values())
    return {
        "status": "descriptive_single_seed_pilot",
        "scenario_count": len(blocks),
        "method_count": len(overall),
        "overall": overall,
        "by_suite": by_suite,
        "rank_union_vs_current": {
            "oriented_mean_deltas": deltas,
            "development_generalization_gate": gate,
        },
    }


def load_pilot(
    caeos_root: Path,
    neural_root: Path,
    seed: int,
    acceptance: float,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, object]]:
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    fingerprints: dict[str, str] = {}
    caeos_tasks: set[tuple[str, str]] = set()
    artifact_checks = 0
    endpoint_replay_checks = 0
    for path in sorted(caeos_root.glob("*/*/metrics.json")):
        directory = path.parent
        artifact_checks += check_artifacts(directory, CAEOS_ARTIFACTS)
        suite, scenario = parse_caeos_task(directory, seed)
        task = (suite, scenario)
        if task in caeos_tasks:
            raise ValueError(f"duplicate CAEOS task: {task}")
        caeos_tasks.add(task)
        metrics = load_json(path)
        if int(metrics.get("seed", -1)) != seed:
            raise ValueError(f"CAEOS seed mismatch for {task}")
        if metrics.get("risk_policy") != "strict_v3_pilot_current_edge_policy":
            raise ValueError(f"CAEOS risk policy mismatch for {task}")
        if metrics.get("selected_risk") != "cauchy_modality_support_union":
            raise ValueError(f"CAEOS selected risk mismatch for {task}")
        key = f"{suite}/{scenario}"
        fingerprints[key] = split_fingerprint(metrics, key)
        replay = replay_caeos_fusions(directory, acceptance)
        endpoint_replay_checks += int(replay["endpoint_replay_checks"])
        blocks[key] = {
            "caeos_current": report_metrics(metrics["selected_report"], f"{key}/current"),
            "caeos_entropy": report_metrics(replay["reports"]["entropy"], f"{key}/entropy"),
            "caeos_cauchy_all": report_metrics(
                replay["reports"]["cauchy_all"], f"{key}/cauchy_all"
            ),
            "caeos_rank_union": report_metrics(
                replay["reports"]["rank_union"], f"{key}/rank_union"
            ),
        }
    validate_expected_tasks(caeos_tasks, "CAEOS")

    neural_tasks: set[tuple[str, str, str]] = set()
    split_checks = 0
    for path in sorted(neural_root.glob("*/*/metrics.json")):
        directory = path.parent
        artifact_checks += check_artifacts(directory, NEURAL_ARTIFACTS)
        suite, scenario, model = parse_neural_task(directory, seed)
        task = (suite, scenario, model)
        if task in neural_tasks:
            raise ValueError(f"duplicate neural task: {task}")
        neural_tasks.add(task)
        if model not in EXPECTED_MODELS:
            raise ValueError(f"unexpected neural model: {model}")
        metrics = load_json(path)
        if int(metrics.get("seed", -1)) != seed or metrics.get("model") != model:
            raise ValueError(f"neural identity mismatch for {task}")
        key = f"{suite}/{scenario}"
        if split_fingerprint(metrics, f"{key}/{model}") != fingerprints[key]:
            raise ValueError(f"split fingerprint mismatch for {key}/{model}")
        split_checks += 1
        reports = metrics.get("reports", {})
        if model == "mlp":
            for risk, report in reports.items():
                blocks[key][f"mlp_{risk}"] = report_metrics(
                    report, f"{key}/mlp_{risk}"
                )
        else:
            blocks[key][model] = report_metrics(reports.get(model), f"{key}/{model}")
    expected_neural = {
        (suite, scenario, model)
        for suite, scenarios in EXPECTED_SCENARIOS.items()
        for scenario in scenarios
        for model in EXPECTED_MODELS
    }
    if neural_tasks != expected_neural:
        raise ValueError(
            "neural task coverage mismatch: "
            f"missing={sorted(expected_neural - neural_tasks)}, "
            f"extra={sorted(neural_tasks - expected_neural)}"
        )
    method_sets = {key: set(value) for key, value in blocks.items()}
    first = next(iter(method_sets.values()))
    mismatched_methods = {
        key: sorted(value ^ first) for key, value in method_sets.items() if value != first
    }
    if mismatched_methods:
        raise ValueError(f"method coverage mismatch: {mismatched_methods}")
    return blocks, {
        "passes": True,
        "caeos_tasks": len(caeos_tasks),
        "neural_tasks": len(neural_tasks),
        "artifact_checks": artifact_checks,
        "split_fingerprint_pair_checks": split_checks,
        "split_fingerprints_identical": True,
        "endpoint_replay_checks": endpoint_replay_checks,
        "method_count": len(first),
    }


def markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    lines = [
        "# Strict-v3 representative pilot",
        "",
        f"Validation: **{'PASS' if report['validation']['passes'] else 'FAIL'}**; "
        f"scenarios: {summary['scenario_count']}; methods: {summary['method_count']}.",
        "This is a descriptive single-seed pilot, not confirmatory inference.",
        "",
        "| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for index, row in enumerate(summary["overall"], start=1):
        lines.append(
            f"| {index} | {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.2f} |"
        )
    gate = summary["rank_union_vs_current"]
    lines.extend(
        [
            "",
            "## Frozen fusion generalization gate",
            "",
            f"Gate: **{'PASS' if gate['development_generalization_gate']['passes'] else 'FAIL'}**.",
            f"Oriented mean deltas: `{gate['oriented_mean_deltas']}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    manifest_path = Path(args.manifest)
    actual_manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if actual_manifest_sha != args.expected_manifest_sha256:
        raise ValueError(
            f"manifest SHA mismatch: expected={args.expected_manifest_sha256} "
            f"actual={actual_manifest_sha}"
        )
    manifest = load_json(manifest_path)
    if manifest.get("status") != "frozen_queued" or int(manifest.get("seed", -1)) != args.seed:
        raise ValueError("manifest status or seed mismatch")
    blocks, validation = load_pilot(
        Path(args.caeos_root), Path(args.neural_root), args.seed, args.known_acceptance
    )
    report = {
        "schema_version": "strict_v3_representative_pilot_summary_v1",
        "manifest": args.manifest,
        "manifest_sha256": actual_manifest_sha,
        "validation": validation,
        "summary": build_summary(blocks),
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "summary.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"validation": validation, "summary": report["summary"]}, indent=2))


if __name__ == "__main__":
    main()
