from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
RUN_PATTERN = re.compile(r"^(?P<scenario>.+)_seed(?P<seed>[0-9]+)$")
MLP_RUN_PATTERN = re.compile(r"^(?P<scenario>.+)_seed(?P<seed>[0-9]+)_mlp$")
MLP_REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "model.pt",
    "provenance.json",
)


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root is not an object: %s" % path)
    return payload


def expected_identities(
    coverage: dict[str, Any], seeds: tuple[int, ...]
) -> set[tuple[str, str, int]]:
    registry = coverage.get("scenario_registry")
    if not isinstance(registry, dict):
        raise ValueError("coverage manifest has no scenario registry")
    identities = set()
    for suite, entry in registry.items():
        scenarios = entry.get("scenarios", [])
        for scenario in scenarios:
            for seed in seeds:
                identities.add((str(suite), str(scenario), int(seed)))
    return identities


def audit_root(
    root: Path,
    coverage: dict[str, Any],
    seeds: tuple[int, ...],
    expected_policy: str,
    expected_selection: str,
) -> dict[str, Any]:
    expected = expected_identities(coverage, seeds)
    observed = set()
    invalid_paths = []
    report_errors = []
    artifact_checks = 0
    policy_counts: Counter[str] = Counter()
    selected_counts: Counter[str] = Counter()
    suite_counts: Counter[str] = Counter()
    fingerprint_counts: Counter[str] = Counter()
    for metrics_path in sorted(root.glob("*/*/metrics.json")):
        suite = metrics_path.parent.parent.name
        match = RUN_PATTERN.match(metrics_path.parent.name)
        if match is None:
            invalid_paths.append(str(metrics_path))
            continue
        identity = (suite, match.group("scenario"), int(match.group("seed")))
        if identity in observed:
            report_errors.append("duplicate identity %r" % (identity,))
            continue
        observed.add(identity)
        if identity not in expected:
            report_errors.append("identity outside frozen coverage/seeds %r" % (identity,))
        missing = [
            name for name in REQUIRED_ARTIFACTS if not (metrics_path.parent / name).is_file()
        ]
        artifact_checks += len(REQUIRED_ARTIFACTS)
        if missing:
            report_errors.append("missing artifacts for %r: %r" % (identity, missing))
            continue
        payload = _read(metrics_path)
        if int(payload.get("seed", -1)) != identity[2]:
            report_errors.append("seed mismatch for %r" % (identity,))
        policy = payload.get("risk_policy")
        selection = payload.get("risk_selection")
        policy_counts[str(policy)] += 1
        if policy != expected_policy:
            report_errors.append("risk policy mismatch for %r: %r" % (identity, policy))
        if selection != expected_selection:
            report_errors.append(
                "risk selection mismatch for %r: %r" % (identity, selection)
            )
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            report_errors.append("selection leakage guard failed for %r" % (identity,))
        selected = payload.get("selected_risk")
        reports = payload.get("reports")
        if not isinstance(selected, str) or not isinstance(reports, dict) or selected not in reports:
            report_errors.append("selected risk/report missing for %r" % (identity,))
        else:
            selected_counts[selected] += 1
        if not isinstance(payload.get("selected_report"), dict):
            report_errors.append("selected_report missing for %r" % (identity,))
        fingerprint = (
            payload.get("split_metadata", {})
            .get("split_fingerprint", {})
            .get("combined")
        )
        if not fingerprint:
            report_errors.append("combined split fingerprint missing for %r" % (identity,))
        else:
            fingerprint_counts[str(fingerprint)] += 1
        provenance = _read(metrics_path.parent / "provenance.json")
        provenance_fingerprint = provenance.get("split_fingerprint")
        if provenance_fingerprint is not None:
            metrics_fingerprint = payload.get("split_metadata", {}).get("split_fingerprint")
            if json.dumps(provenance_fingerprint, sort_keys=True) != json.dumps(
                metrics_fingerprint, sort_keys=True
            ):
                report_errors.append("provenance fingerprint mismatch for %r" % (identity,))
        suite_counts[suite] += 1

    failures = sorted(str(path) for path in root.glob("**/failure.json"))
    missing_identities = expected - observed
    validation = {
        "passes": not invalid_paths and not report_errors and not failures,
        "partial_matrix_allowed": True,
        "completed_runs": len(observed),
        "expected_runs": len(expected),
        "remaining_runs": len(missing_identities),
        "completion_fraction": len(observed) / float(len(expected)),
        "failure_count": len(failures),
        "invalid_path_count": len(invalid_paths),
        "report_error_count": len(report_errors),
        "artifact_checks": artifact_checks,
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "selection_uses_unknown_or_test_labels": False if not report_errors else None,
    }
    return {
        "validation": validation,
        "seeds": list(seeds),
        "expected_policy": expected_policy,
        "expected_selection": expected_selection,
        "suite_completed_counts": dict(sorted(suite_counts.items())),
        "selected_risk_counts": dict(sorted(selected_counts.items())),
        "risk_policy_counts": dict(sorted(policy_counts.items())),
        "unique_split_fingerprint_count": len(fingerprint_counts),
        "invalid_paths": invalid_paths,
        "report_errors": report_errors,
        "failure_files": failures,
        "missing_identity_count": len(missing_identities),
    }


