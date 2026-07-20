from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


METHODS = {"react_energy", "dice", "she"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the frozen-MLP ReAct/DICE/SHE strict-v4 matrix"
    )
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--expected-runs", type=int, default=102)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def source_artifacts(run: Path) -> dict[str, str]:
    return {
        name: sha256_file(run / name)
        for name in ("metrics.json", "scores.npz", "model.pt")
    }


def valid_output(output: Path, expected_source: dict[str, str]) -> bool:
    metrics_path = output / "metrics.json"
    provenance_path = output / "provenance.json"
    scores_path = output / "scores.npz"
    if not metrics_path.is_file() or not provenance_path.is_file() or not scores_path.is_file():
        return False
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        set(metrics.get("reports", {})) == METHODS
        and provenance.get("source_artifact_sha256") == expected_source
        and set(provenance.get("methods", [])) == METHODS
    )


def run_one(
    evaluator: Path,
    source: Path,
    output: Path,
    device: str,
    expected_source: dict[str, str],
    force: bool,
) -> dict[str, Any]:
    if not force and valid_output(output, expected_source):
        return {"source": str(source), "output": str(output), "state": "reused"}
    output.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(evaluator),
        "--source-run",
        str(source),
        "--output-dir",
        str(output),
        "--device",
        device,
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    (output / "run.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError(f"post-hoc OOD run failed for {source}: {completed.stderr[-2000:]}")
    if not valid_output(output, expected_source):
        raise RuntimeError(f"post-hoc OOD output validation failed for {source}")
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    args = parse_arguments()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    evaluator = Path(__file__).resolve().parent / "evaluate_mlp_posthoc_ood.py"
    calibrators = Path(__file__).resolve().parent / "caeos" / "neural_open_set.py"
    sources = sorted(path.parent for path in source_root.glob("*/*_mlp/metrics.json"))
    if len(sources) != args.expected_runs:
        raise ValueError(
            f"expected {args.expected_runs} frozen MLP runs, found {len(sources)} under {source_root}"
        )
    identities = [(path.parent.name, path.name) for path in sources]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate suite/run identities in frozen MLP source matrix")

    source_hashes = {str(path.relative_to(source_root)): source_artifacts(path) for path in sources}
    protocol = {
        "schema_version": "strict_v4_mlp_posthoc_ood_protocol_v1",
        "status": "frozen_before_posthoc_results",
        "source_root": str(source_root),
        "output_root": str(output_root),
        "expected_runs": len(sources),
        "methods": sorted(METHODS),
        "fit_data": "known_train_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_metrics_only",
        "react_percentile": 90.0,
        "dice_percentile": 90.0,
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": {
            "evaluator": sha256_file(evaluator),
            "calibrators": sha256_file(calibrators),
            "runner": sha256_file(Path(__file__).resolve()),
        },
    }
    canonical = json.dumps(protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    protocol["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    output_root.mkdir(parents=True, exist_ok=True)
    protocol_path = output_root / "protocol_manifest.json"
    if protocol_path.is_file():
        existing = json.loads(protocol_path.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing post-hoc OOD protocol differs from frozen inputs")
    else:
        protocol_path.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    futures = {}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for source in sources:
            relative = source.relative_to(source_root)
            output = output_root / relative.parent / relative.name.removesuffix("_mlp")
            future = executor.submit(
                run_one,
                evaluator,
                source,
                output,
                args.device,
                source_hashes[str(relative)],
                args.force,
            )
            futures[future] = relative
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)

    completed = sum(valid_output(
        output_root / source.relative_to(source_root).parent / source.name.removesuffix("_mlp"),
        source_hashes[str(source.relative_to(source_root))],
    ) for source in sources)
    if completed != len(sources):
        raise RuntimeError(f"post-hoc OOD coverage incomplete: {completed}/{len(sources)}")
    summary = {
        "schema_version": "strict_v4_mlp_posthoc_ood_matrix_v1",
        "status": "complete",
        "expected_runs": len(sources),
        "completed_runs": completed,
        "failures": 0,
        "methods_per_run": sorted(METHODS),
        "report_count": completed * len(METHODS),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_root / "posthoc_ood_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
