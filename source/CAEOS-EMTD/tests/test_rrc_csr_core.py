from __future__ import annotations

import numpy as np
import pytest

from caeos.rrc_csr_runtime import RRCCSRRuntime
from certify_rrc_csr_scenario import certify_seed_records


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


def runtime(enabled: bool) -> RRCCSRRuntime:
    return RRCCSRRuntime(
        base_runtime=FakeCSRRuntime(),
        routing_enabled=enabled,
        scenario_identity="suite/scenario",
        scenario_certificate_manifest_sha256="c" * 64,
        training_seed=701,
        certified_training_seeds=(701, 709, 719),
        seed_error_detection_auroc=0.71,
        seed_safety_active_rate_upper_95pct=0.005,
        scenario_mean_error_detection_auroc=0.71 if enabled else 0.69,
        scenario_minimum_error_detection_auroc=0.70 if enabled else 0.67,
        all_seed_safety_checks_pass=True,
    )


def seed_record(seed: int, auroc: float) -> dict:
    return {
        "suite": "suite",
        "scenario": "scenario",
        "training_seed": seed,
        "calibration_known_macro_f1_report_only": 0.6,
        "calibration_error_detection_auroc": auroc,
        "safety_active_rate_upper_95pct": 0.005,
        "structural_safety_passes": True,
        "known_validation_labels_used": True,
        "unknown_or_test_labels_used": False,
        "test_arrays_read": False,
        "test_effect_metrics_read": False,
    }


def test_enabled_runtime_preserves_csr_risk_and_exact_classification() -> None:
    value = runtime(True).predict([np.zeros((2, 1))])
    assert np.array_equal(value["risk"], np.asarray([0.6, 0.9]))
    assert np.array_equal(value["active"], np.asarray([True, False]))
    assert np.array_equal(value["probability"], value["clean_probability"])
    assert np.array_equal(value["prediction"], value["clean_prediction"])


def test_disabled_runtime_is_exact_pairwise() -> None:
    value = runtime(False).predict([np.zeros((2, 1))])
    assert not value["active"].any()
    assert np.array_equal(value["risk"], value["clean_risk"])
    assert np.array_equal(value["probability"], value["clean_probability"])
    assert np.array_equal(value["prediction"], value["clean_prediction"])


def test_scenario_certificate_enables_only_all_three_seed_direct_gates() -> None:
    enabled = certify_seed_records(
        [
            seed_record(701, 0.70),
            seed_record(709, 0.71),
            seed_record(719, 0.72),
        ],
        protocol_manifest_sha256="p" * 64,
        suite="suite",
        scenario="scenario",
        expected_training_seeds=(701, 709, 719),
    )
    assert enabled["routing_enabled"] is True
    assert enabled["thresholds"]["absolute_known_macro_f1_threshold"] is None

    disabled = certify_seed_records(
        [
            seed_record(701, 0.67),
            seed_record(709, 0.72),
            seed_record(719, 0.72),
        ],
        protocol_manifest_sha256="p" * 64,
        suite="suite",
        scenario="scenario",
        expected_training_seeds=(701, 709, 719),
    )
    assert disabled["routing_enabled"] is False


def test_certificate_rejects_missing_seed_and_runtime_mismatch() -> None:
    with pytest.raises(ValueError):
        certify_seed_records(
            [seed_record(701, 0.71), seed_record(709, 0.71)],
            protocol_manifest_sha256="p" * 64,
            suite="suite",
            scenario="scenario",
            expected_training_seeds=(701, 709, 719),
        )
    with pytest.raises(ValueError):
        RRCCSRRuntime(
            base_runtime=FakeCSRRuntime(),
            routing_enabled=True,
            scenario_identity="suite/scenario",
            scenario_certificate_manifest_sha256="c" * 64,
            training_seed=701,
            certified_training_seeds=(701, 709, 719),
            seed_error_detection_auroc=0.67,
            seed_safety_active_rate_upper_95pct=0.005,
            scenario_mean_error_detection_auroc=0.69,
            scenario_minimum_error_detection_auroc=0.67,
            all_seed_safety_checks_pass=True,
        )
