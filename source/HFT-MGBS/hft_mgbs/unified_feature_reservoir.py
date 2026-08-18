"""Unified online feature reservoir for full-traffic extraction.

This module is the backend-neutral correctness implementation that bridges the
CAEOS unified PCAP schema and the HFT-MGBS streaming pipeline.  Cheap behaviour
features and bounded packet primitives are collected for every parsed packet.
Payload distributions and encrypted-protocol structure are materialised only
for flows promoted to the deep tier.  Missing or truncated modalities are
explicit evidence and are never silently replaced with qualified zeroes.
"""

from __future__ import annotations

import hashlib
import base64
import ipaddress
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from .features import FlowKey, PacketRecord, TCP_FLAG_NAMES


RESERVOIR_POLICY_SCOPE = "hft_mgbs_unified_feature_reservoir_policy_v1"
RESERVOIR_RECEIPT_SCOPE = "hft_mgbs_unified_feature_reservoir_receipt_v1"
CAEOS_SCHEMA_SHA256 = "f300834ba34c47d1b8d4bbd5506f081b142889e51f12150ddf55608214ef6ce1"
CAEOS_FEATURE_VIEWS_SHA256 = "3bf4061d62a4c10910f2740652f9676eab7b0f837c8a7bfb97746c2b64e3ad04"

SAFE_SCALAR_COLUMNS: Tuple[str, ...] = (
    "duration_us", "ip_version", "transport_protocol", "packet_count_total",
    "forward_packet_count", "reverse_packet_count", "packet_bytes_total",
    "forward_packet_bytes", "reverse_packet_bytes", "payload_bytes_total",
    "forward_payload_bytes", "reverse_payload_bytes",
    "forward_transport_header_bytes", "reverse_transport_header_bytes",
    "reverse_forward_packet_ratio", "reverse_forward_byte_ratio",
    "direction_switch_count", "direction_switch_rate",
    "direction_switch_iat_us_mean", "direction_switch_iat_us_std",
    "fragmented_packet_count", "noninitial_fragment_count",
    "packet_length_min", "packet_length_max", "packet_length_mean",
    "packet_length_std", "packet_length_median", "packet_length_variance",
    "packet_length_skewness", "packet_length_coefficient_of_variation",
    "forward_packet_length_min", "forward_packet_length_max",
    "forward_packet_length_mean", "forward_packet_length_std",
    "reverse_packet_length_min", "reverse_packet_length_max",
    "reverse_packet_length_mean", "reverse_packet_length_std",
    "packet_iat_us_total", "packet_iat_us_min", "packet_iat_us_max",
    "packet_iat_us_mean", "packet_iat_us_std", "packet_iat_us_median",
    "packet_iat_us_variance", "packet_iat_us_skewness",
    "packet_iat_us_coefficient_of_variation", "forward_packet_iat_us_total",
    "forward_packet_iat_us_min", "forward_packet_iat_us_max",
    "forward_packet_iat_us_mean", "forward_packet_iat_us_std",
    "reverse_packet_iat_us_total", "reverse_packet_iat_us_min",
    "reverse_packet_iat_us_max", "reverse_packet_iat_us_mean",
    "reverse_packet_iat_us_std", "packet_payload_length_min",
    "packet_payload_length_max", "packet_payload_length_mean",
    "packet_payload_length_std", "packet_payload_length_median",
    "packet_payload_length_variance", "packet_payload_length_skewness",
    "packet_payload_length_coefficient_of_variation", "active_duration_us_total",
    "active_duration_us_min", "active_duration_us_max", "active_duration_us_mean",
    "active_duration_us_std", "idle_duration_us_total", "idle_duration_us_min",
    "idle_duration_us_max", "idle_duration_us_mean", "idle_duration_us_std",
    "packets_per_second", "bytes_per_second", "tcp_fin_flag_count",
    "tcp_syn_flag_count", "tcp_rst_flag_count", "tcp_psh_flag_count",
    "tcp_ack_flag_count", "tcp_urg_flag_count", "tcp_ece_flag_count",
    "tcp_cwr_flag_count",
)

SEQUENCE_COLUMNS: Tuple[str, ...] = (
    "packet_length_seq", "ip_length_seq", "packet_iat_us_seq", "direction_seq",
    "packet_protocol_seq", "tcp_flags_seq", "ip_dscp_ecn_seq", "ip_flags_seq",
    "ip_fragment_offset_seq", "ip_fragment_id_seq", "transport_header_length_seq",
    "tcp_sequence_seq", "tcp_acknowledgement_seq", "packet_payload_length_seq",
    "sanitized_l4_packet_length_seq", "packet_ttl_seq", "tcp_window_seq",
)

ENCRYPTED_STRUCTURE_COLUMNS: Tuple[str, ...] = (
    "tls_record_type_seq", "tls_record_version_seq", "tls_record_length_seq",
    "tls_handshake_type_seq", "tls_client_hello_present",
    "tls_server_hello_present", "quic_long_header_packet_count", "quic_version_seq",
)

CONTEXT_COLUMNS: Tuple[str, ...] = (
    "window_packet_count", "window_byte_count", "window_flow_count",
    "window_protocol_entropy", "window_service_port_entropy", "window_syn_rate",
    "window_rst_rate", "window_endpoint_max_fanout",
    "window_endpoint_max_unique_ports", "window_new_flow_rate",
)

PAYLOAD_MODALITY_COLUMNS: Tuple[str, ...] = (
    "payload_b64", "payload_histogram", "payload_bytes_total",
    "payload_bytes_stored", "forward_payload_bytes", "reverse_payload_bytes",
    "sanitized_l4_b64", "sanitized_l4_bytes_total",
    "sanitized_l4_bytes_stored",
)

FOUNDATIONAL_EXTRA_COLUMNS: Tuple[str, ...] = (
    "packet_count_stored", "port_a", "port_b", "application_protocol_hint",
)

AUDIT_ONLY_COLUMNS: Tuple[str, ...] = (
    "schema_version", "dataset_id", "dataset_role", "sample_id", "capture_id",
    "source_container_sha256", "source_member", "label_status", "label_source",
    "label_mapping_version", "dataset_native_label", "flow_key_hash",
    "flow_start_ns", "flow_end_ns", "endpoint_a_hash", "endpoint_b_hash",
    "flow_segment_index",
)

TARGET_COLUMNS: Tuple[str, ...] = (
    "traffic_class", "attack_category", "attack_subcategory", "fine_label",
    "family_label", "binary_label",
)

DERIVED_FEATURE_COLUMNS: Tuple[str, ...] = (
    "initiator_relative_direction_seq", "signed_packet_length_seq",
    "directional_burst_count", "directional_burst_packet_count_summary",
    "directional_burst_byte_summary", "payload_presence_fraction",
    "modality_missingness_mask",
)


