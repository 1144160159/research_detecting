"""Measure fallback and recovery in one configured candidate pipeline.

When ``--pcap`` is supplied, the same pipeline instance that receives the
controlled deep-path fault also processes real PCAP traffic while the breaker
is open.  Recovery probes then close the breaker.  This is an application-path
fault-injection check; it is not evidence of physical-NIC packet loss.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time

from hft_mgbs import (
    AdaptiveExtractionPipeline,
    MultiGranularityExtractor,
    PacketRecord,
    PcapFileReader,
)
from hft_mgbs.batching import bounded_batches
from hft_mgbs.runtime import DeepPathCircuitBreaker
from hft_mgbs.runtime_metrics import RuntimeMetricsCollector


class FailOnceExtractor(MultiGranularityExtractor):
    def __init__(self) -> None:
        super().__init__()
        self.deep_calls = 0

    def deep_payload_features(self, payloads):
        self.deep_calls += 1
        if self.deep_calls == 1:
            raise RuntimeError("injected deep-path failure")
        return super().deep_payload_features(payloads)


def is_key_flow(flow_key, ratio):
    if ratio <= 0:
        return False
    digest = hashlib.sha256(repr(flow_key).encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return value < ratio


def plan_observation(plan):
    return {
        "budget_overrun_count": plan.budget_overrun_count,
        "actual_budget_overrun_count": plan.actual_budget_overrun_count,
        "actual_used_us": plan.actual_used_us,
        "configured_budget_us": plan.configured_budget_us,
        "key_flow_total": plan.key_flow_total,
        "key_flow_covered": plan.key_flow_covered,
        "key_flow_coverage": plan.key_flow_coverage,
        "fallback_active": plan.fallback_active,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap")
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--max-packets", type=int, default=512)
    parser.add_argument("--max-payload-bytes", type=int, default=256)
    parser.add_argument("--key-flow-ratio", type=float, default=0.10)
    parser.add_argument(
        "--execution-budget-safety-ratio", type=float, default=0.50
    )
    parser.add_argument("--recovery-timeout-s", type=float, default=0.25)
    parser.add_argument("--probe-successes", type=int, default=2)
    parser.add_argument("--poll-interval-s", type=float, default=0.01)
    parser.add_argument("--deadline-s", type=float, default=2.0)
    parser.add_argument("--budget-us", type=float, default=5000.0)
    args = parser.parse_args()
    if (
        args.recovery_timeout_s < 0
        or args.poll_interval_s <= 0
        or args.deadline_s <= 0
        or args.budget_us <= 0
        or args.batch_size <= 0
        or args.max_packets < 0
        or args.max_payload_bytes < 0
        or not 0 <= args.key_flow_ratio <= 1
        or not 0 < args.execution_budget_safety_ratio <= 1
    ):
        parser.error("invalid timing configuration")

    breaker = DeepPathCircuitBreaker(
        failure_threshold=1,
        recovery_timeout_s=args.recovery_timeout_s,
        probe_success_threshold=args.probe_successes,
    )
    pipeline = AdaptiveExtractionPipeline(
        extractor=FailOnceExtractor(),
        circuit_breaker=breaker,
        execution_budget_safety_ratio=args.execution_budget_safety_ratio,
    )
    packet = PacketRecord(0.0, "10.0.0.1", "10.0.0.2", 1234, 443, 6, 128, b"probe")
    first = pipeline.process_batch(
        [packet], budget_us=args.budget_us, key_flows=[packet.flow_key]
    )[0]
    opened = breaker.snapshot()
    observations = [plan_observation(pipeline.last_schedule_plan)]
    fallback_pcap_batches = 0
    fallback_pcap_packets = 0
    fallback_runtime = RuntimeMetricsCollector()
    pcap_stats = None
    if args.pcap:
        with PcapFileReader(
            args.pcap, max_payload_bytes=args.max_payload_bytes
        ) as reader:
            for packet_batch in bounded_batches(
                reader, args.batch_size, args.max_packets
            ):
                flow_keys = {
                    pipeline.extractor.canonical_key(item)
                    for item in packet_batch
                }
                key_flows = {
                    key
                    for key in flow_keys
                    if is_key_flow(key, args.key_flow_ratio)
                }
                started_batch = time.perf_counter()
                pipeline.process_batch(
                    packet_batch,
                    budget_us=args.budget_us,
                    key_flows=key_flows,
                )
                latency_us = (
                    time.perf_counter() - started_batch
                ) * 1_000_000.0
                fallback_runtime.record(
                    latency_us,
                    len(packet_batch),
                    pipeline.last_schedule_plan,
                    pipeline.last_fallback_recovery_s,
                    pipeline.last_stage_timings_us,
                )
                observations.append(
                    plan_observation(pipeline.last_schedule_plan)
                )
                fallback_pcap_batches += 1
                fallback_pcap_packets += len(packet_batch)
            pcap_stats = reader.stats

    started = time.monotonic()
    iterations = 0
    while breaker.snapshot().state != "closed" and time.monotonic() - started < args.deadline_s:
        time.sleep(args.poll_interval_s)
        iterations += 1
        probe = PacketRecord(
            time.monotonic(), packet.src_ip, packet.dst_ip, packet.src_port,
            packet.dst_port, packet.protocol, packet.wire_length, packet.payload,
        )
        pipeline.process_batch(
            [probe], budget_us=args.budget_us, key_flows=[probe.flow_key]
        )
        observations.append(plan_observation(pipeline.last_schedule_plan))

    snapshot = breaker.snapshot()
    total_budget_overruns = sum(
        item["budget_overrun_count"] for item in observations
    )
    minimum_key_coverage = min(
        item["key_flow_coverage"] for item in observations
    )
    fallback_pcap_verified = (
        not args.pcap
        or (
            fallback_pcap_batches > 0
            and all(
                item["fallback_active"]
                for item in observations[1 : 1 + fallback_pcap_batches]
            )
        )
    )
    output = {
        "schema_version": 2,
        "status": (
            "complete"
            if snapshot.state == "closed" and fallback_pcap_verified
            else "deadline_exceeded_or_incomplete"
        ),
        "candidate": {
            "batch_size": args.batch_size,
            "budget_us": args.budget_us,
            "execution_budget_safety_ratio": (
                args.execution_budget_safety_ratio
            ),
            "key_flow_ratio": args.key_flow_ratio,
            "deep_enabled": True,
        },
        "fault_injection": "single_deep_extractor_exception",
        "initial_tier_after_failure": first.tier,
        "opened_state": opened.state,
        "final_state": snapshot.state,
        "fallback_recovery_s": snapshot.last_recovery_s,
        "configured_recovery_timeout_s": args.recovery_timeout_s,
        "configured_budget_us": args.budget_us,
        "probe_success_threshold": args.probe_successes,
        "iterations": iterations,
        "key_flow_coverage": pipeline.last_schedule_plan.key_flow_coverage,
        "hard_constraint_observations": {
            "budget_overrun_count": total_budget_overruns,
            "minimum_key_flow_coverage": minimum_key_coverage,
        },
        "fallback_pcap": {
            "source": args.pcap,
            "batches": fallback_pcap_batches,
            "packets": fallback_pcap_packets,
            "runtime": (
                fallback_runtime.summary()
                if fallback_pcap_batches
                else None
            ),
            "reader_stats": (
                None
                if pcap_stats is None
                else {
                    "total_records": pcap_stats.total_records,
                    "parsed_packets": pcap_stats.parsed_packets,
                    "rejected_records": pcap_stats.rejected_records,
                }
            ),
        },
        "schedule_observations": observations,
        "evidence_scope": {
            "fallback_activation_verified": opened.state == "open",
            "fallback_recovery_verified": snapshot.last_recovery_s is not None,
            "fallback_real_pcap_processing_verified": (
                bool(args.pcap) and fallback_pcap_verified
            ),
            "same_candidate_pipeline_instance_verified": True,
            "application_budget_verified": total_budget_overruns == 0,
            "key_flow_coverage_verified": minimum_key_coverage == 1.0,
            "nic_packet_drop_verified": False,
            "end_to_end_latency_verified": False,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
