from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}
ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(
    payload: dict[str, Any], field: str = "manifest_sha256"
) -> str:
    value = dict(payload)
    value.pop(field, None)
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def extract_report(
    payload: dict[str, Any], method: str, path: Path
) -> dict[str, float]:
    reports = payload.get("reports", {})
    if set(reports) != {method}:
        raise ValueError(f"unexpected report set in {path}")
    result = {}
    for metric in METRICS:
        value = float(reports[method][metric])
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"invalid metric in {path}: {metric}")
        result[metric] = value
    return result


def aggregate(rows: list[dict[str, float]]) -> dict[str, float]:
    return {
        metric: sum(row[metric] for row in rows) / len(rows)
        for metric in METRICS
    }


def compare(
    candidate: list[dict[str, float]], reference: list[dict[str, float]]
) -> dict[str, Any]:
    output = {}
    for metric in METRICS:
        deltas = []
        for left, right in zip(candidate, reference):
            raw = left[metric] - right[metric]
            deltas.append(-raw if metric in LOWER_IS_BETTER else raw)
        output[metric] = {
            "direction": (
                "lower_is_better"
                if metric in LOWER_IS_BETTER
                else "higher_is_better"
            ),
            "oriented_mean_delta": sum(deltas) / len(deltas),
            "wins": sum(delta > 1e-12 for delta in deltas),
            "ties": sum(abs(delta) <= 1e-12 for delta in deltas),
            "losses": sum(delta < -1e-12 for delta in deltas),
        }
    return output


