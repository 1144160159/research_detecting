from pathlib import Path

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_external_runtime import evaluate


class Runtime:
    clean_threshold = 0.5

    def evidence(self):
        return {
            "algorithm": "mdr_caeos_v1",
            "augmentation_weight": 0.25,
            "training_seed": 223,
            "modality_count": 1,
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection": (
                False
            ),
        }

    def predict(self, views):
        probability = np.asarray(
            [[0.9, 0.1], [0.2, 0.8], [0.6, 0.4], [0.1, 0.9]]
        )
        clean_probability = probability.copy()
        prediction = probability.argmax(axis=1)
        risk = np.asarray([0.1, 0.2, 0.8, 0.9])
        return {
            "prediction": prediction,
            "risk": risk,
            "probability": probability,
            "clean_prediction": prediction.copy(),
            "clean_risk": risk.copy(),
            "clean_probability": clean_probability,
            "active": np.asarray([False, True, True, False]),
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
    }
    capture = {
        "schema_version": "strict_v4_mdr_caeos_runtime_capture_v1",
        "algorithm": "mdr_caeos_v1",
        "task": {"suite": "LSNM2024", "scenario": "attack-a"},
        "training_seed": 223,
        "weight": 0.25,
        "runtime_artifact": artifact.name,
        "runtime_artifact_sha256": file_hash(artifact),
        "evaluation_inputs": inputs.name,
        "evaluation_inputs_sha256": file_hash(inputs),
        "split_fingerprint": "split-1",
    }
    write_json(capture_dir / "capture_manifest.json", capture)
    write_json(
        capture_dir / "robust_run" / "metrics.json",
        {"split_metadata": split},
    )
    protocol = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_protocol_v1"
        ),
        "selected_algorithm": "mdr_caeos_v1",
        "mdr_policy": {"augmentation_weight": 0.25},
        "scenarios": [
            {
                "dataset": "LSNM2024",
                "unknown_attack_family": "attack-a",
                "seed": 223,
            }
        ],
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    monkeypatch.setattr(
        "evaluate_mdr_external_runtime.joblib.load", lambda _: Runtime()
    )
    return capture_dir, protocol


def test_external_runtime_evaluation_is_canonical(tmp_path, monkeypatch):
    capture_dir, protocol = fixture(tmp_path, monkeypatch)
    result = evaluate(
        capture_dir=capture_dir,
        protocol=protocol,
        scenario={
            "dataset": "LSNM2024",
            "unknown_attack_family": "attack-a",
            "seed": 223,
        },
        output=tmp_path / "metrics.json",
    )
    assert result["reports"]["candidate"]["unknown_auroc"] >= 0
    assert result["routing"]["inactive_probability_exactly_pairwise"]
    assert result["manifest_sha256"] == canonical_hash(result)


def test_external_runtime_rejects_weight_drift(tmp_path, monkeypatch):
    import pytest

    capture_dir, protocol = fixture(tmp_path, monkeypatch)
    protocol["mdr_policy"]["augmentation_weight"] = 0.5
    protocol["manifest_sha256"] = canonical_hash(protocol)
    with pytest.raises(ValueError, match="capture identity"):
        evaluate(
            capture_dir=capture_dir,
            protocol=protocol,
            scenario={
                "dataset": "LSNM2024",
                "unknown_attack_family": "attack-a",
                "seed": 223,
            },
            output=tmp_path / "metrics.json",
        )


def test_external_runtime_rejects_unregistered_scenario(
    tmp_path, monkeypatch
):
    import pytest

    capture_dir, protocol = fixture(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="not in the protocol"):
        evaluate(
            capture_dir=capture_dir,
            protocol=protocol,
            scenario={
                "dataset": "LSNM2024",
                "unknown_attack_family": "other",
                "seed": 223,
            },
            output=tmp_path / "metrics.json",
        )
