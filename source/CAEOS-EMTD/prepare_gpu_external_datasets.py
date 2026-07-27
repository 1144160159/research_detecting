from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import io
import json
import math
import os
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from audit_gpu_dataset_admission import (
    LsnmSessionizer,
    cicddos_group,
    lsnm_path_label,
    normalized_header,
    row_value,
)


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def categorical_number(value: str) -> float:
    digest = hashlib.blake2b(value.encode("utf-8", errors="replace"), digest_size=4)
    return float(int.from_bytes(digest.digest(), "big") % 4096)


def numeric_value(value: str) -> float:
    stripped = value.strip()
    if not stripped:
        return 0.0
    try:
        if stripped.lower().startswith(("0x", "-0x", "+0x")):
            return float(int(stripped, 0))
        number = float(stripped)
        return number if math.isfinite(number) else 0.0
    except ValueError:
        return categorical_number(stripped)


def group_priority(group: str, seed: int) -> int:
    return int(group[:16], 16) ^ ((seed * 0x9E3779B185EBCA87) & ((1 << 64) - 1))


def row_priority(group: str, member: str, row_index: int, seed: int) -> int:
    payload = f"{seed}\x1f{group}\x1f{member}\x1f{row_index}".encode()
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")


class TopGroups:
    def __init__(self, limit: int, seed: int) -> None:
        self.limit = limit
        self.seed = seed
        self.heap: list[tuple[int, str]] = []
        self.selected: set[str] = set()

    def consider(self, group: str) -> tuple[bool, str | None]:
        if group in self.selected:
            return False, None
        priority = group_priority(group, self.seed)
        item = (-priority, group)
        if len(self.heap) < self.limit:
            heapq.heappush(self.heap, item)
            self.selected.add(group)
            return True, None
        worst_priority = -self.heap[0][0]
        worst_group = self.heap[0][1]
        if (priority, group) >= (worst_priority, worst_group):
            return False, None
        _, evicted = heapq.heapreplace(self.heap, item)
        self.selected.remove(evicted)
        self.selected.add(group)
        return True, evicted


class SeedReservoir:
    def __init__(self, seed: int, groups_per_label: int, rows_per_group: int) -> None:
        self.seed = seed
        self.groups_per_label = groups_per_label
        self.rows_per_group = rows_per_group
        self.selectors: dict[str, TopGroups] = {}
        self.rows: dict[str, dict[str, list[tuple[int, int, dict[str, Any]]]]] = defaultdict(dict)
        self.counter = 0

    def consider_group(self, label: str, group: str) -> bool:
        selector = self.selectors.setdefault(
            label, TopGroups(self.groups_per_label, self.seed)
        )
        added, evicted = selector.consider(group)
        if evicted is not None:
            self.rows[label].pop(evicted, None)
        if added:
            self.rows[label].setdefault(group, [])
        return group in selector.selected

    def consider_row(
        self,
        *,
        label: str,
        group: str,
        member: str,
        row_index: int,
        row: dict[str, Any],
    ) -> None:
        heap = self.rows[label].setdefault(group, [])
        priority = row_priority(group, member, row_index, self.seed)
        self.counter += 1
        item = (-priority, self.counter, row)
        if len(heap) < self.rows_per_group:
            heapq.heappush(heap, item)
            return
        if priority < -heap[0][0]:
            heapq.heapreplace(heap, item)

    def output_rows(self) -> list[dict[str, Any]]:
        output = []
        for label in sorted(self.rows):
            for group in sorted(self.rows[label]):
                selected = sorted(
                    self.rows[label][group], key=lambda item: (-item[0], item[1])
                )
                output.extend(item[2] for item in selected)
        return output

    def summary(self) -> dict[str, Any]:
        groups = {label: len(items) for label, items in self.rows.items()}
        rows = {
            label: sum(len(heap) for heap in items.values())
            for label, items in self.rows.items()
        }
        return {
            "seed": self.seed,
            "groups_per_label": dict(sorted(groups.items())),
            "rows_per_label": dict(sorted(rows.items())),
        }


def feature_columns(config: dict[str, Any]) -> list[str]:
    return [
        feature
        for features in config["modalities"].values()
        for feature in features
    ]


