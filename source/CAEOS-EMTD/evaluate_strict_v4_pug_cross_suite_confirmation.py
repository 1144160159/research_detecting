from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.metrics import fpr_at_95_tpr
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from inspect_strict_v4_pug_run import inspect_run


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
EXPECTED_POLICY_NAME = "strict_v4_pug_confirmation_v1"
EXPECTED_RISK_SELECTION = "nested_pug_continuous_outer_min_p"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def report_values(report: dict[str, Any]) -> dict[str, float]:
    values = {}
    for metric in METRICS:
        value = report.get(metric)
        if not isinstance(value, (int, float)) or not np.isfinite(value):
            raise ValueError(f"finite metric required: {metric}")
        values[metric] = float(value)
    return values


def validate_protocol(
    protocol: dict[str, Any], *, check_implementation: bool = True
) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_pug_cross_suite_execution_protocol_v1"
        or protocol.get("state")
        != "frozen_after_positive_pilot_before_cross_suite_execution"
        or protocol.get("execution_admitted") is not True
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical admitted PUG cross-suite protocol required")
    universe = protocol.get("confirmation_universe", {})
    tasks = universe.get("tasks")
    controls = protocol.get("execution_controls", {})
    if (
        universe.get("suite_count") != 7
        or universe.get("scenario_count") != 102
        or universe.get("paired_task_count") != 306
        or universe.get("expected_pairwise_pug_runs") != 306
        or universe.get("expected_fresh_opendetect_runs") != 306
        or universe.get("fresh_seeds") != [269, 271, 277]
        or not isinstance(tasks, list)
        or len(tasks) != 306
        or len(
            {
                (task["suite"], task["scenario"], task["seed"])
                for task in tasks
            }
        )
        != 306
        or controls.get("candidate_policy_name") != EXPECTED_POLICY_NAME
        or controls.get("candidate_risk_selection")
        != EXPECTED_RISK_SELECTION
        or protocol.get("output_contract", {}).get(
            "partial_metrics_must_not_be_aggregated"
        )
        is not True
    ):
        raise ValueError("PUG cross-suite protocol universe drifted")
    if check_implementation:
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items():
            path = Path(relative)
            if not path.is_file() or file_hash(path) != expected:
                raise ValueError(f"frozen implementation drifted: {relative}")


