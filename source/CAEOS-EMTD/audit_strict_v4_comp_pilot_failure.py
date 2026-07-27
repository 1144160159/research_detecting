from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


CONFIRMATION_FILE_SHA256 = (
    "19b5c9031c6e82c98939568cb2c4210272f3a77ea5a484f1ff47495a994c4c34"
)
FEATURE_NAMES = (
    "validation_reference_zero_fraction",
    "validation_plateau_candidate_mean",
    "validation_plateau_candidate_std",
    "validation_plateau_candidate_q90",
    "validation_plateau_candidate_iqr",
)
ORIENTED_METRICS = (
    "unknown_aupr",
    "unknown_auroc",
    "unknown_fpr95",
    "oscr",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def average_rank_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(labels, dtype=bool).reshape(-1)
    values = np.asarray(scores, dtype=np.float64).reshape(-1)
    if y.shape != values.shape or not len(y):
        raise ValueError("AUC labels and scores must have matching shape")
    if not np.isfinite(values).all() or y.all() or (~y).all():
        raise ValueError("finite scores with both binary classes required")
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        stop = start + 1
        while (
            stop < len(values)
            and sorted_values[stop] == sorted_values[start]
        ):
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + 1 + stop)
        start = stop
    positives = int(y.sum())
    negatives = len(y) - positives
    rank_sum = float(ranks[y].sum())
    return float(
        (rank_sum - positives * (positives + 1) / 2)
        / (positives * negatives)
    )


def plateau_features(
    reference: np.ndarray, candidate: np.ndarray
) -> dict[str, float]:
    ref = np.asarray(reference, dtype=np.float64).reshape(-1)
    cand = np.asarray(candidate, dtype=np.float64).reshape(-1)
    if (
        ref.shape != cand.shape
        or not len(ref)
        or not np.isfinite(ref).all()
        or not np.isfinite(cand).all()
    ):
        raise ValueError("finite matching validation risks required")
    plateau = ref == 0.0
    if not plateau.any():
        return {
            "validation_reference_zero_fraction": 0.0,
            "validation_plateau_candidate_mean": 0.0,
            "validation_plateau_candidate_std": 0.0,
            "validation_plateau_candidate_q90": 0.0,
            "validation_plateau_candidate_iqr": 0.0,
        }
    values = cand[plateau]
    return {
        "validation_reference_zero_fraction": float(plateau.mean()),
        "validation_plateau_candidate_mean": float(values.mean()),
        "validation_plateau_candidate_std": float(values.std()),
        "validation_plateau_candidate_q90": float(
            np.quantile(values, 0.90)
        ),
        "validation_plateau_candidate_iqr": float(
            np.quantile(values, 0.75) - np.quantile(values, 0.25)
        ),
    }


def oriented_deltas(task: dict[str, Any]) -> dict[str, float]:
    candidate = task["caeos_comp"]
    reference = task["pairwise"]
    return {
        "unknown_aupr": float(
            candidate["unknown_aupr"] - reference["unknown_aupr"]
        ),
        "unknown_auroc": float(
            candidate["unknown_auroc"] - reference["unknown_auroc"]
        ),
        "unknown_fpr95": float(
            reference["unknown_fpr95"] - candidate["unknown_fpr95"]
        ),
        "oscr": float(candidate["oscr"] - reference["oscr"]),
    }


def threshold_values(values: list[float]) -> list[float]:
    unique = sorted(set(values))
    if len(unique) < 2:
        return []
    return [
        0.5 * (left + right)
        for left, right in zip(unique[:-1], unique[1:])
        if left < right
    ]


