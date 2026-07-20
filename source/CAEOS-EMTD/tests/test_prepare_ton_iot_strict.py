from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

from prepare_stratified_cache import build_cache, sha256


def deterministic_loader(
    csv_path: str,
    label_column: str,
    feature_columns: list[str],
    max_per_class: int,
    chunksize: int,
    seed: int,
    additional_columns: list[str],
) -> pd.DataFrame:
    del chunksize, seed
    required = [*feature_columns, *additional_columns, label_column]
    frame = pd.read_csv(csv_path, usecols=required)
    return (
        frame.groupby(label_column, sort=True, group_keys=False)
        .head(max_per_class)
        .reset_index(drop=True)
    )


def test_ton_iot_cache_is_identity_free_hashed_and_deterministic(tmp_path: Path) -> None:
    config = json.loads(
        Path("configs/cic_ton_iot_strict.json").read_text(encoding="utf-8")
    )
    features = [
        column
        for columns in config["modalities"].values()
        for column in columns
    ]
    source = tmp_path / "ton.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Flow ID", "Src IP", "Dst IP", "Timestamp", *features, "Label", "Attack"])
        for label_index, label in enumerate(("Benign", "xss")):
            for row in range(8):
                writer.writerow(
                    [
                        f"flow-{label}-{row}", "10.0.0.1", "10.0.0.2", "2026-01-01",
                        *[label_index * 1000 + row + index for index in range(len(features))],
                        int(label != "Benign"), label,
                    ]
                )
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"

    report = build_cache(
        str(source), str(config_path), 5, 4, 7, str(first), loader=deterministic_loader
    )
    repeated = build_cache(
        str(source), str(config_path), 5, 4, 7, str(second), loader=deterministic_loader
    )

    assert first.read_bytes() == second.read_bytes()
    assert report["source_sha256"] == sha256(source)
    assert report["config_sha256"] == sha256(config_path)
    assert report["per_class"] == {"Benign": 5, "xss": 5}
    assert repeated["output_sha256"] == report["output_sha256"]
    with first.open("r", encoding="utf-8", newline="") as handle:
        columns = next(csv.reader(handle))
    assert "Flow ID" not in columns
    assert "Src IP" not in columns
    assert "Dst IP" not in columns
    assert "Timestamp" not in columns
    assert "Label" not in columns
    assert columns[-1] == "Attack"
