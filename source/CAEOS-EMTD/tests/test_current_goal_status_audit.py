from __future__ import annotations

import json
from pathlib import Path

from audit_strict_v4_current_goal_status import (
    derive_self_algorithm_status,
    direct_tournament_design_status,
    json_evidence,
    latest_progress_path,
    pug_cross_suite_design_status,
    pug_cross_suite_implementation_status,
    selected_system_adapter_design_status,
    selected_system_adapter_implementation_status,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def test_latest_progress_uses_numeric_suffix(tmp_path: Path) -> None:
    directory = (
        tmp_path / "results/strict_v4_krc_csr_confirmation_progress_v1"
    )
    directory.mkdir(parents=True)
    for name in ("progress_008.json", "progress_100.json", "progress_052.json"):
        (directory / name).write_text("{}", encoding="utf-8")

    assert latest_progress_path(tmp_path).name == "progress_100.json"


def test_json_evidence_separates_existence_and_canonical_validity(
    tmp_path: Path,
) -> None:
    path = tmp_path / "result.json"
    value = {"schema_version": "test_v1", "state": "complete"}
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(json.dumps(value), encoding="utf-8")

    evidence = json_evidence(path, tmp_path)

    assert evidence["exists"] is True
    assert evidence["canonical_valid"] is True
    assert len(evidence["file_sha256"]) == 64


def test_pug_cross_suite_design_is_frozen_but_not_executed(
    tmp_path: Path,
) -> None:
    path = tmp_path / "results/pug/design.json"
    value = {
        "schema_version": (
            "strict_v4_pug_cross_suite_confirmation_design_v1"
        ),
        "state": (
            "conditionally_frozen_before_pilot_completion_and_"
            "cross_suite_outputs"
        ),
        "execution_admitted_at_freeze": False,
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "paired_task_count": 306,
            "expected_pairwise_pug_runs": 306,
            "expected_fresh_opendetect_runs": 306,
        },
        "formal_result_counts_at_freeze": {
            "activation.json": 0,
            "summary.json": 0,
            "audit.json": 0,
            "tasks": 0,
        },
        "required_future_implementation": [f"item-{i}" for i in range(7)],
    }
    write_canonical(path, value)

    status = pug_cross_suite_design_status(path, tmp_path)

    assert status["frozen"] is True
    assert status["execution_admitted"] is False
    assert status["formal_result_count"] == 0
    assert status["candidate_task_count"] == 306
    assert status["fresh_opendetect_task_count"] == 306


def test_pug_cross_suite_implementation_tracks_partial_readiness(
    tmp_path: Path,
) -> None:
    (tmp_path / "write_strict_v4_pug_cross_suite_activation.py").write_text(
        "activation\n", encoding="utf-8"
    )
    (
        tmp_path / "create_strict_v4_pug_cross_suite_execution_protocol.py"
    ).write_text("protocol\n", encoding="utf-8")

    status = pug_cross_suite_implementation_status(tmp_path)

    assert status["required_count"] == 7
    assert status["ready_count"] == 2
    assert status["complete"] is False
    assert (
        status["files"][
            "write_strict_v4_pug_cross_suite_activation.py"
        ]["exists"]
        is True
    )
    assert (
        status["files"]["run_strict_v4_pug_cross_suite_confirmation.py"][
            "exists"
        ]
        is False
    )


def test_direct_tournament_design_is_frozen_but_not_executed(
    tmp_path: Path,
) -> None:
    path = tmp_path / "results/tournament/design.json"
    value = {
        "schema_version": (
            "strict_v4_self_algorithm_direct_tournament_design_v1"
        ),
        "state": "conditionally_frozen_before_dual_positive_outcome",
        "execution_admitted_at_freeze": False,
        "activation": {
            "dual_positive_without_tournament_is_not_final_selection": True,
        },
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "seeds": [809, 811, 821],
            "paired_task_count": 306,
            "expected_incumbent_runs": 306,
            "expected_challenger_runs": 306,
            "expected_paired_evaluations": 918,
        },
        "formal_output_counts_at_freeze": {
            "protocol.json": 0,
            "summary.json": 0,
            "audit.json": 0,
            "execution_complete.json": 0,
            "task_records": 0,
        },
        "required_future_implementation": [f"item-{i}" for i in range(7)],
    }
    write_canonical(path, value)

    status = direct_tournament_design_status(path, tmp_path)

    assert status["frozen"] is True
    assert status["execution_admitted"] is False
    assert status["formal_result_count"] == 0
    assert status["paired_task_count"] == 306


