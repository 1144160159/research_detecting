from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tarfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


PCAP_SUFFIXES = {".pcap", ".pcapng", ".cap"}
UNSW_COLUMNS = (
    "srcip", "sport", "dstip", "dsport", "proto", "state", "dur",
    "sbytes", "dbytes", "sttl", "dttl", "sloss", "dloss", "service",
    "sload", "dload", "spkts", "dpkts", "swin", "dwin", "stcpb",
    "dtcpb", "smeansz", "dmeansz", "trans_depth", "res_bdy_len",
    "sjit", "djit", "stime", "ltime", "sintpkt", "dintpkt", "tcprtt",
    "synack", "ackdat", "is_sm_ips_ports", "ct_state_ttl",
    "ct_flw_http_mthd", "is_ftp_login", "ct_ftp_cmd", "ct_srv_src",
    "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm", "ct_src_dport_ltm",
    "ct_dst_sport_ltm", "ct_dst_src_ltm", "attack_cat", "label",
)

FIVE_GAD_FAMILY = {
    "AMFLookingForUDM": "Reconnaissance",
    "GetAllNFs": "Reconnaissance",
    "GetUserData": "Reconnaissance",
    "randomDataDump": "Reconnaissance",
    "automatedRedirectWithTimer": "Reconnaissance",
    "FakeAMFInsert": "NetworkReconfiguration",
    "randomAMFInsert": "NetworkReconfiguration",
    "CrashNRF": "DoS",
    "FakeAMFDelete": "DoS",
    "automatedDropWithTimer": "DoS",
}

CICIDS_FAMILY = {
    "Benign": "Benign",
    "FTP-BruteForce": "BruteForce",
    "SSH-Bruteforce": "BruteForce",
    "DoS attacks-GoldenEye": "DoS",
    "DoS attacks-Slowloris": "DoS",
    "DoS attacks-SlowHTTPTest": "DoS",
    "DoS attacks-Hulk": "DoS",
    "DDoS attacks-LOIC-HTTP": "DDoS",
    "DDOS attack-LOIC-UDP": "DDoS",
    "DDOS attack-HOIC": "DDoS",
    "Brute Force -Web": "WebAttack",
    "Brute Force -XSS": "WebAttack",
    "SQL Injection": "WebAttack",
    "Infilteration": "Infiltration",
    "Bot": "Botnet",
}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def stat_record(path: Path, root: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def pcap_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in PCAP_SUFFIXES
    )


def five_gad(root: Path) -> dict[str, Any]:
    repository = root / "repository"
    normal = sorted((repository / "Normal-2UE").glob("*.pcapng"))
    attack = sorted((repository / "Attacks").glob("*/Attacks_*.pcapng"))
    other_attack_pcaps = [
        path
        for path in pcap_files(repository / "Attacks")
        if path not in set(attack)
    ]
    attack_labels: Counter[str] = Counter()
    items: list[dict[str, Any]] = []
    for path in normal:
        items.append(
            {
                **stat_record(path, root),
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": "repository/README.md#Normal-2UE",
            }
        )
    unknown: list[str] = []
    for path in attack:
        fine = path.parent.name
        family = FIVE_GAD_FAMILY.get(fine)
        if family is None:
            unknown.append(fine)
            continue
        attack_labels[fine] += 1
        items.append(
            {
                **stat_record(path, root),
                "fine_label": fine,
                "family_label": family,
                "binary_label": 1,
                "label_source": "repository/README.md#attack-only-pcap",
            }
        )
    marker = root / "download_complete"
    gates = {
        "download_complete_marker": marker.is_file(),
        "normal_capture_count_is_15": len(normal) == 15,
        "attack_only_capture_count_is_10": len(attack) == 10,
        "all_attack_names_mapped": not unknown,
        "selected_sources_nonempty": all(item["size_bytes"] > 0 for item in items),
        "mixed_or_duplicate_attack_pcaps_excluded": len(other_attack_pcaps) > 0,
    }
    return {
        "dataset_id": "5gad_2022",
        "root": str(root),
        "modality": "network_pcap",
        "label_binding": "capture_path_official_attack_only_subset",
        "selected_capture_count": len(items),
        "selected_size_bytes": sum(item["size_bytes"] for item in items),
        "excluded_mixed_or_duplicate_capture_count": len(other_attack_pcaps),
        "fine_label_counts": {
            "Benign": len(normal),
            **dict(sorted(attack_labels.items())),
        },
        "items": items,
        "gates": gates,
        "label_intake_passed": all(gates.values()),
        "next_stage": "strict_capture_read_and_flow_materialization",
        "feature_route": "network_packet_flow_window",
    }


