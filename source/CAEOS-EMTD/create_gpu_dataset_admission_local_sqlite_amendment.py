from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_gpu_dataset_admission_execution_protocol import verify_protocol
from create_strict_v4_external_confirmation_protocol import canonical_hash


FAILURE = "sqlite3.OperationalError: database is locked"


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def create(
    protocol: Dict[str, Any],
    *,
    protocol_file_sha256: str,
    failure_log: Path,
    local_work_dir: Path,
    result_path: Path,
    result_complete_marker: Path,
    result_passed_marker: Path,
    implementation_sha256: str,
) -> Dict[str, Any]:
    verify_protocol(protocol)
    if (
        result_path.exists()
        or result_complete_marker.exists()
        or result_passed_marker.exists()
    ):
        raise ValueError("local SQLite amendment requires zero audit results")
    text = failure_log.read_text(encoding="utf-8", errors="replace")
    if FAILURE not in text:
        raise ValueError("bound failure log is not the NFS SQLite lock failure")
    if not local_work_dir.is_absolute():
        raise ValueError("local SQLite work directory must be absolute")
    if str(local_work_dir).startswith("/opt/data/"):
        raise ValueError("local SQLite work directory must not be on NFS")
    bindings = protocol["bindings"]
    value: Dict[str, Any] = {
        "schema_version": (
            "gpu_dataset_admission_local_sqlite_amendment_v1"
        ),
        "status": "frozen_after_nfs_sqlite_failure_before_audit_results",
        "execution_admitted": True,
        "source_execution_protocol_manifest_sha256": protocol[
            "manifest_sha256"
        ],
        "source_execution_protocol_file_sha256": protocol_file_sha256,
        "failure": {
            "class": "sqlite_database_locked_on_nfs_work_directory",
            "exact_error": FAILURE,
            "failure_log": str(failure_log.resolve()),
            "failure_log_sha256": file_hash(failure_log),
            "formal_audit_result_created": False,
        },
        "change": {
            "from_work_directory": (
                "/opt/data/private/wangwt/ParkAttackKE/"
                "CAEOS-EMTD-strict-v4-20260717/"
                "runs/gpu_dataset_full_admission_audit_v1"
            ),
            "to_local_work_directory": str(local_work_dir),
            "sqlite_only_ephemeral_work_location_changed": True,
            "source_archives_changed": False,
            "scanner_changed": False,
            "configs_changed": False,
            "label_group_feature_or_admission_gates_changed": False,
            "result_location_changed": False,
            "model_training_or_effect_metrics_added": False,
        },
        "command": {
            "resource_prefix": ["ionice", "-c3", "nice", "-n", "15"],
            "python": (
                "/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
            ),
            "scanner": bindings["scanner"]["path"],
            "arguments": [
                "--protocol",
                bindings["parent_protocol"]["path"],
                "--lsnm-config",
                bindings["lsnm_config"]["path"],
                "--cic-config",
                bindings["cic_config"]["path"],
                "--work-dir",
                str(local_work_dir),
                "--output-dir",
                str(result_path.parent.resolve()),
            ],
        },
        "result_contract": {
            "result_path": str(result_path.resolve()),
            "complete_marker": str(result_complete_marker.resolve()),
            "passed_marker": str(result_passed_marker.resolve()),
            "source_and_gate_contract_identical_to_original_protocol": True,
        },
        "output_counts_at_freeze": {
            "audit": int(result_path.exists()),
            "complete": int(result_complete_marker.exists()),
            "passed": int(result_passed_marker.exists()),
        },
        "input_file_sha256": {
            "parent_protocol": bindings["parent_protocol"]["sha256"],
            "scanner": bindings["scanner"]["sha256"],
            "lsnm_config": bindings["lsnm_config"]["sha256"],
            "cic_config": bindings["cic_config"]["sha256"],
            "failure_log": file_hash(failure_log),
        },
        "implementation_sha256": {
            "create_gpu_dataset_admission_local_sqlite_amendment.py": (
                implementation_sha256
            )
        },
        "claim_boundary": {
            "amendment_is_storage_recovery_not_scientific_change": True,
            "successful_execution_still_requires_original_full_admission": (
                True
            ),
            "does_not_read_or_create_model_effect_metrics": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--failure-log", type=Path, required=True)
    parser.add_argument("--local-work-dir", type=Path, required=True)
    parser.add_argument("--result-path", type=Path, required=True)
    parser.add_argument("--complete-marker", type=Path, required=True)
    parser.add_argument("--passed-marker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    implementation = Path(__file__).resolve()
    value = create(
        load_json(protocol_path),
        protocol_file_sha256=file_hash(protocol_path),
        failure_log=args.failure_log.resolve(),
        local_work_dir=args.local_work_dir,
        result_path=args.result_path.resolve(),
        result_complete_marker=args.complete_marker.resolve(),
        result_passed_marker=args.passed_marker.resolve(),
        implementation_sha256=file_hash(implementation),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
