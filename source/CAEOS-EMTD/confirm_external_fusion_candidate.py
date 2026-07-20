from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from summarize_neural_comparison_strict_v2 import (
    holm_adjust,
    paired_effect_sizes,
    paired_wilcoxon,
    scenario_block_bootstrap_ci,
)


METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_macro_f1",
)
LOWER_IS_BETTER = {"unknown_fpr95"}
TASK_RE = re.compile(r"^(?P<scenario>.+)_seed(?P<seed>\d+)$")


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_confirmation(
    selection_path: Path,
    raw_path: Path,
    bootstrap_repetitions: int = 10_000,
    bootstrap_seed: int = 20260717,
) -> dict[str, object]:
    selection = read_object(selection_path)
    raw = read_object(raw_path)
    selected = selection.get("selected_candidate")
    if not isinstance(selected, dict):
        raise ValueError("selection manifest has no selected candidate")
    if selection.get("candidate_status") != "frozen_unconfirmed":
        raise ValueError("selection candidate is not frozen_unconfirmed")
    reserved = tuple(int(seed) for seed in selection.get("confirmation_seeds", []))
    if not reserved or set(reserved) & set(selection.get("development_seeds", [])):
        raise ValueError("selection seed roles are invalid")
    scope = raw.get("selection_scope")
    if not isinstance(scope, dict):
        raise ValueError("raw confirmation lacks explicit selection_scope")
    observed_seeds = tuple(sorted(int(seed) for seed in scope.get("seeds", [])))
    if observed_seeds != tuple(sorted(reserved)):
        raise ValueError(
            f"confirmation seed mismatch: expected={sorted(reserved)}, "
            f"observed={list(observed_seeds)}"
        )
    overall = raw.get("overall")
    if not isinstance(overall, dict) or overall.get("expert_name") != selected.get(
        "expert_name"
    ):
        raise ValueError("raw confirmation expert does not match frozen candidate")
    fusion = str(selected.get("fusion"))
    methods = overall.get("methods")
    if not isinstance(methods, dict) or fusion not in methods:
        raise ValueError("raw confirmation lacks frozen fusion")
    runs = raw.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("raw confirmation contains no runs")

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    observed_pairs: set[tuple[str, int]] = set()
    for run in runs:
        if not isinstance(run, dict):
            raise ValueError("raw confirmation run must be an object")
        match = TASK_RE.fullmatch(str(run.get("task")))
        if match is None:
            raise ValueError(f"invalid confirmation task: {run.get('task')!r}")
        scenario = match.group("scenario")
        seed = int(match.group("seed"))
        if seed not in reserved:
            raise ValueError(f"unreserved confirmation seed: {seed}")
        pair = (scenario, seed)
        if pair in observed_pairs:
            raise ValueError(f"duplicate confirmation task: {pair}")
        observed_pairs.add(pair)
        grouped[scenario].append(run)
    if len(grouped) != 14 or any(len(items) != len(reserved) for items in grouped.values()):
        raise ValueError(
            f"confirmation coverage must be 14 scenarios x {len(reserved)} seeds"
        )

    inference: dict[str, object] = {}
    raw_p_values: dict[str, float] = {}
    for metric in METRICS:
        direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
        blocks = []
        deltas = []
        for scenario, items in sorted(grouped.items()):
            gate_mean = float(
                np.mean([float(item["gate_report"][metric]) for item in items])
            )
            candidate_mean = float(
                np.mean(
                    [float(item["reports"][fusion][metric]) for item in items]
                )
            )
            delta = direction * (candidate_mean - gate_mean)
            deltas.append(delta)
            blocks.append(
                {
                    "scenario": scenario,
                    "seed_count": len(items),
                    "gate_mean": gate_mean,
                    "candidate_mean": candidate_mean,
                    "oriented_delta": delta,
                }
            )
        array = np.asarray(deltas, dtype=np.float64)
        wilcoxon = paired_wilcoxon(deltas)
        raw_p_values[metric] = float(wilcoxon["raw_p_value"])
        inference[metric] = {
            "direction": "lower_is_better" if direction < 0 else "higher_is_better",
            "oriented_mean_delta": float(array.mean()),
            "wins": int((array > 1e-12).sum()),
            "ties": int((np.abs(array) <= 1e-12).sum()),
            "losses": int((array < -1e-12).sum()),
            "bootstrap_95_ci": scenario_block_bootstrap_ci(
                deltas,
                bootstrap_repetitions,
                bootstrap_seed + len(inference),
            ),
            "effect_sizes": paired_effect_sizes(deltas),
            "wilcoxon": wilcoxon,
            "scenario_blocks": blocks,
        }
    adjusted = holm_adjust(raw_p_values)
    for metric, value in adjusted.items():
        inference[metric]["wilcoxon"]["holm_adjusted_p_value"] = value

    safety = {
        "auroc_improves": inference["unknown_auroc"]["oriented_mean_delta"] > 0.0,
        "aupr_nonregression": inference["unknown_aupr"]["oriented_mean_delta"] >= -0.01,
        "fpr95_nonregression": inference["unknown_fpr95"]["oriented_mean_delta"] >= -0.01,
        "oscr_nonregression": inference["oscr"]["oriented_mean_delta"] >= -0.01,
    }
    safety["passes"] = all(safety.values())
    primary = inference["unknown_auroc"]
    primary_ci = primary["bootstrap_95_ci"]
    primary_holm = primary["wilcoxon"]["holm_adjusted_p_value"]
    decision = {
        "mean_safety_gate": safety,
        "primary_bootstrap_ci_excludes_zero": primary_ci["lower"] > 0.0,
        "primary_holm_p_below_0_05": primary_holm < 0.05,
    }
    decision["confirmation_passes"] = all(
        [
            safety["passes"],
            decision["primary_bootstrap_ci_excludes_zero"],
            decision["primary_holm_p_below_0_05"],
        ]
    )
    return {
        "schema_version": "external_risk_fusion_confirmation_v1",
        "candidate": {
            "expert_name": selected["expert_name"],
            "expert_model": selected["expert_model"],
            "fusion": fusion,
            "base_risk": selected["base_risk"],
        },
        "development_seeds": selection["development_seeds"],
        "confirmation_seeds": list(observed_seeds),
        "seed_overlap": [],
        "scenario_count": len(grouped),
        "run_count": len(runs),
        "inference_unit": "scenario_after_averaging_confirmation_seeds",
        "metrics": inference,
        "decision": decision,
        "inputs": {
            "selection_manifest": {
                "path": str(selection_path),
                "sha256": sha256(selection_path),
            },
            "raw_confirmation": {"path": str(raw_path), "sha256": sha256(raw_path)},
        },
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Confirm a frozen external-risk fusion")
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--raw-confirmation", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = build_confirmation(
        Path(args.selection_manifest),
        Path(args.raw_confirmation),
        args.bootstrap_repetitions,
        args.bootstrap_seed,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["decision"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
