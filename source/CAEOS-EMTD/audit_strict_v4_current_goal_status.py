from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


MAIN_BASELINES = (
    "MSP",
    "Energy",
    "OpenMax",
    "kNN",
    "ViM",
    "Mahalanobis++",
    "OpenDetect",
)
DOCUMENTATION_SNAPSHOT_SCHEMA = "strict_v4_documentation_snapshot_v1"
REQUIRED_DOCUMENTS = (
    "README.md",
    "02_实验设计/01_核心协议/创新点与基线对比矩阵.md",
    (
        "03_实验报告/01_主线验证/"
        "strict-v4全面SOTA与自有算法优化阶段报告.md"
    ),
    "06_阶段性评价/CAEOS-EMTD评价意见吸收与纠偏记录_2026-07-27.md",
)
PUG_CROSS_SUITE_IMPLEMENTATION_FILES = (
    "write_strict_v4_pug_cross_suite_activation.py",
    "create_strict_v4_pug_cross_suite_execution_protocol.py",
    "run_strict_v4_pug_cross_suite_confirmation.py",
    "evaluate_strict_v4_pug_cross_suite_confirmation.py",
    "summarize_strict_v4_pug_cross_suite_confirmation.py",
    "audit_strict_v4_pug_cross_suite_confirmation.py",
    "watch_strict_v4_pug_cross_suite_confirmation.py",
)
DIRECT_TOURNAMENT_IMPLEMENTATION_FILES = (
    "write_strict_v4_self_algorithm_direct_tournament_activation.py",
    "create_strict_v4_self_algorithm_direct_tournament_execution_protocol.py",
    "run_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "evaluate_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "summarize_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "audit_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "watch_strict_v4_self_algorithm_direct_tournament_confirmation.py",
)
SELECTED_SYSTEM_ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)
SELECTED_SYSTEM_RUNTIME_FILES = (
    "caeos/pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/rrc_csr_runtime.py",
    "caeos/selected_system_runtime.py",
)
SELECTED_SYSTEM_REMAINING_COMPONENTS = (
    "final_selection_activation_writer",
    "algorithm_neutral_external_protocol_and_runner",
    "algorithm_neutral_parrot_protocol_and_runner",
    "algorithm_neutral_efficiency_protocol_and_runner",
    "algorithm_neutral_integrated_auditor",
    "resource_safe_conditional_watcher",
)
SELECTED_SYSTEM_ADAPTER_IMPLEMENTATION_FILES = {
    "final_selection_activation_writer": (
        "write_strict_v4_selected_system_activation.py"
    ),
    "algorithm_neutral_external_protocol_and_runner": (
        "run_strict_v4_selected_system_external_malicious.py"
    ),
    "algorithm_neutral_parrot_protocol_and_runner": (
        "run_strict_v4_selected_system_parrot_safety.py"
    ),
    "algorithm_neutral_efficiency_protocol_and_runner": (
        "run_strict_v4_selected_system_efficiency.py"
    ),
    "algorithm_neutral_integrated_auditor": (
        "audit_strict_v4_selected_system_integrated.py"
    ),
    "resource_safe_conditional_watcher": (
        "watch_strict_v4_selected_system_downstream.py"
    ),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def json_evidence(path: Path, root: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": path.relative_to(root).as_posix(),
            "exists": False,
        }
    value = load(path)
    manifest = value.get("manifest_sha256")
    return {
        "path": path.relative_to(root).as_posix(),
        "exists": True,
        "file_sha256": file_hash(path),
        "schema_version": value.get("schema_version"),
        "manifest_sha256": manifest,
        "canonical_valid": isinstance(manifest, str)
        and manifest == canonical_hash(value),
    }


def documentation_snapshot_status(root: Path) -> dict[str, Any]:
    base = root / "results/strict_v4_documentation_snapshot_v1"
    manifest_path = base / "manifest.json"
    if not manifest_path.is_file():
        return {
            "valid": False,
            "status": "snapshot_absent",
            "document_count": 0,
        }
    try:
        manifest = load(manifest_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return {
            "valid": False,
            "status": "snapshot_manifest_unreadable",
            "document_count": 0,
        }
    records = manifest.get("documents", [])
    observed = []
    files_valid = True
    if not isinstance(records, list):
        records = []
        files_valid = False
    for record in records:
        relative = Path(str(record.get("relative_path", "")))
        safe = bool(
            relative.parts
            and not relative.is_absolute()
            and ".." not in relative.parts
        )
        path = base / "files" / relative
        valid = bool(
            safe
            and path.is_file()
            and path.stat().st_size == int(record.get("size_bytes", -1))
            and file_hash(path) == record.get("sha256")
        )
        files_valid = files_valid and valid
        observed.append(relative.as_posix())
    valid = bool(
        manifest.get("schema_version") == DOCUMENTATION_SNAPSHOT_SCHEMA
        and manifest.get("state") == "complete"
        and manifest.get("manifest_sha256") == canonical_hash(manifest)
        and manifest.get("required_document_count") == len(REQUIRED_DOCUMENTS)
        and tuple(observed) == REQUIRED_DOCUMENTS
        and files_valid
    )
    return {
        "valid": valid,
        "status": "complete" if valid else "snapshot_invalid",
        "document_count": len(records),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "manifest_file_sha256": file_hash(manifest_path),
        "documents": records,
    }


def latest_progress_path(root: Path) -> Path | None:
    directory = (
        root / "results/strict_v4_krc_csr_confirmation_progress_v1"
    )
    candidates = []
    for path in directory.glob("progress_*.json"):
        match = re.fullmatch(r"progress_(\d+)\.json", path.name)
        if match:
            candidates.append((int(match.group(1)), path))
    return max(candidates, default=(0, None))[1]


def complete_pair(root: Path, directory: str) -> dict[str, Any]:
    base = root / "results" / directory
    summary_path = base / "summary.json"
    audit_path = base / "audit.json"
    summary = json_evidence(summary_path, root)
    audit = json_evidence(audit_path, root)
    return {
        "summary": summary,
        "audit": audit,
        "execution_complete": (base / "execution_complete").is_file(),
        "complete": bool(
            summary["exists"]
            and audit["exists"]
            and summary.get("canonical_valid")
            and audit.get("canonical_valid")
        ),
    }


def domain_nearest_ronetc_status(root: Path) -> dict[str, Any]:
    base = root / "results/strict_v4_ronetc_full102_seed7"
    protocol_path = base / "protocol.json"
    protocol_audit_path = base / "protocol_audit.json"
    summary_path = base / "summary.json"
    result_audit_path = base / "audit.json"
    completion_path = base / "execution_complete.json"
    protocol_evidence = json_evidence(protocol_path, root)
    protocol_audit_evidence = {
        "path": protocol_audit_path.relative_to(root).as_posix(),
        "exists": protocol_audit_path.is_file(),
    }
    protocol_audit_valid = False
    if protocol_audit_path.is_file():
        protocol_audit = load(protocol_audit_path)
        claimed = protocol_audit.get("audit_manifest_sha256")
        payload = dict(protocol_audit)
        payload.pop("audit_manifest_sha256", None)
        protocol_audit_valid = bool(
            claimed == canonical_hash(payload)
            and protocol_audit.get("passed") is True
            and all(protocol_audit.get("checks", {}).values())
        )
        protocol_audit_evidence.update(
            {
                "file_sha256": file_hash(protocol_audit_path),
                "schema_version": protocol_audit.get("schema_version"),
                "audit_manifest_sha256": claimed,
                "canonical_valid": protocol_audit_valid,
            }
        )

    protocol = (
        load(protocol_path)
        if protocol_evidence.get("canonical_valid")
        else {}
    )
    protocol_frozen = bool(
        protocol.get("schema_version")
        == "strict_v4_ronetc_full102_protocol_v1"
        and protocol.get("state") == "frozen_zero_result"
        and protocol.get("universe", {}).get("suite_count") == 7
        and protocol.get("universe", {}).get("scenario_count") == 102
        and protocol.get("universe", {}).get("task_count") == 102
        and len(protocol.get("tasks", [])) == 102
        and protocol_audit_valid
    )
    artifact_counts = {
        artifact: sum(
            (
                root
                / "runs/strict_v4_ronetc_full102_seed7"
                / task.get("suite", "")
                / (
                    f"{task.get('scenario', '')}_seed"
                    f"{task.get('seed', '')}_{task.get('model', '')}"
                )
                / artifact
            ).is_file()
            for task in protocol.get("tasks", [])
        )
        for artifact in ("metrics.json", "scores.npz", "provenance.json")
    }
    summary = json_evidence(summary_path, root)
    result_audit = json_evidence(result_audit_path, root)
    completion = json_evidence(completion_path, root)
    summary_value = (
        load(summary_path) if summary.get("canonical_valid") else {}
    )
    result_audit_value = (
        load(result_audit_path)
        if result_audit.get("canonical_valid")
        else {}
    )
    completion_value = (
        load(completion_path)
        if completion.get("canonical_valid")
        else {}
    )
    summary_valid = bool(
        summary_value.get("schema_version")
        == "strict_v4_ronetc_full102_summary_v1"
        and summary_value.get("state")
        == "full102_development_summary_complete"
        and summary_value.get("validation", {}).get("passes") is True
        and summary_value.get("validation", {}).get("scenario_count") == 102
        and summary_value.get("input_evidence", {}).get(
            "protocol_manifest_sha256"
        )
        == protocol.get("manifest_sha256")
        and summary_value.get("input_evidence", {}).get(
            "protocol_file_sha256"
        )
        == (file_hash(protocol_path) if protocol_path.is_file() else None)
        and summary_value.get("claim_boundary", {}).get(
            "authorizes_comprehensive_sota"
        )
        is False
    )
    result_audit_passes = bool(
        result_audit_value.get("schema_version")
        == "strict_v4_ronetc_full102_audit_v1"
        and result_audit_value.get("state")
        == "independent_integrity_audit_complete"
        and result_audit_value.get("passes") is True
        and all(result_audit_value.get("checks", {}).values())
        and result_audit_value.get("input_manifest_sha256", {}).get(
            "protocol"
        )
        == protocol.get("manifest_sha256")
        and result_audit_value.get("input_manifest_sha256", {}).get(
            "summary"
        )
        == summary_value.get("manifest_sha256")
        and result_audit_value.get("claim_boundary", {}).get(
            "authorizes_comprehensive_sota"
        )
        is False
    )
    completion_valid = bool(
        completion_value.get("schema_version")
        == "strict_v4_ronetc_full102_completion_v1"
        and completion_value.get("state") == "complete"
        and completion_value.get("scenario_count") == 102
        and completion_value.get("integrity_passes") is True
        and completion_value.get("protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and completion_value.get("protocol_file_sha256")
        == (file_hash(protocol_path) if protocol_path.is_file() else None)
        and completion_value.get("summary_manifest_sha256")
        == summary_value.get("manifest_sha256")
        and completion_value.get("summary_file_sha256")
        == (file_hash(summary_path) if summary_path.is_file() else None)
        and completion_value.get("audit_manifest_sha256")
        == result_audit_value.get("manifest_sha256")
        and completion_value.get("audit_file_sha256")
        == (
            file_hash(result_audit_path)
            if result_audit_path.is_file()
            else None
        )
        and completion_value.get("authorizes_comprehensive_sota") is False
    )
    if result_audit.get("canonical_valid"):
        result_audit["integrity_passes"] = result_audit_passes
    if summary.get("canonical_valid"):
        summary["contract_valid"] = summary_valid
    if completion.get("canonical_valid"):
        completion["binding_valid"] = completion_valid
    terminal = bool(
        protocol_frozen
        and all(count == 102 for count in artifact_counts.values())
        and summary_valid
        and result_audit_passes
        and completion_valid
    )
    return {
        "protocol_frozen_and_audited": protocol_frozen,
        "execution_terminal": terminal,
        "status": (
            "complete"
            if terminal
            else (
                "frozen_zero_result_not_executed"
                if protocol_frozen
                and all(count == 0 for count in artifact_counts.values())
                else "incomplete_or_inconsistent"
            )
        ),
        "artifact_counts": artifact_counts,
        "protocol": protocol_evidence,
        "protocol_audit": protocol_audit_evidence,
        "summary": summary,
        "result_audit": result_audit,
        "completion": completion,
    }


def canonical_value(
    path: Path, expected_schema: str
) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = load(path)
    if (
        value.get("schema_version") != expected_schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        return None
    return value


def pug_cross_suite_design_status(path: Path, root: Path) -> dict[str, Any]:
    evidence = json_evidence(path, root)
    if not evidence.get("canonical_valid"):
        return {
            "frozen": False,
            "execution_admitted": False,
            "formal_result_count": 0,
            "evidence": evidence,
        }

    value = load(path)
    universe = value.get("confirmation_universe", {})
    formal_counts = value.get("formal_result_counts_at_freeze", {})
    formal_result_count = sum(
        int(count) for count in formal_counts.values()
    )
    frozen = bool(
        value.get("schema_version")
        == "strict_v4_pug_cross_suite_confirmation_design_v1"
        and value.get("state")
        == "conditionally_frozen_before_pilot_completion_and_cross_suite_outputs"
        and value.get("execution_admitted_at_freeze") is False
        and universe.get("suite_count") == 7
        and universe.get("scenario_count") == 102
        and universe.get("paired_task_count") == 306
        and universe.get("expected_pairwise_pug_runs") == 306
        and universe.get("expected_fresh_opendetect_runs") == 306
        and formal_result_count == 0
        and len(value.get("required_future_implementation", [])) == 7
    )
    return {
        "frozen": frozen,
        "execution_admitted": bool(
            value.get("execution_admitted_at_freeze")
        ),
        "formal_result_count": formal_result_count,
        "suite_count": universe.get("suite_count"),
        "scenario_count": universe.get("scenario_count"),
        "candidate_task_count": universe.get(
            "expected_pairwise_pug_runs"
        ),
        "fresh_opendetect_task_count": universe.get(
            "expected_fresh_opendetect_runs"
        ),
        "future_implementation_item_count": len(
            value.get("required_future_implementation", [])
        ),
        "evidence": evidence,
    }


def direct_tournament_design_status(
    path: Path, root: Path
) -> dict[str, Any]:
    evidence = json_evidence(path, root)
    if not evidence.get("canonical_valid"):
        return {"frozen": False, "evidence": evidence}
    value = load(path)
    universe = value.get("confirmation_universe", {})
    output_counts = value.get("formal_output_counts_at_freeze", {})
    frozen = bool(
        value.get("schema_version")
        == "strict_v4_self_algorithm_direct_tournament_design_v1"
        and value.get("state")
        == "conditionally_frozen_before_dual_positive_outcome"
        and value.get("execution_admitted_at_freeze") is False
        and universe.get("suite_count") == 7
        and universe.get("scenario_count") == 102
        and universe.get("seeds") == [809, 811, 821]
        and universe.get("paired_task_count") == 306
        and universe.get("expected_incumbent_runs") == 306
        and universe.get("expected_challenger_runs") == 306
        and universe.get("expected_paired_evaluations") == 918
        and all(int(count) == 0 for count in output_counts.values())
        and len(value.get("required_future_implementation", [])) == 7
        and value.get("activation", {}).get(
            "dual_positive_without_tournament_is_not_final_selection"
        )
        is True
    )
    return {
        "frozen": frozen,
        "execution_admitted": bool(
            value.get("execution_admitted_at_freeze")
        ),
        "formal_result_count": sum(
            int(count) for count in output_counts.values()
        ),
        "suite_count": universe.get("suite_count"),
        "scenario_count": universe.get("scenario_count"),
        "paired_task_count": universe.get("paired_task_count"),
        "paired_evaluation_count": universe.get(
            "expected_paired_evaluations"
        ),
        "future_implementation_item_count": len(
            value.get("required_future_implementation", [])
        ),
        "evidence": evidence,
    }


def direct_tournament_implementation_status(root: Path) -> dict[str, Any]:
    hashes = {
        relative: (
            file_hash(root / relative)
            if (root / relative).is_file()
            else None
        )
        for relative in DIRECT_TOURNAMENT_IMPLEMENTATION_FILES
    }
    return {
        "complete": all(value is not None for value in hashes.values()),
        "implemented_file_count": sum(
            value is not None for value in hashes.values()
        ),
        "required_file_count": len(DIRECT_TOURNAMENT_IMPLEMENTATION_FILES),
        "implementation_sha256": hashes,
    }


def direct_tournament_terminal_status(root: Path) -> dict[str, Any]:
    base = root / "results/strict_v4_self_algorithm_direct_tournament_v1"
    paths = {
        "activation": base / "activation.json",
        "protocol": base / "protocol.json",
        "summary": base / "summary.json",
        "audit": base / "audit.json",
        "completion": base / "execution_complete.json",
    }
    schemas = {
        "activation": (
            "strict_v4_self_algorithm_direct_tournament_activation_v1"
        ),
        "protocol": (
            "strict_v4_self_algorithm_direct_tournament_protocol_v1"
        ),
        "summary": (
            "strict_v4_self_algorithm_direct_tournament_summary_v1"
        ),
        "audit": "strict_v4_self_algorithm_direct_tournament_audit_v1",
        "completion": (
            "strict_v4_self_algorithm_direct_tournament_completion_v1"
        ),
    }
    evidence = {
        name: json_evidence(path, root) for name, path in paths.items()
    }
    values = {
        name: canonical_value(path, schemas[name])
        for name, path in paths.items()
    }
    if not any(path.is_file() for path in paths.values()):
        return {
            "terminal": False,
            "status": "fresh_direct_tournament_not_started",
            "selected_algorithm": None,
            "incumbent_algorithm": None,
            "challenger_algorithm": None,
            "checks": {},
            "evidence": evidence,
        }
    if any(value is None for value in values.values()):
        return {
            "terminal": False,
            "status": "direct_tournament_incomplete_or_noncanonical",
            "selected_algorithm": None,
            "incumbent_algorithm": None,
            "challenger_algorithm": None,
            "checks": {
                f"{name}_canonical": value is not None
                for name, value in values.items()
            },
            "evidence": evidence,
        }
    activation = values["activation"]
    protocol = values["protocol"]
    summary = values["summary"]
    audit = values["audit"]
    completion = values["completion"]
    assert activation is not None
    assert protocol is not None
    assert summary is not None
    assert audit is not None
    assert completion is not None
    incumbent = protocol.get("incumbent_algorithm")
    challenger = protocol.get("challenger_algorithm")
    selected = completion.get("selected_algorithm")
    challenger_passes = completion.get("challenger_gate_passes")
    expected_selected = (
        challenger if challenger_passes is True else incumbent
    )
    counts = summary.get("counts", {})
    checks = {
        "activation_admitted": (
            activation.get("execution_admitted") is True
        ),
        "protocol_activation_binding": (
            protocol.get("input_manifest_sha256", {}).get("activation")
            == activation["manifest_sha256"]
        ),
        "candidate_identity_binding": (
            incumbent
            in ("krc_csr_caeos_v1", "rrc_csr_caeos_v1")
            and challenger == "caeos_pug"
            and activation.get("incumbent_algorithm") == incumbent
            and activation.get("challenger_algorithm") == challenger
        ),
        "exact_universe": (
            protocol.get("confirmation_universe", {}).get(
                "paired_task_count"
            )
            == 306
            and protocol.get("confirmation_universe", {}).get(
                "paired_evaluation_count"
            )
            == 918
            and counts.get("task_records") == 306
            and counts.get("paired_condition_evaluations") == 918
            and counts.get("scenarios") == 102
            and counts.get("suites") == 7
        ),
        "implementation_hash_closure_present": all(
            isinstance(
                protocol.get("implementation_sha256", {}).get(relative),
                str,
            )
            and len(
                protocol.get("implementation_sha256", {}).get(relative)
            )
            == 64
            for relative in DIRECT_TOURNAMENT_IMPLEMENTATION_FILES
        ),
        "summary_protocol_binding": (
            summary.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
        ),
        "audit_integrity": (
            audit.get("integrity", {}).get("passes") is True
        ),
        "audit_protocol_summary_binding": (
            audit.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
            and audit.get("summary_manifest_sha256")
            == summary["manifest_sha256"]
        ),
        "summary_audit_decision_equal": (
            summary.get("decision") == audit.get("independent_recomputation", {})
            .get("decision")
        ),
        "completion_integrity": (
            completion.get("state") == "complete"
            and completion.get("integrity_passes") is True
        ),
        "completion_protocol_binding": (
            completion.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
            and completion.get("protocol_file_sha256")
            == file_hash(paths["protocol"])
        ),
        "completion_summary_binding": (
            completion.get("summary_manifest_sha256")
            == summary["manifest_sha256"]
            and completion.get("summary_file_sha256")
            == file_hash(paths["summary"])
        ),
        "completion_audit_binding": (
            completion.get("audit_manifest_sha256")
            == audit["manifest_sha256"]
            and completion.get("audit_file_sha256")
            == file_hash(paths["audit"])
        ),
        "terminal_selection_binding": (
            isinstance(challenger_passes, bool)
            and selected == expected_selected
            and audit.get("decision", {}).get("selected_algorithm")
            == selected
            and audit.get("decision", {}).get("challenger_gate_passes")
            is challenger_passes
        ),
    }
    terminal = all(checks.values())
    return {
        "terminal": terminal,
        "status": (
            "direct_tournament_terminal_selection_complete"
            if terminal
            else "direct_tournament_inconsistent"
        ),
        "selected_algorithm": selected if terminal else None,
        "incumbent_algorithm": incumbent,
        "challenger_algorithm": challenger,
        "challenger_gate_passes": (
            challenger_passes if terminal else None
        ),
        "checks": checks,
        "evidence": evidence,
    }


def selected_system_adapter_design_status(
    path: Path, root: Path
) -> dict[str, Any]:
    evidence = json_evidence(path, root)
    if not evidence.get("canonical_valid"):
        return {
            "frozen": False,
            "common_runtime_adapter_complete": False,
            "execution_admitted": False,
            "formal_result_count": 0,
            "evidence": evidence,
        }

    value = load(path)
    activation = value.get("activation", {})
    runtime = value.get("runtime_contract", {})
    implementation = value.get("implementation_status_at_freeze", {})
    runtime_hashes = implementation.get(
        "runtime_implementation_sha256", {}
    )
    formal_counts = value.get("formal_output_counts_at_freeze", {})
    formal_result_count = sum(
        int(count) for count in formal_counts.values()
    )
    runtime_hashes_valid = bool(
        set(runtime_hashes) == set(SELECTED_SYSTEM_RUNTIME_FILES)
        and all(
            isinstance(value, str)
            and re.fullmatch(r"[0-9a-f]{64}", value) is not None
            for value in runtime_hashes.values()
        )
    )
    common_runtime_adapter_complete = bool(
        implementation.get("common_runtime_adapter_complete") is True
        and runtime.get("schema_version")
        == "strict_v4_selected_system_runtime_v1"
        and runtime.get("required_output")
        == ["prediction", "probability", "risk"]
        and set(runtime.get("supported_source_runtime", {}))
        == set(SELECTED_SYSTEM_ALGORITHMS)
        and runtime_hashes_valid
    )
    frozen = bool(
        value.get("schema_version")
        == "strict_v4_selected_system_downstream_adapter_design_v1"
        and value.get("state")
        == "frozen_before_final_self_algorithm_selection"
        and value.get("execution_admitted_at_freeze") is False
        and activation.get("allowed_selected_algorithms")
        == list(SELECTED_SYSTEM_ALGORITHMS)
        and formal_result_count == 0
        and common_runtime_adapter_complete
        and implementation.get("remaining_components")
        == list(SELECTED_SYSTEM_REMAINING_COMPONENTS)
        and value.get("claim_boundary", {}).get(
            "common_runtime_support_is_not_downstream_execution"
        )
        is True
    )
    return {
        "frozen": frozen,
        "common_runtime_adapter_complete": (
            common_runtime_adapter_complete
        ),
        "execution_admitted": bool(
            value.get("execution_admitted_at_freeze")
        ),
        "formal_result_count": formal_result_count,
        "allowed_selected_algorithms": activation.get(
            "allowed_selected_algorithms"
        ),
        "remaining_component_count": len(
            implementation.get("remaining_components", [])
        ),
        "runtime_implementation_sha256": runtime_hashes,
        "evidence": evidence,
    }


def selected_system_adapter_implementation_status(
    root: Path,
) -> dict[str, Any]:
    files = {}
    for component, relative in (
        SELECTED_SYSTEM_ADAPTER_IMPLEMENTATION_FILES.items()
    ):
        path = root / relative
        files[component] = {
            "path": relative,
            "exists": path.is_file(),
            "file_sha256": file_hash(path) if path.is_file() else None,
        }
    ready_count = sum(item["exists"] for item in files.values())
    return {
        "required_count": len(files),
        "ready_count": ready_count,
        "complete": ready_count == len(files),
        "files": files,
    }


def selected_system_preconfirmation_status(root: Path) -> dict[str, Any]:
    design_root = (
        root / "results/strict_v4_selected_system_preconfirmation_design_v1"
    )
    result_root = (
        root / "results/strict_v4_selected_system_preconfirmation_v1"
    )
    design_path = design_root / "design.json"
    design_audit_path = design_root / "audit.json"
    completion_path = result_root / "execution_complete.json"
    design = load(design_path) if design_path.is_file() else {}
    design_audit = (
        load(design_audit_path) if design_audit_path.is_file() else {}
    )
    completion = load(completion_path) if completion_path.is_file() else {}
    design_frozen = bool(
        design.get("schema_version")
        == "strict_v4_selected_system_preconfirmation_design_v1"
        and design.get("manifest_sha256") == canonical_hash(design)
        and design.get("universe", {}).get("source_task_count") == 306
        and design.get("universe", {}).get(
            "paired_corruption_record_count"
        )
        == 1530
        and all(
            int(value) == 0
            for value in design.get(
                "formal_output_counts_at_freeze", {}
            ).values()
        )
    )
    design_audited = bool(
        design_frozen
        and design_audit.get("schema_version")
        == "strict_v4_selected_system_preconfirmation_design_audit_v1"
        and design_audit.get("manifest_sha256")
        == canonical_hash(design_audit)
        and design_audit.get("passed") is True
        and design_audit.get("design_manifest_sha256")
        == design.get("manifest_sha256")
        and design_audit.get("design_file_sha256") == file_hash(design_path)
    )
    required = tuple(design.get("required_future_implementation", []))
    implementation = {
        name: {
            "exists": (root / name).is_file(),
            "file_sha256": (
                file_hash(root / name) if (root / name).is_file() else None
            ),
        }
        for name in required
    }
    ready_count = sum(item["exists"] for item in implementation.values())
    completion_integrity = bool(
        completion.get("schema_version")
        == "strict_v4_selected_system_preconfirmation_completion_v1"
        and completion.get("manifest_sha256") == canonical_hash(completion)
        and completion.get("state") == "complete"
        and completion.get("integrity_passes") is True
    )
    selective_sota = bool(
        completion_integrity
        and completion.get("any_selective_sota_authorized") is True
    )
    terminal = bool(
        completion_integrity
        and completion.get("classic_main_gate_passes") is True
        and completion.get("absolute_corruption_gate_passes") is True
        and completion.get("comparative_corruption_gate_passes") is True
    )
    return {
        "design_frozen_and_audited": design_audited,
        "design_manifest_sha256": design.get("manifest_sha256"),
        "required_implementation_count": len(required),
        "ready_implementation_count": ready_count,
        "implementation_complete": bool(required)
        and ready_count == len(required),
        "implementation": implementation,
        "activation_present": (result_root / "activation.json").is_file(),
        "completion_present": completion_path.is_file(),
        "completion_integrity_passes": completion_integrity,
        "classic_main_gate_passes": (
            completion.get("classic_main_gate_passes") is True
        ),
        "absolute_corruption_gate_passes": (
            completion.get("absolute_corruption_gate_passes") is True
        ),
        "comparative_corruption_gate_passes": (
            completion.get("comparative_corruption_gate_passes") is True
        ),
        "selective_unknown_detection_sota_authorized": (
            completion_integrity
            and completion.get(
                "selective_unknown_detection_sota_authorized"
            )
            is True
        ),
        "selective_corruption_robustness_sota_authorized": (
            completion_integrity
            and completion.get(
                "selective_corruption_robustness_sota_authorized"
            )
            is True
        ),
        "any_selective_sota_authorized": selective_sota,
        "evidence_terminal": completion_integrity,
        "terminal": terminal,
        "status": (
            "complete"
            if terminal
            else (
                "complete_selective_sota_only"
                if selective_sota
                else (
                    "design_frozen_implementation_incomplete"
                    if design_audited and ready_count < len(required)
                    else (
                        "implementation_ready_waiting_for_final_selection"
                        if design_audited and ready_count == len(required)
                        else "design_invalid_or_absent"
                    )
                )
            )
        ),
    }


def rrc_realtime_progress_status(root: Path) -> dict[str, Any]:
    base = root / "results/strict_v4_rrc_csr_confirmation_v1"
    snapshot_path = base / "realtime_progress.json"
    state_path = base / "realtime_watcher_state.json"
    if not snapshot_path.is_file() or not state_path.is_file():
        return {
            "valid": False,
            "status": "realtime_evidence_absent",
            "snapshot_present": snapshot_path.is_file(),
            "watcher_state_present": state_path.is_file(),
        }
    try:
        snapshot = load(snapshot_path)
        state = load(state_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return {
            "valid": False,
            "status": "realtime_evidence_unreadable",
        }
    snapshot_valid = bool(
        snapshot.get("schema_version")
        == "strict_v4_rrc_csr_realtime_progress_snapshot_v1"
        and snapshot.get("manifest_sha256") == canonical_hash(snapshot)
        and snapshot.get("effect_aggregation_performed") is False
        and snapshot.get("effect_conclusion_available_from_this_snapshot")
        is False
    )
    state_valid = bool(
        state.get("schema_version")
        == "strict_v4_rrc_csr_realtime_progress_watcher_state_v1"
        and state.get("manifest_sha256") == canonical_hash(state)
        and state.get("snapshot_manifest_sha256")
        == snapshot.get("manifest_sha256")
        and state.get("snapshot_file_sha256") == file_hash(snapshot_path)
        and state.get("partial_effect_aggregation_performed") is False
        and state.get("partial_effect_claim_authorized") is False
    )
    counts_match = bool(
        all(
            state.get("counts", {}).get(name, {}).get("present")
            == item.get("present_count")
            and state.get("counts", {}).get(name, {}).get("expected")
            == item.get("expected_count")
            and state.get("counts", {}).get(name, {}).get("invalid")
            == item.get("invalid_count")
            and state.get("counts", {}).get(name, {}).get("pending")
            == item.get("pending_count")
            for name, item in snapshot.get("inventory", {}).items()
        )
        and len(snapshot.get("inventory", {})) == 4
    )
    valid = snapshot_valid and state_valid and counts_match
    return {
        "valid": valid,
        "status": state.get("state") if valid else "realtime_evidence_invalid",
        "snapshot_manifest_sha256": snapshot.get("manifest_sha256"),
        "snapshot_file_sha256": file_hash(snapshot_path),
        "watcher_state_manifest_sha256": state.get("manifest_sha256"),
        "watcher_state_file_sha256": file_hash(state_path),
        "observed_at_utc": snapshot.get("observed_at_utc"),
        "counts": state.get("counts", {}),
        "runner_pids": state.get("runner_pids", []),
        "terminal_evidence": state.get("terminal_evidence", {}),
        "partial_effect_claim_authorized": False,
    }


def krc_terminal_clarification_status(root: Path) -> dict[str, Any]:
    path = (
        root
        / "results/strict_v4_krc_csr_confirmation_v1/"
        "terminal_decision_clarification.json"
    )
    evidence = json_evidence(path, root)
    if not evidence.get("canonical_valid"):
        return {
            **evidence,
            "valid": False,
            "status": "absent_or_invalid",
        }
    value = load(path)
    valid = bool(
        value.get("schema_version")
        == "strict_v4_krc_terminal_decision_clarification_v1"
        and value.get("state") == "complete"
        and value.get("all_structural_checks_pass") is True
        and value.get("valid_negative_terminal") is True
        and value.get("no_summary_audit_selection_inconsistency") is True
        and value.get("reported_selection") == "caeos_pairwise"
        and value.get("effect_gate_failures")
        == ["enabled_primary_suite_count_minimum"]
        and value.get("claim_boundary", {}).get(
            "rrc_fallback_remains_required"
        )
        is True
    )
    return {
        **evidence,
        "valid": valid,
        "status": "valid_negative_terminal_clarified"
        if valid
        else "clarification_contract_invalid",
        "effect_gate_failures": value.get("effect_gate_failures", []),
        "reported_selection": value.get("reported_selection"),
        "legacy_field_is_not_a_summary_audit_equality_check": value.get(
            "legacy_field_is_not_a_summary_audit_equality_check"
        )
        is True,
    }


def pug_cross_suite_implementation_status(root: Path) -> dict[str, Any]:
    files = {}
    for relative in PUG_CROSS_SUITE_IMPLEMENTATION_FILES:
        path = root / relative
        files[relative] = {
            "exists": path.is_file(),
            "file_sha256": file_hash(path) if path.is_file() else None,
        }
    ready_count = sum(
        evidence["exists"] for evidence in files.values()
    )
    return {
        "required_count": len(PUG_CROSS_SUITE_IMPLEMENTATION_FILES),
        "ready_count": ready_count,
        "complete": ready_count == len(PUG_CROSS_SUITE_IMPLEMENTATION_FILES),
        "files": files,
    }


def pug_cross_suite_terminal_status(root: Path) -> dict[str, Any]:
    base = root / "results/strict_v4_pug_cross_suite_confirmation_v1"
    paths = {
        "protocol": base / "protocol.json",
        "summary": base / "summary.json",
        "audit": base / "audit.json",
        "completion": base / "execution_complete.json",
    }
    evidence = {
        name: json_evidence(path, root) for name, path in paths.items()
    }
    protocol = canonical_value(
        paths["protocol"],
        "strict_v4_pug_cross_suite_execution_protocol_v1",
    )
    summary = canonical_value(
        paths["summary"],
        "strict_v4_pug_cross_suite_confirmation_summary_v1",
    )
    audit = canonical_value(
        paths["audit"],
        "strict_v4_pug_cross_suite_confirmation_audit_v1",
    )
    completion = canonical_value(
        paths["completion"],
        "strict_v4_pug_cross_suite_confirmation_completion_v1",
    )
    if any(
        value is None for value in (protocol, summary, audit, completion)
    ):
        return {
            "terminal": False,
            "status": "cross_suite_confirmation_incomplete",
            "selected_algorithm": None,
            "evidence": evidence,
        }

    effect = audit.get("effect", {}).get("passes")
    selected = audit.get("selection", {}).get("selected_algorithm")
    expected_selected = "caeos_pug" if effect is True else "upstream_incumbent"
    relative_base = base.relative_to(root).as_posix()
    expected_input_files = {
        f"{relative_base}/protocol.json": file_hash(paths["protocol"]),
        f"{relative_base}/summary.json": file_hash(paths["summary"]),
    }
    checks = {
        "protocol_state": (
            protocol.get("state")
            == "frozen_after_positive_pilot_before_cross_suite_execution"
        ),
        "summary_state": (
            summary.get("state")
            == "cross_suite_confirmation_summary_complete"
        ),
        "summary_validation": (
            summary.get("validation", {}).get("passes") is True
            and summary.get("validation", {}).get("task_record_count") == 306
            and summary.get("validation", {}).get("scenario_count") == 102
            and summary.get("validation", {}).get("suite_count") == 7
        ),
        "audit_state": (
            audit.get("state")
            == "cross_suite_confirmation_independent_audit_complete"
        ),
        "audit_integrity": (
            audit.get("integrity", {}).get("passes") is True
        ),
        "effect_is_boolean": isinstance(effect, bool),
        "summary_effect_binding": (
            summary.get("decision", {}).get("passes") is effect
        ),
        "selection_binding": (
            selected == expected_selected
            and audit.get("selection", {}).get("candidate_selected")
            is (effect is True)
        ),
        "summary_protocol_binding": (
            summary.get("input_evidence", {}).get(
                "protocol_manifest_sha256"
            )
            == protocol["manifest_sha256"]
            and summary.get("input_evidence", {}).get(
                "protocol_file_sha256"
            )
            == file_hash(paths["protocol"])
        ),
        "audit_manifest_binding": (
            audit.get("input_manifest_sha256", {}).get("protocol")
            == protocol["manifest_sha256"]
            and audit.get("input_manifest_sha256", {}).get("summary")
            == summary["manifest_sha256"]
        ),
        "audit_file_binding": (
            audit.get("input_file_sha256") == expected_input_files
        ),
        "completion_state": completion.get("state") == "complete",
        "completion_manifest_binding": (
            completion.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
            and completion.get("summary_manifest_sha256")
            == summary["manifest_sha256"]
            and completion.get("audit_manifest_sha256")
            == audit["manifest_sha256"]
        ),
        "completion_file_binding": (
            completion.get("summary_file_sha256")
            == file_hash(paths["summary"])
            and completion.get("audit_file_sha256")
            == file_hash(paths["audit"])
        ),
        "completion_effect_binding": (
            completion.get("effect_passes") is effect
            and completion.get("candidate_selected_by_this_stage")
            is (effect is True)
        ),
    }
    if not all(checks.values()):
        return {
            "terminal": False,
            "status": "cross_suite_confirmation_inconsistent",
            "selected_algorithm": None,
            "checks": checks,
            "evidence": evidence,
        }
    return {
        "terminal": True,
        "status": (
            "cross_suite_positive_pug_provisional_incumbent"
            if effect
            else "cross_suite_negative_retain_upstream_incumbent"
        ),
        "selected_algorithm": (
            "caeos_pug" if effect else "upstream_incumbent"
        ),
        "effect_passes": effect,
        "checks": checks,
        "evidence": evidence,
    }


def derive_self_algorithm_status(
    root: Path,
    *,
    krc_terminal_complete: bool,
    pug_confirmation_path: Path,
) -> dict[str, Any]:
    selected = "caeos_pairwise"
    blockers: list[str] = []
    krc_rrc_terminal = False
    krc_rrc_status = "waiting_for_krc_terminal"
    rrc_evidence: dict[str, Any] = {
        "not_required": json_evidence(
            root
            / "results/strict_v4_rrc_csr_confirmation_v1/not_required.json",
            root,
        ),
        "confirmation": complete_pair(
            root, "strict_v4_rrc_csr_confirmation_v1"
        ),
    }
    if not krc_terminal_complete:
        blockers.append("KRC confirmation is incomplete")
    else:
        decision_path = (
            root
            / "results/strict_v4_krc_integrated_comprehensive_sota_v2/"
            "downstream_decision.json"
        )
        decision = canonical_value(
            decision_path, "strict_v4_krc_downstream_decision_v1"
        )
        if decision is None or decision.get("state") != "complete":
            krc_rrc_status = "krc_terminal_decision_incomplete_or_invalid"
            blockers.append("KRC terminal decision is incomplete or invalid")
        elif decision.get("krc_effect_gate_passes") is True:
            selected = "krc_csr_caeos_v1"
            not_required = canonical_value(
                root
                / "results/strict_v4_rrc_csr_confirmation_v1/"
                "not_required.json",
                "strict_v4_rrc_csr_not_required_v1",
            )
            valid = bool(
                decision.get("selected_algorithm") == selected
                and decision.get("rrc_fallback_execution_permitted") is False
                and not_required is not None
                and not_required.get("state")
                == "terminal_not_required_krc_selected"
                and not_required.get("selected_algorithm") == selected
                and not_required.get("rrc_execution_started") is False
                and not_required.get(
                    "krc_downstream_decision_manifest_sha256"
                )
                == decision["manifest_sha256"]
            )
            krc_rrc_terminal = valid
            krc_rrc_status = (
                "krc_selected_rrc_not_required_terminal"
                if valid
                else "rrc_not_required_marker_incomplete_or_invalid"
            )
            if not valid:
                blockers.append(
                    "RRC terminal not-required marker is incomplete or invalid"
                )
        elif decision.get("krc_effect_gate_passes") is False:
            pair = rrc_evidence["confirmation"]
            if pair["complete"]:
                summary = load(
                    root
                    / "results/strict_v4_rrc_csr_confirmation_v1/"
                    "summary.json"
                )
                audit = load(
                    root
                    / "results/strict_v4_rrc_csr_confirmation_v1/audit.json"
                )
                summary_selection = summary.get("selection")
                audit_selection = audit.get("selection")
                valid = bool(
                    decision.get("selected_algorithm") == "caeos_pairwise"
                    and decision.get("rrc_fallback_execution_permitted") is True
                    and summary.get("schema_version")
                    == "strict_v4_rrc_csr_confirmation_summary_v1"
                    and audit.get("schema_version")
                    == "strict_v4_rrc_csr_confirmation_audit_v1"
                    and audit.get("integrity_passes") is True
                    and summary.get("passes")
                    is audit.get("effect_gate_passes")
                    and summary_selection == audit_selection
                    and summary_selection
                    in ("rrc_csr_caeos_v1", "caeos_pairwise")
                )
                if valid:
                    selected = str(summary_selection)
                    krc_rrc_terminal = True
                    krc_rrc_status = "rrc_confirmation_terminal"
                else:
                    krc_rrc_status = "rrc_confirmation_inconsistent"
                    blockers.append("RRC confirmation is inconsistent")
            else:
                krc_rrc_status = "rrc_confirmation_incomplete"
                blockers.append("RRC fallback confirmation is incomplete")
        else:
            krc_rrc_status = "krc_terminal_decision_inconsistent"
            blockers.append("KRC terminal decision is inconsistent")

    pug = canonical_value(
        pug_confirmation_path, "strict_v4_pug_confirmation_v1"
    )
    upstream_selected = selected
    cross_suite = pug_cross_suite_terminal_status(root)
    pug_terminal = False
    pug_status = "fresh_18_task_confirmation_incomplete"
    tournament_required = False
    if pug is None:
        blockers.append("PUG fresh 18-task confirmation is incomplete")
    else:
        decision = pug.get("decision", {})
        if (
            decision.get("passes") is False
            and decision.get("selected_method") == "caeos_pairwise"
            and decision.get("cross_suite_execution_admitted") is False
        ):
            pug_terminal = True
            pug_status = "pilot_negative_retain_upstream_selection"
        elif (
            decision.get("passes") is True
            and decision.get("selected_method") == "caeos_pug"
            and decision.get("cross_suite_execution_admitted") is False
        ):
            if cross_suite["terminal"]:
                pug_terminal = True
                pug_status = str(cross_suite["status"])
                if cross_suite["selected_algorithm"] == "caeos_pug":
                    if upstream_selected == "caeos_pairwise":
                        selected = "caeos_pug"
                    else:
                        tournament_required = True
                        pug_status = (
                            "cross_suite_positive_direct_tournament_required"
                        )
            elif (
                cross_suite["status"]
                == "cross_suite_confirmation_inconsistent"
            ):
                pug_status = str(cross_suite["status"])
                blockers.append("PUG cross-suite confirmation is inconsistent")
            else:
                pug_status = (
                    "pilot_positive_cross_suite_confirmation_required"
                )
                blockers.append(
                    "PUG pilot passed but fresh cross-suite confirmation is "
                    "incomplete"
                )
        else:
            pug_status = "confirmation_inconsistent"
            blockers.append("PUG confirmation is inconsistent")

    tournament = direct_tournament_terminal_status(root)
    if tournament_required:
        if (
            tournament["terminal"]
            and tournament["incumbent_algorithm"] == upstream_selected
            and tournament["challenger_algorithm"] == "caeos_pug"
        ):
            selected = str(tournament["selected_algorithm"])
        else:
            blockers.append(
                "PUG and the upstream self-algorithm both passed but lack "
                "a valid fresh direct tournament terminal result"
            )
    tournament_terminal = bool(
        not tournament_required or tournament["terminal"]
    )
    final = bool(
        krc_rrc_terminal and pug_terminal and tournament_terminal
    )
    return {
        "final": final,
        "selected_algorithm": selected,
        "provisional_challenger": (
            "caeos_pug"
            if tournament_required and not tournament["terminal"]
            else None
        ),
        "krc_rrc_branch": {
            "terminal": krc_rrc_terminal,
            "status": krc_rrc_status,
        },
        "pug_branch": {
            "terminal": pug_terminal,
            "status": pug_status,
            "cross_suite": cross_suite,
        },
        "direct_tournament": {
            "required": tournament_required,
            "terminal": tournament_terminal,
            "incumbent": upstream_selected,
            "challenger": "caeos_pug" if tournament_required else None,
            "status": (
                tournament["status"]
                if tournament_required and tournament["terminal"]
                else (
                    "fresh_direct_tournament_required"
                    if tournament_required
                    else "not_required"
                )
            ),
            "terminal_evidence": tournament,
        },
        "rrc_evidence": rrc_evidence,
        "blockers": blockers,
    }


def build_audit(root: Path) -> dict[str, Any]:
    classic_path = (
        root
        / "results/strict_v4_incumbent_vs_classical_main_baselines_v1/audit.json"
    )
    classic = load(classic_path)
    classic_names = tuple(
        row.get("display_name")
        for row in classic.get("main_baseline_comparisons", [])
    )
    classic_integrity = bool(
        classic.get("schema_version")
        == "strict_v4_incumbent_vs_classical_main_baselines_audit_v1"
        and classic.get("manifest_sha256") == canonical_hash(classic)
        and classic.get("passes") is True
        and classic_names == MAIN_BASELINES
        and classic.get("summary", {}).get("baseline_count") == 7
    )
    strict_five_count = int(
        classic.get("summary", {}).get(
            "strict_five_metric_dominance_count", 0
        )
    )
    domain_nearest_ronetc = domain_nearest_ronetc_status(root)

    absolute_corruption_path = (
        root
        / "results/strict_v4_postselection_corruption_suite_gate_seed7/audit.json"
    )
    absolute_corruption = load(absolute_corruption_path)
    comparative_path = (
        root / "results/strict_v4_comparative_corruption/independent_audit.json"
    )
    comparative = load(comparative_path)

    progress_path = latest_progress_path(root)
    if progress_path is None:
        raise ValueError("KRC progress evidence is absent")
    progress = load(progress_path)
    observed = progress.get("observed_totals", {})
    capture_count = int(observed.get("captures", 0))
    krc_bottleneck_path = (
        root
        / "results/strict_v4_krc_certificate_bottleneck_v1"
        / f"audit_{capture_count:03d}.json"
    )
    krc_terminal = complete_pair(root, "strict_v4_krc_csr_confirmation_v1")
    krc_terminal_clarification = krc_terminal_clarification_status(root)

    pug_protocol_path = (
        root / "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
    )
    pug_staging_path = (
        root / "results/strict_v4_pug_confirmation_v1/staging_manifest.json"
    )
    pug_confirmation_path = (
        root / "results/strict_v4_pug_confirmation_v1/confirmation.json"
    )
    pug_cross_suite_design_path = (
        root / "results/strict_v4_pug_cross_suite_design_v1/design.json"
    )
    pug_cross_suite_design = pug_cross_suite_design_status(
        pug_cross_suite_design_path, root
    )
    direct_tournament_design_path = (
        root
        / "results/strict_v4_self_algorithm_direct_tournament_design_v1/"
        "design.json"
    )
    direct_tournament_design = direct_tournament_design_status(
        direct_tournament_design_path, root
    )
    direct_tournament_implementation = (
        direct_tournament_implementation_status(root)
    )
    selected_system_adapter_design_path = (
        root
        / "results/strict_v4_selected_system_downstream_adapter_design_v1/"
        "design.json"
    )
    selected_system_adapter_design = (
        selected_system_adapter_design_status(
            selected_system_adapter_design_path, root
        )
    )
    selected_system_adapter_implementation = (
        selected_system_adapter_implementation_status(root)
    )
    selected_system_preconfirmation = (
        selected_system_preconfirmation_status(root)
    )
    rrc_realtime_progress = rrc_realtime_progress_status(root)
    pug_cross_suite_implementation = (
        pug_cross_suite_implementation_status(root)
    )
    remote_deployment_state_path = (
        root
        / "results/strict_v4_pug_confirmation_v1/"
        "deployment_state_remote.json"
    )
    staging_deployment_state_path = (
        root
        / "staging/strict_v4_pug_confirmation_v1/deployment_state.json"
    )
    deployment_state_path = (
        remote_deployment_state_path
        if remote_deployment_state_path.is_file()
        else staging_deployment_state_path
    )
    deployment_state = (
        load(deployment_state_path)
        if deployment_state_path.is_file()
        else {"state": "absent"}
    )

    data_readiness_path = (
        root
        / "results/strict_v4_krc_downstream_sota_design_v1/"
        "data_readiness_v2_complete.json"
    )
    data_readiness = load(data_readiness_path)
    data_ready = bool(
        data_readiness.get("manifest_sha256")
        == canonical_hash(data_readiness)
        and data_readiness.get("ready_for_downstream_execution") is True
        and all(data_readiness.get("checks", {}).values())
    )

    downstream = {
        "external_malicious": complete_pair(
            root, "strict_v4_krc_external_malicious_v1"
        ),
        "selected_system": complete_pair(
            root, "strict_v4_krc_selected_system_v1"
        ),
        "opendetect_efficiency": complete_pair(
            root, "strict_v4_krc_opendetect_efficiency_v1"
        ),
        "parrot_benign_safety": complete_pair(
            root, "strict_v4_krc_parrot_safety_v1"
        ),
    }
    parrot_feature_root = (
        root / "results/parrot2025_full_no_decryption_features_v1"
    )
    parrot_features_complete = bool(
        (parrot_feature_root / "full_feature_extraction_complete").is_file()
        and (parrot_feature_root / "feature_shard_manifest.json").is_file()
    )

    krc_summary = (
        load(
            root
            / "results/strict_v4_krc_csr_confirmation_v1/summary.json"
        )
        if krc_terminal["complete"]
        else None
    )
    krc_effect_terminal = krc_summary is not None
    self_algorithm = derive_self_algorithm_status(
        root,
        krc_terminal_complete=krc_effect_terminal,
        pug_confirmation_path=pug_confirmation_path,
    )
    pug_effect_terminal = self_algorithm["pug_branch"]["terminal"]
    self_algorithm_selection_final = self_algorithm["final"]

    integrated_path = (
        root
        / "results/strict_v4_krc_integrated_comprehensive_sota_v2/audit.json"
    )
    integrated = (
        load(integrated_path) if integrated_path.is_file() else None
    )
    comprehensive_effect_pass = bool(
        integrated is not None
        and integrated.get("manifest_sha256") == canonical_hash(integrated)
        and integrated.get("effect_passes") is True
    )

    documentation = documentation_snapshot_status(root)
    documentation_current = documentation["valid"]

    requirements = {
        "classic_baselines_few_and_persuasive": {
            "satisfied": classic_integrity,
            "status": "complete" if classic_integrity else "invalid",
            "baseline_count": len(classic_names),
            "baselines": list(classic_names),
        },
        "domain_nearest_baseline_confirmed": {
            "satisfied": domain_nearest_ronetc["execution_terminal"],
            "status": domain_nearest_ronetc["status"],
            "primary_domain_nearest": ["OpenDetect", "RoNeTC"],
            "strict_v4_scenario_count": 102,
        },
        "best_self_algorithm_finally_selected": {
            "satisfied": self_algorithm_selection_final,
            "status": (
                "complete"
                if self_algorithm_selection_final
                else (
                    "self_algorithm_direct_tournament_incomplete"
                    if self_algorithm["direct_tournament"]["required"]
                    else "krc_rrc_and_pug_selection_chain_incomplete"
                )
            ),
            "current_incumbent": self_algorithm["selected_algorithm"],
        },
        "comprehensive_sota_verified": {
            "satisfied": comprehensive_effect_pass,
            "status": (
                "complete_pass"
                if comprehensive_effect_pass
                else "not_established"
            ),
        },
        "documentation_updated": {
            "satisfied": documentation_current,
            "status": "complete" if documentation_current else "missing",
        },
    }
    goal_achieved = all(
        row["satisfied"] for row in requirements.values()
    )
    blockers = []
    for blocker in self_algorithm["blockers"]:
        if blocker == "KRC confirmation is incomplete":
            blockers.append(
                f"KRC confirmation is partial at {capture_count}/306 captures"
            )
        else:
            blockers.append(blocker)
    if (
        strict_five_count < 7
        and not selected_system_preconfirmation["terminal"]
    ):
        blockers.append(
            "Pairwise does not strictly dominate all seven main baselines "
            f"on all five metrics ({strict_five_count}/7)"
        )
    if not domain_nearest_ronetc["execution_terminal"]:
        blockers.append(
            "RoNeTC domain-nearest strict-v4 full102 confirmation is incomplete"
        )
    if (
        self_algorithm_selection_final
        and not selected_system_preconfirmation["terminal"]
    ):
        blockers.append(
            "finally selected algorithm pre-downstream classic and corruption "
            "confirmation is incomplete"
        )
    if (
        absolute_corruption.get("passes") is not True
        and not selected_system_preconfirmation["terminal"]
    ):
        blockers.append("absolute five-family corruption gate failed")
    if (
        comparative.get("comparative_robustness_gate_passes") is not True
        and not selected_system_preconfirmation["terminal"]
    ):
        blockers.append(
            "Pairwise-vs-OpenDetect comparative corruption gate failed"
        )
    if not downstream["external_malicious"]["complete"]:
        blockers.append("external malicious confirmation is incomplete")
    if not downstream["parrot_benign_safety"]["complete"]:
        blockers.append("PARROT benign safety confirmation is incomplete")
    if not downstream["opendetect_efficiency"]["complete"]:
        blockers.append("selected-system efficiency comparison is incomplete")
    if (
        self_algorithm["pug_branch"]["status"]
        == "pilot_positive_cross_suite_confirmation_required"
        and not pug_cross_suite_design["frozen"]
    ):
        blockers.append("PUG cross-suite confirmation design is invalid")
    if (
        self_algorithm["direct_tournament"]["required"]
        and not direct_tournament_design["frozen"]
    ):
        blockers.append("self-algorithm direct tournament design is invalid")
    if (
        self_algorithm["direct_tournament"]["required"]
        and not direct_tournament_implementation["complete"]
    ):
        blockers.append(
            "self-algorithm direct tournament implementation is incomplete"
        )
    if (
        self_algorithm_selection_final
        and not selected_system_adapter_design["frozen"]
    ):
        blockers.append("selected-system downstream adapter design is invalid")

    audit: dict[str, Any] = {
        "schema_version": "strict_v4_current_goal_status_audit_v1",
        "state": "current_goal_incomplete" if not goal_achieved else "complete",
        "goal_achieved": goal_achieved,
        "selected_algorithm": self_algorithm["selected_algorithm"],
        "requirements": requirements,
        "evidence": {
            "classic_baselines": json_evidence(classic_path, root),
            "domain_nearest_ronetc": domain_nearest_ronetc,
            "documentation_snapshot": documentation,
            "absolute_corruption": json_evidence(
                absolute_corruption_path, root
            ),
            "comparative_corruption": json_evidence(comparative_path, root),
            "krc_progress": json_evidence(progress_path, root),
            "krc_bottleneck": json_evidence(krc_bottleneck_path, root),
            "krc_terminal": krc_terminal,
            "krc_terminal_decision_clarification": (
                krc_terminal_clarification
            ),
            "pug_execution_protocol": json_evidence(
                pug_protocol_path, root
            ),
            "pug_staging_manifest": json_evidence(pug_staging_path, root),
            "pug_confirmation": json_evidence(
                pug_confirmation_path, root
            ),
            "pug_cross_suite_design": pug_cross_suite_design,
            "self_algorithm_direct_tournament_design": (
                direct_tournament_design
            ),
            "self_algorithm_direct_tournament_implementation": (
                direct_tournament_implementation
            ),
            "selected_system_downstream_adapter_design": (
                selected_system_adapter_design
            ),
            "selected_system_downstream_adapter_implementation": (
                selected_system_adapter_implementation
            ),
            "selected_system_preconfirmation": (
                selected_system_preconfirmation
            ),
            "rrc_realtime_progress": rrc_realtime_progress,
            "pug_cross_suite_implementation": (
                pug_cross_suite_implementation
            ),
            "pug_deployment_state": deployment_state,
            "self_algorithm_selection": self_algorithm,
            "data_readiness": json_evidence(data_readiness_path, root),
            "parrot_features_complete": parrot_features_complete,
            "downstream": downstream,
        },
        "effect_status": {
            "classic_baseline_integrity": classic_integrity,
            "domain_nearest_ronetc_protocol_frozen": (
                domain_nearest_ronetc["protocol_frozen_and_audited"]
            ),
            "domain_nearest_ronetc_terminal": (
                domain_nearest_ronetc["execution_terminal"]
            ),
            "pairwise_strict_five_metric_dominance_count": strict_five_count,
            "selected_system_classic_main_gate_passes": (
                selected_system_preconfirmation[
                    "classic_main_gate_passes"
                ]
            ),
            "pairwise_absolute_corruption_passes": absolute_corruption.get(
                "passes"
            )
            is True,
            "selected_system_absolute_corruption_passes": (
                selected_system_preconfirmation[
                    "absolute_corruption_gate_passes"
                ]
            ),
            "pairwise_comparative_corruption_passes": comparative.get(
                "comparative_robustness_gate_passes"
            )
            is True,
            "selected_system_comparative_corruption_passes": (
                selected_system_preconfirmation[
                    "comparative_corruption_gate_passes"
                ]
            ),
            "selected_system_selective_unknown_detection_sota": (
                selected_system_preconfirmation[
                    "selective_unknown_detection_sota_authorized"
                ]
            ),
            "selected_system_selective_corruption_robustness_sota": (
                selected_system_preconfirmation[
                    "selective_corruption_robustness_sota_authorized"
                ]
            ),
            "selected_system_any_selective_sota_authorized": (
                selected_system_preconfirmation[
                    "any_selective_sota_authorized"
                ]
            ),
            "krc_terminal": krc_effect_terminal,
            "krc_negative_terminal_decision_clarified": (
                krc_terminal_clarification["valid"]
            ),
            "pug_terminal": pug_effect_terminal,
            "pug_cross_suite_design_frozen": pug_cross_suite_design[
                "frozen"
            ],
            "pug_cross_suite_implementation_complete": (
                pug_cross_suite_implementation["complete"]
            ),
            "self_algorithm_direct_tournament_required": self_algorithm[
                "direct_tournament"
            ]["required"],
            "self_algorithm_direct_tournament_design_frozen": (
                direct_tournament_design["frozen"]
            ),
            "self_algorithm_direct_tournament_implementation_complete": (
                direct_tournament_implementation["complete"]
            ),
            "self_algorithm_direct_tournament_terminal": (
                self_algorithm["direct_tournament"]["terminal"]
            ),
            "selected_system_downstream_adapter_design_frozen": (
                selected_system_adapter_design["frozen"]
            ),
            "selected_system_common_runtime_adapter_complete": (
                selected_system_adapter_design[
                    "common_runtime_adapter_complete"
                ]
            ),
            "selected_system_downstream_adapter_implementation_complete": (
                selected_system_adapter_implementation["complete"]
            ),
            "selected_system_preconfirmation_design_frozen": (
                selected_system_preconfirmation[
                    "design_frozen_and_audited"
                ]
            ),
            "selected_system_preconfirmation_terminal": (
                selected_system_preconfirmation["terminal"]
            ),
            "rrc_branch_terminal": self_algorithm["krc_rrc_branch"][
                "terminal"
            ],
            "rrc_realtime_progress_valid": rrc_realtime_progress["valid"],
            "rrc_realtime_progress_counts": rrc_realtime_progress.get(
                "counts", {}
            ),
            "external_data_ready": data_ready,
            "external_malicious_terminal": downstream[
                "external_malicious"
            ]["complete"],
            "parrot_features_complete": parrot_features_complete,
            "benign_safety_terminal": downstream[
                "parrot_benign_safety"
            ]["complete"],
            "efficiency_terminal": downstream[
                "opendetect_efficiency"
            ]["complete"],
            "integrated_comprehensive_effect_passes": (
                comprehensive_effect_pass
            ),
        },
        "blockers": blockers,
        "claim_boundary": {
            "integrity_pass_does_not_imply_effect_pass": True,
            "data_readiness_does_not_imply_external_effect": True,
            "staging_does_not_imply_pug_execution": True,
            "partial_krc_progress_does_not_imply_terminal_result": True,
            "pug_pilot_positive_requires_cross_suite_confirmation": True,
            "pug_cross_suite_design_is_not_execution_or_effect": True,
            "dual_positive_self_algorithms_require_fresh_direct_tournament": (
                True
            ),
            "common_runtime_adapter_does_not_imply_downstream_effect": True,
            "domain_nearest_protocol_does_not_imply_execution_or_effect": True,
            "rrc_is_required_after_valid_negative_krc": True,
            "selective_sota_must_preserve_its_frozen_scope": True,
            "selective_sota_does_not_imply_comprehensive_sota": True,
            "comprehensive_sota_authorized": goal_achieved,
        },
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_current_goal_status_v1/audit.json"
        ),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    audit = build_audit(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "goal_achieved": audit["goal_achieved"],
                "blocker_count": len(audit["blockers"]),
                "manifest_sha256": audit["manifest_sha256"],
                "file_sha256": file_hash(output),
                "output": str(output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
