from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

from select_strict_v4_external_risk_candidate import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_npz(path: Path) -> list[str]:
    with np.load(path) as archive:
        names = list(archive.files)
        for name in names:
            _ = archive[name].shape
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--quarantined-run", type=Path, required=True)
    parser.add_argument("--recovered-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("coverage manifest SHA mismatch")

    old_score = args.quarantined_run / "scores.npz"
    try:
        validate_npz(old_score)
    except zipfile.BadZipFile as exc:
        old_error = f"{type(exc).__name__}: {exc}"
    else:
        raise ValueError("quarantined score archive is not corrupt")

    new_score = args.recovered_run / "scores.npz"
    score_arrays = validate_npz(new_score)
    old_provenance = json.loads(
        (args.quarantined_run / "provenance.json").read_text(encoding="utf-8")
    )
    new_provenance = json.loads(
        (args.recovered_run / "provenance.json").read_text(encoding="utf-8")
    )
    if old_provenance != new_provenance:
        raise ValueError("recovered run provenance differs from quarantined run")
    old_metrics = json.loads(
        (args.quarantined_run / "metrics.json").read_text(encoding="utf-8")
    )
    new_metrics = json.loads(
        (args.recovered_run / "metrics.json").read_text(encoding="utf-8")
    )
    primary_keys = (
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    )
    old_report = old_metrics["selected_report"]
    new_report = new_metrics["selected_report"]
    primary_metric_deltas = {
        key: float(new_report[key] - old_report[key]) for key in primary_keys
    }
    maximum_absolute_primary_delta = max(
        abs(value) for value in primary_metric_deltas.values()
    )
    if maximum_absolute_primary_delta >= 1e-3:
        raise ValueError(
            "recovered primary metrics changed by at least 1e-3: "
            f"{primary_metric_deltas}"
        )

    payload: dict[str, Any] = {
        "schema_version": "strict_v4_corrupt_score_recovery_v1",
        "coverage_manifest_sha256": manifest["manifest_sha256"],
        "suite": "nf_unsw",
        "scenario": "reconnaissance",
        "seed": 7,
        "failure": {
            "error": old_error,
            "scores_sha256": file_hash(old_score),
            "scores_bytes": old_score.stat().st_size,
            "metrics_sha256": file_hash(args.quarantined_run / "metrics.json"),
            "provenance_sha256": file_hash(
                args.quarantined_run / "provenance.json"
            ),
            "detected_before_metric_summary": True,
        },
        "recovery": {
            "action": "quarantine complete run directory and rerun frozen task",
            "algorithm_or_hyperparameter_changed": False,
            "data_or_split_changed": False,
            "provenance_json_identical": True,
            "metrics_json_identical": old_metrics == new_metrics,
            "primary_metric_deltas_new_minus_quarantined": primary_metric_deltas,
            "maximum_absolute_primary_metric_delta": (
                maximum_absolute_primary_delta
            ),
            "scores_sha256": file_hash(new_score),
            "scores_bytes": new_score.stat().st_size,
            "score_arrays": score_arrays,
            "metrics_sha256": file_hash(args.recovered_run / "metrics.json"),
            "provenance_sha256": file_hash(
                args.recovered_run / "provenance.json"
            ),
        },
    }
    payload["record_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
