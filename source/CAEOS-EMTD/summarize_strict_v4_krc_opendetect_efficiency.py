from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_mdr_opendetect_efficiency import (
    aggregate_benchmarks as aggregate_reference,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def reference_inputs(
    records: list[Dict[str, Any]], protocol: Dict[str, Any]
) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_opendetect_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(records) != 306
    ):
        raise ValueError("canonical KRC protocol and 306 benchmarks required")
    reference_protocol = deepcopy(protocol)
    reference_protocol["schema_version"] = (
        "strict_v4_mdr_opendetect_efficiency_protocol_v1"
    )
    reference_protocol["manifest_sha256"] = canonical_hash(
        reference_protocol
    )
    output = []
    for record in records:
        if (
            record.get("schema_version")
            != "strict_v4_krc_opendetect_efficiency_benchmark_v1"
            or record.get("state") != "complete"
            or record.get("manifest_sha256") != canonical_hash(record)
            or record.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
        ):
            raise ValueError("invalid KRC-OpenDetect benchmark record")
        transformed = deepcopy(record)
        transformed["schema_version"] = (
            "strict_v4_mdr_opendetect_efficiency_benchmark_v1"
        )
        transformed["protocol_manifest_sha256"] = reference_protocol[
            "manifest_sha256"
        ]
        transformed["benchmark"] = {
            batch: {
                (
                    "mdr_caeos_v1"
                    if method == "krc_csr_caeos_v1"
                    else method
                ): values
                for method, values in block.items()
            }
            for batch, block in transformed["benchmark"].items()
        }
        cost = transformed["cost"]
        transformed["cost"] = {
            "mdr_fit_wall_seconds_lower_bound_diagnostic": cost[
                "krc_fit_wall_seconds_lower_bound_diagnostic"
            ],
            "mdr_total_capture_wall_seconds": cost[
                "krc_total_capture_wall_seconds"
            ],
            "opendetect_training_seconds": cost[
                "opendetect_training_seconds"
            ],
            "opendetect_source_field": cost["opendetect_source_field"],
            "mdr_artifact_bytes": cost["krc_artifact_bytes"],
            "opendetect_artifact_bytes": cost[
                "opendetect_artifact_bytes"
            ],
        }
        transformed["manifest_sha256"] = canonical_hash(transformed)
        output.append(transformed)
    return output, reference_protocol


def aggregate_benchmarks(
    records: list[Dict[str, Any]], protocol: Dict[str, Any]
) -> Dict[str, Any]:
    transformed, reference_protocol = reference_inputs(records, protocol)
    return aggregate_reference(transformed, reference_protocol)


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    records = []
    registry = []
    for source in protocol["sources"]:
        path = (
            run_root
            / "benchmarks"
            / str(source["suite"])
            / str(source["scenario"])
            / f"seed{int(source['training_seed'])}"
            / "benchmark.json"
        )
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC-OpenDetect benchmark: {path}"
            )
        records.append(load(path))
        registry.append(
            {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "benchmark_file_sha256": file_hash(path),
            }
        )
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_opendetect_efficiency_summary_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate_benchmarks(records, protocol),
        "benchmark_file_registry": registry,
        "claim_boundary": protocol["claim_boundary"],
        "statistical_reference": {
            "implementation": (
                "summarize_strict_v4_mdr_opendetect_efficiency.py"
            ),
            "same_ratio_bootstrap_contract": True,
            "candidate_names_adapted_without_value_changes": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(load(args.protocol.resolve()), args.run_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
