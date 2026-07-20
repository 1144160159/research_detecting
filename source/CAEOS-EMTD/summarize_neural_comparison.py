from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon


REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)

PAIR_ARGUMENT_FIELDS = (
    "csv",
    "config",
    "split_strategy",
    "max_per_class",
    "benign_class",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare fixed neural OOD baselines with a recorded gate method"
    )
    parser.add_argument("--gate-root", required=True)
    parser.add_argument("--neural-root", action="append", required=True, help="suite=directory")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def describe(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(array.mean()),
        "std": float(array.std()),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
    }


def paired_report(gate: list[float], baseline: list[float]) -> dict[str, object]:
    gate_array = np.asarray(gate)
    baseline_array = np.asarray(baseline)
    difference = gate_array - baseline_array
    nonzero = difference[np.abs(difference) > 1e-12]
    p_value = float(wilcoxon(nonzero).pvalue) if len(nonzero) else 1.0
    return {
        "mean_delta": float(difference.mean()),
        "wins": int((difference > 1e-12).sum()),
        "ties": int((np.abs(difference) <= 1e-12).sum()),
        "losses": int((difference < -1e-12).sum()),
        "wilcoxon_p_value": p_value,
    }


def _read_metrics(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read metrics file {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"metrics file must contain a JSON object: {path}")
    return payload


def _required(mapping: dict[str, object], key: str, context: str) -> object:
    if key not in mapping:
        raise ValueError(f"missing {context}.{key}")
    return mapping[key]


def _normalized_argument(field: str, value: object) -> object:
    if field in {"csv", "config"} and isinstance(value, str):
        return str(Path(value).expanduser().resolve(strict=False))
    return value


def protocol_identity(
    metrics: dict[str, object],
    metrics_path: Path,
) -> dict[str, object]:
    arguments = _required(metrics, "arguments", str(metrics_path))
    if not isinstance(arguments, dict):
        raise ValueError(f"{metrics_path}.arguments must be an object")
    identity = {
        "unknown_classes": _required(
            metrics, "unknown_classes", str(metrics_path)
        ),
        "sample_counts": _required(metrics, "sample_counts", str(metrics_path)),
        "split_metadata": _required(
            metrics, "split_metadata", str(metrics_path)
        ),
        "arguments": {},
    }
    for field in PAIR_ARGUMENT_FIELDS:
        value = _required(arguments, field, f"{metrics_path}.arguments")
        identity["arguments"][field] = _normalized_argument(field, value)
    return identity


def _assert_pair_identity(
    gate: dict[str, object],
    gate_path: Path,
    neural: dict[str, object],
    neural_path: Path,
    seed: int,
) -> dict[str, object]:
    gate_seed = _required(gate, "seed", str(gate_path))
    neural_seed = _required(neural, "seed", str(neural_path))
    if gate_seed != seed or neural_seed != seed:
        raise ValueError(
            f"seed mismatch for paired task seed={seed}: "
            f"gate={gate_seed!r}, neural={neural_seed!r}"
        )
    gate_identity = protocol_identity(gate, gate_path)
    neural_identity = protocol_identity(neural, neural_path)
    if gate_identity != neural_identity:
        fields = []
        for field in ("unknown_classes", "sample_counts", "split_metadata"):
            if gate_identity[field] != neural_identity[field]:
                fields.append(field)
        for field in PAIR_ARGUMENT_FIELDS:
            if (
                gate_identity["arguments"][field]
                != neural_identity["arguments"][field]
            ):
                fields.append(f"arguments.{field}")
        raise ValueError(
            f"protocol identity mismatch between {gate_path} and {neural_path}: "
            f"{', '.join(fields)}"
        )
    return gate_identity


def gate_method_name(metrics: dict[str, object], metrics_path: Path) -> str:
    candidates = []
    selection = metrics.get("risk_selection")
    if isinstance(selection, str) and selection.strip():
        candidates.append(selection.strip())
    elif isinstance(selection, dict):
        for key in ("name", "method", "risk_selection"):
            value = selection.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())
                break
    arguments = metrics.get("arguments")
    if isinstance(arguments, dict):
        value = arguments.get("risk_selection")
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    if not candidates:
        raise ValueError(
            f"cannot determine gate method from risk_selection/arguments: {metrics_path}"
        )
    if len(set(candidates)) != 1:
        raise ValueError(
            f"conflicting gate method metadata in {metrics_path}: {candidates}"
        )
    return candidates[0]


