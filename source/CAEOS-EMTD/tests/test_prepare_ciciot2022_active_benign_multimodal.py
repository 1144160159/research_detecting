from __future__ import annotations

import json
from pathlib import Path

import pytest

from prepare_strict_v4_ciciot2022_active_benign_multimodal import (
    load_admitted_active_sources,
)


def write_audit(
    path: Path,
    source_sizes: dict[str, int],
    admitted: bool = True,
) -> None:
    path.write_text(
        json.dumps(
            {
                "status": "passed",
                "dataset_acquisition_admitted": admitted,
                "errors": [],
                "manifest_sha256": "manifest",
                "partial_files": [],
                "symlinks": [],
                "files": [
                    {
                        "kind": "pcap",
                        "relative_path": relative,
                        "size_bytes": size,
                        "sha256": f"sha-{index}",
                        "status": "passed",
                        "structure": {"capture_format": "classic_pcap"},
                    }
                    for index, (relative, size) in enumerate(
                        sorted(source_sizes.items())
                    )
                ],
            }
        ),
        encoding="utf-8",
    )


def test_load_admitted_active_sources_binds_exact_capture_set(
    tmp_path: Path,
) -> None:
    root = tmp_path / "dataset"
    active = root / "5-Active"
    active.mkdir(parents=True)
    source_sizes = {
        "5-Active/one.pcap": 4,
        "5-Active/two.pcap": 5,
    }
    (active / "one.pcap").write_bytes(b"pcap")
    (active / "two.pcap").write_bytes(b"pcap2")
    audit = root / "audit.json"
    write_audit(audit, source_sizes)

    payload, selected = load_admitted_active_sources(
        root,
        audit,
        expected_capture_count=2,
        expected_acquisition_manifest_sha256="manifest",
    )

    assert payload["dataset_acquisition_admitted"] is True
    assert [item["relative_path"] for _, item in selected] == [
        "5-Active/one.pcap",
        "5-Active/two.pcap",
    ]


def test_load_admitted_active_sources_rejects_unadmitted_acquisition(
    tmp_path: Path,
) -> None:
    root = tmp_path / "dataset"
    root.mkdir()
    audit = root / "audit.json"
    write_audit(audit, {}, admitted=False)

    with pytest.raises(ValueError, match="not admitted"):
        load_admitted_active_sources(
            root,
            audit,
            expected_capture_count=0,
            expected_acquisition_manifest_sha256="manifest",
        )
