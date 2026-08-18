#!/usr/bin/env python3
"""Export independent official UNSW labels and frozen-A09 predictions.

The exporter is inference-only and fail-closed.  Its model/runtime identity is
resolved exclusively from a separately trusted evidence-collector prepare
receipt.  Evaluation extraction limits are frozen in this source and are not
CLI tuning surfaces.  No historical result or aggregate summary is accepted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_CONTRACT = ROOT / "configs" / "algorithm_qualification_campaign_v1.json"
LABEL_SCOPE = "hft_mgbs_independent_ground_truth_labels_v2"
PREDICTION_SCOPE = "hft_mgbs_independent_predictions_v2"
SOURCE_SCOPE = "hft_mgbs_unsw_official_quality_source_v1"
RECEIPT_SCOPE = "hft_mgbs_a09_current_279_quality_export_receipt_v2"
PREPARE_SCOPE = "hft_mgbs_current_hardware_2_79_evidence_prepare_v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_EVALUATION_GROUPS = (
    "unsw_2015-02-17_adapt_confirm_shard7",
    "unsw_2015-02-17_adapt_confirm_shard8",
    "unsw_2015-02-17_adapt_confirm_shard9",
)
EXECUTED_BINDINGS = {
    "batching": ("hft_mgbs.batching", ROOT / "hft_mgbs" / "batching.py"),
    "candidate_dataset": (
        "hft_mgbs.candidate_dataset",
        ROOT / "hft_mgbs" / "candidate_dataset.py",
    ),
    "domain_features": ("hft_mgbs.domain_features", ROOT / "hft_mgbs" / "domain_features.py"),
    "features": ("hft_mgbs.features", ROOT / "hft_mgbs" / "features.py"),
    "pcap_reader": ("hft_mgbs.pcap", ROOT / "hft_mgbs" / "pcap.py"),
    "pipeline": ("hft_mgbs.pipeline", ROOT / "hft_mgbs" / "pipeline.py"),
    "runtime": ("hft_mgbs.runtime", ROOT / "hft_mgbs" / "runtime.py"),
    "scheduler": ("hft_mgbs.scheduler", ROOT / "hft_mgbs" / "scheduler.py"),
    "unsw_alignment": ("hft_mgbs.unsw", ROOT / "hft_mgbs" / "unsw.py"),
}
FROZEN_EXTRACTION_POLICY = {
    "batch_size": 512,
    "budget_us": 5000.0,
    "execution_budget_safety_ratio": 0.50,
    "allow_deep": True,
    "key_flow_ratio": 0.10,
    "max_payload_bytes": 256,
    "max_packets_per_capture": 50_000,
    "max_flows_per_capture": 5_000,
    "alignment_tolerance_s": 0.0,
}


class ExportError(ValueError):
    """A trust root, frozen artifact, or official input is invalid."""


def _strict_object(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ExportError("duplicate JSON key: " + key)
        value[key] = item
    return value


def load_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ExportError("non-finite JSON constant: " + token)
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExportError("unreadable JSON {}: {}".format(path, error)) from error
    if not isinstance(value, Mapping):
        raise ExportError("JSON root must be an object: " + str(path))
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _require_sha(name: str, value: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ExportError(name + " must be a lowercase SHA-256")
    return value


def _finite(name: str, value: Any, minimum: Optional[float] = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExportError(name + " must be numeric")
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        raise ExportError(name + " must be finite and in range")
    return number


def _strict_int(name: str, value: Any, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ExportError(name + " must be an integer in range")
    return value


def _safe_relative(root: Path, raw: Any, name: str) -> Path:
    if not isinstance(raw, str) or not raw or any(char in raw for char in "\r\n\x00"):
        raise ExportError(name + " path is missing or unsafe")
    posix = PurePosixPath(raw)
    if posix.is_absolute() or ".." in posix.parts:
        raise ExportError(name + " path must be relative")
    path = root / Path(*posix.parts)
    if not _regular(path):
        raise ExportError(name + " is missing or symlinked")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ExportError(name + " escapes its receipt root") from error
    return path.resolve()


def _snapshot(paths: Iterable[Path]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for path in paths:
        resolved = path.resolve()
        if not _regular(resolved):
            raise ExportError("snapshot input missing or symlinked: " + str(path))
        name = str(resolved)
        if name in result:
            continue
        result[name] = sha256_file(resolved)
    return result


def _verify_snapshot(snapshot: Mapping[str, str]) -> None:
    for raw_path, expected in snapshot.items():
        path = Path(raw_path)
        if not _regular(path) or sha256_file(path) != expected:
            raise ExportError("source drift during export: " + raw_path)


def _durable_write(path: Path, raw: bytes) -> None:
    with path.open("wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    _durable_write(
        temporary,
        (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8"),
    )
    os.replace(str(temporary), str(path))


def _atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    _durable_write(temporary, value.encode("utf-8"))
    os.replace(str(temporary), str(path))


def _staging_directory(final: Path) -> Tuple[Path, Path]:
    final = final.resolve()
    final.parent.mkdir(parents=True, exist_ok=True)
    if final.exists() or final.is_symlink():
        raise ExportError("output directory must not already exist")
    staging = Path(
        tempfile.mkdtemp(prefix="." + final.name + ".staging-", dir=str(final.parent))
    ).resolve()
    return final, staging


def _commit_directory(staging: Path, final: Path) -> None:
    if final.exists() or final.is_symlink():
        raise ExportError("output directory appeared before commit")
    for child in staging.iterdir():
        if child.is_file():
            with child.open("rb") as handle:
                os.fsync(handle.fileno())
    os.replace(str(staging), str(final))


def stable_sample_id(group: str, record: Mapping[str, Any]) -> str:
    """Return a direction-independent, session-time-bound flow identity."""

    if not isinstance(group, str) or not group:
        raise ExportError("sample group is missing")
    key = record.get("forward_key")
    if not isinstance(key, (tuple, list)) or len(key) != 5:
        raise ExportError("flow record has no five-tuple")
    ports_protocol: List[int] = []
    for name, value in zip(("src_port", "dst_port", "protocol"), key[2:]):
        ports_protocol.append(_strict_int(name, value, 0))
    from hft_mgbs.features import MultiGranularityExtractor

    typed = (str(key[0]), str(key[1]), ports_protocol[0], ports_protocol[1], ports_protocol[2])
    canonical = MultiGranularityExtractor.normalize_flow_key(typed)
    start = _finite("start_timestamp", record.get("start_timestamp"), 0.0)
    last = _finite("last_timestamp", record.get("last_timestamp"), 0.0)
    if last < start:
        raise ExportError("flow timestamps are reversed")
    material = {
        "schema": "unsw_canonical_bidirectional_5tuple_time_v2",
        "group": group,
        "canonical_flow_key": list(canonical),
        "start_timestamp": format(start, ".9f"),
        "last_timestamp": format(last, ".9f"),
    }
    return "unsw-flow-" + _canonical_sha(material)


def _verify_prepare_manifest(root: Path, reference: Mapping[str, Any]) -> Path:
    path = _safe_relative(root, reference.get("path"), "prepare_manifest")
    if sha256_file(path) != reference.get("sha256"):
        raise ExportError("prepare manifest hash mismatch")
    entries: Dict[str, str] = {}
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n\x00]+)", line)
        if match is None:
            raise ExportError("malformed prepare manifest line {}".format(index))
        digest, raw_name = match.groups()
        if raw_name in entries:
            raise ExportError("duplicate prepare manifest path")
        candidate = _safe_relative(root, raw_name, "prepare manifest entry")
        if sha256_file(candidate) != digest:
            raise ExportError("prepare manifest artifact drift: " + raw_name)
        entries[raw_name] = digest
    if not entries:
        raise ExportError("empty prepare manifest")
    return path


def validate_prepare_receipt(
    receipt_path: Path, trusted_receipt_sha256: str
) -> Tuple[Mapping[str, Any], Path, Path, Path, List[Path]]:
    _require_sha("trusted prepare receipt SHA-256", trusted_receipt_sha256)
    if not _regular(receipt_path) or sha256_file(receipt_path) != trusted_receipt_sha256:
        raise ExportError("prepare receipt does not match the external trust root")
    receipt = load_json(receipt_path)
    if (
        receipt.get("schema_version") != 1
        or receipt.get("scope") != PREPARE_SCOPE
        or receipt.get("gaps") != []
        or receipt.get("read_only_source_access") is not True
        or receipt.get("service_started_or_stopped") is not False
        or receipt.get("traffic_started_or_stopped") is not False
    ):
        raise ExportError("prepare receipt is incomplete")
    root = receipt_path.parent.resolve()
    manifest_ref = receipt.get("prepare_manifest")
    if not isinstance(manifest_ref, Mapping):
        raise ExportError("prepare manifest reference missing")
    manifest = _verify_prepare_manifest(root, manifest_ref)
    artifacts = receipt.get("artifacts")
    artifact_sha = receipt.get("artifact_sha256")
    if not isinstance(artifacts, Mapping) or not isinstance(artifact_sha, Mapping):
        raise ExportError("prepared artifacts missing")
    resolved: Dict[str, Path] = {}
    for name in ("model", "runtime_manifest", "service_source", "engine_source", "service_launcher"):
        ref = artifacts.get(name)
        if not isinstance(ref, Mapping):
            raise ExportError("prepared artifact missing: " + name)
        path = _safe_relative(root, ref.get("path"), "prepared " + name)
        observed = sha256_file(path)
        if ref.get("sha256") != observed or artifact_sha.get(name) != observed:
            raise ExportError("prepared artifact hash mismatch: " + name)
        resolved[name] = path
    runtime = load_json(resolved["runtime_manifest"])
    if (
        runtime.get("schema_version") != 2
        or runtime.get("candidate_id") != "A09"
        or runtime.get("model_sha256") != artifact_sha.get("model")
        or receipt.get("runtime_manifest_actual_sha256") != artifact_sha.get("runtime_manifest")
    ):
        raise ExportError("prepare/runtime does not bind frozen A09")
    runtime_identity = receipt.get("runtime_identity")
    if not isinstance(runtime_identity, Mapping) or runtime_identity.get("candidate_id") != "A09":
        raise ExportError("prepare runtime identity is not A09")
    paths = [receipt_path.resolve(), manifest, *resolved.values()]
    return receipt, resolved["model"], resolved["runtime_manifest"], manifest, paths


def validate_contract(
    contract_path: Path, trusted_contract_sha256: str
) -> Tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Path], List[Path]]:
    _require_sha("trusted campaign contract SHA-256", trusted_contract_sha256)
    if not _regular(contract_path) or sha256_file(contract_path) != trusted_contract_sha256:
        raise ExportError("campaign contract does not match the external trust root")
    contract = load_json(contract_path)
    if (
        contract.get("schema_version") != 1
        or contract.get("scope") != "hft_mgbs_bounded_algorithm_qualification_campaign_v1"
    ):
        raise ExportError("unsupported campaign contract")
    uniform = contract.get("uniform_protocol")
    roles = contract.get("dataset_roles")
    bound = contract.get("bound_repository_artifacts")
    if not isinstance(uniform, Mapping) or not isinstance(roles, Mapping) or not isinstance(bound, Mapping):
        raise ExportError("campaign protocol bindings missing")
    exact_uniform = {
        "batch_size": 512,
        "budget_us": 5000,
        "execution_budget_safety_ratio": 0.5,
        "max_test_packets_per_capture": 50000,
        "max_test_flows_per_capture": 5000,
        "repeat_seeds": [7, 11, 19],
        "estimators": 200,
        "n_jobs": 8,
        "fresh_evaluation_groups": list(EXPECTED_EVALUATION_GROUPS),
    }
    for name, wanted in exact_uniform.items():
        if uniform.get(name) != wanted or type(uniform.get(name)) is not type(wanted):
            raise ExportError("frozen campaign protocol drift: " + name)
    fresh = roles.get("fresh_evaluation_groups")
    adaptation = roles.get("adaptation_groups")
    calibration = roles.get("calibration_groups")
    if fresh != list(EXPECTED_EVALUATION_GROUPS):
        raise ExportError("fresh evaluation partition drift")
    if not isinstance(adaptation, list) or not isinstance(calibration, list):
        raise ExportError("adaptation/calibration partitions missing")
    if set(fresh) & (set(adaptation) | set(calibration)):
        raise ExportError("outer evaluation partition overlaps tuning data")
    candidate = next(
        (
            item
            for item in contract.get("candidate_protocols", [])
            if isinstance(item, Mapping) and item.get("id") == "A09"
        ),
        None,
    )
    expected_candidate = {
        "feature_profile": "invariant_no_ports_v1",
        "classifier": "extra_trees",
        "threshold_policy": "calibration_macro_f1",
        "calibration_attack_recall_floor": 0.8,
        "calibration_groups": ["unsw_2015-01-22_shard3"],
        "adaptation_policy": "calibration_weighted",
        "adaptation_groups": ["unsw_2015-01-22_shard1", "unsw_2015-01-22_shard2"],
        "adaptation_weight_multiplier": 5.0,
    }
    if not isinstance(candidate, Mapping):
        raise ExportError("A09 candidate protocol missing")
    for name, wanted in expected_candidate.items():
        if candidate.get(name) != wanted:
            raise ExportError("A09 candidate protocol drift: " + name)
    paths: Dict[str, Path] = {}
    snapshot_paths: List[Path] = [contract_path.resolve()]
    required = set(EXECUTED_BINDINGS) | {
        "evaluate_unsw",
        "holdout_manifest",
        "training_manifest",
    }
    for name in required:
        binding = bound.get(name)
        if not isinstance(binding, Mapping):
            raise ExportError("campaign binding missing: " + name)
        raw_path = binding.get("path")
        expected = binding.get("sha256")
        _require_sha("campaign binding " + name, expected)
        if not isinstance(raw_path, str):
            raise ExportError("campaign binding path missing: " + name)
        path = (ROOT / Path(*PurePosixPath(raw_path).parts)).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as error:
            raise ExportError("campaign binding escapes code root: " + name) from error
        if not _regular(path) or sha256_file(path) != expected:
            raise ExportError("campaign-bound source drift: " + name)
        paths[name] = path
        snapshot_paths.append(path)
    search_ref = contract.get("algorithm_search")
    if not isinstance(search_ref, Mapping):
        raise ExportError("algorithm-search trust reference missing")
    search_path = (ROOT / Path(*PurePosixPath(str(search_ref.get("path"))).parts)).resolve()
    if not _regular(search_path) or sha256_file(search_path) != search_ref.get("sha256"):
        raise ExportError("algorithm-search artifact drift")
    search = load_json(search_path)
    selected = next(
        (
            item
            for item in search.get("candidates", [])
            if isinstance(item, Mapping) and item.get("id") == "A09"
        ),
        None,
    )
    if search.get("selected_candidate") != "A09" or not isinstance(selected, Mapping):
        raise ExportError("A09 is not the frozen selected candidate")
    paths["algorithm_search"] = search_path
    snapshot_paths.append(search_path)
    return contract, candidate, paths, snapshot_paths


def verify_import_bindings(contract: Mapping[str, Any], paths: Mapping[str, Path]) -> None:
    bound = contract["bound_repository_artifacts"]
    for name, (module_name, expected_path) in EXECUTED_BINDINGS.items():
        module = importlib.import_module(module_name)
        actual = Path(str(getattr(module, "__file__", ""))).resolve()
        expected = expected_path.resolve()
        if actual != expected or actual != paths[name] or sha256_file(actual) != bound[name]["sha256"]:
            raise ExportError("executed Python module is not campaign-bound: " + module_name)


def validate_input_hash_manifest(
    manifest_path: Path, required_paths: Sequence[Path], expected_sha256: str
) -> Tuple[Mapping[str, Any], Dict[str, Mapping[str, Any]]]:
    if not _regular(manifest_path) or sha256_file(manifest_path) != expected_sha256:
        raise ExportError("input hash manifest is not the frozen A09 manifest")
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != 1 or manifest.get("algorithm") != "sha256":
        raise ExportError("input hash manifest schema drift")
    entries: Dict[str, Mapping[str, Any]] = {}
    raw_entries = manifest.get("entries")
    if not isinstance(raw_entries, list):
        raise ExportError("input hash manifest entries missing")
    for item in raw_entries:
        if not isinstance(item, Mapping) or not isinstance(item.get("path"), str):
            raise ExportError("invalid input hash manifest entry")
        resolved = str(Path(item["path"]).resolve())
        if resolved in entries:
            raise ExportError("duplicate input hash manifest path")
        entries[resolved] = item
    for path in required_paths:
        resolved = str(path.resolve())
        item = entries.get(resolved)
        if (
            item is None
            or not _regular(path)
            or item.get("sha256") != sha256_file(path)
            or item.get("size_bytes") != path.stat().st_size
        ):
            raise ExportError("unfrozen or drifted official input: " + str(path))
    return manifest, entries


def validate_bundle(
    bundle: Mapping[str, Any],
    model_path: Path,
    runtime_path: Path,
    contract: Mapping[str, Any],
    candidate: Mapping[str, Any],
    paths: Mapping[str, Path],
    input_manifest_sha256: str,
) -> None:
    runtime = load_json(runtime_path)
    if runtime.get("model_sha256") != sha256_file(model_path):
        raise ExportError("runtime/model binding drift")
    models = bundle.get("models")
    thresholds = bundle.get("thresholds")
    positive_indices = bundle.get("positive_indices")
    if (
        bundle.get("schema_version") != 1
        or bundle.get("candidate_id") != "A09"
        or bundle.get("feature_profile") != candidate.get("feature_profile")
        or bundle.get("classifier") != candidate.get("classifier")
        or not isinstance(models, list)
        or len(models) != 3
        or not isinstance(thresholds, list)
        or len(thresholds) != 3
        or not isinstance(positive_indices, list)
        or len(positive_indices) != 3
        or not hasattr(bundle.get("vectorizer"), "transform")
    ):
        raise ExportError("unsupported A09 bundle structure")
    metadata = bundle.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ExportError("A09 bundle metadata missing")
    exact_metadata = {
        "adaptation_groups": sorted(candidate["adaptation_groups"]),
        "calibration_groups": sorted(candidate["calibration_groups"]),
        "adaptation_weight_multiplier": candidate["adaptation_weight_multiplier"],
        "calibration_attack_recall_floor": candidate["calibration_attack_recall_floor"],
        "holdout_manifest_sha256": sha256_file(paths["holdout_manifest"]),
        "training_manifest_sha256": sha256_file(paths["training_manifest"]),
        "input_hash_manifest_sha256": input_manifest_sha256,
        "seeds": [7, 11, 19],
        "estimators_per_seed": 200,
    }
    for name, wanted in exact_metadata.items():
        observed = metadata.get(name)
        if name in ("adaptation_groups", "calibration_groups") and isinstance(observed, list):
            observed = sorted(observed)
        if observed != wanted:
            raise ExportError("A09 bundle metadata drift: " + name)
    for index, (model, raw_positive, raw_threshold, seed) in enumerate(
        zip(models, positive_indices, thresholds, (7, 11, 19))
    ):
        positive = _strict_int("positive index", raw_positive, 0)
        threshold = _finite("member threshold", raw_threshold, 0.0)
        if threshold > 1.0:
            raise ExportError("member threshold outside [0,1]")
        classes = list(getattr(model, "classes_", []))
        if positive >= len(classes) or classes[positive] != 1:
            raise ExportError("A09 positive class index drift")
        estimators = getattr(model, "estimators_", None)
        if not isinstance(estimators, (list, tuple)) or len(estimators) != 200:
            raise ExportError("A09 estimator count drift")
        if getattr(model, "n_estimators", None) != 200 or getattr(model, "random_state", None) != seed:
            raise ExportError("A09 estimator protocol drift at member {}".format(index))
        if getattr(model, "min_samples_leaf", None) != 2 or getattr(model, "class_weight", None) != "balanced":
            raise ExportError("A09 classifier parameter drift")


def _official_row_fingerprints(path: Path, wanted: Iterable[int]) -> Dict[int, str]:
    wanted_rows = set(wanted)
    result: Dict[int, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, 1):
            if row_number in wanted_rows:
                result[row_number] = _canonical_sha(
                    {"official_csv_row_number": row_number, "fields": dict(row)}
                )
    if set(result) != wanted_rows:
        raise ExportError("eligible official row is absent from ground-truth CSV")
    return result


def official_label_relations(truth: Any, record: Mapping[str, Any]) -> List[int]:
    key = record.get("forward_key")
    start = _finite("start_timestamp", record.get("start_timestamp"), 0.0)
    last = _finite("last_timestamp", record.get("last_timestamp"), 0.0)
    if not isinstance(key, (tuple, list)) or len(key) != 5 or last < start:
        raise ExportError("invalid extracted flow record")
    matches = truth.matching_intervals(tuple(key), start, last, tolerance_s=0.0)
    return sorted({int(interval.event_id) for interval in matches if interval.event_id >= 0})


def predict_frozen_bundle(bundle: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> List[float]:
    import numpy as np
    from hft_mgbs.domain_features import transform_feature_rows

    projected = transform_feature_rows(rows, "invariant_no_ports_v1")
    matrix = bundle["vectorizer"].transform(projected).astype(np.float32, copy=False)
    probabilities = []
    for model, raw_positive in zip(bundle["models"], bundle["positive_indices"]):
        positive = _strict_int("positive index", raw_positive, 0)
        probabilities.append(model.predict_proba(matrix)[:, positive])
    scores = np.mean(probabilities, axis=0)
    values = [float(value) for value in scores.tolist()]
    if len(values) != len(rows):
        raise ExportError("A09 prediction row-count mismatch")
    for value in values:
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ExportError("A09 returned invalid probability")
    return values


def _input_manifest_expected_sha(paths: Mapping[str, Path]) -> str:
    search = load_json(paths["algorithm_search"])
    candidate = next(
        item
        for item in search["candidates"]
        if isinstance(item, Mapping) and item.get("id") == "A09"
    )
    mode_contract = candidate.get("mode_contract")
    expected = mode_contract.get("input_hash_manifest_sha256") if isinstance(mode_contract, Mapping) else None
    return _require_sha("A09 frozen input manifest SHA-256", expected)


def _portable_source(
    manifest: Mapping[str, Any],
    manifest_sha: str,
    input_rows: Sequence[Mapping[str, Any]],
    eligible_events: Sequence[Mapping[str, Any]],
    relations: Sequence[Mapping[str, Any]],
    contract_sha: str,
    extraction_policy_sha: str,
) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": SOURCE_SCOPE,
        "source_kind": "official_unsw_ground_truth_and_frozen_pcap_inputs",
        "synthetic": False,
        "portable": True,
        "campaign_contract_sha256": contract_sha,
        "input_hash_manifest_sha256": manifest_sha,
        "embedded_input_hash_manifest": manifest,
        "extraction_policy_sha256": extraction_policy_sha,
        "official_inputs": list(input_rows),
        "eligible_events": list(eligible_events),
        "sample_event_relations": list(relations),
    }


def export_quality_evidence(
    *,
    output_dir: Path,
    contract_path: Path,
    trusted_contract_sha256: str,
    trusted_exporter_sha256: str,
    prepare_receipt_path: Path,
    trusted_prepare_receipt_sha256: str,
    input_hash_manifest_path: Path,
) -> Mapping[str, Any]:
    _require_sha("trusted exporter SHA-256", trusted_exporter_sha256)
    if sha256_file(Path(__file__).resolve()) != trusted_exporter_sha256:
        raise ExportError("running exporter does not match its external trust root")
    final, staging = _staging_directory(output_dir)
    try:
        prepare, model_path, runtime_path, _prepare_manifest, prepare_paths = validate_prepare_receipt(
            prepare_receipt_path, trusted_prepare_receipt_sha256
        )
        contract, candidate, paths, contract_paths = validate_contract(
            contract_path, trusted_contract_sha256
        )
        verify_import_bindings(contract, paths)
        expected_input_sha = _input_manifest_expected_sha(paths)
        holdout = load_json(paths["holdout_manifest"])
        samples = holdout.get("samples")
        if not isinstance(samples, list):
            raise ExportError("holdout samples missing")
        fresh = list(contract["dataset_roles"]["fresh_evaluation_groups"])
        selected = [item for item in samples if isinstance(item, Mapping) and item.get("group") in fresh]
        if [item.get("group") for item in selected] != fresh:
            raise ExportError("holdout fresh-group order/content drift")
        truth_path = Path(str(holdout.get("ground_truth_csv"))).resolve()
        pcap_paths = [Path(str(item.get("path"))).resolve() for item in selected]
        required_inputs = [paths["holdout_manifest"], truth_path, *pcap_paths]
        input_manifest, entries = validate_input_hash_manifest(
            input_hash_manifest_path, required_inputs, expected_input_sha
        )
        snapshot = _snapshot(
            [Path(__file__).resolve(), input_hash_manifest_path, *required_inputs, *prepare_paths, *contract_paths]
        )

        import joblib

        bundle = joblib.load(model_path)
        if not isinstance(bundle, Mapping):
            raise ExportError("A09 bundle root must be a mapping")
        validate_bundle(
            bundle,
            model_path,
            runtime_path,
            contract,
            candidate,
            paths,
            expected_input_sha,
        )
        from hft_mgbs.candidate_dataset import extract_candidate_flow_records
        from hft_mgbs.unsw import UnswGroundTruth

        truth = UnswGroundTruth.from_csv(truth_path)
        features: List[Mapping[str, Any]] = []
        label_rows: List[Dict[str, Any]] = []
        eligible_rows: List[Dict[str, Any]] = []
        relation_rows: List[Dict[str, Any]] = []
        capture_audit: List[Dict[str, Any]] = []
        seen_samples = set()
        eligible_groups: Dict[int, set] = {}
        seen_relations = set()
        policy = dict(FROZEN_EXTRACTION_POLICY)
        policy_sha = _canonical_sha(policy)
        for item, pcap_path in zip(selected, pcap_paths):
            group = str(item["group"])
            records, summary = extract_candidate_flow_records(
                str(pcap_path),
                group,
                batch_size=512,
                budget_us=5000.0,
                allow_deep=True,
                key_flow_ratio=0.10,
                max_payload_bytes=256,
                max_packets=50_000,
                max_flows=5_000,
                execution_budget_safety_ratio=0.50,
            )
            packet_start = summary.get("packet_start_timestamp")
            packet_last = summary.get("packet_last_timestamp")
            if packet_start is None or packet_last is None:
                raise ExportError("fresh PCAP has no evaluated packet span: " + group)
            start = _finite("packet_start_timestamp", packet_start, 0.0)
            last = _finite("packet_last_timestamp", packet_last, 0.0)
            if last < start:
                raise ExportError("fresh PCAP packet span is reversed")
            group_eligible = sorted(set(truth.event_ids_overlapping(start, last, tolerance_s=0.0)))
            for row_number in group_eligible:
                eligible_groups.setdefault(row_number, set()).add(group)
            attack = 0
            for record in records:
                sample_id = stable_sample_id(group, record)
                if sample_id in seen_samples:
                    raise ExportError("stable sample_id collision")
                seen_samples.add(sample_id)
                matches = official_label_relations(truth, record)
                label = int(bool(matches))
                attack += label
                label_rows.append({"sample_id": sample_id, "label": label, "group": group})
                features.append(record["features"])
                for row_number in matches:
                    event_id = "unsw-gt-row-{}".format(row_number)
                    relation_key = (sample_id, group, event_id)
                    if relation_key in seen_relations:
                        raise ExportError("duplicate sample/event relation")
                    if row_number not in eligible_groups or group not in eligible_groups[row_number]:
                        raise ExportError("matched event is outside evaluated packet span")
                    seen_relations.add(relation_key)
                    relation_rows.append(
                        {"sample_id": sample_id, "group": group, "event_id": event_id}
                    )
            capture_audit.append(
                {
                    "group": group,
                    "pcap_sha256": sha256_file(pcap_path),
                    "packet_start_timestamp": start,
                    "packet_last_timestamp": last,
                    "selected_flows": len(records),
                    "attack_flows": attack,
                    "benign_flows": len(records) - attack,
                    "eligible_official_events": len(group_eligible),
                    "parsed_packets": _strict_int("parsed_packets", summary.get("parsed_packets"), 0),
                    "rejected_records": _strict_int("rejected_records", summary.get("rejected_records"), 0),
                }
            )
        eligible_rows = [
            {
                "event_id": "unsw-gt-row-{}".format(row_number),
                "eligible_groups": sorted(groups),
                "official_csv_row_number": row_number,
            }
            for row_number, groups in sorted(eligible_groups.items())
        ]
        positives = sum(row["label"] for row in label_rows)
        if not features or not 0 < positives < len(label_rows) or not eligible_rows:
            raise ExportError("official evaluation must contain both classes and eligible events")
        positive_samples = {row["sample_id"] for row in label_rows if row["label"] == 1}
        related_samples = {row["sample_id"] for row in relation_rows}
        if positive_samples != related_samples:
            raise ExportError("positive labels and official event relations are not conserved")
        fingerprints = _official_row_fingerprints(
            truth_path, (int(row["official_csv_row_number"]) for row in eligible_rows)
        )
        for row in eligible_rows:
            row["official_row_sha256"] = fingerprints[int(row["official_csv_row_number"])]
        scores = predict_frozen_bundle(bundle, features)
        thresholds = [_finite("member threshold", value, 0.0) for value in bundle["thresholds"]]
        if any(value > 1.0 for value in thresholds):
            raise ExportError("member threshold outside [0,1]")
        threshold = sorted(thresholds)[1]
        input_rows = []
        roles = [("holdout_manifest", paths["holdout_manifest"]), ("ground_truth_csv", truth_path)]
        roles.extend(("fresh_pcap:" + str(item["group"]), path) for item, path in zip(selected, pcap_paths))
        for role, path in roles:
            entry = entries[str(path.resolve())]
            input_rows.append(
                {
                    "role": role,
                    "basename": path.name,
                    "sha256": entry["sha256"],
                    "size_bytes": entry["size_bytes"],
                }
            )
        source = _portable_source(
            input_manifest,
            expected_input_sha,
            input_rows,
            eligible_rows,
            relation_rows,
            trusted_contract_sha256,
            policy_sha,
        )
        source_path = staging / "official_quality_source.json"
        atomic_json(source_path, source)
        source_sha = sha256_file(source_path)
        prepare_copy = staging / "trusted_prepare_receipt.json"
        _durable_write(prepare_copy, prepare_receipt_path.read_bytes())
        if sha256_file(prepare_copy) != trusted_prepare_receipt_sha256:
            raise ExportError("prepare receipt drift while making portable evidence")
        labels = {
            "schema_version": 2,
            "scope": LABEL_SCOPE,
            "source_kind": "official_labels",
            "synthetic": False,
            "independent_holdout": True,
            "source_artifact_path": "official_quality_source.json",
            "source_artifact_sha256": source_sha,
            "source_record_locator": "UNSW-NB15 official CSV rows over frozen fresh PCAP spans",
            "prepare_receipt_path": "trusted_prepare_receipt.json",
            "label_alignment": "canonical_bidirectional_5tuple_and_exact_flow_attack_time_overlap",
            "alignment_tolerance_s": 0.0,
            "extraction_policy": policy,
            "extraction_policy_sha256": policy_sha,
            "prepare_receipt_sha256": trusted_prepare_receipt_sha256,
            "records": label_rows,
            "eligible_events": eligible_rows,
            "sample_event_relations": relation_rows,
        }
        labels_path = staging / "quality_labels.json"
        atomic_json(labels_path, labels)
        predictions = {
            "schema_version": 2,
            "scope": PREDICTION_SCOPE,
            "synthetic": False,
            "generation_kind": "frozen_model_inference_on_independent_holdout",
            "candidate_id": "A09",
            "feature_profile": "invariant_no_ports_v1",
            "source_artifact_sha256": source_sha,
            "labels_sha256": sha256_file(labels_path),
            "model_sha256": sha256_file(model_path),
            "runtime_manifest_sha256": sha256_file(runtime_path),
            "prepare_receipt_sha256": trusted_prepare_receipt_sha256,
            "campaign_contract_sha256": trusted_contract_sha256,
            "extraction_policy_sha256": policy_sha,
            "decision_rule": "median_of_frozen_member_thresholds",
            "decision_threshold": threshold,
            "threshold_selected_during_export": False,
            "outer_unknown_read_for_tuning": False,
            "records": [
                {"sample_id": row["sample_id"], "prediction": int(score >= threshold), "score": score}
                for row, score in zip(label_rows, scores)
            ],
        }
        predictions_path = staging / "quality_predictions.json"
        atomic_json(predictions_path, predictions)
        _verify_snapshot(snapshot)
        receipt = {
            "schema_version": 2,
            "scope": RECEIPT_SCOPE,
            "candidate_id": "A09",
            "inference_only": True,
            "trained_or_calibrated": False,
            "historical_summary_consumed": False,
            "outer_unknown_read_for_tuning": False,
            "quality_qualified": False,
            "evaluation_groups": fresh,
            "adaptation_groups_excluded": list(contract["dataset_roles"]["adaptation_groups"]),
            "calibration_groups_excluded": list(contract["dataset_roles"]["calibration_groups"]),
            "trusted_prepare_receipt_sha256": trusted_prepare_receipt_sha256,
            "trusted_campaign_contract_sha256": trusted_contract_sha256,
            "trusted_exporter_sha256": trusted_exporter_sha256,
            "input_hash_manifest_sha256": expected_input_sha,
            "model_sha256": sha256_file(model_path),
            "runtime_manifest_sha256": sha256_file(runtime_path),
            "extraction_policy": policy,
            "extraction_policy_sha256": policy_sha,
            "source_artifact_sha256": source_sha,
            "labels_sha256": sha256_file(labels_path),
            "predictions_sha256": sha256_file(predictions_path),
            "sample_count": len(label_rows),
            "attack_count": positives,
            "benign_count": len(label_rows) - positives,
            "eligible_event_count": len(eligible_rows),
            "matched_event_count": len({row["event_id"] for row in relation_rows}),
            "capture_audit": capture_audit,
            "outputs": {
                "source": "official_quality_source.json",
                "prepare_receipt": "trusted_prepare_receipt.json",
                "labels": "quality_labels.json",
                "predictions": "quality_predictions.json",
                "receipt": "export_receipt.json",
                "manifest": "evidence.sha256",
                "complete": "COMPLETE.json",
            },
        }
        receipt_path = staging / "export_receipt.json"
        atomic_json(receipt_path, receipt)
        manifest_rows = []
        for name in (
            "official_quality_source.json",
            "trusted_prepare_receipt.json",
            "quality_labels.json",
            "quality_predictions.json",
            "export_receipt.json",
        ):
            manifest_rows.append("{}  {}\n".format(sha256_file(staging / name), name))
        manifest_path = staging / "evidence.sha256"
        _atomic_text(manifest_path, "".join(manifest_rows))
        atomic_json(
            staging / "COMPLETE.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_a09_current_279_quality_export_complete_v1",
                "complete": True,
                "evidence_manifest_sha256": sha256_file(manifest_path),
            },
        )
        _verify_snapshot(snapshot)
        _commit_directory(staging, final)
        return receipt
    except BaseException:
        if staging.exists():
            shutil.rmtree(str(staging), ignore_errors=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--trusted-contract-sha256", required=True)
    parser.add_argument("--trusted-exporter-sha256", required=True)
    parser.add_argument("--prepare-receipt", type=Path, required=True)
    parser.add_argument("--trusted-prepare-receipt-sha256", required=True)
    parser.add_argument("--input-hash-manifest", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        receipt = export_quality_evidence(
            output_dir=args.output_dir,
            contract_path=args.contract,
            trusted_contract_sha256=args.trusted_contract_sha256,
            trusted_exporter_sha256=args.trusted_exporter_sha256,
            prepare_receipt_path=args.prepare_receipt,
            trusted_prepare_receipt_sha256=args.trusted_prepare_receipt_sha256,
            input_hash_manifest_path=args.input_hash_manifest,
        )
    except (ExportError, OSError, UnicodeError, ValueError, KeyError, ImportError) as error:
        print(
            json.dumps(
                {
                    "schema_version": 2,
                    "scope": "hft_mgbs_a09_current_279_quality_export_error_v2",
                    "ok": False,
                    "quality_qualified": False,
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
