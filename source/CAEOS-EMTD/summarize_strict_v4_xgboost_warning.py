from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


METRICS = (
    "alert_accuracy",
    "alert_precision",
    "alert_recall",
    "alert_f1",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
)


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def gates(mean: dict[str, float]) -> dict[str, bool]:
    result = {
        "alert_accuracy_at_least_95_percent": mean["alert_accuracy"] >= 0.95,
        "alert_precision_at_least_95_percent": mean["alert_precision"] >= 0.95,
        "alert_recall_at_least_95_percent": mean["alert_recall"] >= 0.95,
        "benign_fpr_below_5_percent": mean["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            mean["known_attack_type_accuracy"] >= 0.95
        ),
    }
    result["basic_warning_95_5_gate"] = all(result.values())
    result["full_known_unknown_95_5_gate"] = False
    return result


def summarize(project_root: Path, protocol_path: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol = load(protocol_path)
    run_root = project_root / protocol["run_root"] / "cicids2017"
    records = []
    for path in sorted(run_root.glob("*/metrics.json")):
        record = load(path)
        declared = record.get("manifest_sha256")
        body = dict(record)
        body.pop("manifest_sha256", None)
        if canonical_hash(body) != declared:
            raise ValueError(f"task canonical mismatch: {path}")
        records.append(record)
    if len(records) != protocol["expected_task_count"]:
        raise ValueError("XGBoost task coverage is incomplete")
    identities = {
        (
            record["task"]["scenario"],
            int(record["task"]["seed"]),
        )
        for record in records
    }
    expected = {
        (scenario, int(seed))
        for scenario in protocol["scenarios"]
        for seed in protocol["seeds"]
    }
    if identities != expected or len(identities) != len(records):
        raise ValueError("XGBoost task identity coverage is invalid")

    by_seed = {}
    for seed in protocol["seeds"]:
        selected = [
            record for record in records if int(record["task"]["seed"]) == seed
        ]
        mean = {
            metric: float(
                np.mean(
                    [record["operational_metrics"][metric] for record in selected]
                )
            )
            for metric in METRICS
        }
        by_seed[str(seed)] = {
            "scenario_count": len(selected),
            "mean": mean,
            "gates": gates(mean),
        }
    overall = {
        metric: float(
            np.mean(
                [record["operational_metrics"][metric] for record in records]
            )
        )
        for metric in METRICS
    }
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_warning_summary_v1",
        "state": "complete",
        "scenario_count": len(records),
        "by_seed": by_seed,
        "overall_mean": overall,
        "overall_gates": gates(overall),
        "all_seed_basic_warning_95_5_gate": all(
            item["gates"]["basic_warning_95_5_gate"]
            for item in by_seed.values()
        ),
        "all_seed_full_known_unknown_95_5_gate": False,
        "claim_boundary": protocol["claim_boundary"],
        "bindings": {
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "task_metrics_sha256": {
                f"{record['task']['scenario']}_seed{record['task']['seed']}": (
                    file_hash(
                        run_root
                        / f"{record['task']['scenario']}_seed{record['task']['seed']}"
                        / "metrics.json"
                    )
                )
                for record in records
            },
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = summarize(args.project_root, args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
