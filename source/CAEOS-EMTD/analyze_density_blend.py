from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate fixed density-support blend weights on saved gate runs"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument(
        "--seeds",
        default="",
        help="Optional comma-separated development seeds; empty scans every seed",
    )
    parser.add_argument(
        "--weights", default="0,0.05,0.1,0.2,0.25,0.3,0.4,0.5,0.75,1"
    )
    parser.add_argument(
        "--selection-metric",
        choices=("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"),
        default="unknown_auroc",
    )
    parser.add_argument("--maximum-fpr95-regression", type=float, default=0.01)
    parser.add_argument("--secondary-tolerance", type=float, default=0.0)
    parser.add_argument(
        "--minimum-development-triggers-per-suite", type=int, default=3
    )
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def task_seed(path: Path) -> int:
    try:
        return int(path.parent.name.rsplit("_seed", 1)[1])
    except (IndexError, ValueError) as error:
        raise ValueError(f"cannot parse scenario seed from {path}") from error


def select_safe_evaluation(
    evaluations: list[dict[str, object]],
    selection_metric: str,
    maximum_fpr95_regression: float,
    secondary_tolerance: float,
) -> tuple[dict[str, object], list[float]]:
    if maximum_fpr95_regression < 0.0 or secondary_tolerance < 0.0:
        raise ValueError("selection safety tolerances must be non-negative")
    parents = [item for item in evaluations if abs(float(item["weight"])) <= 1e-12]
    if len(parents) != 1:
        raise ValueError("weight grid must contain exactly one zero-weight parent")
    parent = parents[0]
    eligible = [
        item
        for item in evaluations
        if float(item["mean_unknown_aupr"])
        >= float(parent["mean_unknown_aupr"]) - secondary_tolerance
        and float(item["mean_oscr"])
        >= float(parent["mean_oscr"]) - secondary_tolerance
        and float(item["mean_unknown_fpr95"])
        <= float(parent["mean_unknown_fpr95"]) + maximum_fpr95_regression
    ]
    if not eligible:
        raise ValueError("no blend weight satisfies the frozen safety constraints")
    metric_key = f"mean_{selection_metric}"
    direction = -1.0 if selection_metric == "unknown_fpr95" else 1.0
    selected = max(
        eligible,
        key=lambda item: (direction * float(item[metric_key]), -float(item["weight"])),
    )
    return selected, [float(item["weight"]) for item in eligible]


def load_trigger(path: Path) -> dict[str, object] | None:
    metrics = json.loads(path.read_text(encoding="utf-8"))
    details = metrics.get("risk_selection_details", {})
    parent = details.get("parent_selected_risk")
    selected = metrics.get("selected_risk")
    if parent != "anchor_support" or selected == parent:
        return None
    allowed_endpoints = {"density_support_union", "triple_support_union"}
    endpoint = details.get("density_support_endpoint")
    is_frozen_blend = selected == "density_reliability_blend"
    if endpoint not in allowed_endpoints or (
        not is_frozen_blend and selected != endpoint
    ):
        raise ValueError(
            f"{path} is not a raw density-support endpoint: "
            f"selected={selected!r}, endpoint={endpoint!r}"
        )
    scores_path = path.parent / "scores.npz"
    evidence_path = path.parent / "evidence_package.npz"
    scores = np.load(scores_path, allow_pickle=False)
    evidence = np.load(evidence_path, allow_pickle=False)
    selected_name = str(evidence["selected_risk_name"].item())
    if selected_name != selected:
        raise ValueError(f"selected-risk archive mismatch in {path}")
    validation_parent = scores["validation_anchor_support"]
    test_parent = scores["test_anchor_support"]
    if is_frozen_blend:
        frozen_weight = float(details.get("density_gate_blend_weight", 0.0))
        if not 0.0 < frozen_weight <= 1.0:
            raise ValueError(f"invalid frozen blend weight in {path}: {frozen_weight}")
        validation_selected = evidence["validation_selected_risk"]
        test_selected = evidence["test_selected_risk"]
        validation_candidate = (
            validation_selected - (1.0 - frozen_weight) * validation_parent
        ) / frozen_weight
        test_candidate = (
            test_selected - (1.0 - frozen_weight) * test_parent
        ) / frozen_weight
        if not np.allclose(
            validation_selected,
            (1.0 - frozen_weight) * validation_parent
            + frozen_weight * validation_candidate,
            rtol=1e-10,
            atol=1e-12,
        ) or not np.allclose(
            test_selected,
            (1.0 - frozen_weight) * test_parent
            + frozen_weight * test_candidate,
            rtol=1e-10,
            atol=1e-12,
        ):
            raise ValueError(f"frozen blend reconstruction failed in {path}")
        candidate_source = "reconstructed_from_frozen_blend_and_parent"
    else:
        frozen_weight = None
        validation_candidate = evidence["validation_selected_risk"]
        test_candidate = evidence["test_selected_risk"]
        candidate_source = "saved_raw_density_endpoint"
    return {
        "path": str(path),
        "scenario": path.parent.name,
        "parent": parent,
        "candidate": endpoint,
        "candidate_source": candidate_source,
        "frozen_blend_weight": frozen_weight,
        "artifact_sha256": {
            "metrics.json": sha256(path),
            "scores.npz": sha256(scores_path),
            "evidence_package.npz": sha256(evidence_path),
        },
        "validation_parent": validation_parent,
        "test_parent": test_parent,
        "validation_candidate": validation_candidate,
        "test_candidate": test_candidate,
        "test_labels": scores["test_labels"],
        "test_unknown": scores["test_unknown"],
        "test_prediction": scores["test_prediction"],
    }


