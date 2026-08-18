from __future__ import annotations

from pathlib import Path

import publish_caeos_chunked_artifact
from publish_caeos_chunked_artifact import publish


def test_chunked_publication_survives_fsync_error_and_reuses_parts(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "artifact.bin"
    payload = (b"caeos-emtd" * 300_000) + b"tail"
    source.write_bytes(payload)
    real_fsync = publish_caeos_chunked_artifact.os.fsync
    calls = 0

    def first_fsync_fails(file_descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError(5, "synthetic NFS EIO")
        real_fsync(file_descriptor)

    monkeypatch.setattr(
        publish_caeos_chunked_artifact.os, "fsync", first_fsync_fails
    )
    destination = tmp_path / "published"
    report = publish(source, destination, 1024 * 1024, 2, 0)
    assert report["status"] == "complete"
    assert report["source_retained"] is True
    assert report["chunks"][0]["fsync_errors"]
    rebuilt = b"".join(
        Path(chunk["path"]).read_bytes() for chunk in report["chunks"]
    )
    assert rebuilt == payload

    reused = publish(source, destination, 1024 * 1024, 2, 0)
    assert {chunk["status"] for chunk in reused["chunks"]} == {
        "reused_verified"
    }
