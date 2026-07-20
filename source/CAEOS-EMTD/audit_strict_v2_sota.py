from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

from run_nested_gate_matrix import (
    EDGE_IIOT_SCENARIOS,
    NF_CSE_SCENARIOS,
    USTC_TFC2016_SCENARIOS,
)


SCENARIO_MAPS: dict[str, Mapping[str, str]] = {
    "edge_iiot": EDGE_IIOT_SCENARIOS,
    "nf_cse": NF_CSE_SCENARIOS,
    "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit strict-v2 SOTA matrix completeness and provenance"
    )
    parser.add_argument("--gate-root", required=True)
    parser.add_argument(
        "--baseline-root",
        action="append",
        required=True,
        help="name=directory; repeat for each independently run matrix",
    )
    parser.add_argument(
        "--expected-models",
        action="append",
        required=True,
        help="name=model1,model2; name must match --baseline-root",
    )
    parser.add_argument("--seeds", default="7,11,19,23,37")
    parser.add_argument("--output")
    return parser.parse_args()


def parse_seeds(value: str) -> tuple[int, ...]:
    tokens = [token.strip() for token in value.split(",")]
    if not tokens or any(not token for token in tokens):
        raise ValueError("--seeds must be a non-empty comma-separated list")
    try:
        seeds = tuple(int(token) for token in tokens)
    except ValueError as error:
        raise ValueError("--seeds must contain integers") from error
    if any(seed < 0 for seed in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("--seeds must contain unique non-negative integers")
    return tuple(sorted(seeds))


def parse_named_paths(values: Iterable[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"expected name=directory, got {value!r}")
        name, raw_path = value.split("=", 1)
        name = name.strip()
        raw_path = raw_path.strip()
        if not name or not raw_path or name in result:
            raise ValueError(f"invalid or duplicate named path: {value!r}")
        result[name] = Path(raw_path)
    return result


def parse_expected_models(values: Iterable[str]) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"expected name=model1,model2, got {value!r}")
        name, raw_models = value.split("=", 1)
        models = tuple(token.strip() for token in raw_models.split(","))
        if (
            not name.strip()
            or not models
            or any(not model for model in models)
            or len(set(models)) != len(models)
            or name.strip() in result
        ):
            raise ValueError(f"invalid or duplicate expected models: {value!r}")
        result[name.strip()] = tuple(sorted(models))
    return result


def expected_tasks(
    scenario_maps: Mapping[str, Mapping[str, str]], seeds: Iterable[int]
) -> set[tuple[str, str, int]]:
    return {
        (suite, scenario, int(seed))
        for suite, scenarios in scenario_maps.items()
        for scenario in scenarios
        for seed in seeds
    }


def read_object(path: Path, issues: list[str]) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        issues.append(f"cannot read JSON {path}: {error}")
        return None
    if not isinstance(payload, dict):
        issues.append(f"JSON root is not an object: {path}")
        return None
    return payload


def _valid_sha(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def validate_provenance(
    path: Path,
    expected_task: tuple[str, str, int],
    expected_model: str | None,
    issues: list[str],
) -> None:
    payload = read_object(path, issues)
    if payload is None:
        return
    task = payload.get("task")
    if not isinstance(task, dict):
        issues.append(f"missing provenance task object: {path}")
        return
    suite, scenario, seed = expected_task
    observed = (task.get("suite"), task.get("scenario"), task.get("seed"))
    if observed != expected_task:
        issues.append(
            f"provenance task mismatch at {path}: expected={expected_task}, "
            f"actual={observed}"
        )
    if expected_model is not None and task.get("model") != expected_model:
        issues.append(
            f"provenance model mismatch at {path}: expected={expected_model!r}, "
            f"actual={task.get('model')!r}"
        )
    code = payload.get("code")
    if not isinstance(code, dict) or not _valid_sha(code.get("sha256")):
        issues.append(f"missing valid aggregate code SHA-256: {path}")
    if not _valid_sha(payload.get("parameter_fingerprint")):
        issues.append(f"missing valid parameter fingerprint: {path}")
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict) or not inputs:
        issues.append(f"missing provenance inputs: {path}")


def _task_from_metrics(
    payload: dict[str, object], path: Path, issues: list[str]
) -> tuple[str, str, int] | None:
    try:
        seed = int(payload["seed"])
    except (KeyError, TypeError, ValueError):
        issues.append(f"missing integer seed in {path}")
        return None
    suite = path.parent.parent.name
    marker = f"_seed{seed}"
    if marker not in path.parent.name:
        issues.append(f"run directory does not encode seed {seed}: {path.parent}")
        return None
    scenario = path.parent.name.split(marker, 1)[0]
    return suite, scenario, seed


def _artifact_checks(
    metrics_path: Path,
    task: tuple[str, str, int],
    model: str | None,
    issues: list[str],
    require_evidence_package: bool,
) -> None:
    run_dir = metrics_path.parent
    required = [run_dir / "provenance.json", run_dir / "scores.npz"]
    if require_evidence_package:
        required.append(run_dir / "evidence_package.npz")
    for path in required:
        if not path.is_file() or path.stat().st_size <= 0:
            issues.append(f"missing or empty required artifact: {path}")
    provenance = run_dir / "provenance.json"
    if provenance.is_file():
        validate_provenance(provenance, task, model, issues)


def audit_gate(
    root: Path,
    scenario_maps: Mapping[str, Mapping[str, str]],
    seeds: tuple[int, ...],
) -> dict[str, object]:
    expected = expected_tasks(scenario_maps, seeds)
    observed: list[tuple[str, str, int]] = []
    issues: list[str] = []
    failure_files = sorted(root.glob("**/failure.json"))
    for path in sorted(root.glob("*/*/metrics.json")):
        payload = read_object(path, issues)
        if payload is None:
            continue
        task = _task_from_metrics(payload, path, issues)
        if task is None:
            continue
        observed.append(task)
        _artifact_checks(path, task, None, issues, require_evidence_package=True)
    counts = Counter(observed)
    duplicates = sorted(task for task, count in counts.items() if count > 1)
    actual = set(observed)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    issues.extend(f"failure marker: {path}" for path in failure_files)
    if duplicates:
        issues.append(f"duplicate gate tasks: {duplicates}")
    if unexpected:
        issues.append(f"unexpected gate tasks: {unexpected}")
    return {
        "root": str(root),
        "expected_runs": len(expected),
        "observed_runs": len(observed),
        "missing_count": len(missing),
        "missing": missing,
        "unexpected_count": len(unexpected),
        "failure_markers": [str(path) for path in failure_files],
        "issues": issues,
        "complete": not missing and not issues,
    }


def audit_baseline(
    root: Path,
    models: tuple[str, ...],
    scenario_maps: Mapping[str, Mapping[str, str]],
    seeds: tuple[int, ...],
) -> dict[str, object]:
    base_tasks = expected_tasks(scenario_maps, seeds)
    expected = {(suite, scenario, seed, model) for suite, scenario, seed in base_tasks for model in models}
    observed: list[tuple[str, str, int, str]] = []
    issues: list[str] = []
    failure_files = sorted(root.glob("**/failure.json"))
    for path in sorted(root.glob("*/*/metrics.json")):
        payload = read_object(path, issues)
        if payload is None:
            continue
        task = _task_from_metrics(payload, path, issues)
        if task is None:
            continue
        model = payload.get("model")
        if not isinstance(model, str) or not model:
            issues.append(f"missing model in {path}")
            continue
        observed.append((*task, model))
        _artifact_checks(path, task, model, issues, require_evidence_package=False)
    counts = Counter(observed)
    duplicates = sorted(item for item, count in counts.items() if count > 1)
    actual = set(observed)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    issues.extend(f"failure marker: {path}" for path in failure_files)
    if duplicates:
        issues.append(f"duplicate baseline tasks: {duplicates}")
    if unexpected:
        issues.append(f"unexpected baseline tasks: {unexpected}")

    manifest_path = root / "manifest.json"
    manifest_status = "legacy_compatible_missing"
    manifest: dict[str, object] | None = None
    effective_manifest_state: object = None
    if manifest_path.is_file():
        manifest = read_object(manifest_path, issues)
        manifest_status = "present"
        if manifest is not None:
            if manifest.get("number_of_experiments") != len(expected):
                issues.append(
                    f"manifest experiment count mismatch at {manifest_path}: "
                    f"expected={len(expected)}, "
                    f"actual={manifest.get('number_of_experiments')!r}"
                )
            if int(manifest.get("failed", 0)) != 0:
                issues.append(f"manifest records failures: {manifest_path}")
            effective_manifest_state = manifest.get("state")
            if effective_manifest_state is None:
                legacy_runs = manifest.get("runs")
                legacy_complete = (
                    manifest.get("completed") == len(expected)
                    and manifest.get("failed") == 0
                    and manifest.get("skipped") == 0
                    and isinstance(legacy_runs, list)
                    and len(legacy_runs) == len(expected)
                    and all(
                        isinstance(run, dict) and run.get("status") == "completed"
                        for run in legacy_runs
                    )
                )
                if legacy_complete:
                    effective_manifest_state = "legacy_inferred_complete"
                    manifest_status = "present_legacy_inferred_complete"
            if not missing and effective_manifest_state not in {
                "complete",
                "legacy_inferred_complete",
            }:
                issues.append(
                    f"complete artifacts require complete manifest state: {manifest_path}"
                )
    return {
        "root": str(root),
        "models": list(models),
        "expected_runs": len(expected),
        "observed_runs": len(observed),
        "missing_count": len(missing),
        "missing": missing,
        "unexpected_count": len(unexpected),
        "failure_markers": [str(path) for path in failure_files],
        "manifest_status": manifest_status,
        "manifest_state": effective_manifest_state,
        "issues": issues,
        "complete": not missing and not issues,
    }


def build_audit(
    gate_root: Path,
    baseline_roots: Mapping[str, Path],
    expected_models: Mapping[str, tuple[str, ...]],
    seeds: tuple[int, ...],
    scenario_maps: Mapping[str, Mapping[str, str]] = SCENARIO_MAPS,
) -> dict[str, object]:
    if set(baseline_roots) != set(expected_models):
        raise ValueError(
            "baseline root/model names differ: "
            f"roots={sorted(baseline_roots)}, models={sorted(expected_models)}"
        )
    gate = audit_gate(gate_root, scenario_maps, seeds)
    baselines = {
        name: audit_baseline(
            baseline_roots[name], expected_models[name], scenario_maps, seeds
        )
        for name in sorted(baseline_roots)
    }
    invalid = bool(gate["issues"]) or any(item["issues"] for item in baselines.values())
    complete = bool(gate["complete"]) and all(
        bool(item["complete"]) for item in baselines.values()
    )
    state = "complete" if complete else "invalid" if invalid else "incomplete"
    return {
        "schema_version": "strict_v2_sota_audit_v1",
        "state": state,
        "seeds": list(seeds),
        "suite_scenario_counts": {
            suite: len(scenarios) for suite, scenarios in scenario_maps.items()
        },
        "expected_paired_tasks": len(expected_tasks(scenario_maps, seeds)),
        "gate": gate,
        "baselines": baselines,
    }


def main() -> None:
    args = parse_arguments()
    report = build_audit(
        Path(args.gate_root),
        parse_named_paths(args.baseline_root),
        parse_expected_models(args.expected_models),
        parse_seeds(args.seeds),
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(output)
    print(rendered, end="")
    if report["state"] == "invalid":
        sys.exit(1)
    if report["state"] == "incomplete":
        sys.exit(2)


if __name__ == "__main__":
    main()
