from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def analyze(
    confirmation: dict[str, Any],
    pilot_protocol: dict[str, Any],
    *,
    catastrophic_threshold: float = -0.1,
    top_k: int = 5,
) -> dict[str, Any]:
    inference = confirmation.get("scenario_blocked_inference", {})
    if int(inference.get("scenario_count", 0)) != 102:
        raise ValueError("external confirmation must contain 102 scenario blocks")
    metric_payloads = inference.get("metrics", {})
    if any(metric not in metric_payloads for metric in METRICS):
        raise ValueError("external confirmation is missing required metrics")

    scenario_gains: dict[str, dict[str, float]] = {}
    metric_diagnostics = {}
    for metric in METRICS:
        blocks = metric_payloads[metric].get("scenario_blocks", [])
        if len(blocks) != 102:
            raise ValueError(f"{metric} does not contain 102 scenario blocks")
        losses = []
        for block in blocks:
            scenario = str(block["scenario"])
            gain = float(block["oriented_improvement"])
            scenario_gains.setdefault(scenario, {})[metric] = gain
            if gain < 0.0:
                losses.append((scenario, gain))
        losses.sort(key=lambda item: item[1])
        negative_mass = sum(-gain for _, gain in losses)
        top = losses[:top_k]
        top_mass = sum(-gain for _, gain in top)
        metric_diagnostics[metric] = {
            "oriented_mean_improvement": float(
                metric_payloads[metric]["oriented_mean_improvement"]
            ),
            "loss_count": len(losses),
            "negative_mass": negative_mass,
            "top_loss_negative_mass_share": (
                top_mass / negative_mass if negative_mass > 0.0 else 0.0
            ),
            "catastrophic_loss_count": sum(
                gain <= catastrophic_threshold for _, gain in losses
            ),
            "worst_losses": [
                {"scenario": scenario, "oriented_gain": gain}
                for scenario, gain in top
            ],
        }

    if len(scenario_gains) != 102 or any(
        set(gains) != set(METRICS) for gains in scenario_gains.values()
    ):
        raise ValueError("metric scenario identities are inconsistent")
    joint = []
    for scenario, gains in scenario_gains.items():
        loss_count = sum(value < 0.0 for value in gains.values())
        catastrophic_count = sum(
            value <= catastrophic_threshold for value in gains.values()
        )
        joint.append(
            {
                "scenario": scenario,
                "loss_metric_count": loss_count,
                "catastrophic_metric_count": catastrophic_count,
                "minimum_oriented_gain": min(gains.values()),
                "oriented_gains": gains,
            }
        )
    joint.sort(
        key=lambda row: (
            -row["catastrophic_metric_count"],
            -row["loss_metric_count"],
            row["minimum_oriented_gain"],
            row["scenario"],
        )
    )

    pilot_scenarios = {
        f"{suite}/{scenario}"
        for suite, scenarios in pilot_protocol.get("pilot", {}).get("scenarios", {}).items()
        for scenario in scenarios
    }
    severe = {
        row["scenario"]
        for row in joint
        if row["loss_metric_count"] >= 3 or row["catastrophic_metric_count"] >= 1
    }
    covered = severe & pilot_scenarios
    return {
        "schema_version": "strict_v4_external_failure_concentration_v1",
        "candidate": confirmation.get("selected_algorithm"),
        "comparator": confirmation.get("selected_comparator"),
        "scenario_count": len(scenario_gains),
        "catastrophic_threshold": catastrophic_threshold,
        "top_k": top_k,
        "metric_diagnostics": metric_diagnostics,
        "joint_failure_scenarios": joint,
        "severe_scenario_count": len(severe),
        "severe_scenarios": sorted(severe),
        "lcb_pilot_scenario_count": len(pilot_scenarios),
        "lcb_severe_coverage_count": len(covered),
        "lcb_severe_coverage_ratio": len(covered) / len(severe) if severe else 1.0,
        "lcb_covered_severe_scenarios": sorted(covered),
        "lcb_uncovered_severe_scenarios": sorted(severe - covered),
        "decision_rule": (
            "run the frozen LCB pilot first; add no second tail candidate before its "
            "gate result. If uncovered severe scenarios dominate after LCB, prioritize "
            "representation or suite-safe routing rather than another global score blend"
        ),
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Pairwise-OpenDetect external failure concentration",
        "",
        f"Severe scenarios: `{result['severe_scenario_count']}`; LCB pilot covers "
        f"`{result['lcb_severe_coverage_count']}/{result['severe_scenario_count']}` "
        f"(`{result['lcb_severe_coverage_ratio']:.1%}`).",
        "",
        "| Metric | Mean gain | Losses | Catastrophic | Top-5 negative-mass share |",
        "|---|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        values = result["metric_diagnostics"][metric]
        lines.append(
            f"| {metric} | {values['oriented_mean_improvement']:+.6f} | "
            f"{values['loss_count']} | {values['catastrophic_loss_count']} | "
            f"{values['top_loss_negative_mass_share']:.1%} |"
        )
    lines.extend(["", "## Worst joint failures", ""])
    for row in result["joint_failure_scenarios"][:12]:
        lines.append(
            f"- `{row['scenario']}`: losses={row['loss_metric_count']}/4, "
            f"catastrophic={row['catastrophic_metric_count']}/4, "
            f"minimum gain={row['minimum_oriented_gain']:+.6f}."
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            result["decision_rule"] + ".",
            "",
            "Uncovered severe scenarios: "
            + ", ".join(f"`{name}`" for name in result["lcb_uncovered_severe_scenarios"])
            + ".",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirmation", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(
        json.loads(args.confirmation.read_text(encoding="utf-8")),
        json.loads(args.pilot_protocol.read_text(encoding="utf-8")),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