def _parse_neural_task(path: Path) -> tuple[str, int]:
    try:
        scenario, suffix = path.parent.name.rsplit("_seed", 1)
        seed = int(suffix.split("_", 1)[0])
    except (ValueError, IndexError) as error:
        raise ValueError(f"invalid neural run directory name: {path.parent.name}") from error
    if not scenario:
        raise ValueError(f"empty scenario in run directory: {path.parent.name}")
    return scenario, seed


def _parse_gate_task(path: Path) -> tuple[str, int]:
    try:
        scenario, suffix = path.parent.name.rsplit("_seed", 1)
        seed = int(suffix)
    except (ValueError, IndexError) as error:
        raise ValueError(f"invalid gate run directory name: {path.parent.name}") from error
    if not scenario:
        raise ValueError(f"empty scenario in run directory: {path.parent.name}")
    return scenario, seed


def load_runs(gate_root: Path, suite: str, neural_root: Path) -> list[dict[str, object]]:
    runs = []
    metrics_paths = sorted(neural_root.glob("*/metrics.json"))
    if not metrics_paths:
        raise ValueError(
            f"no neural metrics found for suite {suite!r} in {neural_root}"
        )
    for metrics_path in metrics_paths:
        neural = _read_metrics(metrics_path)
        scenario, seed = _parse_neural_task(metrics_path)
        gate_path = gate_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
        if not gate_path.exists():
            raise ValueError(
                f"missing gate result for {suite}/{scenario}/seed{seed}: {gate_path}"
            )
        gate = _read_metrics(gate_path)
        identity = _assert_pair_identity(
            gate, gate_path, neural, metrics_path, seed
        )
        neural_reports_payload = _required(neural, "reports", str(metrics_path))
        if not isinstance(neural_reports_payload, dict) or not neural_reports_payload:
            raise ValueError(f"empty or invalid reports object: {metrics_path}")
        neural_reports = {
            key: {metric: float(value[metric]) for metric in REPORT_METRICS}
            for key, value in neural_reports_payload.items()
        }
        selected_report = _required(gate, "selected_report", str(gate_path))
        if not isinstance(selected_report, dict):
            raise ValueError(f"invalid selected_report object: {gate_path}")
        gate_report = {
            metric: float(selected_report[metric])
            for metric in REPORT_METRICS
        }
        reports = {
            key: value["unknown_auroc"] for key, value in neural_reports.items()
        }
        runs.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "gate": float(selected_report["unknown_auroc"]),
                "gate_report": gate_report,
                "gate_method": gate_method_name(gate, gate_path),
                "gate_selected_risk": _required(
                    gate, "selected_risk", str(gate_path)
                ),
                "protocol_identity": identity,
                "neural": reports,
                "neural_reports": neural_reports,
                "oracle_neural": max(reports.values()),
            }
        )
    return runs


