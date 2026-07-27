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
        raise ValueError("counterfactual conflict-gate pilot must freeze before results")
    protocol: dict[str, Any] = {
        "schema_version": "mal_tls_counterfactual_conflict_gate_protocol_v1",
        "status": "frozen_before_development_pilot",
        "purpose": (
            "learn a known-only conflict-conditioned evidence attenuation gate from "
            "cross-class TLS and packet-sequence counterfactuals while preserving "
            "the incumbent representation and conflict geometry"
        ),
        "hypothesis_basis": {
            "completed_negative_results_only": [
                "mal_tls_heterogeneous_seed191",
                "mal_tls_conservative_residual_seed193",
            ],
            "geometry_adapter_seed195_results_observed": False,
            "mechanism_gap": (
                "prior representation changes damaged normal-distance geometry, while "
                "known-only routing could not identify safe activation scenarios"
            ),
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
                "counterfactual_conflict_gate": False,
            },
            "candidate": {
                "encoder_profile": "mal_tls_counterfactual_conflict_gate",
                "encoder_kinds": ["mlp", "mlp", "mlp", "mlp"],
                "evidence_adapter_kinds": ["none", "none", "none", "none"],
                "counterfactual_conflict_gate": True,
            },
            "candidate_initializes_from_paired_reference_checkpoint": True,
            "candidate_trainable_scope": "counterfactual_conflict_gate_only",
            "known_validation_evidence_temperature_calibration_for_both": True,
        },
        "known_only_counterfactual_training": {
            "source_split": "known_training_only",
            "source_labels_used": True,
            "cross_class_source_selection": "deterministic_next_different_class",
            "replaced_modalities": ["tls_handshake", "packet_sequence"],
            "consistency_weight": 1.0,
            "counterfactual_weight": 1.0,
            "uncertainty_margin": 0.05,
            "nonattenuation_penalty_weight": 0.1,
            "maximum_absolute_log_attenuation": 1.0,
            "checkpoint_selection": "last_epoch_among_known_macro_f1_ties",
            "unknown_or_test_labels_used": False,
        },
        "training": {
            "development_seed": 201,
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
            "all_non_gate_checkpoint_tensors_bitwise_equal": True,
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
            "minimum_mean_known_validation_counterfactual_uncertainty_gain": 0.02,
            "minimum_mean_margin_satisfaction_fraction": 0.5,
            "positive_mean_counterfactual_log_attenuation_gain": True,
            "all_geometry_invariants_pass": True,
        },
        "reserved_confirmation": {
            "seeds": [203, 205, 207],
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
        "create_mal_tls_counterfactual_conflict_gate_protocol.py",
        "verify_counterfactual_conflict_gate_checkpoints.py",
        "analyze_mal_tls_counterfactual_conflict_gate.py",
        "scripts/run_mal_tls_counterfactual_conflict_gate.sh",
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
