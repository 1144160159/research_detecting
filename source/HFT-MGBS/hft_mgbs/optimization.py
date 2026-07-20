"""Hard-constraint auditing and Pareto selection for deployment candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class ConstraintProfile:
    target_load_mpps: float
    max_packet_drop_count: int
    max_p99_latency_us: float
    max_p999_latency_us: float
    max_cpu_utilization: float
    max_gpu_utilization: float
    max_memory_utilization: float
    max_gpu_memory_utilization: float
    max_budget_overrun_count: int
    min_key_flow_coverage: float
    max_fallback_recovery_s: float

    def __post_init__(self) -> None:
        positive = {
            "target_load_mpps": self.target_load_mpps,
            "max_p99_latency_us": self.max_p99_latency_us,
            "max_p999_latency_us": self.max_p999_latency_us,
            "max_fallback_recovery_s": self.max_fallback_recovery_s,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError("{} must be positive".format(name))
        for name in (
            "max_cpu_utilization",
            "max_gpu_utilization",
            "max_memory_utilization",
            "max_gpu_memory_utilization",
            "min_key_flow_coverage",
        ):
            value = getattr(self, name)
            if not 0 < value <= 1:
                raise ValueError("{} must be in (0, 1]".format(name))
        if self.max_packet_drop_count < 0 or self.max_budget_overrun_count < 0:
            raise ValueError("count constraints must be non-negative")
        if self.max_p999_latency_us < self.max_p99_latency_us:
            raise ValueError("P99.9 constraint cannot be lower than P99")

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "ConstraintProfile":
        return cls(**{field: values[field] for field in cls.__dataclass_fields__})


@dataclass(frozen=True)
class CandidateMetrics:
    name: str
    quality: float
    gain_per_cost: float
    throughput_mpps: float
    packet_drop_count: int
    p99_latency_us: float
    p999_latency_us: float
    cpu_utilization: float
    gpu_utilization: float
    memory_utilization: float
    gpu_memory_utilization: float
    budget_overrun_count: int
    key_flow_coverage: float
    fallback_recovery_s: float
    complexity: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("candidate name is required")
        if self.packet_drop_count < 0 or self.budget_overrun_count < 0:
            raise ValueError("candidate counts must be non-negative")
        for name in (
            "quality",
            "throughput_mpps",
            "p99_latency_us",
            "p999_latency_us",
            "cpu_utilization",
            "gpu_utilization",
            "memory_utilization",
            "gpu_memory_utilization",
            "key_flow_coverage",
            "fallback_recovery_s",
            "complexity",
        ):
            if getattr(self, name) < 0:
                raise ValueError("{} cannot be negative".format(name))
        for name in (
            "quality",
            "cpu_utilization",
            "gpu_utilization",
            "memory_utilization",
            "gpu_memory_utilization",
            "key_flow_coverage",
        ):
            if getattr(self, name) > 1:
                raise ValueError("{} must be normalized to [0, 1]".format(name))

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "CandidateMetrics":
        return cls(**{field: values[field] for field in cls.__dataclass_fields__})

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ConstraintViolation:
    constraint: str
    actual: float
    limit: float
    relation: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateAudit:
    candidate: CandidateMetrics
    feasible: bool
    violations: Tuple[ConstraintViolation, ...]

    def as_dict(self) -> Dict[str, object]:
        return {
            "candidate": self.candidate.as_dict(),
            "feasible": self.feasible,
            "violations": [item.as_dict() for item in self.violations],
        }


@dataclass(frozen=True)
class ParetoSelection:
    audits: Tuple[CandidateAudit, ...]
    pareto_front: Tuple[CandidateMetrics, ...]
    champion: Optional[CandidateMetrics]
    champion_score: Optional[float]

    def as_dict(self) -> Dict[str, object]:
        return {
            "audits": [audit.as_dict() for audit in self.audits],
            "pareto_front": [candidate.as_dict() for candidate in self.pareto_front],
            "champion": None if self.champion is None else self.champion.as_dict(),
            "champion_score": self.champion_score,
        }


DEFAULT_OBJECTIVES: Mapping[str, str] = {
    "quality": "max",
    "key_flow_coverage": "max",
    "gain_per_cost": "max",
    "p99_latency_us": "min",
    "resource_pressure": "min",
    "fallback_recovery_s": "min",
    "complexity": "min",
}

DEFAULT_WEIGHTS: Mapping[str, float] = {
    "quality": 0.30,
    "key_flow_coverage": 0.20,
    "gain_per_cost": 0.15,
    "p99_latency_us": 0.15,
    "resource_pressure": 0.15,
    "fallback_recovery_s": 0.03,
    "complexity": 0.02,
}


class ParetoOptimizer:
    """Rejects constraint violations before computing a multi-objective frontier."""

    def __init__(
        self,
        profile: ConstraintProfile,
        objectives: Mapping[str, str] = DEFAULT_OBJECTIVES,
        weights: Mapping[str, float] = DEFAULT_WEIGHTS,
    ) -> None:
        self.profile = profile
        self.objectives = dict(objectives)
        self.weights = dict(weights)
        if set(self.weights) != set(self.objectives):
            raise ValueError("weights must cover exactly the configured objectives")
        if any(direction not in ("min", "max") for direction in self.objectives.values()):
            raise ValueError("objective direction must be min or max")
        if any(weight < 0 for weight in self.weights.values()) or sum(self.weights.values()) <= 0:
            raise ValueError("objective weights must be non-negative with a positive total")

    def audit(self, candidate: CandidateMetrics) -> CandidateAudit:
        checks = (
            ("throughput_mpps", candidate.throughput_mpps, self.profile.target_load_mpps, ">="),
            ("packet_drop_count", candidate.packet_drop_count, self.profile.max_packet_drop_count, "<="),
            ("p99_latency_us", candidate.p99_latency_us, self.profile.max_p99_latency_us, "<="),
            ("p999_latency_us", candidate.p999_latency_us, self.profile.max_p999_latency_us, "<="),
            ("cpu_utilization", candidate.cpu_utilization, self.profile.max_cpu_utilization, "<="),
            ("gpu_utilization", candidate.gpu_utilization, self.profile.max_gpu_utilization, "<="),
            ("memory_utilization", candidate.memory_utilization, self.profile.max_memory_utilization, "<="),
            ("gpu_memory_utilization", candidate.gpu_memory_utilization, self.profile.max_gpu_memory_utilization, "<="),
            ("budget_overrun_count", candidate.budget_overrun_count, self.profile.max_budget_overrun_count, "<="),
            ("key_flow_coverage", candidate.key_flow_coverage, self.profile.min_key_flow_coverage, ">="),
            ("fallback_recovery_s", candidate.fallback_recovery_s, self.profile.max_fallback_recovery_s, "<="),
        )
        violations: List[ConstraintViolation] = []
        for name, actual, limit, relation in checks:
            failed = actual < limit if relation == ">=" else actual > limit
            if failed:
                violations.append(ConstraintViolation(name, float(actual), float(limit), relation))
        return CandidateAudit(candidate, not violations, tuple(violations))

    def resource_pressure(self, candidate: CandidateMetrics) -> float:
        ratios = (
            candidate.cpu_utilization / self.profile.max_cpu_utilization,
            candidate.gpu_utilization / self.profile.max_gpu_utilization,
            candidate.memory_utilization / self.profile.max_memory_utilization,
            candidate.gpu_memory_utilization / self.profile.max_gpu_memory_utilization,
        )
        return max(ratios)

    def objective_value(self, candidate: CandidateMetrics, name: str) -> float:
        if name == "resource_pressure":
            return self.resource_pressure(candidate)
        return float(getattr(candidate, name))

    def dominates(self, left: CandidateMetrics, right: CandidateMetrics) -> bool:
        no_worse = True
        strictly_better = False
        for name, direction in self.objectives.items():
            left_value = self.objective_value(left, name)
            right_value = self.objective_value(right, name)
            if direction == "max":
                no_worse = no_worse and left_value >= right_value
                strictly_better = strictly_better or left_value > right_value
            else:
                no_worse = no_worse and left_value <= right_value
                strictly_better = strictly_better or left_value < right_value
        return no_worse and strictly_better

    def pareto_front(self, candidates: Sequence[CandidateMetrics]) -> Tuple[CandidateMetrics, ...]:
        front = []
        for candidate in candidates:
            if not any(self.dominates(other, candidate) for other in candidates if other is not candidate):
                front.append(candidate)
        return tuple(sorted(front, key=lambda item: item.name))

    def champion(self, front: Sequence[CandidateMetrics]) -> Tuple[Optional[CandidateMetrics], Optional[float]]:
        if not front:
            return None, None
        values: Dict[str, List[float]] = {
            name: [self.objective_value(candidate, name) for candidate in front]
            for name in self.objectives
        }
        total_weight = sum(self.weights.values())
        scores: Dict[str, float] = {candidate.name: 0.0 for candidate in front}
        for name, direction in self.objectives.items():
            low, high = min(values[name]), max(values[name])
            for candidate in front:
                value = self.objective_value(candidate, name)
                normalized = 1.0 if high == low else (value - low) / (high - low)
                benefit = normalized if direction == "max" else 1.0 - normalized
                scores[candidate.name] += self.weights[name] * benefit / total_weight
        winner = sorted(front, key=lambda item: (-scores[item.name], item.name))[0]
        return winner, scores[winner.name]

    def select(self, candidates: Iterable[CandidateMetrics]) -> ParetoSelection:
        audits = tuple(self.audit(candidate) for candidate in candidates)
        feasible = [audit.candidate for audit in audits if audit.feasible]
        front = self.pareto_front(feasible)
        champion, score = self.champion(front)
        return ParetoSelection(audits, front, champion, score)
