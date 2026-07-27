from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


Identity = Tuple[str, str, float]


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def expected_identities(design: Dict[str, Any]) -> set[Identity]:
    weights = {
        float(value)
        for value in design["mechanism"]["training_augmentation_weight_grid"]
    }
    return {
        (str(suite), str(scenario), weight)
        for suite, scenarios in design["pilot"]["scenarios"].items()
        for scenario in scenarios
        for weight in weights
    }


def identity_key(identity: Identity) -> str:
    suite, scenario, weight = identity
    return f"{suite}/{scenario}/weight_{weight:.3f}"


def resolve_member(root: Path, relative: str) -> Path:
    root_resolved = root.resolve()
    path = (root / relative).resolve()
    if path != root_resolved and root_resolved not in path.parents:
        raise ValueError(f"capture member escapes its directory: {relative}")
    return path


def audit(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    capture_paths: Iterable[Path],
    project_root: Path,
    auditor_path: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR pilot v2 protocol required")
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
        or design.get("manifest_sha256")
        != protocol.get("design_manifest_sha256")
    ):
        raise ValueError("canonical protocol-bound MDR design required")

    implementation_checks = {}
    for name, relative in sorted(protocol["implementation"].items()):
        path = project_root / relative
        expected_sha = protocol["implementation_sha256"][name]
        actual_sha = file_hash(path)
        implementation_checks[name] = {
            "path": str(relative),
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            "passes": actual_sha == expected_sha,
        }

    expected = expected_identities(design)
    observed: Dict[Identity, Dict[str, Any]] = {}
    duplicate_identities = []
    invalid_records = []
    for path in sorted(capture_paths):
        manifest_file_sha256 = file_hash(path)
        manifest = load(path)
        task = manifest.get("task", {})
        identity = (
            str(task.get("suite")),
            str(task.get("scenario")),
            float(manifest.get("weight", -1.0)),
        )
        if identity in observed:
            duplicate_identities.append(identity_key(identity))
            continue

        record_checks = {
            "schema_and_state": (
                manifest.get("schema_version")
                == "strict_v4_mdr_caeos_runtime_capture_v1"
                and manifest.get("state") == "complete"
            ),
            "identity_expected": identity in expected,
            "roundtrip_passes": (
                manifest.get("roundtrip", {}).get("passes") is True
            ),
            "training_selection_leakage_absent": (
                manifest.get(
                    "unknown_or_test_labels_used_for_training_selection_or_calibration"
                )
                is False
            ),
        }
        profile = manifest.get("known_validation_profile", {})
        record_checks["known_validation_profile_contract"] = (
            profile.get("schema_version")
            == "strict_v4_mdr_known_validation_profile_v1"
            and profile.get("record_count") == 15
            and profile.get("known_validation_labels_used") is True
            and profile.get("unknown_or_test_labels_used") is False
        )

        artifact = resolve_member(
            path.parent, str(manifest.get("runtime_artifact", ""))
        )
        inputs = resolve_member(
            path.parent, str(manifest.get("evaluation_inputs", ""))
        )
        record_checks["runtime_artifact_sha256"] = (
            artifact.is_file()
            and file_hash(artifact) == manifest.get("runtime_artifact_sha256")
        )
        record_checks["evaluation_inputs_sha256"] = (
            inputs.is_file()
            and file_hash(inputs)
            == manifest.get("evaluation_inputs_sha256")
        )
        passes = all(record_checks.values())
        if not passes:
            invalid_records.append(identity_key(identity))
        observed[identity] = {
            "identity": identity_key(identity),
            "manifest_path": str(path),
            "manifest_file_sha256": manifest_file_sha256,
            "runtime_artifact_sha256": manifest.get(
                "runtime_artifact_sha256"
            ),
            "evaluation_inputs_sha256": manifest.get(
                "evaluation_inputs_sha256"
            ),
            "checks": record_checks,
            "passes": passes,
        }

    observed_set = set(observed)
    missing = sorted(identity_key(value) for value in expected - observed_set)
    extra = sorted(identity_key(value) for value in observed_set - expected)
    checks = {
        "protocol_and_design_canonical": True,
        "protocol_implementation_sha256": all(
            value["passes"] for value in implementation_checks.values()
        ),
        "duplicate_identity_count_zero": not duplicate_identities,
        "unexpected_identity_count_zero": not extra,
        "observed_capture_integrity": not invalid_records,
        "complete_capture_matrix": (
            observed_set == expected and not duplicate_identities
        ),
        "effect_metrics_read": False,
        "known_validation_effect_values_read": False,
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_capture_integrity_audit_v1",
        "state": (
            "complete_capture_matrix"
            if checks["complete_capture_matrix"]
            else "partial_capture_snapshot"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "auditor_file_sha256": file_hash(auditor_path),
        "expected_capture_count": len(expected),
        "observed_capture_count": len(observed),
        "missing_capture_count": len(missing),
        "unexpected_capture_count": len(extra),
        "duplicate_identity_count": len(duplicate_identities),
        "invalid_record_count": len(invalid_records),
        "missing_identities": missing,
        "unexpected_identities": extra,
        "duplicate_identities": sorted(duplicate_identities),
        "invalid_records": sorted(invalid_records),
        "capture_records": [
            observed[identity] for identity in sorted(observed)
        ],
        "implementation_checks": implementation_checks,
        "checks": checks,
        "observed_integrity_passes": all(
            checks[name]
            for name in (
                "protocol_implementation_sha256",
                "duplicate_identity_count_zero",
                "unexpected_identity_count_zero",
                "observed_capture_integrity",
            )
        ),
        "passes": all(
            checks[name]
            for name in (
                "protocol_implementation_sha256",
                "duplicate_identity_count_zero",
                "unexpected_identity_count_zero",
                "observed_capture_integrity",
                "complete_capture_matrix",
            )
        ),
        "claim_boundary": {
            "integrity_audit_does_not_read_effect_metrics": True,
            "partial_snapshot_does_not_authorize_weight_selection": True,
            "complete_integrity_does_not_establish_algorithm_effect": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol),
        load(args.design),
        args.capture_root.rglob("capture_manifest.json"),
        args.project_root.resolve(),
        Path(__file__).resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
