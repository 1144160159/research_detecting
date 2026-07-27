from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--accuracy-audit", type=Path, required=True)
    parser.add_argument("--post30-compatibility", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    accuracy = load(args.accuracy_audit)
    compatibility = load(args.post30_compatibility)
    if (
        accuracy.get("schema_version")
        != "strict_v4_comprehensive_sota_audit_v12"
        or accuracy.get("manifest_sha256") != canonical_hash(accuracy)
    ):
        raise ValueError("invalid post-30 accuracy audit")
    if (
        compatibility.get("schema_version")
        != "strict_v4_post30_supersession_compatibility_audit_v1"
        or compatibility.get("manifest_sha256")
        != canonical_hash(compatibility)
        or compatibility.get("old_audit_manifest_sha256")
        != accuracy["manifest_sha256"]
        or compatibility.get("old_audit_file_sha256")
        != file_hash(args.accuracy_audit)
        or compatibility.get("post30_baseline_coverage_compatible")
        is not True
    ):
        raise ValueError("invalid post-30 compatibility binding")
    final_root = project / "results/strict_v4_final_paper_readiness"
    if (final_root / "audit.json").exists():
        raise ValueError("readiness protocol must freeze before audit output")
    names = (
        "create_strict_v4_final_readiness_post30_compat_protocol.py",
        "audit_strict_v4_final_paper_readiness_post30_compat.py",
        "audit_strict_v4_final_paper_readiness.py",
        "scripts/wait_and_audit_strict_v4_final_readiness_post30_compat.sh",
        "scripts/wait_and_run_strict_v4_postefficiency_claim_chain_v2.sh",
    )
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_final_readiness_post30_compat_protocol_v1"
        ),
        "status": (
            "frozen_before_final_readiness_output_after_post30_"
            "compatibility"
        ),
        "project_root": str(project),
        "legacy_accuracy_manifest_sha256": accuracy["manifest_sha256"],
        "legacy_post30_coverage_value": accuracy.get(
            "post30_baseline_coverage_complete"
        ),
        "compatibility_manifest_sha256": compatibility[
            "manifest_sha256"
        ],
        "frozen_input_file_sha256": {
            "accuracy_audit": file_hash(args.accuracy_audit),
            "post30_compatibility": file_hash(
                args.post30_compatibility
            ),
        },
        "implementation_sha256": {
            name: file_hash(project / name) for name in names
        },
        "claim_boundary": {
            "legacy_accuracy_audit_is_not_modified": True,
            "compatibility_repairs_protocol_identity_only": True,
            "effect_and_system_gates_are_not_relaxed": True,
        },
        "audit_output_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
