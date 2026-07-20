from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from audit_strict_v2_sota import SCENARIO_MAPS


SEEDS = (7, 11, 19, 23, 37)
EXPECTED_SUITES = set(SCENARIO_MAPS)
POLICY = "final_composite_risk_v1"
CURRENT_SUITE_RISK = "__current_policy__"
REFERENCE = "cauchy_modality_support_union"
ENTROPY = "entropy"
FUSION = "rank_union"
REQUIRED_LINKS = ("scores.npz", "evidence_package.npz")
REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_report(report: object, label: str) -> dict[str, float]:
    if not isinstance(report, dict):
        raise ValueError(f"missing report for {label}")
    missing = [metric for metric in REPORT_METRICS if metric not in report]
    if missing:
        raise ValueError(f"report {label!r} misses metrics: {missing}")
    return {metric: float(report[metric]) for metric in REPORT_METRICS}


def validate_selection(path: Path) -> dict[str, object]:
    selection = read_object(path)
    if selection.get("schema_version") != "final_composite_risk_selection_v1":
        raise ValueError("unexpected final composite-risk selection schema")
    if selection.get("status") != "confirmed_frozen":
        raise ValueError("final composite-risk selection is not confirmed_frozen")
    if selection.get("runtime_selection_uses_unknown_or_test_labels") is not False:
        raise ValueError("final composite-risk runtime label boundary is invalid")
    suite_risks = selection.get("suite_risks")
    if not isinstance(suite_risks, dict) or set(suite_risks) != EXPECTED_SUITES:
        raise ValueError("final composite-risk suite coverage mismatch")
    if any(not isinstance(risk, str) or not risk for risk in suite_risks.values()):
        raise ValueError("final composite-risk selection has an invalid risk name")
    evidence = selection.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("final composite-risk selection has no evidence block")
    if int(evidence.get("edge_heldout_task_count", -1)) != 56:
        raise ValueError("final composite-risk Edge evidence is incomplete")
    if int(evidence.get("cross_suite_heldout_task_count", -1)) != 96:
        raise ValueError("final composite-risk cross-suite evidence is incomplete")
    return selection


def selected_report(
    source: dict[str, object],
    suite: str,
    selected: str,
    replay: dict[str, object] | None,
) -> dict[str, float]:
    if suite == "edge_iiot":
        if selected == REFERENCE:
            if source.get("selected_risk") != REFERENCE:
                raise ValueError("source Edge gate does not use the frozen reference risk")
            return normalized_report(source.get("selected_report"), REFERENCE)
        reports = source.get("reports")
        if not isinstance(reports, dict):
            raise ValueError("source Edge metrics have no reports mapping")
        if selected == ENTROPY:
            return normalized_report(reports.get(ENTROPY), ENTROPY)
        if selected != FUSION:
            raise ValueError(f"unsupported final Edge risk: {selected!r}")
        if replay is None:
            raise ValueError("rank_union materialization requires replay reports")
        replay_reports = replay.get("reports")
        if not isinstance(replay_reports, dict):
            raise ValueError("rank_union replay has no reports mapping")
        return normalized_report(replay_reports.get(FUSION), FUSION)
    if source.get("selected_risk") == selected:
        return normalized_report(source.get("selected_report"), selected)
    reports = source.get("reports")
    if not isinstance(reports, dict) or selected not in reports:
        raise ValueError(f"source metrics have no report for {suite}/{selected}")
    thresholds = source.get("validation_thresholds")
    if not isinstance(thresholds, dict) or selected not in thresholds:
        raise ValueError(f"source metrics have no known-validation threshold for {suite}/{selected}")
    return normalized_report(reports[selected], selected)


