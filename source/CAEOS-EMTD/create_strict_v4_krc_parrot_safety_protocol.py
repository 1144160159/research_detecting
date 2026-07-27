from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_external_malicious_execution_protocol import (
    validate_positive_confirmation,
)
from create_strict_v4_krc_selected_system_protocol import build_sources
from create_strict_v4_mdr_caeos_confirmation_protocol import option_value
from create_strict_v4_mdr_parrot_safety_protocol import (
    build_source_records as build_opendetect_sources,
)


IMPLEMENTATION = (
    "create_strict_v4_krc_parrot_safety_protocol.py",
    "capture_krc_parrot_deployment_bundle.py",
    "evaluate_krc_parrot_capture.py",
    "summarize_strict_v4_krc_parrot_safety.py",
    "audit_strict_v4_krc_parrot_safety.py",
    "run_strict_v4_krc_parrot_safety.py",
    "caeos/krc_deployment.py",
    "caeos/krc_csr_runtime.py",
    "caeos/csr_runtime.py",
    "caeos/csr_exact_replay_runtime.py",
    "caeos/mdr_runtime.py",
    "caeos/pairwise_runtime.py",
    "caeos/pairwise_deployment.py",
    "caeos/open_detect_runtime.py",
    "caeos/conformal_safe_routing.py",
    "caeos/data.py",
    "train_hybrid_open_set.py",
    "capture_pairwise_runtime.py",
    "capture_mdr_parrot_deployment_bundle.py",
    "evaluate_mdr_parrot_capture.py",
    "summarize_strict_v4_mdr_parrot_safety.py",
    "create_strict_v4_mdr_parrot_safety_protocol.py",
    "create_strict_v4_mdr_caeos_confirmation_protocol.py",
    "create_strict_v4_krc_selected_system_protocol.py",
    "create_strict_v4_krc_external_malicious_execution_protocol.py",
    "create_strict_v4_external_confirmation_protocol.py",
)
SEED_PAIRING = {647: 137, 653: 139, 659: 149}


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def verify_implementation(
    project_root: Path, relatives: Iterable[str] = IMPLEMENTATION
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC PARROT implementation: {relative}"
            )
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def zero_output_counts(result_root: Path) -> Dict[str, int]:
    counts = {
        "deployments": len(list(result_root.glob("**/capture_manifest.json")))
        if result_root.exists()
        else 0,
        "metrics": len(list(result_root.glob("**/model_pair_metrics.json")))
        if result_root.exists()
        else 0,
        "summary": int((result_root / "summary.json").is_file()),
        "audit": int((result_root / "audit.json").is_file()),
        "completion": int((result_root / "execution_complete").is_file()),
    }
    if any(counts.values()):
        raise ValueError("KRC PARROT protocol requires a zero-result root")
    return counts


