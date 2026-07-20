"""Allocation-conscious streaming feature extraction at packet, flow and window levels."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from math import log2
from typing import Deque, DefaultDict, Dict, Hashable, Iterable, List, Mapping, Optional, Tuple


FlowKey = Tuple[str, str, int, int, int]
TCP_FLAG_NAMES = ("fin", "syn", "rst", "psh", "ack", "urg", "ece", "cwr")


@dataclass(frozen=True)
class PacketRecord:
    timestamp: float
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: int
    wire_length: int
    payload: bytes = b""
    tcp_flags: int = 0
    payload_length: Optional[int] = None

    @property
    def flow_key(self) -> FlowKey:
        return (self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol)

    @property
    def actual_payload_length(self) -> int:
        return len(self.payload) if self.payload_length is None else self.payload_length


@dataclass
class _FlowState:
    forward_key: FlowKey
    first_ts: float
    last_ts: float
    packets: int = 0
    bytes: int = 0
    payload_bytes: int = 0
    min_length: int = 2**31 - 1
    max_length: int = 0
    length_sum_sq: float = 0.0
    iat_sum: float = 0.0
    iat_sum_sq: float = 0.0
    tcp_flags_or: int = 0
    fwd_packets: int = 0
    bwd_packets: int = 0
    fwd_bytes: int = 0
    bwd_bytes: int = 0
    fwd_payload_bytes: int = 0
    bwd_payload_bytes: int = 0
    fwd_iat_sum: float = 0.0
    bwd_iat_sum: float = 0.0
    fwd_iat_sum_sq: float = 0.0
    bwd_iat_sum_sq: float = 0.0
    last_fwd_ts: Optional[float] = None
    last_bwd_ts: Optional[float] = None
    fwd_tcp_flags_or: int = 0
    bwd_tcp_flags_or: int = 0
    fwd_fin_seen: bool = False
    bwd_fin_seen: bool = False
    rst_seen: bool = False
    tcp_flag_counts: List[int] = field(default_factory=lambda: [0] * 8)
    fwd_tcp_flag_counts: List[int] = field(default_factory=lambda: [0] * 8)
    bwd_tcp_flag_counts: List[int] = field(default_factory=lambda: [0] * 8)

    def update(self, packet: PacketRecord, is_forward: bool) -> None:
        if self.packets:
            iat = max(0.0, packet.timestamp - self.last_ts)
            self.iat_sum += iat
            self.iat_sum_sq += iat * iat
        length = max(0, packet.wire_length)
        self.last_ts = max(self.last_ts, packet.timestamp)
        self.packets += 1
        self.bytes += length
        payload_length = packet.actual_payload_length
        self.payload_bytes += payload_length
        self.min_length = min(self.min_length, length)
        self.max_length = max(self.max_length, length)
        self.length_sum_sq += length * length
        self.tcp_flags_or |= packet.tcp_flags
        if is_forward:
            if self.last_fwd_ts is not None:
                directional_iat = max(0.0, packet.timestamp - self.last_fwd_ts)
                self.fwd_iat_sum += directional_iat
                self.fwd_iat_sum_sq += directional_iat * directional_iat
            self.last_fwd_ts = max(self.last_fwd_ts or packet.timestamp, packet.timestamp)
            self.fwd_packets += 1
            self.fwd_bytes += length
            self.fwd_payload_bytes += payload_length
            self.fwd_tcp_flags_or |= packet.tcp_flags
            self.fwd_fin_seen = self.fwd_fin_seen or bool(packet.tcp_flags & 0x01)
        else:
            if self.last_bwd_ts is not None:
                directional_iat = max(0.0, packet.timestamp - self.last_bwd_ts)
                self.bwd_iat_sum += directional_iat
                self.bwd_iat_sum_sq += directional_iat * directional_iat
            self.last_bwd_ts = max(self.last_bwd_ts or packet.timestamp, packet.timestamp)
            self.bwd_packets += 1
            self.bwd_bytes += length
            self.bwd_payload_bytes += payload_length
            self.bwd_tcp_flags_or |= packet.tcp_flags
            self.bwd_fin_seen = self.bwd_fin_seen or bool(packet.tcp_flags & 0x01)
        self.rst_seen = self.rst_seen or bool(packet.tcp_flags & 0x04)
        directional_counts = self.fwd_tcp_flag_counts if is_forward else self.bwd_tcp_flag_counts
        remaining_flags = packet.tcp_flags & 0xFF
        while remaining_flags:
            lowest_bit = remaining_flags & -remaining_flags
            index = lowest_bit.bit_length() - 1
            self.tcp_flag_counts[index] += 1
            directional_counts[index] += 1
            remaining_flags ^= lowest_bit

    def should_rollover(
        self,
        packet: PacketRecord,
        activity_timeout_s: float,
        max_flow_duration_s: float,
    ) -> bool:
        return (
            packet.timestamp - self.last_ts > activity_timeout_s
            or packet.timestamp - self.first_ts > max_flow_duration_s
            or (self.fwd_fin_seen and self.bwd_fin_seen)
            or self.rst_seen
        )

    def features(self) -> Dict[str, float]:
        count = max(1, self.packets)
        duration = max(0.0, self.last_ts - self.first_ts)
        mean_length = self.bytes / count
        length_var = max(0.0, self.length_sum_sq / count - mean_length * mean_length)
        iat_count = max(1, self.packets - 1)
        mean_iat = self.iat_sum / iat_count
        iat_var = max(0.0, self.iat_sum_sq / iat_count - mean_iat * mean_iat)
        fwd_iat_count = max(1, self.fwd_packets - 1)
        bwd_iat_count = max(1, self.bwd_packets - 1)
        fwd_mean_iat = self.fwd_iat_sum / fwd_iat_count
        bwd_mean_iat = self.bwd_iat_sum / bwd_iat_count
        fwd_iat_var = max(
            0.0, self.fwd_iat_sum_sq / fwd_iat_count - fwd_mean_iat * fwd_mean_iat
        )
        bwd_iat_var = max(
            0.0, self.bwd_iat_sum_sq / bwd_iat_count - bwd_mean_iat * bwd_mean_iat
        )
        output = {
            "flow_packets": float(self.packets),
            "flow_bytes": float(self.bytes),
            "flow_payload_bytes": float(self.payload_bytes),
            "flow_duration_s": duration,
            "flow_mean_length": mean_length,
            "flow_length_std": length_var**0.5,
            "flow_min_length": float(0 if self.min_length == 2**31 - 1 else self.min_length),
            "flow_max_length": float(self.max_length),
            "flow_mean_iat_s": mean_iat,
            "flow_iat_std_s": iat_var**0.5,
            "flow_tcp_flags_or": float(self.tcp_flags_or),
            "flow_fwd_packets": float(self.fwd_packets),
            "flow_bwd_packets": float(self.bwd_packets),
            "flow_fwd_bytes": float(self.fwd_bytes),
            "flow_bwd_bytes": float(self.bwd_bytes),
            "flow_fwd_payload_bytes": float(self.fwd_payload_bytes),
            "flow_bwd_payload_bytes": float(self.bwd_payload_bytes),
            "flow_fwd_mean_iat_s": fwd_mean_iat,
            "flow_bwd_mean_iat_s": bwd_mean_iat,
            "flow_fwd_iat_std_s": fwd_iat_var**0.5,
            "flow_bwd_iat_std_s": bwd_iat_var**0.5,
            "flow_fwd_tcp_flags_or": float(self.fwd_tcp_flags_or),
            "flow_bwd_tcp_flags_or": float(self.bwd_tcp_flags_or),
        }
        for index, name in enumerate(TCP_FLAG_NAMES):
            output["flow_{}_flag_count".format(name)] = float(self.tcp_flag_counts[index])
            output["flow_fwd_{}_flag_count".format(name)] = float(
                self.fwd_tcp_flag_counts[index]
            )
            output["flow_bwd_{}_flag_count".format(name)] = float(
                self.bwd_tcp_flag_counts[index]
            )
        return output


class MultiGranularityExtractor:
    """Maintains bounded flow/window state and exposes progressively costlier features."""

    def __init__(
        self,
        window_seconds: float = 1.0,
        max_active_flows: int = 100_000,
        activity_timeout_s: float = 300.0,
        max_flow_duration_s: float = 120.0,
        max_completed_flows: int = 100_000,
    ) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if max_active_flows <= 0:
            raise ValueError("max_active_flows must be positive")
        if activity_timeout_s <= 0 or max_flow_duration_s <= 0:
            raise ValueError("flow timeouts must be positive")
        if max_completed_flows <= 0:
            raise ValueError("max_completed_flows must be positive")
        self.window_seconds = window_seconds
        self.max_active_flows = max_active_flows
        self.activity_timeout_s = activity_timeout_s
        self.max_flow_duration_s = max_flow_duration_s
        self._flows: Dict[FlowKey, _FlowState] = {}
        self._completed_flows: Deque[_FlowState] = deque(maxlen=max_completed_flows)
        self._window_packets: DefaultDict[int, int] = defaultdict(int)
        self._window_bytes: DefaultDict[int, int] = defaultdict(int)

    @staticmethod
    def packet_features(packet: PacketRecord) -> Dict[str, float]:
        return {
            "packet_wire_length": float(max(0, packet.wire_length)),
            "packet_payload_length": float(len(packet.payload)),
            "packet_protocol": float(packet.protocol),
            "packet_src_port": float(packet.src_port),
            "packet_dst_port": float(packet.dst_port),
            "packet_tcp_flags": float(packet.tcp_flags),
        }

    def update(self, packet: PacketRecord, key: Optional[FlowKey] = None) -> None:
        directional_key = packet.flow_key
        key = self.normalize_flow_key(directional_key) if key is None else key
        state = self._flows.get(key)
        if state is not None and state.should_rollover(
            packet, self.activity_timeout_s, self.max_flow_duration_s
        ):
            self._completed_flows.append(state)
            del self._flows[key]
            state = None
        if state is None:
            if len(self._flows) >= self.max_active_flows:
                oldest = min(self._flows, key=lambda key: self._flows[key].last_ts)
                self._completed_flows.append(self._flows[oldest])
                del self._flows[oldest]
            state = _FlowState(
                forward_key=directional_key,
                first_ts=packet.timestamp,
                last_ts=packet.timestamp,
            )
            self._flows[key] = state
        state.update(packet, is_forward=directional_key == state.forward_key)
        window_id = int(packet.timestamp // self.window_seconds)
        self._window_packets[window_id] += 1
        self._window_bytes[window_id] += max(0, packet.wire_length)

    def flow_features(self, key: FlowKey) -> Dict[str, float]:
        state = self._flows.get(self.normalize_flow_key(key))
        return {} if state is None else state.features()

    @staticmethod
    def normalize_flow_key(key: FlowKey) -> FlowKey:
        reverse = (key[1], key[0], key[3], key[2], key[4])
        return key if key <= reverse else reverse

    @classmethod
    def canonical_key(cls, packet: PacketRecord) -> FlowKey:
        return cls.normalize_flow_key(packet.flow_key)

    def window_features(self, timestamp: float) -> Dict[str, float]:
        window_id = int(timestamp // self.window_seconds)
        packets = self._window_packets.get(window_id, 0)
        total_bytes = self._window_bytes.get(window_id, 0)
        return {
            "window_packets": float(packets),
            "window_bytes": float(total_bytes),
            "window_packets_per_s": packets / self.window_seconds,
            "window_bytes_per_s": total_bytes / self.window_seconds,
        }

    @staticmethod
    def deep_payload_features(payloads: Iterable[bytes]) -> Dict[str, float]:
        counts: Counter = Counter()
        total = 0
        printable = 0
        zeroes = 0
        for payload in payloads:
            counts.update(payload)
            total += len(payload)
            printable += sum(32 <= value <= 126 for value in payload)
            zeroes += payload.count(0)
        if total == 0:
            return {"payload_entropy": 0.0, "payload_printable_ratio": 0.0, "payload_zero_ratio": 0.0}
        entropy = -sum((count / total) * log2(count / total) for count in counts.values())
        return {
            "payload_entropy": entropy,
            "payload_printable_ratio": printable / total,
            "payload_zero_ratio": zeroes / total,
        }

    @property
    def active_flow_count(self) -> int:
        return len(self._flows)

    @property
    def completed_flow_count(self) -> int:
        return len(self._completed_flows)

    def flow_records(self, include_active: bool = True) -> List[Mapping[str, object]]:
        states = list(self._completed_flows)
        if include_active:
            states.extend(self._flows.values())
        return [
            {
                "forward_key": state.forward_key,
                "start_timestamp": state.first_ts,
                "last_timestamp": state.last_ts,
                "features": state.features(),
            }
            for state in states
        ]

    def drain_completed_flow_records(self) -> List[Mapping[str, object]]:
        records = self.flow_records(include_active=False)
        self._completed_flows.clear()
        return records
