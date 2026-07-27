from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"
SELECTION_SEEDS = (311, 313)
ROBUSTNESS_SEEDS = (311, 313, 317)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def require_file(path: Path, expected_sha256: str, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    actual = file_hash(path)
    if actual != expected_sha256:
        raise ValueError(f"{label} SHA mismatch: {path}")
    return actual


def hash_existing_file(path: Path, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    return file_hash(path)


def identity(record: dict[str, Any], seed_key: str) -> tuple[str, str, int]:
    return (
        str(record["suite"]),
        str(record["scenario"]),
        int(record[seed_key]),
    )


def indexed_unique(
    records: list[dict[str, Any]], seed_key: str, label: str
) -> dict[tuple[str, str, int], dict[str, Any]]:
    output: dict[tuple[str, str, int], dict[str, Any]] = {}
    for record in records:
        key = identity(record, seed_key)
        if key in output:
            raise ValueError(f"duplicate {label} identity: {key}")
        output[key] = record
    return output


def validate_authorization(
    *,
    design: dict[str, Any],
    preparation: dict[str, Any],
    selection: dict[str, Any],
    vgrf_protocol: dict[str, Any],
    vgrf_summary: dict[str, Any],
    reconfirmation_protocol: dict[str, Any],
    reconfirmation_summary: dict[str, Any],
    corruption_protocol: dict[str, Any],
) -> None:
    require_canonical(
        design,
        "strict_v4_vgrf_selected_system_confirmation_design_v1",
        "VGRF selected-system design",
    )
    require_canonical(
        preparation,
        "strict_v4_vgrf_selected_system_preparation_protocol_v1",
        "VGRF selected-system preparation",
    )
    require_canonical(
        selection,
        "strict_v4_final_self_algorithm_selection_v1",
        "final self-algorithm selection",
    )
    require_canonical(
        vgrf_protocol,
        "strict_v4_vgrf_confirmation_protocol_v1",
        "VGRF confirmation protocol",
    )
    require_canonical(
        vgrf_summary,
        "strict_v4_vgrf_confirmation_summary_v1",
        "VGRF confirmation summary",
    )
    require_canonical(
        reconfirmation_protocol,
        "strict_v4_selected_external_reconfirmation_protocol_v1",
        "selected external reconfirmation protocol",
    )
    require_canonical(
        reconfirmation_summary,
        "strict_v4_selected_external_reconfirmation_summary_v1",
        "selected external reconfirmation summary",
    )
    require_canonical(
        corruption_protocol,
        "strict_v4_postselection_corruption_protocol_v1",
        "post-selection corruption protocol",
    )
    if preparation.get("design_manifest_sha256") != design["manifest_sha256"]:
        raise ValueError("preparation/design binding mismatch")
    if (
        design.get("input_manifest_sha256", {}).get("corruption")
        != corruption_protocol["manifest_sha256"]
    ):
        raise ValueError("design/corruption protocol binding mismatch")
    if (
        selection.get("selected_algorithm") != VGRF
        or selection.get("vgrf_confirmation_passes") is not True
    ):
        raise ValueError("positive final VGRF selection is required")
    if (
        vgrf_summary.get("selected_algorithm") != VGRF
        or vgrf_summary.get("passes") is not True
        or selection.get("confirmation_summary_manifest_sha256")
        != vgrf_summary["manifest_sha256"]
        or vgrf_summary.get("protocol_manifest_sha256")
        != vgrf_protocol["manifest_sha256"]
    ):
        raise ValueError("VGRF selection/confirmation binding mismatch")
    if (
        reconfirmation_protocol.get("selected_algorithm") != VGRF
        or reconfirmation_protocol.get("input_manifest_sha256", {}).get(
            "final_selection"
        )
        != selection["manifest_sha256"]
        or reconfirmation_protocol.get("input_manifest_sha256", {}).get(
            "vgrf_protocol"
        )
        != vgrf_protocol["manifest_sha256"]
        or reconfirmation_protocol.get("input_manifest_sha256", {}).get(
            "vgrf_summary"
        )
        != vgrf_summary["manifest_sha256"]
    ):
        raise ValueError("external reconfirmation input binding mismatch")
    if (
        reconfirmation_summary.get("protocol_manifest_sha256")
        != reconfirmation_protocol["manifest_sha256"]
        or reconfirmation_summary.get("selected_algorithm") != VGRF
        or reconfirmation_summary.get("validation", {}).get("passes")
        is not True
        or type(
            reconfirmation_summary.get("decision", {}).get("passes")
        )
        is not bool
    ):
        raise ValueError(
            "structurally valid selected external reconfirmation is required"
        )


def build_source_plan(
    *,
    project_root: Path,
    vgrf_protocol: dict[str, Any],
    reconfirmation_protocol: dict[str, Any],
    comparator_root: Path,
    source_run_root: Path,
    deployment_root: Path,
) -> list[dict[str, Any]]:
    inputs = vgrf_protocol["confirmation"]["inputs"]
    vgrf_index = indexed_unique(inputs, "training_seed", "VGRF input")
    source_registry = reconfirmation_protocol["source_registry"]
    reconfirmation_index = indexed_unique(
        source_registry, "seed", "reconfirmation source"
    )
    expected = {
        (
            str(record["suite"]),
            str(record["scenario"]),
            seed,
        )
        for record in design_scenarios(vgrf_protocol)
        for seed in SELECTION_SEEDS
    }
    if set(vgrf_index) != expected or set(reconfirmation_index) != expected:
        raise ValueError("selected-system source identity coverage mismatch")

    plan: list[dict[str, Any]] = []
    scenario_templates: dict[
        tuple[str, str], tuple[dict[str, Any], Path, str]
    ] = {}
    for key in sorted(expected):
        suite, scenario, seed = key
        item = vgrf_index[key]
        source = reconfirmation_index[key]
        if (
            Path(source["candidate_root"]).name
            != f"{scenario}_seed{seed}"
            or Path(source["reference_root"]).name
            != f"{scenario}_seed{seed}"
        ):
            raise ValueError(f"source path identity mismatch: {key}")
        candidate_root = Path(source["candidate_root"])
        reference_root = Path(source["reference_root"])
        source_paths = {
            "vgrf_metrics": candidate_root / "metrics.json",
            "vgrf_scores": candidate_root / "scores.npz",
            "pairwise_metrics": reference_root / "metrics.json",
            "pairwise_scores": reference_root / "scores.npz",
            "pairwise_evidence_package": (
                reference_root / "evidence_package.npz"
            ),
            "pairwise_provenance": reference_root / "provenance.json",
        }
        registry_names = {
            "vgrf_metrics": "candidate_metrics",
            "vgrf_scores": "candidate_scores",
            "pairwise_metrics": "reference_metrics",
            "pairwise_scores": "reference_scores",
            "pairwise_evidence_package": "reference_evidence_package",
            "pairwise_provenance": "reference_provenance",
        }
        source_hashes = {
            name: require_file(
                path,
                source["source_file_sha256"][registry_names[name]],
                name,
            )
            for name, path in source_paths.items()
        }
        vgrf_metrics = load(source_paths["vgrf_metrics"])
        if (
            vgrf_metrics.get("protocol_manifest_sha256")
            != vgrf_protocol["manifest_sha256"]
            or vgrf_metrics.get("diagnostics", {}).get(
                "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
            )
            is not False
        ):
            raise ValueError(f"VGRF source binding or leakage failure: {key}")
        if (
            vgrf_metrics.get("input_sha256", {}).get("scores")
            != source_hashes["pairwise_scores"]
            or vgrf_metrics.get("input_sha256", {}).get("evidence_package")
            != source_hashes["pairwise_evidence_package"]
        ):
            raise ValueError(f"VGRF source input binding mismatch: {key}")

        comparator_dir = (
            comparator_root / suite / f"{scenario}_seed{seed}_opendetect"
        )
        comparator_paths = {
            "opendetect_metrics": comparator_dir / "metrics.json",
            "opendetect_scores": comparator_dir / "scores.npz",
            "opendetect_provenance": comparator_dir / "provenance.json",
            "opendetect_model": comparator_dir / "model.pt",
        }
        comparator_hashes = {
            name: hash_existing_file(path, name)
            for name, path in comparator_paths.items()
        }
        comparator_metrics = load(comparator_paths["opendetect_metrics"])
        if (
            comparator_metrics.get("model") != "opendetect"
            or comparator_metrics.get("selection_evidence", {}).get(
                "unknown_or_test_labels_used_for_fitting_or_selection"
            )
            is not False
        ):
            raise ValueError(f"OpenDetect source binding or leakage failure: {key}")
        pairwise_metrics = load(source_paths["pairwise_metrics"])
        candidate_fingerprint = pairwise_metrics["split_metadata"][
            "split_fingerprint"
        ]["combined"]
        comparator_fingerprint = comparator_metrics["split_metadata"][
            "split_fingerprint"
        ]["combined"]
        if candidate_fingerprint != comparator_fingerprint:
            raise ValueError(f"OpenDetect split mismatch: {key}")

        relative_config = Path(str(item["config"]))
        config_path = (
            relative_config
            if relative_config.is_absolute()
            else project_root / relative_config
        )
        csv_path = Path(str(item["csv"]))
        require_file(csv_path, str(item["csv_sha256"]), "source CSV")
        require_file(config_path, str(item["config_sha256"]), "source config")
        provenance_path = project_root / str(item["source_provenance"])
        require_file(
            provenance_path,
            str(item["source_provenance_sha256"]),
            "source provenance",
        )
        if seed == SELECTION_SEEDS[0]:
            scenario_templates[(suite, scenario)] = (
                item,
                comparator_paths["opendetect_provenance"],
                comparator_hashes["opendetect_provenance"],
            )
        pair_root = deployment_root / suite / f"{scenario}_seed{seed}"
        plan.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "source_mode": "frozen_selection_artifacts",
                "source_roots": {
                    "vgrf": str(candidate_root.resolve()),
                    "pairwise": str(reference_root.resolve()),
                    "opendetect": str(comparator_dir.resolve()),
                },
                "source_file_sha256": {
                    **source_hashes,
                    **comparator_hashes,
                    "csv": str(item["csv_sha256"]),
                    "config": str(item["config_sha256"]),
                    "source_provenance": str(
                        item["source_provenance_sha256"]
                    ),
                },
                "split_fingerprint": candidate_fingerprint,
                "deployment_output_roots": deployment_output_roots(pair_root),
                "pairwise_capture_requires_deterministic_retraining": True,
                "scores_only_inference_forbidden": True,
            }
        )

    if len(scenario_templates) != 102:
        raise ValueError("expected one seed-317 template for 102 scenarios")
    for (suite, scenario), template_value in sorted(
        scenario_templates.items()
    ):
        template, comparator_provenance, comparator_provenance_sha = (
            template_value
        )
        seed = 317
        run_root = source_run_root / suite / f"{scenario}_seed{seed}"
        if any(run_root.rglob("*")):
            raise ValueError(
                f"seed-317 source output exists before freeze: {run_root}"
            )
        pair_root = deployment_root / suite / f"{scenario}_seed{seed}"
        plan.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "source_mode": "preregistered_seed317_execution",
                "source_inputs": {
                    "csv": str(template["csv"]),
                    "csv_sha256": str(template["csv_sha256"]),
                    "config": str(template["config"]),
                    "config_sha256": str(template["config_sha256"]),
                    "unknown_classes": str(template["unknown_classes"]),
                    "source_provenance": str(template["source_provenance"]),
                    "source_provenance_sha256": str(
                        template["source_provenance_sha256"]
                    ),
                    "source_parameter_fingerprint": str(
                        template["source_parameter_fingerprint"]
                    ),
                    "opendetect_source_provenance": str(
                        comparator_provenance.resolve()
                    ),
                    "opendetect_source_provenance_sha256": (
                        comparator_provenance_sha
                    ),
                },
                "run_output_roots": {
                    "pairwise": str((run_root / "pairwise").resolve()),
                    "vgrf": str((run_root / "vgrf").resolve()),
                    "opendetect": str((run_root / "opendetect").resolve()),
                },
                "deployment_output_roots": deployment_output_roots(pair_root),
                "pairwise_capture_requires_deterministic_retraining": True,
                "scores_only_inference_forbidden": True,
            }
        )
    if len(plan) != 306:
        raise ValueError(f"expected 306 source pairs, got {len(plan)}")
    if {identity(item, "seed") for item in plan} != {
        (suite, scenario, seed)
        for suite, scenario in scenario_templates
        for seed in ROBUSTNESS_SEEDS
    }:
        raise ValueError("306-source plan identity mismatch")
    return plan


