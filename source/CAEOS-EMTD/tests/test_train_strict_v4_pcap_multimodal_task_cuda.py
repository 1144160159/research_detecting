from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest
import torch

import train_strict_v4_pcap_multimodal_task_cuda as task


def test_initialize_cuda_device_initializes_context_before_memory_reset(
    monkeypatch,
) -> None:
    calls: list[object] = []

    monkeypatch.setattr(
        task.torch.cuda,
        "init",
        lambda: calls.append("init"),
    )
    monkeypatch.setattr(
        task.torch.cuda,
        "set_device",
        lambda index: calls.append(("set_device", index)),
    )
    monkeypatch.setattr(
        task.torch.cuda,
        "reset_peak_memory_stats",
        lambda device: calls.append(("reset_peak_memory_stats", str(device))),
    )

    device = task.initialize_cuda_device(0)

    assert device == torch.device("cuda", 0)
    assert calls == [
        "init",
        ("set_device", 0),
        ("reset_peak_memory_stats", "cuda:0"),
    ]


def test_tensors_for_indices_accepts_uint16_payload_cache() -> None:
    cache = {
        "payload": np.array([[0, 255, 256], [257, 1, 2]], dtype=np.uint16),
        "sequence": np.ones((2, 4), dtype=np.float32),
        "graph": np.ones((2, 5), dtype=np.float32),
        "quality": np.ones((2, 3), dtype=np.float32),
    }
    labels = np.array([3, 4], dtype=np.int64)

    views, quality, target = task.tensors_for_indices(
        cache,
        labels,
        np.array([1], dtype=np.int64),
        torch.device("cpu"),
    )

    assert views[0].dtype == torch.long
    assert views[0].tolist() == [[257, 1, 2]]
    assert quality.shape == (1, 3)
    assert target.tolist() == [4]


def test_tensors_for_cache_returns_unlabeled_views() -> None:
    cache = cache_arrays(
        ["ExternalSurrogateUnknown", "ExternalSurrogateUnknown"],
        ["Exploits", "Shellcode"],
        ["UNSW-NB15::a.pcap", "UNSW-NB15::b.pcap"],
    )

    views, quality = task.tensors_for_cache(cache, torch.device("cpu"))

    assert [tuple(view.shape) for view in views] == [
        (2, 3),
        (2, 4),
        (2, 5),
    ]
    assert quality.shape == (2, 3)


def test_cross_family_counterfactual_swaps_one_modality_only() -> None:
    labels = torch.tensor([0, 1, 1, 2, 2, 0])
    views = [
        torch.arange(12).reshape(6, 2),
        torch.arange(18, dtype=torch.float32).reshape(6, 3),
        torch.arange(24, dtype=torch.float32).reshape(6, 4),
    ]
    quality = torch.arange(18, dtype=torch.float32).reshape(6, 3)

    mixed_views, mixed_quality, evidence = (
        task.cross_family_modality_counterfactuals(
            views,
            quality,
            labels,
            modality_index=1,
        )
    )

    source = evidence["source_indices"]
    donor = evidence["donor_indices"]
    assert isinstance(source, torch.Tensor)
    assert isinstance(donor, torch.Tensor)
    assert len(source) == 4
    assert torch.equal(evidence["source_labels"], labels[source])
    assert torch.equal(evidence["donor_labels"], labels[donor])
    assert bool((labels[source] != labels[donor]).all())
    assert torch.equal(mixed_views[0], views[0][source])
    assert torch.equal(mixed_views[1], views[1][donor])
    assert torch.equal(mixed_views[2], views[2][source])
    assert torch.equal(mixed_quality[:, 0], quality[source, 0])
    assert torch.equal(mixed_quality[:, 1], quality[donor, 1])
    assert torch.equal(mixed_quality[:, 2], quality[source, 2])


