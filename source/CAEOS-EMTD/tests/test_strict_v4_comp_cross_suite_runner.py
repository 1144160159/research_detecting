from __future__ import annotations

from pathlib import Path

import pytest

from run_strict_v4_comp_cross_suite_confirmation import (
    SEEDS,
    SUITE_SPECS,
    build_opendetect_command,
    build_pairwise_command,
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
            "model_jobs": 8,
            "estimators": 80,
            "pairwise_risk_selection": (
                "nested_boundary_pairwise_pseudo_unknown_blend"
            ),
            "pairwise_policy_name": (
                "strict_v4_comp_cross_suite_pairwise_v1"
            ),
        },
    }


@pytest.mark.parametrize("suite", sorted(SUITE_SPECS))
def test_commands_bind_frozen_seed_suite_and_cache(
    tmp_path: Path, suite: str
) -> None:
    pairwise = build_pairwise_command(
        protocol(), tmp_path, tmp_path / "cache", tmp_path / "pairwise", suite
    )
    opendetect = build_opendetect_command(
        protocol(), tmp_path, tmp_path / "cache", tmp_path / "od", suite
    )
    cache_args = suite_cache_arguments(tmp_path / "cache", suite)

    assert ",".join(map(str, SEEDS)) in pairwise
    assert ",".join(map(str, SEEDS)) in opendetect
    assert "strict_v4_comp_cross_suite_pairwise_v1" in pairwise
    assert "--boundary-training-objective" in pairwise
    assert "pairwise" in pairwise
    assert "opendetect" in opendetect
    assert all(value in pairwise for value in cache_args)
    assert all(value in opendetect for value in cache_args)


def test_validate_suite_artifacts_rejects_partial_pair(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="missing paired artifacts"):
        validate_suite_artifacts(
            protocol(),
            tmp_path / "pairwise",
            tmp_path / "opendetect",
            "edge_iiot",
        )
