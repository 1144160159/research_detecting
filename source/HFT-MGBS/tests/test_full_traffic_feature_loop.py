from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.features import PacketRecord
from hft_mgbs.full_traffic_feature_loop import (
    CURRENT_HARDWARE_BACKEND,
    FAILOVER_RECEIPT_SCOPE,
    NATIVE_XDP_BACKEND,
    CapturedPacketBatch,
    FullTrafficFeatureLoopError,
    FullTrafficFeatureSystem,
    audit_high_speed_metrics,
    validate_feature_loop_policy,
)


ROOT = Path(__file__).resolve().parents[1]


def policy():
    return json.loads(
        (ROOT / "configs" / "full_traffic_feature_loop_v1.json").read_text(
            encoding="utf-8"
        )
    )


def packet(timestamp=0.0, reverse=False, service_port=443):
    if reverse:
        return PacketRecord(
            timestamp, "10.0.0.2", "10.0.0.1", service_port, 10000, 6, 128, b"reply"
        )
    return PacketRecord(
        timestamp, "10.0.0.1", "10.0.0.2", 10000, service_port, 6, 128, b"request"
    )


def failover_receipt(source=NATIVE_XDP_BACKEND, target=CURRENT_HARDWARE_BACKEND):
    return {
        "scope": FAILOVER_RECEIPT_SCOPE,
        "current_backend": source,
        "selected_backend": target,
        "outcome": "switched_to_" + target,
        "mutations_performed": True,
        "recovery_required": False,
        "error": None,
        "after_snapshot": {"active_backend": target},
        "receipt_sha256": "a" * 64,
    }


def runtime_metrics():
    return {
        "packets_received": 1000,
        "packets_parsed": 1000,
        "parse_rejected": 0,
        "capture_packets_dropped": 0,
        "flows_emitted": 5,
        "deep_flows_selected": 3,
        "deep_flows_deferred": 2,
        "budget_overrun_count": 0,
        "key_flows_total": 2,
        "key_flow_coverage": 1.0,
        "key_flow_conservation": {
            "eligible_equals_enqueue_outcomes": True,
            "enqueued_equals_completion_outcomes": True,
            "eligible_conservation_abs_delta": 0,
            "completion_conservation_abs_delta": 0,
        },
    }