def test_cross_family_counterfactual_requires_two_attack_families() -> None:
    views = [torch.ones((3, 2)), torch.ones((3, 2))]
    quality = torch.ones((3, 2))
    labels = torch.tensor([0, 1, 1])

    with pytest.raises(
        ValueError,
        match="requires two known attack families",
    ):
        task.cross_family_modality_counterfactuals(
            views,
            quality,
            labels,
            modality_index=0,
        )


def test_classical_baseline_score_arrays_export_all_splits() -> None:
    def output(offset: float) -> dict[str, torch.Tensor]:
        return {
            "fused_embedding": torch.tensor(
                [[offset, offset + 1.0], [offset + 2.0, offset + 3.0]]
            ),
            "fused_evidence": torch.tensor(
                [[1.0 + offset, 2.0], [3.0, 4.0 + offset]]
            ),
            "fused_belief": torch.tensor([[0.4, 0.6], [0.7, 0.3]]),
        }

    arrays = task.classical_baseline_score_arrays(
        train_output=output(0.0),
        train_labels=torch.tensor([0, 1]),
        validation_output=output(1.0),
        validation_labels=torch.tensor([1, 0]),
        test_output=output(2.0),
        test_labels=torch.tensor([0, -1]),
        is_unknown=np.asarray([False, True]),
    )

    assert set(arrays) == {
        f"baseline_{split}_{name}"
        for split in ("train", "validation", "test")
        for name in ("embedding", "log_evidence", "belief", "label")
    } | {"baseline_test_is_unknown"}
    assert arrays["baseline_train_embedding"].shape == (2, 2)
    assert arrays["baseline_validation_log_evidence"].shape == (2, 2)
    assert arrays["baseline_test_label"].tolist() == [0, -1]
    assert arrays["baseline_test_is_unknown"].tolist() == [False, True]


def test_risk_diagnostic_score_arrays_export_self_and_modal_evidence() -> None:
    class DummyCalibrator:
        def score(self, output):
            return (
                output["risk"],
                output["maliciousness"],
                {
                    "uncertainty": output["fused_uncertainty"],
                    "conflict": output["global_conflict"],
                },
            )

    def output(offset: float) -> dict[str, torch.Tensor]:
        return {
            "risk": torch.tensor([0.1 + offset, 0.2 + offset]),
            "maliciousness": torch.tensor([0.3, 0.4]),
            "fused_uncertainty": torch.tensor([0.5, 0.6]),
            "global_conflict": torch.tensor([0.2, 0.3]),
            "raw_conflict": torch.tensor([0.25, 0.35]),
            "malicious_logit": torch.tensor([-1.0, 1.0]),
            "reliability": torch.ones((2, 3)),
            "discount": torch.full((2, 3), 0.5),
        }

    arrays = task.risk_diagnostic_score_arrays(
        calibrator=DummyCalibrator(),
        train_output=output(0.0),
        validation_output=output(1.0),
        test_output=output(2.0),
    )

    assert arrays["self_train_risk"].tolist() == pytest.approx([0.1, 0.2])
    assert arrays["self_validation_conflict"].tolist() == pytest.approx(
        [0.2, 0.3]
    )
    assert arrays["diagnostic_test_raw_conflict"].tolist() == pytest.approx(
        [0.25, 0.35]
    )
    assert arrays["diagnostic_test_reliability"].shape == (2, 3)
    assert arrays["diagnostic_test_discount"].shape == (2, 3)


def test_external_surrogate_loss_rewards_uniform_low_evidence_attack() -> None:
    favorable = {
        "fused_probability": torch.tensor([[0.5, 0.5]]),
        "fused_evidence": torch.zeros((1, 2)),
        "malicious_logit": torch.tensor([5.0]),
    }
    unfavorable = {
        "fused_probability": torch.tensor([[0.99, 0.01]]),
        "fused_evidence": torch.full((1, 2), 10.0),
        "malicious_logit": torch.tensor([-5.0]),
    }

    favorable_loss = task.external_surrogate_unknown_loss(
        favorable,
        evidence_weight=0.05,
        malicious_weight=0.5,
    )
    unfavorable_loss = task.external_surrogate_unknown_loss(
        unfavorable,
        evidence_weight=0.05,
        malicious_weight=0.5,
    )

    assert favorable_loss["uniform_kl"] < 1e-7
    assert favorable_loss["total"] < unfavorable_loss["total"]


