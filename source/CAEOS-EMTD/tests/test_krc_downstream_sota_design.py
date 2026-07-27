from __future__ import annotations

from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_downstream_sota_design import create


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures():
    krc = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_protocol_v1"
            ),
            "execution_admitted": True,
            "source_registry_count": 102,
            "confirmation": {
                "full_task_count": 306,
                "tasks": [
                    {
                        "suite": "ustc_tfc2016",
                        "scenario": f"family_{scenario}",
                        "training_seed": seed,
                    }
                    for scenario in range(10)
                    for seed in (647, 653, 659)
                ],
            },
        }
    )
    external = canonical(
        {
            "schema_version": (
                "gpu_external_dataset_evaluation_design_protocol_v1"
            ),
            "datasets": ["LSNM2024", "CICDDoS2019"],
            "seeds": [223, 227, 229],
            "scenario_rule": "leave_attack_family_out",
            "split_rule": "fingerprint_grouped",
            "confirmation_gate": {"all_metrics_positive": True},
        }
    )
    parrot = canonical(
        {
            "schema_version": (
                "parrot2025_external_benign_safety_design_v1"
            ),
            "population": {"captures": 320, "applications": 80},
            "confirmation_gate": {"false_alert_upper": 0.1},
        }
    )
    features = canonical(
        {
            "schema_version": (
                "parrot2025_full_no_decryption_feature_protocol_v1"
            ),
            "capture_count": 320,
            "application_count": 80,
            "feature_count": 56,
            "formal_model_metric_count_at_freeze": 0,
            "safety_policy": {"payload_decryption": False},
        }
    )
    efficiency = canonical(
        {
            "schema_version": "strict_v4_final_efficiency_protocol_v2",
            "inference_benchmark": {
                "batch_sizes": [1, 64, 512],
                "warmup_repetitions": 5,
                "timed_repetitions": 30,
                "reported_metrics": ["latency_p99_ms", "throughput"],
            },
        }
    )
    comparative = canonical(
        {
            "schema_version": (
                "strict_v4_comparative_corruption_protocol_v2"
            ),
            "source_registry": [
                {
                    "suite": f"suite_{index // 17}",
                    "scenario": f"scenario_{index}",
                    "seed": 137,
                }
                for index in range(102)
            ],
        }
    )
    return krc, external, parrot, features, efficiency, comparative


def test_design_freezes_all_three_downstream_evidence_roles() -> None:
    values = fixtures()
    design = create(
        project_root=Path("/project"),
        krc_protocol=values[0],
        external_design=values[1],
        parrot_design=values[2],
        parrot_features=values[3],
        efficiency_protocol=values[4],
        comparative_protocol=values[5],
        observed_counts={
            "external_metrics": 0,
            "parrot_metrics": 0,
            "system_benchmark": 0,
            "summary": 0,
            "audit": 0,
        },
        input_file_sha256={"fixture": "0" * 64},
        creator_sha256="1" * 64,
    )
    assert design["manifest_sha256"] == canonical_hash(design)
    assert design["execution_admitted"] is False
    assert design["fresh_external_malicious"]["datasets"] == [
        "LSNM2024",
        "CICDDoS2019",
    ]
    assert (
        design["parrot2025_external_benign_safety"][
            "malicious_accuracy_or_sota_claim"
        ]
        is False
    )
    assert (
        design["selected_system_and_efficiency"]["source_candidate_capture_count"]
        == 306
    )


def test_design_rejects_any_existing_downstream_output() -> None:
    values = fixtures()
    with pytest.raises(ValueError, match="before downstream outputs"):
        create(
            project_root=Path("/project"),
            krc_protocol=values[0],
            external_design=values[1],
            parrot_design=values[2],
            parrot_features=values[3],
            efficiency_protocol=values[4],
            comparative_protocol=values[5],
            observed_counts={
                "external_metrics": 1,
                "parrot_metrics": 0,
                "system_benchmark": 0,
                "summary": 0,
                "audit": 0,
            },
            input_file_sha256={"fixture": "0" * 64},
            creator_sha256="1" * 64,
        )
