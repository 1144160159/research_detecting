from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

import train_hybrid_open_set as trainer
from capture_krc_parrot_deployment_bundle import trainer_namespace
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
    require_canonical,
    write_json,
)
from evaluate_strict_v4_comparative_corruption import (
    METRICS,
    archival_metric_differences,
    degradation,
    report,
)
from run_strict_v4_postselection_corruption import selected_modality
from run_strict_v4_selected_system_parrot_safety import (
    _runtime_context,
    block_path,
    source_capture_dir,
)
from train_hybrid_open_set import apply_test_corruption


SCHEMA = "strict_v4_selected_system_preconfirmation_record_v1"
CLASSIC_REPORT_NAMES = {
    "mlp_msp": "msp",
    "mlp_energy": "energy",
    "mlp_openmax": "openmax",
    "mlp_knn": "knn",
    "mlp_vim": "vim",
}


def source_identity(source: dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(source["suite"]),
        str(source["scenario"]),
        int(source["training_seed"]),
    )


def split_fingerprint(value: Any) -> str:
    output = value.get("combined") if isinstance(value, dict) else value
    if not isinstance(output, str) or len(output) != 64:
        raise ValueError("valid split fingerprint required")
    return output


def metric_report(value: Any, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"metric report required: {label}")
    result = {}
    for metric in METRICS:
        observed = value.get(metric)
        if not isinstance(observed, (int, float)):
            raise ValueError(f"finite metric required: {label}/{metric}")
        number = float(observed)
        if not np.isfinite(number):
            raise ValueError(f"finite metric required: {label}/{metric}")
        result[metric] = number
    return result


