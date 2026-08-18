import copy
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "algorithm_qualification_campaign_v1.json"
SEARCH = ROOT / "configs" / "algorithm_search_rc1.json"

from hft_mgbs.algorithm_campaign import (  # noqa: E402
    CampaignValidationError,
    _aggregate_mode_metrics,
    _candidate_receipt,
    _candidate_raw_metrics,
    _cross_candidate_resource_audit_errors,
    _projection,
    _referenced_input_paths,
    _stable_extraction_identity,
    _stable_file_bytes,
    _validate_code_manifest,
    _validate_environment_identity,
    _validate_input_manifest,
    _validate_raw_payload,
    compile_campaign_plan,
    discover_legacy_evidence,
    finalize_campaign,
    load_strict_json,
    sha256_file,
    validate_contract,
    write_json_atomic,
)
from hft_mgbs.algorithm_optimality import (  # noqa: E402
    METRIC_NAMES as OPTIMALITY_METRIC_NAMES,
    audit_algorithm_search,
)
from hft_mgbs.quality import select_macro_f1_threshold as shared_threshold_selector
from scripts.evaluate_unsw_independent_holdout import train_and_score


class AlgorithmCampaignContractTest(unittest.TestCase):
    def test_contract_compiles_exact_uniform_campaign(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="campaign-test",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        self.assertEqual(plan["candidate_count"], 10)
        self.assertEqual(plan["job_count"], 10)
        self.assertEqual(
            [job["candidate_id"] for job in plan["jobs"]],
            ["A{:02d}".format(index) for index in range(1, 11)],
        )
        self.assertEqual(plan["uniform_protocol"]["modes"], ["normal", "fallback"])
        self.assertEqual(plan["uniform_protocol"]["repeat_seeds"], [7, 11, 19])
        self.assertFalse(plan["execution_authorized"])
        self.assertFalse(plan["algorithm_only_qualification_complete"])
        self.assertFalse(plan["production_joint_optimum_proven"])
        self.assertFalse(plan["final_pareto_ingestion_allowed"])
        self.assertEqual(plan["algorithm_search"]["sha256"], sha256_file(SEARCH))

    def _mutated_contract(self, mutate):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.json"
            payload = json.loads(CONTRACT.read_text("utf-8"))
            mutate(payload)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(CampaignValidationError):
                validate_contract(ROOT, path)

    def test_rejects_search_hash_drift(self):
        self._mutated_contract(
            lambda value: value["algorithm_search"].update({"sha256": "0" * 64})
        )

    def test_rejects_bound_code_hash_drift(self):
        self._mutated_contract(
            lambda value: value["bound_repository_artifacts"]["evaluate_unsw"].update(
                {"sha256": "1" * 64}
            )
        )

    def test_rejects_missing_bound_artifact(self):
        self._mutated_contract(
            lambda value: value["bound_repository_artifacts"].pop("quality")
        )

    def test_rejects_missing_or_escaping_direct_python_execution_identity(self):
        for name in ("python_executable", "environment_prefix"):
            with self.subTest(name=name):
                self._mutated_contract(
                    lambda value, field=name: value["execution"].pop(field)
                )
        self._mutated_contract(
            lambda value: value["execution"].update(
                {"python_executable": "/usr/bin/python3"}
            )
        )

    def test_rejects_candidate_protocol_drift(self):
        self._mutated_contract(
            lambda value: value["candidate_protocols"][8].update(
                {"adaptation_weight_multiplier": 4.0}
            )
        )

    def test_rejects_dataset_role_leakage(self):
        self._mutated_contract(
            lambda value: value["dataset_roles"]["fresh_evaluation_groups"].append(
                "unsw_2015-01-22_shard3"
            )
        )

    def test_rejects_repeat_schedule_drift(self):
        self._mutated_contract(
            lambda value: value["uniform_protocol"].update(
                {"repeat_seeds": [7, 7, 19]}
            )
        )

    def test_rejects_non_dry_default(self):
        self._mutated_contract(
            lambda value: value["execution"].update({"default_mode": "execute"})
        )

    def test_rejects_gpu_result_root_escape(self):
        self._mutated_contract(
            lambda value: value["execution"].update(
                {"gpu_campaign_result_root": "/tmp/results"}
            )
        )

    def test_rejects_unsafe_campaign_id(self):
        with self.assertRaises(CampaignValidationError):
            compile_campaign_plan(
                ROOT,
                CONTRACT,
                campaign_run_id="../escape",
                created_at_utc="2026-08-13T00:00:00Z",
            )

    def test_strict_json_rejects_duplicate_key(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaises(CampaignValidationError):
                load_strict_json(path)

    def test_strict_json_rejects_nan_and_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            nan = Path(directory) / "nan.json"
            nan.write_text('{"x": NaN}', encoding="utf-8")
            with self.assertRaises(CampaignValidationError):
                load_strict_json(nan)
            bom = Path(directory) / "bom.json"
            bom.write_bytes(b"\xef\xbb\xbf{}")
            with self.assertRaises(CampaignValidationError):
                load_strict_json(bom)

    def test_legacy_discovery_never_qualifies(self):
        payload = discover_legacy_evidence(SEARCH)
        self.assertEqual(payload["candidate_count"], 10)
        self.assertEqual(payload["protocol_comparable_candidate_count"], 0)
        self.assertEqual(payload["campaign_qualified_candidate_count"], 0)
        self.assertFalse(payload["legacy_hashes_are_qualification_evidence"])
        self.assertFalse(payload["counts_toward_campaign"])
        self.assertTrue(
            all(record["protocol_comparable"] is False for record in payload["records"])
        )

    def test_prepare_cli_is_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "plan.json"
            environment = dict(os.environ)
            environment.pop("PYTHONPATH", None)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_algorithm_campaign.py"),
                    "--campaign-run-id",
                    "cli-test",
                    "--contract",
                    str(CONTRACT),
                    "--created-at-utc",
                    "2026-08-13T00:00:00Z",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text("utf-8"))
            self.assertEqual(payload["execution_mode"], "dry_run_plan")
            self.assertFalse(payload["execution_authorized"])
            self.assertFalse(payload["final_pareto_ingestion_allowed"])

    def test_finalize_cli_missing_campaign_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = Path(directory) / "missing"
            output = Path(directory) / "receipt.json"
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(ROOT)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "finalize_algorithm_campaign.py"),
                    str(campaign),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            payload = json.loads(output.read_text("utf-8"))
            self.assertFalse(payload["accepted"])
            self.assertFalse(payload["campaign_evidence_complete"])
            self.assertFalse(payload["source_algorithm_search_modified"])
            self.assertFalse(payload["final_pareto_ingestion_allowed"])

    def test_contract_does_not_modify_frozen_search(self):
        before = SEARCH.read_bytes()
        compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="immutability-test",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        self.assertEqual(SEARCH.read_bytes(), before)

    def _isolated_raw_job(self, source_job):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        fixture_root = Path(temporary.name)
        ground_truth_path = fixture_root / "ground_truth.csv"
        with ground_truth_path.open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "Protocol", "Source IP", "Destination IP", "Source Port",
                    "Destination Port", "Start time", "Last time", "Attack category",
                ],
            )
            writer.writeheader()
            for event_id in range(1, 11):
                writer.writerow({
                    "Protocol": "tcp",
                    "Source IP": "10.0.0.{}".format(event_id),
                    "Destination IP": "10.0.1.{}".format(event_id),
                    "Source Port": event_id,
                    "Destination Port": 1000 + event_id,
                    "Start time": 1.0,
                    "Last time": 2.0,
                    "Attack category": "test",
                })
        job = copy.deepcopy(source_job)
        job["expected_ground_truth_csv"] = str(ground_truth_path.resolve())
        samples = []
        seen_samples = set()
        for role in ("calibration", "adaptation", "holdout"):
            for sample in job["expected_capture_roles"][role]:
                identity = (str(sample["group"]), str(sample["path"]))
                if identity not in seen_samples:
                    samples.append(copy.deepcopy(sample))
                    seen_samples.add(identity)
        manifest_path = fixture_root / "holdout_manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "ground_truth_csv": job["expected_ground_truth_csv"],
                    "samples": samples,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        job["_test_holdout_manifest"] = str(manifest_path.resolve())
        return job, manifest_path

    @staticmethod
    def _raw_payload(job, mode, seed, input_hash="f" * 64):
        env = job["runner_environment"]
        fixture_manifest_path = Path(str(job.get("_test_holdout_manifest", "")))
        if not fixture_manifest_path.is_file():
            raise AssertionError("raw payload tests require an isolated holdout fixture")
        fixture_manifest = json.loads(fixture_manifest_path.read_text("utf-8"))
        if fixture_manifest.get("ground_truth_csv") != job.get(
            "expected_ground_truth_csv"
        ):
            raise AssertionError("isolated holdout fixture identity drift")
        evaluation_labels = [1] * 20 + [0] * 60
        evaluation_probabilities = (
            [0.9] * 16 + [0.1] * 4 + [0.9] * 3 + [0.1] * 57
        )
        calibration_selection = None
        if env["THRESHOLD_POLICY"] == "calibration_macro_f1":
            selected = shared_threshold_selector(
                evaluation_labels,
                evaluation_probabilities,
                float(env["CALIBRATION_ATTACK_RECALL_FLOOR"]),
            )
            calibration_selection = {
                name: selected[name]
                for name in (
                    "threshold",
                    "macro_f1",
                    "balanced_accuracy",
                    "attack_recall",
                    "benign_recall",
                    "predicted_attack_ratio",
                    "minimum_attack_recall_constraint",
                )
            }
            decision_threshold = selected["threshold"]
            confusion = {name: selected[name] for name in ("TP", "TN", "FP", "FN")}
            macro_f1 = selected["macro_f1"]
            balanced_accuracy = selected["balanced_accuracy"]
            attack_recall = selected["attack_recall"]
            benign_recall = selected["benign_recall"]
            predicted_attack_ratio = selected["predicted_attack_ratio"]
            auroc = selected["auroc"]
            auprc = selected["auprc"]
            ece = selected["ece"]
        else:
            decision_threshold = 0.5
            confusion = {"TP": 16, "TN": 57, "FP": 3, "FN": 4}
            attack_recall = confusion["TP"] / (confusion["TP"] + confusion["FN"])
            benign_recall = confusion["TN"] / (confusion["TN"] + confusion["FP"])
            balanced_accuracy = (attack_recall + benign_recall) / 2.0
            predicted_attack_ratio = (confusion["TP"] + confusion["FP"]) / 80.0
            macro_f1 = (
                (2.0 * confusion["TP"])
                / (2.0 * confusion["TP"] + confusion["FP"] + confusion["FN"])
                + (2.0 * confusion["TN"])
                / (2.0 * confusion["TN"] + confusion["FP"] + confusion["FN"])
            ) / 2.0
            auroc = 0.875
            auprc = 0.7236842105263157
            ece = 0.04
        role_totals = {
            "training": 100,
            "calibration": 80,
            "adaptation": 10 if env["ADAPTATION_GROUPS"] else 0,
            "holdout": 80,
        }

        def capture_rows(role):
            samples = job["expected_capture_roles"][role]
            total = role_totals[role]
            counts = [
                total // len(samples) + int(index < total % len(samples))
                for index in range(len(samples))
            ] if samples else []
            attack_total = 20 if role in ("calibration", "holdout") else 4
            attack_counts = [
                attack_total // len(samples)
                + int(index < attack_total % len(samples))
                for index in range(len(samples))
            ] if samples and role != "training" else []
            rows = []
            for index, (sample, selected) in enumerate(zip(samples, counts)):
                row = {
                    "group": sample["group"],
                    "path": sample["path"],
                    "execution_budget_safety_ratio": float(env["SAFETY_RATIO"]),
                    "parsed_packets": 100,
                    "rejected_records": 0,
                    "packet_start_timestamp": 1.0,
                    "packet_last_timestamp": 2.0,
                    "flow_records": selected,
                    "selected_flows": selected,
                    "budget_overrun_count": 0,
                    "key_flow_total": 10,
                    "key_flow_covered": 10,
                    "key_flow_coverage": 1.0,
                    "key_flow_coverage_min": 1.0,
                    "max_actual_optional_cost_us": 100.0,
                    "batch_audits": [
                        {
                            "batch_index": 0,
                            "packet_count": 100,
                            "key_flow_total": 10,
                            "key_flow_covered": 10,
                            "budget_overrun_count": 0,
                            "actual_used_us": 100.0,
                        }
                    ],
                    "tier_counts": {"base": 1, "flow": 1, "deep": 1},
                    "selected_flow_sha256": hashlib.sha256(
                        (sample["group"] + "\0" + sample["path"] + "\0" + str(selected)).encode("utf-8")
                    ).hexdigest(),
                }
                if role != "training":
                    attack = attack_counts[index]
                    row["attack_flows"] = attack
                    row["benign_flows"] = selected - attack
                    row["selected_flow_label_sha256"] = hashlib.sha256(
                        json.dumps(
                            [1] * attack + [0] * (selected - attack),
                            separators=(",", ":"),
                        ).encode("utf-8")
                    ).hexdigest()
                rows.append(row)
            return rows

        role_captures = {
            role: capture_rows(role)
            for role in ("training", "calibration", "adaptation", "holdout")
        }
        evaluation_groups = list(job["expected_fresh_evaluation_groups"])
        eligible_by_group = {group: list(range(1, 11)) for group in evaluation_groups}
        matched_by_group = {
            group: values[:8] for group, values in eligible_by_group.items()
        }
        eligible_count = len(set().union(*(set(value) for value in eligible_by_group.values())))
        matched_count = len(set().union(*(set(value) for value in matched_by_group.values())))
        matched_witnesses = [
            {
                "event_id": event_id,
                "group": group,
                "normalized_forward_key": [
                    "10.0.0.{}".format(event_id),
                    "10.0.1.{}".format(event_id),
                    event_id,
                    1000 + event_id,
                    6,
                ],
                "start_timestamp_hex": float(1.0).hex(),
                "last_timestamp_hex": float(2.0).hex(),
            }
            for group in sorted(evaluation_groups)
            for event_id in range(1, 9)
        ]

        def role_audit(role):
            rows = role_captures[role]
            return {
                "budget_overrun_count": 0,
                "key_flow_total": 10 * len(rows),
                "key_flow_covered": 10 * len(rows),
                "key_flow_coverage": 1.0,
                "key_flow_coverage_min": 1.0,
                "max_actual_optional_cost_us": 100.0,
            }
        return {
            "schema_version": 1,
            "scope": "independent_cross_dataset_holdout",
            "candidate": {
                "mode": mode,
                "batch_size": int(env["BATCH_SIZE"]),
                "budget_us": int(env["BUDGET_US"]),
                "execution_budget_safety_ratio": float(env["SAFETY_RATIO"]),
            },
            "protocol": {
                "training_dataset": "USTC-TFC2016",
                "holdout_dataset": "UNSW-NB15",
                "dataset_overlap": (
                    "no_capture_overlap_between_fit_calibration_evaluation"
                    if env["ADAPTATION_GROUPS"]
                    else "none"
                ),
                "holdout_label_alignment": (
                    "bidirectional_5tuple_and_flow_attack_time_overlap"
                ),
                "alignment_tolerance_s": float(env["ALIGNMENT_TOLERANCE_S"]),
                "max_train_packets_per_capture": int(
                    env["MAX_TRAIN_PACKETS_PER_CAPTURE"]
                ),
                "max_train_flows_per_capture": int(
                    env["MAX_TRAIN_FLOWS_PER_CAPTURE"]
                ),
                "max_test_packets_per_capture": int(
                    env["MAX_TEST_PACKETS_PER_CAPTURE"]
                ),
                "max_test_flows_per_capture": int(
                    env["MAX_TEST_FLOWS_PER_CAPTURE"]
                ),
                "estimators": int(env["ESTIMATORS"]),
                "n_jobs": int(env["N_JOBS"]),
                "key_flow_ratio": float(env["KEY_FLOW_RATIO"]),
                "max_payload_bytes": int(env["MAX_PAYLOAD_BYTES"]),
                "seeds": [seed],
                "feature_profile": env["FEATURE_PROFILE"],
                "classifier": env["CLASSIFIER"],
                "threshold_policy": env["THRESHOLD_POLICY"],
                "calibration_used_for_threshold": (
                    env["THRESHOLD_POLICY"] == "calibration_macro_f1"
                ),
                "calibration_attack_recall_floor": float(
                    env["CALIBRATION_ATTACK_RECALL_FLOOR"]
                ),
                "calibration_groups": sorted(
                    filter(None, env["CALIBRATION_GROUPS"].split(","))
                ),
                "adaptation_policy": env["ADAPTATION_POLICY"],
                "adaptation_groups": sorted(
                    filter(None, env["ADAPTATION_GROUPS"].split(","))
                ),
                "adaptation_weight_multiplier": float(
                    env["ADAPTATION_WEIGHT_MULTIPLIER"]
                ),
                "evaluation_groups": list(job["expected_fresh_evaluation_groups"]),
            },
            "capture_counts": dict(job["expected_capture_counts"]),
            "ground_truth": {
                "rows_total": 10,
                "rows_indexed": 10,
                "rows_unsupported_protocol": 0,
                "rows_invalid_endpoint": 0,
                "rows_invalid_time": 0,
                "indexed_key_count": 10,
            },
            "input_hash_evidence": {
                "path": "/gpu/input_sha256.json",
                "sha256": input_hash,
                "entry_count": 27,
                "required_path_count": 27,
                "all_required_paths_frozen": True,
            },
            "training_captures": role_captures["training"],
            "calibration_captures": role_captures["calibration"],
            **(
                {"adaptation_captures": role_captures["adaptation"]}
                if role_captures["adaptation"] else {}
            ),
            "holdout_captures": role_captures["holdout"],
            "training_constraint_audit": role_audit("training"),
            "calibration_constraint_audit": role_audit("calibration"),
            **(
                {"adaptation_constraint_audit": role_audit("adaptation")}
                if role_captures["adaptation"] else {}
            ),
            "holdout_constraint_audit": role_audit("holdout"),
            "ground_truth_event_recall_audit": {
                "scope": "indexed_tcp_udp_events_overlapping_processed_packet_time",
                "eligible_event_count": eligible_count,
                "matched_event_count": matched_count,
                "event_recall": matched_count / eligible_count,
                "computed_before_flow_sampling": True,
                "eligible_event_ids_by_group": eligible_by_group,
                "matched_event_ids_by_group": matched_by_group,
                "eligible_event_ids_sha256": hashlib.sha256(
                    json.dumps(
                        eligible_by_group,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
                "matched_event_ids_sha256": hashlib.sha256(
                    json.dumps(
                        matched_by_group,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
                "matched_event_witnesses": matched_witnesses,
            },
            "quality": {
                "classifier": (
                    {
                        "name": "ExtraTreesClassifier",
                        "n_estimators": int(env["ESTIMATORS"]),
                        "min_samples_leaf": 2,
                        "class_weight": "balanced",
                        "n_jobs": int(env["N_JOBS"]),
                    }
                    if env["CLASSIFIER"] == "extra_trees"
                    else {
                        "name": "LogisticRegression",
                        "solver": "liblinear",
                        "max_iter": 2000,
                        "class_weight": "balanced",
                        "standard_scaler": True,
                    }
                ),
                "feature_profile": env["FEATURE_PROFILE"],
                "threshold_policy": env["THRESHOLD_POLICY"],
                "calibration_used_for_threshold": (
                    env["THRESHOLD_POLICY"] == "calibration_macro_f1"
                ),
                "calibration_attack_recall_floor": float(
                    env["CALIBRATION_ATTACK_RECALL_FLOOR"]
                ),
                "calibration_groups": sorted(
                    filter(None, env["CALIBRATION_GROUPS"].split(","))
                ),
                "adaptation_policy": env["ADAPTATION_POLICY"],
                "adaptation_groups": sorted(
                    filter(None, env["ADAPTATION_GROUPS"].split(","))
                ),
                "adaptation_weight_multiplier": float(
                    env["ADAPTATION_WEIGHT_MULTIPLIER"]
                ),
                "evaluation_groups": list(job["expected_fresh_evaluation_groups"]),
                "feature_count": 20,
                "train_flow_count": 100,
                "adaptation_flow_count": 10 if env["ADAPTATION_GROUPS"] else 0,
                "fit_flow_count": 110 if env["ADAPTATION_GROUPS"] else 100,
                "calibration_flow_count": 80,
                "test_flow_count": 80,
                "test_attack_count": 20,
                "test_benign_count": 60,
                "seeds": [
                    {
                        "seed": seed,
                        "decision_threshold": decision_threshold,
                        **confusion,
                        "evaluation_labels": evaluation_labels,
                        "evaluation_probabilities": evaluation_probabilities,
                        "calibration_labels": (
                            evaluation_labels
                            if env["THRESHOLD_POLICY"] == "calibration_macro_f1"
                            else []
                        ),
                        "calibration_probabilities": (
                            evaluation_probabilities
                            if env["THRESHOLD_POLICY"] == "calibration_macro_f1"
                            else []
                        ),
                        "macro_f1": macro_f1,
                        "balanced_accuracy": balanced_accuracy,
                        "auroc": auroc,
                        "auprc": auprc,
                        "benign_recall": benign_recall,
                        "attack_recall": attack_recall,
                        "ece": ece,
                        "predicted_attack_ratio": predicted_attack_ratio,
                        **(
                            {
                                "calibration_selection": calibration_selection
                            }
                            if env["THRESHOLD_POLICY"]
                            == "calibration_macro_f1"
                            else {}
                        ),
                    }
                ],
                "aggregate_confusion_matrix": confusion,
                "conservative": {
                    "macro_f1_min": macro_f1,
                    "balanced_accuracy_min": balanced_accuracy,
                    "auroc_min": auroc,
                    "attack_recall_min": attack_recall,
                    "benign_recall_min": benign_recall,
                    "auprc_min": auprc,
                    "ece_max": ece,
                }
            },
            "final_quality_eligible": False,
            "missing_final_evidence": ["frozen_min_primary_metric"],
        }

    def test_raw_repeat_recomputes_metrics(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-test",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][0])
        payloads = [
            self._raw_payload(job, "normal", seed)
            for seed in job["expected_repeat_seeds"]
        ]
        for payload, seed in zip(payloads, job["expected_repeat_seeds"]):
            _validate_raw_payload(payload, job, "normal", seed, "f" * 64, 27)
        metrics = _candidate_raw_metrics(payloads, 5000)
        self.assertAlmostEqual(metrics["macro_f1_min"], 0.8813307904216995)
        self.assertEqual(metrics["budget_overrun_count_max"], 0.0)
        paired = _aggregate_mode_metrics(
            {"normal": metrics, "fallback": dict(metrics)}
        )
        self.assertEqual(paired, metrics)

    def test_raw_repeat_uses_configured_hard_budget_for_overrun_evidence(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-hard-budget-boundary",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][0])
        payload = self._raw_payload(job, "normal", 7)
        soft_limit = float(job["runner_environment"]["BUDGET_US"]) * float(
            job["runner_environment"]["SAFETY_RATIO"]
        )
        hard_limit = float(job["runner_environment"]["BUDGET_US"])
        observed_cost = soft_limit + 0.5
        self.assertLess(observed_cost, hard_limit)
        payload["training_captures"][0]["max_actual_optional_cost_us"] = observed_cost
        payload["training_captures"][0]["batch_audits"][0][
            "actual_used_us"
        ] = observed_cost
        payload["training_constraint_audit"][
            "max_actual_optional_cost_us"
        ] = observed_cost
        _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_raw_repeat_replays_directional_event_witness_after_normalization(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-directional-event-witness",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][0])
        payload = self._raw_payload(job, "normal", 7)
        witness = payload["ground_truth_event_recall_audit"][
            "matched_event_witnesses"
        ][0]
        source, destination, source_port, destination_port, protocol = witness[
            "normalized_forward_key"
        ]
        witness["normalized_forward_key"] = [
            destination,
            source,
            destination_port,
            source_port,
            protocol,
        ]
        _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_synthetic_raw_fixture_isolated_from_existing_contract_ground_truth(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-existing-ground-truth-isolation",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        source_job = copy.deepcopy(plan["jobs"][0])
        with tempfile.TemporaryDirectory() as directory:
            production_ground_truth = Path(directory) / "production_gt.csv"
            production_ground_truth.write_text(
                "Protocol,Source IP,Destination IP,Source Port,Destination Port,Start time,Last time,Attack category\n"
                "tcp,192.0.2.1,192.0.2.2,1,2,100,200,production\n",
                encoding="utf-8",
            )
            source_job["expected_ground_truth_csv"] = str(production_ground_truth)
            isolated_job, fixture_manifest = self._isolated_raw_job(source_job)
            self.assertEqual(
                source_job["expected_ground_truth_csv"], str(production_ground_truth)
            )
            self.assertNotEqual(
                isolated_job["expected_ground_truth_csv"],
                source_job["expected_ground_truth_csv"],
            )
            manifest = json.loads(fixture_manifest.read_text("utf-8"))
            self.assertEqual(
                manifest["ground_truth_csv"], isolated_job["expected_ground_truth_csv"]
            )
            payload = self._raw_payload(isolated_job, "normal", 7)
            _validate_raw_payload(
                payload, isolated_job, "normal", 7, "f" * 64, 27
            )

    def test_shared_threshold_selector_preserves_sentinel_and_ascending_tie(self):
        tied = shared_threshold_selector(
            [1, 0, 1, 0], [0.75, 0.6, 0.25, 0.0], 0.0
        )
        self.assertEqual(tied["threshold"], 0.25)
        sentinel = shared_threshold_selector([0, 0, 1], [1.0, 0.8, 0.1], 0.0)
        self.assertEqual(sentinel["threshold"], 1.0 + 1e-12)
        self.assertEqual(sentinel["predicted_attack_ratio"], 0.0)

    def test_real_evaluator_quality_validates_for_fixed_calibrated_and_adapted(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="real-evaluator-validator-test",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        train_labels = [index % 2 for index in range(100)]
        train_rows = [
            {
                "packet_protocol": 6.0,
                "packet_src_port": 1000.0 + index,
                "packet_dst_port": 80.0,
                "flow_packets": 2.0 + 20.0 * label,
                "flow_bytes": 100.0 + 900.0 * label,
                "flow_payload_bytes": 20.0 + 500.0 * label,
                "quality_seen_deep_tier": float(label),
            }
            for index, label in enumerate(train_labels)
        ]
        train_groups = ["train{}".format(index % 10) for index in range(100)]
        for job_index in (0, 1, 8):
            job, _fixture_manifest = self._isolated_raw_job(
                plan["jobs"][job_index]
            )
            env = job["runner_environment"]
            calibration_groups = sorted(filter(None, env["CALIBRATION_GROUPS"].split(",")))
            adaptation_groups = sorted(filter(None, env["ADAPTATION_GROUPS"].split(",")))
            evaluation_groups = list(job["expected_fresh_evaluation_groups"])
            test_groups = []
            test_labels = []

            def append_partition(groups, total, attacks):
                labels = [1] * attacks + [0] * (total - attacks)
                test_labels.extend(labels)
                test_groups.extend(groups[index % len(groups)] for index in range(total))

            append_partition(calibration_groups, 80, 20)
            if adaptation_groups:
                append_partition(adaptation_groups, 10, 4)
            append_partition(evaluation_groups, 80, 20)
            test_rows = [
                {
                    "packet_protocol": 6.0,
                    "packet_src_port": 2000.0 + index,
                    "packet_dst_port": 80.0,
                    "flow_packets": 2.0 + 20.0 * label,
                    "flow_bytes": 100.0 + 900.0 * label,
                    "flow_payload_bytes": 20.0 + 500.0 * label,
                    "quality_seen_deep_tier": float(label),
                }
                for index, label in enumerate(test_labels)
            ]
            quality = train_and_score(
                train_rows, train_labels, train_groups,
                test_rows, test_labels, [7], int(env["ESTIMATORS"]),
                int(env["N_JOBS"]), test_groups=test_groups,
                calibration_groups=calibration_groups,
                adaptation_groups=adaptation_groups,
                adaptation_policy=env["ADAPTATION_POLICY"],
                adaptation_weight_multiplier=float(env["ADAPTATION_WEIGHT_MULTIPLIER"]),
                threshold_policy=env["THRESHOLD_POLICY"],
                calibration_attack_recall_floor=float(env["CALIBRATION_ATTACK_RECALL_FLOOR"]),
                feature_profile=env["FEATURE_PROFILE"], classifier=env["CLASSIFIER"],
            )
            payload = self._raw_payload(job, "normal", 7)
            payload["quality"] = quality
            _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_raw_repeat_rejects_each_frozen_execution_parameter_drift(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-execution-limit-negative",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][8])
        fields = (
            "max_train_packets_per_capture",
            "max_train_flows_per_capture",
            "max_test_packets_per_capture",
            "max_test_flows_per_capture",
            "estimators",
            "n_jobs",
            "key_flow_ratio",
            "max_payload_bytes",
            "alignment_tolerance_s",
        )
        for name in fields:
            payload = self._raw_payload(job, "normal", 7)
            payload["protocol"][name] = payload["protocol"][name] + 1
            with self.subTest(name=name), self.assertRaises(
                CampaignValidationError
            ):
                _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_raw_repeat_rejects_protocol_capture_and_accounting_drift(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-protocol-negative",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][8])
        mutations = (
            lambda value: value["protocol"].update({"training_dataset": "other"}),
            lambda value: value["protocol"].update({"dataset_overlap": "none"}),
            lambda value: value["capture_counts"].update({"holdout": 2}),
            lambda value: value["quality"].update({"train_flow_count": 0}),
            lambda value: value["ground_truth_event_recall_audit"].update(
                {"matched_event_count": 7}
            ),
        )
        for mutate in mutations:
            payload = self._raw_payload(job, "normal", 7)
            mutate(payload)
            with self.assertRaises(CampaignValidationError):
                _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_raw_repeat_rejects_each_role_flow_capacity_tamper(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-flow-capacity-negative",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        no_adaptation, _no_adaptation_manifest = self._isolated_raw_job(
            plan["jobs"][0]
        )
        adapted, _adapted_manifest = self._isolated_raw_job(plan["jobs"][8])
        cases = (
            (
                no_adaptation,
                "train_flow_count",
                no_adaptation["expected_capture_counts"]["training"]
                * int(no_adaptation["runner_environment"]["MAX_TRAIN_FLOWS_PER_CAPTURE"])
                + 1,
            ),
            (
                no_adaptation,
                "calibration_flow_count",
                no_adaptation["expected_capture_counts"]["calibration"]
                * int(no_adaptation["runner_environment"]["MAX_TEST_FLOWS_PER_CAPTURE"])
                + 1,
            ),
            (no_adaptation, "adaptation_flow_count", 1),
            (
                no_adaptation,
                "test_flow_count",
                no_adaptation["expected_capture_counts"]["holdout"]
                * int(no_adaptation["runner_environment"]["MAX_TEST_FLOWS_PER_CAPTURE"])
                + 1,
            ),
            (adapted, "calibration_flow_count", 0),
            (adapted, "adaptation_flow_count", 0),
        )
        for job, name, value in cases:
            payload = self._raw_payload(job, "normal", 7)
            payload["quality"][name] = value
            if name in ("train_flow_count", "adaptation_flow_count"):
                payload["quality"]["fit_flow_count"] = (
                    payload["quality"]["train_flow_count"]
                    + payload["quality"]["adaptation_flow_count"]
                )
            with self.subTest(candidate=job["candidate_id"], field=name):
                with self.assertRaises(CampaignValidationError):
                    _validate_raw_payload(
                        payload, job, "normal", 7, "f" * 64, 27
                    )

    def test_raw_repeat_recomputes_prediction_evidence_and_confusion(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-confusion-negative",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][0])
        mutations = (
            lambda value: value["quality"]["seeds"][0].update({"TP": 17}),
            lambda value: value["quality"]["seeds"][0].update(
                {
                    "attack_recall": 1.0,
                    "benign_recall": 1.0,
                    "balanced_accuracy": 1.0,
                    "macro_f1": 1.0,
                }
            ),
            lambda value: value["quality"]["seeds"][0][
                "evaluation_probabilities"
            ].__setitem__(0, 0.0),
            lambda value: value["quality"]["aggregate_confusion_matrix"].update(
                {"FN": 5}
            ),
            lambda value: value["quality"].update({"test_attack_count": 21}),
        )
        for mutate in mutations:
            payload = self._raw_payload(job, "normal", 7)
            mutate(payload)
            with self.assertRaises(CampaignValidationError):
                _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_raw_repeat_rejects_out_of_range_or_inconsistent_metrics(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-metric-negative",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][0])
        mutations = (
            lambda value: value["quality"]["conservative"].update(
                {"macro_f1_min": 1.01}
            ),
            lambda value: value["quality"]["seeds"][0].update({"auprc": -0.01}),
            lambda value: value["training_constraint_audit"].update(
                {"key_flow_coverage_min": 1.01}
            ),
            lambda value: value["holdout_constraint_audit"].update(
                {"budget_overrun_count": -1}
            ),
            lambda value: value["holdout_constraint_audit"].update(
                {"budget_overrun_count": 0.5}
            ),
            lambda value: value["quality"]["conservative"].update(
                {"macro_f1_min": 0.7}
            ),
        )
        for mutate in mutations:
            payload = self._raw_payload(job, "normal", 7)
            mutate(payload)
            with self.assertRaises(CampaignValidationError):
                _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_raw_repeat_rejects_seed_group_and_metric_tamper(self):
        plan = compile_campaign_plan(
            ROOT,
            CONTRACT,
            campaign_run_id="raw-negative",
            created_at_utc="2026-08-13T00:00:00Z",
        )
        job, _fixture_manifest = self._isolated_raw_job(plan["jobs"][8])
        for mutation in (
            lambda payload: payload["protocol"].update({"seeds": [11]}),
            lambda payload: payload["protocol"]["evaluation_groups"].append(
                "unsw_2015-01-22_shard3"
            ),
            lambda payload: payload["input_hash_evidence"].update(
                {"sha256": "0" * 64}
            ),
        ):
            payload = self._raw_payload(job, "normal", 7)
            mutation(payload)
            with self.assertRaises(CampaignValidationError):
                _validate_raw_payload(payload, job, "normal", 7, "f" * 64, 27)

    def test_projection_accepts_real_receipt_metric_superset_and_proves_only_algorithm_optimum(self):
        search = json.loads(SEARCH.read_text("utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            receipts = {}
            for index in range(1, 11):
                candidate_id = "A{:02d}".format(index)
                path = Path(directory) / "{}.json".format(candidate_id)
                path.write_text(
                    json.dumps({"candidate_id": candidate_id}), encoding="utf-8"
                )
                strong = index == 9
                metrics = {
                    "macro_f1_min": 0.9 if strong else 0.75,
                    "balanced_accuracy_min": 0.91 if strong else 0.76,
                    "auroc_min": 0.92 if strong else 0.77,
                    "attack_recall_min": 0.9 if strong else 0.75,
                    "benign_recall_min": 0.98 if strong else 0.94,
                    "auprc_min": 0.8 if strong else 0.5,
                    "ece_max": 0.01 if strong else 0.04,
                    "ground_truth_event_recall_min": 0.9 if strong else 0.75,
                    "key_flow_coverage_min": 1.0,
                    "budget_overrun_count_max": 0.0,
                    "budget_us_max": 5000.0,
                }
                receipt = {
                    "mode_contract": {
                        "repeat_count_by_mode": {"normal": 3, "fallback": 3},
                        "repeat_seeds_by_mode": {
                            "normal": [7, 11, 19],
                            "fallback": [7, 11, 19],
                        },
                        "input_hash_manifest_sha256": "f" * 64,
                    },
                    "mode_metrics": {
                        "normal": dict(metrics),
                        "fallback": dict(metrics),
                    },
                    "reported_worst_case_metrics": dict(metrics),
                }
                receipts[candidate_id] = (receipt, path)
            # The campaign can only be finalized under the contract's POSIX GPU
            # root.  This Windows-only unit test exercises the projection logic
            # while preserving the production path-cleanliness gate.
            with patch(
                "hft_mgbs.algorithm_optimality._path_is_clean", return_value=True
            ):
                projection, audit = _projection(search, receipts)
            self.assertTrue(audit["accepted"])
            self.assertTrue(audit["algorithm_only_practical_optimum_proven"])
            self.assertFalse(audit["production_joint_optimum_proven"])
            self.assertFalse(audit["final_pareto_ingestion_allowed"])
            self.assertEqual(projection["selected_candidate"], "A09")
            for candidate in projection["candidates"]:
                self.assertEqual(
                    set(candidate["reported_worst_case_metrics"]),
                    set(OPTIMALITY_METRIC_NAMES),
                )
            tampered = copy.deepcopy(projection)
            tampered["candidates"][8]["reported_worst_case_metrics"][
                "macro_f1_min"
            ] -= 0.01
            tampered_audit = audit_algorithm_search(tampered)
            self.assertFalse(tampered_audit["accepted"])
            self.assertIn(
                "A09.reported_worst_case_metrics", tampered_audit["errors"]
            )

    def test_projection_is_not_published_before_end_state_revalidation(self):
        import inspect

        source = inspect.getsource(finalize_campaign)
        publish = source.index("published_projection_sha = write_json_atomic")
        for gate in (
            "campaign contract changed before output sealing",
            "algorithm search changed before output sealing",
            "campaign plan changed before output sealing",
            "bound repository code changed before output sealing",
            "campaign environment changed before output sealing",
            "campaign input changed before output sealing",
            "campaign input stat identity changed before output sealing",
        ):
            self.assertLess(source.index(gate), publish)
        self.assertNotIn("write_json_atomic(projection_path", source[:publish])

    def test_stable_extraction_identity_excludes_runtime_audits(self):
        identity = {
            "role_flow_counts": {"training": 1},
            "role_audits": {"training": {"actual_used_us": 10.0}},
            "role_fingerprints": {"training": ["f" * 64]},
            "role_label_fingerprints": {"training": ["e" * 64]},
            "fresh_evaluation_identity": {"evaluation_labels_sha256": "a" * 64},
        }
        changed = copy.deepcopy(identity)
        changed["role_audits"]["training"]["actual_used_us"] = 99.0
        self.assertEqual(
            _stable_extraction_identity(identity),
            _stable_extraction_identity(changed),
        )
        changed["role_fingerprints"]["training"] = ["d" * 64]
        self.assertNotEqual(
            _stable_extraction_identity(identity),
            _stable_extraction_identity(changed),
        )

    def test_cross_candidate_sample_identity_drift_is_rejected(self):
        jobs = [
            {
                "candidate_id": candidate_id,
                "expected_capture_roles": {
                    "training": ["train"],
                    "calibration": [],
                    "adaptation": [],
                    "holdout": ["fresh"],
                },
            }
            for candidate_id in ("A01", "A02")
        ]

        def receipt(fingerprint):
            role = {
                "flow_count": 1,
                "selected_flow_fingerprints": [fingerprint],
                "selected_flow_label_fingerprints": ["e" * 64],
            }
            return {
                "mode_metrics": {
                    mode: {
                        "key_flow_coverage_min": 1.0,
                        "budget_overrun_count_max": 0,
                        "budget_us_max": 1.0,
                        "ground_truth_event_recall_min": 1.0,
                    }
                    for mode in ("normal", "fallback")
                },
                "mode_resource_identity": {
                    mode: {
                        role_name: copy.deepcopy(role)
                        for role_name in (
                            "training", "calibration", "adaptation", "holdout"
                        )
                    }
                    for mode in ("normal", "fallback")
                }
            }

        receipts = {
            "A01": (receipt("f" * 64), Path("A01.json")),
            "A02": (receipt("d" * 64), Path("A02.json")),
        }
        errors = _cross_candidate_resource_audit_errors(receipts, jobs)
        self.assertIn(
            "campaign:inconsistent_normal_training_resource_identity", errors
        )
        self.assertIn(
            "campaign:inconsistent_fallback_holdout_resource_identity", errors
        )

    def test_cross_candidate_mode_resource_metrics_cross_role_partitions(self):
        jobs = [
            {
                "candidate_id": "A01",
                "expected_capture_roles": {
                    "training": ["train"], "calibration": ["cal-a", "cal-b", "cal-c"],
                    "adaptation": [], "holdout": ["fresh-a", "fresh-b", "fresh-c"],
                },
            },
            {
                "candidate_id": "A09",
                "expected_capture_roles": {
                    "training": ["train"], "calibration": ["cal-a"],
                    "adaptation": ["cal-b", "cal-c"],
                    "holdout": ["fresh-a", "fresh-b", "fresh-c"],
                },
            },
        ]
        role = {
            "flow_count": 1,
            "selected_flow_fingerprints": ["f" * 64],
            "selected_flow_label_fingerprints": ["e" * 64],
        }

        def receipt(**overrides):
            resource_metrics = {
                "key_flow_coverage_min": 1.0,
                "budget_overrun_count_max": 0,
                "budget_us_max": 1.0,
                "ground_truth_event_recall_min": 1.0,
            }
            resource_metrics.update(overrides)
            return {
                "mode_metrics": {
                    mode: copy.deepcopy(resource_metrics)
                    for mode in ("normal", "fallback")
                },
                "mode_resource_identity": {
                    mode: {
                        role_name: copy.deepcopy(role)
                        for role_name in (
                            "training", "calibration", "adaptation", "holdout"
                        )
                    }
                    for mode in ("normal", "fallback")
                },
            }

        for field, value in (
            ("key_flow_coverage_min", 0.99),
            ("budget_overrun_count_max", 1),
            ("budget_us_max", 999.0),
            ("ground_truth_event_recall_min", 0.99),
        ):
            errors = _cross_candidate_resource_audit_errors(
                {
                    "A01": (receipt(), Path("A01.json")),
                    "A09": (receipt(**{field: value}), Path("A09.json")),
                },
                jobs,
            )
            with self.subTest(field=field):
                self.assertEqual(errors, [])

    def test_finalize_rehashes_frozen_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text('{"frozen": true}', encoding="utf-8")
            manifest = root / "input_sha256.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "algorithm": "sha256",
                        "entry_count": 1,
                        "entries": [
                            {
                                "path": str(source),
                                "size_bytes": source.stat().st_size,
                                "sha256": sha256_file(source),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch(
                "hft_mgbs.algorithm_campaign._clean_absolute_path",
                side_effect=lambda value, _name: value,
            ):
                _validate_input_manifest(manifest, verify_referenced_files=True)
                source.write_text('{"frozen": false}', encoding="utf-8")
                with self.assertRaises(CampaignValidationError):
                    _validate_input_manifest(manifest, verify_referenced_files=True)

    def test_input_manifest_requires_exact_referenced_path_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "sample.pcap"
            truth = root / "truth.csv"
            sample.write_bytes(b"pcap")
            truth.write_bytes(b"truth")
            training = root / "training.json"
            holdout = root / "holdout.json"
            training.write_text(
                json.dumps({"samples": [{"path": str(sample)}]}), encoding="utf-8"
            )
            holdout.write_text(
                json.dumps(
                    {"ground_truth_csv": str(truth), "samples": []}
                ),
                encoding="utf-8",
            )
            manifest = root / "input_sha256.json"

            def write_manifest(paths):
                entries = [
                    {
                        "path": str(path),
                        "size_bytes": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                    for path in paths
                ]
                manifest.write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "algorithm": "sha256",
                            "entry_count": len(entries),
                            "entries": entries,
                        }
                    ),
                    encoding="utf-8",
                )

            with patch(
                "hft_mgbs.algorithm_campaign._clean_absolute_path",
                side_effect=lambda value, _name: value,
            ):
                expected = _referenced_input_paths([training, holdout])
                write_manifest([training, holdout, sample, truth])
                result = _validate_input_manifest(
                    manifest, verify_referenced_files=True, expected_paths=expected
                )
                self.assertEqual(result["entry_count"], 4)
                write_manifest([training, holdout, sample])
                with self.assertRaises(CampaignValidationError):
                    _validate_input_manifest(
                        manifest,
                        verify_referenced_files=True,
                        expected_paths=expected,
                    )
                unrelated = root / "unrelated.bin"
                unrelated.write_bytes(b"unrelated")
                write_manifest([training, holdout, sample, truth, unrelated])
                with self.assertRaises(CampaignValidationError):
                    _validate_input_manifest(
                        manifest,
                        verify_referenced_files=True,
                        expected_paths=expected,
                    )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_stable_reader_rejects_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            link = root / "link.json"
            target.write_text("{}", encoding="utf-8")
            try:
                os.symlink(str(target), str(link))
            except OSError:
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(CampaignValidationError):
                _stable_file_bytes(link, "test symlink")

    def test_stable_reader_rejects_mid_read_metadata_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text("{}", encoding="utf-8")
            observed = os.stat(str(path))
            before = types.SimpleNamespace(
                st_mode=observed.st_mode,
                st_dev=observed.st_dev,
                st_ino=observed.st_ino,
                st_size=observed.st_size,
                st_mtime_ns=observed.st_mtime_ns,
                st_ctime_ns=observed.st_ctime_ns,
            )
            after = types.SimpleNamespace(
                st_mode=observed.st_mode,
                st_dev=observed.st_dev,
                st_ino=observed.st_ino,
                st_size=observed.st_size,
                st_mtime_ns=observed.st_mtime_ns + 1,
                st_ctime_ns=observed.st_ctime_ns,
            )
            with patch(
                "hft_mgbs.algorithm_campaign.os.fstat",
                side_effect=[before, after],
            ):
                with self.assertRaises(CampaignValidationError):
                    _stable_file_bytes(path, "drifting file")

    def test_stable_reader_identity_includes_ctime(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text("{}", encoding="utf-8")
            observed = os.stat(str(path))
            before = types.SimpleNamespace(
                st_mode=observed.st_mode,
                st_dev=observed.st_dev,
                st_ino=observed.st_ino,
                st_size=observed.st_size,
                st_mtime_ns=observed.st_mtime_ns,
                st_ctime_ns=observed.st_ctime_ns,
            )
            after = types.SimpleNamespace(
                st_mode=observed.st_mode,
                st_dev=observed.st_dev,
                st_ino=observed.st_ino,
                st_size=observed.st_size,
                st_mtime_ns=observed.st_mtime_ns,
                st_ctime_ns=observed.st_ctime_ns + 1,
            )
            with patch(
                "hft_mgbs.algorithm_campaign.os.fstat",
                side_effect=[before, after],
            ):
                with self.assertRaises(CampaignValidationError):
                    _stable_file_bytes(path, "ctime-drifting file")

    def test_environment_identity_recomputes_exact_target_prefix_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign_root = Path(directory)
            prefix = campaign_root / "env"
            metadata_dir = prefix / "conda-meta"
            metadata_dir.mkdir(parents=True)
            site_packages = prefix / "lib" / "python3.9" / "site-packages"
            site_packages.mkdir(parents=True)
            module_file = site_packages / "module.py"
            module_file.write_bytes(b"__version__ = '1'\n")
            unmanaged_startup = site_packages / "sitecustomize.py"
            unmanaged_startup.write_bytes(b"raise RuntimeError('must not execute')\n")
            python_executable = prefix / "python"
            python_executable.write_bytes(b"frozen-python")
            metadata_path = metadata_dir / "test-1.json"
            metadata_path.write_text(
                json.dumps({"files": ["python"]}), encoding="utf-8"
            )
            environment_entries = []
            for target in sorted(
                prefix.rglob("*"), key=lambda item: item.relative_to(prefix).as_posix()
            ):
                status = target.lstat()
                entry = {
                    "path": target.relative_to(prefix).as_posix(),
                    "device": status.st_dev,
                    "inode": status.st_ino,
                    "mode": status.st_mode,
                    "link_count": status.st_nlink,
                    "size_bytes": status.st_size,
                    "mtime_ns": status.st_mtime_ns,
                    "ctime_ns": status.st_ctime_ns,
                }
                if target.is_dir():
                    entry["type"] = "directory"
                else:
                    entry.update({"type": "regular", "sha256": sha256_file(target)})
                environment_entries.append(entry)
            root_status = prefix.lstat()
            root_identity = {
                "device": root_status.st_dev,
                "inode": root_status.st_ino,
                "mode": root_status.st_mode,
                "link_count": root_status.st_nlink,
                "size_bytes": root_status.st_size,
                "mtime_ns": root_status.st_mtime_ns,
                "ctime_ns": root_status.st_ctime_ns,
            }
            environment_files_path = campaign_root / "environment_files_sha256.json"
            environment_files_path.write_text(json.dumps({
                "schema_version": 4,
                "scope": "hft_mgbs_python_environment_tree_sha256_v4",
                "environment_prefix": str(prefix),
                "root_identity": root_identity,
                "entry_count": len(environment_entries),
                "regular_file_count": sum(
                    item["type"] == "regular" for item in environment_entries
                ),
                "symlink_count": 0,
                "directory_count": sum(
                    item["type"] == "directory" for item in environment_entries
                ),
                "total_hashed_bytes": sum(
                    item["size_bytes"] for item in environment_entries
                    if item["type"] == "regular"
                ),
                "entries": environment_entries,
            }, indent=2, sort_keys=True), encoding="utf-8")
            runtime_path = campaign_root / "runtime_bootstrap_identity.json"
            runtime_path.write_text(json.dumps({
                "schema_version": 1,
                "scope": "hft_mgbs_stdlib_bound_python_runtime_v1",
                "prefix": str(prefix),
                "executable": str(python_executable),
                "executable_sha256": sha256_file(python_executable),
                "site_packages": [str(site_packages)],
            }, indent=2, sort_keys=True), encoding="utf-8")
            tool_file = campaign_root / "tool"
            tool_file.write_bytes(b"frozen-tool")
            tool_names = sorted({
                "bash", "cmp", "date", "dirname", "find", "flock", "id", "mkdir",
                "python3", "rm", "seq", "sha256sum", "stat", "truncate", "wc",
            })
            external_tools_path = campaign_root / "external_tools_sha256.json"
            external_tools_path.write_text(json.dumps({
                "schema_version": 1,
                "scope": "hft_mgbs_algorithm_campaign_external_tools_v1",
                "entry_count": len(tool_names),
                "entries": [
                    {
                        "name": name,
                        "invoked_path": str(tool_file),
                        "resolved_path": os.path.realpath(str(tool_file)),
                        "sha256": sha256_file(tool_file),
                    }
                    for name in tool_names
                ],
            }, indent=2, sort_keys=True), encoding="utf-8")
            thread_names = (
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
                "BLIS_NUM_THREADS",
                "JOBLIB_TEMP_FOLDER",
                "PYTHONHASHSEED",
                "CUDA_VISIBLE_DEVICES",
            )
            identity_path = campaign_root / "environment_identity.json"
            payload = {
                "schema_version": 2,
                "scope": "hft_mgbs_algorithm_campaign_environment_identity_v2",
                "environment_prefix": str(prefix),
                "environment_files_manifest_path": str(environment_files_path),
                "environment_files_manifest_sha256": sha256_file(environment_files_path),
                "environment_files_manifest_entry_count": len(environment_entries),
                "external_tools_manifest_path": str(external_tools_path),
                "external_tools_manifest_sha256": sha256_file(external_tools_path),
                "external_tools_manifest_entry_count": len(tool_names),
                "runtime_bootstrap_identity_path": str(runtime_path),
                "runtime_bootstrap_identity_sha256": sha256_file(runtime_path),
                "python": {
                    "version": "3.9.0",
                    "implementation": "CPython",
                    "executable": str(python_executable),
                    "executable_sha256": sha256_file(python_executable),
                    "site_packages": [str(site_packages)],
                },
                "packages": {
                    name: {
                        "version": "1",
                        "module_file": str(module_file),
                        "module_file_sha256": sha256_file(module_file),
                    }
                    for name in ("numpy", "scipy", "sklearn", "joblib")
                },
                "thread_environment": {name: None for name in thread_names},
            }
            identity_path.write_text(json.dumps(payload), encoding="utf-8")
            execution = {
                "environment_prefix": str(prefix),
                "python_executable": str(python_executable),
            }
            with patch(
                "hft_mgbs.algorithm_campaign._clean_absolute_path",
                side_effect=lambda value, _name: str(value),
            ):
                validated = _validate_environment_identity(identity_path, execution)
                self.assertEqual(validated["environment_prefix"], str(prefix))
                unmanaged_startup.write_bytes(b"raise RuntimeError('drift')\n")
                with self.assertRaises(CampaignValidationError):
                    _validate_environment_identity(identity_path, execution)

    def test_atomic_json_writer_refuses_existing_uncontrolled_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "receipt.json"
            target.write_text('{"owner": "external"}\n', encoding="utf-8")
            before = target.read_bytes()
            with self.assertRaises(CampaignValidationError):
                write_json_atomic(target, {"accepted": False})
            self.assertEqual(target.read_bytes(), before)

    @unittest.skipUnless(hasattr(os, "link"), "hard links required")
    def test_atomic_json_writer_refuses_existing_hard_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "receipt.json"
            alias = root / "alias.json"
            target.write_text("{}\n", encoding="utf-8")
            try:
                os.link(str(target), str(alias))
            except OSError:
                self.skipTest("hard-link creation is unavailable")
            with self.assertRaises(CampaignValidationError):
                write_json_atomic(target, {})

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_atomic_json_writer_refuses_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            link = root / "receipt.json"
            target.write_text("{}\n", encoding="utf-8")
            try:
                os.symlink(str(target), str(link))
            except OSError:
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(CampaignValidationError):
                write_json_atomic(link, {"accepted": True})

    def test_code_manifest_is_exact_and_rejects_alias_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pkg").mkdir()
            artifact = root / "pkg" / "bound.py"
            artifact.write_text("BOUND = True\n", encoding="utf-8")
            digest = sha256_file(artifact)
            artifacts = {
                "bound": {"path": "pkg/bound.py", "sha256": digest}
            }
            manifest = root / "code_sha256.txt"
            manifest.write_text(
                "{}  ./pkg/bound.py\n".format(digest), encoding="utf-8"
            )
            _validate_code_manifest(manifest, root, artifacts)
            manifest.write_text(
                "{}  ./pkg/bound.py\n{}  pkg/bound.py\n".format(
                    digest, digest
                ),
                encoding="utf-8",
            )
            with self.assertRaises(CampaignValidationError):
                _validate_code_manifest(manifest, root, artifacts)

    def test_code_manifest_rejects_extra_unbound_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "bound.py"
            extra = root / "extra.py"
            artifact.write_text("BOUND = True\n", encoding="utf-8")
            extra.write_text("EXTRA = True\n", encoding="utf-8")
            digest = sha256_file(artifact)
            extra_digest = sha256_file(extra)
            manifest = root / "code_sha256.txt"
            manifest.write_text(
                "{}  ./bound.py\n{}  ./extra.py\n".format(
                    digest, extra_digest
                ),
                encoding="utf-8",
            )
            with self.assertRaises(CampaignValidationError):
                _validate_code_manifest(
                    manifest,
                    root,
                    {"bound": {"path": "bound.py", "sha256": digest}},
                )

    def test_candidate_receipt_uses_exact_runner_run_id_not_prefix_glob(self):
        source = __import__("inspect").getsource(_candidate_receipt)
        self.assertIn(
            'run_id = "{}_{}".format(job["result_prefix"], job["run_tag"])',
            source,
        )
        self.assertNotIn("glob(", source)
        self.assertNotIn('"{}_{}_"', source)


class AlgorithmCampaignRunnerContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "scripts" / "run_algorithm_qualification_campaign.sh").read_text(
            "utf-8"
        )

    def _inline_python_after(self, marker):
        marker_index = self.text.index(marker)
        prefix = "-c '\n"
        start = self.text.index(prefix, marker_index) + len(prefix)
        end = self.text.index("\n'", start)
        return self.text[start:end]

    def test_runner_defaults_to_dry_run(self):
        self.assertIn('execute="${HFT_ALGORITHM_CAMPAIGN_EXECUTE:-NO}"', self.text)

    def test_formal_python_bootstraps_are_isolated_and_skip_site(self):
        self.assertNotIn("PYTHONPATH=", self.text)
        self.assertIn(
            '"${target_python}" -I -S -B -c "${bound_python_launcher}"',
            self.text,
        )
        self.assertNotIn("python -I -B", self.text)
        self.assertNotIn('"${bootstrap_python}" -I -B', self.text)
        self.assertNotRegex(
            self.text, r'"\$\{bootstrap_python\}"\s+-(?!I\s+-S\s+-B)'
        )
        self.assertNotRegex(
            self.text, r'"\$\{python_bin\}"\s+-(?!I\s+-S\s+-B)'
        )
        self.assertIn("sys.pycache_prefix", self.text)
        self.assertNotIn("site.addsitedir", self.text)
        self.assertIn("hft_mgbs_python_environment_tree_sha256_v4", self.text)
        self.assertIn("verify_environment_files_fast", self.text)
        self.assertGreaterEqual(
            self.text.count('capture_environment_files_manifest "${environment_files_verify}"'),
            2,
        )

    def test_formal_execution_never_invokes_conda_and_uses_contract_python_directly(self):
        self.assertNotIn("conda_program", self.text)
        self.assertNotIn("conda_environment", self.text)
        self.assertNotRegex(self.text, r"\bconda\s+(?:run|list)\b")
        self.assertIn('target_python="${execution_fields[3]}"', self.text)
        self.assertIn('environment_prefix="${execution_fields[4]}"', self.text)
        self.assertIn(
            '"${target_python}" -I -S -B -c "${bound_python_launcher}"',
            self.text,
        )
        self.assertIn(
            'safe_capture_output "${output}" NO "${bootstrap_python}" -I -S -B -c',
            self.text,
        )

    def test_formal_startup_write_status_python_helper_executes(self):
        code = self._inline_python_after("write_status() {")
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                "-B",
                "-c",
                code,
                "formal-r3",
                "initializing",
                "0",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["campaign_run_id"], "formal-r3")
        self.assertEqual(payload["status"], "initializing")
        self.assertEqual(payload["exit_code"], 0)

    def test_safe_capture_python_c_fixed_argv_contracts_are_in_bounds(self):
        import re

        contracts = (
            ("write_status() {", 3),
            ("capture_runtime_bootstrap_identity() {", 3),
            ('safe_capture_output "${checkpoint}" NO', 13),
            ("write_job_status() {", 4),
            ('safe_capture_output "${code_manifest_output}" NO', 2),
            ("capture_environment_identity() {", 6),
            ("capture_environment_files_manifest() {", 1),
            ("capture_input_stat_manifest() {", 1),
            ('safe_capture_output "${run_dir}/result_sha256.txt"', 1),
        )
        for marker, argument_count in contracts:
            code = self._inline_python_after(marker)
            fixed_indices = [
                int(value) for value in re.findall(r"sys\.argv\[([0-9]+)\]", code)
            ]
            with self.subTest(marker=marker):
                self.assertTrue(fixed_indices)
                self.assertLessEqual(max(fixed_indices), argument_count)

    def test_bound_launcher_ignores_shadow_modules_pth_and_old_repo_pyc(self):
        import py_compile
        import re
        import sysconfig

        match = re.search(
            r"bound_python_launcher='(.*?)'\nbound_python_cmd=",
            self.text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        launcher = match.group(1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            package = repo / "hft_mgbs"
            package.mkdir(parents=True)
            probe = repo / "probe.py"
            scripts_package = repo / "scripts"
            scripts_package.mkdir()
            scripts_init = scripts_package / "__init__.py"
            scripts_init.write_text(
                "raise RuntimeError('executed unbound scripts package initializer')\n",
                encoding="utf-8",
            )
            helper = scripts_package / "bound_helper.py"
            helper.write_text("VALUE = 'bound-helper'\n", encoding="utf-8")
            (repo / "numpy.py").write_text(
                "raise RuntimeError('repo numpy shadow executed')\n", encoding="utf-8"
            )
            sklearn_shadow = repo / "sklearn"
            sklearn_shadow.mkdir()
            (sklearn_shadow / "__init__.py").write_text(
                "raise RuntimeError('repo sklearn shadow executed')\n", encoding="utf-8"
            )
            probe.write_text(
                "import json, pathlib, numpy, sklearn, hft_mgbs\n"
                "from scripts.bound_helper import VALUE\n"
                "print(json.dumps({'safe': hft_mgbs.SAFE, 'helper': VALUE, "
                "'numpy': numpy.__file__, 'sklearn': sklearn.__file__, "
                "'pathlib': pathlib.Path('.').name}))\n",
                encoding="utf-8",
            )
            init = package / "__init__.py"
            init.write_text("raise RuntimeError('executed stale repo pyc')\n", encoding="utf-8")
            (package / "__pycache__").mkdir()
            py_compile.compile(
                str(init),
                cfile=str(package / "__pycache__" / ("__init__.{}.pyc".format(
                    sys.implementation.cache_tag
                ))),
                doraise=True,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
            )
            init.write_text("SAFE = True\n", encoding="utf-8")
            for name in ("json.py", "pathlib.py"):
                (repo / name).write_text("raise RuntimeError('shadow stdlib executed')\n", encoding="utf-8")
            malicious_cwd = root / "cwd"
            malicious_cwd.mkdir()
            for name in ("json.py", "pathlib.py"):
                (malicious_cwd / name).write_text("raise RuntimeError('cwd shadow executed')\n", encoding="utf-8")
            malicious_site = root / "site"
            malicious_site.mkdir()
            marker = root / "site-executed"
            (malicious_site / "sitecustomize.py").write_text(
                "from pathlib import Path\nPath({!r}).write_text('site')\n".format(str(marker)),
                encoding="utf-8",
            )
            (malicious_site / "evil.pth").write_text(
                "import pathlib; pathlib.Path({!r}).write_text('pth')\n".format(str(marker)),
                encoding="utf-8",
            )
            binding = root / "binding.json"
            binding.write_text(json.dumps({
                "bound_repository_artifacts": {
                    "probe": {"path": "probe.py", "sha256": sha256_file(probe)},
                    "package_init": {"path": "hft_mgbs/__init__.py", "sha256": sha256_file(init)},
                    "bound_helper": {
                        "path": "scripts/bound_helper.py",
                        "sha256": sha256_file(helper),
                    },
                }
            }), encoding="utf-8")
            paths = sysconfig.get_paths()
            site_packages = []
            for name in ("purelib", "platlib"):
                value = os.path.realpath(paths[name])
                if value not in site_packages:
                    site_packages.append(value)
            runtime = root / "runtime.json"
            runtime.write_text(json.dumps({
                "schema_version": 1,
                "scope": "hft_mgbs_stdlib_bound_python_runtime_v1",
                "prefix": os.path.realpath(sys.prefix),
                "executable": os.path.realpath(sys.executable),
                "executable_sha256": sha256_file(Path(sys.executable)),
                "site_packages": site_packages,
            }), encoding="utf-8")
            cache = root / "empty-cache"
            cache.mkdir()
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(malicious_site)
            completed = subprocess.run(
                [
                    sys.executable, "-I", "-S", "-B", "-c", launcher,
                    str(repo), str(probe), str(runtime), str(cache), str(binding),
                ],
                cwd=malicious_cwd,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('"safe": true', completed.stdout.lower())
            self.assertIn('"helper": "bound-helper"', completed.stdout.lower())
            self.assertNotIn(str(repo).lower(), completed.stdout.lower())
            self.assertFalse(marker.exists())
        self.assertIn('if [[ "${execute}" != "YES" ]]', self.text)

    def test_runner_requires_exact_authorization_and_contract_root(self):
        self.assertIn("APPROVED_BOUNDED_A01_A10_QUALIFICATION", self.text)
        self.assertIn("HFT_ALGORITHM_CAMPAIGN_TRUSTED_CONTRACT_SHA256", self.text)
        self.assertIn("actual_contract_sha", self.text)

    def test_runner_has_lock_atomic_checkpoints_and_resume(self):
        self.assertIn("flock -n 9", self.text)
        self.assertIn('lock_root="/tmp/hft_algorithm_campaign_locks"', self.text)
        self.assertNotIn("HFT_ALGORITHM_CAMPAIGN_LOCK_ROOT", self.text)
        self.assertIn('lock_path="${lock_root}/${campaign_run_id}.lock"', self.text)
        self.assertNotIn('exec 9> "${campaign_root}/campaign.lock"', self.text)
        self.assertIn("checkpoint_valid", self.text)
        self.assertIn("run_atomic_json", self.text)
        self.assertIn("sha256sum -c --status", self.text)
        self.assertIn('run_id="${result_prefix}_${run_tag}"', self.text)
        self.assertIn("finish_on_signal 129", self.text)

    def test_repeat_checkpoint_binds_all_execution_identity(self):
        for field in (
            "input_manifest_sha256",
            "contract_sha256",
            "code_manifest_sha256",
            "runner_args_sha256",
            "environment_identity_sha256",
            "environment_files_manifest_sha256",
            "external_tools_manifest_sha256",
            "runtime_bootstrap_identity_sha256",
            "input_stat_manifest_sha256",
        ):
            self.assertIn(field, self.text)
        self.assertIn("verify_execution_identity", self.text)
        self.assertGreaterEqual(self.text.count("verify_execution_identity"), 3)
        self.assertIn("verify_frozen_input_files", self.text)

    def test_runner_manifest_records_all_frozen_execution_parameters(self):
        for field in (
            "max_train_packets_per_capture",
            "max_train_flows_per_capture",
            "max_test_packets_per_capture",
            "max_test_flows_per_capture",
            "estimators",
            "n_jobs",
            "key_flow_ratio",
            "max_payload_bytes",
            "alignment_tolerance_s",
        ):
            self.assertIn('"{}"'.format(field), self.text)
        self.assertIn('--key-flow-ratio "${key_flow_ratio}"', self.text)
        self.assertIn('--max-payload-bytes "${max_payload_bytes}"', self.text)
        self.assertIn('--tolerance-s "${alignment_tolerance_s}"', self.text)

    def test_runner_code_manifest_is_exact_contract_allow_set(self):
        self.assertIn("bound_repository_artifacts", self.text)
        self.assertNotIn("find . -type f", self.text)
        self.assertIn("code manifest path set is not exact", self.text)

    def test_runner_rejects_preexisting_symlinked_result_tree(self):
        self.assertIn("ensure_real_directory", self.text)
        for name in ("campaign_root", "runs", "results", "receipts"):
            self.assertIn(name, self.text)

    def test_runner_formal_receipt_uses_fixed_safe_subpath(self):
        self.assertIn(
            '--output "${campaign_root}/receipts/campaign_receipt.json"',
            self.text,
        )

    def test_runner_rejects_unsafe_local_lock_root_and_file(self):
        self.assertIn('[[ ! -d "/" || -L "/" || ! -d "/tmp" || -L "/tmp" ]]', self.text)
        self.assertIn('[[ ! -d "${lock_root}" || -L "${lock_root}" ]]', self.text)
        self.assertIn('stat -f -c %T -- "${lock_root}"', self.text)
        self.assertIn('lock_root_uid="$(stat -c %u -- "${lock_root}")"', self.text)
        self.assertIn('lock_root_mode="$(stat -c %a -- "${lock_root}")"', self.text)
        self.assertIn('"${lock_root_uid}" != "${effective_uid}"', self.text)
        self.assertIn('"${lock_root_mode}" != "700"', self.text)
        self.assertIn('[[ -L "${lock_path}" || ! -f "${lock_path}" ]]', self.text)
        self.assertIn('lock_file_uid="$(stat -c %u -- "${lock_path}")"', self.text)
        self.assertIn('lock_file_mode="$(stat -c %a -- "${lock_path}")"', self.text)
        self.assertIn('lock_file_links="$(stat -c %h -- "${lock_path}")"', self.text)
        self.assertIn('"${lock_file_uid}" != "${effective_uid}"', self.text)
        self.assertIn('"${lock_file_mode}" != "600"', self.text)
        self.assertIn('"${lock_file_links}" != "1"', self.text)
        self.assertIn('lock_fd_identity="$(stat -L -c %d:%i -- "/proc/self/fd/9")"', self.text)
        self.assertIn('lock_fd_links="$(stat -L -c %h -- "/proc/self/fd/9")"', self.text)
        self.assertIn('lock_path_identity="$(stat -c %d:%i -- "${lock_path}")"', self.text)

    def test_runner_locks_before_truncating_owner_metadata(self):
        non_truncating_open = 'exec 9<> "${lock_path}"'
        acquire = "flock -n 9"
        truncate = 'truncate -s 0 -- "/proc/self/fd/9"'
        self.assertIn(non_truncating_open, self.text)
        self.assertNotIn('exec 9> "${lock_path}"', self.text)
        self.assertIn(truncate, self.text)
        self.assertLess(self.text.index(non_truncating_open), self.text.index(acquire))
        self.assertLess(self.text.index(acquire), self.text.index(truncate))

    def test_runner_stays_foreground(self):
        self.assertNotIn("nohup", self.text)
        self.assertNotIn("systemd-run", self.text)
        self.assertNotIn("disown", self.text)

    def test_runner_never_writes_source_search(self):
        self.assertNotIn("algorithm_search_rc1.json.tmp", self.text)
        self.assertIn("suggested_algorithm_search_projection.json", self.text)


if __name__ == "__main__":
    unittest.main()
