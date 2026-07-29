from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from augment_strict_v4_cicids2017_packet_sequence_statistics import (
    aggregate_duplicate_statistics,
    augment,
    statistic_columns,
)
from prepare_strict_v4_cicids2017_packet_sequences import (
    cleaned_header,
    parse_label_row,
)
from strict_v4_cicids2017_attack_family import canonical_hash, file_hash


HEADER = [
    "Flow ID",
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
    "Flow Duration",
    "Flow Bytes/s",
    "Label",
]


def test_statistics_are_joined_by_flow_id_without_label_leakage(
    tmp_path: Path,
) -> None:
    labels_dir = tmp_path / "labels"
    labels_dir.mkdir()
    label_path = labels_dir / "Wednesday-workingHours.pcap_ISCX.csv"
    row = [
        "flow-1",
        "10.0.0.1",
        "1234",
        "10.0.0.2",
        "80",
        "6",
        "05/07/2017 08:42:00",
        "1000000",
        "Infinity",
        "Bot",
    ]
    with label_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerow(row)
    indices = {
        name: index for index, name in enumerate(cleaned_header(HEADER))
    }
    flow = parse_label_row(
        row=row,
        indices=indices,
        capture_id=label_path.stem,
        pcap_name="Wednesday-workingHours.pcap",
        seed=1,
    )
    base = tmp_path / "base.npz"
    with base.open("wb") as handle:
        np.savez_compressed(
            handle,
            packet_lengths=np.ones((1, 4), dtype=np.int16),
            interarrival_us=np.ones((1, 4), dtype=np.float32),
            mask=np.ones((1, 4), dtype=bool),
            flow_ids=np.asarray([flow.flow_id]),
            capture_ids=np.asarray([flow.capture_id]),
            fine_labels=np.asarray([flow.fine_label]),
            families=np.asarray([flow.family]),
        )
    metadata = {
        "schema_version": "test",
        "state": "complete_remote_pcap_sequence_materialization",
        "dataset": {"output_sha256": file_hash(base)},
    }
    metadata["manifest_sha256"] = canonical_hash(metadata)
    base.with_suffix(".npz.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    output = tmp_path / "augmented.npz"
    report = augment(
        sequence_dataset=base,
        labels_dir=labels_dir,
        output=output,
    )
    with np.load(output, allow_pickle=False) as source:
        names = source["flow_statistic_names"].astype(str).tolist()
        values = source["flow_statistics"]
    assert "Label" not in names
    assert "Flow ID" not in names
    assert "Source IP" not in names
    assert values.shape == (1, 5)
    assert np.isnan(values[0, names.index("Flow Bytes/s")])
    assert report["dataset"]["flow_statistic_dimension"] == 5
    assert report["duplicate_flow_id_rows_in_base_dataset"] == 0


def test_duplicate_statistic_names_are_positionally_disambiguated() -> None:
    assert statistic_columns(["Flow ID", "Value", "Value", "Label"]) == [
        ("Value", 1),
        ("Value#2", 2),
    ]


def test_conflicting_duplicate_statistics_use_finite_median() -> None:
    values = aggregate_duplicate_statistics(
        [[1.0, np.inf], [3.0, 7.0], [5.0, np.nan]]
    )
    assert values == [3.0, 7.0]
