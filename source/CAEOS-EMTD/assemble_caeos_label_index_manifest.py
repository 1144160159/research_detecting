from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json, canonical_json_hash, sha256_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--exclusion-policy", type=Path)
    parser.add_argument("--index-audit", action="append", default=[], type=Path)
    parser.add_argument("--coverage-audit", action="append", default=[], type=Path)
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalized_dataset_id(value: Any) -> str:
    return str(value).strip().lower()


def effective_coverage(coverage: dict[str, Any]) -> float:
    if "effective_coverage_fraction" in coverage:
        return float(coverage["effective_coverage_fraction"])
    if "retained_flow_label_coverage_fraction" in coverage:
        return float(coverage["retained_flow_label_coverage_fraction"])
    exclusion = coverage.get("label_exclusion_summary") or {}
    total = int(exclusion.get("total_finalized_flows", 0))
    excluded = int(exclusion.get("excluded_flows", 0))
    retained = total - excluded
    if retained > 0 and "matched_flows" in coverage:
        return int(coverage["matched_flows"]) / retained
    total = int(coverage.get("total_flows", 0))
    excluded = int(coverage.get("excluded_flows", 0))
    retained = total - excluded
    if retained > 0 and "matched_flows" in coverage:
        return int(coverage["matched_flows"]) / retained
    if "coverage_fraction" in coverage:
        return float(coverage["coverage_fraction"])
    accepted = coverage.get("accepted_source_count")
    expected = coverage.get("expected_source_count")
    if accepted is not None and expected:
        return int(accepted) / int(expected)
    raise ValueError("coverage audit has no supported coverage fraction")


def raw_coverage(coverage: dict[str, Any]) -> float:
    if "raw_coverage_fraction" in coverage:
        return float(coverage["raw_coverage_fraction"])
    if "coverage_fraction" in coverage:
        return float(coverage["coverage_fraction"])
    if coverage.get("total_flows") and "matched_flows" in coverage:
        return int(coverage["matched_flows"]) / int(coverage["total_flows"])
    return effective_coverage(coverage)


