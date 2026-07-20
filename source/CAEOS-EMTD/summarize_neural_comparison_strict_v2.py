from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
from scipy.stats import rankdata, wilcoxon


SCHEMA_VERSION = "strict_v2"
REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}
PAIR_ARGUMENT_FIELDS = (
    "csv",
    "config",
    "split_strategy",
    "max_per_class",
    "benign_class",
)
RESOURCE_PATHS = {
    "training_seconds": (
        ("training_seconds",),
        ("runtime", "training_seconds"),
        ("timing", "training_seconds"),
    ),
    "inference_seconds": (
        ("inference_seconds",),
        ("runtime", "inference_seconds"),
        ("timing", "inference_seconds"),
    ),
    "peak_gpu_memory_mb": (
        ("peak_gpu_memory_mb",),
        ("runtime", "peak_gpu_memory_mb"),
        ("resources", "peak_gpu_memory_mb"),
    ),
}
_GATE_RUN_RE = re.compile(r"^(?P<scenario>.+)_seed(?P<seed>\d+)$")
_NEURAL_RUN_RE = re.compile(
    r"^(?P<scenario>.+)_seed(?P<seed>\d+)(?:_.+)?$"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Strict v2 scenario-blocked comparison of CAEOS and neural "
            "open-set baselines"
        )
    )
    parser.add_argument("--gate-root", required=True)
    parser.add_argument(
        "--gate-policy-name",
        help=(
            "explicit composite policy name when suites intentionally use "
            "different frozen source policies"
        ),
    )
    parser.add_argument(
        "--neural-root",
        action="append",
        required=True,
        help="suite=directory; repeat for method-specific result roots",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20250715)
    parser.add_argument(
        "--inference-seeds",
        help=(
            "comma-separated confirmation seeds used for statistical inference; "
            "all discovered seeds are still validated for coverage and integrity"
        ),
    )
    return parser.parse_args()


def parse_inference_seeds(value: Optional[str]) -> Optional[tuple[int, ...]]:
    if value is None:
        return None
    tokens = [token.strip() for token in value.split(",")]
    if not tokens or any(not token for token in tokens):
        raise ValueError("--inference-seeds must be a non-empty comma-separated list")
    try:
        seeds = tuple(int(token) for token in tokens)
    except ValueError as error:
        raise ValueError("--inference-seeds must contain integers") from error
    if any(seed < 0 for seed in seeds):
        raise ValueError("--inference-seeds cannot contain negative values")
    if len(set(seeds)) != len(seeds):
        raise ValueError("--inference-seeds cannot contain duplicates")
    return tuple(sorted(seeds))


def _read_metrics(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read metrics file {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"metrics file must contain a JSON object: {path}")
    return payload


def _required(mapping: dict[str, object], key: str, context: str) -> object:
    if key not in mapping:
        raise ValueError(f"missing {context}.{key}")
    return mapping[key]


def _finite_float(value: object, context: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{context} must be a finite number, not bool")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{context} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{context} must be finite")
    return result


def _metric_report(payload: object, context: str) -> dict[str, float]:
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    return {
        metric: _finite_float(_required(payload, metric, context), f"{context}.{metric}")
        for metric in REPORT_METRICS
    }


def _parse_task(path: Path, suite: str, gate: bool) -> tuple[str, str, int]:
    matcher = _GATE_RUN_RE if gate else _NEURAL_RUN_RE
    match = matcher.fullmatch(path.parent.name)
    if match is None:
        kind = "gate" if gate else "neural"
        raise ValueError(f"invalid {kind} run directory name: {path.parent.name}")
    return suite, match.group("scenario"), int(match.group("seed"))


def _task_name(task: tuple[str, str, int]) -> str:
    return f"{task[0]}/{task[1]}/seed{task[2]}"


def _gate_method_name(metrics: dict[str, object], path: Path) -> str:
    policy_candidates: list[str] = []
    value = metrics.get("risk_policy")
    if isinstance(value, str) and value.strip():
        policy_candidates.append(value.strip())
    arguments = metrics.get("arguments")
    if isinstance(arguments, dict):
        value = arguments.get("risk_policy")
        if isinstance(value, str) and value.strip():
            policy_candidates.append(value.strip())
    if policy_candidates:
        if len(set(policy_candidates)) != 1:
            raise ValueError(
                f"conflicting gate policy metadata in {path}: {policy_candidates}"
            )
        return policy_candidates[0]

    candidates: list[str] = []
    selection = metrics.get("risk_selection")
    if isinstance(selection, str) and selection.strip():
        candidates.append(selection.strip())
    elif isinstance(selection, dict):
        for key in ("name", "method", "risk_selection"):
            value = selection.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())
                break
    arguments = metrics.get("arguments")
    if isinstance(arguments, dict):
        value = arguments.get("risk_selection")
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    if not candidates:
        raise ValueError(f"cannot determine gate method from {path}")
    if len(set(candidates)) != 1:
        raise ValueError(f"conflicting gate method metadata in {path}: {candidates}")
    return candidates[0]