def build_model_pairs(
    *,
    confirmation_protocol: Dict[str, Any],
    capture_root: Path,
    comparative: Dict[str, Any],
    project_root: Path,
    comparative_run_root: Path,
) -> list[Dict[str, Any]]:
    candidates = [
        item
        for item in build_sources(confirmation_protocol, capture_root)
        if item["suite"] == "ustc_tfc2016"
    ]
    comparators = build_opendetect_sources(
        comparative=comparative,
        project_root=project_root,
        comparative_run_root=comparative_run_root,
    )
    comparator_index = {
        (str(item["scenario"]), int(item["training_seed"])): item
        for item in comparators
    }
    records = []
    for candidate in candidates:
        capture_dir = Path(candidate["capture_dir"])
        manifest_path = capture_dir / "capture_manifest.json"
        manifest = load(manifest_path)
        arguments = list(manifest["clean_trainer_arguments"])
        config = Path(option_value(arguments, "--config"))
        if not config.is_absolute():
            config = project_root / config
        csv = Path(option_value(arguments, "--csv"))
        candidate_seed = int(candidate["training_seed"])
        comparator_seed = SEED_PAIRING[candidate_seed]
        comparator = comparator_index[
            (str(candidate["scenario"]), comparator_seed)
        ]
        comparator_capture = (
            Path(comparator["comparative_block"]) / "comparator_capture"
        )
        comparator_manifest_path = comparator_capture / "capture_manifest.json"
        comparator_manifest = load(comparator_manifest_path)
        comparator_inputs = comparator_capture / comparator_manifest[
            "benchmark_inputs"
        ]
        if (
            comparator_manifest.get("schema_version")
            != "strict_v4_opendetect_runtime_capture_v1"
            or comparator_manifest.get("equivalence", {}).get("passes")
            is not True
            or file_hash(comparator_inputs)
            != comparator_manifest["benchmark_inputs_sha256"]
        ):
            raise ValueError("invalid OpenDetect preprocessing replay source")
        split = manifest["split_fingerprint"]
        split_fingerprint = str(
            split["combined"] if isinstance(split, dict) else split
        )
        records.append(
            {
                **candidate,
                "source_capture_manifest_sha256": manifest["manifest_sha256"],
                "source_split_fingerprint": split_fingerprint,
                "clean_trainer_arguments": arguments,
                "csv": str(csv.resolve()),
                "csv_sha256": file_hash(csv),
                "config": str(config.resolve()),
                "config_sha256": file_hash(config),
                "opendetect_training_seed": comparator_seed,
                "opendetect_source_split_fingerprint": comparator[
                    "source_split_fingerprint"
                ],
                "opendetect_preprocessing_arguments": comparator[
                    "base_trainer_arguments"
                ],
                "opendetect_csv": comparator["csv"],
                "opendetect_csv_sha256": comparator["csv_sha256"],
                "opendetect_config": comparator["config"],
                "opendetect_config_sha256": comparator["config_sha256"],
                "opendetect_runtime": comparator["opendetect_runtime"],
                "opendetect_runtime_sha256": comparator[
                    "opendetect_runtime_sha256"
                ],
                "opendetect_capture_manifest_file_sha256": comparator[
                    "opendetect_capture_manifest_file_sha256"
                ],
                "opendetect_source_metrics_file_sha256": comparator[
                    "opendetect_source_metrics_file_sha256"
                ],
                "opendetect_threshold": float(
                    comparator["opendetect_threshold"]
                ),
                "opendetect_benchmark_inputs": str(
                    comparator_inputs.resolve()
                ),
                "opendetect_benchmark_inputs_sha256": file_hash(
                    comparator_inputs
                ),
            }
        )
    identities = {
        (item["scenario"], int(item["training_seed"])) for item in records
    }
    if (
        len(records) != 30
        or len(identities) != 30
        or len({item["scenario"] for item in records}) != 10
        or {int(item["training_seed"]) for item in records}
        != set(SEED_PAIRING)
    ):
        raise ValueError("KRC PARROT source matrix must be USTC 10x3")
    return sorted(
        records, key=lambda item: (item["scenario"], item["training_seed"])
    )


