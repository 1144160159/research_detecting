from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set


REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
    "unknown_f1",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Known-only threshold sensitivity for a frozen CAEOS risk"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--risk", required=True)
    parser.add_argument("--acceptances", default="0.90,0.95,0.975,0.99")
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--expected-scenarios", type=int, required=True)
    parser.add_argument(
        "--allow-extra-seeds",
        action="store_true",
        help="Ignore non-requested seeds while retaining exact requested-seed coverage checks",
    )
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def parse_float_set(value: str, label: str) -> tuple[float, ...]:
    parsed = tuple(float(token.strip()) for token in value.split(",") if token.strip())
    if not parsed or len(parsed) != len(set(parsed)):
        raise ValueError(f"{label} must contain unique values")
    if any(not 0.0 < item < 1.0 for item in parsed):
        raise ValueError(f"{label} values must be in (0, 1)")
    return tuple(sorted(parsed))


def parse_int_set(value: str, label: str) -> tuple[int, ...]:
    parsed = tuple(int(token.strip()) for token in value.split(",") if token.strip())
    if not parsed or len(parsed) != len(set(parsed)):
        raise ValueError(f"{label} must contain unique integers")
    return tuple(sorted(parsed))


def task(path: Path, root: Path) -> tuple[str, str, int]:
    relative = path.relative_to(root)
    if len(relative.parts) != 3 or relative.name != "scores.npz":
        raise ValueError(f"unexpected score path: {path}")
    suite, run = relative.parts[:2]
    if "_seed" not in run:
        raise ValueError(f"run directory has no seed suffix: {path.parent}")
    scenario, seed_text = run.rsplit("_seed", 1)
    return suite, scenario, int(seed_text)


def evaluate_acceptances(
    validation_risk: np.ndarray,
    test_labels: np.ndarray,
    test_unknown: np.ndarray,
    test_prediction: np.ndarray,
    test_risk: np.ndarray,
    acceptances: tuple[float, ...],
) -> dict[float, dict[str, object]]:
    result: dict[float, dict[str, object]] = {}
    for acceptance in acceptances:
        threshold = float(np.quantile(validation_risk, acceptance))
        report = evaluate_hybrid_open_set(
            test_labels, test_unknown, test_prediction, test_risk, threshold
        )
        result[acceptance] = {"threshold": threshold, "report": report}
    return result


def load_runs(
    root: Path,
    risk: str,
    acceptances: tuple[float, ...],
    seeds: tuple[int, ...],
    expected_scenarios: int,
    allow_extra_seeds: bool = False,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    observed: dict[tuple[str, str], set[int]] = defaultdict(set)
    validation_key = f"validation_{risk}"
    test_key = f"test_{risk}"
    for path in sorted(root.glob("*/*/scores.npz")):
        suite, scenario, seed = task(path, root)
        if seed not in seeds:
            if allow_extra_seeds:
                continue
            raise ValueError(f"unexpected seed {seed} in {path}")
        with np.load(path) as scores:
            required = {
                validation_key,
                test_key,
                "test_labels",
                "test_unknown",
                "test_prediction",
            }
            missing = sorted(required - set(scores.files))
            if missing:
                raise ValueError(f"missing score arrays in {path}: {missing}")
            evaluations = evaluate_acceptances(
                scores[validation_key],
                scores["test_labels"],
                scores["test_unknown"].astype(bool),
                scores["test_prediction"],
                scores[test_key],
                acceptances,
            )
        observed[(suite, scenario)].add(seed)
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "scores_path": str(path),
                "evaluations": {
                    str(acceptance): values
                    for acceptance, values in evaluations.items()
                },
            }
        )
    if not rows:
        raise ValueError(f"no scores found under {root}")
    if len(observed) != expected_scenarios:
        raise ValueError(
            f"scenario coverage mismatch: expected {expected_scenarios}, "
            f"found {len(observed)}"
        )
    expected_seed_set = set(seeds)
    mismatched = {
        f"{suite}/{scenario}": sorted(values)
        for (suite, scenario), values in observed.items()
        if values != expected_seed_set
    }
    if mismatched:
        raise ValueError(f"seed coverage mismatch: {mismatched}")
    return rows


def aggregate(
    rows: list[dict[str, object]], acceptances: tuple[float, ...]
) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[f"{row['suite']}/{row['scenario']}"] .append(row)
    result: dict[str, object] = {
        "inference_unit": "scenario",
        "scenario_count": len(grouped),
        "seed_repeats_are_averaged_within_scenario": True,
        "selection_warning": (
            "descriptive sensitivity only; do not select an operating point from "
            "confirmation or formal test metrics"
        ),
        "acceptances": {},
    }
    for acceptance in acceptances:
        key = str(acceptance)
        scenario_rows = []
        for scenario, items in sorted(grouped.items()):
            reports = [item["evaluations"][key]["report"] for item in items]
            thresholds = [item["evaluations"][key]["threshold"] for item in items]
            scenario_rows.append(
                {
                    "scenario": scenario,
                    "seed_count": len(items),
                    "threshold_mean": float(np.mean(thresholds)),
                    "metrics": {
                        metric: float(np.mean([report[metric] for report in reports]))
                        for metric in REPORT_METRICS
                    },
                }
            )
        result["acceptances"][key] = {
            "target_known_acceptance": acceptance,
            "scenario_mean": {
                metric: float(
                    np.mean([row["metrics"][metric] for row in scenario_rows])
                )
                for metric in REPORT_METRICS
            },
            "by_scenario": scenario_rows,
        }
    return result


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# Known-acceptance threshold sensitivity",
        "",
        report["selection_warning"],
        "",
        "| Validation target | Test known acceptance | Unknown rejection | Unknown F1 | AUROC | AUPR | FPR95 | OSCR |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, item in sorted(
        report["acceptances"].items(), key=lambda pair: float(pair[0])
    ):
        metrics = item["scenario_mean"]
        lines.append(
            f"| {item['target_known_acceptance']:.3f} | "
            f"{metrics['known_acceptance_rate']:.6f} | "
            f"{metrics['unknown_rejection_rate']:.6f} | "
            f"{metrics['unknown_f1']:.6f} | "
            f"{metrics['unknown_auroc']:.6f} | "
            f"{metrics['unknown_aupr']:.6f} | "
            f"{metrics['unknown_fpr95']:.6f} | {metrics['oscr']:.6f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    acceptances = parse_float_set(args.acceptances, "acceptances")
    seeds = parse_int_set(args.seeds, "seeds")
    rows = load_runs(
        Path(args.root),
        args.risk,
        acceptances,
        seeds,
        args.expected_scenarios,
        args.allow_extra_seeds,
    )
    summary = aggregate(rows, acceptances)
    report = {
        "root": args.root,
        "risk": args.risk,
        "seeds": list(seeds),
        "run_count": len(rows),
        "coverage_validated": True,
        **summary,
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sensitivity.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "sensitivity.md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
