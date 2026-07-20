from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from summarize_paired_confirmation import METRICS, aggregate


REFERENCE = "cauchy_modality_support_union"
ENTROPY = "entropy"
FUSION = "rank_union"


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(path: Path) -> dict[str, object]:
    manifest = read_object(path)
    recorded = manifest.get("manifest_sha256")
    core = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    actual = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if recorded != actual:
        raise ValueError(
            f"decision manifest hash mismatch: expected={recorded} actual={actual}"
        )
    if manifest.get("status") != "frozen_unconfirmed":
        raise ValueError("decision manifest is not frozen_unconfirmed")
    candidates = manifest.get("candidates")
    if candidates != {
        "reference": REFERENCE,
        "stage_1": ENTROPY,
        "stage_2": FUSION,
    }:
        raise ValueError("decision manifest candidate chain mismatch")
    if manifest.get("unknown_or_test_labels_used_to_define_this_decision_rule") is not False:
        raise ValueError("decision manifest label-boundary disclosure is invalid")
    return manifest


def confirmation_passes(payload: dict[str, object]) -> bool:
    inference = payload.get("scenario_blocked_inference")
    if not isinstance(inference, dict):
        raise ValueError("confirmation lacks scenario_blocked_inference")
    decision = inference.get("decision")
    if not isinstance(decision, dict):
        raise ValueError("confirmation lacks decision")
    passes = decision.get("confirmatory_evidence_passes")
    if not isinstance(passes, bool):
        raise ValueError("confirmation decision is not Boolean")
    expected_status = "confirmed" if passes else "not_confirmed"
    if payload.get("confirmation_status") != expected_status:
        raise ValueError("confirmation status and decision disagree")
    return passes


def validate_confirmation_header(
    payload: dict[str, object], schema: str, manifest: dict[str, object]
) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"confirmation schema mismatch: expected {schema}")
    if payload.get("candidate_status_before_confirmation") != "frozen_unconfirmed":
        raise ValueError("candidate was not frozen before confirmation")
    validation = payload.get("validation")
    if not isinstance(validation, dict):
        raise ValueError("confirmation validation block is missing")
    scope = manifest["scope"]
    assert isinstance(scope, dict)
    expected_seeds = sorted(int(seed) for seed in scope["confirmation_seeds"])
    required = {
        "paired_tasks": int(scope["scenario_count"]) * len(expected_seeds),
        "expected_seeds": expected_seeds,
        "expected_scenarios": int(scope["scenario_count"]),
        "task_sets_identical": True,
        "split_fingerprints_identical": True,
        "candidate_selection_uses_unknown_or_test_labels": False,
        "candidate_was_frozen_before_confirmation": True,
    }
    for key, expected in required.items():
        if validation.get(key) != expected:
            raise ValueError(
                f"confirmation validation mismatch for {key}: "
                f"expected={expected!r} actual={validation.get(key)!r}"
            )


def task_rows(payload: dict[str, object], label: str) -> dict[tuple[str, str, int], dict[str, object]]:
    rows = payload.get("runs")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{label} confirmation has no rows")
    result: dict[tuple[str, str, int], dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"invalid {label} confirmation row")
        key = (str(row.get("suite")), str(row.get("scenario")), int(row["seed"]))
        if key in result:
            raise ValueError(f"duplicate {label} task: {key}")
        result[key] = row
    return result


def reports_equal(first: object, second: object) -> bool:
    if not isinstance(first, dict) or not isinstance(second, dict):
        return False
    return all(
        metric in first
        and metric in second
        and np.isclose(float(first[metric]), float(second[metric]), atol=1e-12)
        for metric in METRICS
    )


