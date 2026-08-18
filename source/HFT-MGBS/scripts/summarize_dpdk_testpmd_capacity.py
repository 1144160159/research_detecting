"""Summarize a sealed two-process DPDK testpmd capacity diagnostic.

The RX and TX testpmd instances print one-second port rates and a final
``show port xstats all`` block.  This module deliberately treats the output as
diagnostic evidence only: it can qualify generator/capture capacity, but can
never qualify the HFT R0 or the full pipeline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


RATE_RE = {
    "rx": re.compile(r"\bRx-pps:\s*([0-9]+)\b", re.IGNORECASE),
    "tx": re.compile(r"\bTx-pps:\s*([0-9]+)\b", re.IGNORECASE),
}
COUNTER_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+):\s*([0-9]+)\s*$")
FINAL_COUNTER_RE = {
    "rx": re.compile(r"\bRX-packets:\s*([0-9]+)\b", re.IGNORECASE),
    "tx": re.compile(r"\bTX-packets:\s*([0-9]+)\b", re.IGNORECASE),
}
STANDARD_ERROR_RE = {
    "rx_missed": re.compile(r"\bRX-missed:\s*([0-9]+)\b", re.IGNORECASE),
    "rx_errors": re.compile(r"\bRX-errors:\s*([0-9]+)\b", re.IGNORECASE),
    "rx_nombuf": re.compile(r"\bRX-nombuf:\s*([0-9]+)\b", re.IGNORECASE),
    "tx_errors": re.compile(r"\bTX-errors:\s*([0-9]+)\b", re.IGNORECASE),
}
ERROR_TOKENS = ("drop", "discard", "error", "miss", "nombuf", "failure")
QUEUE_COUNTER_RE = {
    direction: re.compile(
        rf"(?:^|[_-]){direction}[_-]?(?:q|queue)[_-]?([0-9]+).*packet",
        re.IGNORECASE,
    )
    for direction in ("rx", "tx")
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite_positive(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) and converted > 0 else None


def parse_rates(text: str, direction: str) -> list[int]:
    return [int(match.group(1)) for match in RATE_RE[direction].finditer(text)]


def parse_last_counter(text: str, direction: str) -> int | None:
    values = [
        int(match.group(1)) for match in FINAL_COUNTER_RE[direction].finditer(text)
    ]
    return values[-1] if values else None


def parse_xstats(text: str) -> tuple[dict[str, int], bool]:
    marker = "extended statistics for port"
    marker_index = text.lower().rfind(marker)
    if marker_index < 0:
        return {}, False
    counters: dict[str, int] = {}
    for line in text[marker_index:].splitlines():
        match = COUNTER_RE.match(line)
        if match is not None:
            counters[match.group(1)] = int(match.group(2))
    return counters, bool(counters)


def summarize(
    contract: dict[str, Any],
    rx_text: str,
    tx_text: str,
    *,
    contract_sha256: str,
    rx_log_sha256: str,
    tx_log_sha256: str,
) -> dict[str, Any]:
    errors: list[str] = []
    target_mpps = finite_positive(contract.get("target_capacity_mpps"))
    rx_queue_count = contract.get("rx_queue_count")
    tx_queue_count = contract.get("tx_queue_count")
    rx_lead_windows = contract.get("rx_lead_rate_windows")
    warmup_windows = contract.get("warmup_rate_windows")
    required_windows = contract.get("minimum_measured_rate_windows")
    if (
        contract.get("schema_version") != 1
        or contract.get("scope") != "dpdk_testpmd_dual_pf_capacity_only"
        or contract.get("diagnostic_only") is not True
        or target_mpps is None
        or rx_queue_count != 1
        or type(tx_queue_count) is not int
        or tx_queue_count not in (1, 4)
        or type(rx_lead_windows) is not int
        or rx_lead_windows < 0
        or type(warmup_windows) is not int
        or warmup_windows < 0
        or type(required_windows) is not int
        or required_windows <= 0
    ):
        errors.append("contract_schema")
        rx_lead_windows = 0
        warmup_windows = 0
        required_windows = 1
        target_mpps = target_mpps or math.inf

    rx_rates = parse_rates(rx_text, "rx")
    tx_rates = parse_rates(tx_text, "tx")
    rx_measured = rx_rates[rx_lead_windows + warmup_windows :]
    tx_measured = tx_rates[warmup_windows:]
    if len(rx_measured) < required_windows:
        errors.append("rx_rate_windows")
    if len(tx_measured) < required_windows:
        errors.append("tx_rate_windows")
    rx_used = rx_measured[:required_windows]
    tx_used = tx_measured[:required_windows]
    rx_min = min(rx_used) / 1_000_000.0 if rx_used else None
    tx_min = min(tx_used) / 1_000_000.0 if tx_used else None
    if rx_min is None or rx_min < target_mpps:
        errors.append("rx_target_capacity")
    if tx_min is None or tx_min < target_mpps:
        errors.append("tx_target_capacity")

    rx_xstats, rx_xstats_present = parse_xstats(rx_text)
    tx_xstats, tx_xstats_present = parse_xstats(tx_text)
    if not rx_xstats_present:
        errors.append("rx_xstats_missing")
    if not tx_xstats_present:
        errors.append("tx_xstats_missing")
    nonzero_error_xstats = {
        f"rx.{name}": value
        for name, value in rx_xstats.items()
        if value != 0 and any(token in name.lower() for token in ERROR_TOKENS)
    }
    nonzero_error_xstats.update(
        {
            f"tx.{name}": value
            for name, value in tx_xstats.items()
            if value != 0 and any(token in name.lower() for token in ERROR_TOKENS)
        }
    )
    if nonzero_error_xstats:
        errors.append("nonzero_error_xstats")

    queue_coverage: dict[str, dict[str, int]] = {"rx": {}, "tx": {}}
    if tx_queue_count > 1:
        for name, value in tx_xstats.items():
            match = QUEUE_COUNTER_RE["tx"].search(name)
            if match is not None:
                queue_coverage["tx"][match.group(1)] = value
        if any(queue_coverage["tx"].get(str(index), 0) <= 0 for index in range(tx_queue_count)):
            errors.append("tx_queue_coverage")

    rx_packets = parse_last_counter(rx_text, "rx")
    tx_packets = parse_last_counter(tx_text, "tx")
    if rx_packets is None:
        errors.append("rx_final_counter_missing")
    if tx_packets is None:
        errors.append("tx_final_counter_missing")

    standard_error_counters: dict[str, int] = {}
    for name, expression in STANDARD_ERROR_RE.items():
        source = rx_text if name.startswith("rx_") else tx_text
        values = [int(match.group(1)) for match in expression.finditer(source)]
        if not values:
            errors.append(f"{name}_missing")
        else:
            standard_error_counters[name] = values[-1]
    if any(value != 0 for value in standard_error_counters.values()):
        errors.append("nonzero_standard_error_counters")

    qualified = not errors
    return {
        "schema_version": 1,
        "scope": "dpdk_testpmd_dual_pf_capacity_result",
        "diagnostic_only": True,
        "candidate_id": contract.get("candidate_id"),
        "input_sha256": {
            "contract": contract_sha256,
            "rx_stdout": rx_log_sha256,
            "tx_stdout": tx_log_sha256,
        },
        "target_capacity_mpps": target_mpps,
        "rx_queue_count": rx_queue_count,
        "tx_queue_count": tx_queue_count,
        "queue_xstats_coverage": queue_coverage,
        "rate_window_semantics": "testpmd_explicit_1s_stats_rx_lead_then_common_warmup_v2",
        "rx_lead_rate_windows": rx_lead_windows,
        "warmup_rate_windows": warmup_windows,
        "minimum_measured_rate_windows": required_windows,
        "rx_rate_windows_observed": len(rx_rates),
        "tx_rate_windows_observed": len(tx_rates),
        "rx_rate_windows_used_pps": rx_used,
        "tx_rate_windows_used_pps": tx_used,
        "observed_rx_min_mpps": rx_min,
        "observed_tx_min_mpps": tx_min,
        "final_rx_packets": rx_packets,
        "final_tx_packets": tx_packets,
        "standard_error_counters": standard_error_counters,
        "rx_xstats_present": rx_xstats_present,
        "tx_xstats_present": tx_xstats_present,
        "nonzero_error_xstats": nonzero_error_xstats,
        "capacity_qualified": qualified,
        "errors": errors,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--rx-stdout", type=Path, required=True)
    parser.add_argument("--tx-stdout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    result = summarize(
        contract,
        args.rx_stdout.read_text(encoding="utf-8", errors="replace"),
        args.tx_stdout.read_text(encoding="utf-8", errors="replace"),
        contract_sha256=sha256_file(args.contract),
        rx_log_sha256=sha256_file(args.rx_stdout),
        tx_log_sha256=sha256_file(args.tx_stdout),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["capacity_qualified"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
