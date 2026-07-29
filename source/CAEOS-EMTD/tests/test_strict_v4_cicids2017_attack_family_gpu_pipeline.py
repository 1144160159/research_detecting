from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_cicids2017_attack_family_gpu_protocol import (
    DEVELOPMENT_STATE,
    GPU_UUID,
    build_protocol,
)
from run_strict_v4_cicids2017_attack_family_gpu_matrix import (
    verify_gpu_task,
    xgboost_cuda_command,
)
from strict_v4_cicids2017_attack_family import canonical_hash


IMPLEMENTATIONS = (
    "strict_v4_cicids2017_attack_family.py",
    "create_strict_v4_cicids2017_attack_family_gpu_protocol.py",
    "run_strict_v4_cicids2017_attack_family_gpu_matrix.py",
    "launch_strict_v4_cicids2017_attack_family_gpu_matrix.py",
    "evaluate_strict_v4_cicids2017_attack_family_gpu_hybrid.py",
    "evaluate_strict_v4_hybrid_self_algorithm_development.py",
    "train_hybrid_open_set.py",
    "train_strict_v4_xgboost_warning_task.py",
    "train_strict_v4_xgboost_warning_task_cuda.py",
    "verify_xgboost_cuda_backend.py",
)


def project_inputs(tmp_path: Path) -> tuple[Path, Path]:
    for name in IMPLEMENTATIONS:
        (tmp_path / name).write_text(name, encoding="utf-8")
    source = tmp_path / "source.csv"
    source.write_text("Label,Feature\nBenign,1\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")
    return source, config


def development_protocol(tmp_path: Path) -> dict:
    source, config = project_inputs(tmp_path)
    return build_protocol(
        project_root=tmp_path,
        stage="development",
        source_csv=source,
        config_path=config,
        cache_root=tmp_path / "cache",
        run_root=tmp_path / "runs",
        result_root=tmp_path / "results",
    )


def test_gpu_development_protocol_freezes_new_seed_and_backend(
    tmp_path: Path,
) -> None:
    protocol = development_protocol(tmp_path)
    declared = protocol.pop("manifest_sha256")
    assert canonical_hash(protocol) == declared
    assert protocol["seeds"] == [17]
    assert protocol["expected_task_count"] == 7
    assert protocol["xgboost_known_expert"]["execution_backend"] == "cuda"
    assert protocol["xgboost_known_expert"]["required_gpu_uuid"] == GPU_UUID
    assert protocol["claim_boundary"]["all_model_training_is_gpu"] is False
    assert protocol["claim_boundary"]["pairwise_caeos_component_uses_cpu"] is True


def test_confirmation_freezes_development_configuration(tmp_path: Path) -> None:
    source, config = project_inputs(tmp_path)
    development = {
        "schema_version": "test_development_v1",
        "state": DEVELOPMENT_STATE,
        "selected": {
            "configuration": {
                "alert_variant": "tail_noisy_or",
                "alert_budget": 0.04,
                "open_variant": "tail_noisy_or",
                "open_budget": 0.04,
            }
        },
        "gpu_execution": {"all_tasks_passed": True},
        "claim_boundary": {"authorized_level": "attack_family"},
    }
    development["manifest_sha256"] = canonical_hash(development)
    development_path = tmp_path / "development.json"
    development_path.write_text(
        json.dumps(development, sort_keys=True), encoding="utf-8"
    )
    protocol = build_protocol(
        project_root=tmp_path,
        stage="confirmation",
        source_csv=source,
        config_path=config,
        cache_root=tmp_path / "confirmation_cache",
        run_root=tmp_path / "confirmation_runs",
        result_root=tmp_path / "confirmation_results",
        development_result_path=development_path,
    )
    assert protocol["seeds"] == [953, 967, 971]
    assert protocol["selected_configuration"] == development["selected"][
        "configuration"
    ]
    assert protocol["selection_source"]["selection_seed"] == 17


def test_xgboost_command_uses_cuda_wrapper(tmp_path: Path) -> None:
    protocol = development_protocol(tmp_path)
    command = xgboost_cuda_command(
        python=Path("/python"),
        project_root=tmp_path,
        protocol=protocol,
        cache_path=Path("/cache.csv"),
        pairwise_dir=Path("/pairwise"),
        output_dir=Path("/xgboost"),
    )
    assert command[1].endswith(
        "train_strict_v4_xgboost_warning_task_cuda.py"
    )
    assert "--gpu-sample-interval-seconds" in command


def test_gpu_task_rejects_wrong_uuid(tmp_path: Path) -> None:
    protocol = development_protocol(tmp_path)
    evidence = {
        "schema_version": "strict_v4_xgboost_cuda_task_evidence_v1",
        "state": "complete",
        "requested_device": "cuda",
        "booster_device_values": ["cuda:0"],
        "gpu_identity": {"uuid": "wrong"},
        "peak_gpu_memory_mib": 100.0,
        "compute_process_observed_by_nvidia_smi": True,
        "passes": True,
    }
    evidence["manifest_sha256"] = canonical_hash(evidence)
    path = tmp_path / "gpu_execution.json"
    path.write_text(json.dumps(evidence, sort_keys=True), encoding="utf-8")
    with pytest.raises(ValueError, match="GPU evidence did not pass"):
        verify_gpu_task(protocol, tmp_path)
