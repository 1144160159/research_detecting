from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_PATH = (
    Path(__file__).resolve().parent
    / "contracts"
    / "caeos_delivery_contract_v1.json"
)


def load_delivery_contract(path: str | Path = CONTRACT_PATH) -> dict[str, Any]:
    contract_path = Path(path)
    with contract_path.open("r", encoding="utf-8") as handle:
        contract = json.load(handle)
    validate_delivery_contract(contract)
    return contract


def validate_delivery_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != "caeos_delivery_contract_v1":
        raise ValueError("unsupported delivery contract schema")

    metrics = contract.get("safety_metrics")
    gates = contract.get("acceptance_gates")
    lines = contract.get("delivery_lines")
    layers = contract.get("metric_layers")
    if not isinstance(metrics, Mapping) or not metrics:
        raise ValueError("safety_metrics must be a nonempty object")
    if not isinstance(gates, Mapping) or not gates:
        raise ValueError("acceptance_gates must be a nonempty object")
    if not isinstance(lines, Mapping) or set(lines) != {"engineering", "paper"}:
        raise ValueError("delivery_lines must define engineering and paper")
    if not isinstance(layers, Mapping) or set(layers) != {
        "known_classification",
        "unknown_detection",
        "joint_open_set",
    }:
        raise ValueError("metric_layers must define the three metric layers")

    for metric_name, rule in metrics.items():
        if not isinstance(rule, Mapping):
            raise ValueError(f"metric rule {metric_name} must be an object")
        if rule.get("operator") not in {"ge", "lt"}:
            raise ValueError(f"metric rule {metric_name} has invalid operator")
        threshold = rule.get("threshold")
        if not isinstance(threshold, (int, float)) or not 0.0 <= threshold <= 1.0:
            raise ValueError(f"metric rule {metric_name} has invalid threshold")

    for gate_name, gate_metrics in gates.items():
        if not isinstance(gate_metrics, list) or not gate_metrics:
            raise ValueError(f"gate {gate_name} must list metrics")
        missing = set(gate_metrics) - set(metrics)
        if missing:
            raise ValueError(f"gate {gate_name} references unknown metrics: {missing}")

    for line_name, line in lines.items():
        gate_name = line.get("required_safety_gate")
        if gate_name not in gates:
            raise ValueError(f"delivery line {line_name} references unknown gate")


def evaluate_acceptance_gate(
    observed_metrics: Mapping[str, float],
    gate_name: str,
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    current_contract = (
        dict(contract) if contract is not None else load_delivery_contract()
    )
    validate_delivery_contract(current_contract)
    gates = current_contract["acceptance_gates"]
    if gate_name not in gates:
        raise ValueError(f"unknown acceptance gate: {gate_name}")

    checks: dict[str, Any] = {}
    for metric_name in gates[gate_name]:
        rule = current_contract["safety_metrics"][metric_name]
        raw_value = observed_metrics.get(metric_name)
        if raw_value is None:
            checks[metric_name] = {
                "passed": False,
                "observed": None,
                "operator": rule["operator"],
                "threshold": float(rule["threshold"]),
                "reason": "missing_metric",
            }
            continue
        value = float(raw_value)
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{metric_name} must be within [0, 1]")
        passed = (
            value >= float(rule["threshold"])
            if rule["operator"] == "ge"
            else value < float(rule["threshold"])
        )
        checks[metric_name] = {
            "passed": bool(passed),
            "observed": value,
            "operator": rule["operator"],
            "threshold": float(rule["threshold"]),
            "reason": None if passed else "threshold_not_met",
        }

    return {
        "schema_version": current_contract["schema_version"],
        "gate": gate_name,
        "passed": all(check["passed"] for check in checks.values()),
        "checks": checks,
    }


def evaluate_delivery_line(
    observed_metrics: Mapping[str, float],
    delivery_line: str,
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    current_contract = (
        dict(contract) if contract is not None else load_delivery_contract()
    )
    validate_delivery_contract(current_contract)
    lines = current_contract["delivery_lines"]
    if delivery_line not in lines:
        raise ValueError(f"unknown delivery line: {delivery_line}")
    gate_name = lines[delivery_line]["required_safety_gate"]
    result = evaluate_acceptance_gate(
        observed_metrics,
        gate_name,
        contract=current_contract,
    )
    result["delivery_line"] = delivery_line
    return result
