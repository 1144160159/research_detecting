from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_conflict_topology_copula import evaluate


def verify_source_record(project_root: Path, record: dict) -> Path:
    source = project_root / record["run_root"]
    for name, expected in record["sha256"].items():
        path = source / name
        if not path.is_file():
            raise FileNotFoundError(f"missing frozen conflict-topology input: {path}")
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f"conflict-topology input SHA mismatch: {path}")
    return source


def run(args: argparse.Namespace) -> None:
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "strict_v4_conflict_topology_copula_protocol_v1":
        raise ValueError("unexpected conflict-topology copula protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("conflict-topology copula protocol SHA mismatch")
    parameters = protocol["known_only_fit"]
    alpha = 0.25
    for record in protocol["pilot"]["inputs"]:
        source = verify_source_record(args.project_root, record)
        output = args.output_root / record["suite"] / f'{record["scenario"]}_seed7'
        metrics_path = output / "metrics.json"
        if metrics_path.is_file():
            existing = json.loads(metrics_path.read_text(encoding="utf-8"))
            if existing.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
                raise ValueError(f"existing result has a different protocol: {output}")
            continue
        evaluate(
            argparse.Namespace(
                evidence_package=source / "evidence_package.npz",
                scores=source / "scores.npz",
                output_dir=output,
                protocol_manifest_sha256=protocol["manifest_sha256"],
                suite=record["suite"],
                scenario=record["scenario"],
                seed=record["seed"],
                alpha=alpha,
                calibration_fraction=parameters[
                    "stratified_fit_calibration_fraction"
                ],
                split_seed=parameters["split_seed"],
                known_rejection_quantile=parameters["known_rejection_quantile"],
            )
        )
    (args.output_root / "pilot_execution_complete").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