def audit_mlp_root(
    root: Path,
    coverage: dict[str, Any],
    seeds: tuple[int, ...],
    required_report: str = "openmax",
) -> dict[str, Any]:
    expected = expected_identities(coverage, seeds)
    observed = set()
    invalid_paths = []
    report_errors = []
    artifact_checks = 0
    suite_counts: Counter[str] = Counter()
    fingerprint_counts: Counter[str] = Counter()
    report_counts: Counter[str] = Counter()
    for metrics_path in sorted(root.glob("*/*/metrics.json")):
        suite = metrics_path.parent.parent.name
        match = MLP_RUN_PATTERN.match(metrics_path.parent.name)
        if match is None:
            invalid_paths.append(str(metrics_path))
            continue
        identity = (suite, match.group("scenario"), int(match.group("seed")))
        if identity in observed:
            report_errors.append("duplicate identity %r" % (identity,))
            continue
        observed.add(identity)
        if identity not in expected:
            report_errors.append("identity outside frozen coverage/seeds %r" % (identity,))
        missing = [
            name
            for name in MLP_REQUIRED_ARTIFACTS
            if not (metrics_path.parent / name).is_file()
        ]
        artifact_checks += len(MLP_REQUIRED_ARTIFACTS)
        if missing:
            report_errors.append("missing MLP artifacts for %r: %r" % (identity, missing))
            continue
        payload = _read(metrics_path)
        if int(payload.get("seed", -1)) != identity[2]:
            report_errors.append("seed mismatch for %r" % (identity,))
        if payload.get("model") != "mlp":
            report_errors.append("model mismatch for %r: %r" % (identity, payload.get("model")))
        reports = payload.get("reports")
        if not isinstance(reports, dict) or required_report not in reports:
            report_errors.append(
                "required MLP report %r missing for %r" % (required_report, identity)
            )
        else:
            report_counts[required_report] += 1
        evidence = payload.get("selection_evidence", {})
        if evidence.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            report_errors.append("MLP selection leakage guard failed for %r" % (identity,))
        fingerprint = (
            payload.get("split_metadata", {})
            .get("split_fingerprint", {})
            .get("combined")
        )
        if not fingerprint:
            report_errors.append("combined split fingerprint missing for %r" % (identity,))
        else:
            fingerprint_counts[str(fingerprint)] += 1
        provenance = _read(metrics_path.parent / "provenance.json")
        provenance_fingerprint = provenance.get("split_fingerprint")
        if provenance_fingerprint is not None:
            metrics_fingerprint = payload.get("split_metadata", {}).get(
                "split_fingerprint"
            )
            if json.dumps(provenance_fingerprint, sort_keys=True) != json.dumps(
                metrics_fingerprint, sort_keys=True
            ):
                report_errors.append(
                    "MLP provenance fingerprint mismatch for %r" % (identity,)
                )
        suite_counts[suite] += 1

    failures = sorted(str(path) for path in root.glob("**/failure.json"))
    missing_identities = expected - observed
    validation = {
        "passes": not invalid_paths and not report_errors and not failures,
        "partial_matrix_allowed": True,
        "completed_runs": len(observed),
        "expected_runs": len(expected),
        "remaining_runs": len(missing_identities),
        "completion_fraction": len(observed) / float(len(expected)),
        "failure_count": len(failures),
        "invalid_path_count": len(invalid_paths),
        "report_error_count": len(report_errors),
        "artifact_checks": artifact_checks,
        "required_artifacts": list(MLP_REQUIRED_ARTIFACTS),
        "selection_uses_unknown_or_test_labels": False if not report_errors else None,
    }
    return {
        "validation": validation,
        "seeds": list(seeds),
        "expected_model": "mlp",
        "required_report": required_report,
        "suite_completed_counts": dict(sorted(suite_counts.items())),
        "required_report_counts": dict(sorted(report_counts.items())),
        "unique_split_fingerprint_count": len(fingerprint_counts),
        "invalid_paths": invalid_paths,
        "report_errors": report_errors,
        "failure_files": failures,
        "missing_identity_count": len(missing_identities),
    }