def design_scenarios(
    vgrf_protocol: dict[str, Any],
) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    output: list[dict[str, str]] = []
    for item in vgrf_protocol["confirmation"]["inputs"]:
        key = (str(item["suite"]), str(item["scenario"]))
        if key not in seen:
            seen.add(key)
            output.append({"suite": key[0], "scenario": key[1]})
    if len(output) != 102:
        raise ValueError("VGRF protocol must cover 102 scenarios")
    return output


def deployment_output_roots(root: Path) -> dict[str, str]:
    return {
        "pairwise_capture": str((root / "pairwise_capture").resolve()),
        "pairwise_audit": str((root / "pairwise_audit.json").resolve()),
        "vgrf_capture": str((root / "vgrf_capture").resolve()),
        "vgrf_audit": str((root / "vgrf_audit.json").resolve()),
        "opendetect_capture": str((root / "opendetect_capture").resolve()),
        "opendetect_audit": str((root / "opendetect_audit.json").resolve()),
    }


def create_execution_protocol(
    *,
    project_root: Path,
    design: dict[str, Any],
    preparation: dict[str, Any],
    selection: dict[str, Any],
    vgrf_protocol: dict[str, Any],
    vgrf_summary: dict[str, Any],
    reconfirmation_protocol: dict[str, Any],
    reconfirmation_summary: dict[str, Any],
    corruption_protocol: dict[str, Any],
    comparator_root: Path,
    source_run_root: Path,
    deployment_root: Path,
    source_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_system_outputs: int,
) -> dict[str, Any]:
    validate_authorization(
        design=design,
        preparation=preparation,
        selection=selection,
        vgrf_protocol=vgrf_protocol,
        vgrf_summary=vgrf_summary,
        reconfirmation_protocol=reconfirmation_protocol,
        reconfirmation_summary=reconfirmation_summary,
        corruption_protocol=corruption_protocol,
    )
    if observed_system_outputs != 0:
        raise ValueError("execution protocol must freeze before system outputs")
    source_plan = build_source_plan(
        project_root=project_root,
        vgrf_protocol=vgrf_protocol,
        reconfirmation_protocol=reconfirmation_protocol,
        comparator_root=comparator_root,
        source_run_root=source_run_root,
        deployment_root=deployment_root,
    )
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_execution_protocol_v1"
        ),
        "status": (
            "frozen_after_positive_vgrf_and_completed_external_confirmation_"
            "before_seed317_and_system_outputs"
        ),
        "project_root": str(project_root.resolve()),
        "selected_algorithm": VGRF,
        "design_manifest_sha256": design["manifest_sha256"],
        "preparation_protocol_manifest_sha256": preparation[
            "manifest_sha256"
        ],
        "final_selection_manifest_sha256": selection["manifest_sha256"],
        "vgrf_confirmation_protocol_manifest_sha256": vgrf_protocol[
            "manifest_sha256"
        ],
        "vgrf_confirmation_summary_manifest_sha256": vgrf_summary[
            "manifest_sha256"
        ],
        "selected_external_reconfirmation_protocol_manifest_sha256": (
            reconfirmation_protocol["manifest_sha256"]
        ),
        "selected_external_reconfirmation_summary_manifest_sha256": (
            reconfirmation_summary["manifest_sha256"]
        ),
        "source_registry": source_plan,
        "source_pair_count": 306,
        "source_pair_formula": "102_scenarios_x_seeds_311_313_317",
        "selection_source_pair_count": 204,
        "preregistered_seed317_source_pair_count": 102,
        "execution_order": [
            "run_seed317_pairwise_vgrf_and_opendetect_sources",
            "capture_and_independently_audit_pairwise_vgrf_opendetect_bundles",
            "verify_exact_probability_prediction_risk_rejection_equivalence",
            "benchmark_full_forward_and_risk_transform_on_exclusive_hardware",
            "run_1530_paired_corruption_conditions",
            "summarize_without_metric_or_suite_splicing",
        ],
        "deployment_contract": {
            "pairwise_historical_scores_are_not_a_deployment_bundle": True,
            "pairwise_deterministic_retraining_and_capture_required": True,
            "vgrf_must_wrap_the_audited_pairwise_bundle": True,
            "opendetect_full_model_capture_and_replay_audit_required": True,
            "scores_npz_only_postprocessing_is_not_model_inference": True,
            "all_three_methods_use_identical_split_and_processed_rows": True,
        },
        "vgrf_known_only_parameters": vgrf_protocol[
            "known_only_parameters"
        ],
        "runtime_equivalence_and_efficiency": design[
            "runtime_equivalence_and_efficiency"
        ],
        "training_calibration_efficiency": design[
            "training_calibration_efficiency"
        ],
        "comparative_corruption": design["comparative_corruption"],
        "candidate_graceful_degradation_thresholds": corruption_protocol[
            "confirmatory_graceful_degradation_gate"
        ]["maximum_mean_degradation"],
        "coverage_manifest_sha256": design["input_manifest_sha256"][
            "coverage"
        ],
        "required_output": design["required_output"],
        "claim_boundary": {
            **design["claim_boundary"],
            "external_accuracy_reconfirmation_passed_before_system_work": (
                reconfirmation_summary["decision"]["passes"]
            ),
            "negative_external_accuracy_result_is_preserved": True,
            "execution_protocol_contains_no_effect_metrics": True,
        },
        "input_file_sha256": source_file_sha256,
        "implementation_sha256": implementation_sha256,
        "system_outputs_observed_at_freeze": 0,
        "seed317_outputs_observed_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def count_outputs(roots: list[Path]) -> int:
    names = {
        "metrics.json",
        "capture_manifest.json",
        "benchmark.json",
        "paired_corruption.json",
        "summary.json",
    }
    return sum(
        1
        for root in roots
        if root.exists()
        for path in root.rglob("*")
        if path.is_file() and path.name in names
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--final-selection", type=Path, required=True)
    parser.add_argument("--vgrf-protocol", type=Path, required=True)
    parser.add_argument("--vgrf-summary", type=Path, required=True)
    parser.add_argument(
        "--selected-external-protocol", type=Path, required=True
    )
    parser.add_argument(
        "--selected-external-summary", type=Path, required=True
    )
    parser.add_argument(
        "--corruption-protocol", type=Path, required=True
    )
    parser.add_argument("--comparator-root", type=Path, required=True)
    parser.add_argument("--seed317-run-root", type=Path, required=True)
    parser.add_argument("--deployment-root", type=Path, required=True)
    parser.add_argument("--benchmark-root", type=Path, required=True)
    parser.add_argument("--corruption-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument(
        "--implementation", type=Path, action="append", required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "design": args.design,
        "preparation": args.preparation,
        "final_selection": args.final_selection,
        "vgrf_protocol": args.vgrf_protocol,
        "vgrf_summary": args.vgrf_summary,
        "selected_external_protocol": args.selected_external_protocol,
        "selected_external_summary": args.selected_external_summary,
        "corruption_protocol": args.corruption_protocol,
    }
    implementations = [Path(__file__).resolve(), *args.implementation]
    names = [path.name for path in implementations]
    if len(set(names)) != len(names):
        raise ValueError("implementation filenames must be unique")
    observed = count_outputs(
        [
            args.seed317_run_root,
            args.deployment_root,
            args.benchmark_root,
            args.corruption_root,
            args.result_root,
        ]
    )
    value = create_execution_protocol(
        project_root=args.project_root.resolve(),
        design=load(args.design),
        preparation=load(args.preparation),
        selection=load(args.final_selection),
        vgrf_protocol=load(args.vgrf_protocol),
        vgrf_summary=load(args.vgrf_summary),
        reconfirmation_protocol=load(args.selected_external_protocol),
        reconfirmation_summary=load(args.selected_external_summary),
        corruption_protocol=load(args.corruption_protocol),
        comparator_root=args.comparator_root,
        source_run_root=args.seed317_run_root,
        deployment_root=args.deployment_root,
        source_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        implementation_sha256={
            path.name: file_hash(path) for path in implementations
        },
        observed_system_outputs=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
