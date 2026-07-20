from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


METHOD = "excel"


def output_for(root: Path, key: str) -> Path:
    suite, scenario = key.split("/", 1)
    return root / suite / f"{scenario}_seed7_excel"


def valid_output(output: Path, source_sha256: dict[str, str]) -> bool:
    if any(not (output / name).is_file() for name in ("metrics.json", "scores.npz", "provenance.json")):
        return False
    try:
        metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
        provenance = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        metrics.get("schema_version") == "strict_v4_mlp_excel_v1"
        and set(metrics.get("reports", {})) == {METHOD}
        and provenance.get("source_artifact_sha256") == source_sha256
        and provenance.get("method") == METHOD
    )


def validate_protocol(protocol: dict, root: Path) -> None:
    if protocol.get("schema_version") != "strict_v4_excel_full102_protocol_v1":
        raise ValueError("unexpected ExCeL full102 protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("ExCeL full102 protocol SHA mismatch")
    if len(protocol.get("sources", {})) != 102:
        raise ValueError("ExCeL full102 source coverage mismatch")
    paths = {
        "calibrator": root / "caeos" / "excel_ood.py", "evaluator": root / "evaluate_mlp_excel.py",
        "protocol_creator": root / "create_strict_v4_excel_full102_protocol.py",
        "runner": Path(__file__).resolve(), "summarizer": root / "summarize_strict_v4_excel_full102.py",
    }
    if {name: file_hash(path) for name, path in paths.items()} != protocol.get("implementation_sha256"):
        raise ValueError("ExCeL implementation changed after protocol freeze")


def run_one(evaluator: Path, source: Path, output: Path, source_sha256: dict[str, str], device: str, force: bool) -> dict[str, str]:
    if not force and valid_output(output, source_sha256):
        return {"source": str(source), "output": str(output), "state": "reused"}
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, str(evaluator), "--source-run", str(source), "--output-dir", str(output), "--device", device],
        text=True, capture_output=True,
    )
    (output / "run.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"ExCeL run failed for {source}: {completed.stderr[-2000:]}")
    if not valid_output(output, source_sha256):
        raise RuntimeError(f"ExCeL output validation failed for {source}")
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    root = Path(__file__).resolve().parent
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    validate_protocol(protocol, root)
    mlp_root = Path(protocol["mlp_root"])
    args.output_root.mkdir(parents=True, exist_ok=True)
    results = []
    futures = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for key, source in sorted(protocol["sources"].items()):
            future = executor.submit(
                run_one, root / "evaluate_mlp_excel.py", mlp_root / source["mlp_relative_path"],
                output_for(args.output_root, key), source["mlp_artifact_sha256"], args.device, args.force,
            )
            futures[future] = key
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    completed = sum(valid_output(output_for(args.output_root, key), source["mlp_artifact_sha256"]) for key, source in protocol["sources"].items())
    if completed != 102:
        raise RuntimeError(f"ExCeL full102 coverage incomplete: {completed}/102")
    summary = {
        "schema_version": "strict_v4_excel_full102_matrix_v1", "status": "complete",
        "expected_runs": 102, "completed_runs": completed, "failures": 0, "method": METHOD,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {state: sum(item["state"] == state for item in results) for state in ("completed", "reused")},
    }
    (args.output_root / "matrix_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "full102_complete").write_text(protocol["manifest_sha256"] + "\n", encoding="ascii")
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
