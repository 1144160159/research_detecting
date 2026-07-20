from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


METHOD = "mahalanobis_pp"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen Mahalanobis++ pilot")
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def validate_protocol(protocol: dict[str, Any], root: Path) -> None:
    if protocol.get("schema_version") != "strict_v4_mahalanobis_pp_pilot_protocol_v1":
        raise ValueError("unexpected Mahalanobis++ pilot protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("Mahalanobis++ pilot protocol SHA mismatch")
    if len(protocol.get("sources", {})) != protocol.get("expected_scenarios"):
        raise ValueError("Mahalanobis++ pilot source coverage mismatch")
    expected = protocol.get("implementation_sha256", {})
    paths = {
        "calibrator": root / "caeos" / "mahalanobis_pp.py",
        "evaluator": root / "evaluate_mlp_mahalanobis_pp.py",
        "protocol_creator": root / "create_strict_v4_mahalanobis_pp_pilot_protocol.py",
        "runner": Path(__file__).resolve(),
        "summarizer": root / "summarize_strict_v4_mahalanobis_pp_pilot.py",
    }
    current = {name: file_hash(path) for name, path in paths.items()}
    if current != expected:
        raise ValueError("Mahalanobis++ implementation changed after protocol freeze")


def output_for(root: Path, key: str) -> Path:
    suite, scenario = key.split("/", 1)
    return root / suite / f"{scenario}_seed7_mahalanobis_pp"


def valid_output(output: Path, source_sha256: dict[str, str]) -> bool:
    required = ("metrics.json", "scores.npz", "provenance.json")
    if any(not (output / name).is_file() for name in required):
        return False
    try:
        metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
        provenance = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        metrics.get("schema_version") == "strict_v4_mlp_mahalanobis_pp_v1"
        and set(metrics.get("reports", {})) == {METHOD}
        and provenance.get("source_artifact_sha256") == source_sha256
        and provenance.get("method") == METHOD
    )


def run_one(
    evaluator: Path,
    source: Path,
    output: Path,
    source_sha256: dict[str, str],
    device: str,
    force: bool,
) -> dict[str, str]:
    if not force and valid_output(output, source_sha256):
        return {"source": str(source), "output": str(output), "state": "reused"}
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            sys.executable,
            str(evaluator),
            "--source-run",
            str(source),
            "--output-dir",
            str(output),
            "--device",
            device,
        ],
        text=True,
        capture_output=True,
    )
    (output / "run.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError(
            f"Mahalanobis++ run failed for {source}: {completed.stderr[-2000:]}"
        )
    if not valid_output(output, source_sha256):
        raise RuntimeError(f"Mahalanobis++ output validation failed for {source}")
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    args = parse_arguments()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    root = Path(__file__).resolve().parent
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    validate_protocol(protocol, root)
    mlp_root = Path(protocol["mlp_root"])
    output_root = args.output_root.resolve()
    evaluator = root / "evaluate_mlp_mahalanobis_pp.py"
    output_root.mkdir(parents=True, exist_ok=True)

    futures = {}
    results: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for key, source in sorted(protocol["sources"].items()):
            mlp_run = mlp_root / source["mlp_relative_path"]
            future = executor.submit(
                run_one,
                evaluator,
                mlp_run,
                output_for(output_root, key),
                source["mlp_artifact_sha256"],
                args.device,
                args.force,
            )
            futures[future] = key
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)

    completed = sum(
        valid_output(
            output_for(output_root, key), source["mlp_artifact_sha256"]
        )
        for key, source in protocol["sources"].items()
    )
    expected = int(protocol["expected_scenarios"])
    if completed != expected:
        raise RuntimeError(f"Mahalanobis++ pilot coverage incomplete: {completed}/{expected}")
    summary = {
        "schema_version": "strict_v4_mahalanobis_pp_pilot_matrix_v1",
        "status": "complete",
        "expected_runs": expected,
        "completed_runs": completed,
        "failures": 0,
        "method": METHOD,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "pilot_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