def test_engineering_behavior_features_are_finite_and_address_free() -> None:
    cache = {
        "payload": np.zeros((2, 8), dtype=np.uint16),
        "sequence": np.zeros((2, 12), dtype=np.float32),
        "graph": np.zeros((2, 14), dtype=np.float32),
        "quality": np.ones((2, 3), dtype=np.float32),
        "fine_label": np.asarray(["a", "b"]),
        "family": np.asarray(["Benign", "DDoS"]),
        "capture_group": np.asarray(["one", "two"]),
    }
    cache["graph"][:, 4] = 1.0
    output = {
        "fused_embedding": torch.ones((2, 4)),
        "fused_probability": torch.full((2, 2), 0.5),
        "fused_uncertainty": torch.full((2,), 0.5),
        "global_conflict": torch.zeros((2,)),
        "reliability": torch.ones((2, 3)),
        "discount": torch.ones((2, 3)),
        "fused_evidence": torch.zeros((2, 2)),
        "malicious_logit": torch.zeros((2,)),
    }

    features = task.engineering_behavior_features(
        cache,
        np.asarray([0, 1], dtype=np.int64),
        output,
    )

    assert features.shape[0] == 2
    assert features.shape[1] > 12 + 10 + 3 + 4
    assert np.isfinite(features).all()


def test_family_invariant_alert_features_keep_three_modal_summaries() -> None:
    cache = {
        "payload": np.asarray(
            [
                [65, 66, 256, 256],
                [0, 128, 255, 256],
            ],
            dtype=np.uint16,
        ),
        "sequence": np.zeros((2, 12), dtype=np.float32),
        "graph": np.zeros((2, 14), dtype=np.float32),
        "quality": np.ones((2, 3), dtype=np.float32),
    }
    cache["graph"][:, 4] = 1.0
    cache["graph"][:, 9] = 1.0
    cache["graph"][:, 11] = 1.0
    output = {
        "fused_uncertainty": torch.full((2,), 0.5),
        "global_conflict": torch.zeros((2,)),
        "reliability": torch.ones((2, 3)),
        "discount": torch.ones((2, 3)),
        "fused_evidence": torch.zeros((2, 2)),
        "malicious_logit": torch.zeros((2,)),
    }

    features = task.family_invariant_alert_features(
        cache,
        np.asarray([0, 1], dtype=np.int64),
        output,
    )

    assert features.shape == (2, 39)
    assert np.isfinite(features).all()
    assert not np.array_equal(features[0], features[1])


@pytest.mark.skipif(
    not torch.cuda.is_available()
    or "CAEOS_XGBOOST_ROOT" not in os.environ,
    reason="CUDA XGBoost package root is unavailable",
)
def test_xgboost_behavior_alert_binds_cuda(tmp_path) -> None:
    benign = np.full((16, 4), -1.0, dtype=np.float32)
    attack = np.full((16, 4), 1.0, dtype=np.float32)
    train_features = np.concatenate([benign, attack], axis=0)
    train_labels = torch.tensor([0] * 16 + [1] * 16)
    validation_features = np.concatenate(
        [benign[:8], attack[:8]], axis=0
    )
    validation_labels = torch.tensor([0] * 8 + [1] * 8)

    model, evidence = task.fit_xgboost_behavior_alert(
        train_features,
        train_labels,
        validation_features,
        validation_labels,
        seed=17,
        estimators=8,
        max_depth=2,
        learning_rate=0.2,
        early_stopping_rounds=2,
        jobs=2,
        model_path=tmp_path / "behavior.ubj",
        xgboost_root=Path(os.environ["CAEOS_XGBOOST_ROOT"]),
    )

    probability = model.predict_proba(validation_features)[:, 1]
    assert probability[:8].max() < probability[8:].min()
    assert evidence["xgboost_behavior_device"] == "cuda"
    assert evidence["xgboost_behavior_model_sha256"]


