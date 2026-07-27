from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import load
from summarize_mdr_caeos_confirmation import final_selection, summarize


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    selection: Dict[str, Any],
    evaluation_root: Path,
    project_root: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR confirmation protocol required")
    implementation_checks = {}
    for name, relative in protocol["implementation"].items():
        expected = protocol["implementation_sha256"][name]
        actual = file_hash(project_root / relative)
        implementation_checks[name] = {
            "expected": expected,
            "actual": actual,
            "passes": actual == expected,
        }
    evaluation_paths = sorted(evaluation_root.rglob("evaluation.json"))
    recomputed_summary = summarize(protocol, evaluation_paths)
    recomputed_selection = final_selection(protocol, recomputed_summary)
    checks = {
        "implementation_sha256": all(
            record["passes"] for record in implementation_checks.values()
        ),
        "evaluation_count": len(evaluation_paths) == 1836,
        "summary_canonical_hash": (
            summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "summary_exactly_recomputed": recomputed_summary == summary,
        "selection_canonical_hash": (
            selection.get("manifest_sha256") == canonical_hash(selection)
        ),
        "selection_exactly_recomputed": recomputed_selection == selection,
        "validation_passes": (
            summary.get("validation", {}).get("passes") is True
        ),
        "claim_boundary_preserved": (
            summary.get("claim_boundary", {}).get(
                "confirmation_success_does_not_establish_comprehensive_sota"
            )
            is True
            and selection.get("comprehensive_sota_confirmed") is False
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_confirmation_audit_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "selection_manifest_sha256": selection["manifest_sha256"],
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
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol),
        load(args.summary),
        load(args.selection),
        args.evaluation_root,
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