def test_selected_system_adapter_design_is_frozen_but_not_executed(
    tmp_path: Path,
) -> None:
    path = tmp_path / "results/selected_system/design.json"
    algorithms = [
        "caeos_pairwise",
        "krc_csr_caeos_v1",
        "rrc_csr_caeos_v1",
        "caeos_pug",
    ]
    runtime_files = [
        "caeos/pairwise_runtime.py",
        "caeos/krc_csr_runtime.py",
        "caeos/rrc_csr_runtime.py",
        "caeos/selected_system_runtime.py",
    ]
    remaining = [
        "final_selection_activation_writer",
        "algorithm_neutral_external_protocol_and_runner",
        "algorithm_neutral_parrot_protocol_and_runner",
        "algorithm_neutral_efficiency_protocol_and_runner",
        "algorithm_neutral_integrated_auditor",
        "resource_safe_conditional_watcher",
    ]
    value = {
        "schema_version": (
            "strict_v4_selected_system_downstream_adapter_design_v1"
        ),
        "state": "frozen_before_final_self_algorithm_selection",
        "execution_admitted_at_freeze": False,
        "activation": {"allowed_selected_algorithms": algorithms},
        "runtime_contract": {
            "schema_version": "strict_v4_selected_system_runtime_v1",
            "required_output": ["prediction", "probability", "risk"],
            "supported_source_runtime": {
                algorithm: {} for algorithm in algorithms
            },
        },
        "implementation_status_at_freeze": {
            "common_runtime_adapter_complete": True,
            "remaining_components": remaining,
            "runtime_implementation_sha256": {
                runtime_file: "a" * 64 for runtime_file in runtime_files
            },
        },
        "formal_output_counts_at_freeze": {
            "activation.json": 0,
            "selected_system_protocol.json": 0,
            "external_malicious_protocol.json": 0,
            "parrot_safety_protocol.json": 0,
            "efficiency_protocol.json": 0,
            "integrated_audit.json": 0,
            "execution_complete.json": 0,
        },
        "claim_boundary": {
            "common_runtime_support_is_not_downstream_execution": True,
        },
    }
    write_canonical(path, value)

    status = selected_system_adapter_design_status(path, tmp_path)

    assert status["frozen"] is True
    assert status["common_runtime_adapter_complete"] is True
    assert status["execution_admitted"] is False
    assert status["formal_result_count"] == 0
    assert status["remaining_component_count"] == 6


def test_selected_system_adapter_implementation_tracks_partial_readiness(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "write_strict_v4_selected_system_activation.py"
    ).write_text("activation\n", encoding="utf-8")

    status = selected_system_adapter_implementation_status(tmp_path)

    assert status["required_count"] == 6
    assert status["ready_count"] == 1
    assert status["complete"] is False
    assert (
        status["files"]["final_selection_activation_writer"]["exists"]
        is True
    )
    assert (
        status["files"][
            "algorithm_neutral_external_protocol_and_runner"
        ]["exists"]
        is False
    )