def test_group_conservative_alert_thresholds_use_benign_groups() -> None:
    validation_risk = np.array(
        [0.1, 0.2, 0.7, 0.8, 99.0], dtype=np.float32
    )
    validation_maliciousness = np.array(
        [0.3, 0.4, 0.5, 0.6, 99.0], dtype=np.float32
    )
    validation_labels = np.array([0, 0, 0, 0, 1], dtype=np.int64)
    validation_groups = np.array(
        ["benign-a", "benign-a", "benign-b", "benign-b", "attack-a"]
    )

    risk_threshold, malicious_threshold, group_count = (
        task.calibrate_group_conservative_alert_thresholds(
            validation_risk,
            validation_maliciousness,
            validation_labels,
            validation_groups,
            branch_false_positive_budget=0.02,
        )
    )

    assert risk_threshold == float(validation_risk[3])
    assert malicious_threshold == float(validation_maliciousness[3])
    assert group_count == 2


def test_family_crossfit_settings_allow_disabled_non_family_profile() -> None:
    task.validate_family_crossfit_settings(
        "binary_dual_alert",
        false_positive_budget=0.0,
        checkpoint_interval=25,
    )

    with pytest.raises(ValueError, match="family-crossfit"):
        task.validate_family_crossfit_settings(
            "family_crossfit_dual_alert",
            false_positive_budget=0.0,
            checkpoint_interval=25,
        )


def cache_arrays(
    families: list[str],
    fine_labels: list[str],
    groups: list[str],
) -> dict[str, np.ndarray]:
    count = len(families)
    return {
        "payload": np.zeros((count, 3), dtype=np.uint16),
        "sequence": np.zeros((count, 4), dtype=np.float32),
        "graph": np.zeros((count, 5), dtype=np.float32),
        "quality": np.ones((count, 3), dtype=np.float32),
        "fine_label": np.asarray(fine_labels),
        "family": np.asarray(families),
        "capture_group": np.asarray(groups),
    }


def test_append_training_only_external_benign_cache() -> None:
    primary = cache_arrays(
        ["Benign", "DDoS"],
        ["Benign_Final", "DDoS-SYN_Flood"],
        ["primary-benign", "primary-ddos"],
    )
    external = cache_arrays(
        ["Benign", "Benign"],
        ["Benign_Final", "Benign_Final"],
        [
            "CICIoT2022::5-Active/day-1.pcap",
            "CICIoT2022::5-Active/day-2.pcap",
        ],
    )

    combined, indices, evidence = (
        task.append_training_only_external_benign_cache(primary, external)
    )

    assert indices.tolist() == [2, 3]
    assert combined["family"].tolist() == [
        "Benign",
        "DDoS",
        "Benign",
        "Benign",
    ]
    assert evidence["sample_count"] == 2
    assert evidence["capture_group_count"] == 2
    assert evidence["primary_validation_or_test_modified"] is False


def test_validate_training_only_external_surrogate_cache() -> None:
    primary = cache_arrays(
        ["Benign", "DDoS"],
        ["Benign_Final", "DDoS-SYN_Flood"],
        ["primary-benign", "primary-ddos"],
    )
    external = cache_arrays(
        ["ExternalSurrogateUnknown", "ExternalSurrogateUnknown"],
        ["Exploits", "Shellcode"],
        [
            "UNSW-NB15::pcap22-01-2015/1.pcap",
            "UNSW-NB15::pcap22-01-2015/2.pcap",
        ],
    )

    evidence = task.validate_training_only_external_surrogate_cache(
        primary, external
    )

    assert evidence["sample_count"] == 2
    assert evidence["fine_label_values"] == ["Exploits", "Shellcode"]
    assert evidence["known_class_prototypes_modified"] is False
    assert evidence["threshold_fit_modified"] is False


