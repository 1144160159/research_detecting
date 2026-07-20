"""Measure automatic deep-path fallback and recovery under an injected failure."""

from __future__ import annotations

import argparse
import json
import time

from hft_mgbs import AdaptiveExtractionPipeline, MultiGranularityExtractor, PacketRecord
from hft_mgbs.runtime import DeepPathCircuitBreaker


class FailOnceExtractor(MultiGranularityExtractor):
    def __init__(self) -> None:
        super().__init__()
        self.deep_calls = 0

    def deep_payload_features(self, payloads):
        self.deep_calls += 1
        if self.deep_calls == 1:
            raise RuntimeError("injected deep-path failure")
        return super().deep_payload_features(payloads)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovery-timeout-s", type=float, default=0.25)
    parser.add_argument("--probe-successes", type=int, default=2)
    parser.add_argument("--poll-interval-s", type=float, default=0.01)
    parser.add_argument("--deadline-s", type=float, default=2.0)
    parser.add_argument("--budget-us", type=float, default=1000.0)
    args = parser.parse_args()
    if (
        args.recovery_timeout_s < 0
        or args.poll_interval_s <= 0
        or args.deadline_s <= 0
        or args.budget_us <= 0
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
    )
    packet = PacketRecord(0.0, "10.0.0.1", "10.0.0.2", 1234, 443, 6, 128, b"probe")
    first = pipeline.process_batch(
        [packet], budget_us=args.budget_us, key_flows=[packet.flow_key]
    )[0]
    opened = breaker.snapshot()
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

    snapshot = breaker.snapshot()
    output = {
        "schema_version": 1,
        "status": "complete" if snapshot.state == "closed" else "deadline_exceeded",
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
        "evidence_scope": {
            "fallback_activation_verified": opened.state == "open",
            "fallback_recovery_verified": snapshot.last_recovery_s is not None,
            "key_flow_coverage_verified": pipeline.last_schedule_plan.key_flow_coverage == 1.0,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
