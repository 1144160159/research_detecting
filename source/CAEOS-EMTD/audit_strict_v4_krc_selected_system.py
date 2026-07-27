from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from summarize_strict_v4_krc_selected_system import aggregate_benchmarks


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    run_root: Path,
) -> Dict[str, Any]:
    registry = {
        (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        ): item
        for item in summary.get("benchmark_file_registry", [])
    }
    records = []
    files_match = len(registry) == 306
    for source in protocol.get("sources", []):
        identity = (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        )
        path = (
            run_root
            / "benchmarks"
            / identity[0]
            / identity[1]
            / f"seed{identity[2]}"
            / "benchmark.json"
        )
        if not path.is_file() or identity not in registry:
            files_match = False
            continue
        if file_hash(path) != registry[identity].get(
            "benchmark_file_sha256"
        ):
            files_match = False
        records.append(load(path))
    recomputed: Dict[str, Any] = {}
    recomputation_error = None
    try:
        recomputed = aggregate_benchmarks(records, protocol)
    except Exception as exc:  # fail closed with an addressable audit
        recomputation_error = f"{type(exc).__name__}: {exc}"
    summary_fields_match = bool(
        recomputation_error is None
        and all(
            summary.get(key) == recomputed.get(key)
            for key in (
                "benchmark_count",
                "scenario_block_count",
                "failure_count",
                "scenario_blocks",
                "raw_per_capture_ratios",
                "ratio_inference",
                "suite_equal_secondary_summary",
                "resource_reporting",
                "deployability_decision",
                "strict_efficiency_decision",
            )
        )
    )
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version")
            == "strict_v4_krc_selected_system_protocol_v1"
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version")
            == "strict_v4_krc_selected_system_summary_v1"
            and summary.get("manifest_sha256") == canonical_hash(summary)
            and summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "all_306_benchmarks_bound_by_hash": files_match
        and len(records) == 306,
        "statistics_recomputed_without_summary_decision_reuse": (
            recomputation_error is None
        ),
        "recomputed_fields_match_summary": summary_fields_match,
        "unknown_or_test_labels_not_used_for_benchmark_selection": all(
            record.get(
                "unknown_or_test_labels_used_for_benchmark_selection"
            )
            is False
            for record in records
        ),
    }
    integrity = all(checks.values())
    deployability = bool(
        recomputed.get("deployability_decision", {}).get("passes")
    )
    efficiency = bool(
        recomputed.get("strict_efficiency_decision", {}).get("passes")
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_selected_system_audit_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol.get("manifest_sha256"),
        "summary_manifest_sha256": summary.get("manifest_sha256"),
        "checks": checks,
        "recomputed": recomputed,
        "recomputation_error": recomputation_error,
        "passes": integrity,
        "deployability_gate_passes": integrity and deployability,
        "strict_efficiency_superiority_gate_passes": (
            integrity and efficiency
        ),
        "claim_authorization": {
            "tier1_selected_system_deployability": (
                integrity and deployability
            ),
            "tier2_pairwise_efficiency_superiority": (
                integrity and deployability and efficiency
            ),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol.resolve()),
        load(args.summary.resolve()),
        args.run_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