def validate_protocol(
    protocol: dict[str, Any], schema: str, coverage_sha: str
) -> dict[str, bool]:
    bound_coverage_sha = protocol.get("coverage_manifest_sha256")
    if bound_coverage_sha is None:
        bound_coverage_sha = protocol.get("bindings", {}).get(
            "coverage_manifest_sha256"
        )
    return {
        "schema_matches": protocol.get("schema_version") == schema,
        "manifest_sha_valid": protocol.get("manifest_sha256")
        == canonical_hash(protocol),
        "coverage_sha_matches": bound_coverage_sha == coverage_sha,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 running confirmation health audit",
        "",
        "Generated at UTC: `%s`." % result["generated_at_utc"],
        "",
        "This audit does not read or aggregate test metric values.",
        "",
        "| Matrix | Completed | Expected | Remaining | Failures | Health |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name in ("router_caeos", "router_mlp_openmax", "tail_aware"):
        value = result["matrices"][name]["validation"]
        lines.append(
            "| %s | %d | %d | %d | %d | %s |"
            % (
                name,
                value["completed_runs"],
                value["expected_runs"],
                value["remaining_runs"],
                value["failure_count"],
                "PASS" if value["passes"] else "FAIL",
            )
        )
    lines.extend(["", "Claim boundary: operational integrity only; no interim algorithm decision.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--router-caeos-root", type=Path, required=True)
    parser.add_argument("--router-mlp-root", type=Path, required=True)
    parser.add_argument("--tail-root", type=Path, required=True)
    parser.add_argument("--router-protocol", type=Path, required=True)
    parser.add_argument("--tail-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    coverage = _read(args.coverage)
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("running audit requires strict-v4 coverage manifest v2")
    if coverage.get("scenario_inference_units") != 102:
        raise ValueError("running audit requires 102 scenario inference units")
    coverage_sha = coverage["manifest_sha256"]
    router_protocol = _read(args.router_protocol)
    tail_protocol = _read(args.tail_protocol)
    protocol_checks = {
        "router": validate_protocol(
            router_protocol,
            "strict_v4_domain_safe_router_confirmation_protocol_v1",
            coverage_sha,
        ),
        "tail_aware": validate_protocol(
            tail_protocol,
            "strict_v4_tail_aware_confirmation_protocol_v1",
            coverage_sha,
        ),
    }
    if not all(all(checks.values()) for checks in protocol_checks.values()):
        raise ValueError("confirmation protocol validation failed")
    matrices = {
        "router_caeos": audit_root(
            args.router_caeos_root,
            coverage,
            (137, 139, 149),
            "strict_v4_domain_safe_router_confirmation_pairwise_v1",
            "nested_boundary_pairwise_pseudo_unknown_blend",
        ),
        "router_mlp_openmax": audit_mlp_root(
            args.router_mlp_root,
            coverage,
            (137, 139, 149),
        ),
        "tail_aware": audit_root(
            args.tail_root,
            coverage,
            (157, 163, 167),
            "strict_v4_tail_aware_pairwise_confirmation_v1",
            "nested_tail_aware_pairwise_pseudo_unknown_blend",
        ),
    }
    result = {
        "schema_version": "strict_v4_running_confirmation_health_audit_v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "coverage_manifest_sha256": coverage_sha,
        "protocol_checks": protocol_checks,
        "matrices": matrices,
        "overall_health_passes": all(
            value["validation"]["passes"] for value in matrices.values()
        ),
        "test_metric_values_read_or_aggregated": False,
        "result_may_select_or_modify_algorithm": False,
        "claim_boundary": "operational_integrity_snapshot_only_no_interim_algorithm_decision",
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "health.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render(result)
    (args.output_dir / "health.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
