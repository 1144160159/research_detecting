from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_medaf_tabular_design import SCHEMA as DESIGN_SCHEMA


SCHEMA = "strict_v4_medaf_tabular_pilot_protocol_v1"
COMPARATIVE_SCHEMA = "strict_v4_comparative_corruption_protocol_v2"
SOURCE_SEED = 137
SHARED_OPTIONS = (
    "--csv",
    "--config",
    "--unknown-classes",
    "--benign-class",
    "--split-strategy",
    "--max-per-class",
)


def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def option_value(arguments: List[str], option: str) -> str:
    try:
        return arguments[arguments.index(option) + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"source command lacks {option}") from error


def validate_source_command(
    provenance: Dict[str, Any],
    *,
    trainer: str,
    model: str | None,
) -> List[str]:
    command = list(provenance.get("command", []))
    if len(command) < 3 or Path(command[1]).name != trainer:
        raise ValueError(f"source command is not {trainer}")
    arguments = command[2:]
    if int(option_value(arguments, "--seed")) != SOURCE_SEED:
        raise ValueError("MEDAF pilot source must use seed137 provenance")
    if model is not None and option_value(arguments, "--model") != model:
        raise ValueError(f"source command is not model={model}")
    if trainer == "train_hybrid_open_set.py":
        if option_value(arguments, "--test-corruption-kind") != "none":
            raise ValueError("candidate source is not a clean run")
        if float(option_value(arguments, "--train-label-noise")) != 0.0:
            raise ValueError("candidate source has training label noise")
    return arguments


def build_source_records(
    design: Dict[str, Any],
    comparative: Dict[str, Any],
    project_root: Path,
) -> List[Dict[str, Any]]:
    registry = {
        (record["suite"], record["scenario"], int(record["seed"])): record
        for record in comparative["source_registry"]
    }
    records = []
    scenarios = design["pilot"]["scenario_selection"]["scenarios"]
    for suite, suite_scenarios in sorted(scenarios.items()):
        for scenario in suite_scenarios:
            source = registry.get((suite, scenario, SOURCE_SEED))
            if source is None:
                raise ValueError(f"missing seed137 source: {suite}/{scenario}")
            candidate_root = Path(source["candidate_root"])
            opendetect_root = Path(source["comparator_root"])
            mlp_root = (
                project_root
                / "runs"
                / "strict_v4_domain_safe_router_confirmation_mlp"
                / suite
                / f"{scenario}_seed{SOURCE_SEED}_mlp"
            )
            provenance_paths = {
                "candidate": candidate_root / "provenance.json",
                "mlp_energy": mlp_root / "provenance.json",
                "opendetect": opendetect_root / "provenance.json",
            }
            provenances = {
                name: load(path) for name, path in provenance_paths.items()
            }
            candidate_arguments = validate_source_command(
                provenances["candidate"],
                trainer="train_hybrid_open_set.py",
                model=None,
            )
            mlp_arguments = validate_source_command(
                provenances["mlp_energy"],
                trainer="train_neural_open_set.py",
                model="mlp",
            )
            opendetect_arguments = validate_source_command(
                provenances["opendetect"],
                trainer="train_neural_open_set.py",
                model="opendetect",
            )
            shared = {
                option: option_value(candidate_arguments, option)
                for option in SHARED_OPTIONS
            }
            for arguments in (mlp_arguments, opendetect_arguments):
                observed = {
                    option: option_value(arguments, option)
                    for option in SHARED_OPTIONS
                }
                if observed != shared:
                    raise ValueError(
                        f"source argument mismatch: {suite}/{scenario}"
                    )
            csv_path = Path(shared["--csv"])
            config_path = Path(shared["--config"])
            if not config_path.is_absolute():
                config_path = project_root / config_path
            records.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "source_seed": SOURCE_SEED,
                    "fresh_training_seed": int(
                        design["pilot"]["training_seed"]
                    ),
                    "shared_arguments": shared,
                    "csv_sha256": file_hash(csv_path),
                    "config_sha256": file_hash(config_path),
                    "source_split_fingerprint": source[
                        "split_fingerprint"
                    ],
                    "source_roots": {
                        "candidate": str(candidate_root),
                        "mlp_energy": str(mlp_root),
                        "opendetect": str(opendetect_root),
                    },
                    "source_provenance_sha256": {
                        name: file_hash(path)
                        for name, path in provenance_paths.items()
                    },
                    "trainer_arguments": {
                        "mlp_energy": mlp_arguments,
                        "opendetect": opendetect_arguments,
                    },
                    "source_csv_rows_reused_without_effect_selection": True,
                }
            )
    return records


