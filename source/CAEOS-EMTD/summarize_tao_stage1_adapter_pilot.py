from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
RUNS = (
    ("edge_iiot", "fingerprinting_seed7_mlp"),
    ("nf_cse", "bot_seed7_mlp"),
    ("ustc_tfc2016", "geodo_seed7_mlp"),
)


def summarize(root: Path) -> dict[str, object]:
    rows = []
    for suite, run_name in RUNS:
        path = root / suite / run_name / "metrics.json"
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        evidence = payload["selection_evidence"]["postprocessors"]["tao_stage1_adapter"]
        if evidence["unknown_or_test_labels_used_for_fitting_or_selection"]:
            raise ValueError(f"leakage flag set for {path}")
        adapter = payload["reports"]["tao_stage1_adapter"]
        alternatives = {
            name: report
            for name, report in payload["reports"].items()
            if name != "tao_stage1_adapter"
        }
        strongest = max(
            alternatives,
            key=lambda name: alternatives[name]["unknown_auroc"] + alternatives[name]["oscr"],
        )
        row = {
            "suite": suite,
            "scenario": run_name.split("_seed", 1)[0],
            "seed": 7,
            "strongest_same_run_postprocessor": strongest,
        }
        for metric in METRICS:
            row[f"adapter_{metric}"] = float(adapter[metric])
            row[f"strongest_{metric}"] = float(alternatives[strongest][metric])
            direction = -1.0 if metric == "unknown_fpr95" else 1.0
            row[f"directed_delta_{metric}"] = direction * (
                float(adapter[metric]) - float(alternatives[strongest][metric])
            )
        rows.append(row)

    mean_auroc_delta = float(np.mean([row["directed_delta_unknown_auroc"] for row in rows]))
    mean_oscr_delta = float(np.mean([row["directed_delta_oscr"] for row in rows]))
    decision = "expand" if mean_auroc_delta >= 0.0 or mean_oscr_delta >= 0.0 else "retain_negative"
    return {
        "schema_version": "tao_stage1_adapter_pilot_summary_v1",
        "protocol_class": "paper_code_adapter_not_original_method_reproduction",
        "runs": rows,
        "aggregate": {
            "mean_directed_delta_unknown_auroc": mean_auroc_delta,
            "mean_directed_delta_oscr": mean_oscr_delta,
        },
        "decision": decision,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = summarize(Path(args.input_root))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result["aggregate"], sort_keys=True))
    print("decision=" + result["decision"])


if __name__ == "__main__":
    main()
