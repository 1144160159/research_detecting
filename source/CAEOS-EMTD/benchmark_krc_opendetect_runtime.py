from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from benchmark_mdr_opendetect_runtime import (
    benchmark_once,
    execution_context,
    exact_batch,
    gpu_peak_memory_mb,
    peak_rss,
    peak_rss_mb,
    timing_summary,
    torch,
    validate_prediction,
)
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def benchmark(
    *,
    protocol: Dict[str, Any],
    source_identity: Dict[str, Any],
    output: Path,
) -> Dict[str, Any]:
    if os.environ.get("KRC_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError("exclusive-machine preflight marker is required")
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_opendetect_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError(
            "canonical KRC-OpenDetect efficiency protocol required"
        )
    identity = (
        str(source_identity["suite"]),
        str(source_identity["scenario"]),
        int(source_identity["training_seed"]),
    )
    matches = [
        item
        for item in protocol["sources"]
        if (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        )
        == identity
    ]
    if len(matches) != 1:
        raise ValueError("benchmark identity is not uniquely in protocol")
    source = matches[0]
    candidate = source["candidate"]
    comparator = source["comparator"]
    candidate_dir = Path(candidate["capture_dir"])
    candidate_manifest_path = candidate_dir / "capture_manifest.json"
    candidate_execution_path = candidate_dir / "capture_execution.json"
    candidate_manifest = load(candidate_manifest_path)
    candidate_execution = load(candidate_execution_path)
    candidate_artifact = (
        candidate_dir / candidate_manifest["runtime_artifact"]
    )
    inputs_path = candidate_dir / candidate_manifest["evaluation_inputs"]
    comparator_dir = Path(comparator["capture_dir"])
    comparator_manifest_path = comparator_dir / "capture_manifest.json"
    comparator_manifest = load(comparator_manifest_path)
    comparator_artifact = (
        comparator_dir / comparator_manifest["deployment_artifact"]
    )
    metrics_path = Path(comparator["source_metrics_path"])
    metrics = load(metrics_path)
    if (
        file_hash(candidate_manifest_path)
        != candidate["capture_manifest_file_sha256"]
        or candidate_manifest.get("schema_version")
        != "strict_v4_krc_csr_runtime_capture_v1"
        or candidate_manifest.get("manifest_sha256")
        != canonical_hash(candidate_manifest)
        or candidate_manifest.get("roundtrip", {}).get("passes")
        is not True
        or file_hash(candidate_execution_path)
        != candidate["capture_execution_file_sha256"]
        or candidate_execution.get("manifest_sha256")
        != canonical_hash(candidate_execution)
        or float(
            candidate_execution.get("total_capture_wall_seconds", -1.0)
        )
        != float(candidate["total_capture_wall_seconds"])
        or file_hash(candidate_artifact)
        != candidate["runtime_artifact_sha256"]
        or file_hash(inputs_path) != candidate["evaluation_inputs_sha256"]
        or file_hash(comparator_manifest_path)
        != comparator["capture_manifest_file_sha256"]
        or comparator_manifest.get("schema_version")
        != "strict_v4_opendetect_runtime_capture_v1"
        or comparator_manifest.get("equivalence", {}).get("passes")
        is not True
        or file_hash(comparator_artifact)
        != comparator["runtime_artifact_sha256"]
        or file_hash(metrics_path)
        != comparator["source_metrics_file_sha256"]
        or float(metrics.get("training_seconds", -1.0))
        != float(comparator["source_training_seconds"])
    ):
        raise ValueError("source artifact or manifest binding mismatch")
    krc_runtime = joblib.load(candidate_artifact)
    opendetect_runtime = joblib.load(comparator_artifact)
    with np.load(inputs_path, allow_pickle=False) as archive:
        modality_count = int(krc_runtime.evidence()["modality_count"])
        views = [
            np.asarray(archive[f"view_{index}"])
            for index in range(modality_count)
        ]
    candidate_evidence = dict(krc_runtime.evidence())
    comparator_evidence = dict(opendetect_runtime.evidence())
    if (
        candidate_evidence.get("schema_version")
        != "strict_v4_krc_csr_runtime_v1"
        or candidate_evidence.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
        or comparator_evidence.get("schema_version")
        != "strict_v4_opendetect_runtime_v1"
        or comparator_evidence.get("device")
        != comparator["runtime_device"]
        or comparator_evidence.get("contains_training_or_test_labels")
        is not False
    ):
        raise ValueError("runtime evidence is invalid")
    validate_prediction(krc_runtime.predict(views), len(views[0]))
    validate_prediction(opendetect_runtime.predict(views), len(views[0]))
    comparator_device = str(comparator_evidence["device"])
    if (
        torch is not None
        and torch.device(comparator_device).type == "cuda"
        and torch.cuda.is_available()
    ):
        torch.cuda.reset_peak_memory_stats(torch.device(comparator_device))
    policy = protocol["benchmark"]
    blocks = {}
    peak_before = peak_rss()
    for batch_size in policy["batch_sizes"]:
        batch = exact_batch(views, int(batch_size))
        for _ in range(int(policy["warmup_repetitions"])):
            benchmark_once(krc_runtime, batch)
            benchmark_once(
                opendetect_runtime,
                batch,
                synchronize=opendetect_runtime.synchronize,
            )
        timings = {"krc_csr_caeos_v1": [], "opendetect": []}
        for repetition in range(int(policy["timed_repetitions"])):
            order = (
                ("krc_csr_caeos_v1", krc_runtime, None),
                (
                    "opendetect",
                    opendetect_runtime,
                    opendetect_runtime.synchronize,
                ),
            )
            if repetition % 2:
                order = tuple(reversed(order))
            for name, runtime, synchronize in order:
                timings[name].append(
                    benchmark_once(
                        runtime, batch, synchronize=synchronize
                    )
                )
        blocks[str(batch_size)] = {
            name: {
                **timing_summary(values, int(batch_size)),
                "raw_seconds": values,
            }
            for name, values in timings.items()
        }
    peak_after = peak_rss()
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_opendetect_efficiency_benchmark_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source": {
            "suite": identity[0],
            "scenario": identity[1],
            "training_seed": identity[2],
            "candidate_capture_manifest_file_sha256": candidate[
                "capture_manifest_file_sha256"
            ],
            "candidate_capture_execution_file_sha256": candidate[
                "capture_execution_file_sha256"
            ],
            "candidate_runtime_artifact_sha256": candidate[
                "runtime_artifact_sha256"
            ],
            "evaluation_inputs_sha256": candidate[
                "evaluation_inputs_sha256"
            ],
            "comparator_seed": int(comparator["comparator_seed"]),
            "comparator_capture_manifest_file_sha256": comparator[
                "capture_manifest_file_sha256"
            ],
            "comparator_runtime_artifact_sha256": comparator[
                "runtime_artifact_sha256"
            ],
            "comparator_source_metrics_file_sha256": comparator[
                "source_metrics_file_sha256"
            ],
        },
        "same_input_evidence": {
            "input_origin": "candidate_krc_evaluation_inputs",
            "candidate_and_comparator_received_same_arrays": True,
            "modality_count": modality_count,
            "row_count": int(len(views[0])),
            "view_shapes": [list(view.shape) for view in views],
            "labels_loaded": False,
        },
        "runtime_evidence": {
            "candidate": candidate_evidence,
            "comparator": comparator_evidence,
        },
        "benchmark": blocks,
        "cost": {
            "krc_fit_wall_seconds_lower_bound_diagnostic": float(
                candidate_manifest["clean_capture_wall_seconds"]
                + candidate_manifest["robust_capture_wall_seconds"]
            ),
            "krc_total_capture_wall_seconds": float(
                candidate_execution["total_capture_wall_seconds"]
            ),
            "opendetect_training_seconds": float(
                comparator["source_training_seconds"]
            ),
            "opendetect_source_field": "training_seconds",
            "krc_artifact_bytes": int(candidate_artifact.stat().st_size),
            "opendetect_artifact_bytes": int(
                comparator_artifact.stat().st_size
            ),
        },
        "process_peak_rss": {
            "ru_maxrss_before": peak_before,
            "ru_maxrss_after": peak_after,
            "peak_host_rss_mb": peak_rss_mb(peak_after),
        },
        "peak_gpu_memory_mb": gpu_peak_memory_mb(comparator_device),
        "execution_context": execution_context(
            candidate_evidence, comparator_evidence
        ),
        "exclusive_machine_preflight_marker": "passed",
        "unknown_or_test_labels_used_for_benchmark_selection": False,
        "comparator_seed_reuse_supports_effectiveness_claim": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = benchmark(
        protocol=load(args.protocol.resolve()),
        source_identity={
            "suite": args.suite,
            "scenario": args.scenario,
            "training_seed": args.training_seed,
        },
        output=args.output.resolve(),
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
