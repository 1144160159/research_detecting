from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def create_protocol(project_root: Path, dataset_root: str) -> dict[str, Any]:
    implementations = (
        "prepare_dohbrw2020.py",
        "caeos/data.py",
        "train_hybrid_open_set.py",
        "train_neural_open_set.py",
        "summarize_doh_temporal_external.py",
        "scripts/wait_and_run_doh_temporal_external.sh",
        "configs/dohbrw2020_temporal_multiclass.json",
    )
    payload: dict[str, Any] = {
        "schema_version": "doh_temporal_external_protocol_v1",
        "status": "frozen_before_dataset_preparation_or_model_results",
        "claim_boundary": {
            "supported": "within-class future-capture generalization with a later held-out malicious tool",
            "not_supported": [
                "cross-dataset generalization",
                "cross-organization generalization",
                "comprehensive external SOTA",
            ],
        },
        "dataset": {
            "name": "DoHBrw2020",
            "raw_root": dataset_root,
            "prepared_csv": "caches/doh_temporal_external/doh_all_timed.csv",
            "preparation": {
                "selection": "all",
                "require_capture_time": True,
                "rows_per_capture": 200,
                "seed": 7,
            },
            "known_classes": ["benign", "dnscat2", "iodine"],
            "unknown_classes": ["dns2tcp"],
            "unknown_temporal_relation": "dns2tcp captures occur after retained known malicious tool captures in the audited filenames",
            "split_strategy": "temporal_capture_grouped",
            "split_fractions": [0.70, 0.15, 0.15],
            "split_order": "per-class ascending CaptureTime",
        },
        "experiment": {
            "seeds": [223, 227, 229],
            "max_per_class": 4000,
            "known_acceptance": 0.95,
            "candidate": {
                "name": "CAEOS-Pairwise",
                "estimators": 80,
                "risk_selection": "nested_boundary_pairwise_pseudo_unknown_blend",
                "pseudo_unknown_max_alpha": 0.5,
                "pseudo_unknown_min_fold_gain": -0.05,
                "boundary_hard_pseudo_fraction": 0.5,
                "boundary_interpolation": 0.5,
                "boundary_max_per_task": 512,
                "boundary_training_objective": "pairwise",
            },
            "comparator": {
                "name": "OpenDetect",
                "epochs": 100,
                "patience": 100,
                "hidden_dim": 128,
                "embedding_dim": 64,
            },
        },
        "leakage_controls": {
            "preprocessing_fit": "known train only",
            "threshold_fit": "known validation only",
            "unknown_or_test_labels_used_for_model_selection": False,
            "capture_groups_disjoint": True,
            "future_test_used_for_final_metrics_only": True,
        },
        "pilot_gate": {
            "required_runs": 6,
            "failures": 0,
            "identical_split_fingerprint_per_seed": True,
            "all_group_overlaps_zero": True,
            "all_known_class_time_ranges_ordered": True,
            "oriented_metrics": [
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "minimum_nonnegative_mean_metric_count": 4,
            "unknown_fpr95_orientation": "lower_is_better",
            "decision_use": "generalization evidence only; never tune frozen candidate parameters",
        },
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in implementations
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(args.project_root.resolve(), args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(protocol, sort_keys=True))


if __name__ == "__main__":
    main()
