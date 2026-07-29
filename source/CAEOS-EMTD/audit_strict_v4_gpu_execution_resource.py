from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def audit(
    gpu_execution_path: Path,
    *,
    minimum_mean_utilization: float,
    maximum_peak_memory_mib: float,
) -> dict[str, Any]:
    path = gpu_execution_path.resolve()
    evidence = load_canonical(path, "GPU execution evidence")
    samples = evidence.get("samples", [])
    utilization = [
        float(sample["utilization_percent"]) for sample in samples
    ]
    if not utilization:
        raise ValueError("GPU execution evidence has no utilization samples")
    mean_utilization = statistics.fmean(utilization)
    median_utilization = statistics.median(utilization)
    gates = {
        "source_cuda_evidence_passes": bool(evidence.get("passes")),
        "mean_gpu_utilization_at_least_minimum": (
            mean_utilization >= minimum_mean_utilization
        ),
        "peak_gpu_memory_below_limit": (
            float(evidence["peak_gpu_memory_mib"])
            < maximum_peak_memory_mib
        ),
        "no_sample_errors": not evidence.get("sample_errors"),
    }
    gates["all_pass"] = all(gates.values())
    result: dict[str, Any] = {
        "schema_version": "strict_v4_gpu_execution_resource_audit_v1",
        "state": "pass" if gates["all_pass"] else "fail",
        "source": {
            "path": str(path),
            "file_sha256": file_hash(path),
            "manifest_sha256": evidence["manifest_sha256"],
        },
        "requirements": {
            "minimum_mean_gpu_utilization_percent": (
                minimum_mean_utilization
            ),
            "maximum_peak_gpu_memory_mib": maximum_peak_memory_mib,
        },
        "observed": {
            "sample_count": len(utilization),
            "mean_gpu_utilization_percent": mean_utilization,
            "median_gpu_utilization_percent": median_utilization,
            "fraction_samples_at_least_50_percent": sum(
                item >= 50.0 for item in utilization
            )
            / len(utilization),
            "fraction_samples_at_least_80_percent": sum(
                item >= 80.0 for item in utilization
            )
            / len(utilization),
            "peak_gpu_utilization_percent": evidence[
                "peak_gpu_utilization_percent"
            ],
            "peak_gpu_memory_mib": evidence["peak_gpu_memory_mib"],
            "torch_peak_memory_allocated_mib": evidence[
                "torch_peak_memory_allocated_mib"
            ],
            "torch_peak_memory_reserved_mib": evidence[
                "torch_peak_memory_reserved_mib"
            ],
        },
        "gates": gates,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu-execution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--minimum-mean-utilization", type=float, default=50.0
    )
    parser.add_argument(
        "--maximum-peak-memory-mib", type=float, default=45000.0
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = audit(
        args.gpu_execution,
        minimum_mean_utilization=args.minimum_mean_utilization,
        maximum_peak_memory_mib=args.maximum_peak_memory_mib,
    )
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
