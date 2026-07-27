from __future__ import annotations

from typing import Any

import accelerate_strict_v4_mdr_caeos_pilot_captures as base
from run_strict_v4_mdr_caeos_pilot_v2 import validate_protocol


def validate_paused_pilot_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("state") not in {"T", "t"}:
        raise ValueError("MDR pilot v2 runner is not stopped")
    if "run_strict_v4_mdr_caeos_pilot_v2.py" not in str(
        snapshot.get("cmdline", "")
    ):
        raise ValueError("unexpected MDR pilot v2 runner command")
    active_children = [
        child
        for child in snapshot.get("direct_children", [])
        if child.get("state") != "Z"
    ]
    if active_children:
        raise ValueError("MDR pilot v2 runner still has active children")


def main() -> None:
    base.validate_protocol = validate_protocol
    base.validate_paused_pilot_snapshot = validate_paused_pilot_snapshot
    base.main()


if __name__ == "__main__":
    main()
