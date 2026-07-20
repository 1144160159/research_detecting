from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION_FILES = (
    "create_strict_v4_conflict_fdr_audit_protocol.py",
    "audit_strict_v4_conflict_metric_fdr.py",
    "scripts/run_strict_v4_conflict_fdr_audit.sh",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_protocol(
    project_root: Path, parent_protocol: dict[str, Any], observed_audits: int
) -> dict[str, Any]:
    if observed_audits != 0:
        raise ValueError("FDR audit protocol must be frozen at zero audit results")
    if parent_protocol.get("schema_version") != "strict_v4_conflict_metric_protocol_v3":
        raise ValueError("unexpected parent conflict protocol")
    if parent_protocol.get("manifest_sha256") != canonical_hash(parent_protocol):
        raise ValueError("parent conflict protocol SHA mismatch")
    result = {
        "schema_version": "strict_v4_conflict_fdr_audit_protocol_v1",
        "status": "frozen_before_parent_analysis_completion",
        "parent_protocol_manifest_sha256": parent_protocol["manifest_sha256"],
        "expected_parent_analysis_schema": "strict_v4_conflict_metric_analysis_v2",
        "expected_scenarios": 102,
        "fdr_method": "benjamini_hochberg_within_each_metric_across_scenarios",
        "fdr_alpha": 0.05,
        "increment_rule": "positive_coefficient_and_q_below_alpha",
        "paired_test": "one_sided_wilcoxon_d6_greater_than_d5",
        "bootstrap_repetitions": 10000,
        "bootstrap_seed": 20260720,
        "bootstrap_interval": 0.95,
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATION_FILES
        },
        "audit_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def freeze_or_validate(
    output: Path, expected: dict[str, Any], observed_audits: int
) -> dict[str, Any]:
    if output.is_file():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != expected:
            raise ValueError("existing FDR audit protocol differs from current evidence")
        return existing
    if observed_audits != 0:
        raise ValueError("FDR audit protocol must be frozen at zero audit results")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root", type=Path, default=Path(__file__).resolve().parent
    )
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    parent = json.loads(args.parent_protocol.read_text(encoding="utf-8"))
    observed = int((args.output_dir / "fdr_audit.json").is_file())
    expected = create_protocol(args.project_root.resolve(), parent, 0)
    protocol = freeze_or_validate(
        args.output_dir / "fdr_protocol_manifest.json", expected, observed
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
