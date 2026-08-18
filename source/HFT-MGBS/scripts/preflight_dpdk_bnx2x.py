#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
from dataclasses import asdict, dataclass
from typing import Sequence


@dataclass(frozen=True)
class PortState:
    interface: str
    pci_address: str | None
    driver: str | None
    firmware: str | None
    numa_node: int | None
    carrier: int | None
    speed_mbps: int | None
    sriov_totalvfs: int | None
    sriov_numvfs: int | None


def run(command: Sequence[str]) -> str:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def read_optional(path: pathlib.Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, PermissionError):
        return None


def parse_ethtool_info(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def parse_speed(text: str) -> int | None:
    match = re.search(r"^\s*Speed:\s*(\d+)Mb/s\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def int_or_none(raw: str | None) -> int | None:
    return int(raw) if raw is not None and re.fullmatch(r"-?\d+", raw) else None


def collect_port(interface: str, sys_root: pathlib.Path = pathlib.Path("/sys")) -> PortState:
    info = parse_ethtool_info(run(["ethtool", "-i", interface]))
    pci = info.get("bus-info")
    device = sys_root / "bus/pci/devices" / pci if pci else None
    return PortState(
        interface=interface,
        pci_address=pci,
        driver=info.get("driver"),
        firmware=info.get("firmware-version"),
        numa_node=int_or_none(read_optional(device / "numa_node")) if device else None,
        carrier=int_or_none(read_optional(sys_root / "class/net" / interface / "carrier")),
        speed_mbps=parse_speed(run(["ethtool", interface])),
        sriov_totalvfs=int_or_none(read_optional(device / "sriov_totalvfs")) if device else None,
        sriov_numvfs=int_or_none(read_optional(device / "sriov_numvfs")) if device else None,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interfaces", nargs="+", default=["ens8f0", "ens8f1"])
    parser.add_argument("--dpdk-root", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    ports = [collect_port(interface) for interface in args.interfaces]
    pci_slots = [port.pci_address.rsplit(".", 1)[0] for port in ports if port.pci_address]
    same_adapter = len(pci_slots) == len(ports) and len(set(pci_slots)) == 1
    iommu_enabled = pathlib.Path("/sys/kernel/iommu_groups").exists() and any(
        pathlib.Path("/sys/kernel/iommu_groups").iterdir()
    )
    uio_module_available = pathlib.Path(
        f"/lib/modules/{run(['uname', '-r']).strip()}/kernel/drivers/uio/uio_pci_generic.ko.xz"
    ).exists()
    dpdk_manifest = (
        read_optional(args.dpdk_root / "hft-build-manifest.txt") if args.dpdk_root else None
    )
    blockers: list[str] = []
    constraints: list[str] = []
    if any(port.driver != "bnx2x" for port in ports):
        blockers.append("unexpected_kernel_driver")
    if any(port.speed_mbps != 10_000 or port.carrier != 1 for port in ports):
        blockers.append("link_not_10gbe_up")
    if not same_adapter:
        blockers.append("ports_not_on_same_adapter")
    sriov_available = all(
        port.sriov_totalvfs is not None and port.sriov_totalvfs > 0 for port in ports
    )
    if not sriov_available:
        constraints.extend(
            ["sriov_unavailable", "all_pf_unbind_required", "service_interruption_required"]
        )
    if not uio_module_available:
        blockers.append("uio_pci_generic_unavailable")
    if dpdk_manifest is None:
        blockers.append("dpdk_build_missing")
    requires_all_pf_unbind = same_adapter and not sriov_available
    result = {
        "schema_version": 1,
        "scope": "read_only_dpdk_bnx2x_preflight",
        "ports": [asdict(port) for port in ports],
        "same_adapter": same_adapter,
        "iommu_enabled": iommu_enabled,
        "uio_pci_generic_available": uio_module_available,
        "dpdk_build_manifest_present": dpdk_manifest is not None,
        "sriov_available": sriov_available,
        "requires_all_pf_unbind": requires_all_pf_unbind,
        "rss_supported_by_bnx2x_pmd": False,
        "mutations_performed": False,
        "constraints": constraints,
        "blockers": blockers,
        "ready_for_disruptive_validation": not blockers,
        "ready_for_non_disruptive_validation": not blockers and sriov_available,
        "explicit_approval_required": requires_all_pf_unbind,
        "production_qualified": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not blockers else 10


if __name__ == "__main__":
    raise SystemExit(main())
