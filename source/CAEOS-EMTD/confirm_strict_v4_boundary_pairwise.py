from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import confirm_strict_v4_boundary_pseudo_unknown as base
from analyze_strict_v4_pseudo_unknown_development import canonical_hash
from summarize_paired_confirmation import aggregate


EXPECTED_POLICY = "strict_v4_boundary_pairwise_confirmation_v1"
ORIGINAL_VALIDATE_RUNTIME = base.validate_runtime


def load_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_boundary_pairwise_candidate_v1":
        raise ValueError("unexpected pairwise boundary manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("pairwise boundary candidate is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("pairwise boundary manifest SHA mismatch")
    candidate = payload["candidate"]
    if candidate.get("training_objective") != "pairwise":
        raise ValueError("pairwise boundary objective is not frozen")
    for relative, expected in candidate["implementation_sha256"].items():
        actual = hashlib.sha256((project_root / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    confirmation = payload["confirmation"]
    if confirmation.get("seed_disjoint") is not True:
        raise ValueError("confirmation seeds are not disjoint")
    if confirmation.get("scenario_disjoint_from_pairwise_development") is not True:
        raise ValueError("confirmation scenarios are not disjoint")
    return payload


def validate_runtime(
    payload: dict[str, Any], manifest: dict[str, Any], label: str
) -> dict[str, Any]:
    protocol = ORIGINAL_VALIDATE_RUNTIME(payload, manifest, label)
    learned = payload["risk_selection_details"]["pseudo_unknown_learned_blend"]
    if learned.get("training_objective") != "pairwise":
        raise ValueError(f"pairwise runtime objective mismatch for {label}")
    distribution = learned.get("training_distribution", {})
    if distribution.get("objective") != "pairwise_logistic_ranking":
        raise ValueError(f"pairwise training distribution mismatch for {label}")
    return protocol


def render(report: dict[str, Any]) -> str:
    return base.render(report).replace(
        "# Strict-v4 boundary pseudo-unknown confirmation",
        "# Strict-v4 pairwise boundary pseudo-unknown confirmation",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, args.project_root.resolve())
    base.EXPECTED_POLICY = EXPECTED_POLICY
    base.validate_runtime = validate_runtime
    rows, validation = base.build_rows(args.root, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, 20260718)
    suites = {
        suite: aggregate(
            [row for row in rows if row["suite"] == suite],
            args.bootstrap_repetitions,
            20260718,
        )
        for suite in manifest["confirmation"]["scenarios"]
    }
    endpoints = Counter(row["candidate_selected"] for row in rows)
    decision = base.make_decision(combined, suites, endpoints)
    decision["frozen_gate"] = EXPECTED_POLICY
    result = {
        "schema_version": "strict_v4_boundary_pairwise_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "rows": rows,
        "decision": decision,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
