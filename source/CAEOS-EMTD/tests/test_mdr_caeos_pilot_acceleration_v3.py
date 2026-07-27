from __future__ import annotations

import pytest

from accelerate_strict_v4_mdr_caeos_pilot_captures_v3 import (
    validate_paused_pilot_snapshot,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_pilot_acceleration_amendment import (
    create_amendment,
)


def protocol():
    value = {
        "schema_version": (
            "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        )
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_v3_snapshot_accepts_exact_v2_runner():
    validate_paused_pilot_snapshot(
        {
            "state": "T",
            "cmdline": "python run_strict_v4_mdr_caeos_pilot_v2.py",
            "direct_children": [{"state": "Z"}],
        }
    )
    with pytest.raises(ValueError, match="v2 runner command"):
        validate_paused_pilot_snapshot(
            {
                "state": "T",
                "cmdline": "python run_strict_v4_mdr_caeos_pilot.py",
                "direct_children": [],
            }
        )
    with pytest.raises(ValueError, match="active children"):
        validate_paused_pilot_snapshot(
            {
                "state": "T",
                "cmdline": "python run_strict_v4_mdr_caeos_pilot_v2.py",
                "direct_children": [{"state": "R"}],
            }
        )


def test_scheduler_amendment_preserves_algorithm_and_effect_boundary():
    value = create_amendment(
        protocol(),
        protocol_file_sha256="protocol-file",
        failure_log_path="results/accel-v2/execution.log",
        failure_log_sha256="failure-log",
        completed_captures=[
            {"path": "runs/capture_manifest.json", "sha256": "capture-sha"}
        ],
        observed_counts={
            "capture_manifests": 1,
            "evaluations": 0,
            "weight_selection": 0,
            "summary": 0,
            "audit": 0,
        },
        implementation={"accelerator": "accelerator.py"},
        implementation_sha256={"accelerator": "accelerator-sha"},
    )
    assert value["amendment_scope"]["effect_metrics_read"] is False
    assert value["amendment_scope"]["capture_command_changed"] is False
    assert value["amendment_scope"]["algorithm_or_hyperparameters_changed"] is False
    assert value["manifest_sha256"] == canonical_hash(value)
    with pytest.raises(ValueError, match="zero effect outputs"):
        create_amendment(
            protocol(),
            protocol_file_sha256="protocol-file",
            failure_log_path="failure.log",
            failure_log_sha256="failure-log",
            completed_captures=[
                {"path": "capture.json", "sha256": "capture-sha"}
            ],
            observed_counts={
                "capture_manifests": 1,
                "evaluations": 1,
                "weight_selection": 0,
                "summary": 0,
                "audit": 0,
            },
            implementation={"accelerator": "accelerator.py"},
            implementation_sha256={"accelerator": "accelerator-sha"},
        )
