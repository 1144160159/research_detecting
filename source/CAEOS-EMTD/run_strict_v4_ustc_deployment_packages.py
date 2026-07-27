from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_ustc_deployment_package_design import (
    PAIRWISE,
    VGRF,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def replace_value(command: list[str], flag: str, value: str) -> None:
    index = command.index(flag)
    command[index + 1] = value


def run_logged(
    command: list[str],
    cwd: Path,
    log_path: Path,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed with exit {completed.returncode}: {log_path}"
        )


def validate_existing_record(
    record_path: Path,
    protocol: dict[str, Any],
    expected_package_id: str,
) -> bool:
    if not record_path.is_file():
        return False
    record = load(record_path)
    if (
        record.get("schema_version")
        != "strict_v4_ustc_deployment_package_record_v1"
        or record.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or record.get("package_id") != expected_package_id
        or record.get("selected_algorithm")
        != protocol["selection"]["selected_algorithm"]
    ):
        raise ValueError(f"existing package record mismatch: {record_path}")
    required_audits = {"pairwise", "selected", "parrot_feature_contract"}
    if record["selected_algorithm"] == VGRF:
        required_audits.add("vgrf")
    if not required_audits.issubset(record.get("audits", {})):
        raise ValueError(f"existing package audits are incomplete: {record_path}")
    artifact = Path(record["selected_artifact"])
    if (
        not artifact.is_file()
        or file_hash(artifact) != record["selected_artifact_sha256"]
    ):
        raise ValueError(f"existing selected artifact mismatch: {artifact}")
    for entry in record["audits"].values():
        path = Path(entry["path"])
        if not path.is_file() or file_hash(path) != entry["sha256"]:
            raise ValueError(f"existing package audit mismatch: {path}")
        if load(path).get("passes") is not True:
            raise ValueError(f"existing package audit did not pass: {path}")
    return True


def pairwise_arguments(
    project_root: Path,
    package: dict[str, Any],
    reference_run: Path,
) -> tuple[str, list[str]]:
    provenance_path = project_root / package["source_provenance"]
    if file_hash(provenance_path) != package["source_provenance_sha256"]:
        raise ValueError(f"source provenance mismatch: {provenance_path}")
    if file_hash(Path(package["csv"])) != package["csv_sha256"]:
        raise ValueError(f"source CSV mismatch: {package['package_id']}")
    if file_hash(project_root / package["config"]) != package["config_sha256"]:
        raise ValueError(f"source config mismatch: {package['package_id']}")
    provenance = load(provenance_path)
    command = list(provenance["command"][1:])
    trainer = command.pop(0)
    if Path(trainer).name != "train_hybrid_open_set.py":
        raise ValueError(f"unexpected source trainer: {trainer}")
    replace_value(command, "--seed", str(package["training_seed"]))
    replace_value(command, "--output-dir", str(reference_run.resolve()))
    replace_value(
        command,
        "--risk-policy-name",
        "strict_v4_ustc_deployment_packages_v1",
    )
    return trainer, command


def verify_capture_arguments(
    capture_manifest_path: Path,
    expected_arguments: list[str],
) -> dict[str, Any]:
    manifest = load(capture_manifest_path)
    if (
        manifest.get("schema_version")
        != "strict_v4_pairwise_deployment_capture_v3"
        or manifest.get("trainer_arguments") != expected_arguments
    ):
        raise ValueError(
            f"Pairwise capture arguments mismatch: {capture_manifest_path}"
        )
    return manifest


def vgrf_parameter_arguments(parameters: dict[str, Any]) -> list[str]:
    mapping = (
        ("--shrinkage", "empirical_bayes_shrinkage"),
        ("--minimum-reliability", "minimum_reliability"),
        ("--risk-blend", "risk_blend"),
        ("--known-rejection-quantile", "known_rejection_quantile"),
        ("--minimum-f1-gain", "minimum_f1_gain"),
        (
            "--maximum-correct-risk-increase",
            "maximum_correct_risk_increase",
        ),
        ("--minimum-auc-gain", "minimum_auc_gain"),
        ("--minimum-separation-gain", "minimum_separation_gain"),
        ("--minimum-strict-proxy-gain", "minimum_strict_proxy_gain"),
    )
    result = []
    for flag, name in mapping:
        result.extend([flag, str(parameters[name])])
    return result


def execute_package(
    protocol: dict[str, Any],
    package: dict[str, Any],
    project_root: Path,
    python: str,
) -> None:
    package_root = project_root / package["package_root"]
    package_root.mkdir(parents=True, exist_ok=True)
    record_path = package_root / "package_record.json"
    if validate_existing_record(
        record_path, protocol, package["package_id"]
    ):
        print(f"validated existing {package['package_id']}", flush=True)
        return

    reference_run = project_root / package["pairwise_reference_run"]
    pairwise_capture = package_root / "pairwise_capture"
    trainer, trainer_arguments = pairwise_arguments(
        project_root, package, reference_run
    )
    pairwise_manifest_path = pairwise_capture / "capture_manifest.json"
    if not pairwise_manifest_path.is_file():
        run_logged(
            [
                python,
                "capture_pairwise_deployment_bundle.py",
                "--trainer",
                trainer,
                "--capture-dir",
                str(pairwise_capture),
                "--",
                *trainer_arguments,
            ],
            project_root,
            package_root / "pairwise_capture.log",
        )
    pairwise_manifest = verify_capture_arguments(
        pairwise_manifest_path, trainer_arguments
    )
    pairwise_audit_path = package_root / "pairwise_independent_audit.json"
    run_logged(
        [
            python,
            "audit_pairwise_deployment_bundle.py",
            "--capture-dir",
            str(pairwise_capture),
            "--output",
            str(pairwise_audit_path),
        ],
        project_root,
        package_root / "pairwise_audit.log",
    )
    if load(pairwise_audit_path).get("passes") is not True:
        raise ValueError(f"Pairwise audit failed: {package['package_id']}")

    selected = protocol["selection"]["selected_algorithm"]
    selected_artifact = (
        pairwise_capture / pairwise_manifest["deployment_artifact"]
    )
    selected_audit_path = pairwise_audit_path
    vgrf_audit_path = None
    if selected == VGRF:
        vgrf_capture = package_root / "vgrf_capture"
        vgrf_manifest_path = vgrf_capture / "capture_manifest.json"
        binding = protocol["vgrf_binding"]
        if not vgrf_manifest_path.is_file():
            run_logged(
                [
                    python,
                    "build_vgrf_deployment_bundle.py",
                    "--pairwise-capture-dir",
                    str(pairwise_capture),
                    "--reference-run-dir",
                    str(reference_run),
                    "--output-dir",
                    str(vgrf_capture),
                    "--source-protocol-manifest-sha256",
                    binding["confirmation_protocol_manifest_sha256"],
                    *vgrf_parameter_arguments(
                        binding["known_only_parameters"]
                    ),
                ],
                project_root,
                package_root / "vgrf_build.log",
            )
        vgrf_manifest = load(vgrf_manifest_path)
        selected_artifact = (
            vgrf_capture / vgrf_manifest["deployment_artifact"]
        )
        vgrf_audit_path = package_root / "vgrf_independent_audit.json"
        run_logged(
            [
                python,
                "audit_vgrf_deployment_bundle.py",
                "--capture-dir",
                str(vgrf_capture),
                "--output",
                str(vgrf_audit_path),
            ],
            project_root,
            package_root / "vgrf_audit.log",
        )
        if load(vgrf_audit_path).get("passes") is not True:
            raise ValueError(f"VGRF audit failed: {package['package_id']}")
        selected_audit_path = vgrf_audit_path
    elif selected != PAIRWISE:
        raise ValueError(f"unsupported selected algorithm: {selected}")

    contract_path = package_root / "parrot_feature_contract_audit.json"
    run_logged(
        [
            python,
            "audit_pairwise_parrot_feature_contract.py",
            "--deployment-artifact",
            str(selected_artifact),
            "--source-config",
            str(project_root / package["config"]),
            "--parrot-protocol",
            str(
                project_root
                / protocol["parrot_feature_contract"]["protocol_path"]
            ),
            "--output",
            str(contract_path),
        ],
        project_root,
        package_root / "parrot_contract_audit.log",
    )
    if load(contract_path).get("passes") is not True:
        raise ValueError(f"PARROT contract failed: {package['package_id']}")

    audits = {
        "pairwise": {
            "path": str(pairwise_audit_path.resolve()),
            "sha256": file_hash(pairwise_audit_path),
        },
        "selected": {
            "path": str(selected_audit_path.resolve()),
            "sha256": file_hash(selected_audit_path),
        },
        "parrot_feature_contract": {
            "path": str(contract_path.resolve()),
            "sha256": file_hash(contract_path),
        },
    }
    if vgrf_audit_path is not None:
        audits["vgrf"] = {
            "path": str(vgrf_audit_path.resolve()),
            "sha256": file_hash(vgrf_audit_path),
        }
    record = {
        "schema_version": "strict_v4_ustc_deployment_package_record_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "package_id": package["package_id"],
        "suite": package["suite"],
        "scenario": package["scenario"],
        "unknown_classes": package["unknown_classes"],
        "training_seed": package["training_seed"],
        "selected_algorithm": selected,
        "selected_artifact": str(selected_artifact.resolve()),
        "selected_artifact_sha256": file_hash(selected_artifact),
        "selected_artifact_bytes": selected_artifact.stat().st_size,
        "pairwise_capture_manifest_sha256": file_hash(
            pairwise_manifest_path
        ),
        "audits": audits,
        "formal_model_metrics_admitted": 0,
        "external_execution_admitted": False,
        "storage_policy": "gpu_private_do_not_publish",
    }
    temporary = record_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(record_path)
    print(f"completed {package['package_id']}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_ustc_deployment_package_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid USTC deployment package protocol")
    for name, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"deployment implementation drift: {name}")
    for package in protocol["package_matrix"]["inputs"]:
        execute_package(protocol, package, project_root, args.python)
    run_root = Path(protocol["output_policy"]["run_root"])
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "packages_execution_complete").touch()


if __name__ == "__main__":
    main()
