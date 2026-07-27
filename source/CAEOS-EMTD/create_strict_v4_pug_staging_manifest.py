from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


INSTALL_FILES = (
    "train_hybrid_open_set.py",
    "caeos/pseudo_unknown_gated_continuous.py",
    "create_strict_v4_pug_execution_protocol.py",
    "evaluate_strict_v4_pug_confirmation.py",
    "inspect_strict_v4_pug_run.py",
    "watch_strict_v4_pug_confirmation.py",
    "scripts/run_strict_v4_pug_confirmation.sh",
)
VERIFY_ONLY_FILES = (
    "train_neural_open_set.py",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "prepare_cic_iot2023_strict.py",
    "prepare_group_supported_cache.py",
    "caeos/continuous_outer_min_p.py",
)
EXPECTED_CURRENT_TRAINER_SHA256 = (
    "abf613b43bdab9dd12764cb0b3359ba84fed0d4e9e29e686b86e9823dca458f2"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def create_manifest(
    *,
    root: Path,
    protocol_path: Path,
    deployer_path: Path,
) -> dict[str, Any]:
    protocol = load(protocol_path)
    if (
        protocol.get("schema_version") != "strict_v4_pug_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(protocol.get("tasks", [])) != 18
    ):
        raise ValueError("canonical PUG execution protocol required")
    implementation = protocol["implementation_sha256"]
    expected_files = set(INSTALL_FILES) | set(VERIFY_ONLY_FILES)
    if set(implementation) != expected_files:
        raise ValueError("PUG implementation closure drifted")
    for relative, expected in implementation.items():
        path = root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"local implementation drifted: {relative}")
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_pug_staging_manifest_v1",
        "state": "staged_before_krc_terminal_resource_release",
        "execution_protocol": {
            "path": "results/strict_v4_pug_confirmation_v1/execution_protocol.json",
            "canonical_sha256": protocol["manifest_sha256"],
            "file_sha256": file_hash(protocol_path),
        },
        "deployer": {
            "path": deployer_path.relative_to(root).as_posix(),
            "file_sha256": file_hash(deployer_path),
        },
        "install_files": {
            relative: implementation[relative] for relative in INSTALL_FILES
        },
        "verify_only_files": {
            relative: implementation[relative]
            for relative in VERIFY_ONLY_FILES
        },
        "admission": {
            "krc_summary_and_audit_required": True,
            "all_busy_training_processes_absent": True,
            "resource_idle_consecutive_polls": 3,
            "unexpected_main_trainer_drift_rejected": True,
            "expected_current_main_trainer_sha256": (
                EXPECTED_CURRENT_TRAINER_SHA256
            ),
            "target_trainer_sha256": implementation[
                "train_hybrid_open_set.py"
            ],
            "protocol_installed_last": True,
        },
        "claim_boundary": {
            "staging_is_not_execution": True,
            "staging_is_not_candidate_effect": True,
            "pairwise_remains_incumbent": True,
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--deployer",
        type=Path,
        default=Path("deploy_strict_v4_pug_after_krc.py"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/staging_manifest.json"
        ),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    output = resolve(args.output)
    manifest = create_manifest(
        root=root,
        protocol_path=resolve(args.protocol),
        deployer_path=resolve(args.deployer),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest_sha256": manifest["manifest_sha256"],
                "file_sha256": file_hash(output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
