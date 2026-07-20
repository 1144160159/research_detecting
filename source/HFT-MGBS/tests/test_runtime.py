import unittest

from hft_mgbs.runtime import DeepPathCircuitBreaker


class CircuitBreakerTests(unittest.TestCase):
    def test_failure_opens_fallback_then_successful_probes_recover(self):
        breaker = DeepPathCircuitBreaker(
            failure_threshold=1, recovery_timeout_s=5.0, probe_success_threshold=2
        )
        self.assertTrue(breaker.allow_deep(0.0))
        breaker.record_failure(1.0)
        self.assertFalse(breaker.allow_deep(5.9))
        self.assertTrue(breaker.snapshot().fallback_active)
        self.assertTrue(breaker.allow_deep(6.0))
        self.assertEqual(breaker.snapshot().state, "half_open")
        breaker.record_success(6.1)
        self.assertEqual(breaker.snapshot().state, "half_open")
        breaker.record_success(6.2)
        self.assertEqual(breaker.snapshot().state, "closed")
        self.assertFalse(breaker.snapshot().fallback_active)
        self.assertAlmostEqual(breaker.snapshot().last_recovery_s, 5.2)

    def test_failed_probe_reopens_and_restarts_recovery_timer(self):
        breaker = DeepPathCircuitBreaker(recovery_timeout_s=2.0)
        breaker.force_open(0.0)
        self.assertTrue(breaker.allow_deep(2.0))
        breaker.record_failure(2.1)
        self.assertFalse(breaker.allow_deep(4.0))
        self.assertTrue(breaker.allow_deep(4.1))


if __name__ == "__main__":
    unittest.main()
