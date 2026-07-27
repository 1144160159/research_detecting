"""Domain-stable feature projections for cross-dataset probes."""

from __future__ import annotations

import math
from typing import Dict, Iterable, Mapping


FEATURE_PROFILES = (
    "raw",
    "invariant_v1",
    "invariant_no_ports_v1",
)

COMMON_SERVICE_PORTS = (
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    123,
    143,
    443,
    445,
    993,
    995,
    3389,
)


def _safe_ratio(numerator, denominator):
    return 0.0 if denominator <= 0 else numerator / denominator


def _log_feature(output, name, value):
    output[name] = math.log1p(max(0.0, float(value)))


def transform_feature_row(
    row: Mapping[str, float], profile: str
) -> Dict[str, float]:
    if profile == "raw":
        return dict(row)
    if profile not in FEATURE_PROFILES:
        raise ValueError("unknown feature profile: {}".format(profile))

    output = {}
    protocol = float(row.get("packet_protocol", 0.0))
    output["protocol"] = protocol
    output["protocol_tcp"] = float(protocol == 6.0)
    output["protocol_udp"] = float(protocol == 17.0)

    if profile != "invariant_no_ports_v1":
        src_port = int(row.get("packet_src_port", 0.0))
        dst_port = int(row.get("packet_dst_port", 0.0))
        ports = (src_port, dst_port)
        output["port_any_well_known"] = float(
            any(0 < port < 1024 for port in ports)
        )
        output["port_both_ephemeral"] = float(
            all(port >= 49152 for port in ports)
        )
        for port in COMMON_SERVICE_PORTS:
            output["service_port_{}".format(port)] = float(
                port in ports
            )

    log_names = (
        "flow_packets",
        "flow_bytes",
        "flow_payload_bytes",
        "flow_duration_s",
        "flow_mean_length",
        "flow_length_std",
        "flow_min_length",
        "flow_max_length",
        "flow_mean_iat_s",
        "flow_iat_std_s",
    )
    for name in log_names:
        _log_feature(output, name + "_log1p", row.get(name, 0.0))
    output["flow_tcp_flags_or"] = float(
        row.get("flow_tcp_flags_or", 0.0)
    )
    for name, value in row.items():
        if (
            name.startswith("flow_")
            and name.endswith("_flag_count")
            and not name.startswith("flow_fwd_")
            and not name.startswith("flow_bwd_")
        ):
            _log_feature(output, name + "_log1p", value)

    packets_fwd = float(row.get("flow_fwd_packets", 0.0))
    packets_bwd = float(row.get("flow_bwd_packets", 0.0))
    bytes_fwd = float(row.get("flow_fwd_bytes", 0.0))
    bytes_bwd = float(row.get("flow_bwd_bytes", 0.0))
    payload_fwd = float(row.get("flow_fwd_payload_bytes", 0.0))
    payload_bwd = float(row.get("flow_bwd_payload_bytes", 0.0))
    output["packet_direction_imbalance"] = _safe_ratio(
        abs(packets_fwd - packets_bwd), packets_fwd + packets_bwd
    )
    output["byte_direction_imbalance"] = _safe_ratio(
        abs(bytes_fwd - bytes_bwd), bytes_fwd + bytes_bwd
    )
    output["payload_direction_imbalance"] = _safe_ratio(
        abs(payload_fwd - payload_bwd), payload_fwd + payload_bwd
    )
    output["payload_byte_ratio"] = _safe_ratio(
        payload_fwd + payload_bwd, bytes_fwd + bytes_bwd
    )

    for prefix in ("mean_iat_s", "iat_std_s"):
        fwd = float(row.get("flow_fwd_{}".format(prefix), 0.0))
        bwd = float(row.get("flow_bwd_{}".format(prefix), 0.0))
        _log_feature(
            output,
            "directional_{}_min_log1p".format(prefix),
            min(fwd, bwd),
        )
        _log_feature(
            output,
            "directional_{}_max_log1p".format(prefix),
            max(fwd, bwd),
        )

    for name in (
        "payload_entropy",
        "payload_printable_ratio",
        "payload_zero_ratio",
    ):
        if name in row:
            output[name] = float(row[name])
    output["deep_tier_available"] = float(
        row.get("quality_seen_deep_tier", 0.0)
    )
    return output


def transform_feature_rows(
    rows: Iterable[Mapping[str, float]], profile: str
):
    return [transform_feature_row(row, profile) for row in rows]
