"""Candidate representations adapted from the screened encrypted-traffic literature."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from .features import PacketRecord


def packet_length_sequence(packets: Sequence[PacketRecord], max_packets: int = 20) -> Dict[str, List[float]]:
    """Build a BERT-ps-style signed length/IAT sequence with an explicit mask.

    The first packet defines the forward endpoint pair. Reverse packets receive a
    negative signed length. The function is an independent interface adaptation;
    it does not copy BERT-ps implementation code.
    """
    if max_packets <= 0:
        raise ValueError("max_packets must be positive")
    if not packets:
        return {
            "signed_lengths": [0.0] * max_packets,
            "iat_us": [0.0] * max_packets,
            "mask": [0.0] * max_packets,
        }
    origin = (packets[0].src_ip, packets[0].src_port, packets[0].dst_ip, packets[0].dst_port)
    lengths: List[float] = []
    iats: List[float] = []
    mask: List[float] = []
    previous_ts = packets[0].timestamp
    for packet in packets[:max_packets]:
        direction = 1.0 if (packet.src_ip, packet.src_port, packet.dst_ip, packet.dst_port) == origin else -1.0
        lengths.append(direction * max(0, packet.wire_length))
        iats.append(max(0.0, packet.timestamp - previous_ts) * 1_000_000.0)
        mask.append(1.0)
        previous_ts = packet.timestamp
    padding = max_packets - len(lengths)
    if padding:
        lengths.extend([0.0] * padding)
        iats.extend([0.0] * padding)
        mask.extend([0.0] * padding)
    return {"signed_lengths": lengths, "iat_us": iats, "mask": mask}


def multi_level_vector(packets: Sequence[PacketRecord], max_packets: int = 20) -> Dict[str, List[float]]:
    """Compact packet/flow representation for YaTC/UniNet-style candidate experiments."""
    sequence = packet_length_sequence(packets, max_packets=max_packets)
    if not packets:
        sequence["flow_summary"] = [0.0] * 6
        return sequence
    lengths = [max(0, packet.wire_length) for packet in packets]
    duration = max(0.0, packets[-1].timestamp - packets[0].timestamp)
    payload_bytes = sum(packet.actual_payload_length for packet in packets)
    sequence["flow_summary"] = [
        float(len(packets)),
        float(sum(lengths)),
        float(min(lengths)),
        float(max(lengths)),
        float(payload_bytes),
        duration * 1_000_000.0,
    ]
    return sequence