def clean_source_run(
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> Path:
    block = block_path(run_root, source)
    if protocol["selected_algorithm"] in ("caeos_pairwise", "caeos_pug"):
        return block / "source_train"
    return (
        source_capture_dir(run_root, source, protocol["selected_algorithm"])
        / "clean_run"
    )


def load_npz_views(path: Path) -> list[np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        names = sorted(
            (name for name in archive.files if name.startswith("view_")),
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )
        views = [np.asarray(archive[name]) for name in names]
    if not views or len({len(view) for view in views}) != 1:
        raise ValueError(f"invalid captured views: {path}")
    return views


def arrays_equal(
    left: list[np.ndarray], right: list[np.ndarray]
) -> bool:
    return len(left) == len(right) and all(
        np.array_equal(a, b) for a, b in zip(left, right)
    )


def evaluate_source(
    *,
    protocol: dict[str, Any],
    project_root: Path,
    run_root: Path,
    source: dict[str, Any],
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "preconfirmation protocol")
    if protocol["implementation_sha256"].get(Path(__file__).name) != file_hash(
        Path(__file__).resolve()
    ):
        raise ValueError("active preconfirmation evaluator SHA drifted")
    selected = protocol["selected_algorithm"]
    block = block_path(run_root, source)
    (
        candidate,
        _candidate_source_dir,
        arguments,
        candidate_input_path,
        candidate_threshold,
        candidate_views,
        labels,
        unknown,
    ) = _runtime_context(protocol, run_root, source)
    _args, _config_path, data = trainer_namespace(arguments, project_root)
    reconstructed_test = [
        np.asarray(view) for view in trainer.views(data.test)
    ]
    train_views = [np.asarray(view) for view in trainer.views(data.train)]
    if not arrays_equal(candidate_views, reconstructed_test):
        raise ValueError("candidate capture and reconstructed test arrays differ")

    opendetect_dir = block / "opendetect_capture"
    opendetect_manifest_path = opendetect_dir / "capture_manifest.json"
    opendetect_manifest = load(opendetect_manifest_path)
    opendetect = joblib.load(
        opendetect_dir / opendetect_manifest["deployment_artifact"]
    )
    opendetect_views = load_npz_views(
        opendetect_dir / opendetect_manifest["benchmark_inputs"]
    )
    if not arrays_equal(candidate_views, opendetect_views):
        raise ValueError("candidate and fresh OpenDetect input arrays differ")

    source_run = clean_source_run(protocol, run_root, source)
    source_metrics_path = source_run / "metrics.json"
    source_metrics = load(source_metrics_path)
    opendetect_metrics_path = block / "opendetect_train" / "metrics.json"
    opendetect_metrics = load(opendetect_metrics_path)
    mahalanobis_path = block / "mahalanobis_pp" / "metrics.json"
    mahalanobis = load(mahalanobis_path)
    expected_split = str(source["source_split_fingerprint"])
    split_values = {
        "source": split_fingerprint(
            source_metrics.get("split_metadata", {}).get("split_fingerprint")
        ),
        "opendetect": split_fingerprint(
            opendetect_metrics.get("split_metadata", {}).get(
                "split_fingerprint"
            )
        ),
        "mahalanobis_pp": split_fingerprint(
            mahalanobis.get("split_metadata", {}).get("split_fingerprint")
        ),
        "reconstructed": split_fingerprint(
            data.split_metadata.get("split_fingerprint")
        ),
    }
    if set(split_values.values()) != {expected_split}:
        raise ValueError("preconfirmation source split fingerprints differ")

    candidate_clean = report(
        labels,
        unknown,
        candidate.predict(candidate_views),
        candidate_threshold,
    )
    opendetect_threshold = float(
        opendetect_metrics["validation_thresholds"]["opendetect"]
    )
    opendetect_clean = report(
        labels,
        unknown,
        opendetect.predict(opendetect_views),
        opendetect_threshold,
    )
    classic_reports = {
        method: metric_report(
            source_metrics["reports"][report_name], method
        )
        for method, report_name in CLASSIC_REPORT_NAMES.items()
    }
    classic_reports["mahalanobis_pp"] = metric_report(
        mahalanobis["reports"]["mahalanobis_pp"], "mahalanobis_pp"
    )
    classic_reports["opendetect"] = metric_report(
        opendetect_clean, "opendetect"
    )
    if list(classic_reports) != protocol["classic_main_gate"]["methods"]:
        raise ValueError("classic main baseline method order drifted")

    conditions = []
    corruption = protocol["corruption"]
    for family in corruption["families"]:
        modality = selected_modality(
            corruption["coverage_manifest_sha256"],
            str(source["suite"]),
            str(source["scenario"]),
            family,
        )
        severity = float(corruption["fixed_severity"][family])
        corrupted_views, metadata = apply_test_corruption(
            candidate_views,
            train_views,
            family,
            modality,
            severity,
            int(source["corruption_seed"]),
        )
        candidate_corrupted = report(
            labels,
            unknown,
            candidate.predict(corrupted_views),
            candidate_threshold,
        )
        opendetect_corrupted = report(
            labels,
            unknown,
            opendetect.predict(corrupted_views),
            opendetect_threshold,
        )
        candidate_degradation = {
            metric: degradation(
                candidate_clean, candidate_corrupted, metric
            )
            for metric in (*METRICS, "ece")
        }
        opendetect_degradation = {
            metric: degradation(
                opendetect_clean, opendetect_corrupted, metric
            )
            for metric in (*METRICS, "ece")
        }
        conditions.append(
            {
                "family": family,
                "metadata": metadata,
                "candidate_report": candidate_corrupted,
                "opendetect_report": opendetect_corrupted,
                "candidate_degradation": candidate_degradation,
                "opendetect_degradation": opendetect_degradation,
                "candidate_robustness_advantage": {
                    metric: (
                        opendetect_degradation[metric]
                        - candidate_degradation[metric]
                    )
                    for metric in (*METRICS, "ece")
                },
            }
        )
    value: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": selected,
        "source": {
            "suite": source["suite"],
            "scenario": source["scenario"],
            "training_seed": int(source["training_seed"]),
            "corruption_seed": int(source["corruption_seed"]),
            "source_split_fingerprint": expected_split,
        },
        "candidate_clean_report": candidate_clean,
        "classic_main_reports": classic_reports,
        "conditions": conditions,
        "input_evidence": {
            "candidate_capture_manifest_file_sha256": file_hash(
                block / "candidate_capture" / "capture_manifest.json"
            ),
            "candidate_runtime_input_sha256": file_hash(candidate_input_path),
            "source_metrics_file_sha256": file_hash(source_metrics_path),
            "mahalanobis_pp_metrics_file_sha256": file_hash(
                mahalanobis_path
            ),
            "opendetect_capture_manifest_file_sha256": file_hash(
                opendetect_manifest_path
            ),
            "opendetect_metrics_file_sha256": file_hash(
                opendetect_metrics_path
            ),
            "split_fingerprints": split_values,
        },
        "archival_clean_metric_absolute_differences_diagnostic_only": {
            "opendetect": archival_metric_differences(
                opendetect_clean,
                opendetect_metrics["reports"]["opendetect"],
            )
        },
        "same_candidate_opendetect_clean_arrays": True,
        "same_corrupted_arrays_per_condition": True,
        "fresh_candidate_refit_performed": True,
        "fresh_opendetect_refit_performed": True,
        "mahalanobis_pp_recomputed_from_same_fresh_mlp_run": True,
        "test_labels_used_for_final_metrics_only": True,
        "unknown_or_test_labels_used_for_fitting_selection_or_corruption": False,
        "active_evaluator_sha256": protocol["implementation_sha256"][
            Path(__file__).name
        ],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    protocol = load(args.protocol)
    matches = [
        source
        for source in protocol.get("sources", [])
        if source_identity(source)
        == (args.suite, args.scenario, int(args.seed))
    ]
    if len(matches) != 1:
        raise ValueError("preconfirmation source identity is not unique")
    value = evaluate_source(
        protocol=protocol,
        project_root=root,
        run_root=args.run_root.resolve(),
        source=matches[0],
    )
    write_json(args.output, value)
    print(
        json.dumps(
            {
                "source": value["source"],
                "condition_count": len(value["conditions"]),
                "manifest_sha256": value["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
