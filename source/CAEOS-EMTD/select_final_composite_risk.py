from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from confirm_cross_suite_fixed_risk import confirmation_decision, load_manifest


EDGE_SCHEMA = "final_internal_risk_selection_v1"
CONFIRMATION_SCHEMAS = {
    "cross_suite_fixed_report_confirmation_v1",
    "cross_suite_fixed_risk_confirmation_v1",
}
CURRENT_SUITE_RISK = "__current_policy__"
EXPECTED_SUITES = {"nf_cse", "ustc_tfc2016"}


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_edge_selection(payload: dict[str, object]) -> None:
    if payload.get("schema_version") != EDGE_SCHEMA:
        raise ValueError("unexpected Edge selection schema")
    if payload.get("status") != "confirmed_frozen":
        raise ValueError("Edge selection is not confirmed_frozen")
    if int(payload.get("validated_task_count", -1)) != 56:
        raise ValueError("Edge selection does not cover 56 held-out tasks")
    if int(payload.get("scenario_count", -1)) != 14:
        raise ValueError("Edge selection does not cover 14 scenarios")
    if not isinstance(payload.get("selected_internal_risk"), str):
        raise ValueError("Edge selection has no selected risk")


def validate_confirmation(
    payload: dict[str, object], manifest: dict[str, object]
) -> bool:
    schema = payload.get("schema_version")
    if schema not in CONFIRMATION_SCHEMAS:
        raise ValueError(f"unexpected cross-suite confirmation schema: {schema!r}")
    if payload.get("candidate_status_before_confirmation") != "frozen_unconfirmed":
        raise ValueError("cross-suite candidate was not frozen before confirmation")
    if payload.get("selection_manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("cross-suite confirmation manifest hash mismatch")
    if payload.get("selected_suite_risks") != manifest.get("selected_suite_risks"):
        raise ValueError("cross-suite confirmation risks differ from the manifest")

    validation = payload.get("validation")
    if not isinstance(validation, dict):
        raise ValueError("cross-suite confirmation has no validation block")
    expected_seeds = sorted(int(seed) for seed in manifest["confirmation_seeds"])
    required = {
        "paired_tasks": 24 * len(expected_seeds),
        "expected_seeds": expected_seeds,
        "expected_scenarios": 24,
        "reference_selection_uses_unknown_or_test_labels": False,
    }
    for key, expected in required.items():
        if validation.get(key) != expected:
            raise ValueError(
                f"cross-suite validation mismatch for {key}: "
                f"expected={expected!r} actual={validation.get(key)!r}"
            )
    if schema == "cross_suite_fixed_report_confirmation_v1":
        same_run_required = {
            "scenario_count": 24,
            "candidate_reports_extracted_from_same_model_run": True,
            "candidate_thresholds_fitted_on_known_validation": True,
            "candidate_runtime_selection_uses_unknown_or_test_labels": False,
            "required_artifacts_validated_by_load_root": True,
        }
        for key, expected in same_run_required.items():
            if validation.get(key) != expected:
                raise ValueError(f"same-run validation mismatch for {key}")
    else:
        paired_required = {
            "task_sets_identical": True,
            "split_fingerprints_identical": True,
            "candidate_selection_uses_unknown_or_test_labels": False,
        }
        for key, expected in paired_required.items():
            if validation.get(key) != expected:
                raise ValueError(f"paired-run validation mismatch for {key}")

    combined = payload.get("scenario_blocked_inference")
    suites = payload.get("suite_inference")
    if not isinstance(combined, dict) or not isinstance(suites, dict):
        raise ValueError("cross-suite confirmation inference blocks are missing")
    if set(suites) != EXPECTED_SUITES:
        raise ValueError("cross-suite confirmation inference suite coverage mismatch")
    recomputed = confirmation_decision(combined, suites, 0.01)
    decision = payload.get("frozen_confirmation_decision")
    if not isinstance(decision, dict) or not isinstance(decision.get("passes"), bool):
        raise ValueError("cross-suite confirmation decision is not Boolean")
    if decision != recomputed:
        raise ValueError("cross-suite confirmation decision does not match recomputation")
    passes = bool(decision["passes"])
    expected_status = "confirmed" if passes else "not_confirmed"
    if payload.get("confirmation_status") != expected_status:
        raise ValueError("cross-suite confirmation status and decision disagree")
    return passes


def build_selection(
    edge: dict[str, object],
    confirmation: dict[str, object],
    manifest: dict[str, object],
    edge_sha: str,
    confirmation_sha: str,
    manifest_sha: str,
) -> dict[str, object]:
    validate_edge_selection(edge)
    passes = validate_confirmation(confirmation, manifest)
    candidates = manifest["selected_suite_risks"]
    if not isinstance(candidates, dict) or set(candidates) != EXPECTED_SUITES:
        raise ValueError("cross-suite manifest suite coverage mismatch")
    suite_risks = {
        "edge_iiot": str(edge["selected_internal_risk"]),
        "nf_cse": str(candidates["nf_cse"]) if passes else CURRENT_SUITE_RISK,
        "ustc_tfc2016": (
            str(candidates["ustc_tfc2016"]) if passes else CURRENT_SUITE_RISK
        ),
    }
    return {
        "schema_version": "final_composite_risk_selection_v1",
        "status": "confirmed_frozen",
        "suite_risks": suite_risks,
        "cross_suite_candidate_confirmed": passes,
        "selection_reason": (
            "heldout_cross_suite_gate_passed_apply_frozen_suite_risks"
            if passes
            else "heldout_cross_suite_gate_failed_retain_current_suite_risks"
        ),
        "runtime_selection_uses_unknown_or_test_labels": False,
        "runtime_policy": "fixed risk selected only by known dataset suite identity",
        "evidence": {
            "edge_selection_sha256": edge_sha,
            "cross_suite_confirmation_sha256": confirmation_sha,
            "cross_suite_manifest_sha256": manifest_sha,
            "edge_heldout_task_count": 56,
            "cross_suite_heldout_task_count": 96,
            "cross_suite_confirmation_seeds": manifest["confirmation_seeds"],
        },
    }


def markdown(selection: dict[str, object]) -> str:
    risks = selection["suite_risks"]
    assert isinstance(risks, dict)
    lines = [
        "# Final composite CAEOS risk selection",
        "",
        f"Status: `{selection['status']}`",
        f"Reason: `{selection['selection_reason']}`",
        "",
    ]
    lines.extend(f"- {suite}: `{risk}`" for suite, risk in risks.items())
    lines.extend(
        [
            "",
            "Runtime selection uses only the known dataset suite identity and never "
            "unknown or test labels.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze Edge and cross-suite held-out decisions into one policy"
    )
    parser.add_argument("--edge-selection", required=True)
    parser.add_argument("--cross-suite-confirmation", required=True)
    parser.add_argument("--cross-suite-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output")
    args = parser.parse_args()

    edge_path = Path(args.edge_selection)
    confirmation_path = Path(args.cross_suite_confirmation)
    manifest_path = Path(args.cross_suite_manifest)
    edge = read_object(edge_path)
    confirmation = read_object(confirmation_path)
    manifest = load_manifest(manifest_path)
    selection = build_selection(
        edge,
        confirmation,
        manifest,
        sha256(edge_path),
        sha256(confirmation_path),
        sha256(manifest_path),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if args.markdown_output:
        Path(args.markdown_output).write_text(markdown(selection), encoding="utf-8")
    print(json.dumps(selection, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