def unsw_rows(
    paths: Iterable[Path],
) -> tuple[Counter[str], Counter[int], int, int, int]:
    fine_counts: Counter[str] = Counter()
    binary_counts: Counter[int] = Counter()
    rows = 0
    rejected = 0
    boundary_duplicates = 0
    previous_last: tuple[str, ...] | None = None
    for path in paths:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            current_last: tuple[str, ...] | None = None
            for ordinal, values in enumerate(reader):
                rows += 1
                current = tuple(values)
                if ordinal == 0 and previous_last is not None and current == previous_last:
                    boundary_duplicates += 1
                    current_last = current
                    continue
                if len(values) != len(UNSW_COLUMNS):
                    rejected += 1
                    current_last = current
                    continue
                row = dict(zip(UNSW_COLUMNS, values))
                try:
                    binary = int(row["label"].strip())
                    if binary not in {0, 1}:
                        raise ValueError("invalid binary label")
                    fine = row["attack_cat"].strip() if binary else "Benign"
                    if not fine:
                        raise ValueError("empty malicious attack category")
                    float(row["stime"])
                    float(row["ltime"])
                    if not row["srcip"].strip() or not row["dstip"].strip():
                        raise ValueError("empty endpoint")
                except (KeyError, TypeError, ValueError):
                    rejected += 1
                    continue
                binary_counts[binary] += 1
                fine_counts["Backdoor" if fine == "Backdoors" else fine] += 1
                current_last = current
            previous_last = current_last
    return fine_counts, binary_counts, rows, rejected, boundary_duplicates


def unsw(root: Path) -> dict[str, Any]:
    pcap_root = root / "PCAPs"
    csv_root = root / "CSVs" / "CSV Files"
    pcaps = pcap_files(pcap_root)
    flow_csvs = [csv_root / f"UNSW-NB15_{index}.csv" for index in range(1, 5)]
    fine_counts, binary_counts, rows, rejected, boundary_duplicates = unsw_rows(flow_csvs)
    ground_truth = csv_root / "NUSW-NB15_GT.csv"
    with ground_truth.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        gt_reader = csv.DictReader(handle)
        gt_rows = sum(1 for _ in gt_reader)
        gt_columns = list(gt_reader.fieldnames or ())
    expected_attacks = {
        "Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic",
        "Reconnaissance", "Shellcode", "Worms",
    }
    observed_attacks = set(fine_counts) - {"Benign"}
    gates = {
        "pcap_count_is_80": len(pcaps) == 80,
        "flow_csv_count_is_4": all(path.is_file() for path in flow_csvs),
        "official_flow_rows_after_boundary_dedup_is_2540044": (
            rows - boundary_duplicates == 2_540_044
        ),
        "three_exact_split_boundary_duplicates_identified": boundary_duplicates == 3,
        "all_flow_rows_valid": rejected == 0,
        "binary_classes_present": set(binary_counts) == {0, 1},
        "nine_attack_categories_present": observed_attacks == expected_attacks,
        "ground_truth_present": ground_truth.is_file() and gt_rows > 0,
    }
    return {
        "dataset_id": "unsw_nb15",
        "root": str(root),
        "modality": "network_pcap",
        "label_binding": "official_five_tuple_time_interval_flow_csv_and_gt",
        "pcap_count": len(pcaps),
        "pcap_size_bytes": sum(path.stat().st_size for path in pcaps),
        "pcap_items": [stat_record(path, root) for path in pcaps],
        "official_flow_rows_raw": rows,
        "official_flow_rows": rows - boundary_duplicates,
        "exact_split_boundary_duplicates": boundary_duplicates,
        "rejected_flow_rows": rejected,
        "fine_label_counts": dict(sorted(fine_counts.items())),
        "binary_label_counts": {str(key): value for key, value in sorted(binary_counts.items())},
        "ground_truth_rows": gt_rows,
        "ground_truth_columns": gt_columns,
        "gates": gates,
        "label_intake_passed": all(gates.values()),
        "next_stage": "build_sqlite_label_index_then_strict_pcap_alignment",
        "feature_route": "network_packet_flow_window",
    }


