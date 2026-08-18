"""Fail-closed preflight before launching physical-NIC acceptance."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "hft_mgbs"
    / "live_preflight.py"
)
SPEC = importlib.util.spec_from_file_location(
    "hft_mgbs_live_preflight_standalone", MODULE_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load live_preflight.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
audit_host_preflight = MODULE.audit_host_preflight


def _capability_mask():
    for line in Path("/proc/self/status").read_text(
        encoding="utf-8"
    ).splitlines():
        if line.startswith("CapEff:"):
            return int(line.split(":", 1)[1].strip(), 16)
    raise RuntimeError("CapEff is unavailable")

def _read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _timestamp_capabilities(interface):
    try:
        completed = subprocess.run(
            ["ethtool", "-T", interface],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    capabilities = []
    in_capabilities = False
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if stripped == "Capabilities:":
            in_capabilities = True
            continue
        if in_capabilities and not line.startswith(("\t", " ")):
            break
        if in_capabilities and stripped:
            capabilities.append(stripped)
    return capabilities


def _ip_json(*arguments):
    try:
        completed = subprocess.run(
            ["ip", "-j", *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if completed.returncode != 0:
            return []
        payload = json.loads(completed.stdout)
        return payload if isinstance(payload, list) else []
    except (OSError, ValueError, subprocess.SubprocessError):
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", required=True)
    parser.add_argument("--thresholds-file", type=Path, required=True)
    parser.add_argument("--capture-driver")
    parser.add_argument("--minimum-speed-mbps", type=int)
    parser.add_argument("--require-unmanaged", action="store_true")
    parser.add_argument(
        "--allow-virtual-diagnostic",
        action="store_true",
        help=(
            "Allow a virtual interface only for an explicitly scoped "
            "non-production diagnostic."
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    interface_path = Path("/sys/class/net") / args.interface
    if not interface_path.exists():
        parser.error("interface does not exist: {}".format(args.interface))
    with args.thresholds_file.open("r", encoding="utf-8") as handle:
        thresholds = json.load(handle)
    carrier_text = _read_text(interface_path / "carrier")
    speed_text = _read_text(interface_path / "speed")
    try:
        driver = (interface_path / "device" / "driver").resolve(
            strict=True
        ).name
    except OSError:
        driver = (
            "virtual"
            if args.allow_virtual_diagnostic
            and "/virtual/net/" in str(interface_path.resolve()).replace(
                "\\", "/"
            )
            else None
        )
    try:
        network_master = (interface_path / "master").resolve(
            strict=True
        ).name
    except OSError:
        network_master = None
    address_records = _ip_json(
        "address", "show", "dev", args.interface
    )
    has_ip_address = any(
        record.get("addr_info")
        for record in address_records
        if isinstance(record, dict)
    )
    default_route_devices = {
        str(record.get("dev"))
        for record in _ip_json("route", "show", "default")
        if isinstance(record, dict) and record.get("dev")
    }
    carries_default_route = bool(
        {args.interface, network_master} & default_route_devices
    )
    result = audit_host_preflight(
        str(interface_path.resolve()),
        _capability_mask(),
        thresholds,
        carrier=int(carrier_text) if carrier_text in ("0", "1") else None,
        operstate=_read_text(interface_path / "operstate"),
        speed_mbps=(
            int(speed_text)
            if speed_text is not None and speed_text.lstrip("-").isdigit()
            else None
        ),
        driver=driver,
        capture_driver=args.capture_driver,
        timestamp_capabilities=_timestamp_capabilities(args.interface),
        allow_virtual_diagnostic=args.allow_virtual_diagnostic,
        minimum_speed_mbps=args.minimum_speed_mbps,
        require_unmanaged=args.require_unmanaged,
        network_master=network_master,
        has_ip_address=has_ip_address,
        carries_default_route=carries_default_route,
    )
    result.update(
        {
            "schema_version": 1,
            "scope": (
                "virtual_link_live_host_preflight"
                if args.allow_virtual_diagnostic
                else "physical_nic_live_host_preflight"
            ),
            "interface": args.interface,
            "interface_realpath": str(interface_path.resolve()),
            "thresholds_file": str(args.thresholds_file),
        }
    )
    serialized = json.dumps(
        result, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
