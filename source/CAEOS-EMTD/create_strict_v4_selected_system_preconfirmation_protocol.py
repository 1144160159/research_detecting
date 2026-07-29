from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_design import (
    ALGORITHMS,
    CORRUPTION_FAMILIES,
    MAIN_METHODS,
    SCHEMA as DESIGN_SCHEMA,
)
from run_strict_v4_selected_system_efficiency import build_sources
from run_strict_v4_selected_system_external_malicious import (
    opendetect_policy,
    pairwise_policy,
    rrc_protocol,
)
from write_strict_v4_selected_system_preconfirmation_activation import (
    SCHEMA as ACTIVATION_SCHEMA,
)


SCHEMA = "strict_v4_selected_system_preconfirmation_protocol_v1"
IMPLEMENTATION_FILES = (
    "create_strict_v4_selected_system_preconfirmation_protocol.py",
    "run_strict_v4_selected_system_preconfirmation.py",
    "evaluate_strict_v4_selected_system_preconfirmation.py",
    "summarize_strict_v4_selected_system_preconfirmation.py",
    "audit_strict_v4_selected_system_preconfirmation.py",
    "watch_strict_v4_selected_system_preconfirmation.py",
)
DEPENDENCY_FILES = (
    "run_strict_v4_selected_system_efficiency.py",
    "run_strict_v4_selected_system_parrot_safety.py",
    "run_strict_v4_selected_system_external_malicious.py",
    "evaluate_mlp_mahalanobis_pp.py",
    "evaluate_strict_v4_comparative_corruption.py",
    "train_hybrid_open_set.py",
    "capture_pairwise_runtime.py",
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "capture_opendetect_training_runtime.py",
    "materialize_rrc_csr_runtime.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def formal_output_counts(run_root: Path, result_root: Path) -> dict[str, int]:
    return {
        "task_records": (
            len(list(run_root.glob("model_pairs/**/preconfirmation.json")))
            if run_root.exists()
            else 0
        ),
        "protocol": int((result_root / "protocol.json").is_file()),
        "summary": int((result_root / "summary.json").is_file()),
        "audit": int((result_root / "audit.json").is_file()),
        "completion": int((result_root / "execution_complete.json").is_file()),
    }


def validate_bound_source(
    *,
    name: str,
    path: Path,
    value: dict[str, Any],
    design: dict[str, Any],
) -> None:
    if (
        design["source_manifest_sha256"].get(name)
        != value.get("manifest_sha256")
        or design["source_file_sha256"].get(name) != file_hash(path)
    ):
        raise ValueError(f"preconfirmation design source drifted: {name}")


def build_protocol(
    *,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    activation_path: Path,
    design_path: Path,
    classic_protocol_path: Path,
    confirmation_protocol_path: Path,
    confirmation_capture_root: Path,
    absolute_protocol_path: Path,
    comparative_protocol_path: Path,
    adapter_design_path: Path,
) -> dict[str, Any]:
    activation = load(activation_path)
    design = load(design_path)
    classic = load(classic_protocol_path)
    confirmation = load(confirmation_protocol_path)
    absolute = load(absolute_protocol_path)
    comparative = load(comparative_protocol_path)
    adapter = load(adapter_design_path)
    require_canonical(activation, ACTIVATION_SCHEMA, "preconfirmation activation")
    require_canonical(design, DESIGN_SCHEMA, "preconfirmation design")
    require_canonical(
        classic,
        "strict_v4_classical_main_baseline_protocol_v1",
        "classic main protocol",
    )
    require_canonical(
        confirmation,
        "strict_v4_krc_csr_confirmation_protocol_v1",
        "KRC source protocol",
    )
    require_canonical(
        absolute,
        "strict_v4_postselection_corruption_suite_gate_protocol_v1",
        "absolute corruption protocol",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative corruption protocol",
    )
    require_canonical(
        adapter,
        "strict_v4_selected_system_downstream_adapter_design_v1",
        "selected-system adapter design",
    )
    source_values = {
        "classic_main_protocol": (classic_protocol_path, classic),
        "krc_source_protocol": (confirmation_protocol_path, confirmation),
        "absolute_corruption_protocol": (absolute_protocol_path, absolute),
        "comparative_corruption_protocol": (
            comparative_protocol_path,
            comparative,
        ),
        "selected_system_adapter_design": (adapter_design_path, adapter),
    }
    for name, (path, value) in source_values.items():
        validate_bound_source(
            name=name, path=path, value=value, design=design
        )
    selected = activation.get("selected_algorithm")
    snapshot = activation.get("selection_snapshot", {})
    if (
        activation.get("execution_admitted") is not True
        or selected not in ALGORITHMS
        or snapshot.get("selected_algorithm") != selected
        or activation.get("selection_snapshot_sha256")
        != canonical_hash(snapshot)
        or activation.get("input_manifest_sha256", {}).get(
            "preconfirmation_design"
        )
        != design["manifest_sha256"]
        or design.get("allowed_selected_algorithms") != list(ALGORITHMS)
        or classic.get("main_table", {}).get("method_order")
        != list(MAIN_METHODS)
        or comparative.get("corruption_conditions", {}).get("families")
        != list(CORRUPTION_FAMILIES)
    ):
        raise ValueError("preconfirmation activation or universe drifted")
    counts = formal_output_counts(run_root, result_root)
    if any(counts.values()):
        raise ValueError("preconfirmation protocol requires zero formal results")
    sources = build_sources(confirmation, confirmation_capture_root)
    tasks = [
        {
            "dataset": source["suite"],
            "unknown_attack_family": source["scenario"],
            "training_seed": int(source["training_seed"]),
            "validation_profile_seed": int(source["corruption_seed"]),
        }
        for source in sources
    ]
    implementation = {}
    for relative in (*IMPLEMENTATION_FILES, *DEPENDENCY_FILES):
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        implementation[relative] = file_hash(path)
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "frozen_after_final_selection_before_preconfirmation_execution",
        "execution_admitted": True,
        "selected_algorithm": selected,
        "selection_snapshot": snapshot,
        "selection_snapshot_sha256": activation["selection_snapshot_sha256"],
        "sources": sources,
        # The existing RRC materializer consumes this compatibility name.
        "source_model_pairs": sources,
        "source_count": 306,
        "scenario_block_count": 102,
        "suite_count": 7,
        "training_seeds": [647, 653, 659],
        "candidate_training": {
            "fresh_refit_per_source_split": True,
            "external_test_data_excluded": True,
            "pairwise_runtime_policy": pairwise_policy(selected),
            "robust_runtime_policy": {
                "augmentation_weight": 0.5,
                "training_sample_fraction": 0.25,
                "health_quantile": 0.99,
            },
            "rrc_backend_protocol": (
                rrc_protocol(tasks)
                if selected == "rrc_csr_caeos_v1"
                else None
            ),
        },
        "opendetect_training": {
            **opendetect_policy(),
            "fresh_refit_per_source_split": True,
            "training_seed_equals_source_training_seed": True,
            "external_test_data_excluded": True,
        },
        "classic_main_gate": {
            "methods": list(MAIN_METHODS),
            "metrics": list(
                design["clean_main_baseline_contract"]["metrics"]
            ),
            "metric_direction": {
                "known_macro_f1": "higher",
                "unknown_auroc": "higher",
                "unknown_aupr": "higher",
                "unknown_fpr95": "lower",
                "oscr": "higher",
            },
            "strict_five_metric_dominance_against_all_seven": True,
            "same_source_split_and_training_seed": True,
            "mahalanobis_pp_recomputed_from_same_fresh_mlp_run": True,
            "opendetect_freshly_refit": True,
        },
        "selective_sota_claim_ladder": {
            "frozen_before_results": True,
            "unknown_detection": {
                "metrics": [
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                ],
                "comparators": list(MAIN_METHODS),
                "strict_seven_suite_equal_weight_win": True,
                "scenario_bootstrap_95ci_lower_strictly_positive": True,
                "all_seven_suite_oriented_deltas_nonnegative": True,
                "known_macro_f1_maximum_degradation": 0.01,
                "oscr_reported_but_not_gating": True,
            },
            "corruption_robustness_vs_opendetect": {
                "requires_absolute_five_family_gate": True,
                "requires_comparative_five_family_gate": True,
            },
            "result_dependent_metric_or_comparator_selection_forbidden": True,
            "selective_claim_does_not_authorize_comprehensive_sota": True,
        },
        "corruption": {
            "families": list(CORRUPTION_FAMILIES),
            "fixed_severity": design["corruption_contract"][
                "fixed_severity"
            ],
            "modality_selection_rule": design["corruption_contract"][
                "modality_selection_rule"
            ],
            "coverage_manifest_sha256": comparative[
                "coverage_manifest_sha256"
            ],
            "absolute_maximum_mean_degradation": design[
                "corruption_contract"
            ]["absolute_maximum_mean_degradation"],
            "comparative_gate": design["corruption_contract"][
                "comparative_gate"
            ],
            "metric_direction": {
                "known_macro_f1": "higher",
                "unknown_auroc": "higher",
                "unknown_aupr": "higher",
                "unknown_fpr95": "lower",
                "oscr": "higher",
                "ece": "lower",
            },
            "same_condition_rng_and_test_identity": True,
            "no_threshold_tuning_or_condition_selection": True,
        },
        "aggregation": {
            **design["aggregation_contract"],
            "bootstrap_seed": 20260728,
        },
        "resource_contract": {
            "environment_gate": (
                "SELECTED_SYSTEM_PRECONFIRMATION_EXCLUSIVE_MACHINE_GATE=passed"
            ),
            "candidate_capture_outer_workers": 1,
            "candidate_fit_jobs_per_worker": 1,
            "opendetect_capture_outer_workers": 1,
            "mahalanobis_pp_outer_workers": 1,
            "evaluation_outer_workers": 1,
            "subprocess_prefix": ["ionice", "-c", "3", "nice", "-n", "19"],
            "all_training_and_evaluation_on_same_host": True,
        },
        "run_root": run_root.resolve().as_posix(),
        "output_counts_at_freeze": counts,
        "input_manifest_sha256": {
            "activation": activation["manifest_sha256"],
            "design": design["manifest_sha256"],
            **{
                name: value["manifest_sha256"]
                for name, (_path, value) in source_values.items()
            },
        },
        "input_file_sha256": {
            "activation": file_hash(activation_path),
            "design": file_hash(design_path),
            **{
                name: file_hash(path)
                for name, (path, _value) in source_values.items()
            },
        },
        "implementation_sha256": dict(sorted(implementation.items())),
        "claim_boundary": {
            "selected_algorithm_identity_splicing_forbidden": True,
            "pairwise_evidence_cannot_substitute_for_nonpairwise_selection": True,
            "negative_gate_result_is_reportable": True,
            "completion_requires_integrity_but_effect_gates_remain_boolean": True,
            "comprehensive_sota_requires_all_three_effect_gates": True,
            "selective_sota_requires_its_frozen_claim_gate": True,
            "selective_sota_must_name_scope_metrics_and_comparators": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("runs/strict_v4_selected_system_preconfirmation_v1"),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path("results/strict_v4_selected_system_preconfirmation_v1"),
    )
    parser.add_argument(
        "--activation",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_preconfirmation_v1/"
            "activation.json"
        ),
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_preconfirmation_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--classic-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_classical_main_baseline_protocol_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument(
        "--confirmation-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_krc_csr_confirmation_protocol_v1/protocol.json"
        ),
    )
    parser.add_argument(
        "--confirmation-capture-root",
        type=Path,
        default=Path("runs/strict_v4_krc_csr_confirmation_v1/captures"),
    )
    parser.add_argument(
        "--absolute-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_postselection_corruption_suite_gate_seed7/"
            "protocol_manifest.json"
        ),
    )
    parser.add_argument(
        "--comparative-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_comparative_corruption_protocol/"
            "protocol_manifest_v2.json"
        ),
    )
    parser.add_argument(
        "--adapter-design",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_preconfirmation_v1/"
            "protocol.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else (root / path).resolve()

    output = resolve(args.output)
    if output.is_file():
        existing = load(output)
        require_canonical(existing, SCHEMA, "preconfirmation protocol")
        print(
            json.dumps(
                {
                    "state": "existing_protocol_retained",
                    "selected_algorithm": existing["selected_algorithm"],
                    "manifest_sha256": existing["manifest_sha256"],
                },
                sort_keys=True,
            )
        )
        return
    activation = resolve(args.activation)
    if not activation.is_file():
        print(
            json.dumps(
                {
                    "state": "pending_preconfirmation_activation",
                    "protocol_written": False,
                },
                sort_keys=True,
            )
        )
        return
    value = build_protocol(
        project_root=root,
        run_root=resolve(args.run_root),
        result_root=resolve(args.result_root),
        activation_path=activation,
        design_path=resolve(args.design),
        classic_protocol_path=resolve(args.classic_protocol),
        confirmation_protocol_path=resolve(args.confirmation_protocol),
        confirmation_capture_root=resolve(args.confirmation_capture_root),
        absolute_protocol_path=resolve(args.absolute_protocol),
        comparative_protocol_path=resolve(args.comparative_protocol),
        adapter_design_path=resolve(args.adapter_design),
    )
    write_json(output, value)
    print(
        json.dumps(
            {
                "state": value["state"],
                "selected_algorithm": value["selected_algorithm"],
                "manifest_sha256": value["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
