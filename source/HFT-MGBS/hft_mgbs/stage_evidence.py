"""Recompute R1--R4 production evidence from raw, sealed stage receipts.

The module deliberately ignores any self-reported qualification state.  It is
an independent building block for the unified release auditor: callers still
have to verify the receipt file and evidence-manifest hashes before passing the
decoded JSON object here.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STAGES = ("r1", "r2", "r3", "r4_24h", "r4_72h")
PARETO_NUMERIC_FIELDS = (
    "grouped_macro_f1",
    "independent_macro_f1",
    "independent_attack_recall",
    "independent_benign_recall",
    "independent_auprc",
    "independent_ece",
    "ground_truth_event_recall",
    "gain_per_cost",
    "throughput_mpps",
    "packet_drop_count",
    "p99_latency_us",
    "p999_latency_us",
    "cpu_utilization",
    "gpu_utilization",
    "memory_utilization",
    "gpu_memory_utilization",
    "budget_overrun_count",
    "key_flow_coverage",
    "fallback_recovery_s",
    "complexity",
)
IDENTITY_FIELDS = (
    "run_bundle_identity",
    "generator_run_identity",
    "hardware_identity",
    "code_sha256",
    "input_sha256",
    "contract_sha256",
    "stage_config_sha256",
    "runtime_manifest_sha256",
    "model_sha256",
    "capture_binary_sha256",
    "evidence_manifest_sha256",
)
IDENTITY_MANIFEST_FIELDS = (
    "code",
    "input",
    "stage_config",
    "runtime",
    "model",
)


@dataclass(frozen=True)
class StageContract:
    payload: Mapping[str, Any]
    sha256: str
    path: Path | None = None


def load_contract(path: Path) -> StageContract:
    raw = path.read_bytes()
    payload = json.loads(
        raw.decode("utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError("non-finite JSON constant: " + value)
        ),
    )
    if not isinstance(payload, Mapping):
        raise ValueError("stage contract must be a JSON object")
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported stage contract schema")
    return StageContract(payload, hashlib.sha256(raw).hexdigest(), path.resolve())


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _count(value: Any, *, positive: bool = False) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < (1 if positive else 0):
        return None
    return value


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _add(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def canonical_json_bytes(value: Any) -> bytes:
    """Encode an identity manifest using the frozen, hashable JSON form.

    Production identity manifests are copied both into the sealed evidence
    directory and into the raw receipt.  A single canonical representation is
    therefore required: otherwise equivalent JSON with different whitespace
    could not be tied to the same SHA-256 identity.
    """

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str | None:
    try:
        return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    except (TypeError, ValueError):
        return None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_relative_path(value: Any) -> bool:
    if not _nonempty_string(value) or "\\" in value:
        return False
    path = Path(value)
    return not path.is_absolute() and all(part not in ("", ".", "..") for part in path.parts)


def _exact_keys(
    value: Mapping[str, Any], expected: Sequence[str], prefix: str, errors: list[str]
) -> bool:
    if set(value) != set(expected):
        _add(errors, prefix + ".fields")
        return False
    return True


def _validate_content_digest_list(
    rows: Any,
    *,
    minimum: int,
    key_name: str,
    required_fields: Sequence[str],
    prefix: str,
    errors: list[str],
    row_validator: Any,
) -> bool:
    """Validate a sorted, unique artifact list used by an identity manifest."""

    if not isinstance(rows, list) or len(rows) < minimum:
        _add(errors, prefix)
        return False
    previous: str | None = None
    seen: set[str] = set()
    valid = True
    for index, row in enumerate(rows):
        item = f"{prefix}.{index}"
        if not isinstance(row, Mapping):
            _add(errors, item)
            valid = False
            continue
        if not _exact_keys(row, required_fields, item, errors):
            valid = False
        key = row.get(key_name)
        if (
            not _nonempty_string(key)
            or key in seen
            or (previous is not None and key <= previous)
        ):
            _add(errors, item + ".order_or_identity")
            valid = False
        else:
            seen.add(key)
            previous = key
        if not row_validator(row, item, errors):
            valid = False
    return valid


def _validate_identity_manifests(
    receipt: Mapping[str, Any],
    contract: Mapping[str, Any],
    identities: Mapping[str, Any],
    stage: str,
    backend: Any,
    prefix: str,
    errors: list[str],
) -> None:
    """Validate embedded manifests and their directed provenance graph.

    The outer unified auditor verifies that the evidence directory contains
    files with the identity hashes.  This function validates the *contents*
    whose canonical hashes those identities represent.  Together the two
    checks prevent a one-key dummy JSON file from acting as code/input/model,
    runtime or stage provenance.
    """

    binding = (contract.get("evidence_binding") or {}).get(
        "identity_manifest_content", {}
    )
    specifications = binding.get("manifests") if isinstance(binding, Mapping) else None
    embedded_field = binding.get("embedded_receipt_field") if isinstance(binding, Mapping) else None
    manifests = receipt.get(embedded_field) if isinstance(embedded_field, str) else None
    if (
        not isinstance(specifications, Mapping)
        or set(specifications) != set(IDENTITY_MANIFEST_FIELDS)
        or not isinstance(manifests, Mapping)
        or set(manifests) != set(IDENTITY_MANIFEST_FIELDS)
    ):
        _add(errors, prefix + ".identity_manifests")
        return

    documents: dict[str, Mapping[str, Any]] = {}
    for name in IDENTITY_MANIFEST_FIELDS:
        item = f"{prefix}.identity_manifest.{name}"
        spec = specifications.get(name)
        document = manifests.get(name)
        if not isinstance(spec, Mapping) or not isinstance(document, Mapping):
            _add(errors, item)
            continue
        required_fields = spec.get("required_fields")
        if not isinstance(required_fields, list) or not all(
            isinstance(field, str) for field in required_fields
        ):
            _add(errors, item + ".contract")
            continue
        _exact_keys(document, required_fields, item, errors)
        if document.get("schema_version") != 1 or document.get("scope") != spec.get("scope"):
            _add(errors, item + ".schema")
        if document.get("candidate_id") != contract.get("candidate_id"):
            _add(errors, item + ".candidate_id")
        identity_field = spec.get("identity_field")
        filename = spec.get("evidence_filename")
        identity_to_entry = (contract.get("evidence_binding") or {}).get(
            "identity_to_manifest_entry", {}
        )
        if (
            not isinstance(identity_field, str)
            or not isinstance(filename, str)
            or not isinstance(identity_to_entry, Mapping)
            or identity_to_entry.get(identity_field) != filename
        ):
            _add(errors, item + ".contract_binding")
        elif _canonical_sha256(document) != identities.get(identity_field):
            _add(errors, item + ".sha256")
        documents[name] = document

    code = documents.get("code")
    if code is not None:
        files = code.get("files")

        def code_row(row: Mapping[str, Any], item: str, local_errors: list[str]) -> bool:
            valid = True
            if not _safe_relative_path(row.get("path")):
                _add(local_errors, item + ".path")
                valid = False
            if not _sha256(row.get("sha256")):
                _add(local_errors, item + ".sha256")
                valid = False
            if _count(row.get("size_bytes"), positive=True) is None:
                _add(local_errors, item + ".size_bytes")
                valid = False
            for field in ("language", "role"):
                if not _nonempty_string(row.get(field)):
                    _add(local_errors, item + "." + field)
                    valid = False
            return valid

        _validate_content_digest_list(
            files,
            minimum=int(specifications["code"].get("minimum_files", 1)),
            key_name="path",
            required_fields=("path", "sha256", "size_bytes", "language", "role"),
            prefix=prefix + ".identity_manifest.code.files",
            errors=errors,
            row_validator=code_row,
        )
        languages = {row.get("language") for row in files} if isinstance(files, list) else set()
        roles = {row.get("role") for row in files} if isinstance(files, list) else set()
        if not set(specifications["code"].get("required_languages", [])) <= languages:
            _add(errors, prefix + ".identity_manifest.code.languages")
        if not set(specifications["code"].get("required_roles", [])) <= roles:
            _add(errors, prefix + ".identity_manifest.code.roles")
        if not _sha256(code.get("source_revision_sha256")):
            _add(errors, prefix + ".identity_manifest.code.source_revision_sha256")
        if _canonical_sha256(files) != code.get("source_tree_sha256"):
            _add(errors, prefix + ".identity_manifest.code.source_tree_sha256")

    input_document = documents.get("input")
    if input_document is not None:
        sources = input_document.get("sources")

        def input_row(row: Mapping[str, Any], item: str, local_errors: list[str]) -> bool:
            valid = True
            for field in ("source_id", "role", "provenance_uri"):
                if not _nonempty_string(row.get(field)):
                    _add(local_errors, item + "." + field)
                    valid = False
            if not _sha256(row.get("sha256")):
                _add(local_errors, item + ".sha256")
                valid = False
            for field in ("byte_count", "record_count"):
                if _count(row.get(field), positive=True) is None:
                    _add(local_errors, item + "." + field)
                    valid = False
            return valid

        _validate_content_digest_list(
            sources,
            minimum=1,
            key_name="source_id",
            required_fields=(
                "source_id",
                "role",
                "sha256",
                "byte_count",
                "record_count",
                "provenance_uri",
            ),
            prefix=prefix + ".identity_manifest.input.sources",
            errors=errors,
            row_validator=input_row,
        )
        for field in ("dataset_id", "split_id"):
            if not _nonempty_string(input_document.get(field)):
                _add(errors, prefix + ".identity_manifest.input." + field)
        if not _sha256(input_document.get("feature_schema_sha256")):
            _add(errors, prefix + ".identity_manifest.input.feature_schema_sha256")
        if _canonical_sha256(sources) != input_document.get("source_set_sha256"):
            _add(errors, prefix + ".identity_manifest.input.source_set_sha256")

    model = documents.get("model")
    if model is not None:
        artifacts = model.get("artifacts")

        def model_row(row: Mapping[str, Any], item: str, local_errors: list[str]) -> bool:
            valid = True
            if not _safe_relative_path(row.get("path")):
                _add(local_errors, item + ".path")
                valid = False
            if not _nonempty_string(row.get("role")):
                _add(local_errors, item + ".role")
                valid = False
            if not _sha256(row.get("sha256")):
                _add(local_errors, item + ".sha256")
                valid = False
            if _count(row.get("size_bytes"), positive=True) is None:
                _add(local_errors, item + ".size_bytes")
                valid = False
            return valid

        _validate_content_digest_list(
            artifacts,
            minimum=1,
            key_name="path",
            required_fields=("path", "role", "sha256", "size_bytes"),
            prefix=prefix + ".identity_manifest.model.artifacts",
            errors=errors,
            row_validator=model_row,
        )
        for field in ("model_id", "algorithm_id"):
            if not _nonempty_string(model.get(field)):
                _add(errors, prefix + ".identity_manifest.model." + field)
        if _canonical_sha256(artifacts) != model.get("artifact_set_sha256"):
            _add(errors, prefix + ".identity_manifest.model.artifact_set_sha256")
        if model.get("training_input_manifest_sha256") != identities.get("input_sha256"):
            _add(errors, prefix + ".identity_manifest.model.training_input")
        if input_document is not None and model.get("feature_schema_sha256") != input_document.get(
            "feature_schema_sha256"
        ):
            _add(errors, prefix + ".identity_manifest.model.feature_schema")

    runtime = documents.get("runtime")
    if runtime is not None:
        components = runtime.get("components")

        def runtime_row(row: Mapping[str, Any], item: str, local_errors: list[str]) -> bool:
            valid = True
            for field in ("name", "role", "version"):
                if not _nonempty_string(row.get(field)):
                    _add(local_errors, item + "." + field)
                    valid = False
            if not _sha256(row.get("binary_sha256")):
                _add(local_errors, item + ".binary_sha256")
                valid = False
            return valid

        _validate_content_digest_list(
            components,
            minimum=int(specifications["runtime"].get("minimum_components", 1)),
            key_name="name",
            required_fields=("name", "role", "version", "binary_sha256"),
            prefix=prefix + ".identity_manifest.runtime.components",
            errors=errors,
            row_validator=runtime_row,
        )
        component_roles = (
            {row.get("role") for row in components}
            if isinstance(components, list)
            else set()
        )
        if not set(specifications["runtime"].get("required_roles", [])) <= component_roles:
            _add(errors, prefix + ".identity_manifest.runtime.roles")
        capture_components = [
            row
            for row in components
            if isinstance(row, Mapping) and row.get("role") == "capture"
        ] if isinstance(components, list) else []
        if (
            len(capture_components) != 1
            or capture_components[0].get("binary_sha256")
            != identities.get("capture_binary_sha256")
        ):
            _add(errors, prefix + ".identity_manifest.runtime.capture_component")
        if _canonical_sha256(components) != runtime.get("component_set_sha256"):
            _add(errors, prefix + ".identity_manifest.runtime.component_set_sha256")
        runtime_links = {
            "backend": backend,
            "hardware_identity": identities.get("hardware_identity"),
            "code_manifest_sha256": identities.get("code_sha256"),
            "model_manifest_sha256": identities.get("model_sha256"),
            "capture_binary_sha256": identities.get("capture_binary_sha256"),
        }
        for field, expected in runtime_links.items():
            if runtime.get(field) != expected:
                _add(errors, prefix + ".identity_manifest.runtime." + field)
        roles = runtime.get("host_roles")
        if (
            not isinstance(roles, Mapping)
            or set(roles) != {"capture_host", "inference_host"}
            or not all(_nonempty_string(value) for value in roles.values())
            or roles.get("capture_host") == roles.get("inference_host")
        ):
            _add(errors, prefix + ".identity_manifest.runtime.host_roles")

    stage_config = documents.get("stage_config")
    if stage_config is not None:
        stage_links = {
            "stage": stage,
            "backend": backend,
            "contract_sha256": identities.get("contract_sha256"),
            "hardware_identity": identities.get("hardware_identity"),
            "code_manifest_sha256": identities.get("code_sha256"),
            "input_manifest_sha256": identities.get("input_sha256"),
            "runtime_manifest_sha256": identities.get("runtime_manifest_sha256"),
            "model_manifest_sha256": identities.get("model_sha256"),
            "capture_binary_sha256": identities.get("capture_binary_sha256"),
        }
        for field, expected in stage_links.items():
            if stage_config.get(field) != expected:
                _add(errors, prefix + ".identity_manifest.stage_config." + field)
        parameters = stage_config.get("parameters")
        if not isinstance(parameters, Mapping) or not parameters:
            _add(errors, prefix + ".identity_manifest.stage_config.parameters")
        elif _canonical_sha256(parameters) != stage_config.get("parameters_sha256"):
            _add(errors, prefix + ".identity_manifest.stage_config.parameters_sha256")


def _histogram_quantile(
    histogram: Any, quantile: float, prefix: str, errors: list[str]
) -> float | None:
    if not isinstance(histogram, Mapping):
        _add(errors, prefix + ".histogram")
        return None
    bounds = histogram.get("upper_bounds_us")
    counts = histogram.get("bucket_counts")
    overflow = histogram.get("overflow_count")
    if (
        not isinstance(bounds, list)
        or not bounds
        or not isinstance(counts, list)
        or len(counts) != len(bounds)
        or _count(overflow) is None
    ):
        _add(errors, prefix + ".histogram")
        return None
    parsed_bounds = [_number(value) for value in bounds]
    parsed_counts = [_count(value) for value in counts]
    if (
        any(value is None or value < 0 for value in parsed_bounds)
        or any(value is None for value in parsed_counts)
        or any(left >= right for left, right in zip(parsed_bounds, parsed_bounds[1:]))
    ):
        _add(errors, prefix + ".histogram")
        return None
    total = sum(parsed_counts) + overflow  # type: ignore[arg-type]
    if total < 1:
        _add(errors, prefix + ".samples")
        return None
    rank = max(1, math.ceil(quantile * total))
    cumulative = 0
    for bound, count in zip(parsed_bounds, parsed_counts):
        cumulative += count  # type: ignore[operator]
        if cumulative >= rank:
            return float(bound)  # type: ignore[arg-type]
    _add(errors, prefix + ".overflow")
    return None


def _binary_macro_f1(confusion: Mapping[str, Any], prefix: str, errors: list[str]) -> float | None:
    values = {name: _count(confusion.get(name)) for name in ("tp", "fp", "fn", "tn")}
    if any(value is None for value in values.values()):
        _add(errors, prefix + ".counts")
        return None
    tp, fp, fn, tn = (values[name] for name in ("tp", "fp", "fn", "tn"))
    pos_den = 2 * tp + fp + fn  # type: ignore[operator]
    neg_den = 2 * tn + fp + fn  # type: ignore[operator]
    if pos_den == 0 or neg_den == 0:
        _add(errors, prefix + ".denominator")
        return None
    return ((2 * tp / pos_den) + (2 * tn / neg_den)) / 2  # type: ignore[operator]


def _quality_metrics(
    raw: Any, contract: Mapping[str, Any], prefix: str, errors: list[str]
) -> dict[str, float] | None:
    if not isinstance(raw, Mapping):
        _add(errors, prefix + ".quality")
        return None
    groups = raw.get("group_confusions")
    if not isinstance(groups, list) or not groups:
        _add(errors, prefix + ".quality.group_confusions")
        return None
    grouped_scores = []
    for index, row in enumerate(groups):
        if not isinstance(row, Mapping):
            _add(errors, f"{prefix}.quality.group.{index}")
            continue
        score = _binary_macro_f1(row, f"{prefix}.quality.group.{index}", errors)
        if score is not None:
            grouped_scores.append(score)
    independent = raw.get("independent_confusion")
    if not isinstance(independent, Mapping):
        _add(errors, prefix + ".quality.independent_confusion")
        return None
    independent_f1 = _binary_macro_f1(
        independent, prefix + ".quality.independent", errors
    )
    counts = {name: _count(independent.get(name)) for name in ("tp", "fp", "fn", "tn")}
    if any(value is None for value in counts.values()):
        return None
    tp, fp, fn, tn = (counts[name] for name in ("tp", "fp", "fn", "tn"))
    if tp + fn == 0 or tn + fp == 0:  # type: ignore[operator]
        _add(errors, prefix + ".quality.recall_denominator")
        return None
    buckets = raw.get("score_buckets_descending")
    if not isinstance(buckets, list) or not buckets:
        _add(errors, prefix + ".quality.score_buckets")
        return None
    bucket_pairs: list[tuple[int, int]] = []
    previous_threshold = math.inf
    for index, bucket in enumerate(buckets):
        if not isinstance(bucket, Mapping):
            _add(errors, f"{prefix}.quality.score_bucket.{index}")
            continue
        threshold = _number(bucket.get("score_threshold"))
        positive = _count(bucket.get("positive_count"))
        negative = _count(bucket.get("negative_count"))
        if (
            threshold is None
            or not 0 <= threshold <= 1
            or threshold >= previous_threshold
            or positive is None
            or negative is None
            or positive + negative == 0
        ):
            _add(errors, f"{prefix}.quality.score_bucket.{index}")
        else:
            previous_threshold = threshold
            bucket_pairs.append((positive, negative))
    if sum(value[0] for value in bucket_pairs) != tp + fn or sum(
        value[1] for value in bucket_pairs
    ) != fp + tn:
        _add(errors, prefix + ".quality.score_bucket_accounting")
    total_positive = tp + fn  # type: ignore[operator]
    seen_positive = 0
    seen_total = 0
    average_precision = 0.0
    for positive, negative in bucket_pairs:
        seen_positive += positive
        seen_total += positive + negative
        average_precision += (positive / total_positive) * (seen_positive / seen_total)
    bins = raw.get("calibration_bins")
    frozen_edges = (contract.get("quality_recomputation") or {}).get(
        "ece_bin_edges"
    )
    if (
        not isinstance(frozen_edges, list)
        or len(frozen_edges) < 2
        or any(_number(value) is None for value in frozen_edges)
    ):
        _add(errors, prefix + ".quality.contract_ece_edges")
        return None
    if not isinstance(bins, list) or len(bins) != len(frozen_edges) - 1:
        _add(errors, prefix + ".quality.calibration_bins")
        return None
    calibration_count = 0
    calibration_positive = 0
    calibration_error_sum = 0.0
    for index, row in enumerate(bins):
        if not isinstance(row, Mapping):
            _add(errors, f"{prefix}.quality.calibration_bin.{index}")
            continue
        lower = _number(row.get("lower_bound"))
        upper = _number(row.get("upper_bound"))
        count = _count(row.get("count"), positive=True)
        positive = _count(row.get("positive_count"))
        confidence_sum = _number(row.get("confidence_sum"))
        if (
            row.get("bin_index") != index
            or lower != frozen_edges[index]
            or upper != frozen_edges[index + 1]
            or count is None
            or positive is None
            or positive > count
            or confidence_sum is None
            or not 0 <= confidence_sum <= count
        ):
            _add(errors, f"{prefix}.quality.calibration_bin.{index}")
            continue
        calibration_count += count
        calibration_positive += positive
        calibration_error_sum += abs(confidence_sum / count - positive / count) * count
    total_classified = tp + fp + fn + tn  # type: ignore[operator]
    if calibration_count != total_classified:
        _add(errors, prefix + ".quality.calibration_accounting")
    if calibration_positive != tp + fn:  # type: ignore[operator]
        _add(errors, prefix + ".quality.calibration_positive_accounting")
    total_events = _count(raw.get("ground_truth_event_total"), positive=True)
    matched_events = _count(raw.get("ground_truth_event_matched"))
    if total_events is None or matched_events is None or matched_events > total_events:
        _add(errors, prefix + ".quality.event_accounting")
        return None
    if errors and any(value.startswith(prefix + ".quality") for value in errors):
        return None
    return {
        "grouped_macro_f1": min(grouped_scores),
        "independent_macro_f1": float(independent_f1),
        "independent_attack_recall": tp / (tp + fn),  # type: ignore[operator]
        "independent_benign_recall": tn / (tn + fp),  # type: ignore[operator]
        "independent_auprc": average_precision,
        "independent_ece": calibration_error_sum / calibration_count,
        "ground_truth_event_recall": matched_events / total_events,
    }


def _complexity(raw: Any, contract: Mapping[str, Any], prefix: str, errors: list[str]) -> float | None:
    if not isinstance(raw, Mapping):
        _add(errors, prefix + ".complexity")
        return None
    components = (contract.get("complexity_recomputation") or {}).get("components")
    if not isinstance(components, Mapping) or set(raw) != set(components):
        _add(errors, prefix + ".complexity.components")
        return None
    result = 0.0
    for name, rule in components.items():
        value = _count(raw.get(name))
        weight = _number(rule.get("weight")) if isinstance(rule, Mapping) else None
        normalizer = _number(rule.get("normalizer")) if isinstance(rule, Mapping) else None
        if value is None or weight is None or normalizer is None or normalizer <= 0:
            _add(errors, prefix + ".complexity." + name)
            continue
        result += weight * value / normalizer
    return None if any(value.startswith(prefix + ".complexity") for value in errors) else result


def _resource_maxima(
    raw: Any,
    minimum: int,
    run_start_ns: int | None,
    run_end_ns: int | None,
    prefix: str,
    errors: list[str],
) -> dict[str, float] | None:
    if not isinstance(raw, list) or len(raw) < minimum:
        _add(errors, prefix + ".resource_samples")
        return None
    names = (
        "host_cpu_fraction",
        "host_memory_fraction",
        "service_gpu_utilization_fraction",
        "service_gpu_memory_fraction",
    )
    maxima = {name: 0.0 for name in names}
    previous_timestamp = -1
    for index, sample in enumerate(raw):
        if not isinstance(sample, Mapping):
            _add(errors, f"{prefix}.resource_sample.{index}")
            continue
        timestamp = _count(sample.get("timestamp_unix_ns"), positive=True)
        if timestamp is None or timestamp <= previous_timestamp:
            _add(errors, f"{prefix}.resource_sample.{index}.timestamp")
        else:
            previous_timestamp = timestamp
            if (
                run_start_ns is None
                or run_end_ns is None
                or not run_start_ns <= timestamp <= run_end_ns
            ):
                _add(errors, f"{prefix}.resource_sample.{index}.run_window")
        for name in names:
            value = _number(sample.get(name))
            if value is None or not 0 <= value <= 1:
                _add(errors, f"{prefix}.resource_sample.{index}.{name}")
            else:
                maxima[name] = max(maxima[name], value)
    return None if any(value.startswith(prefix + ".resource_sample") for value in errors) else maxima


def _fallback_max(
    raw: Any,
    minimum: int,
    required_steps: Sequence[str],
    run_start_ns: int | None,
    run_end_ns: int | None,
    prefix: str,
    errors: list[str],
) -> float | None:
    if not isinstance(raw, list) or len(raw) < minimum:
        _add(errors, prefix + ".fallback_trials")
        return None
    recoveries: list[float] = []
    greatest_injected_ns = -1
    greatest_recovered_ns = -1
    trial_ids: set[str] = set()
    injected_times: set[int] = set()
    recovered_times: set[int] = set()
    valid_trials = 0
    for index, trial in enumerate(raw):
        item = f"{prefix}.fallback_trial.{index}"
        if not isinstance(trial, Mapping):
            _add(errors, item)
            continue
        trial_valid = True
        recovery_ns = _count(trial.get("recovery_ns"), positive=True)
        injected_ns = _count(trial.get("fault_injected_unix_ns"), positive=True)
        recovered_ns = _count(trial.get("recovery_completed_unix_ns"), positive=True)
        trial_id = trial.get("trial_id")
        if (
            not isinstance(trial_id, str)
            or not trial_id
            or trial_id in trial_ids
        ):
            _add(errors, item + ".trial_id")
            trial_valid = False
        else:
            trial_ids.add(trial_id)
        time_equation_valid = not (
            recovery_ns is None
            or injected_ns is None
            or recovered_ns is None
            or recovered_ns - injected_ns != recovery_ns
            or run_start_ns is None
            or run_end_ns is None
            or not run_start_ns <= injected_ns < recovered_ns <= run_end_ns
        )
        if not time_equation_valid:
            _add(errors, item + ".recovery_ns")
            trial_valid = False
        else:
            # Both event axes must be globally unique and strictly increasing.
            # Requiring the next injection after the previous recovery also
            # prevents overlapping copies from satisfying a minimum trial count.
            assert injected_ns is not None and recovered_ns is not None
            if injected_ns in injected_times or injected_ns <= greatest_injected_ns:
                _add(errors, item + ".fault_injected_unix_ns")
                _add(errors, item + ".recovery_ns")
                trial_valid = False
            if recovered_ns in recovered_times or recovered_ns <= greatest_recovered_ns:
                _add(errors, item + ".recovery_completed_unix_ns")
                _add(errors, item + ".recovery_ns")
                trial_valid = False
            if greatest_recovered_ns >= 0 and injected_ns <= greatest_recovered_ns:
                _add(errors, item + ".overlap")
                trial_valid = False
            injected_times.add(injected_ns)
            recovered_times.add(recovered_ns)
            greatest_injected_ns = max(greatest_injected_ns, injected_ns)
            greatest_recovered_ns = max(greatest_recovered_ns, recovered_ns)
        if _count(trial.get("transition_packet_gap")) != 0:
            _add(errors, item + ".transition_packet_gap")
            trial_valid = False
        if _count(trial.get("capture_drop_count")) != 0:
            _add(errors, item + ".capture_drop_count")
            trial_valid = False
        if (_count(trial.get("post_switch_packets"), positive=True) or 0) <= 0:
            _add(errors, item + ".post_switch_packets")
            trial_valid = False
        steps = trial.get("steps")
        if not isinstance(steps, Mapping) or any(steps.get(name) is not True for name in required_steps):
            _add(errors, item + ".steps")
            trial_valid = False
        if trial_valid and recovery_ns is not None:
            valid_trials += 1
            recoveries.append(recovery_ns / 1_000_000.0)
    if valid_trials < minimum:
        _add(errors, prefix + ".fallback_trials.distinct_valid_count")
        return None
    return max(recoveries)


def validate_stage_receipt(receipt: Mapping[str, Any], contract: StageContract) -> dict[str, Any]:
    """Return an independently derived stage result; never trust a receipt verdict."""

    errors: list[str] = []
    payload = contract.payload
    stage = receipt.get("stage")
    prefix = str(stage) if stage in STAGES else "stage"
    if receipt.get("schema_version") != 1 or receipt.get("scope") != payload.get("receipt_scope"):
        _add(errors, prefix + ".schema")
    if stage not in STAGES:
        _add(errors, "stage.name")
        return {"qualified": False, "stage": stage, "errors": errors, "derived": None}
    if "qualified" in receipt or "derived_production_pareto_metrics" in receipt or "metrics" in receipt:
        _add(errors, prefix + ".self_reported_verdict")
    if receipt.get("standalone_receipt_trusted") is not False:
        _add(errors, prefix + ".standalone_trust")
    if receipt.get("candidate_id") != payload.get("candidate_id"):
        _add(errors, prefix + ".candidate_id")
    backend = receipt.get("backend")
    if not isinstance(backend, str) or not backend:
        _add(errors, prefix + ".backend")
    identities = receipt.get("identity")
    if not isinstance(identities, Mapping):
        _add(errors, prefix + ".identity")
        identities = {}
    for name in IDENTITY_FIELDS:
        if not _sha256(identities.get(name)):
            _add(errors, prefix + ".identity." + name)
    if identities.get("contract_sha256") != contract.sha256:
        _add(errors, prefix + ".identity.contract_sha256")
    _validate_identity_manifests(
        receipt,
        payload,
        identities,
        str(stage),
        backend,
        prefix,
        errors,
    )
    gate = (payload.get("stage_gates") or {}).get(stage)
    if not isinstance(gate, Mapping):
        _add(errors, prefix + ".contract_gate")
        return {"qualified": False, "stage": stage, "errors": errors, "derived": None}
    windows = receipt.get("windows")
    minimum_windows = _count(gate.get("minimum_full_windows"))
    if minimum_windows is None:
        minimum_windows = _count(gate.get("required_windows"))
    if not isinstance(windows, list) or minimum_windows is None or len(windows) < minimum_windows:
        _add(errors, prefix + ".windows")
        windows = []
    required_latency = {
        "r1": ("kernel_entry_to_shard",),
        "r2": ("kernel_entry_to_feature_enqueue", "internal_feature_enqueue"),
        "r3": ("end_to_end",),
        "r4_24h": ("end_to_end",),
        "r4_72h": ("end_to_end",),
    }[stage]
    throughput_values: list[float] = []
    p99_values: list[float] = []
    p999_values: list[float] = []
    drop_counts: list[int] = []
    budget_counts: list[int] = []
    key_coverages: list[float] = []
    memory_by_window: list[float] = []
    a09_scored_units = 0
    previous_end: int | None = None
    first_start: int | None = None
    last_end: int | None = None
    for index, window in enumerate(windows):
        item = f"{prefix}.window.{index}"
        if not isinstance(window, Mapping):
            _add(errors, item)
            continue
        if window.get("window_index") != index:
            _add(errors, item + ".index")
        start = _count(window.get("start_unix_ns"), positive=True)
        end = _count(window.get("end_unix_ns"), positive=True)
        duration = None if start is None or end is None else (end - start) / 1e9
        minimum_duration = _number((payload.get("packet_window") or {}).get("minimum_duration_s")) or 1.0
        expected_window_duration = _number(gate.get("window_duration_s"))
        if duration is None or duration < max(minimum_duration, expected_window_duration or 0.0):
            _add(errors, item + ".duration")
        if previous_end is not None and start != previous_end:
            _add(errors, item + ".continuity")
        if start is not None and first_start is None:
            first_start = start
        if end is not None:
            last_end = end
            previous_end = end
        offered = _count(window.get("packets_offered"))
        received = _count(window.get("packets_received"))
        parsed = _count(window.get("packets_parsed"))
        rejected = _count(window.get("parse_reject_count"))
        l2_bytes = _count(window.get("l2_bytes_received"))
        shard_packets = _count(window.get("shard_packet_count"))
        shard_bytes = _count(window.get("shard_byte_count"))
        loss = window.get("loss")
        if any(value is None for value in (offered, received, parsed, rejected, l2_bytes, shard_packets, shard_bytes)) or not isinstance(loss, Mapping):
            _add(errors, item + ".packet_counters")
            continue
        components = {name: _count(loss.get(name)) for name in ("nic_rx_missed", "nic_rx_errors", "socket_drops", "sequence_gaps")}
        if any(value is None for value in components.values()):
            _add(errors, item + ".loss_counters")
            continue
        gap = offered - received  # type: ignore[operator]
        accounted = components["nic_rx_missed"] + components["nic_rx_errors"] + components["socket_drops"]  # type: ignore[operator]
        if gap < 0 or gap != components["sequence_gaps"] or gap != accounted:
            _add(errors, item + ".loss_accounting")
        drop_counts.append(gap)
        if received != parsed + rejected or shard_packets != received or shard_bytes != l2_bytes:  # type: ignore[operator]
            _add(errors, item + ".parse_accounting")
        rate = received / duration / 1_000_000.0 if duration and received is not None else 0.0
        throughput_values.append(rate)
        parse_rate = rejected / received if received else (0.0 if rejected == 0 else math.inf)  # type: ignore[operator]
        if rate < float(gate.get("throughput_mpps_min_per_window", 0)):
            _add(errors, item + ".throughput")
        if gap > int(gate.get("packet_drop_count_max", 0)):
            _add(errors, item + ".drop")
        if parse_rate > float(gate.get("parse_reject_rate_max_per_window", 1.0)):
            _add(errors, item + ".parse_reject_rate")
        latency = window.get("latency_histograms")
        if not isinstance(latency, Mapping):
            _add(errors, item + ".latency_histograms")
        else:
            for latency_name in required_latency:
                p99 = _histogram_quantile(latency.get(latency_name), 0.99, item + "." + latency_name, errors)
                p999 = _histogram_quantile(latency.get(latency_name), 0.999, item + "." + latency_name, errors)
                if p99 is not None:
                    minimum_samples = int((payload.get("packet_window") or {}).get("minimum_latency_samples", 1))
                    sample_count = sum(latency[latency_name].get("bucket_counts", [])) + latency[latency_name].get("overflow_count", 0)
                    if sample_count < minimum_samples:
                        _add(errors, item + "." + latency_name + ".samples")
                    p99_values.append(p99)
                    p999_values.append(float(p999) if p999 is not None else math.inf)
                    gate_prefix = {
                        "kernel_entry_to_shard": "kernel_entry_to_shard",
                        "kernel_entry_to_feature_enqueue": "kernel_entry_to_feature_enqueue",
                        "internal_feature_enqueue": "internal_feature_enqueue",
                        "end_to_end": "end_to_end" if stage == "r3" else "",
                    }[latency_name]
                    p99_key = (gate_prefix + "_p99_us_max_per_window") if gate_prefix else "p99_latency_us_max_per_window"
                    p999_key = (gate_prefix + "_p999_us_max_per_window") if gate_prefix else "p999_latency_us_max_per_window"
                    if p99 > float(gate.get(p99_key, math.inf)):
                        _add(errors, item + "." + latency_name + ".p99")
                    if p999 is None or p999 > float(gate.get(p999_key, math.inf)):
                        _add(errors, item + "." + latency_name + ".p999")
        if stage in ("r2", "r3", "r4_24h", "r4_72h"):
            updates = _count(window.get("base_feature_update_count"))
            feature_rejects = _count(window.get("feature_update_reject_count"))
            budget = _count(window.get("budget_overrun_count"))
            key_total = _count(window.get("key_flow_total"))
            key_covered = _count(window.get("key_flow_covered"))
            key_budget_skip = _count(window.get("key_flow_skipped_due_budget"))
            if any(value is None for value in (updates, feature_rejects, budget, key_total, key_covered, key_budget_skip)):
                _add(errors, item + ".feature_counters")
            else:
                if updates + feature_rejects != parsed:  # type: ignore[operator]
                    _add(errors, item + ".feature_accounting")
                if feature_rejects > int(gate.get("feature_update_reject_count_max", 0)):
                    _add(errors, item + ".feature_reject")
                if budget > int(gate.get("budget_overrun_count_max", 0)):
                    _add(errors, item + ".budget")
                if key_covered > key_total or key_budget_skip > int(gate.get("key_flow_skipped_due_budget_max", 0)):
                    _add(errors, item + ".key_flow_accounting")
                if key_total > 0:
                    coverage = key_covered / key_total
                    key_coverages.append(coverage)
                    if coverage < float(gate.get("key_flow_coverage_min_per_nonempty_window", 0)):
                        _add(errors, item + ".key_flow_coverage")
                budget_counts.append(budget)
        if stage in ("r3", "r4_24h", "r4_72h"):
            for name in ("gpu_queue_full_count", "gpu_batches_failed_count", "normal_fallback_unit_count"):
                value = _count(window.get(name))
                limit = int(gate.get(name.replace("_count", "_max").replace("_unit", "_units"), 0))
                if value is None or value > limit:
                    _add(errors, item + "." + name)
            closed_units = _count(window.get("closed_flow_or_window_unit_count"))
            scored_units = _count(window.get("a09_scored_unit_count"))
            fallback_units = _count(window.get("local_fallback_unit_count"))
            if (
                closed_units is None
                or scored_units is None
                or fallback_units is None
                or scored_units + fallback_units != closed_units
            ):
                _add(errors, item + ".inference_accounting")
            elif stage == "r3":
                a09_scored_units += scored_units
        if stage.startswith("r4_"):
            if _count(window.get("clock_step_count")) != 0:
                _add(errors, item + ".clock_step")
            if window.get("runtime_manifest_sha256") != identities.get("runtime_manifest_sha256"):
                _add(errors, item + ".runtime_identity")
            resource = window.get("resource")
            memory = _number(resource.get("host_memory_fraction")) if isinstance(resource, Mapping) else None
            if memory is None:
                _add(errors, item + ".resource")
            else:
                memory_by_window.append(memory)
    if stage in ("r2", "r3", "r4_24h", "r4_72h") and not key_coverages:
        _add(errors, prefix + ".key_flow_nonempty")
    required_duration = _number(gate.get("required_duration_s"))
    if required_duration is not None:
        elapsed = 0.0 if first_start is None or last_end is None else (last_end - first_start) / 1e9
        if elapsed < required_duration:
            _add(errors, prefix + ".time_coverage")
    resource_metrics = None
    if stage in ("r3", "r4_24h", "r4_72h"):
        resource_metrics = _resource_maxima(
            receipt.get("resource_samples"),
            int(gate.get("resource_samples_min", 10)),
            first_start,
            last_end,
            prefix,
            errors,
        )
        if resource_metrics is not None:
            resource_gate_names = {
                "host_cpu_fraction": "host_cpu_fraction_max",
                "host_memory_fraction": "host_memory_fraction_max",
                "service_gpu_utilization_fraction": "service_gpu_utilization_fraction_max",
                "service_gpu_memory_fraction": "service_gpu_memory_fraction_max",
            }
            for name, limit_name in resource_gate_names.items():
                if resource_metrics[name] > float(gate.get(limit_name, 0.85)):
                    _add(errors, prefix + ".resource." + name)
    fallback_recovery_ms = None
    if stage in ("r3", "r4_24h", "r4_72h"):
        minimum_trials = int(gate.get("fallback_trials_min", gate.get("fault_injections_min", 0)))
        required_steps = (payload.get("fallback_restoration") or {}).get("required_steps") or []
        fallback_recovery_ms = _fallback_max(
            receipt.get("fallback_trials"),
            minimum_trials,
            required_steps,
            first_start,
            last_end,
            prefix,
            errors,
        )
        if fallback_recovery_ms is not None and fallback_recovery_ms > float(
            gate.get("fallback_recovery_ms_max", 300.0)
        ):
            _add(errors, prefix + ".fallback_recovery")
        restoration = receipt.get("restoration_steps")
        if not isinstance(restoration, Mapping) or any(restoration.get(name) is not True for name in required_steps):
            _add(errors, prefix + ".restoration")
    if stage.startswith("r4_") and windows:
        quarter = max(1, len(windows) // 4)
        early_rates = throughput_values[:quarter]
        late_rates = throughput_values[-quarter:]
        early_p99 = p99_values[:quarter]
        late_p99 = p99_values[-quarter:]
        early_memory = memory_by_window[:quarter]
        late_memory = memory_by_window[-quarter:]
        drift = payload.get("long_run_drift_gates") or {}
        def mean(values: Sequence[float]) -> float:
            return sum(values) / len(values) if values else math.inf
        throughput_regression = max(0.0, (mean(early_rates) - mean(late_rates)) / max(mean(early_rates), 1e-12))
        p99_inflation = max(0.0, (mean(late_p99) - mean(early_p99)) / max(mean(early_p99), 1e-12))
        memory_growth = max(0.0, mean(late_memory) - mean(early_memory))
        if throughput_regression > float(drift.get("late_quartile_throughput_regression_max", 0)):
            _add(errors, prefix + ".drift.throughput")
        if p99_inflation > float(drift.get("late_quartile_p99_inflation_max", 0)):
            _add(errors, prefix + ".drift.p99")
        if memory_growth > float(drift.get("late_quartile_memory_fraction_growth_max", 0)):
            _add(errors, prefix + ".drift.memory")
    quality = None
    gain_per_cost = None
    complexity = None
    if stage == "r3":
        quality = _quality_metrics(
            receipt.get("quality_raw"), payload, prefix, errors
        )
        if quality is not None:
            independent_confusion = receipt["quality_raw"]["independent_confusion"]
            classified_units = sum(
                independent_confusion[name] for name in ("tp", "fp", "fn", "tn")
            )
            if classified_units != a09_scored_units:
                _add(errors, prefix + ".quality.scored_unit_accounting")
            quality_gates = {
                "grouped_macro_f1": (">=", "grouped_macro_f1_min"),
                "independent_macro_f1": (">=", "independent_macro_f1_min"),
                "independent_attack_recall": (">=", "independent_attack_recall_min"),
                "independent_benign_recall": (">=", "independent_benign_recall_min"),
                "independent_auprc": (">=", "independent_auprc_min"),
                "independent_ece": ("<=", "independent_ece_max"),
                "ground_truth_event_recall": (">=", "ground_truth_event_recall_min"),
            }
            for name, (relation, limit_name) in quality_gates.items():
                limit = float(gate.get(limit_name, math.inf if relation == "<=" else -math.inf))
                failed = quality[name] < limit if relation == ">=" else quality[name] > limit
                if failed:
                    _add(errors, prefix + ".quality_gate." + name)
        efficiency = receipt.get("efficiency_raw")
        if not isinstance(efficiency, Mapping) or quality is None:
            _add(errors, prefix + ".efficiency")
        else:
            baseline = _number(efficiency.get("baseline_independent_macro_f1"))
            optional_cpu = _number(efficiency.get("optional_cpu_us"))
            total_cpu = _number(efficiency.get("total_cpu_us"))
            if (
                baseline is None
                or optional_cpu is None
                or total_cpu is None
                or optional_cpu <= 0
                or total_cpu <= 0
                or optional_cpu > total_cpu
            ):
                _add(errors, prefix + ".efficiency")
            else:
                gain_per_cost = (quality["independent_macro_f1"] - baseline) / (optional_cpu / total_cpu)
                if gain_per_cost < 0:
                    _add(errors, prefix + ".efficiency.negative_gain")
        complexity = _complexity(receipt.get("complexity_raw"), payload, prefix, errors)
    derived = {
        "throughput_mpps": min(throughput_values) if throughput_values else None,
        "packet_drop_count": sum(drop_counts) if drop_counts else None,
        "p99_latency_us": max(p99_values) if p99_values else None,
        "p999_latency_us": max(p999_values) if p999_values else None,
        "budget_overrun_count": sum(budget_counts) if budget_counts else 0,
        "key_flow_coverage": min(key_coverages) if key_coverages else None,
        "fallback_recovery_s": None if fallback_recovery_ms is None else fallback_recovery_ms / 1000.0,
        "quality": quality,
        "gain_per_cost": gain_per_cost,
        "complexity": complexity,
        "resources": resource_metrics,
    }
    return {
        "qualified": not errors,
        "stage": stage,
        "errors": errors,
        "derived": derived,
        "identity": dict(identities),
        "candidate_id": receipt.get("candidate_id"),
        "backend": backend,
    }


def aggregate_stage_evidence(
    receipts: Iterable[Mapping[str, Any]],
    contract: StageContract,
    *,
    backend_binding: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the full campaign and derive the exact final-Pareto metric map."""

    materialized = list(receipts)
    results = [validate_stage_receipt(receipt, contract) for receipt in materialized]
    errors = [f"receipt.{index}.{error}" for index, result in enumerate(results) for error in result["errors"]]
    by_stage = {stage: [] for stage in STAGES}
    for result in results:
        if result.get("stage") in by_stage:
            by_stage[result["stage"]].append(result)
    gates = contract.payload.get("stage_gates") or {}
    stage_qualified: dict[str, bool] = {}
    backend_roles_qualified: dict[str, bool] = {}
    if backend_binding is None:
        for stage in STAGES:
            required = int((gates.get(stage) or {}).get("required_repeats", 0))
            if len(by_stage[stage]) != required:
                _add(errors, f"campaign.{stage}.repeat_count")
            if any(not result["qualified"] for result in by_stage[stage]):
                _add(errors, f"campaign.{stage}.receipt_failure")
            stage_qualified[stage] = (
                len(by_stage[stage]) == required
                and all(result["qualified"] for result in by_stage[stage])
            )
    else:
        expected_binding = {
            "primary": backend_binding.get("primary_backend"),
            "fallback": backend_binding.get("fallback_backend"),
        }
        binding_valid = not (
            set(backend_binding) != {"primary_backend", "fallback_backend"}
            or not all(
                _nonempty_string(value) for value in expected_binding.values()
            )
            or len(set(expected_binding.values())) != 2
        )
        if not binding_valid:
            _add(errors, "campaign.backend_binding")
        for index, (receipt, result) in enumerate(zip(materialized, results)):
            role = receipt.get("backend_role")
            if role not in expected_binding:
                _add(errors, f"campaign.receipt.{index}.backend_role")
            elif result.get("backend") != expected_binding[role]:
                _add(errors, f"campaign.receipt.{index}.backend_role_binding")
        role_stage_qualified = {
            role: {} for role in expected_binding
        }
        for stage in STAGES:
            required = int((gates.get(stage) or {}).get("required_repeats", 0))
            for role, backend in expected_binding.items():
                role_pairs = [
                    (receipt, result)
                    for receipt, result in zip(materialized, results)
                    if result.get("stage") == stage
                    and receipt.get("backend_role") == role
                ]
                role_results = [result for _, result in role_pairs]
                role_ok = (
                    binding_valid
                    and len(role_results) == required
                    and all(result.get("backend") == backend for result in role_results)
                    and all(result["qualified"] for result in role_results)
                )
                role_stage_qualified[role][stage] = role_ok
                if len(role_results) != required:
                    _add(errors, f"campaign.{stage}.{role}.repeat_count")
                if any(not result["qualified"] for result in role_results):
                    _add(errors, f"campaign.{stage}.{role}.receipt_failure")
            stage_qualified[stage] = all(
                role_stage_qualified[role][stage] for role in expected_binding
            )
        backend_roles_qualified = {
            role: all(by_stage.values())
            for role, by_stage in role_stage_qualified.items()
        }
    identities = [result.get("identity") or {} for result in results]
    invariant = (contract.payload.get("common_identity") or {}).get("invariant_across_all_stages") or []
    for name in invariant:
        if backend_binding is not None and name in (
            "backend",
            "runtime_manifest_sha256",
            "capture_binary_sha256",
        ):
            if name != "backend":
                for role in ("primary", "fallback"):
                    role_identities = [
                        result.get("identity") or {}
                        for receipt, result in zip(materialized, results)
                        if receipt.get("backend_role") == role
                    ]
                    if len({identity.get(name) for identity in role_identities}) != 1:
                        _add(errors, f"campaign.identity.{role}.{name}")
            continue
        if len({identity.get(name) for identity in identities}) != 1:
            _add(errors, "campaign.identity." + name)
    if backend_binding is None and len({result.get("backend") for result in results}) != 1:
        _add(errors, "campaign.backend")
    within_stage = (contract.payload.get("common_identity") or {}).get("invariant_within_stage") or []
    for stage, stage_results in by_stage.items():
        for name in within_stage:
            if backend_binding is None:
                groups = ((None, stage_results),)
            else:
                groups = tuple(
                    (
                        role,
                        [
                            result
                            for receipt, result in zip(materialized, results)
                            if result.get("stage") == stage
                            and receipt.get("backend_role") == role
                        ],
                    )
                    for role in ("primary", "fallback")
                )
            for role, role_results in groups:
                if role_results and len(
                    {result["identity"].get(name) for result in role_results}
                ) != 1:
                    suffix = "" if role is None else "." + role
                    _add(errors, f"campaign.{stage}{suffix}.identity.{name}")
    unique = (contract.payload.get("common_identity") or {}).get("unique_across_receipts") or []
    for name in unique:
        values = [identity.get(name) for identity in identities]
        if len(values) != len(set(values)):
            _add(errors, "campaign.independence." + name)
    r3 = by_stage["r3"]
    quality_rows = [result["derived"]["quality"] for result in r3 if result["derived"] and result["derived"]["quality"]]
    all_derived = [result["derived"] for result in results if result.get("derived")]
    def values(field: str, stages: Sequence[str] = STAGES) -> list[float]:
        return [
            float(result["derived"][field])
            for stage in stages
            for result in by_stage[stage]
            if result.get("derived") and result["derived"].get(field) is not None
        ]
    resource_names = (
        "host_cpu_fraction",
        "service_gpu_utilization_fraction",
        "host_memory_fraction",
        "service_gpu_memory_fraction",
    )
    resource_values = {
        name: [
            result["derived"]["resources"][name]
            for stage in ("r3", "r4_24h", "r4_72h")
            for result in by_stage[stage]
            if result.get("derived") and result["derived"].get("resources")
        ]
        for name in resource_names
    }
    candidate_id = str(contract.payload.get("candidate_id", ""))
    metrics: dict[str, Any] | None = None
    if not errors and quality_rows:
        metrics = {
            "name": candidate_id,
            "grouped_macro_f1": min(row["grouped_macro_f1"] for row in quality_rows),
            "independent_macro_f1": min(row["independent_macro_f1"] for row in quality_rows),
            "independent_attack_recall": min(row["independent_attack_recall"] for row in quality_rows),
            "independent_benign_recall": min(row["independent_benign_recall"] for row in quality_rows),
            "independent_auprc": min(row["independent_auprc"] for row in quality_rows),
            "independent_ece": max(row["independent_ece"] for row in quality_rows),
            "ground_truth_event_recall": min(row["ground_truth_event_recall"] for row in quality_rows),
            "gain_per_cost": min(values("gain_per_cost", ("r3",))),
            "throughput_mpps": min(values("throughput_mpps")),
            "packet_drop_count": int(max(values("packet_drop_count"))),
            "p99_latency_us": max(values("p99_latency_us", ("r3", "r4_24h", "r4_72h"))),
            "p999_latency_us": max(values("p999_latency_us", ("r3", "r4_24h", "r4_72h"))),
            "cpu_utilization": max(resource_values["host_cpu_fraction"]),
            "gpu_utilization": max(resource_values["service_gpu_utilization_fraction"]),
            "memory_utilization": max(resource_values["host_memory_fraction"]),
            "gpu_memory_utilization": max(resource_values["service_gpu_memory_fraction"]),
            "budget_overrun_count": int(max(values("budget_overrun_count", ("r2", "r3", "r4_24h", "r4_72h")))),
            "key_flow_coverage": min(values("key_flow_coverage", ("r2", "r3", "r4_24h", "r4_72h"))),
            "fallback_recovery_s": max(values("fallback_recovery_s", ("r3", "r4_24h", "r4_72h"))),
            "complexity": max(values("complexity", ("r3",))),
        }
        expected = set(PARETO_NUMERIC_FIELDS) | {"name"}
        if set(metrics) != expected or any(_number(metrics[name]) is None for name in PARETO_NUMERIC_FIELDS):
            _add(errors, "campaign.derived_metrics_schema")
            metrics = None
    elif not quality_rows:
        _add(errors, "campaign.quality_missing")
    return {
        "qualified": not errors,
        "errors": errors,
        "stage_qualified": stage_qualified,
        "backend_roles_qualified": backend_roles_qualified,
        "derived_production_pareto_metrics": metrics if not errors else None,
        "receipt_count": len(results),
    }
