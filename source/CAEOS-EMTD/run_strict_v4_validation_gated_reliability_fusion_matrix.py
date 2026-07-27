from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_validation_gated_reliability_fusion import evaluate


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_value(command: list[str], flag: str, value: str) -> None:
    index = command.index(flag)
    command[index + 1] = value


def run(args: argparse.Namespace) -> None:
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "strict_v4_validation_gated_reliability_fusion_protocol_v1":
        raise ValueError("unexpected validation-gated protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("validation-gated protocol SHA mismatch")
    for name, expected in protocol["implementation_sha256"].items():
        if file_sha(args.project_root / name) != expected:
            raise ValueError(f"active validation-gated implementation SHA mismatch: {name}")
    parameters = protocol["known_only_parameters"]
    for record in protocol["pilot"]["inputs"]:
        provenance_path = args.project_root / record["source_provenance"]
        if file_sha(provenance_path) != record["source_provenance_sha256"]:
            raise ValueError(f"source provenance SHA mismatch: {provenance_path}")
        if file_sha(Path(record["csv"])) != record["csv_sha256"]:
            raise ValueError(f"source CSV SHA mismatch: {record['suite']}")
        if file_sha(args.project_root / record["config"]) != record["config_sha256"]:
            raise ValueError(f"config SHA mismatch: {record['suite']}")
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        reference = args.reference_root / record["suite"] / f'{record["scenario"]}_seed307'
        candidate = args.candidate_root / record["suite"] / f'{record["scenario"]}_seed307'
        reference_metrics = reference / "metrics.json"
        if not reference_metrics.is_file():
            command = list(provenance["command"][1:])
            if command[0] != "train_hybrid_open_set.py":
                raise ValueError("unexpected source training command")
            replace_value(command, "--seed", str(record["training_seed"]))
            replace_value(command, "--output-dir", str(reference.resolve()))
            replace_value(command, "--risk-policy-name", "strict_v4_vgrf_paired_reference_v1")
            reference.mkdir(parents=True, exist_ok=True)
            with (reference / "paired_training.log").open("w", encoding="utf-8") as handle:
                completed = subprocess.run(
                    [sys.executable, *command], cwd=args.project_root,
                    stdout=handle, stderr=subprocess.STDOUT, check=False,
                )
            if completed.returncode != 0 or not reference_metrics.is_file():
                raise RuntimeError(f"paired reference training failed: {record['suite']}/{record['scenario']}")
        candidate_metrics = candidate / "metrics.json"
        if candidate_metrics.is_file():
            existing = json.loads(candidate_metrics.read_text(encoding="utf-8"))
            if existing.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
                raise ValueError(f"candidate result protocol mismatch: {candidate}")
            continue
        evaluate(
            argparse.Namespace(
                evidence_package=reference / "evidence_package.npz",
                scores=reference / "scores.npz",
                output_dir=candidate,
                protocol_manifest_sha256=protocol["manifest_sha256"],
                suite=record["suite"], scenario=record["scenario"], seed=record["training_seed"],
                shrinkage=parameters["empirical_bayes_shrinkage"],
                minimum_reliability=parameters["minimum_reliability"],
                risk_blend=parameters["risk_blend"],
                known_rejection_quantile=parameters["known_rejection_quantile"],
                minimum_f1_gain=parameters["minimum_f1_gain"],
                maximum_correct_risk_increase=parameters["maximum_correct_risk_increase"],
                minimum_auc_gain=parameters["minimum_auc_gain"],
                minimum_separation_gain=parameters["minimum_separation_gain"],
                minimum_strict_proxy_gain=parameters["minimum_strict_proxy_gain"],
            )
        )
    (args.candidate_root / "pilot_execution_complete").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
