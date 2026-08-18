from __future__ import annotations

from pathlib import Path

from caeos_label_alignment import create_label_index
from persist_caeos_label_index import persist


def test_persist_repairs_corrupt_partial_by_verified_chunks(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    create_label_index(
        source,
        "sample",
        [
            {
                "source_member": "a.pcap",
                "fine_label": "Attack",
                "family_label": "Attack",
                "binary_label": 1,
                "label_source": "official",
            }
        ],
        "registry-sha",
    )
    destination = tmp_path / "persistent" / "sample.sqlite"
    destination.parent.mkdir()
    partial = destination.with_name(destination.name + ".partial")
    payload = bytearray(source.read_bytes())
    payload[len(payload) // 2] ^= 0xFF
    partial.write_bytes(payload)

    report = persist(
        "sample",
        source,
        destination,
        tmp_path / "audit.json",
        chunk_size_bytes=1024,
        maximum_attempts=2,
    )
    assert destination.read_bytes() == source.read_bytes()
    assert report["repaired_chunk_count"] >= 1
    assert report["publication_verified_by_target_reread"] is True
    assert report["label_index"]["record_count"] == 1
