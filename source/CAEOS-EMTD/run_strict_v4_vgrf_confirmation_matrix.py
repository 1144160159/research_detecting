from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_nested_gate_matrix import (
    Experiment,
    build_run_provenance,
    freeze_or_validate_provenance,
)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_value(command: list[str], flag: str, value: str) -> None:
    index = command.index(flag)
    command[index + 1] = value


def prepare_reference_execution(
    record: dict,
    source_provenance: dict,
    reference: Path,
) -> tuple[list[str], dict]:
    command = list(source_provenance["command"])
    command[0] = sys.executable
    replace_value(command, "--seed", str(record["training_seed"]))
    replace_value(command, "--output-dir", str(reference.resolve()))
    replace_value(
        command,
        "--risk-policy-name",
        "strict_v4_vgrf_confirmation_reference_v1",
    )
    expected_provenance = build_run_provenance(
        Experiment(
            suite=record["suite"],
            scenario=record["scenario"],
            unknown_classes=record["unknown_classes"],
            seed=record["training_seed"],
            output_dir=str(reference.resolve()),
        ),
        command,
    )
    return command, expected_provenance


def main() -> None:
    from caeos.vgrf_confirmation_validation import (
        validate_candidate_result,
        validate_reference_result,
    )
    from evaluate_validation_gated_reliability_fusion import evaluate

    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("VGRF confirmation protocol SHA mismatch")
    for name, expected in protocol["implementation_sha256"].items():
        if file_sha(args.project_root / name) != expected:
            raise ValueError(f"implementation SHA mismatch: {name}")
    parameters = protocol["known_only_parameters"]
    for record in protocol["confirmation"]["inputs"]:
        provenance_path = args.project_root / record["source_provenance"]
        if file_sha(provenance_path) != record["source_provenance_sha256"]:
            raise ValueError(f"source provenance mismatch: {provenance_path}")
        if file_sha(Path(record["csv"])) != record["csv_sha256"] or file_sha(args.project_root / record["config"]) != record["config_sha256"]:
            raise ValueError(f"source input mismatch: {record['suite']}/{record['scenario']}")
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        suffix = f'{record["scenario"]}_seed{record["training_seed"]}'
        reference = args.reference_root / record["suite"] / suffix
        candidate = args.candidate_root / record["suite"] / suffix
        command, expected_provenance = prepare_reference_execution(
            record, provenance, reference
        )
        reference.mkdir(parents=True, exist_ok=True)
        complete = freeze_or_validate_provenance(
            reference,
            expected_provenance,
            (
                reference / "metrics.json",
                reference / "evidence_package.npz",
                reference / "scores.npz",
            ),
        )
        if not complete:
            with (reference / "training.log").open("w", encoding="utf-8") as handle:
                completed = subprocess.run(command, cwd=args.project_root, stdout=handle, stderr=subprocess.STDOUT, check=False)
            if completed.returncode != 0 or not (reference / "metrics.json").is_file():
                raise RuntimeError(f"reference training failed: {record['suite']}/{suffix}")
        validate_reference_result(
            reference, record, protocol, args.project_root
        )
        if (candidate / "metrics.json").is_file():
            existing = json.loads((candidate / "metrics.json").read_text(encoding="utf-8"))
            validate_candidate_result(
                existing, record, protocol, reference
            )
            continue
        result = evaluate(argparse.Namespace(
            evidence_package=reference / "evidence_package.npz", scores=reference / "scores.npz",
            output_dir=candidate, protocol_manifest_sha256=protocol["manifest_sha256"],
            suite=record["suite"], scenario=record["scenario"], seed=record["training_seed"],
            shrinkage=parameters["empirical_bayes_shrinkage"], minimum_reliability=parameters["minimum_reliability"],
            risk_blend=parameters["risk_blend"], known_rejection_quantile=parameters["known_rejection_quantile"],
            minimum_f1_gain=parameters["minimum_f1_gain"], maximum_correct_risk_increase=parameters["maximum_correct_risk_increase"],
            minimum_auc_gain=parameters["minimum_auc_gain"], minimum_separation_gain=parameters["minimum_separation_gain"],
            minimum_strict_proxy_gain=parameters["minimum_strict_proxy_gain"],
        ))
        validate_candidate_result(result, record, protocol, reference)
        print(f"completed {record['suite']}/{suffix}", flush=True)
    (args.candidate_root / "confirmation_execution_complete").touch()


if __name__ == "__main__":
    main()
