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


GPU_UUID = "GPU-a186fd29-e5be-496b-d374-4baeada258ee"
UNKNOWN_FAMILIES = ("DDoS", "DoS", "Mirai")
IMPLEMENTATIONS = (
    "caeos/model.py",
    "caeos/losses.py",
    "caeos/open_set.py",
    "caeos/metrics.py",
    "prepare_strict_v4_cic_iot2023_pcap_multimodal.py",
    "prepare_strict_v4_ciciot2022_active_benign_multimodal.py",
    "prepare_strict_v4_unsw_surrogate_unknown_multimodal.py",
    "strict_v4_pcap_multimodal_protocol.py",
    "train_strict_v4_pcap_multimodal_task_cuda.py",
    "run_strict_v4_pcap_multimodal_development.py",
    "evaluate_strict_v4_pcap_multimodal_development.py",
    "create_strict_v4_pcap_multimodal_development_protocol.py",
)


def build_protocol(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    cache = args.cache.resolve()
    cache_manifest_path = args.cache_manifest.resolve()
    cache_manifest = json.loads(
        cache_manifest_path.read_text(encoding="utf-8")
    )
    if cache_manifest["cache_sha256"] != file_hash(cache):
        raise ValueError("multimodal cache hash differs from manifest")
    if cache_manifest["samples"] != args.expected_samples:
        raise ValueError(
            f"cache has {cache_manifest['samples']} samples, "
            f"expected {args.expected_samples}"
        )
    if cache_manifest["capture_group_binding"] != (
        "relative_source_pcap_path"
    ):
        raise ValueError("cache is not source-PCAP capture-group bound")
    hierarchical_fine = args.algorithm_profile in {
        "hierarchical_fine",
        "hierarchical_fine_contrastive",
        "hierarchical_fine_max",
        "nested_pseudo_risk",
    }
    fine_contrastive = (
        args.algorithm_profile == "hierarchical_fine_contrastive"
    )
    nested_pseudo_risk = (
        args.algorithm_profile == "nested_pseudo_risk"
    )
    counterfactual_mix = (
        args.algorithm_profile
        == "external_benign_counterfactual_mix_classscore_dual_alert"
    )
    external_benign = args.algorithm_profile in {
        "external_benign",
        "external_benign_knn_alert",
        "external_benign_binary_alert",
        "external_benign_binary_dual_alert",
        "external_benign_frozen_binary_dual_alert",
        "external_benign_unsw_oe_binary_alert",
        "external_benign_unsw_alert_only",
        "external_benign_xgboost_behavior_alert",
        "external_benign_family_crossfit_dual_alert",
        "external_benign_family_crossfit_meta_select_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
        "external_benign_counterfactual_mix_classscore_dual_alert",
    }
    benign_knn_alert = (
        args.algorithm_profile == "external_benign_knn_alert"
    )
    binary_head_alert = (
        args.algorithm_profile
        in {
            "external_benign_binary_alert",
            "external_benign_binary_dual_alert",
            "external_benign_frozen_binary_dual_alert",
            "external_benign_unsw_oe_binary_alert",
            "external_benign_unsw_alert_only",
            "external_benign_family_crossfit_dual_alert",
            "external_benign_family_crossfit_meta_select_dual_alert",
            "external_benign_family_crossfit_meta_select_classscore_dual_alert",
            "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
            "external_benign_counterfactual_mix_classscore_dual_alert",
        }
    )
    binary_dual_alert = (
        args.algorithm_profile
        in {
            "external_benign_binary_dual_alert",
            "external_benign_frozen_binary_dual_alert",
            "external_benign_family_crossfit_dual_alert",
            "external_benign_family_crossfit_meta_select_dual_alert",
            "external_benign_family_crossfit_meta_select_classscore_dual_alert",
            "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
            "external_benign_counterfactual_mix_classscore_dual_alert",
        }
    )
    xgboost_behavior_alert = (
        args.algorithm_profile
        == "external_benign_xgboost_behavior_alert"
    )
    classscore_dual_alert = args.algorithm_profile in {
        "external_benign_family_crossfit_meta_select_classscore_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
        "external_benign_counterfactual_mix_classscore_dual_alert",
    }
    component_select_dual_alert = (
        args.algorithm_profile
        == "external_benign_family_crossfit_meta_select_classscore_component_dual_alert"
    )
    family_crossfit_meta_select = args.algorithm_profile in {
        "external_benign_family_crossfit_meta_select_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
        "external_benign_counterfactual_mix_classscore_dual_alert",
    }
    family_crossfit_dual_alert = args.algorithm_profile in {
        "external_benign_family_crossfit_dual_alert",
        "external_benign_family_crossfit_meta_select_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_dual_alert",
        "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
        "external_benign_counterfactual_mix_classscore_dual_alert",
    }
    frozen_task_reuse = (
        args.algorithm_profile
        == "external_benign_frozen_binary_dual_alert"
    )
    external_surrogate_unknown = args.algorithm_profile in {
        "external_benign_unsw_oe_binary_alert",
        "external_benign_unsw_alert_only",
    }
    external_surrogate_outlier_exposure = (
        args.algorithm_profile == "external_benign_unsw_oe_binary_alert"
    )
    xgboost_dependency: dict[str, Any] | None = None
    if xgboost_behavior_alert:
        if args.xgboost_root is None:
            raise ValueError("XGBoost behavior profile requires package root")
        xgboost_root = args.xgboost_root.resolve()
        xgboost_init = xgboost_root / "xgboost" / "__init__.py"
        xgboost_library = (
            xgboost_root / "xgboost" / "lib" / "libxgboost.so"
        )
        if not xgboost_init.is_file() or not xgboost_library.is_file():
            raise ValueError("XGBoost package root is incomplete")
        xgboost_dependency = {
            "root": str(xgboost_root),
            "version": "2.1.4",
            "init_sha256": file_hash(xgboost_init),
            "library_sha256": file_hash(xgboost_library),
        }
    elif args.xgboost_root is not None:
        raise ValueError(
            "XGBoost package root is only valid for behavior profile"
        )
    external_cache: dict[str, Any] | None = None
    if external_benign:
        if (
            args.external_benign_cache is None
            or args.external_benign_cache_manifest is None
        ):
            raise ValueError(
                "external_benign profile requires cache and manifest"
            )
        external_path = args.external_benign_cache.resolve()
        external_manifest_path = (
            args.external_benign_cache_manifest.resolve()
        )
        external_manifest = json.loads(
            external_manifest_path.read_text(encoding="utf-8")
        )
        if external_manifest["cache_sha256"] != file_hash(external_path):
            raise ValueError("external benign cache hash differs from manifest")
        if external_manifest["samples"] != args.expected_external_samples:
            raise ValueError(
                f"external cache has {external_manifest['samples']} samples, "
                f"expected {args.expected_external_samples}"
            )
        if external_manifest["source_role"] != (
            "training_only_external_benign"
        ):
            raise ValueError("external cache role is not training-only benign")
        if external_manifest["source_capture_count"] != 24:
            raise ValueError("external cache must bind all 24 Active captures")
        if external_manifest["fine_to_family"] != {
            "Benign_Final": "Benign"
        }:
            raise ValueError("external cache label contract differs")
        external_cache = {
            "path": str(external_path),
            "sha256": file_hash(external_path),
            "manifest_path": str(external_manifest_path),
            "manifest_file_sha256": file_hash(external_manifest_path),
            "manifest_sha256": external_manifest["manifest_sha256"],
            "samples": external_manifest["samples"],
            "source_capture_count": external_manifest[
                "source_capture_count"
            ],
            "source_dataset": external_manifest["source_dataset"],
            "source_experiment": external_manifest["source_experiment"],
            "source_role": external_manifest["source_role"],
            "capture_group_binding": external_manifest[
                "capture_group_binding"
            ],
            "modalities": external_manifest["modalities"],
        }
    external_surrogate_cache: dict[str, Any] | None = None
    if external_surrogate_unknown:
        if (
            args.external_surrogate_unknown_cache is None
            or args.external_surrogate_unknown_cache_manifest is None
        ):
            raise ValueError(
                "UNSW outlier-exposure profile requires cache and manifest"
            )
        surrogate_path = args.external_surrogate_unknown_cache.resolve()
        surrogate_manifest_path = (
            args.external_surrogate_unknown_cache_manifest.resolve()
        )
        surrogate_manifest = json.loads(
            surrogate_manifest_path.read_text(encoding="utf-8")
        )
        if surrogate_manifest["cache_sha256"] != file_hash(surrogate_path):
            raise ValueError(
                "external surrogate cache hash differs from manifest"
            )
        if surrogate_manifest["samples"] != (
            args.expected_external_surrogate_samples
        ):
            raise ValueError(
                "external surrogate cache sample count differs"
            )
        if surrogate_manifest["source_role"] != (
            "training_only_external_surrogate_unknown"
        ):
            raise ValueError(
                "external surrogate cache role is not training-only"
            )
        if surrogate_manifest["source_dataset"] != "UNSW-NB15":
            raise ValueError("external surrogate source dataset differs")
        if surrogate_manifest["claim_boundary"].get(
            "target_ciciot2023_test_unknown_labels_accessed"
        ) is not False:
            raise ValueError(
                "external surrogate cache lacks target-label isolation"
            )
        forbidden = {"ddos", "dos", "mirai"}
        overlap = sorted(
            category
            for category in surrogate_manifest["allowed_categories"]
            if category.casefold() in forbidden
        )
        if overlap:
            raise ValueError(
                "external surrogate categories overlap target families: "
                + ", ".join(overlap)
            )
        external_surrogate_cache = {
            "path": str(surrogate_path),
            "sha256": file_hash(surrogate_path),
            "manifest_path": str(surrogate_manifest_path),
            "manifest_file_sha256": file_hash(
                surrogate_manifest_path
            ),
            "manifest_sha256": surrogate_manifest["manifest_sha256"],
            "samples": surrogate_manifest["samples"],
            "samples_by_category": surrogate_manifest[
                "samples_by_category"
            ],
            "allowed_categories": surrogate_manifest[
                "allowed_categories"
            ],
            "source_dataset": surrogate_manifest["source_dataset"],
            "source_role": surrogate_manifest["source_role"],
            "capture_group_binding": surrogate_manifest[
                "capture_group_binding"
            ],
            "modalities": surrogate_manifest["modalities"],
            "source_file_count": len(
                surrogate_manifest["source_files"]
            ),
        }
    elif (
        args.external_surrogate_unknown_cache is not None
        or args.external_surrogate_unknown_cache_manifest is not None
    ):
        raise ValueError(
            "external surrogate cache is only valid for UNSW OE profile"
        )
    frozen_tasks: dict[str, Any] | None = None
    frozen_task_root: Path | None = None
    if frozen_task_reuse:
        if args.reuse_task_root is None:
            raise ValueError("frozen adapter profile requires reuse task root")
        frozen_task_root = args.reuse_task_root.resolve()
        frozen_tasks = {}
        for unknown_family in UNKNOWN_FAMILIES:
            slug = unknown_family.lower()
            task_dir = frozen_task_root / slug
            metrics_path = task_dir / "metrics.json"
            model_path = task_dir / "model.pt"
            calibrator_path = task_dir / "calibrator.json"
            for required_path in (
                metrics_path,
                model_path,
                calibrator_path,
            ):
                if not required_path.is_file():
                    raise ValueError(
                        f"frozen base task misses {required_path}"
                    )
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            if metrics["unknown_family"] != unknown_family:
                raise ValueError("frozen base task family differs")
            if metrics["seed"] != args.development_seed:
                raise ValueError("frozen base task seed differs")
            if metrics["state"] != "completed":
                raise ValueError("frozen base task is not completed")
            frozen_tasks[unknown_family] = {
                "task_dir": str(task_dir),
                "metrics_sha256": file_hash(metrics_path),
                "metrics_manifest_sha256": metrics["manifest_sha256"],
                "model_sha256": file_hash(model_path),
                "calibrator_sha256": file_hash(calibrator_path),
            }
    elif args.reuse_task_root is not None:
        raise ValueError("reuse task root is only valid for frozen adapter")
    elif not external_benign and (
        args.external_benign_cache is not None
        or args.external_benign_cache_manifest is not None
    ):
        raise ValueError(
            "external benign cache is only valid for external_benign profile"
        )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_development_protocol_v1"
        ),
        "state": "frozen_before_development_effects",
        "stage": "development",
        "algorithm": {
            "name": "CAEOS-EMTD heterogeneous PCAP evidential fusion",
            "architecture": (
                "byte_cnn_plus_packet_tcn_plus_packet_graph_gcn"
            ),
            "modalities": [
                "transport_payload_semantics",
                "packet_behavior_sequence",
                "packet_interaction_graph",
            ],
            "fusion": (
                "reliability_discounted_conflict_aware_dirichlet_"
                "with_bounded_counterfactual_attenuation"
                if counterfactual_mix
                else "reliability_discounted_conflict_aware_dirichlet"
            ),
            "unknown_risk": (
                "counterfactual_conflict_attenuated_uncertainty_conflict_distance_energy"
                if counterfactual_mix
                else "known_normalized_maximum_uncertainty_conflict_hierarchical_fine_distance_energy"
                if args.algorithm_profile == "hierarchical_fine_max"
                else "known_only_nested_pseudo_unknown_learned_hierarchical_risk"
                if nested_pseudo_risk
                else "fixed_uncertainty_conflict_hierarchical_fine_distance_energy"
                if hierarchical_fine
                else "fixed_uncertainty_conflict_distance_energy"
            ),
            "calibrator_profile": (
                "hierarchical_fine_max"
                if args.algorithm_profile == "hierarchical_fine_max"
                else "nested_pseudo_risk"
                if nested_pseudo_risk
                else "hierarchical_fine"
                if hierarchical_fine
                else "base"
            ),
            "fine_contrastive_training": fine_contrastive,
            "nested_pseudo_risk_learning": nested_pseudo_risk,
            "counterfactual_cross_family_modality_exposure": (
                counterfactual_mix
            ),
            "counterfactual_conflict_gate": counterfactual_mix,
            "external_benign_training_augmentation": external_benign,
            "external_surrogate_unknown_outlier_exposure": (
                external_surrogate_outlier_exposure
            ),
            "model_source": (
                "frozen_completed_development_checkpoint"
                if frozen_task_reuse
                else "fresh_training"
            ),
            "engineering_alert": (
                "gpu_xgboost_packet_behavior_graph_and_fused_evidence_head"
                if xgboost_behavior_alert
                else "benign_calibrated_one_minus_benign_probability_plus_known_only_oof_crossfit_and_known_only_selected_risk_component"
                if component_select_dual_alert
                else "benign_calibrated_one_minus_benign_probability_plus_known_only_oof_crossfit_risk_and_maliciousness"
                if classscore_dual_alert
                else "known_only_oof_selected_high_capacity_or_family_invariant_crossfit_plus_binary_risk_and_maliciousness"
                if family_crossfit_meta_select
                else "family_invariant_multimodal_summary_leave_one_family_out_crossfit_plus_binary_risk_and_maliciousness"
                if family_crossfit_dual_alert
                else "known_and_external_surrogate_binary_embedding_head"
                if external_surrogate_unknown
                else "benign_embedding_cosine_5nn"
                if benign_knn_alert
                else "known_only_binary_head_plus_benign_calibrated_risk_and_maliciousness"
                if binary_dual_alert
                else "known_only_binary_embedding_head"
                if binary_head_alert
                else "dual_risk_malicious"
            ),
            "risk_aggregation": (
                "maximum"
                if args.algorithm_profile == "hierarchical_fine_max"
                else "weighted_mean"
            ),
        },
        "cache": {
            "path": str(cache),
            "sha256": file_hash(cache),
            "manifest_path": str(cache_manifest_path),
            "manifest_file_sha256": file_hash(cache_manifest_path),
            "manifest_sha256": cache_manifest["manifest_sha256"],
            "samples": cache_manifest["samples"],
            "capture_group_binding": (
                cache_manifest["capture_group_binding"]
            ),
            "source_files": len(cache_manifest["source_files"]),
            "modalities": cache_manifest["modalities"],
            "external_training_benign": external_cache,
            "external_training_surrogate_unknown": (
                external_surrogate_cache
            ),
        },
        "protocol": {
            "development_seed": args.development_seed,
            "confirmation_seeds": [331, 337, 347],
            "confirmation_seed_access": (
                "forbidden_until_development_full_gate_passes"
            ),
            "unknown_families": list(UNKNOWN_FAMILIES),
            "expected_task_count": len(UNKNOWN_FAMILIES),
            "split": "source_pcap_capture_grouped_family_held_out",
            "external_benign_split": (
                "training_only_primary_validation_and_test_unchanged"
                if external_benign
                else "disabled"
            ),
            "external_surrogate_split": (
                "training_only_not_in_known_prototypes_or_thresholds"
                if external_surrogate_unknown
                else "disabled"
            ),
            "unknown_labels_used_for_training_or_threshold": False,
            "frozen_base_tasks": frozen_tasks,
        },
        "training": {
            "epochs": 80,
            "patience": 12,
            "batch_size": 512,
            "hidden_dim": 128,
            "embedding_dim": 96,
            "learning_rate": 0.0003,
            "calibrator_profile": (
                "hierarchical_fine_max"
                if args.algorithm_profile == "hierarchical_fine_max"
                else "nested_pseudo_risk"
                if nested_pseudo_risk
                else "hierarchical_fine"
                if hierarchical_fine
                else "base"
            ),
            "fine_contrastive_weight": 0.10 if fine_contrastive else 0.0,
            "fine_contrastive_temperature": 0.10,
            "counterfactual_mix_weight": (
                0.10 if counterfactual_mix else 0.0
            ),
            "counterfactual_evidence_weight": 0.05,
            "counterfactual_malicious_weight": 0.50,
            "counterfactual_modality_schedule": (
                "epoch_plus_batch_round_robin"
                if counterfactual_mix
                else "disabled"
            ),
            "counterfactual_checkpoint_selection": (
                "0.4_macro_f1_plus_0.4_balanced_accuracy_plus_"
                "0.1_counterfactual_uncertainty_plus_"
                "0.1_counterfactual_malicious_probability"
                if counterfactual_mix
                else "closed_set_macro_f1_and_balanced_accuracy"
            ),
            "risk_weight_steps": 400,
            "risk_weight_batch_size": 512,
            "risk_weight_margin": 0.10,
            "risk_weight_regularization": 0.05,
            "risk_selector_seed_offset": 100003,
            "maximum_parallel_tasks": 3,
            "formal_training_on_gpu_server_only": True,
            "reproducible_cuda_runtime": {
                "torch_deterministic_algorithms": True,
                "cudnn_deterministic": True,
                "cudnn_benchmark": False,
                "cuda_matmul_allow_tf32": True,
                "cudnn_allow_tf32": True,
                "cublas_workspace_config": ":4096:8",
            },
            "external_training_benign_enabled": external_benign,
            "external_surrogate_unknown_enabled": (
                external_surrogate_unknown
            ),
            "external_surrogate_weight": (
                0.10 if external_surrogate_outlier_exposure else 0.0
            ),
            "external_surrogate_evidence_weight": 0.05,
            "external_surrogate_malicious_weight": 0.50,
            "external_surrogate_binary_head_attack_augmentation": (
                external_surrogate_unknown
            ),
            "reuse_task_root": (
                str(frozen_task_root)
                if frozen_task_root is not None
                else None
            ),
            "alert_profile": (
                "xgboost_behavior_head"
                if xgboost_behavior_alert
                else "family_crossfit_meta_select_classscore_component_dual_alert"
                if component_select_dual_alert
                else "family_crossfit_meta_select_classscore_dual_alert"
                if classscore_dual_alert
                else "family_crossfit_meta_select_dual_alert"
                if family_crossfit_meta_select
                else "family_crossfit_dual_alert"
                if family_crossfit_dual_alert
                else "benign_knn"
                if benign_knn_alert
                else "binary_dual_alert"
                if binary_dual_alert
                else "binary_head"
                if binary_head_alert
                else "dual_risk_malicious"
            ),
            "benign_knn_k": 5,
            "benign_knn_false_positive_budget": 0.04,
            "binary_head_seed_offset": 200003,
            "binary_head_hidden_dim": 64,
            "binary_head_steps": 400,
            "binary_head_batch_size": 1024,
            "binary_head_learning_rate": 0.001,
            "binary_head_weight_decay": 0.0001,
            "binary_head_false_positive_budget": (
                0.01 if binary_dual_alert else 0.04
            ),
            "auxiliary_alert_branch_false_positive_budget": 0.015,
            "family_crossfit_false_positive_budget": (
                0.005 if family_crossfit_dual_alert else 0.0
            ),
            "family_crossfit_checkpoint_interval": 25,
            "family_crossfit_meta_validation": (
                "leave_one_known_attack_family_out_with_capture_disjoint_validation"
                if family_crossfit_dual_alert
                else "disabled"
            ),
            "family_crossfit_features": (
                "known_only_oof_selection_between_high_capacity_and_family_invariant_multimodal_profiles"
                if family_crossfit_meta_select
                else "payload_statistical_semantics_packet_behavior_graph_adjacency_and_evidence_quality_summaries"
                if family_crossfit_dual_alert
                else "disabled"
            ),
            "family_crossfit_meta_selector": (
                "oof_worst_recall_then_mean_recall_then_lower_capacity"
                if family_crossfit_meta_select
                else "disabled"
            ),
            "primary_attack_score": (
                "one_minus_benign_probability"
                if classscore_dual_alert
                else "binary_embedding_head"
                if binary_head_alert
                else "disabled"
            ),
            "known_only_risk_component_selector": (
                "known_attack_validation_worst_recall_then_mean_recall_then_fixed_priority"
                if component_select_dual_alert
                else "disabled"
            ),
            "known_only_risk_component_candidates": (
                [
                    "risk",
                    "uncertainty",
                    "conflict",
                    "distance",
                    "energy",
                ]
                if component_select_dual_alert
                else []
            ),
            "xgboost_behavior_estimators": 800,
            "xgboost_behavior_max_depth": 8,
            "xgboost_behavior_learning_rate": 0.05,
            "xgboost_behavior_early_stopping_rounds": 40,
            "xgboost_behavior_jobs": 20,
            "xgboost_behavior_false_positive_budget": 0.04,
            "xgboost_root": (
                xgboost_dependency["root"]
                if xgboost_dependency is not None
                else None
            ),
        },
        "execution": {
            "required_gpu_uuid": GPU_UUID,
            "minimum_end_to_end_gpu_mean_percent": 50.0,
            "preferred_end_to_end_gpu_mean_percent": 80.0,
            "gpu_sample_interval_seconds": 0.2,
            "exclusive_gpu_preflight_required": True,
            "reproducible_cuda_runtime_required": True,
        },
        "evaluation": {
            "three_layers": {
                "known": [
                    "known_macro_f1",
                    "known_accuracy",
                    "known_balanced_accuracy",
                ],
                "unknown": [
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                    "unknown_f1",
                ],
                "joint": ["oscr"],
                "calibration": ["ece", "brier_score"],
            },
            "safety_target": {
                "alert_accuracy_minimum": 0.95,
                "alert_precision_minimum": 0.95,
                "attack_recall_minimum": 0.95,
                "benign_fpr_strictly_below": 0.05,
                "known_attack_type_accuracy_minimum": 0.95,
                "unknown_attack_alert_recall_minimum": 0.95,
                "unknown_label_recall_minimum": 0.95,
            },
            "paper_open_set_target": {
                "known_macro_f1_minimum": 0.95,
                "unknown_auroc_minimum": 0.95,
                "unknown_aupr_minimum": 0.95,
                "unknown_fpr95_strictly_below": 0.05,
                "oscr_minimum": 0.90,
            },
            "all_three_unknown_family_tasks_must_pass": True,
        },
        "paths": {
            "project_root": str(project_root),
            "run_root": str(args.run_root.resolve()),
            "result_root": str(args.result_root.resolve()),
        },
        "runtime_dependencies": {
            "xgboost": xgboost_dependency,
        },
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATIONS
        },
        "claim_boundary": {
            "development_only": True,
            "unknown_family_excluded_from_train_and_validation": True,
            "thresholds_known_validation_only": True,
            "fine_prototypes_known_training_only": True,
            "nested_pseudo_unknowns_known_fine_labels_only": True,
            "capture_groups_source_pcap_disjoint": True,
            "source_full_pcap_hashes_not_computed": True,
            "external_source_full_hashes_inherited_from_independent_audit": (
                external_benign
            ),
            "external_benign_training_only": external_benign,
            "external_surrogate_unknown_training_only": (
                external_surrogate_unknown
            ),
            "external_surrogate_not_in_known_prototypes": True,
            "external_surrogate_not_in_threshold_fit": True,
            "xgboost_runtime_binary_hash_frozen": (
                xgboost_behavior_alert
            ),
            "primary_validation_and_test_unchanged": True,
            "engineering_alert_thresholds_known_benign_validation_only": True,
            "family_crossfit_true_unknown_never_used": True,
            "family_crossfit_pseudo_unknowns_known_families_only": (
                family_crossfit_dual_alert
            ),
            "family_crossfit_omitted_family_not_used_by_its_head": (
                family_crossfit_dual_alert
            ),
            "family_crossfit_selector_true_unknown_scores_used": False,
            "classification_attack_score_threshold_known_benign_only": (
                classscore_dual_alert
            ),
            "risk_component_selector_known_attack_validation_only": (
                component_select_dual_alert
            ),
            "risk_component_selector_true_unknown_scores_used": False,
            "counterfactuals_known_attack_training_only": (
                counterfactual_mix
            ),
            "counterfactual_validation_known_attack_families_only": (
                counterfactual_mix
            ),
            "counterfactual_true_unknown_used_for_training": False,
            "counterfactual_true_unknown_used_for_checkpoint_selection": False,
            "cache_hash_and_source_prefix_hashes_frozen": True,
            "fresh_confirmation_required_after_full_gate": True,
            "frozen_model_calibrator_and_split_reused": frozen_task_reuse,
            "sota_claim_not_permitted_by_this_stage": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--cache-manifest", type=Path, required=True)
    parser.add_argument("--external-benign-cache", type=Path)
    parser.add_argument("--external-benign-cache-manifest", type=Path)
    parser.add_argument("--xgboost-root", type=Path)
    parser.add_argument("--external-surrogate-unknown-cache", type=Path)
    parser.add_argument(
        "--external-surrogate-unknown-cache-manifest",
        type=Path,
    )
    parser.add_argument("--expected-samples", type=int, default=19456)
    parser.add_argument("--expected-external-samples", type=int, default=1536)
    parser.add_argument(
        "--expected-external-surrogate-samples",
        type=int,
        default=768,
    )
    parser.add_argument("--development-seed", type=int, default=283)
    parser.add_argument(
        "--algorithm-profile",
        choices=(
            "base",
            "hierarchical_fine",
            "hierarchical_fine_contrastive",
            "hierarchical_fine_max",
            "nested_pseudo_risk",
            "external_benign",
            "external_benign_knn_alert",
            "external_benign_binary_alert",
            "external_benign_binary_dual_alert",
            "external_benign_frozen_binary_dual_alert",
            "external_benign_unsw_oe_binary_alert",
            "external_benign_unsw_alert_only",
            "external_benign_xgboost_behavior_alert",
            "external_benign_family_crossfit_dual_alert",
            "external_benign_family_crossfit_meta_select_dual_alert",
            "external_benign_family_crossfit_meta_select_classscore_dual_alert",
            "external_benign_family_crossfit_meta_select_classscore_component_dual_alert",
            "external_benign_counterfactual_mix_classscore_dual_alert",
        ),
        default="base",
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--reuse-task-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite frozen protocol: {output}")
    result_root = args.result_root.resolve()
    if any(
        (result_root / name).exists()
        for name in ("completion.json", "evaluation.json")
    ):
        raise ValueError("development effects exist before protocol freeze")
    protocol = build_protocol(args)
    atomic_json(output, protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
