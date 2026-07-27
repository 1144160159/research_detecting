from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
import run_strict_v4_selected_system_parrot_safety as target


def canonical(value: dict[str, Any]) -> dict[str, Any]:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def activation(selected: str, design: dict[str, Any]) -> dict[str, Any]:
    snapshot = {"final": True, "selected_algorithm": selected}
    return canonical(
        {
            "schema_version": "strict_v4_selected_system_activation_v1",
            "execution_admitted": True,
            "selected_algorithm": selected,
            "selection_snapshot": snapshot,
            "selection_snapshot_sha256": canonical_hash(snapshot),
            "input_manifest_sha256": {
                "adapter_design": design["manifest_sha256"]
            },
        }
    )


def adapter_design() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": (
                "strict_v4_selected_system_downstream_adapter_design_v1"
            ),
            "activation": {
                "allowed_selected_algorithms": list(target.ALGORITHMS)
            },
        }
    )


def safety_design() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": (
                "parrot2025_external_benign_safety_design_v1"
            ),
            "dataset_role": (
                "external_benign_mobile_application_domain_shift_safety_only"
            ),
            "artifact_contract": {
                "parrot_used_for_training_validation_or_calibration": False
            },
            "confirmation_gate": {
                "all_320_captures_and_80_applications_covered": True,
                "applications_with_false_alert_rate_at_most_0_20_minimum_fraction": 0.9,
                "candidate_false_alert_minus_source_benign_95ci_upper_maximum": 0.05,
                "candidate_false_alert_rate_bootstrap_95ci_upper_maximum": 0.1,
                "candidate_known_attack_assignment_95ci_upper_maximum": 0.05,
                "candidate_minus_opendetect_false_alert_95ci_upper_maximum": 0.02,
                "failure_count_zero": True,
                "forbidden_fit_selection_or_threshold_use_observed": False,
            },
        }
    )


def confirmation() -> dict[str, Any]:
    tasks = []
    for scenario_index in range(10):
        for seed, corruption in zip(
            (647, 653, 659), (661, 673, 677)
        ):
            tasks.append(
                {
                    "suite": "ustc_tfc2016",
                    "scenario": f"scenario_{scenario_index}",
                    "training_seed": seed,
                    "corruption_seed": corruption,
                }
            )
    return canonical(
        {
            "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
            "confirmation": {"tasks": tasks},
        }
    )


def comparative() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": "strict_v4_comparative_corruption_protocol_v2"
        }
    )


