"""Strict UNSW-NB15 ground-truth alignment by bidirectional 5-tuple and time."""

from __future__ import annotations

import csv
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

from .features import FlowKey, MultiGranularityExtractor


PROTOCOL_NUMBERS = {"tcp": 6, "udp": 17}


@dataclass(frozen=True)
class AttackInterval:
    start_timestamp: float
    last_timestamp: float
    category: str
    event_id: int = -1


def _parse_port(value: str) -> Optional[int]:
    text = (value or "").strip()
    if not text:
        return None
    try:
        port = int(text, 10)
    except ValueError:
        return None
    return port if 0 <= port <= 65535 else None


def canonical_flow_key(
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    protocol: int,
) -> FlowKey:
    return MultiGranularityExtractor.normalize_flow_key(
        (src_ip.strip(), dst_ip.strip(), src_port, dst_port, protocol)
    )


class UnswGroundTruth:
    def __init__(
        self,
        intervals: Mapping[FlowKey, Iterable[AttackInterval]],
        parse_stats: Optional[Mapping[str, int]] = None,
    ) -> None:
        self._intervals: Dict[FlowKey, Tuple[AttackInterval, ...]] = {}
        self._starts: Dict[FlowKey, Tuple[float, ...]] = {}
        all_intervals: List[AttackInterval] = []
        for key, values in intervals.items():
            ordered = tuple(sorted(values, key=lambda item: item.start_timestamp))
            self._intervals[key] = ordered
            self._starts[key] = tuple(item.start_timestamp for item in ordered)
            all_intervals.extend(ordered)
        self._all_intervals = tuple(all_intervals)
        self.parse_stats = dict(parse_stats or {})

    @classmethod
    def from_csv(cls, path: Path) -> "UnswGroundTruth":
        intervals: Dict[FlowKey, List[AttackInterval]] = {}
        stats = {
            "rows_total": 0,
            "rows_indexed": 0,
            "rows_unsupported_protocol": 0,
            "rows_invalid_endpoint": 0,
            "rows_invalid_time": 0,
        }
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                stats["rows_total"] += 1
                protocol = PROTOCOL_NUMBERS.get((row.get("Protocol") or "").strip().lower())
                if protocol is None:
                    stats["rows_unsupported_protocol"] += 1
                    continue
                src_ip = (row.get("Source IP") or "").strip()
                dst_ip = (row.get("Destination IP") or "").strip()
                src_port = _parse_port(row.get("Source Port") or "")
                dst_port = _parse_port(row.get("Destination Port") or "")
                if not src_ip or not dst_ip or src_port is None or dst_port is None:
                    stats["rows_invalid_endpoint"] += 1
                    continue
                try:
                    start = float((row.get("Start time") or "").strip())
                    last = float((row.get("Last time") or "").strip())
                except ValueError:
                    stats["rows_invalid_time"] += 1
                    continue
                if last < start:
                    stats["rows_invalid_time"] += 1
                    continue
                key = canonical_flow_key(
                    src_ip, dst_ip, src_port, dst_port, protocol
                )
                intervals.setdefault(key, []).append(
                    AttackInterval(
                        start_timestamp=start,
                        last_timestamp=last,
                        category=(row.get("Attack category") or "unknown").strip(),
                        event_id=stats["rows_total"],
                    )
                )
                stats["rows_indexed"] += 1
        return cls(intervals, stats)

    @property
    def indexed_key_count(self) -> int:
        return len(self._intervals)

    def event_ids_overlapping(
        self,
        start_timestamp: float,
        last_timestamp: float,
        tolerance_s: float = 0.0,
    ) -> Tuple[int, ...]:
        """Return indexed GT event IDs overlapping an observed time span."""

        if tolerance_s < 0:
            raise ValueError("tolerance_s must be non-negative")
        if last_timestamp < start_timestamp:
            raise ValueError("last_timestamp must not precede start_timestamp")
        lower = start_timestamp - tolerance_s
        upper = last_timestamp + tolerance_s
        return tuple(
            interval.event_id
            for interval in self._all_intervals
            if interval.event_id >= 0
            and interval.start_timestamp <= upper
            and interval.last_timestamp >= lower
        )

    def matching_intervals(
        self,
        flow_key: FlowKey,
        start_timestamp: float,
        last_timestamp: float,
        tolerance_s: float = 0.0,
    ) -> Tuple[AttackInterval, ...]:
        if tolerance_s < 0:
            raise ValueError("tolerance_s must be non-negative")
        key = MultiGranularityExtractor.normalize_flow_key(flow_key)
        intervals = self._intervals.get(key, ())
        if not intervals:
            return ()
        starts = self._starts[key]
        stop = bisect_right(starts, last_timestamp + tolerance_s)
        lower = start_timestamp - tolerance_s
        return tuple(
            interval
            for interval in intervals[:stop]
            if interval.last_timestamp >= lower
        )

    def label_flow_record(
        self, record: Mapping[str, object], tolerance_s: float = 0.0
    ) -> int:
        raw_key = record["forward_key"]
        key = tuple(raw_key)
        if len(key) != 5:
            raise ValueError("forward_key must contain five fields")
        typed_key: FlowKey = (
            str(key[0]),
            str(key[1]),
            int(key[2]),
            int(key[3]),
            int(key[4]),
        )
        matches = self.matching_intervals(
            typed_key,
            float(record["start_timestamp"]),
            float(record["last_timestamp"]),
            tolerance_s=tolerance_s,
        )
        return int(bool(matches))
