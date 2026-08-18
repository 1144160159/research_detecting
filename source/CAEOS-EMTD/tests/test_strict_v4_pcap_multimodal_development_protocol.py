from __future__ import annotations

import argparse
import json
import unittest

from create_strict_v4_pcap_multimodal_development_protocol import (
    IMPLEMENTATIONS,
    build_protocol,
)
from evaluate_strict_v4_pcap_multimodal_development import gate
from strict_v4_cic_iot2023_attack_family import file_hash


class PcapMultimodalDevelopmentGateTest(unittest.TestCase):
    def test_gate_boundaries_match_95_5_contract(self) -> None:
        self.assertTrue(gate(0.95, "minimum", 0.95))
        self.assertFalse(gate(0.9499, "minimum", 0.95))
        self.assertTrue(gate(0.0499, "strict_maximum", 0.05))
        self.assertFalse(gate(0.05, "strict_maximum", 0.05))


def test_family_crossfit_profile_freezes_known_only_meta_protocol(
    tmp_path,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    for relative_path in IMPLEMENTATIONS:
        implementation = project_root / relative_path
        implementation.parent.mkdir(parents=True, exist_ok=True)
        implementation.write_text("# frozen test implementation\n")
    cache = tmp_path / "primary.npz"
    cache.write_bytes(b"primary")
    cache_manifest = tmp_path / "primary.manifest.json"
    cache_manifest.write_text(
        json.dumps(
            {
                "cache_sha256": file_hash(cache),
                "samples": 12,
                "capture_group_binding": "relative_source_pcap_path",
                "source_files": [{"path": "one.pcap"}],
                "modalities": ["payload", "sequence", "graph"],
                "manifest_sha256": "primary-manifest",
            }
        )
    )
    external_cache = tmp_path / "external.npz"
    external_cache.write_bytes(b"external")
    external_manifest = tmp_path / "external.manifest.json"
    external_manifest.write_text(
        json.dumps(
            {
                "cache_sha256": file_hash(external_cache),
                "samples": 8,
                "source_role": "training_only_external_benign",
                "source_capture_count": 24,
                "fine_to_family": {"Benign_Final": "Benign"},
                "manifest_sha256": "external-manifest",
                "source_dataset": "CICIoT2022",
                "source_experiment": "Active",
                "capture_group_binding": "relative_source_pcap_path",
                "modalities": ["payload", "sequence", "graph"],
            }
        )
    )
    args = argparse.Namespace(
        project_root=project_root,
        cache=cache,
        cache_manifest=cache_manifest,
        external_benign_cache=external_cache,
        external_benign_cache_manifest=external_manifest,
        xgboost_root=None,
        external_surrogate_unknown_cache=None,
        external_surrogate_unknown_cache_manifest=None,
        expected_samples=12,
        expected_external_samples=8,
        expected_external_surrogate_samples=0,
        development_seed=283,
        algorithm_profile=(
            "external_benign_family_crossfit_meta_select_classscore_dual_alert"
        ),
        run_root=tmp_path / "run",
        result_root=tmp_path / "results",
        reuse_task_root=None,
        output=tmp_path / "protocol.json",
    )

    protocol = build_protocol(args)

    assert protocol["training"]["alert_profile"] == (
        "family_crossfit_meta_select_classscore_dual_alert"
    )
    assert protocol["training"]["binary_head_false_positive_budget"] == 0.01
    assert protocol["training"]["family_crossfit_false_positive_budget"] == (
        0.005
    )
    assert protocol["claim_boundary"][
        "family_crossfit_true_unknown_never_used"
    ]
    assert protocol["claim_boundary"][
        "family_crossfit_omitted_family_not_used_by_its_head"
    ]
    assert protocol["claim_boundary"][
        "family_crossfit_selector_true_unknown_scores_used"
    ] is False
    assert protocol["claim_boundary"][
        "classification_attack_score_threshold_known_benign_only"
    ]
    assert protocol["training"]["reproducible_cuda_runtime"] == {
        "torch_deterministic_algorithms": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "cuda_matmul_allow_tf32": True,
        "cudnn_allow_tf32": True,
        "cublas_workspace_config": ":4096:8",
    }
    assert protocol["execution"][
        "reproducible_cuda_runtime_required"
    ]

    args.algorithm_profile = (
        "external_benign_family_crossfit_meta_select_"
        "classscore_component_dual_alert"
    )
    args.run_root = tmp_path / "component-run"
    args.result_root = tmp_path / "component-results"
    args.output = tmp_path / "component-protocol.json"
    component_protocol = build_protocol(args)

    assert component_protocol["training"]["alert_profile"] == (
        "family_crossfit_meta_select_classscore_component_dual_alert"
    )
    assert component_protocol["training"][
        "known_only_risk_component_selector"
    ] == (
        "known_attack_validation_worst_recall_then_mean_recall_"
        "then_fixed_priority"
    )
    assert component_protocol["claim_boundary"][
        "risk_component_selector_known_attack_validation_only"
    ]
    assert component_protocol["claim_boundary"][
        "risk_component_selector_true_unknown_scores_used"
    ] is False

    args.algorithm_profile = (
        "external_benign_counterfactual_mix_classscore_dual_alert"
    )
    args.run_root = tmp_path / "counterfactual-run"
    args.result_root = tmp_path / "counterfactual-results"
    args.output = tmp_path / "counterfactual-protocol.json"
    counterfactual_protocol = build_protocol(args)

    assert counterfactual_protocol["algorithm"][
        "counterfactual_cross_family_modality_exposure"
    ]
    assert counterfactual_protocol["algorithm"][
        "counterfactual_conflict_gate"
    ]
    assert counterfactual_protocol["training"][
        "counterfactual_mix_weight"
    ] == 0.10
    assert counterfactual_protocol["training"]["alert_profile"] == (
        "family_crossfit_meta_select_classscore_dual_alert"
    )
    assert counterfactual_protocol["claim_boundary"][
        "counterfactuals_known_attack_training_only"
    ]
    assert counterfactual_protocol["claim_boundary"][
        "counterfactual_true_unknown_used_for_training"
    ] is False
    assert counterfactual_protocol["claim_boundary"][
        "counterfactual_true_unknown_used_for_checkpoint_selection"
    ] is False


if __name__ == "__main__":
    unittest.main()