def test_bind_external_surrogate_manifest_checks_target_isolation(
    tmp_path,
) -> None:
    cache_path = tmp_path / "external.npz"
    np.savez_compressed(cache_path, value=np.arange(3))
    manifest = {
        "cache_sha256": task.file_hash(cache_path),
        "samples": 3,
        "source_dataset": "UNSW-NB15",
        "source_role": "training_only_external_surrogate_unknown",
        "allowed_categories": ["Exploits"],
        "samples_by_category": {"Exploits": 3},
        "source_files": [{"path": "one.pcap"}],
        "claim_boundary": {
            "target_ciciot2023_test_unknown_labels_accessed": False,
        },
    }
    manifest["manifest_sha256"] = task.canonical_hash(manifest)
    manifest_path = cache_path.with_suffix(
        cache_path.suffix + ".manifest.json"
    )
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True),
        encoding="utf-8",
    )

    evidence = task.bind_external_surrogate_manifest(cache_path, 3)

    assert evidence["manifest_sha256"] == manifest["manifest_sha256"]
    assert evidence["target_test_unknown_labels_accessed"] is False


def test_cosine_knn_distance_uses_nearest_reference_mean() -> None:
    reference = torch.tensor(
        [
            [1.0, 0.0],
            [0.8, 0.2],
            [0.0, 1.0],
        ]
    )
    query = torch.tensor([[1.0, 0.0], [0.0, 1.0]])

    distance = task.cosine_knn_distance(
        query,
        reference,
        k=1,
        device=torch.device("cpu"),
    )

    assert torch.allclose(distance, torch.zeros(2), atol=1e-6)


def test_group_conservative_score_threshold_uses_worst_benign_group() -> None:
    score = np.array([0.1, 0.2, 0.7, 0.8, 99.0], dtype=np.float32)
    labels = np.array([0, 0, 0, 0, 1], dtype=np.int64)
    groups = np.array(["a", "a", "b", "b", "attack"])

    threshold, group_count = (
        task.calibrate_group_conservative_score_threshold(
            score,
            labels,
            groups,
            false_positive_budget=0.04,
        )
    )

    assert threshold == float(score[3])
    assert group_count == 2


def test_binary_alert_head_learns_known_benign_attack_boundary() -> None:
    benign = torch.tensor(
        [
            [-2.0, -1.0],
            [-1.5, -1.2],
            [-1.2, -1.8],
            [-1.8, -1.5],
        ]
    )
    attack = torch.tensor(
        [
            [1.2, 1.8],
            [1.5, 1.2],
            [1.8, 1.5],
            [2.0, 1.0],
        ]
    )
    embeddings = torch.cat((benign, attack))
    labels = torch.tensor([0, 0, 0, 0, 1, 1, 1, 1])

    head, evidence = task.fit_binary_alert_head(
        embeddings,
        labels,
        seed=17,
        hidden_dim=8,
        steps=100,
        batch_size=8,
        learning_rate=0.01,
        device=torch.device("cpu"),
    )
    probability = task.binary_alert_probability(
        head,
        embeddings,
        device=torch.device("cpu"),
    )

    assert probability[:4].max() < 0.2
    assert probability[4:].min() > 0.8
    assert evidence["binary_head_training_accuracy_at_0_5"] == 1.0


def test_known_class_attack_probability_is_one_minus_benign() -> None:
    score = task.known_class_attack_probability(
        {
            "fused_probability": torch.tensor(
                [
                    [0.90, 0.05, 0.05],
                    [0.10, 0.80, 0.10],
                ]
            )
        }
    )

    assert np.allclose(score, [0.10, 0.90])


