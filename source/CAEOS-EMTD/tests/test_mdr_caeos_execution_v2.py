from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pytest

from capture_mdr_caeos_runtime_v2 import load_importable_trainer_module
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_pilot_execution_protocol_v2 import (
    revise_protocol,
)
from run_strict_v4_mdr_caeos_pilot_v2 import validate_protocol


def prior_protocol():
    value = {
        "schema_version": (
            "strict_v4_mdr_caeos_pilot_execution_protocol_v1"
        ),
        "status": "frozen_before_pilot_results",
        "execution_admitted": True,
        "algorithm": "mdr_caeos_v1",
        "design_path": "results/design.json",
        "design_manifest_sha256": "design-sha",
        "source_registry": [],
        "implementation": {"capture": "capture_v1.py"},
        "implementation_sha256": {"capture": "capture-v1-sha"},
        "output_counts_at_freeze": {"capture_manifests": 0},
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_real_dynamic_trainer_class_roundtrips_with_joblib(
    tmp_path: Path,
) -> None:
    project_root = Path(__file__).resolve().parents[1]
    module = load_importable_trainer_module(
        str(project_root / "train_mdr_caeos_open_set.py")
    )
    classifier = module.ConfiguredStructuredRobustClassifier(estimators=2)
    assert classifier.__class__.__module__ == "train_mdr_caeos_open_set"
    assert sys.modules[classifier.__class__.__module__] is module
    artifact = tmp_path / "classifier.joblib"
    joblib.dump(classifier, artifact, compress=3)
    restored = joblib.load(artifact)
    assert restored.__class__.__module__ == "train_mdr_caeos_open_set"


def test_protocol_v2_is_zero_complete_result_only() -> None:
    revised = revise_protocol(
        prior_protocol(),
        prior_protocol_file_sha256="prior-file-sha",
        failure_log_path="results/v1/execution.log",
        failure_log_sha256="failure-log-sha",
        implementation={"capture": "capture_v2.py"},
        implementation_sha256={"capture": "capture-v2-sha"},
        observed_counts={
            "capture_manifests": 0,
            "evaluations": 0,
            "summary": 0,
        },
    )
    assert revised["protocol_revision"]["algorithm_formula_changed"] is False
    assert revised["protocol_revision"]["complete_capture_count_before_revision"] == 0
    assert revised["manifest_sha256"] == canonical_hash(revised)
    validate_protocol(revised)
    with pytest.raises(ValueError, match="fresh zero-output root"):
        revise_protocol(
            prior_protocol(),
            prior_protocol_file_sha256="prior-file-sha",
            failure_log_path="results/v1/execution.log",
            failure_log_sha256="failure-log-sha",
            implementation={"capture": "capture_v2.py"},
            implementation_sha256={"capture": "capture-v2-sha"},
            observed_counts={"capture_manifests": 1},
        )