def _gate_effective_risk_selection(
    metrics: dict[str, object], path: Path
) -> str:
    candidates: list[str] = []
    value = metrics.get("risk_selection")
    if isinstance(value, str) and value.strip():
        candidates.append(value.strip())
    arguments = metrics.get("arguments")
    if isinstance(arguments, dict):
        value = arguments.get("risk_selection")
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    if not candidates:
        raise ValueError(f"cannot determine effective gate risk selection from {path}")
    if len(set(candidates)) != 1:
        raise ValueError(
            f"conflicting effective gate risk metadata in {path}: {candidates}"
        )
    return candidates[0]


def _combined_split_digest(fingerprint: dict[str, object]) -> str:
    digest = hashlib.sha256()
    for name in ("train", "validation", "test"):
        digest.update(name.encode("ascii"))
        digest.update(str(fingerprint[name]).encode("ascii"))
    return digest.hexdigest()


def validate_split_fingerprint(
    metrics: dict[str, object], path: Path
) -> dict[str, object]:
    split_metadata = _required(metrics, "split_metadata", str(path))
    if not isinstance(split_metadata, dict):
        raise ValueError(f"{path}.split_metadata must be an object")
    fingerprint = _required(
        split_metadata, "split_fingerprint", f"{path}.split_metadata"
    )
    if not isinstance(fingerprint, dict):
        raise ValueError(f"{path} split_fingerprint must be an object")
    for key in ("schema_version", "algorithm", "columns"):
        _required(fingerprint, key, f"{path}.split_metadata.split_fingerprint")
    if fingerprint["schema_version"] != "1.0":
        raise ValueError(
            f"unsupported split_fingerprint schema in {path}: "
            f"{fingerprint['schema_version']!r}"
        )
    if not isinstance(fingerprint["algorithm"], str) or not fingerprint["algorithm"]:
        raise ValueError(f"invalid split_fingerprint algorithm in {path}")
    columns = fingerprint["columns"]
    if not isinstance(columns, list) or not columns:
        raise ValueError(f"split_fingerprint columns must be a non-empty list: {path}")
    if len(columns) != len({str(value) for value in columns}):
        raise ValueError(f"split_fingerprint columns contain duplicates: {path}")
    for key in ("train", "validation", "test", "combined"):
        value = _required(
            fingerprint, key, f"{path}.split_metadata.split_fingerprint"
        )
        if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
            raise ValueError(f"invalid split_fingerprint {key} digest in {path}")
    expected_combined = _combined_split_digest(fingerprint)
    if fingerprint["combined"] != expected_combined:
        raise ValueError(
            f"split_fingerprint combined digest is not reproducible in {path}"
        )
    return fingerprint


def _normalized_argument(field: str, value: object) -> object:
    if field in {"csv", "config"} and isinstance(value, str):
        return str(Path(value).expanduser().resolve(strict=False))
    return value


def _provenance_input_identity(
    metrics_path: Path, field: str
) -> Optional[tuple[str, ...]]:
    provenance_path = metrics_path.parent / "provenance.json"
    if not provenance_path.is_file():
        return None
    provenance = _read_metrics(provenance_path)
    inputs = _required(provenance, "inputs", str(provenance_path))
    if not isinstance(inputs, dict):
        raise ValueError(f"{provenance_path}.inputs must be an object")
    item = _required(inputs, field, f"{provenance_path}.inputs")
    if not isinstance(item, dict):
        raise ValueError(f"{provenance_path}.inputs.{field} must be an object")

    direct_sha = item.get("sha256")
    if isinstance(direct_sha, str) and _SHA256_RE.fullmatch(direct_sha):
        return ("sha256", direct_sha)

    if field == "csv":
        sidecar = item.get("sidecar_sha")
        if isinstance(sidecar, dict):
            declared = sidecar.get("declared_sha256")
            sidecar_file = sidecar.get("sidecar_file_sha256")
            if (
                isinstance(declared, str)
                and _SHA256_RE.fullmatch(declared)
                and isinstance(sidecar_file, str)
                and _SHA256_RE.fullmatch(sidecar_file)
            ):
                return ("sidecar_sha256", declared, sidecar_file)
    raise ValueError(
        f"missing valid content SHA-256 for {provenance_path}.inputs.{field}"
    )


