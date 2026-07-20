"""Micro-benchmark candidate feature groups without reading or writing datasets."""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import defaultdict

from hft_mgbs.features import MultiGranularityExtractor, PacketRecord
from hft_mgbs.representations import multi_level_vector, packet_length_sequence


def build_flows(flow_count, packets_per_flow, seed):
    randomizer = random.Random(seed)
    flows = defaultdict(list)
    for flow in range(flow_count):
        timestamp = flow * 0.0001
        for index in range(packets_per_flow):
            reverse = index % 3 == 2
            src, dst = (("server", "client") if reverse else ("client", "server"))
            src_port, dst_port = ((443, 10000 + flow) if reverse else (10000 + flow, 443))
            payload_size = randomizer.randrange(0, 96)
            packet = PacketRecord(
                timestamp=timestamp + index * 0.00001,
                src_ip=src,
                dst_ip=dst,
                src_port=src_port,
                dst_port=dst_port,
                protocol=6,
                wire_length=64 + payload_size,
                payload=bytes([flow % 251]) * payload_size,
                tcp_flags=0x18,
            )
            flows[flow].append(packet)
    return flows


def timed(name, function):
    started = time.perf_counter()
    checksum = function()
    elapsed = max(1e-9, time.perf_counter() - started)
    return name, {"elapsed_s": elapsed, "checksum": checksum}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flows", type=int, default=5000)
    parser.add_argument("--packets-per-flow", type=int, default=8)
    parser.add_argument("--max-sequence", type=int, default=20)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    flows = build_flows(args.flows, args.packets_per_flow, args.seed)
    packets = [packet for flow in flows.values() for packet in flow]

    def base():
        return sum(MultiGranularityExtractor.packet_features(packet)["packet_wire_length"] for packet in packets)

    def flow_stats():
        extractor = MultiGranularityExtractor(max_active_flows=args.flows * 2)
        for packet in packets:
            extractor.update(packet)
        return float(extractor.active_flow_count)

    def sequence():
        return sum(sum(packet_length_sequence(flow, args.max_sequence)["mask"]) for flow in flows.values())

    def multi_level():
        return sum(multi_level_vector(flow, args.max_sequence)["flow_summary"][1] for flow in flows.values())

    def deep_payload():
        return sum(MultiGranularityExtractor.deep_payload_features(packet.payload for packet in flow)["payload_entropy"] for flow in flows.values())

    results = dict(timed(name, function) for name, function in (
        ("base_packet", base),
        ("flow_state", flow_stats),
        ("bert_ps_style_sequence", sequence),
        ("yatc_uninet_style_multi_level", multi_level),
        ("deep_payload", deep_payload),
    ))
    for metrics in results.values():
        metrics["packets_per_s"] = len(packets) / metrics["elapsed_s"]
    print(json.dumps({"flows": args.flows, "packets": len(packets), "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
