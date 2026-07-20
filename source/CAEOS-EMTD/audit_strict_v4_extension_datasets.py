from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from select_strict_v4_external_risk_candidate import canonical_hash


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_dataset(
    dataset_id: str,
    csv_path: Path,
    config_path: Path,
    benign_label: str,
    scenario_labels: list[str],
    minimum_groups: int = 3,
    chunksize: int = 100000,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    label_column = config["label_column"]
    group_column = config["group_column"]
    label_counts: Counter[str] = Counter()
    label_groups: dict[str, set[str]] = defaultdict(set)
    group_labels: dict[str, set[str]] = defaultdict(set)
    rows = 0
    for chunk in pd.read_csv(
        csv_path, usecols=[label_column, group_column], chunksize=chunksize
    ):
        chunk = chunk.dropna(subset=[label_column, group_column])
        labels = chunk[label_column].astype(str)
        groups = chunk[group_column].astype(str)
        rows += len(chunk)
        label_counts.update(labels)
        for label, group in zip(labels, groups):
            label_groups[label].add(group)
            group_labels[group].add(label)
    missing = sorted(set(scenario_labels) - set(label_counts))
    if benign_label not in label_counts or missing:
        raise ValueError(
            f"{dataset_id} misses benign/scenario labels: benign={benign_label in label_counts}, "
            f"scenarios={missing}"
        )
    groups_per_label = {
        label: len(label_groups[label]) for label in sorted(label_counts)
    }
    supported = [
        label
        for label in scenario_labels
        if groups_per_label.get(label, 0) >= minimum_groups
    ]
    excluded = sorted(set(scenario_labels) - set(supported))
    all_labels_group_supported = (
        groups_per_label[benign_label] >= minimum_groups and not excluded
    )
    return {
        "dataset_id": dataset_id,
        "source_csv": str(csv_path.resolve()),
        "source_size_bytes": csv_path.stat().st_size,
        "source_sha256": file_hash(csv_path),
        "config": str(config_path.resolve()),
        "config_sha256": file_hash(config_path),
        "rows_with_label_and_group": rows,
        "label_column": label_column,
        "group_column": group_column,
        "benign_label": benign_label,
        "attack_scenario_labels": scenario_labels,
        "attack_scenario_count": len(scenario_labels),
        "label_counts": dict(sorted(label_counts.items())),
        "groups_per_label": groups_per_label,
        "minimum_groups": minimum_groups,
        "strict_group_supported_attack_labels": sorted(supported),
        "strict_group_excluded_attack_labels": excluded,
        "cross_label_group_count": sum(len(labels) > 1 for labels in group_labels.values()),
        "recommended_split": (
            "capture_grouped" if all_labels_group_supported else "fingerprint_grouped"
        ),
        "evidence_tier": (
            "strict_group_generalization"
            if all_labels_group_supported
            else "fingerprint_isolated_extension"
        ),
        "strict_group_generalization_eligible": all_labels_group_supported,
    }


def build_report(
    coverage: dict[str, Any], doh: dict[str, Any], hikari: dict[str, Any]
) -> dict[str, Any]:
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    extensions = [doh, hikari]
    strict = [
        item for item in extensions if item["strict_group_generalization_eligible"]
    ]
    base_datasets = len(coverage["scenario_registry"])
    base_scenarios = int(coverage["scenario_inference_units"])
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_extension_dataset_audit_v1",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "base": {"datasets": base_datasets, "scenarios": base_scenarios},
        "datasets": {item["dataset_id"]: item for item in extensions},
        "strict_group_extension": {
            "added_datasets": len(strict),
            "added_scenarios": sum(item["attack_scenario_count"] for item in strict),
            "total_datasets": base_datasets + len(strict),
            "total_scenarios": base_scenarios
            + sum(item["attack_scenario_count"] for item in strict),
        },
        "all_protocol_tiers": {
            "added_datasets": len(extensions),
            "added_scenarios": sum(
                item["attack_scenario_count"] for item in extensions
            ),
            "total_datasets": base_datasets + len(extensions),
            "total_scenarios": base_scenarios
            + sum(item["attack_scenario_count"] for item in extensions),
        },
        "mixing_rule": (
            "fingerprint-isolated extensions must be reported separately from "
            "strict capture/group generalization"
        ),
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--doh-csv", type=Path, required=True)
    parser.add_argument("--hikari-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    doh = audit_dataset(
        "dohbrw2020",
        args.doh_csv,
        Path("configs/dohbrw2020_multiclass.json"),
        "benign",
        ["dns2tcp", "dnscat2", "iodine"],
    )
    hikari = audit_dataset(
        "hikari2021",
        args.hikari_csv,
        Path("configs/hikari2021.json"),
        "Benign",
        ["Brutefoce", "Bruteforce-XML", "Probing", "XMRIGCC CryptoMiner"],
    )
    report = build_report(coverage, doh, hikari)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
