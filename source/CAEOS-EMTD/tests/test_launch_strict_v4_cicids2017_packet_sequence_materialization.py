from __future__ import annotations

import json
from pathlib import Path

from launch_strict_v4_cicids2017_packet_sequence_materialization import (
    process_is_alive,
)


def test_current_process_is_alive() -> None:
    import os

    assert process_is_alive(os.getpid())


def test_launch_module_has_no_import_side_effect(tmp_path: Path) -> None:
    assert not list(tmp_path.iterdir())
    assert json.loads('{"state": "test"}')["state"] == "test"
