from __future__ import annotations

import csv
import json
from pathlib import Path

from audit_tabular_config_schema import audit_schema


def test_schema_audit_requires_exact_excluded_columns(tmp_path: Path) -> None:
    source = tmp_path / "source.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerows(
            [["Flow ID", "Feature A", "Feature B", "Attack"], ["id", 1, 2, "xss"]]
        )
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "label_column": "Attack",
                "modalities": {"first": ["Feature A"], "second": ["Feature B"]},
            }
        ),
        encoding="utf-8",
    )

    report = audit_schema(str(source), str(config), 4, {"Flow ID"})
    assert report["passes"] is True
    assert report["feature_count"] == 2

    try:
        audit_schema(str(source), str(config), 4, {"Flow ID", "Unexpected"})
    except ValueError as error:
        assert "excluded column set mismatch" in str(error)
    else:
        raise AssertionError("schema drift must fail closed")
