from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_pug_staging_manifest import create_manifest
from deploy_strict_v4_pug_after_krc import (
    acquire_process_lock,
    release_process_lock,
    terminal_krc_ready,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_staging_manifest_binds_protocol_and_install_boundary() -> None:
    manifest = create_manifest(
        root=PROJECT_ROOT,
        protocol_path=(
            PROJECT_ROOT
            / "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
        ),
        deployer_path=PROJECT_ROOT / "deploy_strict_v4_pug_after_krc.py",
    )

    assert manifest["manifest_sha256"] == canonical_hash(manifest)
    assert "train_hybrid_open_set.py" in manifest["install_files"]
    assert "train_neural_open_set.py" in manifest["verify_only_files"]
    assert manifest["admission"]["protocol_installed_last"] is True
    assert manifest["claim_boundary"]["staging_is_not_execution"] is True


def test_krc_terminal_requires_both_summary_and_audit(tmp_path: Path) -> None:
    result = tmp_path / "results/strict_v4_krc_csr_confirmation_v1"
    result.mkdir(parents=True)
    assert terminal_krc_ready(tmp_path) is False
    summary = {
        "schema_version": "strict_v4_krc_csr_confirmation_summary_v1",
        "state": "complete",
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    (result / "summary.json").write_text(
        json.dumps(summary), encoding="utf-8"
    )
    assert terminal_krc_ready(tmp_path) is False
    audit = {
        "schema_version": "strict_v4_krc_csr_confirmation_audit_v1",
        "state": "complete",
        "summary_manifest_sha256": summary["manifest_sha256"],
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    (result / "audit.json").write_text(
        json.dumps(audit), encoding="utf-8"
    )
    assert terminal_krc_ready(tmp_path) is True


def test_lock_directory_rejects_live_owner_and_recovers_stale_owner(
    tmp_path: Path,
) -> None:
    path = tmp_path / "deployment.lock.d"
    lock = acquire_process_lock(path)
    with pytest.raises(RuntimeError, match="already active"):
        acquire_process_lock(path)
    release_process_lock(lock)

    path.mkdir()
    (path / "pid").write_text("999999999\n", encoding="utf-8")
    recovered = acquire_process_lock(path)
    assert int((recovered / "pid").read_text(encoding="utf-8")) > 0
    release_process_lock(recovered)
