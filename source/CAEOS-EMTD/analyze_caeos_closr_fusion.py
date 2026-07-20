from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from caeos.hybrid_open_set import evaluate_hybrid_open_set


FUSION_METHODS = (
    "rank_mean",
    "rank_union",
    "rank_max",
    "rank_min",
    "rank_cauchy",
    "rank_bonferroni",
)
REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}


def empirical_percentile(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Map risk to its known-validation empirical CDF without test fitting."""

    ref = np.sort(np.asarray(reference, dtype=np.float64).reshape(-1))
    query = np.asarray(values, dtype=np.float64).reshape(-1)
    if not len(ref):
        raise ValueError("risk calibration requires known validation samples")
    if not np.isfinite(ref).all() or not np.isfinite(query).all():
        raise ValueError("risk calibration requires finite values")
    return (np.searchsorted(ref, query, side="right") + 0.5) / (len(ref) + 1.0)


def fixed_fusions(caeos_tail: np.ndarray, closr_tail: np.ndarray) -> dict[str, np.ndarray]:
    a = np.asarray(caeos_tail, dtype=np.float64)
    b = np.asarray(closr_tail, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError("CAEOS and CLOSR risks must have matching shapes")
    p_values = np.stack(
        [np.clip(1.0 - a, 1e-6, 1.0 - 1e-6), np.clip(1.0 - b, 1e-6, 1.0 - 1e-6)],
        axis=1,
    )
    cauchy_statistic = np.tan((0.5 - p_values) * np.pi).mean(axis=1)
    cauchy_p = 0.5 - np.arctan(cauchy_statistic) / np.pi
    bonferroni_p = np.minimum(1.0, 2.0 * p_values.min(axis=1))
    return {
        "rank_mean": 0.5 * (a + b),
        "rank_union": 1.0 - (1.0 - a) * (1.0 - b),
        "rank_max": np.maximum(a, b),
        "rank_min": np.minimum(a, b),
        "rank_cauchy": np.clip(1.0 - cauchy_p, 0.0, 1.0),
        "rank_bonferroni": np.clip(1.0 - bonferroni_p, 0.0, 1.0),
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validation-calibrated fixed fusion of CAEOS and an expert risk"
    )
    parser.add_argument("--gate-root", required=True)
    parser.add_argument("--expert-root")
    parser.add_argument("--expert-name", default="closr")
    parser.add_argument(
        "--expert-model",
        help=(
            "run-directory model suffix; defaults to --expert-name. Use mlp "
            "for risks emitted by the shared MLP checkpoint"
        ),
    )
    parser.add_argument(
        "--closr-root",
        help="legacy alias for --expert-root when --expert-name=closr",
    )
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument(
        "--seeds",
        help="optional comma-separated seed allowlist for development-only analysis",
    )
    parser.add_argument(
        "--suites",
        help="optional comma-separated suite allowlist",
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_allowlist(value: str | None, cast=str) -> set[object] | None:
    if value is None:
        return None
    tokens = [token.strip() for token in value.split(",")]
    if not tokens or any(not token for token in tokens):
        raise ValueError("allowlists must be non-empty comma-separated values")
    try:
        result = {cast(token) for token in tokens}
    except ValueError as error:
        raise ValueError(f"invalid allowlist: {value!r}") from error
    if len(result) != len(tokens):
        raise ValueError(f"allowlist contains duplicates: {value!r}")
    return result


def selected_gate_risk(metrics: dict, scores: np.lib.npyio.NpzFile) -> str:
    details = metrics.get("risk_selection_details", {})
    name = details.get("selected_risk") or metrics.get("selected_risk")
    if name is None:
        raise ValueError("gate metrics do not record the selected risk")
    if f"validation_{name}" not in scores or f"test_{name}" not in scores:
        raise ValueError(f"selected gate risk {name!r} is absent from scores.npz")
    return name


def task_report(
    gate_dir: Path,
    expert_dir: Path,
    expert_name: str,
    acceptance: float,
) -> dict[str, object]:
    with (gate_dir / "metrics.json").open("r", encoding="utf-8") as handle:
        gate_metrics = json.load(handle)
    with (expert_dir / "metrics.json").open("r", encoding="utf-8") as handle:
        expert_metrics = json.load(handle)
    gate_selection = gate_metrics.get("risk_selection_details", {})
    if gate_selection.get("unknown_or_test_labels_used_for_selection") is not False:
        raise ValueError("CAEOS risk selection leakage guard failed")
    expert_selection = expert_metrics.get("selection_evidence", {})
    if (
        expert_selection.get("unknown_or_test_labels_used_for_fitting_or_selection")
        is not False
    ):
        raise ValueError("expert fitting/selection leakage guard failed")
    gate_fingerprint = gate_metrics.get("split_metadata", {}).get(
        "split_fingerprint", {}
    )
    expert_fingerprint = expert_metrics.get("split_metadata", {}).get(
        "split_fingerprint", {}
    )
    if not gate_fingerprint.get("combined"):
        raise ValueError("CAEOS split fingerprint is missing")
    if gate_fingerprint != expert_fingerprint:
        raise ValueError("CAEOS and expert split fingerprints do not match")
    with np.load(gate_dir / "scores.npz") as gate_scores, np.load(
        expert_dir / "scores.npz"
    ) as expert_scores:
        risk_name = selected_gate_risk(gate_metrics, gate_scores)
        unknown = gate_scores["test_unknown"].astype(bool)
        labels = gate_scores["test_labels"]
        prediction = gate_scores["test_prediction"]
        if not np.array_equal(unknown, expert_scores["test_unknown"].astype(bool)):
            raise ValueError("gate and expert unknown masks do not match")
        if not np.array_equal(labels, expert_scores["test_labels"]):
            raise ValueError("gate and expert test labels do not match")

        validation_key = f"validation_{expert_name}"
        test_key = f"test_{expert_name}"
        if validation_key not in expert_scores or test_key not in expert_scores:
            raise ValueError(
                f"expert scores do not contain {validation_key!r} and {test_key!r}"
            )

        gate_validation = empirical_percentile(
            gate_scores[f"validation_{risk_name}"],
            gate_scores[f"validation_{risk_name}"],
        )
        expert_validation = empirical_percentile(
            expert_scores[validation_key], expert_scores[validation_key]
        )
        gate_test = empirical_percentile(
            gate_scores[f"validation_{risk_name}"],
            gate_scores[f"test_{risk_name}"],
        )
        expert_test = empirical_percentile(
            expert_scores[validation_key], expert_scores[test_key]
        )
        correlation = float(np.corrcoef(gate_validation, expert_validation)[0, 1])
        top_gate = gate_validation >= 0.95
        top_expert = expert_validation >= 0.95
        top_union = top_gate | top_expert
        top_intersection = top_gate & top_expert
        validation_diagnostics = {
            "rank_correlation": correlation,
            "mean_absolute_rank_difference": float(
                np.mean(np.abs(gate_validation - expert_validation))
            ),
            "top5_jaccard": float(
                top_intersection.sum() / max(1, top_union.sum())
            ),
            "top5_xor_rate": float(np.mean(top_gate ^ top_expert)),
        }
        validation_fusions = fixed_fusions(gate_validation, expert_validation)
        test_fusions = fixed_fusions(gate_test, expert_test)

        target = unknown.astype(np.int64)
        gate_auroc = float(roc_auc_score(target, gate_test))
        expert_auroc = float(roc_auc_score(target, expert_test))
        gate_threshold = float(np.quantile(gate_validation, acceptance))
        expert_threshold = float(np.quantile(expert_validation, acceptance))
        gate_report = evaluate_hybrid_open_set(
            labels, unknown, prediction, gate_test, gate_threshold
        )
        expert_report = evaluate_hybrid_open_set(
            labels, unknown, prediction, expert_test, expert_threshold
        )
        reports = {}
        for name, risk in test_fusions.items():
            threshold = float(np.quantile(validation_fusions[name], acceptance))
            reports[name] = evaluate_hybrid_open_set(
                labels, unknown, prediction, risk, threshold
            )
        return {
            "gate_selected_risk": risk_name,
            "gate_auroc": gate_auroc,
            "gate_report": gate_report,
            "expert_name": expert_name,
            "expert_auroc": expert_auroc,
            "expert_report": expert_report,
            "audit": {
                "split_fingerprint": gate_fingerprint["combined"],
                "split_fingerprints_identical": True,
                "caeos_unknown_or_test_labels_used_for_selection": False,
                "expert_unknown_or_test_labels_used_for_fitting_or_selection": False,
                "fusion_calibration_split": "known_only_validation",
                "test_labels_used_for_final_metrics_only": True,
            },
            "validation_diagnostics": validation_diagnostics,
            "reports": reports,
            "oracle_fixed_fusion_auroc": max(
                report["unknown_auroc"] for report in reports.values()
            ),
        }


def summarize(runs: list[dict[str, object]]) -> dict[str, object]:
    summary = {}
    gate = np.asarray([run["gate_auroc"] for run in runs], dtype=np.float64)
    expert = np.asarray([run["expert_auroc"] for run in runs], dtype=np.float64)
    for method in FUSION_METHODS:
        values = np.asarray(
            [run["reports"][method]["unknown_auroc"] for run in runs],
            dtype=np.float64,
        )
        delta = values - gate
        metric_summary = {}
        for metric in REPORT_METRICS:
            gate_values = np.asarray(
                [run["gate_report"][metric] for run in runs], dtype=np.float64
            )
            candidate_values = np.asarray(
                [run["reports"][method][metric] for run in runs], dtype=np.float64
            )
            direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
            oriented_delta = direction * (candidate_values - gate_values)
            metric_summary[metric] = {
                "gate_mean": float(gate_values.mean()),
                "candidate_mean": float(candidate_values.mean()),
                "oriented_mean_delta": float(oriented_delta.mean()),
                "wins_ties_losses": [
                    int((oriented_delta > 1e-12).sum()),
                    int((np.abs(oriented_delta) <= 1e-12).sum()),
                    int((oriented_delta < -1e-12).sum()),
                ],
            }
        safety = {
            "auroc_improves": metric_summary["unknown_auroc"][
                "oriented_mean_delta"
            ]
            > 0.0,
            "aupr_nonregression": metric_summary["unknown_aupr"][
                "oriented_mean_delta"
            ]
            >= -0.01,
            "fpr95_nonregression": metric_summary["unknown_fpr95"][
                "oriented_mean_delta"
            ]
            >= -0.01,
            "oscr_nonregression": metric_summary["oscr"][
                "oriented_mean_delta"
            ]
            >= -0.01,
        }
        safety["passes"] = all(safety.values())
        summary[method] = {
            "mean_auroc": float(values.mean()),
            "minimum_auroc": float(values.min()),
            "mean_delta_vs_gate": float(delta.mean()),
            "wins_ties_losses_vs_gate": [
                int((delta > 1e-12).sum()),
                int((np.abs(delta) <= 1e-12).sum()),
                int((delta < -1e-12).sum()),
            ],
            "wins_vs_both_experts": int(((values > gate) & (values > expert)).sum()),
            "metrics": metric_summary,
            "development_safety_gate": safety,
        }
    return {
        "number_of_runs": len(runs),
        "gate_mean_auroc": float(gate.mean()),
        "expert_name": runs[0]["expert_name"],
        "expert_mean_auroc": float(expert.mean()),
        "methods": summary,
    }


def main() -> None:
    args = parse_arguments()
    gate_root = Path(args.gate_root)
    root_value = args.expert_root or args.closr_root
    if root_value is None:
        raise ValueError("--expert-root is required")
    if args.closr_root and args.expert_name != "closr":
        raise ValueError("--closr-root can only be used with --expert-name=closr")
    expert_root = Path(root_value)
    expert_model = args.expert_model or args.expert_name
    allowed_seeds = parse_allowlist(args.seeds, int)
    allowed_suites = parse_allowlist(args.suites)
    runs = []
    for metrics_path in sorted(gate_root.glob("*/*/metrics.json")):
        suite = metrics_path.parent.parent.name
        stem = metrics_path.parent.name
        with metrics_path.open("r", encoding="utf-8") as handle:
            gate_metrics = json.load(handle)
        seed = int(gate_metrics["seed"])
        if allowed_seeds is not None and seed not in allowed_seeds:
            continue
        if allowed_suites is not None and suite not in allowed_suites:
            continue
        expert_dir = expert_root / suite / f"{stem}_{expert_model}"
        if not (expert_dir / "metrics.json").exists():
            continue
        report = task_report(
            metrics_path.parent, expert_dir, args.expert_name, args.known_acceptance
        )
        report.update({"suite": suite, "task": stem})
        runs.append(report)
    if not runs:
        raise ValueError("no matching CAEOS/expert task pairs were found")
    result = {
        "calibration": "each expert empirical CDF fitted on known validation only",
        "candidate_status": (
            "development_only; fixed fusion must be frozen and confirmed on new seeds"
        ),
        "selection_scope": {
            "seeds": sorted(allowed_seeds) if allowed_seeds is not None else "all",
            "suites": sorted(allowed_suites) if allowed_suites is not None else "all",
            "expert_model": expert_model,
        },
        "overall": summarize(runs),
        "by_suite": {
            suite: summarize([run for run in runs if run["suite"] == suite])
            for suite in sorted({run["suite"] for run in runs})
        },
        "runs": runs,
        "arguments": vars(args),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result["overall"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