def create_protocol(
    design: Dict[str, Any],
    comparative: Dict[str, Any],
    *,
    design_path: str,
    design_file_sha256: str,
    comparative_file_sha256: str,
    source_records: List[Dict[str, Any]],
    implementation: Dict[str, str],
    implementation_sha256: Dict[str, str],
    observed_counts: Dict[str, int],
) -> Dict[str, Any]:
    if (
        design.get("schema_version") != DESIGN_SCHEMA
        or design.get("manifest_sha256") != canonical_hash(design)
        or design["candidate_result_count_at_freeze"] != 0
    ):
        raise ValueError("canonical zero-result MEDAF design required")
    if (
        comparative.get("schema_version") != COMPARATIVE_SCHEMA
        or comparative.get("manifest_sha256") != canonical_hash(comparative)
    ):
        raise ValueError("canonical comparative v2 protocol required")
    if any(int(value) != 0 for value in observed_counts.values()):
        raise ValueError("MEDAF protocol requires zero pilot outputs")
    expected = {
        (suite, scenario)
        for suite, scenarios in design["pilot"]["scenario_selection"][
            "scenarios"
        ].items()
        for scenario in scenarios
    }
    observed = {
        (record["suite"], record["scenario"]) for record in source_records
    }
    if observed != expected or len(source_records) != 14:
        raise ValueError("MEDAF source registry must cover 14 frozen tasks")
    if set(implementation) != set(implementation_sha256):
        raise ValueError("implementation path/hash keys differ")
    value: Dict[str, Any] = {
        "schema_version": SCHEMA,
        "status": "frozen_before_pilot_results",
        "execution_admitted": True,
        "method": "medaf_tabular_adapter",
        "design_path": design_path,
        "design_manifest_sha256": design["manifest_sha256"],
        "comparative_protocol_manifest_sha256": comparative[
            "manifest_sha256"
        ],
        "input_file_sha256": {
            "design": design_file_sha256,
            "comparative_protocol": comparative_file_sha256,
        },
        "source_registry": source_records,
        "source_registry_count": len(source_records),
        "implementation": implementation,
        "implementation_sha256": implementation_sha256,
        "execution_plan": {
            "methods": list(design["pilot"]["methods"]),
            "scenario_count": design["pilot"]["scenario_count"],
            "report_count": design["pilot"]["expected_reports"],
            "fresh_training_seed": design["pilot"]["training_seed"],
            "outer_workers": 1,
            "sequential_training": True,
            "resumable_by_canonical_run_manifest": True,
            "mlp_energy_report_selected_from_fresh_mlp_score_suite": True,
        },
        "resource_policy": {
            "wait_for_comparative_corruption_summary": True,
            "wait_for_mdr_pilot_complete": True,
            "five_consecutive_idle_samples": True,
            "idle_sample_interval_seconds": 30,
            "nice_level": 19,
            "ionice_class": "idle",
        },
        "leakage_policy": {
            "same_csv_and_seed_across_three_methods": True,
            "known_training_for_model_fit_only": True,
            "known_validation_for_checkpoint_or_threshold_only": True,
            "unknown_or_test_labels_for_fit_selection_or_routing": False,
            "test_labels_for_final_metrics_only": True,
        },
        "output_counts_at_freeze": observed_counts,
        "completion": {
            "run_manifest_count": 42,
            "summary_and_independent_audit_required": True,
            "negative_result_writes_complete_marker": True,
            "pilot_does_not_auto_launch_full102": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    design_path = args.design.resolve()
    comparative_path = args.comparative_protocol.resolve()
    design = load(design_path)
    comparative = load(comparative_path)
    implementation = {}
    implementation_sha256 = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        path = project_root / relative
        implementation[name] = relative
        implementation_sha256[name] = file_hash(path)
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    observed = {
        "run_manifests": (
            sum(1 for _ in run_root.rglob("run_manifest.json"))
            if run_root.exists()
            else 0
        ),
        "metrics": (
            sum(1 for _ in run_root.rglob("metrics.json"))
            if run_root.exists()
            else 0
        ),
        "failures": (
            sum(1 for _ in run_root.rglob("failure.json"))
            if run_root.exists()
            else 0
        ),
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
    }
    value = create_protocol(
        design,
        comparative,
        design_path=str(design_path.relative_to(project_root)),
        design_file_sha256=file_hash(design_path),
        comparative_file_sha256=file_hash(comparative_path),
        source_records=build_source_records(
            design, comparative, project_root
        ),
        implementation=implementation,
        implementation_sha256=implementation_sha256,
        observed_counts=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