def csv_label_counts(path: Path) -> tuple[Counter[str], int, int, list[str]]:
    counts: Counter[str] = Counter()
    rows = 0
    rejected_headers = 0
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for row in reader:
            rows += 1
            if not row:
                rejected_headers += 1
                continue
            label = row[-1].strip()
            if label == "Label":
                rejected_headers += 1
                continue
            counts[label] += 1
    return counts, rows, rejected_headers, header


def cicids(root: Path) -> dict[str, Any]:
    sync_manifest_path = root / "pcap_sync_manifest.json"
    sync = json.loads(sync_manifest_path.read_text(encoding="utf-8"))
    raw = root / "raw"
    pcap_archives = sorted((raw / "Original Network Traffic and Log data").glob("*/pcap.*"))
    csvs = sorted((raw / "Processed Traffic Data for ML Algorithms").glob("*.csv"))
    counts: Counter[str] = Counter()
    rows = 0
    repeated_headers = 0
    identity_complete_files = 0
    csv_schemas: dict[str, dict[str, Any]] = {}
    for path in csvs:
        current, current_rows, current_repeated, header = csv_label_counts(path)
        counts.update(current)
        rows += current_rows
        repeated_headers += current_repeated
        identity_complete = {
            "Flow ID", "Src IP", "Src Port", "Dst IP", "Dst Port",
            "Protocol", "Timestamp", "Flow Duration", "Label",
        }.issubset(set(header))
        identity_complete_files += int(identity_complete)
        csv_schemas[path.name] = {
            "column_count": len(header),
            "identity_columns_complete": identity_complete,
            "rows": current_rows,
            "repeated_header_rows": current_repeated,
        }
    unmapped = sorted(set(counts) - set(CICIDS_FAMILY))
    gates = {
        "sync_manifest_all_sizes_match": sync.get("all_sizes_match") is True,
        "sync_manifest_object_count_is_10": sync.get("object_count") == 10,
        "ten_pcap_archives_present": len(pcap_archives) == 10,
        "ten_official_flow_csvs_present": len(csvs) == 10,
        "all_labels_mapped": not unmapped,
        "official_schedule_required": True,
        "raw_pcap_exact_join_requires_regeneration": identity_complete_files < len(csvs),
    }
    return {
        "dataset_id": "cicids2018",
        "root": str(root),
        "modality": "network_pcap",
        "label_binding": "official_schedule_ip_port_protocol_plus_regenerated_flow_identity",
        "pcap_archive_count": len(pcap_archives),
        "pcap_archive_size_bytes": sum(path.stat().st_size for path in pcap_archives),
        "pcap_archives": [stat_record(path, root) for path in pcap_archives],
        "official_flow_csv_count": len(csvs),
        "official_flow_rows_including_repeated_headers": rows,
        "repeated_header_rows": repeated_headers,
        "flow_csvs_with_complete_identity_columns": identity_complete_files,
        "fine_label_counts": dict(sorted(counts.items())),
        "family_mapping": CICIDS_FAMILY,
        "unmapped_labels": unmapped,
        "csv_schemas": csv_schemas,
        "gates": gates,
        "label_intake_passed": all(gates.values()),
        "next_stage": "regenerate_five_tuple_flow_identity_from_pcaps_then_join_official_schedule",
        "feature_route": "network_packet_flow_window_after_exact_label_gate",
        "feature_admission": "blocked_until_exact_pcap_label_join_passes",
    }


