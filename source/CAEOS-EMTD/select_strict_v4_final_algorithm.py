from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROUTER_METHOD = "caeos_domain_safe_router"
REQUIRED_CHECKS = {
    "all_unknown_metric_means_strictly_positive",
    "auroc_bootstrap_lower_strictly_positive",
    "aupr_bootstrap_lower_strictly_positive",
    "all_unknown_metric_holm_p_below_0_05",
    "all_suite_unknown_metric_means_nonnegative",
    "known_macro_f1_unchanged",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("manifest_sha256", None)
    encoded = json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_schema(payload: dict[str, Any], expected: str, name: str) -> None:
    if payload.get("schema_version") != expected:
        raise ValueError(f"unexpected {name} schema")


def select_final_algorithm(
    router: dict[str, Any],
    protocol: dict[str, Any],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    _require_schema(
        router, "strict_v4_domain_safe_router_candidate_v1", "router"
    )
    _require_schema(
        protocol,
        "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "protocol",
    )
    _require_schema(
        confirmation,
        "strict_v4_domain_safe_router_confirmation_v1",
        "confirmation",
    )
    router_hash = router.get("manifest_sha256")
    protocol_hash = protocol.get("manifest_sha256")
    if not router_hash or not protocol_hash:
        raise ValueError("missing frozen manifest hash")
    if protocol.get("router_manifest_sha256") != router_hash:
        raise ValueError("protocol router binding mismatch")
    if confirmation.get("router_manifest_sha256") != router_hash:
        raise ValueError("confirmation router binding mismatch")
    if confirmation.get("protocol_manifest_sha256") != protocol_hash:
        raise ValueError("confirmation protocol binding mismatch")

    validation = confirmation.get("validation", {})
    expected_seeds = sorted(protocol.get("confirmation_seeds", []))
    if sorted(validation.get("seeds", [])) != expected_seeds:
        raise ValueError("confirmation seed coverage mismatch")
    validation_checks = {
        "validation_passes": validation.get("passes") is True,
        "task_set_complete": validation.get("task_set_complete") is True,
        "confirmation_selection_is_label_free": validation.get(
            "unknown_or_test_labels_used_for_confirmation_selection"
        )
        is False,
    }
    if not all(validation_checks.values()):
        raise ValueError("confirmation validation is incomplete or unsafe")

    decision = confirmation.get("decision", {})
    checks = decision.get("checks", {})
    if set(checks) != REQUIRED_CHECKS:
        raise ValueError("confirmation decision checks do not match frozen gate")
    computed_pass = all(checks.values())
    if decision.get("passes") is not computed_pass:
        raise ValueError("confirmation decision is inconsistent with its checks")

    fallback = router.get("fallback")
    if fallback != "caeos_pairwise":
        raise ValueError("unexpected frozen fallback")
    selected = ROUTER_METHOD if computed_pass else fallback
    result = {
        "schema_version": "strict_v4_final_algorithm_decision_v1",
        "selection_is_pre_registered": True,
        "confirmation_gate_passes": computed_pass,
        "selected_algorithm": selected,
        "status": (
            "frozen_final_self_algorithm"
            if computed_pass
            else "frozen_safe_fallback_pending_next_generation"
        ),
        "next_action": (
            "freeze_and_report_domain_safe_router"
            if computed_pass
            else "develop_suite_conditioned_ranking_head_on_disjoint_data"
        ),
        "router_manifest_sha256": router_hash,
        "protocol_manifest_sha256": protocol_hash,
        "confirmation_decision_checks": dict(sorted(checks.items())),
        "validation_checks": validation_checks,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 final self-algorithm decision",
        "",
        f"Confirmation gate: **{'PASS' if result['confirmation_gate_passes'] else 'FAIL'}**.",
        f"Selected algorithm: `{result['selected_algorithm']}`.",
        f"Status: `{result['status']}`.",
        f"Next action: `{result['next_action']}`.",
        "",
        "## Frozen checks",
        "",
    ]
    for name, passed in result["confirmation_decision_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--protocol-manifest", type=Path, required=True)
    parser.add_argument("--confirmation", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    protocol = json.loads(args.protocol_manifest.read_text(encoding="utf-8"))
    confirmation = json.loads(args.confirmation.read_text(encoding="utf-8"))
    result = select_final_algorithm(router, protocol, confirmation)
    result["router_manifest_file_sha256"] = file_hash(args.router_manifest)
    result["protocol_manifest_file_sha256"] = file_hash(args.protocol_manifest)
    result["confirmation_file_sha256"] = file_hash(args.confirmation)
    result["selector_implementation_sha256"] = file_hash(Path(__file__))
    result["manifest_sha256"] = canonical_hash(result)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "decision.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "decision.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
