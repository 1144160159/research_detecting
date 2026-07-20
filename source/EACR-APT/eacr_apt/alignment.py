"""Interpretable cross-source candidate alignment baseline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .schema import Event


@dataclass(frozen=True)
class AlignmentCandidate:
    left_event_id: str
    right_event_id: str
    score: float
    components: Dict[str, float]


def _same_nonempty(left: Optional[str], right: Optional[str]) -> bool:
    return left is not None and right is not None and left != "" and left == right


def _network_match(left: Event, right: Event) -> float:
    direct = (
        _same_nonempty(left.src_ip, right.src_ip)
        and _same_nonempty(left.dst_ip, right.dst_ip)
        and left.src_port == right.src_port
        and left.dst_port == right.dst_port
    )
    reverse = (
        _same_nonempty(left.src_ip, right.dst_ip)
        and _same_nonempty(left.dst_ip, right.src_ip)
        and left.src_port == right.dst_port
        and left.dst_port == right.src_port
    )
    if direct:
        return 1.0
    if reverse:
        return 0.9
    if _same_nonempty(left.dst_ip, right.dst_ip):
        return 0.35
    return 0.0


def score_event_pair(
    left: Event,
    right: Event,
    max_time_delta_ns: int = 30_000_000_000,
) -> AlignmentCandidate:
    if left.event_id == right.event_id:
        raise ValueError("cannot align an event to itself")
    if left.modality == right.modality:
        raise ValueError("alignment is defined across different modalities")
    if max_time_delta_ns <= 0:
        raise ValueError("max_time_delta_ns must be positive")

    delta = abs(left.ts_utc_ns - right.ts_utc_ns)
    tolerance = max_time_delta_ns + left.ts_uncertainty_ns + right.ts_uncertainty_ns
    time_score = max(0.0, 1.0 - float(delta) / float(max(1, tolerance)))
    host_score = 1.0 if _same_nonempty(left.host_id, right.host_id) else 0.0

    identifier_hits = (
        _same_nonempty(left.process_guid, right.process_guid),
        _same_nonempty(left.session_id, right.session_id),
        _same_nonempty(left.user_id, right.user_id),
    )
    identifier_score = sum(1.0 for hit in identifier_hits if hit) / 3.0
    network_score = _network_match(left, right)

    components = {
        "time": time_score,
        "host": host_score,
        "identifier": identifier_score,
        "network": network_score,
    }
    score = (
        0.35 * time_score
        + 0.20 * host_score
        + 0.25 * identifier_score
        + 0.20 * network_score
    )
    return AlignmentCandidate(
        left_event_id=left.event_id,
        right_event_id=right.event_id,
        score=min(1.0, max(0.0, score)),
        components=components,
    )


def accept_candidate(
    best: AlignmentCandidate,
    second_best_score: Optional[float] = None,
    threshold: float = 0.65,
    min_margin: float = 0.10,
) -> Tuple[bool, str]:
    if best.score < threshold:
        return False, "below_threshold"
    if second_best_score is not None and best.score - second_best_score < min_margin:
        return False, "ambiguous"
    return True, "accepted"
