"""Bounded newline-delimited JSON inference service for the Rust data plane."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import statistics
import time
from collections import deque
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence

from .domain_features import transform_feature_rows


SCHEMA_VERSION = 1
MAX_LINE_BYTES = 16 * 1024 * 1024
MAX_BATCH_SIZE = 512
RAW_FEATURE_ORDER = (
    "packet_protocol",
    "packet_src_port",
    "packet_dst_port",
    "flow_packets",
    "flow_bytes",
    "flow_payload_bytes",
    "flow_duration_s",
    "flow_mean_length",
    "flow_length_std",
    "flow_min_length",
    "flow_max_length",
    "flow_mean_iat_s",
    "flow_iat_std_s",
    "flow_tcp_flags_or",
    "flow_fwd_packets",
    "flow_bwd_packets",
    "flow_fwd_bytes",
    "flow_bwd_bytes",
    "flow_fwd_payload_bytes",
    "flow_bwd_payload_bytes",
    "flow_fwd_mean_iat_s",
    "flow_bwd_mean_iat_s",
    "flow_fwd_iat_std_s",
    "flow_bwd_iat_std_s",
    "flow_fwd_tcp_flags_or",
    "flow_bwd_tcp_flags_or",
    "flow_fin_flag_count",
    "flow_syn_flag_count",
    "flow_rst_flag_count",
    "flow_psh_flag_count",
    "flow_ack_flag_count",
    "flow_urg_flag_count",
    "flow_ece_flag_count",
    "flow_cwr_flag_count",
    "payload_entropy",
    "payload_printable_ratio",
    "payload_zero_ratio",
    "quality_seen_deep_tier",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_request(
    payload: Mapping[str, object], expected_candidate_id: str = "A09"
) -> Sequence[Mapping[str, object]]:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")
    if payload.get("candidate_id") != expected_candidate_id:
        raise ValueError(
            "request candidate_id differs from expected {}".format(expected_candidate_id)
        )
    flows = payload.get("flows")
    if not isinstance(flows, list) or not flows:
        raise ValueError("flows must be a non-empty list")
    if len(flows) > MAX_BATCH_SIZE:
        raise ValueError("batch exceeds 512-flow release limit")
    for flow in flows:
        if not isinstance(flow, dict):
            raise ValueError("each flow must be an object")
        if (
            payload.get("feature_encoding") != "raw_v1"
            and not isinstance(flow.get("flow_id"), str)
        ):
            raise ValueError("flow_id must be a string")
        features = flow.get("features")
        if isinstance(features, list):
            if payload.get("feature_encoding") != "raw_v1":
                raise ValueError("compact features require raw_v1 encoding")
            if len(features) != len(RAW_FEATURE_ORDER):
                raise ValueError("raw_v1 feature vector length mismatch")
        elif not isinstance(features, dict):
            raise ValueError("features must be an object or raw_v1 vector")
    return flows


class BundleBackend:
    """Hash-bound ensemble backend for the campaign-selected candidate."""

    def __init__(
        self,
        bundle_path: Path,
        model_n_jobs: int = 1,
        inference_engine: str = "sklearn",
        expected_candidate_id: Optional[str] = None,
    ) -> None:
        import joblib

        if model_n_jobs < 1:
            raise ValueError("model_n_jobs must be positive")
        if inference_engine not in ("sklearn", "numpy_exact"):
            raise ValueError("inference_engine must be sklearn or numpy_exact")
        model_sha256 = sha256_file(bundle_path)
        bundle = joblib.load(bundle_path)
        if sha256_file(bundle_path) != model_sha256:
            raise ValueError("model bundle changed while it was being loaded")
        candidate_id = bundle.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError("model bundle candidate_id is invalid")
        if expected_candidate_id is not None and candidate_id != expected_candidate_id:
            raise ValueError("model bundle differs from the expected campaign winner")
        feature_profile = bundle.get("feature_profile")
        if feature_profile not in ("raw", "invariant_v1", "invariant_no_ports_v1"):
            raise ValueError("model bundle feature profile is not release-compatible")
        models = bundle.get("models")
        thresholds = bundle.get("thresholds")
        if not models or not thresholds or len(models) != len(thresholds):
            raise ValueError("model bundle has inconsistent ensemble members")
        self.bundle_path = bundle_path
        self.candidate_id = candidate_id
        self.feature_profile = feature_profile
        self.model_sha256 = model_sha256
        self.vectorizer = bundle["vectorizer"]
        self.models = models
        for model in self.models:
            model.set_params(n_jobs=model_n_jobs)
        self.model_n_jobs = model_n_jobs
        self.thresholds = [float(value) for value in thresholds]
        self.positive_indices = [int(value) for value in bundle["positive_indices"]]
        self.threshold = float(statistics.median(self.thresholds))
        self.metadata = dict(bundle.get("metadata", {}))
        self.inference_engine = inference_engine
        self.fast_predictor = None
        self.engine_compile_us = 0.0
        if inference_engine == "numpy_exact":
            from .a09_numpy_inference import A09NumpyExactPredictor

            started = time.perf_counter()
            self.fast_predictor = A09NumpyExactPredictor(
                self.models, self.positive_indices
            )
            self.engine_compile_us = (time.perf_counter() - started) * 1_000_000.0
        self.warmup_batch_size = 0
        self.warmup_us = 0.0

    def warmup(self, batch_size: int = MAX_BATCH_SIZE) -> float:
        if not 1 <= batch_size <= MAX_BATCH_SIZE:
            raise ValueError("warmup batch size is outside the release limit")
        flows = [
            {
                "flow_id": "warmup-{}".format(index),
                "features": {"flow_packets": float(index + 1)},
            }
            for index in range(batch_size)
        ]
        started = time.perf_counter()
        predictions = self.predict(flows)
        elapsed_us = (time.perf_counter() - started) * 1_000_000.0
        if len(predictions) != batch_size:
            raise RuntimeError("A09 warmup returned an incomplete batch")
        self.warmup_batch_size = batch_size
        self.warmup_us = elapsed_us
        return elapsed_us

    def predict(
        self,
        flows: Sequence[Mapping[str, object]],
        ordered_response: bool = False,
    ):
        import numpy as np

        rows = []
        for flow in flows:
            features = flow["features"]
            if isinstance(features, list):
                rows.append(dict(zip(RAW_FEATURE_ORDER, features)))
            else:
                rows.append(dict(features))
        projected = transform_feature_rows(rows, "invariant_no_ports_v1")
        matrix = self.vectorizer.transform(projected).astype(
            np.float32, copy=False
        )
        if self.fast_predictor is not None:
            probabilities = self.fast_predictor.predict_positive_probability(matrix)
        else:
            member_probabilities = [
                model.predict_proba(matrix)[:, positive_index]
                for model, positive_index in zip(
                    self.models, self.positive_indices
                )
            ]
            probabilities = np.mean(member_probabilities, axis=0)
        if ordered_response:
            return [
                [float(probability), int(probability >= self.threshold)]
                for probability in probabilities
            ]
        return [
            {
                "flow_id": flow.get("flow_id", str(index)),
                "attack_probability": float(probability),
                "label": int(probability >= self.threshold),
            }
            for index, (flow, probability) in enumerate(zip(flows, probabilities))
        ]

    def health(self) -> Dict[str, object]:
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "candidate_id": self.candidate_id,
            "classifier": self.metadata.get("classifier", "extra_trees_3_seed_ensemble"),
            "feature_profile": self.feature_profile,
            "algorithm_device": "cpu",
            "gpu_required": False,
            "deployment_host_role": "python_inference_node",
            "model_n_jobs": self.model_n_jobs,
            "inference_engine": self.inference_engine,
            "engine_compile_us": self.engine_compile_us,
            "warmup_batch_size": self.warmup_batch_size,
            "warmup_us": self.warmup_us,
            "model_bundle": str(self.bundle_path),
            "model_sha256": self.model_sha256,
            "threshold": self.threshold,
            "metadata": self.metadata,
        }


def summarize_samples(values):
    ordered = sorted(values)
    if not ordered:
        return {
            "samples": 0,
            "p50": 0.0,
            "p99": 0.0,
            "p999": 0.0,
            "max": 0.0,
        }

    def at(quantile):
        index = int((len(ordered) - 1) * quantile)
        if index < (len(ordered) - 1) * quantile:
            index += 1
        return float(ordered[min(index, len(ordered) - 1)])

    return {
        "samples": len(ordered),
        "p50": at(0.50),
        "p99": at(0.99),
        "p999": at(0.999),
        "max": float(ordered[-1]),
    }


class InferenceServer:
    def __init__(
        self,
        backend: BundleBackend,
        prediction_execution: str = "thread",
    ) -> None:
        if prediction_execution not in ("thread", "inline"):
            raise ValueError("prediction_execution must be thread or inline")
        self.backend = backend
        self.prediction_execution = prediction_execution
        self.requests = 0
        self.flows = 0
        self.failures = 0
        self.inference_latency_us = deque(maxlen=100_000)
        self.batch_sizes = deque(maxlen=100_000)

    async def handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            line = await reader.readline()
            if not line:
                return
            if len(line) > MAX_LINE_BYTES:
                raise ValueError("request line exceeds service limit")
            response = await self.process(json.loads(line.decode("utf-8")))
        except Exception as exc:  # Keep protocol failure explicit to Rust.
            self.failures += 1
            response = {
                "ok": False,
                "schema_version": SCHEMA_VERSION,
                "error": "{}: {}".format(type(exc).__name__, exc),
            }
        writer.write(
            json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
            + b"\n"
        )
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def process(self, payload):
        if payload.get("op") == "health":
            response = self.backend.health()
            response["service_counters"] = self.counters()
            return response
        flows = validate_request(payload, self.backend.candidate_id)
        started = time.perf_counter()
        ordered_response = payload.get("prediction_encoding") == "ordered_v1"
        if self.prediction_execution == "thread":
            predictions = await asyncio.to_thread(
                self.backend.predict,
                flows,
                ordered_response,
            )
        else:
            predictions = self.backend.predict(flows, ordered_response)
        elapsed_us = (time.perf_counter() - started) * 1_000_000.0
        self.requests += 1
        self.flows += len(flows)
        self.inference_latency_us.append(elapsed_us)
        self.batch_sizes.append(len(flows))
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "request_id": payload.get("request_id"),
            "candidate_id": self.backend.candidate_id,
            "predictions": predictions,
            "server_inference_us": elapsed_us,
        }

    def counters(self) -> Dict[str, object]:
        return {
            "requests": self.requests,
            "flows": self.flows,
            "failures": self.failures,
            "prediction_execution": self.prediction_execution,
            "server_inference_us": summarize_samples(
                self.inference_latency_us
            ),
            "batch_size": summarize_samples(self.batch_sizes),
        }


def parse_bind(value: str):
    host, separator, port = value.rpartition(":")
    if not separator or not host:
        raise argparse.ArgumentTypeError("--bind must be HOST:PORT")
    return host, int(port)


async def reverse_worker(
    connect, service: InferenceServer, reconnect_delay_s: float = 0.3
) -> None:
    while True:
        try:
            reader, writer = await asyncio.open_connection(
                connect[0],
                connect[1],
                limit=MAX_LINE_BYTES + 1,
            )
            print(
                json.dumps(
                    {"status": "reverse_connected", "peer": connect},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            while True:
                line = await reader.readline()
                if not line:
                    break
                try:
                    response = await service.process(
                        json.loads(line.decode("utf-8"))
                    )
                except Exception as exc:
                    service.failures += 1
                    response = {
                        "ok": False,
                        "schema_version": SCHEMA_VERSION,
                        "error": "{}: {}".format(type(exc).__name__, exc),
                    }
                writer.write(
                    json.dumps(
                        response,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                    + b"\n"
                )
                await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception:
            await asyncio.sleep(reconnect_delay_s)


async def serve(
    bind,
    model: Path,
    connect=None,
    model_n_jobs: int = 1,
    warmup_batch_size: int = MAX_BATCH_SIZE,
    prediction_execution: str = "thread",
    inference_engine: str = "sklearn",
    expected_candidate_id: Optional[str] = None,
) -> None:
    backend = BundleBackend(
        model,
        model_n_jobs=model_n_jobs,
        inference_engine=inference_engine,
        expected_candidate_id=expected_candidate_id,
    )
    backend.warmup(warmup_batch_size)
    service = InferenceServer(
        backend, prediction_execution=prediction_execution
    )
    server = await asyncio.start_server(
        service.handle,
        bind[0],
        bind[1],
        limit=MAX_LINE_BYTES + 1,
        reuse_address=True,
    )
    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(
        json.dumps(
            {
                "status": "ready",
                "listen": addresses,
                "health": backend.health(),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    tasks = [asyncio.create_task(server.serve_forever())]
    if connect is not None:
        tasks.append(asyncio.create_task(reverse_worker(connect, service)))
    await asyncio.gather(*tasks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", type=parse_bind, default=("0.0.0.0", 50051))
    parser.add_argument("--connect", type=parse_bind)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--expected-candidate-id")
    parser.add_argument("--model-n-jobs", type=int, default=1)
    parser.add_argument("--warmup-batch-size", type=int, default=MAX_BATCH_SIZE)
    parser.add_argument(
        "--prediction-execution",
        choices=("thread", "inline"),
        default="thread",
    )
    parser.add_argument(
        "--inference-engine",
        choices=("sklearn", "numpy_exact"),
        default="sklearn",
    )
    args = parser.parse_args()
    asyncio.run(
        serve(
            args.bind,
            args.model,
            args.connect,
            model_n_jobs=args.model_n_jobs,
            warmup_batch_size=args.warmup_batch_size,
            prediction_execution=args.prediction_execution,
            inference_engine=args.inference_engine,
            expected_candidate_id=args.expected_candidate_id,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Compatibility alias for existing A09 launchers and tests.  Candidate
# admission is now driven by the loaded, hash-bound bundle identity.
A09BundleBackend = BundleBackend
