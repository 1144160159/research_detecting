from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from project_contract import (
    CONTRACT_PATH,
    evaluate_delivery_line,
    load_delivery_contract,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the CAEOS delivery contract or evaluate a result."
    )
    parser.add_argument("--contract", default=str(CONTRACT_PATH))
    parser.add_argument("--metrics-json")
    parser.add_argument(
        "--delivery-line",
        choices=("engineering", "paper"),
        default="engineering",
    )
    parser.add_argument("--output")
    return parser.parse_args()


def load_metrics(path: str) -> dict[str, float]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value: Any = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("metrics JSON must contain an object")
    return {str(key): float(metric) for key, metric in value.items()}


def main() -> None:
    args = parse_arguments()
    contract = load_delivery_contract(args.contract)
    if args.metrics_json:
        report: dict[str, Any] = evaluate_delivery_line(
            load_metrics(args.metrics_json),
            args.delivery_line,
            contract=contract,
        )
    else:
        report = {
            "schema_version": contract["schema_version"],
            "contract_valid": True,
            "delivery_lines": sorted(contract["delivery_lines"]),
            "metric_layers": list(contract["metric_layers"]),
            "acceptance_gates": sorted(contract["acceptance_gates"]),
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
