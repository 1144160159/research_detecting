from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_postselection_corruption import Task, build_tasks, task_key


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def key_digest(keys: set[str]) -> str:
    payload = "\n".join(sorted(keys)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def record_hash(record: dict[str, Any]) -> str:
    body = dict(record)
    body.pop("record_sha256", None)
    return canonical_hash(body)


def task_from_record(record: dict[str, Any]) -> Task:
    task = record.get("task")
    if not isinstance(task, dict):
        raise ValueError("corruption wrapper lacks task")
    return Task(
        tier=str(task["tier"]),
        suite=str(task["suite"]),
        scenario=str(task["scenario"]),
        corruption=str(task["corruption"]),
        modality=int(task["modality"]),
        severity=float(task["severity"]),
    )


def distribution(tasks: list[Task]) -> dict[str, dict[str, int]]:
    dimensions = {
        "tier": Counter(task.tier for task in tasks),
        "suite": Counter(task.suite for task in tasks),
        "corruption": Counter(task.corruption for task in tasks),
    }
    return {
        name: dict(sorted(counter.items()))
        for name, counter in dimensions.items()
    }


def started_task_key(path: Path, output_root: Path) -> str:
    relative = path.relative_to(output_root)
    if len(relative.parts) < 7:
        raise ValueError(f"unexpected provenance path: {path}")
    return "/".join(relative.parts[:4])


def summarize(
    protocol_path: Path,
    coverage_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    protocol = load(protocol_path)
    coverage = load(coverage_path)
    expected_tasks = build_tasks(protocol, coverage)
    expected = {task_key(task): task for task in expected_tasks}

    completed: dict[str, Task] = {}
    wrapper_paths = sorted(output_root.rglob("corruption_metrics.json"))
    for path in wrapper_paths:
        record = load(path)
        if record.get("schema_version") != (
            "strict_v4_postselection_corruption_run_v1"
        ):
            raise ValueError(f"unsupported corruption wrapper: {path}")
        if record.get("record_sha256") != record_hash(record):
            raise ValueError(f"corruption wrapper SHA mismatch: {path}")
        if (
            record.get("validation_passes") is not True
            or record.get(
                "unknown_or_test_labels_used_for_generation_fitting_or_selection"
            )
            is not False
        ):
            raise ValueError(f"corruption wrapper validation failed: {path}")
        task = task_from_record(record)
        key = task_key(task)
        if key not in expected:
            raise ValueError(f"wrapper task is outside frozen universe: {key}")
        if key in completed:
            raise ValueError(f"duplicate corruption wrapper task: {key}")
        completed[key] = task

    started = set()
    for path in output_root.rglob("provenance.json"):
        key = started_task_key(path, output_root)
        if key not in expected:
            raise ValueError(f"started task is outside frozen universe: {key}")
        started.add(key)

    completed_keys = set(completed)
    started_not_completed = started - completed_keys
    remaining_keys = set(expected) - completed_keys
    if not started_not_completed.issubset(remaining_keys):
        raise ValueError("started task accounting is inconsistent")

    completed_tasks = [expected[key] for key in sorted(completed_keys)]
    remaining_tasks = [expected[key] for key in sorted(remaining_keys)]
    started_tasks = [
        expected[key] for key in sorted(started_not_completed)
    ]
    result = {
        "schema_version": "strict_v4_corruption_progress_summary_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "effect_metrics_read": False,
        "expected": len(expected_tasks),
        "completed": len(completed_tasks),
        "started_not_completed": len(started_tasks),
        "remaining_including_started": len(remaining_tasks),
        "completion_fraction": len(completed_tasks) / len(expected_tasks),
        "completed_task_keys_sha256": key_digest(completed_keys),
        "remaining_task_keys_sha256": key_digest(remaining_keys),
        "completed_distribution": distribution(completed_tasks),
        "started_not_completed_distribution": distribution(started_tasks),
        "remaining_distribution": distribution(remaining_tasks),
        "started_not_completed_tasks": [
            asdict(task) for task in started_tasks
        ],
        "all_completed_wrappers_hash_valid": True,
        "all_completed_tasks_in_frozen_universe": True,
    }
    result["record_sha256"] = record_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = summarize(args.protocol, args.coverage, args.output_root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
