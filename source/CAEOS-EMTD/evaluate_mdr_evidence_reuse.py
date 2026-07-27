from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Sequence

import joblib
import numpy as np

from benchmark_mdr_selected_system_runtime import (
    exact_batch,
    execution_context,
    timing_summary,
)
from caeos.mdr_evidence_reuse_runtime import MDREvidenceReuseRuntime
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_caeos_runtime import selected_modality


DISCRETE_KEYS = (
    "prediction",
    "active",
    "any_missing",
    "clean_prediction",
    "robust_prediction",
    "view_missing",
)
NUMERIC_KEYS = (
    "risk",
    "probability",
    "clean_probability",
    "robust_probability",
    "clean_risk",
    "robust_risk",
    "missing_risk",
    "conflict",
    "disagreement",
    "threshold",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def compare_outputs(
    reference: Dict[str, np.ndarray],
    candidate: Dict[str, np.ndarray],
    *,
    tolerance: float,
) -> Dict[str, Any]:
    discrete = {
        key: bool(
            key in reference
            and key in candidate
            and np.array_equal(reference[key], candidate[key])
        )
        for key in DISCRETE_KEYS
    }
    numeric = {}
    for key in NUMERIC_KEYS:
        if key not in reference or key not in candidate:
            numeric[key] = float("inf")
            continue
        left = np.asarray(reference[key], dtype=np.float64)
        right = np.asarray(candidate[key], dtype=np.float64)
        if (
            left.shape != right.shape
            or not np.isfinite(left).all()
            or not np.isfinite(right).all()
        ):
            numeric[key] = float("inf")
        else:
            numeric[key] = float(np.max(np.abs(left - right)))
    passes = all(discrete.values()) and all(
        value <= float(tolerance) for value in numeric.values()
    )
    return {
        "discrete_array_equal": discrete,
        "numeric_max_absolute_difference": numeric,
        "absolute_tolerance": float(tolerance),
        "passes": bool(passes),
    }


def timed(runtime, views: Sequence[np.ndarray]) -> float:
    started = time.perf_counter()
    output = runtime.predict(views)
    elapsed = time.perf_counter() - started
    if (
        "prediction" not in output
        or len(output["prediction"]) != len(views[0])
        or not np.isfinite(elapsed)
        or elapsed <= 0.0
    ):
        raise ValueError("invalid optimization benchmark output")
    return float(elapsed)


def evaluate(
    *,
    protocol: Dict[str, Any],
    identity: Dict[str, Any],
    output: Path,
) -> Dict[str, Any]:
    if os.environ.get("MDR_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError("exclusive-machine preflight marker is required")
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_evidence_reuse_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR optimization protocol required")
    key = (
        str(identity["suite"]),
        str(identity["scenario"]),
        int(identity["training_seed"]),
    )
    matches = [
        source
        for source in protocol["sources"]
        if (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        )
        == key
    ]
    if len(matches) != 1:
        raise ValueError("optimization source is not uniquely registered")
    source = matches[0]
    capture_dir = Path(source["capture_dir"])
    manifest_path = capture_dir / "capture_manifest.json"
    manifest = load(manifest_path)
    artifact = capture_dir / manifest["runtime_artifact"]
    inputs_path = capture_dir / manifest["evaluation_inputs"]
    if (
        file_hash(manifest_path)
        != source["capture_manifest_file_sha256"]
        or file_hash(artifact) != source["runtime_artifact_sha256"]
        or file_hash(inputs_path) != source["evaluation_inputs_sha256"]
        or manifest.get("roundtrip", {}).get("passes") is not True
    ):
        raise ValueError("MDR optimization source hash mismatch")
    base = joblib.load(artifact)
    optimized = MDREvidenceReuseRuntime(base)
    output.parent.mkdir(parents=True, exist_ok=True)
    optimized_path = output.parent / "mdr_evidence_reuse_runtime.joblib"
    pairwise_path = output.parent / "embedded_pairwise_runtime.joblib"
    joblib.dump(optimized, optimized_path, compress=3)
    joblib.dump(base.clean_runtime, pairwise_path, compress=3)
    optimized_loaded = joblib.load(optimized_path)
    pairwise_loaded = joblib.load(pairwise_path)
    inputs = np.load(inputs_path, allow_pickle=False)
    views = [
        np.asarray(inputs[f"view_{index}"])
        for index in range(base.evidence()["modality_count"])
    ]
    tolerance = float(
        protocol["equivalence"][
            "probability_risk_and_diagnostics_max_absolute_tolerance"
        ]
    )
    condition_records = []
    for condition in protocol["conditions"]:
        if condition == "clean":
            modality = None
            severity = 0.0
            condition_views = views
        else:
            modality = selected_modality(
                protocol["coverage_manifest_sha256"],
                key[0],
                key[1],
                condition,
                len(views),
            )
            severity = float(protocol["fixed_severity"][condition])
            condition_views = base.corrupt(
                views,
                family=condition,
                modality=modality,
                severity=severity,
                seed=int(source["corruption_seed"]),
            )
        reference = base.predict(condition_views)
        candidate = optimized.predict(condition_views)
        reloaded = optimized_loaded.predict(condition_views)
        direct = compare_outputs(
            reference, candidate, tolerance=tolerance
        )
        roundtrip = compare_outputs(
            reference, reloaded, tolerance=tolerance
        )
        if not direct["passes"] or not roundtrip["passes"]:
            raise ValueError(
                f"MDR evidence-reuse equivalence failed: {condition}"
            )
        condition_records.append(
            {
                "condition": condition,
                "modality": modality,
                "severity": severity,
                "corruption_seed": int(source["corruption_seed"]),
                "direct_equivalence": direct,
                "serialization_equivalence": roundtrip,
            }
        )
    policy = protocol["benchmark"]
    warmups = int(policy["warmup_repetitions"])
    repetitions = int(policy["timed_repetitions"])
    benchmark = {}
    methods = {
        "original_mdr_caeos_v1": base,
        "mdr_evidence_reuse_v1": optimized_loaded,
        "embedded_caeos_pairwise": pairwise_loaded,
    }
    for batch_size in policy["batch_sizes"]:
        batch = exact_batch(views, int(batch_size))
        for _ in range(warmups):
            for runtime in methods.values():
                runtime.predict(batch)
        timings = {name: [] for name in methods}
        names = list(methods)
        for repetition in range(repetitions):
            offset = repetition % len(names)
            order = names[offset:] + names[:offset]
            for name in order:
                timings[name].append(timed(methods[name], batch))
        benchmark[str(batch_size)] = {
            name: {
                **timing_summary(values, int(batch_size)),
                "raw_seconds": values,
            }
            for name, values in timings.items()
        }
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_evidence_reuse_capture_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source": {
            "suite": key[0],
            "scenario": key[1],
            "training_seed": key[2],
            "corruption_seed": int(source["corruption_seed"]),
            "capture_manifest_file_sha256": file_hash(manifest_path),
            "runtime_artifact_sha256": file_hash(artifact),
            "evaluation_inputs_sha256": file_hash(inputs_path),
        },
        "equivalence": {
            "condition_count": len(condition_records),
            "conditions": condition_records,
            "all_direct_pass": True,
            "all_serialization_pass": True,
            "labels_loaded": False,
        },
        "benchmark": benchmark,
        "artifact": {
            "original_mdr_bytes": int(artifact.stat().st_size),
            "optimized_mdr_bytes": int(optimized_path.stat().st_size),
            "optimized_mdr_sha256": file_hash(optimized_path),
            "embedded_pairwise_bytes": int(pairwise_path.stat().st_size),
            "embedded_pairwise_sha256": file_hash(pairwise_path),
        },
        "fit_cost": {
            "unchanged_by_inference_optimization": True,
            "clean_plus_robust_wall_seconds_lower_bound": float(
                manifest["clean_capture_wall_seconds"]
                + manifest["robust_capture_wall_seconds"]
            ),
        },
        "runtime_evidence": optimized_loaded.evidence(),
        "execution_context": execution_context(),
        "exclusive_machine_preflight_marker": "passed",
        "unknown_or_test_labels_used": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
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
    value = evaluate(
        protocol=load(args.protocol),
        identity={
            "suite": args.suite,
            "scenario": args.scenario,
            "training_seed": args.training_seed,
        },
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
