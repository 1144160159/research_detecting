from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_selected_system_external_malicious import rrc_protocol


SCHEMA = "strict_v4_self_algorithm_direct_tournament_protocol_v1"
ACTIVATION_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_activation_v1"
)
DESIGN_SCHEMA = "strict_v4_self_algorithm_direct_tournament_design_v1"
KRC_SCHEMA = "strict_v4_krc_csr_confirmation_protocol_v1"
PUG_PROTOCOL_SCHEMA = (
    "strict_v4_pug_cross_suite_confirmation_execution_protocol_v1"
)
PUG_COMPLETION_SCHEMA = (
    "strict_v4_pug_cross_suite_confirmation_completion_v1"
)
IMPLEMENTATION_FILES = (
    "write_strict_v4_self_algorithm_direct_tournament_activation.py",
    "create_strict_v4_self_algorithm_direct_tournament_execution_protocol.py",
    "run_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "evaluate_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "summarize_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "audit_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "watch_strict_v4_self_algorithm_direct_tournament_confirmation.py",
)
DEPENDENCY_FILES = (
    "run_strict_v4_selected_system_external_malicious.py",
    "capture_pairwise_runtime.py",
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "certify_rrc_csr_scenario.py",
    "materialize_rrc_csr_runtime.py",
    "train_hybrid_open_set.py",
    "train_mdr_caeos_open_set.py",
    "evaluate_mdr_caeos_runtime.py",
    "caeos/pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/rrc_csr_runtime.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def corruption_seed(identity: str) -> int:
    digest = hashlib.sha256(
        f"strict-v4-direct-tournament/{identity}".encode("utf-8")
    ).hexdigest()
    return 1_000_000 + int(digest[:8], 16) % 1_000_000_000


def formal_output_counts(result_root: Path) -> dict[str, int]:
    return {
        "task_records": len(
            list(result_root.glob("task_records/**/evaluation.json"))
        ),
        "summary": int((result_root / "summary.json").is_file()),
        "audit": int((result_root / "audit.json").is_file()),
        "completion": int(
            (result_root / "execution_complete.json").is_file()
        ),
    }


def create_execution_protocol(
    *,
    project_root: Path,
    activation_path: Path,
    design_path: Path,
    krc_protocol_path: Path,
    pug_protocol_path: Path,
    pug_completion_path: Path,
    result_root: Path,
) -> dict[str, Any]:
    activation = load(activation_path)
    design = load(design_path)
    krc = load(krc_protocol_path)
    pug_protocol = load(pug_protocol_path)
    pug_completion = load(pug_completion_path)
    require_canonical(
        activation, ACTIVATION_SCHEMA, "direct tournament activation"
    )
    require_canonical(design, DESIGN_SCHEMA, "direct tournament design")
    require_canonical(krc, KRC_SCHEMA, "KRC confirmation protocol")
    require_canonical(
        pug_protocol, PUG_PROTOCOL_SCHEMA, "PUG cross-suite protocol"
    )
    require_canonical(
        pug_completion, PUG_COMPLETION_SCHEMA, "PUG cross-suite completion"
    )
    incumbent = activation.get("incumbent_algorithm")
    if (
        activation.get("execution_admitted") is not True
        or incumbent not in ("krc_csr_caeos_v1", "rrc_csr_caeos_v1")
        or activation.get("challenger_algorithm") != "caeos_pug"
        or activation.get("input_manifest_sha256", {}).get(
            "direct_tournament_design"
        )
        != design["manifest_sha256"]
        or pug_completion.get("effect_passes") is not True
        or pug_completion.get("candidate_selected_by_this_stage") is not True
        or pug_completion.get("protocol_manifest_sha256")
        != pug_protocol["manifest_sha256"]
    ):
        raise ValueError("dual-positive tournament inputs are inconsistent")
    counts = formal_output_counts(result_root)
    if any(counts.values()):
        raise ValueError(
            "direct tournament outputs must be zero before protocol freeze"
        )
    source_registry = {
        (row["suite"], row["scenario"]): row
        for row in krc.get("source_registry", [])
    }
    universe = design["confirmation_universe"]
    if len(source_registry) != 102 or len(universe["tasks"]) != 306:
        raise ValueError("exact 102-scenario source registry required")
    tasks = []
    for frozen in universe["tasks"]:
        key = (frozen["suite"], frozen["scenario"])
        source = source_registry.get(key)
        if source is None:
            raise ValueError(f"source registry misses {key}")
        task = {
            **frozen,
            "training_seed": int(frozen["seed"]),
            "corruption_seed": corruption_seed(frozen["identity"]),
            "primary_heldout_scenario": True,
            "source_registry_manifest": {
                "csv": source["csv"],
                "csv_sha256": source["csv_sha256"],
                "config": source["config"],
                "config_sha256": source["config_sha256"],
                "base_trainer_arguments": source[
                    "base_trainer_arguments"
                ],
            },
        }
        tasks.append(task)
    if len({row["identity"] for row in tasks}) != 306:
        raise ValueError("direct tournament task identities are not unique")
    controls = pug_protocol.get("execution_controls", {})
    required_controls = (
        "candidate_risk_selection",
        "candidate_policy_name",
        "pseudo_unknown_max_alpha",
        "pseudo_unknown_min_fold_gain",
        "boundary_hard_pseudo_fraction",
        "boundary_interpolation",
        "boundary_max_per_task",
        "boundary_training_objective",
    )
    if any(name not in controls for name in required_controls):
        raise ValueError("PUG execution controls are incomplete")
    severity = krc.get("confirmation", {}).get("fixed_severity", {})
    conditions = universe["conditions"]
    if (
        conditions != ["clean", "modality_missing", "gaussian_drift"]
        or float(severity.get("modality_missing", -1.0)) != 1.0
        or float(severity.get("gaussian_drift", -1.0)) != 0.5
    ):
        raise ValueError("frozen tournament corruption profile drifted")
    rrc_tasks = [
        {
            "dataset": row["suite"],
            "unknown_attack_family": row["scenario"],
            "training_seed": row["training_seed"],
            "validation_profile_seed": row["corruption_seed"],
        }
        for row in tasks
    ]
    implementation = {
        relative: file_hash(project_root / relative)
        for relative in (*IMPLEMENTATION_FILES, *DEPENDENCY_FILES)
    }
    protocol: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "frozen_and_admitted_after_dual_positive_activation",
        "execution_admitted": True,
        "incumbent_algorithm": incumbent,
        "challenger_algorithm": "caeos_pug",
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "seeds": [809, 811, 821],
            "conditions": conditions,
            "fixed_severity": {
                "clean": 0.0,
                "modality_missing": 1.0,
                "gaussian_drift": 0.5,
            },
            "paired_task_count": 306,
            "paired_evaluation_count": 918,
            "scenarios_by_suite": universe["scenarios_by_suite"],
            "tasks": tasks,
        },
        "candidate_training": {
            "incumbent_backend": (
                "fresh_krc_capture"
                if incumbent == "krc_csr_caeos_v1"
                else "fresh_csr_capture_then_three_seed_rrc_certificate"
            ),
            "rrc_backend_protocol": (
                rrc_protocol(rrc_tasks)
                if incumbent == "rrc_csr_caeos_v1"
                else None
            ),
            "challenger_backend": "fresh_pairwise_family_pug_capture",
            "pug_execution_controls": {
                name: controls[name] for name in required_controls
            },
            "training_sample_fraction": float(
                krc["confirmation"]["training_sample_fraction"]
            ),
            "fixed_augmentation_weight": float(
                krc["confirmation"]["fixed_augmentation_weight"]
            ),
            "health_quantile": float(
                krc["confirmation"]["health_quantile"]
            ),
            "same_source_csv_config_seed_and_split_required": True,
            "unknown_or_test_labels_used_for_training_selection": False,
        },
        "selection_gate": design["challenger_admission_gate"],
        "statistics": design["statistics"],
        "resource_contract": design["resource_contract"],
        "implementation_sha256": implementation,
        "input_manifest_sha256": {
            "activation": activation["manifest_sha256"],
            "design": design["manifest_sha256"],
            "krc_protocol": krc["manifest_sha256"],
            "pug_cross_suite_protocol": pug_protocol["manifest_sha256"],
            "pug_cross_suite_completion": pug_completion["manifest_sha256"],
        },
        "input_file_sha256": {
            "activation": file_hash(activation_path),
            "design": file_hash(design_path),
            "krc_protocol": file_hash(krc_protocol_path),
            "pug_cross_suite_protocol": file_hash(pug_protocol_path),
            "pug_cross_suite_completion": file_hash(pug_completion_path),
        },
        "formal_output_counts_at_freeze": counts,
        "claim_boundary": {
            "protocol_is_not_execution_or_effect": True,
            "single_task_or_partial_results_cannot_select_candidate": True,
            "test_labels_used_only_for_frozen_final_evaluation": True,
            "external_malicious_benign_safety_and_efficiency_remain_required": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def write_protocol(path: Path, value: dict[str, Any]) -> None:
    if path.is_file():
        if load(path) != value:
            raise ValueError("existing direct tournament protocol is immutable")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1"
        ),
    )
    parser.add_argument(
        "--activation",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1/"
            "activation.json"
        ),
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--krc-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_krc_csr_confirmation_v1/protocol.json"
        ),
    )
    parser.add_argument(
        "--pug-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--pug-completion",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/"
            "execution_complete.json"
        ),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    result_root = resolve(args.result_root)
    protocol = create_execution_protocol(
        project_root=root,
        activation_path=resolve(args.activation),
        design_path=resolve(args.design),
        krc_protocol_path=resolve(args.krc_protocol),
        pug_protocol_path=resolve(args.pug_protocol),
        pug_completion_path=resolve(args.pug_completion),
        result_root=result_root,
    )
    output = result_root / "protocol.json"
    write_protocol(output, protocol)
    print(
        json.dumps(
            {
                "state": "protocol_frozen_execution_not_started",
                "output": str(output),
                "manifest_sha256": protocol["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
