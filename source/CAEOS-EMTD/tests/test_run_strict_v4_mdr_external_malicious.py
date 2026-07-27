from pathlib import Path

import pytest

from run_strict_v4_mdr_external_malicious import (
    capture_command,
    require_clean_or_complete,
    slug,
)


def protocol():
    return {
        "mdr_policy": {
            "augmentation_weight": 0.25,
            "sample_fraction": 0.25,
            "health_quantile": 0.99,
        },
        "pairwise_runtime_policy": {
            "estimators": 80,
            "jobs": 8,
            "known_acceptance": 0.95,
            "risk_selection": "pairwise",
            "pseudo_unknown_max_alpha": 0.5,
            "pseudo_unknown_min_fold_gain": -0.05,
            "boundary_hard_pseudo_fraction": 0.5,
            "boundary_interpolation": 0.5,
            "boundary_max_per_task": 512,
            "boundary_training_objective": "pairwise",
        },
    }


def scenario():
    return {
        "dataset": "LSNM2024",
        "unknown_attack_family": "attack/a",
        "benign_label": "normal",
        "seed": 223,
        "augmentation_seed": 101,
        "validation_profile_seed": 103,
        "csv": "/data/seed223.csv",
    }


def test_capture_command_binds_frozen_mdr_and_split():
    command = capture_command(
        python="python",
        project_root=Path("/project"),
        capture_dir=Path("/run/capture"),
        scenario=scenario(),
        protocol=protocol(),
    )
    joined = " ".join(command)
    assert "--weight 0.25" in joined
    assert "--augmentation-seed 101" in joined
    assert "--validation-corruption-seed 103" in joined
    assert "--split-strategy fingerprint_grouped" in joined
    assert "--unknown-classes attack/a" in joined


def test_partial_directory_fails_closed(tmp_path):
    output = tmp_path / "candidate"
    output.mkdir()
    (output / "metrics.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="partial MDR external"):
        require_clean_or_complete(
            output, ["metrics.json", "provenance.json"]
        )


def test_empty_directory_is_resumable(tmp_path):
    output = tmp_path / "candidate"
    output.mkdir()
    assert not require_clean_or_complete(output, ["metrics.json"])


def test_slug_is_stable():
    assert slug("DNS / Attack") == "dns_attack"
