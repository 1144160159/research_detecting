from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from audit_caeos_label_alignment_coverage import audit as coverage_audit
from build_caeos_edge_iiotset_label_index import build as build_pair_index
from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file
from inventory_caeos_edge_iiotset_pcaps import inventory
from validate_caeos_label_index import validate as validate_index


DATASET_ID = "edge_iiotset"
APPROVED_EXCLUSIONS = {
    "five_tuple_absent_from_official_flow_labels",
    "five_tuple_present_but_time_not_overlapping",
    "protocol_outside_official_tcp_udp_flow_labels",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--idle-seconds", type=float, default=30.0)
    parser.add_argument("--maximum-packets", type=int, default=9_223_372_036_854_775_807)
    parser.add_argument("--maximum-unmatched-samples", type=int, default=100)
    parser.add_argument("--stop-after", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--verify-source-sha-on-resume", action="store_true")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pair_paths(run_root: Path, pair: dict[str, Any]) -> dict[str, Path]:
    pair_id = pair["pair_id"]
    return {
        "index": run_root / "label_indices" / f"{pair_id}.sqlite",
        "index_audit": run_root / "audits" / f"{pair_id}.index.json",
        "validation": run_root / "audits" / f"{pair_id}.validation.json",
        "coverage": run_root / "audits" / f"{pair_id}.coverage.json",
        "summary": run_root / "pairs" / f"{pair_id}.summary.json",
    }


def reusable_pair(
    pair: dict[str, Any],
    paths: dict[str, Path],
    verify_sources: bool,
) -> dict[str, Any] | None:
    if not all(path.exists() for path in paths.values()):
        return None
    summary = read_json(paths["summary"])
    index_audit = read_json(paths["index_audit"])
    if not summary.get("pair_gate_passed"):
        return None
    expected_index_sha = str(index_audit.get("label_index", {}).get("sha256", ""))
    if not expected_index_sha or sha256_file(paths["index"]) != expected_index_sha:
        return None
    registry = index_audit.get("registry", {})
    if registry.get("source_member") != pair["source_member"]:
        return None
    if verify_sources:
        if sha256_file(Path(pair["pcap"])) != registry.get("pcap_sha256"):
            return None
        if sha256_file(Path(pair["packet_csv"])) != registry.get("packet_csv_sha256"):
            return None
    summary["reused"] = True
    return summary


def reusable_index_artifacts(
    pair: dict[str, Any],
    paths: dict[str, Path],
    idle_seconds: float,
    verify_sources: bool,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    required = (paths["index"], paths["index_audit"], paths["validation"])
    if not all(path.exists() for path in required):
        return None
    index_report = read_json(paths["index_audit"])
    validation = read_json(paths["validation"])
    expected_sha = str(index_report.get("label_index", {}).get("sha256", ""))
    registry = index_report.get("registry", {})
    if (
        not index_report.get("pairing_passed")
        or not validation.get("passed")
        or not expected_sha
        or validation.get("sha256") != expected_sha
        or registry.get("source_member") != pair["source_member"]
        or float(registry.get("idle_seconds", -1)) != float(idle_seconds)
        or sha256_file(paths["index"]) != expected_sha
    ):
        return None
    if verify_sources:
        if sha256_file(Path(pair["pcap"])) != registry.get("pcap_sha256"):
            return None
        if sha256_file(Path(pair["packet_csv"])) != registry.get("packet_csv_sha256"):
            return None
    return index_report, validation


def evaluate_pair(
    pair: dict[str, Any],
    paths: dict[str, Path],
    idle_seconds: float,
    maximum_packets: int,
    maximum_unmatched_samples: int,
    reuse_index: bool,
    verify_sources: bool,
) -> dict[str, Any]:
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    reusable = (
        reusable_index_artifacts(
            pair, paths, idle_seconds, verify_sources
        )
        if reuse_index
        else None
    )
    paths["coverage"].unlink(missing_ok=True)
    paths["summary"].unlink(missing_ok=True)
    index_reused = reusable is not None
    if reusable is None:
        for name in ("index", "index_audit", "validation"):
            paths[name].unlink(missing_ok=True)
        index_report = build_pair_index(
            argparse.Namespace(
                pcap=Path(pair["pcap"]),
                packet_csv=Path(pair["packet_csv"]),
                source_member=pair["source_member"],
                label_index=paths["index"],
                audit_output=paths["index_audit"],
                idle_seconds=idle_seconds,
            )
        )
        validation = validate_index(
            argparse.Namespace(
                path=paths["index"],
                dataset_id=DATASET_ID,
                output=paths["validation"],
                group_counts=True,
            )
        )
    else:
        index_report, validation = reusable
    coverage = coverage_audit(
        argparse.Namespace(
            dataset_id=DATASET_ID,
            pcap=Path(pair["pcap"]),
            source_member=pair["source_member"],
            label_index=paths["index"],
            label_index_sha256=index_report["label_index"]["sha256"],
            output=paths["coverage"],
            maximum_packets=maximum_packets,
            idle_seconds=idle_seconds,
            tolerance_ns=0,
            maximum_unmatched_samples=maximum_unmatched_samples,
            conflict_policy="reject",
            drop_unmatched_reason=sorted(APPROVED_EXCLUSIONS),
            time_nonoverlap_policy="reject",
        )
    )
    counters = coverage["counters"]
    flows = int(counters.get("flows", 0))
    matched = int(coverage["matched_flows"])
    excluded = int(coverage["label_exclusion_summary"]["excluded_flows"])
    reasons = set(coverage["label_exclusion_summary"]["reason_counts"])
    conflicts = sum(
        int(value)
        for key, value in counters.items()
        if key.startswith("status::conflicting") and key.count("::") == 1
    )
    retained = flows - excluded
    effective_coverage = matched / retained if retained else float(matched == 0)
    pair_gate = (
        bool(index_report["pairing_passed"])
        and bool(validation["passed"])
        and bool(coverage["complete_pcap_read"])
        and conflicts == 0
        and reasons <= APPROVED_EXCLUSIONS
        and matched + excluded == flows
        and effective_coverage == 1.0
    )
    summary = {
        "schema_version": "caeos_edge_iiotset_per_pcap_strict_audit_v1",
        "dataset_id": DATASET_ID,
        "pair": pair,
        "index": str(paths["index"]),
        "index_sha256": index_report["label_index"]["sha256"],
        "index_record_count": index_report["label_index"]["record_count"],
        "index_audit": str(paths["index_audit"]),
        "validation_audit": str(paths["validation"]),
        "coverage_audit": str(paths["coverage"]),
        "complete_pcap_read": coverage["complete_pcap_read"],
        "flows": flows,
        "matched_flows": matched,
        "excluded_flows": excluded,
        "excluded_reason_counts": coverage["label_exclusion_summary"]["reason_counts"],
        "conflicting_flows": conflicts,
        "raw_coverage_fraction": coverage["coverage_fraction"],
        "effective_retained_flow_coverage": effective_coverage,
        "zero_retained_supported_ip_flows": retained == 0,
        "pair_gate_passed": pair_gate,
        "index_reused": index_reused,
        "reused": False,
    }
    atomic_json(paths["summary"], summary)
    if not pair_gate:
        raise ValueError(f"strict Edge-IIoTset pair gate failed: {pair['source_member']}")
    return summary


def records_from_indices(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        connection = sqlite3.connect(
            f"file:{path.resolve().as_posix()}?mode=ro&immutable=1", uri=True
        )
        try:
            rows = connection.execute(
                """
                SELECT record_id, source_member, endpoint_a, port_a,
                       endpoint_b, port_b, protocol, start_ns, end_ns,
                       fine_label, family_label, binary_label, label_source
                FROM labels ORDER BY record_id
                """
            )
            for row in rows:
                yield {
                    "record_id": row[0],
                    "source_member": row[1],
                    "src_ip": row[2],
                    "src_port": row[3],
                    "dst_ip": row[4],
                    "dst_port": row[5],
                    "protocol": row[6],
                    "start_ns": row[7],
                    "end_ns": row[8],
                    "fine_label": row[9],
                    "family_label": row[10],
                    "binary_label": row[11],
                    "label_source": row[12],
                }
        finally:
            connection.close()


def aggregate_summary(
    run_root: Path,
    inventory_report: dict[str, Any],
    pair_summaries: list[dict[str, Any]],
    complete_requested_scope: bool,
) -> dict[str, Any]:
    summary_path = run_root / "summary.json"
    all_pairs_passed = (
        complete_requested_scope
        and inventory_report["passed"]
        and len(pair_summaries) == inventory_report["pair_count"]
        and all(item["pair_gate_passed"] for item in pair_summaries)
    )
    full_index_report: dict[str, Any] | None = None
    full_validation: dict[str, Any] | None = None
    if all_pairs_passed:
        registry = {
            "inventory_sha256": inventory_report["inventory_sha256"],
            "pair_index_sha256": {
                item["pair"]["pair_id"]: item["index_sha256"]
                for item in pair_summaries
            },
        }
        registry_sha256 = hashlib.sha256(
            json.dumps(registry, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        full_index = run_root / "label_indices" / "edge_iiotset_full.sqlite"
        full_index.unlink(missing_ok=True)
        full_index_report = create_label_index(
            full_index,
            DATASET_ID,
            records_from_indices(Path(item["index"]) for item in pair_summaries),
            registry_sha256,
        )
        full_validation = validate_index(
            argparse.Namespace(
                path=full_index,
                dataset_id=DATASET_ID,
                output=run_root / "audits" / "edge_iiotset_full.validation.json",
                group_counts=True,
            )
        )
        all_pairs_passed = all_pairs_passed and bool(full_validation["passed"])

    result = {
        "schema_version": "caeos_edge_iiotset_all_pcap_strict_audit_v1",
        "dataset_id": DATASET_ID,
        "inventory": str(run_root / "inventory.json"),
        "inventory_sha256": inventory_report["inventory_sha256"],
        "inventory_pair_count": inventory_report["pair_count"],
        "completed_pair_count": len(pair_summaries),
        "complete_pcap_count": sum(
            bool(item.get("complete_pcap_read")) for item in pair_summaries
        ),
        "total_flows": sum(int(item.get("flows", 0)) for item in pair_summaries),
        "matched_flows": sum(
            int(item.get("matched_flows", 0)) for item in pair_summaries
        ),
        "excluded_flows": sum(
            int(item.get("excluded_flows", 0)) for item in pair_summaries
        ),
        "conflicting_flows": sum(
            int(item.get("conflicting_flows", 0)) for item in pair_summaries
        ),
        "pair_summaries": pair_summaries,
        "full_label_index": full_index_report,
        "full_label_index_validation": full_validation,
        "formal_label_gate_passed": all_pairs_passed,
        "formal_label_gate_reason": (
            "all inventoried PCAPs completed strict paired-packet label alignment"
            if all_pairs_passed
            else "partial run or at least one PCAP/inventory/aggregate gate is incomplete"
        ),
        "feature_extraction_started": False,
    }
    atomic_json(summary_path, result)
    return result


def run(args: argparse.Namespace) -> dict[str, Any]:
    args.run_root.mkdir(parents=True, exist_ok=True)
    inventory_report = inventory(args.data_root)
    atomic_json(args.run_root / "inventory.json", inventory_report)
    if not inventory_report["passed"]:
        raise ValueError("Edge-IIoTset PCAP/packet-CSV inventory gate failed")
    pair_summaries: list[dict[str, Any]] = []
    selected_pairs = inventory_report["pairs"]
    if args.stop_after:
        selected_pairs = selected_pairs[: args.stop_after]
    for pair in selected_pairs:
        paths = pair_paths(args.run_root, pair)
        summary = (
            reusable_pair(pair, paths, args.verify_source_sha_on_resume)
            if args.resume
            else None
        )
        if summary is None:
            try:
                summary = evaluate_pair(
                    pair,
                    paths,
                    args.idle_seconds,
                    args.maximum_packets,
                    args.maximum_unmatched_samples,
                    args.resume,
                    args.verify_source_sha_on_resume,
                )
            except BaseException as error:
                existing = (
                    read_json(paths["summary"])
                    if paths["summary"].exists()
                    else {}
                )
                summary = {
                    **existing,
                    "schema_version": "caeos_edge_iiotset_per_pcap_strict_audit_v1",
                    "dataset_id": DATASET_ID,
                    "pair": pair,
                    "complete_pcap_read": bool(
                        existing.get("complete_pcap_read", False)
                    ),
                    "pair_gate_passed": False,
                    "failure_type": type(error).__name__,
                    "failure": str(error),
                    "reused": False,
                }
                atomic_json(paths["summary"], summary)
                pair_summaries.append(summary)
                aggregate_summary(
                    args.run_root, inventory_report, pair_summaries, False
                )
                raise
        pair_summaries.append(summary)
        aggregate_summary(args.run_root, inventory_report, pair_summaries, False)
    return aggregate_summary(
        args.run_root,
        inventory_report,
        pair_summaries,
        len(selected_pairs) == inventory_report["pair_count"],
    )


def main() -> None:
    print(json.dumps(run(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
