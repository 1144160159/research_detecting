from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from analyze_entropy_cauchy_fusion import task_report
from audit_strict_v2_sota import SCENARIO_MAPS
from select_final_internal_risk import ENTROPY, FUSION, REFERENCE


SEEDS = (7, 11, 19, 23, 37)
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


def validate_selection(path: Path) -> dict[str, object]:
    selection = read_object(path)
    if selection.get("schema_version") != "final_internal_risk_selection_v1":
        raise ValueError("unexpected final internal-risk selection schema")
    if selection.get("status") != "confirmed_frozen":
        raise ValueError("final internal-risk selection is not confirmed_frozen")
    selected = selection.get("selected_internal_risk")
    if selected not in {REFERENCE, ENTROPY, FUSION}:
        raise ValueError(f"unsupported final internal risk: {selected!r}")
    if selection.get("validated_task_count") != 56:
        raise ValueError("final selection must validate all 56 held-out tasks")
    if selection.get("scenario_count") != 14:
        raise ValueError("final selection must cover all 14 Edge scenarios")
    return selection


def normalized_report(report: object, label: str) -> dict[str, float]:
    if not isinstance(report, dict):
        raise ValueError(f"missing report for {label}")
    missing = [metric for metric in REPORT_METRICS if metric not in report]
    if missing:
        raise ValueError(f"report {label!r} misses metrics: {missing}")
    return {metric: float(report[metric]) for metric in REPORT_METRICS}


def edge_selected_report(
    metrics: dict[str, object], selected: str, replay: dict[str, object] | None
) -> dict[str, float]:
    if selected == REFERENCE:
        if metrics.get("selected_risk") != REFERENCE:
            raise ValueError("source Edge gate does not use the frozen reference risk")
        return normalized_report(metrics.get("selected_report"), REFERENCE)
    reports = metrics.get("reports")
    if not isinstance(reports, dict):
        raise ValueError("source Edge metrics have no reports mapping")
    if selected == ENTROPY:
        return normalized_report(reports.get(ENTROPY), ENTROPY)
    if replay is None:
        raise ValueError("rank_union materialization requires replay reports")
    replay_reports = replay.get("reports")
    if not isinstance(replay_reports, dict):
        raise ValueError("rank_union replay has no reports mapping")
    return normalized_report(replay_reports.get(FUSION), FUSION)


def rewrite_metrics(
    source: dict[str, object],
    suite: str,
    selected: str,
    selection_sha: str,
    materializer_sha: str,
    replay: dict[str, object] | None = None,
) -> tuple[dict[str, object], str]:
    result = copy.deepcopy(source)
    policy = f"final_selected_internal_risk_{selected}_composite_v1"
    if suite == "edge_iiot":
        result["selected_risk"] = selected
        result["selected_report"] = edge_selected_report(result, selected, replay)
        result["risk_selection"] = selected
    arguments = result.get("arguments")
    if not isinstance(arguments, dict):
        raise ValueError("source metrics have no arguments mapping")
    if suite == "edge_iiot":
        arguments["risk_selection"] = selected
    arguments["risk_policy"] = policy
    result["risk_policy"] = policy
    result["final_internal_risk_selection"] = {
        "selected_edge_risk": selected,
        "selection_sha256": selection_sha,
        "materializer_sha256": materializer_sha,
        "unknown_or_test_labels_used_for_runtime_selection": False,
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "source_parameter_fingerprint": source.get("parameter_fingerprint"),
                "suite": suite,
                "seed": source.get("seed"),
                "selected": selected,
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


def expected_task_count() -> int:
    return sum(len(scenarios) for scenarios in SCENARIO_MAPS.values()) * len(SEEDS)


def materialize(
    source_root: Path,
    selection_path: Path,
    output_root: Path,
    known_acceptance: float,
) -> dict[str, object]:
    if source_root.resolve() == output_root.resolve():
        raise ValueError("source and output gate roots must differ")
    selection = validate_selection(selection_path)
    selected = str(selection["selected_internal_risk"])
    selection_sha = sha256(selection_path)
    materializer_sha = sha256(Path(__file__))
    expected = expected_task_count()
    source_paths = sorted(source_root.glob("*/*/metrics.json"))
    if len(source_paths) != expected:
        raise ValueError(f"source gate coverage mismatch: expected={expected}, found={len(source_paths)}")

    counts: Counter[str] = Counter()
    source_hashes: list[dict[str, str]] = []
    for metrics_path in source_paths:
        suite = metrics_path.parent.parent.name
        if suite not in SCENARIO_MAPS:
            raise ValueError(f"unexpected source suite: {suite}")
        run_name = metrics_path.parent.name
        source_metrics = read_object(metrics_path)
        replay = (
            task_report(metrics_path.parent, known_acceptance)
            if suite == "edge_iiot" and selected == FUSION
            else None
        )
        rewritten, fingerprint = rewrite_metrics(
            source_metrics,
            suite,
            selected,
            selection_sha,
            materializer_sha,
            replay,
        )
        target_dir = output_root / suite / run_name
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
            json.dumps(rewritten, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (target_dir / "provenance.json").write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        counts[suite] += 1
        source_hashes.append(
            {
                "path": metrics_path.relative_to(source_root).as_posix(),
                "sha256": sha256(metrics_path),
            }
        )

    expected_counts = {
        suite: len(scenarios) * len(SEEDS)
        for suite, scenarios in SCENARIO_MAPS.items()
    }
    if dict(counts) != expected_counts:
        raise ValueError(f"suite coverage mismatch: expected={expected_counts}, found={dict(counts)}")
    manifest = {
        "schema_version": "final_selected_gate_materialization_v1",
        "state": "complete",
        "number_of_experiments": expected,
        "completed": expected,
        "failed": 0,
        "selected_edge_risk": selected,
        "suite_run_counts": dict(counts),
        "source_root": str(source_root.resolve()),
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
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
        description="Materialize the held-out-selected internal risk as a strict-v2 gate"
    )
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    args = parser.parse_args()
    result = materialize(
        Path(args.source_root),
        Path(args.selection),
        Path(args.output_root),
        args.known_acceptance,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