def audit(
    protocol_path: Path,
    protocol_audit_path: Path,
    summary_path: Path,
    result_root: Path,
    opendetect_root: Path,
    baseline_manifest_path: Path,
    full_summary_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    protocol_audit = load_json(protocol_audit_path)
    summary = load_json(summary_path)
    baseline_manifest = load_json(baseline_manifest_path)
    full_summary = load_json(full_summary_path)
    checks: dict[str, bool] = {
        "protocol_canonical": (
            protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "protocol_audit_passes": (
            protocol_audit.get("audit_manifest_sha256")
            == canonical_hash(protocol_audit, "audit_manifest_sha256")
            and protocol_audit.get("passed") is True
            and all(protocol_audit.get("checks", {}).values())
        ),
        "summary_canonical": (
            summary.get("schema_version")
            == "strict_v4_ronetc_full102_summary_v1"
            and summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "baseline_manifest_canonical": (
            baseline_manifest.get("manifest_sha256")
            == canonical_hash(baseline_manifest)
        ),
        "full_summary_binding": (
            full_summary.get("baseline_manifest_sha256")
            == baseline_manifest.get("manifest_sha256")
        ),
    }
    inputs = summary.get("input_evidence", {})
    checks["input_file_hashes"] = bool(
        inputs.get("protocol_file_sha256") == file_hash(protocol_path)
        and inputs.get("protocol_audit_file_sha256")
        == file_hash(protocol_audit_path)
        and inputs.get("baseline_manifest_file_sha256")
        == file_hash(baseline_manifest_path)
        and inputs.get("full103_summary_file_sha256")
        == file_hash(full_summary_path)
    )
    implementation = summary.get("analysis_implementation_sha256", {})
    checks["analysis_implementation_hashes"] = bool(
        set(implementation)
        == {
            "summarize_strict_v4_ronetc_full102.py",
            "audit_strict_v4_ronetc_full102.py",
        }
        and all(
            file_hash(project_root / name) == digest
            for name, digest in implementation.items()
        )
    )

    expected = {
        (task["suite"], task["scenario"], int(task["seed"]))
        for task in protocol.get("tasks", [])
    }
    summary_records = {
        (row["suite"], row["scenario"], int(row["seed"])): row
        for row in summary.get("task_records", [])
    }
    records = []
    raw_integrity = len(expected) == 102 and set(summary_records) == expected
    try:
        for suite, scenario, seed in sorted(expected):
            candidate_dir = result_root / suite / f"{scenario}_seed{seed}_ronetc"
            reference_dir = (
                opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
            )
            stored = summary_records[(suite, scenario, seed)]
            hashes = {}
            for label, directory in (
                ("ronetc", candidate_dir),
                ("opendetect", reference_dir),
            ):
                for artifact in ARTIFACTS:
                    path = directory / artifact
                    hashes[f"{label}/{artifact}"] = file_hash(path)
            candidate = load_json(candidate_dir / "metrics.json")
            reference = load_json(reference_dir / "metrics.json")
            candidate_report = extract_report(
                candidate, "ronetc", candidate_dir / "metrics.json"
            )
            reference_report = extract_report(
                reference, "opendetect", reference_dir / "metrics.json"
            )
            candidate_split = candidate["split_metadata"][
                "split_fingerprint"
            ]["combined"]
            reference_split = reference["split_metadata"][
                "split_fingerprint"
            ]["combined"]
            selection_safe = all(
                metrics.get("selection_evidence", {}).get(
                    "unknown_or_test_labels_used_for_fitting_or_selection"
                )
                is False
                for metrics in (candidate, reference)
            )
            raw_integrity = bool(
                raw_integrity
                and hashes == stored.get("artifact_sha256")
                and candidate_report == stored.get("reports", {}).get("ronetc")
                and reference_report
                == stored.get("reports", {}).get("opendetect")
                and candidate_split == reference_split
                and candidate_split == stored.get("split_fingerprint")
                and candidate.get("sample_counts")
                == reference.get("sample_counts")
                and selection_safe
            )
            records.append(
                {
                    "suite": suite,
                    "ronetc": candidate_report,
                    "opendetect": reference_report,
                }
            )
    except (OSError, KeyError, TypeError, ValueError):
        raw_integrity = False
    checks["raw_artifact_and_task_integrity"] = raw_integrity

    recomputed_overall = {}
    recomputed_by_suite = {}
    if records:
        candidate = [row["ronetc"] for row in records]
        reference = [row["opendetect"] for row in records]
        recomputed_overall = {
            "ronetc": aggregate(candidate),
            "opendetect": aggregate(reference),
            "ronetc_vs_opendetect": compare(candidate, reference),
        }
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in records:
            grouped[row["suite"]].append(row)
        for suite, rows in sorted(grouped.items()):
            candidate = [row["ronetc"] for row in rows]
            reference = [row["opendetect"] for row in rows]
            recomputed_by_suite[suite] = {
                "scenario_count": len(rows),
                "ronetc": aggregate(candidate),
                "opendetect": aggregate(reference),
                "ronetc_vs_opendetect": compare(candidate, reference),
            }
    checks["aggregate_recomputation_matches"] = bool(
        recomputed_overall == summary.get("overall")
        and recomputed_by_suite == summary.get("by_suite")
    )
    checks["claim_boundary_conservative"] = bool(
        summary.get("claim_boundary", {}).get(
            "authorizes_algorithm_selection"
        )
        is False
        and summary.get("claim_boundary", {}).get(
            "authorizes_comprehensive_sota"
        )
        is False
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_ronetc_full102_audit_v1",
        "state": "independent_integrity_audit_complete",
        "input_file_sha256": {
            "protocol": file_hash(protocol_path),
            "protocol_audit": file_hash(protocol_audit_path),
            "summary": file_hash(summary_path),
            "baseline_manifest": file_hash(baseline_manifest_path),
            "full103_summary": file_hash(full_summary_path),
        },
        "input_manifest_sha256": {
            "protocol": protocol.get("manifest_sha256"),
            "summary": summary.get("manifest_sha256"),
            "baseline_manifest": baseline_manifest.get("manifest_sha256"),
        },
        "checks": checks,
        "recomputed_overall": recomputed_overall,
        "passes": all(checks.values()),
        "effect_observation": {
            "ronetc_vs_opendetect": recomputed_overall.get(
                "ronetc_vs_opendetect"
            ),
            "controls_integrity_pass": False,
        },
        "claim_boundary": {
            "integrity_pass_is_not_effect_superiority": True,
            "seed7_is_development_screen": True,
            "authorizes_comprehensive_sota": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def completion(
    protocol_path: Path,
    summary_path: Path,
    audit_path: Path,
    audit_value: dict[str, Any],
) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    summary = load_json(summary_path)
    value: dict[str, Any] = {
        "schema_version": "strict_v4_ronetc_full102_completion_v1",
        "state": "complete",
        "scenario_count": 102,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "audit_manifest_sha256": audit_value["manifest_sha256"],
        "audit_file_sha256": file_hash(audit_path),
        "integrity_passes": True,
        "effect_superiority_required_for_completion": False,
        "authorizes_comprehensive_sota": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--protocol-audit", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-audit", type=Path, required=True)
    parser.add_argument("--output-completion", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    value = audit(
        args.protocol.resolve(),
        args.protocol_audit.resolve(),
        args.summary.resolve(),
        args.result_root.resolve(),
        args.opendetect_root.resolve(),
        args.baseline_manifest.resolve(),
        args.full_summary.resolve(),
        args.project_root.resolve(),
    )
    args.output_audit.parent.mkdir(parents=True, exist_ok=True)
    args.output_audit.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if value["passes"]:
        complete = completion(
            args.protocol.resolve(),
            args.summary.resolve(),
            args.output_audit.resolve(),
            value,
        )
        args.output_completion.parent.mkdir(parents=True, exist_ok=True)
        args.output_completion.write_text(
            json.dumps(complete, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "output": str(args.output_audit),
                "passes": value["passes"],
                "manifest_sha256": value["manifest_sha256"],
            }
        )
    )
    if not value["passes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
