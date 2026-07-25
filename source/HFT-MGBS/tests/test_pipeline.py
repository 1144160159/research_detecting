import unittest
from unittest import mock

from hft_mgbs import AdaptiveExtractionPipeline, MultiGranularityExtractor, PacketRecord
from hft_mgbs.pipeline import _suppress_cyclic_gc
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


class RecordingExtractor(MultiGranularityExtractor):
    def __init__(self):
        super().__init__()
        self.calls = []
        self.deep_sampled_bytes = None

    def flow_features(self, key):
        self.calls.append("flow")
        return super().flow_features(key)

    def deep_payload_features(self, payloads):
        payloads = list(payloads)
        self.calls.append("deep")
        self.deep_sampled_bytes = sum(len(payload) for payload in payloads)
        return super().deep_payload_features(payloads)


class PipelineTests(unittest.TestCase):
    def test_cyclic_gc_state_is_restored_after_optional_work(self):
        with mock.patch("hft_mgbs.pipeline.gc.isenabled", return_value=True):
            with mock.patch("hft_mgbs.pipeline.gc.disable") as disable:
                with mock.patch("hft_mgbs.pipeline.gc.enable") as enable:
                    with self.assertRaisesRegex(RuntimeError, "boom"):
                        with _suppress_cyclic_gc():
                            raise RuntimeError("boom")
        disable.assert_called_once_with()
        enable.assert_called_once_with()

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
        self.assertIn("payload_sampled_bytes", result.features)

    def test_deep_payload_work_is_bounded_per_flow(self):
        extractor = RecordingExtractor()
        packets = [
            PacketRecord(float(index), "a", "b", 1, 2, 17, 128, b"abcdef")
            for index in range(3)
        ]
        pipeline = AdaptiveExtractionPipeline(
            extractor=extractor,
            max_deep_payload_bytes_per_flow=8,
        )
        result = pipeline.process_batch(packets, budget_us=1000.0)[0]
        self.assertEqual(result.tier, "deep")
        self.assertEqual(extractor.deep_sampled_bytes, 8)
        self.assertEqual(result.features["payload_sampled_bytes"], 8.0)

    def test_all_key_flow_tiers_are_attempted_before_deep_upgrade(self):
        extractor = RecordingExtractor()
        first = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        second = PacketRecord(0.0, "c", "d", 3, 4, 17, 128, b"def")
        pipeline = AdaptiveExtractionPipeline(extractor=extractor)
        pipeline.process_batch(
            [first, second],
            budget_us=1000.0,
            key_flows=[first.flow_key, second.flow_key],
        )
        first_deep = extractor.calls.index("deep")
        self.assertGreaterEqual(first_deep, 2)
        self.assertEqual(extractor.calls[:2], ["flow", "flow"])
        self.assertEqual(pipeline.last_schedule_plan.key_flow_coverage, 1.0)

    def test_pipeline_fallback_keeps_key_flow_without_deep_features(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline()
        result = pipeline.process_batch(
            [packet],
            budget_us=1000.0,
            allow_deep=False,
            key_flows=[packet.flow_key],
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
        pipeline.process_batch([packet], budget_us=1000.0)
        after = pipeline.scheduler.estimates["cost_us"]
        self.assertNotEqual(before, after)
        self.assertIsNotNone(pipeline.last_batch_runtime_us)
        self.assertEqual(
            set(pipeline.last_stage_timings_us),
            {"state_update", "candidate_build", "schedule", "feature_emit", "feedback"},
        )

    def test_actual_optional_cost_overrun_is_audited(self):
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline(
            cost_clock=IncrementClock(),
            initial_flow_guard_us=20.0,
        )
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
            initial_key_flow_guard_us=20.0,
            initial_flow_guard_us=20.0,
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

    def test_key_flow_guard_is_separate_from_ordinary_flow_guard(self):
        packets = [
            PacketRecord(
                0.0,
                "10.0.0.{}".format(index),
                "10.0.1.1",
                1000 + index,
                443,
                6,
                128,
                b"x",
            )
            for index in range(20)
        ]
        pipeline = AdaptiveExtractionPipeline(
            cost_clock=IncrementClock(step_s=0.00001),
            execution_budget_safety_ratio=0.5,
            initial_key_flow_guard_us=40.0,
            initial_flow_guard_us=250.0,
        )

        pipeline.process_batch(
            packets,
            budget_us=1000.0,
            allow_deep=False,
            key_flows=[packet.flow_key for packet in packets],
        )

        self.assertEqual(pipeline.last_schedule_plan.key_flow_total, 20)
        self.assertEqual(pipeline.last_schedule_plan.key_flow_covered, 20)
        self.assertEqual(pipeline.last_schedule_plan.key_flow_coverage, 1.0)

    def test_key_flows_may_use_hard_cap_beyond_optional_soft_limit(self):
        packets = [
            PacketRecord(
                0.0,
                "10.1.0.{}".format(index),
                "10.2.0.1",
                2000 + index,
                443,
                6,
                128,
                b"x",
            )
            for index in range(6)
        ]
        pipeline = AdaptiveExtractionPipeline(
            cost_clock=IncrementClock(step_s=0.0001),
            execution_budget_safety_ratio=0.5,
            initial_key_flow_guard_us=100.0,
        )

        pipeline.process_batch(
            packets,
            budget_us=1000.0,
            allow_deep=False,
            key_flows=[packet.flow_key for packet in packets],
        )

        plan = pipeline.last_schedule_plan
        self.assertEqual(plan.key_flow_covered, 6)
        self.assertGreater(plan.actual_used_us, 500.0)
        self.assertLessEqual(plan.actual_used_us, 1000.0)
        self.assertEqual(plan.actual_budget_overrun_count, 0)

    def test_key_coverage_is_preserved_and_real_overrun_is_audited(self):
        key = PacketRecord(
            0.0, "10.3.0.1", "10.3.0.2", 3000, 443, 6, 128, b"x"
        )
        pipeline = AdaptiveExtractionPipeline(
            cost_clock=IncrementClock(step_s=0.0006),
            execution_budget_safety_ratio=0.5,
            initial_key_flow_guard_us=1000.0,
        )

        result = pipeline.process_batch(
            [key],
            budget_us=500.0,
            allow_deep=False,
            key_flows=[key.flow_key],
        )[0]

        plan = pipeline.last_schedule_plan
        self.assertEqual(result.tier, "flow")
        self.assertEqual(plan.key_flow_coverage, 1.0)
        self.assertGreater(plan.actual_used_us, plan.configured_budget_us)
        self.assertEqual(plan.actual_budget_overrun_count, 1)

    def test_actual_key_coverage_is_not_inferred_from_unexecuted_plan(self):
        key = PacketRecord(0.0, "a", "b", 1, 2, 17, 128, b"abc")
        pipeline = AdaptiveExtractionPipeline()
        result = pipeline.process_batch(
            [key], budget_us=1.0, allow_deep=False, key_flows=[key.flow_key]
        )[0]
        self.assertEqual(result.tier, "base")
        self.assertEqual(pipeline.last_schedule_plan.key_flow_covered, 0)
        self.assertEqual(pipeline.last_schedule_plan.key_flow_coverage, 0.0)


if __name__ == "__main__":
    unittest.main()
