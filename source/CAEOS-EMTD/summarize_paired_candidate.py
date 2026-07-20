from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon


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
    parser = argparse.ArgumentParser(description="Pair a CAEOS candidate with a reference")
    parser.add_argument("--reference-root", required=True)
    parser.add_argument("--candidate-root", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def paired_p_value(delta: np.ndarray) -> float:
    nonzero = delta[np.abs(delta) > 1e-12]
    return float(wilcoxon(nonzero).pvalue) if len(nonzero) else 1.0


def aggregate(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {
        "number_of_runs": len(rows),
        "selected_paths": dict(Counter(str(row["candidate_selected"]) for row in rows)),
        "metrics": {},
    }
    for metric in METRICS:
        reference = np.asarray([row["reference_report"][metric] for row in rows])
        candidate = np.asarray([row["candidate_report"][metric] for row in rows])
        direction = -1.0 if metric == "unknown_fpr95" else 1.0
        raw_delta = candidate - reference
        oriented = direction * raw_delta
        result["metrics"][metric] = {
            "reference_mean": float(reference.mean()),
            "candidate_mean": float(candidate.mean()),
            "raw_mean_delta": float(raw_delta.mean()),
            "oriented_mean_improvement": float(oriented.mean()),
            "wins": int((oriented > 1e-12).sum()),
            "ties": int((np.abs(oriented) <= 1e-12).sum()),
            "losses": int((oriented < -1e-12).sum()),
            "wilcoxon_p_value": paired_p_value(oriented),
        }
    return result


def build_report(reference_root: Path, candidate_root: Path) -> dict[str, object]:
    rows = []
    for candidate_path in sorted(candidate_root.glob("*/*/metrics.json")):
        suite = candidate_path.parts[-3]
        run = candidate_path.parent.name
        reference_path = reference_root / suite / run / "metrics.json"
        if not reference_path.exists():
            raise FileNotFoundError(f"missing paired reference: {reference_path}")
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "suite": suite,
                "run": run,
                "candidate_selected": candidate["selected_risk"],
                "reference_selected": reference["selected_risk"],
                "candidate_report": candidate["selected_report"],
                "reference_report": reference["selected_report"],
            }
        )
    if not rows:
        raise ValueError(f"no candidate metrics found under {candidate_root}")
    groups = defaultdict(list)
    for row in rows:
        groups[str(row["suite"])].append(row)
    return {
        "reference_root": str(reference_root),
        "candidate_root": str(candidate_root),
        "global": aggregate(rows),
        "by_suite": {name: aggregate(values) for name, values in sorted(groups.items())},
        "runs": rows,
    }


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# Paired CAEOS candidate comparison",
        "",
        "| Scope | Runs | Reference AUROC | Candidate AUROC | Delta | W/T/L | Wilcoxon p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    summaries = [*report["by_suite"].items(), ("global", report["global"])]
    for name, summary in summaries:
        values = summary["metrics"]["unknown_auroc"]
        lines.append(
            "| %s | %d | %.6f | %.6f | %+.6f | %d/%d/%d | %.3g |"
            % (
                name,
                summary["number_of_runs"],
                values["reference_mean"],
                values["candidate_mean"],
                values["raw_mean_delta"],
                values["wins"],
                values["ties"],
                values["losses"],
                values["wilcoxon_p_value"],
            )
        )
    lines.extend(["", "## Secondary metrics", ""])
    lines.extend(
        [
            "| Metric | Reference | Candidate | Oriented improvement | W/T/L |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for metric in METRICS:
        values = report["global"]["metrics"][metric]
        lines.append(
            "| %s | %.6f | %.6f | %+.6f | %d/%d/%d |"
            % (
                metric,
                values["reference_mean"],
                values["candidate_mean"],
                values["oriented_mean_improvement"],
                values["wins"],
                values["ties"],
                values["losses"],
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    report = build_report(Path(args.reference_root), Path(args.candidate_root))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "comparison.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["global"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
