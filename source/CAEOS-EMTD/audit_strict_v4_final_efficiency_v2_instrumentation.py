from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return payload


def count_named_files(root: Path, name: str) -> int:
    return len(list(root.rglob(name))) if root.exists() else 0


def pairwise_equivalence_passes(payload: dict[str, Any]) -> bool:
    return bool(
        payload.get("schema_version") == "strict_v4_pairwise_runtime_equivalence_v2"
        and payload.get("passes") is True
        and payload.get("prediction_array_equal") is True
        and float(payload.get("risk_max_absolute_difference", float("inf"))) <= 1e-12
        and float(
            payload.get("component_max_absolute_difference", float("inf"))
        )
        <= 1e-12
        and payload.get("equivalence_mode")
        == "source_components_plus_stable_runtime_shadow"
        and payload.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is False
    )


def diagnostic_opendetect_passes(payload: dict[str, Any]) -> bool:
    return bool(
        payload.get("schema_version") == "strict_v4_opendetect_runtime_equivalence_v1"
        and payload.get("passes") is True
        and payload.get("prediction_array_equal") is True
        and payload.get("device") == "cpu"
        and float(payload.get("risk_max_absolute_difference", float("inf")))
        <= float(payload.get("absolute_tolerance", -1.0))
        and payload.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is False
    )


def formal_shadow_opendetect_passes(payload: dict[str, Any]) -> bool:
    return bool(
        payload.get("schema_version") == "strict_v4_opendetect_runtime_equivalence_v1"
        and payload.get("passes") is True
        and payload.get("prediction_array_equal") is True
        and payload.get("equivalence_mode")
        == "runtime_vs_uninstrumented_same_device_shadow"
        and float(payload.get("risk_max_absolute_difference", float("inf"))) <= 1e-12
        and float(payload.get("absolute_tolerance", float("inf"))) <= 1e-12
        and payload.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is False
    )


def build_audit(
    pairwise_fallback: dict[str, Any],
    pairwise_learned: dict[str, Any],
    opendetect_cpu_diagnostic: dict[str, Any],
    opendetect_same_device_shadow: dict[str, Any] | None = None,
    *,
    external_completed: int,
    external_expected: int,
    formal_efficiency_metrics: int,
    corruption_metrics: int,
    remote_runtime_tests_passed: int,
) -> dict[str, Any]:
    if not 0 <= external_completed <= external_expected:
        raise ValueError("external completion count is invalid")
    pairwise_checks = {
        "fallback_component_and_shadow_equivalence": pairwise_equivalence_passes(
            pairwise_fallback
        ),
        "learned_component_and_shadow_equivalence": pairwise_equivalence_passes(
            pairwise_learned
        ),
    }
    diagnostic_pass = diagnostic_opendetect_passes(opendetect_cpu_diagnostic)
    formal_shadow_pass = bool(
        opendetect_same_device_shadow is not None
        and formal_shadow_opendetect_passes(opendetect_same_device_shadow)
    )
    instrumentation_code_ready = bool(
        all(pairwise_checks.values())
        and diagnostic_pass
        and formal_shadow_pass
        and remote_runtime_tests_passed >= 15
    )
    external_complete = external_completed == external_expected
    result_free = formal_efficiency_metrics == 0
    audit = {
        "schema_version": "strict_v4_final_efficiency_v2_instrumentation_audit_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "external_confirmation": {
            "completed": external_completed,
            "expected": external_expected,
            "complete": external_complete,
        },
        "pairwise_runtime": pairwise_checks,
        "opendetect_runtime": {
            "cpu_cross_device_diagnostic_passes": diagnostic_pass,
            "risk_max_absolute_difference": opendetect_cpu_diagnostic.get(
                "risk_max_absolute_difference"
            ),
            "formal_same_device_equivalence_observed": formal_shadow_pass,
            "formal_same_device_risk_max_absolute_difference": (
                opendetect_same_device_shadow.get("risk_max_absolute_difference")
                if opendetect_same_device_shadow is not None
                else None
            ),
            "formal_same_device_scope": (
                "single_scenario_instrumentation_smoke"
                if formal_shadow_pass
                else "not_observed"
            ),
            "diagnostic_is_formal_evidence": False,
        },
        "verification": {
            "remote_runtime_and_efficiency_tests_passed": remote_runtime_tests_passed,
            "instrumentation_code_ready": instrumentation_code_ready,
        },
        "downstream_counts": {
            "formal_efficiency_metrics": formal_efficiency_metrics,
            "corruption_metrics": corruption_metrics,
        },
        "gates": {
            "protocol_freeze_allowed": external_complete and result_free,
            "formal_execution_allowed": False,
            "efficiency_claim_allowed": False,
            "reason": (
                "wait_for_external_confirmation_then_freeze_protocol_and_run_same_device_shadow"
            ),
        },
    }
    return audit


def render(audit: dict[str, Any]) -> str:
    external = audit["external_confirmation"]
    pairwise = audit["pairwise_runtime"]
    opendetect = audit["opendetect_runtime"]
    verification = audit["verification"]
    downstream = audit["downstream_counts"]
    return "\n".join(
        [
            "# Strict-v4 final efficiency v2 instrumentation audit",
            "",
            f"- External confirmation: `{external['completed']}/{external['expected']}`.",
            f"- Pairwise fallback component/shadow equivalence: `{pairwise['fallback_component_and_shadow_equivalence']}`.",
            f"- Pairwise learned component/shadow equivalence: `{pairwise['learned_component_and_shadow_equivalence']}`.",
            f"- OpenDetect CPU diagnostic: `{opendetect['cpu_cross_device_diagnostic_passes']}`; formal evidence: `False`.",
            f"- OpenDetect same-device strict shadow: `{opendetect['formal_same_device_equivalence_observed']}`; scope: `{opendetect['formal_same_device_scope']}`.",
            f"- Remote tests passed: `{verification['remote_runtime_and_efficiency_tests_passed']}`.",
            f"- Instrumentation code ready: `{verification['instrumentation_code_ready']}`.",
            f"- Formal efficiency metrics: `{downstream['formal_efficiency_metrics']}`.",
            f"- Corruption metrics: `{downstream['corruption_metrics']}`.",
            "- Efficiency claim allowed: `False`.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise-fallback-equivalence", type=Path, required=True)
    parser.add_argument("--pairwise-learned-equivalence", type=Path, required=True)
    parser.add_argument("--opendetect-cpu-equivalence", type=Path, required=True)
    parser.add_argument("--opendetect-same-device-equivalence", type=Path)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--formal-efficiency-root", type=Path, required=True)
    parser.add_argument("--corruption-root", type=Path, required=True)
    parser.add_argument("--external-expected", type=int, default=306)
    parser.add_argument("--remote-tests-passed", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    audit = build_audit(
        load_json(args.pairwise_fallback_equivalence),
        load_json(args.pairwise_learned_equivalence),
        load_json(args.opendetect_cpu_equivalence),
        (
            load_json(args.opendetect_same_device_equivalence)
            if args.opendetect_same_device_equivalence
            else None
        ),
        external_completed=count_named_files(args.external_root, "metrics.json"),
        external_expected=args.external_expected,
        formal_efficiency_metrics=count_named_files(
            args.formal_efficiency_root, "efficiency_metrics.json"
        ),
        corruption_metrics=count_named_files(args.corruption_root, "metrics.json"),
        remote_runtime_tests_passed=args.remote_tests_passed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "audit.md").write_text(render(audit), encoding="utf-8")
    print(render(audit), end="")


if __name__ == "__main__":
    main()
