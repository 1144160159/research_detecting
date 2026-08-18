from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_pcap_multimodal_counterfactual_pair_protocol import (
    load_development_protocol,
    manifest_matches,
)
from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


PAIR_SCHEMA = "strict_v4_pcap_multimodal_counterfactual_pair_protocol_v1"
COMPLETION_SCHEMA = "strict_v4_pcap_multimodal_development_completion_v1"
EVALUATION_SCHEMA = "strict_v4_pcap_multimodal_development_evaluation_v1"


def load_bound_json(
    path: Path,
    *,
    schema: str,
    description: str,
) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {description} schema: {path}")
    if not manifest_matches(payload):
        raise ValueError(f"{description} manifest mismatch: {path}")
    return payload


def load_method(
    pair: dict[str, Any],
    role: str,
) -> dict[str, Any]:
    binding = pair["methods"][role]
    protocol_path = Path(binding["protocol_path"])
    if file_hash(protocol_path) != binding["protocol_file_sha256"]:
        raise ValueError(f"{role} protocol file hash mismatch")
    protocol = load_development_protocol(protocol_path)
    if protocol["manifest_sha256"] != binding["protocol_manifest_sha256"]:
        raise ValueError(f"{role} protocol manifest binding mismatch")

    result_root = Path(binding["result_root"])
    completion_path = result_root / "completion.json"
    evaluation_path = result_root / "evaluation.json"
    completion = load_bound_json(
        completion_path,
        schema=COMPLETION_SCHEMA,
        description=f"{role} completion",
    )
    evaluation = load_bound_json(
        evaluation_path,
        schema=EVALUATION_SCHEMA,
        description=f"{role} evaluation",
    )
    if completion.get("state") != "completed" or completion.get("failures"):
        raise ValueError(f"{role} experiment is not complete")
    if completion["protocol_file_sha256"] != binding[
        "protocol_file_sha256"
    ]:
        raise ValueError(f"{role} completion protocol file hash mismatch")
    for payload in (completion, evaluation):
        if payload["protocol_manifest_sha256"] != binding[
            "protocol_manifest_sha256"
        ]:
            raise ValueError(f"{role} result protocol manifest mismatch")
    expected_families = pair["pairing_contract"]["unknown_families"]
    if int(completion["task_count"]) != len(expected_families):
        raise ValueError(f"{role} completion task count mismatch")
    if int(evaluation["task_count"]) != len(expected_families):
        raise ValueError(f"{role} evaluation task count mismatch")

    reports: dict[str, dict[str, Any]] = {}
    run_root = Path(binding["run_root"])
    for family in expected_families:
        metric_path = run_root / family.lower() / "metrics.json"
        if file_hash(metric_path) != completion["task_metric_sha256"][family]:
            raise ValueError(f"{role}/{family} metric hash mismatch")
        report = json.loads(metric_path.read_text(encoding="utf-8"))
        if not manifest_matches(report):
            raise ValueError(f"{role}/{family} metric manifest mismatch")
        if report.get("state") != "completed":
            raise ValueError(f"{role}/{family} task is not completed")
        if report.get("unknown_family") != family:
            raise ValueError(f"{role}/{family} task family mismatch")
        if int(report.get("seed")) != int(
            pair["pairing_contract"]["development_seed"]
        ):
            raise ValueError(f"{role}/{family} seed mismatch")
        reports[family] = report
    return {
        "protocol": protocol,
        "completion": completion,
        "evaluation": evaluation,
        "reports": reports,
        "artifacts": {
            "completion_path": str(completion_path),
            "completion_file_sha256": file_hash(completion_path),
            "completion_manifest_sha256": completion["manifest_sha256"],
            "evaluation_path": str(evaluation_path),
            "evaluation_file_sha256": file_hash(evaluation_path),
            "evaluation_manifest_sha256": evaluation["manifest_sha256"],
        },
    }