def test_known_only_risk_component_selection_uses_attack_validation() -> None:
    labels = np.asarray([0, 0, 0, 0, 1, 1, 2, 2], dtype=np.int64)
    groups = np.asarray(
        ["b1", "b1", "b2", "b2", "a1", "a1", "a2", "a2"]
    )
    benign = np.asarray([0.10, 0.20, 0.10, 0.20])
    validation_candidates = {
        "risk": np.concatenate((benign, [0.80, 0.90, 0.10, 0.20])),
        "uncertainty": np.concatenate(
            (benign, [0.30, 0.40, 0.10, 0.20])
        ),
        "conflict": np.concatenate(
            (benign, [0.50, 0.60, 0.50, 0.60])
        ),
        "distance": np.concatenate(
            (benign, [0.80, 0.90, 0.70, 0.80])
        ),
        "energy": np.concatenate(
            (benign, [0.10, 0.20, 0.10, 0.20])
        ),
    }
    test_candidates = {
        name: np.asarray([0.10, 0.90])
        for name in validation_candidates
    }

    selected, margin, evidence = (
        task.select_known_only_risk_component(
            validation_candidates,
            test_candidates,
            labels,
            groups,
            false_positive_budget=0.25,
        )
    )

    assert selected == "distance"
    assert np.allclose(margin, [-0.10, 0.70])
    assert evidence[
        "known_only_risk_component_candidates"
    ]["distance"]["known_attack_validation_recall_worst"] == 1.0
    assert evidence[
        "known_only_risk_component_true_unknown_used_for_selection"
    ] is False


def test_family_crossfit_alert_learns_family_invariant_boundary(
    tmp_path,
) -> None:
    generator = np.random.default_rng(17)
    benign = generator.normal(
        loc=[-2.0, 0.0, 0.0],
        scale=0.15,
        size=(32, 3),
    ).astype(np.float32)
    attack_one = generator.normal(
        loc=[2.0, 4.0, 0.0],
        scale=0.15,
        size=(24, 3),
    ).astype(np.float32)
    attack_two = generator.normal(
        loc=[2.0, 0.0, -4.0],
        scale=0.15,
        size=(24, 3),
    ).astype(np.float32)
    train_features = np.concatenate(
        [benign[:16], attack_one[:16], attack_two[:16]],
        axis=0,
    )
    train_labels = torch.tensor([0] * 16 + [1] * 16 + [2] * 16)
    validation_features = np.concatenate(
        [benign[16:], attack_one[16:], attack_two[16:]],
        axis=0,
    )
    validation_labels = torch.tensor([0] * 16 + [1] * 8 + [2] * 8)
    validation_groups = np.asarray(
        ["benign-a"] * 8
        + ["benign-b"] * 8
        + ["attack-one"] * 8
        + ["attack-two"] * 8
    )
    unknown_test = generator.normal(
        loc=[2.5, 0.0, 0.0],
        scale=0.1,
        size=(8, 3),
    ).astype(np.float32)
    model_path = tmp_path / "family-crossfit.pt"

    margin, evidence = task.fit_family_crossfit_alert(
        train_features,
        train_labels,
        validation_features,
        validation_labels,
        validation_groups,
        unknown_test,
        seed=29,
        hidden_dim=16,
        steps=150,
        batch_size=24,
        learning_rate=0.01,
        weight_decay=1e-4,
        false_positive_budget=0.10,
        checkpoint_interval=10,
        device=torch.device("cpu"),
        model_path=model_path,
    )

    assert evidence["family_crossfit_head_count"] == 2
    assert evidence["family_crossfit_oof_meta_recall_worst"] == 1.0
    assert evidence["family_crossfit_true_unknown_used_for_training"] is False
    assert evidence["family_crossfit_true_unknown_used_for_threshold"] is False
    assert np.all(margin > 0.0)
    assert model_path.is_file()
    assert evidence["family_crossfit_model_sha256"]