def _protocol_identity(
    metrics: dict[str, object], path: Path
) -> dict[str, object]:
    arguments = _required(metrics, "arguments", str(path))
    if not isinstance(arguments, dict):
        raise ValueError(f"{path}.arguments must be an object")
    identity: dict[str, object] = {
        "unknown_classes": _required(metrics, "unknown_classes", str(path)),
        "known_class_names": _required(metrics, "known_class_names", str(path)),
        "sample_counts": _required(metrics, "sample_counts", str(path)),
        "split_sizes": _required(metrics, "split_sizes", str(path)),
        "split_fingerprint": validate_split_fingerprint(metrics, path),
        "arguments": {},
    }
    normalized_arguments = identity["arguments"]
    assert isinstance(normalized_arguments, dict)
    for field in PAIR_ARGUMENT_FIELDS:
        value = _required(arguments, field, f"{path}.arguments")
        content_identity = (
            _provenance_input_identity(path, field)
            if field in {"csv", "config"}
            else None
        )
        normalized_arguments[field] = (
            content_identity
            if content_identity is not None
            else _normalized_argument(field, value)
        )
    return identity


def _validate_pair_identity(
    gate_metrics: dict[str, object],
    gate_path: Path,
    neural_metrics: dict[str, object],
    neural_path: Path,
    task: tuple[str, str, int],
) -> dict[str, object]:
    for payload, path in (
        (gate_metrics, gate_path),
        (neural_metrics, neural_path),
    ):
        observed_seed = _required(payload, "seed", str(path))
        if observed_seed != task[2]:
            raise ValueError(
                f"seed mismatch for {_task_name(task)}: {path} records "
                f"{observed_seed!r}"
            )
    gate_identity = _protocol_identity(gate_metrics, gate_path)
    neural_identity = _protocol_identity(neural_metrics, neural_path)
    if gate_identity != neural_identity:
        differing = []
        for key in (
            "unknown_classes",
            "known_class_names",
            "sample_counts",
            "split_sizes",
            "split_fingerprint",
        ):
            if gate_identity[key] != neural_identity[key]:
                differing.append(key)
        gate_arguments = gate_identity["arguments"]
        neural_arguments = neural_identity["arguments"]
        assert isinstance(gate_arguments, dict)
        assert isinstance(neural_arguments, dict)
        for field in PAIR_ARGUMENT_FIELDS:
            if gate_arguments[field] != neural_arguments[field]:
                differing.append(f"arguments.{field}")
        raise ValueError(
            f"protocol identity mismatch for {_task_name(task)} between "
            f"{gate_path} and {neural_path}: {', '.join(differing)}"
        )
    return gate_identity


