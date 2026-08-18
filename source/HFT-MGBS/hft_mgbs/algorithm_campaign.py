"""Compile and seal a uniform A01--A10 qualification campaign.

The campaign is deliberately separate from production selection.  It proves
only that every bounded-search candidate was evaluated with the same frozen
inputs, code, fresh evaluation groups, repeat seeds, and paired normal/
fallback protocol.  Raw results stay on the GPU host; only small hash-bound
receipts and a suggested search projection are produced.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import secrets
import stat
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set, Tuple

from hft_mgbs.algorithm_optimality import audit_algorithm_search
from hft_mgbs.features import MultiGranularityExtractor
from hft_mgbs.quality import (
    binary_prediction_metrics as shared_binary_prediction_metrics,
    select_macro_f1_threshold as shared_select_macro_f1_threshold,
)
from hft_mgbs.unsw import UnswGroundTruth


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CANDIDATE_ID_RE = re.compile(r"^A(?:0[1-9]|10)$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
MODES = ("normal", "fallback")
RESULT_RE = re.compile(r"^(normal|fallback)_repeat([1-9][0-9]*)\.json$")

METRIC_NAMES = (
    "macro_f1_min",
    "attack_recall_min",
    "benign_recall_min",
    "auprc_min",
    "ece_max",
    "ground_truth_event_recall_min",
    "key_flow_coverage_min",
    "budget_overrun_count_max",
    "budget_us_max",
)


class CampaignValidationError(ValueError):
    """Raised when campaign input cannot be trusted."""


def _reject_constant(value: str) -> None:
    raise CampaignValidationError("non-finite JSON number: {}".format(value))


def _reject_duplicates(pairs: Sequence[Tuple[str, object]]) -> Dict[str, object]:
    result: Dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CampaignValidationError("duplicate JSON key: {}".format(key))
        result[key] = value
    return result


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(str(path)))


def _assert_no_symlink_components(path: Path, name: str) -> Path:
    absolute = _absolute_lexical(path)
    chain = [absolute]
    chain.extend(parent for parent in absolute.parents if parent != absolute)
    for component in reversed(chain):
        try:
            status = os.lstat(str(component))
        except FileNotFoundError as error:
            raise CampaignValidationError("{} is missing: {}".format(name, component)) from error
        if stat.S_ISLNK(status.st_mode):
            raise CampaignValidationError("{} contains a symlink: {}".format(name, component))
    return absolute


def _stat_identity(value: os.stat_result) -> Tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _open_stable_regular(path: Path, name: str) -> Tuple[int, os.stat_result, Path]:
    absolute = _assert_no_symlink_components(path, name)
    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(str(absolute), flags)
    except OSError as error:
        raise CampaignValidationError("cannot open {} as a regular file".format(name)) from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise CampaignValidationError("{} is not a regular file".format(name))
        return descriptor, before, absolute
    except Exception:
        os.close(descriptor)
        raise


def _verify_stable_regular(
    descriptor: int, before: os.stat_result, absolute: Path, name: str
) -> Dict[str, object]:
    after = os.fstat(descriptor)
    current = os.lstat(str(_assert_no_symlink_components(absolute, name)))
    if (
        _stat_identity(before) != _stat_identity(after)
        or _stat_identity(before) != _stat_identity(current)
        or not stat.S_ISREG(current.st_mode)
    ):
        raise CampaignValidationError("{} changed while it was being read".format(name))


def _stable_file_bytes(path: Path, name: str) -> bytes:
    descriptor, before, absolute = _open_stable_regular(path, name)
    try:
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
        _verify_stable_regular(descriptor, before, absolute, name)
        if len(data) != before.st_size:
            raise CampaignValidationError("{} size changed while reading".format(name))
        return data
    finally:
        os.close(descriptor)


def _strict_json_from_bytes(raw: bytes, name: str) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CampaignValidationError("UTF-8 BOM is not allowed: {}".format(name))
    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CampaignValidationError("invalid JSON {}: {}".format(name, error)) from error


def load_strict_json(path: Path) -> object:
    return _strict_json_from_bytes(_stable_file_bytes(path, str(path)), str(path))


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _stable_file_hash_size(
    path: Path, name: str, chunk_size: int = 1024 * 1024
) -> Tuple[str, int]:
    descriptor, before, absolute = _open_stable_regular(path, name)
    digest = hashlib.sha256()
    try:
        while True:
            chunk = os.read(descriptor, chunk_size)
            if not chunk:
                break
            digest.update(chunk)
        _verify_stable_regular(descriptor, before, absolute, name)
        return digest.hexdigest(), before.st_size
    finally:
        os.close(descriptor)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    return _stable_file_hash_size(path, str(path), chunk_size)[0]


def write_json_atomic(path: Path, value: object) -> str:
    data = canonical_json_bytes(value)
    absolute = _absolute_lexical(path)
    parent = _assert_no_symlink_components(absolute.parent, "JSON output parent")
    if not parent.is_dir():
        raise CampaignValidationError("JSON output parent is not a directory")
    try:
        existing = os.lstat(str(absolute))
    except FileNotFoundError:
        existing = None
    if existing is not None:
        if (
            not stat.S_ISREG(existing.st_mode)
            or existing.st_nlink != 1
        ):
            raise CampaignValidationError(
                "JSON output target is not a single-link regular file"
            )
        if _stable_file_bytes(absolute, "existing JSON output") == data:
            return sha256_bytes(data)
        raise CampaignValidationError(
            "refusing to overwrite an existing non-identical JSON output"
        )

    temporary = parent / ".{}.tmp.{}.{}".format(
        absolute.name, os.getpid(), secrets.token_hex(8)
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(str(temporary), flags, 0o600)
        view = memoryview(data)
        written = 0
        while written < len(view):
            count = os.write(descriptor, view[written:])
            if count <= 0:
                raise OSError("short write while sealing JSON output")
            written += count
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        # A hard-link publication is an atomic create-if-absent operation on
        # the same filesystem.  Unlike os.replace(), it cannot overwrite a
        # target that appeared after the lstat above.
        os.link(str(temporary), str(absolute), follow_symlinks=False)
        os.unlink(str(temporary))
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(str(temporary))
        except FileNotFoundError:
            pass
        raise
    return sha256_bytes(data)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise CampaignValidationError("{} must be a mapping".format(name))
    return value


def _list(value: object, name: str) -> List[object]:
    if not isinstance(value, list):
        raise CampaignValidationError("{} must be a list".format(name))
    return value


def _finite(value: object, name: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise CampaignValidationError("{} must be a finite number".format(name))
    return float(value)


def _unit_interval(value: object, name: str) -> float:
    result = _finite(value, name)
    if result < 0.0 or result > 1.0:
        raise CampaignValidationError("{} must be in [0, 1]".format(name))
    return result


def _integer(value: object, name: str, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise CampaignValidationError(
            "{} must be an integer >= {}".format(name, minimum)
        )
    return value


def _clean_relative_path(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or any(c in value for c in "\r\n\x00"):
        raise CampaignValidationError("{} must be a clean relative path".format(name))
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != value.replace("\\", "/"):
        raise CampaignValidationError("{} escapes the repository".format(name))
    return value


def _clean_absolute_path(value: object, name: str) -> str:
    native_absolute = (
        isinstance(value, str)
        and Path(value).is_absolute()
        and str(Path(value)) == value
        and ".." not in Path(value).parts
    )
    if (
        not isinstance(value, str)
        or (not value.startswith("/") and not native_absolute)
        or any(c in value for c in "\r\n\x00")
        or ".." in PurePosixPath(value).parts
        or (value.startswith("/") and str(PurePosixPath(value)) != value)
    ):
        raise CampaignValidationError("{} must be a clean absolute path".format(name))
    return value


def _repo_file(repo_root: Path, relative: str) -> Path:
    root = _assert_no_symlink_components(repo_root, "repository root")
    resolved = _absolute_lexical(root / relative)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise CampaignValidationError("repository path escapes root: {}".format(relative)) from error
    _assert_no_symlink_components(resolved, "repository artifact")
    if not resolved.is_file():
        raise CampaignValidationError("repository artifact is missing: {}".format(relative))
    return resolved


def _directory_under(root: Path, candidate: Path, name: str) -> Path:
    absolute_root = _assert_no_symlink_components(root, "{} root".format(name))
    absolute = _assert_no_symlink_components(candidate, name)
    try:
        absolute.relative_to(absolute_root)
    except ValueError as error:
        raise CampaignValidationError("{} escapes its root".format(name)) from error
    if not absolute.is_dir():
        raise CampaignValidationError("{} is not a directory".format(name))
    return absolute


def _existing_campaign_root(path: Path, configured_root: Path) -> Path:
    configured = _assert_no_symlink_components(
        configured_root, "configured campaign result root"
    )
    root = _assert_no_symlink_components(path, "campaign root")
    try:
        root.relative_to(configured)
    except ValueError as error:
        raise CampaignValidationError(
            "campaign root is outside the GPU result root"
        ) from error
    if root == configured or not root.is_dir():
        raise CampaignValidationError("campaign root must be a child directory")
    return root


def _iso8601(value: object, name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise CampaignValidationError("{} must be an ISO-8601 timestamp".format(name))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise CampaignValidationError("{} is not ISO-8601".format(name)) from error
    if parsed.tzinfo is None:
        raise CampaignValidationError("{} must include a timezone".format(name))
    return parsed.astimezone(timezone.utc)


def _normalize_threshold(search_value: object) -> Tuple[str, float]:
    mapping = {
        "fixed_0.5": ("fixed", 0.0),
        "calibration_macro_f1_floor000": ("calibration_macro_f1", 0.0),
        "calibration_macro_f1_floor080": ("calibration_macro_f1", 0.8),
        "calibration_macro_f1_floor090": ("calibration_macro_f1", 0.9),
    }
    if search_value not in mapping:
        raise CampaignValidationError(
            "unsupported search threshold policy: {}".format(search_value)
        )
    return mapping[search_value]


def _normalize_adaptation(search_value: object) -> Tuple[str, float]:
    mapping = {
        "none": ("none", 1.0),
        "calibration_weighted_weight500": ("calibration_weighted", 5.0),
    }
    if search_value not in mapping:
        raise CampaignValidationError(
            "unsupported search adaptation policy: {}".format(search_value)
        )
    return mapping[search_value]


def _artifact_bindings(
    repo_root: Path, contract: Mapping[str, object]
) -> Dict[str, Dict[str, object]]:
    artifacts = _mapping(contract.get("bound_repository_artifacts"), "bound_repository_artifacts")
    required = set(_list(contract.get("required_bound_artifacts"), "required_bound_artifacts"))
    if not required or set(artifacts) != required:
        raise CampaignValidationError("bound artifact set does not match required_bound_artifacts")
    verified: Dict[str, Dict[str, object]] = {}
    for name in sorted(artifacts):
        reference = _mapping(artifacts[name], "artifact.{}".format(name))
        relative = _clean_relative_path(reference.get("path"), "artifact.{}.path".format(name))
        expected = reference.get("sha256")
        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            raise CampaignValidationError("artifact.{}.sha256 is invalid".format(name))
        path = _repo_file(repo_root, relative)
        actual = sha256_file(path)
        if actual != expected:
            raise CampaignValidationError(
                "artifact hash mismatch {}: expected {}, got {}".format(
                    relative, expected, actual
                )
            )
        verified[name] = {
            "path": relative,
            "sha256": actual,
            "size_bytes": path.stat().st_size,
        }
    return verified


def _candidate_specs(
    contract: Mapping[str, object], search: Mapping[str, object]
) -> List[Dict[str, object]]:
    raw_specs = _list(contract.get("candidate_protocols"), "candidate_protocols")
    search_candidates = _list(search.get("candidates"), "search.candidates")
    if len(raw_specs) != 10 or len(search_candidates) != 10:
        raise CampaignValidationError("campaign and search must contain exactly 10 candidates")
    by_id: Dict[str, Mapping[str, object]] = {}
    for raw in search_candidates:
        candidate = _mapping(raw, "search.candidate")
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or candidate_id in by_id:
            raise CampaignValidationError("search candidate IDs must be unique strings")
        by_id[candidate_id] = candidate
    specs: List[Dict[str, object]] = []
    seen = set()
    for raw in raw_specs:
        spec = dict(_mapping(raw, "candidate_protocol"))
        candidate_id = spec.get("id")
        if (
            not isinstance(candidate_id, str)
            or not CANDIDATE_ID_RE.fullmatch(candidate_id)
            or candidate_id in seen
        ):
            raise CampaignValidationError("invalid or duplicate campaign candidate ID")
        seen.add(candidate_id)
        if candidate_id not in by_id:
            raise CampaignValidationError("campaign candidate is absent from search: {}".format(candidate_id))
        search_candidate = by_id[candidate_id]
        for name in ("feature_profile", "classifier"):
            if spec.get(name) != search_candidate.get(name):
                raise CampaignValidationError("{}.{} does not match search".format(candidate_id, name))
        threshold, floor = _normalize_threshold(search_candidate.get("threshold_policy"))
        adaptation, multiplier = _normalize_adaptation(search_candidate.get("adaptation_policy"))
        expected = {
            "threshold_policy": threshold,
            "calibration_attack_recall_floor": floor,
            "adaptation_policy": adaptation,
            "adaptation_weight_multiplier": multiplier,
        }
        for name, value in expected.items():
            actual = spec.get(name)
            if isinstance(value, float):
                if _finite(actual, "{}.{}".format(candidate_id, name)) != value:
                    raise CampaignValidationError("{}.{} does not match search".format(candidate_id, name))
            elif actual != value:
                raise CampaignValidationError("{}.{} does not match search".format(candidate_id, name))
        specs.append(spec)
    expected_ids = ["A{:02d}".format(index) for index in range(1, 11)]
    if sorted(seen) != expected_ids or sorted(by_id) != expected_ids:
        raise CampaignValidationError("candidate IDs must be exactly A01--A10")
    return sorted(specs, key=lambda item: str(item["id"]))


def validate_contract(
    repo_root: Path,
    contract_path: Path,
    search_path: Optional[Path] = None,
) -> Tuple[Mapping[str, object], Mapping[str, object], Dict[str, Dict[str, object]], List[Dict[str, object]]]:
    contract = _mapping(load_strict_json(contract_path), "contract")
    if contract.get("schema_version") != 1:
        raise CampaignValidationError("contract.schema_version must be 1")
    if contract.get("scope") != "hft_mgbs_bounded_algorithm_qualification_campaign_v1":
        raise CampaignValidationError("contract.scope is invalid")
    campaign_id = contract.get("campaign_id")
    if not isinstance(campaign_id, str) or not RUN_ID_RE.fullmatch(campaign_id):
        raise CampaignValidationError("contract.campaign_id is invalid")

    search_ref = _mapping(contract.get("algorithm_search"), "algorithm_search")
    relative_search = _clean_relative_path(search_ref.get("path"), "algorithm_search.path")
    expected_search_hash = search_ref.get("sha256")
    if not isinstance(expected_search_hash, str) or not SHA256_RE.fullmatch(expected_search_hash):
        raise CampaignValidationError("algorithm_search.sha256 is invalid")
    expected_search_path = _repo_file(repo_root, relative_search)
    selected_search_path = expected_search_path if search_path is None else search_path.resolve()
    if selected_search_path != expected_search_path:
        raise CampaignValidationError("search path does not match the contract-bound repository file")
    if sha256_file(selected_search_path) != expected_search_hash:
        raise CampaignValidationError("algorithm search hash mismatch")
    search = _mapping(load_strict_json(selected_search_path), "search")
    budget = _mapping(search.get("exploration_budget"), "search.exploration_budget")
    if budget.get("actual_candidates") != 10 or len(_list(search.get("candidates"), "search.candidates")) != 10:
        raise CampaignValidationError("algorithm search actual candidate count is not 10")

    execution = _mapping(contract.get("execution"), "execution")
    if execution.get("default_mode") != "dry_run":
        raise CampaignValidationError("execution.default_mode must be dry_run")
    for name in (
        "gpu_project_root",
        "gpu_code_root",
        "gpu_campaign_result_root",
        "python_executable",
        "environment_prefix",
    ):
        _clean_absolute_path(execution.get(name), "execution.{}".format(name))
    project_path = PurePosixPath(str(execution["gpu_project_root"]))
    code_path = PurePosixPath(str(execution["gpu_code_root"]))
    result_path = PurePosixPath(str(execution["gpu_campaign_result_root"]))
    if project_path not in code_path.parents or project_path not in result_path.parents:
        raise CampaignValidationError("GPU code/result roots must remain under gpu_project_root")
    python_path = PurePosixPath(str(execution["python_executable"]))
    environment_path = PurePosixPath(str(execution["environment_prefix"]))
    if environment_path not in python_path.parents:
        raise CampaignValidationError(
            "execution.python_executable must remain under environment_prefix"
        )
    authorization = _mapping(execution.get("authorization"), "execution.authorization")
    expected_authorization = {
        "execute_env": "HFT_ALGORITHM_CAMPAIGN_EXECUTE",
        "execute_value": "YES",
        "authorization_env": "HFT_ALGORITHM_CAMPAIGN_AUTHORIZATION",
        "authorization_value": "APPROVED_BOUNDED_A01_A10_QUALIFICATION",
        "trusted_contract_sha256_env": "HFT_ALGORITHM_CAMPAIGN_TRUSTED_CONTRACT_SHA256",
    }
    if dict(authorization) != expected_authorization:
        raise CampaignValidationError("execution authorization contract is not exact")

    protocol = _mapping(contract.get("uniform_protocol"), "uniform_protocol")
    modes = protocol.get("modes")
    seeds = protocol.get("repeat_seeds")
    if modes != list(MODES) or seeds != [7, 11, 19]:
        raise CampaignValidationError("uniform modes/seeds must be normal,fallback and 7,11,19")
    if protocol.get("repeats_per_mode") != len(seeds):
        raise CampaignValidationError("repeats_per_mode does not match repeat seeds")
    if protocol.get("batch_size") != 512 or protocol.get("budget_us") != 5000:
        raise CampaignValidationError("uniform batch or budget is not frozen")
    if _finite(protocol.get("execution_budget_safety_ratio"), "execution_budget_safety_ratio") != 0.5:
        raise CampaignValidationError("uniform safety ratio must be 0.5")
    expected_execution_limits = {
        "max_train_packets_per_capture": 20000,
        "max_train_flows_per_capture": 2000,
        "max_test_packets_per_capture": 50000,
        "max_test_flows_per_capture": 5000,
        "estimators": 200,
        "n_jobs": 8,
        "max_payload_bytes": 256,
    }
    for name, expected in expected_execution_limits.items():
        if protocol.get(name) != expected:
            raise CampaignValidationError(
                "uniform protocol {} must be {}".format(name, expected)
            )
    if _finite(protocol.get("key_flow_ratio"), "uniform_protocol.key_flow_ratio") != 0.1:
        raise CampaignValidationError("uniform key_flow_ratio must be 0.1")
    if _finite(
        protocol.get("alignment_tolerance_s"),
        "uniform_protocol.alignment_tolerance_s",
    ) != 0.0:
        raise CampaignValidationError("uniform alignment_tolerance_s must be 0.0")

    groups = _mapping(contract.get("dataset_roles"), "dataset_roles")
    adaptation_groups = _list(groups.get("adaptation_groups"), "dataset_roles.adaptation_groups")
    calibration_groups = _list(groups.get("calibration_groups"), "dataset_roles.calibration_groups")
    evaluation_groups = _list(groups.get("fresh_evaluation_groups"), "dataset_roles.fresh_evaluation_groups")
    all_role_groups = adaptation_groups + calibration_groups + evaluation_groups
    if len(all_role_groups) != len(set(all_role_groups)):
        raise CampaignValidationError("dataset roles overlap")
    if protocol.get("fresh_evaluation_groups") != evaluation_groups:
        raise CampaignValidationError("uniform protocol evaluation groups drift")

    artifacts = _artifact_bindings(repo_root, contract)
    training_name = groups.get("training_manifest_artifact")
    holdout_name = groups.get("holdout_manifest_artifact")
    if training_name not in artifacts or holdout_name not in artifacts:
        raise CampaignValidationError("training/holdout manifests are not bound artifacts")
    holdout_path = _repo_file(repo_root, str(artifacts[str(holdout_name)]["path"]))
    holdout = _mapping(load_strict_json(holdout_path), "holdout_manifest")
    holdout_groups = [
        _mapping(item, "holdout.sample").get("group")
        for item in _list(holdout.get("samples"), "holdout.samples")
    ]
    if len(holdout_groups) != len(set(holdout_groups)) or set(holdout_groups) != set(all_role_groups):
        raise CampaignValidationError("holdout groups do not equal the frozen dataset-role partition")

    specs = _candidate_specs(contract, search)
    for spec in specs:
        candidate_id = str(spec["id"])
        spec_calibration = _list(spec.get("calibration_groups"), "{}.calibration_groups".format(candidate_id))
        spec_adaptation = _list(spec.get("adaptation_groups"), "{}.adaptation_groups".format(candidate_id))
        if spec.get("adaptation_policy") == "calibration_weighted":
            if spec_adaptation != adaptation_groups or spec_calibration != calibration_groups:
                raise CampaignValidationError("{} has incorrect adaptation/calibration roles".format(candidate_id))
        else:
            if spec_adaptation or spec_calibration != adaptation_groups + calibration_groups:
                raise CampaignValidationError("{} must exclude all pre-evaluation groups".format(candidate_id))
    return contract, search, artifacts, specs


def compile_campaign_plan(
    repo_root: Path,
    contract_path: Path,
    search_path: Optional[Path] = None,
    campaign_run_id: Optional[str] = None,
    created_at_utc: Optional[str] = None,
) -> Dict[str, object]:
    contract, search, artifacts, specs = validate_contract(repo_root, contract_path, search_path)
    contract_hash = sha256_file(contract_path)
    campaign_id = str(contract["campaign_id"])
    if campaign_run_id is None:
        campaign_run_id = campaign_id + "_dry_run"
    if not RUN_ID_RE.fullmatch(campaign_run_id):
        raise CampaignValidationError("campaign_run_id contains unsafe characters")
    if created_at_utc is None:
        created_at_utc = datetime.now(timezone.utc).isoformat()
    _iso8601(created_at_utc, "created_at_utc")
    protocol = _mapping(contract["uniform_protocol"], "uniform_protocol")
    execution = _mapping(contract["execution"], "execution")
    groups = _mapping(contract["dataset_roles"], "dataset_roles")
    training_artifact = str(groups["training_manifest_artifact"])
    holdout_artifact = str(groups["holdout_manifest_artifact"])
    if training_artifact not in artifacts or holdout_artifact not in artifacts:
        raise CampaignValidationError("training/holdout manifests are not bound artifacts")
    training_manifest = _mapping(
        load_strict_json(
            _repo_file(repo_root, str(artifacts[training_artifact]["path"]))
        ),
        "training_manifest",
    )
    holdout_manifest = _mapping(
        load_strict_json(
            _repo_file(repo_root, str(artifacts[holdout_artifact]["path"]))
        ),
        "holdout_manifest",
    )
    training_samples = []
    for raw_sample in _list(training_manifest.get("samples"), "training_manifest.samples"):
        sample = _mapping(raw_sample, "training_manifest.sample")
        group = sample.get("group")
        sample_path = sample.get("path")
        if not isinstance(group, str) or not group or not isinstance(sample_path, str):
            raise CampaignValidationError("training sample identity is invalid")
        training_samples.append({"group": group, "path": sample_path})
    training_capture_count = len(training_samples)
    holdout_group_counts: Dict[str, int] = {}
    holdout_samples_by_group: Dict[str, List[Dict[str, str]]] = {}
    for raw_sample in _list(
        holdout_manifest.get("samples"), "holdout_manifest.samples"
    ):
        sample = _mapping(raw_sample, "holdout_manifest.sample")
        group = sample.get("group")
        sample_path = sample.get("path")
        if not isinstance(group, str) or not group or not isinstance(sample_path, str):
            raise CampaignValidationError("holdout sample group is invalid")
        holdout_group_counts[group] = holdout_group_counts.get(group, 0) + 1
        holdout_samples_by_group.setdefault(group, []).append(
            {"group": group, "path": sample_path}
        )
    jobs: List[Dict[str, object]] = []
    for spec in specs:
        candidate_id = str(spec["id"])
        jobs.append(
            {
                "job_index": len(jobs),
                "candidate_id": candidate_id,
                "result_prefix": "HFT_ALGQUAL_{}".format(candidate_id),
                "run_tag": campaign_run_id,
                "runner_environment": {
                    "REPEATS": str(protocol["repeats_per_mode"]),
                    "BATCH_SIZE": str(protocol["batch_size"]),
                    "BUDGET_US": str(protocol["budget_us"]),
                    "SAFETY_RATIO": str(protocol["execution_budget_safety_ratio"]),
                    "MAX_TRAIN_PACKETS_PER_CAPTURE": str(protocol["max_train_packets_per_capture"]),
                    "MAX_TRAIN_FLOWS_PER_CAPTURE": str(protocol["max_train_flows_per_capture"]),
                    "MAX_TEST_PACKETS_PER_CAPTURE": str(protocol["max_test_packets_per_capture"]),
                    "MAX_TEST_FLOWS_PER_CAPTURE": str(protocol["max_test_flows_per_capture"]),
                    "ESTIMATORS": str(protocol["estimators"]),
                    "N_JOBS": str(protocol["n_jobs"]),
                    "KEY_FLOW_RATIO": str(protocol["key_flow_ratio"]),
                    "MAX_PAYLOAD_BYTES": str(protocol["max_payload_bytes"]),
                    "ALIGNMENT_TOLERANCE_S": str(protocol["alignment_tolerance_s"]),
                    "FEATURE_PROFILE": str(spec["feature_profile"]),
                    "CLASSIFIER": str(spec["classifier"]),
                    "THRESHOLD_POLICY": str(spec["threshold_policy"]),
                    "CALIBRATION_ATTACK_RECALL_FLOOR": str(spec["calibration_attack_recall_floor"]),
                    "CALIBRATION_GROUPS": ",".join(str(v) for v in spec["calibration_groups"]),
                    "ADAPTATION_POLICY": str(spec["adaptation_policy"]),
                    "ADAPTATION_GROUPS": ",".join(str(v) for v in spec["adaptation_groups"]),
                    "ADAPTATION_WEIGHT_MULTIPLIER": str(spec["adaptation_weight_multiplier"]),
                },
                "expected_modes": list(MODES),
                "expected_repeat_seeds": list(protocol["repeat_seeds"]),
                "expected_fresh_evaluation_groups": list(groups["fresh_evaluation_groups"]),
                "expected_ground_truth_csv": str(holdout_manifest["ground_truth_csv"]),
                "expected_capture_counts": {
                    "training": training_capture_count,
                    "calibration": sum(
                        holdout_group_counts.get(str(value), 0)
                        for value in spec["calibration_groups"]
                    ),
                    "adaptation": sum(
                        holdout_group_counts.get(str(value), 0)
                        for value in spec["adaptation_groups"]
                    ),
                    "holdout": sum(
                        holdout_group_counts.get(str(value), 0)
                        for value in groups["fresh_evaluation_groups"]
                    ),
                },
                "expected_capture_roles": {
                    "training": list(training_samples),
                    "calibration": [
                        sample
                        for value in spec["calibration_groups"]
                        for sample in holdout_samples_by_group.get(str(value), [])
                    ],
                    "adaptation": [
                        sample
                        for value in spec["adaptation_groups"]
                        for sample in holdout_samples_by_group.get(str(value), [])
                    ],
                    "holdout": [
                        sample
                        for value in groups["fresh_evaluation_groups"]
                        for sample in holdout_samples_by_group.get(str(value), [])
                    ],
                },
            }
        )
    return {
        "schema_version": 1,
        "scope": "hft_mgbs_algorithm_qualification_campaign_plan_v1",
        "campaign_id": campaign_id,
        "campaign_run_id": campaign_run_id,
        "created_at_utc": created_at_utc,
        "execution_mode": "dry_run_plan",
        "execution_authorized": False,
        "contract": {
            "path": str(contract_path.resolve()),
            "sha256": contract_hash,
        },
        "algorithm_search": {
            "path": str(_repo_file(repo_root, str(_mapping(contract["algorithm_search"], "algorithm_search")["path"]))),
            "sha256": _mapping(contract["algorithm_search"], "algorithm_search")["sha256"],
            "candidate_count": len(_list(search["candidates"], "search.candidates")),
        },
        "hard_constraints": copy.deepcopy(
            _mapping(search.get("hard_constraints"), "algorithm_search.hard_constraints")
        ),
        "bound_repository_artifacts": artifacts,
        "gpu_execution": {
            "project_root": execution["gpu_project_root"],
            "code_root": execution["gpu_code_root"],
            "campaign_result_root": execution["gpu_campaign_result_root"],
            "python_executable": execution["python_executable"],
            "environment_prefix": execution["environment_prefix"],
            "training_manifest": str(
                PurePosixPath(str(execution["gpu_code_root"]))
                / str(artifacts[training_artifact]["path"])
            ),
            "holdout_manifest": str(
                PurePosixPath(str(execution["gpu_code_root"]))
                / str(artifacts[holdout_artifact]["path"])
            ),
            "raw_results_remain_on_gpu": True,
        },
        "uniform_protocol": copy.deepcopy(protocol),
        "dataset_roles": copy.deepcopy(groups),
        "candidate_count": len(jobs),
        "job_count": len(jobs),
        "jobs": jobs,
        "algorithm_only_qualification_complete": False,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
    }


def discover_legacy_evidence(
    search_path: Path,
    max_schema_bytes: int = 16 * 1024 * 1024,
) -> Dict[str, object]:
    """Inventory legacy summaries without treating them as campaign evidence."""

    search = _mapping(load_strict_json(search_path), "search")
    candidates = _list(search.get("candidates"), "search.candidates")
    records: List[Dict[str, object]] = []
    for raw in candidates:
        candidate = _mapping(raw, "search.candidate")
        candidate_id = candidate.get("id")
        path_value = candidate.get("evidence")
        record: Dict[str, object] = {
            "candidate_id": candidate_id,
            "path": path_value,
            "exists": False,
            "regular_file": False,
            "symlink": False,
            "size_bytes": None,
            "sha256": None,
            "schema_inspected": False,
            "top_level_type": None,
            "top_level_keys": None,
            "protocol_comparable": False,
            "counts_toward_campaign": False,
            "qualification_status": "legacy_discovery_only",
            "errors": [],
        }
        try:
            clean = _clean_absolute_path(
                path_value, "{}.evidence".format(candidate_id)
            )
            path = Path(clean)
            record["exists"] = path.exists()
            record["symlink"] = path.is_symlink()
            record["regular_file"] = path.is_file() and not path.is_symlink()
            if not record["regular_file"]:
                record["errors"].append("not_regular_file")
            else:
                size = path.stat().st_size
                record["size_bytes"] = size
                record["sha256"] = sha256_file(path)
                if size <= max_schema_bytes:
                    payload = load_strict_json(path)
                    record["schema_inspected"] = True
                    record["top_level_type"] = type(payload).__name__
                    record["top_level_keys"] = (
                        sorted(payload) if isinstance(payload, Mapping) else None
                    )
                else:
                    record["errors"].append("schema_inspection_size_limit")
        except (OSError, UnicodeError, CampaignValidationError, ValueError) as error:
            record["errors"].append(
                "{}:{}".format(type(error).__name__, error)
            )
        records.append(record)
    discovered = sum(
        bool(record["regular_file"] and record["sha256"]) for record in records
    )
    return {
        "schema_version": 1,
        "scope": "hft_mgbs_legacy_algorithm_evidence_discovery_v1",
        "algorithm_search": {
            "path": str(search_path.resolve()),
            "sha256": sha256_file(search_path),
        },
        "candidate_count": len(records),
        "discovered_regular_file_count": discovered,
        "protocol_comparable_candidate_count": 0,
        "campaign_qualified_candidate_count": 0,
        "legacy_hashes_are_qualification_evidence": False,
        "counts_toward_campaign": False,
        "records": records,
    }


def _decode_utf8(raw: bytes, name: str) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CampaignValidationError("UTF-8 BOM is not allowed: {}".format(name))
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise CampaignValidationError("invalid UTF-8 {}".format(name)) from error


def _parse_key_value_bytes(raw_bytes: bytes, name: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line_number, raw in enumerate(_decode_utf8(raw_bytes, name).splitlines(), start=1):
        if not raw or "=" not in raw:
            raise CampaignValidationError("invalid manifest line {} in {}".format(line_number, name))
        key, value = raw.split("=", 1)
        if not key or key in result or any(c in key + value for c in "\r\n\x00"):
            raise CampaignValidationError("invalid or duplicate manifest key in {}".format(name))
        result[key] = value
    return result


def _parse_key_value(path: Path) -> Dict[str, str]:
    return _parse_key_value_bytes(_stable_file_bytes(path, str(path)), str(path))


def _parse_sha256_manifest_bytes(raw_bytes: bytes, manifest_name: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line_number, raw in enumerate(
        _decode_utf8(raw_bytes, manifest_name).splitlines(), start=1
    ):
        match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", raw)
        if match is None:
            raise CampaignValidationError(
                "invalid SHA-256 manifest line {} in {}".format(
                    line_number, manifest_name
                )
            )
        digest, path_name = match.groups()
        if path_name in result or any(c in path_name for c in "\r\n\x00"):
            raise CampaignValidationError("duplicate or unsafe SHA-256 manifest path")
        result[path_name] = digest
    return result


def _parse_sha256_manifest(path: Path) -> Dict[str, str]:
    return _parse_sha256_manifest_bytes(_stable_file_bytes(path, str(path)), str(path))


def _same_number(left: object, right: object, tolerance: float = 1e-12) -> bool:
    try:
        return abs(_finite(left, "metric") - _finite(right, "metric")) <= tolerance
    except CampaignValidationError:
        return False


def _validate_constraint_audit(
    value: object, name: str, no_overrun_cost_limit_us: Optional[float] = None
) -> Mapping[str, object]:
    audit = _mapping(value, name)
    expected_fields = {
        "budget_overrun_count",
        "key_flow_total",
        "key_flow_covered",
        "key_flow_coverage",
        "key_flow_coverage_min",
        "max_actual_optional_cost_us",
    }
    if set(audit) != expected_fields:
        raise CampaignValidationError("{} field set is not exact".format(name))
    budget_overrun = _integer(
        audit.get("budget_overrun_count"),
        "{}.budget_overrun_count".format(name),
        0,
    )
    key_total = _integer(
        audit.get("key_flow_total"), "{}.key_flow_total".format(name), 1
    )
    key_covered = _integer(
        audit.get("key_flow_covered"), "{}.key_flow_covered".format(name), 0
    )
    if key_covered > key_total:
        raise CampaignValidationError(
            "{}.key_flow_covered exceeds key_flow_total".format(name)
        )
    coverage = _unit_interval(
        audit.get("key_flow_coverage"), "{}.key_flow_coverage".format(name)
    )
    coverage_min = _unit_interval(
        audit.get("key_flow_coverage_min"),
        "{}.key_flow_coverage_min".format(name),
    )
    if not _same_number(coverage, key_covered / key_total):
        raise CampaignValidationError(
            "{}.key_flow_coverage does not match covered/total".format(name)
        )
    if coverage_min > coverage:
        raise CampaignValidationError(
            "{}.key_flow_coverage_min exceeds aggregate coverage".format(name)
        )
    optional_cost = _finite(
        audit.get("max_actual_optional_cost_us"),
        "{}.max_actual_optional_cost_us".format(name),
    )
    if optional_cost < 0.0:
        raise CampaignValidationError(
            "{}.max_actual_optional_cost_us must be non-negative".format(name)
        )
    if (
        budget_overrun == 0
        and no_overrun_cost_limit_us is not None
        and optional_cost > no_overrun_cost_limit_us + 1e-9
    ):
        raise CampaignValidationError(
            "{}.optional cost contradicts zero budget overruns".format(name)
        )
    # Keep the validated values live so a future schema extension cannot
    # silently turn the checks above into dead code.
    if budget_overrun < 0:
        raise CampaignValidationError("{} budget accounting is invalid".format(name))
    return audit


def _validate_capture_role(
    payload: Mapping[str, object],
    role: str,
    expected_samples: Sequence[object],
    packet_limit: int,
    flow_limit: int,
    safety_ratio: float,
    no_overrun_cost_limit_us: float,
) -> Dict[str, object]:
    field = "{}_captures".format(role)
    expected = [
        _mapping(item, "expected {} capture".format(role))
        for item in expected_samples
    ]
    if not expected:
        if field in payload:
            raise CampaignValidationError("unexpected empty-role capture evidence: {}".format(role))
        return {
            "flow_count": 0,
            "audit": None,
            "fingerprints": {},
            "attack_flow_count": 0,
            "benign_flow_count": 0,
            "capture_time_bounds": [],
            "label_fingerprints": {},
        }
    rows = _list(payload.get(field), "raw.{}".format(field))
    if len(rows) != len(expected):
        raise CampaignValidationError("{} capture evidence count drift".format(role))
    expected_identities = sorted(
        (str(item.get("group")), str(item.get("path"))) for item in expected
    )
    observed_identities = []
    validated_rows = []
    base_fields = {
        "group",
        "path",
        "execution_budget_safety_ratio",
        "parsed_packets",
        "rejected_records",
        "packet_start_timestamp",
        "packet_last_timestamp",
        "flow_records",
        "selected_flows",
        "budget_overrun_count",
        "key_flow_total",
        "key_flow_covered",
        "key_flow_coverage",
        "key_flow_coverage_min",
        "max_actual_optional_cost_us",
        "batch_audits",
        "tier_counts",
        "selected_flow_sha256",
    }
    expected_fields = base_fields if role == "training" else base_fields | {
        "attack_flows",
        "benign_flows",
        "selected_flow_label_sha256",
    }
    for raw_row in rows:
        row = _mapping(raw_row, "raw.{} row".format(field))
        if set(row) != expected_fields:
            raise CampaignValidationError("{} capture row field set is not exact".format(role))
        group = row.get("group")
        path = row.get("path")
        if not isinstance(group, str) or not isinstance(path, str):
            raise CampaignValidationError("{} capture identity is invalid".format(role))
        observed_identities.append((group, path))
        if not _same_number(row.get("execution_budget_safety_ratio"), safety_ratio):
            raise CampaignValidationError("{} capture safety-ratio drift".format(role))
        parsed_packets = _integer(row.get("parsed_packets"), "capture parsed_packets", 0)
        _integer(row.get("rejected_records"), "capture rejected_records", 0)
        flow_records = _integer(row.get("flow_records"), "capture flow_records", 0)
        selected_flows = _integer(row.get("selected_flows"), "capture selected_flows", 0)
        if parsed_packets > packet_limit or selected_flows > flow_limit or selected_flows > flow_records:
            raise CampaignValidationError("{} capture cap/accounting drift".format(role))
        start = row.get("packet_start_timestamp")
        end = row.get("packet_last_timestamp")
        if (start is None) is not (end is None):
            raise CampaignValidationError("capture timestamp bounds are incomplete")
        if start is not None and _finite(start, "capture start") > _finite(end, "capture end"):
            raise CampaignValidationError("capture timestamps are reversed")
        budget_overrun = _integer(row.get("budget_overrun_count"), "capture budget overrun", 0)
        key_total = _integer(row.get("key_flow_total"), "capture key total", 0)
        key_covered = _integer(row.get("key_flow_covered"), "capture key covered", 0)
        if key_covered > key_total:
            raise CampaignValidationError("capture key-flow accounting drift")
        coverage = _unit_interval(row.get("key_flow_coverage"), "capture key coverage")
        expected_coverage = 1.0 if key_total == 0 else key_covered / key_total
        if not _same_number(coverage, expected_coverage):
            raise CampaignValidationError("capture key-flow coverage drift")
        coverage_min = _unit_interval(row.get("key_flow_coverage_min"), "capture key coverage min")
        optional_cost = _finite(row.get("max_actual_optional_cost_us"), "capture optional cost")
        if optional_cost < 0.0 or (
            budget_overrun == 0 and optional_cost > no_overrun_cost_limit_us + 1e-9
        ):
            raise CampaignValidationError("capture budget evidence is inconsistent")
        batches = _list(row.get("batch_audits"), "capture batch audits")
        if (parsed_packets > 0) is not bool(batches):
            raise CampaignValidationError("capture batch evidence presence drift")
        batch_packet_count = batch_key_total = batch_key_covered = 0
        batch_budget_overrun = 0
        batch_coverage_min = 1.0
        batch_max_cost = 0.0
        for batch_index, raw_batch in enumerate(batches):
            batch = _mapping(raw_batch, "capture batch audit")
            if set(batch) != {
                "batch_index",
                "packet_count",
                "key_flow_total",
                "key_flow_covered",
                "budget_overrun_count",
                "actual_used_us",
            }:
                raise CampaignValidationError("capture batch audit field set is not exact")
            if _integer(batch.get("batch_index"), "batch index", 0) != batch_index:
                raise CampaignValidationError("capture batch indexes are not contiguous")
            batch_packet_count += _integer(batch.get("packet_count"), "batch packet count", 1)
            batch_total = _integer(batch.get("key_flow_total"), "batch key total", 0)
            batch_covered = _integer(batch.get("key_flow_covered"), "batch key covered", 0)
            if batch_covered > batch_total:
                raise CampaignValidationError("batch key-flow accounting drift")
            batch_key_total += batch_total
            batch_key_covered += batch_covered
            batch_coverage_min = min(
                batch_coverage_min,
                1.0 if batch_total == 0 else batch_covered / batch_total,
            )
            batch_overrun = _integer(batch.get("budget_overrun_count"), "batch budget overrun", 0)
            batch_budget_overrun += batch_overrun
            batch_cost = _finite(batch.get("actual_used_us"), "batch actual cost")
            if batch_cost < 0.0 or (
                batch_overrun == 0 and batch_cost > no_overrun_cost_limit_us + 1e-9
            ):
                raise CampaignValidationError("batch budget evidence is inconsistent")
            batch_max_cost = max(batch_max_cost, batch_cost)
        if (
            batch_packet_count != parsed_packets
            or batch_key_total != key_total
            or batch_key_covered != key_covered
            or batch_budget_overrun != budget_overrun
            or not _same_number(batch_coverage_min, coverage_min)
            or not _same_number(batch_max_cost, optional_cost)
        ):
            raise CampaignValidationError("capture aggregate does not match batch audits")
        tier_counts = _mapping(row.get("tier_counts"), "capture tier counts")
        if set(tier_counts) != {"base", "flow", "deep"}:
            raise CampaignValidationError("capture tier-count field set is not exact")
        for tier in tier_counts:
            _integer(tier_counts[tier], "capture tier count", 0)
        fingerprint = row.get("selected_flow_sha256")
        if not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint):
            raise CampaignValidationError("capture selected-flow fingerprint is invalid")
        if role != "training":
            attack = _integer(row.get("attack_flows"), "capture attack flows", 0)
            benign = _integer(row.get("benign_flows"), "capture benign flows", 0)
            if attack + benign != selected_flows:
                raise CampaignValidationError("capture label-flow accounting drift")
            label_fingerprint = row.get("selected_flow_label_sha256")
            if not isinstance(label_fingerprint, str) or not SHA256_RE.fullmatch(label_fingerprint):
                raise CampaignValidationError("capture label fingerprint is invalid")
        validated_rows.append(
            {
                "selected_flows": selected_flows,
                "budget_overrun_count": budget_overrun,
                "key_flow_total": key_total,
                "key_flow_covered": key_covered,
                "key_flow_coverage_min": coverage_min,
                "max_actual_optional_cost_us": optional_cost,
                "fingerprint": fingerprint,
                "identity": "{}\x00{}".format(group, path),
                "attack_flows": 0 if role == "training" else attack,
                "benign_flows": 0 if role == "training" else benign,
                "group": group,
                "packet_start_timestamp": start,
                "packet_last_timestamp": end,
                "label_fingerprint": None if role == "training" else label_fingerprint,
            }
        )
    if sorted(observed_identities) != expected_identities:
        raise CampaignValidationError("{} capture path/group roles drift".format(role))
    key_total = sum(item["key_flow_total"] for item in validated_rows)
    key_covered = sum(item["key_flow_covered"] for item in validated_rows)
    if key_total <= 0:
        raise CampaignValidationError("{} capture aggregate has no key flows".format(role))
    audit = {
        "budget_overrun_count": sum(item["budget_overrun_count"] for item in validated_rows),
        "key_flow_total": key_total,
        "key_flow_covered": key_covered,
        "key_flow_coverage": key_covered / key_total,
        "key_flow_coverage_min": min(item["key_flow_coverage_min"] for item in validated_rows),
        "max_actual_optional_cost_us": max(item["max_actual_optional_cost_us"] for item in validated_rows),
    }
    return {
        "flow_count": sum(item["selected_flows"] for item in validated_rows),
        "audit": audit,
        "fingerprints": {
            item["identity"]: item["fingerprint"] for item in validated_rows
        },
        "attack_flow_count": sum(item["attack_flows"] for item in validated_rows),
        "benign_flow_count": sum(item["benign_flows"] for item in validated_rows),
        "capture_time_bounds": [
            {
                "group": item["group"],
                "packet_start_timestamp": item["packet_start_timestamp"],
                "packet_last_timestamp": item["packet_last_timestamp"],
            }
            for item in validated_rows
        ],
        "label_fingerprints": {
            item["identity"]: item["label_fingerprint"]
            for item in validated_rows if item["label_fingerprint"] is not None
        },
    }


def _binary_prediction_metrics(
    labels: Sequence[int], probabilities: Sequence[float], threshold: float
) -> Dict[str, object]:
    try:
        return shared_binary_prediction_metrics(labels, probabilities, threshold)
    except (TypeError, ValueError) as error:
        raise CampaignValidationError(str(error)) from error
    if len(labels) != len(probabilities) or not labels:
        raise CampaignValidationError("prediction evidence arrays must align and be non-empty")
    clean_labels = [
        _integer(value, "prediction label", 0) for value in labels
    ]
    if any(value not in (0, 1) for value in clean_labels):
        raise CampaignValidationError("prediction labels must be binary")
    clean_probabilities = [
        _unit_interval(value, "prediction probability") for value in probabilities
    ]
    threshold_value = _unit_interval(threshold, "decision threshold")
    tp = tn = fp = fn = 0
    for label, probability in zip(clean_labels, clean_probabilities):
        predicted = int(probability >= threshold_value)
        if label == 1 and predicted == 1:
            tp += 1
        elif label == 0 and predicted == 0:
            tn += 1
        elif label == 0:
            fp += 1
        else:
            fn += 1
    attack_total = tp + fn
    benign_total = tn + fp
    if attack_total == 0 or benign_total == 0:
        raise CampaignValidationError("prediction evidence must contain both classes")
    attack_recall = tp / attack_total
    benign_recall = tn / benign_total
    attack_denominator = 2 * tp + fp + fn
    benign_denominator = 2 * tn + fp + fn
    attack_f1 = 0.0 if attack_denominator == 0 else 2.0 * tp / attack_denominator
    benign_f1 = 0.0 if benign_denominator == 0 else 2.0 * tn / benign_denominator

    ranked = sorted(
        zip(clean_probabilities, clean_labels), key=lambda item: item[0]
    )
    positive_rank_sum = 0.0
    index = 0
    while index < len(ranked):
        stop = index + 1
        while stop < len(ranked) and ranked[stop][0] == ranked[index][0]:
            stop += 1
        average_rank = ((index + 1) + stop) / 2.0
        positive_rank_sum += average_rank * sum(
            item[1] for item in ranked[index:stop]
        )
        index = stop
    auroc = (
        positive_rank_sum - attack_total * (attack_total + 1) / 2.0
    ) / (attack_total * benign_total)

    descending = sorted(
        zip(clean_probabilities, clean_labels),
        key=lambda item: item[0],
        reverse=True,
    )
    true_positive = false_positive = previous_true_positive = 0
    auprc = 0.0
    index = 0
    while index < len(descending):
        stop = index + 1
        while stop < len(descending) and descending[stop][0] == descending[index][0]:
            stop += 1
        true_positive += sum(item[1] for item in descending[index:stop])
        false_positive += (stop - index) - sum(
            item[1] for item in descending[index:stop]
        )
        precision = true_positive / (true_positive + false_positive)
        auprc += (
            (true_positive - previous_true_positive) / attack_total
        ) * precision
        previous_true_positive = true_positive
        index = stop

    ece = 0.0
    total = len(clean_labels)
    for bin_index in range(10):
        lower = bin_index / 10.0
        upper = (bin_index + 1) / 10.0
        members = [
            position
            for position, probability in enumerate(clean_probabilities)
            if lower <= probability < upper
            or (bin_index == 9 and probability == 1.0)
        ]
        if members:
            confidence = sum(clean_probabilities[position] for position in members) / len(members)
            accuracy = sum(clean_labels[position] for position in members) / len(members)
            ece += len(members) / total * abs(accuracy - confidence)
    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "macro_f1": (attack_f1 + benign_f1) / 2.0,
        "balanced_accuracy": (attack_recall + benign_recall) / 2.0,
        "auroc": auroc,
        "auprc": auprc,
        "benign_recall": benign_recall,
        "attack_recall": attack_recall,
        "ece": ece,
        "predicted_attack_ratio": (tp + fp) / total,
    }


def _select_macro_f1_threshold_replay(
    labels: Sequence[int], probabilities: Sequence[float], floor: float
) -> Dict[str, object]:
    try:
        return shared_select_macro_f1_threshold(labels, probabilities, floor)
    except (TypeError, ValueError) as error:
        raise CampaignValidationError(str(error)) from error
    clean_probabilities = [
        _unit_interval(value, "calibration probability") for value in probabilities
    ]
    thresholds = sorted(set(clean_probabilities))
    if not thresholds:
        raise CampaignValidationError("calibration prediction evidence is empty")
    thresholds = sorted(set(thresholds + [min(1.0, max(thresholds) + 1e-12)]))
    candidates = []
    for threshold in thresholds:
        item = _binary_prediction_metrics(labels, clean_probabilities, threshold)
        item["threshold"] = threshold
        if float(item["attack_recall"]) >= floor:
            candidates.append(item)
    if not candidates:
        raise CampaignValidationError("calibration threshold replay has no feasible candidate")
    return max(
        candidates,
        key=lambda item: (
            float(item["macro_f1"]),
            float(item["balanced_accuracy"]),
            -abs(float(item["threshold"]) - 0.5),
        ),
    )


def _validate_quality_payload(
    value: object,
    expected_seed: int,
    expected_env: Optional[Mapping[str, object]] = None,
    expected_evaluation_groups: Optional[Sequence[object]] = None,
    expected_capture_counts: Optional[Mapping[str, object]] = None,
) -> Mapping[str, object]:
    quality = _mapping(value, "raw.quality")
    if set(quality) != {
        "classifier",
        "feature_profile",
        "threshold_policy",
        "calibration_used_for_threshold",
        "calibration_attack_recall_floor",
        "calibration_groups",
        "adaptation_policy",
        "adaptation_groups",
        "adaptation_weight_multiplier",
        "evaluation_groups",
        "feature_count",
        "train_flow_count",
        "adaptation_flow_count",
        "fit_flow_count",
        "calibration_flow_count",
        "test_flow_count",
        "test_attack_count",
        "test_benign_count",
        "seeds",
        "aggregate_confusion_matrix",
        "conservative",
    }:
        raise CampaignValidationError("quality field set is not exact")
    train_flow_count = _integer(
        quality.get("train_flow_count"), "quality.train_flow_count", 1
    )
    adaptation_flow_count = _integer(
        quality.get("adaptation_flow_count"), "quality.adaptation_flow_count", 0
    )
    fit_flow_count = _integer(
        quality.get("fit_flow_count"), "quality.fit_flow_count", 1
    )
    calibration_flow_count = _integer(
        quality.get("calibration_flow_count"), "quality.calibration_flow_count", 0
    )
    test_flow_count = _integer(
        quality.get("test_flow_count"), "quality.test_flow_count", 1
    )
    test_attack_count = _integer(
        quality.get("test_attack_count"), "quality.test_attack_count", 1
    )
    test_benign_count = _integer(
        quality.get("test_benign_count"), "quality.test_benign_count", 1
    )
    _integer(quality.get("feature_count"), "quality.feature_count", 1)
    if fit_flow_count != train_flow_count + adaptation_flow_count:
        raise CampaignValidationError("quality fit-flow accounting is inconsistent")
    if test_flow_count != test_attack_count + test_benign_count:
        raise CampaignValidationError("quality test-flow accounting is inconsistent")
    if expected_env is not None and expected_capture_counts is not None:
        role_limits = {
            "train_flow_count": (
                train_flow_count,
                _integer(expected_capture_counts.get("training"), "training captures", 0),
                int(str(expected_env["MAX_TRAIN_FLOWS_PER_CAPTURE"])),
            ),
            "calibration_flow_count": (
                calibration_flow_count,
                _integer(expected_capture_counts.get("calibration"), "calibration captures", 0),
                int(str(expected_env["MAX_TEST_FLOWS_PER_CAPTURE"])),
            ),
            "adaptation_flow_count": (
                adaptation_flow_count,
                _integer(expected_capture_counts.get("adaptation"), "adaptation captures", 0),
                int(str(expected_env["MAX_TEST_FLOWS_PER_CAPTURE"])),
            ),
            "test_flow_count": (
                test_flow_count,
                _integer(expected_capture_counts.get("holdout"), "holdout captures", 0),
                int(str(expected_env["MAX_TEST_FLOWS_PER_CAPTURE"])),
            ),
        }
        for role_name, (observed, captures, per_capture_limit) in role_limits.items():
            if (captures == 0 and observed != 0) or (
                captures > 0 and not 0 < observed <= captures * per_capture_limit
            ):
                raise CampaignValidationError(
                    "quality {} exceeds or contradicts frozen capture capacity".format(role_name)
                )
    threshold_policy = None
    if expected_env is not None:
        scalar_expected = {
            "feature_profile": expected_env["FEATURE_PROFILE"],
            "threshold_policy": expected_env["THRESHOLD_POLICY"],
            "adaptation_policy": expected_env["ADAPTATION_POLICY"],
        }
        for name, expected in scalar_expected.items():
            if quality.get(name) != expected:
                raise CampaignValidationError("quality {} drift".format(name))
        threshold_policy = str(expected_env["THRESHOLD_POLICY"])
        if quality.get("calibration_used_for_threshold") is not (
            threshold_policy == "calibration_macro_f1"
        ):
            raise CampaignValidationError("quality threshold-use flag drift")
        for name, env_name in (
            ("calibration_attack_recall_floor", "CALIBRATION_ATTACK_RECALL_FLOOR"),
            ("adaptation_weight_multiplier", "ADAPTATION_WEIGHT_MULTIPLIER"),
        ):
            if not _same_number(
                quality.get(name), float(str(expected_env[env_name]))
            ):
                raise CampaignValidationError("quality {} drift".format(name))
        for name, env_name in (
            ("calibration_groups", "CALIBRATION_GROUPS"),
            ("adaptation_groups", "ADAPTATION_GROUPS"),
        ):
            expected_groups = sorted(
                filter(None, str(expected_env[env_name]).split(","))
            )
            if quality.get(name) != expected_groups:
                raise CampaignValidationError("quality {} drift".format(name))
        has_adaptation_groups = bool(str(expected_env["ADAPTATION_GROUPS"]))
        has_calibration_groups = bool(str(expected_env["CALIBRATION_GROUPS"]))
        if (adaptation_flow_count > 0) is not has_adaptation_groups:
            raise CampaignValidationError(
                "quality adaptation-flow count contradicts adaptation roles"
            )
        if (calibration_flow_count > 0) is not has_calibration_groups:
            raise CampaignValidationError(
                "quality calibration-flow count contradicts calibration roles"
            )
        if quality.get("evaluation_groups") != list(expected_evaluation_groups or []):
            raise CampaignValidationError("quality evaluation groups drift")
        classifier_name = str(expected_env["CLASSIFIER"])
        classifier = _mapping(quality.get("classifier"), "quality.classifier")
        if classifier_name == "extra_trees":
            classifier_expected = {
                "name": "ExtraTreesClassifier",
                "n_estimators": int(str(expected_env["ESTIMATORS"])),
                "min_samples_leaf": 2,
                "class_weight": "balanced",
                "n_jobs": int(str(expected_env["N_JOBS"])),
            }
        elif classifier_name == "logistic":
            classifier_expected = {
                "name": "LogisticRegression",
                "solver": "liblinear",
                "max_iter": 2000,
                "class_weight": "balanced",
                "standard_scaler": True,
            }
        else:
            raise CampaignValidationError("quality classifier is unsupported")
        if dict(classifier) != classifier_expected:
            raise CampaignValidationError("quality classifier metadata drift")
    seed_rows = _list(quality.get("seeds"), "quality.seeds")
    if len(seed_rows) != 1:
        raise CampaignValidationError("quality.seeds must contain exactly one repeat seed")
    seed_row = _mapping(seed_rows[0], "quality.seed")
    expected_seed_fields = {
        "seed",
        "decision_threshold",
        "TP",
        "TN",
        "FP",
        "FN",
        "evaluation_labels",
        "evaluation_probabilities",
        "calibration_labels",
        "calibration_probabilities",
        "macro_f1",
        "balanced_accuracy",
        "auroc",
        "auprc",
        "benign_recall",
        "attack_recall",
        "ece",
        "predicted_attack_ratio",
    }
    if threshold_policy == "calibration_macro_f1":
        expected_seed_fields.add("calibration_selection")
    if set(seed_row) != expected_seed_fields:
        raise CampaignValidationError("quality seed field set is not exact")
    if _integer(seed_row.get("seed"), "quality.seed.seed", 0) != expected_seed:
        raise CampaignValidationError("quality seed does not match repeat seed")
    seed_metric_names = (
        "macro_f1",
        "balanced_accuracy",
        "auroc",
        "auprc",
        "benign_recall",
        "attack_recall",
        "ece",
        "predicted_attack_ratio",
    )
    seed_metrics = {
        name: _unit_interval(seed_row.get(name), "quality.seed.{}".format(name))
        for name in seed_metric_names
    }
    decision_threshold = _finite(
        seed_row.get("decision_threshold"), "quality.seed.decision_threshold"
    )
    evaluation_labels = _list(
        seed_row.get("evaluation_labels"), "quality.seed.evaluation_labels"
    )
    evaluation_probabilities = _list(
        seed_row.get("evaluation_probabilities"),
        "quality.seed.evaluation_probabilities",
    )
    recomputed = _binary_prediction_metrics(
        evaluation_labels, evaluation_probabilities, decision_threshold
    )
    if len(evaluation_labels) != test_flow_count:
        raise CampaignValidationError("prediction evidence count does not match test flows")
    for name in ("TP", "TN", "FP", "FN"):
        if _integer(seed_row.get(name), "quality.seed.{}".format(name), 0) != recomputed[name]:
            raise CampaignValidationError("quality seed confusion matrix drift")
    if (
        recomputed["TP"] + recomputed["FN"] != test_attack_count
        or recomputed["TN"] + recomputed["FP"] != test_benign_count
    ):
        raise CampaignValidationError("quality label counts contradict prediction evidence")
    for name in seed_metric_names:
        if not _same_number(seed_metrics[name], recomputed[name]):
            raise CampaignValidationError(
                "quality seed metric {} is not replayable".format(name)
            )
    aggregate_confusion = _mapping(
        quality.get("aggregate_confusion_matrix"),
        "quality.aggregate_confusion_matrix",
    )
    if set(aggregate_confusion) != {"TP", "TN", "FP", "FN"} or any(
        _integer(aggregate_confusion.get(name), "aggregate confusion {}".format(name), 0)
        != recomputed[name]
        for name in ("TP", "TN", "FP", "FN")
    ):
        raise CampaignValidationError("aggregate confusion matrix drift")
    calibration = seed_row.get("calibration_selection")
    calibration_labels = _list(
        seed_row.get("calibration_labels"), "quality.seed.calibration_labels"
    )
    calibration_probabilities = _list(
        seed_row.get("calibration_probabilities"),
        "quality.seed.calibration_probabilities",
    )
    if threshold_policy == "fixed":
        if calibration is not None or calibration_labels or calibration_probabilities or not _same_number(
            seed_row.get("decision_threshold"), 0.5
        ):
            raise CampaignValidationError("fixed threshold policy evidence drift")
    elif threshold_policy == "calibration_macro_f1":
        if (
            calibration is None
            or len(calibration_labels) != calibration_flow_count
            or len(calibration_probabilities) != calibration_flow_count
        ):
            raise CampaignValidationError("calibration selection is missing")
    if calibration is not None:
        selection = _mapping(calibration, "quality.seed.calibration_selection")
        if set(selection) != {
            "threshold",
            "macro_f1",
            "balanced_accuracy",
            "attack_recall",
            "benign_recall",
            "predicted_attack_ratio",
            "minimum_attack_recall_constraint",
        }:
            raise CampaignValidationError("calibration selection field set is not exact")
        for name in (
            "macro_f1",
            "balanced_accuracy",
            "attack_recall",
            "benign_recall",
            "predicted_attack_ratio",
            "minimum_attack_recall_constraint",
        ):
            _unit_interval(
                selection.get(name),
                "quality.seed.calibration_selection.{}".format(name),
            )
        selected_threshold = _finite(
            selection.get("threshold"),
            "quality.seed.calibration_selection.threshold",
        )
        if not _same_number(
            seed_row.get("decision_threshold"), selected_threshold
        ):
            raise CampaignValidationError("selected threshold evidence drift")
        floor = _unit_interval(
            selection.get("minimum_attack_recall_constraint"),
            "quality.seed.calibration_selection.minimum_attack_recall_constraint",
        )
        if expected_env is not None and not _same_number(
            floor, float(str(expected_env["CALIBRATION_ATTACK_RECALL_FLOOR"]))
        ):
            raise CampaignValidationError("calibration attack recall floor drift")
        replayed_selection = _select_macro_f1_threshold_replay(
            calibration_labels, calibration_probabilities, floor
        )
        for name in (
            "threshold",
            "macro_f1",
            "balanced_accuracy",
            "attack_recall",
            "benign_recall",
            "predicted_attack_ratio",
        ):
            if not _same_number(selection.get(name), replayed_selection[name]):
                raise CampaignValidationError("calibration threshold selection replay drift")
        if float(replayed_selection["attack_recall"]) < floor:
            raise CampaignValidationError("calibration attack recall floor is not met")
    conservative = _mapping(
        quality.get("conservative"), "quality.conservative"
    )
    conservative_to_seed = {
        "macro_f1_min": "macro_f1",
        "balanced_accuracy_min": "balanced_accuracy",
        "auroc_min": "auroc",
        "auprc_min": "auprc",
        "benign_recall_min": "benign_recall",
        "attack_recall_min": "attack_recall",
        "ece_max": "ece",
    }
    if set(conservative) != set(conservative_to_seed):
        raise CampaignValidationError("quality conservative field set is not exact")
    for conservative_name, seed_name in conservative_to_seed.items():
        observed = _unit_interval(
            conservative.get(conservative_name),
            "quality.conservative.{}".format(conservative_name),
        )
        if not _same_number(observed, seed_metrics[seed_name]):
            raise CampaignValidationError(
                "quality conservative metric {} does not match raw seed".format(
                    conservative_name
                )
            )
    return quality


def _candidate_raw_metrics(payloads: Sequence[Mapping[str, object]], budget_us: int) -> Dict[str, float]:
    conservative = [
        _mapping(_mapping(payload.get("quality"), "quality").get("conservative"), "quality.conservative")
        for payload in payloads
    ]
    audits = [
        _validate_constraint_audit(payload.get(name), name)
        for payload in payloads
        for name in (
            "training_constraint_audit",
            "calibration_constraint_audit",
            "adaptation_constraint_audit",
            "holdout_constraint_audit",
        )
        if name in payload
    ]
    event_audits = [
        _mapping(payload.get("ground_truth_event_recall_audit"), "ground_truth_event_recall_audit")
        for payload in payloads
    ]
    return {
        "macro_f1_min": min(_unit_interval(item.get("macro_f1_min"), "macro_f1_min") for item in conservative),
        "balanced_accuracy_min": min(_unit_interval(item.get("balanced_accuracy_min"), "balanced_accuracy_min") for item in conservative),
        "auroc_min": min(_unit_interval(item.get("auroc_min"), "auroc_min") for item in conservative),
        "attack_recall_min": min(_unit_interval(item.get("attack_recall_min"), "attack_recall_min") for item in conservative),
        "benign_recall_min": min(_unit_interval(item.get("benign_recall_min"), "benign_recall_min") for item in conservative),
        "auprc_min": min(_unit_interval(item.get("auprc_min"), "auprc_min") for item in conservative),
        "ece_max": max(_unit_interval(item.get("ece_max"), "ece_max") for item in conservative),
        "ground_truth_event_recall_min": min(_unit_interval(item.get("event_recall"), "event_recall") for item in event_audits),
        "key_flow_coverage_min": min(_unit_interval(item.get("key_flow_coverage_min"), "key_flow_coverage_min") for item in audits),
        "budget_overrun_count_max": max(_integer(item.get("budget_overrun_count"), "budget_overrun_count", 0) for item in audits),
        "budget_us_max": float(budget_us),
    }


def _aggregate_mode_metrics(mode_metrics: Mapping[str, Mapping[str, float]]) -> Dict[str, float]:
    return {
        "macro_f1_min": min(mode_metrics[mode]["macro_f1_min"] for mode in MODES),
        "balanced_accuracy_min": min(mode_metrics[mode]["balanced_accuracy_min"] for mode in MODES),
        "auroc_min": min(mode_metrics[mode]["auroc_min"] for mode in MODES),
        "attack_recall_min": min(mode_metrics[mode]["attack_recall_min"] for mode in MODES),
        "benign_recall_min": min(mode_metrics[mode]["benign_recall_min"] for mode in MODES),
        "auprc_min": min(mode_metrics[mode]["auprc_min"] for mode in MODES),
        "ece_max": max(mode_metrics[mode]["ece_max"] for mode in MODES),
        "ground_truth_event_recall_min": min(mode_metrics[mode]["ground_truth_event_recall_min"] for mode in MODES),
        "key_flow_coverage_min": min(mode_metrics[mode]["key_flow_coverage_min"] for mode in MODES),
        "budget_overrun_count_max": max(mode_metrics[mode]["budget_overrun_count_max"] for mode in MODES),
        "budget_us_max": max(mode_metrics[mode]["budget_us_max"] for mode in MODES),
    }


def _hard_constraint_violations(
    metrics: Mapping[str, object], constraints: Mapping[str, object]
) -> List[str]:
    rules = {
        "min_macro_f1_min": ("macro_f1_min", "min"),
        "min_attack_recall_min": ("attack_recall_min", "min"),
        "min_benign_recall_min": ("benign_recall_min", "min"),
        "min_auprc_min": ("auprc_min", "min"),
        "min_ground_truth_event_recall_min": (
            "ground_truth_event_recall_min",
            "min",
        ),
        "min_key_flow_coverage_min": ("key_flow_coverage_min", "min"),
        "max_ece_max": ("ece_max", "max"),
        "max_budget_overrun_count_max": ("budget_overrun_count_max", "max"),
        "max_budget_us": ("budget_us_max", "max"),
    }
    if set(constraints) != set(rules):
        raise CampaignValidationError("algorithm-search hard-constraint set is not exact")
    violations = []
    for constraint_name, (metric_name, direction) in rules.items():
        observed = _finite(metrics.get(metric_name), "hard-gate metric {}".format(metric_name))
        boundary = _finite(constraints.get(constraint_name), "hard constraint {}".format(constraint_name))
        if (direction == "min" and observed < boundary) or (
            direction == "max" and observed > boundary
        ):
            violations.append(constraint_name)
    return violations


def _referenced_input_paths(manifest_paths: Sequence[Path]) -> Set[str]:
    paths: Set[str] = set()
    for manifest_path in manifest_paths:
        absolute_manifest = _assert_no_symlink_components(
            manifest_path, "input source manifest"
        )
        if not absolute_manifest.is_file():
            raise CampaignValidationError("input source manifest is not a file")
        paths.add(str(absolute_manifest))
        manifest = _mapping(
            load_strict_json(absolute_manifest), "input source manifest"
        )
        ground_truth = manifest.get("ground_truth_csv")
        if ground_truth is not None:
            value = _clean_absolute_path(
                ground_truth, "input source manifest.ground_truth_csv"
            )
            paths.add(
                str(
                    _assert_no_symlink_components(
                        Path(value), "input ground-truth file"
                    )
                )
            )
        for raw_sample in _list(
            manifest.get("samples"), "input source manifest.samples"
        ):
            sample = _mapping(raw_sample, "input source manifest.sample")
            value = _clean_absolute_path(
                sample.get("path"), "input source manifest.sample.path"
            )
            paths.add(
                str(
                    _assert_no_symlink_components(
                        Path(value), "input sample file"
                    )
                )
            )
    for value in paths:
        if not Path(value).is_file():
            raise CampaignValidationError("referenced campaign input is not a file")
    return paths


def _validate_input_manifest(
    path: Path,
    verify_referenced_files: bool = False,
    expected_paths: Optional[Set[str]] = None,
) -> Dict[str, object]:
    manifest_bytes = _stable_file_bytes(path, "input hash manifest")
    payload = _mapping(
        _strict_json_from_bytes(manifest_bytes, "input hash manifest"),
        "input_hash_manifest",
    )
    if payload.get("schema_version") != 1 or payload.get("algorithm") != "sha256":
        raise CampaignValidationError("input hash manifest schema/algorithm is invalid")
    entries = _list(payload.get("entries"), "input_hash_manifest.entries")
    if payload.get("entry_count") != len(entries) or not entries:
        raise CampaignValidationError("input hash manifest entry_count is invalid")
    seen = set()
    for raw in entries:
        entry = _mapping(raw, "input_hash_manifest.entry")
        value = _clean_absolute_path(entry.get("path"), "input_hash_manifest.entry.path")
        if value in seen:
            raise CampaignValidationError("duplicate input hash manifest path")
        seen.add(value)
        _integer(entry.get("size_bytes"), "input_hash_manifest.entry.size_bytes", 0)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise CampaignValidationError("invalid input entry SHA-256")
        if verify_referenced_files:
            referenced = _assert_no_symlink_components(
                Path(value), "input manifest referenced file"
            )
            actual_digest, actual_size = _stable_file_hash_size(
                referenced, "input manifest referenced file"
            )
            if actual_size != entry["size_bytes"]:
                raise CampaignValidationError(
                    "input manifest referenced size drift: {}".format(value)
                )
            if actual_digest != digest:
                raise CampaignValidationError(
                    "input manifest referenced hash drift: {}".format(value)
                )
    if expected_paths is not None and seen != set(expected_paths):
        missing = sorted(set(expected_paths) - seen)
        extra = sorted(seen - set(expected_paths))
        raise CampaignValidationError(
            "input hash manifest path set is not exact; missing={}, extra={}".format(
                missing, extra
            )
        )
    return {
        "path": str(_absolute_lexical(path)),
        "sha256": sha256_bytes(manifest_bytes),
        "entry_count": len(entries),
    }


def _validate_environment_files_manifest(path: Path) -> Dict[str, object]:
    raw_bytes = _stable_file_bytes(path, "environment files manifest")
    payload = _mapping(
        _strict_json_from_bytes(raw_bytes, "environment files manifest"),
        "environment files manifest",
    )
    expected_top = {
        "schema_version", "scope", "environment_prefix", "root_identity",
        "entry_count", "regular_file_count", "symlink_count",
        "directory_count", "total_hashed_bytes", "entries",
    }
    if (
        set(payload) != expected_top
        or payload.get("schema_version") != 4
        or payload.get("scope")
        != "hft_mgbs_python_environment_tree_sha256_v4"
    ):
        raise CampaignValidationError("environment files manifest envelope is invalid")
    prefix = Path(
        _clean_absolute_path(
            payload.get("environment_prefix"),
            "environment files manifest.environment_prefix",
        )
    )
    prefix = _assert_no_symlink_components(prefix, "Conda environment prefix")
    if not prefix.is_dir():
        raise CampaignValidationError("Conda environment prefix is not a directory")

    identity_names = (
        "device", "inode", "mode", "link_count", "size_bytes", "mtime_ns", "ctime_ns",
    )

    def expected_identity(
        value: Mapping[str, object], label: str, field_prefix: str = ""
    ) -> Tuple[int, int, int, int, int, int, int]:
        return tuple(
            _integer(
                value.get(field_prefix + name),
                "{} {}{}".format(label, field_prefix, name),
                1 if name == "link_count" else 0,
            )
            for name in identity_names
        )  # type: ignore[return-value]

    def current_identity(value: os.stat_result) -> Tuple[int, int, int, int, int, int, int]:
        return (
            value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns,
        )

    root_identity = _mapping(
        payload.get("root_identity"), "environment files manifest.root_identity"
    )
    if set(root_identity) != set(identity_names):
        raise CampaignValidationError("environment root identity field set is not exact")
    root_status = os.lstat(str(prefix))
    if (
        current_identity(root_status)
        != expected_identity(root_identity, "environment root identity")
        or not stat.S_ISDIR(root_status.st_mode)
        or stat.S_ISLNK(root_status.st_mode)
    ):
        raise CampaignValidationError("Conda environment root identity drift")

    current_paths: List[Path] = []

    def walk_error(error: OSError) -> None:
        raise error

    for current_root, directory_names, file_names in os.walk(
        str(prefix), topdown=True, onerror=walk_error, followlinks=False
    ):
        directory_names.sort()
        file_names.sort()
        retained = []
        for name in directory_names:
            target = Path(current_root) / name
            current_paths.append(target)
            if not stat.S_ISLNK(os.lstat(str(target)).st_mode):
                retained.append(name)
        directory_names[:] = retained
        current_paths.extend(Path(current_root) / name for name in file_names)
    current_paths.sort(key=lambda item: item.relative_to(prefix).as_posix())
    current_relatives = [item.relative_to(prefix).as_posix() for item in current_paths]

    entries = _list(payload.get("entries"), "environment files manifest.entries")
    if _integer(payload.get("entry_count"), "environment files manifest.entry_count", 1) != len(entries):
        raise CampaignValidationError("environment files manifest entry count drift")
    observed_order: List[str] = []
    regular_count = symlink_count = directory_count = total_hashed_bytes = 0
    for raw_entry in entries:
        entry = _mapping(raw_entry, "environment files manifest entry")
        relative = _clean_relative_path(entry.get("path"), "environment tree path")
        if relative in observed_order:
            raise CampaignValidationError("duplicate environment tree path")
        base_fields = {
            "path", "type", "device", "inode", "mode", "link_count",
            "size_bytes", "mtime_ns", "ctime_ns",
        }
        entry_type = entry.get("type")
        if entry_type == "regular":
            expected_fields = base_fields | {"sha256"}
        elif entry_type == "directory":
            expected_fields = base_fields
        elif entry_type == "symlink":
            expected_fields = base_fields | {
                "link_target", "resolved_path", "resolved_type", "resolved_mode",
                "resolved_device", "resolved_inode", "resolved_link_count", "resolved_size_bytes",
                "resolved_mtime_ns", "resolved_ctime_ns",
            }
            if entry.get("resolved_type") == "regular":
                expected_fields.add("resolved_sha256")
        else:
            raise CampaignValidationError("environment tree entry type is invalid")
        if set(entry) != expected_fields:
            raise CampaignValidationError("environment files manifest entry field set is not exact")
        target = _absolute_lexical(prefix / relative)
        try:
            target.relative_to(prefix)
        except ValueError as error:
            raise CampaignValidationError("environment tree path escapes prefix") from error
        current = os.lstat(str(target))
        if current_identity(current) != expected_identity(entry, "environment tree entry"):
            raise CampaignValidationError("Conda environment tree identity drift")
        if entry_type == "regular":
            if not stat.S_ISREG(current.st_mode):
                raise CampaignValidationError("Conda environment regular-file type drift")
            expected_hash = entry.get("sha256")
            actual_hash, actual_size = _stable_file_hash_size(
                target, "Conda environment tree regular file"
            )
            if (
                not isinstance(expected_hash, str)
                or not SHA256_RE.fullmatch(expected_hash)
                or actual_hash != expected_hash
                or actual_size != current.st_size
            ):
                raise CampaignValidationError("Conda environment tree file hash drift")
            regular_count += 1
            total_hashed_bytes += actual_size
        elif entry_type == "directory":
            if not stat.S_ISDIR(current.st_mode):
                raise CampaignValidationError("Conda environment directory type drift")
            directory_count += 1
        else:
            if not stat.S_ISLNK(current.st_mode):
                raise CampaignValidationError("Conda environment symlink type drift")
            link_target = entry.get("link_target")
            if (
                not isinstance(link_target, str)
                or not link_target
                or any(value in link_target for value in ("\x00", "\n", "\r"))
                or os.readlink(str(target)) != link_target
            ):
                raise CampaignValidationError("Conda environment symlink target drift")
            resolved = Path(os.path.realpath(str(target)))
            try:
                resolved_relative = resolved.relative_to(prefix).as_posix()
            except ValueError as error:
                raise CampaignValidationError("Conda environment symlink escapes prefix") from error
            if resolved_relative != entry.get("resolved_path"):
                raise CampaignValidationError("Conda environment symlink resolution drift")
            resolved_status = os.lstat(str(resolved))
            if expected_identity(entry, "resolved environment entry", "resolved_") != current_identity(
                resolved_status
            ):
                raise CampaignValidationError("resolved Conda symlink identity drift")
            if entry.get("resolved_type") == "regular":
                if not stat.S_ISREG(resolved_status.st_mode):
                    raise CampaignValidationError("resolved Conda symlink type drift")
                actual_hash, actual_size = _stable_file_hash_size(
                    resolved, "resolved Conda environment tree file"
                )
                if actual_hash != entry.get("resolved_sha256") or actual_size != resolved_status.st_size:
                    raise CampaignValidationError("resolved Conda symlink hash drift")
                total_hashed_bytes += actual_size
            elif entry.get("resolved_type") != "directory" or not stat.S_ISDIR(resolved_status.st_mode):
                raise CampaignValidationError("resolved Conda symlink type drift")
            symlink_count += 1
        observed_order.append(relative)
    if observed_order != current_relatives:
        raise CampaignValidationError("environment files manifest is not the exact prefix tree")
    expected_summaries = {
        "regular_file_count": regular_count,
        "symlink_count": symlink_count,
        "directory_count": directory_count,
        "total_hashed_bytes": total_hashed_bytes,
    }
    for name, expected in expected_summaries.items():
        if _integer(payload.get(name), "environment files manifest." + name, 0) != expected:
            raise CampaignValidationError("environment files manifest summary drift")
    return {
        "path": str(_absolute_lexical(path)),
        "sha256": sha256_bytes(raw_bytes),
        "entry_count": len(entries),
        "environment_prefix": str(prefix),
    }


def _validate_input_stat_manifest(
    path: Path, input_manifest: Mapping[str, object]
) -> Dict[str, object]:
    raw_bytes = _stable_file_bytes(path, "input stat identity manifest")
    payload = _mapping(
        _strict_json_from_bytes(raw_bytes, "input stat identity manifest"),
        "input stat identity manifest",
    )
    if set(payload) != {
        "schema_version", "scope", "input_manifest_sha256", "entry_count", "entries",
    } or payload.get("schema_version") != 1 or payload.get("scope") != "hft_mgbs_campaign_input_stat_identity_v1":
        raise CampaignValidationError("input stat identity envelope is invalid")
    if payload.get("input_manifest_sha256") != input_manifest["sha256"]:
        raise CampaignValidationError("input stat identity is not bound to input manifest")
    rows = _list(payload.get("entries"), "input stat identity entries")
    frozen = _mapping(load_strict_json(Path(str(input_manifest["path"]))), "input hash manifest")
    frozen_paths = [str(_mapping(item, "input hash entry")["path"]) for item in _list(frozen["entries"], "input entries")]
    if _integer(payload.get("entry_count"), "input stat entry count", 1) != len(rows) or len(rows) != len(frozen_paths):
        raise CampaignValidationError("input stat identity count drift")
    observed = []
    for raw_row in rows:
        row = _mapping(raw_row, "input stat identity entry")
        if set(row) != {
            "path", "device", "inode", "mode", "link_count", "size_bytes", "mtime_ns", "ctime_ns",
        }:
            raise CampaignValidationError("input stat identity field set is not exact")
        target = Path(_clean_absolute_path(row.get("path"), "input stat path"))
        status = os.lstat(str(target))
        expected = tuple(
            _integer(row.get(name), "input stat " + name, 0 if name != "link_count" else 1)
            for name in ("device", "inode", "mode", "link_count", "size_bytes", "mtime_ns", "ctime_ns")
        )
        if expected != (
            status.st_dev, status.st_ino, status.st_mode, status.st_nlink,
            status.st_size, status.st_mtime_ns, status.st_ctime_ns,
        ) or not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
            raise CampaignValidationError("input stat identity drift")
        observed.append(str(target))
    if observed != frozen_paths:
        raise CampaignValidationError("input stat identity path set/order drift")
    return {
        "path": str(_absolute_lexical(path)),
        "sha256": sha256_bytes(raw_bytes),
        "entry_count": len(rows),
    }


def _validate_external_tools_manifest(path: Path) -> Dict[str, object]:
    raw_bytes = _stable_file_bytes(path, "external tools manifest")
    payload = _mapping(
        _strict_json_from_bytes(raw_bytes, "external tools manifest"),
        "external tools manifest",
    )
    if set(payload) != {"schema_version", "scope", "entry_count", "entries"} or payload.get("schema_version") != 1 or payload.get("scope") != "hft_mgbs_algorithm_campaign_external_tools_v1":
        raise CampaignValidationError("external tools manifest envelope is invalid")
    required_names = {
        "bash", "cmp", "date", "dirname", "find", "flock", "id", "mkdir",
        "python3", "rm", "seq", "sha256sum", "stat", "truncate", "wc",
    }
    entries = _list(payload.get("entries"), "external tools manifest.entries")
    if _integer(payload.get("entry_count"), "external tools manifest.entry_count", 1) != len(entries):
        raise CampaignValidationError("external tools manifest entry count drift")
    names = []
    for raw_entry in entries:
        entry = _mapping(raw_entry, "external tool entry")
        if set(entry) != {"name", "invoked_path", "resolved_path", "sha256"}:
            raise CampaignValidationError("external tool entry field set is not exact")
        name = entry.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+", name):
            raise CampaignValidationError("external tool name is invalid")
        invoked = _clean_absolute_path(entry.get("invoked_path"), "external tool invoked path")
        resolved = Path(_clean_absolute_path(entry.get("resolved_path"), "external tool resolved path"))
        if os.path.normcase(os.path.realpath(invoked)) != os.path.normcase(
            os.path.realpath(str(resolved))
        ):
            raise CampaignValidationError("external tool resolution drift")
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest) or sha256_file(resolved) != digest:
            raise CampaignValidationError("external tool executable identity drift")
        names.append(name)
    if names != sorted(names) or set(names) != required_names:
        raise CampaignValidationError("external tools manifest set is not exact")
    return {
        "path": str(_absolute_lexical(path)),
        "sha256": sha256_bytes(raw_bytes),
        "entry_count": len(entries),
    }


def _validate_environment_identity(
    path: Path, execution: Mapping[str, object]
) -> Dict[str, object]:
    raw_bytes = _stable_file_bytes(path, "campaign environment identity")
    payload = _mapping(
        _strict_json_from_bytes(raw_bytes, "campaign environment identity"),
        "campaign environment identity",
    )
    expected_top = {
        "schema_version",
        "scope",
        "environment_prefix",
        "environment_files_manifest_path",
        "environment_files_manifest_sha256",
        "environment_files_manifest_entry_count",
        "external_tools_manifest_path",
        "external_tools_manifest_sha256",
        "external_tools_manifest_entry_count",
        "runtime_bootstrap_identity_path",
        "runtime_bootstrap_identity_sha256",
        "python",
        "packages",
        "thread_environment",
    }
    if set(payload) != expected_top:
        raise CampaignValidationError("environment identity field set is not exact")
    if (
        payload.get("schema_version") != 2
        or payload.get("scope")
        != "hft_mgbs_algorithm_campaign_environment_identity_v2"
    ):
        raise CampaignValidationError("environment identity contract drift")
    environment_files = _validate_environment_files_manifest(
        path.parent / "environment_files_sha256.json"
    )
    external_tools = _validate_external_tools_manifest(
        path.parent / "external_tools_sha256.json"
    )
    environment_prefix = _clean_absolute_path(
        payload.get("environment_prefix"),
        "environment_identity.environment_prefix",
    )
    if (
        environment_prefix != execution.get("environment_prefix")
        or environment_prefix != environment_files["environment_prefix"]
    ):
        raise CampaignValidationError("environment prefix identity drift")
    runtime_path = Path(
        _clean_absolute_path(
            payload.get("runtime_bootstrap_identity_path"),
            "environment_identity.runtime_bootstrap_identity_path",
        )
    )
    expected_runtime_path = _absolute_lexical(
        path.parent / "runtime_bootstrap_identity.json"
    )
    if _absolute_lexical(runtime_path) != expected_runtime_path:
        raise CampaignValidationError("runtime bootstrap identity is not campaign-local")
    runtime_raw = _stable_file_bytes(runtime_path, "runtime bootstrap identity")
    runtime_hash = payload.get("runtime_bootstrap_identity_sha256")
    if (
        not isinstance(runtime_hash, str)
        or not SHA256_RE.fullmatch(runtime_hash)
        or sha256_bytes(runtime_raw) != runtime_hash
    ):
        raise CampaignValidationError("runtime bootstrap identity hash drift")
    runtime = _mapping(
        _strict_json_from_bytes(runtime_raw, "runtime bootstrap identity"),
        "runtime bootstrap identity",
    )
    if set(runtime) != {
        "schema_version", "scope", "prefix", "executable",
        "executable_sha256", "site_packages",
    } or runtime.get("schema_version") != 1 or runtime.get("scope") != "hft_mgbs_stdlib_bound_python_runtime_v1":
        raise CampaignValidationError("runtime bootstrap identity envelope is invalid")
    if runtime.get("prefix") != environment_prefix:
        raise CampaignValidationError("runtime bootstrap prefix identity drift")
    runtime_sites = _list(runtime.get("site_packages"), "runtime site-packages")
    normalized_sites = []
    for raw_site in runtime_sites:
        site_path = Path(_clean_absolute_path(raw_site, "runtime site-packages path"))
        try:
            site_path.relative_to(Path(environment_prefix))
        except ValueError as error:
            raise CampaignValidationError("runtime site-packages escapes Conda prefix") from error
        if not site_path.is_dir() or str(site_path) in normalized_sites:
            raise CampaignValidationError("runtime site-packages identity is invalid")
        normalized_sites.append(str(site_path))
    if not normalized_sites:
        raise CampaignValidationError("runtime site-packages set is empty")
    bound_environment_fields = {
        "environment_files_manifest_path": environment_files["path"],
        "environment_files_manifest_sha256": environment_files["sha256"],
        "environment_files_manifest_entry_count": environment_files["entry_count"],
        "external_tools_manifest_path": external_tools["path"],
        "external_tools_manifest_sha256": external_tools["sha256"],
        "external_tools_manifest_entry_count": external_tools["entry_count"],
    }
    for name, expected in bound_environment_fields.items():
        if payload.get(name) != expected:
            raise CampaignValidationError("environment identity {} drift".format(name))

    python = _mapping(payload.get("python"), "environment_identity.python")
    if set(python) != {
        "version",
        "implementation",
        "executable",
        "executable_sha256",
        "site_packages",
    }:
        raise CampaignValidationError("environment Python identity field set is not exact")
    if (
        not isinstance(python.get("version"), str)
        or not str(python["version"]).startswith("3.9.")
        or python.get("implementation") != "CPython"
    ):
        raise CampaignValidationError("environment Python runtime is not frozen py3.9 CPython")
    python_path = Path(
        _clean_absolute_path(
            python.get("executable"), "environment_identity.python.executable"
        )
    )
    python_hash = python.get("executable_sha256")
    if (
        not isinstance(python_hash, str)
        or not SHA256_RE.fullmatch(python_hash)
        or sha256_file(python_path) != python_hash
    ):
        raise CampaignValidationError("live Python executable identity drift")
    if (
        runtime.get("executable") != str(python_path)
        or runtime.get("executable_sha256") != python_hash
        or python.get("site_packages") != normalized_sites
        or runtime_sites != normalized_sites
    ):
        raise CampaignValidationError("bound Python launcher runtime identity drift")
    try:
        python_path.relative_to(Path(environment_prefix))
    except ValueError as error:
        raise CampaignValidationError("Python executable escapes the frozen Conda prefix") from error
    if str(python_path) != execution.get("python_executable"):
        raise CampaignValidationError("environment Python executable contract drift")

    packages = _mapping(payload.get("packages"), "environment_identity.packages")
    if set(packages) != {"numpy", "scipy", "sklearn", "joblib"}:
        raise CampaignValidationError("environment package set is not exact")
    for name in sorted(packages):
        package = _mapping(packages[name], "environment package {}".format(name))
        if set(package) != {"version", "module_file", "module_file_sha256"}:
            raise CampaignValidationError("environment package field set is not exact")
        if not isinstance(package.get("version"), str) or not package["version"]:
            raise CampaignValidationError("environment package version is invalid")
        module_path = Path(
            _clean_absolute_path(
                package.get("module_file"),
                "environment package {} module file".format(name),
            )
        )
        module_hash = package.get("module_file_sha256")
        if (
            not isinstance(module_hash, str)
            or not SHA256_RE.fullmatch(module_hash)
            or sha256_file(module_path) != module_hash
        ):
            raise CampaignValidationError(
                "live environment package identity drift: {}".format(name)
            )
    thread_environment = _mapping(
        payload.get("thread_environment"), "environment_identity.thread_environment"
    )
    thread_names = {
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "BLIS_NUM_THREADS",
        "JOBLIB_TEMP_FOLDER",
        "PYTHONHASHSEED",
        "CUDA_VISIBLE_DEVICES",
    }
    if set(thread_environment) != thread_names or any(
        value is not None
        and (
            not isinstance(value, str)
            or any(character in value for character in "\r\n\x00")
        )
        for value in thread_environment.values()
    ):
        raise CampaignValidationError("thread environment identity is invalid")
    return {
        "path": str(_absolute_lexical(path)),
        "sha256": sha256_bytes(raw_bytes),
        "environment_prefix": environment_prefix,
        "environment_files_manifest": environment_files,
        "external_tools_manifest": external_tools,
        "runtime_bootstrap_identity": {
            "path": str(expected_runtime_path),
            "sha256": runtime_hash,
        },
        "python_version": python["version"],
        "package_versions": {
            name: _mapping(packages[name], "environment package")["version"]
            for name in sorted(packages)
        },
    }


def _validate_code_manifest(
    path: Path,
    code_root: Path,
    artifacts: Mapping[str, Mapping[str, object]],
) -> str:
    raw_bytes = _stable_file_bytes(path, "code SHA-256 manifest")
    manifest = _parse_sha256_manifest_bytes(raw_bytes, str(path))
    normalized: Dict[str, str] = {}
    for name, digest in manifest.items():
        value = name.replace("\\", "/")
        if value.startswith("./"):
            value = value[2:]
        value = _clean_relative_path(value, "code SHA-256 manifest path")
        if value in normalized:
            raise CampaignValidationError(
                "code SHA-256 manifest contains a normalized path collision"
            )
        normalized[value] = digest
    expected = {
        str(artifact["path"]): str(artifact["sha256"])
        for artifact in artifacts.values()
    }
    if normalized != expected:
        raise CampaignValidationError("code manifest path set is not exact")
    for artifact in artifacts.values():
        relative = str(artifact["path"])
        if normalized.get(relative) != artifact["sha256"]:
            raise CampaignValidationError("code manifest does not bind {}".format(relative))
        if sha256_file(_repo_file(code_root, relative)) != artifact["sha256"]:
            raise CampaignValidationError("live code artifact drift: {}".format(relative))
    return sha256_bytes(raw_bytes)


def _validate_result_manifest(
    path: Path, result_hashes: Mapping[str, str]
) -> str:
    raw_bytes = _stable_file_bytes(path, "result SHA-256 manifest")
    manifest = _parse_sha256_manifest_bytes(raw_bytes, str(path))
    normalized: Dict[str, str] = {}
    for name, digest in manifest.items():
        clean = _clean_absolute_path(name, "result SHA-256 manifest path")
        normalized_name = str(_absolute_lexical(Path(clean)))
        if normalized_name in normalized:
            raise CampaignValidationError(
                "result SHA-256 manifest contains a normalized path collision"
            )
        normalized[normalized_name] = digest
    expected = {
        str(_absolute_lexical(Path(name))): digest
        for name, digest in result_hashes.items()
    }
    if normalized != expected:
        raise CampaignValidationError("result_sha256.txt does not exactly bind result files")
    return sha256_bytes(raw_bytes)


def _validate_raw_payload(
    payload: Mapping[str, object],
    job: Mapping[str, object],
    mode: str,
    seed: int,
    common_input_hash: str,
    common_input_count: int,
    common_input_path: Optional[str] = None,
) -> Dict[str, object]:
    if payload.get("schema_version") != 1:
        raise CampaignValidationError("raw result schema_version is invalid")
    if payload.get("scope") != "independent_cross_dataset_holdout":
        raise CampaignValidationError("raw result scope is invalid")
    if payload.get("final_quality_eligible") is not False:
        raise CampaignValidationError("raw result crosses the quality boundary")
    expected_env = _mapping(job.get("runner_environment"), "job.runner_environment")
    candidate = _mapping(payload.get("candidate"), "raw.candidate")
    if set(candidate) != {
        "mode",
        "batch_size",
        "budget_us",
        "execution_budget_safety_ratio",
    }:
        raise CampaignValidationError("raw candidate field set is not exact")
    if candidate.get("mode") != mode:
        raise CampaignValidationError("raw candidate mode does not match filename")
    for field, expected in (
        ("batch_size", int(str(expected_env["BATCH_SIZE"]))),
        ("budget_us", int(str(expected_env["BUDGET_US"]))),
    ):
        if _integer(candidate.get(field), "raw.candidate.{}".format(field), 1) != expected:
            raise CampaignValidationError("raw candidate {} drift".format(field))
    if not _same_number(candidate.get("execution_budget_safety_ratio"), float(str(expected_env["SAFETY_RATIO"]))):
        raise CampaignValidationError("raw candidate safety ratio drift")
    _unit_interval(
        candidate.get("execution_budget_safety_ratio"),
        "raw.candidate.execution_budget_safety_ratio",
    )
    protocol = _mapping(payload.get("protocol"), "raw.protocol")
    expected_protocol_fields = {
        "training_dataset",
        "holdout_dataset",
        "dataset_overlap",
        "holdout_label_alignment",
        "alignment_tolerance_s",
        "max_train_packets_per_capture",
        "max_train_flows_per_capture",
        "max_test_packets_per_capture",
        "max_test_flows_per_capture",
        "estimators",
        "n_jobs",
        "key_flow_ratio",
        "max_payload_bytes",
        "seeds",
        "threshold_policy",
        "calibration_used_for_threshold",
        "calibration_attack_recall_floor",
        "feature_profile",
        "classifier",
        "calibration_groups",
        "adaptation_policy",
        "adaptation_groups",
        "adaptation_weight_multiplier",
        "evaluation_groups",
    }
    if set(protocol) != expected_protocol_fields:
        raise CampaignValidationError("raw protocol field set is not exact")
    if protocol.get("seeds") != [seed]:
        raise CampaignValidationError("raw repeat seed does not match the frozen schedule")
    scalar_expected = {
        "training_dataset": "USTC-TFC2016",
        "holdout_dataset": "UNSW-NB15",
        "dataset_overlap": (
            "no_capture_overlap_between_fit_calibration_evaluation"
            if str(expected_env["ADAPTATION_GROUPS"])
            else "none"
        ),
        "holdout_label_alignment": (
            "bidirectional_5tuple_and_flow_attack_time_overlap"
        ),
        "feature_profile": expected_env["FEATURE_PROFILE"],
        "classifier": expected_env["CLASSIFIER"],
        "threshold_policy": expected_env["THRESHOLD_POLICY"],
        "adaptation_policy": expected_env["ADAPTATION_POLICY"],
    }
    for name, expected in scalar_expected.items():
        if protocol.get(name) != expected:
            raise CampaignValidationError("raw protocol {} drift".format(name))
    if protocol.get("calibration_used_for_threshold") is not (
        str(expected_env["THRESHOLD_POLICY"]) == "calibration_macro_f1"
    ):
        raise CampaignValidationError("raw protocol threshold-use flag drift")
    integer_execution_fields = {
        "max_train_packets_per_capture": "MAX_TRAIN_PACKETS_PER_CAPTURE",
        "max_train_flows_per_capture": "MAX_TRAIN_FLOWS_PER_CAPTURE",
        "max_test_packets_per_capture": "MAX_TEST_PACKETS_PER_CAPTURE",
        "max_test_flows_per_capture": "MAX_TEST_FLOWS_PER_CAPTURE",
        "estimators": "ESTIMATORS",
        "n_jobs": "N_JOBS",
        "max_payload_bytes": "MAX_PAYLOAD_BYTES",
    }
    for name, env_name in integer_execution_fields.items():
        observed = _integer(protocol.get(name), "raw.protocol.{}".format(name), 1)
        if observed != int(str(expected_env[env_name])):
            raise CampaignValidationError("raw protocol {} drift".format(name))
    for name, env_name in (
        ("key_flow_ratio", "KEY_FLOW_RATIO"),
        ("alignment_tolerance_s", "ALIGNMENT_TOLERANCE_S"),
    ):
        if not _same_number(protocol.get(name), float(str(expected_env[env_name]))):
            raise CampaignValidationError("raw protocol {} drift".format(name))
    _unit_interval(protocol.get("key_flow_ratio"), "raw.protocol.key_flow_ratio")
    tolerance = _finite(
        protocol.get("alignment_tolerance_s"),
        "raw.protocol.alignment_tolerance_s",
    )
    if tolerance < 0.0:
        raise CampaignValidationError("raw alignment tolerance must be non-negative")
    for name, env_name in (
        ("calibration_attack_recall_floor", "CALIBRATION_ATTACK_RECALL_FLOOR"),
        ("adaptation_weight_multiplier", "ADAPTATION_WEIGHT_MULTIPLIER"),
    ):
        if not _same_number(protocol.get(name), float(str(expected_env[env_name]))):
            raise CampaignValidationError("raw protocol {} drift".format(name))
    for name, env_name in (
        ("calibration_groups", "CALIBRATION_GROUPS"),
        ("adaptation_groups", "ADAPTATION_GROUPS"),
    ):
        expected_groups = sorted(filter(None, str(expected_env[env_name]).split(",")))
        if protocol.get(name) != expected_groups:
            raise CampaignValidationError("raw protocol {} drift".format(name))
    if protocol.get("evaluation_groups") != job.get("expected_fresh_evaluation_groups"):
        raise CampaignValidationError("raw evaluation groups are not the fresh frozen groups")
    capture_counts = _mapping(payload.get("capture_counts"), "raw.capture_counts")
    expected_capture_counts = _mapping(
        job.get("expected_capture_counts"), "job.expected_capture_counts"
    )
    observed_capture_counts = {
        name: _integer(
            capture_counts.get(name), "raw.capture_counts.{}".format(name), 0
        )
        for name in ("training", "calibration", "adaptation", "holdout")
    }
    if set(capture_counts) != set(observed_capture_counts):
        raise CampaignValidationError("raw capture count field set is not exact")
    if observed_capture_counts != dict(expected_capture_counts):
        raise CampaignValidationError("raw capture counts drift from frozen roles")
    expected_top_fields = {
        "schema_version",
        "scope",
        "candidate",
        "protocol",
        "ground_truth",
        "input_hash_evidence",
        "capture_counts",
        "ground_truth_event_recall_audit",
        "quality",
        "final_quality_eligible",
        "missing_final_evidence",
    }
    for role, count in observed_capture_counts.items():
        if count:
            expected_top_fields.update(
                {"{}_captures".format(role), "{}_constraint_audit".format(role)}
            )
    if set(payload) != expected_top_fields:
        raise CampaignValidationError("raw result top-level field set is not exact")
    if payload.get("missing_final_evidence") != ["frozen_min_primary_metric"]:
        raise CampaignValidationError("raw missing-final-evidence boundary drift")
    evidence = _mapping(payload.get("input_hash_evidence"), "raw.input_hash_evidence")
    if set(evidence) != {
        "path",
        "sha256",
        "entry_count",
        "required_path_count",
        "all_required_paths_frozen",
    }:
        raise CampaignValidationError("raw input hash evidence field set is not exact")
    if (
        evidence.get("sha256") != common_input_hash
        or evidence.get("all_required_paths_frozen") is not True
        or not isinstance(evidence.get("path"), str)
    ):
        raise CampaignValidationError("raw input hash evidence is not bound")
    if (
        _integer(
            evidence.get("entry_count"), "raw.input_hash_evidence.entry_count", 1
        )
        != common_input_count
        or _integer(
            evidence.get("required_path_count"),
            "raw.input_hash_evidence.required_path_count",
            1,
        )
        != common_input_count
    ):
        raise CampaignValidationError("raw input hash evidence path count drift")
    if common_input_path is not None and str(evidence.get("path")) != common_input_path:
        raise CampaignValidationError("raw input hash evidence path drift")

    # The execution safety ratio is a soft admission limit for ordinary and
    # deep work.  Key-flow work is intentionally allowed to consume the full
    # configured hard budget, and the pipeline records an overrun only when
    # measured optional cost exceeds that configured budget.  Validate the
    # evidence against the same hard-budget boundary used by the producer.
    no_overrun_cost_limit = float(str(expected_env["BUDGET_US"]))
    expected_roles = _mapping(
        job.get("expected_capture_roles"), "job.expected_capture_roles"
    )
    role_evidence: Dict[str, Dict[str, object]] = {}
    for role in ("training", "calibration", "adaptation", "holdout"):
        role_evidence[role] = _validate_capture_role(
            payload,
            role,
            _list(expected_roles.get(role), "expected {} captures".format(role)),
            int(
                str(
                    expected_env[
                        "MAX_TRAIN_PACKETS_PER_CAPTURE"
                        if role == "training"
                        else "MAX_TEST_PACKETS_PER_CAPTURE"
                    ]
                )
            ),
            int(
                str(
                    expected_env[
                        "MAX_TRAIN_FLOWS_PER_CAPTURE"
                        if role == "training"
                        else "MAX_TEST_FLOWS_PER_CAPTURE"
                    ]
                )
            ),
            float(str(expected_env["SAFETY_RATIO"])),
            no_overrun_cost_limit,
        )
        audit_name = "{}_constraint_audit".format(role)
        expected_audit = role_evidence[role]["audit"]
        if expected_audit is None:
            if audit_name in payload:
                raise CampaignValidationError("unexpected {}".format(audit_name))
        else:
            observed_audit = _validate_constraint_audit(
                payload.get(audit_name), audit_name, no_overrun_cost_limit
            )
            if any(
                not _same_number(observed_audit.get(name), expected_audit[name])
                for name in expected_audit
            ):
                raise CampaignValidationError("{} does not match capture rows".format(audit_name))
    event_audit = _mapping(
        payload.get("ground_truth_event_recall_audit"),
        "raw.ground_truth_event_recall_audit",
    )
    if set(event_audit) != {
        "scope",
        "eligible_event_count",
        "matched_event_count",
        "event_recall",
        "computed_before_flow_sampling",
        "eligible_event_ids_by_group",
        "matched_event_ids_by_group",
        "eligible_event_ids_sha256",
        "matched_event_ids_sha256",
        "matched_event_witnesses",
    }:
        raise CampaignValidationError("ground-truth event audit field set is not exact")
    if (
        event_audit.get("scope")
        != "indexed_tcp_udp_events_overlapping_processed_packet_time"
        or event_audit.get("computed_before_flow_sampling") is not True
    ):
        raise CampaignValidationError("ground-truth event denominator semantics drift")
    eligible = _integer(
        event_audit.get("eligible_event_count"),
        "ground_truth_event_recall_audit.eligible_event_count",
        1,
    )
    matched = _integer(
        event_audit.get("matched_event_count"),
        "ground_truth_event_recall_audit.matched_event_count",
        0,
    )
    expected_evaluation_groups = list(job.get("expected_fresh_evaluation_groups") or [])
    eligible_by_group = _mapping(
        event_audit.get("eligible_event_ids_by_group"),
        "ground_truth_event_recall_audit.eligible_event_ids_by_group",
    )
    matched_by_group = _mapping(
        event_audit.get("matched_event_ids_by_group"),
        "ground_truth_event_recall_audit.matched_event_ids_by_group",
    )
    if set(eligible_by_group) != set(expected_evaluation_groups) or set(matched_by_group) != set(expected_evaluation_groups):
        raise CampaignValidationError("ground-truth event group set drift")
    ground_truth_path = Path(
        _clean_absolute_path(
            job.get("expected_ground_truth_csv"), "job.expected_ground_truth_csv"
        )
    )
    truth = UnswGroundTruth.from_csv(ground_truth_path)
    recomputed_eligible_by_group = {
        group: set() for group in expected_evaluation_groups
    }
    for bounds in role_evidence["holdout"]["capture_time_bounds"]:
        start = bounds["packet_start_timestamp"]
        end = bounds["packet_last_timestamp"]
        if start is not None:
            recomputed_eligible_by_group[bounds["group"]].update(
                truth.event_ids_overlapping(start, end, tolerance_s=tolerance)
            )
    eligible_union: Set[int] = set()
    matched_union: Set[int] = set()
    for group in expected_evaluation_groups:
        eligible_values = _list(eligible_by_group[group], "eligible event IDs")
        matched_values = _list(matched_by_group[group], "matched event IDs")
        clean_eligible = [_integer(value, "eligible event ID", 0) for value in eligible_values]
        clean_matched = [_integer(value, "matched event ID", 0) for value in matched_values]
        if clean_eligible != sorted(set(clean_eligible)) or clean_matched != sorted(set(clean_matched)):
            raise CampaignValidationError("ground-truth event IDs are not unique and sorted")
        if not set(clean_matched).issubset(set(clean_eligible)):
            raise CampaignValidationError("matched event IDs are not eligible")
        if clean_eligible != sorted(recomputed_eligible_by_group[group]):
            raise CampaignValidationError(
                "eligible event IDs do not replay from frozen ground truth"
            )
        eligible_union.update(clean_eligible)
        matched_union.update(clean_matched)
    witnesses = _list(
        event_audit.get("matched_event_witnesses"),
        "ground_truth_event_recall_audit.matched_event_witnesses",
    )
    expected_witness_pairs = {
        (group, event_id)
        for group in expected_evaluation_groups
        for event_id in matched_by_group[group]
    }
    observed_witness_pairs = []
    for raw_witness in witnesses:
        witness = _mapping(raw_witness, "matched event witness")
        if set(witness) != {
            "event_id", "group", "normalized_forward_key",
            "start_timestamp_hex", "last_timestamp_hex",
        }:
            raise CampaignValidationError("matched event witness field set is not exact")
        group = witness.get("group")
        event_id = _integer(witness.get("event_id"), "witness event ID", 0)
        raw_key = _list(witness.get("normalized_forward_key"), "witness flow key")
        if len(raw_key) != 5 or not all(isinstance(value, str) for value in raw_key[:2]):
            raise CampaignValidationError("matched event witness flow key is invalid")
        key = (
            raw_key[0], raw_key[1],
            _integer(raw_key[2], "witness source port", 0),
            _integer(raw_key[3], "witness destination port", 0),
            _integer(raw_key[4], "witness protocol", 0),
        )
        # Historical raw receipts named this field ``normalized_forward_key``
        # but preserved the observed packet direction.  Direction is not a
        # trust claim: normalize the fully typed five-tuple here, then require
        # the event ID to replay against the frozen ground truth below.
        key = MultiGranularityExtractor.normalize_flow_key(key)
        try:
            start = float.fromhex(witness.get("start_timestamp_hex"))
            end = float.fromhex(witness.get("last_timestamp_hex"))
        except (TypeError, ValueError) as error:
            raise CampaignValidationError("matched event witness timestamp is invalid") from error
        if not math.isfinite(start) or not math.isfinite(end) or end < start:
            raise CampaignValidationError("matched event witness timestamp is invalid")
        if group not in expected_evaluation_groups:
            raise CampaignValidationError("matched event witness group is invalid")
        replayed_ids = {
            interval.event_id
            for interval in truth.matching_intervals(key, start, end, tolerance_s=tolerance)
        }
        if event_id not in replayed_ids:
            raise CampaignValidationError("matched event witness does not replay")
        observed_witness_pairs.append((group, event_id))
    if observed_witness_pairs != sorted(set(observed_witness_pairs)) or set(observed_witness_pairs) != expected_witness_pairs:
        raise CampaignValidationError("matched event witness set is not exact")
    if len(eligible_union) != eligible or len(matched_union) != matched:
        raise CampaignValidationError("ground-truth event counts do not match addressable IDs")
    for name, mapping_value in (
        ("eligible", eligible_by_group),
        ("matched", matched_by_group),
    ):
        observed_hash = event_audit.get("{}_event_ids_sha256".format(name))
        expected_hash = sha256_bytes(
            json.dumps(
                mapping_value,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
        if observed_hash != expected_hash:
            raise CampaignValidationError("ground-truth {} event fingerprint drift".format(name))
    if matched > eligible:
        raise CampaignValidationError("matched event count exceeds eligible count")
    recall = _unit_interval(
        event_audit.get("event_recall"),
        "ground_truth_event_recall_audit.event_recall",
    )
    if not _same_number(recall, matched / eligible):
        raise CampaignValidationError("event recall does not match matched/eligible")
    ground_truth = _mapping(payload.get("ground_truth"), "raw.ground_truth")
    ground_truth_fields = {
        "rows_total",
        "rows_indexed",
        "rows_unsupported_protocol",
        "rows_invalid_endpoint",
        "rows_invalid_time",
        "indexed_key_count",
    }
    if set(ground_truth) != ground_truth_fields:
        raise CampaignValidationError("ground-truth parse field set is not exact")
    gt = {
        name: _integer(ground_truth.get(name), "ground_truth.{}".format(name), 0)
        for name in ground_truth_fields
    }
    if gt["rows_total"] != (
        gt["rows_indexed"]
        + gt["rows_unsupported_protocol"]
        + gt["rows_invalid_endpoint"]
        + gt["rows_invalid_time"]
    ) or gt["indexed_key_count"] > gt["rows_indexed"]:
        raise CampaignValidationError("ground-truth parse accounting is inconsistent")
    replayed_ground_truth = dict(truth.parse_stats)
    replayed_ground_truth["indexed_key_count"] = truth.indexed_key_count
    if gt != replayed_ground_truth:
        raise CampaignValidationError("ground-truth parse evidence does not replay")
    quality = _validate_quality_payload(
        payload.get("quality"),
        seed,
        expected_env,
        list(job.get("expected_fresh_evaluation_groups") or []),
        expected_capture_counts,
    )
    role_quality_counts = {
        "training": "train_flow_count",
        "calibration": "calibration_flow_count",
        "adaptation": "adaptation_flow_count",
        "holdout": "test_flow_count",
    }
    for role, quality_name in role_quality_counts.items():
        if _integer(quality.get(quality_name), "quality.{}".format(quality_name), 0) != role_evidence[role]["flow_count"]:
            raise CampaignValidationError("quality flow count does not match {} captures".format(role))
    if (
        _integer(quality.get("test_attack_count"), "quality.test_attack_count", 1)
        != role_evidence["holdout"]["attack_flow_count"]
        or _integer(quality.get("test_benign_count"), "quality.test_benign_count", 1)
        != role_evidence["holdout"]["benign_flow_count"]
    ):
        raise CampaignValidationError("quality label counts do not match holdout captures")
    if _integer(quality.get("test_attack_count"), "quality.test_attack_count", 1) > 0 and matched < 1:
        raise CampaignValidationError("positive evaluation labels require a matched ground-truth event")
    return {
        "role_flow_counts": {
            role: role_evidence[role]["flow_count"]
            for role in ("training", "calibration", "adaptation", "holdout")
        },
        "role_audits": {
            role: role_evidence[role]["audit"]
            for role in ("training", "calibration", "adaptation", "holdout")
        },
        "role_fingerprints": {
            role: role_evidence[role]["fingerprints"]
            for role in ("training", "calibration", "adaptation", "holdout")
        },
        "role_label_fingerprints": {
            role: role_evidence[role]["label_fingerprints"]
            for role in ("training", "calibration", "adaptation", "holdout")
        },
        "fresh_evaluation_identity": {
            "eligible_event_ids_by_group": {
                group: list(eligible_by_group[group])
                for group in expected_evaluation_groups
            },
            "matched_event_ids_by_group": {
                group: list(matched_by_group[group])
                for group in expected_evaluation_groups
            },
            "test_flow_count": quality["test_flow_count"],
            "test_attack_count": quality["test_attack_count"],
            "test_benign_count": quality["test_benign_count"],
            "selected_flow_fingerprints": role_evidence["holdout"]["fingerprints"],
            "selected_flow_label_fingerprints": role_evidence["holdout"]["label_fingerprints"],
            "evaluation_labels_sha256": sha256_bytes(
                json.dumps(
                    _mapping(payload.get("quality"), "quality")["seeds"][0]["evaluation_labels"],
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode("utf-8")
            ),
        },
    }


def _stable_extraction_identity(
    identity: Mapping[str, object],
) -> Dict[str, object]:
    """Return the seed-independent sample identity from validated raw evidence.

    Resource audits contain measured runtime costs and scheduler tier counts.
    Those observations remain hard-gated per repeat, but they are not an
    extraction identity and are expected to vary across seeds and candidates.
    """

    return {
        "role_flow_counts": copy.deepcopy(
            _mapping(identity.get("role_flow_counts"), "role flow counts")
        ),
        "role_fingerprints": copy.deepcopy(
            _mapping(identity.get("role_fingerprints"), "role fingerprints")
        ),
        "role_label_fingerprints": copy.deepcopy(
            _mapping(
                identity.get("role_label_fingerprints"),
                "role label fingerprints",
            )
        ),
        "fresh_evaluation_identity": copy.deepcopy(
            _mapping(
                identity.get("fresh_evaluation_identity"),
                "fresh evaluation identity",
            )
        ),
    }


def _validate_summary(
    summary: Mapping[str, object],
    mode_metrics: Mapping[str, Mapping[str, float]],
    repeats: int,
    payloads_by_mode: Mapping[str, Sequence[Mapping[str, object]]],
    job: Mapping[str, object],
    input_hash: str,
    hard_constraints: Mapping[str, object],
) -> None:
    if set(summary) != {
        "schema_version",
        "scope",
        "aggregation_policy",
        "minimum_repeats",
        "candidate_count",
        "feasible_candidate_count",
        "rejected_files",
        "candidates",
        "final_quality_eligible",
    }:
        raise CampaignValidationError("summary top-level field set is not exact")
    if (
        summary.get("schema_version") != 2
        or summary.get("scope") != "independent_cross_dataset_holdout_summary"
        or summary.get("aggregation_policy")
        != "worst_case_across_full_extraction_repeats"
        or _integer(summary.get("minimum_repeats"), "summary.minimum_repeats", 1)
        != repeats
        or _integer(summary.get("candidate_count"), "summary.candidate_count", 0)
        != len(MODES)
        or summary.get("rejected_files") != []
        or summary.get("final_quality_eligible") is not False
    ):
        raise CampaignValidationError("summary campaign envelope drift")
    candidates = _list(summary.get("candidates"), "summary.candidates")
    by_mode: Dict[str, Mapping[str, object]] = {}
    for raw in candidates:
        item = _mapping(raw, "summary.candidate")
        mode = item.get("mode")
        if mode not in MODES or mode in by_mode:
            raise CampaignValidationError("summary has invalid/duplicate mode")
        by_mode[str(mode)] = item
    if set(by_mode) != set(MODES):
        raise CampaignValidationError("summary does not contain paired modes")
    feasible = 0
    env = _mapping(job.get("runner_environment"), "job.runner_environment")
    expected_policy = {
        "feature_profile": env["FEATURE_PROFILE"],
        "classifier": env["CLASSIFIER"],
        "threshold_policy": env["THRESHOLD_POLICY"],
        "calibration_attack_recall_floor": float(str(env["CALIBRATION_ATTACK_RECALL_FLOOR"])),
        "calibration_groups": sorted(filter(None, str(env["CALIBRATION_GROUPS"]).split(","))),
        "evaluation_groups": list(job.get("expected_fresh_evaluation_groups") or []),
        "adaptation_policy": env["ADAPTATION_POLICY"],
        "adaptation_groups": sorted(filter(None, str(env["ADAPTATION_GROUPS"]).split(","))),
        "adaptation_weight_multiplier": float(str(env["ADAPTATION_WEIGHT_MULTIPLIER"])),
    }
    expected_candidate_fields = {
        "mode",
        "repeat_ids",
        "repeat_count",
        "repeat_gate_passed",
        "batch_size",
        "budget_us",
        "execution_budget_safety_ratio",
        "budget_overrun_count_max",
        "key_flow_coverage_min",
        "ground_truth_event_recall_min",
        "input_hash_manifest_sha256",
        "decision_policy",
        "hard_constraint_violations",
        "hard_constraints_passed",
        "train_flow_count_min",
        "test_flow_count_min",
        "macro_f1_min",
        "balanced_accuracy_min",
        "auroc_min",
        "auprc_min",
        "benign_recall_min",
        "attack_recall_min",
        "ece_max",
        "final_quality_eligible",
        "missing_final_evidence",
    }
    for mode in MODES:
        item = by_mode[mode]
        if set(item) != expected_candidate_fields:
            raise CampaignValidationError("summary candidate field set is not exact")
        payloads = payloads_by_mode[mode]
        violations = _hard_constraint_violations(
            mode_metrics[mode], hard_constraints
        )
        hard_passed = not violations
        feasible += int(hard_passed)
        structural_expected = {
            "mode": mode,
            "repeat_ids": list(range(1, repeats + 1)),
            "repeat_count": repeats,
            "repeat_gate_passed": True,
            "batch_size": int(str(env["BATCH_SIZE"])),
            "budget_us": int(str(env["BUDGET_US"])),
            "execution_budget_safety_ratio": float(str(env["SAFETY_RATIO"])),
            "input_hash_manifest_sha256": input_hash,
            "decision_policy": expected_policy,
            "hard_constraint_violations": violations,
            "hard_constraints_passed": hard_passed,
            "train_flow_count_min": min(
                _mapping(payload.get("quality"), "quality")["train_flow_count"]
                for payload in payloads
            ),
            "test_flow_count_min": min(
                _mapping(payload.get("quality"), "quality")["test_flow_count"]
                for payload in payloads
            ),
            "final_quality_eligible": False,
            "missing_final_evidence": ["frozen_min_primary_metric"],
        }
        for name, expected in structural_expected.items():
            if item.get(name) != expected:
                raise CampaignValidationError("summary candidate {} drift".format(name))
        for name, expected in mode_metrics[mode].items():
            summary_name = name
            if name == "budget_us_max":
                summary_name = "budget_us"
            if not _same_number(item.get(summary_name), expected):
                raise CampaignValidationError("summary metric {}.{} drift".format(mode, name))
    if _integer(summary.get("feasible_candidate_count"), "summary.feasible_candidate_count", 0) != feasible:
        raise CampaignValidationError("summary feasible candidate count drift")


def _candidate_receipt(
    campaign_root: Path,
    repo_root: Path,
    contract_path: Path,
    plan: Mapping[str, object],
    job: Mapping[str, object],
    artifacts: Mapping[str, Mapping[str, object]],
    input_manifest: Mapping[str, object],
    frozen_contract_sha256: Optional[str] = None,
    environment_identity: Optional[Mapping[str, object]] = None,
    input_stat_identity: Optional[Mapping[str, object]] = None,
) -> Tuple[Dict[str, object], Path]:
    candidate_id = str(job["candidate_id"])
    result_parent = _directory_under(
        campaign_root, campaign_root / "results", "campaign results directory"
    )
    run_parent = _directory_under(
        campaign_root, campaign_root / "runs", "campaign runs directory"
    )
    run_id = "{}_{}".format(job["result_prefix"], job["run_tag"])
    if not RUN_ID_RE.fullmatch(run_id):
        raise CampaignValidationError("unsafe run ID")
    result_dir = _directory_under(
        result_parent, result_parent / run_id, "candidate result directory"
    )
    run_dir = _directory_under(
        run_parent, run_parent / run_id, "candidate run directory"
    )
    expected_names = {
        "summary.json",
        *{
            "{}_repeat{}.json".format(mode, repeat)
            for mode in MODES
            for repeat in range(1, len(job["expected_repeat_seeds"]) + 1)
        },
    }
    observed_names = {path.name for path in result_dir.iterdir()}
    if observed_names != expected_names:
        raise CampaignValidationError("{} result file set is not exact".format(candidate_id))
    result_files = [
        _assert_no_symlink_components(
            result_dir / name, "candidate result file"
        )
        for name in sorted(expected_names)
    ]
    result_data: Dict[str, Tuple[bytes, str, int]] = {}
    for path in result_files:
        raw_bytes = _stable_file_bytes(path, "candidate result file")
        result_data[path.name] = (raw_bytes, sha256_bytes(raw_bytes), len(raw_bytes))

    manifest_path = _assert_no_symlink_components(
        run_dir / "manifest.txt", "candidate run manifest"
    )
    manifest_bytes = _stable_file_bytes(manifest_path, "candidate run manifest")
    manifest = _parse_key_value_bytes(manifest_bytes, str(manifest_path))
    if manifest.get("status") != "complete" or manifest.get("run_id") != run_id:
        raise CampaignValidationError("{} run manifest is not complete".format(candidate_id))
    manifest_result = _clean_absolute_path(
        manifest.get("result_dir"), "manifest.result_dir"
    )
    if str(_absolute_lexical(Path(manifest_result))) != str(result_dir):
        raise CampaignValidationError("{} run manifest result_dir drift".format(candidate_id))
    if manifest.get("input_hash_manifest_sha256") != input_manifest["sha256"]:
        raise CampaignValidationError("{} run input hash drift".format(candidate_id))
    if manifest.get("result_count") != str(2 * len(job["expected_repeat_seeds"])):
        raise CampaignValidationError("{} run result_count drift".format(candidate_id))
    started = _iso8601(manifest.get("started_at"), "manifest.started_at")
    ended = _iso8601(manifest.get("ended_at"), "manifest.ended_at")
    if ended < started:
        raise CampaignValidationError("{} run timestamps are reversed".format(candidate_id))
    if started < _iso8601(plan.get("created_at_utc"), "plan.created_at_utc"):
        raise CampaignValidationError("{} predates the campaign plan".format(candidate_id))

    env = _mapping(job["runner_environment"], "job.runner_environment")
    contract_sha256 = (
        sha256_file(contract_path)
        if frozen_contract_sha256 is None
        else frozen_contract_sha256
    )
    manifest_expected = {
        "training_manifest": _mapping(plan["gpu_execution"], "plan.gpu_execution")["training_manifest"],
        "holdout_manifest": _mapping(plan["gpu_execution"], "plan.gpu_execution")["holdout_manifest"],
        "input_hash_manifest": input_manifest["path"],
        "input_hash_manifest_sha256": input_manifest["sha256"],
        "contract_sha256": contract_sha256,
        "environment_identity_sha256": (
            None
            if environment_identity is None
            else environment_identity["sha256"]
        ),
        "environment_files_manifest_sha256": (
            None if environment_identity is None
            else _mapping(environment_identity["environment_files_manifest"], "environment files manifest")["sha256"]
        ),
        "external_tools_manifest_sha256": (
            None if environment_identity is None
            else _mapping(environment_identity["external_tools_manifest"], "external tools manifest")["sha256"]
        ),
        "runtime_bootstrap_identity_sha256": (
            None if environment_identity is None
            else _mapping(
                environment_identity["runtime_bootstrap_identity"],
                "runtime bootstrap identity",
            )["sha256"]
        ),
        "input_stat_manifest_sha256": (
            None if input_stat_identity is None else input_stat_identity["sha256"]
        ),
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
        "calibration_attack_recall_floor": env["CALIBRATION_ATTACK_RECALL_FLOOR"],
        "feature_profile": env["FEATURE_PROFILE"],
        "classifier": env["CLASSIFIER"],
        "adaptation_policy": env["ADAPTATION_POLICY"],
        "adaptation_groups": env["ADAPTATION_GROUPS"],
        "adaptation_weight_multiplier": env["ADAPTATION_WEIGHT_MULTIPLIER"],
    }
    exact_manifest_keys = set(manifest_expected) | {
        "run_id",
        "status",
        "started_at",
        "ended_at",
        "result_dir",
        "result_count",
        "code_manifest_sha256",
        "environment_identity_sha256",
    }
    if set(manifest) != exact_manifest_keys:
        raise CampaignValidationError(
            "{} run manifest field set is not exact".format(candidate_id)
        )
    for name, expected in manifest_expected.items():
        if manifest.get(name) != str(expected):
            raise CampaignValidationError("{} manifest field {} drift".format(candidate_id, name))

    code_manifest_sha = _validate_code_manifest(
        run_dir / "code_sha256.txt", repo_root, artifacts
    )
    if manifest.get("code_manifest_sha256") != code_manifest_sha:
        raise CampaignValidationError(
            "{} manifest code identity drift".format(candidate_id)
        )
    result_manifest_sha = _validate_result_manifest(
        run_dir / "result_sha256.txt",
        {str(result_dir / name): values[1] for name, values in result_data.items()},
    )

    payloads_by_mode: Dict[str, List[Mapping[str, object]]] = {mode: [] for mode in MODES}
    identities_by_mode: Dict[str, List[Mapping[str, object]]] = {mode: [] for mode in MODES}
    evidence_files: List[Dict[str, object]] = []
    raw_hashes = set()
    seeds = list(job["expected_repeat_seeds"])
    for path in result_files:
        raw_bytes, raw_hash, raw_size = result_data[path.name]
        evidence_files.append(
            {
                "path": str(path),
                "size_bytes": raw_size,
                "sha256": raw_hash,
            }
        )
        match = RESULT_RE.fullmatch(path.name)
        if match is None:
            continue
        mode, repeat_text = match.groups()
        repeat = int(repeat_text)
        if repeat > len(seeds):
            raise CampaignValidationError("unexpected repeat number")
        payload = _mapping(
            _strict_json_from_bytes(raw_bytes, "raw result"), "raw_result"
        )
        extraction_identity = _validate_raw_payload(
            payload,
            job,
            mode,
            seeds[repeat - 1],
            str(input_manifest["sha256"]),
            int(input_manifest["entry_count"]),
            str(input_manifest["path"]),
        )
        if raw_hash in raw_hashes:
            raise CampaignValidationError("duplicate raw repeat payload")
        raw_hashes.add(raw_hash)
        payloads_by_mode[mode].append(payload)
        identities_by_mode[mode].append(extraction_identity)
    if any(len(payloads_by_mode[mode]) != len(seeds) for mode in MODES):
        raise CampaignValidationError("paired repeat payloads are incomplete")
    for mode in MODES:
        identity_hashes = {
            sha256_bytes(
                canonical_json_bytes(_stable_extraction_identity(identity))
            )
            for identity in identities_by_mode[mode]
        }
        if len(identity_hashes) != 1:
            raise CampaignValidationError(
                "{} extraction evidence drifts across repeat seeds".format(mode)
            )
    fresh_identities = [
        _mapping(identity.get("fresh_evaluation_identity"), "fresh evaluation identity")
        for mode in MODES
        for identity in identities_by_mode[mode]
    ]
    if len({sha256_bytes(canonical_json_bytes(identity)) for identity in fresh_identities}) != 1:
        raise CampaignValidationError("fresh extraction identity drifts across modes or repeats")
    fresh_evaluation_identity = dict(fresh_identities[0])
    for role in ("training", "calibration", "adaptation", "holdout"):
        comparable = []
        for mode in MODES:
            identity = identities_by_mode[mode][0]
            comparable.append({
                "flow_count": _mapping(identity["role_flow_counts"], "role flow counts")[role],
                "fingerprints": _mapping(identity["role_fingerprints"], "role fingerprints")[role],
                "label_fingerprints": _mapping(
                    identity["role_label_fingerprints"], "role label fingerprints"
                )[role],
            })
        if comparable[0] != comparable[1]:
            raise CampaignValidationError(
                "{} extraction identity drifts across normal/fallback".format(role)
            )
    mode_metrics = {
        mode: _candidate_raw_metrics(payloads_by_mode[mode], int(str(env["BUDGET_US"])))
        for mode in MODES
    }
    summary = _mapping(
        _strict_json_from_bytes(result_data["summary.json"][0], "summary"),
        "summary",
    )
    _validate_summary(
        summary,
        mode_metrics,
        len(seeds),
        payloads_by_mode,
        job,
        str(input_manifest["sha256"]),
        _mapping(plan.get("hard_constraints"), "plan.hard_constraints"),
    )
    worst = _aggregate_mode_metrics(mode_metrics)
    hard_constraint_violations = _hard_constraint_violations(
        worst,
        _mapping(plan.get("hard_constraints"), "plan.hard_constraints"),
    )
    receipt: Dict[str, object] = {
        "schema_version": 1,
        "scope": "hft_mgbs_algorithm_candidate_qualification_receipt_v1",
        "campaign_id": plan["campaign_id"],
        "campaign_run_id": plan["campaign_run_id"],
        "candidate_id": candidate_id,
        "run_id": run_id,
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "contract_sha256": contract_sha256,
        "algorithm_search_sha256": _mapping(plan["algorithm_search"], "plan.algorithm_search")["sha256"],
        "bound_repository_artifacts": copy.deepcopy(artifacts),
        "input_hash_manifest": dict(input_manifest),
        "run_manifest": {
            "path": str(manifest_path),
            "sha256": sha256_bytes(manifest_bytes),
        },
        "code_manifest": {
            "path": str((run_dir / "code_sha256.txt").resolve()),
            "sha256": code_manifest_sha,
        },
        "environment_identity": (
            None if environment_identity is None else dict(environment_identity)
        ),
        "input_stat_identity": (
            None if input_stat_identity is None else dict(input_stat_identity)
        ),
        "fresh_evaluation_identity": fresh_evaluation_identity,
        "extraction_identity": _stable_extraction_identity(
            identities_by_mode["normal"][0]
        ),
        "mode_resource_identity": {
            mode: {
                role: {
                    "flow_count": _mapping(
                        identities_by_mode[mode][0]["role_flow_counts"],
                        "role flow counts",
                    )[role],
                    "selected_flow_fingerprints": copy.deepcopy(
                        _mapping(
                            identities_by_mode[mode][0]["role_fingerprints"],
                            "role fingerprints",
                        )[role]
                    ),
                    "selected_flow_label_fingerprints": copy.deepcopy(
                        _mapping(
                            identities_by_mode[mode][0]["role_label_fingerprints"],
                            "role label fingerprints",
                        )[role]
                    ),
                }
                for role in ("training", "calibration", "adaptation", "holdout")
            }
            for mode in MODES
        },
        "result_manifest": {
            "path": str((run_dir / "result_sha256.txt").resolve()),
            "sha256": result_manifest_sha,
        },
        "evidence_files": evidence_files,
        "mode_contract": {
            "repeat_count_by_mode": {mode: len(seeds) for mode in MODES},
            "repeat_seeds_by_mode": {mode: list(seeds) for mode in MODES},
            "input_hash_manifest_sha256": input_manifest["sha256"],
            "fresh_evaluation_groups": list(job["expected_fresh_evaluation_groups"]),
        },
        "mode_metrics": mode_metrics,
        "reported_worst_case_metrics": worst,
        "evidence_recomputed_from_raw_repeats": True,
        "candidate_evaluated": True,
        "hard_constraint_violations": hard_constraint_violations,
        "hard_constraints_passed": not hard_constraint_violations,
        "algorithm_candidate_feasible": not hard_constraint_violations,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
    }
    receipt_path = campaign_root / "receipts" / "{}.json".format(candidate_id)
    write_json_atomic(receipt_path, receipt)
    return receipt, receipt_path


def _projection(
    search: Mapping[str, object],
    candidate_receipts: Mapping[str, Tuple[Mapping[str, object], Path]],
) -> Tuple[Dict[str, object], Dict[str, object]]:
    projection: Dict[str, object] = copy.deepcopy(dict(search))
    candidates = _list(projection.get("candidates"), "projection.candidates")
    for raw in candidates:
        candidate = _mapping(raw, "projection.candidate")
        candidate_id = str(candidate["id"])
        receipt, receipt_path = candidate_receipts[candidate_id]
        if not isinstance(candidate, MutableMapping):
            raise CampaignValidationError("projection candidate is not mutable")
        candidate["stage"] = "fresh_confirmatory"
        candidate["evidence"] = str(receipt_path.resolve())
        candidate["evidence_sha256"] = sha256_file(receipt_path)
        candidate["mode_contract"] = copy.deepcopy(receipt["mode_contract"])
        candidate["mode_metrics"] = copy.deepcopy(receipt["mode_metrics"])
        receipt_worst = _mapping(
            receipt.get("reported_worst_case_metrics"),
            "receipt.reported_worst_case_metrics",
        )
        missing_metrics = sorted(set(METRIC_NAMES).difference(receipt_worst))
        if missing_metrics:
            raise CampaignValidationError(
                "receipt reported worst-case metrics are missing: {}".format(
                    ", ".join(missing_metrics)
                )
            )
        for name in METRIC_NAMES:
            _finite(receipt_worst[name], "reported worst-case metric {}".format(name))
        # Candidate receipts retain the full 11-field diagnostic envelope, but
        # the frozen optimality auditor deliberately defines an exact 9-field
        # decision protocol.  Project only that protocol so diagnostics cannot
        # make otherwise valid evidence fail the exact-set comparison.
        candidate["reported_worst_case_metrics"] = {
            name: copy.deepcopy(receipt_worst[name]) for name in METRIC_NAMES
        }
    preliminary = audit_algorithm_search(projection)
    strict_front = preliminary["strict_pareto_front_recomputed_from_available_metrics"]
    practical_front = preliminary["practical_front_recomputed_from_available_metrics"]
    projection["strict_pareto_front"] = strict_front
    projection["practical_front"] = practical_front
    projection["selected_candidate"] = practical_front[0] if len(practical_front) == 1 else None
    projection["status"] = "suggested_after_uniform_fresh_qualification"
    projection["selection_reason"] = (
        "Recomputed from the uniform A01-A10 qualification campaign; this is a "
        "suggested projection and does not modify the frozen source search."
    )
    projection["selection_reason_zh"] = (
        "由统一 A01-A10 新鲜资格 campaign 重算；该文件仅为建议投影，不修改冻结的源搜索记录。"
    )
    final_audit = audit_algorithm_search(projection)
    return projection, final_audit


def _cross_candidate_resource_audit_errors(
    candidate_receipts: Mapping[str, Tuple[Mapping[str, object], Path]],
    jobs: Sequence[Mapping[str, object]],
) -> List[str]:
    """Require identical sample identity for comparable role sets.

    Resource outcomes are independently replayed and hard-gated for every
    repeat.  They must not be equal across different algorithms: measured
    execution time, tier assignment, and budget outcomes are candidate results.
    """

    jobs_by_candidate = {
        str(_mapping(item, "plan.job")["candidate_id"]): _mapping(item, "plan.job")
        for item in jobs
    }
    comparable: Dict[Tuple[str, str, str], str] = {}
    errors: List[str] = []
    for candidate_id, (receipt, _path) in sorted(candidate_receipts.items()):
        mode_metrics = _mapping(receipt.get("mode_metrics"), "receipt.mode_metrics")
        if set(mode_metrics) != set(MODES):
            raise CampaignValidationError("receipt mode metric set is not exact")
        for mode in MODES:
            metrics = _mapping(mode_metrics.get(mode), "receipt mode metrics")
            required_metric_names = (
                "key_flow_coverage_min",
                "budget_overrun_count_max",
                "budget_us_max",
                "ground_truth_event_recall_min",
            )
            if any(name not in metrics for name in required_metric_names):
                raise CampaignValidationError("receipt resource metric set is incomplete")
        resources = _mapping(
            receipt.get("mode_resource_identity"), "receipt.mode_resource_identity"
        )
        if set(resources) != set(MODES):
            raise CampaignValidationError("receipt mode resource identity set is not exact")
        expected_roles = _mapping(
            jobs_by_candidate[candidate_id].get("expected_capture_roles"),
            "expected capture roles",
        )
        for mode in MODES:
            mode_resources = _mapping(resources.get(mode), "mode resource identity")
            if set(mode_resources) != {"training", "calibration", "adaptation", "holdout"}:
                raise CampaignValidationError("receipt resource role set is not exact")
            for role in ("training", "calibration", "adaptation", "holdout"):
                resource = _mapping(mode_resources.get(role), "role resource identity")
                if set(resource) != {
                    "flow_count", "selected_flow_fingerprints",
                    "selected_flow_label_fingerprints",
                }:
                    raise CampaignValidationError("receipt role resource field set is not exact")
                role_set_hash = sha256_bytes(canonical_json_bytes(expected_roles[role]))
                observed_hash = sha256_bytes(canonical_json_bytes(resource))
                key = (mode, role, role_set_hash)
                previous = comparable.get(key)
                if previous is not None and previous != observed_hash:
                    errors.append(
                        "campaign:inconsistent_{}_{}_resource_identity".format(mode, role)
                    )
                comparable[key] = observed_hash
    return sorted(set(errors))


def _validate_formal_output_paths(
    campaign_root: Path, output_path: Path, projection_path: Path
) -> Tuple[Path, Path]:
    receipts_root = _directory_under(
        campaign_root,
        campaign_root / "receipts",
        "campaign receipts directory",
    )
    expected_output = _absolute_lexical(receipts_root / "campaign_receipt.json")
    expected_projection = _absolute_lexical(
        campaign_root / "suggested_algorithm_search_projection.json"
    )
    if _absolute_lexical(output_path) != expected_output:
        raise CampaignValidationError(
            "formal output must be campaign_root/receipts/campaign_receipt.json"
        )
    if _absolute_lexical(projection_path) != expected_projection:
        raise CampaignValidationError(
            "formal projection output must use its fixed campaign-root path"
        )
    # Existing targets, if any, must also have a completely real parent chain.
    _assert_no_symlink_components(expected_output.parent, "formal output parent")
    _assert_no_symlink_components(
        expected_projection.parent, "formal projection parent"
    )
    return expected_output, expected_projection


def finalize_campaign(
    repo_root: Path,
    contract_path: Path,
    campaign_root: Path,
    output_path: Path,
    projection_path: Path,
    search_path: Optional[Path] = None,
    trusted_contract_sha256: Optional[str] = None,
) -> Dict[str, object]:
    contract_start_bytes = _stable_file_bytes(contract_path, "campaign contract")
    contract_start_sha256 = sha256_bytes(contract_start_bytes)
    if trusted_contract_sha256 is not None and (
        not SHA256_RE.fullmatch(trusted_contract_sha256)
        or trusted_contract_sha256 != contract_start_sha256
    ):
        raise CampaignValidationError("campaign contract does not match external trust root")
    initial_contract = _mapping(
        _strict_json_from_bytes(contract_start_bytes, "campaign contract"),
        "contract",
    )
    initial_search_ref = _mapping(
        initial_contract.get("algorithm_search"), "algorithm_search"
    )
    initial_search_relative = _clean_relative_path(
        initial_search_ref.get("path"), "algorithm_search.path"
    )
    initial_search_path = _repo_file(repo_root, initial_search_relative)
    if search_path is not None and _absolute_lexical(search_path) != initial_search_path:
        raise CampaignValidationError(
            "search path does not match the contract-bound repository file"
        )
    search_start_sha256 = sha256_file(initial_search_path)
    contract, search, artifacts, _specs = validate_contract(repo_root, contract_path, search_path)
    if sha256_file(contract_path) != contract_start_sha256:
        raise CampaignValidationError("campaign contract changed during finalization")
    if sha256_file(initial_search_path) != search_start_sha256:
        raise CampaignValidationError("algorithm search changed during finalization")
    plan_path = campaign_root / "plan.json"
    plan_start_bytes = _stable_file_bytes(plan_path, "campaign plan")
    plan_start_sha256 = sha256_bytes(plan_start_bytes)
    plan = _mapping(
        _strict_json_from_bytes(plan_start_bytes, "campaign plan"), "plan"
    )
    if plan.get("scope") != "hft_mgbs_algorithm_qualification_campaign_plan_v1":
        raise CampaignValidationError("campaign plan scope is invalid")
    if _mapping(plan.get("contract"), "plan.contract").get("sha256") != sha256_file(contract_path):
        raise CampaignValidationError("campaign plan contract hash drift")
    if _mapping(plan.get("algorithm_search"), "plan.algorithm_search").get("sha256") != _mapping(contract["algorithm_search"], "contract.algorithm_search").get("sha256"):
        raise CampaignValidationError("campaign plan search hash drift")
    jobs = _list(plan.get("jobs"), "plan.jobs")
    if plan.get("candidate_count") != 10 or plan.get("job_count") != 10 or len(jobs) != 10:
        raise CampaignValidationError("campaign plan is incomplete")
    expected_plan = compile_campaign_plan(
        repo_root,
        contract_path,
        search_path,
        campaign_run_id=str(plan.get("campaign_run_id")),
        created_at_utc=str(plan.get("created_at_utc")),
    )
    if plan != expected_plan:
        raise CampaignValidationError("campaign plan does not replay from its contract")

    execution = _mapping(contract["execution"], "execution")
    configured_root = Path(str(execution["gpu_campaign_result_root"]))
    resolved_campaign_root = _existing_campaign_root(campaign_root, configured_root)
    campaign_root = resolved_campaign_root
    output_path, projection_path = _validate_formal_output_paths(
        campaign_root, output_path, projection_path
    )
    code_root = _assert_no_symlink_components(
        Path(str(execution["gpu_code_root"])), "contract-bound GPU code root"
    )
    if _assert_no_symlink_components(repo_root, "finalizer repository root") != code_root:
        raise CampaignValidationError("finalizer repo root is not the contract-bound GPU code root")

    input_manifest_path = campaign_root / "input_sha256.json"
    gpu_execution = _mapping(plan.get("gpu_execution"), "plan.gpu_execution")
    expected_input_paths = _referenced_input_paths(
        [
            Path(
                _clean_absolute_path(
                    gpu_execution.get("training_manifest"),
                    "plan.gpu_execution.training_manifest",
                )
            ),
            Path(
                _clean_absolute_path(
                    gpu_execution.get("holdout_manifest"),
                    "plan.gpu_execution.holdout_manifest",
                )
            ),
        ]
    )
    input_manifest = _validate_input_manifest(
        input_manifest_path,
        verify_referenced_files=True,
        expected_paths=expected_input_paths,
    )
    environment_identity_path = campaign_root / "environment_identity.json"
    environment_identity = _validate_environment_identity(
        environment_identity_path, execution
    )
    input_stat_identity = _validate_input_stat_manifest(
        campaign_root / "input_stat_identity.json", input_manifest
    )
    candidate_receipts: Dict[str, Tuple[Mapping[str, object], Path]] = {}
    errors: List[str] = []
    for raw_job in jobs:
        job = _mapping(raw_job, "plan.job")
        candidate_id = str(job.get("candidate_id"))
        try:
            receipt, receipt_path = _candidate_receipt(
                campaign_root,
                repo_root,
                contract_path,
                plan,
                job,
                artifacts,
                input_manifest,
                contract_start_sha256,
                environment_identity,
                input_stat_identity,
            )
            candidate_receipts[candidate_id] = (receipt, receipt_path)
        except (OSError, UnicodeError, CampaignValidationError, ValueError, KeyError) as error:
            errors.append("{}:{}:{}".format(candidate_id, type(error).__name__, error))

    code_manifest_hashes = {
        str(_mapping(receipt["code_manifest"], "receipt.code_manifest")["sha256"])
        for receipt, _path in candidate_receipts.values()
    }
    if candidate_receipts and len(code_manifest_hashes) != 1:
        errors.append("campaign:inconsistent_code_manifest_across_candidates")
    receipt_contract_hashes = {
        str(receipt.get("contract_sha256"))
        for receipt, _path in candidate_receipts.values()
    }
    receipt_search_hashes = {
        str(receipt.get("algorithm_search_sha256"))
        for receipt, _path in candidate_receipts.values()
    }
    if candidate_receipts and receipt_contract_hashes != {contract_start_sha256}:
        errors.append("campaign:inconsistent_contract_identity_across_candidates")
    if candidate_receipts and receipt_search_hashes != {search_start_sha256}:
        errors.append("campaign:inconsistent_search_identity_across_candidates")
    receipt_environment_hashes = {
        str(
            _mapping(
                receipt.get("environment_identity"),
                "receipt.environment_identity",
            ).get("sha256")
        )
        for receipt, _path in candidate_receipts.values()
    }
    if candidate_receipts and receipt_environment_hashes != {
        str(environment_identity["sha256"])
    }:
        errors.append("campaign:inconsistent_environment_identity_across_candidates")
    fresh_identity_hashes = {
        sha256_bytes(
            canonical_json_bytes(
                _mapping(
                    receipt.get("fresh_evaluation_identity"),
                    "receipt.fresh_evaluation_identity",
                )
            )
        )
        for receipt, _path in candidate_receipts.values()
    }
    if candidate_receipts and len(fresh_identity_hashes) != 1:
        errors.append("campaign:inconsistent_fresh_extraction_identity_across_candidates")
    comparable_role_identities: Dict[Tuple[str, str], str] = {}
    jobs_by_candidate = {
        str(_mapping(item, "plan.job")["candidate_id"]): _mapping(item, "plan.job")
        for item in jobs
    }
    for candidate_id, (receipt, _path) in candidate_receipts.items():
        extraction = _mapping(receipt.get("extraction_identity"), "receipt.extraction_identity")
        role_counts = _mapping(extraction.get("role_flow_counts"), "role flow counts")
        role_fingerprints = _mapping(extraction.get("role_fingerprints"), "role fingerprints")
        role_label_fingerprints = _mapping(
            extraction.get("role_label_fingerprints"), "role label fingerprints"
        )
        expected_roles = _mapping(
            jobs_by_candidate[candidate_id].get("expected_capture_roles"),
            "expected capture roles",
        )
        for role in ("training", "calibration", "adaptation", "holdout"):
            role_set_hash = sha256_bytes(canonical_json_bytes(expected_roles[role]))
            observed_hash = sha256_bytes(canonical_json_bytes({
                "flow_count": role_counts[role],
                "selected_flow_fingerprints": role_fingerprints[role],
                "selected_flow_label_fingerprints": role_label_fingerprints[role],
            }))
            key = (role, role_set_hash)
            if key in comparable_role_identities and comparable_role_identities[key] != observed_hash:
                errors.append("campaign:inconsistent_{}_sample_identity".format(role))
            comparable_role_identities[key] = observed_hash
    errors.extend(_cross_candidate_resource_audit_errors(candidate_receipts, jobs))

    projection: Optional[Dict[str, object]] = None
    projection_audit: Optional[Dict[str, object]] = None
    projection_sha: Optional[str] = None
    if len(candidate_receipts) == 10 and not errors:
        projection, projection_audit = _projection(search, candidate_receipts)
        projection_sha = sha256_bytes(canonical_json_bytes(projection))
    complete = len(candidate_receipts) == 10 and not errors
    optimum = bool(
        complete
        and projection_audit
        and projection_audit.get("accepted") is True
        and projection_audit.get("algorithm_only_practical_optimum_proven") is True
    )
    if sha256_file(contract_path) != contract_start_sha256:
        raise CampaignValidationError("campaign contract changed before output sealing")
    if sha256_file(initial_search_path) != search_start_sha256:
        raise CampaignValidationError("algorithm search changed before output sealing")
    if sha256_file(plan_path) != plan_start_sha256:
        raise CampaignValidationError("campaign plan changed before output sealing")
    _end_contract, _end_search, end_artifacts, _end_specs = validate_contract(
        repo_root, contract_path, search_path
    )
    if end_artifacts != artifacts:
        raise CampaignValidationError("bound repository code changed before output sealing")
    if _validate_environment_identity(
        environment_identity_path, execution
    ) != environment_identity:
        raise CampaignValidationError("campaign environment changed before output sealing")
    if _validate_input_manifest(
        input_manifest_path,
        verify_referenced_files=True,
        expected_paths=expected_input_paths,
    ) != input_manifest:
        raise CampaignValidationError("campaign input changed before output sealing")
    if _validate_input_stat_manifest(
        campaign_root / "input_stat_identity.json", input_manifest
    ) != input_stat_identity:
        raise CampaignValidationError("campaign input stat identity changed before output sealing")
    if projection is not None:
        published_projection_sha = write_json_atomic(projection_path, projection)
        if published_projection_sha != projection_sha:
            raise CampaignValidationError("projection hash changed during publication")
    result: Dict[str, object] = {
        "schema_version": 1,
        "scope": "hft_mgbs_algorithm_qualification_campaign_receipt_v1",
        "campaign_id": plan.get("campaign_id"),
        "campaign_run_id": plan.get("campaign_run_id"),
        "contract_sha256": contract_start_sha256,
        "external_trust_root_sha256": trusted_contract_sha256,
        "algorithm_search_sha256": search_start_sha256,
        "input_hash_manifest": input_manifest,
        "environment_identity": environment_identity,
        "expected_candidate_count": 10,
        "evaluated_candidate_count": len(candidate_receipts),
        "feasible_candidate_count": sum(
            receipt.get("algorithm_candidate_feasible") is True
            for receipt, _path in candidate_receipts.values()
        ),
        "qualified_candidate_count": sum(
            receipt.get("algorithm_candidate_feasible") is True
            for receipt, _path in candidate_receipts.values()
        ),
        "candidate_receipts": [
            {
                "candidate_id": candidate_id,
                "path": str(path.resolve()),
                "sha256": sha256_file(path),
            }
            for candidate_id, (_receipt, path) in sorted(candidate_receipts.items())
        ],
        "suggested_algorithm_search_projection": (
            {"path": str(projection_path.resolve()), "sha256": projection_sha}
            if projection_sha is not None
            else None
        ),
        "projection_optimality_audit": projection_audit,
        "campaign_evidence_complete": complete,
        "algorithm_only_practical_optimum_proven": optimum,
        "accepted": optimum,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
        "source_algorithm_search_modified": False,
        "raw_results_remain_on_gpu": True,
        "errors": sorted(errors),
    }
    write_json_atomic(output_path, result)
    return result
