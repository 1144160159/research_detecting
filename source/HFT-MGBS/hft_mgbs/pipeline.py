"""End-to-end progressive extraction pipeline."""

from __future__ import annotations

import gc
import time
from collections import defaultdict
from contextlib import contextmanager
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


@contextmanager
def _suppress_cyclic_gc():
    """Keep cyclic-GC scans outside the optional-tier budget interval.

    Feature results are acyclic and are reclaimed by reference counting. A
    cyclic collection triggered by one allocation can otherwise be charged to
    that call, poison the execution guard, and starve later key flows.
    """

    was_enabled = gc.isenabled()
    if was_enabled:
        gc.disable()
    try:
        yield
    finally:
        if was_enabled:
            gc.enable()


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
        cost_clock: Callable[[], float] = getattr(
            time, "thread_time", time.process_time
        ),
        stage_clock: Callable[[], float] = time.perf_counter,
        execution_budget_safety_ratio: float = 0.75,
        initial_key_flow_guard_us: float = 50.0,
        initial_flow_guard_us: float = 250.0,
        initial_deep_guard_us: float = 500.0,
        max_deep_payload_bytes_per_flow: int = 4096,
    ) -> None:
        if not 0 < execution_budget_safety_ratio <= 1.0:
            raise ValueError("execution_budget_safety_ratio must be in (0, 1]")
        if (
            initial_key_flow_guard_us <= 0
            or initial_flow_guard_us <= 0
            or initial_deep_guard_us <= 0
        ):
            raise ValueError("execution cost guards must be positive")
        if max_deep_payload_bytes_per_flow <= 0:
            raise ValueError(
                "max_deep_payload_bytes_per_flow must be positive"
            )
        self.extractor = extractor or MultiGranularityExtractor()
        self.scheduler = scheduler or AdaptiveBudgetScheduler()
        self.circuit_breaker = circuit_breaker or DeepPathCircuitBreaker()
        self.clock = clock
        self.cost_clock = cost_clock
        self.stage_clock = stage_clock
        self.execution_budget_safety_ratio = execution_budget_safety_ratio
        self.max_deep_payload_bytes_per_flow = (
            max_deep_payload_bytes_per_flow
        )
        self._execution_cost_guard_us = {
            "key_flow": initial_key_flow_guard_us,
            "flow": initial_flow_guard_us,
            "deep": initial_deep_guard_us,
        }
        self.last_schedule_plan: Optional[SchedulePlan] = None
        self.last_deep_error: Optional[str] = None
        self.last_fallback_recovery_s: Optional[float] = None
        self.last_batch_runtime_us: Optional[float] = None
        self.last_stage_timings_us: Mapping[str, float] = {}

    def _bounded_payloads(
        self, packets: Iterable[PacketRecord]
    ) -> List[bytes]:
        remaining = self.max_deep_payload_bytes_per_flow
        sampled = []
        for packet in packets:
            if remaining <= 0:
                break
            chunk = packet.payload[:remaining]
            if chunk:
                sampled.append(chunk)
                remaining -= len(chunk)
        return sampled

    def process_batch(
        self,
        packets: Iterable[PacketRecord],
        budget_us: float,
        allow_deep: bool = True,
        key_flows: Optional[Iterable[FlowKey]] = None,
    ) -> List[PipelineResult]:
        batch_started = self.stage_clock()
        by_flow: DefaultDict[FlowKey, List[PacketRecord]] = defaultdict(list)
        for packet in packets:
            key = self.extractor.canonical_key(packet)
            self.extractor.update(packet, key=key)
            by_flow[key].append(packet)
        state_update_finished = self.stage_clock()

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
        candidate_build_finished = self.stage_clock()

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
        schedule_finished = self.stage_clock()
        decisions = {decision.key: decision for decision in planned.decisions}
        actual_tiers: Dict[FlowKey, str] = {}
        deep_available = effective_allow_deep
        deep_failure = False
        flow_costs_us: List[float] = []
        flow_utilities: List[float] = []
        deep_costs_us: List[float] = []
        deep_utilities: List[float] = []
        self.last_deep_error = None
        actual_used_us = 0.0
        execution_limit_us = budget_us * self.execution_budget_safety_ratio
        execution_items = sorted(
            by_flow.items(),
            key=lambda item: (
                item[0] not in key_flow_set,
                -decisions[item[0]].score if item[0] in decisions else 0.0,
                str(item[0]),
            ),
        )
        features_by_key: Dict[FlowKey, Dict[str, float]] = {}
        desired_deep: List[FlowKey] = []

        # Phase 1: grant the flow tier first. Key flows are ordered before
        # ordinary flows, so deep work can never consume their reserve. Key
        # flow coverage is a hard constraint and may use the configured hard
        # cap; ordinary/deep work is restricted to the safety soft limit.
        for key, flow_packets in execution_items:
            last = flow_packets[-1]
            features: Dict[str, float] = self.extractor.packet_features(last)
            features.update(self.extractor.window_features(last.timestamp))
            decision = decisions.get(key)
            tier = "base"
            if decision is not None:
                guard_tier = (
                    "key_flow" if key in key_flow_set else "flow"
                )
                flow_guard_us = self._execution_cost_guard_us[guard_tier]
                tier_limit_us = (
                    budget_us
                    if key in key_flow_set
                    else execution_limit_us
                )
                # Key-flow coverage is not traded away to make a predicted
                # guard look feasible. Execute every planned key flow and
                # audit the measured hard-budget result afterwards. Ordinary
                # work remains preempted by the safety soft limit.
                guard_blocks = (
                    key not in key_flow_set
                    and actual_used_us + flow_guard_us > tier_limit_us
                )
                if guard_blocks:
                    tier = "base"
                else:
                    with _suppress_cyclic_gc():
                        flow_started = self.cost_clock()
                        flow_features = self.extractor.flow_features(key)
                        flow_elapsed_us = (
                            self.cost_clock() - flow_started
                        ) * 1_000_000.0
                    actual_used_us += flow_elapsed_us
                    flow_costs_us.append(flow_elapsed_us)
                    flow_utilities.append(priorities[key])
                    self._execution_cost_guard_us[guard_tier] = max(
                        self._execution_cost_guard_us[guard_tier] * 0.98,
                        flow_elapsed_us * 1.25,
                    )
                    features.update(flow_features)
                    tier = "flow"
                    if decision.tier == "deep":
                        desired_deep.append(key)
                actual_tiers[key] = tier
            features_by_key[key] = features

        # Phase 2: use only the remaining optional budget for bounded deep
        # upgrades after every planned flow-tier grant has been attempted.
        for key in desired_deep:
            if not deep_available:
                break
            deep_guard_us = self._execution_cost_guard_us["deep"]
            if actual_used_us + deep_guard_us > execution_limit_us:
                continue
            sampled_payloads = self._bounded_payloads(by_flow[key])
            try:
                with _suppress_cyclic_gc():
                    deep_started = self.cost_clock()
                    deep_features = self.extractor.deep_payload_features(
                        sampled_payloads
                    )
                    deep_elapsed_us = (
                        self.cost_clock() - deep_started
                    ) * 1_000_000.0
            except Exception as exc:
                deep_elapsed_us = (
                    self.cost_clock() - deep_started
                ) * 1_000_000.0
                actual_used_us += deep_elapsed_us
                deep_costs_us.append(deep_elapsed_us)
                deep_utilities.append(0.0)
                self._execution_cost_guard_us["deep"] = max(
                    self._execution_cost_guard_us["deep"] * 0.98,
                    deep_elapsed_us * 1.25,
                )
                self.circuit_breaker.record_failure(self.clock())
                self.last_deep_error = "{}: {}".format(
                    type(exc).__name__, exc
                )
                deep_available = False
                deep_failure = True
            else:
                actual_used_us += deep_elapsed_us
                deep_costs_us.append(deep_elapsed_us)
                deep_utilities.append(priorities[key])
                self._execution_cost_guard_us["deep"] = max(
                    self._execution_cost_guard_us["deep"] * 0.98,
                    deep_elapsed_us * 1.25,
                )
                deep_features["payload_sampled_bytes"] = float(
                    sum(len(payload) for payload in sampled_payloads)
                )
                features_by_key[key].update(deep_features)
                actual_tiers[key] = "deep"
                self.circuit_breaker.record_success(self.clock())

        results = [
            PipelineResult(
                key,
                actual_tiers.get(key, "base"),
                features_by_key[key],
            )
            for key, _ in execution_items
        ]
        feature_emit_finished = self.stage_clock()
        actual_decisions = tuple(
            ExtractionDecision(
                decision.key,
                actual_tiers.get(decision.key, decision.tier),
                decision.estimated_cost_us,
                decision.score,
            )
            for decision in planned.decisions
        )
        actual_budget_overrun = int(actual_used_us > budget_us + 1e-9)
        present_key_flows = key_flow_set.intersection(by_flow)
        actual_key_covered = sum(
            actual_tiers.get(key, "base") in ("flow", "deep")
            for key in present_key_flows
        )
        actual_key_total = len(present_key_flows)
        actual_key_coverage = (
            1.0 if actual_key_total == 0 else actual_key_covered / actual_key_total
        )
        self.last_schedule_plan = SchedulePlan(
            decisions=actual_decisions,
            effective_budget_us=planned.effective_budget_us,
            estimated_used_us=planned.estimated_used_us,
            budget_overrun_count=max(
                planned.estimated_budget_overrun_count, actual_budget_overrun
            ),
            key_flow_total=actual_key_total,
            key_flow_covered=actual_key_covered,
            key_flow_coverage=actual_key_coverage,
            fallback_active=planned.fallback_active or deep_failure,
            configured_budget_us=budget_us,
            actual_used_us=actual_used_us,
            estimated_budget_overrun_count=planned.estimated_budget_overrun_count,
            actual_budget_overrun_count=actual_budget_overrun,
        )
        self.last_batch_runtime_us = (
            self.stage_clock() - batch_started
        ) * 1_000_000.0
        utilization = actual_used_us / max(0.001, budget_us)
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
        feedback_finished = self.stage_clock()
        self.last_stage_timings_us = {
            "state_update": (state_update_finished - batch_started) * 1_000_000.0,
            "candidate_build": (candidate_build_finished - state_update_finished) * 1_000_000.0,
            "schedule": (schedule_finished - candidate_build_finished) * 1_000_000.0,
            "feature_emit": (feature_emit_finished - schedule_finished) * 1_000_000.0,
            "feedback": (feedback_finished - feature_emit_finished) * 1_000_000.0,
        }
        return results
