import json
from pathlib import Path

from watch_strict_v4_xgboost_warning import parent_ready


def test_parent_ready_requires_integrity_complete(tmp_path: Path) -> None:
    parent = {
        "execution": {"result_root": "results/core"},
    }
    parent_path = tmp_path / "results/core_protocol.json"
    parent_path.parent.mkdir(parents=True)
    parent_path.write_text(json.dumps(parent), encoding="utf-8")
    protocol = {
        "parent_protocol": {"path": "results/core_protocol.json"},
    }
    assert parent_ready(tmp_path, protocol) is False

    completion = tmp_path / "results/core/completion.json"
    completion.parent.mkdir(parents=True)
    completion.write_text(
        json.dumps({"state": "complete", "integrity_passes": True}),
        encoding="utf-8",
    )
    assert parent_ready(tmp_path, protocol) is True
