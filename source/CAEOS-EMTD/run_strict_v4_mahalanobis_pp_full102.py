from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import sys

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from run_strict_v4_mahalanobis_pp_pilot import output_for, run_one, valid_output


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen Mahalanobis++ full102 screen")
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def validate_protocol(protocol: dict, root: Path) -> None:
    if protocol.get("schema_version") != "strict_v4_mahalanobis_pp_full102_protocol_v1":
        raise ValueError("unexpected Mahalanobis++ full102 protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("Mahalanobis++ full102 protocol SHA mismatch")
    if len(protocol.get("sources", {})) != 102 or protocol.get("expected_scenarios") != 102:
        raise ValueError("Mahalanobis++ full102 source coverage mismatch")
    paths = {
        "calibrator": root / "caeos" / "mahalanobis_pp.py",
        "evaluator": root / "evaluate_mlp_mahalanobis_pp.py",
        "full_protocol_creator": root / "create_strict_v4_mahalanobis_pp_full102_protocol.py",
        "full_runner": Path(__file__).resolve(),
        "full_summarizer": root / "summarize_strict_v4_mahalanobis_pp_full102.py",
        "pilot_runner_helper": root / "run_strict_v4_mahalanobis_pp_pilot.py",
    }
    current = {name: file_hash(path) for name, path in paths.items()}
    if current != protocol.get("implementation_sha256"):
        raise ValueError("Mahalanobis++ full102 implementation changed after protocol freeze")


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
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for key, source in sorted(protocol["sources"].items()):
            future = executor.submit(
                run_one,
                evaluator,
                mlp_root / source["mlp_relative_path"],
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
        valid_output(output_for(output_root, key), source["mlp_artifact_sha256"])
        for key, source in protocol["sources"].items()
    )
    if completed != 102:
        raise RuntimeError(f"Mahalanobis++ full102 coverage incomplete: {completed}/102")
    summary = {
        "schema_version": "strict_v4_mahalanobis_pp_full102_matrix_v1",
        "status": "complete",
        "expected_runs": 102,
        "completed_runs": completed,
        "failures": 0,
        "method": "mahalanobis_pp",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "full102_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
