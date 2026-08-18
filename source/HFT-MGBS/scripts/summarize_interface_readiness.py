"""Summarize fail-closed physical-interface preflight records."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def summarize(paths: list[Path], excluded: set[str]) -> dict:
    rows = []
    seen = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        interface = str(payload.get("interface", ""))
        if not interface or interface in seen:
            raise ValueError("preflight interfaces must be present and unique")
        seen.add(interface)
        errors = [str(item) for item in payload.get("errors") or []]
        hardware_errors = [
            item for item in errors if not item.startswith("thresholds.")
        ]
        explicitly_excluded = interface in excluded
        rows.append(
            {
                "interface": interface,
                "source": str(path),
                "accepted": payload.get("accepted") is True,
                "physical_nic_visible": payload.get(
                    "physical_nic_visible"
                ),
                "carrier": payload.get("carrier"),
                "operstate": payload.get("operstate"),
                "speed_mbps": payload.get("speed_mbps"),
                "driver": payload.get("driver"),
                "network_master": payload.get("network_master"),
                "has_ip_address": payload.get("has_ip_address"),
                "carries_default_route": payload.get(
                    "carries_default_route"
                ),
                "explicitly_excluded": explicitly_excluded,
                "errors": errors,
                "hardware_errors": hardware_errors,
                "hardware_eligible": (
                    not explicitly_excluded and not hardware_errors
                ),
                "full_preflight_eligible": (
                    not explicitly_excluded
                    and payload.get("accepted") is True
                ),
            }
        )

    hardware_interfaces = sorted(
        row["interface"] for row in rows if row["hardware_eligible"]
    )
    full_interfaces = sorted(
        row["interface"]
        for row in rows
        if row["full_preflight_eligible"]
    )
    hardware_pairs = [
        list(pair)
        for pair in itertools.combinations(hardware_interfaces, 2)
    ]
    full_pairs = [
        list(pair) for pair in itertools.combinations(full_interfaces, 2)
    ]
    return {
        "schema_version": 1,
        "scope": "final_10gbe_interface_readiness",
        "required_distinct_interface_count": 2,
        "minimum_speed_mbps": 10000,
        "require_unmanaged": True,
        "excluded_interfaces": sorted(excluded),
        "interfaces": sorted(rows, key=lambda row: row["interface"]),
        "hardware_eligible_interfaces": hardware_interfaces,
        "hardware_pair_count": len(hardware_pairs),
        "hardware_pairs": hardware_pairs,
        "full_preflight_eligible_interfaces": full_interfaces,
        "full_preflight_pair_count": len(full_pairs),
        "full_preflight_pairs": full_pairs,
        "final_live_run_allowed": bool(full_pairs),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("preflight", type=Path, nargs="+")
    parser.add_argument("--excluded", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.preflight, set(args.excluded))
    serialized = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["final_live_run_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
