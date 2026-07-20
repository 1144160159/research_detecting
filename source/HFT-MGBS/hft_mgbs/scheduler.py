"""Adaptive budget scheduling by marginal utility per estimated microsecond."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Iterable, List, Mapping, Tuple


@dataclass(frozen=True)
class ExtractionCandidate:
    key: Hashable
    priority: float
    flow_cost_us: float = 4.0
    deep_cost_us: float = 40.0
    is_key_flow: bool = False


@dataclass(frozen=True)
class ExtractionDecision:
    key: Hashable
    tier: str
    estimated_cost_us: float
    score: float


@dataclass(frozen=True)
class SchedulePlan:
    decisions: Tuple[ExtractionDecision, ...]
    effective_budget_us: float
    estimated_used_us: float
    budget_overrun_count: int
    key_flow_total: int
    key_flow_covered: int
    key_flow_coverage: float
    fallback_active: bool


class AdaptiveBudgetScheduler:
    """Selects optional extraction tiers while tracking measured cost and utility."""

    def __init__(
        self,
        target_utilization: float = 0.85,
        ema_alpha: float = 0.2,
        min_budget_ratio: float = 0.25,
        max_budget_ratio: float = 1.25,
    ) -> None:
        if not 0 < target_utilization <= 1:
            raise ValueError("target_utilization must be in (0, 1]")
        if not 0 < ema_alpha <= 1:
            raise ValueError("ema_alpha must be in (0, 1]")
        self.target_utilization = target_utilization
        self.ema_alpha = ema_alpha
        self.min_budget_ratio = min_budget_ratio
        self.max_budget_ratio = max_budget_ratio
        self._cost_ema: Dict[str, float] = {"flow": 4.0, "deep": 40.0}
        self._utility_ema: Dict[str, float] = {"flow": 1.0, "deep": 1.0}
        self._last_utilization = target_utilization

    def effective_budget(self, configured_budget_us: float) -> float:
        if configured_budget_us < 0:
            raise ValueError("configured_budget_us must be non-negative")
        pressure_ratio = self.target_utilization / max(0.05, self._last_utilization)
        ratio = min(self.max_budget_ratio, max(self.min_budget_ratio, pressure_ratio))
        return configured_budget_us * ratio

    def plan(
        self, candidates: Iterable[ExtractionCandidate], configured_budget_us: float
    ) -> List[ExtractionDecision]:
        return list(self.plan_with_audit(candidates, configured_budget_us).decisions)

    def plan_with_audit(
        self,
        candidates: Iterable[ExtractionCandidate],
        configured_budget_us: float,
        allow_deep: bool = True,
        recovery_probe: bool = False,
    ) -> SchedulePlan:
        budget = self.effective_budget(configured_budget_us)
        candidates = list(candidates)
        flow_estimate = max(0.001, self._cost_ema["flow"])
        deep_estimate = max(0.001, self._cost_ema["deep"])
        if recovery_probe and allow_deep and candidates:
            # A half-open breaker must be able to run one bounded probe. The
            # reserve may reclaim pressure-reduced budget, but never exceeds
            # the operator-configured hard cap.
            probe_cost = flow_estimate + deep_estimate
            budget = min(configured_budget_us, max(budget, probe_cost))
        options: List[Tuple[float, str, ExtractionCandidate, float]] = []
        for candidate in candidates:
            priority = max(0.0, candidate.priority)
            flow_cost = max(0.001, self._cost_ema.get("flow", candidate.flow_cost_us))
            deep_cost = max(0.001, self._cost_ema.get("deep", candidate.deep_cost_us))
            flow_score = priority * self._utility_ema["flow"] / flow_cost
            deep_score = priority * self._utility_ema["deep"] / deep_cost
            options.append((flow_score, "flow", candidate, flow_cost))
            if allow_deep:
                options.append((deep_score, "deep", candidate, deep_cost))

        selected_tiers: Dict[Hashable, str] = {}
        decisions: Dict[Hashable, ExtractionDecision] = {}
        used = 0.0
        tier_rank = {"flow": 1, "deep": 2}
        flow_cost = max(0.001, self._cost_ema["flow"])

        # Reserve the cheapest useful tier for key flows before ordinary utility sorting.
        key_candidates = sorted(
            (candidate for candidate in candidates if candidate.is_key_flow),
            key=lambda item: (-item.priority, str(item.key)),
        )
        for candidate in key_candidates:
            if used + flow_cost > budget:
                break
            score = max(0.0, candidate.priority) * self._utility_ema["flow"] / flow_cost
            selected_tiers[candidate.key] = "flow"
            decisions[candidate.key] = ExtractionDecision(candidate.key, "flow", flow_cost, score)
            used += flow_cost

        if recovery_probe and allow_deep and candidates:
            probe_pool = key_candidates or sorted(
                candidates, key=lambda item: (-item.priority, str(item.key))
            )
            probe = probe_pool[0]
            current = selected_tiers.get(probe.key)
            incremental = deep_estimate if current == "flow" else flow_estimate + deep_estimate
            if used + incremental <= budget:
                score = max(0.0, probe.priority) * self._utility_ema["deep"] / deep_estimate
                prior_cost = 0.0 if current is None else decisions[probe.key].estimated_cost_us
                selected_tiers[probe.key] = "deep"
                decisions[probe.key] = ExtractionDecision(
                    probe.key, "deep", prior_cost + incremental, score
                )
                used += incremental

        for score, tier, candidate, cost in sorted(options, key=lambda item: (-item[0], str(item[2].key), tier_rank[item[1]])):
            current = selected_tiers.get(candidate.key)
            if current is not None and tier_rank[current] >= tier_rank[tier]:
                continue
            incremental_cost = cost
            if tier == "deep" and current is None:
                incremental_cost += max(0.001, self._cost_ema.get("flow", candidate.flow_cost_us))
            if used + incremental_cost > budget:
                continue
            selected_tiers[candidate.key] = tier
            used += incremental_cost
            prior_cost = 0.0 if current is None else decisions[candidate.key].estimated_cost_us
            decisions[candidate.key] = ExtractionDecision(candidate.key, tier, prior_cost + incremental_cost, score)
        key_covered = sum(candidate.key in decisions for candidate in key_candidates)
        key_total = len(key_candidates)
        coverage = 1.0 if key_total == 0 else key_covered / key_total
        ordered = tuple(sorted(decisions.values(), key=lambda item: str(item.key)))
        return SchedulePlan(
            decisions=ordered,
            effective_budget_us=budget,
            estimated_used_us=used,
            budget_overrun_count=int(used > budget + 1e-9),
            key_flow_total=key_total,
            key_flow_covered=key_covered,
            key_flow_coverage=coverage,
            fallback_active=not allow_deep,
        )

    def observe(self, tier: str, measured_cost_us: float, realized_utility: float, utilization: float) -> None:
        if tier not in self._cost_ema:
            raise ValueError(f"unknown tier: {tier}")
        alpha = self.ema_alpha
        self._cost_ema[tier] = (1 - alpha) * self._cost_ema[tier] + alpha * max(0.001, measured_cost_us)
        self._utility_ema[tier] = (1 - alpha) * self._utility_ema[tier] + alpha * max(0.0, realized_utility)
        self._last_utilization = min(2.0, max(0.05, utilization))

    @property
    def estimates(self) -> Mapping[str, Mapping[str, float]]:
        return {"cost_us": dict(self._cost_ema), "utility": dict(self._utility_ema)}