def write_canonical(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_krc_decision(root: Path, positive: bool) -> dict:
    selected = "krc_csr_caeos_v1" if positive else "caeos_pairwise"
    decision = {
        "schema_version": "strict_v4_krc_downstream_decision_v1",
        "state": "complete",
        "krc_effect_gate_passes": positive,
        "selected_algorithm": selected,
        "rrc_fallback_execution_permitted": not positive,
    }
    write_canonical(
        root
        / "results/strict_v4_krc_integrated_comprehensive_sota_v2/"
        "downstream_decision.json",
        decision,
    )
    return decision


def write_pug_confirmation(root: Path, positive: bool) -> Path:
    path = (
        root / "results/strict_v4_pug_confirmation_v1/confirmation.json"
    )
    value = {
        "schema_version": "strict_v4_pug_confirmation_v1",
        "decision": {
            "passes": positive,
            "selected_method": "caeos_pug" if positive else "caeos_pairwise",
            "cross_suite_execution_admitted": False,
        },
    }
    write_canonical(path, value)
    return path


def write_pug_cross_suite_terminal(root: Path, positive: bool) -> None:
    base = root / "results/strict_v4_pug_cross_suite_confirmation_v1"
    protocol_path = base / "protocol.json"
    summary_path = base / "summary.json"
    audit_path = base / "audit.json"
    write_canonical(
        protocol_path,
        {
            "schema_version": (
                "strict_v4_pug_cross_suite_execution_protocol_v1"
            ),
            "state": (
                "frozen_after_positive_pilot_before_cross_suite_execution"
            ),
        },
    )
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    summary = {
        "schema_version": (
            "strict_v4_pug_cross_suite_confirmation_summary_v1"
        ),
        "state": "cross_suite_confirmation_summary_complete",
        "validation": {
            "passes": True,
            "task_record_count": 306,
            "scenario_count": 102,
            "suite_count": 7,
        },
        "decision": {"passes": positive},
        "input_evidence": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "protocol_file_sha256": file_hash(protocol_path),
        },
    }
    write_canonical(summary_path, summary)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    relative = base.relative_to(root).as_posix()
    audit = {
        "schema_version": (
            "strict_v4_pug_cross_suite_confirmation_audit_v1"
        ),
        "state": "cross_suite_confirmation_independent_audit_complete",
        "integrity": {"passes": True},
        "effect": {"passes": positive},
        "selection": {
            "candidate_selected": positive,
            "selected_algorithm": (
                "caeos_pug" if positive else "upstream_incumbent"
            ),
        },
        "input_manifest_sha256": {
            "protocol": protocol["manifest_sha256"],
            "summary": summary["manifest_sha256"],
        },
        "input_file_sha256": {
            f"{relative}/protocol.json": file_hash(protocol_path),
            f"{relative}/summary.json": file_hash(summary_path),
        },
    }
    write_canonical(audit_path, audit)
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    write_canonical(
        base / "execution_complete.json",
        {
            "schema_version": (
                "strict_v4_pug_cross_suite_confirmation_completion_v1"
            ),
            "state": "complete",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "summary_manifest_sha256": summary["manifest_sha256"],
            "summary_file_sha256": file_hash(summary_path),
            "audit_manifest_sha256": audit["manifest_sha256"],
            "audit_file_sha256": file_hash(audit_path),
            "effect_passes": positive,
            "candidate_selected_by_this_stage": positive,
        },
    )


