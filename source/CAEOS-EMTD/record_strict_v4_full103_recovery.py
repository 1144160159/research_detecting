from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--failed-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("coverage manifest SHA mismatch")
    directories = sorted(path.parent for path in args.failed_root.glob("*/run.log"))
    if len(directories) != 14:
        raise ValueError(f"expected 14 failed CICIDS directories, found {len(directories)}")
    unexpected_metrics = [str(path) for path in args.failed_root.glob("*/metrics.json")]
    if unexpected_metrics:
        raise ValueError(f"recovery must precede successful CICIDS metrics: {unexpected_metrics}")
    marker = "FileNotFoundError: [Errno 2] No such file or directory: "
    expected_suffix = "'configs/cicids2017_strict.json'"
    for directory in directories:
        text = (directory / "run.log").read_text(encoding="utf-8")
        if marker not in text or expected_suffix not in text:
            raise ValueError(f"unexpected failure cause under {directory}")
        if not (directory / "provenance.json").is_file():
            raise ValueError(f"missing frozen provenance under {directory}")
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_full103_runtime_recovery_v1",
        "coverage_manifest_sha256": manifest["manifest_sha256"],
        "state_before_recovery": {
            "completed_scenarios": 47,
            "cicids_failed_directories": len(directories),
            "cicids_successful_metrics": 0,
            "failure": "missing runtime config file configs/cicids2017_strict.json",
            "algorithm_or_data_failure": False,
        },
        "recovery": {
            "action": "restore the already versioned local runtime config and resume",
            "config_path": "configs/cicids2017_strict.json",
            "config_sha256": file_hash(args.config),
            "failed_provenance_quarantined_before_resume": True,
            "quarantine_reason": (
                "the failed provenance recorded config SHA None, so restoring the "
                "config correctly changes the parameter fingerprint"
            ),
            "successful_provenance_reuse_allowed": False,
            "completed_artifacts_modified": False,
        },
    }
    payload["record_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
