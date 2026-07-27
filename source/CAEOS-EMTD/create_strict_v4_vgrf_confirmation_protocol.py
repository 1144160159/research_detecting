from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from summarize_strict_v4_validation_gated_reliability_fusion import (
    analyze as analyze_pilot,
)


SEEDS = (311, 313)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def command_value(command: list[str], flag: str) -> str:
    index = command.index(flag)
    return command[index + 1]


def validate_pilot_analysis(
    pilot_protocol: dict[str, Any],
    pilot_analysis: dict[str, Any],
    pilot_run_root: Path,
) -> None:
    if (
        pilot_analysis.get("protocol_manifest_sha256")
        != pilot_protocol["manifest_sha256"]
    ):
        raise ValueError("pilot analysis binding mismatch")
    recomputed = analyze_pilot(pilot_protocol, pilot_run_root)
    if recomputed != pilot_analysis:
        raise ValueError("pilot analysis differs from deterministic recomputation")
    if (
        pilot_analysis.get("passes") is not True
        or pilot_analysis.get("decision")
        != "freeze_seed311_313_full102_confirmation"
    ):
        raise ValueError("VGRF pilot did not authorize confirmation")


def build_inputs(project: Path, coverage: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    source_root = project / "runs/strict_v4_full103_pairwise_caeos_seed7"
    for suite, entry in sorted(coverage["scenario_registry"].items()):
        for scenario in entry["scenarios"]:
            provenance_path = source_root / suite / f"{scenario}_seed7" / "provenance.json"
            provenance = load(provenance_path)
            command = provenance["command"]
            csv_path = Path(command_value(command, "--csv"))
            config_path = project / command_value(command, "--config")
            if file_hash(csv_path) != coverage["cache_artifacts"][suite]["sha256"]:
                raise ValueError(f"coverage cache SHA mismatch: {suite}")
            for seed in SEEDS:
                records.append({
                    "suite": suite,
                    "scenario": scenario,
                    "source_seed": 7,
                    "training_seed": seed,
                    "source_provenance": provenance_path.relative_to(project).as_posix(),
                    "source_provenance_sha256": file_hash(provenance_path),
                    "unknown_classes": command_value(command, "--unknown-classes"),
                    "csv": csv_path.as_posix(),
                    "csv_sha256": file_hash(csv_path),
                    "config": config_path.relative_to(project).as_posix(),
                    "config_sha256": file_hash(config_path),
                    "source_parameter_fingerprint": provenance["parameter_fingerprint"],
                })
    if len(records) != 204:
        raise ValueError(f"expected 204 confirmation inputs, got {len(records)}")
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--pilot-run-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    coverage = load(args.coverage)
    pilot_protocol = load(args.pilot_protocol)
    pilot_analysis = load(args.pilot_analysis)
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage SHA mismatch")
    if pilot_protocol.get("manifest_sha256") != canonical_hash(pilot_protocol):
        raise ValueError("pilot protocol SHA mismatch")
    validate_pilot_analysis(
        pilot_protocol, pilot_analysis, args.pilot_run_root
    )
    reference_metrics = len(list(args.reference_root.rglob("metrics.json"))) if args.reference_root.exists() else 0
    candidate_metrics = len(list(args.candidate_root.rglob("metrics.json"))) if args.candidate_root.exists() else 0
    if reference_metrics or candidate_metrics:
        raise ValueError("confirmation protocol must freeze before confirmation metrics")
    names = (
        "create_strict_v4_vgrf_confirmation_protocol.py",
        "run_strict_v4_vgrf_confirmation_matrix.py",
        "summarize_strict_v4_vgrf_confirmation.py",
        "summarize_strict_v4_validation_gated_reliability_fusion.py",
        "evaluate_validation_gated_reliability_fusion.py",
        "caeos/class_conditional_reliability_fusion.py",
        "caeos/validation_gated_reliability_fusion.py",
        "caeos/vgrf_confirmation_validation.py",
        "train_hybrid_open_set.py",
        "scripts/run_strict_v4_vgrf_confirmation_branch.sh",
        "scripts/wait_and_run_strict_v4_vgrf_confirmation_branch.sh",
    )
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_vgrf_confirmation_protocol_v1",
        "status": "frozen_after_positive_seed307_pilot_before_seed311_313_full102_metrics",
        "candidate": pilot_protocol["candidate"],
        "known_only_parameters": pilot_protocol["known_only_parameters"],
        "confirmation": {
            "seeds": list(SEEDS),
            "suite_count": 7,
            "scenario_count_per_seed": 102,
            "paired_scenario_seed_count": 204,
            "inputs": build_inputs(project, coverage),
            "aggregation": "mean_within_suite_across_scenarios_and_seeds_then_equal_mean_across_seven_suites",
            "bootstrap": {
                "replicates": 10000,
                "seed": 20260723,
                "resampling": "resample_suites_then_scenario_seed_rows_within_suite",
                "primary_endpoint": "equal_suite_four_open_metric_composite_gain",
            },
            "gate": {
                "all_four_equal_suite_oriented_means_strictly_positive": True,
                "primary_bootstrap_lower_bound_strictly_positive": True,
                "minimum_fully_nonregressing_suite_count": 6,
                "minimum_suite_metric_gain": -0.005,
                "minimum_enabled_scenarios": 20,
                "minimum_positive_scenario_composite_count": 120,
                "minimum_mean_known_macro_f1_gain": -0.002,
                "minimum_scenario_known_macro_f1_gain": -0.01,
                "maximum_temperature_reconstruction_error": 1e-10,
                "exact_fallback_for_every_disabled_scenario": True,
            },
        },
        "selection_rule": {
            "if_passes": "select_caeos_validation_gated_reliability_fusion",
            "otherwise": "retain_caeos_pairwise",
            "no_component_or_metric_wise_splicing": True,
        },
        "claim_boundary": {
            "confirmation_does_not_replace_external_dataset_corruption_or_efficiency_gates": True,
            "same_seed7_sample_cache_limits_data_resampling_claim": True,
        },
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_file_sha256": file_hash(args.coverage),
        "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
        "pilot_protocol_file_sha256": file_hash(args.pilot_protocol),
        "pilot_analysis_file_sha256": file_hash(args.pilot_analysis),
        "paired_metrics_observed_at_freeze": {"reference": 0, "candidate": 0},
        "implementation_sha256": {name: file_hash(project / name) for name in names},
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
