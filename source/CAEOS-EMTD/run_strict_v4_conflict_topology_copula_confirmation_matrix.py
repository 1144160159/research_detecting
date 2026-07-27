from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_conflict_topology_copula import evaluate


def verify_pairwise_source(
    source: Path, *, seed: int, risk_policy: str, risk_selection: str
) -> dict:
    required = ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise FileNotFoundError(f"missing Pairwise confirmation artifacts: {source}: {missing}")
    metrics = json.loads((source / "metrics.json").read_text(encoding="utf-8"))
    if metrics.get("seed") != seed:
        raise ValueError(f"Pairwise confirmation seed mismatch: {source}")
    if metrics.get("risk_policy") != risk_policy:
        raise ValueError(f"Pairwise confirmation risk policy mismatch: {source}")
    if metrics.get("risk_selection") != risk_selection:
        raise ValueError(f"Pairwise confirmation risk selection mismatch: {source}")
    details = metrics.get("risk_selection_details", {})
    if details.get("unknown_or_test_labels_used_for_selection") is not False:
        raise ValueError(f"Pairwise confirmation leakage guard failed: {source}")
    fingerprint = metrics.get("split_metadata", {}).get("split_fingerprint", {})
    if not fingerprint.get("combined"):
        raise ValueError(f"Pairwise confirmation split fingerprint is absent: {source}")
    return metrics


def run(args: argparse.Namespace) -> None:
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "strict_v4_conflict_topology_copula_confirmation_protocol_v1":
        raise ValueError("unexpected CTC confirmation protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("CTC confirmation protocol SHA mismatch")
    for name, expected in protocol["implementation_sha256"].items():
        observed = hashlib.sha256((args.project_root / name).read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f"CTC confirmation implementation SHA mismatch: {name}")

    generation = protocol["pairwise_generation"]
    parameters = protocol["ctc_parameters"]
    completed = 0
    for suite, registry in protocol["scenario_registry"].items():
        for scenario in registry["scenarios"]:
            for seed in protocol["seeds"]:
                source = args.pairwise_root / suite / f"{scenario}_seed{seed}"
                verify_pairwise_source(
                    source,
                    seed=seed,
                    risk_policy=generation["risk_policy_name"],
                    risk_selection=generation["risk_selection"],
                )
                output = args.output_root / suite / f"{scenario}_seed{seed}"
                metrics_path = output / "metrics.json"
                if metrics_path.is_file():
                    existing = json.loads(metrics_path.read_text(encoding="utf-8"))
                    if existing.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
                        raise ValueError(f"existing CTC confirmation binding mismatch: {output}")
                    completed += 1
                    continue
                evaluate(
                    argparse.Namespace(
                        evidence_package=source / "evidence_package.npz",
                        scores=source / "scores.npz",
                        output_dir=output,
                        protocol_manifest_sha256=protocol["manifest_sha256"],
                        suite=suite,
                        scenario=scenario,
                        seed=seed,
                        alpha=parameters["alpha"],
                        calibration_fraction=parameters["calibration_fraction"],
                        split_seed=parameters["split_seed"],
                        known_rejection_quantile=parameters[
                            "known_rejection_quantile"
                        ],
                    )
                )
                completed += 1
    if completed != protocol["expected_ctc_runs"]:
        raise ValueError("CTC confirmation run count is incomplete")
    (args.output_root / "confirmation_execution_complete").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--pairwise-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
