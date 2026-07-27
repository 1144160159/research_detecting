from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_medaf_tabular_pilot_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
)
from summarize_strict_v4_medaf_tabular_pilot import (
    SCHEMA as SUMMARY_SCHEMA,
    summarize,
)


SCHEMA = "strict_v4_medaf_tabular_pilot_audit_v1"


def audit(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    summary: Dict[str, Any],
    run_root: Path,
    project_root: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version") != PROTOCOL_SCHEMA
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("invalid MEDAF execution protocol")
    if (
        design.get("manifest_sha256")
        != protocol["design_manifest_sha256"]
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("MEDAF design binding mismatch")
    if (
        summary.get("schema_version") != SUMMARY_SCHEMA
        or summary.get("manifest_sha256") != canonical_hash(summary)
    ):
        raise ValueError("invalid MEDAF summary")
    implementation_checks = {}
    for name, relative in protocol["implementation"].items():
        expected = protocol["implementation_sha256"][name]
        actual = file_hash(project_root / relative)
        implementation_checks[name] = {
            "expected": expected,
            "actual": actual,
            "passes": actual == expected,
        }
    recomputed = summarize(design, protocol, run_root)
    run_manifests = list(run_root.rglob("run_manifest.json"))
    failures = list(run_root.rglob("failure.json"))
    checks = {
        "implementation_sha256": all(
            record["passes"] for record in implementation_checks.values()
        ),
        "summary_canonical_hash": (
            summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "summary_exactly_recomputed": recomputed == summary,
        "run_manifest_count": len(run_manifests) == 42,
        "failure_count": len(failures) == 0,
        "validation_passes": (
            summary.get("validation", {}).get("passes") is True
        ),
        "claim_boundary_preserved": (
            summary.get("claim_boundary", {}).get(
                "pilot_success_does_not_establish_sota"
            )
            is True
            and summary.get("claim_boundary", {}).get(
                "adapter_is_not_native_medaf_reproduction"
            )
            is True
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "method": "medaf_tabular_adapter",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "implementation_checks": implementation_checks,
        "checks": checks,
        "passes": all(checks.values()),
        "effect_decision_inherited_without_override": summary["decision"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol),
        load(args.design),
        load(args.summary),
        args.run_root.resolve(),
        args.project_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
