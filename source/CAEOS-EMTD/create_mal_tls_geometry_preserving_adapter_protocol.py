from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_mal_tls_heterogeneous_pilot_protocol import SCENARIOS
from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_protocol(
    *, dataset_sha256: str, implementation_sha256: dict[str, str], observed_metrics: int
) -> dict[str, Any]:
    if len(dataset_sha256) != 64:
        raise ValueError("dataset SHA is invalid")
    if observed_metrics != 0:
        raise ValueError("geometry-preserving pilot must be frozen before results")
    protocol: dict[str, Any] = {
        "schema_version": "mal_tls_geometry_preserving_adapter_protocol_v1",
        "status": "frozen_before_development_pilot",
        "purpose": (
            "preserve the uniform backbone's fused geometry while learning bounded "
            "TLS and packet-sequence corrections only in fused evidence space"
        ),
        "diagnostic_basis": {
            "source_protocol_manifest_sha256": (
                "66fa6b6f9d1153873daaa92daf1ecf7a3a7c15d660d02667a28725811cfb7b9a"
            ),
            "largest_mean_component_regression": "normal_distance_auroc",
            "largest_mean_component_gain": -0.04779174763325322,
            "used_for_hypothesis_generation_only": True,
        },
        "dataset": {
            "name": "Mal_TLS2023",
            "sha256": dataset_sha256,
            "benign_class": "benign",
            "modalities": [
                "tls_handshake",
                "ip_flow_statistics",
                "payload_statistics",
                "packet_sequence",
            ],
            "scenarios": SCENARIOS,
        },
        "paired_methods": {
            "reference": {
                "encoder_profile": "uniform_mlp",
                "encoder_kinds": ["mlp", "mlp", "mlp", "mlp"],
                "evidence_adapter_kinds": ["none", "none", "none", "none"],
            },
            "candidate": {
                "encoder_profile": "mal_tls_geometry_preserving_adapter",
                "encoder_kinds": ["mlp", "mlp", "mlp", "mlp"],
                "evidence_adapter_kinds": [
                    "tls_gated",
                    "none",
                    "none",
                    "sequence_tcn",
                ],
            },
            "candidate_initializes_from_paired_reference_checkpoint": True,
            "candidate_trainable_scope": "evidence_adapters_only",
            "evidence_adapter_scale": 0.25,
            "known_clean_to_corrupted_consistency_weight": 1.0,
            "known_validation_evidence_temperature_calibration_for_both": True,
        },
        "training": {
            "development_seed": 195,
            "max_per_class": 1000,
            "split_strategy": "fingerprint_grouped",
            "epochs": 15,
            "batch_size": 512,
            "hidden_dim": 128,
            "embedding_dim": 64,
            "calibrator": "conformal",
            "expected_development_runs": 12,
            "unknown_or_test_labels_used_for_training_or_selection": False,
        },
        "hard_invariants": {
            "all_non_adapter_checkpoint_tensors_bitwise_equal": True,
            "distance_and_conflict_metric_absolute_tolerance": 1e-12,
            "invariant_metrics": [
                "distance_auroc",
                "normal_distance_auroc",
                "conflict_auroc",
                "raw_conflict_auroc",
            ],
        },
        "development_gate": {
            "all_four_mean_oriented_gains_positive": True,
            "minimum_scenario_metric_gain": -0.03,
            "minimum_all_metric_nonregressing_scenarios": 4,
            "minimum_mean_known_macro_f1_gain": -0.01,
            "minimum_mean_ece_gain": 0.0,
            "all_geometry_invariants_pass": True,
        },
        "reserved_confirmation": {
            "seeds": [197, 199, 211],
            "must_freeze_after_pilot_before_confirmation": True,
        },
        "claim_boundary": {
            "development_success_does_not_establish_sota": True,
            "does_not_replace_paper_incumbent": "caeos_pairwise",
        },
        "metrics_observed_at_freeze": observed_metrics,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    names = (
        "caeos/model.py",
        "caeos/training.py",
        "train.py",
        "verify_geometry_preserving_adapter_checkpoints.py",
        "analyze_mal_tls_geometry_preserving_adapter.py",
        "scripts/run_mal_tls_geometry_preserving_adapter.sh",
    )
    protocol = create_protocol(
        dataset_sha256=file_hash(args.dataset),
        implementation_sha256={name: file_hash(args.project_root / name) for name in names},
        observed_metrics=(
            len(list(args.run_root.rglob("metrics.json"))) if args.run_root.exists() else 0
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
