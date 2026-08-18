from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def complete(
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    protocol = load_json(protocol_path)
    tasks = {}
    all_pass = True
    for identity in protocol["tasks"]:
        seed = int(identity["seed"])
        task_dir = run_root / f"unknown_botnet_seed{seed}"
        metrics_path = task_dir / "metrics.json"
        gpu_path = task_dir / "gpu_execution.json"
        audit_path = result_root / f"resource_audit_seed{seed}.json"
        metrics = load_canonical(metrics_path, f"seed{seed} metrics")
        gpu = load_canonical(gpu_path, f"seed{seed} GPU evidence")
        audit = load_canonical(audit_path, f"seed{seed} resource audit")
        history = metrics["training"]["history"]
        finite_meta = bool(history) and all(
            item["meta_outer_loss"] is not None
            and math.isfinite(float(item["meta_outer_loss"]))
            for item in history
        )
        task_pass = (
            metrics["state"] == "complete"
            and metrics["model"]["name"].startswith("FHMM-CAEOS")
            and metrics["training"]["meta_heldout_loss_weight"] > 0.0
            and gpu["passes"]
            and audit["gates"]["all_pass"]
            and finite_meta
        )
        all_pass = all_pass and task_pass
        tasks[str(seed)] = {
            "passes": task_pass,
            "finite_meta_outer_loss_each_epoch": finite_meta,
            "metrics_sha256": file_hash(metrics_path),
            "metrics_manifest_sha256": metrics["manifest_sha256"],
            "gpu_execution_sha256": file_hash(gpu_path),
            "gpu_execution_manifest_sha256": gpu["manifest_sha256"],
            "resource_audit_sha256": file_hash(audit_path),
            "resource_audit_manifest_sha256": audit["manifest_sha256"],
            "resource_observed": audit["observed"],
        }
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_family_heldout_meta_parallel_smoke_completion_v1"
        ),
        "state": "complete_pass" if all_pass else "complete_fail",
        "all_tasks_passed": all_pass,
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
        },
        "tasks": tasks,
        "effect_claim_authorized": False,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = complete(args.protocol, args.run_root, args.result_root)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
