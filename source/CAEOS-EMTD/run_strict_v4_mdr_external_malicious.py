from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_") or (
        "unnamed"
    )


def verify_protocol(
    protocol: Dict[str, Any], project_root: Path
) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_external_malicious_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("selected_algorithm") != "mdr_caeos_v1"
    ):
        raise ValueError("canonical MDR external protocol required")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(
                f"MDR external implementation SHA mismatch: {relative}"
            )


def config_path(project_root: Path, dataset: str) -> Path:
    if dataset == "LSNM2024":
        return project_root / "configs/lsnm2024_external.json"
    if dataset == "CICDDoS2019":
        return project_root / "configs/cicids2017_strict.json"
    raise ValueError(f"unsupported MDR external dataset: {dataset}")


def base_arguments(
    project_root: Path,
    scenario: Dict[str, Any],
    policy: Dict[str, Any],
) -> list[str]:
    return [
        "--csv",
        scenario["csv"],
        "--config",
        str(config_path(project_root, scenario["dataset"])),
        "--unknown-classes",
        scenario["unknown_attack_family"],
        "--benign-class",
        scenario["benign_label"],
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        "4000",
        "--estimators",
        str(policy["estimators"]),
        "--jobs",
        str(policy["jobs"]),
        "--known-acceptance",
        str(policy["known_acceptance"]),
        "--risk-selection",
        policy["risk_selection"],
        "--pseudo-unknown-max-alpha",
        str(policy["pseudo_unknown_max_alpha"]),
        "--pseudo-unknown-min-fold-gain",
        str(policy["pseudo_unknown_min_fold_gain"]),
        "--boundary-hard-pseudo-fraction",
        str(policy["boundary_hard_pseudo_fraction"]),
        "--boundary-interpolation",
        str(policy["boundary_interpolation"]),
        "--boundary-max-per-task",
        str(policy["boundary_max_per_task"]),
        "--boundary-training-objective",
        policy["boundary_training_objective"],
        "--risk-policy-name",
        "strict_v4_mdr_external_pairwise_v1",
        "--seed",
        str(scenario["seed"]),
        "--output-dir",
        "replaced_by_capture",
    ]


def capture_command(
    *,
    python: str,
    project_root: Path,
    capture_dir: Path,
    scenario: Dict[str, Any],
    protocol: Dict[str, Any],
) -> list[str]:
    mdr = protocol["mdr_policy"]
    return [
        python,
        str(project_root / "capture_mdr_caeos_runtime.py"),
        "--clean-trainer",
        str(project_root / "train_hybrid_open_set.py"),
        "--robust-trainer",
        str(project_root / "train_mdr_caeos_open_set.py"),
        "--capture-dir",
        str(capture_dir),
        "--suite",
        scenario["dataset"],
        "--scenario",
        scenario["unknown_attack_family"],
        "--weight",
        str(mdr["augmentation_weight"]),
        "--sample-fraction",
        str(mdr["sample_fraction"]),
        "--training-seed",
        str(scenario["seed"]),
        "--augmentation-seed",
        str(scenario["augmentation_seed"]),
        "--health-quantile",
        str(mdr["health_quantile"]),
        "--validation-corruption-seed",
        str(scenario["validation_profile_seed"]),
        "--",
        *base_arguments(
            project_root, scenario, protocol["pairwise_runtime_policy"]
        ),
    ]


def opendetect_command(
    *,
    python: str,
    project_root: Path,
    output: Path,
    scenario: Dict[str, Any],
    policy: Dict[str, Any],
) -> list[str]:
    return [
        python,
        str(project_root / "train_neural_open_set.py"),
        "--dataset",
        "tabular",
        "--csv",
        scenario["csv"],
        "--config",
        str(config_path(project_root, scenario["dataset"])),
        "--unknown-classes",
        scenario["unknown_attack_family"],
        "--benign-class",
        scenario["benign_label"],
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        "4000",
        "--model",
        "opendetect",
        "--epochs",
        str(policy["epochs"]),
        "--patience",
        str(policy["patience"]),
        "--hidden-dim",
        str(policy["hidden_dim"]),
        "--embedding-dim",
        str(policy["embedding_dim"]),
        "--known-acceptance",
        str(policy["known_acceptance"]),
        "--seed",
        str(scenario["seed"]),
        "--device",
        "auto",
        "--output-dir",
        str(output),
    ]


