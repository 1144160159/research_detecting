"""Conservative aggregation of split inference-node resource evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .resource_sampling import sha256_file


IDENTITY_FIELDS = (
    "candidate_id",
    "runtime_candidate",
    "algorithm_device",
    "gpu_required",
    "manifest_sha256",
    "resource_limits_sha256",
)


def aggregate_resource_evidence(
    runs: list[Mapping[str, object]],
    minimum_runs: int = 3,
) -> dict[str, object]:
    errors = []
    if len(runs) < minimum_runs:
        errors.append("run_count")
    reference_identity = None
    process_rows = []
    gpu_rows = []
    for index, run in enumerate(runs, start=1):
        prefix = "run{}".format(index)
        if (
            run.get("scope")
            != "split_inference_node_resource_sampling"
        ):
            errors.append("{}.scope".format(prefix))
        if run.get("accepted") is not True:
            errors.append("{}.accepted".format(prefix))
        if run.get("final_pareto_ingestion_allowed") is not False:
            errors.append("{}.final_pareto_marker".format(prefix))
        identity = {name: run.get(name) for name in IDENTITY_FIELDS}
        if reference_identity is None:
            reference_identity = identity
        elif identity != reference_identity:
            errors.append("{}.identity".format(prefix))
        process = run.get("process")
        gpu = run.get("gpu")
        if not isinstance(process, Mapping):
            errors.append("{}.process".format(prefix))
        else:
            process_rows.append(process)
        if not isinstance(gpu, Mapping):
            errors.append("{}.gpu".format(prefix))
        else:
            gpu_rows.append(gpu)

    def maximum(rows, name):
        values = [row.get(name) for row in rows]
        if (
            not values
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                for value in values
            )
        ):
            errors.append("observed.{}".format(name))
            return None
        return max(values)

    def minimum(rows, name):
        values = [row.get(name) for row in rows]
        if (
            not values
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                for value in values
            )
        ):
            errors.append("observed.{}".format(name))
            return None
        return min(values)

    observed = {
        "process_sample_count_min": minimum(
            process_rows, "sample_count"
        ),
        "cpu_cores_used_max": maximum(
            process_rows, "cpu_cores_used_max"
        ),
        "host_cpu_fraction_max": maximum(
            process_rows, "host_cpu_fraction_max"
        ),
        "rss_bytes_max": maximum(process_rows, "rss_bytes_max"),
        "host_memory_fraction_max": maximum(
            process_rows, "host_memory_fraction_max"
        ),
        "threads_max": maximum(process_rows, "threads_max"),
        "process_tree_pid_count_max": maximum(
            process_rows, "process_tree_pid_count_max"
        ),
        "gpu_sample_count_min": minimum(gpu_rows, "sample_count"),
        "system_gpu_utilization_fraction_max": maximum(
            gpu_rows, "system_gpu_utilization_fraction_max"
        ),
        "system_gpu_memory_fraction_max": maximum(
            gpu_rows, "system_gpu_memory_fraction_max"
        ),
        "service_gpu_utilization_fraction_max": maximum(
            gpu_rows, "service_gpu_utilization_fraction_max"
        ),
        "service_gpu_memory_fraction_max": maximum(
            gpu_rows, "service_gpu_memory_fraction_max"
        ),
        "service_gpu_memory_mib_max": maximum(
            gpu_rows, "service_gpu_memory_mib_max"
        ),
        "service_gpu_process_present": any(
            row.get("service_gpu_process_present") is True
            for row in gpu_rows
        ),
    }
    if observed["service_gpu_process_present"]:
        errors.append("observed.service_gpu_process_present")
    return {
        "schema_version": 1,
        "scope": "split_inference_node_resource_repeat_audit",
        "accepted": not errors,
        "errors": sorted(set(errors)),
        "run_count": len(runs),
        "identity": reference_identity or {},
        "observed_worst_case": observed,
        "final_pareto_ingestion_allowed": False,
    }


def load_resource_runs(paths: list[Path]):
    import json

    runs = []
    provenance = []
    seen = set()
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            raise ValueError("duplicate resource evidence path")
        seen.add(resolved)
        runs.append(json.loads(path.read_text(encoding="utf-8")))
        provenance.append(
            {"path": str(path), "sha256": sha256_file(path)}
        )
    return runs, provenance