def _nested_value(
    payload: dict[str, object], path: tuple[str, ...]
) -> Optional[object]:
    current: object = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def extract_resource_usage(
    metrics: dict[str, object], metrics_path: Path
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for resource, candidates in RESOURCE_PATHS.items():
        observed: list[tuple[str, float]] = []
        for candidate in candidates:
            value = _nested_value(metrics, candidate)
            if value is None:
                continue
            numeric = _finite_float(value, f"{metrics_path}.{'.'.join(candidate)}")
            if numeric < 0:
                raise ValueError(
                    f"{metrics_path}.{'.'.join(candidate)} must be non-negative"
                )
            observed.append((".".join(candidate), numeric))
        if observed:
            unique_values = {value for _, value in observed}
            if len(unique_values) != 1:
                raise ValueError(
                    f"conflicting {resource} values in {metrics_path}: {observed}"
                )
            result[resource] = {
                "status": "recorded",
                "value": observed[0][1],
                "source": observed[0][0],
            }
        else:
            result[resource] = {
                "status": "missing",
                "value": None,
                "source": None,
            }
    return result


def extract_report_resource_usage(
    metrics: dict[str, object], metrics_path: Path, method: str
) -> dict[str, dict[str, object]]:
    by_report = metrics.get("resource_usage_by_report")
    if by_report is None:
        return extract_resource_usage(metrics, metrics_path)
    if not isinstance(by_report, dict):
        raise ValueError(f"{metrics_path}.resource_usage_by_report must be an object")
    payload = by_report.get(method)
    if not isinstance(payload, dict):
        raise ValueError(
            f"missing resource usage for report {method!r} in {metrics_path}"
        )
    return extract_resource_usage(
        payload, Path(f"{metrics_path}.resource_usage_by_report.{method}")
    )


def _coverage_error(
    label: str,
    expected: set[tuple[str, str, int]],
    actual: set[tuple[str, str, int]],
) -> ValueError:
    missing = sorted(_task_name(task) for task in expected - actual)
    unexpected = sorted(_task_name(task) for task in actual - expected)
    return ValueError(
        f"task coverage mismatch for {label}: missing={missing}, "
        f"unexpected={unexpected}"
    )


def load_suite_runs(
    gate_root: Path,
    suite: str,
    neural_roots: Iterable[Path],
    gate_policy_name: Optional[str] = None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    gate_entries: dict[tuple[str, str, int], tuple[Path, dict[str, object]]] = {}
    for path in sorted((gate_root / suite).glob("*/metrics.json")):
        task = _parse_task(path, suite, gate=True)
        if task in gate_entries:
            raise ValueError(f"duplicate gate task: {_task_name(task)}")
        gate_entries[task] = (path, _read_metrics(path))
    if not gate_entries:
        raise ValueError(f"no gate metrics found for suite {suite!r}")

    expected_tasks = set(gate_entries)
    runs: dict[tuple[str, str, int], dict[str, object]] = {}
    for task, (path, payload) in gate_entries.items():
        gate_seed = _required(payload, "seed", str(path))
        if gate_seed != task[2]:
            raise ValueError(
                f"seed mismatch for {_task_name(task)}: gate records {gate_seed!r}"
            )
        identity = _protocol_identity(payload, path)
        source_method = _gate_method_name(payload, path)
        runs[task] = {
            "suite": suite,
            "scenario": task[1],
            "seed": task[2],
            "task_id": _task_name(task),
            "gate_method": gate_policy_name or source_method,
            "gate_source_method": source_method,
            "gate_effective_risk_selection": _gate_effective_risk_selection(
                payload, path
            ),
            "gate_selected_risk": _required(payload, "selected_risk", str(path)),
            "gate_report": _metric_report(
                _required(payload, "selected_report", str(path)),
                f"{path}.selected_report",
            ),
            "gate_resources": extract_resource_usage(payload, path),
            "gate_metrics_path": str(path),
            "split_fingerprint": identity["split_fingerprint"],
            "neural_reports": {},
            "neural_resources": {},
            "neural_metrics_paths": {},
        }

    root_coverage = []
    method_coverage: dict[str, set[tuple[str, str, int]]] = defaultdict(set)
    split_fingerprint_checks = 0
    roots = list(neural_roots)
    if not roots:
        raise ValueError(f"no neural roots supplied for suite {suite!r}")
    for root in roots:
        paths = sorted(root.glob("*/metrics.json"))
        if not paths:
            raise ValueError(f"no neural metrics found for suite {suite!r} in {root}")
        actual_tasks = {_parse_task(path, suite, gate=False) for path in paths}
        if actual_tasks != expected_tasks:
            raise _coverage_error(f"suite={suite!r}, root={root}", expected_tasks, actual_tasks)
        root_coverage.append(
            {
                "root": str(root),
                "task_count": len(actual_tasks),
                "missing_tasks": [],
                "unexpected_tasks": [],
                "validated": True,
            }
        )
        for path in paths:
            task = _parse_task(path, suite, gate=False)
            payload = _read_metrics(path)
            gate_path, gate_payload = gate_entries[task]
            _validate_pair_identity(gate_payload, gate_path, payload, path, task)
            split_fingerprint_checks += 1
            reports = _required(payload, "reports", str(path))
            if not isinstance(reports, dict) or not reports:
                raise ValueError(f"empty or invalid reports object: {path}")
            run = runs[task]
            neural_reports = run["neural_reports"]
            neural_resources = run["neural_resources"]
            neural_paths = run["neural_metrics_paths"]
            assert isinstance(neural_reports, dict)
            assert isinstance(neural_resources, dict)
            assert isinstance(neural_paths, dict)
            for method, report_payload in reports.items():
                if not isinstance(method, str) or not method:
                    raise ValueError(f"invalid neural method name in {path}: {method!r}")
                if method in neural_reports:
                    raise ValueError(
                        f"duplicate neural method {method!r} for {_task_name(task)}"
                    )
                neural_reports[method] = _metric_report(
                    report_payload, f"{path}.reports.{method}"
                )
                neural_resources[method] = extract_report_resource_usage(
                    payload, path, method
                )
                neural_paths[method] = str(path)
                method_coverage[method].add(task)

    for method, actual_tasks in sorted(method_coverage.items()):
        if actual_tasks != expected_tasks:
            raise _coverage_error(
                f"suite={suite!r}, method={method!r}", expected_tasks, actual_tasks
            )
    if not method_coverage:
        raise ValueError(f"no neural methods found for suite {suite!r}")
    expected_methods = set(method_coverage)
    for task, run in runs.items():
        actual_methods = set(run["neural_reports"])
        if actual_methods != expected_methods:
            raise ValueError(
                f"method coverage mismatch for {_task_name(task)}: "
                f"missing={sorted(expected_methods - actual_methods)}, "
                f"unexpected={sorted(actual_methods - expected_methods)}"
            )

    coverage = {
        "validated": True,
        "authoritative_task_source": str(gate_root / suite),
        "expected_task_count": len(expected_tasks),
        "expected_tasks": sorted(_task_name(task) for task in expected_tasks),
        "neural_roots": root_coverage,
        "methods": {
            method: {
                "task_count": len(tasks),
                "missing_tasks": [],
                "unexpected_tasks": [],
                "validated": True,
            }
            for method, tasks in sorted(method_coverage.items())
        },
        "split_fingerprint_pair_checks": split_fingerprint_checks,
        "split_fingerprints_validated": True,
    }
    return [runs[task] for task in sorted(runs)], coverage


def describe(values: Iterable[float]) -> dict[str, float]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.size == 0:
        raise ValueError("cannot describe zero values")
    return {
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "std": float(array.std(ddof=0)),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
    }


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=lambda name: (p_values[name], name))
    adjusted: dict[str, float] = {}
    running_max = 0.0
    hypotheses = len(ordered)
    for rank, name in enumerate(ordered):
        candidate = min(1.0, (hypotheses - rank) * p_values[name])
        running_max = max(running_max, candidate)
        adjusted[name] = running_max
    return adjusted


def _stable_bootstrap_seed(base_seed: int, scope: str, key: str) -> int:
    payload = f"{base_seed}|{scope}|{key}".encode("utf-8")
    offset = int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")
    return (int(base_seed) + offset) % (2**63 - 1)


def scenario_block_bootstrap_ci(
    scenario_deltas: Iterable[float],
    repetitions: int,
    seed: int,
) -> dict[str, object]:
    values = np.asarray(list(scenario_deltas), dtype=np.float64)
    if values.size == 0:
        raise ValueError("cannot bootstrap zero scenario blocks")
    if repetitions < 100:
        raise ValueError("bootstrap_repetitions must be at least 100")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(repetitions, values.size))
    bootstrap_means = values[indices].mean(axis=1)
    lower, upper = np.percentile(bootstrap_means, [2.5, 97.5])
    return {
        "method": "percentile_scenario_block_bootstrap",
        "confidence_level": 0.95,
        "repetitions": repetitions,
        "seed": int(seed),
        "lower": float(lower),
        "upper": float(upper),
    }


