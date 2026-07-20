from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--previous-addendum", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--helper", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    previous = json.loads(args.previous_addendum.read_text(encoding="utf-8"))
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("coverage manifest SHA mismatch")
    previous_core = dict(previous)
    previous_record_sha = previous_core.pop("record_sha256", None)
    if previous_record_sha != canonical_hash(previous_core):
        raise ValueError("previous scheduler addendum SHA mismatch")

    metrics = list(args.run_root.glob("*/*/metrics.json"))
    failures = list(args.run_root.glob("*/*/failure.json"))
    cic_iot_metrics = list((args.run_root / "cic_iot2023").glob("*/metrics.json"))
    if not 78 <= len(metrics) < 103 or failures:
        raise ValueError(
            "workers6 change expected 78-102 completed and zero failed: "
            f"metrics={len(metrics)} failures={len(failures)}"
        )

    payload: dict[str, Any] = {
        "schema_version": "strict_v4_full103_scheduler_addendum_v2",
        "coverage_manifest_sha256": manifest["manifest_sha256"],
        "previous_addendum_sha256": previous_record_sha,
        "state_at_change": {
            "completed_scenarios": len(metrics),
            "cic_iot2023_completed": len(cic_iot_metrics),
            "failures": 0,
        },
        "change": {
            "suite": "cic_iot2023",
            "outer_scenario_workers_before": 4,
            "outer_scenario_workers_after": 6,
            "per_scenario_model_jobs": 8,
            "per_scenario_training_command_changed": False,
            "random_seed_changed": False,
            "algorithm_or_hyperparameter_changed": False,
            "reason": (
                "Observed about 12 CPU cores and 11 GiB per task on an "
                "80-core, 503-GiB host; reduce wall-clock without oversubscription"
            ),
        },
        "implementation_sha256": {
            "run_nested_gate_matrix.py": file_hash(args.runner),
            "scripts/resume_strict_v4_ciciot_workers6.sh": file_hash(args.helper),
        },
    }
    payload["record_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