def lsnm_row(
    row: list[str],
    columns: dict[str, int],
    features: list[str],
    group: str,
    label: str,
    delta: float,
) -> dict[str, Any]:
    presence = {
        "Has HTTP Method": "HTTP Request Method",
        "Has HTTP URI": "HTTP Request URI",
        "Has HTTP Host": "HTTP Host",
        "Has HTTP Cookie": "HTTP Cookie",
        "Has DNS Query": "DNS Query Name",
    }
    result: dict[str, Any] = {}
    for feature in features:
        if feature == "Packet Time Delta":
            result[feature] = delta
        elif feature in presence:
            result[feature] = float(bool(row_value(row, columns, presence[feature])))
        else:
            result[feature] = numeric_value(row_value(row, columns, feature))
    result["Flow_Group"] = group
    result["Attack"] = label
    return result


def cicddos_row(
    row: list[str],
    columns: dict[str, int],
    features: list[str],
    group: str,
    label: str,
) -> dict[str, Any]:
    result = {
        feature: numeric_value(row_value(row, columns, feature))
        for feature in features
    }
    result["Flow_Group"] = group
    result["Label"] = label
    return result


def iter_csv_members(paths: list[Path]) -> Iterable[tuple[zipfile.ZipFile, zipfile.ZipInfo]]:
    for path in paths:
        with zipfile.ZipFile(path) as archive:
            members = sorted(
                (
                    info
                    for info in archive.infolist()
                    if not info.is_dir() and info.filename.lower().endswith(".csv")
                ),
                key=lambda item: item.filename,
            )
            for info in members:
                yield archive, info


def prepare_dataset(
    *,
    dataset: str,
    archive_paths: list[Path],
    config: dict[str, Any],
    seeds: list[int],
    groups_per_label: int,
    rows_per_group: int,
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any]]:
    features = feature_columns(config)
    states = {
        seed: SeedReservoir(seed, groups_per_label, rows_per_group)
        for seed in seeds
    }
    source_rows = 0
    missing_group_rows = 0
    source_labels: Counter[str] = Counter()
    for archive, info in iter_csv_members(archive_paths):
        with archive.open(info) as raw:
            text = io.TextIOWrapper(
                raw, encoding="utf-8-sig", errors="replace", newline=""
            )
            reader = csv.reader(text)
            header = [normalized_header(value) for value in next(reader, [])]
            columns = {name: index for index, name in enumerate(header)}
            sessionizer = LsnmSessionizer(info.filename) if dataset == "LSNM2024" else None
            previous_time: dict[str, float] = {}
            for row_index, row in enumerate(reader, 1):
                if not row:
                    continue
                source_rows += 1
                if dataset == "LSNM2024":
                    label = lsnm_path_label(info.filename)
                    group = sessionizer.group(row, columns) if sessionizer else None
                else:
                    label = row_value(row, columns, "Label")
                    group = cicddos_group(info.filename, row, columns)
                if not label or group is None:
                    missing_group_rows += 1
                    continue
                source_labels[label] += 1
                selected_states = [
                    state
                    for state in states.values()
                    if state.consider_group(label, group)
                ]
                if not selected_states:
                    continue
                if dataset == "LSNM2024":
                    timestamp = numeric_value(
                        row_value(row, columns, "Frame Time (Epoch)", "Time")
                    )
                    delta = max(0.0, timestamp - previous_time.get(group, timestamp))
                    previous_time[group] = timestamp
                    normalized = lsnm_row(
                        row, columns, features, group, label, delta
                    )
                else:
                    normalized = cicddos_row(row, columns, features, group, label)
                for state in selected_states:
                    state.consider_row(
                        label=label,
                        group=group,
                        member=info.filename,
                        row_index=row_index,
                        row=normalized,
                    )
    outputs = {seed: state.output_rows() for seed, state in states.items()}
    summary = {
        "dataset": dataset,
        "source_rows": source_rows,
        "source_label_counts": dict(sorted(source_labels.items())),
        "missing_group_or_label_rows": missing_group_rows,
        "features": features,
        "seeds": {str(seed): states[seed].summary() for seed in seeds},
    }
    return outputs, summary


