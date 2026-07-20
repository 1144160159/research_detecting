from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable, Optional


RESOURCE_PATHS = {
    "training_seconds": (
        ("training_seconds",),
        ("runtime", "training_seconds"),
        ("timing", "training_seconds"),
    ),
    "elapsed_seconds": (
        ("elapsed_seconds",),
        ("runtime", "elapsed_seconds"),
        ("timing", "elapsed_seconds"),
    ),
    "inference_seconds": (
        ("inference_seconds",),
        ("runtime", "inference_seconds"),
        ("timing", "inference_seconds"),
    ),
    "inference_samples_per_second": (
        ("inference_samples_per_second",),
        ("runtime", "inference_samples_per_second"),
        ("timing", "inference_samples_per_second"),
    ),
    "peak_gpu_memory_mb": (
        ("peak_gpu_memory_mb",),
        ("runtime", "peak_gpu_memory_mb"),
        ("resources", "peak_gpu_memory_mb"),
    ),
    "trainable_parameters": (
        ("trainable_parameters",),
        ("resources", "trainable_parameters"),
    ),
}

HARDWARE_PATHS = (
    ("hardware", "gpu_name"),
    ("runtime", "gpu_name"),
    ("environment", "gpu_name"),
)


def _lookup(payload: dict[str, Any], paths: Iterable[tuple[str, ...]]) -> object:
    for path in paths:
        value: object = payload
        for key in path:
            if not isinstance(value, dict) or key not in value:
                break
            value = value[key]
        else:
            return value
    return None


def _finite_nonnegative(value: object) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0.0 else None


def _describe(values: list[float]) -> Optional[dict[str, float]]:
    if not values:
        return None
    ordered = sorted(values)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "minimum": ordered[0],
        "median": statistics.median(ordered),
        "mean": sum(ordered) / len(ordered),
        "p95": ordered[p95_index],
        "maximum": ordered[-1],
    }


def _parse_mapping(values: list[str], option: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"{option} must use NAME=VALUE: {value!r}")
        name, item = value.split("=", 1)
        name, item = name.strip(), item.strip()
        if not name or not item or name in result:
            raise ValueError(f"invalid or duplicate {option}: {value!r}")
        result[name] = item
    return result


