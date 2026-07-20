from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


SEEDS = (7, 11, 19, 23, 29)
BENIGN_CLASS = "benign"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_protocol(
    project_root: Path,
    csv_path: Path,
    config_path: Path,
    xgboost_version: str,
    observed_metrics: int,
) -> dict[str, Any]:
    if observed_metrics != 0:
        raise ValueError("XGBoost protocol must be frozen at zero results")
    result = {
        "schema_version": "mal_tls_xgboost_closed_set_protocol_v3",
        "status": "frozen_before_results",
        "scope": "supporting_closed_set_row_stratified_evidence_not_strict_v4_confirmation",
        "dataset": "Mal_TLS2023",
        "benign_class": BENIGN_CLASS,
        "csv_sha256": file_hash(csv_path),
        "config_sha256": file_hash(config_path),
        "implementation_sha256": {
            "trainer": file_hash(project_root / "train_classical.py"),
            "protocol_generator": file_hash(
                project_root / "create_mal_tls_xgboost_protocol.py"
            ),
            "runner": file_hash(
                project_root / "scripts" / "run_mal_tls_xgboost_multiseed.sh"
            ),
            "summarizer": file_hash(
                project_root / "summarize_mal_tls_xgboost_multiseed.py"
            ),
        },
        "xgboost_version": xgboost_version,
        "seeds": list(SEEDS),
        "max_per_class": 500,
        "model": "xgboost",
        "n_estimators": 1000,
        "max_depth": 8,
        "learning_rate": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "early_stopping_rounds": 30,
        "class_weighting": "balanced_sample_weight_on_training_only",
        "iteration_selection": "known_validation_mlogloss_only",
        "metrics_identity_field": "seed",
        "test_labels_used_for_fitting_or_selection": False,
        "expected_runs": len(SEEDS),
        "metrics_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def freeze_or_validate_protocol(
    output: Path, expected: dict[str, Any], observed_metrics: int
) -> dict[str, Any]:
    if output.is_file():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != expected:
            raise ValueError("existing XGBoost protocol differs from current evidence")
        return existing
    if observed_metrics != 0:
        raise ValueError("XGBoost protocol must be frozen at zero results")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--xgboost-version", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    observed = len(list(args.run_root.glob("seed*/metrics.json"))) if args.run_root.is_dir() else 0
    expected = create_protocol(
        args.project_root.resolve(),
        args.csv.resolve(),
        args.config.resolve(),
        args.xgboost_version,
        0,
    )
    freeze_or_validate_protocol(args.output, expected, observed)
    print(expected["manifest_sha256"])


if __name__ == "__main__":
    main()
