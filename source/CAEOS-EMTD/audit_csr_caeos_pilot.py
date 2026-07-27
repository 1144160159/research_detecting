from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_csr_caeos_pilot import (
    clean_admission,
    load_json,
    summarize,
)


def audit(
    design: Dict[str, Any],
    admission: Dict[str, Any],
    summary: Dict[str, Any],
    capture_paths: List[Path],
    evaluation_paths: List[Path],
    *,
    implementation_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    recomputed_admission = clean_admission(design, capture_paths)
    if admission != recomputed_admission:
        raise ValueError("CSR clean admission differs from recomputation")
    if admission.get("passes") is not True:
        raise ValueError("CSR test evaluation requires passing clean admission")
    recomputed_summary = summarize(
        design, recomputed_admission, evaluation_paths
    )
    if summary != recomputed_summary:
        raise ValueError("CSR pilot summary differs from recomputation")
    checks = {
        "design_canonical": (
            design.get("manifest_sha256") == canonical_hash(design)
        ),
        "admission_canonical_and_recomputed": (
            admission.get("manifest_sha256") == canonical_hash(admission)
        ),
        "summary_canonical_and_recomputed": (
            summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "capture_count_14": len(capture_paths) == 14,
        "evaluation_count_84": len(evaluation_paths) == 84,
        "implementation_hashes_nonempty": bool(
            implementation_file_sha256
        )
        and all(
            len(str(value)) == 64
            for value in implementation_file_sha256.values()
        ),
        "zero_unknown_or_test_selection": (
            admission.get("unknown_or_test_labels_used") is False
            and summary["checks"].get(
                "zero_unknown_or_test_labels_used_for_routing_or_selection"
            )
            is True
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_pilot_audit_v1",
        "state": "complete",
        "design_manifest_sha256": design["manifest_sha256"],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "capture_manifest_file_sha256": {
            str(path): file_hash(path) for path in sorted(capture_paths)
        },
        "evaluation_file_sha256": {
            str(path): file_hash(path) for path in sorted(evaluation_paths)
        },
        "implementation_file_sha256": implementation_file_sha256,
        "checks": checks,
        "passes": all(checks.values()),
        "scientific_effect_gate_passes": bool(summary["passes"]),
        "expand_to_full102": bool(summary["expand_to_full102"]),
        "audit_pass_does_not_imply_positive_effect": True,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    implementation_hashes = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementation_hashes[name] = file_hash(project_root / relative)
    value = audit(
        load_json(args.design),
        load_json(args.admission),
        load_json(args.summary),
        sorted(args.capture_root.rglob("capture_manifest.json")),
        sorted(args.evaluation_root.rglob("evaluation.json")),
        implementation_file_sha256=implementation_hashes,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
