"""Independent two-stage release gate for the current 2.79 Mpps envelope.

This namespace deliberately does not alter the historical 10/12 Mpps unified
release chain.  Stage A proves one sealed v2 campaign is a Pareto candidate;
Stage B replays Stage A for at least two candidates before selecting a champion.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from hft_mgbs.current_hardware_279 import (
    compose_current_hardware_candidate_v2,
    compose_current_hardware_raw_run_v2,
)


POLICY_SCOPE = "hft_mgbs_current_hardware_2_79_two_stage_release_policy_v1"
CAMPAIGN_RECEIPT_SCOPE = "hft_mgbs_current_hardware_2_79_campaign_receipt_v1"
STAGE_A_MANIFEST_SCOPE = "hft_mgbs_current_hardware_2_79_stage_a_manifest_v1"
STAGE_A_AUDIT_SCOPE = "hft_mgbs_current_hardware_2_79_unified_candidate_audit_v1"
STAGE_B_MANIFEST_SCOPE = "hft_mgbs_current_hardware_2_79_stage_b_candidates_v1"
STAGE_B_AUDIT_SCOPE = "hft_mgbs_current_hardware_2_79_champion_release_v1"
RAW_RUN_SCOPE = "hft_mgbs_current_hardware_2_79_raw_run_v2"
CANDIDATE_AUDIT_SCOPE = "hft_mgbs_current_hardware_2_79_candidate_audit_v2"
MODES = ("normal", "fallback")
REPEATS = (1, 2, 3)

CAMPAIGN_IDENTITY_FIELDS = (
    "hardware_identity_sha256",
    "code_tree_sha256",
    "runner",
    "config",
    "capture_binary",
    "model",
    "runtime_manifest",
    "service_source",
    "engine_source",
    "service_launcher",
)
CANDIDATE_VARIANT_IDENTITY_FIELDS = CAMPAIGN_IDENTITY_FIELDS[1:]
RELEASE_BOUND_ARTIFACTS = (
    "runner",
    "config",
    "capture_binary",
    "model",
    "runtime_manifest",
    "service_source",
    "engine_source",
    "service_launcher",
)
EXPECTED_OBJECTIVES = {
    "minimum_mpps": "max",
    "grouped_macro_f1": "max",
    "independent_macro_f1": "max",
    "independent_attack_recall": "max",
    "independent_benign_recall": "max",
    "independent_auprc": "max",
    "independent_ece": "min",
    "ground_truth_event_recall": "max",
    "key_flow_coverage": "max",
    "packet_p999_us": "min",
    "flow_p999_us": "min",
    "kernel_to_feature_p999_us": "min",
    "end_to_end_p999_us": "min",
    "gpu_batch_max_us": "min",
    "fallback_recovery_s": "min",
}
EXPECTED_HARD_CONSTRAINTS = {
    "minimum_mpps": {"relation": ">=", "limit": 2.79, "unit": "Mpps"},
    "minimum_consecutive_complete_windows": {
        "relation": ">=", "limit": 15.0, "unit": "windows"
    },
    "grouped_macro_f1": {"relation": ">=", "limit": 0.90, "unit": "ratio"},
    "independent_macro_f1": {"relation": ">=", "limit": 0.70, "unit": "ratio"},
    "independent_attack_recall": {"relation": ">=", "limit": 0.72, "unit": "ratio"},
    "independent_benign_recall": {"relation": ">=", "limit": 0.93, "unit": "ratio"},
    "independent_auprc": {"relation": ">=", "limit": 0.45, "unit": "ratio"},
    "independent_ece": {"relation": "<=", "limit": 0.05, "unit": "ratio"},
    "ground_truth_event_recall": {"relation": ">=", "limit": 0.70, "unit": "ratio"},
    "packet_drop_count": {"relation": "<=", "limit": 0.0, "unit": "packets"},
    "key_flow_coverage": {"relation": ">=", "limit": 0.99, "unit": "ratio"},
    "packet_p99_us": {"relation": "<=", "limit": 100.0, "unit": "us"},
    "packet_p999_us": {"relation": "<=", "limit": 500.0, "unit": "us"},
    "flow_p99_us": {"relation": "<=", "limit": 5000.0, "unit": "us"},
    "flow_p999_us": {"relation": "<=", "limit": 50000.0, "unit": "us"},
    "kernel_to_feature_p99_us": {"relation": "<=", "limit": 10000.0, "unit": "us"},
    "kernel_to_feature_p999_us": {"relation": "<=", "limit": 50000.0, "unit": "us"},
    "end_to_end_p99_us": {"relation": "<=", "limit": 10000.0, "unit": "us"},
    "end_to_end_p999_us": {"relation": "<=", "limit": 50000.0, "unit": "us"},
    "gpu_batch_max_us": {"relation": "<=", "limit": 50000.0, "unit": "us"},
    "fallback_recovery_s": {"relation": "<=", "limit": 0.3, "unit": "s"},
}
EXPECTED_CHAMPION_ORDER = [
    {"field": "minimum_mpps", "direction": "max"},
    {"field": "independent_macro_f1", "direction": "max"},
    {"field": "end_to_end_p999_us", "direction": "min"},
    {"field": "packet_p999_us", "direction": "min"},
    {"field": "fallback_recovery_s", "direction": "min"},
]
STRUCTURED_RAW_ARTIFACTS = {
    "runtime_manifest",
    "pipeline_raw",
    "diagnostic_receipt",
    "pipeline_ready",
    "identity_receipt",
    "window_observations",
    "physical_resources",
    "service_resources",
}


def _duplicates(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON value: {token}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value, raw


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _add(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def _exact_value(observed: Any, expected: Any) -> bool:
    """Compare JSON claims without accepting bool/int coercion."""

    return type(observed) is type(expected) and observed == expected


def _exact_json(observed: Any, expected: Any) -> bool:
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(observed) == set(expected) and all(
            _exact_json(observed[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(observed) == len(expected) and all(
            _exact_json(left, right) for left, right in zip(observed, expected)
        )
    return observed == expected


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(str(path)))


def _has_symlink_component(path: Path) -> bool:
    absolute = _lexical_absolute(path)
    parts = absolute.parts
    if not parts:
        return True
    current = Path(parts[0])
    for part in parts[1:]:
        current /= part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def _strict_regular_file(path: Path) -> Path:
    lexical = _lexical_absolute(path)
    if _has_symlink_component(lexical):
        raise ValueError(f"symlinked path is forbidden: {path}")
    resolved = lexical.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"not a regular file: {path}")
    return resolved


def _regular_path(base: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value or any(c in value for c in "\r\n\x00"):
        return None
    candidate = Path(value)
    candidate = candidate if candidate.is_absolute() else base / candidate
    lexical = _lexical_absolute(candidate)
    if _has_symlink_component(lexical):
        return None
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _reference(
    base: Path, reference: Any, prefix: str, errors: list[str]
) -> tuple[Path | None, dict[str, Any] | None, bytes | None]:
    if not isinstance(reference, Mapping):
        _add(errors, prefix + ".reference")
        return None, None, None
    path = _regular_path(base, reference.get("path"))
    expected = reference.get("sha256")
    if path is None:
        _add(errors, prefix + ".path")
        return None, None, None
    try:
        value, raw = _load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        _add(errors, prefix + ".json")
        return path, None, None
    if not _is_sha(expected) or _sha256_bytes(raw) != expected:
        _add(errors, prefix + ".sha256")
    return path, value, raw


def _plain_reference(path: Path) -> dict[str, str]:
    resolved = _strict_regular_file(path)
    return {"path": str(resolved), "sha256": _sha256(resolved)}


def _load_policy(path: Path) -> tuple[dict[str, Any], str]:
    value, raw = _load_json(_strict_regular_file(path))
    if value.get("schema_version") != 1 or value.get("scope") != POLICY_SCOPE:
        raise ValueError("unsupported current-hardware release policy")
    boundary = value.get("claim_boundary")
    if not _exact_json(boundary, {
        "current_hardware_operating_point_only": True,
        "nominal_mpps": 2.79,
        "ten_mpps_or_line_rate_claim_allowed": False,
        "historical_release_chain_modified": False,
    }):
        raise ValueError("current-hardware release claim boundary drift")
    stage_a = value.get("stage_a")
    stage_b = value.get("stage_b")
    if not isinstance(stage_a, Mapping) or (
        stage_a.get("campaign_receipt_scope") != CAMPAIGN_RECEIPT_SCOPE
        or stage_a.get("required_normal_repeats") != 3
        or stage_a.get("required_fallback_repeats") != 3
        or stage_a.get("production_release_accepted") is not False
        or stage_a.get("selection_performed") is not False
        or stage_a.get("campaign_identity_fields") != list(CAMPAIGN_IDENTITY_FIELDS)
        or stage_a.get("candidate_variant_identity_fields")
        != list(CANDIDATE_VARIANT_IDENTITY_FIELDS)
        or stage_a.get("release_bound_artifacts") != list(RELEASE_BOUND_ARTIFACTS)
        or stage_a.get("identity_and_diagnostic_dual_binding_required") is not True
    ):
        raise ValueError("current-hardware Stage A policy drift")
    if not isinstance(stage_b, Mapping) or (
        stage_b.get("minimum_evaluated_candidates") != 2
        or not isinstance(stage_b.get("maximum_evaluated_candidates"), int)
        or stage_b.get("maximum_evaluated_candidates") < 2
        or stage_b.get("rehash_stage_a_and_campaign_receipt") is not True
        or stage_b.get("hard_gates_before_pareto") is not True
        or stage_b.get("single_candidate_release_allowed") is not False
        or stage_b.get("minimum_distinct_evaluation_identities") != 2
        or stage_b.get("production_release_scope")
        != "current_hardware_bcm57810_2.79_mpps_only"
    ):
        raise ValueError("current-hardware Stage B policy drift")
    objectives = stage_b.get("objectives")
    if not _exact_json(objectives, EXPECTED_OBJECTIVES):
        raise ValueError("current-hardware Stage B objectives drift")
    if not _exact_json(stage_b.get("hard_constraints"), EXPECTED_HARD_CONSTRAINTS):
        raise ValueError("current-hardware Stage B hard constraints drift")
    if not _exact_json(
        stage_b.get("champion_lexicographic_order"), EXPECTED_CHAMPION_ORDER
    ):
        raise ValueError("current-hardware Stage B champion order drift")
    return value, _sha256_bytes(raw)


def _policy_file(path: Path) -> tuple[dict[str, Any], str, Path]:
    resolved = _strict_regular_file(path)
    value, observed = _load_policy(resolved)
    try:
        stable = _sha256(resolved) == observed
    except OSError:
        stable = False
    if not stable:
        raise ValueError("current-hardware release policy changed during read")
    return value, observed, resolved


def _profile_reference(policy_path: Path, policy: Mapping[str, Any]) -> Path:
    profile = policy.get("profile")
    if not isinstance(profile, Mapping):
        raise ValueError("policy profile reference missing")
    path = _regular_path(policy_path.parent, profile.get("path"))
    if path is None or not _is_sha(profile.get("sha256")):
        raise ValueError("policy profile reference invalid")
    if _sha256(path) != profile["sha256"]:
        raise ValueError("policy profile hash drift")
    return path


def _candidate_run_paths(
    candidate_input_path: Path,
) -> dict[tuple[str, int], tuple[Path, str]]:
    candidate, _ = _load_json(candidate_input_path)
    root_value = candidate.get("evidence_root")
    if not isinstance(root_value, str) or not root_value:
        raise ValueError("candidate evidence root missing")
    root_candidate = Path(root_value)
    root_candidate = (
        root_candidate
        if root_candidate.is_absolute()
        else candidate_input_path.parent / root_candidate
    )
    lexical_root = _lexical_absolute(root_candidate)
    if _has_symlink_component(lexical_root):
        raise ValueError("candidate evidence root is a symlink")
    root = lexical_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("candidate evidence root is not a directory")
    result: dict[tuple[str, int], tuple[Path, str]] = {}
    references = candidate.get("raw_runs")
    if not isinstance(references, list):
        raise ValueError("candidate raw runs missing")
    for index, reference in enumerate(references):
        if not isinstance(reference, Mapping):
            raise ValueError(f"candidate raw run {index} invalid")
        path = _regular_path(root, reference.get("path"))
        expected = reference.get("sha256")
        if path is None or not _is_sha(expected) or _sha256(path) != expected:
            raise ValueError(f"candidate raw run {index} hash drift")
        value, raw = _load_json(path)
        if _sha256_bytes(raw) != expected:
            raise ValueError(f"candidate raw run {index} changed during read")
        key = (value.get("mode"), value.get("repeat_index"))
        if key in result:
            raise ValueError("candidate raw run matrix duplicated")
        result[key] = (path, expected)  # type: ignore[index]
    return result


def _campaign_identity(run: Mapping[str, Any]) -> dict[str, str]:
    artifacts = run.get("artifact_sha256")
    if not isinstance(artifacts, Mapping):
        raise ValueError("run artifact identity missing")
    identity = {
        "hardware_identity_sha256": run.get("hardware_identity_sha256"),
        "code_tree_sha256": run.get("code_tree_sha256"),
        **{name: artifacts.get(name) for name in CAMPAIGN_IDENTITY_FIELDS[2:]},
    }
    if set(identity) != set(CAMPAIGN_IDENTITY_FIELDS) or any(
        not _is_sha(value) for value in identity.values()
    ):
        raise ValueError("run artifact identity invalid")
    return identity  # type: ignore[return-value]


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return _sha256_bytes(raw)


def _variant_identity(identity: Mapping[str, str]) -> tuple[dict[str, str], str]:
    variant = {name: identity[name] for name in CANDIDATE_VARIANT_IDENTITY_FIELDS}
    return variant, _canonical_sha256(variant)


def _raw_input_tree_snapshot(
    input_path: Path,
    request: Mapping[str, Any],
    prefix: str,
    errors: list[str],
) -> dict[str, str]:
    root_value = request.get("evidence_root")
    if not isinstance(root_value, str) or not root_value:
        _add(errors, prefix + ".evidence_root")
        return {}
    candidate = Path(root_value)
    candidate = candidate if candidate.is_absolute() else input_path.parent / candidate
    lexical_root = _lexical_absolute(candidate)
    if _has_symlink_component(lexical_root):
        _add(errors, prefix + ".evidence_root.symlink")
        return {}
    try:
        root = lexical_root.resolve(strict=True)
    except (OSError, RuntimeError):
        _add(errors, prefix + ".evidence_root")
        return {}
    if not root.is_dir():
        _add(errors, prefix + ".evidence_root")
        return {}

    rows: list[tuple[str, Any, bool]] = [
        ("evidence_manifest", request.get("evidence_manifest"), False)
    ]
    artifacts = request.get("artifacts")
    if not isinstance(artifacts, Mapping):
        _add(errors, prefix + ".artifacts")
        artifacts = {}
    for name, reference in artifacts.items():
        rows.append(("artifacts." + str(name), reference, name in STRUCTURED_RAW_ARTIFACTS))
    pktgen = request.get("pktgen_devices")
    if not isinstance(pktgen, list):
        _add(errors, prefix + ".pktgen_devices")
        pktgen = []
    rows.extend((f"pktgen_devices.{index}", reference, False) for index, reference in enumerate(pktgen))
    quality = request.get("quality")
    if not isinstance(quality, Mapping):
        _add(errors, prefix + ".quality")
        quality = {}
    rows.extend(
        ("quality." + name, quality.get(name), True)
        for name in ("labels", "predictions")
    )
    fallback = request.get("fallback_events")
    if fallback is not None:
        rows.append(("fallback_events", fallback, True))

    snapshot: dict[str, str] = {}
    for name, reference, structured in rows:
        item = prefix + "." + name
        if not isinstance(reference, Mapping):
            _add(errors, item + ".reference")
            continue
        path = _regular_path(root, reference.get("path"))
        expected = reference.get("sha256")
        if path is None:
            _add(errors, item + ".path")
            continue
        if path == input_path:
            _add(errors, item + ".self_reference")
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            _add(errors, item + ".read")
            continue
        observed = _sha256_bytes(raw)
        if not _is_sha(expected) or expected != observed:
            _add(errors, item + ".sha256")
        key = str(path)
        if key in snapshot:
            _add(errors, item + ".aliased_reference")
        snapshot[key] = observed
        if name == "evidence_manifest":
            try:
                manifest_text = raw.decode("utf-8")
            except UnicodeError:
                _add(errors, item + ".encoding")
                continue
            manifest_names: set[str] = set()
            for line_index, line in enumerate(manifest_text.splitlines()):
                match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n\x00]+)", line)
                if match is None:
                    _add(errors, f"{item}.line.{line_index}")
                    continue
                manifest_sha, raw_name = match.groups()
                posix = PurePosixPath(raw_name)
                if (
                    posix.is_absolute()
                    or ".." in posix.parts
                    or raw_name in manifest_names
                ):
                    _add(errors, f"{item}.entry_path.{line_index}")
                    continue
                manifest_names.add(raw_name)
                entry_path = _regular_path(root, raw_name)
                if entry_path is None or entry_path == path or entry_path == input_path:
                    _add(errors, f"{item}.entry_file.{line_index}")
                    continue
                try:
                    entry_sha = _sha256(entry_path)
                except OSError:
                    _add(errors, f"{item}.entry_read.{line_index}")
                    continue
                if entry_sha != manifest_sha:
                    _add(errors, f"{item}.entry_sha256.{line_index}")
                snapshot["manifest_entry:" + str(entry_path)] = entry_sha
        if structured:
            try:
                parsed, parsed_raw = _load_json(path)
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                _add(errors, item + ".strict_json")
                continue
            if _sha256_bytes(parsed_raw) != observed or not isinstance(parsed, dict):
                _add(errors, item + ".stability")
    expected_binding = {
        name: (artifacts.get(name) or {}).get("sha256")
        if isinstance(artifacts.get(name), Mapping)
        else None
        for name in RELEASE_BOUND_ARTIFACTS
    }
    if any(not _is_sha(value) for value in expected_binding.values()):
        _add(errors, prefix + ".release_identity.artifacts")
        return snapshot

    def structured_artifact(name: str) -> dict[str, Any] | None:
        reference = artifacts.get(name)
        if not isinstance(reference, Mapping):
            return None
        path = _regular_path(root, reference.get("path"))
        if path is None:
            return None
        try:
            value, raw = _load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            return None
        return value if _sha256_bytes(raw) == reference.get("sha256") else None

    identity = structured_artifact("identity_receipt")
    diagnostic = structured_artifact("diagnostic_receipt")
    if not isinstance(identity, Mapping):
        _add(errors, prefix + ".release_identity.identity_receipt")
        return snapshot
    if identity.get("release_artifact_sha256") != expected_binding:
        _add(errors, prefix + ".release_identity.identity_binding")
    if not isinstance(diagnostic, Mapping):
        _add(errors, prefix + ".release_identity.diagnostic_receipt")
        return snapshot
    if diagnostic.get("release_artifact_sha256") != expected_binding:
        _add(errors, prefix + ".release_identity.diagnostic_binding")
    for field in (
        "campaign_id",
        "candidate_id",
        "backend",
        "mode",
        "repeat_index",
        "run_id",
        "generator_run_id",
        "generator_process_start_ticks",
        "hardware_identity_sha256",
        "code_tree_sha256",
    ):
        if diagnostic.get(field) != identity.get(field):
            _add(errors, prefix + ".release_identity.diagnostic_" + field)
    return snapshot


def _derived_metrics(
    candidate_audit: Mapping[str, Any], runs: Iterable[Mapping[str, Any]]
) -> dict[str, float]:
    materialized = list(runs)
    metrics = candidate_audit.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("candidate metrics missing")
    result = {name: float(value) for name, value in metrics.items()}
    windows = [
        window
        for run in materialized
        for window in (run.get("windows") or [])
        if isinstance(window, Mapping)
    ]
    if not windows:
        raise ValueError("candidate windows missing")

    def extrema(latency: str, field: str) -> float:
        values = [
            ((window.get("derived_latency") or {}).get(latency) or {}).get(field)
            for window in windows
        ]
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
            raise ValueError(f"candidate latency missing: {latency}.{field}")
        return max(float(value) for value in values)

    result.update(
        {
            "packet_drop_count": float(
                sum(int(window.get("derived_loss", -1)) for window in windows)
            ),
            "key_flow_coverage": min(
                float(window.get("derived_key_flow_coverage", -1)) for window in windows
            ),
            "packet_p99_us": extrema("packet_latency_us", "p99_us"),
            "packet_p999_us": extrema("packet_latency_us", "p999_us"),
            "flow_p99_us": extrema("flow_latency_us", "p99_us"),
            "flow_p999_us": extrema("flow_latency_us", "p999_us"),
            "kernel_to_feature_p99_us": extrema(
                "kernel_to_feature_latency_us", "p99_us"
            ),
            "kernel_to_feature_p999_us": extrema(
                "kernel_to_feature_latency_us", "p999_us"
            ),
            "end_to_end_p99_us": extrema("end_to_end_latency_us", "p99_us"),
            "end_to_end_p999_us": extrema("end_to_end_latency_us", "p999_us"),
            "gpu_batch_max_us": extrema("gpu_batch_latency_us", "max_us"),
            "fallback_recovery_s": max(
                float((run.get("fallback_trial") or {}).get("recovery_ms", 0.0))
                for run in materialized
                if run.get("mode") == "fallback"
            )
            / 1000.0,
        }
    )
    if any(not math.isfinite(value) for value in result.values()):
        raise ValueError("candidate metrics are non-finite")
    return result


def _hard_gate_errors(
    metrics: Mapping[str, Any], hard_constraints: Mapping[str, Any], prefix: str
) -> list[str]:
    errors: list[str] = []
    for name, expected in EXPECTED_HARD_CONSTRAINTS.items():
        if hard_constraints.get(name) != expected:
            _add(errors, prefix + ".contract." + name)
            continue
        value = metrics.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            _add(errors, prefix + ".metric." + name)
            continue
        number = float(value)
        relation = expected["relation"]
        limit = float(expected["limit"])
        if (relation == ">=" and number < limit) or (
            relation == "<=" and number > limit
        ):
            _add(errors, prefix + ".failed." + name)
    return errors


def _recompute_campaign(
    policy_path: Path,
    policy: Mapping[str, Any],
    policy_sha: str,
    receipt_path: Path,
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if receipt.get("schema_version") != 1:
        _add(errors, "campaign_receipt.schema_version")
    if receipt.get("scope") != CAMPAIGN_RECEIPT_SCOPE:
        _add(errors, "campaign_receipt.scope")
    if receipt.get("policy_sha256") != policy_sha:
        _add(errors, "campaign_receipt.policy_sha256")
    try:
        frozen_profile = _profile_reference(policy_path, policy)
    except (OSError, ValueError):
        _add(errors, "campaign_receipt.policy_profile")
        frozen_profile = None
    profile_path, _profile, profile_raw = _reference(
        receipt_path.parent,
        receipt.get("profile"),
        "campaign_receipt.profile",
        errors,
    )
    if frozen_profile is not None and profile_path != frozen_profile:
        _add(errors, "campaign_receipt.profile.path")
    candidate_input_path, candidate_input, candidate_input_raw = _reference(
        receipt_path.parent,
        receipt.get("candidate_input"),
        "campaign_receipt.candidate_input",
        errors,
    )
    candidate_audit_path, stored_candidate_audit, candidate_audit_raw = _reference(
        receipt_path.parent,
        receipt.get("candidate_audit"),
        "campaign_receipt.candidate_audit",
        errors,
    )
    raw_references = receipt.get("raw_run_inputs")
    if not isinstance(raw_references, list):
        _add(errors, "campaign_receipt.raw_run_inputs")
        raw_references = []
    recomputed_runs: dict[tuple[str, int], dict[str, Any]] = {}
    raw_input_hashes: set[str] = set()
    for index, reference in enumerate(raw_references):
        path, value, raw = _reference(
            receipt_path.parent,
            reference,
            f"campaign_receipt.raw_run_inputs.{index}",
            errors,
        )
        if path is None or value is None or raw is None or frozen_profile is None:
            continue
        raw_input_hashes.add(_sha256_bytes(raw))
        tree_before = _raw_input_tree_snapshot(
            path,
            value,
            f"campaign_receipt.raw_run_inputs.{index}.tree",
            errors,
        )
        result = compose_current_hardware_raw_run_v2(frozen_profile, path)
        tree_after = _raw_input_tree_snapshot(
            path,
            value,
            f"campaign_receipt.raw_run_inputs.{index}.tree_after",
            errors,
        )
        if tree_before != tree_after:
            _add(errors, f"campaign_receipt.raw_run_inputs.{index}.tree.stability")
        initial_digest = _sha256_bytes(raw)
        try:
            stable = _sha256(path) == initial_digest
        except OSError:
            stable = False
        if result.get("input_sha256") != initial_digest or not stable:
            _add(errors, f"campaign_receipt.raw_run_inputs.{index}.stability")
        key = (result.get("mode"), result.get("repeat_index"))
        if (
            reference.get("mode") != result.get("mode")
            or reference.get("repeat_index") != result.get("repeat_index")
        ):
            _add(errors, f"campaign_receipt.raw_run_inputs.{index}.identity")
        if (
            result.get("scope") != RAW_RUN_SCOPE
            or result.get("audit_complete") is not True
            or result.get("run_qualified") is not True
            or result.get("errors") != []
            or key in recomputed_runs
        ):
            _add(errors, f"campaign_receipt.raw_run_inputs.{index}.recompute")
            continue
        recomputed_runs[key] = result  # type: ignore[index]
    expected_matrix = {(mode, repeat) for mode in MODES for repeat in REPEATS}
    if (
        set(recomputed_runs) != expected_matrix
        or len(raw_references) != 6
        or len(raw_input_hashes) != 6
    ):
        _add(errors, "campaign_receipt.raw_run_matrix")

    if candidate_input_path is not None and candidate_input is not None:
        try:
            stored_run_paths = _candidate_run_paths(candidate_input_path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            _add(errors, "campaign_receipt.candidate_input.raw_runs")
            stored_run_paths = {}
        if set(stored_run_paths) != expected_matrix:
            _add(errors, "campaign_receipt.candidate_input.raw_run_matrix")
        for key, result in recomputed_runs.items():
            stored_reference = stored_run_paths.get(key)
            if stored_reference is None:
                continue
            stored_path, stored_expected = stored_reference
            try:
                stored, stored_raw = _load_json(stored_path)
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
                _add(errors, f"campaign_receipt.raw_result.{key[0]}.{key[1]}.json")
                continue
            try:
                stable = (
                    _sha256_bytes(stored_raw) == stored_expected
                    and _sha256(stored_path) == stored_expected
                )
            except OSError:
                stable = False
            if not stable:
                _add(errors, f"campaign_receipt.raw_result.{key[0]}.{key[1]}.stability")
            if not _exact_json(stored, result):
                _add(errors, f"campaign_receipt.raw_result.{key[0]}.{key[1]}.recomputed")

    recomputed_candidate = None
    if frozen_profile is not None and candidate_input_path is not None:
        recomputed_candidate = compose_current_hardware_candidate_v2(
            frozen_profile, candidate_input_path
        )
        expected_candidate_input_sha = (
            _sha256_bytes(candidate_input_raw)
            if candidate_input_raw is not None
            else None
        )
        try:
            candidate_input_stable = (
                expected_candidate_input_sha is not None
                and _sha256(candidate_input_path) == expected_candidate_input_sha
            )
        except OSError:
            candidate_input_stable = False
        if (
            recomputed_candidate.get("input_sha256") != expected_candidate_input_sha
            or not candidate_input_stable
        ):
            _add(errors, "campaign_receipt.candidate_input.stability")
        if (
            recomputed_candidate.get("scope") != CANDIDATE_AUDIT_SCOPE
            or recomputed_candidate.get("audit_complete") is not True
            or recomputed_candidate.get("candidate_evidence_qualified") is not True
            or recomputed_candidate.get("full_pipeline_qualified") is not True
            or recomputed_candidate.get("production_release_accepted") is not False
            or recomputed_candidate.get("final_pareto_ingestion_allowed") is not False
            or recomputed_candidate.get("errors") != []
        ):
            _add(errors, "campaign_receipt.candidate_recompute")
        if not _exact_json(stored_candidate_audit, recomputed_candidate):
            _add(errors, "campaign_receipt.candidate_audit.recomputed")
        if candidate_audit_path is not None and candidate_audit_raw is not None:
            try:
                candidate_audit_stable = (
                    _sha256(candidate_audit_path) == _sha256_bytes(candidate_audit_raw)
                )
            except OSError:
                candidate_audit_stable = False
            if not candidate_audit_stable:
                _add(errors, "campaign_receipt.candidate_audit.stability")

    if recomputed_candidate is not None:
        for field in ("campaign_id", "candidate_id", "backend"):
            if receipt.get(field) != recomputed_candidate.get(field):
                _add(errors, "campaign_receipt." + field)
    declarations = {
        "normal_run_count": 3,
        "fallback_run_count": 3,
        "candidate_evidence_qualified": True,
        "full_pipeline_qualified": True,
        "selection_performed": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": True,
        "accepted": False,
        "selected_candidate": None,
        "ten_mpps_or_line_rate_claim_allowed": False,
    }
    for name, expected in declarations.items():
        if not _exact_value(receipt.get(name), expected):
            _add(errors, "campaign_receipt." + name)
    derived = None
    if recomputed_candidate is not None and set(recomputed_runs) == expected_matrix:
        try:
            metrics = _derived_metrics(recomputed_candidate, recomputed_runs.values())
            identities = [_campaign_identity(run) for run in recomputed_runs.values()]
            if any(identity != identities[0] for identity in identities[1:]):
                raise ValueError("campaign artifact identity drift")
            variant_identity, variant_identity_sha = _variant_identity(identities[0])
        except (TypeError, ValueError):
            _add(errors, "campaign_receipt.metrics.recompute")
        else:
            if not _exact_json(receipt.get("metrics"), metrics):
                _add(errors, "campaign_receipt.metrics")
            if not _exact_json(receipt.get("campaign_identity"), identities[0]):
                _add(errors, "campaign_receipt.campaign_identity")
            if not _exact_json(
                receipt.get("candidate_variant_identity"), variant_identity
            ):
                _add(errors, "campaign_receipt.candidate_variant_identity")
            if receipt.get("candidate_variant_identity_sha256") != variant_identity_sha:
                _add(errors, "campaign_receipt.candidate_variant_identity_sha256")
            derived = {
                "campaign_id": recomputed_candidate.get("campaign_id"),
                "candidate_id": recomputed_candidate.get("candidate_id"),
                "backend": recomputed_candidate.get("backend"),
                "profile_sha256": recomputed_candidate.get("profile_sha256"),
                "candidate_input_sha256": recomputed_candidate.get("input_sha256"),
                "verified_normal_run_count": 3,
                "verified_fallback_run_count": 3,
                "campaign_identity": identities[0],
                "candidate_variant_identity": variant_identity,
                "candidate_variant_identity_sha256": variant_identity_sha,
                "metrics": metrics,
            }
    for name, path, raw in (
        ("profile", profile_path, profile_raw),
        ("candidate_input", candidate_input_path, candidate_input_raw),
        ("candidate_audit", candidate_audit_path, candidate_audit_raw),
    ):
        if path is not None and raw is not None:
            try:
                stable = _sha256(path) == _sha256_bytes(raw)
            except OSError:
                stable = False
            if not stable:
                _add(errors, "campaign_receipt." + name + ".stability")
    return (derived if not errors else None), errors


def build_current_hardware_campaign_receipt(
    policy_path: Path,
    profile_path: Path,
    candidate_input_path: Path,
    candidate_audit_path: Path,
    raw_run_input_paths: Sequence[Path],
) -> dict[str, Any]:
    """Seal a v2 campaign; this receipt is still non-production Stage-A input."""

    policy, policy_sha, policy_path = _policy_file(policy_path)
    frozen_profile = _profile_reference(policy_path, policy)
    if _strict_regular_file(profile_path) != frozen_profile:
        raise ValueError("profile does not match the policy-frozen profile")
    candidate_audit_path = _strict_regular_file(candidate_audit_path)
    candidate_input_path = _strict_regular_file(candidate_input_path)
    candidate_audit, _ = _load_json(candidate_audit_path)
    recomputed = compose_current_hardware_candidate_v2(
        frozen_profile, candidate_input_path
    )
    if not _exact_json(candidate_audit, recomputed):
        raise ValueError("stored candidate audit does not match recomputation")
    runs = [
        compose_current_hardware_raw_run_v2(frozen_profile, _strict_regular_file(path))
        for path in raw_run_input_paths
    ]
    matrix = {(run.get("mode"), run.get("repeat_index")): run for run in runs}
    expected = {(mode, repeat) for mode in MODES for repeat in REPEATS}
    if (
        len(runs) != 6
        or set(matrix) != expected
        or any(run.get("run_qualified") is not True or run.get("errors") != [] for run in runs)
        or recomputed.get("candidate_evidence_qualified") is not True
    ):
        raise ValueError("campaign is not a qualified 3 normal + 3 fallback matrix")
    stored_run_paths = _candidate_run_paths(candidate_input_path)
    if set(stored_run_paths) != expected:
        raise ValueError("candidate input does not contain the same six-run matrix")
    for key, result in matrix.items():
        stored_path, stored_expected = stored_run_paths[key]
        stored, stored_raw = _load_json(stored_path)
        if _sha256_bytes(stored_raw) != stored_expected:
            raise ValueError("candidate raw audit changed during receipt sealing")
        if not _exact_json(stored, result):
            raise ValueError(
                f"raw input recomputation does not match candidate audit {key[0]}-{key[1]}"
            )
    metrics = _derived_metrics(recomputed, runs)
    identities = [_campaign_identity(run) for run in runs]
    if any(identity != identities[0] for identity in identities[1:]):
        raise ValueError("campaign artifact identity drift")
    variant_identity, variant_identity_sha = _variant_identity(identities[0])
    receipt = {
        "schema_version": 1,
        "scope": CAMPAIGN_RECEIPT_SCOPE,
        "policy_sha256": policy_sha,
        "profile": _plain_reference(frozen_profile),
        "candidate_input": _plain_reference(candidate_input_path),
        "candidate_audit": _plain_reference(candidate_audit_path),
        "raw_run_inputs": [
            {
                **_plain_reference(path),
                "mode": result.get("mode"),
                "repeat_index": result.get("repeat_index"),
            }
            for path, result in zip(raw_run_input_paths, runs)
        ],
        "campaign_id": recomputed.get("campaign_id"),
        "candidate_id": recomputed.get("candidate_id"),
        "backend": recomputed.get("backend"),
        "campaign_identity": identities[0],
        "candidate_variant_identity": variant_identity,
        "candidate_variant_identity_sha256": variant_identity_sha,
        "normal_run_count": 3,
        "fallback_run_count": 3,
        "metrics": metrics,
        "candidate_evidence_qualified": True,
        "full_pipeline_qualified": True,
        "selection_performed": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": True,
        "accepted": False,
        "selected_candidate": None,
        "ten_mpps_or_line_rate_claim_allowed": False,
    }
    return receipt


def _stage_a_failure(errors: Sequence[str], manifest_sha: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": STAGE_A_AUDIT_SCOPE,
        "input_manifest_sha256": manifest_sha,
        "campaign_id": None,
        "candidate_id": None,
        "backend": None,
        "campaign_receipt_sha256": None,
        "campaign_identity": None,
        "candidate_variant_identity": None,
        "candidate_variant_identity_sha256": None,
        "verified_normal_run_count": 0,
        "verified_fallback_run_count": 0,
        "metrics": None,
        "audit_complete": True,
        "candidate_evidence_accepted": False,
        "full_pipeline_qualified": False,
        "selection_performed": False,
        "selected_candidate": None,
        "production_release_accepted": False,
        "accepted": False,
        "ten_mpps_or_line_rate_claim_allowed": False,
        "final_pareto_ingestion_allowed": False,
        "errors": list(errors),
    }


def audit_current_hardware_stage_a(
    policy_path: Path, manifest_path: Path
) -> dict[str, Any]:
    """Rehash and replay one campaign.  Stage A can never grant production."""

    errors: list[str] = []
    try:
        policy, policy_sha, policy_resolved = _policy_file(policy_path)
        manifest_resolved = _strict_regular_file(manifest_path)
        manifest, manifest_raw = _load_json(manifest_resolved)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _stage_a_failure([f"stage_a.input:{type(error).__name__}:{error}"])
    manifest_sha = _sha256_bytes(manifest_raw)
    if manifest.get("schema_version") != 1 or manifest.get("scope") != STAGE_A_MANIFEST_SCOPE:
        _add(errors, "stage_a.manifest.scope")
    if manifest.get("policy_sha256") != policy_sha:
        _add(errors, "stage_a.manifest.policy_sha256")
    receipt_path, receipt, receipt_raw = _reference(
        manifest_resolved.parent,
        manifest.get("campaign_receipt"),
        "stage_a.campaign_receipt",
        errors,
    )
    derived = None
    if receipt_path is not None and receipt is not None and receipt_raw is not None:
        derived, campaign_errors = _recompute_campaign(
            policy_resolved, policy, policy_sha, receipt_path, receipt
        )
        errors.extend(error for error in campaign_errors if error not in errors)
    accepted = derived is not None and not errors
    expected_claims = {
        "candidate_evidence_accepted": accepted,
        "full_pipeline_qualified": accepted,
        "selection_performed": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": accepted,
        "accepted": False,
        "selected_candidate": None,
        "ten_mpps_or_line_rate_claim_allowed": False,
    }
    claims = manifest.get("claimed_final_state")
    if not isinstance(claims, Mapping):
        _add(errors, "stage_a.manifest.claimed_final_state")
    else:
        if set(claims) != set(expected_claims):
            _add(errors, "stage_a.manifest.claimed_final_state.keys")
        for name, expected in expected_claims.items():
            if not _exact_value(claims.get(name), expected):
                _add(errors, "stage_a.manifest.claim." + name)
    accepted = accepted and not errors
    try:
        if _sha256(manifest_resolved) != manifest_sha:
            _add(errors, "stage_a.manifest.stability")
        if _sha256(policy_resolved) != policy_sha:
            _add(errors, "stage_a.policy.stability")
        if (
            receipt_path is not None
            and receipt_raw is not None
            and _sha256(receipt_path) != _sha256_bytes(receipt_raw)
        ):
            _add(errors, "stage_a.campaign_receipt.stability")
    except OSError:
        _add(errors, "stage_a.input.stability")
    accepted = accepted and not errors
    result = _stage_a_failure(errors, manifest_sha)
    if derived is not None:
        result.update(derived)
    result.update(
        {
            "campaign_receipt_sha256": (
                _sha256_bytes(receipt_raw) if receipt_raw is not None else None
            ),
            "candidate_evidence_accepted": accepted,
            "full_pipeline_qualified": accepted,
            "final_pareto_ingestion_allowed": accepted,
            "errors": errors,
        }
    )
    return result


def _dominates(
    left: Mapping[str, float],
    right: Mapping[str, float],
    objectives: Mapping[str, str],
) -> bool:
    weak = True
    strict = False
    for name, direction in objectives.items():
        a, b = left[name], right[name]
        if direction == "max":
            weak = weak and a >= b
            strict = strict or a > b
        else:
            weak = weak and a <= b
            strict = strict or a < b
    return weak and strict


def _champion_key(
    candidate: Mapping[str, Any], order: Sequence[Mapping[str, str]]
) -> tuple[Any, ...]:
    metrics = candidate["metrics"]
    key: list[Any] = []
    for item in order:
        field, direction = item["field"], item["direction"]
        value = float(metrics[field])
        key.append(-value if direction == "max" else value)
    key.append(candidate["candidate_id"])
    return tuple(key)


def _stage_b_failure(errors: Sequence[str], manifest_sha: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": STAGE_B_AUDIT_SCOPE,
        "input_manifest_sha256": manifest_sha,
        "audit_complete": True,
        "evaluated_candidate_count": 0,
        "evaluated_candidates": [],
        "pareto_front": [],
        "champion_id": None,
        "selection_performed": False,
        "current_hardware_operating_point_release_accepted": False,
        "production_release_scope": None,
        "production_release_accepted": False,
        "accepted": False,
        "ten_mpps_or_line_rate_claim_allowed": False,
        "errors": list(errors),
    }


def select_current_hardware_stage_b(
    policy_path: Path, manifest_path: Path
) -> dict[str, Any]:
    """Recompute every Stage-A candidate, then select a scoped 2.79 champion."""

    errors: list[str] = []
    try:
        policy, policy_sha, policy_resolved = _policy_file(policy_path)
        manifest_resolved = _strict_regular_file(manifest_path)
        manifest, manifest_raw = _load_json(manifest_resolved)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _stage_b_failure([f"stage_b.input:{type(error).__name__}:{error}"])
    manifest_sha = _sha256_bytes(manifest_raw)
    if manifest.get("schema_version") != 1 or manifest.get("scope") != STAGE_B_MANIFEST_SCOPE:
        _add(errors, "stage_b.manifest.scope")
    if manifest.get("policy_sha256") != policy_sha:
        _add(errors, "stage_b.manifest.policy_sha256")
    references = manifest.get("candidates")
    if not isinstance(references, list):
        _add(errors, "stage_b.candidates")
        references = []
    stage_b = policy["stage_b"]
    minimum = int(stage_b["minimum_evaluated_candidates"])
    maximum = int(stage_b["maximum_evaluated_candidates"])
    if len(references) < minimum:
        _add(errors, f"stage_b.candidate_count_below_min:{len(references)}<{minimum}")
    if len(references) > maximum:
        _add(errors, f"stage_b.candidate_count_above_max:{len(references)}>{maximum}")
    evaluated: list[dict[str, Any]] = []
    candidate_ids: list[str] = []
    receipt_hashes: list[str] = []
    evaluation_identity_hashes: list[str] = []
    for index, reference in enumerate(references):
        prefix = f"stage_b.candidates.{index}"
        if not isinstance(reference, Mapping):
            _add(errors, prefix + ".reference")
            continue
        stage_a_manifest_path, _stage_a_manifest, stage_a_manifest_raw = _reference(
            manifest_resolved.parent,
            reference.get("stage_a_manifest"),
            prefix + ".stage_a_manifest",
            errors,
        )
        unified_path, unified, unified_raw = _reference(
            manifest_resolved.parent,
            reference.get("unified_candidate_evidence_audit"),
            prefix + ".unified",
            errors,
        )
        receipt_path, receipt, receipt_raw = _reference(
            manifest_resolved.parent,
            reference.get("campaign_receipt"),
            prefix + ".campaign_receipt",
            errors,
        )
        if stage_a_manifest_path is None or unified is None or unified_path is None:
            continue
        recomputed_unified = audit_current_hardware_stage_a(
            policy_resolved, stage_a_manifest_path
        )
        try:
            stable_stage_a = (
                stage_a_manifest_raw is not None
                and _sha256(stage_a_manifest_path) == _sha256_bytes(stage_a_manifest_raw)
            )
            stable_unified = (
                unified_raw is not None
                and _sha256(unified_path) == _sha256_bytes(unified_raw)
            )
            stable_receipt = (
                receipt_path is not None
                and receipt_raw is not None
                and _sha256(receipt_path) == _sha256_bytes(receipt_raw)
            )
        except OSError:
            stable_stage_a = stable_unified = stable_receipt = False
        if not stable_stage_a:
            _add(errors, prefix + ".stage_a_manifest.stability")
        if not stable_unified:
            _add(errors, prefix + ".unified.stability")
        if not stable_receipt:
            _add(errors, prefix + ".campaign_receipt.stability")
        if not (stable_stage_a and stable_unified and stable_receipt):
            continue
        if not _exact_json(unified, recomputed_unified):
            _add(errors, prefix + ".unified.recomputed")
            continue
        if (
            recomputed_unified.get("candidate_evidence_accepted") is not True
            or recomputed_unified.get("full_pipeline_qualified") is not True
            or recomputed_unified.get("final_pareto_ingestion_allowed") is not True
            or recomputed_unified.get("selection_performed") is not False
            or recomputed_unified.get("production_release_accepted") is not False
            or recomputed_unified.get("errors") != []
        ):
            _add(errors, prefix + ".unified.not_eligible")
            continue
        if receipt_path is None or receipt is None or receipt_raw is None:
            continue
        direct_receipt_sha = _sha256_bytes(receipt_raw)
        if recomputed_unified.get("campaign_receipt_sha256") != direct_receipt_sha:
            _add(errors, prefix + ".campaign_receipt.binding")
            continue
        stage_a_manifest, _ = _load_json(stage_a_manifest_path)
        stage_a_receipt = stage_a_manifest.get("campaign_receipt")
        if not isinstance(stage_a_receipt, Mapping):
            _add(errors, prefix + ".campaign_receipt.stage_a_binding")
            continue
        bound_path = _regular_path(stage_a_manifest_path.parent, stage_a_receipt.get("path"))
        if bound_path != receipt_path or stage_a_receipt.get("sha256") != direct_receipt_sha:
            _add(errors, prefix + ".campaign_receipt.stage_a_binding")
            continue
        candidate_id = recomputed_unified.get("candidate_id")
        if reference.get("candidate_id") != candidate_id:
            _add(errors, prefix + ".candidate_id")
            continue
        metrics = recomputed_unified.get("metrics")
        objectives = stage_b["objectives"]
        if not isinstance(metrics, Mapping) or any(
            not isinstance(metrics.get(name), (int, float))
            or not math.isfinite(float(metrics[name]))
            for name in objectives
        ):
            _add(errors, prefix + ".metrics")
            continue
        hard_gate_failures = _hard_gate_errors(
            metrics, stage_b["hard_constraints"], prefix + ".hard_gate"
        )
        if hard_gate_failures:
            errors.extend(
                error for error in hard_gate_failures if error not in errors
            )
            continue
        candidate_variant_identity_sha = recomputed_unified.get(
            "candidate_variant_identity_sha256"
        )
        candidate_variant_identity = recomputed_unified.get("candidate_variant_identity")
        if (
            not _is_sha(candidate_variant_identity_sha)
            or not isinstance(candidate_variant_identity, Mapping)
            or set(candidate_variant_identity) != set(CANDIDATE_VARIANT_IDENTITY_FIELDS)
            or any(not _is_sha(value) for value in candidate_variant_identity.values())
            or _canonical_sha256(candidate_variant_identity)
            != candidate_variant_identity_sha
        ):
            _add(errors, prefix + ".evaluation_identity")
            continue
        evaluation_identity = {
            "backend": recomputed_unified.get("backend"),
            "candidate_variant_identity_sha256": candidate_variant_identity_sha,
        }
        if not isinstance(evaluation_identity["backend"], str) or not evaluation_identity["backend"]:
            _add(errors, prefix + ".evaluation_identity.backend")
            continue
        evaluation_identity_sha = _canonical_sha256(evaluation_identity)
        candidate_ids.append(str(candidate_id))
        receipt_hashes.append(direct_receipt_sha)
        evaluation_identity_hashes.append(evaluation_identity_sha)
        evaluated.append(
            {
                "candidate_id": candidate_id,
                "campaign_id": recomputed_unified.get("campaign_id"),
                "backend": recomputed_unified.get("backend"),
                "campaign_receipt_sha256": direct_receipt_sha,
                "unified_candidate_evidence_audit_sha256": _sha256(unified_path),
                "evaluation_identity_sha256": evaluation_identity_sha,
                "candidate_artifact_variant_identity_sha256": candidate_variant_identity_sha,
                "metrics": {name: float(value) for name, value in metrics.items()},
            }
        )
    if len(set(candidate_ids)) != len(candidate_ids):
        _add(errors, "stage_b.duplicate_candidate_id")
    if len(set(receipt_hashes)) != len(receipt_hashes):
        _add(errors, "stage_b.duplicate_campaign_receipt")
    if len(set(evaluation_identity_hashes)) != len(evaluation_identity_hashes):
        _add(errors, "stage_b.duplicate_evaluation_identity")
    if len(evaluated) < minimum:
        _add(errors, f"stage_b.evaluated_candidate_count_below_min:{len(evaluated)}<{minimum}")
    objectives = stage_b["objectives"]
    front = [
        item
        for item in evaluated
        if not any(
            other is not item
            and _dominates(other["metrics"], item["metrics"], objectives)
            for other in evaluated
        )
    ]
    order = stage_b.get("champion_lexicographic_order")
    champion = min(front, key=lambda item: _champion_key(item, order)) if front and order else None
    selectable = len(evaluated) >= minimum and champion is not None and not errors
    claims = manifest.get("claimed_final_state")
    expected_claims = {
        "selection_performed": selectable,
        "production_release_accepted": selectable,
        "current_hardware_operating_point_release_accepted": selectable,
        "production_release_scope": (
            "current_hardware_bcm57810_2.79_mpps_only" if selectable else None
        ),
        "accepted": selectable,
        "ten_mpps_or_line_rate_claim_allowed": False,
    }
    if not isinstance(claims, Mapping):
        _add(errors, "stage_b.manifest.claimed_final_state")
    else:
        if set(claims) != set(expected_claims):
            _add(errors, "stage_b.manifest.claimed_final_state.keys")
        for name, expected in expected_claims.items():
            if not _exact_value(claims.get(name), expected):
                _add(errors, "stage_b.manifest.claim." + name)
    accepted = selectable and not errors
    try:
        if _sha256(manifest_resolved) != manifest_sha:
            _add(errors, "stage_b.manifest.stability")
        if _sha256(policy_resolved) != policy_sha:
            _add(errors, "stage_b.policy.stability")
    except OSError:
        _add(errors, "stage_b.input.stability")
    accepted = accepted and not errors
    result = _stage_b_failure(errors, manifest_sha)
    result.update(
        {
            "evaluated_candidate_count": len(evaluated),
            "evaluated_candidates": sorted(evaluated, key=lambda item: item["candidate_id"]),
            "pareto_front": sorted(item["candidate_id"] for item in front) if accepted else [],
            "champion_id": champion["candidate_id"] if accepted and champion else None,
            "selection_performed": accepted,
            "current_hardware_operating_point_release_accepted": accepted,
            "production_release_scope": (
                "current_hardware_bcm57810_2.79_mpps_only" if accepted else None
            ),
            "production_release_accepted": accepted,
            "accepted": accepted,
            "errors": errors,
        }
    )
    return result
