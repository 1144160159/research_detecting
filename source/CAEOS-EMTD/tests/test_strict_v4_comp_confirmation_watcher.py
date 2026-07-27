from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from watch_strict_v4_comp_confirmation import (
    OPENDETECT_REQUIRED,
    PAIRWISE_REQUIRED,
    build_progress,
    write_progress,
)


def _write_pairwise(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "metrics.json").write_text(
        json.dumps(
            {"risk_policy": "strict_v4_comp_confirmation_pairwise_v1"}
        ),
        encoding="utf-8",
    )
    (directory / "provenance.json").write_text("{}", encoding="utf-8")
    np.savez(
        directory / "scores.npz",
        test_unknown=np.asarray([False]),
        test_labels=np.asarray([0]),
        test_prediction=np.asarray([0]),
    )
    np.savez(directory / "evidence_package.npz", evidence=np.asarray([1.0]))


def _write_opendetect(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "metrics.json").write_text(
        json.dumps({"reports": {"opendetect": {}}}),
        encoding="utf-8",
    )
    (directory / "provenance.json").write_text("{}", encoding="utf-8")
    np.savez(
        directory / "scores.npz",
        test_unknown=np.asarray([False]),
        test_labels=np.asarray([0]),
        test_opendetect=np.asarray([0.0]),
    )


def test_progress_counts_only_complete_artifact_sets(tmp_path: Path) -> None:
    protocol = {
        "manifest_sha256": "frozen",
        "tasks": [
            {"suite": "suite", "scenario": "first", "seed": 139},
            {"suite": "suite", "scenario": "second", "seed": 149},
        ],
    }
    pairwise_root = tmp_path / "pairwise"
    opendetect_root = tmp_path / "opendetect"
    _write_pairwise(pairwise_root / "suite" / "first_seed139")
    partial = pairwise_root / "suite" / "second_seed149"
    _write_pairwise(partial)
    (partial / PAIRWISE_REQUIRED[-1]).unlink()
    _write_opendetect(opendetect_root / "suite" / "first_seed139_opendetect")

    progress = build_progress(
        protocol,
        pairwise_root,
        opendetect_root,
        tmp_path / "confirmation.json",
    )

    assert progress["pairwise"]["complete_count"] == 1
    assert progress["opendetect"]["complete_count"] == 1
    assert progress["confirmation"]["state"] == "pending"
    assert progress["manifest_sha256"] == canonical_hash(progress)


def test_zero_byte_artifact_is_not_complete(tmp_path: Path) -> None:
    protocol = {
        "manifest_sha256": "frozen",
        "tasks": [{"suite": "suite", "scenario": "only", "seed": 163}],
    }
    directory = tmp_path / "pairwise" / "suite" / "only_seed163"
    _write_pairwise(directory)
    (directory / "scores.npz").write_bytes(b"")

    progress = build_progress(
        protocol,
        tmp_path / "pairwise",
        tmp_path / "opendetect",
        tmp_path / "confirmation.json",
    )

    assert progress["pairwise"]["complete_count"] == 0


def test_corrupted_nonempty_npz_is_not_complete(tmp_path: Path) -> None:
    protocol = {
        "manifest_sha256": "frozen",
        "tasks": [{"suite": "suite", "scenario": "only", "seed": 139}],
    }
    directory = tmp_path / "pairwise" / "suite" / "only_seed139"
    _write_pairwise(directory)
    (directory / "scores.npz").write_bytes(b"not-an-npz")

    progress = build_progress(
        protocol,
        tmp_path / "pairwise",
        tmp_path / "opendetect",
        tmp_path / "confirmation.json",
    )

    assert progress["pairwise"]["complete_count"] == 0


def test_confirmation_requires_a_canonical_manifest(tmp_path: Path) -> None:
    protocol = {"manifest_sha256": "frozen", "tasks": []}
    confirmation_path = tmp_path / "confirmation.json"
    confirmation = {"decision": {"passes": True}}
    confirmation["manifest_sha256"] = canonical_hash(confirmation)
    confirmation_path.write_text(json.dumps(confirmation), encoding="utf-8")

    valid = build_progress(
        protocol,
        tmp_path / "pairwise",
        tmp_path / "opendetect",
        confirmation_path,
    )
    assert valid["confirmation"]["state"] == "complete"
    assert valid["confirmation"]["decision_passes"] is True

    confirmation["manifest_sha256"] = "corrupted"
    confirmation_path.write_text(json.dumps(confirmation), encoding="utf-8")
    invalid = build_progress(
        protocol,
        tmp_path / "pairwise",
        tmp_path / "opendetect",
        confirmation_path,
    )
    assert invalid["confirmation"]["state"] == "invalid"


def test_progress_snapshots_are_immutable_for_equal_counts(
    tmp_path: Path,
) -> None:
    progress = {
        "observed_at_utc": "2026-07-26T12:00:00.000001+00:00",
        "pairwise": {"complete_count": 6},
        "opendetect": {"complete_count": 0},
    }
    first = write_progress(progress, tmp_path)
    progress["observed_at_utc"] = "2026-07-26T12:05:00.000002+00:00"
    second = write_progress(progress, tmp_path)

    assert first != second
    assert first.is_file()
    assert second.is_file()
