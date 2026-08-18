from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--capture-index", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--coverage-summary", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def real_capture_member(name: str) -> bool:
    path = PurePosixPath(name)
    lowered = path.name.lower()
    return (
        lowered.endswith((".pcap", ".pcapng"))
        and not path.name.startswith("._")
        and "__MACOSX" not in path.parts
    )


def record(
    dataset_id: str,
    source_member: str,
    fine_label: str,
    family_label: str,
    binary_label: int,
    label_source: str,
) -> dict[str, Any]:
    identity = json.dumps(
        [dataset_id, source_member, fine_label, family_label, binary_label],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return {
        "record_id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
        "source_member": source_member,
        "fine_label": fine_label,
        "family_label": family_label,
        "binary_label": binary_label,
        "label_source": label_source,
    }


def manifest_dataset(source_manifest: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    matches = [item for item in source_manifest["datasets"] if item["id"] == dataset_id]
    if len(matches) != 1:
        raise ValueError(f"source manifest dataset cardinality is {len(matches)}: {dataset_id}")
    return matches[0]


def ciciot2023_records(
    dataset_id: str,
    dataset: dict[str, Any],
    capture_index: dict[str, Any],
    label_source: str,
) -> Iterable[dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for item in capture_index["captures"]:
        member = str(item["capture"]).replace("\\", "/")
        if member.startswith("PCAP/"):
            member = member[len("PCAP/") :]
        labels[member] = item

    source_root = str(dataset["source_root"]).replace("\\", "/")
    for source in dataset["source_files"]:
        if source["kind"] != "pcap":
            raise ValueError("CICIoT2023 source manifest unexpectedly contains an archive")
        member = posixpath.relpath(str(source["path"]).replace("\\", "/"), source_root)
        item = labels.get(member)
        if item is None:
            raise ValueError(f"missing official capture label: {member}")
        yield record(
            dataset_id,
            member,
            str(item["attack_fine"]),
            str(item["attack_family"]),
            int(bool(item["is_malicious"])),
            label_source,
        )


def ciciot2022_records(
    dataset_id: str,
    dataset: dict[str, Any],
    capture_index: dict[str, Any],
    label_source: str,
) -> Iterable[dict[str, Any]]:
    direct_labels = {str(item["capture"]): item for item in capture_index["active_captures"]}
    attack_labels = {str(item["member"]): item for item in capture_index["attack_members"]}
    benign_archives = {
        str(item["archive"]): item for item in capture_index["benign_archive_rules"]
    }
    source_root = str(dataset["source_root"]).replace("\\", "/")

    for source in dataset["source_files"]:
        kind = source["kind"]
        if kind == "pcap":
            member = posixpath.relpath(
                str(source["path"]).replace("\\", "/"), source_root
            )
            item = direct_labels.get(member)
            if item is None:
                raise ValueError(f"missing official direct-capture label: {member}")
            yield record(
                dataset_id,
                member,
                str(item["attack_fine"]),
                str(item["attack_family"]),
                int(bool(item["is_malicious"])),
                label_source,
            )
            continue
        if kind != "archive":
            raise ValueError(f"unsupported CICIoT2022 source kind: {kind}")

        archive_name = PurePosixPath(str(source["path"]).replace("\\", "/")).name
        benign_rule = benign_archives.get(archive_name)
        for member_entry in source.get("capture_members", []):
            member = str(member_entry["name"])
            if not real_capture_member(member):
                continue
            item = attack_labels.get(member)
            if item is None and benign_rule is None:
                raise ValueError(f"missing official archive-member label: {archive_name}::{member}")
            if item is None:
                item = benign_rule
            yield record(
                dataset_id,
                member,
                str(item["attack_fine"]),
                str(item["attack_family"]),
                int(bool(item["is_malicious"])),
                label_source,
            )


def manifest_source_ids(dataset_id: str, dataset: dict[str, Any]) -> set[str]:
    source_root = str(dataset["source_root"]).replace("\\", "/")
    identities: set[str] = set()
    for source in dataset["source_files"]:
        if source["kind"] == "pcap":
            member = posixpath.relpath(
                str(source["path"]).replace("\\", "/"), source_root
            )
            if dataset_id == "ciciot2023":
                member = f"PCAP/{member}"
            identities.add(member)
        elif source["kind"] == "archive":
            archive = PurePosixPath(str(source["path"]).replace("\\", "/")).name
            for member in source.get("capture_members", []):
                identities.add(f"{archive}::{member['name']}")
    return identities


def inventory_records(
    dataset_id: str,
    dataset: dict[str, Any],
    inventory: dict[str, Any],
    label_source: str,
) -> list[dict[str, Any]]:
    available = manifest_source_ids(dataset_id, dataset)
    records: list[dict[str, Any]] = []
    for item in inventory["entries"]:
        source_id = str(item["source_id"])
        if source_id not in available:
            raise ValueError(f"inventory source is absent from source manifest: {source_id}")
        member = str(item.get("member") or item.get("capture") or "")
        if dataset_id == "ciciot2023" and member.startswith("PCAP/"):
            member = member[len("PCAP/") :]
        if not real_capture_member(member):
            raise ValueError(f"inventory contains a non-PCAP member: {source_id}")
        label = item["label"]
        records.append(
            record(
                dataset_id,
                member,
                str(label["attack_fine"]),
                str(label["attack_family"]),
                int(bool(label["is_malicious"])),
                label_source,
            )
        )
    return records


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_manifest = load(args.source_manifest)
    capture_index = load(args.capture_index)
    inventory = load(args.inventory)
    coverage = load(args.coverage_summary)
    dataset_id = args.dataset_id
    dataset = manifest_dataset(source_manifest, dataset_id)

    expected_capture_dataset = {"ciciot2022": "CICIoT2022", "ciciot2023": "CICIoT2023"}
    if capture_index.get("dataset_id") != expected_capture_dataset.get(dataset_id):
        raise ValueError("capture index dataset mismatch")
    if coverage.get("dataset_id") != expected_capture_dataset.get(dataset_id):
        raise ValueError("coverage summary dataset mismatch")
    if inventory.get("dataset_id") != expected_capture_dataset.get(dataset_id):
        raise ValueError("capture inventory dataset mismatch")
    if not bool(coverage.get("formal_dataset_gate_passed")):
        raise ValueError("capture dataset has not passed the full-inventory gate")

    capture_index_sha256 = sha256_file(args.capture_index)
    if inventory.get("label_index_sha256") != capture_index_sha256:
        raise ValueError("capture inventory was not frozen against this capture index")
    label_source = (
        f"{capture_index['authoritative_label_source']}"
        f"#sha256={capture_index_sha256}"
    )
    if dataset_id not in {"ciciot2022", "ciciot2023"}:
        raise ValueError(f"unsupported capture-member dataset: {dataset_id}")
    records = inventory_records(dataset_id, dataset, inventory, label_source)

    source_members = [str(item["source_member"]) for item in records]
    if len(source_members) != len(set(source_members)):
        raise ValueError("capture-member label index contains duplicate source_member values")
    expected_count = int(coverage["selected_source_count"])
    if len(records) != expected_count:
        raise ValueError(
            f"capture-member coverage mismatch: {len(records)} != {expected_count}"
        )

    index = create_label_index(
        args.output,
        dataset_id,
        records,
        sha256_file(args.registry),
    )
    audit = {
        "schema_version": "caeos_capture_member_label_sqlite_audit_v1",
        "dataset_id": dataset_id,
        "authority_granularity": capture_index["authority_granularity"],
        "source_manifest_path": str(args.source_manifest),
        "source_manifest_sha256": sha256_file(args.source_manifest),
        "capture_index_path": str(args.capture_index),
        "capture_index_sha256": capture_index_sha256,
        "inventory_path": str(args.inventory),
        "inventory_sha256": sha256_file(args.inventory),
        "coverage_summary_path": str(args.coverage_summary),
        "coverage_summary_sha256": sha256_file(args.coverage_summary),
        "expected_source_count": expected_count,
        "indexed_source_count": len(records),
        "exact_source_member_coverage": True,
        "label_index": index,
    }
    atomic_json(args.audit_output, audit)
    return audit


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
