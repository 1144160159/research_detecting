"""Fail-closed audit for one HFT-MGBS Pareto candidate evidence manifest.

This audit stops at the candidate boundary.  It may prove that a sealed full
pipeline candidate is eligible for Pareto ingestion, but it never selects a
champion or grants the final production release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

# Support the documented direct invocation from a checked-out project root
# without requiring an editable install or caller-provided PYTHONPATH.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_release_candidate import (
    MAX_GATE_MAP,
    MIN_GATE_MAP,
    PHYSICAL_MAX_GATE_MAP,
    audit as audit_offline_release,
)
from hft_mgbs.algorithm_optimality import audit_algorithm_search
from hft_mgbs.algorithm_campaign_gate import verify_algorithm_campaign_gate
from hft_mgbs.stage_evidence import StageContract, aggregate_stage_evidence
from hft_mgbs.new_nic_r0_unified import (
    audit_new_nic_r0_campaign,
    stage_backend_binding_from_r0_identity,
)


SHA256_LENGTH = 64
PRODUCTION_STAGES = ("r1", "r2", "r3", "r4_24h", "r4_72h")
TPACKET_REQUIRED_EVIDENCE = {
    "breakthrough_acceptance.json",
    "capture.json",
    "capture_process_status.txt",
    "capture.stderr",
    "capture.stdout",
    "channels_before.txt",
    "coalesce_before.txt",
    "coalesce_restored.txt",
    "irq_affinity_active.tsv",
    "irq_affinity_before.tsv",
    "irq_affinity_pre_restore.tsv",
    "irq_affinity_restored.tsv",
    "irqbalance_state.txt",
    "meminfo_after.txt",
    "meminfo_before.txt",
    "mpstat.txt",
    "pktgen_module_post.txt",
    "pktgen_pgctrl.txt",
    "post_capture_link.txt",
    "post_replay_link.txt",
    "pre_capture_link.txt",
    "pre_replay_link.txt",
    "proc_stat_after.txt",
    "proc_stat_before.txt",
    "ready.json",
    "ring_active.txt",
    "ring_before.txt",
    "ring_restored.txt",
    "run_config.json",
    "runner_exit_status.env",
    "stats_after.txt",
    "stats_before.txt",
    *(f"pktgen_device_{index}.txt" for index in range(8)),
}
DPDK_RESTORATION_STEPS = {
    "child_stopped",
    "netdevs_reappeared",
    "runtime_prefix_removed",
    "hugepage_count_restored",
    "hugetlb_mount_preserved",
    "final_state_verification",
}
EXPECTED_BACKEND_PRIORITY = [
    "native_af_xdp_forced_zerocopy",
    "dpdk_multiqueue_rss_tss",
    "tpacket_v3_diagnostic",
    "af_packet_timestamp_fallback",
]
COUNTABLE_R0_BACKENDS = {
    "native_af_xdp_forced_zerocopy",
    "dpdk_multiqueue_rss_tss",
}
XDP_RESTORATION_STEPS = {
    "xdp_program_detached",
    "umem_released",
    "interfaces_restored",
    "final_state_verification",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def nonnegative_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def load_json(path: Path) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    payload = json.loads(
        path.read_text(encoding="utf-8"), parse_constant=reject_constant
    )
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value must be an object")
    return payload


def resolve_config_path(manifest_path: Path, reference: dict[str, Any]) -> Path:
    path = Path(str(reference.get("path", "")))
    if path.is_absolute():
        raise ValueError("config path must be relative to the manifest directory")
    base = manifest_path.parent.resolve()
    resolved = (base / path).resolve()
    resolved.relative_to(base)
    return resolved


def resolve_remote_path(receipt_root: Path, remote_path: str) -> Path:
    if not remote_path.startswith("/"):
        raise ValueError("remote evidence path must be absolute")
    base = receipt_root.resolve()
    resolved = (base / remote_path.lstrip("/\\")).resolve()
    resolved.relative_to(base)
    return resolved


def add_once(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def verify_config_artifacts(
    manifest_path: Path,
    manifest: dict[str, Any],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    hashes: dict[str, str] = {}
    references = manifest.get("config_artifacts")
    required = {
        "algorithm_search",
        "algorithm_optimality_audit",
        "release_candidate",
        "capture_search",
        "hardware_gate",
        "ten_mpps_target",
        "tpacket_search",
        "dpdk_1m_contract",
        "dpdk_12m_contract",
        "production_stage_contract",
        "new_nic_r0_trust_profile",
    }
    if not isinstance(references, dict):
        errors.append("manifest.config_artifacts.missing")
        return loaded, hashes
    for name in sorted(required - set(references)):
        errors.append(f"config.{name}.reference")
    for name, reference in sorted(references.items()):
        if re.fullmatch(r"[a-z0-9_]+", name) is None:
            errors.append(f"config.{name}.name")
            continue
        if not isinstance(reference, dict):
            errors.append(f"config.{name}.reference")
            continue
        expected_hash = reference.get("sha256")
        if not valid_sha256(expected_hash):
            errors.append(f"config.{name}.declared_sha256")
            continue
        try:
            path = resolve_config_path(manifest_path, reference)
        except (ValueError, OSError):
            errors.append(f"config.{name}.path")
            continue
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"config.{name}.missing")
            continue
        actual_hash = sha256_file(path)
        hashes[f"config.{name}"] = actual_hash
        if actual_hash != expected_hash:
            errors.append(f"config.{name}.sha256")
            continue
        try:
            loaded[name] = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            errors.append(f"config.{name}.json")
    return loaded, hashes


def audit_algorithm(
    search: dict[str, Any],
    release: dict[str, Any],
    frozen_optimality_audit: dict[str, Any],
    errors: list[str],
    authoritative_campaign: dict[str, Any] | None = None,
) -> tuple[bool, bool]:
    """Audit the offline winner from source evidence, not declarations.

    The frozen audit is hash-bound by ``verify_config_artifacts``.  It is still
    treated as a cache only: this function recomputes the audit from the
    independently hash-verified algorithm search and requires structural
    equality before either offline gate can become true.
    """

    result = audit_offline_release(search, release)
    for error in result.get("errors", []):
        add_once(errors, f"offline.{error}")
    candidates = search.get("candidates") or []
    dimensions = search.get("search_dimensions") or {}
    allowed_fields = {
        "feature_profile": set(dimensions.get("feature_profiles") or []),
        "classifier": set(dimensions.get("classifier_families") or []),
        "threshold_policy": set(dimensions.get("threshold_policies") or []),
        "adaptation_policy": set(dimensions.get("adaptation_policies") or []),
    }
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            add_once(errors, f"algorithm.candidate.{index}.object")
            continue
        if not isinstance(candidate.get("id"), str) or not candidate["id"]:
            add_once(errors, f"algorithm.candidate.{index}.id")
        for field, allowed in allowed_fields.items():
            if candidate.get(field) not in allowed:
                add_once(errors, f"algorithm.candidate.{index}.{field}")
    protocol = search.get("selection_protocol") or {}
    if protocol.get("hard_constraints_before_pareto") is not True:
        errors.append("algorithm.hard_constraints_before_pareto")
    if protocol.get("normal_and_fallback_must_be_paired") is not True:
        errors.append("algorithm.normal_fallback_pairing")
    gates = release.get("frozen_non_live_gates") or {}
    observed = release.get("observed_confirmatory_lower_bounds") or {}
    for gate_name, observed_name in (*MIN_GATE_MAP.items(), *MAX_GATE_MAP.items()):
        if not finite_number(gates.get(gate_name)):
            add_once(errors, f"offline.numeric.{gate_name}")
        if not finite_number(observed.get(observed_name)):
            add_once(errors, f"offline.numeric.{observed_name}")
    physical = release.get("observed_physical_offline_confirmation") or {}
    if not nonnegative_integer(physical.get("run_count")):
        add_once(errors, "offline.numeric.physical_run_count")
    for gate_name, observed_name in PHYSICAL_MAX_GATE_MAP.items():
        if not finite_number(gates.get(gate_name)):
            add_once(errors, f"offline.numeric.{gate_name}")
        if not finite_number(physical.get(observed_name)):
            add_once(errors, f"offline.numeric.{observed_name}")
    algorithm_errors = [
        error
        for error in errors
        if error.startswith("algorithm.") or error.startswith("offline.search.")
    ]
    offline_errors = [error for error in errors if error.startswith("offline.")]

    recomputed = audit_algorithm_search(search)
    selected = search.get("selected_candidate")
    campaign_qualified = (
        isinstance(authoritative_campaign, dict)
        and authoritative_campaign.get("qualified") is True
        and authoritative_campaign.get("winner") == selected
    )
    if frozen_optimality_audit.get("scope") != (
        "bounded_offline_algorithm_optimality_audit"
    ):
        add_once(errors, "algorithm.optimality.scope")
    if frozen_optimality_audit != recomputed:
        add_once(errors, "algorithm.optimality.frozen_drift")
    if not campaign_qualified and (
        frozen_optimality_audit.get("accepted") is True
        and recomputed.get("accepted") is not True
    ):
        add_once(errors, "algorithm.optimality.fabricated_acceptance")

    recomputed_winner = recomputed.get("confirmatory_practical_winner")
    frozen_winner = frozen_optimality_audit.get("confirmatory_practical_winner")
    candidate_ids = {
        candidate.get("id")
        for candidate in candidates
        if isinstance(candidate, Mapping) and isinstance(candidate.get("id"), str)
    }
    if not isinstance(selected, str) or not selected or selected not in candidate_ids:
        add_once(errors, "algorithm.optimality.selected_candidate")
    if recomputed_winner != selected or frozen_winner != selected:
        add_once(errors, "algorithm.optimality.winner_mismatch")

    if not campaign_qualified and recomputed.get("accepted") is not True:
        add_once(errors, "algorithm.optimality.recomputed_not_accepted")
    if not campaign_qualified and recomputed.get("algorithm_only_practical_optimum_proven") is not True:
        add_once(errors, "algorithm.optimality.optimum_not_proven")
    if not campaign_qualified and frozen_optimality_audit.get("accepted") is not True:
        add_once(errors, "algorithm.optimality.frozen_not_accepted")
    if not campaign_qualified and (
        frozen_optimality_audit.get("algorithm_only_practical_optimum_proven")
        is not True
    ):
        add_once(errors, "algorithm.optimality.frozen_optimum_not_proven")

    optimality_qualified = not any(
        error.startswith("algorithm.optimality.") for error in errors
    )
    algorithm_errors = [
        error
        for error in errors
        if error.startswith("algorithm.") or error.startswith("offline.search.")
    ]
    offline_errors = [error for error in errors if error.startswith("offline.")]
    return (
        not algorithm_errors and optimality_qualified,
        not offline_errors and optimality_qualified,
    )


def audit_capture_configs(
    capture: dict[str, Any], hardware: dict[str, Any], errors: list[str]
) -> bool:
    candidates = capture.get("candidates") or []
    budget = capture.get("candidate_budget")
    evaluated = capture.get("candidates_evaluated")
    active = capture.get("active_candidates")
    if (
        not isinstance(budget, int)
        or isinstance(budget, bool)
        or evaluated != budget
        or len(candidates) != budget
    ):
        errors.append("capture.search_budget")
    ids = [row.get("id") for row in candidates if isinstance(row, dict)]
    if len(ids) != len(candidates) or len(set(ids)) != len(ids):
        errors.append("capture.candidate_ids")
    if active != 0:
        errors.append("capture.active_candidates")
    gates = capture.get("hard_gates") or {}
    if gates.get("r0_capture_only_min_mpps") != 12.0:
        errors.append("capture.r0_target")
    if gates.get("capture_drop_rate_max") != 0.0:
        errors.append("capture.drop_gate")
    if (capture.get("pareto_result") or {}).get(
        "final_production_pareto_exists"
    ) is not False:
        errors.append("capture.feasible_set_marker")
    if capture.get("full_pipeline_qualified") is not False:
        errors.append("capture.full_pipeline_marker")
    if capture.get("final_pareto_ingestion_allowed") is not False:
        errors.append("capture.final_pareto_marker")

    mandatory = hardware.get("mandatory_capabilities") or {}
    hardware_gates = hardware.get("hard_gates") or {}
    if hardware.get("status") != "frozen_requirements__hardware_pending":
        errors.append("hardware.pending_status")
    if hardware.get("candidate_budget") != 2:
        errors.append("hardware.candidate_budget")
    if (hardware.get("current_adapter") or {}).get("eligible") is not False:
        errors.append("hardware.current_adapter_eligibility")
    for name in (
        "traffic_generator_must_not_share_current_adapter_packet_budget",
        "native_xdp_driver_mode_required",
        "af_xdp_force_zerocopy_bind_required",
        "dpdk_pmd_rss_required",
        "dpdk_pmd_tss_required",
        "numa_local_pcie_required",
    ):
        if mandatory.get(name) is not True:
            errors.append(f"hardware.{name}")
    for name in ("64b_offered_mpps_min", "64b_zero_loss_capture_mpps_min"):
        if mandatory.get(name) != 12.0:
            errors.append(f"hardware.{name}")
    for name in ("rx_queues_min", "tx_queues_min"):
        if mandatory.get(name) != 8:
            errors.append(f"hardware.{name}")
    if hardware_gates.get("capture_drop_rate_max") != 0.0:
        errors.append("hardware.capture_drop_rate")
    if hardware.get("full_pipeline_qualified") is not False:
        errors.append("hardware.full_pipeline_marker")
    if hardware.get("final_pareto_ingestion_allowed") is not False:
        errors.append("hardware.final_pareto_marker")
    return not any(
        error.startswith("capture.") or error.startswith("hardware.")
        for error in errors
    )


def validate_dpdk_receipt(
    receipt: dict[str, Any],
    expected: bool,
    errors: list[str],
    prefix: str,
    *,
    contract: dict[str, Any] | None = None,
    contract_sha256: str | None = None,
    countable: bool = False,
    policy: dict[str, Any] | None = None,
) -> None:
    if (
        receipt.get("schema_version") != 1
        or receipt.get("scope") != "dpdk_release_gate_runner_acceptance"
        or receipt.get("receipt_semantics")
        != "derived_from_preacceptance_sealed_evidence_v1"
        or receipt.get("standalone_receipt_trusted") is not False
    ):
        errors.append(f"{prefix}.schema")
    status = receipt.get("status")
    if not isinstance(status, dict):
        errors.append(f"{prefix}.status")
        return
    observed = receipt.get("r0_capture_only_qualified")
    if observed is not expected:
        errors.append(f"{prefix}.expected_r0_state")
    if receipt.get("full_pipeline_qualified") is not False:
        errors.append(f"{prefix}.full_pipeline_marker")
    if receipt.get("final_pareto_ingestion_allowed") is not False:
        errors.append(f"{prefix}.final_pareto_marker")
    if receipt.get("restoration_verified") is not True:
        errors.append(f"{prefix}.restoration")
    if receipt.get("evidence_complete_before_hash") is not True:
        errors.append(f"{prefix}.inventory")
    if receipt.get("hash_checks_verified") is not True:
        errors.append(f"{prefix}.hash_checks")
    input_sha256 = receipt.get("input_sha256")
    if not isinstance(input_sha256, dict) or any(
        not valid_sha256(input_sha256.get(name))
        for name in (
            "data_resource_acceptance",
            "evidence_inventory",
            "evidence_sha256_base_check",
            "evidence_sha256_complete_check",
        )
    ):
        errors.append(f"{prefix}.input_sha256")
    if contract is None or not valid_sha256(contract_sha256):
        errors.append(f"{prefix}.contract")
    else:
        if receipt.get("candidate_id") != contract.get("candidate_id"):
            errors.append(f"{prefix}.candidate_id")
        if receipt.get("frozen_thresholds_sha256") != contract_sha256:
            errors.append(f"{prefix}.frozen_thresholds_sha256")
    if receipt.get("termination_signal") not in (None, "", "none"):
        errors.append(f"{prefix}.termination_signal")
    if expected:
        for name in (
            "original_exit_status",
            "validator_exit_status",
            "restore_status",
            "evidence_status",
            "base_hash_check_status",
            "complete_hash_check_status",
        ):
            if status.get(name) != 0:
                errors.append(f"{prefix}.status.{name}")
        if receipt.get("runner_qualified") is not True:
            errors.append(f"{prefix}.runner")
        if receipt.get("data_resource_qualified") is not True:
            errors.append(f"{prefix}.data_resource")
        if receipt.get("errors") != []:
            errors.append(f"{prefix}.errors")
    else:
        for name in (
            "restore_status",
            "evidence_status",
            "base_hash_check_status",
            "complete_hash_check_status",
        ):
            if status.get(name) != 0:
                errors.append(f"{prefix}.status.{name}")
        original = status.get("original_exit_status")
        validator = status.get("validator_exit_status")
        if (
            not nonnegative_integer(original)
            or not nonnegative_integer(validator)
            or (original == 0 and validator == 0)
        ):
            errors.append(f"{prefix}.failed_status")
        if receipt.get("runner_qualified") is not False:
            errors.append(f"{prefix}.failed_runner_marker")
        if receipt.get("data_resource_qualified") is not False:
            errors.append(f"{prefix}.failed_data_resource_marker")
        receipt_errors = receipt.get("errors")
        if not isinstance(receipt_errors, list) or not receipt_errors:
            errors.append(f"{prefix}.failed_errors")

    if countable:
        policy = policy or {}
        if contract is None:
            return
        if contract.get("target_load_mpps") != policy.get(
            "required_r0_target_mpps"
        ):
            errors.append(f"{prefix}.target_load")
        if contract.get("frame_size_bytes") != 64:
            errors.append(f"{prefix}.frame_size")
        min_windows = contract.get("min_rate_full_windows")
        if (
            not nonnegative_integer(min_windows)
            or min_windows < policy.get("required_r0_full_windows", 0)
        ):
            errors.append(f"{prefix}.full_windows")
        if contract.get("max_pipeline_drop_rate") != policy.get(
            "max_capture_drop_rate"
        ):
            errors.append(f"{prefix}.drop_gate")
        p99_gate = contract.get("max_end_to_end_p99_us")
        if (
            not finite_number(p99_gate)
            or float(p99_gate) > policy.get("max_p99_us", 0)
        ):
            errors.append(f"{prefix}.p99_gate")
        p999_gate = contract.get("max_end_to_end_p999_us")
        if (
            not finite_number(p999_gate)
            or float(p999_gate) > policy.get("max_p999_us", 0)
        ):
            errors.append(f"{prefix}.p999_gate")


def validate_tpacket_receipt(
    receipt: dict[str, Any],
    expected: bool,
    errors: list[str],
    prefix: str,
    *,
    countable: bool = False,
    policy: dict[str, Any] | None = None,
) -> None:
    policy = policy or {
        "required_r0_target_mpps": 12.0,
        "required_r0_full_windows": 15,
        "max_p99_us": 100.0,
        "max_p999_us": 500.0,
    }
    if (
        receipt.get("schema_version") != 1
        or receipt.get("scope") != "tpacket_v3_breakthrough_r0_acceptance"
        or not isinstance(receipt.get("candidate_id"), str)
        or not receipt.get("candidate_id")
    ):
        errors.append(f"{prefix}.schema")
    if receipt.get("r0_capture_only_qualified") is not expected:
        errors.append(f"{prefix}.expected_r0_state")
    if receipt.get("full_pipeline_qualified") is not False:
        errors.append(f"{prefix}.full_pipeline_marker")
    if receipt.get("final_pareto_ingestion_allowed") is not False:
        errors.append(f"{prefix}.final_pareto_marker")
    if receipt.get("restoration_verified") is not True:
        errors.append(f"{prefix}.restoration")
    for name in (
        "offered_mpps_sum",
        "synthetic_rx_min_full_epoch_mpps",
        "p99_us",
        "p999_us",
        "host_cpu_fraction",
        "capture_memory_fraction",
    ):
        if not finite_number(receipt.get(name)):
            errors.append(f"{prefix}.{name}")
    offered = receipt.get("offered_packets")
    received = receipt.get("synthetic_test_packets")
    gap = receipt.get("offered_received_gap")
    discards = receipt.get("rx_discards_delta")
    socket_drops = receipt.get("packet_socket_drops")
    freezes = receipt.get("packet_socket_freeze_queue_count")
    if not all(
        nonnegative_integer(value)
        for value in (offered, received, gap, discards, socket_drops, freezes)
    ):
        errors.append(f"{prefix}.packet_accounting")
        return
    exact = (
        gap == offered - received
        and gap == discards + socket_drops
        and receipt.get("loss_accounting_exact") is True
    )
    if not exact:
        errors.append(f"{prefix}.loss_accounting")
    target = policy.get("required_r0_target_mpps")
    offered_mpps = receipt.get("offered_mpps_sum")
    capture_mpps = receipt.get("synthetic_rx_min_full_epoch_mpps")
    p99 = receipt.get("p99_us")
    p999 = receipt.get("p999_us")
    generator_gate = finite_number(offered_mpps) and float(offered_mpps) >= target
    capture_gate = finite_number(capture_mpps) and float(capture_mpps) >= target
    loss_gate = (
        offered == received
        and discards == 0
        and socket_drops == 0
        and freezes == 0
        and exact
    )
    latency_gate = (
        finite_number(p99)
        and finite_number(p999)
        and float(p99) <= policy.get("max_p99_us")
        and float(p999) <= policy.get("max_p999_us")
    )
    resource_gate = (
        finite_number(receipt.get("host_cpu_fraction"))
        and finite_number(receipt.get("capture_memory_fraction"))
        and float(receipt["host_cpu_fraction"]) <= 0.85
        and float(receipt["capture_memory_fraction"]) <= 0.85
    )
    restoration_gate = all(
        receipt.get(name) is True
        for name in (
            "irq_assignment_verified",
            "irq_affinity_stable",
            "irq_restoration_verified",
            "ring_restoration_verified",
            "coalesce_restoration_verified",
            "links_restored",
            "pktgen_module_unloaded",
            "restoration_verified",
        )
    ) and receipt.get("runner_exit_status") == 0
    derived = {
        "generator_12mpps_gate_qualified": generator_gate,
        "capture_rate_12mpps_gate_qualified": capture_gate,
        "loss_gate_qualified": loss_gate,
        "latency_gate_qualified": latency_gate,
        "resource_gate_qualified": resource_gate,
    }
    for name, value in derived.items():
        if receipt.get(name) is not value:
            errors.append(f"{prefix}.{name}")
    windows = receipt.get("synthetic_rx_full_epoch_windows")
    windows_gate = nonnegative_integer(windows) and windows >= policy.get(
        "required_r0_full_windows", 0
    )
    qualified = all(
        (
            generator_gate,
            capture_gate,
            loss_gate,
            latency_gate,
            resource_gate,
            restoration_gate,
            windows_gate,
        )
    )
    if receipt.get("r0_capture_only_qualified") is not qualified:
        errors.append(f"{prefix}.derived_r0_state")
    if countable and not windows_gate:
        errors.append(f"{prefix}.full_windows")


def validate_native_xdp_receipt(
    receipt: dict[str, Any],
    errors: list[str],
    prefix: str,
    *,
    contract: dict[str, Any] | None,
    contract_sha256: str | None,
    policy: dict[str, Any],
) -> None:
    """Validate a production native-AF_XDP receipt from raw, sealed facts."""

    before = len(errors)
    if (
        receipt.get("schema_version") != 1
        or receipt.get("scope")
        != "native_af_xdp_release_gate_runner_acceptance"
        or receipt.get("receipt_semantics")
        != "derived_from_preacceptance_sealed_evidence_v1"
        or receipt.get("standalone_receipt_trusted") is not False
        or receipt.get("backend") != "native_af_xdp_forced_zerocopy"
    ):
        errors.append(f"{prefix}.schema")
    if contract is None or not valid_sha256(contract_sha256):
        errors.append(f"{prefix}.contract")
        return
    if receipt.get("candidate_id") != contract.get("candidate_id"):
        errors.append(f"{prefix}.candidate_id")
    if receipt.get("frozen_thresholds_sha256") != contract_sha256:
        errors.append(f"{prefix}.frozen_thresholds_sha256")
    if (
        contract.get("target_load_mpps") != policy.get("required_r0_target_mpps")
        or contract.get("frame_size_bytes") != 64
        or contract.get("frozen") is not True
        or contract.get("diagnostic_only") is not False
        or contract.get("expected_backend")
        != "native_af_xdp_forced_zerocopy"
        or not nonnegative_integer(contract.get("min_rate_full_windows"))
        or contract.get("min_rate_full_windows")
        < policy.get("required_r0_full_windows", 0)
        or contract.get("native_xdp_driver_mode_required") is not True
        or contract.get("af_xdp_force_zerocopy_required") is not True
        or contract.get("independent_generator_required") is not True
    ):
        errors.append(f"{prefix}.contract_shape")
    for name in (
        "native_xdp_driver_mode_verified",
        "af_xdp_force_zerocopy_verified",
        "independent_generator_verified",
        "restoration_verified",
        "evidence_complete_before_hash",
        "hash_checks_verified",
        "runner_qualified",
        "data_resource_qualified",
        "r0_capture_only_qualified",
    ):
        if receipt.get(name) is not True:
            errors.append(f"{prefix}.{name}")
    if receipt.get("full_pipeline_qualified") is not False:
        errors.append(f"{prefix}.full_pipeline_marker")
    if receipt.get("final_pareto_ingestion_allowed") is not False:
        errors.append(f"{prefix}.final_pareto_marker")
    if receipt.get("termination_signal") not in (None, "", "none"):
        errors.append(f"{prefix}.termination_signal")
    if receipt.get("errors") != []:
        errors.append(f"{prefix}.errors")
    inputs = receipt.get("input_sha256")
    if (
        not isinstance(inputs, dict)
        or not inputs
        or any(not valid_sha256(value) for value in inputs.values())
    ):
        errors.append(f"{prefix}.input_sha256")
    status = receipt.get("status")
    if (
        not isinstance(status, dict)
        or not status
        or any(not nonnegative_integer(value) or value != 0 for value in status.values())
    ):
        errors.append(f"{prefix}.status")
    numeric = {
        name: receipt.get(name)
        for name in (
            "target_mpps",
            "observed_tx_mpps_min_1s",
            "observed_rx_mpps_min_1s",
            "p99_us",
            "p999_us",
        )
    }
    if any(not finite_number(value) for value in numeric.values()):
        errors.append(f"{prefix}.numeric")
    else:
        target = policy.get("required_r0_target_mpps")
        if (
            numeric["target_mpps"] != target
            or numeric["observed_tx_mpps_min_1s"] < target
            or numeric["observed_rx_mpps_min_1s"] < target
            or numeric["p99_us"] > policy.get("max_p99_us")
            or numeric["p999_us"] > policy.get("max_p999_us")
        ):
            errors.append(f"{prefix}.performance_gate")
    offered = receipt.get("offered_packets")
    received = receipt.get("received_packets")
    if (
        not nonnegative_integer(offered)
        or offered == 0
        or not nonnegative_integer(received)
        or offered != received
        or receipt.get("offered_received_gap") != 0
        or receipt.get("capture_drop_count") != 0
        or receipt.get("rx_nombuf_count") != 0
        or receipt.get("full_rate_windows", 0)
        < policy.get("required_r0_full_windows", 0)
    ):
        errors.append(f"{prefix}.packet_gate")
    if len(errors) == before and receipt.get("r0_capture_only_qualified") is not True:
        errors.append(f"{prefix}.derived_r0_state")


def validate_backend_selection(
    receipt: dict[str, Any],
    backend: str,
    errors: list[str],
    prefix: str,
    *,
    contract: dict[str, Any] | None = None,
    contract_sha256: str | None = None,
) -> tuple[str | None, str | None]:
    """Bind the XDP-first decision and the identity used for repeat counting."""

    before = len(errors)
    capture_hardware = receipt.get("capture_hardware_identity_sha256")
    generator_hardware = receipt.get("generator_hardware_identity_sha256")
    run_identity = receipt.get("run_bundle_identity")
    generator_identity = receipt.get("generator_run_identity")
    inputs = receipt.get("input_sha256")
    required_inputs = {
        "hardware_identity.json",
        "generator_topology.json",
        "xdp_probe_acceptance.json",
        "evidence_inventory.json",
        "result.json",
        "restoration_ledger.json",
    }
    if backend == "dpdk_multiqueue_rss_tss":
        required_inputs.add("dpdk_capability.json")
    if (
        receipt.get("schema_version") != 1
        or receipt.get("scope") != "hft_capture_backend_selection_receipt"
        or receipt.get("preferred_backend") != EXPECTED_BACKEND_PRIORITY[0]
        or receipt.get("selected_backend") != backend
        or receipt.get("independent_generator_verified") is not True
        or receipt.get("generator_shares_capture_adapter_packet_budget") is not False
        or receipt.get("restoration_verified") is not True
        or not valid_sha256(capture_hardware)
        or receipt.get("hardware_identity_sha256") != capture_hardware
        or not valid_sha256(generator_hardware)
        or capture_hardware == generator_hardware
        or not valid_sha256(run_identity)
        or not valid_sha256(generator_identity)
        or not isinstance(inputs, dict)
        or not required_inputs.issubset(inputs)
        or any(
            not isinstance(name, str)
            or re.fullmatch(r"[A-Za-z0-9_.-]+", name) is None
            or name in {".", ".."}
            or not valid_sha256(digest)
            for name, digest in (inputs.items() if isinstance(inputs, dict) else [])
        )
    ):
        errors.append(f"{prefix}.schema")
    if (
        contract is None
        or not valid_sha256(contract_sha256)
        or receipt.get("candidate_id") != contract.get("candidate_id")
        or receipt.get("frozen_contract_sha256") != contract_sha256
    ):
        errors.append(f"{prefix}.contract")
    if backend == "native_af_xdp_forced_zerocopy":
        if (
            receipt.get("native_xdp_probe_attempted") is not True
            or receipt.get("af_xdp_force_zerocopy_requested") is not True
            or receipt.get("native_af_xdp_qualified") is not True
            or receipt.get("fallback_reason") not in (None, "", "none")
        ):
            errors.append(f"{prefix}.xdp_selection")
    elif backend == "dpdk_multiqueue_rss_tss":
        if (
            receipt.get("native_xdp_probe_attempted") is not True
            or receipt.get("af_xdp_force_zerocopy_requested") is not True
            or receipt.get("native_af_xdp_qualified") is not False
            or receipt.get("dpdk_multiqueue_rss_tss_verified") is not True
            or receipt.get("fallback_reason")
            not in {
                "native_xdp_unavailable",
                "forced_zerocopy_bind_failed",
                "native_xdp_r0_gate_failed",
            }
        ):
            errors.append(f"{prefix}.dpdk_fallback")
    else:
        errors.append(f"{prefix}.backend")
    if len(errors) != before:
        return None, None
    return run_identity, generator_identity


def validate_r0_raw_result(
    raw: dict[str, Any],
    backend: str,
    contract: dict[str, Any] | None,
    contract_sha256: str | None,
    policy: dict[str, Any],
    errors: list[str],
    prefix: str,
) -> None:
    """Recompute countable R0 gates from the hash-bound raw counter record."""

    if contract is None or not valid_sha256(contract_sha256):
        errors.append(f"{prefix}.contract")
        return
    if (
        raw.get("schema_version") != 1
        or raw.get("scope") != "r0_production_capture_only_raw_v1"
        or raw.get("evidence_semantics") != "raw_counter_snapshot_v1"
        or raw.get("self_qualification_trusted") is not False
        or raw.get("candidate_id") != contract.get("candidate_id")
        or raw.get("frozen_contract_sha256") != contract_sha256
        or raw.get("backend") != backend
        or raw.get("target_mpps") != policy.get("required_r0_target_mpps")
        or raw.get("frame_size_bytes") != 64
        or raw.get("errors") != []
        or raw.get("full_pipeline_qualified") is not False
        or raw.get("final_pareto_ingestion_allowed") is not False
    ):
        errors.append(f"{prefix}.schema")
    code_identity_pairs = (
        ("runner_sha256", "expected_runner_sha256"),
        ("binary_sha256", "expected_binary_sha256"),
        ("validator_sha256", "expected_validator_sha256"),
        ("composer_sha256", "expected_composer_sha256"),
    )
    if any(
        not valid_sha256(contract.get(expected_name))
        or raw.get(observed_name) != contract.get(expected_name)
        for observed_name, expected_name in code_identity_pairs
    ):
        errors.append(f"{prefix}.code_identity")

    numeric_fields = (
        "observed_tx_mpps_min_1s",
        "observed_rx_mpps_min_1s",
        "duration_s",
    )
    if any(not finite_number(raw.get(name)) for name in numeric_fields):
        errors.append(f"{prefix}.numeric")
    else:
        min_duration = contract.get("min_run_duration_s")
        if (
            not finite_number(min_duration)
            or raw["observed_tx_mpps_min_1s"]
            < policy.get("required_r0_target_mpps")
            or raw["observed_rx_mpps_min_1s"]
            < policy.get("required_r0_target_mpps")
            or (finite_number(min_duration) and raw["duration_s"] < min_duration)
        ):
            errors.append(f"{prefix}.rate_duration_gate")

    offered = raw.get("offered_packets")
    received = raw.get("received_packets")
    capture_stats = raw.get("capture_stats_delta")
    replay_stats = raw.get("replay_stats_delta")
    if (
        not nonnegative_integer(offered)
        or offered == 0
        or not nonnegative_integer(received)
        or received != offered
        or raw.get("offered_received_gap") != 0
        or not isinstance(capture_stats, dict)
        or any(capture_stats.get(name) != 0 for name in ("imissed", "ierrors", "rx_nombuf"))
        or not isinstance(replay_stats, dict)
        or replay_stats.get("oerrors") != 0
    ):
        errors.append(f"{prefix}.packet_loss_gate")

    tx_windows = raw.get("tx_rate_full_windows")
    rx_windows = raw.get("rx_rate_full_windows")
    if (
        raw.get("rate_window_alignment")
        != "shared_monotonic_epoch_fixed_1s_v1"
        or not nonnegative_integer(tx_windows)
        or tx_windows < policy.get("required_r0_full_windows", 0)
        or not nonnegative_integer(rx_windows)
        or rx_windows < policy.get("required_r0_full_windows", 0)
    ):
        errors.append(f"{prefix}.full_windows")

    latency = raw.get("end_to_end_latency_us")
    sampling = contract.get("latency_sampling")
    if not isinstance(sampling, dict):
        sampling = {}
    if not isinstance(latency, dict):
        latency = {}
    samples = latency.get("samples")
    p99 = latency.get("p99")
    p999 = latency.get("p999")
    min_samples = sampling.get("min_samples")
    if (
        not nonnegative_integer(samples)
        or not nonnegative_integer(min_samples)
        or (
            nonnegative_integer(samples)
            and nonnegative_integer(min_samples)
            and samples < min_samples
        )
        or not finite_number(p99)
        or p99 > policy.get("max_p99_us")
        or not finite_number(p999)
        or p999 > policy.get("max_p999_us")
        or raw.get("latency_sample_stride") != sampling.get("stride_packets")
        or raw.get("latency_timestamp_source") != sampling.get("timestamp_source")
    ):
        errors.append(f"{prefix}.latency_gate")

    if backend == "native_af_xdp_forced_zerocopy":
        if (
            raw.get("native_xdp_driver_mode_verified") is not True
            or raw.get("af_xdp_force_zerocopy_verified") is not True
        ):
            errors.append(f"{prefix}.xdp_mode")
    elif backend == "dpdk_multiqueue_rss_tss":
        rx_queues = raw.get("rx_queue_count")
        tx_queues = raw.get("tx_queue_count")
        if (
            raw.get("dpdk_rss_verified") is not True
            or raw.get("dpdk_tss_verified") is not True
            or not nonnegative_integer(rx_queues)
            or rx_queues < policy.get("required_r0_rx_queues", 0)
            or not nonnegative_integer(tx_queues)
            or tx_queues < policy.get("required_r0_tx_queues", 0)
        ):
            errors.append(f"{prefix}.dpdk_multiqueue")


def verify_remote_json_artifact(
    reference: object,
    receipt_root: Path | None,
    prefix: str,
    errors: list[str],
    hashes: dict[str, str],
) -> dict[str, Any] | None:
    if not isinstance(reference, dict):
        errors.append(f"{prefix}.reference")
        return None
    declared_hash = reference.get("sha256")
    if not valid_sha256(declared_hash):
        errors.append(f"{prefix}.declared_sha256")
        return None
    remote_path = str(reference.get("path", ""))
    if not remote_path.startswith("/"):
        errors.append(f"{prefix}.remote_path")
        return None
    if receipt_root is None:
        errors.append(f"{prefix}.unverified")
        return None
    try:
        local_path = resolve_remote_path(receipt_root, remote_path)
    except (ValueError, OSError):
        errors.append(f"{prefix}.path_escape")
        return None
    if not local_path.is_file() or local_path.stat().st_size == 0:
        errors.append(f"{prefix}.missing")
        return None
    actual_hash = sha256_file(local_path)
    hashes[prefix] = actual_hash
    if actual_hash != declared_hash:
        errors.append(f"{prefix}.sha256")
        return None
    try:
        return load_json(local_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        errors.append(f"{prefix}.json")
        return None


def verify_remote_evidence_manifest(
    reference: object,
    receipt_root: Path | None,
    prefix: str,
    errors: list[str],
    hashes: dict[str, str],
    *,
    required_entries: set[str] | None = None,
    require_release_inventory: bool = False,
    receipt: dict[str, Any] | None = None,
    required_hash_entries: dict[str, str] | None = None,
    required_restoration_steps: set[str] | None = None,
) -> tuple[bool, bool]:
    restoration_evidence_verified = not require_release_inventory
    if not isinstance(reference, dict):
        errors.append(f"{prefix}.reference")
        return False, False
    declared_hash = reference.get("sha256")
    remote_path = str(reference.get("path", ""))
    if not valid_sha256(declared_hash):
        errors.append(f"{prefix}.declared_sha256")
        return False, False
    if not remote_path.startswith("/"):
        errors.append(f"{prefix}.remote_path")
        return False, False
    if receipt_root is None:
        errors.append(f"{prefix}.unverified")
        return False, False
    try:
        path = resolve_remote_path(receipt_root, remote_path)
    except (ValueError, OSError):
        errors.append(f"{prefix}.path_escape")
        return False, False
    if not path.is_file() or path.stat().st_size == 0:
        errors.append(f"{prefix}.missing")
        return False, False
    actual_hash = sha256_file(path)
    hashes[prefix] = actual_hash
    if actual_hash != declared_hash:
        errors.append(f"{prefix}.sha256")
        return False, False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        errors.append(f"{prefix}.read")
        return False, False
    if not lines:
        errors.append(f"{prefix}.empty")
        return False, False
    base = path.parent.resolve()
    manifest_entries: dict[str, str] = {}
    for index, line in enumerate(lines):
        parts = line.split(None, 1)
        if len(parts) != 2 or not valid_sha256(parts[0]):
            errors.append(f"{prefix}.entry.{index}.format")
            continue
        name = parts[1].lstrip("*")
        if name in manifest_entries:
            errors.append(f"{prefix}.entry.{index}.duplicate")
            continue
        candidate = (base / name).resolve()
        try:
            candidate.relative_to(base)
        except ValueError:
            errors.append(f"{prefix}.entry.{index}.path")
            continue
        if not candidate.is_file() or sha256_file(candidate) != parts[0]:
            errors.append(f"{prefix}.entry.{index}.sha256")
            continue
        manifest_entries[name] = parts[0]
    if required_entries is not None and not required_entries.issubset(
        manifest_entries
    ):
        errors.append(f"{prefix}.required_entries")
    for name, digest in (required_hash_entries or {}).items():
        if manifest_entries.get(name) != digest:
            errors.append(f"{prefix}.required_hash.{name}")
    if require_release_inventory:
        inventory_hash = manifest_entries.get("evidence_inventory.json")
        inventory_path = base / "evidence_inventory.json"
        if inventory_hash is None or not inventory_path.is_file():
            errors.append(f"{prefix}.inventory")
        else:
            try:
                inventory = load_json(inventory_path)
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                inventory = None
                errors.append(f"{prefix}.inventory_json")
            if isinstance(inventory, dict):
                required = inventory.get("required")
                present = inventory.get("present")
                lists_valid = (
                    isinstance(required, list)
                    and isinstance(present, list)
                    and all(isinstance(name, str) for name in required + present)
                )
                if (
                    inventory.get("schema_version") != 1
                    or not lists_valid
                    or (lists_valid and len(required) != len(set(required)))
                    or (lists_valid and len(present) != len(set(present)))
                    or (lists_valid and set(required) != set(present))
                    or inventory.get("missing") != []
                    or inventory.get("empty_required") != []
                    or inventory.get("restoration_verified") is not True
                    or inventory.get("evidence_complete_before_hash") is not True
                    or (lists_valid and not set(required).issubset(manifest_entries))
                ):
                    errors.append(f"{prefix}.inventory_membership")
                if isinstance(receipt, dict):
                    inputs = receipt.get("input_sha256")
                    if (
                        not isinstance(inputs, dict)
                        or inputs.get("evidence_inventory") != inventory_hash
                    ):
                        errors.append(f"{prefix}.receipt_inventory_hash")
            ledger_hash = manifest_entries.get("restoration_ledger.json")
            ledger_path = base / "restoration_ledger.json"
            if ledger_hash is None or not ledger_path.is_file():
                errors.append(f"{prefix}.restoration_ledger")
            else:
                try:
                    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                    ledger = None
                ledger_valid = not (
                    not isinstance(ledger, list)
                    or not ledger
                    or not (required_restoration_steps or set()).issubset(
                        {
                            row.get("step")
                            for row in ledger
                            if isinstance(row, dict)
                            and isinstance(row.get("step"), str)
                            and row.get("status") == 0
                            and row.get("ok") is True
                        }
                    )
                    or any(
                        not isinstance(row, dict)
                        or row.get("status") != 0
                        or row.get("ok") is not True
                        for row in ledger
                    )
                )
                if not ledger_valid:
                    errors.append(f"{prefix}.restoration_ledger_status")
                else:
                    restoration_evidence_verified = True
    return (
        not any(error.startswith(f"{prefix}.") for error in errors),
        restoration_evidence_verified,
    )


def validate_r0_repeat_independence(
    run_count: int,
    paths: list[str],
    receipt_hashes: list[str],
    manifest_hashes: list[str],
    run_identities: list[str],
    generator_identities: list[str],
    hardware_identities: list[str],
    backends: list[str],
    contracts: list[str],
    errors: list[str],
) -> bool:
    """Require independent run/generator identities on one frozen setup."""

    independent = run_count > 0 and not (
        len(paths) != run_count
        or len(set(paths)) != run_count
        or len(receipt_hashes) != run_count
        or len(set(receipt_hashes)) != run_count
        or len(manifest_hashes) != run_count
        or len(set(manifest_hashes)) != run_count
        or len(run_identities) != run_count
        or len(set(run_identities)) != run_count
        or len(generator_identities) != run_count
        or len(set(generator_identities)) != run_count
        or len(hardware_identities) != run_count
        or len(set(hardware_identities)) != 1
        or len(backends) != run_count
        or len(set(backends)) != 1
        or len(contracts) != run_count
        or len(set(contracts)) != 1
    )
    if not independent:
        errors.append("physical.independent_runs")
    return independent


def audit_physical_observations(
    manifest: dict[str, Any],
    configs: dict[str, dict[str, Any]],
    receipt_root: Path | None,
    errors: list[str],
) -> tuple[bool, bool, dict[str, str], dict[str, list[str]]]:
    observations = manifest.get("physical_observations")
    policy = manifest.get("audit_policy") or {}
    config_references = manifest.get("config_artifacts") or {}
    hashes: dict[str, str] = {}
    production_qualified: list[bool] = []
    production_paths: list[str] = []
    production_receipt_hashes: list[str] = []
    production_manifest_hashes: list[str] = []
    production_run_identities: list[str] = []
    production_generator_identities: list[str] = []
    production_hardware_identities: list[str] = []
    production_backends: list[str] = []
    production_contracts: list[str] = []
    all_restored = True
    identity_summary = {
        "run_bundle_identities": production_run_identities,
        "generator_run_identities": production_generator_identities,
        "hardware_identity_sha256": production_hardware_identities,
        "backends": production_backends,
        "contracts": production_contracts,
    }
    if not isinstance(observations, list) or not observations:
        errors.append("physical.observations")
        return False, False, hashes, identity_summary
    observation_ids = [
        observation.get("id")
        for observation in observations
        if isinstance(observation, dict)
    ]
    if (
        len(observation_ids) != len(observations)
        or any(not isinstance(value, str) or not value for value in observation_ids)
        or len(set(observation_ids)) != len(observation_ids)
    ):
        errors.append("physical.observation_ids")
    for index, observation in enumerate(observations):
        prefix = f"physical.{index}"
        observation_error_start = len(errors)
        if not isinstance(observation, dict):
            errors.append(f"{prefix}.object")
            continue
        reference = observation.get("acceptance")
        expected = observation.get("expected_r0_qualified")
        counts_toward_r0 = observation.get("counts_toward_r0")
        production_scope = observation.get("production_scope")
        if (
            not isinstance(reference, dict)
            or not isinstance(expected, bool)
            or not isinstance(counts_toward_r0, bool)
            or not isinstance(production_scope, bool)
        ):
            errors.append(f"{prefix}.contract")
            all_restored = False
            continue
        if counts_toward_r0 and not expected:
            errors.append(f"{prefix}.r0_counting_false_receipt")
        if counts_toward_r0 and not production_scope:
            errors.append(f"{prefix}.production_scope")
        if counts_toward_r0 and observation.get("kind") == "tpacket_breakthrough_acceptance":
            errors.append(f"{prefix}.diagnostic_not_countable")
        backend = observation.get("backend")
        if counts_toward_r0 and backend not in COUNTABLE_R0_BACKENDS:
            errors.append(f"{prefix}.backend")
        declared_hash = reference.get("sha256")
        if not valid_sha256(declared_hash):
            errors.append(f"{prefix}.declared_sha256")
            all_restored = False
            continue
        if receipt_root is None:
            errors.append(f"{prefix}.unverified")
            if counts_toward_r0:
                production_qualified.append(False)
            all_restored = False
            continue
        remote_path = str(reference.get("path", ""))
        if not remote_path.startswith("/"):
            errors.append(f"{prefix}.remote_path")
            all_restored = False
            continue
        try:
            local_path = resolve_remote_path(receipt_root, remote_path)
        except (ValueError, OSError):
            errors.append(f"{prefix}.path_escape")
            if counts_toward_r0:
                production_qualified.append(False)
            all_restored = False
            continue
        if not local_path.is_file() or local_path.stat().st_size == 0:
            errors.append(f"{prefix}.missing")
            if counts_toward_r0:
                production_qualified.append(False)
            all_restored = False
            continue
        actual_hash = sha256_file(local_path)
        hashes[f"physical.{observation.get('id', index)}"] = actual_hash
        if actual_hash != declared_hash:
            errors.append(f"{prefix}.sha256")
            if counts_toward_r0:
                production_qualified.append(False)
            all_restored = False
            continue
        try:
            receipt = load_json(local_path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            errors.append(f"{prefix}.json")
            all_restored = False
            continue
        kind = observation.get("kind")
        backend_selection: dict[str, Any] | None = None
        required_hash_entries: dict[str, str] = {}
        run_identity: str | None = None
        generator_identity: str | None = None
        hardware_identity: str | None = None
        selection_reference = observation.get("backend_selection")
        if counts_toward_r0:
            selection_contract_name = observation.get("contract")
            selection_contract = (
                configs.get(selection_contract_name)
                if isinstance(selection_contract_name, str)
                else None
            )
            selection_contract_reference = (
                config_references.get(selection_contract_name)
                if isinstance(selection_contract_name, str)
                else None
            )
            selection_contract_sha256 = (
                selection_contract_reference.get("sha256")
                if isinstance(selection_contract_reference, dict)
                else None
            )
            backend_selection = verify_remote_json_artifact(
                selection_reference,
                receipt_root,
                f"{prefix}.backend_selection",
                errors,
                hashes,
            )
            if backend_selection is not None:
                run_identity, generator_identity = validate_backend_selection(
                    backend_selection,
                    str(backend),
                    errors,
                    f"{prefix}.backend_selection",
                    contract=selection_contract,
                    contract_sha256=selection_contract_sha256,
                )
                if run_identity is not None and generator_identity is not None:
                    hardware_identity = backend_selection.get(
                        "hardware_identity_sha256"
                    )
                selection_inputs = backend_selection.get("input_sha256")
                if isinstance(selection_inputs, dict):
                    for name, digest in selection_inputs.items():
                        if isinstance(name, str) and valid_sha256(digest):
                            previous = required_hash_entries.get(name)
                            if previous is not None and previous != digest:
                                errors.append(
                                    f"{prefix}.backend_selection.input_sha256_collision"
                                )
                            required_hash_entries[name] = digest
            if isinstance(selection_reference, dict):
                selection_path_text = str(selection_reference.get("path", ""))
                selection_hash = selection_reference.get("sha256")
                try:
                    selection_path = resolve_remote_path(
                        receipt_root, selection_path_text
                    )
                    if selection_path.parent != local_path.parent:
                        errors.append(f"{prefix}.backend_selection.run_directory")
                    if valid_sha256(selection_hash):
                        required_hash_entries[selection_path.name] = selection_hash
                except (TypeError, ValueError, OSError):
                    errors.append(f"{prefix}.backend_selection.path")
        required_restoration_steps: set[str] | None = None
        if kind == "dpdk_release_acceptance":
            contract_name = observation.get("contract")
            contract = configs.get(contract_name) if isinstance(
                contract_name, str
            ) else None
            if isinstance(contract, dict):
                required_restoration_steps = DPDK_RESTORATION_STEPS | {
                    f"bind_{contract.get('capture_pci')}_bnx2x",
                    f"bind_{contract.get('replay_pci')}_bnx2x",
                    f"restore_{contract.get('capture_interface')}",
                    f"restore_{contract.get('replay_interface')}",
                }
        elif kind == "native_af_xdp_release_acceptance":
            required_restoration_steps = XDP_RESTORATION_STEPS
        evidence_reference = observation.get("evidence_manifest")
        if isinstance(evidence_reference, dict):
            try:
                evidence_path = resolve_remote_path(
                    receipt_root, str(evidence_reference.get("path", ""))
                )
                if evidence_path.parent != local_path.parent:
                    errors.append(f"{prefix}.evidence_manifest.run_directory")
            except (TypeError, ValueError, OSError):
                errors.append(f"{prefix}.evidence_manifest.path")
        manifest_verified, restoration_evidence_verified = (
            verify_remote_evidence_manifest(
            evidence_reference,
            receipt_root,
            f"{prefix}.evidence_manifest",
            errors,
            hashes,
            required_entries=(
                TPACKET_REQUIRED_EVIDENCE
                if kind == "tpacket_breakthrough_acceptance"
                else None
            ),
            require_release_inventory=kind
            in {"dpdk_release_acceptance", "native_af_xdp_release_acceptance"},
            receipt=receipt,
            required_hash_entries=required_hash_entries,
            required_restoration_steps=required_restoration_steps,
            )
        )
        if counts_toward_r0:
            raw_result_hash = required_hash_entries.get("result.json")
            raw_result_path = local_path.parent / "result.json"
            raw_result: dict[str, Any] | None = None
            if (
                not valid_sha256(raw_result_hash)
                or not raw_result_path.is_file()
                or sha256_file(raw_result_path) != raw_result_hash
            ):
                errors.append(f"{prefix}.raw_result.sha256")
            else:
                hashes[f"{prefix}.raw_result"] = raw_result_hash
                try:
                    raw_result = load_json(raw_result_path)
                except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                    errors.append(f"{prefix}.raw_result.json")
            if raw_result is not None:
                raw_contract_name = observation.get("contract")
                raw_contract = (
                    configs.get(raw_contract_name)
                    if isinstance(raw_contract_name, str)
                    else None
                )
                raw_contract_reference = (
                    config_references.get(raw_contract_name)
                    if isinstance(raw_contract_name, str)
                    else None
                )
                raw_contract_sha256 = (
                    raw_contract_reference.get("sha256")
                    if isinstance(raw_contract_reference, dict)
                    else None
                )
                validate_r0_raw_result(
                    raw_result,
                    str(backend),
                    raw_contract,
                    raw_contract_sha256,
                    policy,
                    errors,
                    f"{prefix}.raw_result",
                )
        if kind == "dpdk_release_acceptance":
            contract_name = observation.get("contract")
            contract = configs.get(contract_name) if isinstance(
                contract_name, str
            ) else None
            contract_reference = config_references.get(contract_name) if isinstance(
                contract_name, str
            ) else None
            contract_sha256 = (
                contract_reference.get("sha256")
                if isinstance(contract_reference, dict)
                else None
            )
            validate_dpdk_receipt(
                receipt,
                expected,
                errors,
                prefix,
                contract=contract,
                contract_sha256=contract_sha256,
                countable=counts_toward_r0,
                policy=policy,
            )
            rx_queue_count = (
                contract.get("rx_queue_count") if isinstance(contract, dict) else None
            )
            tx_queue_count = (
                contract.get("tx_queue_count") if isinstance(contract, dict) else None
            )
            if counts_toward_r0 and (
                backend != "dpdk_multiqueue_rss_tss"
                or not isinstance(contract, dict)
                or contract.get("expected_backend")
                != "dpdk_multiqueue_rss_tss"
                or contract.get("frozen") is not True
                or contract.get("diagnostic_only") is not False
                or not nonnegative_integer(rx_queue_count)
                or rx_queue_count < policy.get("required_r0_rx_queues", 8)
                or not nonnegative_integer(tx_queue_count)
                or tx_queue_count < policy.get("required_r0_tx_queues", 8)
                or contract.get("rss_required") is not True
                or contract.get("tss_required") is not True
                or contract.get("independent_generator_required") is not True
            ):
                errors.append(f"{prefix}.dpdk_production_contract")
        elif kind == "native_af_xdp_release_acceptance":
            contract_name = observation.get("contract")
            contract = configs.get(contract_name) if isinstance(
                contract_name, str
            ) else None
            contract_reference = config_references.get(contract_name) if isinstance(
                contract_name, str
            ) else None
            contract_sha256 = (
                contract_reference.get("sha256")
                if isinstance(contract_reference, dict)
                else None
            )
            if counts_toward_r0 and backend != "native_af_xdp_forced_zerocopy":
                errors.append(f"{prefix}.xdp_backend")
            validate_native_xdp_receipt(
                receipt,
                errors,
                prefix,
                contract=contract,
                contract_sha256=contract_sha256,
                policy=policy,
            )
        elif kind == "tpacket_breakthrough_acceptance":
            validate_tpacket_receipt(
                receipt,
                expected,
                errors,
                prefix,
                countable=counts_toward_r0,
                policy=policy,
            )
        else:
            errors.append(f"{prefix}.kind")
        observation_ok = (
            manifest_verified and len(errors) == observation_error_start
        )
        receipt_restored = receipt.get("restoration_verified") is True
        if kind in {"dpdk_release_acceptance", "native_af_xdp_release_acceptance"}:
            receipt_restored = receipt_restored and restoration_evidence_verified
        elif kind == "tpacket_breakthrough_acceptance":
            receipt_restored = receipt_restored and all(
                receipt.get(name) is True
                for name in (
                    "irq_restoration_verified",
                    "ring_restoration_verified",
                    "coalesce_restoration_verified",
                    "links_restored",
                    "pktgen_module_unloaded",
                )
            ) and receipt.get("runner_exit_status") == 0
        all_restored = all_restored and receipt_restored
        if counts_toward_r0:
            production_qualified.append(observation_ok and expected)
            production_paths.append(str(local_path.resolve()))
            production_receipt_hashes.append(actual_hash)
            manifest_hash = hashes.get(f"{prefix}.evidence_manifest")
            if isinstance(manifest_hash, str):
                production_manifest_hashes.append(manifest_hash)
            if isinstance(run_identity, str):
                production_run_identities.append(run_identity)
            if isinstance(generator_identity, str):
                production_generator_identities.append(generator_identity)
            if isinstance(hardware_identity, str):
                production_hardware_identities.append(hardware_identity)
            if isinstance(backend, str):
                production_backends.append(backend)
            contract_name = observation.get("contract")
            if isinstance(contract_name, str):
                production_contracts.append(contract_name)
    if production_qualified and not validate_r0_repeat_independence(
        len(production_qualified),
        production_paths,
        production_receipt_hashes,
        production_manifest_hashes,
        production_run_identities,
        production_generator_identities,
        production_hardware_identities,
        production_backends,
        production_contracts,
        errors,
    ):
        production_qualified.append(False)
    return (
        len(production_qualified) >= policy.get("required_r0_repeats", 3)
        and all(production_qualified),
        all_restored,
        hashes,
        identity_summary,
    )


def production_receipt_qualified(
    payload: dict[str, Any], candidate_id: str, prefix: str, errors: list[str]
) -> bool:
    before = len(errors)
    if payload.get("candidate_id") != candidate_id:
        errors.append(f"{prefix}.candidate_id")
    if payload.get("diagnostic_only") is not False:
        errors.append(f"{prefix}.diagnostic_scope")
    if payload.get("qualified") is not True:
        errors.append(f"{prefix}.qualified")
    if not isinstance(payload.get("run_bundle_identity"), str) or not payload.get(
        "run_bundle_identity"
    ):
        errors.append(f"{prefix}.run_bundle_identity")
    return len(errors) == before


def reject_unimplemented_stage_validator(prefix: str, errors: list[str]) -> bool:
    """Fail closed until a stage-specific raw-metric validator exists.

    R1--R4 receipts currently share only a generic envelope.  Candidate identity,
    a hash and a self-reported ``qualified`` flag are not sufficient evidence for
    a production stage, so no such receipt can promote the unified release.
    """

    errors.append(f"{prefix}.stage_validator_unimplemented")
    return False


def audit_stage_campaign(
    evidence: dict[str, Any],
    contract: StageContract | None,
    receipt_root: Path | None,
    errors: list[str],
    hashes: dict[str, str],
    *,
    physical_r0_qualified: bool = False,
    physical_identity_summary: dict[str, Any] | None = None,
    runtime_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    """Verify sealed R1--R4 receipts, then independently recompute all gates."""

    result: dict[str, Any] = {
        "qualified": False,
        "stage_qualified": {name: False for name in PRODUCTION_STAGES},
        "derived_production_pareto_metrics": None,
        "blockers": [],
    }
    campaign = evidence.get("stage_campaign")
    if not isinstance(campaign, dict) or campaign.get("status") != "qualified":
        errors.append("stage.campaign.pending")
        result["blockers"] = ["stage.campaign.pending"]
        return result
    if contract is None:
        errors.append("stage.campaign.contract_unverified")
        result["blockers"] = ["stage.campaign.contract_unverified"]
        return result
    references = campaign.get("receipts")
    if not isinstance(references, list):
        errors.append("stage.campaign.receipts")
        result["blockers"] = ["stage.campaign.receipts"]
        return result

    before = len(errors)
    identity_summary = physical_identity_summary or {}
    expected_backends = set(identity_summary.get("backends", []))
    expected_hardware = set(
        identity_summary.get("hardware_identity_sha256", [])
    )
    backend_binding = None
    dual_backend_identity = (
        "primary_backend" in identity_summary
        or "fallback_backend" in identity_summary
    )
    if dual_backend_identity:
        try:
            backend_binding = stage_backend_binding_from_r0_identity(
                identity_summary
            )
        except (TypeError, ValueError):
            backend_binding = None
    backend_identity_valid = (
        backend_binding is not None
        if dual_backend_identity
        else not (len(expected_backends) != 1)
    )
    if not (
        physical_r0_qualified
        and backend_identity_valid
        and len(expected_hardware) == 1
    ):
        errors.append("stage.campaign.physical_r0_binding")
    if not valid_sha256(runtime_manifest_sha256):
        errors.append("stage.campaign.runtime_manifest_binding")

    receipts: list[dict[str, Any]] = []
    declared_pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(references):
        prefix = f"stage.campaign.{index}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}.reference")
            continue
        declared_stage = item.get("stage")
        if declared_stage not in PRODUCTION_STAGES:
            errors.append(f"{prefix}.stage")
        receipt_ref = item.get("receipt")
        manifest_ref = item.get("evidence_manifest")
        receipt = verify_remote_json_artifact(
            receipt_ref, receipt_root, f"{prefix}.receipt", errors, hashes
        )
        manifest_verified, _ = verify_remote_evidence_manifest(
            manifest_ref,
            receipt_root,
            f"{prefix}.evidence_manifest",
            errors,
            hashes,
        )
        if not isinstance(receipt_ref, dict) or not isinstance(manifest_ref, dict):
            continue
        receipt_path = str(receipt_ref.get("path", ""))
        manifest_path = str(manifest_ref.get("path", ""))
        if (
            not receipt_path.startswith("/")
            or not manifest_path.startswith("/")
            or PurePosixPath(receipt_path).parent
            != PurePosixPath(manifest_path).parent
        ):
            errors.append(f"{prefix}.sealed_directory")
        pair = (receipt_path, manifest_path)
        if pair in declared_pairs:
            errors.append(f"{prefix}.duplicate_reference")
        declared_pairs.add(pair)
        if receipt is None:
            continue
        if receipt.get("stage") != declared_stage:
            errors.append(f"{prefix}.stage_binding")
        identity = receipt.get("identity")
        if (
            not isinstance(identity, dict)
            or identity.get("evidence_manifest_sha256")
            != manifest_ref.get("sha256")
        ):
            errors.append(f"{prefix}.evidence_manifest_binding")
        identity_binding = (
            (contract.payload.get("evidence_binding") or {})
            .get("identity_to_manifest_entry", {})
        )
        receipt_backend = receipt.get("backend")
        receipt_backend_role = receipt.get("backend_role")
        if isinstance(identity, dict):
            if identity.get("hardware_identity") not in expected_hardware:
                errors.append(f"{prefix}.hardware_identity_binding")
            runtime_is_live_primary = (
                backend_binding is None
                or receipt_backend_role == "primary"
            )
            if (
                runtime_is_live_primary
                and identity.get("runtime_manifest_sha256")
                != runtime_manifest_sha256
            ):
                errors.append(f"{prefix}.runtime_manifest_binding")
            required_hash_entries = {
                filename: identity.get(identity_field)
                for identity_field, filename in identity_binding.items()
                if valid_sha256(identity.get(identity_field))
            }
        else:
            required_hash_entries = {}
        if receipt_backend not in expected_backends:
            errors.append(f"{prefix}.backend_binding")
        if backend_binding is not None:
            expected_role_backends = {
                "primary": backend_binding["primary_backend"],
                "fallback": backend_binding["fallback_backend"],
            }
            if (
                receipt_backend_role not in expected_role_backends
                or receipt_backend
                != expected_role_backends.get(receipt_backend_role)
            ):
                errors.append(f"{prefix}.backend_role_binding")
        if (
            not isinstance(identity_binding, dict)
            or len(identity_binding) != 6
            or len(required_hash_entries) != len(identity_binding)
        ):
            errors.append(f"{prefix}.required_hash_entries")
        else:
            # Re-run the manifest verifier with the identity-bound required
            # entries.  This prevents a non-empty dummy file from standing in
            # for code, input, runtime, model, stage config and capture binary.
            manifest_verified, _ = verify_remote_evidence_manifest(
                manifest_ref,
                receipt_root,
                f"{prefix}.identity_evidence_manifest",
                errors,
                hashes,
                required_entries=set(required_hash_entries),
                required_hash_entries=required_hash_entries,
            )
        if manifest_verified:
            receipts.append(receipt)

    aggregated = aggregate_stage_evidence(
        receipts,
        contract,
        backend_binding=backend_binding,
    )
    for error in aggregated.get("errors", []):
        errors.append(f"stage.campaign.recompute.{error}")
    qualified = aggregated.get("qualified") is True and len(errors) == before
    result["qualified"] = qualified
    if qualified:
        result["stage_qualified"] = dict(aggregated["stage_qualified"])
        result["derived_production_pareto_metrics"] = aggregated[
            "derived_production_pareto_metrics"
        ]
    result["blockers"] = errors[before:]
    return result


def audit_production_evidence(
    manifest: dict[str, Any],
    release: dict[str, Any],
    receipt_root: Path | None,
    errors: list[str],
    hashes: dict[str, str],
    stage_contract: StageContract | None = None,
    physical_r0_qualified: bool = False,
    physical_identity_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = manifest.get("production_evidence")
    result = {name: False for name in ("runtime_identity", "resources", "key_flow", "fallback")}
    result.update({name: False for name in PRODUCTION_STAGES})
    result["derived_production_pareto_metrics"] = None
    result["stage_campaign_blockers"] = []
    if not isinstance(evidence, dict):
        errors.append("production_evidence.missing")
        return result
    candidate_id = str(manifest.get("candidate_id", ""))
    runtime_contract = release.get("runtime") or {}
    runtime = evidence.get("runtime_identity")
    if not isinstance(runtime, dict) or runtime.get("status") != "verified":
        errors.append("runtime_identity.unverified")
    elif not valid_sha256(runtime.get("expected_manifest_sha256")):
        errors.append("runtime_identity.expected_manifest_sha256")
    else:
        runtime_manifest = verify_remote_json_artifact(
            {
                "path": runtime.get("expected_manifest_path"),
                "sha256": runtime.get("expected_manifest_sha256"),
            },
            receipt_root,
            "runtime_identity.manifest",
            errors,
            hashes,
        )
        live_probe = verify_remote_json_artifact(
            runtime.get("live_identity_probe"),
            receipt_root,
            "runtime_identity.live_probe",
            errors,
            hashes,
        )
        before = len(errors)
        if runtime_manifest is not None:
            expected_runtime_fields = {
                "candidate_id": candidate_id,
                "runtime_candidate": runtime_contract.get("runtime_candidate"),
                "prediction_execution": runtime_contract.get(
                    "prediction_execution"
                ),
                "model_n_jobs": runtime_contract.get("model_n_jobs"),
            }
            for name, expected in expected_runtime_fields.items():
                if runtime_manifest.get(name) != expected:
                    errors.append(f"runtime_identity.manifest.{name}")
            if runtime_manifest.get("bind") != "0.0.0.0:50051":
                errors.append("runtime_identity.manifest.bind")
            if runtime_manifest.get("connect") != "10.0.5.8:50052":
                errors.append("runtime_identity.manifest.connect")
            if not isinstance(runtime_manifest.get("pid"), int) or isinstance(
                runtime_manifest.get("pid"), bool
            ):
                errors.append("runtime_identity.manifest.pid")
        if live_probe is not None:
            if live_probe.get("candidate_id") != candidate_id:
                errors.append("runtime_identity.live_probe.candidate_id")
            if live_probe.get("runtime_candidate") != runtime_contract.get(
                "runtime_candidate"
            ):
                errors.append("runtime_identity.live_probe.runtime_candidate")
            if live_probe.get("runtime_manifest_sha256") != runtime.get(
                "expected_manifest_sha256"
            ):
                errors.append("runtime_identity.live_probe.manifest_sha256")
            for name in (
                "process_alive",
                "listener_owned_by_process_tree",
                "protocol_health_ok",
                "rust_reverse_connection_healthy",
            ):
                if live_probe.get(name) is not True:
                    errors.append(f"runtime_identity.live_probe.{name}")
        result["runtime_identity"] = (
            runtime_manifest is not None
            and live_probe is not None
            and len(errors) == before
        )
    campaign = audit_stage_campaign(
        evidence,
        stage_contract,
        receipt_root,
        errors,
        hashes,
        physical_r0_qualified=physical_r0_qualified,
        physical_identity_summary=physical_identity_summary,
        runtime_manifest_sha256=(
            runtime.get("expected_manifest_sha256")
            if result["runtime_identity"] and isinstance(runtime, dict)
            else None
        ),
    )
    result.update(campaign["stage_qualified"])
    # The raw stage campaign owns these gates because it proves they overlap
    # the same sealed run.  Legacy summary artifacts remain non-authoritative.
    result["resources"] = all(
        campaign["stage_qualified"][name]
        for name in ("r3", "r4_24h", "r4_72h")
    )
    result["key_flow"] = all(
        campaign["stage_qualified"][name]
        for name in ("r2", "r3", "r4_24h", "r4_72h")
    )
    result["fallback"] = all(
        campaign["stage_qualified"][name]
        for name in ("r3", "r4_24h", "r4_72h")
    )
    result["derived_production_pareto_metrics"] = campaign[
        "derived_production_pareto_metrics"
    ]
    result["stage_campaign_blockers"] = campaign["blockers"]
    return result


def audit_manifest(
    manifest_path: Path,
    manifest: dict[str, Any],
    receipt_root: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    evidence_hashes: dict[str, str] = {}
    if manifest.get("schema_version") != 2:
        errors.append("manifest.schema_version")
    if manifest.get("scope") != "hft_mgbs_unified_release_manifest":
        errors.append("manifest.scope")
    algorithm_id = manifest.get("candidate_id")
    if (
        not isinstance(algorithm_id, str)
        or not algorithm_id
        or any(character in algorithm_id for character in "\r\n\x00")
    ):
        errors.append("manifest.candidate_id")
    deployment_candidate_id = manifest.get("deployment_candidate_id")
    if (
        not isinstance(deployment_candidate_id, str)
        or not deployment_candidate_id
        or any(character in deployment_candidate_id for character in "\r\n\x00")
    ):
        errors.append("manifest.deployment_candidate_id")
    policy = manifest.get("audit_policy") or {}
    if policy.get("hard_constraints_before_pareto") is not True:
        errors.append("manifest.hard_constraints_before_pareto")
    if policy.get("normal_and_fallback_must_be_paired") is not True:
        errors.append("manifest.normal_fallback_pairing")
    if policy.get("required_r0_repeats") != 3:
        errors.append("manifest.required_r0_repeats")
    if policy.get("required_r0_target_mpps") != 12.0:
        errors.append("manifest.required_r0_target_mpps")
    if policy.get("required_r0_full_windows") != 15:
        errors.append("manifest.required_r0_full_windows")
    if policy.get("backend_priority") != EXPECTED_BACKEND_PRIORITY:
        errors.append("manifest.backend_priority")
    if policy.get("countable_r0_backends") != EXPECTED_BACKEND_PRIORITY[:2]:
        errors.append("manifest.countable_r0_backends")
    if policy.get("dpdk_requires_xdp_fallback_proof") is not True:
        errors.append("manifest.dpdk_requires_xdp_fallback_proof")
    if policy.get("required_independent_generator") is not True:
        errors.append("manifest.required_independent_generator")
    if policy.get("required_r0_rx_queues") != 8:
        errors.append("manifest.required_r0_rx_queues")
    if policy.get("required_r0_tx_queues") != 8:
        errors.append("manifest.required_r0_tx_queues")
    if policy.get("required_stages") != [
        "r0", "r1", "r2", "r3", "r4_24h", "r4_72h"
    ]:
        errors.append("manifest.required_stages")

    configs, config_hashes = verify_config_artifacts(manifest_path, manifest, errors)
    evidence_hashes.update(config_hashes)
    algorithm_campaign = verify_algorithm_campaign_gate(
        ROOT,
        manifest.get("algorithm_campaign_gate"),
        reference_base=manifest_path.parent,
        remote_artifact_root=receipt_root,
    )
    for error in algorithm_campaign["errors"]:
        add_once(errors, error)
    for name in ("contract", "receipt", "projection"):
        value = algorithm_campaign.get(name + "_sha256")
        if value is not None:
            evidence_hashes["algorithm_campaign." + name] = value
    target_order = (configs.get("ten_mpps_target") or {}).get("backend_order")
    if (
        not isinstance(target_order, list)
        or not target_order
        or target_order[0] != "af_xdp_native_zero_copy_on_capable_nic"
    ):
        errors.append("capture.backend_order")
    algorithm_qualified = False
    offline_quality_qualified = False
    capture_contract_qualified = False
    if all(
        name in configs
        for name in (
            "algorithm_search",
            "algorithm_optimality_audit",
            "release_candidate",
        )
    ):
        algorithm_qualified, offline_quality_qualified = audit_algorithm(
            configs["algorithm_search"],
            configs["release_candidate"],
            configs["algorithm_optimality_audit"],
            errors,
            algorithm_campaign,
        )
    if "capture_search" in configs and "hardware_gate" in configs:
        capture_contract_qualified = audit_capture_configs(
            configs["capture_search"], configs["hardware_gate"], errors
        )
    capture_search = configs.get("capture_search") or {}
    capture_backend_feasible_set_empty = (
        (capture_search.get("pareto_result") or {}).get(
            "final_production_pareto_exists"
        )
        is False
    )

    campaign_bridge = manifest.get("new_nic_r0_campaign")
    legacy_countable = any(
        isinstance(item, dict) and item.get("counts_toward_r0") is True
        for item in (manifest.get("physical_observations") or [])
    )
    if campaign_bridge is not None and legacy_countable:
        errors.append("physical.r0_double_counting")
        physical_r0_qualified = False
        host_restore_qualified = False
        physical_hashes = {}
        physical_identity_summary = {
            "run_bundle_identities": [],
            "generator_run_identities": [],
            "hardware_identity_sha256": [],
            "backends": [],
            "contracts": [],
        }
    elif campaign_bridge is not None:
        physical_hashes = {}
        (
            physical_r0_qualified,
            host_restore_qualified,
            physical_identity_summary,
        ) = audit_new_nic_r0_campaign(
            campaign_bridge,
            configs.get("new_nic_r0_trust_profile") or {},
            receipt_root,
            errors,
            physical_hashes,
        )
    else:
        (
            physical_r0_qualified,
            host_restore_qualified,
            physical_hashes,
            physical_identity_summary,
        ) = audit_physical_observations(manifest, configs, receipt_root, errors)
    evidence_hashes.update(physical_hashes)
    stage_contract = None
    if "production_stage_contract" in configs:
        stage_reference = (manifest.get("config_artifacts") or {}).get(
            "production_stage_contract"
        ) or {}
        stage_contract_hash = config_hashes.get("config.production_stage_contract")
        if valid_sha256(stage_contract_hash):
            stage_contract = StageContract(
                configs["production_stage_contract"],
                stage_contract_hash,
                resolve_config_path(manifest_path, stage_reference),
            )
    production = audit_production_evidence(
        manifest,
        configs.get("release_candidate") or {},
        receipt_root,
        errors,
        evidence_hashes,
        stage_contract,
        physical_r0_qualified,
        physical_identity_summary,
    )
    evidence_integrity_qualified = not any(
        error.startswith("config.")
        or error.startswith("algorithm_campaign.")
        or error.startswith("physical.")
        or error.startswith("runtime_identity.")
        or error.startswith("stage.")
        for error in errors
    )
    r_stages_qualified = all(production[name] for name in PRODUCTION_STAGES)
    full_pipeline_qualified = (
        physical_r0_qualified
        and production["resources"]
        and production["key_flow"]
        and production["fallback"]
        and production["runtime_identity"]
        and host_restore_qualified
        and r_stages_qualified
    )
    derived_metrics = production["derived_production_pareto_metrics"]
    normalized_metrics = None
    if full_pipeline_qualified:
        if not isinstance(derived_metrics, dict):
            errors.append("candidate.derived_production_pareto_metrics")
        elif derived_metrics.get("name") != algorithm_id:
            errors.append("candidate.derived_production_pareto_metrics.name")
        else:
            normalized_metrics = dict(derived_metrics)
            normalized_metrics["name"] = deployment_candidate_id

    provisional_candidate_evidence_accepted = (
        evidence_integrity_qualified
        and algorithm_campaign["qualified"] is True
        and algorithm_campaign.get("winner") == algorithm_id
        and algorithm_qualified
        and offline_quality_qualified
        and capture_contract_qualified
        and full_pipeline_qualified
        and normalized_metrics is not None
        and not errors
    )
    claims = manifest.get("claimed_final_state") or {}
    expected_claims = {
        "candidate_evidence_accepted": provisional_candidate_evidence_accepted,
        "production_release_accepted": False,
        "full_pipeline_qualified": full_pipeline_qualified,
        "final_pareto_eligible": False,
        "final_pareto_ingestion_allowed": provisional_candidate_evidence_accepted,
    }
    claims_match = True
    for name, expected in expected_claims.items():
        if claims.get(name) is not expected:
            errors.append(f"manifest.claim.{name}")
            claims_match = False
    candidate_evidence_accepted = (
        provisional_candidate_evidence_accepted and claims_match and not errors
    )

    return {
        "schema_version": 1,
        "scope": "hft_mgbs_unified_candidate_evidence_audit",
        "release_id": manifest.get("release_id"),
        "candidate_id": deployment_candidate_id,
        "algorithm_id": algorithm_id,
        "input_manifest_sha256": sha256_file(manifest_path),
        "audit_complete": True,
        "offline_algorithm_candidate_accepted": offline_quality_qualified,
        "algorithm_search_qualified": algorithm_qualified,
        "algorithm_campaign_qualified": algorithm_campaign["qualified"],
        "algorithm_campaign_winner": algorithm_campaign["winner"],
        "capture_contract_qualified": capture_contract_qualified,
        "capture_backend_feasible_set_empty": capture_backend_feasible_set_empty,
        "physical_r0_qualified": physical_r0_qualified,
        "physical_r0_identity_summary": physical_identity_summary,
        "resource_qualified": production["resources"],
        "key_flow_qualified": production["key_flow"],
        "fallback_qualified": production["fallback"],
        "runtime_identity_current": production["runtime_identity"],
        "host_restoration_qualified": host_restore_qualified,
        "r1_qualified": production["r1"],
        "r2_qualified": production["r2"],
        "r3_qualified": production["r3"],
        "r4_24h_qualified": production["r4_24h"],
        "r4_72h_qualified": production["r4_72h"],
        "evidence_integrity_qualified": evidence_integrity_qualified,
        "full_pipeline_qualified": full_pipeline_qualified,
        "feasible_candidates": [],
        "pareto_front": [],
        "selected_candidate": None,
        "selection_performed": False,
        "selected_on_full_pipeline_pareto": False,
        "candidate_evidence_accepted": candidate_evidence_accepted,
        "pareto_ingestion_qualified": candidate_evidence_accepted,
        "production_release_accepted": False,
        "derived_production_pareto_metrics": normalized_metrics,
        "derived_production_pareto_metrics_available": (
            normalized_metrics is not None and r_stages_qualified
        ),
        "derived_production_pareto_metrics_blockers": production[
            "stage_campaign_blockers"
        ],
        "accepted": False,
        "final_pareto_eligible": False,
        "final_pareto_ingestion_allowed": candidate_evidence_accepted,
        "errors": errors,
        "warnings": warnings,
        "evidence_sha256": evidence_hashes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--receipt-root",
        type=Path,
        help=(
            "mirror root for absolute remote receipt paths; omitted receipts "
            "are intentionally reported unverified"
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        manifest = load_json(args.manifest)
        result = audit_manifest(args.manifest, manifest, args.receipt_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        result = {
            "schema_version": 1,
            "scope": "hft_mgbs_unified_candidate_evidence_audit",
            "audit_complete": False,
            "candidate_evidence_accepted": False,
            "production_release_accepted": False,
            "accepted": False,
            "full_pipeline_qualified": False,
            "final_pareto_eligible": False,
            "final_pareto_ingestion_allowed": False,
            "errors": [f"audit_input:{type(error).__name__}:{error}"],
        }
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    if not result.get("audit_complete"):
        return 3
    return 0 if result.get("candidate_evidence_accepted") else 2


if __name__ == "__main__":
    raise SystemExit(main())
