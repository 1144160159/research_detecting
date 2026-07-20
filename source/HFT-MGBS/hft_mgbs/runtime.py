"""Runtime health controls for bounded deep-path fallback and recovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CircuitBreakerSnapshot:
    state: str
    consecutive_failures: int
    consecutive_probe_successes: int
    opened_at: Optional[float]
    fallback_active: bool
    last_recovery_s: Optional[float]


class DeepPathCircuitBreaker:
    """Fail closed to the flow tier, then probe and recover with hysteresis."""

    def __init__(
        self,
        failure_threshold: int = 1,
        recovery_timeout_s: float = 5.0,
        probe_success_threshold: int = 2,
    ) -> None:
        if failure_threshold <= 0 or probe_success_threshold <= 0:
            raise ValueError("circuit breaker thresholds must be positive")
        if recovery_timeout_s < 0:
            raise ValueError("recovery_timeout_s cannot be negative")
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.probe_success_threshold = probe_success_threshold
        self._state = "closed"
        self._consecutive_failures = 0
        self._probe_successes = 0
        self._opened_at: Optional[float] = None
        self._last_recovery_s: Optional[float] = None

    def allow_deep(self, now: float) -> bool:
        if self._state == "open":
            elapsed = now - (self._opened_at if self._opened_at is not None else now)
            if elapsed + 1e-12 >= self.recovery_timeout_s:
                self._state = "half_open"
                self._probe_successes = 0
            else:
                return False
        return True

    def record_failure(self, now: float) -> None:
        self._consecutive_failures += 1
        self._probe_successes = 0
        if self._state == "half_open" or self._consecutive_failures >= self.failure_threshold:
            self._state = "open"
            self._opened_at = now
            self._last_recovery_s = None

    def record_success(self, now: Optional[float] = None) -> None:
        self._consecutive_failures = 0
        if self._state == "half_open":
            self._probe_successes += 1
            if self._probe_successes >= self.probe_success_threshold:
                if now is not None and self._opened_at is not None:
                    self._last_recovery_s = max(0.0, now - self._opened_at)
                self._state = "closed"
                self._opened_at = None
                self._probe_successes = 0

    def force_open(self, now: float) -> None:
        self._state = "open"
        self._opened_at = now
        self._consecutive_failures = self.failure_threshold
        self._probe_successes = 0
        self._last_recovery_s = None

    def snapshot(self) -> CircuitBreakerSnapshot:
        return CircuitBreakerSnapshot(
            state=self._state,
            consecutive_failures=self._consecutive_failures,
            consecutive_probe_successes=self._probe_successes,
            opened_at=self._opened_at,
            fallback_active=self._state == "open",
            last_recovery_s=self._last_recovery_s,
        )
