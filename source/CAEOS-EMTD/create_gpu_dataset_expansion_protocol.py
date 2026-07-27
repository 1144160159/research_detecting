from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


def central_directory_identity(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        members = [
            {
                "filename": info.filename,
                "crc32": f"{info.CRC:08x}",
                "compressed_size": info.compress_size,
                "uncompressed_size": info.file_size,
            }
            for info in archive.infolist()
            if not info.is_dir()
        ]
    canonical = json.dumps(members, sort_keys=True, separators=(",", ":"))
    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "member_count": len(members),
        "central_directory_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def require_candidate(
    audit: dict[str, Any], name: str, status: str, minimum_families: int
) -> dict[str, Any]:
    candidate = audit["candidates"][name]
    if candidate["admission_status"] != status:
        raise ValueError(f"{name} has unexpected admission status")
    family_key = (
        "malicious_families_from_paths"
        if name == "LSNM2024"
        else "attack_families_from_paths"
    )
    if len(candidate[family_key]) < minimum_families:
        raise ValueError(f"{name} has fewer than {minimum_families} path families")
    return candidate


def build_protocol(audit: dict[str, Any]) -> dict[str, Any]:
    if audit.get("status") != "complete_sampled_read_only_audit":
        raise ValueError("candidate audit is not complete")
    lsnm = require_candidate(
        audit, "LSNM2024", "priority_1_prepare_grouped_open_set", 15
    )
    ddos = require_candidate(
        audit, "CICDDoS2019", "priority_2_ddos_family_external_suite", 16
    )
    archives = [Path(path) for path in lsnm["source_files"] + ddos["source_files"]]
    return {
        "schema_version": "gpu_malicious_dataset_expansion_protocol_v1",
        "status": "frozen_before_full_scan_and_training",
        "claim_boundary": {
            "formal_selection_evidence": False,
            "may_expand_dataset_count_before_admission_gate": False,
            "may_claim_cross_dataset_sota_before_confirmatory_runs": False,
            "cicddos_scope": "narrow_ddos_family_external_generalization_only",
        },
        "source_identity": [central_directory_identity(path) for path in archives],
        "shared_rules": {
            "split_unit": "canonical_bidirectional_five_tuple_or_session",
            "forbidden_split": "random_packet_or_random_flow_row_split",
            "forbidden_model_features": [
                "raw_source_address",
                "raw_destination_address",
                "flow_or_stream_identifier",
                "payload_or_content_string",
                "checksum",
                "source_member_path",
            ],
            "unknown_protocol": "leave_one_attack_family_out",
            "minimum_groups_per_retained_label": 3,
            "required_overlap": {
                "train_validation": 0,
                "train_test": 0,
                "validation_test": 0,
            },
            "external_suite_hyperparameter_tuning": "forbidden",
            "seeds": [223, 227, 229],
        },
        "datasets": {
            "LSNM2024": {
                "source_kind": "packet_table_csv_in_zip",
                "families": lsnm["malicious_families_from_paths"],
                "benign_label": "normal",
                "label_rule": (
                    "benign member maps to normal; malicious member maps to its parent "
                    "family path; any explicit label is retained only as an audit field"
                ),
                "schema_rule": "normalize 59/60/61 columns by canonical column name",
                "session_rule": (
                    "canonicalize source/destination addresses and TCP/UDP ports with IP "
                    "protocol; use capture-local time gaps to split repeated sessions"
                ),
                "representation": "numeric packet/network/transport metadata only",
                "admission_gate": [
                    "all rows receive exactly one benign or malicious-family label",
                    "at least three nonoverlapping session groups per retained label",
                    "no forbidden model feature survives normalization",
                    "duplicate fingerprints do not cross train/validation/test",
                ],
            },
            "CICDDoS2019": {
                "source_kind": "flow_csv_in_zip",
                "families": ddos["attack_families_from_paths"],
                "label_rule": "strip Label whitespace and reconcile it with member stem",
                "schema_rule": "strip header whitespace and map common CICFlowMeter names",
                "group_rule": "canonical bidirectional five tuple; fallback fingerprint group",
                "representation": "CICFlowMeter numeric flow features shared with strict-v4",
                "admission_gate": [
                    "full-scan labels are reconciled with the 16 path families",
                    "benign availability and counts are reported explicitly",
                    "at least three nonoverlapping groups per retained label",
                    "raw addresses and identifiers are excluded from model features",
                ],
            },
        },
        "algorithm_evaluation": {
            "incumbent": "CAEOS-Pairwise",
            "challengers": [
                "mal_tls_geometry_preserving_adapter",
                "mal_tls_counterfactual_conflict_gate",
            ],
            "challenger_eligibility": "pilot_and_reserved_seed_confirmation_must_pass",
            "selection_order": [
                "worst_four_metric_bootstrap_lower_bound",
                "mean_four_metric_gain",
                "known_f1_noninferiority",
            ],
            "baseline_scope": (
                "reuse the frozen strict-v4 baseline panel and add only baselines whose "
                "independent implementation audits have passed"
            ),
        },
        "execution_order": [
            "wait_for_current_efficiency_and_claim_chain",
            "full_scan_schema_label_and_group_audit",
            "freeze_normalized_dataset_manifest_and_hashes",
            "run_baselines_and_incumbent",
            "run_only_eligible_self_algorithm_challengers",
            "bootstrap_gate_and_update_claim_tier",
        ],
    }


def render(protocol: dict[str, Any]) -> str:
    lines = [
        "# GPU malicious-dataset expansion admission protocol",
        "",
        f"- Status: `{protocol['status']}`",
        "- Evidence boundary: no new dataset count or SOTA claim before admission and confirmation gates",
        "- Self algorithm: retained as a gated challenger track, not removed",
        "",
        "## Dataset roles",
        "",
        "- LSNM2024: broad 15-family packet/session external open-set suite",
        "- CICDDoS2019: narrow 16-family DDoS external generalization suite",
        "",
        "## Required order",
        "",
    ]
    lines.extend(
        f"{index}. `{step}`"
        for index, step in enumerate(protocol["execution_order"], 1)
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    protocol = build_protocol(audit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "protocol.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "protocol.md").write_text(render(protocol), encoding="utf-8")
    (args.output_dir / "protocol_frozen").touch()
    print(render(protocol), end="")


if __name__ == "__main__":
    main()