def write_prepared(
    *,
    dataset: str,
    outputs: dict[int, list[dict[str, Any]]],
    summary: dict[str, Any],
    config: dict[str, Any],
    output_root: Path,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    dataset_root = output_root / dataset
    dataset_root.mkdir(parents=True, exist_ok=True)
    columns = feature_columns(config) + [config["group_column"], config["label_column"]]
    files = {}
    for seed, rows in sorted(outputs.items()):
        path = dataset_root / f"seed{seed}.csv"
        temporary = path.with_suffix(".csv.tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, path)
        label_counts = Counter(str(row[config["label_column"]]) for row in rows)
        group_counts: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            group_counts[str(row[config["label_column"]])].add(
                str(row[config["group_column"]])
            )
        checks = {
            "has_rows": bool(rows),
            "minimum_three_groups_per_label": bool(group_counts)
            and min(map(len, group_counts.values())) >= 3,
            "all_values_finite": all(
                math.isfinite(float(row[feature]))
                for row in rows
                for feature in feature_columns(config)
            ),
        }
        sidecar = {
            "schema_version": "gpu_external_prepared_seed_v1",
            "dataset": dataset,
            "seed": seed,
            "rows": len(rows),
            "label_counts": dict(sorted(label_counts.items())),
            "groups_per_label": {
                label: len(groups) for label, groups in sorted(group_counts.items())
            },
            "columns": columns,
            "csv_sha256": sha256_file(path),
            "checks": checks,
            "passed": all(checks.values()),
            "provenance": provenance,
        }
        atomic_json(Path(str(path) + ".json"), sidecar)
        files[str(seed)] = sidecar
    manifest = {
        "schema_version": "gpu_external_prepared_dataset_manifest_v1",
        "dataset": dataset,
        "source_summary": summary,
        "files": files,
        "passed": bool(files) and all(item["passed"] for item in files.values()),
    }
    atomic_json(dataset_root / "manifest.json", manifest)
    if manifest["passed"]:
        (dataset_root / "preparation_complete").touch()
    return manifest


def require_admission(audit: dict[str, Any], dataset: str) -> None:
    if audit.get("schema_version") != "gpu_malicious_dataset_full_admission_audit_v1":
        raise ValueError("unexpected full admission audit schema")
    if not audit.get("admission_passed"):
        raise ValueError("full dataset admission audit did not pass")
    if not audit["datasets"][dataset]["admission_passed"]:
        raise ValueError(f"{dataset} did not pass its admission gate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("LSNM2024", "CICDDoS2019"), required=True)
    parser.add_argument("--admission-audit", type=Path, required=True)
    parser.add_argument("--expansion-protocol", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[223, 227, 229])
    parser.add_argument("--groups-per-label", type=int, required=True)
    parser.add_argument("--rows-per-group", type=int, required=True)
    args = parser.parse_args()
    audit = json.loads(args.admission_audit.read_text(encoding="utf-8"))
    protocol = json.loads(args.expansion_protocol.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require_admission(audit, args.dataset)
    identities = protocol["source_identity"]
    token = "LSNM2024" if args.dataset == "LSNM2024" else "CICDDoS2019"
    archives = [Path(item["path"]) for item in identities if token in item["path"]]
    outputs, summary = prepare_dataset(
        dataset=args.dataset,
        archive_paths=archives,
        config=config,
        seeds=args.seeds,
        groups_per_label=args.groups_per_label,
        rows_per_group=args.rows_per_group,
    )
    provenance = {
        "admission_audit_sha256": sha256_file(args.admission_audit),
        "expansion_protocol_sha256": sha256_file(args.expansion_protocol),
        "config_sha256": sha256_file(args.config),
        "source_sha256": audit["source_sha256"],
        "groups_per_label": args.groups_per_label,
        "rows_per_group": args.rows_per_group,
    }
    manifest = write_prepared(
        dataset=args.dataset,
        outputs=outputs,
        summary=summary,
        config=config,
        output_root=args.output_root,
        provenance=provenance,
    )
    if not manifest["passed"]:
        raise SystemExit(f"{args.dataset} preparation failed integrity gates")
    print(json.dumps({"dataset": args.dataset, "passed": True}, sort_keys=True))


if __name__ == "__main__":
    main()
