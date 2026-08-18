from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Optional


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def valid_existing_report(path: Path, manifest: dict[str, Any]) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    return bool(
        value.get("gate_pass")
        and value.get("dataset_manifest_sha256") == manifest.get("manifest_sha256")
    )


def dataset_size(manifest: dict[str, Any]) -> int:
    return sum(int(item.get("size_bytes", 0)) for item in manifest["class_csvs"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--audit-script", required=True, type=Path)
    parser.add_argument("--scratch-root", required=True, type=Path)
    parser.add_argument("--dataset-parallelism", type=int, default=2)
    parser.add_argument("--class-parallelism", type=int, default=2)
    parser.add_argument("--shards-per-class", type=int, default=8)
    parser.add_argument("--buckets", type=int, default=256)
    parser.add_argument("--dataset-attempts", type=int, default=4)
    parser.add_argument("--retry-delay-seconds", type=int, default=60)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--readiness-watcher", type=Path)
    args = parser.parse_args()

    manifests: list[tuple[Path, dict[str, Any]]] = []
    for path in args.output_root.glob("*/dataset.manifest.json"):
        manifest = load_json(path)
        if manifest.get("complete") and manifest.get("class_csvs"):
            manifests.append((path, manifest))
    manifests.sort(
        key=lambda item: (
            item[1].get("dataset_id") == "ciciot2023",
            dataset_size(item[1]),
        ),
        reverse=True,
    )
    control = args.output_root / "_control" / "paper_protocol_v1"
    report_root = control / "duplicate_audits"
    log_root = report_root / "logs"
    report_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    state: dict[str, Any] = {
        "schema_version": "caeos_parallel_duplicate_audit_queue_v1",
        "configuration": {
            "dataset_parallelism": args.dataset_parallelism,
            "class_parallelism": args.class_parallelism,
            "shards_per_class": args.shards_per_class,
            "maximum_worker_processes": (
                args.dataset_parallelism
                * args.class_parallelism
                * args.shards_per_class
            ),
        },
        "started_at_epoch": time.time(),
        "datasets": {
            manifest["dataset_id"]: {
                "state": "pending",
                "rows": manifest["row_count"],
                "bytes": dataset_size(manifest),
                "manifest": str(path),
            }
            for path, manifest in manifests
        },
        "all_complete": False,
    }

    def save_state() -> None:
        state["updated_at_epoch"] = time.time()
        atomic_json(args.status, state)

    save_state()

    def run_dataset(item: tuple[Path, dict[str, Any]]) -> tuple[str, str]:
        manifest_path, manifest = item
        dataset_id = manifest["dataset_id"]
        report = report_root / f"{dataset_id}.json"
        if valid_existing_report(report, manifest):
            with lock:
                state["datasets"][dataset_id]["state"] = "skipped_current_pass"
                save_state()
            return dataset_id, "skipped_current_pass"
        with lock:
            state["datasets"][dataset_id]["state"] = "running"
            state["datasets"][dataset_id]["started_at_epoch"] = time.time()
            save_state()
        command = [
            sys.executable,
            str(args.audit_script),
            "--dataset-manifest",
            str(manifest_path),
            "--scratch",
            str(args.scratch_root / dataset_id),
            "--output",
            str(report),
            "--buckets",
            str(args.buckets),
            "--class-parallelism",
            str(args.class_parallelism),
            "--shards-per-class",
            str(args.shards_per_class),
            "--resume",
        ]
        log_path = log_root / f"{dataset_id}.log"
        result: Optional[subprocess.CompletedProcess[Any]] = None
        with log_path.open("a", encoding="utf-8", newline="\n") as log:
            for attempt in range(1, args.dataset_attempts + 1):
                log.write(
                    f"START {time.time()} attempt={attempt}/{args.dataset_attempts} "
                    f"{' '.join(command)}\n"
                )
                log.flush()
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
                if result.returncode == 0:
                    break
                log.write(f"RETRY returncode={result.returncode}\n")
                log.flush()
                if attempt < args.dataset_attempts:
                    time.sleep(args.retry_delay_seconds)
        if result is None:
            raise RuntimeError(f"duplicate audit did not start for {dataset_id}")
        final_state = "complete" if result.returncode == 0 else "failed"
        with lock:
            state["datasets"][dataset_id]["state"] = final_state
            state["datasets"][dataset_id]["returncode"] = result.returncode
            state["datasets"][dataset_id]["finished_at_epoch"] = time.time()
            save_state()
        if result.returncode != 0:
            raise RuntimeError(f"duplicate audit failed for {dataset_id}: {result.returncode}")
        return dataset_id, final_state

    failures: list[str] = []
    watcher_started = False
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.dataset_parallelism
    ) as executor:
        futures = {executor.submit(run_dataset, item): item for item in manifests}
        for future in concurrent.futures.as_completed(futures):
            manifest = futures[future][1]
            dataset_id = manifest["dataset_id"]
            try:
                _, result_state = future.result()
            except BaseException as error:
                failures.append(f"{dataset_id}: {error}")
                continue
            if (
                dataset_id == "ciciot2023"
                and result_state in {"complete", "skipped_current_pass"}
                and args.readiness_watcher is not None
                and not watcher_started
            ):
                subprocess.Popen(
                    [
                        str(args.readiness_watcher),
                        str(args.readiness_watcher.parent),
                        str(args.output_root),
                        "60",
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                watcher_started = True
    state["all_complete"] = not failures
    state["failures"] = failures
    state["finished_at_epoch"] = time.time()
    save_state()
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
