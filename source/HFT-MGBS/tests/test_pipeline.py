import unittest

from hft_mgbs import AdaptiveExtractionPipeline, MultiGranularityExtractor, PacketRecord
from hft_mgbs.runtime import DeepPathCircuitBreaker


class FailOnceExtractor(MultiGranularityExtractor):
    def __init__(self):
        super().__init__()
        self.deep_calls = 0

    def deep_payload_features(self, payloads):
        self.deep_calls += 1
        if self.deep_calls == 1:
            raise RuntimeError("injected deep-path failure")
        return super().deep_payload_features(payloads)


class IncrementClock:
    def __init__(self, step_s=0.001):
        self.value = 0.0
        self.step_s = step_s

    def __call__(self):
        current = self.value
        self.value += self.step_s
        return current


class PipelineTests(unittest.TestCase):
    def test_zero_budget_keeps_base_features(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        result = AdaptiveExtractionPipeline().process_batch([packet], budget_us=0.0)[0]
        self.assertEqual(result.tier, "base")
        self.assertIn("packet_wire_length", result.features)
        self.assertNotIn("flow_packets", result.features)

    def test_deep_budget_adds_payload_features(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        result = AdaptiveExtractionPipeline().process_batch([packet], budget_us=1000.0)[0]
        self.assertEqual(result.tier, "deep")
        self.assertIn("flow_packets", result.features)
        self.assertIn("payload_entropy", result.features)

    def test_pipeline_fallback_keeps_key_flow_without_deep_features(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline()
        result = pipeline.process_batch(
            [packet], budget_us=100.0, allow_deep=False, key_flows=[packet.flow_key]
        )[0]
        self.assertEqual(result.tier, "flow")
        self.assertNotIn("payload_entropy", result.features)
        self.assertTrue(pipeline.last_schedule_plan.fallback_active)
        self.assertEqual(pipeline.last_schedule_plan.key_flow_coverage, 1.0)

    def test_deep_failure_opens_fallback_and_measures_recovery(self):
        now = [0.0]
        pipeline = AdaptiveExtractionPipeline(
            extractor=FailOnceExtractor(),
            circuit_breaker=DeepPathCircuitBreaker(
                failure_threshold=1,
                recovery_timeout_s=1.0,
                probe_success_threshold=1,
            ),
            clock=lambda: now[0],
        )
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")

        failed = pipeline.process_batch(
            [packet], budget_us=1000.0, key_flows=[packet.flow_key]
        )[0]
        self.assertEqual(failed.tier, "flow")
        self.assertTrue(pipeline.last_schedule_plan.fallback_active)
        self.assertIn("injected deep-path failure", pipeline.last_deep_error)

        now[0] = 0.5
        fallback = pipeline.process_batch(
            [packet], budget_us=1000.0, key_flows=[packet.flow_key]
        )[0]
        self.assertEqual(fallback.tier, "flow")
        self.assertTrue(pipeline.last_schedule_plan.fallback_active)

        now[0] = 1.0
        recovered = pipeline.process_batch(
            [packet], budget_us=1000.0, key_flows=[packet.flow_key]
        )[0]
        self.assertEqual(recovered.tier, "deep")
        self.assertFalse(pipeline.last_schedule_plan.fallback_active)
        self.assertAlmostEqual(pipeline.last_fallback_recovery_s, 1.0)

    def test_runtime_feedback_updates_scheduler_cost_estimates(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline()
        before = pipeline.scheduler.estimates["cost_us"]
        pipeline.process_batch([packet], budget_us=100.0)
        after = pipeline.scheduler.estimates["cost_us"]
        self.assertNotEqual(before, after)
        self.assertIsNotNone(pipeline.last_batch_runtime_us)
        self.assertEqual(
            set(pipeline.last_stage_timings_us),
            {"state_update", "candidate_build", "schedule", "feature_emit", "feedback"},
        )

    def test_actual_optional_cost_overrun_is_audited(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline(cost_clock=IncrementClock())
        pipeline.process_batch([packet], budget_us=100.0)
        plan = pipeline.last_schedule_plan
        self.assertEqual(plan.estimated_budget_overrun_count, 0)
        self.assertGreater(plan.actual_used_us, plan.configured_budget_us)
        self.assertEqual(plan.actual_budget_overrun_count, 1)
        self.assertEqual(plan.budget_overrun_count, 1)

    def test_execution_guard_runs_key_flow_first_and_stays_under_cap(self):
        ordinary = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        key = PacketRecord(0.0, "c", "d", 3, 4, 17, 128, b"def")
        pipeline = AdaptiveExtractionPipeline(
            cost_clock=IncrementClock(step_s=0.00001),
            execution_budget_safety_ratio=1.0,
        )
        results = pipeline.process_batch(
            [ordinary, key],
            budget_us=25.0,
            allow_deep=False,
            key_flows=[key.flow_key],
        )
        tiers = {result.flow_key: result.tier for result in results}
        self.assertEqual(tiers[pipeline.extractor.normalize_flow_key(key.flow_key)], "flow")
        self.assertEqual(tiers[pipeline.extractor.normalize_flow_key(ordinary.flow_key)], "base")
        self.assertEqual(pipeline.last_schedule_plan.actual_budget_overrun_count, 0)
        self.assertEqual(pipeline.last_schedule_plan.key_flow_coverage, 1.0)

    def test_actual_key_coverage_is_not_inferred_from_unexecuted_plan(self):
        key = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline()
        result = pipeline.process_batch(
            [key], budget_us=10.0, allow_deep=False, key_flows=[key.flow_key]
        )[0]
        self.assertEqual(result.tier, "base")
        self.assertEqual(pipeline.last_schedule_plan.key_flow_covered, 0)
        self.assertEqual(pipeline.last_schedule_plan.key_flow_coverage, 0.0)


if __name__ == "__main__":
    unittest.main()
