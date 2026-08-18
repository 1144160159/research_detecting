#!/usr/bin/env python3
"""Build the official capture-level label index for CICIoT2023."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


FAMILY_BY_FINE = {
    "Benign_Final": "Benign",
    "Backdoor_Malware": "Web",
    "BrowserHijacking": "Web",
    "CommandInjection": "Web",
    "DictionaryBruteForce": "BruteForce",
    "DNS_Spoofing": "Spoofing",
    "MITM-ArpSpoofing": "Spoofing",
    "SqlInjection": "Web",
    "Uploading_Attack": "Web",
    "VulnerabilityScan": "Recon",
    "XSS": "Web",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def family_for(fine: str) -> str:
    if fine in FAMILY_BY_FINE:
        return FAMILY_BY_FINE[fine]
    for prefix, family in (
        ("DDoS-", "DDoS"),
        ("DoS-", "DoS"),
        ("Recon-", "Recon"),
        ("Mirai-", "Mirai"),
    ):
        if fine.startswith(prefix):
            return family
    raise ValueError(f"unknown official CICIoT2023 label directory: {fine}")


def official_notebook_mapping(path: Path) -> dict[str, str]:
    notebook = json.loads(path.read_text())
    mapping = {}
    pattern = re.compile(r"dict_7classes\['([^']+)'\]\s*=\s*'([^']+)'")
    for cell in notebook.get("cells", []):
        for line in cell.get("source", []):
            match = pattern.search(line)
            if match:
                mapping[match.group(1)] = match.group(2)
    return mapping


def build_index(dataset_root: Path) -> dict:
    pcap_root = dataset_root / "PCAP"
    csv_root = dataset_root / "CSV" / "CSV"
    notebook = dataset_root / "example" / "example.ipynb"
    if not pcap_root.is_dir() or not csv_root.is_dir() or not notebook.is_file():
        raise FileNotFoundError("expected official PCAP, CSV/CSV, and example notebook assets")
    notebook_mapping = official_notebook_mapping(notebook)
    csv_directories = {path.name.casefold(): path for path in csv_root.iterdir() if path.is_dir()}

    captures = []
    missing_csv = []
    expected_csv_keys = set()
    for pcap in sorted(pcap_root.glob("*/*.pcap")):
        fine = pcap.parent.name
        family = family_for(fine)
        official_fine = "BenignTraffic" if fine == "Benign_Final" else fine
        if notebook_mapping.get(official_fine) != family:
            raise ValueError(
                f"official notebook mapping mismatch for {fine}: "
                f"{notebook_mapping.get(official_fine)!r} != {family!r}"
            )
        csv_directory = csv_directories.get(fine.casefold(), csv_root / fine)
        csv_path = csv_directory / f"{pcap.name}.csv"
        relative = pcap.relative_to(dataset_root).as_posix()
        csv_relative = csv_path.relative_to(dataset_root).as_posix()
        if not csv_path.is_file():
            missing_csv.append(csv_relative)
        expected_csv_keys.add((fine.casefold(), f"{pcap.name}.csv".casefold()))
        captures.append(
            {
                "capture": relative,
                "pcap_bytes": pcap.stat().st_size,
                "official_feature_csv": csv_relative,
                "official_feature_csv_present": csv_path.is_file(),
                "is_malicious": family != "Benign",
                "attack_family": family,
                "attack_fine": official_fine,
            }
        )

    actual_csv_keys = {
        (path.parent.name.casefold(), path.name.casefold())
        for path in csv_root.glob("*/*.csv")
    }
    extra_csv_keys = sorted(actual_csv_keys - expected_csv_keys)
    directory_labels = sorted({item["attack_fine"] for item in captures})
    return {
        "schema": "caeos.ciciot2023.capture_label_index.v1",
        "dataset_id": "CICIoT2023",
        "label_granularity": "capture_member",
        "authority_granularity": "capture_member_not_official_flow_label",
        "authoritative_label_source": (
            "Official PCAP attack directory, cross-checked against the official "
            "same-name CSV/CSV directory and capture CSV."
        ),
        "limitations": (
            "Official CSVs contain derived features but no five-tuple/time-window "
            "flow label. Every retained TCP/UDP flow inherits its capture label."
        ),
        "official_example_notebook_sha256": sha256_file(notebook),
        "captures": captures,
        "summary": {
            "capture_count": len(captures),
            "fine_label_count": len(directory_labels),
            "malicious_capture_count": sum(item["is_malicious"] for item in captures),
            "benign_capture_count": sum(not item["is_malicious"] for item in captures),
            "missing_official_csv_count": len(missing_csv),
            "missing_official_csv": missing_csv,
            "extra_official_csv_count": len(extra_csv_keys),
            "extra_official_csv": ["/".join(item) for item in extra_csv_keys],
            "pcap_csv_same_name_set_check_passed": not missing_csv and not extra_csv_keys,
            "ready_for_prefix_check": bool(captures) and not missing_csv and not extra_csv_keys,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_index(args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output), **report["summary"]}))
    return 0 if report["summary"]["ready_for_prefix_check"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
