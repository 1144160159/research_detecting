from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from summarize_strict_v4_mdr_opendetect_efficiency import (
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
        "diagnostic_inference",
        "suite_equal_secondary_summary",
        "resource_reporting",
        "integrity_decision",
        "strict_efficiency_decision",
    )
    records = recomputed.get("_records", [])
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version")
            == "strict_v4_mdr_opendetect_efficiency_protocol_v1"
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version")
            == "strict_v4_mdr_opendetect_efficiency_summary_v1"
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
        "same_inputs_used_within_each_process": all(
            item.get("same_input_evidence", {}).get(
                "candidate_and_comparator_received_same_arrays"
            )
            is True
            and item.get("same_input_evidence", {}).get("labels_loaded")
            is False
            for item in records
        ),
        "unknown_or_test_labels_not_used_for_benchmark_selection": all(
            item.get(
                "unknown_or_test_labels_used_for_benchmark_selection"
            )
            is False
            for item in records
        ),
        "comparator_seed_reuse_not_used_for_effectiveness": all(
            item.get("comparator_seed_reuse_supports_effectiveness_claim")
            is False
            for item in records
        ),
        "full_capture_wall_not_lower_bound_used_for_fit_gate": (
            protocol.get("cost_policy", {}).get(
                "strict_fit_gate_candidate_measure"
            )
            == "full_capture_subprocess_wall_seconds"
            and summary.get("claim_boundary", {}).get(
                "lower_bound_fit_ratio_is_diagnostic_only"
            )
            is True
        ),
    }
    integrity_passes = all(checks.values())
    summary_integrity = bool(
        recomputed.get("integrity_decision", {}).get("passes")
    )
    efficiency = bool(
        recomputed.get("strict_efficiency_decision", {}).get("passes")
    )
    return {
        "checks": checks,
        "passes": integrity_passes and summary_integrity,
        "strict_efficiency_superiority_gate_passes": (
            integrity_passes and summary_integrity and efficiency
        ),
        "claim_tiers": {
            "mdr_efficiency_vs_opendetect_is_reportable": (
                integrity_passes and summary_integrity
            ),
            "mdr_strictly_outperforms_opendetect_on_all_efficiency_axes": (
                integrity_passes and summary_integrity and efficiency
            ),
            "efficiency_does_not_support_accuracy_or_robustness": True,
            "failure_blocks_only_multidimensional_comprehensive_sota": True,
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
        "schema_version": (
            "strict_v4_mdr_opendetect_efficiency_audit_v1"
        ),
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
