from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.metrics import fpr_at_95_tpr
from caeos.pseudo_unknown_gated_continuous import PUG_RISK_NAME
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from inspect_strict_v4_pug_run import inspect_run


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


def oriented(candidate: float, reference: float, direction: str) -> float:
    return candidate - reference if direction == "higher" else reference - candidate


def aggregate(
    rows: list[dict[str, Any]], candidate: str, reference: str
) -> dict[str, Any]:
    result = {}
    for metric, direction in METRICS:
        candidate_values = np.asarray(
            [row[candidate][metric] for row in rows], dtype=np.float64
        )
        reference_values = np.asarray(
            [row[reference][metric] for row in rows], dtype=np.float64
        )
        deltas = np.asarray(
            [
                oriented(candidate_value, reference_value, direction)
                for candidate_value, reference_value in zip(
                    candidate_values, reference_values
                )
            ]
        )
        result[metric] = {
            "direction": direction,
            "candidate_mean": float(candidate_values.mean()),
            "reference_mean": float(reference_values.mean()),
            "oriented_mean_delta": float(deltas.mean()),
            "minimum_oriented_delta": float(deltas.min()),
            "win_count": int((deltas > 1e-12).sum()),
            "tie_count": int((np.abs(deltas) <= 1e-12).sum()),
            "loss_count": int((deltas < -1e-12).sum()),
        }
    return {"candidate": candidate, "reference": reference, "metrics": result}


def validate_protocol(protocol: dict[str, Any]) -> None:
    if (
        protocol.get("schema_version") != "strict_v4_pug_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("state") != "frozen_before_fresh_seed_execution"
        or len(protocol.get("tasks", [])) != 18
    ):
        raise ValueError("canonical PUG execution protocol required")
    for relative, expected in protocol.get("implementation_sha256", {}).items():
        path = Path(relative)
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"frozen implementation drifted: {relative}")


def evaluate_task(
    task: dict[str, Any], candidate_root: Path, opendetect_root: Path
) -> tuple[dict[str, Any], dict[str, str]]:
    suite = str(task["suite"])
    scenario = str(task["scenario"])
    seed = int(task["seed"])
    candidate_dir = candidate_root / suite / f"{scenario}_seed{seed}"
    opendetect_dir = (
        opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
    )
    inspection = inspect_run(candidate_dir)
    candidate_metrics = load(candidate_dir / "metrics.json")
    opendetect_metrics = load(opendetect_dir / "metrics.json")
    if (
        candidate_metrics.get("risk_policy") != "strict_v4_pug_confirmation_v1"
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
        raise ValueError(f"split mismatch: {suite}/{scenario}/seed{seed}")

    base = inspection["pairwise_base_selected_risk"]
    selected = inspection["selected_risk"]
    with np.load(candidate_dir / "scores.npz", allow_pickle=False) as scores, np.load(
        opendetect_dir / "scores.npz", allow_pickle=False
    ) as opendetect_scores:
        unknown = np.asarray(scores["test_unknown"], dtype=bool)
        if (
            not np.array_equal(unknown, opendetect_scores["test_unknown"])
            or not np.array_equal(
                scores["test_labels"], opendetect_scores["test_labels"]
            )
        ):
            raise ValueError("paired labels differ")
        reports = {}
        for name in (base, selected):
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
                for metric, _direction in METRICS
            ):
                raise ValueError(f"report recomputation mismatch: {name}")
            reports[name] = report_values(report)
        opendetect_report = opendetect_metrics["reports"]["opendetect"]
        recomputed_fpr95 = fpr_at_95_tpr(
            unknown.astype(np.int64), opendetect_scores["test_opendetect"]
        )
        if not close(recomputed_fpr95, opendetect_report["unknown_fpr95"]):
            raise ValueError("OpenDetect FPR95 recomputation mismatch")

    hashes = {}
    for prefix, directory, names in (
        (
            "candidate",
            candidate_dir,
            ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json"),
        ),
        ("opendetect", opendetect_dir, ("metrics.json", "scores.npz", "provenance.json")),
    ):
        for name in names:
            path = directory / name
            if not path.is_file():
                raise ValueError(f"missing artifact: {path}")
            hashes[f"{suite}/{scenario}/seed{seed}/{prefix}/{name}"] = file_hash(path)
    return (
        {
            "suite": suite,
            "scenario": scenario,
            "group": task["group"],
            "seed": seed,
            "pairwise_base_selected_risk": base,
            "pug_selected_risk": selected,
            "pug_gate_passes": inspection["pug_gate_passes"],
            "pug_selected": inspection["pug_selected"],
            "pairwise": reports[base],
            "caeos_pug": reports[selected],
            "opendetect": report_values(opendetect_report),
            "split_fingerprint": candidate_fingerprint,
            "unknown_or_test_labels_used_for_selection": False,
        },
        hashes,
    )


