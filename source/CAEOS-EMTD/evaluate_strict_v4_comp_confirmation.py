from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from analyze_caeos_closr_fusion import empirical_percentile
from caeos.continuous_outer_min_p import reconstruct_candidate_risks
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.metrics import fpr_at_95_tpr
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


METRICS = (
    ("known_macro_f1", "higher"),
    ("unknown_auroc", "higher"),
    ("unknown_aupr", "higher"),
    ("unknown_fpr95", "lower"),
    ("oscr", "higher"),
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def report_values(report: dict[str, Any]) -> dict[str, float]:
    values = {}
    for metric, _direction in METRICS:
        value = report.get(metric)
        if not isinstance(value, (int, float)) or not np.isfinite(value):
            raise ValueError(f"finite metric required: {metric}")
        values[metric] = float(value)
    return values


def oriented_delta(candidate: float, reference: float, direction: str) -> float:
    return candidate - reference if direction == "higher" else reference - candidate


def aggregate(rows: list[dict[str, Any]], candidate: str, reference: str) -> dict[str, Any]:
    metrics = {}
    for metric, direction in METRICS:
        candidate_values = np.asarray(
            [row[candidate][metric] for row in rows], dtype=np.float64
        )
        reference_values = np.asarray(
            [row[reference][metric] for row in rows], dtype=np.float64
        )
        deltas = np.asarray(
            [
                oriented_delta(c, r, direction)
                for c, r in zip(candidate_values, reference_values)
            ],
            dtype=np.float64,
        )
        metrics[metric] = {
            "direction": direction,
            "candidate_mean": float(candidate_values.mean()),
            "reference_mean": float(reference_values.mean()),
            "oriented_mean_delta": float(deltas.mean()),
            "win_count": int((deltas > 1e-12).sum()),
            "tie_count": int((np.abs(deltas) <= 1e-12).sum()),
            "loss_count": int((deltas < -1e-12).sum()),
            "minimum_oriented_delta": float(deltas.min()),
            "maximum_oriented_delta": float(deltas.max()),
        }
    return {
        "candidate": candidate,
        "reference": reference,
        "task_count": len(rows),
        "metrics": metrics,
    }


def validate_protocol(protocol: dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_comp_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("state") != "frozen_before_fresh_seed_execution"
        or protocol.get("candidate", {}).get("method") != "caeos_comp"
        or protocol.get("pilot_scope", {}).get("paired_task_count") != 18
        or len(protocol.get("tasks", [])) != 18
    ):
        raise ValueError("canonical frozen CAEOS-COMP protocol required")
    implementation = protocol.get("implementation_sha256")
    if not isinstance(implementation, dict) or not implementation:
        raise ValueError("frozen implementation hashes are required")
    for relative, expected in implementation.items():
        path = Path(relative)
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"frozen implementation drifted: {relative}")


def evaluate_task(
    task: dict[str, Any],
    pairwise_root: Path,
    opendetect_root: Path,
) -> tuple[dict[str, Any], dict[str, str]]:
    suite = str(task["suite"])
    scenario = str(task["scenario"])
    seed = int(task["seed"])
    pairwise_dir = pairwise_root / suite / f"{scenario}_seed{seed}"
    opendetect_dir = opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
    pairwise_files = {
        name: pairwise_dir / name
        for name in ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")
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
        pairwise_metrics.get("risk_policy")
        != "strict_v4_comp_confirmation_pairwise_v1"
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
    pairwise_fingerprint = pairwise_metrics["split_metadata"]["split_fingerprint"][
        "combined"
    ]
    opendetect_fingerprint = opendetect_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    if pairwise_fingerprint != opendetect_fingerprint:
        raise ValueError(f"split fingerprint mismatch: {suite}/{scenario}/seed{seed}")

    with np.load(pairwise_files["scores.npz"], allow_pickle=False) as scores, np.load(
        pairwise_files["evidence_package.npz"], allow_pickle=False
    ) as evidence, np.load(
        opendetect_files["scores.npz"], allow_pickle=False
    ) as opendetect_scores:
        unknown = np.asarray(scores["test_unknown"], dtype=bool)
        if (
            not np.array_equal(unknown, opendetect_scores["test_unknown"].astype(bool))
            or not np.array_equal(scores["test_labels"], opendetect_scores["test_labels"])
        ):
            raise ValueError(f"paired labels differ: {suite}/{scenario}/seed{seed}")
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
        opendetect_report = opendetect_metrics.get("reports", {}).get("opendetect")
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
        "group": str(task["group"]),
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
            f"{suite}/{scenario}/seed{seed}/opendetect/{name}": file_hash(path)
            for name, path in opendetect_files.items()
        }
    )
    return row, hashes


