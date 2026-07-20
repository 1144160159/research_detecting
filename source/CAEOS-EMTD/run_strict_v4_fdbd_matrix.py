from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


METHOD = "fdbd"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def without_suffix(value: str, suffix: str) -> str:
    if not value.endswith(suffix):
        raise ValueError("%r does not end with %r" % (value, suffix))
    return value[: -len(suffix)]


def select_pilot_scenarios(coverage: dict[str, Any]) -> dict[str, list[str]]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    coverage_sha = coverage.get("manifest_sha256")
    registry = coverage.get("scenario_registry")
    if not isinstance(coverage_sha, str) or not isinstance(registry, dict):
        raise ValueError("coverage manifest is incomplete")
    selected = {}
    for suite in sorted(registry):
        scenarios = registry[suite].get("scenarios", [])
        if len(scenarios) < 2:
            raise ValueError("suite %s has fewer than two scenarios" % suite)
        indices = []
        attempt = 0
        while len(indices) < 2:
            digest = hashlib.sha256(("%s:fdbd:%s:%d" % (coverage_sha, suite, attempt)).encode("utf-8")).hexdigest()
            index = int(digest[:16], 16) % len(scenarios)
            if index not in indices:
                indices.append(index)
            attempt += 1
        selected[suite] = [scenarios[index] for index in indices]
    return selected


def source_artifacts(run: Path) -> dict[str, str]:
    return {name: sha256_file(run / name) for name in ("metrics.json", "scores.npz", "model.pt")}


def valid_output(output: Path, expected_source: dict[str, str]) -> bool:
    paths = {name: output / name for name in ("metrics.json", "provenance.json", "scores.npz")}
    if not all(path.is_file() for path in paths.values()):
        return False
    try:
        metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
        provenance = json.loads(paths["provenance.json"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        set(metrics.get("reports", {})) == {METHOD}
        and provenance.get("source_artifact_sha256") == expected_source
        and provenance.get("methods") == [METHOD]
    )


def run_one(evaluator: Path, source: Path, output: Path, device: str, expected_source: dict[str, str]) -> dict[str, str]:
    if valid_output(output, expected_source):
        return {"source": str(source), "output": str(output), "state": "reused"}
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, str(evaluator), "--source-run", str(source), "--output-dir", str(output), "--device", device],
        text=True, capture_output=True,
    )
    (output / "run.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError("fDBD run failed for %s: %s" % (source, completed.stderr[-3000:]))
    if not valid_output(output, expected_source):
        raise RuntimeError("fDBD output validation failed for %s" % source)
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--protocol-only", action="store_true")
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    pilot = select_pilot_scenarios(coverage)
    all_sources = sorted(path.parent for path in source_root.glob("*/*_mlp/metrics.json"))
    if len(all_sources) != 102:
        raise ValueError("expected 102 frozen MLP runs, found %d" % len(all_sources))
    source_by_identity = {}
    for source in all_sources:
        scenario_seed = without_suffix(source.name, "_mlp")
        scenario = without_suffix(scenario_seed, "_seed7")
        source_by_identity[(source.parent.name, scenario)] = source
    if len(source_by_identity) != 102:
        raise ValueError("frozen MLP source identities are not unique")
    selected_identities = sorted(source_by_identity) if args.mode == "full" else sorted(
        (suite, scenario) for suite, items in pilot.items() for scenario in items
    )
    sources = [source_by_identity[identity] for identity in selected_identities]
    base = Path(__file__).resolve().parent
    evaluator = base / "evaluate_mlp_fdbd.py"
    scorer = base / "caeos" / "fdbd_posthoc.py"
    source_hashes = {str(path.relative_to(source_root)): source_artifacts(path) for path in sources}
    protocol = {
        "schema_version": "strict_v4_mlp_fdbd_protocol_v1",
        "status": "frozen_before_fdbd_results", "mode": args.mode,
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": "all frozen scenarios" if args.mode == "full" else "two fDBD-SHA-indexed scenarios per suite independent of metric values",
        "selected_scenarios": {
            suite: [scenario for selected_suite, scenario in selected_identities if selected_suite == suite]
            for suite in sorted({suite for suite, _ in selected_identities})
        },
        "expected_runs": len(sources), "methods": [METHOD],
        "paper": "https://proceedings.mlr.press/v235/liu24ax.html",
        "official_implementation": "https://github.com/litianliu/fDBD-OOD",
        "official_implementation_commit": "961621e320bfeb9d7456356945fdcafb8a12868b",
        "formula": "official hyperparameter-free fDBD closed-form decision-boundary confidence",
        "parameter_policy": "no tunable hyperparameters and no OOD sweep",
        "fit_data": "known_training_features_only",
        "threshold_data": "known_validation_only", "ood_parameter_sweep": False,
        "test_labels": "final_metrics_and_development_expansion_gate_only",
        "prediction_policy": "unmodified_frozen_classifier_prediction",
        "numerical_policy": "epsilon 1e-12 only for zero norms",
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": {"evaluator": sha256_file(evaluator), "scorer": sha256_file(scorer), "runner": sha256_file(Path(__file__).resolve())},
    }
    canonical = json.dumps(protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    protocol["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    output_root.mkdir(parents=True, exist_ok=True)
    protocol_path = output_root / "protocol_manifest.json"
    if protocol_path.is_file():
        if json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
            raise ValueError("existing fDBD protocol differs from frozen inputs")
    else:
        protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.protocol_only:
        print(json.dumps(protocol, ensure_ascii=False, sort_keys=True), flush=True)
        return
    futures = {}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for source in sources:
            relative = source.relative_to(source_root)
            output = output_root / relative.parent / without_suffix(relative.name, "_mlp")
            future = executor.submit(run_one, evaluator, source, output, args.device, source_hashes[str(relative)])
            futures[future] = relative
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    completed = sum(
        valid_output(output_root / source.relative_to(source_root).parent / without_suffix(source.name, "_mlp"), source_hashes[str(source.relative_to(source_root))])
        for source in sources
    )
    if completed != len(sources):
        raise RuntimeError("fDBD coverage incomplete: %d/%d" % (completed, len(sources)))
    summary = {
        "schema_version": "strict_v4_mlp_fdbd_matrix_v1", "status": "complete", "mode": args.mode,
        "expected_runs": len(sources), "completed_runs": completed, "failures": 0,
        "methods_per_run": [METHOD], "report_count": completed,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {state: sum(item["state"] == state for item in results) for state in ("completed", "reused")},
    }
    (output_root / "matrix_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "fdbd_complete").write_text(protocol["manifest_sha256"] + "\n", encoding="ascii")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