def run_command(command: list[str], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / "execution.log"
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"command": command}) + "\n")
        handle.flush()
        completed = subprocess.run(
            command, stdout=handle, stderr=subprocess.STDOUT
        )
    if completed.returncode != 0:
        failure = {
            "schema_version": (
                "strict_v4_mdr_external_execution_failure_v1"
            ),
            "returncode": completed.returncode,
            "command": command,
            "log_sha256": file_hash(log),
        }
        (directory / "failure.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError(f"MDR external command failed: {directory}")


def require_clean_or_complete(
    directory: Path, required: list[str]
) -> bool:
    if not directory.exists():
        return False
    files = [path for path in directory.rglob("*") if path.is_file()]
    if not files:
        return False
    missing = [name for name in required if not (directory / name).is_file()]
    if missing:
        raise ValueError(
            f"partial MDR external output at {directory}: {missing}"
        )
    return True


def write_provenance(
    *,
    output: Path,
    protocol: Dict[str, Any],
    scenario: Dict[str, Any],
    method: str,
    command: list[str],
) -> None:
    metrics = output / "metrics.json"
    value = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_provenance_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "dataset": scenario["dataset"],
        "unknown_attack_family": scenario["unknown_attack_family"],
        "seed": int(scenario["seed"]),
        "method": method,
        "csv_sha256": scenario["csv_sha256"],
        "sidecar_sha256": scenario["sidecar_sha256"],
        "metrics_sha256": file_hash(metrics),
        "command": command,
        "unknown_or_test_metrics_used_for_configuration": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    (output / "provenance.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> None:
    protocol = load(args.protocol)
    verify_protocol(protocol, args.project_root)
    completed = 0
    for scenario in protocol["scenarios"]:
        if (
            file_hash(Path(scenario["csv"])) != scenario["csv_sha256"]
            or file_hash(Path(scenario["sidecar"]))
            != scenario["sidecar_sha256"]
        ):
            raise ValueError("MDR external prepared input SHA changed")
        block = (
            args.output_root
            / scenario["dataset"]
            / (
                f"{slug(scenario['unknown_attack_family'])}_"
                f"seed{scenario['seed']}"
            )
        )
        capture_dir = block / "mdr_capture"
        candidate = block / "mdr_caeos_v1"
        comparator = block / "opendetect"
        capture_cmd = capture_command(
            python=args.python,
            project_root=args.project_root,
            capture_dir=capture_dir,
            scenario=scenario,
            protocol=protocol,
        )
        if not require_clean_or_complete(
            capture_dir,
            [
                "capture_manifest.json",
                "mdr_runtime.joblib",
                "evaluation_inputs.npz",
            ],
        ):
            run_command(capture_cmd, capture_dir)
        candidate_cmd = [
            args.python,
            str(args.project_root / "evaluate_mdr_external_runtime.py"),
            "--capture-dir",
            str(capture_dir),
            "--protocol",
            str(args.protocol),
            "--dataset",
            scenario["dataset"],
            "--unknown-attack-family",
            scenario["unknown_attack_family"],
            "--seed",
            str(scenario["seed"]),
            "--output",
            str(candidate / "metrics.json"),
        ]
        if not require_clean_or_complete(
            candidate, ["metrics.json", "provenance.json"]
        ):
            run_command(candidate_cmd, candidate)
            write_provenance(
                output=candidate,
                protocol=protocol,
                scenario=scenario,
                method="mdr_caeos_v1",
                command=candidate_cmd,
            )
        comparator_cmd = opendetect_command(
            python=args.python,
            project_root=args.project_root,
            output=comparator,
            scenario=scenario,
            policy=protocol["opendetect_policy"],
        )
        if not require_clean_or_complete(
            comparator, ["metrics.json", "provenance.json"]
        ):
            run_command(comparator_cmd, comparator)
            write_provenance(
                output=comparator,
                protocol=protocol,
                scenario=scenario,
                method="opendetect",
                command=comparator_cmd,
            )
        completed += 2
    if (
        completed != protocol["expected_formal_runs"]
        or list(args.output_root.glob("**/failure.json"))
    ):
        raise ValueError("MDR external execution coverage/failure gate failed")
    (args.output_root / "execution_complete").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", default="python")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
