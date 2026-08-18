from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


OPERATIONAL_GATES = {
    "alert_accuracy": ("minimum", 0.95),
    "alert_precision": ("minimum", 0.95),
    "attack_recall": ("minimum", 0.95),
    "benign_fpr": ("strict_maximum", 0.05),
    "known_attack_type_accuracy": ("minimum", 0.95),
    "unknown_attack_alert_recall": ("minimum", 0.95),
    "unknown_label_recall": ("minimum", 0.95),
}
PAPER_GATES = {
    "known_macro_f1": ("minimum", 0.95),
    "unknown_auroc": ("minimum", 0.95),
    "unknown_aupr": ("minimum", 0.95),
    "unknown_fpr95": ("strict_maximum", 0.05),
    "oscr": ("minimum", 0.90),
}


def gate(value: float, kind: str, threshold: float) -> bool:
    if kind == "minimum":
        return value >= threshold
    if kind == "strict_maximum":
        return value < threshold
    raise ValueError(f"unknown gate kind: {kind}")


def aggregate(
    protocol: dict[str, Any],
    reports: list[dict[str, Any]],
    completion: dict[str, Any],
) -> dict[str, Any]:
    expected = protocol["protocol"]["expected_task_count"]
    if len(reports) != expected:
        raise ValueError(f"found {len(reports)} reports, expected {expected}")
    operational_values = {
        metric: np.asarray(
            [report["operational_95_5"][metric] for report in reports],
            dtype=np.float64,
        )
        for metric in OPERATIONAL_GATES
    }
    paper_values = {
        metric: np.asarray(
            [report["three_layer_metrics"][metric] for report in reports],
            dtype=np.float64,
        )
        for metric in PAPER_GATES
    }
    scenario_gates = []
    for report in reports:
        operational_pass = {
            metric: gate(
                float(report["operational_95_5"][metric]), kind, threshold
            )
            for metric, (kind, threshold) in OPERATIONAL_GATES.items()
        }
        paper_pass = {
            metric: gate(
                float(report["three_layer_metrics"][metric]),
                kind,
                threshold,
            )
            for metric, (kind, threshold) in PAPER_GATES.items()
        }
        scenario_gates.append(
            {
                "unknown_family": report["unknown_family"],
                "operational": operational_pass,
                "paper": paper_pass,
                "engineering_full_pass": all(operational_pass.values()),
                "paper_full_pass": (
                    all(operational_pass.values())
                    and all(paper_pass.values())
                ),
            }
        )
    gpu_mean = float(
        completion["resource_summary"]["gpu_utilization_mean_percent"]
    )
    gpu_minimum_pass = gpu_mean >= float(
        protocol["execution"]["minimum_end_to_end_gpu_mean_percent"]
    )
    gpu_preferred_pass = gpu_mean >= float(
        protocol["execution"]["preferred_end_to_end_gpu_mean_percent"]
    )
    engineering_pass = (
        gpu_minimum_pass
        and all(item["engineering_full_pass"] for item in scenario_gates)
    )
    paper_pass = (
        gpu_minimum_pass
        and all(item["paper_full_pass"] for item in scenario_gates)
    )
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_development_evaluation_v1"
        ),
        "state": (
            "development_full_gate_passed"
            if engineering_pass and paper_pass
            else "development_gate_not_met"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "task_count": len(reports),
        "unknown_families": [
            report["unknown_family"] for report in reports
        ],
        "operational_95_5": {
            metric: {
                "mean": float(values.mean()),
                "worst": (
                    float(values.max())
                    if OPERATIONAL_GATES[metric][0] == "strict_maximum"
                    else float(values.min())
                ),
            }
            for metric, values in operational_values.items()
        },
        "paper_open_set": {
            metric: {
                "mean": float(values.mean()),
                "worst": (
                    float(values.max())
                    if PAPER_GATES[metric][0] == "strict_maximum"
                    else float(values.min())
                ),
            }
            for metric, values in paper_values.items()
        },
        "scenario_gates": scenario_gates,
        "resource_gate": {
            "gpu_utilization_mean_percent": gpu_mean,
            "minimum_50_percent_pass": gpu_minimum_pass,
            "preferred_80_percent_pass": gpu_preferred_pass,
        },
        "engineering_delivery_gate_pass": engineering_pass,
        "paper_delivery_gate_pass": paper_pass,
        "confirmation_seed_access": (
            "permitted"
            if engineering_pass and paper_pass
            else "forbidden"
        ),
        "task_manifest_sha256": {
            report["unknown_family"]: report["manifest_sha256"]
            for report in reports
        },
        "claim_boundary": {
            "development_effects_only": True,
            "confirmation_metrics_generated": False,
            "sota_claim_permitted": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    completion = json.loads(args.completion.read_text(encoding="utf-8"))
    reports = []
    for unknown_family in protocol["protocol"]["unknown_families"]:
        path = args.run_root / unknown_family.lower() / "metrics.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        if report["cache"]["sha256"] != protocol["cache"]["sha256"]:
            raise ValueError(f"{path} cache hash differs from protocol")
        reports.append(report)
    result = aggregate(protocol, reports, completion)
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
