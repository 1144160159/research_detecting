from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_mdr_caeos_confirmation_protocol import option_value


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def verify_implementation(
    project_root: Path, relatives: Iterable[str]
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing MDR PARROT implementation: {relative}"
            )
        output[relative] = file_hash(path)
    for relative in (
        "capture_mdr_caeos_runtime.py",
        "train_hybrid_open_set.py",
        "train_mdr_caeos_open_set.py",
        "caeos/mdr_runtime.py",
        "caeos/open_detect_runtime.py",
    ):
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing frozen runtime dependency: {relative}"
            )
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def build_source_records(
    *,
    comparative: Dict[str, Any],
    project_root: Path,
    comparative_run_root: Path,
) -> list[Dict[str, Any]]:
    records = []
    sources = [
        item
        for item in comparative["source_registry"]
        if str(item["suite"]) == "ustc_tfc2016"
    ]
    for source in sorted(
        sources, key=lambda item: (item["scenario"], int(item["seed"]))
    ):
        scenario = str(source["scenario"])
        seed = int(source["seed"])
        candidate_root = Path(source["candidate_root"])
        provenance_path = candidate_root / "provenance.json"
        provenance = load(provenance_path)
        command = list(provenance["command"])
        if (
            len(command) < 3
            or Path(command[1]).name != "train_hybrid_open_set.py"
        ):
            raise ValueError("MDR PARROT source must use Pairwise trainer")
        arguments = command[2:]
        if (
            int(option_value(arguments, "--seed")) != seed
            or option_value(arguments, "--test-corruption-kind") != "none"
        ):
            raise ValueError("MDR PARROT requires clean matched source seeds")
        csv_path = Path(option_value(arguments, "--csv"))
        config_path = Path(option_value(arguments, "--config"))
        if not config_path.is_absolute():
            config_path = project_root / config_path
        block_root = (
            comparative_run_root
            / "blocks"
            / "ustc_tfc2016"
            / scenario
            / f"seed{seed}"
        )
        paired_path = block_root / "paired_corruption.json"
        paired = load(paired_path)
        comparator_capture = block_root / "comparator_capture"
        comparator_manifest_path = (
            comparator_capture / "capture_manifest.json"
        )
        comparator_manifest = load(comparator_manifest_path)
        comparator_artifact = comparator_capture / comparator_manifest[
            "deployment_artifact"
        ]
        comparator_metrics_path = (
            Path(source["comparator_root"]) / "metrics.json"
        )
        comparator_metrics = load(comparator_metrics_path)
        threshold = float(
            comparator_metrics["validation_thresholds"]["opendetect"]
        )
        if (
            paired.get("schema_version")
            != "strict_v4_comparative_corruption_block_v1"
            or paired.get("manifest_sha256") != canonical_hash(paired)
            or paired.get("protocol_manifest_sha256")
            != comparative["manifest_sha256"]
            or paired.get("suite") != "ustc_tfc2016"
            or paired.get("scenario") != scenario
            or int(paired.get("seed", -1)) != seed
            or paired.get("source_split_fingerprint")
            != source["split_fingerprint"]
            or paired.get("candidate_comparator_input_arrays_equal")
            is not True
            or paired.get(
                "unknown_or_test_labels_used_for_fitting_selection_or_"
                "corruption_generation"
            )
            is not False
            or comparator_manifest.get("schema_version")
            != "strict_v4_opendetect_runtime_capture_v1"
            or comparator_manifest.get("equivalence", {}).get("passes")
            is not True
            or not comparator_artifact.is_file()
            or file_hash(comparator_artifact)
            != comparator_manifest["deployment_artifact_sha256"]
            or not (0.0 < threshold < float("inf"))
        ):
            raise ValueError(
                f"invalid comparative source for MDR PARROT: {scenario}/{seed}"
            )
        records.append(
            {
                "suite": "ustc_tfc2016",
                "scenario": scenario,
                "training_seed": seed,
                "augmentation_seed": seed,
                "validation_corruption_seed": 20260724 + seed,
                "source_split_fingerprint": source["split_fingerprint"],
                "candidate_source_root": str(candidate_root.resolve()),
                "candidate_source_provenance_sha256": file_hash(
                    provenance_path
                ),
                "csv": str(csv_path.resolve()),
                "csv_sha256": file_hash(csv_path),
                "config": str(config_path.resolve()),
                "config_sha256": file_hash(config_path),
                "base_trainer_arguments": arguments,
                "comparative_block": str(block_root.resolve()),
                "paired_corruption_file_sha256": file_hash(paired_path),
                "opendetect_runtime": str(comparator_artifact.resolve()),
                "opendetect_runtime_sha256": file_hash(comparator_artifact),
                "opendetect_capture_manifest_file_sha256": file_hash(
                    comparator_manifest_path
                ),
                "opendetect_source_metrics_file_sha256": file_hash(
                    comparator_metrics_path
                ),
                "opendetect_threshold": threshold,
            }
        )
    identities = {
        (item["scenario"], int(item["training_seed"])) for item in records
    }
    if len(records) != 30 or len(identities) != 30:
        raise ValueError("MDR PARROT source registry must contain 30 pairs")
    return records


