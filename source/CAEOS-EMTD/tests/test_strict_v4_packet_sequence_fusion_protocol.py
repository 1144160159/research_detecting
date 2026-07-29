from __future__ import annotations

from pathlib import Path

from create_strict_v4_packet_sequence_fusion_protocol import (
    DEVELOPMENT_SEED,
    GPU_UUID,
)
from run_strict_v4_packet_sequence_fusion_development import (
    ResourceSampler,
    resource_summary,
    slug,
)


def test_development_identity_is_frozen() -> None:
    assert DEVELOPMENT_SEED == 29
    assert GPU_UUID.startswith("GPU-")


def test_task_slug_is_stable() -> None:
    assert slug("Web Attack") == "web_attack"


def test_empty_resource_summary_does_not_claim_success() -> None:
    sampler = ResourceSampler()
    summary = resource_summary(sampler)
    assert summary["sample_count"] == 0
    assert summary["passes_observation"] is False


def test_protocol_implementation_names_exist_locally() -> None:
    project_root = Path(__file__).resolve().parents[1]
    assert (project_root / "create_strict_v4_packet_sequence_fusion_protocol.py").is_file()
    assert (project_root / "run_strict_v4_packet_sequence_fusion_development.py").is_file()