def paired_effect_sizes(deltas: Iterable[float]) -> dict[str, dict[str, object]]:
    values = np.asarray(list(deltas), dtype=np.float64)
    nonzero = values[np.abs(values) > 1e-12]
    if values.size < 2:
        dz = {"value": None, "status": "undefined_fewer_than_two_pairs"}
    else:
        std = float(values.std(ddof=1))
        if std <= 1e-15:
            dz = {"value": None, "status": "undefined_zero_variance"}
        else:
            dz = {"value": float(values.mean() / std), "status": "computed"}
    if nonzero.size == 0:
        rank_biserial = {"value": 0.0, "status": "all_ties"}
    else:
        ranks = rankdata(np.abs(nonzero), method="average")
        positive = float(ranks[nonzero > 0].sum())
        negative = float(ranks[nonzero < 0].sum())
        rank_biserial = {
            "value": (positive - negative) / (positive + negative),
            "status": "computed",
        }
    return {
        "paired_cohens_dz": dz,
        "matched_pairs_rank_biserial": rank_biserial,
    }


def paired_wilcoxon(deltas: Iterable[float]) -> dict[str, object]:
    values = np.asarray(list(deltas), dtype=np.float64)
    nonzero = values[np.abs(values) > 1e-12]
    if nonzero.size == 0:
        return {
            "statistic": 0.0,
            "raw_p_value": 1.0,
            "holm_adjusted_p_value": None,
            "nonzero_pairs": 0,
            "status": "all_ties",
        }
    result = wilcoxon(nonzero, alternative="two-sided")
    return {
        "statistic": float(result.statistic),
        "raw_p_value": float(result.pvalue),
        "holm_adjusted_p_value": None,
        "nonzero_pairs": int(nonzero.size),
        "status": "computed",
    }


def _scenario_key(run: dict[str, object], include_suite: bool) -> str:
    scenario = str(run["scenario"])
    return f"{run['suite']}/{scenario}" if include_suite else scenario