def test_self_selection_accepts_krc_positive_rrc_not_required_and_pug_negative(
    tmp_path: Path,
) -> None:
    decision = write_krc_decision(tmp_path, positive=True)
    write_canonical(
        tmp_path
        / "results/strict_v4_rrc_csr_confirmation_v1/not_required.json",
        {
            "schema_version": "strict_v4_rrc_csr_not_required_v1",
            "state": "terminal_not_required_krc_selected",
            "krc_downstream_decision_manifest_sha256": decision[
                "manifest_sha256"
            ],
            "selected_algorithm": "krc_csr_caeos_v1",
            "rrc_execution_started": False,
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=False)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is True
    assert status["selected_algorithm"] == "krc_csr_caeos_v1"
    assert status["blockers"] == []


def test_self_selection_accepts_rrc_positive_after_krc_negative(
    tmp_path: Path,
) -> None:
    write_krc_decision(tmp_path, positive=False)
    result = tmp_path / "results/strict_v4_rrc_csr_confirmation_v1"
    summary = {
        "schema_version": "strict_v4_rrc_csr_confirmation_summary_v1",
        "state": "complete",
        "passes": True,
        "selection": "rrc_csr_caeos_v1",
    }
    write_canonical(result / "summary.json", summary)
    write_canonical(
        result / "audit.json",
        {
            "schema_version": "strict_v4_rrc_csr_confirmation_audit_v1",
            "state": "complete",
            "integrity_passes": True,
            "effect_gate_passes": True,
            "selection": "rrc_csr_caeos_v1",
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=False)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is True
    assert status["selected_algorithm"] == "rrc_csr_caeos_v1"


def test_self_selection_does_not_treat_positive_pug_pilot_as_final(
    tmp_path: Path,
) -> None:
    decision = write_krc_decision(tmp_path, positive=True)
    write_canonical(
        tmp_path
        / "results/strict_v4_rrc_csr_confirmation_v1/not_required.json",
        {
            "schema_version": "strict_v4_rrc_csr_not_required_v1",
            "state": "terminal_not_required_krc_selected",
            "krc_downstream_decision_manifest_sha256": decision[
                "manifest_sha256"
            ],
            "selected_algorithm": "krc_csr_caeos_v1",
            "rrc_execution_started": False,
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=True)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is False
    assert (
        status["pug_branch"]["status"]
        == "pilot_positive_cross_suite_confirmation_required"
    )


def test_self_selection_requires_tournament_for_krc_and_pug_positive(
    tmp_path: Path,
) -> None:
    decision = write_krc_decision(tmp_path, positive=True)
    write_canonical(
        tmp_path
        / "results/strict_v4_rrc_csr_confirmation_v1/not_required.json",
        {
            "schema_version": "strict_v4_rrc_csr_not_required_v1",
            "state": "terminal_not_required_krc_selected",
            "krc_downstream_decision_manifest_sha256": decision[
                "manifest_sha256"
            ],
            "selected_algorithm": "krc_csr_caeos_v1",
            "rrc_execution_started": False,
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=True)
    write_pug_cross_suite_terminal(tmp_path, positive=True)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is False
    assert status["selected_algorithm"] == "krc_csr_caeos_v1"
    assert status["provisional_challenger"] == "caeos_pug"
    assert (
        status["pug_branch"]["status"]
        == "cross_suite_positive_direct_tournament_required"
    )
    assert status["direct_tournament"]["required"] is True


def test_self_selection_accepts_negative_pug_cross_suite_terminal(
    tmp_path: Path,
) -> None:
    decision = write_krc_decision(tmp_path, positive=True)
    write_canonical(
        tmp_path
        / "results/strict_v4_rrc_csr_confirmation_v1/not_required.json",
        {
            "schema_version": "strict_v4_rrc_csr_not_required_v1",
            "state": "terminal_not_required_krc_selected",
            "krc_downstream_decision_manifest_sha256": decision[
                "manifest_sha256"
            ],
            "selected_algorithm": "krc_csr_caeos_v1",
            "rrc_execution_started": False,
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=True)
    write_pug_cross_suite_terminal(tmp_path, positive=False)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is True
    assert status["selected_algorithm"] == "krc_csr_caeos_v1"
    assert (
        status["pug_branch"]["status"]
        == "cross_suite_negative_retain_upstream_incumbent"
    )


def test_self_selection_accepts_pug_when_upstream_retains_pairwise(
    tmp_path: Path,
) -> None:
    write_krc_decision(tmp_path, positive=False)
    result = tmp_path / "results/strict_v4_rrc_csr_confirmation_v1"
    write_canonical(
        result / "summary.json",
        {
            "schema_version": "strict_v4_rrc_csr_confirmation_summary_v1",
            "state": "complete",
            "passes": False,
            "selection": "caeos_pairwise",
        },
    )
    write_canonical(
        result / "audit.json",
        {
            "schema_version": "strict_v4_rrc_csr_confirmation_audit_v1",
            "state": "complete",
            "integrity_passes": True,
            "effect_gate_passes": False,
            "selection": "caeos_pairwise",
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=True)
    write_pug_cross_suite_terminal(tmp_path, positive=True)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is True
    assert status["selected_algorithm"] == "caeos_pug"
    assert status["direct_tournament"]["required"] is False


def test_self_selection_rejects_cross_suite_completion_hash_drift(
    tmp_path: Path,
) -> None:
    decision = write_krc_decision(tmp_path, positive=True)
    write_canonical(
        tmp_path
        / "results/strict_v4_rrc_csr_confirmation_v1/not_required.json",
        {
            "schema_version": "strict_v4_rrc_csr_not_required_v1",
            "state": "terminal_not_required_krc_selected",
            "krc_downstream_decision_manifest_sha256": decision[
                "manifest_sha256"
            ],
            "selected_algorithm": "krc_csr_caeos_v1",
            "rrc_execution_started": False,
        },
    )
    pug = write_pug_confirmation(tmp_path, positive=True)
    write_pug_cross_suite_terminal(tmp_path, positive=True)
    completion_path = (
        tmp_path
        / "results/strict_v4_pug_cross_suite_confirmation_v1/"
        "execution_complete.json"
    )
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    completion["summary_file_sha256"] = "0" * 64
    write_canonical(completion_path, completion)

    status = derive_self_algorithm_status(
        tmp_path,
        krc_terminal_complete=True,
        pug_confirmation_path=pug,
    )

    assert status["final"] is False
    assert (
        status["pug_branch"]["status"]
        == "cross_suite_confirmation_inconsistent"
    )