def gate_decision(
    protocol: dict[str, Any],
    rows: list[dict[str, Any]],
    vs_pairwise: dict[str, Any],
    vs_opendetect: dict[str, Any],
) -> dict[str, Any]:
    gate = protocol["admission_gate"]
    pair_gate = gate["candidate_vs_pairwise"]
    open_gate = gate["candidate_vs_opendetect"]
    pair_metrics = vs_pairwise["metrics"]
    stress = [row for row in rows if row["group"] == "stress"]
    stress_wins = sum(
        row["caeos_comp"]["unknown_fpr95"]
        < row["pairwise"]["unknown_fpr95"] - 1e-12
        for row in stress
    )
    checks = {
        "mean_fpr95_improvement": pair_metrics["unknown_fpr95"][
            "oriented_mean_delta"
        ]
        >= pair_gate["mean_unknown_fpr95_oriented_improvement_minimum"],
        "auroc_nonregression": pair_metrics["unknown_auroc"][
            "oriented_mean_delta"
        ]
        >= pair_gate["mean_unknown_auroc_oriented_nonregression"],
        "aupr_nonregression": pair_metrics["unknown_aupr"][
            "oriented_mean_delta"
        ]
        >= pair_gate["mean_unknown_aupr_oriented_nonregression"],
        "oscr_nonregression": pair_metrics["oscr"]["oriented_mean_delta"]
        >= pair_gate["mean_oscr_oriented_nonregression"],
        "known_f1_invariant": abs(
            pair_metrics["known_macro_f1"]["oriented_mean_delta"]
        )
        <= pair_gate["known_macro_f1_absolute_tolerance"],
        "per_task_fpr95_nonregression": pair_metrics["unknown_fpr95"][
            "minimum_oriented_delta"
        ]
        >= -pair_gate["per_task_unknown_fpr95_regression_tolerance"],
        "stress_group_fpr95_wins": stress_wins
        >= pair_gate["stress_group_fpr95_win_minimum"],
        "opendetect_fpr95_noninferiority": vs_opendetect["metrics"][
            "unknown_fpr95"
        ]["oriented_mean_delta"]
        >= -open_gate["mean_unknown_fpr95_noninferiority_margin"],
    }
    return {
        "passes": all(checks.values()),
        "checks": checks,
        "stress_group_task_count": len(stress),
        "stress_group_fpr95_win_count": stress_wins,
        "pairwise_remains_incumbent_if_false": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/protocol.json"),
    )
    parser.add_argument(
        "--pairwise-root",
        type=Path,
        default=Path("runs/strict_v4_comp_confirmation_v1/pairwise"),
    )
    parser.add_argument(
        "--opendetect-root",
        type=Path,
        default=Path("runs/strict_v4_comp_confirmation_v1/opendetect"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/confirmation.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = load(args.protocol)
    validate_protocol(protocol)
    rows = []
    artifact_hashes = {}
    for task in protocol["tasks"]:
        row, hashes = evaluate_task(task, args.pairwise_root, args.opendetect_root)
        rows.append(row)
        artifact_hashes.update(hashes)
    task_keys = [
        (row["suite"], row["scenario"], row["seed"]) for row in rows
    ]
    if len(rows) != 18 or len(set(task_keys)) != 18:
        raise ValueError("exactly 18 unique paired tasks required")
    vs_pairwise = aggregate(rows, "caeos_comp", "pairwise")
    vs_opendetect = aggregate(rows, "caeos_comp", "opendetect")
    result: dict[str, Any] = {
        "schema_version": "strict_v4_comp_confirmation_v1",
        "state": "fresh_seed_confirmation_complete",
        "validation": {
            "passes": True,
            "paired_task_count": len(rows),
            "seeds": sorted(set(row["seed"] for row in rows)),
            "scenario_count": len(set(row["scenario"] for row in rows)),
            "split_fingerprint_pair_checks": len(rows),
            "unknown_or_test_labels_used_for_candidate_routing": False,
            "unknown_or_test_labels_used_for_candidate_thresholds": False,
            "artifact_hash_count": len(artifact_hashes),
            "route_distribution": dict(Counter(row["route"] for row in rows)),
        },
        "candidate_vs_pairwise": vs_pairwise,
        "candidate_vs_opendetect": vs_opendetect,
        "decision": gate_decision(protocol, rows, vs_pairwise, vs_opendetect),
        "tasks": rows,
        "input_evidence": {
            "protocol_path": str(args.protocol.resolve()),
            "protocol_file_sha256": file_hash(args.protocol),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "artifact_sha256": dict(sorted(artifact_hashes.items())),
        },
        "claim_boundary": {
            "fresh_seeds_are_independent_of_candidate_formula_selection": True,
            "scenario_identities_are_development_selected": True,
            "pilot_does_not_authorize_universal_sota": True,
            "cross_suite_expansion_required_after_pilot_pass": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["decision"], indent=2, sort_keys=True))
    print(f"manifest_sha256={result['manifest_sha256']}")
    print(f"file_sha256={file_hash(args.output)}")


if __name__ == "__main__":
    main()
