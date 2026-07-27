from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pytest

from caeos.pseudo_unknown_gated_continuous import PUG_RISK_NAME
from create_strict_v4_external_confirmation_protocol import canonical_hash
import run_strict_v4_selected_system_external_malicious as target


def canonical(value: dict[str, Any]) -> dict[str, Any]:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def task(index: int) -> dict[str, Any]:
    dataset = "dataset_a" if index < 51 else "dataset_b"
    family_index = index // 3
    seed = (223, 227, 229)[index % 3]
    return {
        "dataset": dataset,
        "unknown_attack_family": f"family_{family_index}",
        "training_seed": seed,
        "prepared_seed": seed,
        "split_seed": seed,
        "opendetect_seed": seed,
        "augmentation_seed": 1000 + index,
        "validation_profile_seed": 2000 + index,
        "csv": f"/data/{dataset}_{seed}.csv",
        "csv_sha256": "a" * 64,
        "sidecar": f"/data/{dataset}_{seed}.csv.json",
        "sidecar_file_sha256": "b" * 64,
        "config": f"/data/{dataset}.json",
        "config_sha256": "c" * 64,
        "benign_label": "BENIGN",
    }


def frozen_inputs() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": (
                "strict_v4_krc_external_malicious_input_protocol_v2"
            ),
            "execution_admitted": False,
            "tasks": [task(index) for index in range(96)],
            "task_counts": {
                "dataset_a": 51,
                "dataset_b": 45,
                "attack_families": 32,
                "datasets": 2,
                "total_scenarios_per_algorithm": 96,
                "training_seeds": 3,
            },
            "dataset_registry": {
                "dataset_a": {},
                "dataset_b": {},
            },
            "confirmation_gate": {
                "all_four_label_block_bootstrap_95ci_lower_strictly_positive": (
                    True
                ),
                "all_four_oriented_means_strictly_positive": True,
                "all_four_wilcoxon_holm_p_below_0_05": True,
                "both_dataset_four_metric_means_nonnegative": True,
                "coverage_complete_and_failure_count_zero": True,
                "known_macro_f1_each_dataset_gain_minimum": -0.02,
                "known_macro_f1_mean_gain_minimum": -0.01,
                "unknown_or_test_labels_excluded_from_fit_selection_and_"
                "threshold": True,
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


def activation(
    selected: str, design: dict[str, Any]
) -> dict[str, Any]:
    snapshot = {
        "final": True,
        "selected_algorithm": selected,
    }
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


def prepare_files(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected: str,
) -> tuple[Path, Path, Path]:
    implementation = root / "implementation.py"
    implementation.write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(
        target, "IMPLEMENTATION_FILES", ("implementation.py",)
    )
    design = adapter_design()
    activation_value = activation(selected, design)
    inputs = frozen_inputs()
    activation_path = root / "activation.json"
    design_path = root / "design.json"
    input_path = root / "inputs.json"
    write(activation_path, activation_value)
    write(design_path, design)
    write(input_path, inputs)
    return activation_path, design_path, input_path


@pytest.mark.parametrize("selected", target.ALGORITHMS)
def test_create_protocol_binds_each_selected_algorithm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected: str,
) -> None:
    activation_path, design_path, input_path = prepare_files(
        tmp_path, monkeypatch, selected
    )
    protocol = target.create_protocol(
        project_root=tmp_path,
        run_root=tmp_path / "run",
        activation_path=activation_path,
        adapter_design_path=design_path,
        input_protocol_path=input_path,
    )
    assert protocol["manifest_sha256"] == canonical_hash(protocol)
    assert protocol["selected_algorithm"] == selected
    assert len(protocol["tasks"]) == 96
    assert protocol["task_counts"]["attack_families"] == 32
    if selected == "caeos_pairwise":
        assert protocol["comparators"] == ["opendetect"]
    else:
        assert protocol["comparators"] == [
            "embedded_pairwise",
            "opendetect",
        ]
    if selected == "caeos_pug":
        policy = protocol["pairwise_runtime_policy"]
        assert policy["risk_selection"] == target.PUG_SELECTION
        assert policy["expected_runtime_selected_risk"] == PUG_RISK_NAME
    if selected == "rrc_csr_caeos_v1":
        backend = protocol["rrc_backend_protocol"]
        assert backend["manifest_sha256"] == canonical_hash(backend)
        assert len(backend["tasks"]) == 96
        assert backend["tasks"][0] == {
            "suite": "dataset_a",
            "scenario": "family_0",
            "training_seed": 223,
            "corruption_seed": 2000,
        }
    else:
        assert protocol["rrc_backend_protocol"] is None


