from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from analyze_caeos_closr_fusion import empirical_percentile
from caeos.continuous_outer_min_p import reconstruct_candidate_risks
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.metrics import fpr_at_95_tpr
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from evaluate_strict_v4_comp_confirmation import close, load, report_values


def validate_protocol(
    protocol: dict[str, Any], *, check_implementation: bool = True
) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_comp_cross_suite_execution_protocol_v1"
        or protocol.get("state")
        != "frozen_after_positive_pilot_before_cross_suite_execution"
        or protocol.get("execution_admitted") is not True
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical admitted cross-suite protocol required")
    universe = protocol.get("confirmation_universe", {})
    tasks = universe.get("tasks")
    if (
        universe.get("suite_count") != 7
        or universe.get("scenario_count") != 102
        or universe.get("paired_task_count") != 306
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
        or protocol.get("execution_controls", {}).get("pairwise_policy_name")
        != "strict_v4_comp_cross_suite_pairwise_v1"
        or protocol.get("output_contract", {}).get(
            "partial_metrics_must_not_be_aggregated"
        )
        is not True
    ):
        raise ValueError("cross-suite protocol universe drifted")
    if check_implementation:
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items():
            path = Path(relative)
            if not path.is_file() or file_hash(path) != expected:
                raise ValueError(f"frozen implementation drifted: {relative}")


def evaluate_cross_task(
    task: dict[str, Any],
    pairwise_root: Path,
    opendetect_root: Path,
    expected_policy_name: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    suite = str(task["suite"])
    scenario = str(task["scenario"])
    seed = int(task["seed"])
    pairwise_dir = pairwise_root / suite / f"{scenario}_seed{seed}"
    opendetect_dir = (
        opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
    )
    pairwise_files = {
        name: pairwise_dir / name
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
        for path in [*pairwise_files.values(), *opendetect_files.values()]
        if not path.is_file()
    ]
    if missing:
        raise ValueError(f"missing confirmation artifacts: {missing}")
    pairwise_metrics = load(pairwise_files["metrics.json"])
    opendetect_metrics = load(opendetect_files["metrics.json"])
    if (
        pairwise_metrics.get("risk_policy") != expected_policy_name
        or pairwise_metrics.get("risk_selection_details", {}).get(
            "unknown_or_test_labels_used_for_selection"
        )
        is not False
        or opendetect_metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError(f"leakage guard failed: {suite}/{scenario}/seed{seed}")
    pairwise_fingerprint = pairwise_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    opendetect_fingerprint = opendetect_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    if pairwise_fingerprint != opendetect_fingerprint:
        raise ValueError(
            f"split fingerprint mismatch: {suite}/{scenario}/seed{seed}"
        )

    with np.load(
        pairwise_files["scores.npz"], allow_pickle=False
    ) as scores, np.load(
        pairwise_files["evidence_package.npz"], allow_pickle=False
    ) as evidence, np.load(
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
        risks = reconstruct_candidate_risks(scores, evidence)
        validation_reference = empirical_percentile(
            risks["validation_reference"], risks["validation_reference"]
        )
        test_reference = empirical_percentile(
            risks["validation_reference"], risks["test_reference"]
        )
        validation_candidate = empirical_percentile(
            risks["validation_candidate"], risks["validation_candidate"]
        )
        test_candidate = empirical_percentile(
            risks["validation_candidate"], risks["test_candidate"]
        )
        reference_threshold = float(np.quantile(validation_reference, 0.95))
        candidate_threshold = float(np.quantile(validation_candidate, 0.95))
        pairwise_report = evaluate_hybrid_open_set(
            scores["test_labels"],
            unknown,
            scores["test_prediction"],
            test_reference,
            reference_threshold,
        )
        candidate_report = evaluate_hybrid_open_set(
            scores["test_labels"],
            unknown,
            scores["test_prediction"],
            test_candidate,
            candidate_threshold,
        )
        opendetect_report = opendetect_metrics.get("reports", {}).get(
            "opendetect"
        )
        if not isinstance(opendetect_report, dict):
            raise ValueError("OpenDetect report is absent")
        recomputed_fpr95 = fpr_at_95_tpr(
            unknown.astype(np.int64), opendetect_scores["test_opendetect"]
        )
        if not close(recomputed_fpr95, opendetect_report["unknown_fpr95"]):
            raise ValueError("OpenDetect FPR95 recomputation mismatch")

    row = {
        "suite": suite,
        "scenario": scenario,
        "group": "cross_suite",
        "seed": seed,
        "route": risks["route"],
        "changed": bool(risks["changed"]),
        "selected_risk_name": risks["selected_risk_name"],
        "pairwise": report_values(pairwise_report),
        "caeos_comp": report_values(candidate_report),
        "opendetect": report_values(opendetect_report),
        "split_fingerprint": pairwise_fingerprint,
    }
    hashes = {
        f"{suite}/{scenario}/seed{seed}/pairwise/{name}": file_hash(path)
        for name, path in pairwise_files.items()
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
    if row.get("group") != "cross_suite":
        raise ValueError("cross-suite evaluation group required")
    if not isinstance(artifact_sha256, dict) or len(artifact_sha256) != 7:
        raise ValueError("exactly seven paired artifact hashes required")
    record: dict[str, Any] = {
        "schema_version": (
            "strict_v4_comp_cross_suite_task_evaluation_v1"
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
            "evaluate_strict_v4_comp_cross_suite_confirmation.py": (
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
            "results/strict_v4_comp_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    parser.add_argument("--suite", default="")
    parser.add_argument("--scenario", default="")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--pairwise-root",
        type=Path,
        default=Path(
            "runs/strict_v4_comp_cross_suite_confirmation_v1/pairwise"
        ),
    )
    parser.add_argument(
        "--opendetect-root",
        type=Path,
        default=Path(
            "runs/strict_v4_comp_cross_suite_confirmation_v1/opendetect"
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
        resolve(args.pairwise_root),
        resolve(args.opendetect_root),
        protocol["execution_controls"]["pairwise_policy_name"],
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
        / "results/strict_v4_comp_cross_suite_confirmation_v1/tasks"
        / args.suite
        / f"{args.scenario}_seed{args.seed}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        existing = load(output)
        if existing != record:
            raise ValueError("existing task evaluation is immutable")
    else:
        temporary = output.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
    print(f"manifest_sha256={record['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