def rewrite_metrics(
    source: dict[str, object],
    suite: str,
    selected: str,
    selection_sha: str,
    materializer_sha: str,
    replay: dict[str, object] | None = None,
) -> tuple[dict[str, object], str]:
    effective_selected = (
        str(source.get("selected_risk", ""))
        if selected == CURRENT_SUITE_RISK
        else selected
    )
    if not effective_selected:
        raise ValueError(f"source metrics have no current selected risk for {suite}")
    chosen_report = selected_report(source, suite, effective_selected, replay)
    result = copy.deepcopy(source)
    result["selected_risk"] = effective_selected
    result["selected_report"] = chosen_report
    result["risk_selection"] = effective_selected
    result["risk_policy"] = POLICY
    arguments = result.get("arguments")
    if not isinstance(arguments, dict):
        raise ValueError("source metrics have no arguments mapping")
    arguments["risk_selection"] = effective_selected
    arguments["risk_policy"] = POLICY
    result["final_composite_risk_selection"] = {
        "suite": suite,
        "suite_policy": selected,
        "selected_risk": effective_selected,
        "selection_sha256": selection_sha,
        "materializer_sha256": materializer_sha,
        "selection_uses_only_known_suite_identity": True,
        "unknown_or_test_labels_used_for_runtime_selection": False,
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "source_parameter_fingerprint": source.get("parameter_fingerprint"),
                "suite": suite,
                "seed": source.get("seed"),
                "suite_policy": selected,
                "selected": effective_selected,
                "selection_sha256": selection_sha,
                "materializer_sha256": materializer_sha,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    result["parameter_fingerprint"] = fingerprint
    return result, fingerprint


def link_artifact(source: Path, target: Path) -> None:
    if not source.is_file() or source.stat().st_size <= 0:
        raise ValueError(f"missing source artifact: {source}")
    if target.exists() or target.is_symlink():
        if target.resolve() != source.resolve():
            raise ValueError(f"existing target points elsewhere: {target}")
        return
    os.symlink(source.resolve(), target)


def materialize(
    source_root: Path,
    selection_path: Path,
    output_root: Path,
    known_acceptance: float,
) -> dict[str, object]:
    if source_root.resolve() == output_root.resolve():
        raise ValueError("source and output gate roots must differ")
    selection = validate_selection(selection_path)
    suite_risks = selection["suite_risks"]
    assert isinstance(suite_risks, dict)
    selection_sha = sha256(selection_path)
    materializer_sha = sha256(Path(__file__))
    expected = sum(len(scenarios) for scenarios in SCENARIO_MAPS.values()) * len(SEEDS)
    source_paths = sorted(source_root.glob("*/*/metrics.json"))
    if len(source_paths) != expected:
        raise ValueError(f"source gate coverage mismatch: expected={expected}, found={len(source_paths)}")

    counts: Counter[str] = Counter()
    source_hashes: list[dict[str, str]] = []
    for metrics_path in source_paths:
        suite = metrics_path.parent.parent.name
        if suite not in SCENARIO_MAPS:
            raise ValueError(f"unexpected source suite: {suite}")
        selected = str(suite_risks[suite])
        source_metrics = read_object(metrics_path)
        replay = None
        if suite == "edge_iiot" and selected == FUSION:
            from analyze_entropy_cauchy_fusion import task_report

            replay = task_report(metrics_path.parent, known_acceptance)
        rewritten, fingerprint = rewrite_metrics(
            source_metrics, suite, selected, selection_sha, materializer_sha, replay
        )
        target_dir = output_root / suite / metrics_path.parent.name
        target_dir.mkdir(parents=True, exist_ok=True)
        for name in REQUIRED_LINKS:
            link_artifact(metrics_path.parent / name, target_dir / name)

        source_provenance_path = metrics_path.parent / "provenance.json"
        source_provenance = read_object(source_provenance_path)
        provenance = copy.deepcopy(source_provenance)
        provenance["code"] = {
            "sha256": materializer_sha,
            "entrypoint": str(Path(__file__).resolve()),
        }
        provenance["parameter_fingerprint"] = fingerprint
        provenance["derived_from"] = {
            "metrics_path": str(metrics_path.resolve()),
            "metrics_sha256": sha256(metrics_path),
            "provenance_path": str(source_provenance_path.resolve()),
            "provenance_sha256": sha256(source_provenance_path),
            "selection_path": str(selection_path.resolve()),
            "selection_sha256": selection_sha,
        }
        (target_dir / "metrics.json").write_text(
            json.dumps(rewritten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (target_dir / "provenance.json").write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        counts[suite] += 1
        source_hashes.append(
            {
                "path": metrics_path.relative_to(source_root).as_posix(),
                "sha256": sha256(metrics_path),
            }
        )

    expected_counts = {
        suite: len(scenarios) * len(SEEDS) for suite, scenarios in SCENARIO_MAPS.items()
    }
    if dict(counts) != expected_counts:
        raise ValueError(f"suite coverage mismatch: expected={expected_counts}, found={dict(counts)}")
    manifest = {
        "schema_version": "final_composite_gate_materialization_v1",
        "state": "complete",
        "number_of_experiments": expected,
        "completed": expected,
        "failed": 0,
        "suite_risks": suite_risks,
        "suite_run_counts": dict(counts),
        "source_root": str(source_root.resolve()),
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "selection_path": str(selection_path.resolve()),
        "selection_sha256": selection_sha,
        "materializer_sha256": materializer_sha,
        "runtime_selection_uses_unknown_or_test_labels": False,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the final suite-composite CAEOS risk gate"
    )
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    args = parser.parse_args()
    result = materialize(
        Path(args.source_root), Path(args.selection), Path(args.output_root), args.known_acceptance
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
