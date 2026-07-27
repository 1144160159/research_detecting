from __future__ import annotations

from pathlib import Path

import pytest

from accelerate_strict_v4_csr_caeos_pilot_captures import (
    capture_command,
    task_matrix,
    validate_paused_pilot_snapshot,
)
from create_strict_v4_csr_caeos_pilot_acceleration_amendment import (
    create_amendment,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def protocol() -> dict:
    value = {
        "schema_version": "strict_v4_csr_caeos_pilot_protocol_v1",
        "execution_admitted": True,
        "implementation": {
            "capture": "capture.py",
            "clean_trainer": "clean.py",
            "robust_trainer": "robust.py",
        },
        "source_registry": [
            {
                "suite": f"suite_{index // 2}",
                "scenario": f"scenario_{index}",
                "base_trainer_arguments": ["--csv", f"data_{index}.csv"],
            }
            for index in range(14)
        ],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def design() -> dict:
    return {
        "development": {
            "scenario_count": 14,
            "scenarios": {
                f"suite_{index}": [
                    f"scenario_{2 * index}",
                    f"scenario_{2 * index + 1}",
                ]
                for index in range(7)
            },
            "training_seed": 607,
            "augmentation_seed": 613,
            "corruption_seed": 617,
        },
        "mechanism": {
            "fixed_augmentation_weight": 0.5,
            "training_sample_fraction": 0.25,
            "legacy_health_quantile_argument": {"value": 0.99},
        },
    }


def test_task_matrix_and_capture_command_preserve_frozen_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks = task_matrix(protocol(), design())
    assert len(tasks) == 14
    assert [task["index"] for task in tasks] == list(range(14))
    monkeypatch.setattr(
        "accelerate_strict_v4_csr_caeos_pilot_captures.sys.executable",
        "/python",
    )
    command = capture_command(
        protocol=protocol(),
        design=design(),
        project_root=Path("/project"),
        capture_dir=Path("/captures/suite_0/scenario_0"),
        task=tasks[0],
    )
    assert command[:2] == ["/python", "/project/capture.py"]
    assert command[command.index("--weight") + 1] == "0.5"
    assert command[command.index("--sample-fraction") + 1] == "0.25"
    assert command[command.index("--training-seed") + 1] == "607"
    assert command[command.index("--augmentation-seed") + 1] == "613"
    assert command[command.index("--validation-corruption-seed") + 1] == "617"
    assert command[-2:] == ["--csv", "data_0.csv"]


def test_amendment_requires_partial_capture_and_zero_effect_outputs() -> None:
    observed = {
        "capture_manifests": 2,
        "evaluations": 0,
        "clean_admission": 0,
        "summary": 0,
        "audit": 0,
        "completion": 0,
    }
    amendment = create_amendment(
        protocol(),
        protocol_file_sha256="p" * 64,
        completed_captures=[
            {"path": "a", "sha256": "a" * 64},
            {"path": "b", "sha256": "b" * 64},
        ],
        observed_counts=observed,
        implementation={"accelerator": "accelerator.py"},
        implementation_sha256={"accelerator": "c" * 64},
    )
    assert amendment["manifest_sha256"] == canonical_hash(amendment)
    assert amendment["amendment_scope"]["effect_metrics_read"] is False
    assert amendment["amendment_scope"]["maximum_outer_workers"] == 4

    with pytest.raises(ValueError, match="zero effect outputs"):
        create_amendment(
            protocol(),
            protocol_file_sha256="p" * 64,
            completed_captures=[
                {"path": "a", "sha256": "a" * 64},
                {"path": "b", "sha256": "b" * 64},
            ],
            observed_counts={**observed, "evaluations": 1},
            implementation={"accelerator": "accelerator.py"},
            implementation_sha256={"accelerator": "c" * 64},
        )


def test_paused_runner_snapshot_fails_closed() -> None:
    validate_paused_pilot_snapshot(
        {
            "state": "T",
            "cmdline": "python run_strict_v4_csr_caeos_pilot.py",
            "direct_children": [],
        }
    )
    with pytest.raises(ValueError, match="not stopped"):
        validate_paused_pilot_snapshot(
            {
                "state": "S",
                "cmdline": "python run_strict_v4_csr_caeos_pilot.py",
                "direct_children": [],
            }
        )
    with pytest.raises(ValueError, match="active children"):
        validate_paused_pilot_snapshot(
            {
                "state": "T",
                "cmdline": "python run_strict_v4_csr_caeos_pilot.py",
                "direct_children": [{"state": "R"}],
            }
        )