def admission_gate(coverage: dict[str, Any]) -> tuple[str, bool, bool, str | None]:
    if coverage.get("authority_granularity") == "documented_single_class_capture":
        passed = bool(coverage.get("formal_label_gate_passed", False))
        if passed and not coverage.get("all_sources_complete", False):
            raise ValueError(
                "documented single-class capture admission requires all sources complete"
            )
        return (
            "full_capture_member_inventory",
            passed,
            False,
            coverage.get("formal_label_gate_reason"),
        )
    if "formal_dataset_gate_passed" in coverage:
        passed = bool(coverage["formal_dataset_gate_passed"])
        return (
            "full_capture_member_inventory",
            passed,
            False,
            coverage.get("formal_gate_reason"),
        )
    # A strict flow-label pass is stronger than a source-quality-adjusted pass.
    # Some audits emit both fields; prefer the strict gate so an unused quality
    # exception policy cannot weaken or block the admission decision.
    if coverage.get("formal_label_gate_passed") is True:
        return (
            "strict_flow_label",
            True,
            True,
            coverage.get("formal_label_gate_reason")
            or coverage.get("formal_gate_reason"),
        )
    if "source_quality_adjusted_gate_passed" in coverage:
        passed = bool(coverage["source_quality_adjusted_gate_passed"])
        policy_hash = coverage.get("source_quality_policy_sha256")
        if passed and (
            not coverage.get("all_sources_usable_or_quarantined") or not policy_hash
        ):
            raise ValueError(
                "source-quality-adjusted admission requires a complete/quarantined "
                "inventory and an immutable policy hash"
            )
        return (
            "source_quality_adjusted_flow_label",
            passed,
            bool(coverage.get("formal_label_gate_passed", False)),
            coverage.get("source_quality_adjusted_gate_reason"),
        )
    if "formal_label_gate_passed" in coverage:
        passed = bool(coverage["formal_label_gate_passed"])
        return (
            "strict_flow_label",
            passed,
            passed,
            coverage.get("formal_label_gate_reason")
            or coverage.get("formal_gate_reason"),
        )
    passed = bool(coverage["formal_gate_passed"])
    return (
        "strict_flow_label",
        passed,
        passed,
        coverage.get("formal_gate_reason"),
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    registry = load(args.registry)
    registry_sha256 = sha256_file(args.registry)
    exclusion_policy = load(args.exclusion_policy) if args.exclusion_policy else None
    index_audits = {
        normalized_dataset_id(load(path)["dataset_id"]): (path, load(path))
        for path in args.index_audit
    }
    coverage_audits: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path in args.coverage_audit:
        audit = load(path)
        coverage_audits.setdefault(
            normalized_dataset_id(audit["dataset_id"]), []
        ).append((path, audit))
    datasets: list[dict[str, Any]] = []
    for dataset_id, registration in registry["datasets"].items():
        item: dict[str, Any] = {
            "id": dataset_id,
            "registration_status": registration["status"],
            "status": "blocked_no_label_index",
        }
        if exclusion_policy is not None:
            dataset_exclusion = exclusion_policy.get("datasets", {}).get(dataset_id)
            if dataset_exclusion is not None:
                item.update(
                    {
                        "conflict_policy": dataset_exclusion.get(
                            "conflict_policy", "reject"
                        ),
                        "time_nonoverlap_policy": dataset_exclusion.get(
                            "time_nonoverlap_policy", "reject"
                        ),
                        "tolerance_ns": int(
                            dataset_exclusion.get("resolver_tolerance_ns", 0)
                        ),
                        "external_label_precedence": bool(
                            dataset_exclusion.get(
                                "external_label_precedence", False
                            )
                        ),
                        "maximum_excluded_packet_fraction": float(
                            dataset_exclusion.get(
                                "maximum_excluded_packet_fraction", 1.0
                            )
                        ),
                        "official_boundary_split": bool(
                            dataset_exclusion.get(
                                "official_boundary_split", False
                            )
                        ),
                        "drop_unmatched_reasons": sorted(
                            dataset_exclusion.get("drop_unmatched_reasons", [])
                        ),
                        "label_exclusion_rule_version": dataset_exclusion[
                            "rule_version"
                        ],
                    }
                )
        index_entry = index_audits.get(dataset_id)
        if index_entry is not None:
            index_path, audit = index_entry
            index = audit["label_index"]
            item.update(
                {
                    "path": index["path"],
                    "sha256": index["sha256"],
                    "record_count": int(index["record_count"]),
                    "tolerance_ns": int(
                        item.get(
                            "tolerance_ns", audit.get("resolver_tolerance_ns", 0)
                        )
                    ),
                    "index_audit_path": str(index_path),
                    "index_audit_sha256": sha256_file(index_path),
                    "status": "index_ready_coverage_pending",
                }
            )
        coverage_entries = coverage_audits.get(dataset_id, [])
        if coverage_entries:
            evidence = []
            for path, coverage in coverage_entries:
                try:
                    gate_type, admitted, strict_formal, gate_reason = admission_gate(
                        coverage
                    )
                except ValueError as exc:
                    raise ValueError(
                        f"{dataset_id}: invalid coverage evidence {path}: {exc}"
                    ) from exc
                evidence.append({
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "scope": coverage.get("scope", "full_frozen_capture_inventory"),
                    "raw_coverage_fraction": raw_coverage(coverage),
                    "effective_coverage_fraction": effective_coverage(coverage),
                    "gate_type": gate_type,
                    "admission_gate_passed": admitted,
                    "formal_gate_passed": strict_formal,
                    "gate_reason": gate_reason,
                    "authority_granularity": coverage.get("authority_granularity"),
                    "source_quality_policy_sha256": coverage.get(
                        "source_quality_policy_sha256"
                    ),
                })
            all_admitted = all(item["admission_gate_passed"] for item in evidence)
            all_formal = all(item["formal_gate_passed"] for item in evidence)
            all_effective = all(
                item["effective_coverage_fraction"] >= 1.0 - 1e-12
                for item in evidence
            )
            item.update(
                {
                    "coverage_evidence": evidence,
                    "coverage_fraction": min(
                        entry["raw_coverage_fraction"] for entry in evidence
                    ),
                    "effective_coverage_fraction": min(
                        entry["effective_coverage_fraction"] for entry in evidence
                    ),
                    "formal_gate_passed": all_formal,
                    "admission_gate_passed": all_admitted,
                    "admission_gate_types": sorted(
                        {entry["gate_type"] for entry in evidence}
                    ),
                }
            )
            if item["admission_gate_passed"] and all_effective:
                if "path" not in item:
                    raise ValueError(f"coverage audit without label index: {dataset_id}")
                item["status"] = "ready"
            elif all_effective:
                item["status"] = "index_ready_sampled_coverage_only"
            else:
                item["status"] = "blocked_formal_coverage_failed"
        datasets.append(item)
    manifest = {
        "schema_version": "caeos_label_index_manifest_v1",
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "exclusion_policy_path": (
            str(args.exclusion_policy) if args.exclusion_policy else None
        ),
        "exclusion_policy_sha256": (
            sha256_file(args.exclusion_policy) if args.exclusion_policy else None
        ),
        "datasets": datasets,
        "ready_dataset_count": sum(item["status"] == "ready" for item in datasets),
        "dataset_count": len(datasets),
    }
    manifest["manifest_sha256"] = canonical_json_hash(manifest)
    atomic_json(args.output, manifest)
    return manifest


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
