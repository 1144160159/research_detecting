from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_pcap_multimodal_counterfactual_pair_protocol import (
    build_pair_protocol,
)
from evaluate_strict_v4_pcap_multimodal_counterfactual_pair import (
    evaluate_pair,
)
from strict_v4_cic_iot2023_attack_family import canonical_hash, file_hash


FAMILIES = ["DDoS", "DoS", "Mirai"]


def seal(payload: dict) -> dict:
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def development_protocol(
    root: Path,
    role: str,
    *,
    counterfactual: bool,
) -> Path:
    run_root = root / f"{role}-runs"
    result_root = root / f"{role}-results"
    protocol = seal(
        {
            "schema_version": (
                "strict_v4_pcap_multimodal_development_protocol_v1"
            ),
            "state": "frozen_before_development_effects",
            "algorithm": {
                "architecture": "byte_cnn_tcn_gcn",
                "modalities": ["payload", "sequence", "graph"],
                "counterfactual_cross_family_modality_exposure": (
                    counterfactual
                ),
                "counterfactual_conflict_gate": counterfactual,
            },
            "cache": {
                "sha256": "a" * 64,
                "manifest_sha256": "b" * 64,
                "external_training_benign": {
                    "sha256": "c" * 64,
                    "manifest_sha256": "d" * 64,
                },
            },
            "protocol": {
                "development_seed": 307,
                "unknown_families": FAMILIES,
                "split": "capture_grouped_family_held_out",
            },
            "training": {
                "epochs": 80,
                "patience": 12,
                "batch_size": 512,
                "hidden_dim": 128,
                "embedding_dim": 96,
                "learning_rate": 0.0003,
                "alert_profile": (
                    "family_crossfit_meta_select_classscore_dual_alert"
                ),
                "external_training_benign_enabled": True,
                "reproducible_cuda_runtime": {"deterministic": True},
                "counterfactual_mix_weight": (
                    0.10 if counterfactual else 0.0
                ),
            },
            "paths": {
                "run_root": str(run_root),
                "result_root": str(result_root),
            },
            "implementation_sha256": {"trainer.py": "e" * 64},
            "claim_boundary": {
                "counterfactual_true_unknown_used_for_training": False,
                "counterfactual_true_unknown_used_for_checkpoint_selection": (
                    False
                ),
            },
        }
    )
    path = root / f"{role}-protocol.json"
    path.write_text(
        json.dumps(protocol, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def write_method_results(
    protocol_path: Path,
    *,
    improvement: float,
    gpu_mean: float,
) -> None:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    run_root = Path(protocol["paths"]["run_root"])
    result_root = Path(protocol["paths"]["result_root"])
    result_root.mkdir(parents=True)
    metric_hashes = {}
    for index, family in enumerate(FAMILIES):
        metrics = seal(
            {
                "schema_version": "task_v1",
                "state": "completed",
                "unknown_family": family,
                "seed": 307,
                "three_layer_metrics": {
                    "known_macro_f1": 0.90 + improvement,
                    "unknown_auroc": 0.70 + improvement + index * 0.01,
                    "unknown_aupr": 0.68 + improvement + index * 0.01,
                    "unknown_fpr95": 0.40 - improvement,
                    "oscr": 0.60 + improvement,
                },
            }
        )
        path = run_root / family.lower() / "metrics.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(metrics, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metric_hashes[family] = file_hash(path)

    completion = seal(
        {
            "schema_version": (
                "strict_v4_pcap_multimodal_development_completion_v1"
            ),
            "state": "completed",
            "failures": [],
            "task_count": 3,
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "task_metric_sha256": metric_hashes,
            "resource_summary": {
                "gpu_utilization_mean_percent": gpu_mean,
            },
        }
    )
    paper = {
        "known_macro_f1": {
            "mean": 0.90 + improvement,
            "worst": 0.90 + improvement,
        },
        "unknown_auroc": {
            "mean": 0.71 + improvement,
            "worst": 0.70 + improvement,
        },
        "unknown_aupr": {
            "mean": 0.69 + improvement,
            "worst": 0.68 + improvement,
        },
        "unknown_fpr95": {
            "mean": 0.40 - improvement,
            "worst": 0.40 - improvement,
        },
        "oscr": {
            "mean": 0.60 + improvement,
            "worst": 0.60 + improvement,
        },
    }
    evaluation = seal(
        {
            "schema_version": (
                "strict_v4_pcap_multimodal_development_evaluation_v1"
            ),
            "state": "development_gate_not_met",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "task_count": 3,
            "operational_95_5": {
                "alert_accuracy": {"mean": 0.8, "worst": 0.8},
                "benign_fpr": {"mean": 0.1, "worst": 0.1},
            },
            "paper_open_set": paper,
            "engineering_delivery_gate_pass": False,
            "paper_delivery_gate_pass": False,
        }
    )
    (result_root / "completion.json").write_text(
        json.dumps(completion, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (result_root / "evaluation.json").write_text(
        json.dumps(evaluation, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_pair_protocol_freezes_before_results_and_evaluator_passes(
    tmp_path: Path,
) -> None:
    project_root = Path(__file__).resolve().parents[1]
    base_path = development_protocol(
        tmp_path,
        "base",
        counterfactual=False,
    )
    candidate_path = development_protocol(
        tmp_path,
        "candidate",
        counterfactual=True,
    )
    pair = build_pair_protocol(
        project_root=project_root,
        base_protocol_path=base_path,
        candidate_protocol_path=candidate_path,
    )
    assert pair["pairing_contract"]["development_seed"] == 307
    assert pair["reserved_confirmation"]["access"].startswith("forbidden")

    write_method_results(base_path, improvement=0.0, gpu_mean=91.0)
    write_method_results(candidate_path, improvement=0.03, gpu_mean=93.0)
    result = evaluate_pair(pair)
    assert result["passes"] is True
    assert result["comparison"]["mean_unknown_auroc_gain"] == pytest.approx(
        0.03
    )
    assert result["checks"]["dos_unknown_auroc_gain_minimum"] is True
    assert result["candidate_absolute_metrics"][
        "engineering_delivery_gate_pass"
    ] is False


def test_pair_protocol_refuses_post_result_freeze(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    base_path = development_protocol(
        tmp_path,
        "base",
        counterfactual=False,
    )
    candidate_path = development_protocol(
        tmp_path,
        "candidate",
        counterfactual=True,
    )
    write_method_results(base_path, improvement=0.0, gpu_mean=90.0)
    with pytest.raises(ValueError, match="base results exist"):
        build_pair_protocol(
            project_root=project_root,
            base_protocol_path=base_path,
            candidate_protocol_path=candidate_path,
        )
