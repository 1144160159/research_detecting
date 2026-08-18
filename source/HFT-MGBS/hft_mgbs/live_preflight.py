"""Physical-NIC host preflight for HFT-MGBS live acceptance."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional


CAP_NET_ADMIN = 12
CAP_NET_RAW = 13


def audit_host_preflight(
    interface_realpath: str,
    capability_mask: int,
    thresholds: Mapping[str, object],
    *,
    carrier: Optional[int] = None,
    operstate: Optional[str] = None,
    speed_mbps: Optional[int] = None,
    driver: Optional[str] = None,
    capture_driver: Optional[str] = None,
    timestamp_capabilities: Optional[Iterable[str]] = None,
    allow_virtual_diagnostic: bool = False,
    minimum_speed_mbps: Optional[int] = None,
    require_unmanaged: bool = False,
    network_master: Optional[str] = None,
    has_ip_address: Optional[bool] = None,
    carries_default_route: Optional[bool] = None,
):
    errors = []
    normalized_path = str(interface_realpath).replace("\\", "/")
    is_virtual = "/virtual/net/" in normalized_path
    if (is_virtual and not allow_virtual_diagnostic) or not normalized_path:
        errors.append("interface.not_physical")
    if not capability_mask & (1 << CAP_NET_RAW):
        errors.append("capability.cap_net_raw")
    if not capability_mask & (1 << CAP_NET_ADMIN):
        errors.append("capability.cap_net_admin")
    if carrier != 1:
        errors.append("link.no_carrier")
    if operstate != "up":
        errors.append("link.operstate")
    if not isinstance(speed_mbps, int) or speed_mbps <= 0:
        errors.append("link.speed")
    if (
        isinstance(minimum_speed_mbps, int)
        and minimum_speed_mbps > 0
        and isinstance(speed_mbps, int)
        and speed_mbps > 0
        and speed_mbps < minimum_speed_mbps
    ):
        errors.append("link.speed_below_minimum")
    if not driver:
        errors.append("link.driver")
    if require_unmanaged:
        if network_master:
            errors.append("interface.network_master")
        if has_ip_address is not False:
            errors.append("interface.ip_address_configured")
        if carries_default_route is not False:
            errors.append("interface.default_route")
    timestamp_capabilities = set(timestamp_capabilities or ())
    required_timestamp_capabilities = {
        "software-receive",
        "software-system-clock",
    }
    if capture_driver == "af-packet-ts" and not (
        required_timestamp_capabilities <= timestamp_capabilities
    ):
        errors.append("timestamp.so_timestampns_unsupported")
    if thresholds.get("frozen") is not True:
        errors.append("thresholds.not_frozen")
    if (
        thresholds.get("target_load_mpps") is None
        and thresholds.get("target_load_gbps") is None
    ):
        errors.append("thresholds.target_load")
    for field in (
        "max_parse_reject_rate",
        "max_end_to_end_p99_us",
        "max_end_to_end_p999_us",
        "min_run_duration_s",
    ):
        value = thresholds.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append("thresholds.{}".format(field))
    return {
        "accepted": not errors,
        "errors": errors,
        "physical_nic_visible": bool(normalized_path) and not is_virtual,
        "virtual_diagnostic_allowed": allow_virtual_diagnostic,
        "virtual_interface_visible": is_virtual,
        "cap_net_raw": bool(capability_mask & (1 << CAP_NET_RAW)),
        "cap_net_admin": bool(capability_mask & (1 << CAP_NET_ADMIN)),
        "carrier": carrier,
        "operstate": operstate,
        "speed_mbps": speed_mbps,
        "driver": driver,
        "capture_driver": capture_driver,
        "minimum_speed_mbps": minimum_speed_mbps,
        "require_unmanaged": require_unmanaged,
        "network_master": network_master,
        "has_ip_address": has_ip_address,
        "carries_default_route": carries_default_route,
        "timestamp_capabilities": sorted(timestamp_capabilities),
        "kernel_receive_timestamp_ready": (
            capture_driver == "af-packet-ts"
            and required_timestamp_capabilities
            <= timestamp_capabilities
        ),
        "link_ready": not any(error.startswith("link.") for error in errors),
        "thresholds_frozen": thresholds.get("frozen") is True,
    }