def _read_metrics(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("metrics root is not an object")
    return payload


def audit_source(
    name: str,
    root: Path,
    expected_runs: int,
    model_filter: Optional[str] = None,
) -> dict[str, Any]:
    metrics_paths = sorted(root.glob("**/metrics.json"))
    failure_paths = sorted(root.glob("**/failure.json"))
    selected: list[tuple[Path, dict[str, Any]]] = []
    issues: list[str] = []
    for path in metrics_paths:
        try:
            payload = _read_metrics(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            issues.append(f"cannot read {path}: {error}")
            continue
        if model_filter is not None and not (
            payload.get("model") == model_filter or payload.get("method") == model_filter
        ):
            continue
        selected.append((path, payload))

    fields: dict[str, Any] = {}
    for field, paths in RESOURCE_PATHS.items():
        values: list[float] = []
        invalid = 0
        present = 0
        for path, payload in selected:
            raw = _lookup(payload, paths)
            if raw is None:
                continue
            present += 1
            number = _finite_nonnegative(raw)
            if number is None:
                invalid += 1
                issues.append(f"invalid {field}={raw!r}: {path}")
            else:
                values.append(number)
        fields[field] = {
            "valid_count": len(values),
            "present_count": present,
            "invalid_count": invalid,
            "coverage_fraction": len(values) / expected_runs if expected_runs else 0.0,
            "complete": len(values) == expected_runs and invalid == 0,
            "descriptive_statistics": _describe(values),
        }

    hardware_values = set()
    for _, payload in selected:
        value = _lookup(payload, HARDWARE_PATHS)
        if value not in (None, ""):
            hardware_values.add(str(value))
    observed = len(selected)
    coverage_complete = observed == expected_runs and not failure_paths
    return {
        "name": name,
        "root": str(root),
        "model_filter": model_filter,
        "expected_runs": expected_runs,
        "discovered_metrics_files": len(metrics_paths),
        "observed_runs": observed,
        "failure_count": len(failure_paths),
        "coverage_complete": coverage_complete,
        "hardware_provenance_complete": len(hardware_values) == 1 and observed > 0,
        "hardware_values": sorted(hardware_values),
        "fields": fields,
        "issues": issues,
    }


def build_audit(sources: list[dict[str, Any]]) -> dict[str, Any]:
    if len(sources) < 2:
        raise ValueError("at least two efficiency evidence sources are required")

    def complete(field: str) -> bool:
        return all(source["fields"][field]["complete"] for source in sources)

    gates = {
        "run_coverage_complete": all(source["coverage_complete"] for source in sources),
        "training_time_same_semantics": complete("training_seconds"),
        "inference_time_complete": complete("inference_seconds"),
        "throughput_complete": complete("inference_samples_per_second"),
        "peak_gpu_memory_complete": complete("peak_gpu_memory_mb"),
        "parameter_count_complete": complete("trainable_parameters"),
        "hardware_provenance_complete": all(
            source["hardware_provenance_complete"] for source in sources
        ),
    }
    direct_required = (
        "run_coverage_complete",
        "training_time_same_semantics",
        "inference_time_complete",
        "throughput_complete",
        "peak_gpu_memory_complete",
        "hardware_provenance_complete",
    )
    direct_allowed = all(gates[name] for name in direct_required)
    any_existing = any(
        field["valid_count"] > 0
        for source in sources
        for field in source["fields"].values()
    )
    return {
        "schema_version": "strict_v4_efficiency_evidence_audit_v1",
        "scope": "artifact_only_no_experiment_rerun",
        "source_count": len(sources),
        "sources": sources,
        "comparison_gates": gates,
        "descriptive_existing_evidence_allowed": any_existing,
        "direct_efficiency_comparison_allowed": direct_allowed,
        "claim_rule": (
            "Existing fields may be described per method. Cross-method efficiency "
            "claims require complete same-semantics training and inference timing, "
            "throughput, peak GPU memory, and explicit hardware provenance."
        ),
        "required_follow_up": (
            []
            if direct_allowed
            else [
                "run a controlled post-selection efficiency benchmark on identical hardware",
                "separate training, calibration, and inference wall time",
                "record warm-up, repetitions, batch size, P50/P95/P99 latency and throughput",
                "record peak GPU memory and exact hardware/software provenance",
            ]
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 efficiency evidence audit",
        "",
        f"Direct comparison allowed: `{'YES' if report['direct_efficiency_comparison_allowed'] else 'NO'}`.",
        "",
        "| Method | Runs | Train | Wall | Inference | Throughput | GPU memory | Params |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for source in report["sources"]:
        fields = source["fields"]
        coverage = [
            f"{fields[name]['valid_count']}/{source['expected_runs']}"
            for name in RESOURCE_PATHS
        ]
        lines.append(
            f"| {source['name']} | {source['observed_runs']}/{source['expected_runs']} | "
            + " | ".join(coverage)
            + " |"
        )
    lines.extend(["", "## Comparison gates", ""])
    for name, passed in report["comparison_gates"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    if report["required_follow_up"]:
        lines.extend(["", "## Required follow-up", ""])
        lines.extend(f"- {item}" for item in report["required_follow_up"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit strict-v4 efficiency evidence without rerunning experiments"
    )
    parser.add_argument("--source", action="append", required=True, help="NAME=ROOT")
    parser.add_argument(
        "--expected", action="append", required=True, help="NAME=EXPECTED_RUNS"
    )
    parser.add_argument(
        "--model-filter", action="append", default=[], help="NAME=MODEL_OR_METHOD"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--require-comparable", action="store_true")
    args = parser.parse_args()

    roots = _parse_mapping(args.source, "--source")
    expected_raw = _parse_mapping(args.expected, "--expected")
    filters = _parse_mapping(args.model_filter, "--model-filter")
    if set(roots) != set(expected_raw):
        raise ValueError("--source and --expected names must match exactly")
    if not set(filters).issubset(roots):
        raise ValueError("--model-filter names must also be declared by --source")
    sources = [
        audit_source(
            name,
            Path(root),
            int(expected_raw[name]),
            filters.get(name),
        )
        for name, root in roots.items()
    ]
    report = build_audit(sources)
    report["audit_implementation_sha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "audit.md").write_text(
        render_markdown(report), encoding="utf-8"
    )
    print(render_markdown(report), end="")
    if args.require_comparable and not report["direct_efficiency_comparison_allowed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