def _resource_summary(
    runs: list[dict[str, object]], methods: list[str]
) -> dict[str, object]:
    owners = ["gate", *methods]
    summary: dict[str, object] = {}
    for owner in owners:
        owner_summary: dict[str, object] = {}
        for resource in RESOURCE_PATHS:
            recorded: list[float] = []
            missing_tasks: list[str] = []
            sources: set[str] = set()
            for run in runs:
                usage = (
                    run["gate_resources"]
                    if owner == "gate"
                    else run["neural_resources"][owner]
                )
                item = usage[resource]
                if item["status"] == "recorded":
                    recorded.append(float(item["value"]))
                    sources.add(str(item["source"]))
                else:
                    missing_tasks.append(str(run["task_id"]))
            if not recorded:
                status = "missing"
            elif missing_tasks:
                status = "partially_recorded"
            else:
                status = "recorded"
            owner_summary[resource] = {
                "status": status,
                "recorded_count": len(recorded),
                "missing_count": len(missing_tasks),
                "missing_tasks": missing_tasks,
                "sources": sorted(sources),
                "descriptive": describe(recorded) if recorded else None,
            }
        summary[owner] = owner_summary
    return summary


def aggregate_scope(
    runs: list[dict[str, object]],
    scope: str,
    bootstrap_repetitions: int,
    bootstrap_seed: int,
    include_suite_in_scenario: bool,
) -> dict[str, object]:
    if not runs:
        raise ValueError(f"cannot aggregate zero runs for {scope}")
    gate_methods = {str(run["gate_method"]) for run in runs}
    if len(gate_methods) != 1:
        raise ValueError(f"inconsistent gate methods for {scope}: {sorted(gate_methods)}")
    method_sets = [set(run["neural_reports"]) for run in runs]
    expected_methods = method_sets[0]
    if not expected_methods:
        raise ValueError(f"no neural methods for {scope}")
    for run, methods in zip(runs, method_sets):
        if methods != expected_methods:
            raise ValueError(
                f"method coverage mismatch for {run['task_id']}: "
                f"expected={sorted(expected_methods)}, actual={sorted(methods)}"
            )
    methods = sorted(expected_methods)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        grouped[_scenario_key(run, include_suite_in_scenario)].append(run)
    scenario_seed_counts = {
        scenario: len({int(run["seed"]) for run in items})
        for scenario, items in sorted(grouped.items())
    }

    result: dict[str, object] = {
        "scope": scope,
        "gate_method": next(iter(gate_methods)),
        "gate_source_methods": sorted(
            {str(run["gate_source_method"]) for run in runs}
        ),
        "gate_effective_risk_selections": sorted(
            {str(run["gate_effective_risk_selection"]) for run in runs}
        ),
        "run_count": len(runs),
        "scenario_inference_units": len(grouped),
        "inference_unit": "scenario",
        "seed_role": "repeated_measurement_averaged_within_scenario",
        "scenario_seed_counts": scenario_seed_counts,
        "holm_family": "all_method_by_metric_tests_within_this_scope",
        "holm_hypotheses": len(methods) * len(REPORT_METRICS),
        "methods": {},
        "resource_summary": _resource_summary(runs, methods),
    }
    raw_p_values: dict[str, float] = {}
    for method in methods:
        method_result: dict[str, object] = {"metrics": {}}
        for metric in REPORT_METRICS:
            direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
            gate_scenario_means: list[float] = []
            baseline_scenario_means: list[float] = []
            scenario_deltas: list[float] = []
            scenario_rows: list[dict[str, object]] = []
            for scenario, items in sorted(grouped.items()):
                gate_mean = float(
                    np.mean([run["gate_report"][metric] for run in items])
                )
                baseline_mean = float(
                    np.mean(
                        [run["neural_reports"][method][metric] for run in items]
                    )
                )
                oriented_delta = direction * (gate_mean - baseline_mean)
                gate_scenario_means.append(gate_mean)
                baseline_scenario_means.append(baseline_mean)
                scenario_deltas.append(oriented_delta)
                scenario_rows.append(
                    {
                        "scenario": scenario,
                        "seed_count": len(items),
                        "gate_mean": gate_mean,
                        "baseline_mean": baseline_mean,
                        "oriented_gate_delta": oriented_delta,
                    }
                )
            wilcoxon_report = paired_wilcoxon(scenario_deltas)
            hypothesis = f"{method}::{metric}"
            raw_p_values[hypothesis] = float(wilcoxon_report["raw_p_value"])
            inference = {
                "oriented_higher_is_better": True,
                "mean_delta": float(np.mean(scenario_deltas)),
                "median_delta": float(np.median(scenario_deltas)),
                "wins": int(np.sum(np.asarray(scenario_deltas) > 1e-12)),
                "ties": int(np.sum(np.abs(scenario_deltas) <= 1e-12)),
                "losses": int(np.sum(np.asarray(scenario_deltas) < -1e-12)),
                "bootstrap_95_ci": scenario_block_bootstrap_ci(
                    scenario_deltas,
                    bootstrap_repetitions,
                    _stable_bootstrap_seed(bootstrap_seed, scope, hypothesis),
                ),
                "effect_sizes": paired_effect_sizes(scenario_deltas),
                "wilcoxon": wilcoxon_report,
            }
            method_result["metrics"][metric] = {
                "direction": "lower_is_better" if direction < 0 else "higher_is_better",
                "gate_scenario_mean": float(np.mean(gate_scenario_means)),
                "baseline_scenario_mean": float(np.mean(baseline_scenario_means)),
                "paired_inference": inference,
                "scenario_blocks": scenario_rows,
            }
        result["methods"][method] = method_result

    adjusted = holm_adjust(raw_p_values)
    for hypothesis, adjusted_p in adjusted.items():
        method, metric = hypothesis.split("::", 1)
        wilcoxon_report = result["methods"][method]["metrics"][metric][
            "paired_inference"
        ]["wilcoxon"]
        wilcoxon_report["holm_adjusted_p_value"] = adjusted_p
    return result