def direct_rows(
    entropy_rows: dict[tuple[str, str, int], dict[str, object]],
    fusion_rows: dict[tuple[str, str, int], dict[str, object]],
    candidate: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key in sorted(entropy_rows):
        entropy_row = entropy_rows[key]
        fusion_row = fusion_rows[key]
        candidate_report = (
            fusion_row["candidate_report"]
            if candidate == FUSION
            else entropy_row["candidate_report"]
        )
        rows.append(
            {
                "suite": key[0],
                "scenario": key[1],
                "seed": key[2],
                "candidate_selected": candidate,
                "reference_selected": REFERENCE,
                "candidate_report": candidate_report,
                "reference_report": entropy_row["reference_report"],
                "split_fingerprint": entropy_row["split_fingerprint"],
            }
        )
    return rows


def build_selection(
    entropy: dict[str, object],
    fusion: dict[str, object],
    manifest: dict[str, object],
    bootstrap_repetitions: int,
    bootstrap_seed: int,
) -> dict[str, object]:
    validate_confirmation_header(
        entropy, "fixed_report_candidate_confirmation_v1", manifest
    )
    validate_confirmation_header(
        fusion, "entropy_cauchy_fusion_confirmation_v1", manifest
    )
    entropy_rows = task_rows(entropy, ENTROPY)
    fusion_rows = task_rows(fusion, FUSION)
    if set(entropy_rows) != set(fusion_rows):
        raise ValueError("entropy and fusion task sets differ")
    for key in entropy_rows:
        first = entropy_rows[key]
        second = fusion_rows[key]
        if first.get("candidate_selected") != ENTROPY or first.get(
            "reference_selected"
        ) != REFERENCE:
            raise ValueError(f"entropy candidate chain mismatch for {key}")
        if second.get("candidate_selected") != FUSION or second.get(
            "reference_selected"
        ) != ENTROPY:
            raise ValueError(f"fusion candidate chain mismatch for {key}")
        if first.get("split_fingerprint") != second.get("split_fingerprint"):
            raise ValueError(f"split fingerprint mismatch for {key}")
        if not reports_equal(first.get("candidate_report"), second.get("reference_report")):
            raise ValueError(f"entropy replay mismatch for {key}")

    entropy_passes = confirmation_passes(entropy)
    fusion_passes = confirmation_passes(fusion)
    fusion_vs_reference = aggregate(
        direct_rows(entropy_rows, fusion_rows, FUSION),
        bootstrap_repetitions,
        bootstrap_seed,
    )
    fusion_direct_passes = bool(
        fusion_vs_reference["decision"]["confirmatory_evidence_passes"]
    )
    if entropy_passes and fusion_passes and fusion_direct_passes:
        selected = FUSION
        reason = "all_three_preregistered_rank_union_gates_passed"
        selected_vs_reference = fusion_vs_reference
    elif entropy_passes:
        selected = ENTROPY
        reason = "entropy_confirmed_but_rank_union_gate_failed"
        selected_vs_reference = entropy["scenario_blocked_inference"]
    else:
        selected = REFERENCE
        reason = "entropy_confirmation_failed_retain_reference"
        selected_vs_reference = None
    return {
        "schema_version": "final_internal_risk_selection_v1",
        "status": "confirmed_frozen",
        "selected_internal_risk": selected,
        "selection_reason": reason,
        "decision_trace": {
            "entropy_vs_reference_passes": entropy_passes,
            "rank_union_vs_entropy_passes": fusion_passes,
            "rank_union_vs_reference_passes": fusion_direct_passes,
        },
        "selected_vs_reference_inference": selected_vs_reference,
        "rank_union_vs_reference_inference": fusion_vs_reference,
        "validated_task_count": len(entropy_rows),
        "scenario_count": int(manifest["scope"]["scenario_count"]),
        "confirmation_seeds": manifest["scope"]["confirmation_seeds"],
        "external_expert_fusion_role": manifest["external_expert_fusion_role"],
    }


def markdown(result: dict[str, object]) -> str:
    trace = result["decision_trace"]
    return "\n".join(
        [
            "# Final internal CAEOS risk selection",
            "",
            f"Selected risk: `{result['selected_internal_risk']}`",
            f"Status: `{result['status']}`",
            f"Reason: `{result['selection_reason']}`",
            "",
            f"- entropy vs reference: `{trace['entropy_vs_reference_passes']}`",
            f"- rank_union vs entropy: `{trace['rank_union_vs_entropy_passes']}`",
            f"- rank_union vs reference: `{trace['rank_union_vs_reference_passes']}`",
            "",
            "External expert fusion remains a separately reported augmentation.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the final internal CAEOS risk")
    parser.add_argument("--entropy-confirmation", required=True)
    parser.add_argument("--fusion-confirmation", required=True)
    parser.add_argument("--decision-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output")
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    args = parser.parse_args()
    entropy_path = Path(args.entropy_confirmation)
    fusion_path = Path(args.fusion_confirmation)
    manifest_path = Path(args.decision_manifest)
    result = build_selection(
        read_object(entropy_path),
        read_object(fusion_path),
        validate_manifest(manifest_path),
        args.bootstrap_repetitions,
        args.bootstrap_seed,
    )
    result["inputs"] = {
        "entropy_confirmation": {"path": str(entropy_path), "sha256": sha256(entropy_path)},
        "fusion_confirmation": {"path": str(fusion_path), "sha256": sha256(fusion_path)},
        "decision_manifest": {"path": str(manifest_path), "sha256": sha256(manifest_path)},
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_path = Path(args.markdown_output) if args.markdown_output else output.with_suffix(".md")
    markdown_path.write_text(markdown(result), encoding="utf-8")
    print(json.dumps(result["decision_trace"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
