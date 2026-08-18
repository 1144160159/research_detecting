from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


DESIGN_CANONICAL_SHA256 = (
    "dd5339d86af37455b3abf2febf9e0ae3675557d97ad80f590f735aae682241e6"
)
DESIGN_FILE_SHA256 = (
    "18551cb1caec615145e8a0cf6ee55f69b3bdc506c9c7267658c46a10d1bbd3c2"
)
FORMAL_OUTPUTS = (
    "confirmation.json",
    "confirmation_complete",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_design(design: dict[str, Any], path: Path) -> None:
    pilot = design.get("fresh_pilot", {})
    tasks = pilot.get("tasks", [])
    identities = {
        (row.get("suite"), row.get("scenario"), row.get("seed"))
        for row in tasks
        if isinstance(row, dict)
    }
    if (
        file_hash(path) != DESIGN_FILE_SHA256
        or design.get("manifest_sha256") != DESIGN_CANONICAL_SHA256
        or design.get("manifest_sha256") != canonical_hash(design)
        or design.get("schema_version") != "strict_v4_pug_design_protocol_v1"
        or design.get("state")
        != "frozen_before_candidate_integration_and_fresh_seed_execution"
        or design.get("candidate", {}).get("method") != "caeos_pug"
        or pilot.get("paired_task_count") != 18
        or len(tasks) != 18
        or len(identities) != 18
        or pilot.get("execution_admitted_at_design_freeze") is not False
        or any(design.get("observed_output_counts_at_freeze", {}).values())
    ):
        raise ValueError("canonical zero-result PUG design is required")


def create_protocol(
    design: dict[str, Any],
    design_file_path: Path,
    design_record_path: Path,
    implementation_sha256: dict[str, str],
    recovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_design(design, design_file_path)
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_pug_execution_protocol_v1",
        "state": "frozen_before_fresh_seed_execution",
        "design": {
            "path": design_record_path.as_posix(),
            "canonical_sha256": DESIGN_CANONICAL_SHA256,
            "file_sha256": DESIGN_FILE_SHA256,
        },
        "candidate": design["candidate"],
        "training_time_selection": design["training_time_selection"],
        "pilot_scope": {
            **{
                key: design["fresh_pilot"][key]
                for key in (
                    "suite",
                    "stress_scenarios",
                    "control_scenarios",
                    "seeds",
                    "paired_task_count",
                )
            },
            "max_per_class": 1000,
        },
        "tasks": design["fresh_pilot"]["tasks"],
        "execution": {
            "candidate_risk_selection": "nested_pug_continuous_outer_min_p",
            "candidate_policy_name": "strict_v4_pug_confirmation_v1",
            "pseudo_unknown_max_alpha": 0.5,
            "pseudo_unknown_min_fold_gain": -0.05,
            "boundary_hard_pseudo_fraction": 0.5,
            "boundary_interpolation": 0.5,
            "boundary_max_per_task": 512,
            "boundary_training_objective": "pairwise",
            "estimators": 80,
            "model_jobs": 8,
            "workers": 2,
            "opendetect_epochs": 0,
            "cache_must_be_seed_specific": True,
            "split_fingerprints_must_match_within_each_pair": True,
            "candidate_run_contains_exact_pairwise_reference": True,
            "resource_idle_consecutive_polls": 3,
        },
        "admission_gate": design["fresh_pilot_admission_gate"],
        "implementation_sha256": implementation_sha256,
        "result_contract": {
            "candidate_run_count": 18,
            "fresh_opendetect_run_count": 18,
            "paired_task_count": 18,
            "partial_metrics_must_not_be_aggregated": True,
            "confirmation_required_before_candidate_decision": True,
        },
        "claim_boundary": {
            **design["claim_boundary"],
            "isolated_seed997_smoke_is_implementation_evidence_only": True,
            "passing_pilot_requires_fresh_cross_suite_confirmation": True,
            "pairwise_remains_incumbent_until_all_gates_pass": True,
        },
    }
    if recovery is not None:
        protocol["infrastructure_recovery"] = recovery
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def create_recovery_record(
    *,
    root: Path,
    protocol_path: Path,
    failed_log_path: Path,
) -> dict[str, Any]:
    original = load(protocol_path)
    failure_text = failed_log_path.read_text(encoding="utf-8", errors="replace")
    failure_marker = (
        "invalid choice: 'nested_pug_continuous_outer_min_p'"
    )
    if (
        original.get("schema_version") != "strict_v4_pug_execution_protocol_v1"
        or original.get("manifest_sha256") != canonical_hash(original)
        or original.get("state") != "frozen_before_fresh_seed_execution"
        or original.get("execution", {}).get("candidate_risk_selection")
        != "nested_pug_continuous_outer_min_p"
        or len(original.get("tasks", [])) != 18
        or failure_marker not in failure_text
    ):
        raise ValueError("canonical failed PUG execution evidence required")
    return {
        "kind": "entrypoint_choice_integration_recovery",
        "original_protocol": {
            "path": protocol_path.relative_to(root).as_posix(),
            "canonical_sha256": original["manifest_sha256"],
            "file_sha256": file_hash(protocol_path),
        },
        "failed_candidate_log": {
            "path": failed_log_path.relative_to(root).as_posix(),
            "file_sha256": file_hash(failed_log_path),
            "failure_marker": failure_marker,
        },
        "allowed_change": {
            "path": "run_nested_gate_matrix.py",
            "description": (
                "Expose the already implemented frozen PUG risk-selection name "
                "through the matrix entrypoint."
            ),
        },
        "unchanged_effect_design": (
            "Seeds, scenarios, data caches, model settings, candidate rule, "
            "references, and admission gates remain identical."
        ),
        "claim_boundary": (
            "This record repairs infrastructure only and does not use candidate "
            "effects for method selection."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--design",
        type=Path,
        default=Path("results/strict_v4_pug_design_v1/design_protocol.json"),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path("results/strict_v4_pug_confirmation_v1"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
        ),
    )
    parser.add_argument("--recovery-of-protocol", type=Path)
    parser.add_argument("--failed-log", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    design_path = resolve(args.design)
    result_root = resolve(args.result_root)
    existing = [name for name in FORMAL_OUTPUTS if (result_root / name).exists()]
    existing.extend(
        str(path.relative_to(result_root))
        for path in result_root.glob("tasks/*.json")
        if path.is_file()
    )
    if existing:
        raise ValueError("PUG formal outputs must be zero before protocol freeze")
    implementation_paths = [
        Path(__file__).resolve(),
        root / "train_hybrid_open_set.py",
        root / "train_neural_open_set.py",
        root / "run_nested_gate_matrix.py",
        root / "run_neural_baseline_matrix.py",
        root / "prepare_cic_iot2023_strict.py",
        root / "prepare_group_supported_cache.py",
        root / "caeos/continuous_outer_min_p.py",
        root / "caeos/pseudo_unknown_gated_continuous.py",
        root / "inspect_strict_v4_pug_run.py",
        root / "evaluate_strict_v4_pug_confirmation.py",
        root / "watch_strict_v4_pug_confirmation.py",
        root / "scripts/run_strict_v4_pug_confirmation.sh",
    ]
    implementation_sha256 = {
        path.relative_to(root).as_posix(): file_hash(path)
        for path in implementation_paths
    }
    if bool(args.recovery_of_protocol) != bool(args.failed_log):
        raise ValueError(
            "--recovery-of-protocol and --failed-log must be provided together"
        )
    recovery = None
    if args.recovery_of_protocol is not None:
        recovery = create_recovery_record(
            root=root,
            protocol_path=resolve(args.recovery_of_protocol),
            failed_log_path=resolve(args.failed_log),
        )
    protocol = create_protocol(
        load(design_path),
        design_path,
        design_path.relative_to(root),
        implementation_sha256,
        recovery,
    )
    output = resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest_sha256": protocol["manifest_sha256"],
                "file_sha256": file_hash(output),
                "task_count": len(protocol["tasks"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
