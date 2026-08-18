#!/usr/bin/env python3
"""Build the official experiment/capture label index for CICIoT2022."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path, PurePosixPath


BENIGN_ARCHIVES = ["1-Power.tar.gz", "2-Idle.tar.gz", "3-Interactions.tar.gz", "4-Scenarios.tar.gz"]
ATTACK_ARCHIVE = "6-Attacks.tar.gz"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_order(value: str) -> str:
    return re.sub(r"^\d+-", "", value).strip()


def attack_labels(member_name: str) -> tuple[str, str]:
    parts = PurePosixPath(member_name).parts
    if len(parts) < 3 or parts[0] != "6-Attacks":
        raise ValueError(f"unexpected official attack member path: {member_name}")
    family = strip_order(parts[1])
    if family == "Flood":
        protocol = parts[-2] if len(parts) >= 4 else "Unspecified"
        fine = f"{family}-{protocol}"
    elif family == "RTSP Brute Force":
        tool = parts[2] if len(parts) >= 4 else "Unspecified"
        fine = f"{family}-{tool}"
    else:
        detail = parts[2] if len(parts) >= 4 else "Unspecified"
        fine = f"{family}-{detail}"
    return family, fine


def is_real_pcap_member(member: tarfile.TarInfo) -> bool:
    name = PurePosixPath(member.name).name
    return member.isfile() and name.lower().endswith((".pcap", ".pcapng")) and not name.startswith("._")


def build_index(dataset_root: Path) -> dict:
    readme = dataset_root / "Readme.txt"
    attack_archive = dataset_root / ATTACK_ARCHIVE
    if not readme.is_file() or not attack_archive.is_file():
        raise FileNotFoundError("official Readme.txt or 6-Attacks.tar.gz is absent")

    active = []
    for pcap in sorted((dataset_root / "5-Active").glob("*.pcap")):
        active.append(
            {
                "capture": pcap.relative_to(dataset_root).as_posix(),
                "pcap_bytes": pcap.stat().st_size,
                "experiment": "Active",
                "is_malicious": False,
                "attack_family": "Benign",
                "attack_fine": "Benign",
            }
        )

    attacks = []
    ignored_appledouble = 0
    attack_readme = None
    with tarfile.open(attack_archive, "r:gz") as archive:
        for member in archive:
            basename = PurePosixPath(member.name).name
            if member.name == "6-Attacks/Readme.txt" and member.isfile():
                source = archive.extractfile(member)
                attack_readme = source.read() if source is not None else None
            if member.isfile() and basename.startswith("._") and basename.lower().endswith((".pcap", ".pcapng")):
                ignored_appledouble += 1
            if not is_real_pcap_member(member):
                continue
            family, fine = attack_labels(member.name)
            attacks.append(
                {
                    "archive": ATTACK_ARCHIVE,
                    "member": member.name,
                    "pcap_bytes": member.size,
                    "experiment": "Attacks",
                    "is_malicious": True,
                    "attack_family": family,
                    "attack_fine": fine,
                }
            )
    if attack_readme is None:
        raise ValueError("official 6-Attacks/Readme.txt is absent from attack archive")
    attack_readme_text = attack_readme.decode("utf-8", errors="replace")
    if "1-Flood" not in attack_readme_text or "2-RTSP BruteForce" not in attack_readme_text:
        raise ValueError("official attack Readme does not document the indexed attack hierarchy")

    benign_archive_rules = []
    missing_benign_archives = []
    for name in BENIGN_ARCHIVES:
        path = dataset_root / name
        if not path.is_file():
            missing_benign_archives.append(name)
            continue
        benign_archive_rules.append(
            {
                "archive": name,
                "archive_bytes": path.stat().st_size,
                "experiment": strip_order(name.removesuffix(".tar.gz")),
                "member_rule": "all real .pcap/.pcapng members are official benign profiling captures",
                "is_malicious": False,
                "attack_family": "Benign",
                "attack_fine": "Benign",
            }
        )

    ready = bool(active) and bool(attacks) and not missing_benign_archives
    return {
        "schema": "caeos.ciciot2022.capture_label_index.v1",
        "dataset_id": "CICIoT2022",
        "label_granularity": "official_experiment_and_capture_member",
        "authority_granularity": "capture_member_not_official_flow_label",
        "authoritative_label_source": "Official Readme experiment semantics and official 6-Attacks archive hierarchy.",
        "limitations": (
            "No official five-tuple/time-window labels are supplied. TCP/UDP flows inherit the label of "
            "their official capture member. Benign archives use an explicit lazy member rule to avoid "
            "reading multi-gigabyte compressed PCAP payloads during index construction."
        ),
        "readme_sha256": sha256_file(readme),
        "attack_readme_sha256": hashlib.sha256(attack_readme).hexdigest(),
        "active_captures": active,
        "attack_members": attacks,
        "benign_archive_rules": benign_archive_rules,
        "summary": {
            "active_capture_count": len(active),
            "attack_capture_count": len(attacks),
            "attack_family_count": len({item["attack_family"] for item in attacks}),
            "attack_fine_count": len({item["attack_fine"] for item in attacks}),
            "benign_archive_rule_count": len(benign_archive_rules),
            "ignored_appledouble_pcap_entries": ignored_appledouble,
            "missing_benign_archives": missing_benign_archives,
            "ready_for_prefix_check": ready,
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
