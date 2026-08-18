"""Fail-closed acceptance logic for a newly installed high-speed capture NIC.

The module is deliberately independent from the legacy bnx2x runners.  It only
evaluates inventory and immutable probe receipts; it never changes a PF, loads
an XDP program, or binds a DPDK driver.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def canonical_sha256(value: Any) -> str:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def receipt_content_sha256(receipt: Mapping[str, Any]) -> str:
    """Hash a receipt without its self-hash field."""

    return canonical_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_finite_number(value: Any) -> bool:
    return _is_number(value) and (
        not isinstance(value, float)
        or (value == value and value not in (float("inf"), float("-inf")))
    )


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _int_at_least(value: Any, minimum: int) -> bool:
    return _is_nonnegative_int(value) and value >= minimum


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and "\n" not in value


def _utc(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_contract(contract: Mapping[str, Any]) -> List[str]:
    """Return contract errors.  An empty list means the contract is usable."""

    errors: List[str] = []
    if contract.get("schema_version") != 1:
        errors.append("contract.schema_version")
    if contract.get("frozen") is not True:
        errors.append("contract.not_frozen")
    if not _nonempty(contract.get("contract_id")):
        errors.append("contract.contract_id")

    for section in (
        "hardware_identity",
        "management_plane",
        "pcie",
        "numa",
        "driver_firmware_ddp",
        "native_xdp_af_xdp",
        "dpdk_multiqueue",
        "independent_generator",
        "mutation_authorization",
    ):
        if not isinstance(contract.get(section), Mapping):
            errors.append("contract.missing_section." + section)

    hardware = contract.get("hardware_identity", {})
    excluded = hardware.get("excluded_pci_addresses")
    if not isinstance(excluded, list) or not all(_nonempty(item) for item in excluded):
        errors.append("contract.hardware_identity.excluded_pci_addresses")
    excluded_ids = hardware.get("excluded_vendor_device_ids")
    if not isinstance(excluded_ids, list) or not all(
        isinstance(item, str) and re.fullmatch(r"[0-9a-f]{4}:[0-9a-f]{4}", item)
        for item in excluded_ids
    ):
        errors.append("contract.hardware_identity.excluded_vendor_device_ids")
    if not isinstance(hardware.get("candidate_ports_min"), int):
        errors.append("contract.hardware_identity.candidate_ports_min")

    pcie = contract.get("pcie", {})
    for name in ("current_width_min", "current_speed_gtps_min"):
        if not _is_finite_number(pcie.get(name)) or pcie.get(name) <= 0:
            errors.append("contract.pcie." + name)

    numa = contract.get("numa", {})
    if not isinstance(numa.get("worker_cpu_count_min"), int) or numa.get(
        "worker_cpu_count_min", 0
    ) < 1:
        errors.append("contract.numa.worker_cpu_count_min")

    xdp = contract.get("native_xdp_af_xdp", {})
    if xdp.get("attach_mode_required") != "native":
        errors.append("contract.native_xdp_af_xdp.attach_mode_required")
    if xdp.get("xsk_bind_mode_required") != "forced_zerocopy":
        errors.append("contract.native_xdp_af_xdp.xsk_bind_mode_required")
    if xdp.get("copy_fallback_allowed") is not False:
        errors.append("contract.native_xdp_af_xdp.copy_fallback_allowed")
    if (
        not _is_finite_number(xdp.get("min_active_queue_share"))
        or not 0 < xdp.get("min_active_queue_share") <= 1
    ):
        errors.append("contract.native_xdp_af_xdp.min_active_queue_share")

    dpdk = contract.get("dpdk_multiqueue", {})
    for name in ("rx_queues_min", "tx_queues_min"):
        if not isinstance(dpdk.get(name), int) or dpdk.get(name, 0) < 8:
            errors.append("contract.dpdk_multiqueue." + name)
    if dpdk.get("rss_required") is not True:
        errors.append("contract.dpdk_multiqueue.rss_required")
    if dpdk.get("tss_required") is not True:
        errors.append("contract.dpdk_multiqueue.tss_required")
    if (
        not _is_finite_number(dpdk.get("min_active_queue_share"))
        or not 0 < dpdk.get("min_active_queue_share") <= 1
    ):
        errors.append("contract.dpdk_multiqueue.min_active_queue_share")

    auth = contract.get("mutation_authorization", {})
    if not _nonempty(auth.get("environment_variable")):
        errors.append("contract.mutation_authorization.environment_variable")
    if not _nonempty(auth.get("exact_value")):
        errors.append("contract.mutation_authorization.exact_value")
    if auth.get("default_mode") != "read_only":
        errors.append("contract.mutation_authorization.default_mode")
    if auth.get("restore_required") is not True:
        errors.append("contract.mutation_authorization.restore_required")
    return sorted(set(errors))


def _check(
    checks: List[Dict[str, Any]],
    blockers: List[str],
    pending: List[str],
    name: str,
    condition: Optional[bool],
    detail: Any,
) -> None:
    if condition is None:
        state = "pending"
        pending.append(name)
    elif condition:
        state = "pass"
    else:
        state = "fail"
        blockers.append(name)
    checks.append({"id": name, "state": state, "detail": detail})


def _port_map(items: Any, key: str) -> Dict[str, Mapping[str, Any]]:
    if not isinstance(items, list):
        return {}
    result: Dict[str, Mapping[str, Any]] = {}
    for item in items:
        if isinstance(item, Mapping) and _nonempty(item.get(key)):
            result[str(item[key])] = item
    return result


def _receipt_identity_ok(
    receipt: Mapping[str, Any], host_id: Any, pci_addresses: Sequence[str]
) -> bool:
    receipt_pci = receipt.get("pci_addresses")
    return (
        _nonempty(host_id)
        and receipt.get("capture_host_id") == host_id
        and isinstance(receipt_pci, list)
        and sorted(receipt_pci) == sorted(pci_addresses)
        and len(receipt_pci) == len(set(receipt_pci))
        and _nonempty(receipt.get("run_id"))
        and _is_sha256(receipt.get("receipt_sha256"))
        and receipt.get("receipt_sha256") == receipt_content_sha256(receipt)
        and _is_sha256(receipt.get("probe_binary_sha256"))
        and _utc(receipt.get("started_at_utc")) is not None
        and _utc(receipt.get("completed_at_utc")) is not None
        and _utc(receipt.get("completed_at_utc"))
        > _utc(receipt.get("started_at_utc"))
    )


def restoration_fingerprint(inventory: Mapping[str, Any]) -> Dict[str, Any]:
    """Return only identity/control-plane fields that must survive a probe."""

    management = inventory.get("management_plane")
    if not isinstance(management, Mapping):
        management = {}
    candidates = inventory.get("candidate_ports")
    if not isinstance(candidates, list):
        candidates = []
    ports: List[Dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        ports.append(
            {
                "interface": candidate.get("interface"),
                "pci_address": candidate.get("pci_address"),
                "vendor_id": candidate.get("vendor_id"),
                "device_id": candidate.get("device_id"),
                "kernel_driver": candidate.get("kernel_driver"),
                "master": candidate.get("master"),
                "ip_addresses": sorted(candidate.get("ip_addresses") or []),
                "default_route": candidate.get("default_route"),
                "carrier": candidate.get("carrier"),
                "operstate": candidate.get("operstate"),
                "link_speed_mbps": candidate.get("link_speed_mbps"),
                "numa_node": candidate.get("numa_node"),
                "pcie_current_width": candidate.get("pcie_current_width"),
                "pcie_current_speed_gtps": candidate.get("pcie_current_speed_gtps"),
                "restoration_state": candidate.get("restoration_state"),
            }
        )
    ports.sort(key=lambda item: (str(item["pci_address"]), str(item["interface"])))
    return {
        "capture_host_id": inventory.get("capture_host_id"),
        "management_interfaces_present": sorted(
            management.get("interfaces_present") or []
        ),
        "default_route_interfaces": sorted(
            management.get("default_route_interfaces") or []
        ),
        "lower_to_master": dict(sorted((management.get("lower_to_master") or {}).items())),
        "candidate_ports": ports,
        "host_restoration_state": inventory.get("host_restoration_state"),
    }


def compare_restoration(
    before: Mapping[str, Any], after: Mapping[str, Any]
) -> Dict[str, Any]:
    before_fingerprint = restoration_fingerprint(before)
    after_fingerprint = restoration_fingerprint(after)
    return {
        "verified": before_fingerprint == after_fingerprint,
        "before_sha256": canonical_sha256(before_fingerprint),
        "after_sha256": canonical_sha256(after_fingerprint),
        "before": before_fingerprint,
        "after": after_fingerprint,
    }


def evaluate_inventory(
    inventory: Mapping[str, Any],
    contract: Mapping[str, Any],
    baseline_inventory: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Recompute the frozen new-NIC preflight decision from raw inventory."""

    contract_errors = validate_contract(contract)
    if contract_errors:
        return {
            "schema_version": 1,
            "scope": "new_high_speed_nic_acceptance_preflight",
            "status": "invalid_contract",
            "contract_errors": contract_errors,
            "checks": [],
            "blockers": contract_errors,
            "pending": [],
            "hardware_present": False,
            "inventory_ready_for_authorized_probes": False,
            "read_only_preflight_qualified": False,
            "self_consistent_capability_receipts_valid": False,
            "receipt_trust_level": "not_established",
            "production_qualified": False,
            "final_pareto_ingestion_allowed": False,
            "mutations_performed": False,
        }

    checks: List[Dict[str, Any]] = []
    blockers: List[str] = []
    pending: List[str] = []
    inventory_invalid = not (
        inventory.get("schema_version") == 1
        and inventory.get("scope") == "new_high_speed_nic_inventory"
        and inventory.get("collection_mode") == "read_only"
        and inventory.get("mutations_performed") is False
        and _utc(inventory.get("captured_at_utc")) is not None
        and _nonempty(inventory.get("capture_host_id"))
    )
    _check(
        checks,
        blockers,
        pending,
        "inventory.envelope",
        not inventory_invalid,
        {
            "schema_version": inventory.get("schema_version"),
            "scope": inventory.get("scope"),
            "collection_mode": inventory.get("collection_mode"),
            "mutations_performed": inventory.get("mutations_performed"),
        },
    )
    candidates_raw = inventory.get("candidate_ports")
    if not isinstance(candidates_raw, list):
        _check(checks, blockers, pending, "inventory.candidate_ports", False, "not_list")
        candidates: List[Mapping[str, Any]] = []
        inventory_invalid = True
    else:
        candidates = [item for item in candidates_raw if isinstance(item, Mapping)]
        inventory_invalid = inventory_invalid or len(candidates) != len(candidates_raw)
        _check(
            checks,
            blockers,
            pending,
            "inventory.candidate_ports",
            not inventory_invalid,
            {"declared": len(candidates_raw), "structured": len(candidates)},
        )

    hardware_present = bool(candidates)
    if not hardware_present and not inventory_invalid:
        _check(
            checks,
            blockers,
            pending,
            "hardware.candidate_not_present",
            None,
            "install a non-excluded dedicated capture adapter",
        )

    hardware = contract["hardware_identity"]
    excluded_pci = set(hardware["excluded_pci_addresses"])
    excluded_vendor_devices = set(hardware["excluded_vendor_device_ids"])
    min_ports = int(hardware["candidate_ports_min"])
    max_ports = int(hardware.get("candidate_ports_max", 64))
    if hardware_present:
        _check(
            checks,
            blockers,
            pending,
            "hardware.port_count",
            min_ports <= len(candidates) <= max_ports,
            {"actual": len(candidates), "min": min_ports, "max": max_ports},
        )

    interfaces = [item.get("interface") for item in candidates]
    pci_addresses = [item.get("pci_address") for item in candidates]
    serials = [item.get("adapter_serial") for item in candidates]
    identities_valid = bool(candidates) and all(
        _nonempty(value) for value in interfaces + pci_addresses + serials
    )
    if hardware_present:
        _check(
            checks,
            blockers,
            pending,
            "hardware.identity_complete_unique",
            identities_valid
            and len(set(interfaces)) == len(interfaces)
            and len(set(pci_addresses)) == len(pci_addresses),
            {"interfaces": interfaces, "pci_addresses": pci_addresses, "serials": serials},
        )
        _check(
            checks,
            blockers,
            pending,
            "hardware.preexisting_pci_excluded",
            all(item not in excluded_pci for item in pci_addresses),
            {"excluded": sorted(excluded_pci), "observed": pci_addresses},
        )
        vendor_devices = [
            "{}:{}".format(item.get("vendor_id"), item.get("device_id"))
            for item in candidates
        ]
        _check(
            checks,
            blockers,
            pending,
            "hardware.preexisting_device_id_excluded",
            all(
                re.fullmatch(r"[0-9a-f]{4}:[0-9a-f]{4}", item) is not None
                and item not in excluded_vendor_devices
                for item in vendor_devices
            ),
            {"excluded": sorted(excluded_vendor_devices), "observed": vendor_devices},
        )

    management_contract = contract["management_plane"]
    management = inventory.get("management_plane")
    if not isinstance(management, Mapping):
        management = {}
        inventory_invalid = True
    excluded_interfaces = set(management_contract["capture_excluded_interfaces"])
    if hardware_present:
        _check(
            checks,
            blockers,
            pending,
            "management.capture_interface_isolation",
            all(
                item.get("interface") not in excluded_interfaces
                and item.get("master") in (None, "")
                and item.get("default_route") is False
                and item.get("ip_addresses") == []
                for item in candidates
            ),
            {"excluded_interfaces": sorted(excluded_interfaces)},
        )
    required_lower = management_contract["required_lower_interface"]
    required_master = management_contract["required_master_interface"]
    required_default = management_contract["required_default_route_interface"]
    interfaces_present = management.get("interfaces_present") or []
    lower_to_master = management.get("lower_to_master") or {}
    default_routes = management.get("default_route_interfaces") or []
    _check(
        checks,
        blockers,
        pending,
        "management.control_plane_present",
        isinstance(interfaces_present, list)
        and required_lower in interfaces_present
        and required_master in interfaces_present
        and isinstance(lower_to_master, Mapping)
        and lower_to_master.get(required_lower) == required_master
        and isinstance(default_routes, list)
        and required_default in default_routes,
        {
            "required_lower": required_lower,
            "required_master": required_master,
            "required_default_route": required_default,
        },
    )

    pcie_contract = contract["pcie"]
    if hardware_present:
        pcie_ok = all(
            _is_finite_number(item.get("pcie_current_width"))
            and item.get("pcie_current_width") >= pcie_contract["current_width_min"]
            and _is_finite_number(item.get("pcie_current_speed_gtps"))
            and item.get("pcie_current_speed_gtps")
            >= pcie_contract["current_speed_gtps_min"]
            and (
                pcie_contract.get("require_not_degraded") is not True
                or (
                    _is_finite_number(item.get("pcie_max_width"))
                    and item.get("pcie_current_width") >= item.get("pcie_max_width")
                    and _is_finite_number(item.get("pcie_max_speed_gtps"))
                    and item.get("pcie_current_speed_gtps")
                    >= item.get("pcie_max_speed_gtps")
                )
            )
            for item in candidates
        )
        _check(
            checks,
            blockers,
            pending,
            "pcie.link_width_speed",
            pcie_ok,
            {
                "min_width": pcie_contract["current_width_min"],
                "min_speed_gtps": pcie_contract["current_speed_gtps_min"],
                "require_not_degraded": pcie_contract.get("require_not_degraded"),
            },
        )

    link_speed_min = hardware["capture_link_speed_mbps_min"]
    if hardware_present:
        _check(
            checks,
            blockers,
            pending,
            "hardware.capture_links_up",
            all(
                item.get("physical") is True
                and item.get("carrier") == 1
                and item.get("operstate") == "up"
                and _is_finite_number(item.get("link_speed_mbps"))
                and item.get("link_speed_mbps") >= link_speed_min
                for item in candidates
            ),
            {"minimum_speed_mbps": link_speed_min},
        )

    numa_contract = contract["numa"]
    worker_plan = inventory.get("worker_cpu_plan")
    if not isinstance(worker_plan, Mapping):
        worker_plan = {}
        inventory_invalid = True
    worker_cpus = worker_plan.get("cpus")
    worker_nodes = worker_plan.get("numa_nodes")
    port_nodes = [item.get("numa_node") for item in candidates]
    if hardware_present:
        numa_ok = (
            all(isinstance(node, int) and not isinstance(node, bool) and node >= 0 for node in port_nodes)
            and len(set(port_nodes)) == 1
            and isinstance(worker_cpus, list)
            and len(worker_cpus) >= numa_contract["worker_cpu_count_min"]
            and len(worker_cpus) == len(set(worker_cpus))
            and isinstance(worker_nodes, list)
            and len(worker_nodes) == len(worker_cpus)
            and set(worker_nodes) == set(port_nodes)
        )
        _check(
            checks,
            blockers,
            pending,
            "numa.local_worker_plan",
            numa_ok,
            {
                "port_nodes": port_nodes,
                "worker_cpus": worker_cpus,
                "worker_nodes": worker_nodes,
                "minimum_workers": numa_contract["worker_cpu_count_min"],
            },
        )

    queue_contract = contract["dpdk_multiqueue"]
    if hardware_present:
        queue_ok = True
        queue_details = []
        for item in candidates:
            queues = item.get("queue_capabilities")
            if not isinstance(queues, Mapping):
                queue_ok = False
                queue_details.append(None)
                continue
            combined = queues.get("max_combined")
            raw_rx = queues.get("max_rx")
            raw_tx = queues.get("max_tx")
            if not all(
                _is_nonnegative_int(value) for value in (combined, raw_rx, raw_tx)
            ):
                queue_ok = False
                queue_details.append(
                    {"max_rx": raw_rx, "max_tx": raw_tx, "max_combined": combined}
                )
                continue
            max_rx = max(raw_rx, combined)
            max_tx = max(raw_tx, combined)
            queue_ok = queue_ok and (
                _int_at_least(max_rx, queue_contract["rx_queues_min"])
                and _int_at_least(max_tx, queue_contract["tx_queues_min"])
            )
            queue_details.append({"effective_rx": max_rx, "effective_tx": max_tx})
        _check(
            checks,
            blockers,
            pending,
            "queues.advertised_capacity",
            queue_ok,
            queue_details,
        )

    stack_contract = contract["driver_firmware_ddp"]
    stack = inventory.get("stack_attestation")
    stack_ports = _port_map(stack.get("ports") if isinstance(stack, Mapping) else None, "pci_address")
    if hardware_present:
        stack_ok = (
            isinstance(stack, Mapping)
            and stack.get("compatibility_verified") is True
            and _nonempty(stack.get("compatibility_source"))
            and _is_sha256(stack.get("compatibility_matrix_sha256"))
            and _nonempty(stack.get("kernel_release"))
            and _nonempty(stack.get("dpdk_version"))
        )
        for item in candidates:
            attested = stack_ports.get(str(item.get("pci_address")), {})
            stack_ok = bool(stack_ok) and (
                attested.get("compatible") is True
                and attested.get("kernel_driver") == item.get("kernel_driver")
                and attested.get("driver_version") == item.get("driver_version")
                and attested.get("firmware_version") == item.get("firmware_version")
                and _nonempty(attested.get("ddp_package"))
                and _nonempty(attested.get("ddp_version"))
                and _nonempty(attested.get("ddp_profile"))
                and _is_sha256(attested.get("ddp_sha256"))
                and attested.get("native_xdp_driver_supported") is True
                and attested.get("af_xdp_zerocopy_driver_supported") is True
                and attested.get("dpdk_rss_supported") is True
                and attested.get("dpdk_tss_supported") is True
                and _nonempty(attested.get("dpdk_pmd"))
                and _nonempty(attested.get("capability_source"))
                and _is_sha256(attested.get("capability_evidence_sha256"))
            )
        _check(
            checks,
            blockers,
            pending,
            "stack.driver_firmware_ddp_compatibility",
            stack_ok,
            {"attested_pci_addresses": sorted(stack_ports), "required": pci_addresses},
        )

    host_id = inventory.get("capture_host_id")
    generator = inventory.get("independent_generator")
    generator_contract = contract["independent_generator"]
    if hardware_present:
        generator_ok = (
            isinstance(generator, Mapping)
            and _nonempty(host_id)
            and _nonempty(generator.get("generator_host_id"))
            and generator.get("generator_host_id") != host_id
            and _nonempty(generator.get("generator_nic_serial"))
            and generator.get("generator_nic_serial") not in serials
            and generator.get("same_adapter_loopback") is False
            and generator.get("identity_verified") is True
            and _is_sha256(generator.get("identity_receipt_sha256"))
            and _is_finite_number(generator.get("max_sustained_64b_mpps"))
            and generator.get("max_sustained_64b_mpps")
            >= generator_contract["max_sustained_64b_mpps_min"]
            and _is_finite_number(generator.get("link_speed_mbps"))
            and generator.get("link_speed_mbps")
            >= generator_contract["link_speed_mbps_min"]
            and _nonempty(generator.get("physical_link_id"))
        )
        _check(
            checks,
            blockers,
            pending,
            "generator.independent_identity_capacity",
            generator_ok,
            {
                "capture_host_id": host_id,
                "candidate_serials": serials,
                "minimum_64b_mpps": generator_contract[
                    "max_sustained_64b_mpps_min"
                ],
            },
        )

    foundational_blockers = list(blockers)

    xdp = inventory.get("xdp_probe_receipt")
    xdp_contract = contract["native_xdp_af_xdp"]
    if hardware_present:
        if xdp is None:
            _check(
                checks,
                blockers,
                pending,
                "xdp.native_forced_zerocopy_live_receipt",
                None,
                "authorized live probe receipt is absent",
            )
        elif not isinstance(xdp, Mapping):
            _check(
                checks,
                blockers,
                pending,
                "xdp.native_forced_zerocopy_live_receipt",
                False,
                "receipt_not_object",
            )
        else:
            queue_results = xdp.get("queue_results")
            xdp_queue_ids: List[Any] = []
            xdp_queues_ok = isinstance(queue_results, list)
            if isinstance(queue_results, list):
                for queue in queue_results:
                    if not isinstance(queue, Mapping):
                        xdp_queues_ok = False
                        continue
                    xdp_queue_ids.append(queue.get("queue_id"))
                    packets = queue.get("packets")
                    xdp_queues_ok = bool(xdp_queues_ok) and (
                        _is_nonnegative_int(queue.get("queue_id"))
                        and queue.get("xsk_bind_mode")
                        == xdp_contract["xsk_bind_mode_required"]
                        and queue.get("zero_copy_confirmed") is True
                        and _is_nonnegative_int(packets)
                    )
            xdp_packets = (
                [queue.get("packets") for queue in queue_results]
                if isinstance(queue_results, list)
                and all(isinstance(queue, Mapping) for queue in queue_results)
                else []
            )
            xdp_total_packets = (
                sum(xdp_packets)
                if xdp_packets
                and all(
                    _is_nonnegative_int(value)
                    for value in xdp_packets
                )
                else 0
            )
            xdp_queues_ok = bool(xdp_queues_ok) and (
                len(xdp_queue_ids) >= xdp_contract["tested_queue_count_min"]
                and len(xdp_queue_ids) == len(set(xdp_queue_ids))
                and xdp_total_packets > 0
                and sum(
                    1
                    for packets in xdp_packets
                    if packets / xdp_total_packets
                    >= xdp_contract["min_active_queue_share"]
                )
                >= xdp_contract["tested_queue_count_min"]
            )
            xdp_ok = (
                _receipt_identity_ok(xdp, host_id, [str(item) for item in pci_addresses])
                and xdp.get("success") is True
                and xdp.get("native_feature_supported") is True
                and xdp.get("attach_mode") == xdp_contract["attach_mode_required"]
                and xdp.get("xsk_bind_mode") == xdp_contract["xsk_bind_mode_required"]
                and xdp.get("zero_copy_confirmed") is True
                and xdp.get("copy_fallback_detected") is False
                and xdp_queues_ok
                and xdp.get("state_restored") is True
                and xdp.get("persistent_mutations") is False
            )
            _check(
                checks,
                blockers,
                pending,
                "xdp.native_forced_zerocopy_live_receipt",
                xdp_ok,
                {
                    "run_id": xdp.get("run_id"),
                    "attach_mode": xdp.get("attach_mode"),
                    "xsk_bind_mode": xdp.get("xsk_bind_mode"),
                    "verified_queue_ids": sorted(xdp_queue_ids)
                    if all(isinstance(item, int) for item in xdp_queue_ids)
                    else xdp_queue_ids,
                    "total_packets_recomputed": xdp_total_packets,
                },
            )

    dpdk = inventory.get("dpdk_probe_receipt")
    if hardware_present:
        if dpdk is None:
            _check(
                checks,
                blockers,
                pending,
                "dpdk.rss_tss_multiqueue_live_receipt",
                None,
                "authorized live probe receipt is absent",
            )
        elif not isinstance(dpdk, Mapping):
            _check(
                checks,
                blockers,
                pending,
                "dpdk.rss_tss_multiqueue_live_receipt",
                False,
                "receipt_not_object",
            )
        else:
            rx_queue_packets = dpdk.get("rx_queue_packets")
            tx_queue_packets = dpdk.get("tx_queue_packets")
            rx_active = (
                sum(
                    1
                    for value in rx_queue_packets
                    if _is_nonnegative_int(value) and value > 0
                )
                if isinstance(rx_queue_packets, list)
                else 0
            )
            tx_active = (
                sum(
                    1
                    for value in tx_queue_packets
                    if _is_nonnegative_int(value) and value > 0
                )
                if isinstance(tx_queue_packets, list)
                else 0
            )
            raw_queue_counts_ok = (
                isinstance(rx_queue_packets, list)
                and isinstance(tx_queue_packets, list)
                and len(rx_queue_packets) >= queue_contract["rx_queues_min"]
                and len(tx_queue_packets) >= queue_contract["tx_queues_min"]
                and all(
                    _is_nonnegative_int(value)
                    for value in rx_queue_packets + tx_queue_packets
                )
            )
            rx_total = sum(rx_queue_packets) if raw_queue_counts_ok else 0
            tx_total = sum(tx_queue_packets) if raw_queue_counts_ok else 0
            rx_balanced = (
                sum(
                    1
                    for value in rx_queue_packets
                    if rx_total > 0
                    and value / rx_total >= queue_contract["min_active_queue_share"]
                )
                if raw_queue_counts_ok
                else 0
            )
            tx_balanced = (
                sum(
                    1
                    for value in tx_queue_packets
                    if tx_total > 0
                    and value / tx_total >= queue_contract["min_active_queue_share"]
                )
                if raw_queue_counts_ok
                else 0
            )
            dpdk_ok = (
                _receipt_identity_ok(dpdk, host_id, [str(item) for item in pci_addresses])
                and dpdk.get("success") is True
                and dpdk.get("rss_enabled") is True
                and dpdk.get("tss_enabled") is True
                and dpdk.get("reta_programmed") is True
                and _int_at_least(
                    dpdk.get("rx_queues_configured"), queue_contract["rx_queues_min"]
                )
                and _int_at_least(
                    dpdk.get("tx_queues_configured"), queue_contract["tx_queues_min"]
                )
                and raw_queue_counts_ok
                and rx_total > 0
                and tx_total > 0
                and rx_active >= queue_contract["rx_queues_with_packets_min"]
                and tx_active >= queue_contract["tx_queues_with_packets_min"]
                and rx_balanced >= queue_contract["rx_queues_min"]
                and tx_balanced >= queue_contract["tx_queues_min"]
                and dpdk.get("state_restored") is True
                and dpdk.get("persistent_mutations") is False
            )
            _check(
                checks,
                blockers,
                pending,
                "dpdk.rss_tss_multiqueue_live_receipt",
                dpdk_ok,
                {
                    "run_id": dpdk.get("run_id"),
                    "pmd": dpdk.get("pmd"),
                    "rx_queues_with_packets_recomputed": rx_active,
                    "tx_queues_with_packets_recomputed": tx_active,
                    "rx_queues_above_min_share_recomputed": rx_balanced,
                    "tx_queues_above_min_share_recomputed": tx_balanced,
                },
            )

    if isinstance(xdp, Mapping) and isinstance(dpdk, Mapping):
        _check(
            checks,
            blockers,
            pending,
            "probes.distinct_runs",
            xdp.get("run_id") != dpdk.get("run_id"),
            {"xdp": xdp.get("run_id"), "dpdk": dpdk.get("run_id")},
        )

    restoration: Optional[Dict[str, Any]] = None
    if baseline_inventory is not None:
        restoration = compare_restoration(baseline_inventory, inventory)
        _check(
            checks,
            blockers,
            pending,
            "restoration.control_plane_and_kernel_binding",
            restoration["verified"],
            {
                "before_sha256": restoration["before_sha256"],
                "after_sha256": restoration["after_sha256"],
            },
        )

    if inventory_invalid:
        status = "invalid_inventory"
    elif not hardware_present:
        status = "hardware_pending"
    elif foundational_blockers:
        status = "preflight_failed"
    elif any(item.startswith("xdp.") or item.startswith("dpdk.") for item in pending):
        status = "capability_probe_pending"
    elif blockers:
        status = "preflight_failed"
    elif pending:
        status = "preflight_pending"
    else:
        status = "self_consistent_capability_receipts_only"

    result = {
        "schema_version": 1,
        "scope": "new_high_speed_nic_acceptance_preflight",
        "contract_id": contract["contract_id"],
        "contract_sha256": canonical_sha256(contract),
        "inventory_sha256": canonical_sha256(inventory),
        "status": status,
        "checks": checks,
        "blockers": sorted(set(blockers)),
        "pending": sorted(set(pending)),
        "hardware_present": hardware_present,
        "inventory_ready_for_authorized_probes": (
            hardware_present and not foundational_blockers
        ),
        "read_only_preflight_qualified": False,
        "self_consistent_capability_receipts_valid": (
            status == "self_consistent_capability_receipts_only"
        ),
        "receipt_trust_level": (
            "self_consistent_hash_bound_to_frozen_local_helper_not_external_attestation"
            if status == "self_consistent_capability_receipts_only"
            else "not_established"
        ),
        "authorized_probe_execution_required": status == "capability_probe_pending",
        "production_qualified": False,
        "final_pareto_ingestion_allowed": False,
        "mutations_performed": False,
    }
    if restoration is not None:
        result["restoration"] = restoration
    return result


def exit_code_for_status(status: str) -> int:
    return {
        "self_consistent_capability_receipts_only": 26,
        "hardware_pending": 20,
        "capability_probe_pending": 21,
        "preflight_pending": 21,
        "preflight_failed": 22,
        "invalid_inventory": 23,
        "invalid_contract": 24,
    }.get(status, 25)