def create_protocol(
    *,
    project_root: Path,
    run_root: Path,
    design: Dict[str, Any],
    selection: Dict[str, Any],
    confirmation_protocol: Dict[str, Any],
    confirmation_summary: Dict[str, Any],
    confirmation_audit: Dict[str, Any],
    feature_protocol: Dict[str, Any],
    feature_summary: Dict[str, Any],
    comparative: Dict[str, Any],
    sources: list[Dict[str, Any]],
    implementation_sha256: Dict[str, str],
    input_file_sha256: Dict[str, str],
    observed_metrics: int,
) -> Dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_mdr_parrot_safety_design_v1",
        "MDR PARROT design",
    )
    require_canonical(
        selection,
        "strict_v4_final_self_algorithm_selection_v2",
        "final selection",
    )
    require_canonical(
        confirmation_protocol,
        "strict_v4_mdr_caeos_confirmation_protocol_v1",
        "MDR confirmation protocol",
    )
    require_canonical(
        confirmation_summary,
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        "MDR confirmation summary",
    )
    require_canonical(
        confirmation_audit,
        "strict_v4_mdr_caeos_confirmation_audit_v1",
        "MDR confirmation audit",
    )
    require_canonical(
        feature_protocol,
        "parrot2025_full_no_decryption_feature_protocol_v1",
        "PARROT feature protocol",
    )
    require_canonical(
        feature_summary,
        "parrot2025_full_no_decryption_feature_summary_v1",
        "PARROT feature summary",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative protocol",
    )
    if int(observed_metrics) != 0:
        raise ValueError("MDR PARROT protocol must freeze before metrics")
    if (
        selection.get("selected_algorithm") != "mdr_caeos_v1"
        or selection.get("mdr_confirmation_passes") is not True
        or selection.get("protocol_manifest_sha256")
        != confirmation_protocol["manifest_sha256"]
        or selection.get("summary_manifest_sha256")
        != confirmation_summary["manifest_sha256"]
        or confirmation_summary.get("decision", {}).get("passes")
        is not True
        or confirmation_audit.get("passes") is not True
    ):
        raise ValueError("positive canonical MDR confirmation is required")
    if (
        feature_summary.get("protocol_manifest_sha256")
        != feature_protocol["manifest_sha256"]
        or int(feature_summary.get("capture_count", -1)) != 320
        or int(feature_summary.get("application_count", -1)) != 80
        or feature_summary.get("passed") is not True
        or not all(feature_summary.get("validation", {}).values())
    ):
        raise ValueError("complete canonical PARROT features are required")
    identities = {
        (item["scenario"], int(item["training_seed"])) for item in sources
    }
    if len(sources) != 30 or len(identities) != 30:
        raise ValueError("MDR PARROT protocol requires 30 model pairs")
    required = set(design["required_implementation"])
    if not required.issubset(implementation_sha256):
        raise ValueError("MDR PARROT implementation hashes are incomplete")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_parrot_safety_protocol_v1",
        "status": (
            "frozen_after_positive_mdr_selection_and_feature_completion_"
            "before_parrot_metrics"
        ),
        "selected_algorithm": "mdr_caeos_v1",
        "primary_comparator": "opendetect",
        "design_manifest_sha256": design["manifest_sha256"],
        "selection_manifest_sha256": selection["manifest_sha256"],
        "confirmation_protocol_manifest_sha256": confirmation_protocol[
            "manifest_sha256"
        ],
        "confirmation_summary_manifest_sha256": confirmation_summary[
            "manifest_sha256"
        ],
        "confirmation_audit_manifest_sha256": confirmation_audit[
            "manifest_sha256"
        ],
        "comparative_protocol_manifest_sha256": comparative[
            "manifest_sha256"
        ],
        "feature_protocol_manifest_sha256": feature_protocol[
            "manifest_sha256"
        ],
        "feature_summary_manifest_sha256": feature_summary[
            "manifest_sha256"
        ],
        "feature_root": str(Path(feature_protocol["output_root"]).resolve()),
        "feature_shard_manifest_sha256": feature_summary[
            "shard_manifest_sha256"
        ],
        "mdr_policy": {
            "augmentation_weight": float(
                confirmation_protocol["selected_augmentation_weight"]
            ),
            "sample_fraction": float(
                confirmation_protocol["confirmation"][
                    "training_sample_fraction"
                ]
            ),
            "health_quantile": float(
                confirmation_protocol["confirmation"]["health_quantile"]
            ),
            "weight_reselected_on_parrot": False,
        },
        "parrot_captures": feature_protocol["captures"],
        "capture_count": 320,
        "application_count": 80,
        "feature_columns": feature_protocol["feature_columns"],
        "metadata_columns": feature_protocol["metadata_columns"],
        "feature_count": 56,
        "source_model_pairs": sources,
        "source_model_pair_count": 30,
        "formal_metrics": design["formal_metrics"],
        "confirmation_gate": design["confirmation_gate"],
        "aggregation": design["aggregation"],
        "leakage_policy": design["leakage_policy"],
        "paths": {
            "project_root": str(project_root.resolve()),
            "run_root": str(run_root.resolve()),
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
        "formal_metric_count_at_freeze": 0,
        "claim_boundary": design["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--comparative-run-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--feature-protocol", type=Path, required=True)
    parser.add_argument("--feature-summary", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "design": args.design,
        "selection": args.selection,
        "confirmation_protocol": args.confirmation_protocol,
        "confirmation_summary": args.confirmation_summary,
        "confirmation_audit": args.confirmation_audit,
        "feature_protocol": args.feature_protocol,
        "feature_summary": args.feature_summary,
        "comparative_protocol": args.comparative_protocol,
    }
    design = load(args.design)
    comparative = load(args.comparative_protocol)
    observed = (
        len(list(args.run_root.glob("**/model_pair_metrics.json")))
        if args.run_root.exists()
        else 0
    )
    value = create_protocol(
        project_root=args.project_root,
        run_root=args.run_root,
        design=design,
        selection=load(args.selection),
        confirmation_protocol=load(args.confirmation_protocol),
        confirmation_summary=load(args.confirmation_summary),
        confirmation_audit=load(args.confirmation_audit),
        feature_protocol=load(args.feature_protocol),
        feature_summary=load(args.feature_summary),
        comparative=comparative,
        sources=build_source_records(
            comparative=comparative,
            project_root=args.project_root,
            comparative_run_root=args.comparative_run_root,
        ),
        implementation_sha256=verify_implementation(
            args.project_root, design["required_implementation"]
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        observed_metrics=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
