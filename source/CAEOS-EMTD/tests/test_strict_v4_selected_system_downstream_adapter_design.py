import pytest

from create_strict_v4_selected_system_downstream_adapter_design import (
    ALGORITHMS,
    IMPLEMENTATION_FILES,
    build_design,
)


def sources() -> tuple[dict, dict, dict, dict]:
    return (
        {"execution_admitted": True, "manifest_sha256": "krc"},
        {"execution_admitted": False, "manifest_sha256": "rrc"},
        {
            "confirmation_universe": {"scenario_count": 102},
            "manifest_sha256": "pug",
        },
        {
            "confirmation_universe": {"scenario_count": 102},
            "manifest_sha256": "tournament",
        },
    )


def empty_counts() -> dict[str, int]:
    return {
        "activation.json": 0,
        "selected_system_protocol.json": 0,
        "external_malicious_protocol.json": 0,
        "parrot_safety_protocol.json": 0,
        "efficiency_protocol.json": 0,
        "integrated_audit.json": 0,
        "execution_complete.json": 0,
    }


def test_design_freezes_all_selected_algorithms_and_branches() -> None:
    krc, rrc, pug, tournament = sources()
    design = build_design(
        krc_protocol=krc,
        rrc_implementation=rrc,
        pug_cross_suite_design=pug,
        direct_tournament_design=tournament,
        input_file_sha256={"input": "sha"},
        implementation_sha256={
            name: f"sha-{index}"
            for index, name in enumerate(IMPLEMENTATION_FILES)
        },
        creator_sha256="creator",
        observed_output_counts=empty_counts(),
    )

    assert design["activation"]["allowed_selected_algorithms"] == list(
        ALGORITHMS
    )
    assert (
        design["implementation_status_at_freeze"][
            "common_runtime_adapter_complete"
        ]
        is True
    )
    assert len(
        design["implementation_status_at_freeze"]["remaining_components"]
    ) == 6
    assert design["execution_admitted_at_freeze"] is False
    assert design["parrot_benign_safety_branch"][
        "does_not_treat_benign_as_attack_subclassification"
    ]


def test_design_rejects_partial_runtime_implementation() -> None:
    krc, rrc, pug, tournament = sources()
    with pytest.raises(ValueError, match="complete selected-system runtime"):
        build_design(
            krc_protocol=krc,
            rrc_implementation=rrc,
            pug_cross_suite_design=pug,
            direct_tournament_design=tournament,
            input_file_sha256={"input": "sha"},
            implementation_sha256={"caeos/pairwise_runtime.py": "sha"},
            creator_sha256="creator",
            observed_output_counts=empty_counts(),
        )


def test_design_rejects_preexisting_downstream_output() -> None:
    krc, rrc, pug, tournament = sources()
    counts = empty_counts()
    counts["activation.json"] = 1
    with pytest.raises(ValueError, match="zero formal output"):
        build_design(
            krc_protocol=krc,
            rrc_implementation=rrc,
            pug_cross_suite_design=pug,
            direct_tournament_design=tournament,
            input_file_sha256={"input": "sha"},
            implementation_sha256={
                name: f"sha-{index}"
                for index, name in enumerate(IMPLEMENTATION_FILES)
            },
            creator_sha256="creator",
            observed_output_counts=counts,
        )
