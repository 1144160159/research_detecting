from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from summarize_paired_confirmation import (
    METRICS,
    REQUIRED_ARTIFACTS,
    aggregate,
    markdown,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confirm a frozen fixed-risk report on fully held-out seeds"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-scenarios", type=int, default=14)
    parser.add_argument(
        "--expected-reference-risk", default="cauchy_modality_support_union"
    )
    parser.add_argument(
        "--expected-risk-policy",
        default="confirmed_cauchy_modality_union_v1_edge_external_fusion_holdout",
    )
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    return parser.parse_args()


def validate_manifest(path: Path) -> dict[str, object]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    recorded = manifest.get("manifest_sha256")
    if not isinstance(recorded, str):
        raise ValueError("selection manifest has no manifest_sha256")
    core = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    actual = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if actual != recorded:
        raise ValueError(
            f"selection manifest hash mismatch: expected={recorded} actual={actual}"
        )
    if manifest.get("status") != "frozen_unconfirmed":
        raise ValueError("selection manifest is not frozen_unconfirmed")
    if manifest.get("development_candidate_screening_uses_test_unknown_labels") is not True:
        raise ValueError("selection manifest does not disclose development screening")
    if manifest.get("candidate_runtime_selection_uses_unknown_or_test_labels") is not False:
        raise ValueError("candidate runtime label boundary is invalid")
    seeds = manifest.get("confirmation_seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("selection manifest has no confirmation seeds")
    if set(seeds) & set(manifest.get("development_seeds", [])):
        raise ValueError("development and confirmation seeds overlap")
    return manifest


def task_key(path: Path, root: Path) -> tuple[str, str, int]:
    relative = path.relative_to(root)
    if len(relative.parts) != 3 or relative.name != "metrics.json":
        raise ValueError(f"unexpected metrics path: {path}")
    suite, run = relative.parts[:2]
    if "_seed" not in run:
        raise ValueError(f"run directory has no seed suffix: {path.parent}")
    scenario, seed_text = run.rsplit("_seed", 1)
    return suite, scenario, int(seed_text)


def normalized_report(report: object, label: str, key: tuple[str, str, int]) -> dict[str, float]:
    if not isinstance(report, dict):
        raise ValueError(f"missing {label} report for {key}")
    missing = [metric for metric in METRICS if metric not in report]
    if missing:
        raise ValueError(f"{label} report for {key} misses metrics {missing}")
    return {metric: float(report[metric]) for metric in METRICS}


def load_confirmation_rows(
    root: Path,
    manifest: dict[str, object],
    expected_scenarios: int,
    expected_reference_risk: str,
    expected_risk_policy: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    candidate = str(manifest["selected_candidate"])
    seeds = {int(seed) for seed in manifest["confirmation_seeds"]}
    rows: list[dict[str, object]] = []
    grouped: dict[tuple[str, str], set[int]] = defaultdict(set)
    for path in sorted(root.glob("*/*/metrics.json")):
        key = task_key(path, root)
        suite, scenario, seed = key
        if seed not in seeds:
            raise ValueError(f"unexpected confirmation seed {seed} for {key}")
        missing_artifacts = [
            name for name in REQUIRED_ARTIFACTS if not (path.parent / name).exists()
        ]
        if missing_artifacts:
            raise ValueError(f"missing artifacts for {key}: {missing_artifacts}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("risk_policy") != expected_risk_policy:
            raise ValueError(f"risk policy mismatch for {key}")
        if payload.get("selected_risk") != expected_reference_risk:
            raise ValueError(f"reference selected risk mismatch for {key}")
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"reference runtime leakage guard failed for {key}")
        fingerprint = (
            payload.get("split_metadata", {})
            .get("split_fingerprint", {})
            .get("combined")
        )
        if not fingerprint:
            raise ValueError(f"missing split fingerprint for {key}")
        reports = payload.get("reports", {})
        candidate_report = normalized_report(reports.get(candidate), candidate, key)
        reference_report = normalized_report(
            reports.get(expected_reference_risk), expected_reference_risk, key
        )
        selected_report = normalized_report(
            payload.get("selected_report"), "selected", key
        )
        if any(
            not np.isclose(selected_report[metric], reference_report[metric], atol=1e-12)
            for metric in METRICS
        ):
            raise ValueError(f"selected report mismatch for {key}")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": candidate,
                "reference_selected": expected_reference_risk,
                "candidate_report": candidate_report,
                "reference_report": reference_report,
                "split_fingerprint": str(fingerprint),
            }
        )
        grouped[(suite, scenario)].add(seed)

    if len(grouped) != expected_scenarios:
        raise ValueError(
            f"scenario coverage mismatch: expected {expected_scenarios}, "
            f"found {len(grouped)}"
        )
    mismatched = {
        f"{suite}/{scenario}": sorted(values)
        for (suite, scenario), values in grouped.items()
        if values != seeds
    }
    if mismatched:
        raise ValueError(
            f"seed coverage mismatch: expected {sorted(seeds)}, observed {mismatched}"
        )
    expected_runs = expected_scenarios * len(seeds)
    if len(rows) != expected_runs:
        raise ValueError(
            f"run coverage mismatch: expected {expected_runs}, found {len(rows)}"
        )
    return rows, {
        "paired_tasks": len(rows),
        "expected_seeds": sorted(seeds),
        "expected_scenarios": expected_scenarios,
        "task_sets_identical": True,
        "split_fingerprint_pair_checks": len(rows),
        "split_fingerprints_identical": True,
        "candidate_selection_uses_unknown_or_test_labels": False,
        "candidate_was_frozen_before_confirmation": True,
        "candidate_report_extracted_from_same_model_run": True,
        "required_artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
    }


def main() -> None:
    args = parse_arguments()
    manifest = validate_manifest(Path(args.selection_manifest))
    rows, validation = load_confirmation_rows(
        Path(args.root),
        manifest,
        args.expected_scenarios,
        args.expected_reference_risk,
        args.expected_risk_policy,
    )
    report = {
        "schema_version": "fixed_report_candidate_confirmation_v1",
        "reference_root": args.root,
        "candidate_root": args.root,
        "selection_manifest": args.selection_manifest,
        "selection_manifest_sha256": manifest["manifest_sha256"],
        "candidate_status_before_confirmation": manifest["status"],
        "validation": validation,
        "scenario_blocked_inference": aggregate(
            rows, args.bootstrap_repetitions, args.bootstrap_seed
        ),
        "runs": rows,
    }
    report["confirmation_status"] = (
        "confirmed"
        if report["scenario_blocked_inference"]["decision"][
            "confirmatory_evidence_passes"
        ]
        else "not_confirmed"
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "confirmation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "confirmation.md").write_text(markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "confirmation_status": report["confirmation_status"],
                "validation": validation,
                "decision": report["scenario_blocked_inference"]["decision"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
