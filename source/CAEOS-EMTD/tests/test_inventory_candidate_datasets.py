from __future__ import annotations

import csv
import zipfile
from pathlib import Path

from inventory_candidate_datasets import (
    inventory_dataset,
    parse_dataset,
    select_label_column,
)


def write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def test_select_label_column_uses_attack_before_label() -> None:
    assert select_label_column(["Flow ID", "Label", "Attack"]) == "Attack"
    assert select_label_column(["label", "subLabel", "subLabelCat"]) == "subLabelCat"


def test_inventory_profiles_headers_labels_and_zip(tmp_path: Path) -> None:
    root = tmp_path / "candidate"
    write_csv(
        root / "part-a.csv",
        [["f1", "Attack"], ["1", "Benign"], ["2", "DDoS"]],
    )
    write_csv(
        root / "nested" / "part-b.csv",
        [["f1", "Attack"], ["3", "DDoS"], ["4", "Scan"]],
    )
    with zipfile.ZipFile(root / "raw.zip", "w") as archive:
        archive.writestr("flows/a.csv", "value,label\n1,benign\n")

    report = inventory_dataset(
        "candidate",
        root,
        max_depth=4,
        max_tabular_files=10,
        sample_rows=10,
        archive_member_limit=100,
    )

    assert report["state"] == "inventoried"
    assert report["file_count"] == 3
    assert report["tabular_file_count"] == 2
    assert report["tabular_files_profiled"] == 2
    assert len(report["header_signature_counts"]) == 1
    assert report["detected_label_columns"] == {"Attack": 2}
    assert report["zip_profiles"][0]["member_suffix_counts"] == {".csv": 1}
    profiles = {profile["path"]: profile for profile in report["tabular_profiles"]}
    assert profiles["part-a.csv"]["sample_label_counts"] == {
        "Benign": 1,
        "DDoS": 1,
    }


def test_duplicate_label_columns_are_explicitly_ambiguous(tmp_path: Path) -> None:
    root = tmp_path / "candidate"
    write_csv(root / "duplicate.csv", [["f1", "Label", "Label"], ["1", "a", "b"]])

    report = inventory_dataset(
        "candidate",
        root,
        max_depth=2,
        max_tabular_files=10,
        sample_rows=10,
        archive_member_limit=100,
    )
    profile = report["tabular_profiles"][0]

    assert profile["duplicate_columns"] == {"Label": 2}
    assert profile["normalized_duplicate_columns"] == {"label": 2}
    assert profile["label_column_ambiguous"] is True


def test_depth_limit_and_dataset_parser(tmp_path: Path) -> None:
    root = tmp_path / "candidate"
    write_csv(root / "one" / "two" / "deep.csv", [["Label"], ["x"]])

    name, parsed = parse_dataset(f"demo={root}")
    report = inventory_dataset(
        name,
        parsed,
        max_depth=2,
        max_tabular_files=10,
        sample_rows=10,
        archive_member_limit=100,
    )

    assert name == "demo"
    assert report["file_count"] == 0
