#!/usr/bin/env python3
"""Retain only native dataset payloads under apt_public."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_ROOT = Path(
    "/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public"
)
RECEIPT_DIR = Path(
    "/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/"
    "output/trace/dataset_cleanup"
)

# Paths are relative to each top-level dataset directory. Everything outside
# these payload roots is downloader state, local metadata, tooling, or a cache.
KEEP: dict[str, tuple[str, ...]] = {
    "ainception": ("raw",),
    "ait_ads": ("raw",),
    "ait_lds_v2": ("raw",),
    "ait_lds_v2_1": ("raw",),
    "ait_nds": ("raw",),
    "apt_sandworm": ("raw",),
    "aptsdataset": (
        "repository/APT3",
        "repository/APT5",
        "repository/APT10",
        "repository/APT19",
        "repository/APT28",
        "repository/APT29",
        "repository/APT32",
        "repository/APT35",
        "repository/APT39",
        "repository/APT41",
        "repository/Aquatic Panda",
        "repository/Dragonfly",
        "repository/FIN5",
        "repository/Windshift",
    ),
    "autolabel_selected": ("raw",),
    "cam_lds": ("raw",),
    "cam_lds_scenario3_pcaps": ("raw",),
    "cicapt_iiot_2024": ("raw",),
    "dapt2020": ("raw",),
    "darpa_tc": ("raw", "ground_truth"),
    "darpa_tc_e3_theia_hf_reapr": ("raw",),
    "dedale_v2": ("raw",),
    "linux_apt_dataset_2024": ("raw",),
    "magic_preprocessed": ("raw",),
    "nodlink_simulated_data": ("raw",),
    "optc": ("raw_original",),
    "optc_corrected": ("raw",),
    "otrf_apt29": ("raw",),
    "provcon": (
        "repository/APT1",
        "repository/APT17",
        "repository/APT29",
        "repository/APT32",
        "repository/APT32-variant",
        "repository/APT41",
    ),
    "pwnjutsu": ("network_json", "system_json", "reference"),
    "saga_v2": (
        "Known_APT_Campaigns_Dataset.zip",
        "Generated_APT_Campaigns_Dataset.zip",
        "Composite_APT_Campaigns_Dataset.zip",
    ),
    "socbed": (
        "evaluation_dataset/dataset.zip",
        "evaluation_dataset/True Positives.fods",
    ),
    "splunk_attack_data": ("repository/datasets",),
    "streamspot": ("repository/all.tar.gz",),
    "unraveled": ("raw",),
    "windows_apt_2025_mendeley_v3": ("raw",),
}

# These folders contain no downloaded dataset payload.
REMOVE_DATASET_DIRS = {"security_datasets", "simuland"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def files_under(root: Path) -> list[Path]:
    files: list[Path] = []
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in list(dirnames):
            path = base / name
            if path.is_symlink():
                files.append(path)
                dirnames.remove(name)
        files.extend(base / name for name in filenames)
    return files


def is_within(path: Path, prefix: Path) -> bool:
    try:
        path.relative_to(prefix)
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=EXPECTED_ROOT)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve(strict=True)
    if root != EXPECTED_ROOT:
        raise SystemExit(f"refusing unexpected root: {root}")

    actual_dataset_dirs = {p.name for p in root.iterdir() if p.is_dir()}
    expected_dataset_dirs = set(KEEP) | REMOVE_DATASET_DIRS
    unknown = actual_dataset_dirs - expected_dataset_dirs
    absent = set(KEEP) - actual_dataset_dirs
    if unknown or absent:
        raise SystemExit(
            f"dataset directory mismatch: unknown={sorted(unknown)} absent={sorted(absent)}"
        )

    keep_prefixes: dict[str, list[Path]] = {}
    missing_payload_roots: list[str] = []
    empty_payload_roots: list[str] = []
    for dataset, relatives in KEEP.items():
        prefixes = [(root / dataset / relative).resolve(strict=False) for relative in relatives]
        keep_prefixes[dataset] = prefixes
        for prefix in prefixes:
            if not prefix.exists():
                missing_payload_roots.append(str(prefix.relative_to(root)))
            elif prefix.is_dir() and not any(path.is_file() for path in prefix.rglob("*")):
                empty_payload_roots.append(str(prefix.relative_to(root)))
            elif prefix.is_file() and prefix.stat().st_size == 0:
                empty_payload_roots.append(str(prefix.relative_to(root)))
    if missing_payload_roots or empty_payload_roots:
        raise SystemExit(
            "payload validation failed: "
            f"missing={missing_payload_roots} empty={empty_payload_roots}"
        )

    payload_symlinks: list[Path] = []
    for dataset, prefixes in keep_prefixes.items():
        for prefix in prefixes:
            if prefix.is_symlink():
                payload_symlinks.append(prefix)
            elif prefix.is_dir():
                payload_symlinks.extend(path for path in prefix.rglob("*") if path.is_symlink())

    if args.execute:
        for link in payload_symlinks:
            target = link.resolve(strict=True)
            if not target.is_file():
                raise SystemExit(f"cannot materialize non-file symlink: {link} -> {target}")
            temporary = link.with_name(link.name + ".materializing")
            if temporary.exists():
                temporary.unlink()
            shutil.copy2(target, temporary)
            os.replace(temporary, link)

    before_files = files_under(root)
    keep_files: set[Path] = set()
    deletion_candidates: list[Path] = []
    per_dataset_before: dict[str, int] = {}
    per_dataset_keep: dict[str, int] = {}
    per_dataset_delete: dict[str, int] = {}
    for path in before_files:
        relative = path.relative_to(root)
        dataset = relative.parts[0] if relative.parts else "_root"
        per_dataset_before[dataset] = per_dataset_before.get(dataset, 0) + 1
        allowed = dataset in keep_prefixes and any(
            is_within(path, prefix) for prefix in keep_prefixes[dataset]
        )
        if allowed:
            keep_files.add(path)
            per_dataset_keep[dataset] = per_dataset_keep.get(dataset, 0) + 1
        else:
            deletion_candidates.append(path)
            per_dataset_delete[dataset] = per_dataset_delete.get(dataset, 0) + 1

    before_bytes = sum(p.stat().st_size for p in before_files if p.is_file())
    keep_bytes = sum(p.stat().st_size for p in keep_files if p.is_file())
    delete_bytes = before_bytes - keep_bytes
    summary = {
        "time": utc_now(),
        "root": str(root),
        "execute": args.execute,
        "dataset_dirs_before": len(actual_dataset_dirs),
        "dataset_dirs_to_remove": sorted(REMOVE_DATASET_DIRS),
        "payload_symlinks_to_materialize": [str(path.relative_to(root)) for path in payload_symlinks],
        "files_before": len(before_files),
        "files_to_keep": len(keep_files),
        "files_to_delete": len(deletion_candidates),
        "bytes_before": before_bytes,
        "bytes_to_keep": keep_bytes,
        "bytes_to_delete": delete_bytes,
        "per_dataset_before": per_dataset_before,
        "per_dataset_keep": per_dataset_keep,
        "per_dataset_delete": per_dataset_delete,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if not args.execute:
        return 0

    deleted_paths: list[str] = []
    for path in deletion_candidates:
        deleted_paths.append(str(path.relative_to(root)))
        path.unlink()

    for directory, _, _ in os.walk(root, topdown=False):
        candidate = Path(directory)
        if candidate == root:
            continue
        if candidate.exists() and not any(candidate.iterdir()):
            candidate.rmdir()

    after_files = files_under(root)
    extras_after = [path for path in after_files if path not in keep_files]
    missing_after = [path for path in keep_files if not path.exists()]
    if extras_after or missing_after or len(after_files) != len(keep_files):
        raise SystemExit(
            "final verification failed: "
            f"files={len(after_files)} expected={len(keep_files)} "
            f"extras={len(extras_after)} missing={len(missing_after)}"
        )

    receipt = {
        **summary,
        "finished_at": utc_now(),
        "dataset_dirs_after": sorted(p.name for p in root.iterdir() if p.is_dir()),
        "files_after": len(after_files),
        "bytes_after": sum(p.stat().st_size for p in after_files if p.is_file()),
        "extras_after": 0,
        "missing_after": 0,
        "deleted_paths": deleted_paths,
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPT_DIR / (
        "apt_public_cleanup_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "receipt": str(receipt_path),
                "files_after": receipt["files_after"],
                "bytes_after": receipt["bytes_after"],
                "deleted": len(deletion_candidates),
                "deleted_bytes": delete_bytes,
                "dataset_dirs_after": len(receipt["dataset_dirs_after"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
