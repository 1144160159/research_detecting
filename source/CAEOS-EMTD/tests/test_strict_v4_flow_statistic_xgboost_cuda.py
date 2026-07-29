from __future__ import annotations

from pathlib import Path

from create_strict_v4_flow_statistic_xgboost_protocol import (
    DEVELOPMENT_SEED,
    GPU_UUID,
    IMPLEMENTATIONS,
)
from train_strict_v4_flow_statistic_xgboost_task_cuda import booster_uses_cuda


def test_xgboost_cuda_configuration_detection_is_explicit() -> None:
    assert booster_uses_cuda('{"generic_param":{"device":"cuda:0"}}')
    assert not booster_uses_cuda('{"generic_param":{"device":"cpu"}}')


def test_fsx_development_identity_is_frozen() -> None:
    assert DEVELOPMENT_SEED == 29
    assert GPU_UUID.startswith("GPU-")


def test_fsx_protocol_implementations_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert all((root / name).is_file() for name in IMPLEMENTATIONS)
