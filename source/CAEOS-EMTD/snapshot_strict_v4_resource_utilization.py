from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def read_cpu_totals() -> tuple[int, int]:
    fields = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()
    values = [int(value) for value in fields[1:]]
    total = sum(values)
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return total, idle


def busy_fraction(
    before: tuple[int, int], after: tuple[int, int]
) -> float:
    total_delta = after[0] - before[0]
    idle_delta = after[1] - before[1]
    if total_delta <= 0:
        raise ValueError("nonpositive CPU tick delta")
    return float(1.0 - idle_delta / total_delta)


def memory_snapshot() -> dict[str, Any]:
    values = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        key, raw = line.split(":", 1)
        values[key] = int(raw.strip().split()[0]) * 1024
    total = values["MemTotal"]
    available = values["MemAvailable"]
    return {
        "total_bytes": total,
        "available_bytes": available,
        "used_fraction": float((total - available) / total),
        "swap_total_bytes": values["SwapTotal"],
        "swap_free_bytes": values["SwapFree"],
    }


def gpu_snapshot() -> list[dict[str, Any]]:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        output = subprocess.check_output(command, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    rows = []
    for line in output.splitlines():
        if not line.strip():
            continue
        index, name, used, total, utilization = [
            value.strip() for value in line.split(",", 4)
        ]
        rows.append(
            {
                "index": int(index),
                "name": name,
                "memory_used_mib": int(used),
                "memory_total_mib": int(total),
                "utilization_percent": int(utilization),
            }
        )
    return rows


def snapshot(
    *,
    protocol_path: Path,
    progress_path: Path,
    interval_seconds: float,
    sample_count: int,
) -> dict[str, Any]:
    if interval_seconds <= 0 or sample_count < 1:
        raise ValueError("positive interval and sample count are required")
    protocol = load(protocol_path)
    progress = load(progress_path)
    samples = []
    previous = read_cpu_totals()
    for index in range(sample_count):
        time.sleep(interval_seconds)
        current = read_cpu_totals()
        samples.append(
            {
                "sample": index + 1,
                "busy_fraction": busy_fraction(previous, current),
            }
        )
        previous = current
    busy_values = [sample["busy_fraction"] for sample in samples]
    minimum_target = float(
        protocol["execution"]["resource_policy"][
            "minimum_target_cpu_utilization_fraction"
        ]
    )
    preferred_target = float(
        protocol["execution"]["resource_policy"][
            "preferred_cpu_utilization_fraction"
        ]
    )
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_resource_utilization_snapshot_v1",
        "state": "complete_observation",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "logical_cpu_count": os.cpu_count(),
        "interval_seconds": interval_seconds,
        "sample_count": sample_count,
        "cpu": {
            "samples": samples,
            "minimum_busy_fraction": min(busy_values),
            "mean_busy_fraction": sum(busy_values) / len(busy_values),
            "maximum_busy_fraction": max(busy_values),
            "minimum_target_fraction": minimum_target,
            "preferred_target_fraction": preferred_target,
            "all_samples_at_least_minimum_target": all(
                value >= minimum_target for value in busy_values
            ),
            "mean_at_least_preferred_target": (
                sum(busy_values) / len(busy_values) >= preferred_target
            ),
        },
        "memory": memory_snapshot(),
        "gpu": gpu_snapshot(),
        "bindings": {
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "progress_file_sha256": file_hash(progress_path),
            "progress_manifest_sha256": progress["manifest_sha256"],
        },
        "claim_boundary": {
            "snapshot_is_time_bounded_not_full_run_utilization": True,
            "utilization_does_not_prove_scientific_effect": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--interval-seconds", type=float, default=2.0)
    parser.add_argument("--sample-count", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = snapshot(
        protocol_path=args.protocol,
        progress_path=args.progress,
        interval_seconds=args.interval_seconds,
        sample_count=args.sample_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
