#!/usr/bin/env python3
"""Bind one runner evidence directory into a fail-closed raw_run_v2 receipt.

The adapter discovers immutable runner artifacts, independently verifies the
runner's evidence.sha256, hashes staged split-host evidence, writes a binding
manifest/input, and delegates every scientific gate to current_hardware_279.
It never fabricates missing windows, resources, identities, fallback events,
labels, predictions, or latency samples.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.current_hardware_279 import compose_current_hardware_raw_run_v2


RAW_SCOPE = "hft_mgbs_current_hardware_2_79_raw_run_v2"
INPUT_SCOPE = "hft_mgbs_current_hardware_2_79_raw_run_input_v2"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

AUTO_ARTIFACTS = {
    "runner": "frozen/runner.sh",
    "config": "frozen/config.json",
    "capture_binary": "frozen/tpacket_v3_full_pipeline",
    "pipeline_raw": "pipeline_raw.json",
    "diagnostic_receipt": "diagnostic_receipt.json",
    "pipeline_ready": "pipeline_ready.json",
    "execution_events": "execution_events.tsv",
    "nic_statistics_before": "before_ens8f0_statistics.txt",
    "nic_statistics_after": "pre_restore_ens8f0_statistics.txt",
}

STAGED_ARTIFACT_FLAGS = {
    "model": "model",
    "runtime_manifest": "runtime_manifest",
    "service_source": "service_source",
    "engine_source": "engine_source",
    "service_launcher": "service_launcher",
    "identity_receipt": "identity_receipt",
    "window_observations": "window_observations",
    "physical_resources": "physical_resources",
    "service_resources": "service_resources",
}


class AdapterError(ValueError):
    """The source evidence cannot be trusted or safely bound."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _reference(root: Path, path: Path) -> dict[str, str]:
    if not _regular(path) or not _within(root, path):
        raise AdapterError(f"unsafe artifact path: {path}")
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": _sha256(path),
    }


def verify_runner_manifest(evidence_dir: Path, manifest_path: Path) -> dict[str, str]:
    """Rehash every source-manifest entry; textual check receipts are ignored."""

    root = evidence_dir.resolve()
    manifest = manifest_path.resolve()
    if not _regular(manifest_path) or not _within(root, manifest):
        raise AdapterError("runner evidence manifest is missing, symlinked, or outside evidence_dir")
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise AdapterError(f"runner evidence manifest is unreadable: {error}") from error
    if not lines:
        raise AdapterError("runner evidence manifest is empty")
    entries: dict[str, str] = {}
    for index, line in enumerate(lines, 1):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n\x00]+)", line)
        if match is None:
            raise AdapterError(f"runner evidence manifest line {index} is malformed")
        expected, name = match.groups()
        posix = PurePosixPath(name)
        if posix.is_absolute() or ".." in posix.parts or name in entries:
            raise AdapterError(f"runner evidence manifest line {index} has an unsafe/duplicate path")
        candidate = root / Path(*posix.parts)
        if not _regular(candidate) or not _within(root, candidate):
            raise AdapterError(f"runner evidence manifest entry is missing or unsafe: {name}")
        observed = _sha256(candidate)
        if observed != expected:
            raise AdapterError(
                f"runner evidence manifest hash drift: {name}: expected={expected}: observed={observed}"
            )
        entries[name] = observed
    return entries


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(value.encode("utf-8"))
    os.replace(temporary, path)


def _failure(error: Exception | str, gaps: Sequence[str] = ()) -> dict[str, Any]:
    detail = str(error)
    return {
        "schema_version": 2,
        "scope": RAW_SCOPE,
        "audit_complete": False,
        "run_qualified": False,
        "candidate_evidence_qualified": False,
        "full_pipeline_qualified": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "adapter": {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_runner_adapter_v1",
            "source_manifest_verified": False,
            "binding_manifest_verified_by_composer": False,
        },
        "evidence_gaps": sorted(set(gaps)),
        "errors": ["adapter:" + detail],
    }


def _staged_path(root: Path, raw: Path | None, name: str, gaps: list[str]) -> Path | None:
    if raw is None:
        gaps.append("missing:" + name)
        return None
    path = raw.resolve()
    if not _regular(raw):
        gaps.append("missing_or_symlinked:" + name)
        return None
    if not _within(root, path):
        gaps.append("outside_binding_root:" + name)
        return None
    return path


