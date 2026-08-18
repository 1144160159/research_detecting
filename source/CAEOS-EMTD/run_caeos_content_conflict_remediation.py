from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional


SCHEMA_VERSION = "caeos_content_conflict_remediation_queue_v1"
DATASETS = (
    "5gad_2022",
    "edge_iiotset",
    "dohbrw2020",
    "cicids2017",
    "ciciot2022",
    "cicids2018",
    "cicddos2019",
    "cic_bot_iot",
    "ciciot2023",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_json(path: Path, value: Any) -> None:
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


def run_logged(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab", buffering=0) as handle:
        encoded = ("COMMAND " + " ".join(command) + "\n").encode("utf-8")
        handle.write(encoded)
        result = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"command failed with exit {result.returncode}: {command[1]}")


def wait_for_ciciot_repair(transaction: Path, status: dict[str, Any], status_path: Path) -> Path:
    receipt_path = transaction / "application_receipt.json"
    rollback_path = transaction / "rollback_receipt.json"
    while True:
        if rollback_path.is_file():
            raise RuntimeError(f"CICIoT2023 identity repair rolled back: {rollback_path}")
        if receipt_path.is_file():
            receipt = load_json(receipt_path)
            if receipt.get("status") != "applied":
                raise RuntimeError("CICIoT2023 identity repair receipt is not applied")
            proof_path = Path(receipt["proof_path"])
            if not proof_path.is_file():
                raise FileNotFoundError(f"CICIoT2023 identity proof absent: {proof_path}")
            return proof_path
        status["waiting_for"] = str(receipt_path)
        status["updated_at_unix"] = time.time()
        atomic_json(status_path, status)
        time.sleep(60)


def rebuild_edge_completion(
    args: argparse.Namespace,
    manifest: Path,
    item: dict[str, Any],
    status_path: Path,
    state: dict[str, Any],
    log_path: Path,
) -> Path:
    item["stage"] = "rebuild_completion"
    atomic_json(status_path, state)
    completion_path = (
        args.output_root
        / "_control"
        / "feature_extraction"
        / "completion.lane2.edge_iiotset.json"
    )
    completion_command = [
        sys.executable,
        str(args.code_root / "rebuild_caeos_dataset_completion.py"),
        "--dataset-manifest",
        str(manifest),
        "--template-completion",
        str(args.completion_template),
        "--output",
        str(completion_path),
        "--workers",
        str(args.workers),
    ]
    run_logged(completion_command, log_path)
    item["completion_path"] = str(completion_path)
    return completion_path


def queue_state(workers: int) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workers": workers,
        "dataset_parallelism": 1,
        "dataset_order": list(DATASETS),
        "started_at_unix": time.time(),
        "updated_at_unix": time.time(),
        "all_complete": False,
        "datasets": {dataset_id: {"state": "pending"} for dataset_id in DATASETS},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--code-root", required=True, type=Path)
    parser.add_argument("--scratch-root", required=True, type=Path)
    parser.add_argument("--ciciot-audit-scratch", required=True, type=Path)
    parser.add_argument("--ciciot-transaction", required=True, type=Path)
    parser.add_argument("--completion-template", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--buckets", type=int, default=256)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 16:
        raise ValueError("workers must be between 1 and 16")

    control = args.output_root / "_control" / "paper_protocol_v1"
    audit_root = control / "duplicate_audits"
    policy_root = control / "content_conflict_policies"
    queue_root = control / "content_conflict_remediation"
    status_path = queue_root / "queue.status.json"
    log_root = queue_root / "logs"
    state = queue_state(args.workers)
    atomic_json(status_path, state)
    try:
        for dataset_id in DATASETS:
            item = state["datasets"][dataset_id]
            item.update({"state": "running", "started_at_unix": time.time()})
            state["active_dataset"] = dataset_id
            state["updated_at_unix"] = time.time()
            atomic_json(status_path, state)

            manifest = args.output_root / dataset_id / "dataset.manifest.json"
            if not manifest.is_file():
                raise FileNotFoundError(f"dataset manifest absent: {manifest}")
            output_dir = policy_root / dataset_id
            success_path = output_dir / "SUCCESS.json"
            if success_path.is_file():
                success = load_json(success_path)
                if success.get("gate_pass") is True:
                    if dataset_id == "edge_iiotset":
                        completion_path = (
                            args.output_root
                            / "_control"
                            / "feature_extraction"
                            / "completion.lane2.edge_iiotset.json"
                        )
                        if not completion_path.is_file():
                            rebuild_edge_completion(
                                args,
                                manifest,
                                item,
                                status_path,
                                state,
                                log_root / f"{dataset_id}.log",
                            )
                        scratch = args.scratch_root / dataset_id
                        if scratch.exists():
                            shutil.rmtree(scratch)
                    item.update(
                        {
                            "state": "complete",
                            "completed_at_unix": time.time(),
                            "resumed_existing_success": True,
                            "success_path": str(success_path),
                        }
                    )
                    atomic_json(status_path, state)
                    continue

            repair_proof: Optional[Path] = None
            if dataset_id == "ciciot2023":
                repair_proof = wait_for_ciciot_repair(
                    args.ciciot_transaction, state, status_path
                )
                state.pop("waiting_for", None)
                scratch = args.ciciot_audit_scratch
                audit_path = audit_root / "ciciot2023.v2.json"
                scratch_owned = False
            else:
                scratch = args.scratch_root / dataset_id
                audit_path = audit_root / f"{dataset_id}.content_contract_v2.json"
                scratch_owned = True
                audit_command = [
                    sys.executable,
                    str(args.code_root / "audit_caeos_flow_duplicates.py"),
                    "--dataset-manifest",
                    str(manifest),
                    "--scratch",
                    str(scratch),
                    "--output",
                    str(audit_path),
                    "--buckets",
                    str(args.buckets),
                    "--class-parallelism",
                    "1",
                    "--shards-per-class",
                    str(args.workers),
                    "--resume",
                    "--keep-scratch",
                ]
                item["stage"] = "refresh_duplicate_audit"
                atomic_json(status_path, state)
                run_logged(audit_command, log_root / f"{dataset_id}.log")

            policy_command = [
                sys.executable,
                str(args.code_root / "build_caeos_content_conflict_policy.py"),
                "--dataset-manifest",
                str(manifest),
                "--audit",
                str(audit_path),
                "--scratch",
                str(scratch),
                "--output-dir",
                str(output_dir),
                "--workers",
                str(args.workers),
                "--buckets",
                str(args.buckets),
                "--resume",
                "--reuse-partitions",
            ]
            if repair_proof is not None:
                policy_command.extend(["--repair-proof", str(repair_proof)])
            item["stage"] = "build_content_conflict_policy"
            atomic_json(status_path, state)
            run_logged(policy_command, log_root / f"{dataset_id}.log")
            success = load_json(success_path)
            if success.get("gate_pass") is not True:
                raise RuntimeError(f"content policy gate failed for {dataset_id}")
            if dataset_id == "edge_iiotset":
                rebuild_edge_completion(
                    args,
                    manifest,
                    item,
                    status_path,
                    state,
                    log_root / f"{dataset_id}.log",
                )
            if scratch_owned:
                shutil.rmtree(scratch)
            item.update(
                {
                    "state": "complete",
                    "stage": "complete",
                    "completed_at_unix": time.time(),
                    "success_path": str(success_path),
                    "scratch_removed": scratch_owned,
                }
            )
            state["updated_at_unix"] = time.time()
            atomic_json(status_path, state)
    except BaseException as error:
        active = state.get("active_dataset")
        if active:
            state["datasets"][active].update(
                {"state": "failed", "error": f"{type(error).__name__}: {error}"}
            )
        state["all_complete"] = False
        state["updated_at_unix"] = time.time()
        atomic_json(status_path, state)
        raise

    state.pop("active_dataset", None)
    state["all_complete"] = True
    state["completed_at_unix"] = time.time()
    state["updated_at_unix"] = time.time()
    atomic_json(status_path, state)
    print(json.dumps(state, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