def features(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    captures = [
        {
            "capture_id": f"capture_{index:03d}",
            "application": f"app_{index // 4:02d}",
        }
        for index in range(320)
    ]
    protocol = canonical(
        {
            "schema_version": (
                "parrot2025_full_no_decryption_feature_protocol_v1"
            ),
            "output_root": str(root / "features"),
            "feature_columns": [f"feature_{index}" for index in range(56)],
            "metadata_columns": ["capture_id"],
            "captures": captures,
        }
    )
    summary = canonical(
        {
            "schema_version": (
                "parrot2025_full_no_decryption_feature_summary_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "passed": True,
            "validation": {
                "all_captures": True,
                "column_order": True,
                "no_decryption": True,
            },
            "capture_count": 320,
            "application_count": 80,
            "shard_manifest_sha256": {
                capture["capture_id"]: "a" * 64 for capture in captures
            },
        }
    )
    return protocol, summary


def base_arguments(seed: int) -> list[str]:
    return [
        "--csv",
        "/data/ustc.csv",
        "--config",
        "/data/ustc.json",
        "--unknown-classes",
        "scenario",
        "--benign-class",
        "Benign",
        "--split-strategy",
        "capture_grouped",
        "--jobs",
        "8",
        "--risk-selection",
        "old",
        "--seed",
        str(seed),
        "--output-dir",
        "/old",
    ]


def model_pairs() -> list[dict[str, Any]]:
    values = []
    for scenario_index in range(10):
        for seed in (647, 653, 659):
            values.append(
                {
                    "suite": "ustc_tfc2016",
                    "scenario": f"scenario_{scenario_index}",
                    "training_seed": seed,
                    "clean_trainer_arguments": base_arguments(seed),
                    "csv": "/data/ustc.csv",
                    "csv_sha256": "1" * 64,
                    "config": "/data/ustc.json",
                    "config_sha256": "2" * 64,
                    "source_split_fingerprint": f"{scenario_index:02d}{seed}"
                    .ljust(64, "f"),
                    "opendetect_runtime": f"/models/{scenario_index}_{seed}.joblib",
                    "opendetect_runtime_sha256": "3" * 64,
                    "opendetect_threshold": 0.5,
                }
            )
    return values


def prepare(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected: str,
) -> dict[str, Path]:
    implementation = root / "implementation.py"
    implementation.write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(
        target, "IMPLEMENTATION_FILES", ("implementation.py",)
    )
    monkeypatch.setattr(
        target, "build_model_pairs", lambda **_: model_pairs()
    )
    design = adapter_design()
    values = {
        "activation": activation(selected, design),
        "design": design,
        "safety": safety_design(),
        "confirmation": confirmation(),
        "comparative": comparative(),
    }
    feature_protocol, feature_summary = features(root)
    values["feature_protocol"] = feature_protocol
    values["feature_summary"] = feature_summary
    paths = {}
    for name, value in values.items():
        path = root / f"{name}.json"
        write(path, value)
        paths[name] = path
    return paths


def create(
    root: Path,
    paths: dict[str, Path],
) -> dict[str, Any]:
    return target.create_protocol(
        project_root=root,
        run_root=root / "run",
        activation_path=paths["activation"],
        adapter_design_path=paths["design"],
        safety_design_path=paths["safety"],
        confirmation_protocol_path=paths["confirmation"],
        confirmation_capture_root=root / "captures",
        comparative_protocol_path=paths["comparative"],
        comparative_run_root=root / "comparative_run",
        feature_protocol_path=paths["feature_protocol"],
        feature_summary_path=paths["feature_summary"],
    )


@pytest.mark.parametrize("selected", target.ALGORITHMS)
def test_protocol_binds_all_four_selected_algorithms(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected: str,
) -> None:
    paths = prepare(tmp_path, monkeypatch, selected)
    protocol = create(tmp_path, paths)
    assert protocol["manifest_sha256"] == canonical_hash(protocol)
    assert protocol["selected_algorithm"] == selected
    assert len(protocol["source_model_pairs"]) == 30
    assert len(protocol["parrot_captures"]) == 320
    assert protocol["claim_boundary"][
        "all_algorithms_use_same_ustc_source_matrix"
    ]
    assert protocol["candidate_training"][
        "fresh_refit_per_source_split"
    ]
    backend = protocol["candidate_training"]["rrc_backend_protocol"]
    if selected == "rrc_csr_caeos_v1":
        assert backend["manifest_sha256"] == canonical_hash(backend)
        assert len(backend["tasks"]) == 30
    else:
        assert backend is None


@pytest.mark.parametrize(
    ("selected", "script", "capture_fragment"),
    [
        ("caeos_pairwise", "capture_pairwise_runtime.py", "candidate_capture"),
        ("caeos_pug", "capture_pairwise_runtime.py", "candidate_capture"),
        (
            "krc_csr_caeos_v1",
            "capture_krc_csr_confirmation_runtime.py",
            "candidate_capture",
        ),
        (
            "rrc_csr_caeos_v1",
            "capture_csr_caeos_runtime.py",
            "source_csr_capture",
        ),
    ],
)
def test_candidate_command_uses_selected_backend_and_frozen_split_arguments(
    tmp_path: Path,
    selected: str,
    script: str,
    capture_fragment: str,
) -> None:
    source = model_pairs()[0]
    protocol = {
        "selected_algorithm": selected,
        "candidate_training": {
            "pairwise_runtime_policy": target.pairwise_policy(selected),
            "robust_runtime_policy": {
                "augmentation_weight": 0.5,
                "training_sample_fraction": 0.25,
                "health_quantile": 0.99,
            },
        },
        "resource_contract": {"candidate_fit_jobs_per_worker": 8},
    }
    source["augmentation_seed"] = source["training_seed"]
    source["corruption_seed"] = 661
    command = target.candidate_capture_command(
        python="python",
        project_root=tmp_path,
        run_root=tmp_path / "run",
        protocol=protocol,
        source=source,
    )
    assert script in command[1]
    assert capture_fragment in " ".join(command)
    assert "capture_grouped" in command
    assert "/data/ustc.csv" in command
    assert str(source["training_seed"]) in command


def test_protocol_rejects_incomplete_feature_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = prepare(tmp_path, monkeypatch, "caeos_pairwise")
    summary = json.loads(paths["feature_summary"].read_text(encoding="utf-8"))
    summary["passed"] = False
    summary["manifest_sha256"] = canonical_hash(summary)
    write(paths["feature_summary"], summary)
    with pytest.raises(ValueError, match="activation/feature gate"):
        create(tmp_path, paths)


def test_main_without_activation_is_read_only_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "protocol.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            target.__file__,
            "--project-root",
            str(tmp_path),
            "--activation",
            "missing.json",
            "--protocol",
            str(output),
        ],
    )
    target.main()
    assert json.loads(capsys.readouterr().out) == {
        "protocol_written": False,
        "state": "pending_selected_system_activation",
    }
    assert not output.exists()