class FullTrafficFeatureLoopTests(unittest.TestCase):
    def test_frozen_policy_is_self_consistent(self):
        validate_feature_loop_policy(policy())

    def test_feature_reservoir_binding_is_fail_closed(self):
        value = policy()
        value["unified_feature_reservoir"]["canonical_policy_sha256"] = "0" * 64
        with self.assertRaisesRegex(FullTrafficFeatureLoopError, "reservoir binding"):
            validate_feature_loop_policy(value)

    def test_every_parsed_packet_is_recognized_and_every_flow_emits_a_result(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=NATIVE_XDP_BACKEND
        )
        packets = (
            packet(0.0),
            packet(0.1, reverse=True),
            PacketRecord(0.2, "a", "b", 12345, 23456, 17, 64, b""),
        )
        result = system.process_batch(
            CapturedPacketBatch(NATIVE_XDP_BACKEND, 1, 1, packets, source_id="batch-1")
        )
        self.assertEqual(len(result.recognitions), 3)
        self.assertEqual(len(result.flow_results), 2)
        self.assertEqual(len(result.unified_flow_records), 2)
        self.assertEqual(
            result.receipt["extraction"]["safe_scalar_count"], 85
        )
        self.assertEqual(
            result.receipt["extraction"]["sequence_column_count"], 17
        )
        self.assertEqual(
            result.receipt["extraction"]["persistent_schema_column_count"], 143
        )
        self.assertEqual(
            result.receipt["extraction"]["online_extractable_column_count"], 120
        )
        self.assertEqual(
            result.receipt["extraction"]["model_candidate_persistent_column_count"],
            116,
        )
        self.assertTrue(
            result.receipt["conservation"]["unified_feature_reservoir"]
        )
        self.assertTrue(result.recognitions[0].is_key_flow)
        self.assertEqual(result.recognitions[0].service_class, "https")
        self.assertEqual(result.recognitions[2].service_class, "unclassified")
        self.assertTrue(result.receipt["all_traffic_recognition_complete"])
        self.assertTrue(result.receipt["feature_extraction_loop_closed"])
        self.assertTrue(all(result.receipt["conservation"].values()))
        self.assertFalse(result.receipt["production_sla_qualified"])

    def test_one_online_flow_can_emit_multiple_exact_sixty_four_packet_segments(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=NATIVE_XDP_BACKEND
        )
        packets = tuple(packet(index * 0.001) for index in range(65))
        result = system.process_batch(
            CapturedPacketBatch(NATIVE_XDP_BACKEND, 1, 1, packets)
        )
        self.assertEqual(len(result.flow_results), 1)
        self.assertEqual(len(result.unified_flow_records), 2)
        self.assertEqual(
            [record.flow_segment_index for record in result.unified_flow_records],
            [0, 1],
        )
        self.assertEqual(
            result.receipt["extraction"]["unified_flow_segments"], 2
        )
        self.assertTrue(result.receipt["conservation"]["unified_feature_reservoir"])
        self.assertTrue(result.receipt["feature_extraction_loop_closed"])

    def test_rejected_or_dropped_packets_remain_in_denominator_and_fail_closed(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=CURRENT_HARDWARE_BACKEND
        )
        result = system.process_batch(
            CapturedPacketBatch(
                CURRENT_HARDWARE_BACKEND,
                1,
                1,
                (packet(),),
                parse_rejected=1,
                capture_dropped=2,
            )
        )
        self.assertEqual(result.receipt["capture"]["packets_received"], 2)
        self.assertFalse(result.receipt["capture"]["lossless"])
        self.assertFalse(result.receipt["all_traffic_recognition_complete"])
        self.assertFalse(result.receipt["feature_extraction_loop_closed"])
        self.assertTrue(result.receipt["degraded_mode"])

    def test_backend_switch_preserves_flow_state_and_scheduler_feedback(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=NATIVE_XDP_BACKEND
        )
        first = system.process_batch(
            CapturedPacketBatch(NATIVE_XDP_BACKEND, 1, 1, (packet(0.0),))
        )
        first_cost = first.receipt["budget"]["scheduler_estimates"]["cost_us"]["flow"]
        self.assertTrue(system.apply_failover_receipt(failover_receipt()))
        second = system.process_batch(
            CapturedPacketBatch(
                CURRENT_HARDWARE_BACKEND,
                2,
                1,
                (packet(0.1, reverse=True),),
            )
        )
        self.assertEqual(second.flow_results[0].features["flow_packets"], 2.0)
        self.assertEqual(
            second.unified_flow_records[0].safe_scalars["packet_count_total"],
            2.0,
        )
        self.assertTrue(second.receipt["degraded_mode"])
        self.assertNotEqual(
            second.receipt["budget"]["scheduler_estimates"]["cost_us"]["flow"],
            first_cost,
        )
        summary = system.summary()
        self.assertTrue(summary["flow_state_preserved_across_switches"])
        self.assertTrue(
            summary["unified_feature_reservoir_preserved_across_switches"]
        )
        self.assertEqual(len(summary["transitions"]), 1)

    def test_stale_pre_switch_batch_is_rejected_after_handoff(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=NATIVE_XDP_BACKEND
        )
        system.apply_failover_receipt(failover_receipt())
        with self.assertRaisesRegex(FullTrafficFeatureLoopError, "stale"):
            system.process_batch(
                CapturedPacketBatch(NATIVE_XDP_BACKEND, 1, 1, (packet(),))
            )

    def test_high_speed_rust_metrics_recompute_the_same_method_closure(self):
        audit = audit_high_speed_metrics(
            runtime_metrics(), backend=CURRENT_HARDWARE_BACKEND, policy=policy()
        )
        self.assertTrue(audit["method_contract_verified"])
        self.assertTrue(audit["degraded_mode"])
        self.assertEqual(audit["errors"], [])
        self.assertFalse(audit["production_sla_qualified"])

    def test_high_speed_metrics_reject_feature_or_parse_conservation_drift(self):
        metrics = runtime_metrics()
        metrics["parse_rejected"] = 1
        metrics["deep_flows_deferred"] = 1
        audit = audit_high_speed_metrics(
            metrics, backend=NATIVE_XDP_BACKEND, policy=policy()
        )
        self.assertFalse(audit["method_contract_verified"])
        self.assertIn("metrics.parse_conservation", audit["errors"])
        self.assertIn("metrics.feature_tier_conservation", audit["errors"])

    def test_failed_or_unsealed_transition_cannot_change_generation(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=NATIVE_XDP_BACKEND
        )
        receipt = failover_receipt()
        receipt["receipt_sha256"] = "not-a-sha"
        with self.assertRaisesRegex(FullTrafficFeatureLoopError, "sealed"):
            system.apply_failover_receipt(receipt)
        self.assertEqual(system.active_backend, NATIVE_XDP_BACKEND)
        self.assertEqual(system.generation, 1)

    def test_malformed_normalized_packet_is_rejected_before_state_update(self):
        system = FullTrafficFeatureSystem(
            policy=policy(), active_backend=NATIVE_XDP_BACKEND
        )
        malformed = PacketRecord(0.0, "a", "b", 70000, 53, 17, 64)
        with self.assertRaisesRegex(FullTrafficFeatureLoopError, "port"):
            system.process_batch(
                CapturedPacketBatch(NATIVE_XDP_BACKEND, 1, 1, (malformed,))
            )
        self.assertEqual(system.pipeline.extractor.active_flow_count, 0)

    def test_high_speed_audit_cli_accepts_nested_tpacket_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            raw = base / "raw.json"
            raw.write_text(
                json.dumps({"pipeline_metrics": runtime_metrics()}), encoding="utf-8"
            )
            output = base / "audit.json"
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(ROOT)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "audit_full_traffic_feature_loop.py"),
                    "--metrics",
                    str(raw),
                    "--policy",
                    str(ROOT / "configs" / "full_traffic_feature_loop_v1.json"),
                    "--backend",
                    CURRENT_HARDWARE_BACKEND,
                    "--output",
                    str(output),
                    "--require-closed-loop",
                ],
                cwd=str(ROOT),
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            audit = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(audit["method_contract_verified"])
            self.assertTrue(audit["degraded_mode"])


if __name__ == "__main__":
    unittest.main()