def parse_neural_roots(values: Iterable[str]) -> dict[str, list[Path]]:
    roots: dict[str, list[Path]] = defaultdict(list)
    for value in values:
        if "=" not in value:
            raise ValueError(f"--neural-root must use suite=directory: {value!r}")
        suite, raw_path = value.split("=", 1)
        if not suite.strip() or not raw_path.strip():
            raise ValueError(f"--neural-root must use suite=directory: {value!r}")
        roots[suite.strip()].append(Path(raw_path))
    return dict(roots)


def build_report(
    gate_root: Path,
    roots: dict[str, list[Path]],
    bootstrap_repetitions: int = 10_000,
    bootstrap_seed: int = 20250715,
    inference_seeds: Optional[Iterable[int]] = None,
    gate_policy_name: Optional[str] = None,
) -> dict[str, object]:
    if bootstrap_repetitions < 100:
        raise ValueError("bootstrap_repetitions must be at least 100")
    requested_inference_seeds = (
        None
        if inference_seeds is None
        else tuple(sorted({int(seed) for seed in inference_seeds}))
    )
    if requested_inference_seeds == ():
        raise ValueError("inference_seeds cannot be empty")
    if requested_inference_seeds is not None and any(
        seed < 0 for seed in requested_inference_seeds
    ):
        raise ValueError("inference_seeds cannot contain negative values")
    all_runs: list[dict[str, object]] = []
    all_validated_runs: list[dict[str, object]] = []
    coverage: dict[str, object] = {}
    by_suite: dict[str, object] = {}
    for suite, neural_roots in sorted(roots.items()):
        validated_runs, suite_coverage = load_suite_runs(
            gate_root, suite, neural_roots, gate_policy_name=gate_policy_name
        )
        all_validated_runs.extend(validated_runs)
        validated_seeds = sorted({int(run["seed"]) for run in validated_runs})
        if requested_inference_seeds is None:
            runs = validated_runs
        else:
            missing_seeds = sorted(
                set(requested_inference_seeds) - set(validated_seeds)
            )
            if missing_seeds:
                raise ValueError(
                    f"inference seed coverage mismatch for {suite}: "
                    f"missing={missing_seeds}, validated={validated_seeds}"
                )
            runs = [
                run
                for run in validated_runs
                if int(run["seed"]) in requested_inference_seeds
            ]
        suite_coverage["validated_seeds"] = validated_seeds
        suite_coverage["validated_task_count"] = len(validated_runs)
        suite_coverage["inference_seeds"] = sorted(
            {int(run["seed"]) for run in runs}
        )
        suite_coverage["inference_task_count"] = len(runs)
        all_runs.extend(runs)
        coverage[suite] = suite_coverage
        by_suite[suite] = aggregate_scope(
            runs,
            scope=f"suite:{suite}",
            bootstrap_repetitions=bootstrap_repetitions,
            bootstrap_seed=bootstrap_seed,
            include_suite_in_scenario=False,
        )
    if not all_runs:
        raise ValueError("cannot build report without paired runs")
    validated_seeds = sorted(
        {int(run["seed"]) for run in all_validated_runs}
    )
    selected_inference_seeds = sorted({int(run["seed"]) for run in all_runs})
    excluded_seeds = sorted(set(validated_seeds) - set(selected_inference_seeds))
    global_summary = aggregate_scope(
        all_runs,
        scope="global",
        bootstrap_repetitions=bootstrap_repetitions,
        bootstrap_seed=bootstrap_seed,
        include_suite_in_scenario=True,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "inference_protocol": {
            "primary_inference_unit": "scenario",
            "seed_role": "repeated_measurement_averaged_within_scenario",
            "bootstrap": "scenario-block percentile bootstrap",
            "confidence_level": 0.95,
            "bootstrap_repetitions": bootstrap_repetitions,
            "bootstrap_seed": bootstrap_seed,
            "validated_seeds": validated_seeds,
            "inference_seeds": selected_inference_seeds,
            "excluded_from_inference_seeds": excluded_seeds,
            "validated_run_count": len(all_validated_runs),
            "inference_run_count": len(all_runs),
            "paired_effect_sizes": [
                "paired_cohens_dz",
                "matched_pairs_rank_biserial",
            ],
            "test": "two-sided paired Wilcoxon on scenario means",
            "multiplicity": (
                "Holm correction across all method-by-metric tests within "
                "each reported scope"
            ),
        },
        "metric_contract": {
            metric: {
                "direction": (
                    "lower_is_better" if metric in LOWER_IS_BETTER else "higher_is_better"
                )
            }
            for metric in REPORT_METRICS
        },
        "coverage_validation": coverage,
        "by_suite": by_suite,
        "global": global_summary,
        "runs": all_runs,
    }


