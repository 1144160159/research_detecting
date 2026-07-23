"""Deterministic synthetic smoke benchmark; it reads no dataset and writes no artifact."""

from __future__ import annotations

import argparse
import json
import random
import time

from hft_mgbs import AdaptiveExtractionPipeline, PacketRecord


def build_packets(count: int, flows: int, seed: int):
    randomizer = random.Random(seed)
    packets = []
    for index in range(count):
        flow = index % flows
        payload_size = randomizer.randrange(0, 128)
        packets.append(
            PacketRecord(
                timestamp=index / 100_000.0,
                src_ip=f"10.0.{flow // 256}.{flow % 256}",
                dst_ip="10.255.0.1",
                src_port=10_000 + flow,
                dst_port=443,
                protocol=6,
                wire_length=64 + payload_size,
                payload=bytes(randomizer.randrange(0, 256) for _ in range(payload_size)),
                tcp_flags=0x18,
            )
        )
    return packets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", type=int, default=20_000)
    parser.add_argument("--flows", type=int, default=1_000)
    parser.add_argument("--budget-us", type=float, default=25_000.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--key-flow-ratio", type=float, default=0.10)
    parser.add_argument("--disable-deep", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.key_flow_ratio <= 1:
        parser.error("--key-flow-ratio must be in [0, 1]")
    packets = build_packets(args.packets, args.flows, args.seed)
    pipeline = AdaptiveExtractionPipeline()
    unique_flow_keys = list(dict.fromkeys(packet.flow_key for packet in packets))
    key_count = int(len(unique_flow_keys) * args.key_flow_ratio)
    key_flows = unique_flow_keys[:key_count]
    started = time.perf_counter()
    results = pipeline.process_batch(
        packets,
        args.budget_us,
        allow_deep=not args.disable_deep,
        key_flows=key_flows,
    )
    elapsed = max(1e-9, time.perf_counter() - started)
    tier_counts = {tier: sum(result.tier == tier for result in results) for tier in ("base", "flow", "deep")}
    print(json.dumps({
        "packets": args.packets,
        "flows": args.flows,
        "elapsed_s": elapsed,
        "packets_per_s": args.packets / elapsed,
        "tier_counts": tier_counts,
        "active_flows": pipeline.extractor.active_flow_count,
        "schedule": {
            "effective_budget_us": pipeline.last_schedule_plan.effective_budget_us,
            "estimated_used_us": pipeline.last_schedule_plan.estimated_used_us,
            "actual_used_us": pipeline.last_schedule_plan.actual_used_us,
            "budget_overrun_count": pipeline.last_schedule_plan.budget_overrun_count,
            "estimated_budget_overrun_count": (
                pipeline.last_schedule_plan.estimated_budget_overrun_count
            ),
            "actual_budget_overrun_count": (
                pipeline.last_schedule_plan.actual_budget_overrun_count
            ),
            "key_flow_total": pipeline.last_schedule_plan.key_flow_total,
            "key_flow_covered": pipeline.last_schedule_plan.key_flow_covered,
            "key_flow_coverage": pipeline.last_schedule_plan.key_flow_coverage,
            "fallback_active": pipeline.last_schedule_plan.fallback_active,
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
