from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file
from intake_caeos_four_new_label_datasets import FIVE_GAD_FAMILY


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    return parser.parse_args()


def selected(dataset_root: Path) -> list[tuple[Path, str, str, int]]:
    repository = dataset_root / "repository"
    result = [
        (path, "Benign", "Benign", 0)
        for path in sorted((repository / "Normal-2UE").glob("*.pcapng"))
    ]
    attacks = sorted((repository / "Attacks").glob("*/Attacks_*.pcapng"))
    for path in attacks:
        fine = path.parent.name
        if fine not in FIVE_GAD_FAMILY:
            raise ValueError(f"unmapped 5GAD attack: {fine}")
        result.append((path, fine, FIVE_GAD_FAMILY[fine], 1))
    if len(result) != 25:
        raise ValueError(f"expected 25 selected 5GAD captures, found {len(result)}")
    return result


def build(args: argparse.Namespace) -> dict[str, Any]:
    captures = selected(args.dataset_root)
    records = []
    for path, fine, family, binary in captures:
        relative = path.resolve().relative_to(args.dataset_root.resolve()).as_posix()
        records.append(
            {
                "record_id": hashlib.sha256(relative.encode("utf-8")).hexdigest(),
                "source_member": relative,
                "fine_label": fine,
                "family_label": family,
                "binary_label": binary,
                "label_source": (
                    "repository/README.md#Normal-2UE"
                    if binary == 0
                    else "repository/README.md#attack-only-pcap"
                ),
            }
        )
    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index, "5gad_2022", records, registry_sha256
    )
    audit: dict[str, Any] = {
        "schema_version": "caeos_5gad2022_label_index_audit_v1",
        "dataset_id": "5gad_2022",
        "dataset_root": str(args.dataset_root),
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "capture_count": len(records),
        "source_size_bytes": sum(path.stat().st_size for path, *_ in captures),
        "fine_label_counts": dict(sorted(Counter(row["fine_label"] for row in records).items())),
        "family_label_counts": dict(sorted(Counter(row["family_label"] for row in records).items())),
        "binary_label_counts": {
            str(key): value
            for key, value in sorted(Counter(row["binary_label"] for row in records).items())
        },
        "selection_policy": {
            "normal": "Normal-2UE/*.pcapng",
            "malicious": "Attacks/*/Attacks_*.pcapng",
            "excluded": "allcap, locap and per-interface attack captures because README says they may contain benign incidental traffic and duplicate the attack-only capture",
        },
        "label_index": index,
        "ready_for_strict_capture_audit": True,
    }
    audit["audit_sha256"] = hashlib.sha256(
        json.dumps(audit, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    atomic_json(args.audit_output, audit)
    return audit


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