def evaluate(
    protocol: dict[str, Any], candidate_root: Path, opendetect_root: Path
) -> dict[str, Any]:
    validate_protocol(protocol)
    rows = []
    hashes = {}
    for task in protocol["tasks"]:
        row, task_hashes = evaluate_task(task, candidate_root, opendetect_root)
        rows.append(row)
        hashes.update(task_hashes)
    pairwise = aggregate(rows, "caeos_pug", "pairwise")
    external = aggregate(rows, "caeos_pug", "opendetect")
    pairwise_metrics = pairwise["metrics"]
    gates = protocol["admission_gate"]
    own_gate = gates["candidate_vs_pairwise"]
    external_gate = gates["candidate_vs_opendetect"]
    checks = {
        "paired_task_count": len(rows) == 18,
        "known_f1_invariant": abs(
            pairwise_metrics["known_macro_f1"]["oriented_mean_delta"]
        )
        <= own_gate["known_macro_f1_absolute_tolerance"],
        "mean_fpr95_improvement": pairwise_metrics["unknown_fpr95"][
            "oriented_mean_delta"
        ]
        >= own_gate["mean_unknown_fpr95_oriented_improvement_minimum"],
        "mean_auroc_nonregression": pairwise_metrics["unknown_auroc"][
            "oriented_mean_delta"
        ]
        >= own_gate["mean_unknown_auroc_oriented_nonregression"],
        "mean_aupr_nonregression": pairwise_metrics["unknown_aupr"][
            "oriented_mean_delta"
        ]
        >= own_gate["mean_unknown_aupr_oriented_nonregression"],
        "mean_oscr_nonregression": pairwise_metrics["oscr"][
            "oriented_mean_delta"
        ]
        >= own_gate["mean_oscr_oriented_nonregression"],
        "per_task_aupr_protection": pairwise_metrics["unknown_aupr"][
            "minimum_oriented_delta"
        ]
        >= -own_gate["per_task_unknown_aupr_regression_tolerance"],
        "per_task_fpr95_protection": pairwise_metrics["unknown_fpr95"][
            "minimum_oriented_delta"
        ]
        >= -own_gate["per_task_unknown_fpr95_regression_tolerance"],
        "stress_fpr95_wins": sum(
            row["group"] == "stress"
            and row["caeos_pug"]["unknown_fpr95"]
            < row["pairwise"]["unknown_fpr95"] - 1e-12
            for row in rows
        )
        >= own_gate["stress_group_fpr95_win_minimum"],
        "opendetect_fpr95_noninferiority": external["metrics"]["unknown_fpr95"][
            "oriented_mean_delta"
        ]
        >= -external_gate["mean_unknown_fpr95_noninferiority_margin"],
        "selection_isolation": all(
            row["unknown_or_test_labels_used_for_selection"] is False
            for row in rows
        ),
    }
    result = {
        "schema_version": "strict_v4_pug_confirmation_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "task_count": len(rows),
        "tasks": rows,
        "artifact_sha256": hashes,
        "candidate_vs_pairwise": pairwise,
        "candidate_vs_opendetect": external,
        "gate_checks": checks,
        "decision": {
            "passes": all(checks.values()),
            "selected_method": "caeos_pug" if all(checks.values()) else "caeos_pairwise",
            "cross_suite_execution_admitted": False,
        },
        "partial_metrics_aggregated": False,
        "unknown_or_test_labels_used_for_selection": False,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(load(args.protocol), args.candidate_root, args.opendetect_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["decision"], sort_keys=True))


if __name__ == "__main__":
    main()
