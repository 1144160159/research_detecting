from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np

from caeos.csr_runtime import CSRRuntime
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_rrc_csr_runtime import evaluate
from materialize_rrc_csr_runtime import materialize


class FakeCSRRuntime(CSRRuntime):
    def __init__(self):
        pass

    clean_threshold = 0.5
    training_seed = 701

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


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(tmp_path: Path, enabled: bool):
    source = tmp_path / "source"
    source.mkdir()
    artifact = source / "csr_runtime.joblib"
    inputs = source / "evaluation_inputs.npz"
    joblib.dump(FakeCSRRuntime(), artifact)
    np.savez_compressed(
        inputs,
        view_0=np.zeros((2, 1)),
        test_labels=np.asarray([0, 1]),
        test_unknown=np.asarray([False, True]),
    )
    source_manifest = {
        "schema_version": "strict_v4_csr_caeos_runtime_capture_v1",
        "state": "complete",
        "algorithm": "csr_caeos_v1",
        "task": {"suite": "suite", "scenario": "scenario"},
        "training_seed": 701,
        "weight": 0.5,
        "runtime_artifact": artifact.name,
        "runtime_artifact_sha256": file_hash(artifact),
        "evaluation_inputs": inputs.name,
        "evaluation_inputs_sha256": file_hash(inputs),
        "unknown_or_test_labels_used_for_training_selection_or_calibration": (
            False
        ),
        "test_labels_read_for_roundtrip_or_selection": False,
        "test_effect_metrics_computed": False,
    }
    source_manifest_path = source / "capture_manifest.json"
    source_manifest_path.write_text(
        json.dumps(source_manifest), encoding="utf-8"
    )
    protocol = canonical(
        {
            "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
            "execution_admitted": True,
            "coverage_manifest_sha256": "c" * 64,
            "conditions": ["clean"],
            "fixed_severity": {},
            "tasks": [
                {
                    "suite": "suite",
                    "scenario": "scenario",
                    "training_seed": 701,
                    "corruption_seed": 727,
                }
            ],
        }
    )
    mean_auroc = 0.71 if enabled else 0.69
    minimum_auroc = 0.70 if enabled else 0.67
    records = [
        {
            "training_seed": seed,
            "calibration_error_detection_auroc": (
                minimum_auroc if seed == 701 else mean_auroc
            ),
            "safety_active_rate_upper_95pct": 0.005,
            "source_capture_manifest_file_sha256": (
                file_hash(source_manifest_path)
                if seed == 701
                else f"{seed:064x}"
            ),
        }
        for seed in (701, 709, 719)
    ]
    certificate = canonical(
        {
            "schema_version": (
                "strict_v4_rrc_csr_scenario_certificate_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "suite": "suite",
            "scenario": "scenario",
            "training_seeds": [701, 709, 719],
            "seed_records": records,
            "scenario_aggregation": {
                "mean_calibration_error_detection_auroc": mean_auroc,
                "minimum_calibration_error_detection_auroc": minimum_auroc,
                "all_seed_safety_checks_pass": True,
            },
            "thresholds": {
                "scenario_mean_error_detection_auroc_minimum": 0.7,
                "per_seed_error_detection_auroc_minimum": 0.68,
                "per_seed_safety_active_rate_upper_95pct_maximum": 0.01,
            },
            "routing_enabled": enabled,
            "unknown_or_test_labels_used": False,
            "test_arrays_read": False,
            "test_effect_metrics_read": False,
        }
    )
    return source, protocol, certificate


def test_enabled_materialization_roundtrip_and_clean_evaluation(
    tmp_path: Path,
) -> None:
    source, protocol, certificate = fixtures(tmp_path, True)
    capture_dir = tmp_path / "rrc"
    capture = materialize(
        protocol,
        certificate,
        source,
        capture_dir,
        suite="suite",
        scenario="scenario",
        training_seed=701,
        corruption_seed=727,
    )
    assert capture["manifest_sha256"] == canonical_hash(capture)
    assert capture["roundtrip"]["passes"] is True
    result = evaluate(
        protocol,
        capture_dir,
        suite="suite",
        scenario="scenario",
        training_seed=701,
        corruption_seed=727,
        condition="clean",
        output=tmp_path / "evaluation.json",
    )
    assert result["manifest_sha256"] == canonical_hash(result)
    assert result["routing"]["prediction_exactly_pairwise_all_rows"] is True
    assert result["routing"]["probability_exactly_pairwise_all_rows"] is True
    assert result["routing"]["risk_monotone_not_below_pairwise"] is True


def test_disabled_materialization_is_exact_pairwise(tmp_path: Path) -> None:
    source, protocol, certificate = fixtures(tmp_path, False)
    capture_dir = tmp_path / "rrc"
    materialize(
        protocol,
        certificate,
        source,
        capture_dir,
        suite="suite",
        scenario="scenario",
        training_seed=701,
        corruption_seed=727,
    )
    result = evaluate(
        protocol,
        capture_dir,
        suite="suite",
        scenario="scenario",
        training_seed=701,
        corruption_seed=727,
        condition="clean",
        output=tmp_path / "evaluation.json",
    )
    assert (
        result["routing"]["disabled_risk_exactly_pairwise_all_rows"] is True
    )
    assert result["candidate_report"] == result["pairwise_report"]
