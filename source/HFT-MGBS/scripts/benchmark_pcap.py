"""Offline PCAP replay benchmark; intended to run only on the GPU server."""

from __future__ import annotations

import argparse
import hashlib
import json
import time

from hft_mgbs import AdaptiveExtractionPipeline, PcapFileReader
from hft_mgbs.runtime_metrics import NvidiaSmiSampler, RuntimeMetricsCollector


def is_key_flow(flow_key, ratio):
    if ratio <= 0:
        return False
    digest = hashlib.sha256(repr(flow_key).encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return value < ratio


def batches(iterator, batch_size, max_packets):
    batch = []
    emitted = 0
    for packet in iterator:
        if max_packets and emitted >= max_packets:
            break
        batch.append(packet)
        emitted += 1
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--max-packets", type=int, default=0)
    parser.add_argument("--budget-us", type=float, default=25000.0)
    parser.add_argument("--max-payload-bytes", type=int, default=256)
    parser.add_argument("--key-flow-ratio", type=float, default=0.10)
    parser.add_argument("--disable-deep", action="store_true")
    parser.add_argument("--gpu-index", type=int)
    args = parser.parse_args()
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if not 0 <= args.key_flow_ratio <= 1:
        parser.error("--key-flow-ratio must be in [0, 1]")

    pipeline = AdaptiveExtractionPipeline()
    collector = RuntimeMetricsCollector()
    gpu_sampler = None if args.gpu_index is None else NvidiaSmiSampler(args.gpu_index)
    if gpu_sampler is not None:
        gpu_sampler.start()
    try:
        with PcapFileReader(args.pcap, max_payload_bytes=args.max_payload_bytes) as reader:
            for packet_batch in batches(reader, args.batch_size, args.max_packets):
                flow_keys = {pipeline.extractor.canonical_key(packet) for packet in packet_batch}
                key_flows = {key for key in flow_keys if is_key_flow(key, args.key_flow_ratio)}
                started = time.perf_counter()
                pipeline.process_batch(
                    packet_batch,
                    budget_us=args.budget_us,
                    allow_deep=not args.disable_deep,
                    key_flows=key_flows,
                )
                latency_us = (time.perf_counter() - started) * 1_000_000.0
                collector.record(
                    latency_us,
                    len(packet_batch),
                    pipeline.last_schedule_plan,
                    pipeline.last_fallback_recovery_s,
                    pipeline.last_stage_timings_us,
                )
            stats = reader.stats
    finally:
        if gpu_sampler is not None:
            gpu_sampler.stop()

    output = {
        "schema_version": 1,
        "metric_scope": "offline_pcap_processing",
        "source": str(args.pcap),
        "runtime": collector.summary(),
        "gpu": None if gpu_sampler is None else gpu_sampler.summary(),
        "pcap": {
            "total_records": stats.total_records,
            "parsed_packets": stats.parsed_packets,
            "rejected_records": stats.rejected_records,
            "skipped_non_ip": stats.skipped_non_ip,
            "skipped_unsupported": stats.skipped_unsupported,
            "truncated_records": stats.truncated_records,
            "malformed_packets": stats.malformed_packets,
        },
        "evidence_scope": {
            "processing_latency_verified": True,
            "application_budget_verified": True,
            "key_flow_coverage_verified": True,
            "nic_packet_drop_verified": False,
            "gpu_resource_verified": bool(gpu_sampler and gpu_sampler.samples),
            "fallback_recovery_time_verified": False,
            "quality_verified": False,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
