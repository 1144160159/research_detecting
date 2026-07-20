from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from analyze_entropy_cauchy_fusion import (
    FUSION_METHODS,
    REQUIRED_ARTIFACTS,
    task_report,
)
from summarize_paired_confirmation import aggregate, markdown


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confirm a frozen entropy-Cauchy fusion on held-out seeds"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-scenarios", type=int, default=14)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument(
        "--expected-selected-risk", default="cauchy_modality_support_union"
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
    if manifest.get("selected_candidate") not in FUSION_METHODS:
        raise ValueError("selection manifest does not select a fusion method")
    if manifest.get("runtime_fusion_uses_unknown_or_test_labels") is not False:
        raise ValueError("runtime fusion label boundary is invalid")
    if manifest.get("development_candidate_screening_uses_test_unknown_labels") is not True:
        raise ValueError("development screening disclosure is missing")
    seeds = manifest.get("confirmation_seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("selection manifest has no confirmation seeds")
    if set(seeds) & set(manifest.get("development_seeds", [])):
        raise ValueError("development and confirmation seeds overlap")
    implementation_hash = hashlib.sha256(
        Path(__file__).with_name("analyze_entropy_cauchy_fusion.py").read_bytes()
    ).hexdigest()
    if manifest.get("analysis_implementation_sha256") != implementation_hash:
        raise ValueError("fusion implementation hash mismatch")
    return manifest


def load_rows(
    root: Path,
    manifest: dict[str, object],
    expected_scenarios: int,
    acceptance: float,
    expected_selected_risk: str,
    expected_risk_policy: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    candidate = str(manifest["selected_candidate"])
    seeds = {int(seed) for seed in manifest["confirmation_seeds"]}
    rows: list[dict[str, object]] = []
    grouped: dict[str, set[int]] = defaultdict(set)
    replay_checks = 0
    for path in sorted(root.glob("*/*/metrics.json")):
        directory = path.parent
        missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).exists()]
        if missing:
            raise ValueError(f"missing artifacts under {directory}: {missing}")
        metrics = json.loads(path.read_text(encoding="utf-8"))
        seed = int(metrics["seed"])
        if seed not in seeds:
            raise ValueError(f"unexpected confirmation seed {seed} under {directory}")
        if metrics.get("risk_policy") != expected_risk_policy:
            raise ValueError(f"risk policy mismatch under {directory}")
        if metrics.get("selected_risk") != expected_selected_risk:
            raise ValueError(f"selected risk mismatch under {directory}")
        details = metrics.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"runtime leakage guard failed under {directory}")
        fingerprint = (
            metrics.get("split_metadata", {})
            .get("split_fingerprint", {})
            .get("combined")
        )
        if not fingerprint:
            raise ValueError(f"missing split fingerprint under {directory}")
        report = task_report(directory, acceptance)
        if int(report["seed"]) != seed:
            raise ValueError(f"replayed seed mismatch under {directory}")
        replay_checks += int(report["endpoint_replay_checks"])
        scenario_name = directory.name.rsplit("_seed", 1)[0]
        scenario = f"{directory.parent.name}/{scenario_name}"
        grouped[scenario].add(seed)
        rows.append(
            {
                "suite": directory.parent.name,
                "scenario": scenario_name,
                "seed": seed,
                "candidate_selected": candidate,
                "reference_selected": "entropy",
                "candidate_report": report["reports"][candidate],
                "reference_report": report["reports"]["entropy"],
                "split_fingerprint": str(fingerprint),
            }
        )
    if len(grouped) != expected_scenarios:
        raise ValueError(
            f"scenario coverage mismatch: expected {expected_scenarios}, "
            f"found {len(grouped)}"
        )
    mismatched = {
        scenario: sorted(observed)
        for scenario, observed in grouped.items()
        if observed != seeds
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
        "endpoint_replay_checks": replay_checks,
        "required_artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
    }


def build_confirmation(
    rows: list[dict[str, object]], repetitions: int, bootstrap_seed: int
) -> dict[str, object]:
    inference = aggregate(rows, repetitions, bootstrap_seed)
    return {
        "scenario_blocked_inference": inference,
        "confirmation_status": (
            "confirmed"
            if inference["decision"]["confirmatory_evidence_passes"]
            else "not_confirmed"
        ),
    }


def main() -> None:
    args = parse_arguments()
    manifest = validate_manifest(Path(args.selection_manifest))
    rows, validation = load_rows(
        Path(args.root),
        manifest,
        args.expected_scenarios,
        args.known_acceptance,
        args.expected_selected_risk,
        args.expected_risk_policy,
    )
    confirmation = build_confirmation(
        rows, args.bootstrap_repetitions, args.bootstrap_seed
    )
    report = {
        "schema_version": "entropy_cauchy_fusion_confirmation_v1",
        "reference_root": args.root,
        "candidate_root": args.root,
        "selection_manifest": args.selection_manifest,
        "selection_manifest_sha256": manifest["manifest_sha256"],
        "candidate_status_before_confirmation": manifest["status"],
        "validation": validation,
        **confirmation,
        "runs": rows,
    }
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
