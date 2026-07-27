from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def option_value(arguments: List[str], option: str) -> str:
    try:
        return arguments[arguments.index(option) + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"source command lacks {option}") from error


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
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            source = registry.get((suite, scenario, 137))
            if source is None:
                raise ValueError(f"missing seed137 source: {suite}/{scenario}")
            root = Path(source["candidate_root"])
            provenance_path = root / "provenance.json"
            provenance = load_json(provenance_path)
            command = list(provenance["command"])
            if Path(command[1]).name != "train_hybrid_open_set.py":
                raise ValueError("CSR source must use frozen Pairwise trainer")
            arguments = command[2:]
            if (
                option_value(arguments, "--test-corruption-kind") != "none"
                or int(option_value(arguments, "--seed")) != 137
            ):
                raise ValueError("CSR source is not a clean seed137 run")
            csv_path = Path(option_value(arguments, "--csv"))
            config_path = Path(option_value(arguments, "--config"))
            if not config_path.is_absolute():
                config_path = project_root / config_path
            records.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "source_seed": 137,
                    "candidate_source_root": str(root),
                    "candidate_source_provenance_sha256": file_hash(
                        provenance_path
                    ),
                    "csv": str(csv_path),
                    "csv_sha256": file_hash(csv_path),
                    "config": str(config_path),
                    "config_sha256": file_hash(config_path),
                    "base_trainer_arguments": arguments,
                    "fresh_training_seed": int(
                        design["development"]["training_seed"]
                    ),
                    "source_effect_metrics_used_for_selection": False,
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
        design.get("schema_version") != "strict_v4_csr_caeos_design_v4"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical CSR v4 design required")
    if (
        comparative.get("schema_version")
        != "strict_v4_comparative_corruption_protocol_v2"
        or comparative.get("manifest_sha256")
        != canonical_hash(comparative)
    ):
        raise ValueError("canonical comparative v2 protocol required")
    if any(int(value) != 0 for value in observed_counts.values()):
        raise ValueError("CSR protocol requires a zero-output root")
    expected = {
        (suite, scenario)
        for suite, scenarios in design["development"]["scenarios"].items()
        for scenario in scenarios
    }
    observed = {
        (record["suite"], record["scenario"]) for record in source_records
    }
    if observed != expected or len(source_records) != 14:
        raise ValueError("CSR source registry must cover 14 scenarios")
    required = {
        "clean_trainer",
        "robust_trainer",
        "capture",
        "evaluator",
        "runner",
        "summarizer",
        "auditor",
        "watcher",
    }
    if (
        set(implementation) != required
        or set(implementation_sha256) != required
    ):
        raise ValueError("complete CSR execution implementation required")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "execution_admitted": True,
        "algorithm": "csr_caeos_v1",
        "design_path": design_path,
        "design_manifest_sha256": design["manifest_sha256"],
        "input_file_sha256": {
            "design": design_file_sha256,
            "comparative_protocol": comparative_file_sha256,
        },
        "comparative_protocol_manifest_sha256": comparative[
            "manifest_sha256"
        ],
        "source_registry": source_records,
        "source_registry_count": len(source_records),
        "implementation": implementation,
        "implementation_sha256": implementation_sha256,
        "execution_plan": {
            "capture_count": 14,
            "fit_count": 28,
            "fixed_augmentation_weight": 0.5,
            "clean_admission_before_any_test_evaluation": True,
            "pilot_evaluation_count_if_admitted": 84,
            "resumable_by_validated_capture_and_evaluation": True,
            "outer_workers": 1,
            "trainer_jobs": 8,
        },
        "resource_policy": {
            "five_consecutive_idle_samples": True,
            "idle_sample_interval_seconds": 30,
            "nice_level": 19,
            "ionice_class": "idle",
            "no_parallel_csr_training": True,
        },
        "leakage_policy": {
            "known_training_for_model_fit_only": True,
            "even_known_validation_for_health_and_risk_calibration": True,
            "odd_known_validation_for_clean_admission_only": True,
            "unknown_or_test_for_fit_routing_or_admission": False,
            "test_labels_for_final_pilot_evaluation_only": True,
        },
        "output_counts_at_freeze": observed_counts,
        "completion": {
            "positive_capture_count": 14,
            "positive_evaluation_count": 84,
            "summary_and_independent_audit_required": True,
            "clean_rejection_is_terminal_negative_pilot": True,
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
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    design = load_json(design_path)
    comparative = load_json(comparative_path)
    implementation = {}
    implementation_sha256 = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementation[name] = relative
        implementation_sha256[name] = file_hash(project_root / relative)
    observed = {
        "capture_manifests": (
            sum(1 for _ in run_root.rglob("capture_manifest.json"))
            if run_root.exists()
            else 0
        ),
        "evaluations": (
            sum(1 for _ in run_root.rglob("evaluation.json"))
            if run_root.exists()
            else 0
        ),
        "clean_admission": int(
            (result_root / "clean_admission.json").exists()
        ),
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
        "completion": int((result_root / "pilot_complete").exists()),
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
