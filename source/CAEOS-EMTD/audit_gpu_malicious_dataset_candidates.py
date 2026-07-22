from __future__ import annotations

import argparse
import csv
import io
import json
import os
import zipfile
from pathlib import Path
from typing import Any, Iterable


def sample_csv_rows(lines: Iterable[str], limit: int = 24) -> dict[str, Any]:
    reader = csv.reader(lines)
    header = next(reader, [])
    rows = []
    for row in reader:
        if row:
            rows.append(row)
        if len(rows) >= limit:
            break
    lowered = [column.strip().lower() for column in header]
    label_indices = [
        index
        for index, name in enumerate(lowered)
        if any(token in name for token in ("label", "attack", "category", "class"))
    ]
    label_samples = {
        header[index]: sorted(
            {
                row[index].strip()
                for row in rows
                if index < len(row) and row[index].strip()
            }
        )[:20]
        for index in label_indices
    }
    tail_samples = []
    for row in rows[:5]:
        tail_samples.append(row[-min(6, len(row)) :])
    return {
        "column_count": len(header),
        "columns": header,
        "sampled_rows": len(rows),
        "candidate_label_columns": [header[index] for index in label_indices],
        "candidate_label_samples": label_samples,
        "sample_row_tail": tail_samples,
    }


def sample_plain(path: Path, limit: int = 24) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        sample = sample_csv_rows(handle, limit)
    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        **sample,
    }


def sample_zip_members(
    path: Path, *, member_filter: str = ".csv", limit: int = 8
) -> list[dict[str, Any]]:
    records = []
    with zipfile.ZipFile(path) as archive:
        members = sorted(
            (
                info
                for info in archive.infolist()
                if not info.is_dir() and info.filename.lower().endswith(member_filter)
            ),
            key=lambda info: info.filename,
        )
        for info in members:
            with archive.open(info) as raw:
                text = io.TextIOWrapper(
                    raw, encoding="utf-8-sig", errors="replace", newline=""
                )
                sample = sample_csv_rows(text, limit)
            records.append(
                {
                    "member": info.filename,
                    "uncompressed_size_bytes": info.file_size,
                    **sample,
                }
            )
    return records


