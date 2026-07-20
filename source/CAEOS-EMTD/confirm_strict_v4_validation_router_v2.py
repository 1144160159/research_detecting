from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_strict_v4_validation_router import REFERENCE, canonical_hash, select_endpoint, validation_features
from confirm_strict_v4_validation_router import (
    EXPECTED_POLICY,
    REQUIRED_ARTIFACTS,
    decision,
    metric_report,
    render_markdown,
)
from summarize_paired_confirmation import aggregate


def load_manifest(path: Path, implementation: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_validation_suite_router_candidate_v1":
        raise ValueError("unexpected suite-router manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("suite-router candidate is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("suite-router manifest internal SHA mismatch")
    actual = hashlib.sha256(implementation.read_bytes()).hexdigest()
    if payload.get("candidate", {}).get("implementation_sha256") != actual:
        raise ValueError("suite-router implementation SHA mismatch")
    if payload.get("candidate", {}).get("runtime_features_use_known_validation_only") is not True:
        raise ValueError("suite-router runtime feature boundary is invalid")
    if payload.get("candidate", {}).get("runtime_routing_uses_known_suite_identity") is not True:
        raise ValueError("suite-router identity boundary is invalid")
    if payload.get("development", {}).get("rule_selection_uses_test_unknown_labels") is not True:
        raise ValueError("suite-router development disclosure is missing")
    if payload.get("confirmation", {}).get("seed_disjoint") is not True:
        raise ValueError("suite-router confirmation seeds are not disjoint")
    return payload


def build_rows(root: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    confirmation = manifest["confirmation"]
    rules = manifest["candidate"]["selected_rules"]
    if set(rules) != set(confirmation["scenarios"]):
        raise ValueError("suite-router rule coverage mismatch")
    rows = []
    fingerprints = set()
    source_metrics = []
    for suite, scenarios in confirmation["scenarios"].items():
        rule = rules[suite]
        for scenario in scenarios:
            for seed in confirmation["seeds"]:
                directory = root / suite / f"{scenario}_seed{seed}"
                missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()]
                if missing:
                    raise ValueError(f"missing artifacts under {directory}: {missing}")
                path = directory / "metrics.json"
                raw = path.read_bytes()
                payload = json.loads(raw.decode("utf-8"))
                if int(payload.get("seed", -1)) != int(seed):
                    raise ValueError(f"seed mismatch under {directory}")
                if payload.get("risk_policy") != EXPECTED_POLICY or payload.get("selected_risk") != REFERENCE:
                    raise ValueError(f"reference policy mismatch under {directory}")
                if payload.get("risk_selection_details", {}).get("unknown_or_test_labels_used_for_selection") is not False:
                    raise ValueError(f"runtime leakage guard failed under {directory}")
                features = validation_features(directory)
                endpoint = select_endpoint(rule, {"features": features})
                reports = payload.get("reports", {})
                candidate = metric_report(reports.get(endpoint), f"{suite}/{scenario}/{seed}/candidate")
                reference = metric_report(reports.get(REFERENCE), f"{suite}/{scenario}/{seed}/reference")
                selected_report = metric_report(payload.get("selected_report"), f"{suite}/{scenario}/{seed}/selected")
                if selected_report != reference:
                    raise ValueError(f"selected report mismatch under {directory}")
                fingerprint = payload.get("split_metadata", {}).get("split_fingerprint", {}).get("combined")
                if not fingerprint:
                    raise ValueError(f"missing split fingerprint under {directory}")
                fingerprints.add(str(fingerprint))
                source_metrics.append({
                    "path": path.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                })
                rows.append({
                    "suite": suite,
                    "scenario": scenario,
                    "seed": int(seed),
                    "candidate_selected": endpoint,
                    "reference_selected": REFERENCE,
                    "candidate_report": candidate,
                    "reference_report": reference,
                    "validation_router_feature": rule["feature"],
                    "validation_router_value": features[rule["feature"]],
                    "validation_router_threshold": rule["threshold"],
                    "split_fingerprint": str(fingerprint),
                })
    expected = int(confirmation["expected_run_count"])
    if len(rows) != expected:
        raise ValueError(f"suite-router run count mismatch: {len(rows)} != {expected}")
    source_hash = hashlib.sha256(
        json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": sum(len(values) for values in confirmation["scenarios"].values()),
        "seeds": confirmation["seeds"],
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "source_metrics_combined_sha256": source_hash,
        "runtime_features_use_known_validation_only": True,
        "runtime_uses_unknown_or_test_labels": False,
        "scenario_boundary": confirmation["scenario_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Confirm frozen strict-v4 suite-aware validation routers")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--router-implementation", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, args.router_implementation)
    rows, validation = build_rows(args.root, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, args.bootstrap_seed)
    suites = {
        suite: aggregate(
            [row for row in rows if row["suite"] == suite],
            args.bootstrap_repetitions,
            args.bootstrap_seed,
        )
        for suite in sorted(manifest["confirmation"]["scenarios"])
    }
    paths = Counter(row["candidate_selected"] for row in rows)
    result = {
        "schema_version": "strict_v4_validation_suite_router_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "rows": rows,
        "decision": decision(combined, suites, paths, args.nonregression_tolerance),
    }
    result["decision"]["frozen_gate"] = "strict_v4_known_validation_suite_router_confirmation_v1"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
