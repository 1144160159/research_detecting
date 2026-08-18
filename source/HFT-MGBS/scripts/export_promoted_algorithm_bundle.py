#!/usr/bin/env python3
"""Export and qualify normal/fallback bundles for a promoted A09/A10 protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.algorithm_campaign import load_strict_json, sha256_file, validate_contract
from hft_mgbs.candidate_dataset import extract_candidate_flow_records
from hft_mgbs.quality import binary_prediction_metrics
from hft_mgbs.release_materializer import _json, _promotion_artifacts
from hft_mgbs.unsw import UnswGroundTruth
from hft_mgbs.domain_features import transform_feature_rows
from scripts.evaluate_unsw_independent_holdout import (
    canonical_sha256,
    selected_flow_fingerprint,
)
from scripts.export_a09_bundle import validate_candidate_policy


class PromotedBundleExportError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PromotedBundleExportError(name + " is not an object")
    return value


def _list(value: object, name: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise PromotedBundleExportError(name + " is not a list")
    return value


def _promotion_context(
    repo_root: Path,
    contract_path: Path,
    campaign_root: Path,
    promotion_dir: Path,
) -> Dict[str, Any]:
    _contract, _search, _artifacts, _protocols = validate_contract(
        repo_root, contract_path
    )
    promotion_manifest, promotion_artifacts = _promotion_artifacts(promotion_dir)
    promotion_receipt, promotion_receipt_raw = _json(
        promotion_artifacts["promotion_receipt.json"]
    )
    promoted_search, promoted_search_raw = _json(
        promotion_artifacts["algorithm_search_promoted.json"]
    )
    optimality, _optimality_raw = _json(
        promotion_artifacts["algorithm_optimality_audit.json"]
    )
    formal_path = campaign_root / "receipts" / "campaign_receipt.json"
    formal, formal_raw = _json(formal_path)
    contract_raw = contract_path.read_bytes()
    winner = promotion_receipt.get("winner")
    if (
        promotion_receipt.get("accepted") is not True
        or winner not in ("A09", "A10")
        or promoted_search.get("selected_candidate") != winner
        or promotion_manifest.get("winner") != winner
        or optimality.get("accepted") is not True
        or optimality.get("confirmatory_practical_winner") != winner
        or formal.get("accepted") is not True
        or formal.get("campaign_evidence_complete") is not True
        or formal.get("algorithm_only_practical_optimum_proven") is not True
    ):
        raise PromotedBundleExportError("promotion does not bind one accepted A09/A10 winner")
    if (
        _sha(formal_raw) != promotion_receipt.get("formal_receipt_sha256")
        or _sha(contract_raw) != promotion_receipt.get("contract_sha256")
        or _sha(promoted_search_raw)
        != promotion_receipt.get("promoted_algorithm_search_sha256")
    ):
        raise PromotedBundleExportError("promotion trust roots drifted")
    plan = _mapping(load_strict_json(campaign_root / "plan.json"), "campaign plan")
    if (
        plan.get("campaign_run_id") != formal.get("campaign_run_id")
        or _mapping(plan.get("contract"), "plan contract").get("sha256")
        != promotion_receipt.get("contract_sha256")
    ):
        raise PromotedBundleExportError("campaign plan identity drifted")
    jobs = {
        str(_mapping(item, "campaign job").get("candidate_id")): _mapping(
            item, "campaign job"
        )
        for item in _list(plan.get("jobs"), "campaign jobs")
    }
    job = jobs.get(str(winner))
    if job is None:
        raise PromotedBundleExportError("promoted winner is absent from the campaign plan")
    promoted_candidates = {
        str(_mapping(item, "promoted candidate").get("id")): _mapping(
            item, "promoted candidate"
        )
        for item in _list(promoted_search.get("candidates"), "promoted candidates")
    }
    promoted_candidate = promoted_candidates.get(str(winner))
    if promoted_candidate is None:
        raise PromotedBundleExportError("promoted winner has no candidate protocol")
    runner_environment = _mapping(
        job.get("runner_environment"), "winner runner environment"
    )
    expected_roles = _mapping(
        job.get("expected_capture_roles"), "winner expected capture roles"
    )
    protocol = {
        "adaptation_groups": [
            str(_mapping(item, "adaptation role")["group"])
            for item in _list(expected_roles.get("adaptation"), "adaptation roles")
        ],
        "calibration_groups": [
            str(_mapping(item, "calibration role")["group"])
            for item in _list(expected_roles.get("calibration"), "calibration roles")
        ],
        "adaptation_policy": runner_environment.get("ADAPTATION_POLICY"),
        "adaptation_weight_multiplier": float(
            runner_environment["ADAPTATION_WEIGHT_MULTIPLIER"]
        ),
        "calibration_attack_recall_floor": float(
            runner_environment["CALIBRATION_ATTACK_RECALL_FLOOR"]
        ),
        "classifier": runner_environment.get("CLASSIFIER"),
        "feature_profile": runner_environment.get("FEATURE_PROFILE"),
        "threshold_policy": runner_environment.get("THRESHOLD_POLICY"),
    }
    expected_adaptation_label = "{}_weight{:03d}".format(
        protocol["adaptation_policy"],
        int(round(float(protocol["adaptation_weight_multiplier"]) * 100.0)),
    )
    expected_threshold_label = "{}_floor{:03d}".format(
        protocol["threshold_policy"],
        int(round(float(protocol["calibration_attack_recall_floor"]) * 100.0)),
    )
    if (
        promoted_candidate.get("adaptation_policy") != expected_adaptation_label
        or promoted_candidate.get("threshold_policy") != expected_threshold_label
        or promoted_candidate.get("classifier") != protocol["classifier"]
        or promoted_candidate.get("feature_profile") != protocol["feature_profile"]
    ):
        raise PromotedBundleExportError(
            "promoted candidate labels do not replay the runner protocol"
        )
    validate_candidate_policy(str(winner), float(protocol["calibration_attack_recall_floor"]))
    if (
        protocol.get("classifier") != "extra_trees"
        or protocol.get("feature_profile") != "invariant_no_ports_v1"
        or protocol.get("adaptation_policy") != "calibration_weighted"
        or protocol.get("threshold_policy") != "calibration_macro_f1"
    ):
        raise PromotedBundleExportError("promoted winner is outside the bundle exporter profile")
    gpu = _mapping(plan.get("gpu_execution"), "plan gpu execution")
    return {
        "winner": str(winner),
        "formal_path": formal_path,
        "formal_sha256": _sha(formal_raw),
        "promotion_receipt_sha256": _sha(promotion_receipt_raw),
        "promoted_search_sha256": _sha(promoted_search_raw),
        "contract_sha256": _sha(contract_raw),
        "plan": plan,
        "job": job,
        "protocol": protocol,
        "hard_constraints": _mapping(
            promoted_search.get("hard_constraints"), "promoted hard constraints"
        ),
        "training_manifest": Path(str(gpu["training_manifest"])),
        "holdout_manifest": Path(str(gpu["holdout_manifest"])),
        "input_manifest": campaign_root / "input_sha256.json",
    }


def _extract_evaluation(
    holdout: Mapping[str, Any],
    truth: UnswGroundTruth,
    groups: Sequence[str],
    uniform: Mapping[str, Any],
    *,
    allow_deep: bool,
) -> Dict[str, Any]:
    selected_groups = set(groups)
    rows = []
    labels = []
    summaries = []
    eligible_event_ids = set()
    matched_event_ids = set()
    for sample in _list(holdout.get("samples"), "holdout samples"):
        sample = _mapping(sample, "holdout sample")
        group = str(sample["group"])
        if group not in selected_groups:
            continue

        def observe_flow(record: Mapping[str, Any]) -> None:
            for interval in truth.matching_intervals(
                tuple(record["forward_key"]),
                float(record["start_timestamp"]),
                float(record["last_timestamp"]),
                tolerance_s=0.0,
            ):
                if interval.event_id >= 0:
                    matched_event_ids.add(interval.event_id)

        records, summary = extract_candidate_flow_records(
            str(sample["path"]),
            group,
            batch_size=int(uniform["batch_size"]),
            budget_us=float(uniform["budget_us"]),
            allow_deep=allow_deep,
            key_flow_ratio=float(uniform["key_flow_ratio"]),
            max_payload_bytes=int(uniform["max_payload_bytes"]),
            max_packets=int(uniform["max_test_packets_per_capture"]),
            max_flows=int(uniform["max_test_flows_per_capture"]),
            execution_budget_safety_ratio=float(
                uniform["execution_budget_safety_ratio"]
            ),
            flow_record_observer=observe_flow,
        )
        sample_labels = [
            truth.label_flow_record(record, tolerance_s=0.0)
            for record in records
        ]
        if (
            summary["packet_start_timestamp"] is not None
            and summary["packet_last_timestamp"] is not None
        ):
            eligible_event_ids.update(
                truth.event_ids_overlapping(
                    summary["packet_start_timestamp"],
                    summary["packet_last_timestamp"],
                    tolerance_s=0.0,
                )
            )
        rows.extend(record["features"] for record in records)
        labels.extend(sample_labels)
        summaries.append(
            {
                "group": group,
                "selected_flows": len(records),
                "selected_flow_sha256": selected_flow_fingerprint(records),
                "selected_flow_label_sha256": canonical_sha256(sample_labels),
                "budget_overrun_count": int(summary["budget_overrun_count"]),
                "key_flow_coverage_min": float(summary["key_flow_coverage_min"]),
                "max_actual_optional_cost_us": float(
                    summary["max_actual_optional_cost_us"]
                ),
            }
        )
    if not rows or not eligible_event_ids:
        raise PromotedBundleExportError("deployment evaluation extraction is empty")
    if set(groups) != {item["group"] for item in summaries}:
        raise PromotedBundleExportError("deployment evaluation groups are incomplete")
    return {
        "rows": rows,
        "labels": [int(item) for item in labels],
        "summaries": summaries,
        "eligible_event_count": len(eligible_event_ids),
        "matched_event_count": len(matched_event_ids & eligible_event_ids),
        "ground_truth_event_recall": len(matched_event_ids & eligible_event_ids)
        / len(eligible_event_ids),
        "budget_overrun_count": sum(
            item["budget_overrun_count"] for item in summaries
        ),
        "key_flow_coverage_min": min(
            item["key_flow_coverage_min"] for item in summaries
        ),
        "budget_us_max": max(
            item["max_actual_optional_cost_us"] for item in summaries
        ),
    }


def _expected_sample_identity(raw: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    return [
        {
            "group": str(item["group"]),
            "selected_flows": int(item["selected_flows"]),
            "selected_flow_sha256": str(item["selected_flow_sha256"]),
            "selected_flow_label_sha256": str(item["selected_flow_label_sha256"]),
        }
        for item in _list(raw.get("holdout_captures"), "raw holdout captures")
    ]


def _constraint_violations(
    metrics: Mapping[str, Any], constraints: Mapping[str, Any]
) -> Sequence[str]:
    checks = (
        ("macro_f1", "min_macro_f1_min", lambda a, b: a >= b),
        ("attack_recall", "min_attack_recall_min", lambda a, b: a >= b),
        ("benign_recall", "min_benign_recall_min", lambda a, b: a >= b),
        ("auprc", "min_auprc_min", lambda a, b: a >= b),
        ("ece", "max_ece_max", lambda a, b: a <= b),
        (
            "ground_truth_event_recall",
            "min_ground_truth_event_recall_min",
            lambda a, b: a >= b,
        ),
        (
            "key_flow_coverage_min",
            "min_key_flow_coverage_min",
            lambda a, b: a >= b,
        ),
        (
            "budget_overrun_count",
            "max_budget_overrun_count_max",
            lambda a, b: a <= b,
        ),
        ("budget_us_max", "max_budget_us", lambda a, b: a <= b),
    )
    return [
        "{}={!r} violates {}={!r}".format(metric, metrics[metric], gate, constraints[gate])
        for metric, gate, predicate in checks
        if not predicate(float(metrics[metric]), float(constraints[gate]))
    ]


def export_promoted_bundle(
    *,
    repo_root: Path,
    contract_path: Path,
    campaign_root: Path,
    promotion_dir: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    if output_dir.exists() or output_dir.is_symlink():
        raise PromotedBundleExportError("bundle output directory must be new")
    context = _promotion_context(
        repo_root.resolve(strict=True),
        contract_path.resolve(strict=True),
        campaign_root.resolve(strict=True),
        promotion_dir.resolve(strict=True),
    )
    protocol = context["protocol"]
    plan = context["plan"]
    uniform = _mapping(plan.get("uniform_protocol"), "uniform protocol")
    parent = output_dir.parent.resolve(strict=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=output_dir.name + ".", suffix=".tmp", dir=str(parent))
    )
    try:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONPATH"] = str(repo_root)
        import joblib
        import numpy as np

        holdout = load_strict_json(context["holdout_manifest"])
        truth = UnswGroundTruth.from_csv(Path(str(holdout["ground_truth_csv"])))
        result_dir = campaign_root / "results" / "{}_{}".format(
            context["job"]["result_prefix"], context["job"]["run_tag"]
        )
        mode_qualifications = []
        for mode in ("normal", "fallback"):
            bundle_path = temporary / "{}_algorithm_bundle.joblib".format(mode)
            command = [
                sys.executable,
                str(repo_root / "scripts" / "export_a09_bundle.py"),
                str(context["training_manifest"]),
                str(context["holdout_manifest"]),
                "--output",
                str(bundle_path),
                "--candidate-id",
                context["winner"],
                "--release-id",
                "hft-mgbs-{}-formal-r5-{}".format(
                    context["winner"].lower(), mode
                ),
                "--adaptation-groups",
            ]
            command.extend(str(item) for item in protocol["adaptation_groups"])
            command.append("--calibration-groups")
            command.extend(str(item) for item in protocol["calibration_groups"])
            command.extend(
                [
                    "--adaptation-weight-multiplier",
                    str(protocol["adaptation_weight_multiplier"]),
                    "--calibration-attack-recall-floor",
                    str(protocol["calibration_attack_recall_floor"]),
                    "--max-train-packets-per-capture",
                    str(uniform["max_train_packets_per_capture"]),
                    "--max-train-flows-per-capture",
                    str(uniform["max_train_flows_per_capture"]),
                    "--max-holdout-packets-per-capture",
                    str(uniform["max_test_packets_per_capture"]),
                    "--max-holdout-flows-per-capture",
                    str(uniform["max_test_flows_per_capture"]),
                    "--estimators",
                    str(uniform["estimators"]),
                    "--n-jobs",
                    str(uniform["n_jobs"]),
                    "--seeds",
                ]
            )
            command.extend(str(item) for item in uniform["repeat_seeds"])
            command.extend(
                ["--input-hash-manifest", str(context["input_manifest"])]
            )
            if mode == "fallback":
                command.append("--disable-deep")
            completed = subprocess.run(
                command,
                cwd=str(repo_root),
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if completed.returncode != 0:
                raise PromotedBundleExportError(
                    "{} bundle exporter failed: {}".format(
                        mode, completed.stderr.strip()
                    )
                )
            bundle = joblib.load(bundle_path)
            if (
                bundle.get("candidate_id") != context["winner"]
                or bundle.get("execution_mode") != mode
                or bundle.get("feature_profile") != protocol["feature_profile"]
                or bundle.get("classifier") != protocol["classifier"]
                or len(bundle.get("models", [])) != len(uniform["repeat_seeds"])
                or len(bundle.get("thresholds", []))
                != len(uniform["repeat_seeds"])
            ):
                raise PromotedBundleExportError(
                    "{} exported bundle identity is invalid".format(mode)
                )
            evaluations = []
            for index in range(1, len(uniform["repeat_seeds"]) + 1):
                extracted = _extract_evaluation(
                    holdout,
                    truth,
                    uniform["fresh_evaluation_groups"],
                    uniform,
                    allow_deep=mode == "normal",
                )
                raw_path = result_dir / "{}_repeat{}.json".format(mode, index)
                raw = load_strict_json(raw_path)
                actual_identity = [
                    {
                        key: summary[key]
                        for key in (
                            "group",
                            "selected_flows",
                            "selected_flow_sha256",
                            "selected_flow_label_sha256",
                        )
                    }
                    for summary in extracted["summaries"]
                ]
                if actual_identity != list(_expected_sample_identity(raw)):
                    raise PromotedBundleExportError(
                        "{} deployment sample identity drifted in repeat {}".format(
                            mode, index
                        )
                    )
                matrix = bundle["vectorizer"].transform(
                    transform_feature_rows(
                        extracted["rows"], protocol["feature_profile"]
                    )
                ).astype(np.float32, copy=False)
                member_probabilities = [
                    model.predict_proba(matrix)[:, int(positive_index)]
                    for model, positive_index in zip(
                        bundle["models"], bundle["positive_indices"]
                    )
                ]
                probabilities = np.mean(member_probabilities, axis=0)
                threshold = float(statistics.median(bundle["thresholds"]))
                metrics = dict(
                    binary_prediction_metrics(
                        extracted["labels"], probabilities.tolist(), threshold
                    )
                )
                metrics.update(
                    {
                        "ground_truth_event_recall": extracted[
                            "ground_truth_event_recall"
                        ],
                        "eligible_event_count": extracted["eligible_event_count"],
                        "matched_event_count": extracted["matched_event_count"],
                        "key_flow_coverage_min": extracted[
                            "key_flow_coverage_min"
                        ],
                        "budget_overrun_count": extracted[
                            "budget_overrun_count"
                        ],
                        "budget_us_max": extracted["budget_us_max"],
                    }
                )
                violations = _constraint_violations(
                    metrics, context["hard_constraints"]
                )
                if violations:
                    raise PromotedBundleExportError(
                        "{} deployment bundle failed repeat {}: {}".format(
                            mode, index, "; ".join(violations)
                        )
                    )
                evaluations.append(
                    {
                        "repeat": index,
                        "formal_raw_path": str(raw_path),
                        "formal_raw_sha256": sha256_file(raw_path),
                        "sample_identity": actual_identity,
                        "evaluation_flow_count": len(extracted["labels"]),
                        "evaluation_labels_sha256": canonical_sha256(
                            extracted["labels"]
                        ),
                        "ensemble_probabilities_sha256": canonical_sha256(
                            probabilities.tolist()
                        ),
                        "decision_threshold": threshold,
                        "metrics": metrics,
                        "hard_constraint_violations": [],
                    }
                )
            manifest_path = bundle_path.with_suffix(".manifest.json")
            mode_qualifications.append(
                {
                    "mode": mode,
                    "bundle": bundle_path.name,
                    "bundle_sha256": sha256_file(bundle_path),
                    "bundle_manifest": manifest_path.name,
                    "bundle_manifest_sha256": sha256_file(manifest_path),
                    "model_count": len(bundle["models"]),
                    "feature_count": int(bundle["metadata"]["feature_count"]),
                    "thresholds": [float(item) for item in bundle["thresholds"]],
                    "ensemble_threshold": float(
                        statistics.median(bundle["thresholds"])
                    ),
                    "evaluation_repeats": evaluations,
                    "qualified": True,
                }
            )
        receipt = {
            "schema_version": 1,
            "scope": "hft_mgbs_promoted_algorithm_deployment_bundle_receipt_v2",
            "accepted": True,
            "candidate_id": context["winner"],
            "contract_sha256": context["contract_sha256"],
            "formal_receipt_sha256": context["formal_sha256"],
            "promotion_receipt_sha256": context["promotion_receipt_sha256"],
            "promoted_algorithm_search_sha256": context["promoted_search_sha256"],
            "exporter_sha256": sha256_file(repo_root / "scripts" / "export_a09_bundle.py"),
            "binding_exporter_sha256": sha256_file(Path(__file__)),
            "hard_constraints": dict(context["hard_constraints"]),
            "mode_qualifications": mode_qualifications,
            "normal_and_fallback_bundles_qualified": True,
            "formal_sample_identity_bound": True,
            "campaign_prediction_exact_replay": False,
            "campaign_prediction_exact_replay_inapplicable_reason": (
                "campaign feature tiers are measured-time adaptive; deployment "
                "artifacts are protocol-equivalent retrains and are independently "
                "qualified instead of being misreported as byte-identical models"
            ),
            "deployment_artifact_qualification_complete": True,
            "production_joint_optimum_proven": False,
            "final_pareto_ingestion_allowed": False,
        }
        (temporary / "export_receipt.json").write_bytes(_canonical(receipt))
        manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_promoted_algorithm_bundle_manifest_v1",
            "candidate_id": context["winner"],
            "artifacts": [
                {"path": path.name, "sha256": sha256_file(path)}
                for path in sorted(temporary.iterdir(), key=lambda item: item.name)
                if path.is_file()
            ],
            "production_release_accepted": False,
        }
        (temporary / "manifest.json").write_bytes(_canonical(manifest))
        if output_dir.exists() or output_dir.is_symlink():
            raise PromotedBundleExportError("bundle output raced")
        os.replace(str(temporary), str(output_dir))
    except BaseException:
        shutil.rmtree(str(temporary), ignore_errors=True)
        raise
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--promotion-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = export_promoted_bundle(
            repo_root=args.repo_root,
            contract_path=args.contract,
            campaign_root=args.campaign_root,
            promotion_dir=args.promotion_dir,
            output_dir=args.output_dir,
        )
    except (OSError, ValueError, KeyError, PromotedBundleExportError) as error:
        print("promoted bundle export rejected: {}".format(error), file=sys.stderr)
        return 74
    print(
        "candidate={} deployment_artifact_qualification_complete=true "
        "campaign_prediction_exact_replay=false".format(
            receipt["candidate_id"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
