from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from prepare_strict_v4_cicids2017_packet_sequences import (
    IDENTITY_COLUMNS,
    cleaned_header,
    parse_label_row,
    pcap_name_for_label_file,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


STATISTIC_EXCLUDED_COLUMNS = {
    "Flow ID",
    "Source IP",
    "Destination IP",
    "Timestamp",
    "Label",
}


def statistic_columns(header: list[str]) -> list[tuple[str, int]]:
    occurrences: Counter[str] = Counter()
    columns = []
    for index, name in enumerate(header):
        if not name or name in STATISTIC_EXCLUDED_COLUMNS:
            continue
        occurrences[name] += 1
        suffix = "" if occurrences[name] == 1 else f"#{occurrences[name]}"
        columns.append((f"{name}{suffix}", index))
    return columns


def numeric_value(value: str) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return float("nan")


def aggregate_duplicate_statistics(rows: list[list[float]]) -> list[float]:
    matrix = np.asarray(rows, dtype=np.float64)
    result = []
    for index in range(matrix.shape[1]):
        finite = matrix[:, index][np.isfinite(matrix[:, index])]
        result.append(float(np.median(finite)) if finite.size else float("nan"))
    return result


def augment(
    *,
    sequence_dataset: Path,
    labels_dir: Path,
    output: Path,
) -> dict[str, Any]:
    sequence_dataset = sequence_dataset.resolve()
    labels_dir = labels_dir.resolve()
    output = output.resolve()
    source_metadata = load_canonical(
        sequence_dataset.with_suffix(sequence_dataset.suffix + ".json"),
        "base packet-sequence metadata",
    )
    with np.load(sequence_dataset, allow_pickle=False) as source:
        arrays = {name: np.asarray(source[name]).copy() for name in source.files}
    flow_ids = np.asarray(arrays["flow_ids"]).astype(str)
    original_rows = int(flow_ids.size)
    seen_flow_ids: set[str] = set()
    unique_indices = []
    for index, flow_id in enumerate(flow_ids):
        if flow_id in seen_flow_ids:
            continue
        seen_flow_ids.add(flow_id)
        unique_indices.append(index)
    unique_indices_array = np.asarray(unique_indices, dtype=np.int64)
    duplicate_dataset_rows = int(original_rows - unique_indices_array.size)
    for name, values in list(arrays.items()):
        if values.ndim > 0 and values.shape[0] == original_rows:
            arrays[name] = values[unique_indices_array]
    flow_ids = np.asarray(arrays["flow_ids"]).astype(str)
    target = set(flow_ids.tolist())
    rows_by_flow_id: dict[str, list[list[float]]] = defaultdict(list)
    conflicting_duplicate_groups: set[str] = set()
    selected_names: list[str] | None = None
    counters: Counter[str] = Counter()
    label_files = sorted(
        path for path in labels_dir.glob("*.csv") if path.is_file()
    )
    if not label_files:
        raise FileNotFoundError(f"no CICIDS2017 label CSVs under {labels_dir}")
    for label_path in label_files:
        capture_id = label_path.stem
        pcap_name = pcap_name_for_label_file(label_path)
        with label_path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.reader(handle)
            try:
                header = cleaned_header(next(reader))
            except StopIteration as error:
                raise ValueError(f"empty label CSV: {label_path}") from error
            indices = {name: index for index, name in enumerate(header)}
            missing_identity = sorted(set(IDENTITY_COLUMNS) - set(indices))
            if missing_identity:
                raise ValueError(
                    f"{label_path.name} missing identity columns: {missing_identity}"
                )
            current_columns = statistic_columns(header)
            current_names = [name for name, _ in current_columns]
            if selected_names is None:
                selected_names = current_names
            elif current_names != selected_names:
                raise ValueError(
                    f"statistic columns drifted in {label_path.name}"
                )
            maximum_index = max(indices.values())
            for row in reader:
                counters["rows_seen"] += 1
                if len(row) <= maximum_index:
                    counters["malformed_rows"] += 1
                    continue
                try:
                    flow = parse_label_row(
                        row=row,
                        indices=indices,
                        capture_id=capture_id,
                        pcap_name=pcap_name,
                        seed=0,
                    )
                except (TypeError, ValueError, OverflowError):
                    counters["invalid_rows"] += 1
                    continue
                if flow.flow_id not in target:
                    continue
                values = [
                    numeric_value(row[index]) for _, index in current_columns
                ]
                previous_rows = rows_by_flow_id[flow.flow_id]
                if previous_rows:
                    if not np.allclose(
                        np.asarray(previous_rows[0]),
                        np.asarray(values),
                        equal_nan=True,
                    ):
                        conflicting_duplicate_groups.add(flow.flow_id)
                        counters["conflicting_duplicate_target_rows"] += 1
                    else:
                        counters["exact_duplicate_target_rows"] += 1
                rows_by_flow_id[flow.flow_id].append(values)
                counters["matched_target_source_rows"] += 1
    if selected_names is None:
        raise ValueError("no statistic columns were discovered")
    missing_flow_ids = sorted(target - set(rows_by_flow_id))
    if missing_flow_ids:
        raise ValueError(
            f"statistics missing for {len(missing_flow_ids)} target flows; "
            f"first={missing_flow_ids[:3]}"
        )
    statistics = np.asarray(
        [
            aggregate_duplicate_statistics(rows_by_flow_id[flow_id])
            for flow_id in flow_ids
        ],
        dtype=np.float32,
    )
    arrays["flow_statistics"] = statistics
    arrays["flow_statistic_names"] = np.asarray(selected_names)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, output)
    nonfinite_counts = {
        name: int((~np.isfinite(statistics[:, index])).sum())
        for index, name in enumerate(selected_names)
        if (~np.isfinite(statistics[:, index])).any()
    }
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_cicids2017_packet_sequence_statistic_augmentation_v1"
        ),
        "state": "complete_remote_packet_sequence_statistic_augmentation",
        "dataset": {
            "output_path": str(output),
            "output_sha256": file_hash(output),
            "rows": int(statistics.shape[0]),
            "base_rows_before_flow_id_deduplication": original_rows,
            "sequence_length": int(arrays["packet_lengths"].shape[1]),
            "flow_statistic_dimension": int(statistics.shape[1]),
            "flow_statistic_names": selected_names,
            "family_counts": dict(
                sorted(Counter(np.asarray(arrays["families"]).astype(str)).items())
            ),
        },
        "base_dataset": {
            "path": str(sequence_dataset),
            "file_sha256": file_hash(sequence_dataset),
            "metadata_manifest_sha256": source_metadata["manifest_sha256"],
        },
        "label_files": [
            {
                "path": str(path.resolve()),
                "size": path.stat().st_size,
                "sha256": file_hash(path),
            }
            for path in label_files
        ],
        "matching": dict(sorted(counters.items())),
        "duplicate_flow_id_rows_in_base_dataset": duplicate_dataset_rows,
        "conflicting_duplicate_identity_group_count": len(
            conflicting_duplicate_groups
        ),
        "nonfinite_counts_before_training_only_scaling": nonfinite_counts,
        "claim_boundary": {
            "data_preparation_only": True,
            "model_effect_result": False,
            "label_column_excluded_from_statistics": True,
            "flow_id_and_ip_addresses_excluded_from_statistics": True,
            "statistics_are_unscaled": True,
            "training_only_scaling_required_by_model": True,
            "duplicate_flow_ids_are_deduplicated_before_training": True,
            "conflicting_duplicate_statistics_use_finite_value_median": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output.with_suffix(output.suffix + ".json"), report)
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence-dataset", type=Path, required=True)
    parser.add_argument("--labels-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    report = augment(
        sequence_dataset=args.sequence_dataset,
        labels_dir=args.labels_dir,
        output=args.output,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
