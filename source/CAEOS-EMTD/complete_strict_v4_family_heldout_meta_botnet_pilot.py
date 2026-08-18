from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


METRIC_NAMES = (
    "alert_accuracy",
    "alert_precision",
    "alert_recall",
    "alert_f1",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
    "unknown_attack_recall",
    "unknown_label_precision",
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
    metrics_by_seed = []
    all_integrity_passed = True
    all_resources_passed = True
    all_effect_gates_passed = True
    for identity in protocol["tasks"]:
        seed = int(identity["seed"])
        task_dir = run_root / f"unknown_botnet_seed{seed}"
        metrics_path = task_dir / "metrics.json"
        gpu_path = task_dir / "gpu_execution.json"
        audit_path = result_root / f"resource_audit_seed{seed}.json"
        evaluation_path = result_root / f"evaluation_seed{seed}.json"
        metrics = load_canonical(metrics_path, f"seed{seed} task metrics")
        gpu = load_canonical(gpu_path, f"seed{seed} GPU evidence")
        audit = load_canonical(audit_path, f"seed{seed} resource audit")
        evaluation = load_canonical(
            evaluation_path, f"seed{seed} fixed evaluation"
        )
        history = metrics["training"]["history"]
        finite_meta = bool(history) and all(
            item["meta_outer_loss"] is not None
            and math.isfinite(float(item["meta_outer_loss"]))
            for item in history
        )
        fixed = evaluation["fixed_evaluation"]
        integrity_pass = (
            finite_meta
            and metrics["state"] == "complete"
            and metrics["model"]["name"].startswith("FHMM-CAEOS")
            and metrics["training"]["meta_heldout_loss_weight"] > 0.0
            and gpu["passes"]
            and evaluation["claim_boundary"][
                "true_unknown_used_for_configuration_selection"
            ]
            is False
        )
        resource_pass = bool(audit["gates"]["all_pass"])
        effect_pass = bool(
            fixed["expansion_gate"]["expand_to_seven_scenarios"]
        )
        all_integrity_passed = all_integrity_passed and integrity_pass
        all_resources_passed = all_resources_passed and resource_pass
        all_effect_gates_passed = all_effect_gates_passed and effect_pass
        metrics_by_seed.append(fixed["metrics"])
        tasks[str(seed)] = {
            "finite_meta_outer_loss_each_epoch": finite_meta,
            "integrity_pass": integrity_pass,
            "resource_pass": resource_pass,
            "effect_expansion_gate_pass": effect_pass,
            "metrics": fixed["metrics"],
            "effect_gates": fixed["expansion_gate"],
            "resource_observed": audit["observed"],
            "metrics_sha256": file_hash(metrics_path),
            "metrics_manifest_sha256": metrics["manifest_sha256"],
            "gpu_execution_sha256": file_hash(gpu_path),
            "gpu_execution_manifest_sha256": gpu["manifest_sha256"],
            "resource_audit_sha256": file_hash(audit_path),
            "resource_audit_manifest_sha256": audit["manifest_sha256"],
            "evaluation_sha256": file_hash(evaluation_path),
            "evaluation_manifest_sha256": evaluation["manifest_sha256"],
        }
    macro_mean = {
        name: float(np.mean([value[name] for value in metrics_by_seed]))
        for name in METRIC_NAMES
    }
    expand = (
        all_integrity_passed
        and all_resources_passed
        and all_effect_gates_passed
    )
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_family_heldout_meta_botnet_pilot_completion_v1"
        ),
        "state": (
            "pilot_expansion_gate_passed"
            if expand
            else "pilot_expansion_gate_not_met"
        ),
        "expand_to_seven_scenarios": expand,
        "all_integrity_passed": all_integrity_passed,
        "all_resources_passed": all_resources_passed,
        "all_effect_gates_passed": all_effect_gates_passed,
        "macro_mean": macro_mean,
        "tasks": tasks,
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
        },
        "claim_boundary": {
            "development_only": True,
            "true_unknown_used_for_configuration_selection": False,
            "fresh_confirmation_effect_claim_authorized": False,
        },
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