def evaluate_pair(pair: dict[str, Any]) -> dict[str, Any]:
    if pair.get("schema_version") != PAIR_SCHEMA:
        raise ValueError("unexpected counterfactual pair protocol schema")
    if pair.get("state") != "frozen_before_paired_development_effects":
        raise ValueError("counterfactual pair protocol is not frozen")
    if not manifest_matches(pair):
        raise ValueError("counterfactual pair protocol manifest mismatch")
    base = load_method(pair, "base")
    candidate = load_method(pair, "candidate")

    base_paper = base["evaluation"]["paper_open_set"]
    candidate_paper = candidate["evaluation"]["paper_open_set"]
    comparison = {
        "mean_unknown_auroc_gain": (
            candidate_paper["unknown_auroc"]["mean"]
            - base_paper["unknown_auroc"]["mean"]
        ),
        "worst_unknown_auroc_gain": (
            candidate_paper["unknown_auroc"]["worst"]
            - base_paper["unknown_auroc"]["worst"]
        ),
        "mean_unknown_aupr_gain": (
            candidate_paper["unknown_aupr"]["mean"]
            - base_paper["unknown_aupr"]["mean"]
        ),
        "mean_unknown_fpr95_reduction": (
            base_paper["unknown_fpr95"]["mean"]
            - candidate_paper["unknown_fpr95"]["mean"]
        ),
        "mean_oscr_gain": (
            candidate_paper["oscr"]["mean"]
            - base_paper["oscr"]["mean"]
        ),
        "mean_known_macro_f1_gain": (
            candidate_paper["known_macro_f1"]["mean"]
            - base_paper["known_macro_f1"]["mean"]
        ),
        "worst_known_macro_f1_gain": (
            candidate_paper["known_macro_f1"]["worst"]
            - base_paper["known_macro_f1"]["worst"]
        ),
        "dos_unknown_auroc_gain": (
            candidate["reports"]["DoS"]["three_layer_metrics"][
                "unknown_auroc"
            ]
            - base["reports"]["DoS"]["three_layer_metrics"][
                "unknown_auroc"
            ]
        ),
    }
    comparison = {name: float(value) for name, value in comparison.items()}
    gate = pair["development_gate"]
    base_gpu = float(
        base["completion"]["resource_summary"][
            "gpu_utilization_mean_percent"
        ]
    )
    candidate_gpu = float(
        candidate["completion"]["resource_summary"][
            "gpu_utilization_mean_percent"
        ]
    )
    minimum_gpu = float(
        gate["both_gpu_utilization_mean_minimum_percent"]
    )
    preferred_gpu = float(
        gate["preferred_gpu_utilization_mean_percent"]
    )
    checks = {
        "mean_unknown_auroc_gain_strictly_positive": (
            comparison["mean_unknown_auroc_gain"]
            > float(gate["mean_unknown_auroc_gain_strictly_positive"])
        ),
        "worst_unknown_auroc_gain_strictly_positive": (
            comparison["worst_unknown_auroc_gain"]
            > float(gate["worst_unknown_auroc_gain_strictly_positive"])
        ),
        "mean_unknown_aupr_gain_strictly_positive": (
            comparison["mean_unknown_aupr_gain"]
            > float(gate["mean_unknown_aupr_gain_strictly_positive"])
        ),
        "mean_unknown_fpr95_reduction_strictly_positive": (
            comparison["mean_unknown_fpr95_reduction"]
            > float(
                gate[
                    "mean_unknown_fpr95_reduction_strictly_positive"
                ]
            )
        ),
        "mean_oscr_gain_strictly_positive": (
            comparison["mean_oscr_gain"]
            > float(gate["mean_oscr_gain_strictly_positive"])
        ),
        "dos_unknown_auroc_gain_minimum": (
            comparison["dos_unknown_auroc_gain"]
            >= float(gate["dos_unknown_auroc_gain_minimum"])
        ),
        "mean_known_macro_f1_gain_minimum": (
            comparison["mean_known_macro_f1_gain"]
            >= float(gate["mean_known_macro_f1_gain_minimum"])
        ),
        "worst_known_macro_f1_gain_minimum": (
            comparison["worst_known_macro_f1_gain"]
            >= float(gate["worst_known_macro_f1_gain_minimum"])
        ),
        "both_gpu_utilization_mean_minimum_percent": (
            base_gpu >= minimum_gpu and candidate_gpu >= minimum_gpu
        ),
    }
    passes = all(checks.values())
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_counterfactual_pair_evaluation_v1"
        ),
        "state": (
            "candidate_qualified_for_reserved_seed_design"
            if passes
            else "candidate_rejected_at_paired_development_gate"
        ),
        "pair_protocol_manifest_sha256": pair["manifest_sha256"],
        "development_seed": pair["pairing_contract"]["development_seed"],
        "comparison": comparison,
        "checks": checks,
        "passes": passes,
        "resource": {
            "base_gpu_utilization_mean_percent": base_gpu,
            "candidate_gpu_utilization_mean_percent": candidate_gpu,
            "minimum_50_percent_pass": (
                base_gpu >= minimum_gpu and candidate_gpu >= minimum_gpu
            ),
            "base_preferred_80_percent_pass": base_gpu >= preferred_gpu,
            "candidate_preferred_80_percent_pass": (
                candidate_gpu >= preferred_gpu
            ),
        },
        "candidate_absolute_metrics": {
            "operational_95_5": candidate["evaluation"][
                "operational_95_5"
            ],
            "paper_open_set": candidate_paper,
            "engineering_delivery_gate_pass": candidate["evaluation"][
                "engineering_delivery_gate_pass"
            ],
            "paper_delivery_gate_pass": candidate["evaluation"][
                "paper_delivery_gate_pass"
            ],
        },
        "method_artifacts": {
            "base": base["artifacts"],
            "candidate": candidate["artifacts"],
        },
        "claim_boundary": {
            "paired_development_only": True,
            "unknown_metrics_used_after_both_methods_completed": True,
            "loss_weights_changed_after_result_access": False,
            "sota_claim_permitted": False,
            "reserved_confirmation_executed": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite pair evaluation: {output}")
    pair = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = evaluate_pair(pair)
    atomic_json(output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
