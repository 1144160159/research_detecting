from pathlib import Path

import pytest

from create_strict_v4_self_algorithm_direct_tournament_design import (
    build_design,
)


def source_values() -> tuple[dict, dict, dict]:
    krc = {
        "execution_admitted": True,
        "manifest_sha256": "krc",
    }
    rrc = {
        "execution_admitted": False,
        "state": (
            "full_execution_chain_implemented_waiting_terminal_krc_decision"
        ),
        "manifest_sha256": "rrc",
    }
    scenarios = {
        f"suite-{suite}": [
            f"scenario-{suite}-{index}"
            for index in range(15 if suite < 4 else 14)
        ]
        for suite in range(7)
    }
    assert sum(len(values) for values in scenarios.values()) == 102
    pug = {
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "scenarios_by_suite": scenarios,
        },
        "manifest_sha256": "pug",
    }
    return krc, rrc, pug


def test_design_freezes_fresh_direct_tournament_at_zero_results() -> None:
    krc, rrc, pug = source_values()
    design = build_design(
        krc_protocol=krc,
        rrc_implementation=rrc,
        pug_cross_suite_design=pug,
        input_file_sha256={"a": "1"},
        creator_sha256="creator",
        observed_output_counts={
            "protocol.json": 0,
            "summary.json": 0,
            "audit.json": 0,
            "execution_complete.json": 0,
            "task_records": 0,
        },
    )

    universe = design["confirmation_universe"]
    assert universe["paired_task_count"] == 306
    assert universe["expected_paired_evaluations"] == 918
    assert universe["seeds"] == [809, 811, 821]
    assert design["execution_admitted_at_freeze"] is False
    assert len(design["required_future_implementation"]) == 7
    assert (
        design["activation"][
            "dual_positive_without_tournament_is_not_final_selection"
        ]
        is True
    )


def test_design_rejects_any_preexisting_formal_output() -> None:
    krc, rrc, pug = source_values()
    with pytest.raises(ValueError, match="zero formal output"):
        build_design(
            krc_protocol=krc,
            rrc_implementation=rrc,
            pug_cross_suite_design=pug,
            input_file_sha256={"a": "1"},
            creator_sha256="creator",
            observed_output_counts={
                "protocol.json": 1,
                "summary.json": 0,
                "audit.json": 0,
                "execution_complete.json": 0,
                "task_records": 0,
            },
        )


def test_design_rejects_incomplete_scenario_universe() -> None:
    krc, rrc, pug = source_values()
    pug["confirmation_universe"]["scenarios_by_suite"]["suite-0"].pop()
    with pytest.raises(ValueError, match="102-scenario"):
        build_design(
            krc_protocol=krc,
            rrc_implementation=rrc,
            pug_cross_suite_design=pug,
            input_file_sha256={"a": "1"},
            creator_sha256="creator",
            observed_output_counts={
                "protocol.json": 0,
                "summary.json": 0,
                "audit.json": 0,
                "execution_complete.json": 0,
                "task_records": 0,
            },
        )
