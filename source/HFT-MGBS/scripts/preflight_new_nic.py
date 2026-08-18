#!/usr/bin/env python3
"""Collect and validate a read-only inventory for a newly installed capture NIC."""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.new_nic_acceptance import evaluate_inventory, exit_code_for_status


DEFAULT_CONTRACT = ROOT / "configs" / "new_nic_acceptance_contract_v1.json"


def reject_duplicate_keys(pairs: Sequence[tuple]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: {}".format(key))
        result[key] = value
    return result


def reject_nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON number: {}".format(value))


def read_json(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if path is None:
        return None
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError("{} must contain a JSON object".format(path))
    return value


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def run_optional(command: Sequence[str], timeout_s: int = 5) -> Optional[str]:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s,
        )
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip()


def collect_host_restoration_state(sys_root: Path) -> Dict[str, Any]:
    hugepages: Dict[str, Optional[str]] = {}
    for path in sorted(
        (sys_root / "devices/system/node").glob(
            "node*/hugepages/hugepages-*/nr_hugepages"
        )
    ):
        hugepages[str(path.relative_to(sys_root))] = read_optional(path)
    runtime_prefixes: List[str] = []
    for root in (Path("/var/run/dpdk"), Path("/run/dpdk")):
        try:
            runtime_prefixes.extend(
                str(path) for path in sorted(root.iterdir()) if path.is_dir()
            )
        except (FileNotFoundError, PermissionError, OSError):
            pass
    return {
        "numa_hugepages": hugepages,
        "dpdk_runtime_prefixes": sorted(set(runtime_prefixes)),
    }


def read_optional(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, PermissionError, OSError, UnicodeDecodeError):
        return None


def int_optional(value: Optional[str]) -> Optional[int]:
    if value is None or re.fullmatch(r"-?\d+", value) is None:
        return None
    return int(value)


def speed_gtps(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*GT/s", value)
    return float(match.group(1)) if match else None


def parse_key_values(text: Optional[str]) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for line in (text or "").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return values


def parse_channels(text: Optional[str]) -> Dict[str, int]:
    result = {"max_rx": 0, "max_tx": 0, "max_combined": 0}
    in_maximums = False
    for raw in (text or "").splitlines():
        line = raw.strip()
        lowered = line.lower()
        if lowered.startswith("pre-set maximums"):
            in_maximums = True
            continue
        if lowered.startswith("current hardware settings"):
            in_maximums = False
            continue
        if not in_maximums or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if not value.isdigit():
            continue
        normalized = key.strip().lower()
        if normalized == "rx":
            result["max_rx"] = int(value)
        elif normalized == "tx":
            result["max_tx"] = int(value)
        elif normalized == "combined":
            result["max_combined"] = int(value)
    return result


def parse_device_serial(text: Optional[str]) -> Optional[str]:
    match = re.search(
        r"^\s*Device Serial Number\s+([^\s]+)\s*$", text or "", re.MULTILINE
    )
    return match.group(1).strip() if match else None


def parse_permanent_mac(text: Optional[str]) -> Optional[str]:
    match = re.search(r"Permanent address:\s*([0-9a-fA-F:]{17})", text or "")
    return match.group(1).lower() if match else None


def cpu_numa_node(cpu: int, sys_root: Path) -> Optional[int]:
    cpu_path = sys_root / "devices/system/cpu" / "cpu{}".format(cpu)
    try:
        nodes = sorted(cpu_path.glob("node*"))
    except OSError:
        return None
    if len(nodes) != 1:
        return None
    match = re.fullmatch(r"node(\d+)", nodes[0].name)
    return int(match.group(1)) if match else None


def master_name(interface_path: Path) -> Optional[str]:
    master = interface_path / "master"
    try:
        return master.resolve(strict=True).name
    except (FileNotFoundError, OSError, RuntimeError):
        return None


def load_ip_state() -> tuple:
    addresses_raw = run_optional(["ip", "-j", "address", "show"])
    routes_raw = run_optional(["ip", "-j", "route", "show", "default"])
    addresses: Dict[str, List[str]] = {}
    default_routes: List[str] = []
    try:
        address_items = json.loads(addresses_raw) if addresses_raw else []
    except json.JSONDecodeError:
        address_items = []
    for item in address_items if isinstance(address_items, list) else []:
        if not isinstance(item, Mapping):
            continue
        name = item.get("ifname")
        if not isinstance(name, str):
            continue
        addresses[name] = [
            str(info.get("local"))
            for info in item.get("addr_info", [])
            if isinstance(info, Mapping) and info.get("local") is not None
        ]
    try:
        route_items = json.loads(routes_raw) if routes_raw else []
    except json.JSONDecodeError:
        route_items = []
    for item in route_items if isinstance(route_items, list) else []:
        if isinstance(item, Mapping) and isinstance(item.get("dev"), str):
            default_routes.append(str(item["dev"]))
    return addresses, sorted(set(default_routes))


def supplemental_port_map(attestation: Optional[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    result: Dict[str, Mapping[str, Any]] = {}
    ports = attestation.get("ports") if isinstance(attestation, Mapping) else None
    for item in ports if isinstance(ports, list) else []:
        if isinstance(item, Mapping) and isinstance(item.get("pci_address"), str):
            result[str(item["pci_address"])] = item
    return result


def discover_interfaces(
    sys_root: Path,
    requested: Optional[Iterable[str]],
    contract: Mapping[str, Any],
) -> List[str]:
    if requested:
        return sorted(set(requested))
    net_root = sys_root / "class/net"
    if not net_root.exists():
        return []
    excluded_pci = set(contract["hardware_identity"]["excluded_pci_addresses"])
    excluded_interfaces = set(
        contract["management_plane"]["capture_excluded_interfaces"]
    )
    result: List[str] = []
    for interface_path in sorted(net_root.iterdir()):
        if interface_path.name in excluded_interfaces:
            continue
        device = interface_path / "device"
        try:
            resolved = device.resolve(strict=True)
        except (FileNotFoundError, OSError, RuntimeError):
            continue
        pci = resolved.name
        if pci in excluded_pci:
            continue
        result.append(interface_path.name)
    return result


def collect_port(
    interface: str,
    sys_root: Path,
    addresses: Mapping[str, List[str]],
    default_routes: Sequence[str],
    supplemental: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    interface_path = sys_root / "class/net" / interface
    device_link = interface_path / "device"
    try:
        device = device_link.resolve(strict=True)
        pci = device.name
        physical = True
    except (FileNotFoundError, OSError, RuntimeError):
        device = Path("/__hft_missing_device__")
        pci = None
        physical = False
    info = parse_key_values(run_optional(["ethtool", "-i", interface]))
    link = parse_key_values(run_optional(["ethtool", interface]))
    lspci = run_optional(["lspci", "-vv", "-s", pci]) if pci else None
    permanent_mac = run_optional(["ethtool", "-P", interface])
    attested = supplemental.get(str(pci), {})
    serial = parse_device_serial(lspci) or attested.get("adapter_serial")
    if serial is None:
        permanent = parse_permanent_mac(permanent_mac)
        serial = "permanent-mac:" + permanent if permanent else None
    driver_link = device / "driver"
    try:
        sysfs_driver = driver_link.resolve(strict=True).name
    except (FileNotFoundError, OSError, RuntimeError):
        sysfs_driver = None
    speed_text = link.get("speed", "")
    speed_match = re.search(r"(\d+)\s*Mb/s", speed_text)
    irq_affinity: Dict[str, Optional[str]] = {}
    if pci:
        for irq_path in sorted((device / "msi_irqs").glob("*")):
            if not irq_path.name.isdigit():
                continue
            affinity_path = (
                Path("/proc/irq") / irq_path.name / "smp_affinity_list"
            )
            irq_affinity[irq_path.name] = read_optional(affinity_path)
    xdp_state = None
    ip_link = run_optional(["ip", "-details", "-j", "link", "show", "dev", interface])
    try:
        ip_items = json.loads(ip_link) if ip_link else []
        if isinstance(ip_items, list) and ip_items and isinstance(ip_items[0], Mapping):
            xdp_state = ip_items[0].get("xdp")
    except json.JSONDecodeError:
        xdp_state = None
    restoration_state = {
        "xdp_attachment": xdp_state,
        "driver_override": read_optional(device / "driver_override"),
        "kernel_driver": info.get("driver") or sysfs_driver,
        "mtu": int_optional(read_optional(interface_path / "mtu")),
        "tx_queue_len": int_optional(read_optional(interface_path / "tx_queue_len")),
        "features": normalize_optional_text(run_optional(["ethtool", "-k", interface])),
        "channels": normalize_optional_text(run_optional(["ethtool", "-l", interface])),
        "rings": normalize_optional_text(run_optional(["ethtool", "-g", interface])),
        "coalesce": normalize_optional_text(run_optional(["ethtool", "-c", interface])),
        "rss_indirection": normalize_optional_text(run_optional(["ethtool", "-x", interface])),
        "irq_affinity": irq_affinity,
    }
    return {
        "interface": interface,
        "pci_address": pci,
        "vendor_id": (read_optional(device / "vendor") or "").removeprefix("0x") or None,
        "device_id": (read_optional(device / "device") or "").removeprefix("0x") or None,
        "adapter_serial": serial,
        "physical": physical,
        "kernel_driver": info.get("driver") or sysfs_driver,
        "driver_version": info.get("version"),
        "firmware_version": info.get("firmware-version"),
        "numa_node": int_optional(read_optional(device / "numa_node")),
        "carrier": int_optional(read_optional(interface_path / "carrier")),
        "operstate": read_optional(interface_path / "operstate"),
        "link_speed_mbps": int(speed_match.group(1)) if speed_match else None,
        "pcie_current_width": int_optional(read_optional(device / "current_link_width")),
        "pcie_current_speed_gtps": speed_gtps(read_optional(device / "current_link_speed")),
        "pcie_max_width": int_optional(read_optional(device / "max_link_width")),
        "pcie_max_speed_gtps": speed_gtps(read_optional(device / "max_link_speed")),
        "master": master_name(interface_path),
        "ip_addresses": list(addresses.get(interface, [])),
        "default_route": interface in default_routes,
        "queue_capabilities": parse_channels(run_optional(["ethtool", "-l", interface])),
        "read_only_xdp_feature_query": run_optional(
            ["bpftool", "feature", "probe", "dev", interface]
        ),
        "restoration_state": restoration_state,
    }


def collect_inventory(
    contract: Mapping[str, Any],
    interfaces: Optional[Iterable[str]],
    worker_cpus: Sequence[int],
    stack_attestation: Optional[Dict[str, Any]],
    generator_attestation: Optional[Dict[str, Any]],
    xdp_receipt: Optional[Dict[str, Any]],
    dpdk_receipt: Optional[Dict[str, Any]],
    sys_root: Path = Path("/sys"),
) -> Dict[str, Any]:
    addresses, default_routes = load_ip_state()
    selected = discover_interfaces(sys_root, interfaces, contract)
    supplemental = supplemental_port_map(stack_attestation)
    ports = [
        collect_port(name, sys_root, addresses, default_routes, supplemental)
        for name in selected
    ]
    net_root = sys_root / "class/net"
    interfaces_present = (
        sorted(path.name for path in net_root.iterdir()) if net_root.exists() else []
    )
    lower_to_master = {}
    for name in interfaces_present:
        master = master_name(net_root / name)
        if master is not None:
            lower_to_master[name] = master
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    return {
        "schema_version": 1,
        "scope": "new_high_speed_nic_inventory",
        "captured_at_utc": now,
        "capture_host_id": socket.gethostname(),
        "collection_mode": "read_only",
        "candidate_ports": ports,
        "management_plane": {
            "interfaces_present": interfaces_present,
            "default_route_interfaces": default_routes,
            "lower_to_master": lower_to_master,
        },
        "worker_cpu_plan": {
            "cpus": list(worker_cpus),
            "numa_nodes": [cpu_numa_node(cpu, sys_root) for cpu in worker_cpus],
        },
        "stack_attestation": stack_attestation,
        "independent_generator": generator_attestation,
        "xdp_probe_receipt": xdp_receipt,
        "dpdk_probe_receipt": dpdk_receipt,
        "host_restoration_state": collect_host_restoration_state(sys_root),
        "mutations_performed": False,
    }


def parse_cpu_list(value: str) -> List[int]:
    if not value.strip():
        return []
    result = []
    for token in value.split(","):
        token = token.strip()
        if not token.isdigit():
            raise argparse.ArgumentTypeError("worker CPUs must be comma-separated integers")
        result.append(int(token))
    if len(result) != len(set(result)):
        raise argparse.ArgumentTypeError("worker CPUs must be unique")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only inventory and fail-closed acceptance preflight for a newly "
            "installed high-speed capture NIC"
        )
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--inventory", type=Path, help="validate a previously captured inventory")
    parser.add_argument("--inventory-output", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--interfaces", nargs="+")
    parser.add_argument("--worker-cpus", type=parse_cpu_list, default=parse_cpu_list(""))
    parser.add_argument("--stack-attestation", type=Path)
    parser.add_argument("--generator-attestation", type=Path)
    parser.add_argument("--xdp-receipt", type=Path)
    parser.add_argument("--dpdk-receipt", type=Path)
    parser.add_argument("--baseline-inventory", type=Path)
    parser.add_argument("--sys-root", type=Path, default=Path("/sys"))
    args = parser.parse_args()

    try:
        contract = read_json(args.contract)
        if contract is None:
            raise ValueError("contract is required")
        if args.inventory is not None:
            inventory = read_json(args.inventory)
            if inventory is None:
                raise ValueError("inventory is required")
        else:
            inventory = collect_inventory(
                contract=contract,
                interfaces=args.interfaces,
                worker_cpus=args.worker_cpus,
                stack_attestation=read_json(args.stack_attestation),
                generator_attestation=read_json(args.generator_attestation),
                xdp_receipt=read_json(args.xdp_receipt),
                dpdk_receipt=read_json(args.dpdk_receipt),
                sys_root=args.sys_root,
            )
        baseline = read_json(args.baseline_inventory)
        result = evaluate_inventory(inventory, contract, baseline_inventory=baseline)
        if args.inventory_output is not None:
            write_json_atomic(args.inventory_output, inventory)
        write_json_atomic(args.output, result)
    except (OSError, ValueError, TypeError, ArithmeticError, json.JSONDecodeError) as exc:
        error = {
            "schema_version": 1,
            "scope": "new_high_speed_nic_acceptance_preflight",
            "status": "invalid_inventory",
            "error": str(exc),
            "checks": [],
            "blockers": ["input.parse_or_io"],
            "pending": [],
            "hardware_present": False,
            "inventory_ready_for_authorized_probes": False,
            "read_only_preflight_qualified": False,
            "self_consistent_capability_receipts_valid": False,
            "receipt_trust_level": "not_established",
            "production_qualified": False,
            "final_pareto_ingestion_allowed": False,
            "mutations_performed": False,
        }
        write_json_atomic(args.output, error)
        print(json.dumps(error, ensure_ascii=False, indent=2, sort_keys=True))
        return 23

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code_for_status(str(result["status"]))


if __name__ == "__main__":
    raise SystemExit(main())
