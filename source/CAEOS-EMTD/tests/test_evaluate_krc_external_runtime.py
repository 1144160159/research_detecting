from pathlib import Path

import numpy as np
import pytest

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_krc_external_runtime import evaluate


class Runtime:
    clean_threshold = 0.5

    def __init__(self, *, invalid_prediction: bool = False):
        self.invalid_prediction = invalid_prediction

    def evidence(self):
        return {
            "algorithm": "krc_csr_caeos_v1",
            "augmentation_weight": 0.5,
            "training_seed": 223,
            "modality_count": 1,
            "routing_enabled": True,
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection": (
                False
            ),
        }

    def predict(self, views):
        clean_probability = np.asarray(
            [[0.9, 0.1], [0.2, 0.8], [0.6, 0.4], [0.1, 0.9]]
        )
        prediction = clean_probability.argmax(axis=1)
        if self.invalid_prediction:
            prediction = prediction.copy()
            prediction[0] = 1 - prediction[0]
        clean_risk = np.asarray([0.1, 0.2, 0.8, 0.9])
        active = np.asarray([False, True, True, False])
        risk = clean_risk.copy()
        risk[active] += 0.05
        return {
            "prediction": prediction,
            "probability": clean_probability.copy(),
            "risk": risk,
            "clean_probability": clean_probability,
            "clean_risk": clean_risk,
            "active": active,
            "any_missing": np.asarray([False, False, True, False]),
        }


def write_json(path: Path, value):
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture(tmp_path, monkeypatch):
    capture_dir = tmp_path / "capture"
    artifact = capture_dir / "runtime.joblib"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"runtime")
    inputs = capture_dir / "inputs.npz"
    np.savez_compressed(
        inputs,
        view_0=np.arange(8).reshape(4, 2),
        test_labels=np.asarray([0, 1, 0, 1]),
        test_unknown=np.asarray([False, False, True, True]),
    )
    split = {
        "split_fingerprint": "split-1",
        "fingerprint_overlap": {
            "train_validation": 0,
            "train_test": 0,
            "validation_test": 0,
        },
        "cross_label_fingerprint_filter": {
            "unknown_labels_used": False
        },
    }
    capture = {
        "schema_version": "strict_v4_krc_csr_runtime_capture_v1",
        "algorithm": "krc_csr_caeos_v1",
        "task": {"suite": "LSNM2024", "scenario": "attack-a"},
        "training_seed": 223,
        "weight": 0.5,
        "runtime_artifact": artifact.name,
        "runtime_artifact_sha256": file_hash(artifact),
        "evaluation_inputs": inputs.name,
        "evaluation_inputs_sha256": file_hash(inputs),
        "split_fingerprint": "split-1",
        "known_only_certificate": {
            "routing_enabled": True,
            "calibration_known_macro_f1": 0.95,
            "calibration_error_detection_auroc": 0.8,
        },
        "unknown_or_test_labels_used_for_training_selection_or_calibration": (
            False
        ),
        "test_labels_read_for_certificate_or_roundtrip": False,
    }
    capture["manifest_sha256"] = canonical_hash(capture)
    write_json(capture_dir / "capture_manifest.json", capture)
    write_json(
        capture_dir / "robust_run" / "metrics.json",
        {"split_metadata": split},
    )
    task = {
        "dataset": "LSNM2024",
        "unknown_attack_family": "attack-a",
        "training_seed": 223,
    }
    protocol = {
        "schema_version": (
            "strict_v4_krc_external_malicious_execution_protocol_v1"
        ),
        "execution_admitted": True,
        "algorithm": "krc_csr_caeos_v1",
        "krc_policy": {"augmentation_weight": 0.5},
        "tasks": [task],
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    monkeypatch.setattr(
        "evaluate_krc_external_runtime.joblib.load", lambda _: Runtime()
    )
    return capture_dir, protocol, task


def test_krc_external_runtime_is_canonical(tmp_path, monkeypatch):
    capture_dir, protocol, task = fixture(tmp_path, monkeypatch)
    result = evaluate(
        capture_dir=capture_dir,
        protocol=protocol,
        task=task,
        output=tmp_path / "metrics.json",
    )
    assert result["reports"]["candidate"]["unknown_auroc"] >= 0
    assert result["routing"]["prediction_exactly_pairwise_all_rows"]
    assert result["routing"]["probability_exactly_pairwise_all_rows"]
    assert result["routing"]["risk_monotone_not_below_pairwise"]
    assert result["manifest_sha256"] == canonical_hash(result)


def test_krc_external_runtime_rejects_prediction_change(
    tmp_path, monkeypatch
):
    capture_dir, protocol, task = fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "evaluate_krc_external_runtime.joblib.load",
        lambda _: Runtime(invalid_prediction=True),
    )
    with pytest.raises(ValueError, match="routing contract"):
        evaluate(
            capture_dir=capture_dir,
            protocol=protocol,
            task=task,
            output=tmp_path / "metrics.json",
        )


def test_krc_external_runtime_rejects_split_overlap(
    tmp_path, monkeypatch
):
    capture_dir, protocol, task = fixture(tmp_path, monkeypatch)
    metrics_path = capture_dir / "robust_run" / "metrics.json"
    metrics = {
        "split_metadata": {
            "split_fingerprint": "split-1",
            "fingerprint_overlap": {
                "train_validation": 0,
                "train_test": 1,
                "validation_test": 0,
            },
            "cross_label_fingerprint_filter": {
                "unknown_labels_used": False
            },
        }
    }
    write_json(metrics_path, metrics)
    with pytest.raises(ValueError, match="overlap"):
        evaluate(
            capture_dir=capture_dir,
            protocol=protocol,
            task=task,
            output=tmp_path / "metrics.json",
        )


def test_krc_external_runtime_rejects_unregistered_task(
    tmp_path, monkeypatch
):
    capture_dir, protocol, task = fixture(tmp_path, monkeypatch)
    task = dict(task)
    task["unknown_attack_family"] = "other"
    with pytest.raises(ValueError, match="not in the frozen protocol"):
        evaluate(
            capture_dir=capture_dir,
            protocol=protocol,
            task=task,
            output=tmp_path / "metrics.json",
        )
