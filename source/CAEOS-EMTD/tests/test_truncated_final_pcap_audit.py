from __future__ import annotations

import struct
import subprocess
from pathlib import Path

from scripts import audit_truncated_final_pcap_records as audit
from scripts.audit_truncated_final_pcap_records import inspect_capture


def write_capture(path: Path, declared_final_length: int, final: bytes) -> None:
    first = b"a" * 64
    with path.open("wb") as handle:
        handle.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        handle.write(struct.pack("<IIII", 1, 1, len(first), len(first)))
        handle.write(first)
        handle.write(struct.pack("<IIII", 2, 2, declared_final_length, declared_final_length))
        handle.write(final)


def test_inspect_capture_detects_truncated_final_record(tmp_path: Path) -> None:
    capture = tmp_path / "truncated.pcap"
    write_capture(capture, 68, b"b" * 19)

    result = inspect_capture(capture)

    assert result["status"] == "truncated_final_record"
    assert result["packet_count"] == 2
    assert result["declared_captured_length"] == 68
    assert result["available_captured_length"] == 19


def test_inspect_capture_accepts_valid_capture(tmp_path: Path) -> None:
    capture = tmp_path / "valid.pcap"
    write_capture(capture, 19, b"b" * 19)

    result = inspect_capture(capture)

    assert result["status"] == "valid"
    assert result["packet_count"] == 2


def test_inspect_capture_delegates_pcapng_to_capinfos(
    tmp_path: Path, monkeypatch
) -> None:
    capture = tmp_path / "capture.pcap"
    capture.write_bytes(audit.PCAPNG_MAGIC + b"pcapng-placeholder" * 2)
    monkeypatch.setattr(
        audit.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout="Number of packets: 1\n", stderr=""
        ),
    )

    result = inspect_capture(capture)

    assert result["status"] == "valid_pcapng"
    assert result["capinfos_returncode"] == 0
