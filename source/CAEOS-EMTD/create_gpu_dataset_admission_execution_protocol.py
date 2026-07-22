from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("manifest_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def create_protocol(
    *,
    parent_protocol: Path,
    scanner: Path,
    lsnm_config: Path,
    cic_config: Path,
    runner: Path,
    result_path: Path,
) -> dict[str, Any]:
    parent = json.loads(parent_protocol.read_text(encoding="utf-8"))
    if parent.get("status") != "frozen_before_full_scan_and_training":
        raise ValueError("parent dataset expansion protocol is not frozen")
    if result_path.exists():
        raise ValueError("admission execution protocol must be frozen before results")
    bindings = {
        name: {"path": str(path), "sha256": file_sha256(path)}
        for name, path in {
            "parent_protocol": parent_protocol,
            "scanner": scanner,
            "lsnm_config": lsnm_config,
            "cic_config": cic_config,
            "runner": runner,
        }.items()
    }
    protocol: dict[str, Any] = {
        "schema_version": "gpu_dataset_admission_execution_protocol_v1",
        "status": "frozen_before_full_scan",
        "result_count_at_freeze": 0,
        "parent_schema": parent["schema_version"],
        "bindings": bindings,
        "resource_policy": {
            "prerequisite": "strict_v4_postefficiency_claim_chain_v2/chain_complete",
            "nice": 15,
            "ionice_class": 3,
            "model_training": False,
        },
    }
    protocol["manifest_sha256"] = canonical_sha256(protocol)
    return protocol


def verify_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("schema_version") != "gpu_dataset_admission_execution_protocol_v1":
        raise ValueError("unexpected admission execution protocol schema")
    if protocol.get("manifest_sha256") != canonical_sha256(protocol):
        raise ValueError("admission execution protocol canonical hash mismatch")
    for binding in protocol["bindings"].values():
        path = Path(binding["path"])
        if file_sha256(path) != binding["sha256"]:
            raise ValueError(f"bound implementation changed: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--scanner", type=Path, required=True)
    parser.add_argument("--lsnm-config", type=Path, required=True)
    parser.add_argument("--cic-config", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--result-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        parent_protocol=args.parent_protocol,
        scanner=args.scanner,
        lsnm_config=args.lsnm_config,
        cic_config=args.cic_config,
        runner=args.runner,
        result_path=args.result_path,
    )
    verify_protocol(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
