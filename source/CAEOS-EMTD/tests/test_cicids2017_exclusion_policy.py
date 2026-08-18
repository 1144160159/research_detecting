from __future__ import annotations

import json
from pathlib import Path


def test_cicids2017_drops_cross_capture_scope_without_relaxing_conflicts() -> None:
    project_root = Path(__file__).resolve().parents[1]
    policy = json.loads(
        (project_root / "configs" / "unified_multimodal_v5.exclusions.json").read_text(
            encoding="utf-8"
        )
    )["datasets"]["cicids2017"]

    assert "five_tuple_present_only_in_other_capture_scope" in policy[
        "drop_unmatched_reasons"
    ]
    assert "conflicting_label" in policy["never_drop"]
    assert "conflicting_nearest_official_label" in policy["never_drop"]
