from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


FINE_TO_FAMILY = {
    "Benign": "Benign",
    "Bot": "Botnet",
    "DDoS": "DDoS",
    "DoS GoldenEye": "DoS",
    "DoS Hulk": "DoS",
    "DoS Slowhttptest": "DoS",
    "DoS slowloris": "DoS",
    "FTP-Patator": "BruteForce",
    "SSH-Patator": "BruteForce",
    "Web Attack - Brute Force": "BruteForce",
    "Web Attack - Sql Injection": "WebAttack",
    "Web Attack - XSS": "WebAttack",
    "Heartbleed": "Exploit",
    "Infiltration": "Exploit",
    "PortScan": "Reconnaissance",
}

FAMILY_SCENARIOS = {
    "botnet": "Botnet",
    "bruteforce": "BruteForce",
    "ddos": "DDoS",
    "dos": "DoS",
    "exploit": "Exploit",
    "reconnaissance": "Reconnaissance",
    "web_attack": "WebAttack",
}

ATTACK_FAMILIES = tuple(FAMILY_SCENARIOS.values())
BENIGN_FAMILY = "Benign"


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_canonical(path: Path, label: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical hash mismatch")
    return payload


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def required_columns(config_path: Path) -> tuple[str, str, list[str]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    label_column = str(config["label_column"])
    group_column = str(config.get("group_column", ""))
    feature_columns = [
        str(column)
        for columns in config["modalities"].values()
        for column in columns
    ]
    columns = [label_column, *feature_columns]
    if group_column:
        columns.append(group_column)
    return label_column, group_column, list(dict.fromkeys(columns))


def _valid_existing_cache(
    *,
    output_path: Path,
    metadata_path: Path,
    source_path: Path,
    config_path: Path,
    seed: int,
    maximum_per_family: int,
) -> dict[str, Any] | None:
    if not output_path.is_file() or not metadata_path.is_file():
        return None
    try:
        metadata = load_canonical(metadata_path, "attack-family cache metadata")
    except (ValueError, json.JSONDecodeError, OSError):
        return None
    expected = {
        "source_sha256": file_hash(source_path),
        "config_sha256": file_hash(config_path),
        "seed": seed,
        "maximum_per_family": maximum_per_family,
        "mapping": FINE_TO_FAMILY,
        "output_sha256": file_hash(output_path),
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            return None
    return metadata


def materialize_attack_family_cache(
    *,
    source_path: Path,
    config_path: Path,
    output_path: Path,
    seed: int,
    maximum_per_family: int,
    chunksize: int = 50_000,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    config_path = config_path.resolve()
    output_path = output_path.resolve()
    metadata_path = output_path.with_suffix(output_path.suffix + ".json")
    existing = _valid_existing_cache(
        output_path=output_path,
        metadata_path=metadata_path,
        source_path=source_path,
        config_path=config_path,
        seed=seed,
        maximum_per_family=maximum_per_family,
    )
    if existing is not None:
        return existing
    if maximum_per_family <= 0 or chunksize <= 0:
        raise ValueError("positive maximum_per_family and chunksize are required")
    label_column, _, columns = required_columns(config_path)
    rng = np.random.default_rng(seed)
    reservoirs: dict[str, pd.DataFrame] = {}
    fine_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    observed_labels: set[str] = set()
    for chunk in pd.read_csv(
        source_path,
        usecols=columns,
        chunksize=chunksize,
        low_memory=False,
    ):
        fine_labels = chunk[label_column].astype(str).str.strip()
        unknown = sorted(set(fine_labels) - set(FINE_TO_FAMILY))
        if unknown:
            raise ValueError(f"unmapped CICIDS2017 labels: {unknown}")
        families = fine_labels.map(FINE_TO_FAMILY)
        observed_labels.update(fine_labels.unique().tolist())
        fine_counts.update(fine_labels.tolist())
        family_counts.update(families.tolist())
        chunk.insert(1, "Fine_Label", fine_labels)
        chunk[label_column] = families
        chunk["_family_priority"] = rng.random(len(chunk))
        for family, family_chunk in chunk.groupby(label_column, sort=False):
            candidate = family_chunk
            if family in reservoirs:
                candidate = pd.concat(
                    [reservoirs[family], family_chunk], ignore_index=True
                )
            reservoirs[family] = candidate.nsmallest(
                maximum_per_family, "_family_priority"
            ).copy()
    missing = sorted(set(FINE_TO_FAMILY) - observed_labels)
    if missing:
        raise ValueError(f"source is missing required CICIDS2017 labels: {missing}")
    expected_families = {BENIGN_FAMILY, *ATTACK_FAMILIES}
    if set(reservoirs) != expected_families:
        raise ValueError("attack-family cache does not contain all frozen families")
    output_frame = pd.concat(
        [reservoirs[name] for name in sorted(reservoirs)],
        ignore_index=True,
    )
    output_frame = output_frame.sort_values(
        [label_column, "_family_priority"], kind="stable"
    ).drop(columns=["_family_priority"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    output_frame.to_csv(temporary, index=False)
    os.replace(temporary, output_path)
    selected_counts = {
        str(label): int(count)
        for label, count in output_frame[label_column]
        .value_counts()
        .sort_index()
        .items()
    }
    report: dict[str, Any] = {
        "schema_version": "strict_v4_cicids2017_attack_family_cache_v1",
        "state": "complete_gpu_materialization",
        "source_path": str(source_path),
        "source_sha256": file_hash(source_path),
        "config_path": str(config_path),
        "config_sha256": file_hash(config_path),
        "seed": seed,
        "chunksize": chunksize,
        "maximum_per_family": maximum_per_family,
        "mapping": FINE_TO_FAMILY,
        "source_fine_counts": dict(sorted(fine_counts.items())),
        "source_family_counts": dict(sorted(family_counts.items())),
        "selected_family_counts": selected_counts,
        "rows": int(len(output_frame)),
        "columns": [str(column) for column in output_frame.columns],
        "output_path": str(output_path),
        "output_sha256": file_hash(output_path),
        "claim_boundary": {
            "authorized_level": "attack_family",
            "fine_subtype_claim_authorized": False,
            "benign_is_a_safety_class_not_an_attack_type": True,
            "family_balancing_uses_no_test_labels": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(metadata_path, report)
    return report
