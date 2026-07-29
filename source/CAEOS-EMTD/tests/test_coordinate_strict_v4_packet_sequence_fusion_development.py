from __future__ import annotations

import json
from pathlib import Path

from coordinate_strict_v4_packet_sequence_fusion_development import (
    dataset_is_ready,
    write_state,
)
from strict_v4_cicids2017_attack_family import canonical_hash


def test_missing_dataset_is_not_ready(tmp_path: Path) -> None:
    ready, reason = dataset_is_ready(tmp_path / "missing.npz")
    assert ready is False
    assert reason == "dataset_or_metadata_missing"


def test_coordinator_state_is_canonical(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    payload = write_state(path, "testing", confirmation_seeds_read_or_launched=False)
    stored = json.loads(path.read_text(encoding="utf-8"))
    declared = stored.pop("manifest_sha256")
    assert payload["manifest_sha256"] == declared
    assert canonical_hash(stored) == declared


def test_dataset_without_all_families_is_not_ready(tmp_path: Path) -> None:
    import numpy as np

    dataset = tmp_path / "partial.npz"
    with dataset.open("wb") as handle:
        np.savez_compressed(
            handle,
            packet_lengths=np.ones((2, 4), dtype=np.int16),
            interarrival_us=np.ones((2, 4), dtype=np.float32),
            mask=np.ones((2, 4), dtype=bool),
            families=np.asarray(["Benign", "Botnet"]),
            flow_statistics=np.ones((2, 3), dtype=np.float32),
            flow_statistic_names=np.asarray(["a", "b", "c"]),
        )
    from strict_v4_cicids2017_attack_family import file_hash

    metadata = {
        "schema_version": "test",
        "state": "complete_remote_pcap_sequence_materialization",
        "dataset": {"output_sha256": file_hash(dataset)},
    }
    metadata["manifest_sha256"] = canonical_hash(metadata)
    dataset.with_suffix(".npz.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    ready, reason = dataset_is_ready(dataset)
    assert ready is False
    assert reason.startswith("family_coverage_incomplete:")
