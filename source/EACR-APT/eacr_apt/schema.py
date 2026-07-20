"""Unified observation schema.

Ground truth is intentionally represented separately from observations so that
ATT&CK labels and campaign identifiers cannot silently leak into model inputs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple


MODALITIES = frozenset(("endpoint", "log", "flow"))


@dataclass(frozen=True)
class Event:
    event_id: str
    ts_utc_ns: int
    ts_uncertainty_ns: int
    host_id: str
    sensor_id: str
    modality: str
    event_type: str
    actor_id: str
    object_id: str
    process_guid: Optional[str] = None
    parent_guid: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    src_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_ip: Optional[str] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    raw_ref: Optional[str] = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id must be non-empty")
        if self.modality not in MODALITIES:
            raise ValueError("unsupported modality: {}".format(self.modality))
        if self.ts_utc_ns < 0 or self.ts_uncertainty_ns < 0:
            raise ValueError("timestamps and uncertainty must be non-negative")
        for name, port in (("src_port", self.src_port), ("dst_port", self.dst_port)):
            if port is not None and not 0 <= port <= 65535:
                raise ValueError("{} out of range".format(name))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, record: Mapping[str, Any]) -> "Event":
        values = dict(record)
        for key in ("ts_utc_ns", "ts_uncertainty_ns"):
            values[key] = int(values[key])
        for key in ("src_port", "dst_port"):
            if values.get(key) not in (None, ""):
                values[key] = int(values[key])
            elif key in values:
                values[key] = None
        values.setdefault("attributes", {})
        return cls(**values)


@dataclass(frozen=True)
class ChainGroundTruth:
    """Evaluation-only chain truth; never merge these fields into Event."""

    chain_id: str
    campaign_id: str
    event_ids: Tuple[str, ...]
    tactic_sequence: Tuple[str, ...]
    source_ref: str

    def __post_init__(self) -> None:
        if not self.chain_id or not self.campaign_id:
            raise ValueError("chain_id and campaign_id must be non-empty")
        if not self.event_ids:
            raise ValueError("ground-truth chain must contain at least one event")