def _ordered_union(*groups: Iterable[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(name for group in groups for name in group))


MODEL_CANDIDATE_PERSISTENT_COLUMNS: Tuple[str, ...] = _ordered_union(
    SAFE_SCALAR_COLUMNS,
    SEQUENCE_COLUMNS,
    ENCRYPTED_STRUCTURE_COLUMNS,
    PAYLOAD_MODALITY_COLUMNS,
)

ONLINE_EXTRACTABLE_COLUMNS: Tuple[str, ...] = _ordered_union(
    MODEL_CANDIDATE_PERSISTENT_COLUMNS,
    FOUNDATIONAL_EXTRA_COLUMNS,
)

UNIFIED_PCAP_COLUMN_COUNT = 143

CSV_SEQUENCE_COLUMNS: Tuple[str, ...] = SEQUENCE_COLUMNS + (
    "tls_record_type_seq", "tls_record_version_seq", "tls_record_length_seq",
    "tls_handshake_type_seq", "quic_version_seq", "payload_histogram",
)

INTEGER_ONLINE_COLUMNS: Tuple[str, ...] = (
    "duration_us", "ip_version", "transport_protocol", "packet_count_total",
    "packet_count_stored", "forward_packet_count", "reverse_packet_count",
    "packet_bytes_total", "forward_packet_bytes", "reverse_packet_bytes",
    "payload_bytes_total", "forward_payload_bytes", "reverse_payload_bytes",
    "forward_transport_header_bytes", "reverse_transport_header_bytes",
    "direction_switch_count", "fragmented_packet_count", "noninitial_fragment_count",
    "packet_length_min", "packet_length_max", "forward_packet_length_min",
    "forward_packet_length_max", "reverse_packet_length_min",
    "reverse_packet_length_max", "packet_iat_us_total", "packet_iat_us_min",
    "packet_iat_us_max", "forward_packet_iat_us_total",
    "forward_packet_iat_us_min", "forward_packet_iat_us_max",
    "reverse_packet_iat_us_total", "reverse_packet_iat_us_min",
    "reverse_packet_iat_us_max", "packet_payload_length_min",
    "packet_payload_length_max", "active_duration_us_total",
    "active_duration_us_min", "active_duration_us_max", "idle_duration_us_total",
    "idle_duration_us_min", "idle_duration_us_max", "tcp_fin_flag_count",
    "tcp_syn_flag_count", "tcp_rst_flag_count", "tcp_psh_flag_count",
    "tcp_ack_flag_count", "tcp_urg_flag_count", "tcp_ece_flag_count",
    "tcp_cwr_flag_count", "payload_bytes_stored", "sanitized_l4_bytes_total",
    "sanitized_l4_bytes_stored", "tls_client_hello_present",
    "tls_server_hello_present", "quic_long_header_packet_count", "port_a", "port_b",
)


class UnifiedFeatureReservoirError(ValueError):
    """Raised when online feature semantics or evidence are invalid."""


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _ratio(numerator: float, denominator: float) -> float:
    return 0.0 if denominator <= 0.0 else numerator / denominator


def _entropy(counts: Mapping[Any, int]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return -sum((value / total) * math.log2(value / total) for value in counts.values() if value)


def _canonical_key_material(flow_key: FlowKey) -> Tuple[bytes, bytes, bytes]:
    try:
        endpoint_a = ipaddress.ip_address(flow_key[0]).packed
        endpoint_b = ipaddress.ip_address(flow_key[1]).packed
    except ValueError as error:
        raise UnifiedFeatureReservoirError(
            "a unified PCAP row requires canonical IPv4 or IPv6 endpoints"
        ) from error
    port_a = int(flow_key[2])
    port_b = int(flow_key[3])
    protocol = int(flow_key[4])
    material = (
        endpoint_a
        + port_a.to_bytes(2, "big")
        + endpoint_b
        + port_b.to_bytes(2, "big")
        + protocol.to_bytes(1, "big")
    )
    return endpoint_a, endpoint_b, material


def materialize_unified_pcap_row(
    record: "UnifiedFlowFeatureRecord",
    context: "UnifiedPcapExportContext",
    *,
    require_complete_modalities: bool = True,
) -> Mapping[str, Any]:
    """Materialise the exact 143-column CAEOS v4 persistent row.

    The function is deliberately fail-closed: a fully qualified offline row
    cannot be emitted when the budget deferred payload/TLS/QUIC observation or
    when the payload histogram does not conserve observed payload bytes.
    """

    if not isinstance(record, UnifiedFlowFeatureRecord) or not isinstance(
        context, UnifiedPcapExportContext
    ):
        raise UnifiedFeatureReservoirError("unified PCAP export types are invalid")
    if context.schema_version != "caeos_unified_multimodal_csv_schema_v4":
        raise UnifiedFeatureReservoirError("unified PCAP schema version is not frozen v4")
    if len(context.source_container_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in context.source_container_sha256
    ):
        raise UnifiedFeatureReservoirError("source container SHA-256 is invalid")
    if context.binary_label not in (-1, 0, 1):
        raise UnifiedFeatureReservoirError("binary label is outside the frozen domain")
    if require_complete_modalities and (
        not record.quality.get("deep_tier_selected")
        or not record.quality.get("payload_histogram_complete")
    ):
        raise UnifiedFeatureReservoirError(
            "full 143-column export requires complete budgeted modalities"
        )

    endpoint_a, endpoint_b, key_material = _canonical_key_material(record.flow_key)
    dataset_bytes = context.dataset_id.encode("utf-8")
    flow_hash = hashlib.sha256(dataset_bytes + b"\0" + key_material).hexdigest()
    sample_material = "|".join(
        [
            context.dataset_id,
            context.source_container_sha256,
            context.source_member,
            flow_hash,
            str(record.flow_start_ns),
            str(record.flow_segment_index),
            context.sample_disambiguator,
        ]
    )
    row: Dict[str, Any] = {
        "schema_version": context.schema_version,
        "dataset_id": context.dataset_id,
        "dataset_role": context.dataset_role,
        "sample_id": hashlib.sha256(sample_material.encode("utf-8")).hexdigest(),
        "capture_id": context.capture_id,
        "source_container_sha256": context.source_container_sha256,
        "source_member": context.source_member,
        "label_status": context.label_status,
        "label_source": context.label_source,
        "label_mapping_version": context.label_mapping_version,
        "dataset_native_label": context.dataset_native_label,
        "traffic_class": context.traffic_class,
        "attack_category": context.attack_category,
        "attack_subcategory": context.attack_subcategory,
        "fine_label": context.fine_label,
        "family_label": context.family_label,
        "binary_label": context.binary_label,
        "flow_segment_index": record.flow_segment_index,
        "flow_key_hash": flow_hash,
        "flow_start_ns": record.flow_start_ns,
        "flow_end_ns": record.flow_end_ns,
        "endpoint_a_hash": hashlib.sha256(dataset_bytes + b"\0" + endpoint_a)
        .hexdigest()[:16],
        "endpoint_b_hash": hashlib.sha256(dataset_bytes + b"\0" + endpoint_b)
        .hexdigest()[:16],
    }
    row.update(record.persistent_features)
    for name in CSV_SEQUENCE_COLUMNS:
        values = row[name]
        if not isinstance(values, (tuple, list)):
            raise UnifiedFeatureReservoirError(
                "{} must be an in-memory integer sequence before CSV export".format(name)
            )
        row[name] = ";".join(str(int(value)) for value in values)
    for name in INTEGER_ONLINE_COLUMNS:
        row[name] = int(row[name])
    if len(row) != UNIFIED_PCAP_COLUMN_COUNT:
        raise UnifiedFeatureReservoirError(
            "unified PCAP row must contain exactly {} columns, got {}".format(
                UNIFIED_PCAP_COLUMN_COUNT, len(row)
            )
        )
    return row


@dataclass(frozen=True)
class PacketMetadata:
    """Optional parsed-header sidecar not present in the frozen A09 record."""

    ip_version: int = 0
    ip_length: int = 0
    ip_dscp_ecn: int = 0
    ip_flags: int = 0
    ip_fragment_offset: int = 0
    ip_fragment_id: int = 0
    more_fragments: bool = False
    transport_header_length: int = 0
    tcp_sequence: int = 0
    tcp_acknowledgement: int = 0
    packet_ttl: int = 0
    tcp_window: int = 0
    sanitized_l4: bytes = b""
    sanitized_l4_total: Optional[int] = None


@dataclass(frozen=True)
class UnifiedPcapExportContext:
    """External provenance and labels needed to materialise a 143-column row.

    Packet capture must not invent these values.  They are supplied by the
    dataset/label control plane, while flow identity and all 120 extractable
    columns are recomputed from the observed packet record.
    """

    schema_version: str
    dataset_id: str
    dataset_role: str
    capture_id: str
    source_container_sha256: str
    source_member: str
    label_status: str
    label_source: str
    label_mapping_version: str
    dataset_native_label: str
    traffic_class: str
    attack_category: str
    attack_subcategory: str
    fine_label: str
    family_label: str
    binary_label: int
    sample_disambiguator: str


@dataclass(frozen=True)
class UnifiedFlowFeatureRecord:
    flow_key: FlowKey
    flow_key_hash: str
    flow_segment_index: int
    flow_start_ns: int
    flow_end_ns: int
    safe_scalars: Mapping[str, float]
    packet_sequences: Mapping[str, Tuple[int, ...]]
    payload_features: Mapping[str, Any]
    encrypted_protocol_structure: Mapping[str, Any]
    persistent_features: Mapping[str, Any]
    packet_interaction_graph: Mapping[str, Any]
    derived_features: Mapping[str, Any]
    quality: Mapping[str, Any]


@dataclass(frozen=True)
class ReservoirBatchResult:
    flow_records: Tuple[UnifiedFlowFeatureRecord, ...]
    window_contexts: Tuple[Mapping[str, Any], ...]
    receipt: Mapping[str, Any]


@dataclass
class _RunningStats:
    count: int = 0
    total: float = 0.0
    total_sq: float = 0.0
    total_cube: float = 0.0
    minimum: float = math.inf
    maximum: float = -math.inf
    median_samples: List[float] = field(default_factory=list)
    median_sample_limit: int = 64

    def add(self, value: float) -> None:
        value = float(value)
        self.count += 1
        self.total += value
        self.total_sq += value * value
        self.total_cube += value * value * value
        self.minimum = min(self.minimum, value)
        self.maximum = max(self.maximum, value)
        if len(self.median_samples) < self.median_sample_limit:
            self.median_samples.append(value)

    @property
    def mean(self) -> float:
        return self.total / self.count if self.count else 0.0

    @property
    def variance(self) -> float:
        return max(0.0, self.total_sq / self.count - self.mean * self.mean) if self.count else 0.0

    @property
    def std(self) -> float:
        return math.sqrt(self.variance)

    @property
    def median(self) -> float:
        if not self.median_samples:
            return 0.0
        values = sorted(self.median_samples)
        middle = len(values) // 2
        return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2.0

    @property
    def skewness(self) -> float:
        if self.count < 2 or self.std == 0.0:
            return 0.0
        mean = self.mean
        third = self.total_cube / self.count - 3.0 * mean * self.total_sq / self.count + 2.0 * mean**3
        return third / self.std**3

    @property
    def cv(self) -> float:
        return _ratio(self.std, abs(self.mean))

    def values(self, *, median: bool = False, distribution: bool = False) -> Mapping[str, float]:
        result = {
            "total": self.total,
            "min": 0.0 if not self.count else self.minimum,
            "max": 0.0 if not self.count else self.maximum,
            "mean": self.mean,
            "std": self.std,
        }
        if median:
            result["median"] = self.median
        if distribution:
            result.update(variance=self.variance, skewness=self.skewness, coefficient_of_variation=self.cv)
        return result

    def with_value(self, value: float) -> "_RunningStats":
        result = _RunningStats(
            count=self.count,
            total=self.total,
            total_sq=self.total_sq,
            total_cube=self.total_cube,
            minimum=self.minimum,
            maximum=self.maximum,
            median_samples=list(self.median_samples),
            median_sample_limit=self.median_sample_limit,
        )
        result.add(value)
        return result


@dataclass
class _FlowState:
    canonical_key: FlowKey
    first_directional_key: FlowKey
    first_timestamp: float
    last_timestamp: float
    max_sequence_packets: int
    payload_prefix_bytes: int
    sanitized_prefix_bytes: int
    segment_index: int = 0
    ip_version: int = 0
    packet_lengths: _RunningStats = field(default_factory=_RunningStats)
    fwd_lengths: _RunningStats = field(default_factory=_RunningStats)
    rev_lengths: _RunningStats = field(default_factory=_RunningStats)
    iats_us: _RunningStats = field(default_factory=_RunningStats)
    fwd_iats_us: _RunningStats = field(default_factory=_RunningStats)
    rev_iats_us: _RunningStats = field(default_factory=_RunningStats)
    payload_lengths: _RunningStats = field(default_factory=_RunningStats)
    switch_iats_us: _RunningStats = field(default_factory=_RunningStats)
    active_durations_us: _RunningStats = field(default_factory=_RunningStats)
    idle_durations_us: _RunningStats = field(default_factory=_RunningStats)
    packet_count: int = 0
    fwd_packets: int = 0
    rev_packets: int = 0
    packet_bytes: int = 0
    fwd_bytes: int = 0
    rev_bytes: int = 0
    payload_bytes: int = 0
    fwd_payload_bytes: int = 0
    rev_payload_bytes: int = 0
    fwd_header_bytes: int = 0
    rev_header_bytes: int = 0
    fragmented_packets: int = 0
    noninitial_fragments: int = 0
    direction_switch_count: int = 0
    last_direction: Optional[int] = None
    last_fwd_timestamp: Optional[float] = None
    last_rev_timestamp: Optional[float] = None
    active_start_timestamp: Optional[float] = None
    tcp_flag_counts: List[int] = field(default_factory=lambda: [0] * 8)
    sequences: MutableMapping[str, List[int]] = field(
        default_factory=lambda: {name: [] for name in SEQUENCE_COLUMNS}
    )
    payload_prefix: bytearray = field(default_factory=bytearray)
    sanitized_prefix: bytearray = field(default_factory=bytearray)
    payload_histogram: List[int] = field(default_factory=lambda: [0] * 256)
    payload_histogram_observed_bytes: int = 0
    sanitized_l4_bytes_total: int = 0
    tls_record_type_seq: List[int] = field(default_factory=list)
    tls_record_version_seq: List[int] = field(default_factory=list)
    tls_record_length_seq: List[int] = field(default_factory=list)
    tls_handshake_type_seq: List[int] = field(default_factory=list)
    tls_client_hello_present: bool = False
    tls_server_hello_present: bool = False
    quic_long_header_packet_count: int = 0
    quic_version_seq: List[int] = field(default_factory=list)
    deep_observed: bool = False
    metadata_complete: bool = True

    def _append_sequence(self, name: str, value: int) -> None:
        if len(self.sequences[name]) < self.max_sequence_packets:
            self.sequences[name].append(int(value))

    def update(
        self,
        packet: PacketRecord,
        metadata: PacketMetadata,
        *,
        deep: bool,
        activity_idle_threshold_s: float,
    ) -> None:
        direction = 1 if packet.flow_key == self.canonical_key else -1
        timestamp = float(packet.timestamp)
        iat_s = max(0.0, timestamp - self.last_timestamp) if self.packet_count else 0.0
        iat_us = iat_s * 1_000_000.0
        if self.packet_count:
            self.iats_us.add(iat_us)
            if iat_s > activity_idle_threshold_s:
                active_start = self.active_start_timestamp if self.active_start_timestamp is not None else self.first_timestamp
                self.active_durations_us.add(max(0.0, self.last_timestamp - active_start) * 1_000_000.0)
                self.idle_durations_us.add(iat_us)
                self.active_start_timestamp = timestamp
            if self.last_direction is not None and direction != self.last_direction:
                self.direction_switch_count += 1
                self.switch_iats_us.add(iat_us)
        else:
            self.active_start_timestamp = timestamp

        wire_length = max(0, int(packet.wire_length))
        payload_length = max(0, int(packet.actual_payload_length))
        self.packet_count += 1
        self.packet_bytes += wire_length
        self.payload_bytes += payload_length
        self.packet_lengths.add(wire_length)
        self.payload_lengths.add(payload_length)
        if direction == 1:
            self.fwd_packets += 1
            self.fwd_bytes += wire_length
            self.fwd_payload_bytes += payload_length
            self.fwd_header_bytes += max(0, metadata.transport_header_length)
            self.fwd_lengths.add(wire_length)
            if self.last_fwd_timestamp is not None:
                self.fwd_iats_us.add(max(0.0, timestamp - self.last_fwd_timestamp) * 1_000_000.0)
            self.last_fwd_timestamp = timestamp
        else:
            self.rev_packets += 1
            self.rev_bytes += wire_length
            self.rev_payload_bytes += payload_length
            self.rev_header_bytes += max(0, metadata.transport_header_length)
            self.rev_lengths.add(wire_length)
            if self.last_rev_timestamp is not None:
                self.rev_iats_us.add(max(0.0, timestamp - self.last_rev_timestamp) * 1_000_000.0)
            self.last_rev_timestamp = timestamp

        fragmented = metadata.more_fragments or metadata.ip_fragment_offset > 0
        self.fragmented_packets += int(fragmented)
        self.noninitial_fragments += int(metadata.ip_fragment_offset > 0)
        for index in range(8):
            self.tcp_flag_counts[index] += int(bool(packet.tcp_flags & (1 << index)))

        ip_version = metadata.ip_version or (6 if ":" in packet.src_ip else 4)
        if self.ip_version == 0:
            self.ip_version = ip_version
        elif self.ip_version != ip_version:
            self.metadata_complete = False
        ip_length = metadata.ip_length or wire_length
        sanitized_length = (
            metadata.sanitized_l4_total
            if metadata.sanitized_l4_total is not None
            else len(metadata.sanitized_l4) or metadata.transport_header_length + payload_length
        )
        self.sanitized_l4_bytes_total += max(0, int(sanitized_length))
        sequence_values = {
            "packet_length_seq": wire_length,
            "ip_length_seq": ip_length,
            "packet_iat_us_seq": int(round(iat_us)),
            "direction_seq": direction,
            "packet_protocol_seq": packet.protocol,
            "tcp_flags_seq": packet.tcp_flags,
            "ip_dscp_ecn_seq": metadata.ip_dscp_ecn,
            "ip_flags_seq": metadata.ip_flags,
            "ip_fragment_offset_seq": metadata.ip_fragment_offset,
            "ip_fragment_id_seq": metadata.ip_fragment_id,
            "transport_header_length_seq": metadata.transport_header_length,
            "tcp_sequence_seq": metadata.tcp_sequence,
            "tcp_acknowledgement_seq": metadata.tcp_acknowledgement,
            "packet_payload_length_seq": payload_length,
            "sanitized_l4_packet_length_seq": sanitized_length,
            "packet_ttl_seq": metadata.packet_ttl,
            "tcp_window_seq": metadata.tcp_window,
        }
        for name, value in sequence_values.items():
            self._append_sequence(name, value)

        self.metadata_complete = self.metadata_complete and metadata.ip_version in (4, 6)
        self.last_direction = direction
        self.last_timestamp = max(self.last_timestamp, timestamp)

        if deep:
            self.deep_observed = True
            available = packet.payload
            remaining = self.payload_prefix_bytes - len(self.payload_prefix)
            if remaining > 0:
                self.payload_prefix.extend(available[:remaining])
            sanitized_remaining = self.sanitized_prefix_bytes - len(self.sanitized_prefix)
            if sanitized_remaining > 0:
                self.sanitized_prefix.extend(metadata.sanitized_l4[:sanitized_remaining])
            for value in available:
                self.payload_histogram[value] += 1
            self.payload_histogram_observed_bytes += len(available)
            self._observe_encrypted_structure(available)

    def _observe_encrypted_structure(self, payload: bytes) -> None:
        offset = 0
        while offset + 5 <= len(payload) and len(self.tls_record_type_seq) < self.max_sequence_packets:
            record_type = payload[offset]
            if record_type not in (20, 21, 22, 23, 24):
                break
            version = int.from_bytes(payload[offset + 1 : offset + 3], "big")
            length = int.from_bytes(payload[offset + 3 : offset + 5], "big")
            self.tls_record_type_seq.append(record_type)
            self.tls_record_version_seq.append(version)
            self.tls_record_length_seq.append(length)
            if record_type == 22 and offset + 6 <= len(payload):
                handshake = payload[offset + 5]
                self.tls_handshake_type_seq.append(handshake)
                self.tls_client_hello_present |= handshake == 1
                self.tls_server_hello_present |= handshake == 2
            if length <= 0 or offset + 5 + length > len(payload):
                break
            offset += 5 + length
        if len(payload) >= 5 and payload[0] & 0x80:
            self.quic_long_header_packet_count += 1
            version = int.from_bytes(payload[1:5], "big")
            if len(self.quic_version_seq) < self.max_sequence_packets:
                self.quic_version_seq.append(version)

    @staticmethod
    def _prefix(prefix: str, values: Mapping[str, float], fields: Iterable[str]) -> Dict[str, float]:
        return {prefix + name: float(values[name]) for name in fields}

    def safe_scalars(self) -> Dict[str, float]:
        duration_s = max(0.0, self.last_timestamp - self.first_timestamp)
        current_active_us = max(0.0, self.last_timestamp - (self.active_start_timestamp or self.first_timestamp)) * 1_000_000.0
        active = self.active_durations_us.with_value(current_active_us)
        packet_length = self.packet_lengths.values(median=True, distribution=True)
        fwd_length = self.fwd_lengths.values()
        rev_length = self.rev_lengths.values()
        iat = self.iats_us.values(median=True, distribution=True)
        fwd_iat = self.fwd_iats_us.values()
        rev_iat = self.rev_iats_us.values()
        payload_length = self.payload_lengths.values(median=True, distribution=True)
        active_values = active.values()
        idle_values = self.idle_durations_us.values()
        values: Dict[str, float] = {
            "duration_us": duration_s * 1_000_000.0,
            "ip_version": float(self.ip_version),
            "transport_protocol": float(self.canonical_key[4]),
            "packet_count_total": float(self.packet_count),
            "forward_packet_count": float(self.fwd_packets),
            "reverse_packet_count": float(self.rev_packets),
            "packet_bytes_total": float(self.packet_bytes),
            "forward_packet_bytes": float(self.fwd_bytes),
            "reverse_packet_bytes": float(self.rev_bytes),
            "payload_bytes_total": float(self.payload_bytes),
            "forward_payload_bytes": float(self.fwd_payload_bytes),
            "reverse_payload_bytes": float(self.rev_payload_bytes),
            "forward_transport_header_bytes": float(self.fwd_header_bytes),
            "reverse_transport_header_bytes": float(self.rev_header_bytes),
            "reverse_forward_packet_ratio": _ratio(self.rev_packets, self.fwd_packets),
            "reverse_forward_byte_ratio": _ratio(self.rev_bytes, self.fwd_bytes),
            "direction_switch_count": float(self.direction_switch_count),
            "direction_switch_rate": _ratio(self.direction_switch_count, max(0, self.packet_count - 1)),
            "direction_switch_iat_us_mean": self.switch_iats_us.mean,
            "direction_switch_iat_us_std": self.switch_iats_us.std,
            "fragmented_packet_count": float(self.fragmented_packets),
            "noninitial_fragment_count": float(self.noninitial_fragments),
            "packets_per_second": _ratio(self.packet_count, duration_s),
            "bytes_per_second": _ratio(self.packet_bytes, duration_s),
        }
        for name in ("min", "max", "mean", "std", "median", "variance", "skewness", "coefficient_of_variation"):
            values["packet_length_" + name] = packet_length[name]
            values["packet_payload_length_" + name] = payload_length[name]
        for direction, stats in (("forward", fwd_length), ("reverse", rev_length)):
            for name in ("min", "max", "mean", "std"):
                values[direction + "_packet_length_" + name] = stats[name]
        for name in ("total", "min", "max", "mean", "std", "median", "variance", "skewness", "coefficient_of_variation"):
            values["packet_iat_us_" + name] = iat[name]
        for direction, stats in (("forward", fwd_iat), ("reverse", rev_iat)):
            for name in ("total", "min", "max", "mean", "std"):
                values[direction + "_packet_iat_us_" + name] = stats[name]
        for kind, stats in (("active", active_values), ("idle", idle_values)):
            for name in ("total", "min", "max", "mean", "std"):
                values[kind + "_duration_us_" + name] = stats[name]
        for index, name in enumerate(TCP_FLAG_NAMES):
            values["tcp_{}_flag_count".format(name)] = float(self.tcp_flag_counts[index])
        if set(values) != set(SAFE_SCALAR_COLUMNS):
            missing = sorted(set(SAFE_SCALAR_COLUMNS) - set(values))
            extra = sorted(set(values) - set(SAFE_SCALAR_COLUMNS))
            raise UnifiedFeatureReservoirError("safe scalar shape drift: missing={} extra={}".format(missing, extra))
        return values

    def record(self) -> UnifiedFlowFeatureRecord:
        sequences = {name: tuple(values) for name, values in self.sequences.items()}
        directions = sequences["direction_seq"]
        lengths = sequences["packet_length_seq"]
        bursts: List[List[int]] = []
        for direction, length in zip(directions, lengths):
            if not bursts or bursts[-1][0] != direction:
                bursts.append([direction, 0, 0])
            bursts[-1][1] += 1
            bursts[-1][2] += length
        graph_nodes = tuple(
            {
                "signed_packet_length": direction * length,
                "packet_iat_us": sequences["packet_iat_us_seq"][index],
                "direction": direction,
                "packet_payload_length": sequences["packet_payload_length_seq"][index],
                "tcp_flags": sequences["tcp_flags_seq"][index],
                "packet_ttl": sequences["packet_ttl_seq"][index],
            }
            for index, (direction, length) in enumerate(zip(directions, lengths))
        )
        graph_edges: List[Mapping[str, Any]] = []
        for index in range(max(0, len(graph_nodes) - 1)):
            graph_edges.append({"source": index, "target": index + 1, "type": "temporal"})
            if directions[index] == directions[index + 1]:
                graph_edges.append({"source": index, "target": index + 1, "type": "same_direction_burst"})
            else:
                graph_edges.append({"source": index, "target": index + 1, "type": "request_response"})
        payload_complete = self.payload_histogram_observed_bytes == self.payload_bytes
        sequence_complete = self.packet_count <= self.max_sequence_packets
        missingness = {
            "packet_sequence_truncated": not sequence_complete,
            "header_metadata_incomplete": not self.metadata_complete,
            "deep_tier_not_selected": not self.deep_observed,
            "payload_bytes_unobserved": self.deep_observed and not payload_complete,
            "sanitized_l4_unavailable": self.deep_observed and not bool(self.sanitized_prefix),
        }
        initiator_factor = 1 if self.first_directional_key == self.canonical_key else -1
        initiator_directions = tuple(direction * initiator_factor for direction in directions)
        derived = {
            "initiator_relative_direction_seq": initiator_directions,
            "signed_packet_length_seq": tuple(direction * length for direction, length in zip(directions, lengths)),
            "directional_burst_count": len(bursts),
            "directional_burst_packet_count_summary": tuple(item[1] for item in bursts),
            "directional_burst_byte_summary": tuple(item[2] for item in bursts),
            "payload_presence_fraction": _ratio(sum(value > 0 for value in sequences["packet_payload_length_seq"]), len(sequences["packet_payload_length_seq"])),
            "modality_missingness_mask": missingness,
        }
        payload_features = {
            "payload_bytes_total": self.payload_bytes,
            "payload_bytes_stored": len(self.payload_prefix),
            "payload_b64": base64.b64encode(bytes(self.payload_prefix)).decode("ascii"),
            "payload_prefix": bytes(self.payload_prefix),
            "sanitized_l4_bytes_total": self.sanitized_l4_bytes_total,
            "sanitized_l4_bytes_stored": len(self.sanitized_prefix),
            "sanitized_l4_b64": base64.b64encode(bytes(self.sanitized_prefix)).decode("ascii"),
            "sanitized_l4_prefix": bytes(self.sanitized_prefix),
            "payload_histogram": tuple(self.payload_histogram) if self.deep_observed else tuple(),
        }
        encrypted = {
            "tls_record_type_seq": tuple(self.tls_record_type_seq),
            "tls_record_version_seq": tuple(self.tls_record_version_seq),
            "tls_record_length_seq": tuple(self.tls_record_length_seq),
            "tls_handshake_type_seq": tuple(self.tls_handshake_type_seq),
            "tls_client_hello_present": int(self.tls_client_hello_present),
            "tls_server_hello_present": int(self.tls_server_hello_present),
            "quic_long_header_packet_count": self.quic_long_header_packet_count,
            "quic_version_seq": tuple(self.quic_version_seq),
        }
        ports = {int(self.canonical_key[2]), int(self.canonical_key[3])}
        if self.quic_version_seq:
            application_hint = "QUIC"
        elif self.tls_record_type_seq:
            application_hint = "TLS"
        elif ports.intersection({53, 5353}):
            application_hint = "DNS"
        elif 443 in ports:
            application_hint = "HTTPS_or_encrypted"
        elif ports.intersection({80, 8080}):
            application_hint = "HTTP"
        else:
            application_hint = "Other"
        persistent: Dict[str, Any] = dict(self.safe_scalars())
        persistent.update(sequences)
        persistent.update(encrypted)
        persistent.update(
            {
                "payload_b64": payload_features["payload_b64"],
                "payload_histogram": payload_features["payload_histogram"],
                "payload_bytes_stored": payload_features["payload_bytes_stored"],
                "sanitized_l4_b64": payload_features["sanitized_l4_b64"],
                "sanitized_l4_bytes_total": payload_features["sanitized_l4_bytes_total"],
                "sanitized_l4_bytes_stored": payload_features["sanitized_l4_bytes_stored"],
                "packet_count_stored": len(sequences["packet_length_seq"]),
                "port_a": int(self.canonical_key[2]),
                "port_b": int(self.canonical_key[3]),
                "application_protocol_hint": application_hint,
            }
        )
        if set(persistent) != set(ONLINE_EXTRACTABLE_COLUMNS):
            missing = sorted(set(ONLINE_EXTRACTABLE_COLUMNS) - set(persistent))
            extra = sorted(set(persistent) - set(ONLINE_EXTRACTABLE_COLUMNS))
            raise UnifiedFeatureReservoirError(
                "persistent feature shape drift: missing={} extra={}".format(missing, extra)
            )
        start_ns = int(round(self.first_timestamp * 1_000_000_000.0))
        end_ns = int(round(self.last_timestamp * 1_000_000_000.0))
        return UnifiedFlowFeatureRecord(
            flow_key=self.canonical_key,
            flow_key_hash=hashlib.sha256(
                json.dumps(self.canonical_key, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            flow_segment_index=self.segment_index,
            flow_start_ns=start_ns,
            flow_end_ns=end_ns,
            safe_scalars={name: persistent[name] for name in SAFE_SCALAR_COLUMNS},
            packet_sequences=sequences,
            payload_features=payload_features,
            encrypted_protocol_structure=encrypted,
            persistent_features=persistent,
            packet_interaction_graph={"nodes": graph_nodes, "edges": tuple(graph_edges)},
            derived_features=derived,
            quality={
                "persistent_schema_column_count": UNIFIED_PCAP_COLUMN_COUNT,
                "online_extractable_column_count": len(ONLINE_EXTRACTABLE_COLUMNS),
                "model_candidate_persistent_column_count": len(
                    MODEL_CANDIDATE_PERSISTENT_COLUMNS
                ),
                "safe_scalar_count": len(SAFE_SCALAR_COLUMNS),
                "sequence_column_count": len(SEQUENCE_COLUMNS),
                "sequence_complete": sequence_complete,
                "payload_histogram_complete": self.deep_observed and payload_complete,
                "deep_tier_selected": self.deep_observed,
                "median_exact": self.packet_count <= self.packet_lengths.median_sample_limit,
                "missingness": missingness,
            },
        )


def validate_reservoir_policy(policy: Mapping[str, Any]) -> None:
    expected = {
        "schema_version", "scope", "policy_id", "source_contracts", "flow_semantics",
        "feature_contract", "context_contract", "qualification_boundaries",
    }
    if set(policy) != expected or policy.get("schema_version") != 1 or policy.get("scope") != RESERVOIR_POLICY_SCOPE:
        raise UnifiedFeatureReservoirError("unified feature reservoir policy envelope is invalid")
    source = policy.get("source_contracts")
    if source != {
        "caeos_schema_sha256": CAEOS_SCHEMA_SHA256,
        "caeos_feature_views_sha256": CAEOS_FEATURE_VIEWS_SHA256,
    }:
        raise UnifiedFeatureReservoirError("CAEOS feature source contract drifted")
    semantics = policy.get("flow_semantics")
    if not isinstance(semantics, Mapping) or set(semantics) != {
        "flow_idle_timeout_seconds", "activity_idle_threshold_seconds",
        "maximum_packets_stored", "payload_prefix_bytes", "sanitized_l4_prefix_bytes",
    }:
        raise UnifiedFeatureReservoirError("flow semantic contract is invalid")
    if semantics.get("flow_idle_timeout_seconds") != 30.0 or semantics.get("activity_idle_threshold_seconds") != 5.0:
        raise UnifiedFeatureReservoirError("flow timeout semantics must match CAEOS v4")
    if semantics.get("maximum_packets_stored") != 64 or semantics.get("payload_prefix_bytes") != 4096 or semantics.get("sanitized_l4_prefix_bytes") != 2048:
        raise UnifiedFeatureReservoirError("bounded feature reservoir dimensions drifted")
    feature = policy.get("feature_contract")
    if feature != {
        "persistent_schema_column_count": UNIFIED_PCAP_COLUMN_COUNT,
        "online_extractable_column_count": len(ONLINE_EXTRACTABLE_COLUMNS),
        "model_candidate_persistent_column_count": len(
            MODEL_CANDIDATE_PERSISTENT_COLUMNS
        ),
        "audit_only_column_count": len(AUDIT_ONLY_COLUMNS),
        "target_column_count": len(TARGET_COLUMNS),
        "derived_feature_count": len(DERIVED_FEATURE_COLUMNS),
        "safe_scalar_count": 85,
        "sequence_column_count": 17,
        "encrypted_structure_count": 8,
        "payload_histogram_bins": 256,
        "deep_features_budgeted": True,
        "forbid_identifier_features_in_model": True,
    }:
        raise UnifiedFeatureReservoirError("feature count or safety contract drifted")
    context = policy.get("context_contract")
    if context != {"window_seconds": 1.0, "context_feature_count": len(CONTEXT_COLUMNS), "raw_endpoint_identifiers_emitted": False}:
        raise UnifiedFeatureReservoirError("network context contract drifted")
    if policy.get("qualification_boundaries") != {
        "reference_semantics_are_high_speed_performance_proof": False,
        "rust_parity_benchmark_required": True,
        "hardware_experiment_required": True,
    }:
        raise UnifiedFeatureReservoirError("qualification boundaries drifted")


def default_reservoir_policy() -> Mapping[str, Any]:
    """Return the embedded policy used when no external policy is supplied."""

    return {
        "schema_version": 1,
        "scope": RESERVOIR_POLICY_SCOPE,
        "policy_id": "HFT_MGBS_UNIFIED_FEATURE_RESERVOIR_V1",
        "source_contracts": {
            "caeos_schema_sha256": CAEOS_SCHEMA_SHA256,
            "caeos_feature_views_sha256": CAEOS_FEATURE_VIEWS_SHA256,
        },
        "flow_semantics": {
            "flow_idle_timeout_seconds": 30.0,
            "activity_idle_threshold_seconds": 5.0,
            "maximum_packets_stored": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
        },
        "feature_contract": {
            "persistent_schema_column_count": UNIFIED_PCAP_COLUMN_COUNT,
            "online_extractable_column_count": len(ONLINE_EXTRACTABLE_COLUMNS),
            "model_candidate_persistent_column_count": len(
                MODEL_CANDIDATE_PERSISTENT_COLUMNS
            ),
            "audit_only_column_count": len(AUDIT_ONLY_COLUMNS),
            "target_column_count": len(TARGET_COLUMNS),
            "derived_feature_count": len(DERIVED_FEATURE_COLUMNS),
            "safe_scalar_count": 85,
            "sequence_column_count": 17,
            "encrypted_structure_count": 8,
            "payload_histogram_bins": 256,
            "deep_features_budgeted": True,
            "forbid_identifier_features_in_model": True,
        },
        "context_contract": {
            "window_seconds": 1.0,
            "context_feature_count": len(CONTEXT_COLUMNS),
            "raw_endpoint_identifiers_emitted": False,
        },
        "qualification_boundaries": {
            "reference_semantics_are_high_speed_performance_proof": False,
            "rust_parity_benchmark_required": True,
            "hardware_experiment_required": True,
        },
    }


class UnifiedFeatureReservoir:
    """Stateful flow, sequence, payload and context feature closure."""

    def __init__(self, policy: Mapping[str, Any]) -> None:
        validate_reservoir_policy(policy)
        semantics = policy["flow_semantics"]
        self.policy = dict(policy)
        self.policy_sha256 = _canonical_sha256(policy)
        self.idle_timeout_s = float(semantics["flow_idle_timeout_seconds"])
        self.activity_idle_threshold_s = float(semantics["activity_idle_threshold_seconds"])
        self.max_sequence_packets = int(semantics["maximum_packets_stored"])
        self.payload_prefix_bytes = int(semantics["payload_prefix_bytes"])
        self.sanitized_prefix_bytes = int(semantics["sanitized_l4_prefix_bytes"])
        self.window_seconds = float(policy["context_contract"]["window_seconds"])
        self._flows: Dict[FlowKey, _FlowState] = {}
        self._continuations: Dict[FlowKey, int] = {}

    @staticmethod
    def canonical_key(packet: PacketRecord) -> FlowKey:
        key = packet.flow_key
        reverse = (key[1], key[0], key[3], key[2], key[4])
        return key if key <= reverse else reverse

    @staticmethod
    def _validate_metadata(value: PacketMetadata) -> None:
        if value.ip_version not in (0, 4, 6):
            raise UnifiedFeatureReservoirError("packet metadata ip_version is invalid")
        limits = {
            "ip_length": (value.ip_length, 0, 2**32 - 1),
            "ip_dscp_ecn": (value.ip_dscp_ecn, 0, 255),
            "ip_flags": (value.ip_flags, 0, 255),
            "ip_fragment_offset": (value.ip_fragment_offset, 0, 65535),
            "ip_fragment_id": (value.ip_fragment_id, 0, 2**32 - 1),
            "transport_header_length": (value.transport_header_length, 0, 255),
            "tcp_sequence": (value.tcp_sequence, 0, 2**32 - 1),
            "tcp_acknowledgement": (value.tcp_acknowledgement, 0, 2**32 - 1),
            "packet_ttl": (value.packet_ttl, 0, 255),
            "tcp_window": (value.tcp_window, 0, 65535),
        }
        for name, (item, minimum, maximum) in limits.items():
            if isinstance(item, bool) or not isinstance(item, int) or not minimum <= item <= maximum:
                raise UnifiedFeatureReservoirError(
                    "packet metadata {} is outside [{}, {}]".format(name, minimum, maximum)
                )
        if not isinstance(value.sanitized_l4, bytes):
            raise UnifiedFeatureReservoirError("sanitized_l4 must be bytes")
        if value.sanitized_l4_total is not None and (
            isinstance(value.sanitized_l4_total, bool)
            or not isinstance(value.sanitized_l4_total, int)
            or value.sanitized_l4_total < len(value.sanitized_l4)
        ):
            raise UnifiedFeatureReservoirError("sanitized_l4_total is invalid")

    @staticmethod
    def _validate_packet(value: PacketRecord) -> None:
        if not math.isfinite(float(value.timestamp)) or value.timestamp < 0:
            raise UnifiedFeatureReservoirError("packet timestamp is invalid")
        if not 0 <= value.src_port <= 65535 or not 0 <= value.dst_port <= 65535:
            raise UnifiedFeatureReservoirError("packet port is invalid")
        if not 0 <= value.protocol <= 255 or value.wire_length < 0:
            raise UnifiedFeatureReservoirError("packet protocol or length is invalid")
        if not isinstance(value.payload, bytes) or value.actual_payload_length < len(value.payload):
            raise UnifiedFeatureReservoirError("packet payload evidence is invalid")

    def _new_state(self, packet: PacketRecord, key: FlowKey) -> _FlowState:
        return _FlowState(
            canonical_key=key,
            first_directional_key=packet.flow_key,
            first_timestamp=float(packet.timestamp),
            last_timestamp=float(packet.timestamp),
            max_sequence_packets=self.max_sequence_packets,
            payload_prefix_bytes=self.payload_prefix_bytes,
            sanitized_prefix_bytes=self.sanitized_prefix_bytes,
            segment_index=self._continuations.pop(key, 0),
        )

    def observe_batch(
        self,
        packets: Sequence[PacketRecord],
        metadata: Sequence[PacketMetadata] = (),
        *,
        deep_flow_keys: Iterable[FlowKey] = (),
    ) -> ReservoirBatchResult:
        if metadata and len(metadata) != len(packets):
            raise UnifiedFeatureReservoirError("packet metadata count must equal parsed packet count")
        sidecars = tuple(metadata) if metadata else tuple(PacketMetadata() for _ in packets)
        for packet, sidecar in zip(packets, sidecars):
            if not isinstance(packet, PacketRecord) or not isinstance(sidecar, PacketMetadata):
                raise UnifiedFeatureReservoirError("reservoir input types are invalid")
            self._validate_packet(packet)
            self._validate_metadata(sidecar)
        deep = frozenset(deep_flow_keys)
        observed: List[FlowKey] = []
        completed_records: List[UnifiedFlowFeatureRecord] = []
        windows: Dict[int, Dict[str, Any]] = {}
        for packet, sidecar in zip(packets, sidecars):
            key = self.canonical_key(packet)
            state = self._flows.get(key)
            idle_split = (
                state is not None
                and float(packet.timestamp) - state.last_timestamp > self.idle_timeout_s
            )
            if idle_split:
                completed_records.append(state.record())
                self._flows.pop(key, None)
                self._continuations.pop(key, None)
                state = None
            created = state is None
            if state is None:
                state = self._new_state(packet, key)
                self._flows[key] = state
            state.update(
                packet, sidecar, deep=key in deep,
                activity_idle_threshold_s=self.activity_idle_threshold_s,
            )
            if key not in observed:
                observed.append(key)
            if state.packet_count >= self.max_sequence_packets:
                completed_records.append(state.record())
                self._flows.pop(key, None)
                self._continuations[key] = state.segment_index + 1
            window_id = int(float(packet.timestamp) // self.window_seconds)
            window = windows.setdefault(
                window_id,
                {
                    "packets": 0, "bytes": 0, "flows": set(), "new_flows": set(), "protocols": Counter(),
                    "ports": Counter(), "syn": 0, "rst": 0,
                    "peers": defaultdict(set), "endpoint_ports": defaultdict(set),
                },
            )
            window["packets"] += 1
            window["bytes"] += max(0, packet.wire_length)
            window["flows"].add(key)
            if created:
                window["new_flows"].add(key)
            window["protocols"][packet.protocol] += 1
            service_port = packet.dst_port if packet.dst_port <= 1024 else packet.src_port if packet.src_port <= 1024 else 0
            window["ports"][service_port] += 1
            window["syn"] += int(bool(packet.tcp_flags & 0x02))
            window["rst"] += int(bool(packet.tcp_flags & 0x04))
            window["peers"][packet.src_ip].add(packet.dst_ip)
            window["endpoint_ports"][packet.src_ip].add(packet.dst_port)

        active_records = [
            self._flows[key].record() for key in observed if key in self._flows
        ]
        records = tuple(completed_records + active_records)
        context_records = []
        for window_id, value in sorted(windows.items()):
            packet_count = value["packets"]
            context = {
                "window_id": window_id,
                "window_start_s": window_id * self.window_seconds,
                "window_packet_count": packet_count,
                "window_byte_count": value["bytes"],
                "window_flow_count": len(value["flows"]),
                "window_protocol_entropy": _entropy(value["protocols"]),
                "window_service_port_entropy": _entropy(value["ports"]),
                "window_syn_rate": _ratio(value["syn"], packet_count),
                "window_rst_rate": _ratio(value["rst"], packet_count),
                "window_endpoint_max_fanout": max((len(peers) for peers in value["peers"].values()), default=0),
                "window_endpoint_max_unique_ports": max((len(ports) for ports in value["endpoint_ports"].values()), default=0),
                "window_new_flow_rate": len(value["new_flows"]) / self.window_seconds,
            }
            if set(context) - {"window_id", "window_start_s"} != set(CONTEXT_COLUMNS):
                raise UnifiedFeatureReservoirError("window context shape drifted")
            context_records.append(context)
        safe_complete = all(set(record.safe_scalars) == set(SAFE_SCALAR_COLUMNS) for record in records)
        sequence_complete = all(set(record.packet_sequences) == set(SEQUENCE_COLUMNS) for record in records)
        persistent_complete = all(
            set(record.persistent_features) == set(ONLINE_EXTRACTABLE_COLUMNS)
            for record in records
        )
        deep_count = sum(record.quality["deep_tier_selected"] for record in records)
        receipt: Dict[str, Any] = {
            "schema_version": 1,
            "scope": RESERVOIR_RECEIPT_SCOPE,
            "policy_id": self.policy["policy_id"],
            "policy_sha256": self.policy_sha256,
            "parsed_packets": len(packets),
            "observed_flows": len(observed),
            "observed_flow_segments": len(records),
            "feature_records": len(records),
            "persistent_schema_column_count": UNIFIED_PCAP_COLUMN_COUNT,
            "online_extractable_column_count": len(ONLINE_EXTRACTABLE_COLUMNS),
            "model_candidate_persistent_column_count": len(
                MODEL_CANDIDATE_PERSISTENT_COLUMNS
            ),
            "safe_scalar_count": len(SAFE_SCALAR_COLUMNS),
            "sequence_column_count": len(SEQUENCE_COLUMNS),
            "encrypted_structure_count": len(ENCRYPTED_STRUCTURE_COLUMNS),
            "audit_only_column_count": len(AUDIT_ONLY_COLUMNS),
            "target_column_count": len(TARGET_COLUMNS),
            "derived_feature_count": len(DERIVED_FEATURE_COLUMNS),
            "context_feature_count": len(CONTEXT_COLUMNS),
            "deep_selected_flows": deep_count,
            "deep_deferred_flows": len(records) - deep_count,
            "conservation": {
                "one_record_per_observed_flow_segment": len(records)
                == len(completed_records) + len(active_records),
                "every_observed_flow_represented": {
                    record.flow_key for record in records
                }
                == set(observed),
                "safe_scalar_shape": safe_complete,
                "packet_sequence_shape": sequence_complete,
                "persistent_feature_shape": persistent_complete,
                "deep_tier_partition": deep_count + (len(records) - deep_count) == len(records),
                "raw_identifiers_not_emitted_in_context": True,
            },
            "semantic_parity": {
                "caeos_schema_sha256": CAEOS_SCHEMA_SHA256,
                "caeos_feature_views_sha256": CAEOS_FEATURE_VIEWS_SHA256,
                "flow_idle_timeout_seconds": self.idle_timeout_s,
                "activity_idle_threshold_seconds": self.activity_idle_threshold_s,
                "maximum_packets_stored": self.max_sequence_packets,
                "payload_prefix_bytes": self.payload_prefix_bytes,
                "sanitized_l4_prefix_bytes": self.sanitized_prefix_bytes,
            },
            "feature_reservoir_closed": bool(records or not observed)
            and {record.flow_key for record in records} == set(observed)
            and safe_complete
            and sequence_complete
            and persistent_complete,
            "rust_hotpath_parity_qualified": False,
            "hardware_experiment_required": True,
            "final_pareto_ingestion_allowed": False,
        }
        receipt["receipt_sha256"] = _canonical_sha256(receipt)
        return ReservoirBatchResult(records, tuple(context_records), receipt)
