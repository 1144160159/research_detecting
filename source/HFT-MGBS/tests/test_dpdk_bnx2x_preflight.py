from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "preflight_dpdk_bnx2x.py"
SPEC = importlib.util.spec_from_file_location("preflight_dpdk_bnx2x", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_parse_ethtool_info_preserves_firmware_value() -> None:
    parsed = MODULE.parse_ethtool_info(
        "driver: bnx2x\nfirmware-version: mbi 7.15.42 bc 7.15.23\n"
    )
    assert parsed == {
        "driver": "bnx2x",
        "firmware-version": "mbi 7.15.42 bc 7.15.23",
    }


def test_parse_speed_requires_mbps_line() -> None:
    assert MODULE.parse_speed("Speed: 10000Mb/s\nDuplex: Full\n") == 10_000
    assert MODULE.parse_speed("Speed: Unknown!\n") is None


def test_int_or_none_rejects_non_integer_sysfs_values() -> None:
    assert MODULE.int_or_none("16") == 16
    assert MODULE.int_or_none("-1") == -1
    assert MODULE.int_or_none("unsupported") is None