def read_tar_text(tar: tarfile.TarFile, name: str) -> str:
    member = tar.getmember(name)
    extracted = tar.extractfile(member)
    if extracted is None:
        raise ValueError(f"cannot read {name}")
    return extracted.read().decode("utf-8", errors="replace")


def cert(root: Path) -> dict[str, Any]:
    archive = root / "raw" / "12841247.zip"
    with zipfile.ZipFile(archive) as outer:
        names = outer.namelist()
        answer_bytes = outer.read("answers.tar.bz2")
        inner_release_names = sorted(name for name in names if name.startswith("r") and name.endswith(".tar.bz2"))
    with tarfile.open(fileobj=io.BytesIO(answer_bytes), mode="r:bz2") as answers:
        members = [member for member in answers.getmembers() if member.isfile()]
        csv_members = sorted(member.name for member in members if member.name.lower().endswith(".csv"))
        insiders_text = read_tar_text(answers, "answers/insiders.csv")
        scenarios_text = read_tar_text(answers, "answers/scenarios.txt")
        readme_text = read_tar_text(answers, "answers/readme.txt")
    insider_rows = list(csv.reader(io.StringIO(insiders_text)))
    nonempty_insider_rows = [row for row in insider_rows if any(cell.strip() for cell in row)]
    gates = {
        "outer_archive_present": archive.is_file() and archive.stat().st_size > 0,
        "ten_release_archives_present": len(inner_release_names) == 10,
        "answers_archive_present": bool(answer_bytes),
        "answer_csvs_present": len(csv_members) > 0,
        "insider_truth_present": len(nonempty_insider_rows) > 1,
        "scenario_truth_present": bool(scenarios_text.strip()),
        "no_pcap_members": not any(name.lower().endswith(tuple(PCAP_SUFFIXES)) for name in names),
    }
    return {
        "dataset_id": "cert_insider_threat",
        "root": str(root),
        "modality": "host_user_behavior_logs",
        "label_binding": "official_answers_malicious_user_scenario_and_event_rows",
        "outer_archive": stat_record(archive, root),
        "release_archives": inner_release_names,
        "answer_csv_count": len(csv_members),
        "answer_csv_members": csv_members,
        "insiders_nonempty_row_count": len(nonempty_insider_rows),
        "answers_readme_sha256": hashlib.sha256(readme_text.encode("utf-8")).hexdigest(),
        "scenarios_sha256": hashlib.sha256(scenarios_text.encode("utf-8")).hexdigest(),
        "gates": gates,
        "label_intake_passed": all(gates.values()),
        "next_stage": "stream_release_logs_and_join_official_answer_events",
        "feature_route": "host_user_behavior_only",
        "network_feature_admission": "not_applicable_no_pcap",
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def build(args: argparse.Namespace) -> dict[str, Any]:
    datasets = [
        five_gad(args.datasets_root / "5GAD-2022"),
        unsw(args.datasets_root / "UNSW-NB15"),
        cicids(args.datasets_root / "cic" / "cic_cse_cic_ids2018"),
        cert(args.datasets_root / "cert" / "cert_insider_threat"),
    ]
    payload: dict[str, Any] = {
        "schema_version": "caeos_four_new_label_dataset_intake_v1",
        "datasets_root": str(args.datasets_root),
        "dataset_count": len(datasets),
        "datasets": datasets,
        "all_intake_gates_passed": all(item["label_intake_passed"] for item in datasets),
        "feature_policy": {
            "network_datasets": ["5gad_2022", "unsw_nb15", "cicids2018"],
            "behavior_dataset": "cert_insider_threat",
            "require_label_gate_before_feature_extraction": True,
            "do_not_coerce_cert_to_network_features": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    atomic_json(args.output, payload)
    return payload


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