def test_create_protocol_rejects_activation_algorithm_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    activation_path, design_path, input_path = prepare_files(
        tmp_path, monkeypatch, "caeos_pairwise"
    )
    value = json.loads(activation_path.read_text(encoding="utf-8"))
    value["selected_algorithm"] = "caeos_pug"
    value["manifest_sha256"] = canonical_hash(value)
    write(activation_path, value)
    with pytest.raises(ValueError, match="activation/input mismatch"):
        target.create_protocol(
            project_root=tmp_path,
            run_root=tmp_path / "run",
            activation_path=activation_path,
            adapter_design_path=design_path,
            input_protocol_path=input_path,
        )


def test_prepare_without_activation_is_fail_closed(
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
    observed = json.loads(capsys.readouterr().out)
    assert observed == {
        "protocol_written": False,
        "state": "pending_selected_system_activation",
    }
    assert not output.exists()


def test_capture_commands_use_algorithm_specific_backends(
    tmp_path: Path,
) -> None:
    record = task(0)
    pairwise = {
        "selected_algorithm": "caeos_pug",
        "pairwise_runtime_policy": target.pairwise_policy("caeos_pug"),
    }
    command = target.pairwise_capture_command(
        python="python",
        project_root=tmp_path,
        block=tmp_path / "run",
        task=record,
        protocol=pairwise,
    )
    assert "capture_pairwise_runtime.py" in command[1]
    assert target.PUG_SELECTION in command

    robust = {
        "selected_algorithm": "rrc_csr_caeos_v1",
        "pairwise_runtime_policy": target.pairwise_policy(
            "rrc_csr_caeos_v1"
        ),
        "robust_runtime_policy": {
            "augmentation_weight": 0.5,
            "training_sample_fraction": 0.25,
            "health_quantile": 0.99,
        },
    }
    command = target.robust_capture_command(
        python="python",
        project_root=tmp_path,
        block=tmp_path / "run",
        task=record,
        protocol=robust,
    )
    assert "capture_csr_caeos_runtime.py" in command[1]
    assert "source_csr_capture" in " ".join(command)


class FakePUGRuntime:
    def __init__(
        self, probability: np.ndarray, risk: np.ndarray
    ) -> None:
        self.probability = np.asarray(probability, dtype=np.float64)
        self.risk = np.asarray(risk, dtype=np.float64)

    def evidence(self) -> dict[str, Any]:
        return {
            "schema_version": "strict_v4_pairwise_runtime_v2",
            "selected_risk": PUG_RISK_NAME,
            "contains_training_or_test_labels": False,
            "contains_test_ground_truth": False,
        }

    def predict(self, views: list[np.ndarray]) -> dict[str, np.ndarray]:
        assert len(views[0]) == len(self.probability)
        return {
            "prediction": self.probability.argmax(axis=1).astype(np.int64),
            "probability": self.probability.copy(),
            "risk": self.risk.copy(),
        }


def split_metadata() -> dict[str, Any]:
    return {
        "split_fingerprint": "f" * 64,
        "fingerprint_overlap": {
            "train_validation": 0,
            "train_test": 0,
            "validation_test": 0,
        },
        "cross_label_fingerprint_filter": {
            "unknown_labels_used": False
        },
    }


def test_pug_evaluation_uses_common_adapter_and_final_metrics_only(
    tmp_path: Path,
) -> None:
    record = task(0)
    protocol = canonical(
        {
            "schema_version": target.PROTOCOL_SCHEMA,
            "execution_admitted": True,
            "selected_algorithm": "caeos_pug",
            "tasks": [record],
            "pairwise_runtime_policy": target.pairwise_policy("caeos_pug"),
        }
    )
    block = target.task_block(tmp_path, record)
    capture = block / "candidate_capture"
    train = block / "source_train"
    capture.mkdir(parents=True)
    train.mkdir(parents=True)
    probability = np.asarray(
        [
            [0.8, 0.2],
            [0.2, 0.8],
            [0.7, 0.3],
            [0.3, 0.7],
            [0.6, 0.4],
            [0.4, 0.6],
            [0.55, 0.45],
            [0.45, 0.55],
        ]
    )
    pug_risk = np.asarray([0.1, 0.2, 0.15, 0.25, 0.7, 0.8, 0.9, 0.75])
    pairwise_risk = np.asarray(
        [0.15, 0.25, 0.2, 0.3, 0.6, 0.7, 0.8, 0.65]
    )
    runtime_path = capture / "pairwise_runtime.joblib"
    inputs_path = capture / "benchmark_inputs.npz"
    joblib.dump(FakePUGRuntime(probability, pug_risk), runtime_path)
    np.savez_compressed(inputs_path, view_0=np.ones((8, 2)))
    manifest = {
        "schema_version": "strict_v4_pairwise_runtime_capture_v1",
        "deployment_artifact": runtime_path.name,
        "deployment_artifact_sha256": target.file_hash(runtime_path),
        "benchmark_inputs": inputs_path.name,
        "benchmark_inputs_sha256": target.file_hash(inputs_path),
        "benchmark_inputs_contain_labels": False,
        "trainer_arguments": target.base_arguments(
            record,
            protocol["pairwise_runtime_policy"],
            train,
        ),
        "runtime_evidence": FakePUGRuntime(
            probability, pug_risk
        ).evidence(),
        "equivalence": {"passes": True},
    }
    write(capture / "capture_manifest.json", manifest)
    write(
        train / "metrics.json",
        {
            "validation_thresholds": {
                PUG_RISK_NAME: 0.5,
                target.PAIRWISE_RISK: 0.5,
            },
            "split_metadata": split_metadata(),
        },
    )
    labels = np.asarray([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    unknown = np.asarray(
        [False, False, False, False, True, True, True, True]
    )
    np.savez_compressed(
        train / "scores.npz",
        test_labels=labels,
        test_unknown=unknown,
        test_prediction=probability.argmax(axis=1),
        **{f"test_{target.PAIRWISE_RISK}": pairwise_risk},
    )
    value = target.evaluate_candidate(
        protocol=protocol,
        run_root=tmp_path,
        task=record,
    )
    assert value["manifest_sha256"] == canonical_hash(value)
    assert value["runtime_evidence"]["selected_algorithm"] == "caeos_pug"
    assert set(value["reports"]) == {"candidate", "embedded_pairwise"}
    assert (
        value["diagnostics"][
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing"
        ]
        is False
    )
    assert (
        value["diagnostics"]["test_labels_used_for_final_metrics_only"]
        is True
    )
    assert target.validate_bound_metrics(
        block / "candidate", protocol, record, "caeos_pug"
    )


def test_common_adapter_rejects_runtime_algorithm_splicing(
    tmp_path: Path,
) -> None:
    record = task(0)
    protocol = canonical(
        {
            "schema_version": target.PROTOCOL_SCHEMA,
            "execution_admitted": True,
            "selected_algorithm": "caeos_pairwise",
            "tasks": [record],
            "pairwise_runtime_policy": target.pairwise_policy(
                "caeos_pairwise"
            ),
        }
    )
    block = target.task_block(tmp_path, record)
    capture = block / "candidate_capture"
    train = block / "source_train"
    capture.mkdir(parents=True)
    train.mkdir(parents=True)
    probability = np.asarray(
        [[0.8, 0.2], [0.2, 0.8], [0.7, 0.3], [0.3, 0.7]]
    )
    runtime_path = capture / "pairwise_runtime.joblib"
    inputs_path = capture / "benchmark_inputs.npz"
    joblib.dump(
        FakePUGRuntime(probability, np.asarray([0.1, 0.2, 0.8, 0.9])),
        runtime_path,
    )
    np.savez_compressed(inputs_path, view_0=np.ones((4, 2)))
    write(
        capture / "capture_manifest.json",
        {
            "schema_version": "strict_v4_pairwise_runtime_capture_v1",
            "deployment_artifact": runtime_path.name,
            "deployment_artifact_sha256": target.file_hash(runtime_path),
            "benchmark_inputs": inputs_path.name,
            "benchmark_inputs_sha256": target.file_hash(inputs_path),
            "benchmark_inputs_contain_labels": False,
            "trainer_arguments": target.base_arguments(
                record,
                protocol["pairwise_runtime_policy"],
                train,
            ),
            "runtime_evidence": {
                "schema_version": "strict_v4_pairwise_runtime_v2",
                "selected_risk": target.PAIRWISE_RISK,
                "contains_training_or_test_labels": False,
                "contains_test_ground_truth": False,
            },
            "equivalence": {"passes": True},
        },
    )
    write(
        train / "metrics.json",
        {
            "validation_thresholds": {
                PUG_RISK_NAME: 0.5,
                target.PAIRWISE_RISK: 0.5,
            },
            "split_metadata": split_metadata(),
        },
    )
    np.savez_compressed(
        train / "scores.npz",
        test_labels=np.asarray([0, 1, 0, 1]),
        test_unknown=np.asarray([False, False, True, True]),
        test_prediction=probability.argmax(axis=1),
        **{
            f"test_{target.PAIRWISE_RISK}": np.asarray(
                [0.1, 0.2, 0.8, 0.9]
            )
        },
    )
    with pytest.raises(
        ValueError, match="selected algorithm disagrees with runtime evidence"
    ):
        target.evaluate_candidate(
            protocol=protocol,
            run_root=tmp_path,
            task=record,
        )


def test_pairwise_summary_and_audit_recompute_bound_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = task(0)
    protocol = canonical(
        {
            "schema_version": target.PROTOCOL_SCHEMA,
            "execution_admitted": True,
            "selected_algorithm": "caeos_pairwise",
            "comparators": ["opendetect"],
            "tasks": [record],
            "task_counts": {"total_scenarios_per_algorithm": 1},
            "statistics": {
                "bootstrap_repetitions": 10,
                "bootstrap_seed": 7,
            },
            "confirmation_gate": {
                "against_each_comparator": {}
            },
            "claim_boundary": {},
        }
    )
    block = target.task_block(tmp_path, record)
    candidate_dir = block / "candidate"
    opendetect_dir = block / "opendetect"
    candidate_report = {
        "unknown_auroc": 0.8,
        "unknown_aupr": 0.7,
        "unknown_fpr95": 0.2,
        "oscr": 0.6,
        "known_macro_f1": 0.9,
    }
    candidate_metrics = canonical(
        {
            "schema_version": target.METRICS_SCHEMA,
            "state": "complete",
            "selected_algorithm": "caeos_pairwise",
            "split_metadata": split_metadata(),
            "reports": {"candidate": candidate_report},
            "diagnostics": {
                "unknown_or_test_labels_used_for_fit_selection_calibration_"
                "threshold_or_routing": False,
                "test_labels_used_for_final_metrics_only": True,
                "external_parameters_reselected": False,
            },
        }
    )
    write(candidate_dir / "metrics.json", candidate_metrics)
    write(
        opendetect_dir / "metrics.json",
        {
            "method": "opendetect",
            "split_metadata": split_metadata(),
            "reports": {
                "opendetect": {
                    **candidate_report,
                    "unknown_auroc": 0.7,
                }
            },
        },
    )
    target.write_provenance(
        output=candidate_dir,
        protocol=protocol,
        task=record,
        method="caeos_pairwise",
        command=["candidate"],
    )
    target.write_provenance(
        output=opendetect_dir,
        protocol=protocol,
        task=record,
        method="opendetect",
        command=["opendetect"],
    )
    monkeypatch.setattr(
        target,
        "aggregate",
        lambda rows, repetitions, bootstrap_seed: {
            "row_count": len(rows),
            "repetitions": repetitions,
            "bootstrap_seed": bootstrap_seed,
        },
    )
    monkeypatch.setattr(
        target,
        "comparator_checks",
        lambda aggregation, gates: {"synthetic_effect_gate": True},
    )
    summary = target.summarize(protocol, tmp_path)
    assert summary["comparators"] == ["opendetect"]
    assert summary["validation"]["integrity_passes"] is True
    assert summary["validation"]["effect_passes"] is True
    assert summary["manifest_sha256"] == canonical_hash(summary)
    audit = target.audit_summary(protocol, summary, tmp_path)
    assert audit["summary_recomputation_matches"] is True
    assert audit["integrity_passes"] is True
    assert audit["effect_passes"] is True
    assert audit["comprehensive_sota_authorized"] is False