def test_main_without_feature_summary_is_read_only_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    activation_path = tmp_path / "activation.json"
    write(activation_path, {"present": True})
    output = tmp_path / "protocol.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            target.__file__,
            "--project-root",
            str(tmp_path),
            "--activation",
            str(activation_path),
            "--feature-summary",
            "missing.json",
            "--protocol",
            str(output),
        ],
    )
    target.main()
    assert json.loads(capsys.readouterr().out) == {
        "protocol_written": False,
        "state": "pending_parrot_feature_summary",
    }
    assert not output.exists()


def test_candidate_arguments_replace_policy_without_changing_source_split(
    tmp_path: Path,
) -> None:
    source = model_pairs()[0]
    protocol = {
        "candidate_training": {
            "pairwise_runtime_policy": target.pairwise_policy("caeos_pug")
        },
        "resource_contract": {"candidate_fit_jobs_per_worker": 8},
    }
    arguments = target.candidate_arguments(
        source, protocol, tmp_path / "output"
    )
    assert arguments[arguments.index("--split-strategy") + 1] == (
        "capture_grouped"
    )
    assert arguments[arguments.index("--csv") + 1] == "/data/ustc.csv"
    assert arguments[arguments.index("--risk-selection") + 1] == (
        target.pairwise_policy("caeos_pug")["risk_selection"]
    )
    assert arguments[arguments.index("--output-dir") + 1] == str(
        tmp_path / "output"
    )


def test_validate_source_capture_rejects_split_fingerprint_splicing(
    tmp_path: Path,
) -> None:
    source = model_pairs()[0]
    source["corruption_seed"] = 661
    source["augmentation_seed"] = source["training_seed"]
    protocol = {
        "selected_algorithm": "caeos_pairwise",
        "candidate_training": {
            "pairwise_runtime_policy": target.pairwise_policy(
                "caeos_pairwise"
            )
        },
        "resource_contract": {"candidate_fit_jobs_per_worker": 8},
    }
    block = target.block_path(tmp_path, source)
    capture = block / "candidate_capture"
    train = block / "source_train"
    capture.mkdir(parents=True)
    train.mkdir(parents=True)
    artifact = capture / "runtime.joblib"
    inputs = capture / "inputs.npz"
    artifact.write_bytes(b"runtime")
    inputs.write_bytes(b"inputs")
    write(
        capture / "capture_manifest.json",
        {
            "schema_version": "strict_v4_pairwise_runtime_capture_v1",
            "deployment_artifact": artifact.name,
            "deployment_artifact_sha256": target.file_hash(artifact),
            "benchmark_inputs": inputs.name,
            "benchmark_inputs_sha256": target.file_hash(inputs),
            "benchmark_inputs_contain_labels": False,
            "trainer_arguments": target.candidate_arguments(
                source, protocol, train
            ),
            "runtime_evidence": {
                "selected_risk": protocol["candidate_training"][
                    "pairwise_runtime_policy"
                ]["expected_runtime_selected_risk"]
            },
            "equivalence": {"passes": True},
        },
    )
    write(
        train / "metrics.json",
        {
            "split_metadata": {
                "split_fingerprint": "different-split"
            }
        },
    )
    with pytest.raises(ValueError, match="split fingerprint drifted"):
        target.validate_source_capture(protocol, tmp_path, source)
