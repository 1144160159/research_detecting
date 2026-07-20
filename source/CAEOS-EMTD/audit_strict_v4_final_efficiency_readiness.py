from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Optional


LOADABLE_MODEL_NAMES = ("model.pt", "model.pkl", "model.joblib")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_metrics(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"metrics root is not an object: {path}")
    return payload


def audit_method(
    name: str,
    root: Path,
    expected_runs: int,
    model_filter: Optional[str] = None,
) -> dict[str, Any]:
    selected: list[Path] = []
    issues: list[str] = []
    for metrics_path in sorted(root.glob("**/metrics.json")):
        try:
            metrics = _read_metrics(metrics_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            issues.append(str(error))
            continue
        if model_filter is not None and not (
            metrics.get("model") == model_filter
            or metrics.get("method") == model_filter
        ):
            continue
        selected.append(metrics_path)

    artifact_counts = {name: 0 for name in LOADABLE_MODEL_NAMES}
    loadable_runs = 0
    missing_examples: list[str] = []
    for metrics_path in selected:
        present = [
            artifact
            for artifact in LOADABLE_MODEL_NAMES
            if (metrics_path.parent / artifact).is_file()
            and (metrics_path.parent / artifact).stat().st_size > 0
        ]
        for artifact in present:
            artifact_counts[artifact] += 1
        if present:
            loadable_runs += 1
        elif len(missing_examples) < 10:
            missing_examples.append(str(metrics_path.parent))

    failures = len(list(root.glob("**/failure.json")))
    run_coverage_complete = len(selected) == expected_runs and failures == 0
    saved_artifact_coverage_complete = (
        run_coverage_complete and loadable_runs == expected_runs
    )
    return {
        "name": name,
        "root": str(root),
        "model_filter": model_filter,
        "expected_runs": expected_runs,
        "observed_runs": len(selected),
        "failure_count": failures,
        "run_coverage_complete": run_coverage_complete,
        "loadable_model_artifact_names": list(LOADABLE_MODEL_NAMES),
        "artifact_counts": artifact_counts,
        "runs_with_loadable_model": loadable_runs,
        "saved_artifact_coverage_complete": saved_artifact_coverage_complete,
        "missing_artifact_examples": missing_examples,
        "issues": issues,
    }


def build_readiness(
    protocol: dict[str, Any], candidate: dict[str, Any], comparator: dict[str, Any]
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_final_efficiency_protocol_v1":
        raise ValueError("unexpected final efficiency protocol schema")
    inference = protocol.get("inference_benchmark", {})
    saved_only = inference.get("saved_artifacts_only_no_refit") is True
    gates = {
        "protocol_requires_saved_artifacts_only": saved_only,
        "candidate_run_coverage_complete": candidate["run_coverage_complete"],
        "comparator_run_coverage_complete": comparator["run_coverage_complete"],
        "candidate_saved_artifact_coverage_complete": candidate[
            "saved_artifact_coverage_complete"
        ],
        "comparator_saved_artifact_coverage_complete": comparator[
            "saved_artifact_coverage_complete"
        ],
    }
    executable = (
        saved_only
        and gates["candidate_run_coverage_complete"]
        and gates["comparator_run_coverage_complete"]
        and gates["candidate_saved_artifact_coverage_complete"]
        and gates["comparator_saved_artifact_coverage_complete"]
    )
    blockers: list[str] = []
    if saved_only and not candidate["saved_artifact_coverage_complete"]:
        blockers.append(
            "candidate runs do not contain loadable per-scenario model artifacts"
        )
    if saved_only and not comparator["saved_artifact_coverage_complete"]:
        blockers.append(
            "comparator runs do not contain loadable per-scenario model artifacts"
        )
    if not candidate["run_coverage_complete"]:
        blockers.append("candidate run coverage is incomplete")
    if not comparator["run_coverage_complete"]:
        blockers.append("comparator run coverage is incomplete")
    return {
        "schema_version": "strict_v4_final_efficiency_execution_readiness_v1",
        "scope": "read_only_saved_artifact_execution_check",
        "protocol_manifest_sha256": protocol.get("manifest_sha256"),
        "methods": {"candidate": candidate, "comparator": comparator},
        "execution_gates": gates,
        "v1_protocol_executable": executable,
        "direct_efficiency_claim_allowed": False,
        "blockers": blockers,
        "required_resolution": (
            []
            if executable
            else [
                "wait for the frozen optimal self-algorithm decision",
                "freeze a result-free v2 amendment bound to the selected branch",
                "instrument controlled deterministic replay so training, calibration, and full inference are timed with identical semantics",
                "retain the v1 protocol and this readiness audit as methodology history",
            ]
        ),
        "claim_rule": (
            "Do not time scores.npz post-processing as model inference. No direct "
            "efficiency comparison is allowed until an executable post-selection "
            "protocol produces complete same-hardware evidence."
        ),
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 final efficiency execution readiness",
        "",
        f"Protocol v1 executable: `{'YES' if report['v1_protocol_executable'] else 'NO'}`.",
        f"Direct efficiency claim allowed: `{'YES' if report['direct_efficiency_claim_allowed'] else 'NO'}`.",
        "",
        "| Method | Runs | Loadable models | Saved-artifact gate |",
        "|---|---:|---:|---:|",
    ]
    for method in ("candidate", "comparator"):
        item = report["methods"][method]
        lines.append(
            f"| {item['name']} | {item['observed_runs']}/{item['expected_runs']} | "
            f"{item['runs_with_loadable_model']}/{item['expected_runs']} | "
            f"{'PASS' if item['saved_artifact_coverage_complete'] else 'FAIL'} |"
        )
    if report["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {item}" for item in report["blockers"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--comparator-root", type=Path, required=True)
    parser.add_argument("--candidate-expected", type=int, default=102)
    parser.add_argument("--comparator-expected", type=int, default=102)
    parser.add_argument("--candidate-model-filter")
    parser.add_argument("--comparator-model-filter", default="opendetect")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    report = build_readiness(
        protocol,
        audit_method(
            "pairwise_candidate_source_seed7",
            args.candidate_root,
            args.candidate_expected,
            args.candidate_model_filter,
        ),
        audit_method(
            "opendetect_source",
            args.comparator_root,
            args.comparator_expected,
            args.comparator_model_filter,
        ),
    )
    report["audit_implementation_sha256"] = file_hash(Path(__file__))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "readiness.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "readiness.md").write_text(
        render(report), encoding="utf-8"
    )
    print(render(report), end="")


if __name__ == "__main__":
    main()
