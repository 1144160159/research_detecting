from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a CADE experiment matrix")
    parser.add_argument("--input-root", required=True)
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


def aggregate(runs: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {"number_of_runs": len(runs)}
    for protocol in ("calibrated", "official_mad35"):
        result[protocol] = {
            metric: describe([run[protocol][metric] for run in runs])
            for metric in METRICS
        }
    result["training_seconds"] = describe(
        [float(run["training_seconds"]) for run in runs]
    )
    result["validation_threshold"] = describe(
        [float(run["validation_threshold"]) for run in runs]
    )
    return result


def load_runs(root: Path) -> list[dict[str, object]]:
    runs = []
    for path in sorted(root.glob("*/*/metrics.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        run_name = path.parent.name
        scenario, suffix = run_name.rsplit("_seed", 1)
        seed = int(suffix.split("_", 1)[0])
        runs.append(
            {
                "suite": path.parent.parent.name,
                "scenario": scenario,
                "seed": seed,
                "calibrated": {
                    metric: float(payload["reports"]["cade"][metric])
                    for metric in METRICS
                },
                "official_mad35": {
                    metric: float(
                        payload["auxiliary_reports"]["cade_official_mad35"][metric]
                    )
                    for metric in METRICS
                },
                "validation_threshold": float(
                    payload["validation_thresholds"]["cade"]
                ),
                "training_seconds": float(payload["training_seconds"]),
                "trainable_parameters": int(payload["trainable_parameters"]),
            }
        )
    if not runs:
        raise ValueError(f"no CADE metrics found under {root}")
    return runs


def build_summary(runs: list[dict[str, object]]) -> dict[str, object]:
    by_suite = defaultdict(list)
    by_scenario = defaultdict(list)
    for run in runs:
        by_suite[run["suite"]].append(run)
        by_scenario[f"{run['suite']}/{run['scenario']}"] .append(run)
    return {
        "global": aggregate(runs),
        "by_suite": {
            name: aggregate(values) for name, values in sorted(by_suite.items())
        },
        "by_scenario": {
            name: aggregate(values) for name, values in sorted(by_scenario.items())
        },
        "trainable_parameters": sorted(
            {int(run["trainable_parameters"]) for run in runs}
        ),
        "runs": runs,
    }


def markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CADE same-split matrix summary",
        "",
        "The calibrated protocol uses the 95th percentile of known validation risk. "
        "The official protocol uses the fixed CADE MAD threshold 3.5.",
        "",
        "| Scope | Runs | Protocol | Known Macro-F1 | AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    scopes = [("global", summary["global"]), *summary["by_suite"].items()]
    for name, values in scopes:
        for protocol in ("calibrated", "official_mad35"):
            metrics = values[protocol]
            lines.append(
                "| %s | %d | %s | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |"
                % (
                    name,
                    values["number_of_runs"],
                    protocol,
                    *(metrics[metric]["mean"] for metric in METRICS),
                )
            )
    lines.extend(
        [
            "",
            "## Scenario AUROC",
            "",
            "| Scenario | Runs | AUROC | Known Macro-F1 | Unknown reject (calibrated) | Unknown reject (MAD=3.5) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name, values in summary["by_scenario"].items():
        calibrated = values["calibrated"]
        official = values["official_mad35"]
        lines.append(
            "| %s | %d | %.6f | %.6f | %.6f | %.6f |"
            % (
                name,
                values["number_of_runs"],
                calibrated["unknown_auroc"]["mean"],
                calibrated["known_macro_f1"]["mean"],
                calibrated["unknown_rejection_rate"]["mean"],
                official["unknown_rejection_rate"]["mean"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_arguments()
    runs = load_runs(Path(args.input_root))
    summary = build_summary(runs)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cade_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "cade_summary.md").write_text(
        markdown(summary), encoding="utf-8"
    )
    print(json.dumps({"global": summary["global"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