def create_protocol(
    *,
    project_root: Path,
    result_root: Path,
    downstream_path: Path,
    confirmation_protocol_path: Path,
    confirmation_summary_path: Path,
    confirmation_audit_path: Path,
    capture_root: Path,
    feature_protocol_path: Path,
    feature_summary_path: Path,
    comparative_path: Path,
    comparative_run_root: Path,
) -> Dict[str, Any]:
    downstream = load(downstream_path)
    confirmation_protocol = load(confirmation_protocol_path)
    confirmation_summary = load(confirmation_summary_path)
    confirmation_audit = load(confirmation_audit_path)
    feature_protocol = load(feature_protocol_path)
    feature_summary = load(feature_summary_path)
    comparative = load(comparative_path)
    require_canonical(
        downstream,
        "strict_v4_krc_downstream_sota_design_v1",
        "KRC downstream design",
    )
    validate_positive_confirmation(
        confirmation_protocol,
        confirmation_summary,
        confirmation_audit,
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
    if (
        downstream["input_manifest_sha256"]["krc_confirmation_protocol"]
        != confirmation_protocol["manifest_sha256"]
        or downstream["input_manifest_sha256"]["parrot_feature_protocol"]
        != feature_protocol["manifest_sha256"]
        or downstream["input_manifest_sha256"]["comparative_protocol"]
        != comparative["manifest_sha256"]
        or feature_summary.get("protocol_manifest_sha256")
        != feature_protocol["manifest_sha256"]
        or int(feature_summary.get("capture_count", -1)) != 320
        or int(feature_summary.get("application_count", -1)) != 80
        or feature_summary.get("passed") is not True
        or not all(feature_summary.get("validation", {}).values())
    ):
        raise ValueError("KRC PARROT upstream binding or feature gate failed")
    sources = build_model_pairs(
        confirmation_protocol=confirmation_protocol,
        capture_root=capture_root,
        comparative=comparative,
        project_root=project_root,
        comparative_run_root=comparative_run_root,
    )
    design = downstream["parrot2025_external_benign_safety"]
    if (
        int(design["captures"]) != 320
        or int(design["applications"]) != 80
        or int(design["feature_count"]) != 56
        or int(design["candidate_bundle_count"]) != 30
        or int(design["opendetect_bundle_count"]) != 30
    ):
        raise ValueError("KRC PARROT downstream design drifted")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_parrot_safety_protocol_v1",
        "status": "admitted_after_positive_krc_and_complete_features",
        "execution_admitted": True,
        "selected_algorithm": "krc_csr_caeos_v1",
        "primary_comparator": "opendetect",
        "source_model_pairs": sources,
        "source_model_pair_count": 30,
        "candidate_training_seeds": sorted(SEED_PAIRING),
        "opendetect_training_seeds": sorted(SEED_PAIRING.values()),
        "seed_pairing": {
            str(left): right for left, right in SEED_PAIRING.items()
        },
        "feature_root": str(Path(feature_protocol["output_root"]).resolve()),
        "feature_columns": list(feature_protocol["feature_columns"]),
        "metadata_columns": list(feature_protocol["metadata_columns"]),
        "feature_shard_manifest_sha256": feature_summary[
            "shard_manifest_sha256"
        ],
        "parrot_captures": list(feature_protocol["captures"]),
        "capture_count": 320,
        "application_count": 80,
        "aggregation": {
            "unit": "capture_after_averaging_30_model_pairs",
            "capture_block_bootstrap_repetitions": 10000,
            "capture_block_bootstrap_seed": 20260726,
            "application_has_four_capture_blocks": True,
        },
        "confirmation_gate": design["confirmation_gate"],
        "output_counts_at_freeze": zero_output_counts(result_root),
        "paths": {
            "project_root": str(project_root.resolve()),
            "result_root": str(result_root.resolve()),
        },
        "input_manifest_sha256": {
            "downstream_design": downstream["manifest_sha256"],
            "confirmation_protocol": confirmation_protocol["manifest_sha256"],
            "confirmation_summary": confirmation_summary["manifest_sha256"],
            "confirmation_audit": confirmation_audit["manifest_sha256"],
            "feature_protocol": feature_protocol["manifest_sha256"],
            "feature_summary": feature_summary["manifest_sha256"],
            "comparative_protocol": comparative["manifest_sha256"],
        },
        "input_file_sha256": {
            "downstream_design": file_hash(downstream_path),
            "confirmation_protocol": file_hash(confirmation_protocol_path),
            "confirmation_summary": file_hash(confirmation_summary_path),
            "confirmation_audit": file_hash(confirmation_audit_path),
            "feature_protocol": file_hash(feature_protocol_path),
            "feature_summary": file_hash(feature_summary_path),
            "comparative_protocol": file_hash(comparative_path),
        },
        "implementation_sha256": verify_implementation(project_root),
        "claim_boundary": {
            "parrot_is_external_benign_safety_only": True,
            "malicious_accuracy_or_parrot_sota_not_supported": True,
            "cannot_replace_external_malicious_confirmation": True,
            "parrot_not_used_for_fit_selection_calibration_or_threshold": True,
            "candidate_model_refit_for_parrot": False,
            "payload_decryption_used": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--feature-protocol", type=Path, required=True)
    parser.add_argument("--feature-summary", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--comparative-run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root.resolve(),
        result_root=args.result_root.resolve(),
        downstream_path=args.downstream_design.resolve(),
        confirmation_protocol_path=args.confirmation_protocol.resolve(),
        confirmation_summary_path=args.confirmation_summary.resolve(),
        confirmation_audit_path=args.confirmation_audit.resolve(),
        capture_root=args.capture_root.resolve(),
        feature_protocol_path=args.feature_protocol.resolve(),
        feature_summary_path=args.feature_summary.resolve(),
        comparative_path=args.comparative_protocol.resolve(),
        comparative_run_root=args.comparative_run_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
