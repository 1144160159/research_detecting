import json
from pathlib import Path

from snapshot_strict_v4_core_warning_progress import canonical_hash, snapshot


def test_progress_snapshot_counts_partial_evidence(tmp_path: Path) -> None:
    protocol = {
        "execution": {
            "run_root": "runs/formal",
            "result_root": "results/formal",
        },
        "data": {"cache_root": "caches/formal", "cache_max_per_class": 5000},
        "seeds": [907, 911, 919],
        "expected_task_count": 42,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
    task = tmp_path / "runs/formal/cicids2017/bot_seed907"
    task.mkdir(parents=True)
    for name in ("metrics.json", "provenance.json"):
        (task / name).write_text("{}", encoding="utf-8")
    (task / "evidence_package.npz").write_bytes(b"evidence")

    result = snapshot(tmp_path, protocol_path)

    assert result["state"] == "valid_partial_progress"
    assert result["counts"]["metrics"] == 1
    assert result["counts"]["failures"] == 0
    assert result["coverage_valid_so_far"] is True