def _format_optional(value: object, digits: int = 6) -> str:
    return "NA" if value is None else f"{float(value):.{digits}f}"


def markdown_report(report: dict[str, object]) -> str:
    protocol = report["inference_protocol"]
    lines = [
        "# Neural comparison strict v2",
        "",
        "Inference unit: scenario. Seed repeats are averaged within scenario before inference.",
        "CI: scenario-block percentile bootstrap. Wilcoxon p-values use Holm correction within each scope.",
        "Positive oriented deltas favor the gate method; FPR95 is sign-reversed.",
        f"Validated seeds: {protocol['validated_seeds']}; inference seeds: "
        f"{protocol['inference_seeds']}; excluded from inference: "
        f"{protocol['excluded_from_inference_seeds']}.",
        "",
        "## Coverage",
        "",
    ]
    for suite, item in report["coverage_validation"].items():
        lines.append(
            f"- {suite}: {item['expected_task_count']} tasks; "
            f"{item['split_fingerprint_pair_checks']} paired split-fingerprint checks; validated"
        )
    scopes = [("Global", report["global"])] + [
        (f"Suite: {suite}", summary)
        for suite, summary in report["by_suite"].items()
    ]
    for title, summary in scopes:
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                f"Runs: {summary['run_count']}; scenario units: {summary['scenario_inference_units']}.",
                "",
                "| Method | Metric | Gate | Baseline | Oriented delta [95% CI] | dz | Rank-biserial | W/T/L | p | Holm p |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for method, method_item in summary["methods"].items():
            for metric in REPORT_METRICS:
                item = method_item["metrics"][metric]
                paired = item["paired_inference"]
                ci = paired["bootstrap_95_ci"]
                effects = paired["effect_sizes"]
                test = paired["wilcoxon"]
                lines.append(
                    f"| {method} | {metric} | {item['gate_scenario_mean']:.6f} | "
                    f"{item['baseline_scenario_mean']:.6f} | {paired['mean_delta']:+.6f} "
                    f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
                    f"{_format_optional(effects['paired_cohens_dz']['value'], 3)} | "
                    f"{_format_optional(effects['matched_pairs_rank_biserial']['value'], 3)} | "
                    f"{paired['wins']}/{paired['ties']}/{paired['losses']} | "
                    f"{test['raw_p_value']:.3g} | {test['holm_adjusted_p_value']:.3g} |"
                )
        lines.extend(
            [
                "",
                "### Resource reporting",
                "",
                "Missing measurements are reported as NA; they are never imputed as zero.",
                "",
                "| Method | Resource | Status | Recorded/Missing | Mean |",
                "|---|---|---|---:|---:|",
            ]
        )
        for method, resources in summary["resource_summary"].items():
            display = summary["gate_method"] if method == "gate" else method
            for resource, item in resources.items():
                descriptive = item["descriptive"]
                mean = descriptive["mean"] if descriptive is not None else None
                lines.append(
                    f"| {display} | {resource} | {item['status']} | "
                    f"{item['recorded_count']}/{item['missing_count']} | "
                    f"{_format_optional(mean)} |"
                )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    roots = parse_neural_roots(args.neural_root)
    report = build_report(
        Path(args.gate_root),
        roots,
        bootstrap_repetitions=args.bootstrap_repetitions,
        bootstrap_seed=args.bootstrap_seed,
        inference_seeds=parse_inference_seeds(args.inference_seeds),
        gate_policy_name=args.gate_policy_name,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "comparison_strict_v2.json"
    markdown_path = output_dir / "comparison_strict_v2.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(markdown_report(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "schema_version": report["schema_version"],
                "suites": sorted(report["by_suite"]),
                "runs": report["global"]["run_count"],
                "scenario_inference_units": report["global"][
                    "scenario_inference_units"
                ],
                "output_json": str(json_path),
                "output_markdown": str(markdown_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
