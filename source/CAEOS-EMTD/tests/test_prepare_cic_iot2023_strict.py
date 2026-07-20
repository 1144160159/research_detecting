from __future__ import annotations

import csv
from pathlib import Path

from prepare_cic_iot2023_strict import FEATURE_COLUMNS, build_cache


def write_source(path: Path, offset: int, rows: int = 12) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(FEATURE_COLUMNS)
        for row_index in range(rows):
            writer.writerow(
                [str(offset + row_index + column) for column in range(len(FEATURE_COLUMNS))]
            )


def test_build_cache_is_deterministic_grouped_and_identity_free(tmp_path: Path) -> None:
    source = tmp_path / "CSV"
    write_source(source / "Benign_Final" / "benign-1.csv", 0)
    write_source(source / "CommandInjection" / "attack-1.csv", 1000)
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"

    report = build_cache(
        str(source),
        str(first),
        seed=7,
        max_per_class=5,
        group_rows=3,
        expected_labels={"Benign_Final", "CommandInjection"},
        expected_source_files=2,
    )
    repeated = build_cache(
        str(source),
        str(second),
        seed=7,
        max_per_class=5,
        group_rows=3,
        expected_labels={"Benign_Final", "CommandInjection"},
        expected_source_files=2,
    )

    assert first.read_bytes() == second.read_bytes()
    assert report["source_selection"]["merged_csv_excluded"] is True
    assert report["rows_seen_per_class"] == {"Benign": 12, "CommandInjection": 12}
    assert report["rows_sampled_per_class"] == {"Benign": 5, "CommandInjection": 5}
    assert report["output_rows"] == 10
    assert repeated["output_sha256"] == report["output_sha256"]

    with first.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert set(rows[0]) == {*FEATURE_COLUMNS, "CaptureGroup", "Attack"}
    assert {row["Attack"] for row in rows} == {"Benign", "CommandInjection"}
    assert all(len(row["CaptureGroup"]) == 64 for row in rows)
    assert "Source IP" not in rows[0]


def test_build_cache_rejects_source_drift(tmp_path: Path) -> None:
    source = tmp_path / "CSV"
    write_source(source / "Benign_Final" / "benign.csv", 0)

    try:
        build_cache(
            str(source),
            str(tmp_path / "cache.csv"),
            seed=7,
            max_per_class=5,
            group_rows=3,
            expected_labels={"Benign_Final", "MissingAttack"},
            expected_source_files=2,
        )
    except ValueError as error:
        assert "source labels mismatch" in str(error)
    else:
        raise AssertionError("source drift must fail closed")
