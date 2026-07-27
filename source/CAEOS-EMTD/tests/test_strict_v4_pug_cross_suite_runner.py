from __future__ import annotations

from pathlib import Path

import pytest

from run_strict_v4_pug_cross_suite_confirmation import (
    PUG_POLICY,
    SEEDS,
    SUITE_SPECS,
    build_candidate_command,
    build_opendetect_command,
    suite_cache_arguments,
    validate_suite_artifacts,
)


def protocol():
    scenarios = {
        suite: [f"{suite}_scenario"] for suite in SUITE_SPECS
    }
    return {
        "confirmation_universe": {"scenarios_by_suite": scenarios},
        "execution_controls": {
            "workers": 2,
            "model_jobs": 8,
            "estimators": 80,
            "opendetect_epochs": 0,
            "candidate_risk_selection": (
                "nested_pug_continuous_outer_min_p"
            ),
            "candidate_policy_name": PUG_POLICY,
            "pseudo_unknown_max_alpha": 0.5,
            "pseudo_unknown_min_fold_gain": -0.05,
            "boundary_hard_pseudo_fraction": 0.5,
            "boundary_interpolation": 0.5,
            "boundary_max_per_task": 512,
            "boundary_training_objective": "pairwise",
        },
    }


@pytest.mark.parametrize("suite", sorted(SUITE_SPECS))
def test_commands_bind_frozen_seed_suite_cache_and_pug_policy(
    tmp_path: Path, suite: str
) -> None:
    candidate = build_candidate_command(
        protocol(),
        tmp_path,
        tmp_path / "cache",
        tmp_path / "candidate",
        suite,
    )
    opendetect = build_opendetect_command(
        protocol(),
        tmp_path,
        tmp_path / "cache",
        tmp_path / "od",
        suite,
    )
    cache_args = suite_cache_arguments(tmp_path / "cache", suite)

    assert ",".join(map(str, SEEDS)) in candidate
    assert ",".join(map(str, SEEDS)) in opendetect
    assert "nested_pug_continuous_outer_min_p" in candidate
    assert PUG_POLICY in candidate
    assert "--boundary-training-objective" in candidate
    assert "pairwise" in candidate
    assert "opendetect" in opendetect
    assert all(value in candidate for value in cache_args)
    assert all(value in opendetect for value in cache_args)


def test_validate_suite_artifacts_rejects_partial_pair(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="missing paired artifacts"):
        validate_suite_artifacts(
            protocol(),
            tmp_path / "candidate",
            tmp_path / "opendetect",
            "edge_iiot",
        )
