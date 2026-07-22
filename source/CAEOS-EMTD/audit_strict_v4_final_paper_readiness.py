from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def efficiency_superiority(summary: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    native = summary["inference"]["native_primary"]["by_batch_size"]
    for batch, payload in native.items():
        paired = payload["paired"]
        for metric in ("latency_p50_ms", "latency_p95_ms", "latency_p99_ms"):
            checks[f"native_batch{batch}_{metric}_upper_ci_le_1"] = (
                float(paired[metric]["bootstrap_95ci"][1]) <= 1.0
            )
        checks[f"native_batch{batch}_throughput_lower_ci_ge_1"] = (
            float(paired["samples_per_second"]["bootstrap_95ci"][0]) >= 1.0
        )
    training = summary["training"]["paired_candidate_over_comparator"]
    for metric in ("total_fit_seconds", "deployment_artifact_bytes", "peak_host_rss_mb"):
        checks[f"training_{metric}_upper_ci_le_1"] = (
            float(training[metric]["bootstrap_95ci"][1]) <= 1.0
        )
    return {"checks": checks, "passes": all(checks.values())}


def render(audit: dict[str, Any]) -> str:
    gates = audit["gates"]
    lines = [
        "# Strict-v4 final paper readiness audit",
        "",
        f"Claim tier: `{audit['claim_tier']}`.",
        "",
        "| Gate | Result |",
        "|---|---|",
    ]
    for name, value in gates.items():
        lines.append(f"| {name} | {'PASS' if value else 'FAIL'} |")
    lines.extend(
        [
            "",
            "Accuracy SOTA, efficiency superiority, graceful degradation, and comparative robustness are separate claims.",
            "Candidate-only corruption degradation cannot establish robustness SOTA against OpenDetect.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accuracy-audit", type=Path, required=True)
    parser.add_argument("--efficiency-summary", type=Path, required=True)
    parser.add_argument("--corruption-summary", type=Path, required=True)
    parser.add_argument("--comparative-corruption-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    accuracy = load_json(args.accuracy_audit)
    efficiency = load_json(args.efficiency_summary)
    corruption = load_json(args.corruption_summary)
    comparative = load_json(args.comparative_corruption_summary)
    if accuracy.get("schema_version") != "strict_v4_comprehensive_sota_audit_v11":
        raise ValueError("unexpected comprehensive accuracy audit schema")
    if (
        efficiency.get("schema_version") != "strict_v4_final_efficiency_summary_v2"
        or efficiency.get("manifest_sha256") != canonical_hash(efficiency)
        or efficiency.get("gates", {}).get("formal_efficiency_claim_allowed") is not True
    ):
        raise ValueError("formal efficiency summary validation failed")
    if (
        corruption.get("schema_version")
        != "strict_v4_postselection_corruption_summary_v1"
        or corruption.get("manifest_sha256") != canonical_hash(corruption)
        or corruption.get("validation", {}).get("passes") is not True
    ):
        raise ValueError("post-selection corruption summary validation failed")
    if (
        comparative.get("schema_version")
        != "strict_v4_comparative_corruption_summary_v1"
        or comparative.get("manifest_sha256") != canonical_hash(comparative)
        or comparative.get("validation", {}).get("passes") is not True
    ):
        raise ValueError("comparative corruption summary validation failed")
    efficiency_gate = efficiency_superiority(efficiency)
    gates = {
        "confirmed_external_accuracy_sota_7_datasets_102_scenarios": accuracy.get(
            "strict_v4_confirmed_external_sota_allowed"
        )
        is True,
        "formal_same_hardware_efficiency_characterized": True,
        "efficiency_superiority_all_required_native_metrics": efficiency_gate["passes"],
        "candidate_graceful_degradation_gate": corruption.get(
            "confirmatory_gate", {}
        ).get("passes")
        is True,
        "comparative_corruption_robustness_against_opendetect": comparative.get(
            "comparative_robustness_gate", {}
        ).get("passes")
        is True,
    }
    multidimensional = all(gates.values())
    accuracy_allowed = gates[
        "confirmed_external_accuracy_sota_7_datasets_102_scenarios"
    ]
    claim_tier = (
        "multidimensional_comprehensive_sota"
        if multidimensional
        else (
            "confirmed_external_accuracy_sota_with_measured_system_tradeoffs"
            if accuracy_allowed
            else "development_complete_confirmatory_accuracy_sota_not_established"
        )
    )
    audit = {
        "schema_version": "strict_v4_final_paper_readiness_audit_v1",
        "status": "complete",
        "input_file_sha256": {
            "accuracy_audit": file_hash(args.accuracy_audit),
            "efficiency_summary": file_hash(args.efficiency_summary),
            "corruption_summary": file_hash(args.corruption_summary),
            "comparative_corruption_summary": file_hash(
                args.comparative_corruption_summary
            ),
        },
        "audit_implementation_sha256": file_hash(Path(__file__)),
        "selected_algorithm": accuracy.get("selected_algorithm"),
        "efficiency_superiority": efficiency_gate,
        "gates": gates,
        "multidimensional_comprehensive_sota_allowed": multidimensional,
        "claim_tier": claim_tier,
        "required_follow_up_if_comprehensive_claim_is_desired": [
            "report every failed multidimensional gate as a negative result",
            "do not tune algorithms or corruption conditions after seeing comparative results",
            "retain metric-specific efficiency tradeoffs if any native efficiency gate fails",
        ],
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "audit.md").write_text(render(audit), encoding="utf-8")
    (args.output_dir / "audit_complete").touch()
    print(render(audit), end="")


if __name__ == "__main__":
    main()
