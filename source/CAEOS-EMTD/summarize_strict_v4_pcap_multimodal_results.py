from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


OPERATIONAL_METRICS = (
    "alert_accuracy",
    "alert_precision",
    "attack_recall",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
    "unknown_label_recall",
)
PAPER_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_result(result_dir: Path) -> dict[str, Any]:
    result_dir = result_dir.resolve()
    protocol_path = result_dir / "protocol.json"
    completion_path = result_dir / "completion.json"
    evaluation_path = result_dir / "evaluation.json"
    protocol = load_json(protocol_path)
    completion = load_json(completion_path)
    evaluation = load_json(evaluation_path)
    scenarios = {}
    for family in evaluation["unknown_families"]:
        metrics_path = result_dir / f"{family.lower()}_metrics.json"
        metrics = load_json(metrics_path)
        operational = metrics["operational_95_5"]
        paper = metrics["three_layer_metrics"]
        scenarios[family] = {
            "metrics_sha256": file_hash(metrics_path),
            "task_manifest_sha256": metrics["manifest_sha256"],
            "operational_95_5": {
                name: operational[name] for name in OPERATIONAL_METRICS
            },
            "paper_open_set": {
                name: paper[name] for name in PAPER_METRICS
            },
            "family_crossfit": {
                "enabled": str(
                    operational.get("alert_profile", "")
                ).startswith("family_crossfit_"),
                "selected_feature_profile": operational.get(
                    "family_crossfit_selected_feature_profile"
                ),
                "meta_selection_key": operational.get(
                    "family_crossfit_meta_selection_key"
                ),
                "meta_candidates": operational.get(
                    "family_crossfit_meta_candidates"
                ),
                "meta_true_unknown_scores_used": operational.get(
                    "family_crossfit_meta_true_unknown_scores_used"
                ),
                "oof_meta_recall_mean": operational.get(
                    "family_crossfit_oof_meta_recall_mean"
                ),
                "oof_meta_recall_worst": operational.get(
                    "family_crossfit_oof_meta_recall_worst"
                ),
                "oof_meta_recalls": operational.get(
                    "family_crossfit_oof_meta_recalls"
                ),
                "model_sha256": operational.get(
                    "family_crossfit_model_sha256"
                ),
                "true_unknown_used_for_training": operational.get(
                    "family_crossfit_true_unknown_used_for_training"
                ),
                "true_unknown_used_for_model_selection": operational.get(
                    "family_crossfit_true_unknown_used_for_model_selection"
                ),
                "true_unknown_used_for_threshold": operational.get(
                    "family_crossfit_true_unknown_used_for_threshold"
                ),
            },
        }
    return {
        "schema_version": (
            "strict_v4_pcap_multimodal_result_summary_v1"
        ),
        "result_dir": str(result_dir),
        "state": evaluation["state"],
        "protocol": {
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
            "alert_profile": protocol["training"]["alert_profile"],
        },
        "completion": {
            "file_sha256": file_hash(completion_path),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "evaluation": {
            "file_sha256": file_hash(evaluation_path),
            "manifest_sha256": evaluation["manifest_sha256"],
            "engineering_delivery_gate_pass": evaluation[
                "engineering_delivery_gate_pass"
            ],
            "paper_delivery_gate_pass": evaluation[
                "paper_delivery_gate_pass"
            ],
        },
        "resource_gate": evaluation["resource_gate"],
        "operational_95_5": evaluation["operational_95_5"],
        "paper_open_set": evaluation["paper_open_set"],
        "scenarios": scenarios,
    }


def mean_delta(
    candidate: dict[str, Any],
    reference: dict[str, Any],
    section: str,
    metrics: tuple[str, ...],
) -> dict[str, float]:
    return {
        name: (
            float(candidate[section][name]["mean"])
            - float(reference[section][name]["mean"])
        )
        for name in metrics
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--reference-dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    summary = summarize_result(args.result_dir)
    if args.reference_dir is not None:
        reference = summarize_result(args.reference_dir)
        summary["reference"] = {
            "result_dir": reference["result_dir"],
            "protocol_manifest_sha256": reference["protocol"][
                "manifest_sha256"
            ],
        }
        summary["mean_delta_vs_reference"] = {
            "operational_95_5": mean_delta(
                summary,
                reference,
                "operational_95_5",
                OPERATIONAL_METRICS,
            ),
            "paper_open_set": mean_delta(
                summary,
                reference,
                "paper_open_set",
                PAPER_METRICS,
            ),
        }
    rendered = json.dumps(
        summary,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    if args.output is not None:
        output = args.output.resolve()
        if output.exists():
            raise ValueError(f"refusing to overwrite summary: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