def bind_runner_evidence(
    *,
    profile_path: Path,
    evidence_dir: Path,
    binding_root: Path,
    work_dir: Path,
    campaign_id: str,
    candidate_id: str,
    backend: str,
    mode: str,
    repeat_index: int,
    source_manifest: Path,
    staged_artifacts: Mapping[str, Path | None],
    quality_labels: Path | None,
    quality_predictions: Path | None,
    fallback_events: Path | None,
) -> tuple[dict[str, Any], Path, Path]:
    """Create binding files and return the independently recomputed receipt."""

    evidence = evidence_dir.resolve()
    root = binding_root.resolve()
    work = work_dir.resolve()
    if evidence_dir.is_symlink() or not evidence.is_dir():
        raise AdapterError("evidence_dir is missing or symlinked")
    if binding_root.is_symlink() or not root.is_dir():
        raise AdapterError("binding_root is missing or symlinked")
    if not _within(root, evidence):
        raise AdapterError("evidence_dir must be inside binding_root")
    if not _within(root, work):
        raise AdapterError("work_dir must be inside binding_root")
    if work.exists():
        if work.is_symlink() or not work.is_dir() or any(work.iterdir()):
            raise AdapterError("work_dir must be new or empty")
    else:
        work.mkdir(parents=True, mode=0o700)

    source_entries = verify_runner_manifest(evidence, source_manifest)
    gaps: list[str] = []
    artifacts: dict[str, Path | None] = {}
    for name, relative in AUTO_ARTIFACTS.items():
        path = evidence / Path(*PurePosixPath(relative).parts)
        if not _regular(path):
            gaps.append("missing:" + name)
            artifacts[name] = None
            continue
        if source_entries.get(relative) != _sha256(path):
            gaps.append("not_bound_by_runner_manifest:" + name)
        artifacts[name] = path.resolve()
    for name in STAGED_ARTIFACT_FLAGS:
        artifacts[name] = _staged_path(root, staged_artifacts.get(name), name, gaps)

    pktgen_paths = sorted(evidence.glob("pktgen_device_*.txt"))
    safe_pktgen: list[Path] = []
    if not pktgen_paths:
        gaps.append("missing:pktgen_devices")
    for path in pktgen_paths:
        relative = path.resolve().relative_to(evidence).as_posix()
        if not _regular(path):
            gaps.append("missing_or_symlinked:pktgen_device")
        elif source_entries.get(relative) != _sha256(path):
            gaps.append("not_bound_by_runner_manifest:" + relative)
        else:
            safe_pktgen.append(path.resolve())

    labels = _staged_path(root, quality_labels, "quality_labels", gaps)
    predictions = _staged_path(root, quality_predictions, "quality_predictions", gaps)
    quality_source = None
    quality_prepare_receipt = None
    if labels is not None:
        try:
            label_value = json.loads(labels.read_text(encoding="utf-8"))
            raw_source = label_value.get("source_artifact_path") if isinstance(label_value, Mapping) else None
            if isinstance(raw_source, str) and raw_source:
                source_candidate = labels.parent / Path(*PurePosixPath(raw_source).parts)
                quality_source = _staged_path(root, source_candidate, "quality_source", gaps)
            raw_prepare = label_value.get("prepare_receipt_path") if isinstance(label_value, Mapping) else None
            if isinstance(raw_prepare, str) and raw_prepare:
                prepare_candidate = labels.parent / Path(*PurePosixPath(raw_prepare).parts)
                quality_prepare_receipt = _staged_path(
                    root, prepare_candidate, "quality_prepare_receipt", gaps
                )
        except (OSError, UnicodeError, json.JSONDecodeError):
            gaps.append("invalid:quality_labels_source_reference")
    fallback = None
    if mode == "fallback":
        fallback = _staged_path(root, fallback_events, "fallback_events", gaps)
    elif fallback_events is not None:
        gaps.append("unexpected:fallback_events_for_normal_mode")

    bound_paths = [path for path in artifacts.values() if path is not None]
    bound_paths.extend(safe_pktgen)
    bound_paths.extend(
        path
        for path in (labels, quality_source, quality_prepare_receipt, predictions, fallback)
        if path is not None
    )
    bound_paths.append(source_manifest.resolve())
    unique: dict[str, Path] = {}
    for path in bound_paths:
        if not _regular(path) or not _within(root, path):
            raise AdapterError(f"bound path became unsafe: {path}")
        relative = path.resolve().relative_to(root).as_posix()
        if relative in unique and unique[relative] != path:
            raise AdapterError(f"duplicate binding path: {relative}")
        unique[relative] = path
    binding_manifest = work / "raw_run_v2.binding.sha256"
    manifest_text = "".join(f"{_sha256(path)}  {name}\n" for name, path in sorted(unique.items()))
    _atomic_text(binding_manifest, manifest_text)

    def ref(path: Path | None) -> dict[str, str] | None:
        return _reference(root, path) if path is not None else None

    request = {
        "schema_version": 2,
        "scope": INPUT_SCOPE,
        "profile_sha256": _sha256(profile_path),
        "evidence_root": str(root),
        "campaign_id": campaign_id,
        "candidate_id": candidate_id,
        "backend": backend,
        "mode": mode,
        "repeat_index": repeat_index,
        "evidence_manifest": ref(binding_manifest),
        "artifacts": {name: ref(path) for name, path in artifacts.items()},
        "pktgen_devices": [ref(path) for path in safe_pktgen],
        "quality": {"source": ref(quality_source), "labels": ref(labels), "predictions": ref(predictions)}
        if labels is not None and predictions is not None
        else None,
        "fallback_events": ref(fallback),
        "adapter_source": {
            "runner_evidence_dir": str(evidence),
            "runner_manifest": ref(source_manifest.resolve()),
            "runner_manifest_entry_count": len(source_entries),
        },
    }
    input_path = work / "raw_run_v2.input.json"
    _atomic_json(input_path, request)
    result = compose_current_hardware_raw_run_v2(profile_path, input_path)
    result["adapter"] = {
        "schema_version": 1,
        "scope": "hft_mgbs_current_hardware_2_79_runner_adapter_v1",
        "source_manifest_verified": True,
        "source_manifest_sha256": _sha256(source_manifest),
        "source_manifest_entry_count": len(source_entries),
        "binding_manifest_verified_by_composer": not any(
            str(error).startswith("evidence_manifest") for error in result.get("errors", [])
        ),
        "binding_manifest_sha256": _sha256(binding_manifest),
        "input_sha256": _sha256(input_path),
    }
    result["evidence_gaps"] = sorted(set(gaps))
    if gaps and result.get("run_qualified") is True:
        raise AdapterError("internal error: a run with evidence gaps qualified")
    return result, input_path, binding_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bind a current-hardware runner directory into raw_run_v2 without synthesizing evidence."
    )
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--binding-root", type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--backend", default="tpacket_v3")
    parser.add_argument("--mode", choices=("normal", "fallback"), required=True)
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--output", type=Path)
    for option in STAGED_ARTIFACT_FLAGS.values():
        parser.add_argument("--" + option.replace("_", "-"), dest=option, type=Path)
    parser.add_argument("--quality-labels", type=Path)
    parser.add_argument("--quality-predictions", type=Path)
    parser.add_argument("--fallback-events", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    evidence = args.evidence_dir.resolve()
    root = (args.binding_root or evidence).resolve()
    work = (args.work_dir or (evidence / f"v2_binding_{args.mode}_r{args.repeat_index}")).resolve()
    manifest = (
        (args.source_manifest if args.source_manifest.is_absolute() else evidence / args.source_manifest)
        if args.source_manifest is not None
        else evidence / "evidence.sha256"
    ).resolve()
    output = (args.output or (work / "raw_run_v2.json")).resolve()
    def staged_path(value: Path | None) -> Path | None:
        if value is None:
            return None
        return (value if value.is_absolute() else root / value).resolve()

    staged = {
        name: staged_path(getattr(args, option))
        for name, option in STAGED_ARTIFACT_FLAGS.items()
    }
    try:
        result, input_path, binding_manifest = bind_runner_evidence(
            profile_path=args.profile.resolve(),
            evidence_dir=evidence,
            binding_root=root,
            work_dir=work,
            campaign_id=args.campaign_id,
            candidate_id=args.candidate_id,
            backend=args.backend,
            mode=args.mode,
            repeat_index=args.repeat_index,
            source_manifest=manifest,
            staged_artifacts=staged,
            quality_labels=staged_path(args.quality_labels),
            quality_predictions=staged_path(args.quality_predictions),
            fallback_events=staged_path(args.fallback_events),
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        _atomic_json(output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        print(f"input={input_path}", file=sys.stderr)
        print(f"binding_manifest={binding_manifest}", file=sys.stderr)
        if not result.get("audit_complete"):
            return 3
        return 0 if result.get("run_qualified") else 2
    except (AdapterError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        result = _failure(error)
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _atomic_json(output, result)
        except OSError:
            pass
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
