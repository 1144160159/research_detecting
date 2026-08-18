import unittest

from hft_mgbs.gpu_service import (
    RAW_FEATURE_ORDER,
    InferenceServer,
    summarize_samples,
    validate_request,
)


class GpuServiceProtocolTests(unittest.TestCase):
    def test_accepts_release_candidate_batch(self):
        flows = validate_request(
            {
                "schema_version": 1,
                "candidate_id": "A09",
                "flows": [{"flow_id": "a", "features": {"flow_packets": 1.0}}],
            }
        )
        self.assertEqual(len(flows), 1)

    def test_rejects_unadmitted_candidate(self):
        with self.assertRaisesRegex(ValueError, "A09"):
            validate_request(
                {
                    "schema_version": 1,
                    "candidate_id": "A10",
                    "flows": [{"flow_id": "a", "features": {}}],
                }
            )

    def test_campaign_selected_candidate_can_be_admitted_explicitly(self):
        flows = validate_request(
            {
                "schema_version": 1,
                "candidate_id": "A10",
                "feature_encoding": "named_v1",
                "flows": [{"flow_id": "a", "features": {}}],
            },
            expected_candidate_id="A10",
        )
        self.assertEqual(len(flows), 1)

    def test_rejects_oversized_batch(self):
        with self.assertRaisesRegex(ValueError, "512"):
            validate_request(
                {
                    "schema_version": 1,
                    "candidate_id": "A09",
                    "flows": [
                        {"flow_id": str(index), "features": {}}
                        for index in range(513)
                    ],
                }
            )

    def test_accepts_compact_raw_v1_batch(self):
        flows = validate_request(
            {
                "schema_version": 1,
                "candidate_id": "A09",
                "feature_encoding": "raw_v1",
                "flows": [
                    {
                        "features": [0.0] * len(RAW_FEATURE_ORDER),
                    }
                ],
            }
        )
        self.assertEqual(len(flows), 1)

    def test_rejects_wrong_compact_vector_length(self):
        with self.assertRaisesRegex(ValueError, "length"):
            validate_request(
                {
                    "schema_version": 1,
                    "candidate_id": "A09",
                    "feature_encoding": "raw_v1",
                    "flows": [{"flow_id": "compact", "features": [0.0]}],
                }
            )

    def test_service_latency_summary_uses_conservative_tail_index(self):
        summary = summarize_samples([1.0, 2.0, 3.0, 100.0])

        self.assertEqual(summary["samples"], 4)
        self.assertEqual(summary["p50"], 3.0)
        self.assertEqual(summary["p99"], 100.0)
        self.assertEqual(summary["max"], 100.0)

    def test_prediction_execution_mode_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "thread or inline"):
            InferenceServer(object(), prediction_execution="unbounded")


if __name__ == "__main__":
    unittest.main()