def test_family_crossfit_meta_selection_uses_known_oof_metrics_only() -> None:
    common = {
        "family_crossfit_true_unknown_used_for_training": False,
        "family_crossfit_true_unknown_used_for_model_selection": False,
        "family_crossfit_true_unknown_used_for_threshold": False,
    }
    candidates = {
        "high_capacity": (
            np.asarray([-1.0, -1.0]),
            {
                **common,
                "family_crossfit_feature_count": 306,
                "family_crossfit_oof_meta_recall_worst": 0.25,
                "family_crossfit_oof_meta_recall_mean": 0.75,
                "family_crossfit_model_sha256": "high",
            },
        ),
        "family_invariant": (
            np.asarray([1.0, 1.0]),
            {
                **common,
                "family_crossfit_feature_count": 39,
                "family_crossfit_oof_meta_recall_worst": 0.50,
                "family_crossfit_oof_meta_recall_mean": 0.60,
                "family_crossfit_model_sha256": "invariant",
            },
        ),
    }

    profile, margin, evidence = (
        task.select_family_crossfit_candidate(candidates)
    )

    assert profile == "family_invariant"
    assert margin.tolist() == [1.0, 1.0]
    assert evidence["family_crossfit_meta_true_unknown_scores_used"] is False
    assert evidence["family_crossfit_meta_selection_key"].startswith(
        "known_only_oof"
    )


def test_binary_dual_alert_uses_benign_calibrated_auxiliary_branch() -> None:
    class DummyCalibrator:
        risk_threshold = 0.5

        def predict(self, output):
            return {
                "risk": output["risk"],
                "maliciousness": output["maliciousness"],
                "known_prediction": output["known_prediction"],
                "is_unknown": output["unknown_prediction"],
            }

        def score(self, output):
            return (
                output["risk"],
                output["maliciousness"],
                output["known_prediction"],
            )

    train_embedding = torch.tensor(
        [
            [-2.0, -1.0],
            [-1.5, -1.2],
            [-1.2, -1.8],
            [-1.8, -1.5],
            [1.2, 1.8],
            [1.5, 1.2],
            [1.8, 1.5],
            [2.0, 1.0],
        ]
    )
    validation_output = {
        "fused_embedding": torch.tensor(
            [
                [-2.0, -1.0],
                [-1.7, -1.2],
                [-1.4, -1.8],
                [-1.8, -1.4],
                [1.4, 1.6],
            ]
        ),
        "risk": torch.tensor([0.10, 0.15, 0.12, 0.20, 0.90]),
        "maliciousness": torch.tensor([0.10, 0.12, 0.15, 0.18, 0.90]),
        "known_prediction": torch.tensor([0, 0, 0, 0, 1]),
    }
    test_output = {
        "fused_embedding": torch.tensor(
            [
                [-1.9, -1.1],
                [1.5, 1.5],
                [-1.5, -1.5],
            ]
        ),
        "risk": torch.tensor([0.10, 0.20, 0.95]),
        "maliciousness": torch.tensor([0.10, 0.90, 0.20]),
        "known_prediction": torch.tensor([0, 1, 0]),
        "unknown_prediction": torch.tensor([False, False, True]),
    }

    metrics, arrays = task.operational_metrics(
        DummyCalibrator(),
        validation_output,
        torch.tensor([0, 0, 0, 0, 1]),
        np.array(["a", "a", "b", "b", "attack"]),
        test_output,
        torch.tensor([0, 1, 0]),
        torch.tensor([False, False, True]),
        train_output={"fused_embedding": train_embedding},
        train_labels=torch.tensor([0, 0, 0, 0, 1, 1, 1, 1]),
        external_attack_output={
            "fused_embedding": torch.tensor([[2.5, 2.5]])
        },
        alert_profile="binary_dual_alert",
        binary_head_seed=17,
        binary_head_hidden_dim=8,
        binary_head_steps=100,
        binary_head_batch_size=8,
        binary_head_learning_rate=0.01,
        binary_head_false_positive_budget=0.01,
        auxiliary_alert_branch_false_positive_budget=0.015,
        distance_device=torch.device("cpu"),
    )

    assert metrics["alert_profile"] == "binary_dual_alert"
    assert metrics["alert_joint_false_positive_budget_upper_bound"] == 0.04
    assert metrics["benign_fpr"] == 0.0
    assert metrics["unknown_attack_alert_recall"] == 1.0
    assert metrics["binary_head_external_surrogate_attack_samples"] == 1
    assert arrays["alert"].tolist() == [False, True, True]
