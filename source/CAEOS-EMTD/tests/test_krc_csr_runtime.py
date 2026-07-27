import numpy as np
import joblib

from caeos.krc_csr_runtime import KRCCSRRuntime
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_krc_csr_confirmation_runtime import evaluate


class FakeCSRRuntime:
    clean_threshold = 0.5

    def predict(self, raw_views):
        clean_probability = np.asarray(
            [[0.8, 0.2], [0.3, 0.7]], dtype=np.float64
        )
        return {
            "prediction": clean_probability.argmax(axis=1),
            "probability": clean_probability.copy(),
            "clean_probability": clean_probability,
            "robust_probability": clean_probability.copy(),
            "risk": np.asarray([0.6, 0.9]),
            "clean_risk": np.asarray([0.2, 0.9]),
            "robust_risk": np.asarray([0.6, 0.9]),
            "missing_risk": np.asarray([0.7, 0.8]),
            "active": np.asarray([True, False]),
            "any_missing": np.asarray([False, False]),
            "conflict_active": np.asarray([True, False]),
            "disagreement_active": np.asarray([False, False]),
        }

    def corrupt(self, raw_views, **kwargs):
        return [np.asarray(view).copy() for view in raw_views]

    def evidence(self):
        return {
            "schema_version": "strict_v4_csr_caeos_runtime_v1",
            "algorithm": "csr_caeos_v1",
            "modality_count": 1,
            "contains_test_ground_truth": False,
        }


def runtime(enabled):
    return KRCCSRRuntime(
        base_runtime=FakeCSRRuntime(),
        routing_enabled=enabled,
        calibration_known_macro_f1=0.95,
        calibration_error_detection_auroc=0.8,
    )


def test_enabled_krc_preserves_csr_risk_and_exact_clean_classification():
    value = runtime(True).predict([np.zeros((2, 1))])
    assert np.array_equal(value["risk"], np.asarray([0.6, 0.9]))
    assert np.array_equal(value["active"], np.asarray([True, False]))
    assert np.array_equal(value["probability"], value["clean_probability"])
    assert np.array_equal(value["prediction"], value["clean_prediction"])


def test_disabled_krc_is_exact_pairwise_for_all_rows():
    value = runtime(False).predict([np.zeros((2, 1))])
    assert not value["active"].any()
    assert np.array_equal(value["risk"], value["clean_risk"])
    assert np.array_equal(value["probability"], value["clean_probability"])
    assert np.array_equal(value["prediction"], value["clean_prediction"])


def test_confirmation_evaluator_loads_canonical_runtime_capture(tmp_path):
    capture_dir = tmp_path / "capture"
    capture_dir.mkdir()
    artifact = capture_dir / "runtime.joblib"
    inputs = capture_dir / "evaluation_inputs.npz"
    joblib.dump(runtime(False), artifact)
    np.savez_compressed(
        inputs,
        view_0=np.zeros((2, 1)),
        test_labels=np.asarray([0, 1]),
        test_unknown=np.asarray([False, True]),
    )
    protocol = {
        "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
        "execution_admitted": True,
        "coverage_manifest_sha256": "c" * 64,
        "confirmation": {
            "conditions": ["clean"],
            "fixed_severity": {},
            "tasks": [
                {
                    "suite": "suite",
                    "scenario": "scenario",
                    "training_seed": 647,
                    "corruption_seed": 661,
                    "primary_heldout_scenario": True,
                }
            ],
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    manifest = {
        "schema_version": "strict_v4_krc_csr_runtime_capture_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "task": {"suite": "suite", "scenario": "scenario"},
        "training_seed": 647,
        "weight": 0.5,
        "runtime_artifact": artifact.name,
        "runtime_artifact_sha256": file_hash(artifact),
        "evaluation_inputs": inputs.name,
        "evaluation_inputs_sha256": file_hash(inputs),
        "unknown_or_test_labels_used_for_training_selection_or_calibration": (
            False
        ),
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    (capture_dir / "capture_manifest.json").write_text(
        __import__("json").dumps(manifest), encoding="utf-8"
    )
    result = evaluate(
        protocol,
        capture_dir,
        suite="suite",
        scenario="scenario",
        training_seed=647,
        corruption_seed=661,
        condition="clean",
        output=tmp_path / "evaluation.json",
    )
    assert result["manifest_sha256"] == canonical_hash(result)
    assert result["routing"]["prediction_exactly_pairwise_all_rows"] is True
    assert result["routing"]["probability_exactly_pairwise_all_rows"] is True
    assert (
        result["routing"]["disabled_risk_exactly_pairwise_all_rows"] is True
    )