def main() -> None:
    args = parse_arguments()
    root = Path(args.root)
    metrics_paths = sorted(root.rglob("metrics.json"))
    requested_seeds = {
        int(value) for value in args.seeds.split(",") if value.strip()
    }
    if requested_seeds:
        metrics_paths = [
            path for path in metrics_paths if task_seed(path) in requested_seeds
        ]
    triggers = []
    for path in metrics_paths:
        item = load_trigger(path)
        if item is not None:
            triggers.append(item)
    weights = [float(value) for value in args.weights.split(",") if value.strip()]
    if not triggers:
        raise ValueError(f"no raw density-support triggers found under {root}")
    if not weights or any(weight < 0.0 or weight > 1.0 for weight in weights):
        raise ValueError("weights must contain at least one value in [0, 1]")
    if len(set(weights)) != len(weights):
        raise ValueError("weights must be unique")
    for trigger in triggers:
        trigger["task_id"] = Path(trigger["path"]).parent.relative_to(root).as_posix()
    task_ids = [str(trigger["task_id"]) for trigger in triggers]
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("development task IDs must be unique")
    if args.minimum_development_triggers_per_suite <= 0:
        raise ValueError("minimum development triggers per suite must be positive")
    suite_trigger_counts = Counter(task_id.split("/", 1)[0] for task_id in task_ids)
    supported_suites = sorted(
        suite
        for suite, count in suite_trigger_counts.items()
        if count >= args.minimum_development_triggers_per_suite
    )
    if not supported_suites:
        raise ValueError("no suite has enough development triggers for deployment")
    evaluations = []
    for weight in weights:
        reports = []
        for trigger in triggers:
            validation_risk = (
                (1.0 - weight) * trigger["validation_parent"]
                + weight * trigger["validation_candidate"]
            )
            test_risk = (
                (1.0 - weight) * trigger["test_parent"]
                + weight * trigger["test_candidate"]
            )
            threshold = float(np.quantile(validation_risk, args.known_acceptance))
            report = evaluate_hybrid_open_set(
                trigger["test_labels"],
                trigger["test_unknown"],
                trigger["test_prediction"],
                test_risk,
                threshold,
            )
            reports.append(
                {
                    "path": trigger["path"],
                    "scenario": trigger["scenario"],
                    "parent": trigger["parent"],
                    "candidate": trigger["candidate"],
                    **report,
                }
            )
        evaluations.append(
            {
                "weight": weight,
                "trigger_count": len(reports),
                "mean_unknown_auroc": float(
                    np.mean([report["unknown_auroc"] for report in reports])
                ),
                "mean_unknown_aupr": float(
                    np.mean([report["unknown_aupr"] for report in reports])
                ),
                "mean_oscr": float(np.mean([report["oscr"] for report in reports])),
                "mean_unknown_fpr95": float(
                    np.mean([report["unknown_fpr95"] for report in reports])
                ),
                "reports": reports,
            }
        )
    selected_evaluation, eligible_weights = select_safe_evaluation(
        evaluations,
        args.selection_metric,
        args.maximum_fpr95_regression,
        args.secondary_tolerance,
    )
    selection_manifest = {
        "purpose": "development_only_hyperparameter_selection",
        "unknown_test_labels_used": True,
        "eligible_for_confirmation_or_final_metrics": False,
        "primary_selection_metric": args.selection_metric,
        "selection_policy": "maximize_primary_subject_to_secondary_safety",
        "safety_constraints": {
            "mean_unknown_aupr_minimum": "zero_weight_parent_minus_tolerance",
            "mean_oscr_minimum": "zero_weight_parent_minus_tolerance",
            "maximum_absolute_fpr95_regression": args.maximum_fpr95_regression,
            "secondary_tolerance": args.secondary_tolerance,
        },
        "candidate_weights": weights,
        "eligible_weights": eligible_weights,
        "applicability_policy": "suite_requires_development_trigger_support",
        "minimum_development_triggers_per_suite": (
            args.minimum_development_triggers_per_suite
        ),
        "development_trigger_count_by_suite": dict(sorted(suite_trigger_counts.items())),
        "supported_suites": supported_suites,
        "tie_break": "smallest_weight",
        "selected_weight": selected_evaluation["weight"],
        "development_tasks": task_ids,
        "development_artifacts": {
            str(trigger["task_id"]): trigger["artifact_sha256"]
            for trigger in triggers
        },
        "confirmation_requirement": (
            "confirmation scenario-seed task IDs and artifact hashes must be disjoint "
            "from development tasks"
        ),
    }
    result = {
        "root": str(root),
        "development_seeds": sorted(requested_seeds),
        "known_acceptance": args.known_acceptance,
        "trigger_count": len(triggers),
        "selection_manifest": selection_manifest,
        "evaluations": evaluations,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "trigger_count": len(triggers),
                "weights": [
                    {key: value for key, value in item.items() if key != "reports"}
                    for item in evaluations
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
