from pathlib import Path

from run_strict_v4_krc_external_malicious import (
    base_arguments,
    capture_command,
    opendetect_command,
    task_block,
)


def task():
    return {
        "dataset": "LSNM2024",
        "unknown_attack_family": "attack-a",
        "benign_label": "normal",
        "training_seed": 223,
        "prepared_seed": 223,
        "split_seed": 223,
        "opendetect_seed": 223,
        "augmentation_seed": 1234,
        "validation_profile_seed": 5678,
        "csv": "/data/seed223.csv",
        "config": "/project/config.json",
    }


def policy():
    return {
        "estimators": 80,
        "jobs": 8,
        "known_acceptance": 0.95,
        "risk_selection": "nested",
        "pseudo_unknown_max_alpha": 0.5,
        "pseudo_unknown_min_fold_gain": -0.05,
        "boundary_hard_pseudo_fraction": 0.5,
        "boundary_interpolation": 0.5,
        "boundary_max_per_task": 512,
        "boundary_training_objective": "pairwise",
    }


def test_all_split_coupled_commands_use_training_seed():
    value = task()
    protocol = {
        "krc_policy": {
            "augmentation_weight": 0.5,
            "sample_fraction": 0.25,
            "health_quantile": 0.99,
        },
        "pairwise_runtime_policy": policy(),
    }
    capture = capture_command(
        python="python",
        project_root=Path("/project"),
        capture_dir=Path("/run/capture"),
        task=value,
        protocol=protocol,
    )
    arguments = base_arguments(value, policy())
    opendetect = opendetect_command(
        python="python",
        project_root=Path("/project"),
        output=Path("/run/opendetect"),
        task=value,
        policy={
            "epochs": 100,
            "patience": 100,
            "hidden_dim": 128,
            "embedding_dim": 64,
            "known_acceptance": 0.95,
        },
    )
    assert capture[capture.index("--training-seed") + 1] == "223"
    assert capture[capture.index("--augmentation-seed") + 1] == "1234"
    assert (
        capture[capture.index("--validation-corruption-seed") + 1]
        == "5678"
    )
    assert arguments[arguments.index("--seed") + 1] == "223"
    assert opendetect[opendetect.index("--seed") + 1] == "223"


def test_task_block_is_deterministic_and_seed_scoped():
    value = task()
    first = task_block(Path("/run"), value)
    second = task_block(Path("/run"), dict(value))
    assert first == second
    assert first.as_posix().endswith("LSNM2024/attack_a_seed223")
