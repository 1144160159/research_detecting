from __future__ import annotations

import json
from pathlib import Path

from audit_strict_v4_selected_system_preconfirmation_design import audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_design import (
    ALGORITHMS,
    CORRUPTION_FAMILIES,
    IMPLEMENTATION_FILES,
    MAIN_METHODS,
    build_design,
)
from write_strict_v4_selected_system_preconfirmation_activation import (
    build_activation,
)


def write(path: Path, value: dict) -> Path:
    value["manifest_sha256"] = canonical_hash(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def fixture(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "project"
    for name in IMPLEMENTATION_FILES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n", encoding="utf-8")
    classic = write(
        tmp_path / "classic.json",
        {
            "schema_version": "strict_v4_classical_main_baseline_protocol_v1",
            "main_table": {
                "baselines": [{"method": method} for method in MAIN_METHODS]
            },
        },
    )
    tasks = []
    for index in range(102):
        for seed in (647, 653, 659):
            tasks.append(
                {
                    "suite": f"suite_{index % 7}",
                    "scenario": f"scenario_{index:03d}",
                    "training_seed": seed,
                }
            )
    krc = write(
        tmp_path / "krc.json",
        {
            "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
            "confirmation": {"tasks": tasks},
        },
    )
    corruption = write(
        tmp_path / "corruption.json",
        {
            "schema_version": (
                "strict_v4_postselection_corruption_suite_gate_protocol_v1"
            ),
            "corruption_families": list(CORRUPTION_FAMILIES),
            "maximum_mean_degradation": {
                "known_macro_f1": 0.1,
                "unknown_auroc": 0.15,
                "unknown_aupr": 0.15,
                "unknown_fpr95": 0.2,
                "oscr": 0.15,
            },
        },
    )
    comparative = write(
        tmp_path / "comparative.json",
        {
            "schema_version": "strict_v4_comparative_corruption_protocol_v2",
            "corruption_conditions": {
                "families": list(CORRUPTION_FAMILIES),
                "fixed_severity": {
                    family: 0.5 for family in CORRUPTION_FAMILIES
                },
                "modality_selection_rule": "frozen",
            },
            "comparative_robustness_gate": {"passes_required": True},
        },
    )
    adapter = write(
        tmp_path / "adapter.json",
        {
            "schema_version": (
                "strict_v4_selected_system_downstream_adapter_design_v1"
            ),
            "activation": {
                "allowed_selected_algorithms": list(ALGORITHMS)
            },
        },
    )
    return {
        "root": root,
        "classic": classic,
        "krc": krc,
        "corruption": corruption,
        "comparative": comparative,
        "adapter": adapter,
    }


def design(tmp_path: Path) -> tuple[dict, dict[str, Path]]:
    paths = fixture(tmp_path)
    value = build_design(
        project_root=paths["root"],
        classic_protocol_path=paths["classic"],
        krc_protocol_path=paths["krc"],
        corruption_protocol_path=paths["corruption"],
        comparative_protocol_path=paths["comparative"],
        adapter_design_path=paths["adapter"],
        result_root=paths["root"] / "results/preconfirmation",
    )
    return value, paths


def test_design_freezes_full_clean_and_corruption_universe(
    tmp_path: Path,
) -> None:
    value, _paths = design(tmp_path)
    universe = value["universe"]
    assert universe["source_task_count"] == 306
    assert universe["classic_main_baseline_count"] == 7
    assert universe["paired_corruption_record_count"] == 1530
    assert value["manifest_sha256"] == canonical_hash(value)


def test_independent_design_audit_rejects_implementation_drift(
    tmp_path: Path,
) -> None:
    value, paths = design(tmp_path)
    design_path = tmp_path / "design.json"
    design_path.write_text(json.dumps(value), encoding="utf-8")
    assert audit(design_path, paths["root"])["passed"] is True
    (paths["root"] / IMPLEMENTATION_FILES[0]).write_text(
        "drift\n", encoding="utf-8"
    )
    result = audit(design_path, paths["root"])
    assert result["passed"] is False
    assert result["checks"]["implementation_hashes_match"] is False


def test_preconfirmation_activation_waits_for_final_selection(
    tmp_path: Path,
) -> None:
    value, _paths = design(tmp_path)
    goal = {
        "schema_version": "strict_v4_current_goal_status_audit_v1",
        "selected_algorithm": "caeos_pairwise",
        "requirements": {
            "best_self_algorithm_finally_selected": {
                "satisfied": False,
                "current_incumbent": "caeos_pairwise",
            }
        },
        "evidence": {
            "self_algorithm_selection": {
                "final": False,
                "selected_algorithm": "caeos_pairwise",
            }
        },
    }
    goal["manifest_sha256"] = canonical_hash(goal)
    assert (
        build_activation(
            goal,
            value,
            goal_file_sha256="a" * 64,
            design_file_sha256="b" * 64,
        )
        is None
    )
    goal["requirements"]["best_self_algorithm_finally_selected"][
        "satisfied"
    ] = True
    goal["evidence"]["self_algorithm_selection"]["final"] = True
    goal["manifest_sha256"] = canonical_hash(goal)
    activation = build_activation(
        goal,
        value,
        goal_file_sha256="a" * 64,
        design_file_sha256="b" * 64,
    )
    assert activation["selected_algorithm"] == "caeos_pairwise"
    assert activation["manifest_sha256"] == canonical_hash(activation)
