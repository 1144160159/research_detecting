from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


METHODS = ("shannon_entropy", "prototype_distance")


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
        tuple(metrics.get("reports", {}).keys()) == METHODS
        and metrics.get("selection_evidence", {}).get("unknown_or_test_labels_used_for_fitting_or_selection") is False
        and provenance.get("source_artifact_sha256") == expected_source
        and tuple(provenance.get("methods", [])) == METHODS
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
        raise RuntimeError("mandatory score run failed for %s: %s" % (source, completed.stderr[-3000:]))
    if not valid_output(output, expected_source):
        raise RuntimeError("mandatory score output validation failed for %s" % source)
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--protocol-only", action="store_true")
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    all_sources = sorted(path.parent for path in source_root.glob("*/*_mlp/metrics.json"))
    if len(all_sources) != 102:
        raise ValueError("expected 102 frozen MLP runs, found %d" % len(all_sources))
    source_by_identity = {}
    for source in all_sources:
        scenario_seed = without_suffix(source.name, "_mlp")
        scenario = without_suffix(scenario_seed, "_seed7")
        source_by_identity[(source.parent.name, scenario)] = source
    selected_identities = sorted(source_by_identity)
    registry_identities = sorted(
        (suite, scenario)
        for suite, item in coverage["scenario_registry"].items()
        for scenario in item["scenarios"]
    )
    if selected_identities != registry_identities:
        raise ValueError("frozen MLP identities differ from the 102-scenario coverage registry")
    base = Path(__file__).resolve().parent
    evaluator = base / "evaluate_mlp_mandatory_scores.py"
    scorer = base / "caeos" / "mandatory_scores.py"
    source_hashes = {str(path.relative_to(source_root)): source_artifacts(path) for path in all_sources}
    protocol = {
        "schema_version": "strict_v4_mlp_mandatory_scores_protocol_v1",
        "status": "frozen_before_mandatory_score_results", "mode": "full",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": "all 102 frozen seed7 scenarios; mandatory baseline coverage, no result-based expansion gate",
        "selected_scenarios": {
            suite: [scenario for selected_suite, scenario in selected_identities if selected_suite == suite]
            for suite in sorted({suite for suite, _ in selected_identities})
        },
        "expected_runs": 102, "methods": list(METHODS),
        "entropy_formula": "negative sum_k softmax_k * log(softmax_k)",
        "prototype_formula": "minimum squared Euclidean distance to known-training class mean in frozen embedding",
        "fit_data": {"shannon_entropy": "none", "prototype_distance": "known_training_embeddings_and_labels_only"},
        "threshold_data": "known_validation_only", "ood_parameter_sweep": False,
        "prediction_policy": "unmodified frozen MLP argmax for both scores",
        "test_labels": "final_metrics_only",
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": {"evaluator": sha256_file(evaluator), "scorer": sha256_file(scorer), "runner": sha256_file(Path(__file__).resolve())},
    }
    canonical = json.dumps(protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    protocol["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    protocol_path = output_root / "protocol_manifest.json"
    if args.protocol_only:
        observed = len(list(output_root.glob("*/*/metrics.json"))) if output_root.is_dir() else 0
        if observed != 0:
            raise ValueError("mandatory score protocol must be frozen before every full102 result")
        output_root.mkdir(parents=True, exist_ok=True)
        if protocol_path.is_file() and json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
            raise ValueError("existing mandatory score protocol differs from frozen inputs")
        if not protocol_path.is_file():
            protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(protocol, ensure_ascii=False, sort_keys=True), flush=True)
        return
    if not protocol_path.is_file():
        raise ValueError("run --protocol-only before starting the mandatory full102 matrix")
    if json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
        raise ValueError("existing mandatory score protocol differs from frozen inputs")
    futures = {}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for source in all_sources:
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
        for source in all_sources
    )
    if completed != 102:
        raise RuntimeError("mandatory score coverage incomplete: %d/102" % completed)
    summary = {
        "schema_version": "strict_v4_mlp_mandatory_scores_matrix_v1", "status": "complete", "mode": "full",
        "expected_runs": 102, "completed_runs": completed, "failures": 0,
        "methods_per_run": list(METHODS), "report_count": completed * len(METHODS),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {state: sum(item["state"] == state for item in results) for state in ("completed", "reused")},
    }
    (output_root / "matrix_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "mandatory_scores_complete").write_text(protocol["manifest_sha256"] + "\n", encoding="ascii")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
