from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


SCENARIOS = {
    "caphaw": ["Caphaw.AH_None_TLS_CC", "Caphaw.A_None_TLS_CC"],
    "cobalt": ["CobaltStrike_None_TLS_CC"],
    "panda": ["Panda.BZA!tr_None_TLS_CC", "PandaZeuSCC_None_TLS_CC"],
    "qakbot": ["Qakbot_None_TLS_CC"],
    "scanners": [
        "arachni_arachni_TLS_scan",
        "burpsuite_burpsuite_TLS_scan",
        "golistmero_golistmero_TLS_scan",
        "nessus_nessus_TLS_scan",
    ],
    "tor": ["Tor_None_TLS_CC"],
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_protocol(
    *,
    dataset_sha256: str,
    implementation_sha256: dict[str, str],
    observed_metrics: int,
) -> dict[str, Any]:
    if len(dataset_sha256) != 64:
        raise ValueError("dataset SHA is invalid")
    if observed_metrics != 0:
        raise ValueError("heterogeneous pilot must be frozen before results")
    protocol: dict[str, Any] = {
        "schema_version": "mal_tls_heterogeneous_pilot_protocol_v1",
        "status": "frozen_before_development_pilot",
        "purpose": "test whether encoder heterogeneity adds evidence beyond feature partitioning",
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
            },
            "candidate": {
                "encoder_profile": "mal_tls_heterogeneous",
                "encoder_kinds": ["tls_gated", "mlp", "mlp", "sequence_tcn"],
            },
            "all_other_training_and_calibration_settings_identical": True,
        },
        "training": {
            "development_seed": 191,
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
        "development_gate": {
            "all_four_mean_oriented_gains_positive": True,
            "minimum_scenario_metric_gain": -0.03,
            "minimum_all_metric_nonregressing_scenarios": 4,
            "minimum_mean_known_macro_f1_gain": -0.01,
            "minimum_mean_ece_gain": 0.0,
        },
        "reserved_confirmation": {
            "seeds": [197, 199, 211],
            "expected_runs": 36,
            "must_freeze_after_pilot_before_confirmation": True,
            "claim_gate": (
                "paired scenario-blocked confidence intervals for AUROC, AUPR, FPR95 "
                "and OSCR plus known-F1 and ECE nonregression"
            ),
        },
        "claim_boundary": {
            "before_confirmation": "multi_view_encrypted_traffic_only",
            "after_passing_confirmation": "heterogeneous_multimodal_encoder_evidence_allowed",
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
        "train.py",
        "analyze_mal_tls_heterogeneous_pilot.py",
        "scripts/run_mal_tls_heterogeneous_pilot.sh",
    )
    protocol = create_protocol(
        dataset_sha256=file_hash(args.dataset),
        implementation_sha256={
            name: file_hash(args.project_root / name) for name in names
        },
        observed_metrics=len(list(args.run_root.rglob("metrics.json")))
        if args.run_root.exists()
        else 0,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
