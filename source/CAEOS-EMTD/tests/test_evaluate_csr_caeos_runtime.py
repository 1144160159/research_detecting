from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_csr_caeos_runtime import evaluate


class FakeCSRRuntime:
    clean_threshold = 0.5

    def evidence(self):
        return {
            "algorithm": "csr_caeos_v1",
            "modality_count": 1,
            "contains_test_ground_truth": False,
        }

    def corrupt(self, views, **kwargs):
        return views

    def predict(self, views):
        count = len(views[0])
        probability = np.tile([[0.9, 0.1]], (count, 1))
        clean_risk = np.linspace(0.1, 0.4, count)
        active = np.arange(count) % 2 == 0
        risk = clean_risk.copy()
        risk[active] += 0.2
        return {
            "prediction": probability.argmax(axis=1),
            "probability": probability.copy(),
            "risk": risk,
            "active": active,
            "any_missing": np.zeros(count, dtype=bool),
            "clean_probability": probability,
            "clean_risk": clean_risk,
        }


def test_evaluator_enforces_risk_only_contract(tmp_path: Path) -> None:
    artifact = tmp_path / "runtime.joblib"
    inputs = tmp_path / "evaluation_inputs.npz"
    joblib.dump(FakeCSRRuntime(), artifact)
    np.savez(
        inputs,
        view_0=np.ones((4, 1)),
        test_labels=np.asarray([0, 0, 1, 1]),
        test_unknown=np.asarray([False, False, True, True]),
    )
    capture = {
        "schema_version": "strict_v4_csr_caeos_runtime_capture_v1",
        "algorithm": "csr_caeos_v1",
        "test_effect_metrics_computed": False,
        "runtime_artifact": artifact.name,
        "runtime_artifact_sha256": file_hash(artifact),
        "evaluation_inputs": inputs.name,
        "evaluation_inputs_sha256": file_hash(inputs),
        "weight": 0.5,
    }
    (tmp_path / "capture_manifest.json").write_text(
        json.dumps(capture), encoding="utf-8"
    )
    design = {
        "schema_version": "strict_v4_csr_caeos_design_v2",
        "input_manifest_sha256": {"coverage": "coverage"},
        "development": {"training_seed": 607, "corruption_seed": 617},
    }
    design["manifest_sha256"] = canonical_hash(design)
    value = evaluate(
        tmp_path,
        design,
        suite="suite",
        scenario="scenario",
        condition="clean",
        output=tmp_path / "evaluation.json",
    )
    assert value["routing"]["prediction_exactly_pairwise_all_rows"] is True
    assert value["routing"]["probability_exactly_pairwise_all_rows"] is True
    assert value["routing"]["risk_monotone_not_below_pairwise"] is True
    assert value["routing"]["inactive_risk_exactly_pairwise"] is True
    assert value["test_labels_used_for_final_evaluation_only"] is True
    assert value["manifest_sha256"] == canonical_hash(value)
