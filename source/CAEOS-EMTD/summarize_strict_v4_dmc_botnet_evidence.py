from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any


ARCHIVE_SHA256 = (
    "3a9bc5dc38d11251e53d060a01b9d5402ce4299b848cc45276a4062f755cba31"
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def resource_summary(path: Path) -> dict[str, Any]:
    value = load(path)
    samples = value["samples"]
    utilization = [float(sample["utilization_percent"]) for sample in samples]
    if not utilization:
        raise ValueError(f"GPU evidence has no samples: {path}")
    return {
        "file": str(path),
        "file_sha256": file_hash(path),
        "manifest_sha256": value["manifest_sha256"],
        "passes": bool(value["passes"]),
        "sample_count": len(utilization),
        "mean_gpu_utilization_percent": statistics.fmean(utilization),
        "median_gpu_utilization_percent": statistics.median(utilization),
        "fraction_samples_at_least_50_percent": sum(
            item >= 50.0 for item in utilization
        )
        / len(utilization),
        "fraction_samples_at_least_80_percent": sum(
            item >= 80.0 for item in utilization
        )
        / len(utilization),
        "peak_gpu_utilization_percent": value[
            "peak_gpu_utilization_percent"
        ],
        "peak_gpu_memory_mib": value["peak_gpu_memory_mib"],
        "torch_peak_memory_allocated_mib": value[
            "torch_peak_memory_allocated_mib"
        ],
        "torch_peak_memory_reserved_mib": value[
            "torch_peak_memory_reserved_mib"
        ],
    }


def selected_metrics(path: Path) -> dict[str, Any]:
    value = load(path)
    selected = value["selected"]
    return {
        "file": str(path),
        "file_sha256": file_hash(path),
        "manifest_sha256": value["manifest_sha256"],
        "state": value["state"],
        "configuration": selected["configuration"],
        "metrics": selected["macro_mean"],
        "gates": selected["gates"],
    }


def summarize(root: Path) -> dict[str, Any]:
    results = root / "results"
    runs = root / "runs"
    branches = {
        "dmc_v1_full_statistics": selected_metrics(
            results
            / "strict_v4_dual_metric_contrastive_botnet_pilot_v1.json"
        ),
        "dmc_v2_dropout_0p5": selected_metrics(
            results
            / "strict_v4_dual_metric_contrastive_botnet_dropout_pilot_v2"
            / "dropout_0p5.json"
        ),
        "dmc_v2_dropout_1p0_interpretation_invalid": selected_metrics(
            results
            / "strict_v4_dual_metric_contrastive_botnet_dropout_pilot_v2"
            / "dropout_1p0.json"
        ),
        "dmc_v3_corrected_sequence_only": selected_metrics(
            results
            / "strict_v4_dual_metric_contrastive_botnet_sequence_control_v3"
            / "development.json"
        ),
    }
    complementarity_path = (
        results
        / "strict_v4_psf_dmc_complementarity_botnet_v1"
        / "development.json"
    )
    complementarity = load(complementarity_path)
    resource_paths = {
        "dmc_v1_full_statistics": (
            runs
            / "strict_v4_dual_metric_contrastive_botnet_pilot_v1"
            / "unknown_botnet_seed29"
            / "gpu_execution.json"
        ),
        "dmc_v2_dropout_0p5": (
            runs
            / "strict_v4_dual_metric_contrastive_botnet_dropout_pilot_v2"
            / "dropout_0p5"
            / "gpu_execution.json"
        ),
        "dmc_v2_dropout_1p0_interpretation_invalid": (
            runs
            / "strict_v4_dual_metric_contrastive_botnet_dropout_pilot_v2"
            / "dropout_1p0"
            / "gpu_execution.json"
        ),
        "dmc_v3_corrected_sequence_only": (
            runs
            / "strict_v4_dual_metric_contrastive_botnet_sequence_control_v3"
            / "gpu_execution.json"
        ),
    }
    return {
        "schema_version": "strict_v4_dmc_botnet_local_evidence_summary_v1",
        "archive_sha256": ARCHIVE_SHA256,
        "branches": branches,
        "resources": {
            name: resource_summary(path)
            for name, path in resource_paths.items()
        },
        "complementarity": {
            "file": str(complementarity_path),
            "file_sha256": file_hash(complementarity_path),
            "manifest_sha256": complementarity["manifest_sha256"],
            "state": complementarity["state"],
            "alignment": complementarity["alignment"],
            "selected_candidate": complementarity["selected_candidate"],
            "selected_validation": complementarity["selected_validation"],
            "test": complementarity["test"],
        },
        "incumbent_reference": {
            "system": "packet_sequence_fusion_development_v1",
            "botnet_alert_accuracy": 0.8970614425645592,
            "botnet_benign_fpr": 0.03651685393258427,
            "botnet_known_attack_type_accuracy": 0.9471821399401035,
            "botnet_unknown_attack_alert_recall": 0.5536585365853659,
        },
        "decision": {
            "expand_dmc_to_seven_scenarios": False,
            "retain_dmc_as_best_self_algorithm": False,
            "reason": (
                "No DMC or validation-selected PSF-DMC fusion branch met the "
                "pre-registered Botnet expansion threshold."
            ),
            "next_modeling_priority": (
                "Train an explicit shared malicious-boundary objective with "
                "family-held-out meta episodes; do not add another score fusion."
            ),
        },
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = summarize(args.bundle_root.resolve())
    args.output.resolve().write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["decision"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
