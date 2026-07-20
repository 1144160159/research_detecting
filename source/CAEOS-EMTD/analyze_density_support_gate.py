from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay a validation-only density-support gate on saved runs"
    )
    parser.add_argument("--root", action="append", required=True)
    parser.add_argument("--thresholds", default="0,0.005,0.01,0.02,0.03,0.04,0.05")
    parser.add_argument("--joint-fallback-minimum-gain", type=float, default=0.055)
    parser.add_argument("--minimum-known-classes", type=int, default=8)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def rank(aggregates: dict[str, dict[str, float]], name: str) -> tuple[float, float, float]:
    values = aggregates[name]
    return (
        float(values["robust_objective"]),
        float(values["minimum_auroc"]),
        float(values["mean_auroc"]),
    )


def stable_parent(
    aggregates: dict[str, dict[str, float]], joint_minimum_gain: float
) -> str:
    first_stage = max(
        ("support_union", "cauchy_evidence"),
        key=lambda name: rank(aggregates, name),
    )
    if first_stage == "support_union":
        return "anchor_support"
    gain = rank(aggregates, "cauchy_all")[0] - rank(aggregates, "cauchy_evidence")[0]
    return "cauchy_all" if gain > joint_minimum_gain + 1e-12 else "cauchy_evidence"


def choose_density_support(
    aggregates: dict[str, dict[str, float]],
    parent: str,
    minimum_gain: float,
) -> tuple[str, str | None, float]:
    if parent != "anchor_support":
        return parent, None, 0.0
    challenger = max(
        ("density_support_union", "triple_support_union"),
        key=lambda name: rank(aggregates, name),
    )
    gain = rank(aggregates, challenger)[0] - rank(aggregates, parent)[0]
    selected = challenger if gain > minimum_gain + 1e-12 else parent
    return selected, challenger, float(gain)


def paired_summary(values: list[float]) -> dict[str, object]:
    array = np.asarray(values, dtype=np.float64)
    nonzero = array[np.abs(array) > 1e-12]
    return {
        "mean_delta": float(array.mean()) if len(array) else 0.0,
        "wins": int((array > 1e-12).sum()),
        "ties": int((np.abs(array) <= 1e-12).sum()),
        "losses": int((array < -1e-12).sum()),
        "wilcoxon_p_value": (
            float(wilcoxon(nonzero).pvalue) if len(nonzero) else 1.0
        ),
    }


def load_runs(roots: list[str], joint_minimum_gain: float) -> list[dict[str, object]]:
    runs = []
    for root_value in roots:
        root = Path(root_value)
        for path in sorted(root.rglob("metrics.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            details = payload.get("risk_selection_details", {})
            aggregates = details.get("candidate_aggregates", {})
            reports = payload.get("reports", {})
            required = {
                "support_union",
                "anchor_support",
                "cauchy_evidence",
                "cauchy_all",
                "density_support_union",
                "triple_support_union",
            }
            if not required.issubset(aggregates) or not required.issubset(reports):
                continue
            parent = stable_parent(aggregates, joint_minimum_gain)
            runs.append(
                {
                    "path": str(path),
                    "root": str(root),
                    "parent": parent,
                    "known_classes": len(payload.get("known_class_names", [])),
                    "aggregates": aggregates,
                    "reports": reports,
                    "held_out_reports": details.get("held_out_reports", []),
                }
            )
    return runs


def evaluate(runs: list[dict[str, object]], threshold: float) -> dict[str, object]:
    auroc_delta = []
    oscr_delta = []
    triggers = []
    for run in runs:
        parent = str(run["parent"])
        reliable = int(run["known_classes"]) >= int(run["minimum_known_classes"])
        selected, challenger, gain = (
            choose_density_support(run["aggregates"], parent, threshold)
            if reliable
            else (parent, None, 0.0)
        )
        reports = run["reports"]
        auroc = float(reports[selected]["unknown_auroc"])
        parent_auroc = float(reports[parent]["unknown_auroc"])
        oscr = float(reports[selected]["oscr"])
        parent_oscr = float(reports[parent]["oscr"])
        auroc_delta.append(auroc - parent_auroc)
        oscr_delta.append(oscr - parent_oscr)
        if selected != parent:
            held_out_gains = [
                float(item["candidate_auroc"][selected])
                - float(item["candidate_auroc"][parent])
                for item in run["held_out_reports"]
                if selected in item.get("candidate_auroc", {})
                and parent in item.get("candidate_auroc", {})
            ]
            held_out_array = np.asarray(held_out_gains, dtype=np.float64)
            triggers.append(
                {
                    "path": run["path"],
                    "parent": parent,
                    "selected": selected,
                    "challenger": challenger,
                    "validation_gain": gain,
                    "known_classes": run["known_classes"],
                    "parent_aggregate": run["aggregates"][parent],
                    "candidate_aggregate": run["aggregates"][selected],
                    "held_out_gain_mean": float(held_out_array.mean()),
                    "held_out_gain_median": float(np.median(held_out_array)),
                    "held_out_gain_minimum": float(held_out_array.min()),
                    "held_out_gain_maximum": float(held_out_array.max()),
                    "held_out_positive_fraction": float(
                        (held_out_array > 1e-12).mean()
                    ),
                    "auroc_delta": auroc - parent_auroc,
                    "oscr_delta": oscr - parent_oscr,
                }
            )
    return {
        "threshold": threshold,
        "runs": len(runs),
        "triggers": len(triggers),
        "auroc": paired_summary(auroc_delta),
        "oscr": paired_summary(oscr_delta),
        "trigger_details": triggers,
    }


def main() -> None:
    args = parse_arguments()
    runs = load_runs(args.root, args.joint_fallback_minimum_gain)
    for run in runs:
        run["minimum_known_classes"] = args.minimum_known_classes
    thresholds = [float(value) for value in args.thresholds.split(",") if value.strip()]
    report = {
        "roots": args.root,
        "number_of_runs": len(runs),
        "joint_fallback_minimum_gain": args.joint_fallback_minimum_gain,
        "minimum_known_classes": args.minimum_known_classes,
        "evaluations": [evaluate(runs, threshold) for threshold in thresholds],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