def screen_known_only_gates(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError("gate screen requires task rows")
    results: list[dict[str, Any]] = []
    for feature in FEATURE_NAMES:
        values = [float(row["validation_features"][feature]) for row in rows]
        for threshold in threshold_values(values):
            for direction in ("at_least", "at_most"):
                selected = [
                    (
                        value >= threshold
                        if direction == "at_least"
                        else value <= threshold
                    )
                    for value in values
                ]
                if not any(selected) or all(selected):
                    continue
                by_scenario: dict[str, set[bool]] = defaultdict(set)
                for row, admitted in zip(rows, selected):
                    by_scenario[str(row["scenario"])].add(admitted)
                scenario_consistent = all(
                    len(decisions) == 1
                    for decisions in by_scenario.values()
                )
                if not scenario_consistent:
                    continue
                aggregate = {
                    metric: float(
                        np.mean(
                            [
                                (
                                    row["oriented_delta"][metric]
                                    if admitted
                                    else 0.0
                                )
                                for row, admitted in zip(rows, selected)
                            ]
                        )
                    )
                    for metric in ORIENTED_METRICS
                }
                admitted_scenarios = sorted(
                    {
                        str(row["scenario"])
                        for row, admitted in zip(rows, selected)
                        if admitted
                    }
                )
                feasible = bool(
                    aggregate["unknown_fpr95"] >= 0.02
                    and aggregate["unknown_aupr"] >= -0.005
                    and aggregate["unknown_auroc"] >= -0.005
                    and aggregate["oscr"] >= -0.005
                )
                results.append(
                    {
                        "feature": feature,
                        "direction": direction,
                        "threshold": float(threshold),
                        "admitted_task_count": int(sum(selected)),
                        "admitted_scenarios": admitted_scenarios,
                        "scenario_consistent_on_three_seeds": True,
                        "oriented_mean_delta": aggregate,
                        "development_feasible": feasible,
                    }
                )
    return sorted(
        results,
        key=lambda item: (
            not item["development_feasible"],
            -item["oriented_mean_delta"]["unknown_fpr95"],
            -item["oriented_mean_delta"]["unknown_aupr"],
            item["feature"],
            item["direction"],
            item["threshold"],
        ),
    )


def task_diagnostic(
    task: dict[str, Any],
    pairwise_root: Path,
) -> tuple[dict[str, Any], dict[str, str]]:
    from caeos.continuous_outer_min_p import reconstruct_candidate_risks

    suite = str(task["suite"])
    scenario = str(task["scenario"])
    seed = int(task["seed"])
    directory = pairwise_root / suite / f"{scenario}_seed{seed}"
    score_path = directory / "scores.npz"
    evidence_path = directory / "evidence_package.npz"
    if not score_path.is_file() or not evidence_path.is_file():
        raise ValueError(f"paired evidence absent: {suite}/{scenario}/{seed}")
    with np.load(score_path, allow_pickle=False) as scores, np.load(
        evidence_path, allow_pickle=False
    ) as evidence:
        risks = reconstruct_candidate_risks(scores, evidence)
        validation_features = plateau_features(
            risks["validation_reference"], risks["validation_candidate"]
        )
        reference = np.asarray(risks["test_reference"], dtype=np.float64)
        candidate = np.asarray(risks["test_candidate"], dtype=np.float64)
        unknown = np.asarray(scores["test_unknown"], dtype=bool)
        plateau = reference == 0.0
        known_plateau = plateau & ~unknown
        unknown_plateau = plateau & unknown
        within_auc = None
        if known_plateau.any() and unknown_plateau.any():
            within_auc = average_rank_auc(
                unknown[plateau], candidate[plateau]
            )
        test_plateau = {
            "overall_fraction": float(plateau.mean()),
            "known_fraction": float(known_plateau.sum() / max((~unknown).sum(), 1)),
            "unknown_fraction": float(
                unknown_plateau.sum() / max(unknown.sum(), 1)
            ),
            "candidate_within_plateau_unknown_auroc": within_auc,
        }
    row = {
        "suite": suite,
        "scenario": scenario,
        "seed": seed,
        "group": task["group"],
        "validation_features": validation_features,
        "test_plateau_diagnostic": test_plateau,
        "oriented_delta": oriented_deltas(task),
    }
    return row, {
        f"{suite}/{scenario}/seed{seed}/scores.npz": file_hash(score_path),
        f"{suite}/{scenario}/seed{seed}/evidence_package.npz": file_hash(
            evidence_path
        ),
    }


def build_audit(
    confirmation: dict[str, Any],
    rows: list[dict[str, Any]],
    artifact_sha256: dict[str, str],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    if (
        confirmation.get("schema_version")
        != "strict_v4_comp_confirmation_v1"
        or confirmation.get("state")
        != "fresh_seed_confirmation_complete"
        or confirmation.get("manifest_sha256")
        != canonical_hash(confirmation)
        or confirmation.get("validation", {}).get("passes") is not True
        or confirmation.get("validation", {}).get("paired_task_count") != 18
        or confirmation.get("decision", {}).get("passes") is not False
        or len(rows) != 18
    ):
        raise ValueError("canonical negative 18-task confirmation required")
    identities = {
        (row["suite"], row["scenario"], int(row["seed"])) for row in rows
    }
    if len(identities) != 18:
        raise ValueError("unique 18-task diagnostics required")
    screens = screen_known_only_gates(rows)
    feasible = [item for item in screens if item["development_feasible"]]
    scenario_rows: list[dict[str, Any]] = []
    for scenario in sorted({str(row["scenario"]) for row in rows}):
        selected = [row for row in rows if row["scenario"] == scenario]
        scenario_rows.append(
            {
                "scenario": scenario,
                "group": selected[0]["group"],
                "seed_count": len(selected),
                "oriented_mean_delta": {
                    metric: float(
                        np.mean(
                            [row["oriented_delta"][metric] for row in selected]
                        )
                    )
                    for metric in ORIENTED_METRICS
                },
                "validation_feature_mean": {
                    feature: float(
                        np.mean(
                            [
                                row["validation_features"][feature]
                                for row in selected
                            ]
                        )
                    )
                    for feature in FEATURE_NAMES
                },
            }
        )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_comp_confirmation_failure_audit_v1",
        "state": "posthoc_development_diagnosis_complete",
        "source_decision": {
            "passes": False,
            "failed_checks": sorted(
                key
                for key, value in confirmation["decision"]["checks"].items()
                if not value
            ),
            "pairwise_remains_incumbent": True,
        },
        "diagnostics": {
            "task_count": 18,
            "scenario_count": 6,
            "tasks": rows,
            "scenarios": scenario_rows,
            "known_only_gate_screen_count": len(screens),
            "development_feasible_gate_count": len(feasible),
            "best_development_gate": feasible[0] if feasible else None,
            "top_gate_screens": screens[:20],
        },
        "input_file_sha256": input_file_sha256,
        "artifact_sha256": dict(sorted(artifact_sha256.items())),
        "implementation_sha256": implementation_sha256,
        "claim_boundary": {
            "test_unknown_labels_used_for_failure_diagnosis": True,
            "test_unknown_labels_used_for_source_decision": False,
            "source_negative_activation_is_immutable": True,
            "gate_screen_is_development_only": True,
            "gate_screen_cannot_reactivate_cross_suite_execution": True,
            "new_candidate_requires_new_scenarios_and_new_seeds": True,
            "pairwise_remains_incumbent": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--confirmation",
        type=Path,
        default=Path(
            "results/strict_v4_comp_confirmation_v1/confirmation.json"
        ),
    )
    parser.add_argument(
        "--pairwise-root",
        type=Path,
        default=Path(
            "runs/strict_v4_comp_confirmation_v1/pairwise"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_comp_confirmation_failure_audit_v1/"
            "audit.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    confirmation_path = resolve(args.confirmation)
    pairwise_root = resolve(args.pairwise_root)
    output = resolve(args.output)
    if file_hash(confirmation_path) != CONFIRMATION_FILE_SHA256:
        raise ValueError("exact frozen CAEOS-COMP confirmation required")
    confirmation = load(confirmation_path)
    rows: list[dict[str, Any]] = []
    artifact_sha256: dict[str, str] = {}
    for task in confirmation["tasks"]:
        row, hashes = task_diagnostic(task, pairwise_root)
        rows.append(row)
        artifact_sha256.update(hashes)
    script_path = Path(__file__).resolve()
    audit = build_audit(
        confirmation,
        rows,
        artifact_sha256,
        {
            str(confirmation_path.relative_to(root)): file_hash(
                confirmation_path
            )
        },
        {
            str(script_path.relative_to(root)): file_hash(script_path)
        },
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and load(output) != audit:
        raise ValueError("existing failure audit is immutable")
    if not output.exists():
        temporary = output.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(audit, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
    print(
        json.dumps(
            {
                "failed_checks": audit["source_decision"]["failed_checks"],
                "development_feasible_gate_count": audit["diagnostics"][
                    "development_feasible_gate_count"
                ],
                "best_development_gate": audit["diagnostics"][
                    "best_development_gate"
                ],
                "manifest_sha256": audit["manifest_sha256"],
                "file_sha256": file_hash(output),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
