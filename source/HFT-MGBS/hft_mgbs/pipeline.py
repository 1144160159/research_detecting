"""End-to-end progressive extraction pipeline."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, DefaultDict, Dict, Iterable, List, Mapping, Optional

from .features import FlowKey, MultiGranularityExtractor, PacketRecord
from .runtime import DeepPathCircuitBreaker
from .scheduler import (
    AdaptiveBudgetScheduler,
    ExtractionCandidate,
    ExtractionDecision,
    SchedulePlan,
)


@dataclass(frozen=True)
class PipelineResult:
    flow_key: FlowKey
    tier: str
    features: Mapping[str, float]


class AdaptiveExtractionPipeline:
    def __init__(
        self,
        extractor: Optional[MultiGranularityExtractor] = None,
        scheduler: Optional[AdaptiveBudgetScheduler] = None,
        circuit_breaker: Optional[DeepPathCircuitBreaker] = None,
        clock: Callable[[], float] = time.monotonic,
        cost_clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.extractor = extractor or MultiGranularityExtractor()
        self.scheduler = scheduler or AdaptiveBudgetScheduler()
        self.circuit_breaker = circuit_breaker or DeepPathCircuitBreaker()
        self.clock = clock
        self.cost_clock = cost_clock
        self.last_schedule_plan: Optional[SchedulePlan] = None
        self.last_deep_error: Optional[str] = None
        self.last_fallback_recovery_s: Optional[float] = None
        self.last_batch_runtime_us: Optional[float] = None
        self.last_stage_timings_us: Mapping[str, float] = {}

    def process_batch(
        self,
        packets: Iterable[PacketRecord],
        budget_us: float,
        allow_deep: bool = True,
        key_flows: Optional[Iterable[FlowKey]] = None,
    ) -> List[PipelineResult]:
        batch_started = self.cost_clock()
        by_flow: DefaultDict[FlowKey, List[PacketRecord]] = defaultdict(list)
        for packet in packets:
            key = self.extractor.canonical_key(packet)
            self.extractor.update(packet, key=key)
            by_flow[key].append(packet)
        state_update_finished = self.cost_clock()

        candidates = []
        priorities: Dict[FlowKey, float] = {}
        key_flow_set = {
            self.extractor.normalize_flow_key(key) for key in (key_flows or ())
        }
        for key, flow_packets in by_flow.items():
            total_bytes = sum(packet.wire_length for packet in flow_packets)
            payload_bytes = sum(len(packet.payload) for packet in flow_packets)
            # Favor large/payload-bearing flows while keeping a non-zero floor.
            priority = 1.0 + total_bytes / 1500.0 + payload_bytes / 512.0
            priorities[key] = priority
            candidates.append(
                ExtractionCandidate(key=key, priority=priority, is_key_flow=key in key_flow_set)
            )
        candidate_build_finished = self.cost_clock()

        breaker_allows_deep = self.circuit_breaker.allow_deep(self.clock()) if allow_deep else False
        effective_allow_deep = allow_deep and breaker_allows_deep
        recovery_probe = (
            effective_allow_deep and self.circuit_breaker.snapshot().state == "half_open"
        )
        planned = self.scheduler.plan_with_audit(
            candidates,
            budget_us,
            allow_deep=effective_allow_deep,
            recovery_probe=recovery_probe,
        )
        schedule_finished = self.cost_clock()
        decisions = {decision.key: decision for decision in planned.decisions}
        actual_tiers: Dict[FlowKey, str] = {}
        deep_available = effective_allow_deep
        deep_failure = False
        flow_costs_us: List[float] = []
        flow_utilities: List[float] = []
        deep_costs_us: List[float] = []
        deep_utilities: List[float] = []
        self.last_deep_error = None
        results: List[PipelineResult] = []
        for key, flow_packets in by_flow.items():
            last = flow_packets[-1]
            features: Dict[str, float] = self.extractor.packet_features(last)
            features.update(self.extractor.window_features(last.timestamp))
            decision = decisions.get(key)
            tier = "base"
            if decision is not None:
                tier = decision.tier
                flow_started = self.cost_clock()
                flow_features = self.extractor.flow_features(key)
                flow_costs_us.append((self.cost_clock() - flow_started) * 1_000_000.0)
                flow_utilities.append(priorities[key])
                features.update(flow_features)
                if tier == "deep":
                    if deep_available:
                        try:
                            deep_started = self.cost_clock()
                            deep_features = self.extractor.deep_payload_features(
                                packet.payload for packet in flow_packets
                            )
                        except Exception as exc:
                            self.circuit_breaker.record_failure(self.clock())
                            self.last_deep_error = "{}: {}".format(type(exc).__name__, exc)
                            deep_available = False
                            deep_failure = True
                            tier = "flow"
                        else:
                            deep_costs_us.append((self.cost_clock() - deep_started) * 1_000_000.0)
                            deep_utilities.append(priorities[key])
                            features.update(deep_features)
                            self.circuit_breaker.record_success(self.clock())
                    else:
                        tier = "flow"
                actual_tiers[key] = tier
            results.append(PipelineResult(key, tier, features))
        feature_emit_finished = self.cost_clock()
        actual_decisions = tuple(
            ExtractionDecision(
                decision.key,
                actual_tiers.get(decision.key, decision.tier),
                decision.estimated_cost_us,
                decision.score,
            )
            for decision in planned.decisions
        )
        self.last_schedule_plan = SchedulePlan(
            decisions=actual_decisions,
            effective_budget_us=planned.effective_budget_us,
            estimated_used_us=planned.estimated_used_us,
            budget_overrun_count=planned.budget_overrun_count,
            key_flow_total=planned.key_flow_total,
            key_flow_covered=planned.key_flow_covered,
            key_flow_coverage=planned.key_flow_coverage,
            fallback_active=planned.fallback_active or deep_failure,
        )
        self.last_batch_runtime_us = (self.cost_clock() - batch_started) * 1_000_000.0
        utilization = self.last_batch_runtime_us / max(0.001, budget_us)
        if flow_costs_us:
            self.scheduler.observe(
                "flow",
                sum(flow_costs_us) / len(flow_costs_us),
                sum(flow_utilities) / len(flow_utilities),
                utilization,
            )
        if deep_costs_us:
            self.scheduler.observe(
                "deep",
                sum(deep_costs_us) / len(deep_costs_us),
                sum(deep_utilities) / len(deep_utilities),
                utilization,
            )
        self.last_fallback_recovery_s = self.circuit_breaker.snapshot().last_recovery_s
        feedback_finished = self.cost_clock()
        self.last_stage_timings_us = {
            "state_update": (state_update_finished - batch_started) * 1_000_000.0,
            "candidate_build": (candidate_build_finished - state_update_finished) * 1_000_000.0,
            "schedule": (schedule_finished - candidate_build_finished) * 1_000_000.0,
            "feature_emit": (feature_emit_finished - schedule_finished) * 1_000_000.0,
            "feedback": (feedback_finished - feature_emit_finished) * 1_000_000.0,
        }
        return results
