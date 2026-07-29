from __future__ import annotations

from pathlib import Path

import numpy as np

from create_strict_v4_packet_sequence_cuda_smoke_fixture import create_fixture


def test_smoke_fixture_has_all_required_arrays(tmp_path: Path) -> None:
    path = tmp_path / "smoke.npz"
    report = create_fixture(
        output=path, rows_per_family=5, sequence_length=8, seed=17
    )
    assert report["claim_boundary"]["effect_result"] is False
    with np.load(path, allow_pickle=False) as source:
        assert source["packet_lengths"].shape == (40, 8)
        assert set(source["families"].tolist()) == set(report["families"])