def merge_runs(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    """Merge method-specific roots on the same suite/scenario/seed task."""
    merged: dict[tuple[str, str, int], dict[str, object]] = {}
    for run in runs:
        key = (run["suite"], run["scenario"], int(run["seed"]))
        if key not in merged:
            merged[key] = {
                **run,
                "neural": dict(run["neural"]),
                "neural_reports": dict(run["neural_reports"]),
            }
            continue
        target = merged[key]
        if abs(float(target["gate"]) - float(run["gate"])) > 1e-12:
            raise ValueError(f"gate metric mismatch for {key}")
        for field in (
            "gate_report",
            "gate_method",
            "gate_selected_risk",
            "protocol_identity",
        ):
            if target.get(field) != run.get(field):
                raise ValueError(f"{field} mismatch for {key}")
        duplicate = set(target["neural"]) & set(run["neural"])
        if duplicate:
            raise ValueError(f"duplicate neural methods for {key}: {sorted(duplicate)}")
        target["neural"].update(run["neural"])
        target["neural_reports"].update(run["neural_reports"])
        target["oracle_neural"] = max(target["neural"].values())
    return [merged[key] for key in sorted(merged)]


def aggregate(runs: list[dict[str, object]]) -> dict[str, object]:
    if not runs:
        raise ValueError("cannot aggregate zero paired runs")
    gate = [run["gate"] for run in runs]
    gate_methods = {run.get("gate_method") for run in runs}
    if None in gate_methods or len(gate_methods) != 1:
        raise ValueError(f"inconsistent or missing gate methods: {sorted(map(str, gate_methods))}")
    expected_methods = set(runs[0]["neural"])
    if not expected_methods:
        raise ValueError("paired runs contain no neural methods")
    for run in runs[1:]:
        methods = set(run["neural"])
        if methods != expected_methods:
            task = (
                run.get("suite", "?"),
                run.get("scenario", "?"),
                run.get("seed", "?"),
            )
            raise ValueError(
                f"neural method set mismatch for {task}: "
                f"expected={sorted(expected_methods)}, actual={sorted(methods)}"
            )
    methods = sorted(expected_methods)
    result = {
        "number_of_runs": len(runs),
        "gate_method": next(iter(gate_methods)),
        "gate": describe(gate),
        "oracle_neural_upper_bound": describe([run["oracle_neural"] for run in runs]),
        "methods": {},
    }
    for method in methods:
        values = [run["neural"][method] for run in runs]
        metric_summary = {}
        for metric in REPORT_METRICS:
            gate_metric = [run["gate_report"][metric] for run in runs]
            baseline_metric = [
                run["neural_reports"][method][metric] for run in runs
            ]
            direction = -1.0 if metric == "unknown_fpr95" else 1.0
            metric_summary[metric] = {
                "gate": describe(gate_metric),
                "baseline": describe(baseline_metric),
                "oriented_gate_delta": float(
                    direction
                    * (
                        np.asarray(gate_metric, dtype=np.float64)
                        - np.asarray(baseline_metric, dtype=np.float64)
                    ).mean()
                ),
            }
        result["methods"][method] = {
            **describe(values),
            "paired_gate_comparison": paired_report(gate, values),
            "metric_summary": metric_summary,
        }
    return result


def markdown_report(report: dict[str, object]) -> str:
    lines = ["# Neural open-set baseline comparison", ""]
    for suite, summary in report["by_suite"].items():
        gate_method = summary["gate_method"]
        lines.extend(
            [
                f"## {suite}", "",
                f"Runs: {summary['number_of_runs']}", "",
                "| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |",
                "|---|---:|---:|---:|---:|---:|---:|",
                f"| {gate_method} | {summary['gate']['mean']:.6f} | {summary['gate']['std']:.6f} | {summary['gate']['minimum']:.6f} | - | - | - |",
            ]
        )
        ordered = sorted(summary["methods"].items(), key=lambda item: -item[1]["mean"])
        for method, values in ordered:
            paired = values["paired_gate_comparison"]
            lines.append(
                f"| {method} | {values['mean']:.6f} | {values['std']:.6f} | {values['minimum']:.6f} | "
                f"{paired['mean_delta']:+.6f} | {paired['wins']}/{paired['ties']}/{paired['losses']} | {paired['wilcoxon_p_value']:.3g} |"
            )
        oracle = summary["oracle_neural_upper_bound"]
        lines.extend(["", f"Test-label oracle neural upper bound: {oracle['mean']:.6f}; this is diagnostic only and is not a deployable baseline.", ""])
        lines.extend(
            [
                "| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        gate_metrics = {
            metric: describe([run["gate_report"][metric] for run in report["runs"] if run["suite"] == suite])["mean"]
            for metric in REPORT_METRICS
        }
        lines.append(
            f"| {gate_method} | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |"
            % tuple(gate_metrics[metric] for metric in REPORT_METRICS)
        )
        for method, values in ordered:
            metrics = values["metric_summary"]
            lines.append(
                "| %s | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |"
                % (
                    method,
                    *(
                        metrics[metric]["baseline"]["mean"]
                        for metric in REPORT_METRICS
                    ),
                )
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_arguments()
    gate_root = Path(args.gate_root)
    roots = defaultdict(list)
    for value in args.neural_root:
        if "=" not in value:
            raise ValueError(f"--neural-root must use suite=directory: {value!r}")
        suite, path = value.split("=", 1)
        if not suite.strip() or not path.strip():
            raise ValueError(f"--neural-root must use suite=directory: {value!r}")
        roots[suite].append(Path(path))
    all_runs = []
    by_suite = {}
    for suite, paths in roots.items():
        runs = merge_runs(
            [
                run
                for path in paths
                for run in load_runs(gate_root, suite, path)
            ]
        )
        gate_paths = sorted((gate_root / suite).glob("*/metrics.json"))
        expected_tasks = {_parse_gate_task(path) for path in gate_paths}
        actual_tasks = {(run["scenario"], int(run["seed"])) for run in runs}
        if not expected_tasks:
            raise ValueError(f"no gate metrics found for suite {suite!r}")
        if actual_tasks != expected_tasks:
            raise ValueError(
                f"task coverage mismatch for suite {suite!r}: "
                f"missing={sorted(expected_tasks - actual_tasks)}, "
                f"unexpected={sorted(actual_tasks - expected_tasks)}"
            )
        all_runs.extend(runs)
        by_suite[suite] = aggregate(runs)
    report = {"by_suite": by_suite, "global": aggregate(all_runs), "runs": all_runs}
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "comparison.md").write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({"by_suite": by_suite, "global": report["global"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
