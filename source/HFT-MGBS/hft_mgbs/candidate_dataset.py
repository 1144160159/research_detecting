"""Candidate-faithful flow samples for grouped and independent quality probes."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Callable, Dict, List, Mapping, Optional, Tuple

from .batching import bounded_batches
from .features import MultiGranularityExtractor
from .pcap import PcapFileReader
from .pipeline import AdaptiveExtractionPipeline


def is_key_flow(flow_key, ratio: float) -> bool:
    if ratio <= 0:
        return False
    digest = hashlib.sha256(repr(flow_key).encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return value < ratio


def extract_candidate_flow_records(
    pcap_path: str,
    group: str,
    batch_size: int = 512,
    budget_us: float = 5000.0,
    allow_deep: bool = True,
    key_flow_ratio: float = 0.10,
    max_payload_bytes: int = 256,
    max_packets: int = 20000,
    max_flows: int = 2000,
    execution_budget_safety_ratio: float = 0.75,
    flow_record_observer: Optional[
        Callable[[Mapping[str, object]], None]
    ] = None,
) -> Tuple[List[Mapping[str, object]], Mapping[str, object]]:
    pipeline = AdaptiveExtractionPipeline(
        execution_budget_safety_ratio=execution_budget_safety_ratio
    )
    emitted_by_key: Dict[Tuple, Dict[str, float]] = {}
    tier_rank = {"base": 0, "flow": 1, "deep": 2}
    tier_counts: Counter = Counter()
    budget_overruns = 0
    key_total = 0
    key_covered = 0
    key_coverage_min = 1.0
    max_actual_optional_cost_us = 0.0
    packet_start_timestamp = None
    packet_last_timestamp = None
    batch_audits = []
    with PcapFileReader(
        pcap_path, max_payload_bytes=max_payload_bytes
    ) as reader:
        for packet_batch in bounded_batches(
            reader, batch_size, max_packets
        ):
            batch_start = min(packet.timestamp for packet in packet_batch)
            batch_last = max(packet.timestamp for packet in packet_batch)
            packet_start_timestamp = (
                batch_start
                if packet_start_timestamp is None
                else min(packet_start_timestamp, batch_start)
            )
            packet_last_timestamp = (
                batch_last
                if packet_last_timestamp is None
                else max(packet_last_timestamp, batch_last)
            )
            flow_keys = {
                pipeline.extractor.canonical_key(packet) for packet in packet_batch
            }
            key_flows = {
                key for key in flow_keys if is_key_flow(key, key_flow_ratio)
            }
            results = pipeline.process_batch(
                packet_batch,
                budget_us=budget_us,
                allow_deep=allow_deep,
                key_flows=key_flows,
            )
            plan = pipeline.last_schedule_plan
            budget_overruns += plan.budget_overrun_count
            key_total += plan.key_flow_total
            key_covered += plan.key_flow_covered
            key_coverage_min = min(
                key_coverage_min, plan.key_flow_coverage
            )
            max_actual_optional_cost_us = max(
                max_actual_optional_cost_us, plan.actual_used_us
            )
            batch_audits.append(
                {
                    "batch_index": len(batch_audits),
                    "packet_count": len(packet_batch),
                    "key_flow_total": plan.key_flow_total,
                    "key_flow_covered": plan.key_flow_covered,
                    "budget_overrun_count": plan.budget_overrun_count,
                    "actual_used_us": plan.actual_used_us,
                }
            )
            for result in results:
                tier_counts[result.tier] += 1
                record = emitted_by_key.setdefault(result.flow_key, {})
                for name, value in result.features.items():
                    if name.startswith("flow_"):
                        continue
                    if name.startswith("payload_") and result.tier != "deep":
                        continue
                    record[name] = float(value)
                rank = tier_rank[result.tier]
                record["quality_seen_flow_tier"] = max(
                    record.get("quality_seen_flow_tier", 0.0),
                    float(rank >= 1),
                )
                record["quality_seen_deep_tier"] = max(
                    record.get("quality_seen_deep_tier", 0.0),
                    float(rank >= 2),
                )
        pcap_stats = reader.stats

    samples = []
    for flow_record in pipeline.extractor.flow_records():
        forward_key = tuple(flow_record["forward_key"])
        canonical_key = MultiGranularityExtractor.normalize_flow_key(forward_key)
        features = dict(emitted_by_key.get(canonical_key, {}))
        if features.get("quality_seen_flow_tier", 0.0):
            features.update(flow_record["features"])
        sample = {
            "forward_key": forward_key,
            "start_timestamp": flow_record["start_timestamp"],
            "last_timestamp": flow_record["last_timestamp"],
            "features": features,
        }
        samples.append(sample)
        if flow_record_observer is not None:
            flow_record_observer(sample)
    samples.sort(
        key=lambda item: hashlib.sha256(
            (
                group
                + repr(item["forward_key"])
                + repr(item["start_timestamp"])
            ).encode("utf-8")
        ).digest()
    )
    selected = samples[:max_flows]
    summary = {
        "group": group,
        "path": pcap_path,
        "execution_budget_safety_ratio": execution_budget_safety_ratio,
        "parsed_packets": pcap_stats.parsed_packets,
        "rejected_records": pcap_stats.rejected_records,
        "packet_start_timestamp": packet_start_timestamp,
        "packet_last_timestamp": packet_last_timestamp,
        "flow_records": len(samples),
        "selected_flows": len(selected),
        "budget_overrun_count": budget_overruns,
        "key_flow_total": key_total,
        "key_flow_covered": key_covered,
        "key_flow_coverage": 1.0
        if key_total == 0
        else key_covered / key_total,
        "key_flow_coverage_min": key_coverage_min,
        "max_actual_optional_cost_us": max_actual_optional_cost_us,
        "batch_audits": batch_audits,
        "tier_counts": {
            tier: tier_counts.get(tier, 0)
            for tier in ("base", "flow", "deep")
        },
    }
    return selected, summary
