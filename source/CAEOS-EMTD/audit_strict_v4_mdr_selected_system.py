from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from summarize_strict_v4_mdr_selected_system import (
    aggregate_benchmarks,
    load,
)


def evaluate_audit(
    *,
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    recomputed: Dict[str, Any],
    implementation_hashes_match: bool,
    benchmark_hashes_match: bool,
) -> Dict[str, Any]:
    aggregate_keys = (
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
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version")
            == "strict_v4_mdr_selected_system_protocol_v1"
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version")
            == "strict_v4_mdr_selected_system_summary_v1"
            and summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "summary_binds_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "all_306_benchmarks_bound_by_hash": benchmark_hashes_match,
        "implementation_hashes_match": implementation_hashes_match,
        "independent_recomputation_exact": all(
            summary.get(key) == recomputed.get(key) for key in aggregate_keys
        ),
        "unknown_or_test_labels_not_used_for_benchmark_selection": all(
            item.get(
                "unknown_or_test_labels_used_for_benchmark_selection"
            )
            is False
            for item in recomputed.get("_records", [])
        ),
    }
    integrity_passes = all(checks.values())
    deployability = bool(
        recomputed.get("deployability_decision", {}).get("passes")
    )
    efficiency = bool(
        recomputed.get("strict_efficiency_decision", {}).get("passes")
    )
    return {
        "checks": checks,
        "passes": integrity_passes,
        "deployability_gate_passes": integrity_passes and deployability,
        "strict_efficiency_superiority_gate_passes": (
            integrity_passes and efficiency
        ),
        "claim_tiers": {
            "selected_mdr_is_deployment_equivalent_and_reportable": (
                integrity_passes and deployability
            ),
            "multidimensional_comprehensive_sota_supported": (
                integrity_passes and deployability and efficiency
            ),
            "deployability_alone_does_not_imply_efficiency_sota": True,
        },
    }


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    project_root: Path,
    run_root: Path,
) -> Dict[str, Any]:
    records = []
    benchmark_hashes_match = True
    registry = {
        (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        ): item
        for item in summary.get("benchmark_file_registry", [])
    }
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
        if (
            not path.is_file()
            or identity not in registry
            or file_hash(path)
            != registry[identity].get("benchmark_file_sha256")
        ):
            benchmark_hashes_match = False
            continue
        records.append(load(path))
    implementation_hashes_match = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    try:
        recomputed = aggregate_benchmarks(records, protocol)
    except (KeyError, TypeError, ValueError):
        recomputed = {}
    recomputed["_records"] = records
    evaluated = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=implementation_hashes_match,
        benchmark_hashes_match=(
            benchmark_hashes_match
            and len(records) == 306
            and len(registry) == 306
        ),
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_selected_system_audit_v1",
        "protocol_manifest_sha256": protocol.get("manifest_sha256"),
        "summary_manifest_sha256": summary.get("manifest_sha256"),
        **evaluated,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol),
        load(args.summary),
        args.project_root,
        args.run_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
