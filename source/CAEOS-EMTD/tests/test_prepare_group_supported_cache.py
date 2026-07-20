from __future__ import annotations

import csv
import json
from pathlib import Path

from prepare_group_supported_cache import build_group_supported_cache, file_sha256


def test_excludes_classes_without_three_groups(tmp_path: Path) -> None:
    source = tmp_path / "source.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["feature", "CaptureGroup", "Attack"])
        writer.writerows(
            [
                [1, "g1", "eligible"],
                [2, "g2", "eligible"],
                [3, "g3", "eligible"],
                [4, "g1", "excluded"],
                [5, "g2", "excluded"],
            ]
        )
    Path(f"{source}.json").write_text(
        json.dumps(
            {
                "schema_version": "source_v1",
                "output_sha256": file_sha256(source),
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "filtered.csv"
    report = build_group_supported_cache(
        source,
        output,
        label_column="Attack",
        group_column="CaptureGroup",
        minimum_groups=3,
    )
    assert report["excluded_labels"] == ["excluded"]
    assert report["eligible_labels"] == ["eligible"]
    assert report["output_rows"] == 3
    assert "excluded" not in output.read_text(encoding="utf-8")
