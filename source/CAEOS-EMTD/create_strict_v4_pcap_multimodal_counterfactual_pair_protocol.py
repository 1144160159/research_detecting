from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


DEVELOPMENT_SCHEMA = "strict_v4_pcap_multimodal_development_protocol_v1"
BASE_PROFILE = "external_benign_family_crossfit_meta_select_classscore_dual_alert"
CANDIDATE_PROFILE = (
    "external_benign_counterfactual_mix_classscore_dual_alert"
)
IMPLEMENTATIONS = (
    "create_strict_v4_pcap_multimodal_counterfactual_pair_protocol.py",
    "evaluate_strict_v4_pcap_multimodal_counterfactual_pair.py",
)


def manifest_matches(payload: dict[str, Any]) -> bool:
    expected = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    return expected == canonical_hash(body)


def load_development_protocol(path: Path) -> dict[str, Any]:
    protocol = json.loads(path.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != DEVELOPMENT_SCHEMA:
        raise ValueError(f"unexpected development protocol schema: {path}")
    if protocol.get("state") != "frozen_before_development_effects":
        raise ValueError(f"development protocol is not frozen: {path}")
    if not manifest_matches(protocol):
        raise ValueError(f"development protocol manifest mismatch: {path}")
    return protocol


def pairing_contract(protocol: dict[str, Any]) -> dict[str, Any]:
    external_benign = protocol["cache"]["external_training_benign"]
    if not external_benign:
        raise ValueError("paired experiment requires external benign training")
    training = protocol["training"]
    return {
        "cache_sha256": protocol["cache"]["sha256"],
        "cache_manifest_sha256": protocol["cache"]["manifest_sha256"],
        "external_benign_cache_sha256": external_benign["sha256"],
        "external_benign_manifest_sha256": external_benign[
            "manifest_sha256"
        ],
        "development_seed": protocol["protocol"]["development_seed"],
        "unknown_families": protocol["protocol"]["unknown_families"],
        "split": protocol["protocol"]["split"],
        "architecture": protocol["algorithm"]["architecture"],
        "modalities": protocol["algorithm"]["modalities"],
        "epochs": training["epochs"],
        "patience": training["patience"],
        "batch_size": training["batch_size"],
        "hidden_dim": training["hidden_dim"],
        "embedding_dim": training["embedding_dim"],
        "learning_rate": training["learning_rate"],
        "alert_profile": training["alert_profile"],
        "external_training_benign_enabled": training[
            "external_training_benign_enabled"
        ],
        "reproducible_cuda_runtime": training[
            "reproducible_cuda_runtime"
        ],
        "implementation_sha256": protocol["implementation_sha256"],
    }


def assert_no_effects(protocol: dict[str, Any], role: str) -> None:
    result_root = Path(protocol["paths"]["result_root"])
    run_root = Path(protocol["paths"]["run_root"])
    if any(
        (result_root / name).exists()
        for name in ("completion.json", "evaluation.json")
    ):
        raise ValueError(f"{role} results exist before pair freeze")
    if run_root.exists() and any(run_root.rglob("metrics.json")):
        raise ValueError(f"{role} task metrics exist before pair freeze")


def build_pair_protocol(
    *,
    project_root: Path,
    base_protocol_path: Path,
    candidate_protocol_path: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    base_protocol_path = base_protocol_path.resolve()
    candidate_protocol_path = candidate_protocol_path.resolve()
    base = load_development_protocol(base_protocol_path)
    candidate = load_development_protocol(candidate_protocol_path)

    if pairing_contract(base) != pairing_contract(candidate):
        raise ValueError("base and candidate pairing contracts differ")
    if base["paths"]["run_root"] == candidate["paths"]["run_root"]:
        raise ValueError("paired methods cannot share a run root")
    if base["paths"]["result_root"] == candidate["paths"]["result_root"]:
        raise ValueError("paired methods cannot share a result root")
    if base["algorithm"].get(
        "counterfactual_cross_family_modality_exposure"
    ):
        raise ValueError("base protocol unexpectedly enables counterfactuals")
    if float(base["training"]["counterfactual_mix_weight"]) != 0.0:
        raise ValueError("base counterfactual weight must be zero")
    if candidate["algorithm"].get(
        "counterfactual_cross_family_modality_exposure"
    ) is not True:
        raise ValueError("candidate protocol does not enable counterfactuals")
    if candidate["algorithm"].get("counterfactual_conflict_gate") is not True:
        raise ValueError("candidate protocol does not enable conflict gate")
    if float(candidate["training"]["counterfactual_mix_weight"]) != 0.10:
        raise ValueError("candidate counterfactual weight differs from 0.10")
    if candidate["claim_boundary"].get(
        "counterfactual_true_unknown_used_for_training"
    ) is not False:
        raise ValueError("candidate training isolation declaration failed")
    if candidate["claim_boundary"].get(
        "counterfactual_true_unknown_used_for_checkpoint_selection"
    ) is not False:
        raise ValueError("candidate checkpoint isolation declaration failed")
    assert_no_effects(base, "base")
    assert_no_effects(candidate, "candidate")

    pair: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_counterfactual_pair_protocol_v1"
        ),
        "state": "frozen_before_paired_development_effects",
        "stage": "paired_development",
        "purpose": (
            "same-seed causal comparison of cross-family modality "
            "counterfactual exposure against the unchanged PCAP incumbent"
        ),
        "pairing_contract": pairing_contract(base),
        "methods": {
            "base": {
                "profile": BASE_PROFILE,
                "protocol_path": str(base_protocol_path),
                "protocol_file_sha256": file_hash(base_protocol_path),
                "protocol_manifest_sha256": base["manifest_sha256"],
                "run_root": base["paths"]["run_root"],
                "result_root": base["paths"]["result_root"],
            },
            "candidate": {
                "profile": CANDIDATE_PROFILE,
                "protocol_path": str(candidate_protocol_path),
                "protocol_file_sha256": file_hash(
                    candidate_protocol_path
                ),
                "protocol_manifest_sha256": candidate["manifest_sha256"],
                "run_root": candidate["paths"]["run_root"],
                "result_root": candidate["paths"]["result_root"],
            },
        },
        "development_gate": {
            "mean_unknown_auroc_gain_strictly_positive": 0.0,
            "worst_unknown_auroc_gain_strictly_positive": 0.0,
            "mean_unknown_aupr_gain_strictly_positive": 0.0,
            "mean_unknown_fpr95_reduction_strictly_positive": 0.0,
            "mean_oscr_gain_strictly_positive": 0.0,
            "dos_unknown_auroc_gain_minimum": 0.0,
            "mean_known_macro_f1_gain_minimum": -0.01,
            "worst_known_macro_f1_gain_minimum": -0.01,
            "both_gpu_utilization_mean_minimum_percent": 50.0,
            "preferred_gpu_utilization_mean_percent": 80.0,
        },
        "execution": {
            "protocols_frozen_before_either_result": True,
            "recommended_order": ["base", "candidate"],
            "sequential_gpu_execution": True,
            "shared_gpu_execution_forbidden": True,
            "formal_execution_gpu_only": True,
        },
        "reserved_confirmation": {
            "seeds": [331, 337, 347],
            "access": "forbidden_by_this_paired_development_protocol",
        },
        "claim_boundary": {
            "development_only": True,
            "unknown_test_metrics_not_used_to_select_loss_weights": True,
            "paired_gate_failure_rejects_candidate": True,
            "paired_gate_success_does_not_establish_sota": True,
            "fresh_reserved_seed_confirmation_required": True,
        },
        "implementation_sha256": {
            name: file_hash(project_root / name)
            for name in IMPLEMENTATIONS
        },
    }
    pair["manifest_sha256"] = canonical_hash(pair)
    return pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--base-protocol", type=Path, required=True)
    parser.add_argument("--candidate-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite frozen pair protocol: {output}")
    protocol = build_pair_protocol(
        project_root=args.project_root,
        base_protocol_path=args.base_protocol,
        candidate_protocol_path=args.candidate_protocol,
    )
    atomic_json(output, protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
