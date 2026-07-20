from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scenario(task: str, expected_seed: int) -> str:
    scenario, marker, seed = str(task).rpartition("_seed")
    if marker != "_seed" or int(seed) != int(expected_seed) or not scenario:
        raise ValueError(f"unexpected development task identity: {task}")
    return scenario


def hardest_scenarios(
    runs: list[dict[str, Any]], *, per_suite: int = 2, seed: int = 7
) -> dict[str, list[str]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        suite = str(run["suite"])
        report = run.get("gate_report", {})
        if any(metric not in report for metric in METRICS):
            raise ValueError(f"development report is incomplete for {run.get('task')}")
        audit = run.get("audit", {})
        if audit.get("split_fingerprints_identical") is not True:
            raise ValueError("development split fingerprint mismatch")
        if audit.get("caeos_unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError("development CAEOS leakage guard failed")
        grouped.setdefault(suite, []).append(run)
    if len(grouped) != 7:
        raise ValueError("tail-aware pilot requires all seven strict-v4 suites")

    selected: dict[str, list[str]] = {}
    for suite, suite_runs in sorted(grouped.items()):
        if len(suite_runs) < int(per_suite):
            raise ValueError(f"suite {suite} has too few development runs")
        ranks = {id(run): [] for run in suite_runs}
        for metric in METRICS:
            ordered = sorted(
                suite_runs,
                key=lambda run: (run["gate_report"][metric], run["task"]),
                reverse=metric != "unknown_fpr95",
            )
            denominator = max(1, len(ordered) - 1)
            for index, run in enumerate(ordered):
                ranks[id(run)].append(index / denominator)
        hardest = sorted(
            suite_runs,
            key=lambda run: (
                sum(ranks[id(run)]) / len(METRICS),
                run["task"],
            ),
            reverse=True,
        )[: int(per_suite)]
        selected[suite] = sorted(_scenario(run["task"], seed) for run in hardest)
    return selected


def create_protocol(
    raw_fusion: dict[str, Any],
    *,
    raw_fusion_sha256: str,
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    runs = raw_fusion.get("runs", [])
    if len(runs) != 102:
        raise ValueError("tail-aware pilot requires the complete 102-scene screen")
    selected = hardest_scenarios(runs)
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_tail_aware_pilot_protocol_v1",
        "status": "frozen_before_pilot",
        "candidate": {
            "risk_selection": "nested_tail_aware_pairwise_pseudo_unknown_blend",
            "risk_endpoint": "pseudo_unknown_tail_aware_blend",
            "reference_endpoint": "cauchy_modality_support_union",
            "maximum_alpha": 0.5,
            "minimum_fold_gain": -0.05,
            "hard_pseudo_fraction": 0.5,
            "boundary_interpolation": 0.5,
            "boundary_max_per_task": 512,
            "tail_gammas": [0.0, 1.0, 2.0, 4.0],
            "monotone_powers": [1, 2, 4],
        },
        "pilot": {
            "development_seed": 7,
            "scenarios": selected,
            "expected_run_count": sum(len(values) for values in selected.values()),
            "selection_uses_opened_seed7_test_labels": True,
            "purpose": "cross-suite hard-scene development stress screen only",
            "gate": {
                "all_four_overall_oriented_means_positive": True,
                "minimum_suite_metric_gain": -0.05,
                "minimum_fully_nonregressing_suite_count": 5,
                "known_macro_f1_nonregression": True,
                "candidate_endpoint_must_be_exercised": True,
            },
        },
        "reserved_confirmation": {
            "seeds": [157, 163, 167],
            "scenario_scope": "all_102_strict_v4_scenarios",
            "expected_run_count": 306,
            "seed_disjoint_from_all_tail_aware_development": True,
            "must_freeze_candidate_before_first_confirmation_run": True,
        },
        "leakage_boundary": {
            "runtime_training_and_selection": "known_train_and_known_validation_only",
            "pilot_test_labels": "development_metrics_and_freeze_decision_only",
            "reserved_confirmation_labels": "final_metrics_only",
        },
        "source_raw_fusion_sha256": raw_fusion_sha256,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.raw_fusion.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    sources = {
        path: args.project_root / path
        for path in (
            "caeos/tail_aware_ranking.py",
            "train_hybrid_open_set.py",
            "run_nested_gate_matrix.py",
        )
    }
    protocol = create_protocol(
        payload,
        raw_fusion_sha256=hashlib.sha256(raw).hexdigest(),
        implementation_sha256={name: file_hash(path) for name, path in sources.items()},
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(protocol["pilot"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