def existing(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def build_audit(base: Path) -> dict[str, Any]:
    lsnm_zip = existing(base / "LSNM2024" / "LSNM2024_Dataset.zip")
    ddos_zips = [
        existing(base / "cic" / "CICDDoS2019" / "CSVs" / name)
        for name in ("CSV-01-12.zip", "CSV-03-11.zip")
    ]
    bot_iot = existing(
        base
        / "cic"
        / "CIC-BoT-IoT"
        / "a27809afa6caa7e0_MOHANAD_A4706"
        / "data"
        / "CIC-BoT-IoT.csv"
    )
    apt_files = [
        existing(base / "cic" / "CICAPT-IIoT2024" / name)
        for name in ("phase1_NetworkData.csv", "phase2_NetworkData.csv")
    ]
    darknet = existing(base / "cic" / "CICDarknet2020" / "Darknet.CSV")

    lsnm_members = sample_zip_members(lsnm_zip)
    ddos_members = [
        record
        for archive in ddos_zips
        for record in sample_zip_members(archive)
    ]
    lsnm_families = sorted(
        {
            Path(record["member"]).parent.name
            for record in lsnm_members
            if "/Malicious/" in record["member"]
        }
    )
    ddos_families = sorted(
        {Path(record["member"]).stem for record in ddos_members}
    )
    candidates = {
        "LSNM2024": {
            "source_kind": "packet_table_csv_in_zip",
            "source_files": [str(lsnm_zip)],
            "archive_csv_members": len(lsnm_members),
            "malicious_family_count_from_paths": len(lsnm_families),
            "malicious_families_from_paths": lsnm_families,
            "has_benign_member": any("/Benign/" in item["member"] for item in lsnm_members),
            "samples": lsnm_members,
            "admission_status": "priority_1_prepare_grouped_open_set",
            "reason": (
                "new 2024 source with benign traffic and diverse attack families; "
                "mixed schemas and one-file families require normalized bidirectional "
                "flow/session groups before admission"
            ),
            "admission_constraints": [
                "derive missing attack labels from the malicious family path",
                "normalize the 59/60/61-column packet schemas",
                "split by canonical bidirectional flow/session groups, not source file alone",
                "exclude raw addresses, payload/content strings, checksums, and capture IDs",
            ],
        },
        "CICDDoS2019": {
            "source_kind": "flow_csv_in_zip",
            "source_files": [str(path) for path in ddos_zips],
            "archive_csv_members": len(ddos_members),
            "attack_family_count_from_paths": len(ddos_families),
            "attack_families_from_paths": ddos_families,
            "samples": ddos_members,
            "admission_status": "priority_2_ddos_family_external_suite",
            "reason": (
                "large family-granular DDoS source, useful for narrow attack-family "
                "generalization but not a substitute for broad malware coverage"
            ),
            "admission_constraints": [
                "strip CICFlowMeter header whitespace and verify every label by full scan",
                "split by canonical bidirectional five-tuple or fingerprint groups",
                "exclude raw addresses and flow identifiers from model features",
                "report as a narrow DDoS-family external suite",
            ],
        },
        "CIC-BoT-IoT": {
            "source_kind": "flow_csv",
            "source_files": [str(bot_iot)],
            "samples": [sample_plain(bot_iot)],
            "admission_status": "schema_and_label_mapping_required",
            "reason": "large botnet/IoT table; admit only after exact label and group audit",
        },
        "CICAPT-IIoT2024": {
            "source_kind": "flow_csv_two_phase",
            "source_files": [str(path) for path in apt_files],
            "samples": [sample_plain(path) for path in apt_files],
            "admission_status": "priority_3_phase_grouped_apt_external_suite",
            "reason": (
                "highly relevant APT-IIoT network source; phase must be retained as a "
                "group and labels must be audited before training"
            ),
        },
        "CICDarknet2020": {
            "source_kind": "flow_csv",
            "source_files": [str(darknet)],
            "samples": [sample_plain(darknet)],
            "admission_status": "excluded_not_malicious_attack_ground_truth",
            "reason": (
                "Tor/VPN traffic and application categories are privacy/traffic classes, "
                "not malicious attack-family labels"
            ),
        },
    }
    return {
        "schema_version": "gpu_malicious_dataset_candidate_audit_v1",
        "status": "complete_sampled_read_only_audit",
        "dataset_root": str(base),
        "formal_selection_evidence": False,
        "full_file_scans_performed": False,
        "sample_policy": "header_plus_at_most_24_rows_per_plain_file_and_8_rows_per_zip_member",
        "current_strict_v4_dataset_count": 7,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "recommended_next_actions": [
            "prepare LSNM2024 with normalized session groups and attack-family leave-one-out scenarios",
            "audit CICDDoS2019 benign rows and freeze a DDoS-family external suite",
            "resolve exact label/group fields for CICAPT-IIoT2024 and CIC-BoT-IoT",
            "do not count CICDarknet2020 as malicious attack coverage",
        ],
    }


def render(audit: dict[str, Any]) -> str:
    lines = [
        "# GPU malicious-traffic dataset candidate audit",
        "",
        f"- Current strict-v4 suites: {audit['current_strict_v4_dataset_count']}",
        f"- Candidates inspected: {audit['candidate_count']}",
        "- Scope: sampled read-only schema audit; no full file scans or training",
        "",
        "| Dataset | Status | Evidence boundary |",
        "|---|---|---|",
    ]
    for name, record in audit["candidates"].items():
        lines.append(
            f"| {name} | `{record['admission_status']}` | {record['reason']} |"
        )
    lines.extend(["", "## Next actions", ""])
    lines.extend(f"{index}. {action}" for index, action in enumerate(audit["recommended_next_actions"], 1))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    audit = build_audit(args.dataset_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "audit.md").write_text(render(audit), encoding="utf-8")
    (args.output_dir / "audit_complete").touch()
    print(render(audit), end="")


if __name__ == "__main__":
    main()