def evaluate_cross_task(
    task: dict[str, Any],
    candidate_root: Path,
    opendetect_root: Path,
    expected_policy_name: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    suite = str(task["suite"])
    scenario = str(task["scenario"])
    seed = int(task["seed"])
    candidate_dir = candidate_root / suite / f"{scenario}_seed{seed}"
    opendetect_dir = (
        opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
    )
    candidate_files = {
        name: candidate_dir / name
        for name in (
            "metrics.json",
            "scores.npz",
            "evidence_package.npz",
            "provenance.json",
        )
    }
    opendetect_files = {
        name: opendetect_dir / name
        for name in ("metrics.json", "scores.npz", "provenance.json")
    }
    missing = [
        str(path)
        for path in [*candidate_files.values(), *opendetect_files.values()]
        if not path.is_file()
    ]
    if missing:
        raise ValueError(f"missing confirmation artifacts: {missing}")

    inspection = inspect_run(candidate_dir)
    candidate_metrics = load(candidate_files["metrics.json"])
    opendetect_metrics = load(opendetect_files["metrics.json"])
    if (
        candidate_metrics.get("risk_policy") != expected_policy_name
        or candidate_metrics.get("risk_selection_details", {}).get(
            "unknown_or_test_labels_used_for_selection"
        )
        is not False
        or inspection.get("unknown_or_test_labels_used_for_selection")
        is not False
        or opendetect_metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError(f"leakage guard failed: {suite}/{scenario}/seed{seed}")

    candidate_fingerprint = candidate_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    opendetect_fingerprint = opendetect_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    if candidate_fingerprint != opendetect_fingerprint:
        raise ValueError(
            f"split fingerprint mismatch: {suite}/{scenario}/seed{seed}"
        )

    base = str(inspection["pairwise_base_selected_risk"])
    selected = str(inspection["selected_risk"])
    with np.load(
        candidate_files["scores.npz"], allow_pickle=False
    ) as scores, np.load(
        opendetect_files["scores.npz"], allow_pickle=False
    ) as opendetect_scores:
        unknown = np.asarray(scores["test_unknown"], dtype=bool)
        if (
            not np.array_equal(
                unknown, opendetect_scores["test_unknown"].astype(bool)
            )
            or not np.array_equal(
                scores["test_labels"], opendetect_scores["test_labels"]
            )
        ):
            raise ValueError(
                f"paired labels differ: {suite}/{scenario}/seed{seed}"
            )
        reports = {}
        for name in dict.fromkeys((base, selected)):
            report = evaluate_hybrid_open_set(
                scores["test_labels"],
                unknown,
                scores["test_prediction"],
                scores[f"test_{name}"],
                float(candidate_metrics["validation_thresholds"][name]),
            )
            expected = candidate_metrics["reports"][name]
            if any(
                not close(report[metric], expected[metric])
                for metric in METRICS
            ):
                raise ValueError(f"report recomputation mismatch: {name}")
            reports[name] = report_values(report)

        opendetect_report = opendetect_metrics.get("reports", {}).get(
            "opendetect"
        )
        if not isinstance(opendetect_report, dict):
            raise ValueError("OpenDetect report is absent")
        recomputed_fpr95 = fpr_at_95_tpr(
            unknown.astype(np.int64),
            opendetect_scores["test_opendetect"],
        )
        if not close(
            recomputed_fpr95, opendetect_report["unknown_fpr95"]
        ):
            raise ValueError("OpenDetect FPR95 recomputation mismatch")

    row = {
        "suite": suite,
        "scenario": scenario,
        "group": "cross_suite",
        "seed": seed,
        "pairwise_base_selected_risk": base,
        "pug_selected_risk": selected,
        "pug_gate_passes": bool(inspection["pug_gate_passes"]),
        "pug_selected": bool(inspection["pug_selected"]),
        "pairwise": reports[base],
        "caeos_pug": reports[selected],
        "opendetect": report_values(opendetect_report),
        "split_fingerprint": candidate_fingerprint,
        "unknown_or_test_labels_used_for_selection": False,
    }
    hashes = {
        f"{suite}/{scenario}/seed{seed}/candidate/{name}": file_hash(path)
        for name, path in candidate_files.items()
    }
    hashes.update(
        {
            f"{suite}/{scenario}/seed{seed}/opendetect/{name}": file_hash(
                path
            )
            for name, path in opendetect_files.items()
        }
    )
    return row, hashes


def select_task(
    protocol: dict[str, Any], suite: str, scenario: str, seed: int
) -> dict[str, Any]:
    matches = [
        task
        for task in protocol["confirmation_universe"]["tasks"]
        if task["suite"] == suite
        and task["scenario"] == scenario
        and int(task["seed"]) == seed
    ]
    if len(matches) != 1:
        raise ValueError("exactly one frozen task identity required")
    return matches[0]


def create_task_record(
    *,
    protocol: dict[str, Any],
    task: dict[str, Any],
    row: dict[str, Any],
    artifact_sha256: dict[str, str],
    protocol_file_sha256: str,
    evaluator_sha256: str,
) -> dict[str, Any]:
    identity = (task["suite"], task["scenario"], int(task["seed"]))
    observed = (row["suite"], row["scenario"], int(row["seed"]))
    if identity != observed:
        raise ValueError("evaluated task identity drifted")
    if (
        row.get("group") != "cross_suite"
        or row.get("unknown_or_test_labels_used_for_selection") is not False
    ):
        raise ValueError("isolated cross-suite evaluation required")
    if not isinstance(artifact_sha256, dict) or len(artifact_sha256) != 7:
        raise ValueError("exactly seven paired artifact hashes required")
    record: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pug_cross_suite_task_evaluation_v1"
        ),
        "state": "single_paired_task_evaluation_complete",
        "task": {
            "suite": identity[0],
            "scenario": identity[1],
            "seed": identity[2],
        },
        "evaluation": row,
        "input_evidence": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "protocol_file_sha256": protocol_file_sha256,
            "artifact_sha256": dict(sorted(artifact_sha256.items())),
        },
        "implementation_sha256": {
            "evaluate_strict_v4_pug_cross_suite_confirmation.py": (
                evaluator_sha256
            )
        },
        "claim_boundary": {
            "single_task_record_is_not_aggregated_effect": True,
            "single_task_record_cannot_select_candidate": True,
            "test_labels_are_used_only_for_frozen_final_evaluation": True,
            "unknown_or_test_labels_are_not_used_for_fit_selection_or_threshold": True,
        },
    }
    record["manifest_sha256"] = canonical_hash(record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    parser.add_argument("--suite", default="")
    parser.add_argument("--scenario", default="")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--candidate-root",
        type=Path,
        default=Path(
            "runs/strict_v4_pug_cross_suite_confirmation_v1/candidate"
        ),
    )
    parser.add_argument(
        "--opendetect-root",
        type=Path,
        default=Path(
            "runs/strict_v4_pug_cross_suite_confirmation_v1/opendetect"
        ),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    if not protocol_path.is_file():
        print("state=pending_execution_protocol")
        return
    if not args.suite or not args.scenario or args.seed <= 0:
        raise ValueError("suite, scenario and seed are required after activation")

    protocol = load(protocol_path)
    validate_protocol(protocol)
    task = select_task(protocol, args.suite, args.scenario, args.seed)
    row, hashes = evaluate_cross_task(
        task,
        resolve(args.candidate_root),
        resolve(args.opendetect_root),
        protocol["execution_controls"]["candidate_policy_name"],
    )
    evaluator_path = Path(__file__).resolve()
    record = create_task_record(
        protocol=protocol,
        task=task,
        row=row,
        artifact_sha256=hashes,
        protocol_file_sha256=file_hash(protocol_path),
        evaluator_sha256=file_hash(evaluator_path),
    )
    output = (
        resolve(args.output)
        if args.output is not None
        else root
        / "results/strict_v4_pug_cross_suite_confirmation_v1/tasks"
        / args.suite
        / f"{args.scenario}_seed{args.seed}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        if load(output) != record:
            raise ValueError("existing task evaluation is immutable")
    else:
        temporary = output.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(record, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output)
    print(f"manifest_sha256={record['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
