from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_pug_execution_protocol import create_recovery_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    PROJECT_ROOT
    / "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
)


def test_recovery_record_binds_original_failure(tmp_path: Path) -> None:
    original = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol_path = tmp_path / "execution_protocol.json"
    protocol_path.write_text(
        json.dumps(original, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    failure_path = tmp_path / "candidate_training.failed.log"
    failure_path.write_text(
        "invalid choice: 'nested_pug_continuous_outer_min_p'\n",
        encoding="utf-8",
    )

    record = create_recovery_record(
        root=tmp_path,
        protocol_path=protocol_path,
        failed_log_path=failure_path,
    )

    assert record["original_protocol"]["canonical_sha256"] == canonical_hash(
        original
    )
    assert record["allowed_change"]["path"] == "run_nested_gate_matrix.py"
    assert "does not use candidate effects" in record["claim_boundary"]


def test_recovery_record_rejects_unrelated_failure(tmp_path: Path) -> None:
    original = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol_path = tmp_path / "execution_protocol.json"
    protocol_path.write_text(json.dumps(original), encoding="utf-8")
    failure_path = tmp_path / "candidate_training.failed.log"
    failure_path.write_text("different failure\n", encoding="utf-8")

    with pytest.raises(
        ValueError, match="canonical failed PUG execution evidence"
    ):
        create_recovery_record(
            root=tmp_path,
            protocol_path=protocol_path,
            failed_log_path=failure_path,
        )
