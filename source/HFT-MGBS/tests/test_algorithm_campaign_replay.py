import copy
import csv
import json
import os
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "algorithm_qualification_campaign_v1.json"
SEARCH = ROOT / "configs" / "algorithm_search_rc1.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import hft_mgbs.algorithm_campaign as campaign  # noqa: E402
import test_algorithm_campaign as _campaign_tests  # noqa: E402
from hft_mgbs.algorithm_campaign_replay import (  # noqa: E402
    verify_algorithm_campaign_raw_replay,
)


def write_json(path, value):
    path.write_bytes(campaign.canonical_json_bytes(value))


class ReplayFixture:
    def __init__(self, root):
        self.root = Path(root)
        self.campaign_root = self.root / "campaign"
        self.campaign_root.mkdir()
        self.campaign_root = self.campaign_root.resolve()
        for name in ("runs", "results", "receipts"):
            (self.campaign_root / name).mkdir()
        (
            source_contract,
            self.search,
            self.artifacts,
            candidate_protocols,
        ) = campaign.validate_contract(ROOT, CONTRACT)
        with patch.object(
            campaign,
            "validate_contract",
            return_value=(
                source_contract,
                self.search,
                self.artifacts,
                candidate_protocols,
            ),
        ):
            self.plan = campaign.compile_campaign_plan(
                ROOT,
                CONTRACT,
                campaign_run_id="algorithm_replay_fixture",
                created_at_utc="2026-08-13T00:00:00Z",
            )
        self.contract = copy.deepcopy(source_contract)
        self.contract["execution"].update(
            {
                "gpu_code_root": str(ROOT),
                "gpu_campaign_result_root": str(self.root),
            }
        )
        self._build_inputs()
        self._build_environment_identity()
        write_json(self.campaign_root / "plan.json", self.plan)
        self.raw_paths = {}
        for job in self.plan["jobs"]:
            self._build_candidate(job)
        self.receipt_path = self.campaign_root / "receipts" / "campaign_receipt.json"
        self.projection_path = (
            self.campaign_root / "suggested_algorithm_search_projection.json"
        )
        with self.patches():
            result = campaign.finalize_campaign(
                ROOT,
                CONTRACT,
                self.campaign_root,
                self.receipt_path,
                self.projection_path,
                trusted_contract_sha256=campaign.sha256_file(CONTRACT),
            )
        if result.get("accepted") is not True:
            raise AssertionError(
                "fixture did not produce an accepted formal receipt: {}".format(result)
            )

    def patches(self):
        stack = ExitStack()
        stack.enter_context(
            patch.object(
                campaign,
                "validate_contract",
                return_value=(self.contract, self.search, self.artifacts, []),
            )
        )
        stack.enter_context(
            patch.object(campaign, "compile_campaign_plan", return_value=self.plan)
        )
        stack.enter_context(
            patch.object(
                campaign,
                "_existing_campaign_root",
                return_value=self.campaign_root.resolve(),
            )
        )
        stack.enter_context(
            patch.object(
                campaign,
                "_clean_absolute_path",
                side_effect=lambda value, _name: value,
            )
        )
        stack.enter_context(
            patch(
                "hft_mgbs.algorithm_optimality._path_is_clean", return_value=True
            )
        )
        return stack

    def replay(self):
        with self.patches():
            return verify_algorithm_campaign_raw_replay(
                ROOT,
                CONTRACT,
                self.campaign_root,
                self.receipt_path,
            )

    def _build_inputs(self):
        inputs = self.root / "inputs"
        inputs.mkdir()
        samples = []
        for index in range(24):
            path = inputs / "sample_{:02d}.pcap".format(index)
            path.write_bytes("pcap-{}".format(index).encode("ascii"))
            samples.append(path)
        truth = inputs / "ground_truth.csv"
        with truth.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "Protocol",
                    "Source IP",
                    "Destination IP",
                    "Source Port",
                    "Destination Port",
                    "Start time",
                    "Last time",
                    "Attack category",
                ],
            )
            writer.writeheader()
            for event_id in range(1, 11):
                writer.writerow(
                    {
                        "Protocol": "tcp",
                        "Source IP": "10.0.0.{}".format(event_id),
                        "Destination IP": "10.0.1.{}".format(event_id),
                        "Source Port": event_id,
                        "Destination Port": 1000 + event_id,
                        "Start time": 1.0,
                        "Last time": 2.0,
                        "Attack category": "test",
                    }
                )
        training = inputs / "training.json"
        holdout = inputs / "holdout.json"
        self.isolated_holdout_manifest_path = holdout
        write_json(
            training,
            {"samples": [{"path": str(path.resolve())} for path in samples[:12]]},
        )
        write_json(
            holdout,
            {
                "ground_truth_csv": str(truth.resolve()),
                "samples": [
                    {"path": str(path.resolve())} for path in samples[12:]
                ],
            },
        )
        self.plan["gpu_execution"].update(
            {
                "code_root": str(ROOT),
                "campaign_result_root": str(self.root),
                "training_manifest": str(training.resolve()),
                "holdout_manifest": str(holdout.resolve()),
            }
        )
        for job in self.plan["jobs"]:
            job["expected_ground_truth_csv"] = str(truth.resolve())
        frozen_paths = [training, holdout, truth] + samples
        entries = []
        for path in frozen_paths:
            entries.append(
                {
                    "path": str(path.resolve()),
                    "size_bytes": path.stat().st_size,
                    "sha256": campaign.sha256_file(path),
                }
            )
        self.input_manifest_path = self.campaign_root / "input_sha256.json"
        write_json(
            self.input_manifest_path,
            {
                "schema_version": 1,
                "algorithm": "sha256",
                "entry_count": 27,
                "entries": entries,
            },
        )
        self.input_manifest_sha = campaign.sha256_file(self.input_manifest_path)
        stat_entries = []
        for path in frozen_paths:
            status = os.lstat(str(path.resolve()))
            stat_entries.append(
                {
                    "path": str(path.resolve()),
                    "device": status.st_dev,
                    "inode": status.st_ino,
                    "mode": status.st_mode,
                    "link_count": status.st_nlink,
                    "size_bytes": status.st_size,
                    "mtime_ns": status.st_mtime_ns,
                    "ctime_ns": status.st_ctime_ns,
                }
            )
        self.input_stat_identity_path = (
            self.campaign_root / "input_stat_identity.json"
        )
        write_json(
            self.input_stat_identity_path,
            {
                "schema_version": 1,
                "scope": "hft_mgbs_campaign_input_stat_identity_v1",
                "input_manifest_sha256": self.input_manifest_sha,
                "entry_count": len(stat_entries),
                "entries": stat_entries,
            },
        )
        self.input_stat_identity_sha = campaign.sha256_file(
            self.input_stat_identity_path
        )

    def _build_environment_identity(self):
        prefix = self.root / "env"
        metadata_dir = prefix / "conda-meta"
        metadata_dir.mkdir(parents=True)
        site_packages = prefix / "lib" / "python3.9" / "site-packages"
        site_packages.mkdir(parents=True)
        self.site_packages_path = site_packages
        module_file = site_packages / "module.py"
        module_file.write_bytes(b"__version__ = '1'\n")
        python_executable = prefix / "python"
        python_executable.write_bytes(b"frozen-python")
        self.python_executable_path = python_executable
        self.python_executable_sha = campaign.sha256_file(python_executable)
        self.contract["execution"]["environment_prefix"] = str(prefix.resolve())
        self.contract["execution"]["python_executable"] = str(
            python_executable.resolve()
        )
        self.plan["gpu_execution"]["environment_prefix"] = str(prefix.resolve())
        self.plan["gpu_execution"]["python_executable"] = str(
            python_executable.resolve()
        )
        metadata_path = metadata_dir / "test-1.json"
        write_json(metadata_path, {"files": ["python"]})
        environment_entries = []
        for target in sorted(
            prefix.rglob("*"),
            key=lambda item: item.relative_to(prefix).as_posix(),
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
                entry.update(
                    {"type": "regular", "sha256": campaign.sha256_file(target)}
                )
            environment_entries.append(entry)
        prefix_status = prefix.lstat()
        root_identity = {
            "device": prefix_status.st_dev,
            "inode": prefix_status.st_ino,
            "mode": prefix_status.st_mode,
            "link_count": prefix_status.st_nlink,
            "size_bytes": prefix_status.st_size,
            "mtime_ns": prefix_status.st_mtime_ns,
            "ctime_ns": prefix_status.st_ctime_ns,
        }
        environment_files_path = (
            self.campaign_root / "environment_files_sha256.json"
        )
        self.environment_files_path = environment_files_path
        write_json(
            environment_files_path,
            {
                "schema_version": 4,
                "scope": "hft_mgbs_python_environment_tree_sha256_v4",
                "environment_prefix": str(prefix.resolve()),
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
                    item["size_bytes"]
                    for item in environment_entries
                    if item["type"] == "regular"
                ),
                "entries": environment_entries,
            },
        )
        self.environment_files_sha = campaign.sha256_file(environment_files_path)
        runtime_path = self.campaign_root / "runtime_bootstrap_identity.json"
        self.runtime_bootstrap_identity_path = runtime_path
        write_json(
            runtime_path,
            {
                "schema_version": 1,
                "scope": "hft_mgbs_stdlib_bound_python_runtime_v1",
                "prefix": str(prefix.resolve()),
                "executable": str(python_executable.resolve()),
                "executable_sha256": campaign.sha256_file(python_executable),
                "site_packages": [str(site_packages.resolve())],
            },
        )
        self.runtime_bootstrap_identity_sha = campaign.sha256_file(runtime_path)
        tool_file = self.root / "tool"
        tool_file.write_bytes(b"frozen-tool")
        tool_names = sorted(
            {
                "bash",
                "cmp",
                "date",
                "dirname",
                "find",
                "flock",
                "id",
                "mkdir",
                "python3",
                "rm",
                "seq",
                "sha256sum",
                "stat",
                "truncate",
                "wc",
            }
        )
        external_tools_path = self.campaign_root / "external_tools_sha256.json"
        self.external_tools_path = external_tools_path
        write_json(
            external_tools_path,
            {
                "schema_version": 1,
                "scope": "hft_mgbs_algorithm_campaign_external_tools_v1",
                "entry_count": len(tool_names),
                "entries": [
                    {
                        "name": name,
                        "invoked_path": str(tool_file.resolve()),
                        "resolved_path": os.path.realpath(str(tool_file.resolve())),
                        "sha256": campaign.sha256_file(tool_file),
                    }
                    for name in tool_names
                ],
            },
        )
        self.external_tools_sha = campaign.sha256_file(external_tools_path)
        packages = {
            name: {
                "version": "1",
                "module_file": str(module_file.resolve()),
                "module_file_sha256": campaign.sha256_file(module_file),
            }
            for name in ("numpy", "scipy", "sklearn", "joblib")
        }
        payload = {
            "schema_version": 2,
            "scope": "hft_mgbs_algorithm_campaign_environment_identity_v2",
            "environment_prefix": str(prefix.resolve()),
            "environment_files_manifest_path": str(
                environment_files_path.resolve()
            ),
            "environment_files_manifest_sha256": self.environment_files_sha,
            "environment_files_manifest_entry_count": len(environment_entries),
            "external_tools_manifest_path": str(external_tools_path.resolve()),
            "external_tools_manifest_sha256": self.external_tools_sha,
            "external_tools_manifest_entry_count": len(tool_names),
            "runtime_bootstrap_identity_path": str(runtime_path.resolve()),
            "runtime_bootstrap_identity_sha256": (
                self.runtime_bootstrap_identity_sha
            ),
            "python": {
                "version": "3.9.0",
                "implementation": "CPython",
                "executable": str(python_executable.resolve()),
                "executable_sha256": campaign.sha256_file(python_executable),
                "site_packages": [str(site_packages.resolve())],
            },
            "packages": packages,
            "thread_environment": {
                name: None
                for name in (
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
            },
        }
        self.environment_identity_path = (
            self.campaign_root / "environment_identity.json"
        )
        write_json(self.environment_identity_path, payload)
        self.environment_identity_sha = campaign.sha256_file(
            self.environment_identity_path
        )

    def _authoritative_raw_payload(self, job, mode, seed):
        fixture_job = copy.deepcopy(job)
        fixture_job["_test_holdout_manifest"] = str(
            self.isolated_holdout_manifest_path.resolve()
        )
        payload = _campaign_tests.AlgorithmCampaignContractTest._raw_payload(
            fixture_job,
            mode,
            seed,
            self.input_manifest_sha,
        )
        payload["input_hash_evidence"].update(
            {
                "path": str(self.input_manifest_path.resolve()),
                "sha256": self.input_manifest_sha,
                "entry_count": 27,
                "required_path_count": 27,
                "all_required_paths_frozen": True,
            }
        )
        env = job["runner_environment"]
        original_seed = payload["quality"]["seeds"][0]
        if job["candidate_id"] == "A09":
            labels = [1] * 20 + [0] * 60
            probabilities = [0.99] * 20 + [0.01] * 60
            calibration_labels = list(labels)
            calibration_probabilities = list(probabilities)
        else:
            labels = list(original_seed["evaluation_labels"])
            probabilities = list(original_seed["evaluation_probabilities"])
            calibration_labels = list(original_seed["calibration_labels"])
            calibration_probabilities = list(
                original_seed["calibration_probabilities"]
            )
        if env["THRESHOLD_POLICY"] == "calibration_macro_f1":
            floor = float(env["CALIBRATION_ATTACK_RECALL_FLOOR"])
            selected = campaign._select_macro_f1_threshold_replay(
                calibration_labels, calibration_probabilities, floor
            )
            threshold = float(selected["threshold"])
        else:
            floor = None
            selected = None
            threshold = 0.5
        metrics = campaign._binary_prediction_metrics(
            labels, probabilities, threshold
        )
        seed_row = {
            "seed": seed,
            "decision_threshold": threshold,
            "TP": metrics["TP"],
            "TN": metrics["TN"],
            "FP": metrics["FP"],
            "FN": metrics["FN"],
            "evaluation_labels": labels,
            "evaluation_probabilities": probabilities,
            "calibration_labels": (
                calibration_labels if selected is not None else []
            ),
            "calibration_probabilities": (
                calibration_probabilities if selected is not None else []
            ),
            "macro_f1": metrics["macro_f1"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "auroc": metrics["auroc"],
            "auprc": metrics["auprc"],
            "benign_recall": metrics["benign_recall"],
            "attack_recall": metrics["attack_recall"],
            "ece": metrics["ece"],
            "predicted_attack_ratio": metrics["predicted_attack_ratio"],
        }
        if selected is not None:
            seed_row["calibration_selection"] = {
                "threshold": selected["threshold"],
                "macro_f1": selected["macro_f1"],
                "balanced_accuracy": selected["balanced_accuracy"],
                "attack_recall": selected["attack_recall"],
                "benign_recall": selected["benign_recall"],
                "predicted_attack_ratio": selected["predicted_attack_ratio"],
                "minimum_attack_recall_constraint": floor,
            }
        quality = payload["quality"]
        quality["seeds"] = [seed_row]
        quality["aggregate_confusion_matrix"] = {
            name: metrics[name] for name in ("TP", "TN", "FP", "FN")
        }
        quality["conservative"] = {
            "macro_f1_min": metrics["macro_f1"],
            "balanced_accuracy_min": metrics["balanced_accuracy"],
            "auroc_min": metrics["auroc"],
            "auprc_min": metrics["auprc"],
            "benign_recall_min": metrics["benign_recall"],
            "attack_recall_min": metrics["attack_recall"],
            "ece_max": metrics["ece"],
        }
        return payload

    def _build_candidate(self, job):
        run_id = "{}_{}".format(job["result_prefix"], job["run_tag"])
        result_dir = self.campaign_root / "results" / run_id
        run_dir = self.campaign_root / "runs" / run_id
        result_dir.mkdir()
        run_dir.mkdir()
        payloads_by_mode = {"normal": [], "fallback": []}
        for mode in ("normal", "fallback"):
            for repeat, seed in enumerate(job["expected_repeat_seeds"], start=1):
                payload = self._authoritative_raw_payload(job, mode, seed)
                path = result_dir / "{}_repeat{}.json".format(mode, repeat)
                write_json(path, payload)
                self.raw_paths[(job["candidate_id"], mode, repeat)] = path
                payloads_by_mode[mode].append(payload)
        metrics = {
            mode: campaign._candidate_raw_metrics(
                payloads_by_mode[mode], int(job["runner_environment"]["BUDGET_US"])
            )
            for mode in ("normal", "fallback")
        }
        env = job["runner_environment"]
        decision_policy = {
            "feature_profile": env["FEATURE_PROFILE"],
            "classifier": env["CLASSIFIER"],
            "threshold_policy": env["THRESHOLD_POLICY"],
            "calibration_attack_recall_floor": float(
                env["CALIBRATION_ATTACK_RECALL_FLOOR"]
            ),
            "calibration_groups": sorted(
                filter(None, env["CALIBRATION_GROUPS"].split(","))
            ),
            "evaluation_groups": list(job["expected_fresh_evaluation_groups"]),
            "adaptation_policy": env["ADAPTATION_POLICY"],
            "adaptation_groups": sorted(
                filter(None, env["ADAPTATION_GROUPS"].split(","))
            ),
            "adaptation_weight_multiplier": float(
                env["ADAPTATION_WEIGHT_MULTIPLIER"]
            ),
        }
        summary_rows = []
        feasible_count = 0
        for mode in ("normal", "fallback"):
            row = dict(metrics[mode])
            row.pop("budget_us_max")
            violations = campaign._hard_constraint_violations(
                metrics[mode], self.plan["hard_constraints"]
            )
            feasible_count += int(not violations)
            row.update(
                {
                    "mode": mode,
                    "repeat_ids": [1, 2, 3],
                    "repeat_count": 3,
                    "repeat_gate_passed": True,
                    "batch_size": int(env["BATCH_SIZE"]),
                    "budget_us": int(env["BUDGET_US"]),
                    "execution_budget_safety_ratio": float(env["SAFETY_RATIO"]),
                    "input_hash_manifest_sha256": self.input_manifest_sha,
                    "decision_policy": decision_policy,
                    "hard_constraint_violations": violations,
                    "hard_constraints_passed": not violations,
                    "train_flow_count_min": min(
                        payload["quality"]["train_flow_count"]
                        for payload in payloads_by_mode[mode]
                    ),
                    "test_flow_count_min": min(
                        payload["quality"]["test_flow_count"]
                        for payload in payloads_by_mode[mode]
                    ),
                    "final_quality_eligible": False,
                    "missing_final_evidence": ["frozen_min_primary_metric"],
                }
            )
            summary_rows.append(row)
        write_json(
            result_dir / "summary.json",
            {
                "schema_version": 2,
                "scope": "independent_cross_dataset_holdout_summary",
                "aggregation_policy": "worst_case_across_full_extraction_repeats",
                "minimum_repeats": 3,
                "candidate_count": 2,
                "feasible_candidate_count": feasible_count,
                "rejected_files": [],
                "candidates": summary_rows,
                "final_quality_eligible": False,
            },
        )
        code_lines = [
            "{}  {}\n".format(artifact["sha256"], artifact["path"])
            for artifact in self.artifacts.values()
        ]
        (run_dir / "code_sha256.txt").write_text(
            "".join(code_lines), encoding="utf-8"
        )
        code_manifest_sha = campaign.sha256_file(run_dir / "code_sha256.txt")
        self._reseal_result_manifest(result_dir, run_dir)
        fields = {
            "run_id": run_id,
            "training_manifest": self.plan["gpu_execution"]["training_manifest"],
            "holdout_manifest": self.plan["gpu_execution"]["holdout_manifest"],
            "input_hash_manifest": str(self.input_manifest_path.resolve()),
            "input_hash_manifest_sha256": self.input_manifest_sha,
            "contract_sha256": campaign.sha256_file(CONTRACT),
            "repeats": env["REPEATS"],
            "batch_size": env["BATCH_SIZE"],
            "budget_us": env["BUDGET_US"],
            "execution_budget_safety_ratio": env["SAFETY_RATIO"],
            "max_train_packets_per_capture": env["MAX_TRAIN_PACKETS_PER_CAPTURE"],
            "max_train_flows_per_capture": env["MAX_TRAIN_FLOWS_PER_CAPTURE"],
            "max_test_packets_per_capture": env["MAX_TEST_PACKETS_PER_CAPTURE"],
            "max_test_flows_per_capture": env["MAX_TEST_FLOWS_PER_CAPTURE"],
            "estimators": env["ESTIMATORS"],
            "n_jobs": env["N_JOBS"],
            "key_flow_ratio": env["KEY_FLOW_RATIO"],
            "max_payload_bytes": env["MAX_PAYLOAD_BYTES"],
            "alignment_tolerance_s": env["ALIGNMENT_TOLERANCE_S"],
            "threshold_policy": env["THRESHOLD_POLICY"],
            "calibration_groups": env["CALIBRATION_GROUPS"],
            "calibration_attack_recall_floor": env[
                "CALIBRATION_ATTACK_RECALL_FLOOR"
            ],
            "feature_profile": env["FEATURE_PROFILE"],
            "classifier": env["CLASSIFIER"],
            "adaptation_policy": env["ADAPTATION_POLICY"],
            "adaptation_groups": env["ADAPTATION_GROUPS"],
            "adaptation_weight_multiplier": env["ADAPTATION_WEIGHT_MULTIPLIER"],
            "started_at": "2026-08-13T00:01:00Z",
            "status": "complete",
            "ended_at": "2026-08-13T00:02:00Z",
            "result_dir": str(result_dir.resolve()),
            "result_count": "6",
            "code_manifest_sha256": code_manifest_sha,
            "environment_identity_sha256": self.environment_identity_sha,
            "environment_files_manifest_sha256": self.environment_files_sha,
            "external_tools_manifest_sha256": self.external_tools_sha,
            "runtime_bootstrap_identity_sha256": (
                self.runtime_bootstrap_identity_sha
            ),
            "input_stat_manifest_sha256": self.input_stat_identity_sha,
        }
        manifest = "".join("{}={}\n".format(key, value) for key, value in fields.items())
        (run_dir / "manifest.txt").write_text(manifest, encoding="utf-8")

    @staticmethod
    def _reseal_result_manifest(result_dir, run_dir):
        lines = []
        for path in sorted(result_dir.iterdir(), key=lambda item: item.name):
            lines.append("{}  {}\n".format(campaign.sha256_file(path), path.resolve()))
        (run_dir / "result_sha256.txt").write_text("".join(lines), encoding="utf-8")

    def mutate_raw(self, candidate_id, mode, repeat, mutate):
        path = self.raw_paths[(candidate_id, mode, repeat)]
        payload = json.loads(path.read_text("utf-8"))
        mutate(payload)
        write_json(path, payload)
        run_id = next(
            "{}_{}".format(job["result_prefix"], job["run_tag"])
            for job in self.plan["jobs"]
            if job["candidate_id"] == candidate_id
        )
        self._reseal_result_manifest(
            self.campaign_root / "results" / run_id,
            self.campaign_root / "runs" / run_id,
        )


class AlgorithmCampaignRawReplayTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.fixture = ReplayFixture(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_replays_27_inputs_and_10_by_2_by_3_raw_without_writes(self):
        before = {
            str(path.relative_to(self.fixture.campaign_root)): (
                path.stat().st_size,
                path.stat().st_mtime_ns,
                campaign.sha256_file(path),
            )
            for path in self.fixture.campaign_root.rglob("*")
            if path.is_file()
        }
        result = self.fixture.replay()
        after = {
            str(path.relative_to(self.fixture.campaign_root)): (
                path.stat().st_size,
                path.stat().st_mtime_ns,
                campaign.sha256_file(path),
            )
            for path in self.fixture.campaign_root.rglob("*")
            if path.is_file()
        }
        self.assertTrue(result["accepted"], result["errors"])
        self.assertTrue(result["authoritative_raw_replay_complete"])
        self.assertTrue(result["campaign_tree_unchanged"])
        self.assertEqual(result["input_manifest_entry_count"], 27)
        self.assertEqual(result["candidate_count"], 10)
        self.assertEqual(result["evaluated_candidate_count"], 10)
        self.assertEqual(result["feasible_candidate_count"], 8)
        self.assertEqual(result["qualified_candidate_count"], 8)
        self.assertEqual(result["raw_repeat_count"], 60)
        self.assertEqual(result["regenerated_artifact_count"], 12)
        self.assertTrue(result["formal_algorithm_only_accepted"])
        self.assertEqual(result["selected_candidate"], "A09")
        self.assertEqual(
            result["environment_identity_sha256"],
            self.fixture.environment_identity_sha,
        )
        self.assertEqual(
            result["environment_prefix"],
            self.fixture.contract["execution"]["environment_prefix"],
        )
        self.assertEqual(
            result["python_executable"],
            str(self.fixture.python_executable_path.resolve()),
        )
        self.assertEqual(
            result["python_executable_sha256"],
            self.fixture.python_executable_sha,
        )
        self.assertEqual(
            result["python_site_packages"],
            [str(self.fixture.site_packages_path.resolve())],
        )
        self.assertEqual(
            result["environment_files_manifest_sha256"],
            self.fixture.environment_files_sha,
        )
        self.assertEqual(
            result["external_tools_manifest_sha256"],
            self.fixture.external_tools_sha,
        )
        self.assertEqual(
            result["runtime_bootstrap_identity_sha256"],
            self.fixture.runtime_bootstrap_identity_sha,
        )
        self.assertEqual(
            result["input_stat_identity_sha256"],
            self.fixture.input_stat_identity_sha,
        )
        self.assertEqual(before, after)

    def test_rejects_raw_seed_drift_even_when_result_manifest_is_resealed(self):
        self.fixture.mutate_raw(
            "A01",
            "normal",
            1,
            lambda value: value["protocol"].update({"seeds": [11]}),
        )
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("seed", " ".join(result["errors"]))
        self.assertTrue(result["campaign_tree_unchanged"])

    def test_rejects_group_label_fingerprint_and_event_witness_drift(self):
        key = ("A02", "fallback", 2)
        raw_path = self.fixture.raw_paths[key]
        run_id = next(
            "{}_{}".format(job["result_prefix"], job["run_tag"])
            for job in self.fixture.plan["jobs"]
            if job["candidate_id"] == key[0]
        )
        run_dir = self.fixture.campaign_root / "runs" / run_id
        result_dir = self.fixture.campaign_root / "results" / run_id
        cases = (
            (
                "fresh_group",
                lambda value: value["protocol"].update(
                    {"evaluation_groups": ["forged_holdout"]}
                ),
            ),
            (
                "selected_flow_label_sha256",
                lambda value: value["holdout_captures"][0].update(
                    {"selected_flow_label_sha256": "0" * 64}
                ),
            ),
            (
                "matched_event_witnesses",
                lambda value: value["ground_truth_event_recall_audit"][
                    "matched_event_witnesses"
                ].pop(),
            ),
        )
        original = raw_path.read_bytes()
        for name, mutation in cases:
            with self.subTest(evidence=name):
                try:
                    self.fixture.mutate_raw(*key, mutate=mutation)
                    result = self.fixture.replay()
                finally:
                    raw_path.write_bytes(original)
                    ReplayFixture._reseal_result_manifest(result_dir, run_dir)
                self.assertFalse(result["accepted"], result)
                self.assertTrue(result["campaign_tree_unchanged"], result)

    def test_rejects_summary_substitution(self):
        job = self.fixture.plan["jobs"][2]
        run_id = "{}_{}".format(job["result_prefix"], job["run_tag"])
        result_dir = self.fixture.campaign_root / "results" / run_id
        summary_path = result_dir / "summary.json"
        summary = json.loads(summary_path.read_text("utf-8"))
        summary["candidates"][0]["macro_f1_min"] = 0.999
        write_json(summary_path, summary)
        ReplayFixture._reseal_result_manifest(
            result_dir, self.fixture.campaign_root / "runs" / run_id
        )
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("summary metric", " ".join(result["errors"]))

    def test_rejects_direct_python_executable_drift(self):
        self.fixture.python_executable_path.write_bytes(b"forged-python")
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("environment tree", " ".join(result["errors"]).lower())
        self.assertTrue(result["campaign_tree_unchanged"])

    def test_rejects_missing_raw_repeat(self):
        os.remove(str(self.fixture.raw_paths[("A04", "normal", 3)]))
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("result file set is not exact", " ".join(result["errors"]))

    def test_rejects_forged_candidate_campaign_identity(self):
        formal = json.loads(self.fixture.receipt_path.read_text("utf-8"))
        reference = next(
            item for item in formal["candidate_receipts"] if item["candidate_id"] == "A05"
        )
        candidate_path = Path(reference["path"])
        candidate = json.loads(candidate_path.read_text("utf-8"))
        candidate["campaign_id"] = "forged_campaign"
        write_json(candidate_path, candidate)
        forged_hash = campaign.sha256_file(candidate_path)
        reference["sha256"] = forged_hash
        projection = json.loads(self.fixture.projection_path.read_text("utf-8"))
        next(item for item in projection["candidates"] if item["id"] == "A05")[
            "evidence_sha256"
        ] = forged_hash
        write_json(self.fixture.projection_path, projection)
        formal["suggested_algorithm_search_projection"]["sha256"] = campaign.sha256_file(
            self.fixture.projection_path
        )
        write_json(self.fixture.receipt_path, formal)
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("field drift", " ".join(result["errors"]))

    def test_rejects_receipt_path_escape(self):
        outside = self.fixture.root / "outside.json"
        write_json(outside, {"forged": True})
        formal = json.loads(self.fixture.receipt_path.read_text("utf-8"))
        formal["candidate_receipts"][0].update(
            {"path": str(outside.resolve()), "sha256": campaign.sha256_file(outside)}
        )
        write_json(self.fixture.receipt_path, formal)
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("escapes campaign root", " ".join(result["errors"]))

    def test_rejects_plan_input_run_code_result_projection_and_audit_drift(self):
        first_job = self.fixture.plan["jobs"][0]
        run_id = "{}_{}".format(
            first_job["result_prefix"], first_job["run_tag"]
        )
        run_dir = self.fixture.campaign_root / "runs" / run_id

        def mutate_json(path, mutation):
            value = json.loads(path.read_text("utf-8"))
            mutation(value)
            return campaign.canonical_json_bytes(value)

        cases = (
            (
                "plan_campaign_identity",
                self.fixture.campaign_root / "plan.json",
                lambda path: mutate_json(
                    path, lambda value: value.update({"campaign_id": "forged"})
                ),
            ),
            (
                "input_entry_count",
                self.fixture.input_manifest_path,
                lambda path: mutate_json(
                    path, lambda value: value.update({"entry_count": 26})
                ),
            ),
            (
                "input_stat_identity",
                self.fixture.input_stat_identity_path,
                lambda path: mutate_json(
                    path, lambda value: value.update({"entry_count": 26})
                ),
            ),
            (
                "environment_files_manifest",
                self.fixture.environment_files_path,
                lambda path: mutate_json(
                    path, lambda value: value.update({"entry_count": 2})
                ),
            ),
            (
                "external_tools_manifest",
                self.fixture.external_tools_path,
                lambda path: mutate_json(
                    path, lambda value: value.update({"entry_count": 14})
                ),
            ),
            (
                "runtime_bootstrap_identity",
                self.fixture.runtime_bootstrap_identity_path,
                lambda path: mutate_json(
                    path, lambda value: value.update({"scope": "forged"})
                ),
            ),
            (
                "run_manifest",
                run_dir / "manifest.txt",
                lambda path: path.read_bytes().replace(
                    b"status=complete", b"status=forged"
                ),
            ),
            (
                "code_manifest",
                run_dir / "code_sha256.txt",
                lambda path: (
                    (b"0" if path.read_bytes()[:1] != b"0" else b"1")
                    + path.read_bytes()[1:]
                ),
            ),
            (
                "result_manifest",
                run_dir / "result_sha256.txt",
                lambda path: (
                    (b"0" if path.read_bytes()[:1] != b"0" else b"1")
                    + path.read_bytes()[1:]
                ),
            ),
            (
                "projection",
                self.fixture.projection_path,
                lambda path: mutate_json(
                    path,
                    lambda value: value.update({"selected_candidate": "A10"}),
                ),
            ),
            (
                "formal_projection_audit",
                self.fixture.receipt_path,
                lambda path: mutate_json(
                    path,
                    lambda value: value["projection_optimality_audit"].update(
                        {"accepted": False}
                    ),
                ),
            ),
            (
                "formal_external_trust_root",
                self.fixture.receipt_path,
                lambda path: mutate_json(
                    path,
                    lambda value: value.update(
                        {"external_trust_root_sha256": "0" * 64}
                    ),
                ),
            ),
        )
        for name, path, mutation in cases:
            with self.subTest(layer=name):
                original = path.read_bytes()
                try:
                    path.write_bytes(mutation(path))
                    result = self.fixture.replay()
                finally:
                    path.write_bytes(original)
                self.assertFalse(result["accepted"], result)
                self.assertTrue(result["campaign_tree_unchanged"], result)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_rejects_symlink_anywhere_in_campaign_tree(self):
        target = self.fixture.campaign_root / "plan.json"
        link = self.fixture.campaign_root / "forged-link.json"
        try:
            os.symlink(str(target), str(link))
        except OSError:
            self.skipTest("symlink creation is unavailable")
        result = self.fixture.replay()
        self.assertFalse(result["accepted"])
        self.assertIn("symlink", " ".join(result["errors"]))

    def test_detects_direct_tree_write_outside_intercepted_writer(self):
        original = campaign.finalize_campaign

        def malicious(*args, **kwargs):
            (self.fixture.campaign_root / "unexpected-write").write_bytes(b"x")
            return original(*args, **kwargs)

        with self.fixture.patches(), patch.object(
            campaign, "finalize_campaign", side_effect=malicious
        ):
            result = verify_algorithm_campaign_raw_replay(
                ROOT,
                CONTRACT,
                self.fixture.campaign_root,
                self.fixture.receipt_path,
            )
        self.assertFalse(result["accepted"])
        self.assertTrue(result["campaign_tree_unchanged"])
        self.assertIn("write attempted", " ".join(result["errors"]))
        self.assertFalse((self.fixture.campaign_root / "unexpected-write").exists())


if __name__ == "__main__":
    unittest.main()
