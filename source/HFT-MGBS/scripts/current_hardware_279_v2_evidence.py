#!/usr/bin/env python3
"""Read-only evidence collection and strict v2 normalization.

The tool has three phases:

* ``prepare`` freezes already-running GPU runtime artifacts and rehashes every
  runtime binding.  It never starts or stops the service.
* ``collect`` samples one node at aligned one-second boundaries.  It never
  starts traffic and never changes a process, NIC, IRQ, or service.
* ``finalize`` emits adapter artifacts only when the underlying timestamped
  observations are sufficient.  Missing evidence is reported as a gap; totals
  and percentiles are never expanded into per-window observations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "current_hardware_2_79_evidence_collector_v1.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PREPARE_SCOPE = "hft_mgbs_current_hardware_2_79_evidence_prepare_v1"
RAW_SCOPE = "hft_mgbs_current_hardware_2_79_node_raw_boundaries_v1"
FINALIZE_SCOPE = "hft_mgbs_current_hardware_2_79_evidence_finalize_v1"
RESOURCE_SCOPE = "hft_mgbs_current_hardware_2_79_resource_samples_v2"
WINDOW_SCOPE = "hft_mgbs_current_hardware_2_79_window_observations_v2"
IDENTITY_SCOPE = "hft_mgbs_current_hardware_2_79_run_identity_receipt_v2"
LABEL_SCOPE = "hft_mgbs_independent_ground_truth_labels_v1"
PREDICTION_SCOPE = "hft_mgbs_independent_predictions_v1"
LABEL_SCOPE_V2 = "hft_mgbs_independent_ground_truth_labels_v2"
PREDICTION_SCOPE_V2 = "hft_mgbs_independent_predictions_v2"
QUALITY_SOURCE_SCOPE = "hft_mgbs_unsw_official_quality_source_v1"
FALLBACK_SCOPE = "hft_mgbs_current_hardware_2_79_fallback_events_v2"


class CollectorError(ValueError):
    """An input cannot be safely frozen, read, or normalized."""


def _strict_object(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CollectorError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CollectorError("unreadable JSON {}: {}".format(path, error)) from error
    if not isinstance(value, Mapping):
        raise CollectorError("JSON root must be an object: {}".format(path))
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(
        (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
            "utf-8"
        )
    )
    os.replace(str(temporary), str(path))


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(str(temporary), str(path))


def _regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _new_directory(path: Path) -> Path:
    resolved = path.resolve()
    if path.exists():
        if path.is_symlink() or not path.is_dir() or any(path.iterdir()):
            raise CollectorError("output directory must be new or empty: {}".format(path))
    else:
        path.mkdir(parents=True, mode=0o700)
    return resolved


def _config(path: Path) -> Mapping[str, Any]:
    value = _load_json(path)
    expected_samples = {
        "packet_latency_us": 1000,
        "flow_latency_us": 1000,
        "kernel_to_feature_latency_us": 1000,
        "end_to_end_latency_us": 1000,
        "gpu_batch_latency_us": 100,
    }
    if (
        value.get("schema_version") != 1
        or value.get("scope") != "hft_mgbs_current_hardware_2_79_evidence_collector_v1"
        or value.get("boundary_interval_ns") != 1_000_000_000
        or value.get("required_consecutive_windows") != 15
        or value.get("boundary_max_skew_ns") != 250_000_000
        or value.get("clock_sync_max_absolute_offset_ns") != 50_000_000
        or value.get("cross_node_clock_max_offset_bound_ns") != 250_000_000
        or value.get("cross_node_boundary_max_skew_ns") != 100_000_000
        or value.get("minimum_latency_samples_per_window") != expected_samples
        or not isinstance(value.get("clock_sync_max_absolute_offset_ns"), int)
        or value.get("clock_sync_max_absolute_offset_ns", 0) <= 0
        or not isinstance(value.get("cross_node_boundary_max_skew_ns"), int)
        or value.get("cross_node_boundary_max_skew_ns", 0) <= 0
        or not isinstance(value.get("cross_node_clock_max_offset_bound_ns"), int)
        or value.get("cross_node_clock_max_offset_bound_ns", 0) <= 0
    ):
        raise CollectorError("unsupported or drifted collector config")
    return value


def _copy_regular(source: Path, target: Path) -> Dict[str, str]:
    if not _regular(source):
        raise CollectorError("source is missing or symlinked: {}".format(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    shutil.copyfile(str(source), str(temporary))
    os.replace(str(temporary), str(target))
    return {"path": target.as_posix(), "sha256": _sha256(target)}


def _artifact_ref(root: Path, path: Path) -> Dict[str, str]:
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": _sha256(path),
    }


def prepare_evidence(
    *,
    config_path: Path,
    output_dir: Path,
    campaign_id: str,
    candidate_id: str,
    backend: str,
    mode: str,
    repeat_index: int,
    runtime_manifest: Path,
    model: Path,
    service_source: Path,
    engine_source: Path,
    service_launcher: Path,
) -> Dict[str, Any]:
    config = _config(config_path)
    output = _new_directory(output_dir)
    sources = {
        "model": model.resolve(),
        "runtime_manifest": runtime_manifest.resolve(),
        "service_source": service_source.resolve(),
        "engine_source": engine_source.resolve(),
        "service_launcher": service_launcher.resolve(),
    }
    frozen_names = {
        "model": "a09_model" + model.suffix,
        "runtime_manifest": "runtime_manifest.json",
        "service_source": "gpu_service.py",
        "engine_source": "a09_numpy_inference.py",
        "service_launcher": "start_gpu_service.sh",
    }
    artifacts: Dict[str, Dict[str, str]] = {}
    artifact_sha: Dict[str, str] = {}
    for name, source in sources.items():
        target = output / "frozen" / frozen_names[name]
        _copy_regular(source, target)
        artifacts[name] = _artifact_ref(output, target)
        artifact_sha[name] = artifacts[name]["sha256"]
    runtime = _load_json(output / artifacts["runtime_manifest"]["path"])
    if runtime.get("schema_version") != 2:
        raise CollectorError("runtime_manifest.schema")
    bindings = config.get("runtime_artifact_bindings")
    if not isinstance(bindings, Mapping):
        raise CollectorError("collector config runtime bindings missing")
    for artifact, field in bindings.items():
        if artifact not in artifact_sha or runtime.get(field) != artifact_sha[artifact]:
            raise CollectorError("runtime_manifest binding mismatch: {}".format(artifact))
    if (
        runtime.get("candidate_id") != "A09"
        or not isinstance(runtime.get("process_start_ticks"), int)
        or runtime.get("process_start_ticks", 0) <= 0
        or not isinstance(runtime.get("pid"), int)
        or isinstance(runtime.get("pid"), bool)
        or runtime.get("pid", 0) <= 0
        or not isinstance(runtime.get("python_executable"), str)
        or not runtime.get("python_executable")
        or not isinstance(runtime.get("working_directory"), str)
        or not runtime.get("working_directory")
        or not isinstance(runtime.get("command_sha256"), str)
        or not SHA256_RE.fullmatch(runtime.get("command_sha256", ""))
    ):
        raise CollectorError("runtime_manifest process/candidate identity is incomplete")
    config_copy = output / "frozen" / "collector_config.json"
    _copy_regular(config_path.resolve(), config_copy)
    manifest_paths = [output / item["path"] for item in artifacts.values()] + [config_copy]
    manifest = output / "prepare_manifest.sha256"
    _atomic_text(
        manifest,
        "".join(
            "{}  {}\n".format(_sha256(path), path.relative_to(output).as_posix())
            for path in sorted(manifest_paths)
        ),
    )
    receipt: Dict[str, Any] = {
        "schema_version": 1,
        "scope": PREPARE_SCOPE,
        "read_only_source_access": True,
        "service_started_or_stopped": False,
        "traffic_started_or_stopped": False,
        "campaign_id": campaign_id,
        "candidate_id": candidate_id,
        "backend": backend,
        "mode": mode,
        "repeat_index": repeat_index,
        "collector_config_sha256": _sha256(config_path),
        "runtime_manifest_actual_sha256": artifact_sha["runtime_manifest"],
        "runtime_identity": {
            field: runtime.get(field)
            for field in (
                "candidate_id",
                "pid",
                "process_start_ticks",
                "python_executable",
                "working_directory",
                "command_sha256",
                "bind",
                "connect",
                "inference_engine",
            )
        },
        "artifact_sha256": artifact_sha,
        "artifacts": artifacts,
        "prepare_manifest": _artifact_ref(output, manifest),
        "gaps": [],
    }
    _atomic_json(output / "prepare_receipt.json", receipt)
    return receipt


def _parse_proc_stat(line: str) -> Tuple[int, int, int]:
    closing = line.rfind(")")
    if closing < 0:
        raise CollectorError("invalid /proc stat")
    fields = line[closing + 1 :].split()
    if len(fields) < 20:
        raise CollectorError("truncated /proc stat")
    return int(fields[1]), int(fields[11]) + int(fields[12]), int(fields[19])


def _process_record(pid: int) -> Optional[Dict[str, Any]]:
    root = Path("/proc") / str(pid)
    try:
        parent, ticks, start_ticks = _parse_proc_stat((root / "stat").read_text(encoding="utf-8"))
        status = (root / "status").read_text(encoding="utf-8")
        cmdline_raw = (root / "cmdline").read_bytes()
        environ_raw = (root / "environ").read_bytes()
        exe = str((root / "exe").resolve())
        cwd = str((root / "cwd").resolve())
    except (OSError, CollectorError):
        return None
    rss_kib = 0
    for line in status.splitlines():
        if line.startswith("VmRSS:"):
            try:
                rss_kib = int(line.split()[1])
            except (IndexError, ValueError):
                return None
    environment = {}
    for item in environ_raw.split(b"\0"):
        key, separator, value = item.partition(b"=")
        if separator and key == b"PYTHONPATH":
            environment["PYTHONPATH"] = value.decode("utf-8", errors="replace")
    return {
        "pid": pid,
        "parent_pid": parent,
        "cpu_ticks": ticks,
        "start_ticks": start_ticks,
        "rss_bytes": rss_kib * 1024,
        "exe": exe,
        "cwd": cwd,
        "cmdline_sha256": hashlib.sha256(cmdline_raw).hexdigest(),
        "argv": [item.decode("utf-8", errors="replace") for item in cmdline_raw.split(b"\0") if item],
        "python_path": environment.get("PYTHONPATH", ""),
    }


def _process_tree(root_pid: int) -> Tuple[List[Dict[str, Any]], List[str]]:
    records: Dict[int, Dict[str, Any]] = {}
    errors: List[str] = []
    try:
        entries = list(Path("/proc").iterdir())
    except OSError as error:
        return [], ["proc.enumeration:" + str(error)]
    for entry in entries:
        if not entry.name.isdigit():
            continue
        record = _process_record(int(entry.name))
        if record is not None:
            records[record["pid"]] = record
    if root_pid not in records:
        return [], ["process.root_not_alive"]
    included = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, record in records.items():
            if pid not in included and record["parent_pid"] in included:
                included.add(pid)
                changed = True
    return [records[pid] for pid in sorted(included)], errors


def _argv_option(argv: Sequence[Any], option: str) -> Optional[str]:
    for index, value in enumerate(argv[:-1]):
        if value == option and isinstance(argv[index + 1], str) and argv[index + 1]:
            return argv[index + 1]
    return None


def _resolved_live_file(raw_path: str, cwd: Path) -> Optional[Path]:
    requested = Path(raw_path)
    if not requested.is_absolute():
        requested = cwd / requested
    try:
        resolved = requested.resolve(strict=True)
    except OSError:
        return None
    return resolved if resolved.is_file() else None


def _live_service_artifacts(
    process: Mapping[str, Any],
    inference_engine: str,
    health: Mapping[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    """Hash the files addressed by the live process, not manifest claims."""
    gaps: List[str] = []
    argv = process.get("argv")
    cwd_raw = process.get("cwd")
    if not isinstance(argv, list) or not isinstance(cwd_raw, str):
        return {}, ["live_runtime.process_argv_or_cwd"]
    cwd = Path(cwd_raw)
    model_raw = _argv_option(argv, "--model")
    model = _resolved_live_file(model_raw, cwd) if model_raw is not None else None
    if model is None:
        gaps.append("live_runtime.model_path")

    search_roots = [cwd]
    python_path = process.get("python_path")
    if isinstance(python_path, str):
        for item in python_path.split(os.pathsep):
            if item:
                root = Path(item)
                search_roots.append(root if root.is_absolute() else cwd / root)
    module_candidates = [root / "hft_mgbs" / "gpu_service.py" for root in search_roots]
    service_source: Optional[Path] = None
    for candidate in module_candidates:
        resolved = _resolved_live_file(str(candidate), cwd)
        if resolved is not None:
            service_source = resolved
            break
    if service_source is None:
        # Direct ``python /path/gpu_service.py`` remains supported, but only
        # when the argv file exists and is hashed in place.
        direct = next((value for value in argv[1:] if isinstance(value, str) and value.endswith("gpu_service.py")), None)
        service_source = _resolved_live_file(direct, cwd) if direct is not None else None
    if service_source is None:
        gaps.append("live_runtime.service_source_path")

    engine_source: Optional[Path] = None
    if inference_engine == "numpy_exact" and service_source is not None:
        engine_source = _resolved_live_file(str(service_source.with_name("a09_numpy_inference.py")), cwd)
        if engine_source is None:
            gaps.append("live_runtime.engine_source_path")

    executable_raw = process.get("exe")
    executable = (
        _resolved_live_file(executable_raw, cwd) if isinstance(executable_raw, str) else None
    )
    if executable is None:
        gaps.append("live_runtime.python_executable")

    paths = {
        "model": model,
        "service_source": service_source,
        "engine_source": engine_source,
        "python_executable": executable,
    }
    hashes = {name: _sha256(path) for name, path in paths.items() if path is not None}
    resolved_paths = {name: str(path) for name, path in paths.items() if path is not None}
    response = health.get("response") if isinstance(health, Mapping) else None
    health_model = response.get("model_bundle") if isinstance(response, Mapping) else None
    health_model_sha = response.get("model_sha256") if isinstance(response, Mapping) else None
    health_engine = response.get("inference_engine") if isinstance(response, Mapping) else None
    health_path_matches = False
    if isinstance(health_model, str) and model is not None:
        candidate = _resolved_live_file(health_model, cwd)
        health_path_matches = candidate == model
    if (
        not isinstance(response, Mapping)
        or response.get("ok") is not True
        or health_model_sha != hashes.get("model")
        or not health_path_matches
        or health_engine != inference_engine
    ):
        gaps.append("live_runtime.health_model_binding")
    return {
        "resolved_paths": resolved_paths,
        "sha256": hashes,
        "health_model_path_matches": health_path_matches,
        "health_model_sha256": health_model_sha,
        "health_inference_engine": health_engine,
    }, gaps


def _read_host_cpu() -> List[int]:
    first = Path("/proc/stat").read_text(encoding="ascii").splitlines()[0].split()
    if not first or first[0] != "cpu" or len(first) < 9:
        raise CollectorError("/proc/stat aggregate CPU row missing")
    return [int(value) for value in first[1:]]


def _read_memory() -> Tuple[int, int]:
    values: Dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        key, separator, raw = line.partition(":")
        if separator:
            try:
                values[key] = int(raw.split()[0]) * 1024
            except (IndexError, ValueError):
                continue
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", 0)
    if total <= 0 or available < 0 or available > total:
        raise CollectorError("/proc/meminfo total/available missing")
    return total, available


def _duration_ns(raw_value: str, raw_unit: str) -> Optional[int]:
    units = {
        "ns": 1.0,
        "us": 1_000.0,
        "µs": 1_000.0,
        "ms": 1_000_000.0,
        "s": 1_000_000_000.0,
        "seconds": 1_000_000_000.0,
    }
    try:
        value = float(raw_value)
    except ValueError:
        return None
    multiplier = units.get(raw_unit.lower())
    if multiplier is None or not math.isfinite(value):
        return None
    return int(round(value * multiplier))


def _clock_sync_snapshot() -> Dict[str, Any]:
    """Read independent kernel/NTP status; never adjusts either clock."""
    observed_epoch_ns = time.time_ns()
    observed_monotonic_ns = time.monotonic_ns()
    errors: List[str] = []
    try:
        completed = subprocess.run(
            ["chronyc", "-n", "tracking"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        )
        system = re.search(
            r"^System time\s*:\s*([+-]?[0-9.]+)\s+seconds\s+(fast|slow)\s+of\s+NTP\s+time\s*$",
            completed.stdout,
            re.MULTILINE | re.IGNORECASE,
        )
        leap = re.search(r"^Leap status\s*:\s*(.+?)\s*$", completed.stdout, re.MULTILINE)
        reference = re.search(r"^Reference ID\s*:\s*(.+?)\s*$", completed.stdout, re.MULTILINE)
        if system is not None and leap is not None:
            offset = _duration_ns(system.group(1), "seconds")
            if offset is not None:
                if system.group(2).lower() == "slow":
                    offset = -offset
                synchronized = leap.group(1).strip().lower() == "normal"
                return {
                    "query_ok": synchronized,
                    "synchronized": synchronized,
                    "source": "chronyc_tracking",
                    "absolute_clock_offset_ns": abs(offset),
                    "signed_clock_offset_ns": offset,
                    "reference": reference.group(1).strip() if reference is not None else None,
                    "observed_epoch_ns": observed_epoch_ns,
                    "observed_monotonic_ns": observed_monotonic_ns,
                }
        errors.append("chronyc_unparseable")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append("chronyc:" + type(error).__name__)

    # systemd-timesyncd exposes an independently measured offset on newer
    # systemd versions.  NTPSynchronized alone is insufficient and is never
    # converted into a zero offset.
    try:
        synchronized = subprocess.run(
            ["timedatectl", "show", "--property=NTPSynchronized", "--value"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        ).stdout.strip().lower() == "yes"
        status = subprocess.run(
            ["timedatectl", "timesync-status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        ).stdout
        offset_match = re.search(r"^\s*Offset:\s*([+-]?[0-9.]+)\s*(ns|us|µs|ms|s)\s*$", status, re.MULTILINE)
        server = re.search(r"^\s*Server:\s*(.+?)\s*$", status, re.MULTILINE)
        if synchronized and offset_match is not None:
            offset = _duration_ns(offset_match.group(1), offset_match.group(2))
            if offset is not None:
                return {
                    "query_ok": True,
                    "synchronized": True,
                    "source": "systemd_timesync_status",
                    "absolute_clock_offset_ns": abs(offset),
                    "signed_clock_offset_ns": offset,
                    "reference": server.group(1).strip() if server is not None else None,
                    "observed_epoch_ns": observed_epoch_ns,
                    "observed_monotonic_ns": observed_monotonic_ns,
                }
        errors.append("timedatectl_no_measured_offset")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append("timedatectl:" + type(error).__name__)

    try:
        completed = subprocess.run(
            ["ntpq", "-pn"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        )
        selected = next((line for line in completed.stdout.splitlines() if line.startswith("*")), None)
        fields = selected.split() if selected is not None else []
        if len(fields) >= 10:
            offset = _duration_ns(fields[8], "ms")
            if offset is not None:
                return {
                    "query_ok": True,
                    "synchronized": True,
                    "source": "ntpq_selected_peer",
                    "absolute_clock_offset_ns": abs(offset),
                    "signed_clock_offset_ns": offset,
                    "reference": fields[0],
                    "observed_epoch_ns": observed_epoch_ns,
                    "observed_monotonic_ns": observed_monotonic_ns,
                }
        errors.append("ntpq_no_selected_peer")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append("ntpq:" + type(error).__name__)
    return {
        "query_ok": False,
        "synchronized": False,
        "source": None,
        "absolute_clock_offset_ns": None,
        "signed_clock_offset_ns": None,
        "reference": None,
        "observed_epoch_ns": observed_epoch_ns,
        "observed_monotonic_ns": observed_monotonic_ns,
        "errors": errors,
    }


class _ClockProbeServer:
    """Short-lived read-only epoch responder owned by the service collector."""

    def __init__(self, host: str, port: int) -> None:
        self._stop = threading.Event()
        self._errors: List[str] = []
        self._queries = 0
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, port))
        self._socket.listen(8)
        self._socket.settimeout(0.2)
        self.address = self._socket.getsockname()
        self._thread = threading.Thread(target=self._run, name="hft-clock-probe", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                connection, _peer = self._socket.accept()
            except socket.timeout:
                continue
            except OSError as error:
                if not self._stop.is_set():
                    self._errors.append(type(error).__name__ + ":" + str(error))
                break
            try:
                with connection:
                    connection.settimeout(1.0)
                    raw = b""
                    while not raw.endswith(b"\n") and len(raw) <= 4096:
                        block = connection.recv(4096)
                        if not block:
                            break
                        raw += block
                    request = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
                    nonce = request.get("nonce") if isinstance(request, Mapping) else None
                    if not isinstance(nonce, str) or not nonce:
                        raise CollectorError("clock probe nonce missing")
                    response = {
                        "schema_version": 1,
                        "scope": "hft_mgbs_clock_probe_v1",
                        "nonce": nonce,
                        "server_epoch_ns": time.time_ns(),
                        "server_monotonic_ns": time.monotonic_ns(),
                    }
                    connection.sendall(
                        json.dumps(response, sort_keys=True, separators=(",", ":")).encode("utf-8")
                        + b"\n"
                    )
                    self._queries += 1
            except (OSError, UnicodeError, json.JSONDecodeError, CollectorError) as error:
                self._errors.append(type(error).__name__ + ":" + str(error))

    def finish(self) -> Dict[str, Any]:
        self._stop.set()
        self._thread.join(timeout=1.0)
        try:
            self._socket.close()
        except OSError:
            pass
        return {
            "bind_host": str(self.address[0]),
            "bind_port": int(self.address[1]),
            "queries_served": self._queries,
            "errors": sorted(set(self._errors)),
            "stopped": not self._thread.is_alive(),
        }


def _cross_node_clock_probe(host: str, port: int, attempts: int = 5) -> Dict[str, Any]:
    observations: List[Dict[str, Any]] = []
    errors: List[str] = []
    for index in range(attempts):
        nonce = hashlib.sha256(os.urandom(32)).hexdigest()
        start_epoch_ns = time.time_ns()
        start_monotonic_ns = time.monotonic_ns()
        try:
            with socket.create_connection((host, port), timeout=1.0) as connection:
                connection.settimeout(1.0)
                connection.sendall(
                    json.dumps({"nonce": nonce}, sort_keys=True).encode("utf-8") + b"\n"
                )
                raw = b""
                while not raw.endswith(b"\n") and len(raw) <= 4096:
                    block = connection.recv(4096)
                    if not block:
                        break
                    raw += block
            end_monotonic_ns = time.monotonic_ns()
            end_epoch_ns = time.time_ns()
            response = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
            server_epoch_ns = response.get("server_epoch_ns") if isinstance(response, Mapping) else None
            if (
                not isinstance(response, Mapping)
                or response.get("schema_version") != 1
                or response.get("scope") != "hft_mgbs_clock_probe_v1"
                or response.get("nonce") != nonce
                or isinstance(server_epoch_ns, bool)
                or not isinstance(server_epoch_ns, int)
            ):
                raise CollectorError("clock probe response identity")
            rtt_ns = end_monotonic_ns - start_monotonic_ns
            offset_low_ns = server_epoch_ns - end_epoch_ns
            offset_high_ns = server_epoch_ns - start_epoch_ns
            observations.append(
                {
                    "attempt": index,
                    "nonce": nonce,
                    "client_send_epoch_ns": start_epoch_ns,
                    "client_receive_epoch_ns": end_epoch_ns,
                    "client_send_monotonic_ns": start_monotonic_ns,
                    "client_receive_monotonic_ns": end_monotonic_ns,
                    "server_epoch_ns": server_epoch_ns,
                    "server_monotonic_ns": response.get("server_monotonic_ns"),
                    "rtt_ns": rtt_ns,
                    "offset_interval_low_ns": offset_low_ns,
                    "offset_interval_high_ns": offset_high_ns,
                    "maximum_absolute_offset_bound_ns": max(
                        abs(offset_low_ns), abs(offset_high_ns)
                    ),
                }
            )
        except (OSError, UnicodeError, json.JSONDecodeError, CollectorError) as error:
            errors.append("attempt.{}:{}:{}".format(index, type(error).__name__, error))
    best = min(observations, key=lambda row: int(row["rtt_ns"])) if observations else None
    return {
        "query_ok": best is not None,
        "host": host,
        "port": port,
        "observations": observations,
        "best_observation": best,
        "errors": errors,
    }


def _parse_counter(text: str, name: str) -> Optional[int]:
    matches = re.findall(r"^\s*{}:\s*(\d+)\s*$".format(re.escape(name)), text, re.MULTILINE)
    return int(matches[-1]) if matches else None


def _nic_snapshot(interface: str) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            ["ethtool", "-S", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2.0,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"query_ok": False, "error": type(error).__name__ + ":" + str(error)}
    ucast = _parse_counter(completed.stdout, "rx_ucast_packets")
    discards = _parse_counter(completed.stdout, "rx_discards")
    if ucast is None or discards is None:
        return {"query_ok": False, "error": "required_ethtool_counters_missing"}
    return {"query_ok": True, "rx_ucast": ucast, "rx_discards": discards}


def _pktgen_snapshot(devices: Sequence[Path]) -> Dict[str, Any]:
    packets = 0
    rows: List[Dict[str, Any]] = []
    for device in devices:
        try:
            text = device.read_text(encoding="ascii")
        except OSError as error:
            return {"query_ok": False, "error": "{}:{}".format(device, error)}
        match = re.search(r"^\s*pkts-sofar:\s*(\d+)\b", text, re.MULTILINE)
        if match is None:
            return {"query_ok": False, "error": "pkts-sofar_missing:" + str(device)}
        value = int(match.group(1))
        packets += value
        rows.append({"path": str(device), "pkts_sofar": value})
    if not devices:
        return {"query_ok": False, "error": "pktgen_devices_missing"}
    return {"query_ok": True, "packets": packets, "devices": rows}


def _nvidia_snapshot(service_pids: Sequence[int]) -> Dict[str, Any]:
    try:
        gpu = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        )
        first = gpu.stdout.splitlines()[0]
        parts = [part.strip() for part in first.split(",")]
        utilization = float(parts[0]) / 100.0
        memory_used = float(parts[1]) * 1024 * 1024
        memory_total = float(parts[2]) * 1024 * 1024
        apps = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,used_memory",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        )
    except (OSError, subprocess.SubprocessError, IndexError, ValueError) as error:
        return {"query_ok": False, "error": type(error).__name__ + ":" + str(error)}
    app_rows: List[Dict[str, Any]] = []
    service_set = set(service_pids)
    for line in apps.stdout.splitlines():
        fields = [part.strip() for part in line.split(",")]
        if len(fields) != 2:
            continue
        try:
            pid = int(fields[0])
            used = float(fields[1]) * 1024 * 1024
        except ValueError:
            continue
        app_rows.append({"pid": pid, "memory_bytes": used, "belongs_to_service": pid in service_set})
    # pmon supplies process-attributed SM utilization on drivers that support
    # it.  Absence is retained as null, never replaced by system utilization.
    pmon_error: Optional[str] = None
    try:
        pmon = subprocess.run(
            ["nvidia-smi", "pmon", "-c", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        )
        for line in pmon.stdout.splitlines():
            fields = line.split()
            if not fields or fields[0].startswith("#") or len(fields) < 4:
                continue
            try:
                pid = int(fields[1])
                sm = None if fields[3] == "-" else float(fields[3]) / 100.0
            except ValueError:
                continue
            for row in app_rows:
                if row["pid"] == pid:
                    row["sm_fraction"] = sm
    except (OSError, subprocess.SubprocessError) as error:
        pmon_error = type(error).__name__ + ":" + str(error)
    return {
        "query_ok": True,
        "gpu_fraction": utilization,
        "gpu_memory_used_bytes": memory_used,
        "gpu_memory_total_bytes": memory_total,
        "compute_apps": app_rows,
        "pmon_error": pmon_error,
    }


def _health(host: str, port: int) -> Dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=2.0) as connection:
            connection.settimeout(2.0)
            connection.sendall(b'{"op":"health"}\n')
            raw = b""
            while not raw.endswith(b"\n") and len(raw) <= 1024 * 1024:
                block = connection.recv(65536)
                if not block:
                    break
                raw += block
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
        if not isinstance(value, Mapping):
            raise CollectorError("health response is not an object")
        return {"query_ok": True, "response": value}
    except (OSError, UnicodeError, json.JSONDecodeError, CollectorError) as error:
        return {"query_ok": False, "error": type(error).__name__ + ":" + str(error)}


def _listener_owner(port: int) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            ["ss", "-H", "-ltnp", "sport", "=", ":{}".format(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2.0,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"query_ok": False, "error": type(error).__name__ + ":" + str(error)}
    pids = sorted(set(int(value) for value in re.findall(r"pid=(\d+)", completed.stdout)))
    return {"query_ok": True, "owner_pids": pids, "raw_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest()}


def _reverse_socket_snapshot(port: int) -> Dict[str, Any]:
    listener = _listener_owner(port)
    try:
        completed = subprocess.run(
            ["ss", "-H", "-tnp"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3.0,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {
            "query_ok": False,
            "listener": listener,
            "error": type(error).__name__ + ":" + str(error),
        }
    needle = ":{}".format(port)
    established_rows = [
        line
        for line in completed.stdout.splitlines()
        if line.startswith("ESTAB") and needle in line
    ]
    return {
        "query_ok": listener.get("query_ok") is True,
        "listener": listener,
        "established": bool(established_rows),
        "established_owner_pids": sorted(
            set(
                int(value)
                for line in established_rows
                for value in re.findall(r"pid=(\d+)", line)
            )
        ),
        "established_rows_sha256": hashlib.sha256(
            ("\n".join(established_rows) + ("\n" if established_rows else "")).encode()
        ).hexdigest(),
    }


def _hardware_material(interface: Optional[str]) -> Dict[str, Any]:
    material: Dict[str, Any] = {}
    for name, path in (
        ("machine_id", Path("/etc/machine-id")),
        ("boot_id", Path("/proc/sys/kernel/random/boot_id")),
        ("product_uuid", Path("/sys/class/dmi/id/product_uuid")),
    ):
        try:
            material[name] = path.read_text(encoding="ascii").strip()
        except OSError:
            material[name] = None
    material["host_cpu_count"] = os.cpu_count()
    try:
        material["cpuinfo_sha256"] = _sha256(Path("/proc/cpuinfo"))
    except OSError:
        material["cpuinfo_sha256"] = None
    if interface:
        net = Path("/sys/class/net") / interface
        try:
            material["interface"] = interface
            material["ifindex"] = int((net / "ifindex").read_text(encoding="ascii"))
            material["device"] = str((net / "device").resolve())
            material["driver"] = str((net / "device/driver").resolve())
        except (OSError, ValueError):
            material["interface_error"] = "identity_unavailable"
    return material


def _generator_process_records() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for comm in Path("/proc").glob("[0-9]*/comm"):
        try:
            name = comm.read_text(encoding="ascii").strip()
        except OSError:
            continue
        if not name.startswith("kpktgend_"):
            continue
        try:
            parent, ticks, start_ticks = _parse_proc_stat(
                (comm.parent / "stat").read_text(encoding="utf-8")
            )
        except (OSError, CollectorError):
            continue
        rows.append(
            {
                "pid": int(comm.parent.name),
                "parent_pid": parent,
                "cpu_ticks": ticks,
                "start_ticks": start_ticks,
                "comm": name,
            }
        )
    return sorted(rows, key=lambda row: (row["start_ticks"], row["pid"]))


def _parse_env_pid(path: Optional[Path]) -> Optional[int]:
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^pid=(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def collect_node_evidence(
    *,
    config_path: Path,
    role: str,
    output_path: Path,
    duration_seconds: int,
    interface: Optional[str] = None,
    pktgen_devices: Sequence[Path] = (),
    pipeline_identity_file: Optional[Path] = None,
    runtime_manifest: Optional[Path] = None,
    gpu_health_host: Optional[str] = None,
    gpu_health_port: int = 50051,
    reverse_port: int = 50052,
    clock_probe_host: Optional[str] = None,
    clock_probe_listen_host: Optional[str] = None,
    clock_probe_port: int = 50053,
) -> Dict[str, Any]:
    config = _config(config_path)
    if role not in ("physical", "service"):
        raise CollectorError("role must be physical or service")
    if duration_seconds < 1 or duration_seconds > int(config["maximum_collection_seconds"]):
        raise CollectorError("invalid collection duration")
    if output_path.exists():
        raise CollectorError("collection output already exists")
    runtime: Optional[Mapping[str, Any]] = None
    runtime_sha: Optional[str] = None
    service_pid: Optional[int] = None
    service_start_ticks: Optional[int] = None
    runtime_engine: Optional[str] = None
    if role == "service":
        if runtime_manifest is None or not _regular(runtime_manifest):
            raise CollectorError("service collection requires a regular runtime manifest")
        runtime = _load_json(runtime_manifest)
        runtime_sha = _sha256(runtime_manifest)
        raw_pid = runtime.get("pid")
        raw_ticks = runtime.get("process_start_ticks")
        if (
            isinstance(raw_pid, bool)
            or not isinstance(raw_pid, int)
            or raw_pid <= 0
            or isinstance(raw_ticks, bool)
            or not isinstance(raw_ticks, int)
            or raw_ticks <= 0
        ):
            raise CollectorError("runtime manifest process identity is invalid")
        service_pid = raw_pid
        service_start_ticks = raw_ticks
        runtime_engine = str(runtime.get("inference_engine") or "")
    pipeline_pid = _parse_env_pid(pipeline_identity_file)
    if role == "physical" and (
        not isinstance(gpu_health_host, str)
        or not gpu_health_host
        or gpu_health_host in ("127.0.0.1", "localhost", "::1")
    ):
        raise CollectorError("physical collection requires the explicit non-loopback GPU host")
    if role == "service" and not gpu_health_host:
        gpu_health_host = "127.0.0.1"
    errors: List[str] = []
    if bool(clock_probe_host) == bool(clock_probe_listen_host):
        errors.append("clock_probe_direction_requires_exactly_one_client_or_server")
    samples: List[Dict[str, Any]] = []
    service_identity: Optional[Dict[str, Any]] = None
    pipeline_identity: Optional[Dict[str, Any]] = None
    generator_identity: Optional[List[Dict[str, Any]]] = None
    physical_network_identity: Optional[Dict[str, Any]] = None
    clock_probe_server: Optional[_ClockProbeServer] = None
    clock_probe_observations: List[Dict[str, Any]] = []
    if clock_probe_listen_host:
        try:
            clock_probe_server = _ClockProbeServer(clock_probe_listen_host, clock_probe_port)
        except OSError as error:
            errors.append("clock_probe_server:" + type(error).__name__ + ":" + str(error))
    if clock_probe_host:
        clock_probe_observations.append(
            _cross_node_clock_probe(clock_probe_host, clock_probe_port)
        )
    clock_sync_observations = (
        [_clock_sync_snapshot()]
        if role == "physical"
        else [
            {
                "query_ok": False,
                "synchronized": None,
                "source": "container_ntp_not_required_cross_node_bound_used",
                "absolute_clock_offset_ns": None,
                "observed_epoch_ns": time.time_ns(),
                "observed_monotonic_ns": time.monotonic_ns(),
            }
        ]
    )
    # duration N needs N+1 boundary snapshots to derive N one-second deltas.
    first_boundary = int(math.floor(time.time())) + 1
    for offset in range(duration_seconds + 1):
        boundary = first_boundary + offset
        remaining = boundary - time.time()
        if remaining > 0:
            time.sleep(remaining)
        observed_ns = time.time_ns()
        try:
            host_cpu = _read_host_cpu()
            memory_total, memory_available = _read_memory()
        except (OSError, ValueError, CollectorError) as error:
            errors.append("host_sample.{}:{}".format(boundary, error))
            continue
        sample: Dict[str, Any] = {
            "boundary_epoch_second": boundary,
            "observed_epoch_ns": observed_ns,
            "host_cpu": host_cpu,
            "memory_total_bytes": memory_total,
            "memory_available_bytes": memory_available,
        }
        if role == "physical":
            nic = _nic_snapshot(interface) if interface else {"query_ok": False, "error": "interface_missing"}
            pktgen = _pktgen_snapshot(pktgen_devices)
            sample["nic"] = nic
            sample["pktgen"] = pktgen
            if nic.get("query_ok") is True and pktgen.get("query_ok") is True:
                sample["external_counters"] = {
                    "pktgen_offered": int(pktgen["packets"]),
                    "nic_rx_ucast": int(nic["rx_ucast"]),
                    "nic_rx_discards": int(nic["rx_discards"]),
                }
            if pipeline_identity is None and pipeline_pid is not None:
                pipeline_identity = _process_record(pipeline_pid)
            if pipeline_identity is None and pipeline_identity_file is not None:
                pipeline_pid = _parse_env_pid(pipeline_identity_file)
                if pipeline_pid is not None:
                    pipeline_identity = _process_record(pipeline_pid)
            if physical_network_identity is None and pipeline_identity is not None:
                assert gpu_health_host is not None
                gpu_health = _health(gpu_health_host, gpu_health_port)
                reverse_socket = _reverse_socket_snapshot(reverse_port)
                health_response = gpu_health.get("response") if isinstance(gpu_health, Mapping) else None
                if (
                    isinstance(health_response, Mapping)
                    and health_response.get("ok") is True
                    and health_response.get("candidate_id") == "A09"
                    and reverse_socket.get("query_ok") is True
                    and reverse_socket.get("established") is True
                    and pipeline_identity.get("pid")
                    in reverse_socket.get("established_owner_pids", [])
                ):
                    physical_network_identity = {
                        "observed_boundary_epoch_second": boundary,
                        "gpu_host": gpu_health_host,
                        "gpu_port": gpu_health_port,
                        "gpu_health": gpu_health,
                        "reverse_port": reverse_port,
                        "reverse_socket": reverse_socket,
                    }
            if generator_identity is None:
                rows = _generator_process_records()
                if rows:
                    generator_identity = rows
        else:
            assert service_pid is not None
            tree, tree_errors = _process_tree(service_pid)
            errors.extend("service.{}".format(item) for item in tree_errors)
            if tree:
                root = next((row for row in tree if row["pid"] == service_pid), None)
                if root is not None and root["start_ticks"] != service_start_ticks:
                    errors.append("service.process_reused:{}".format(boundary))
                    tree = []
            if tree:
                sample["service"] = {
                    "pid": service_pid,
                    "start_ticks": service_start_ticks,
                    "pids": [row["pid"] for row in tree],
                    "cpu_ticks": sum(int(row["cpu_ticks"]) for row in tree),
                    "rss_bytes": sum(int(row["rss_bytes"]) for row in tree),
                }
                sample["nvidia"] = _nvidia_snapshot(sample["service"]["pids"])
                if service_identity is None:
                    process = next(row for row in tree if row["pid"] == service_pid)
                    localhost_health = _health(gpu_health_host, gpu_health_port)
                    live_artifacts, live_gaps = _live_service_artifacts(
                        process, runtime_engine or "", localhost_health
                    )
                    errors.extend(live_gaps)
                    service_identity = {
                        "manifest_actual_sha256": runtime_sha,
                        "manifest_declared_pid": service_pid,
                        "manifest_process_start_ticks": service_start_ticks,
                        "process": process,
                        "live_artifacts": live_artifacts,
                        "listener_50051": _listener_owner(gpu_health_port),
                        "localhost_health": localhost_health,
                    }
        sample["sample_finished_epoch_ns"] = time.time_ns()
        samples.append(sample)
    if role == "physical":
        clock_sync_observations.append(_clock_sync_snapshot())
    else:
        clock_sync_observations.append(
            {
                "query_ok": False,
                "synchronized": None,
                "source": "container_ntp_not_required_cross_node_bound_used",
                "absolute_clock_offset_ns": None,
                "observed_epoch_ns": time.time_ns(),
                "observed_monotonic_ns": time.monotonic_ns(),
            }
        )
    if clock_probe_host:
        clock_probe_observations.append(
            _cross_node_clock_probe(clock_probe_host, clock_probe_port)
        )
    clock_probe_server_receipt = clock_probe_server.finish() if clock_probe_server is not None else None
    if role == "service" and service_identity is not None:
        assert service_pid is not None
        end_tree, end_tree_errors = _process_tree(service_pid)
        errors.extend("service.final.{}".format(item) for item in end_tree_errors)
        end_process = next((row for row in end_tree if row["pid"] == service_pid), None)
        if (
            end_process is None
            or end_process.get("start_ticks") != service_start_ticks
            or runtime_manifest is None
            or not _regular(runtime_manifest)
            or _sha256(runtime_manifest) != runtime_sha
        ):
            errors.append("service.final.runtime_identity_drift")
        else:
            final_health = _health(gpu_health_host, gpu_health_port)
            final_artifacts, final_gaps = _live_service_artifacts(
                end_process, runtime_engine or "", final_health
            )
            errors.extend("service.final.{}".format(item) for item in final_gaps)
            service_identity["final_observation"] = {
                "process": end_process,
                "live_artifacts": final_artifacts,
                "listener_50051": _listener_owner(gpu_health_port),
                "localhost_health": final_health,
            }
    hardware = _hardware_material(interface)
    if role == "physical" and physical_network_identity is None:
        assert gpu_health_host is not None
        physical_network_identity = {
            "observed_boundary_epoch_second": None,
            "gpu_host": gpu_health_host,
            "gpu_port": gpu_health_port,
            "gpu_health": _health(gpu_health_host, gpu_health_port),
            "reverse_port": reverse_port,
            "reverse_socket": _reverse_socket_snapshot(reverse_port),
        }
    payload: Dict[str, Any] = {
        "schema_version": 1,
        "scope": RAW_SCOPE,
        "read_only": True,
        "service_started_or_stopped": False,
        "traffic_started_or_stopped": False,
        "node_role": role,
        "collector_config_sha256": _sha256(config_path),
        "clock_ticks_per_second": int(os.sysconf("SC_CLK_TCK")),
        "host_cpu_count": os.cpu_count() or 0,
        "hardware_identity_material": hardware,
        "hardware_identity_sha256": _canonical_sha(hardware),
        "runtime_manifest_actual_sha256": runtime_sha,
        "runtime_inference_engine": runtime_engine,
        "clock_sync_observations": clock_sync_observations,
        "cross_node_clock_probe_observations": clock_probe_observations,
        "clock_probe_server": clock_probe_server_receipt,
        "pipeline_process_identity": pipeline_identity,
        "generator_process_identities": generator_identity,
        "service_runtime_identity": service_identity,
        "physical_network_identity": physical_network_identity,
        "samples": samples,
        "errors": sorted(set(errors)),
    }
    _atomic_json(output_path, payload)
    return payload


def _finite(value: Any, minimum: float = 0.0) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number >= minimum else None


def validate_collection_receipt(
    raw: Mapping[str, Any],
    role: str,
    config_sha256: str,
    max_clock_offset_ns: int,
) -> List[str]:
    """Fail closed on partial, drifted, or unsynchronised collection output."""
    prefix = "collection.{}".format(role)
    gaps: List[str] = []
    if (
        raw.get("schema_version") != 1
        or raw.get("scope") != RAW_SCOPE
        or raw.get("node_role") != role
        or raw.get("read_only") is not True
        or raw.get("service_started_or_stopped") is not False
        or raw.get("traffic_started_or_stopped") is not False
    ):
        gaps.append(prefix + ".schema_or_read_only_contract")
    if raw.get("collector_config_sha256") != config_sha256:
        gaps.append(prefix + ".collector_config_hash")
    errors = raw.get("errors")
    if errors != []:
        gaps.append(prefix + ".errors_present")
    samples = raw.get("samples")
    if not isinstance(samples, list) or len(samples) < 2:
        gaps.append(prefix + ".boundary_samples")
    observations = raw.get("clock_sync_observations")
    # The physical node must independently prove UTC discipline.  A GPU
    # Kubernetes container commonly has no chronyd/systemd of its own; its
    # kernel realtime is instead bounded by the cross-node midpoint probe.
    if role == "physical":
        if not isinstance(observations, list) or len(observations) < 2:
            gaps.append(prefix + ".clock_sync_missing")
        else:
            for index, observation in enumerate(observations):
                offset = observation.get("absolute_clock_offset_ns") if isinstance(observation, Mapping) else None
                if (
                    not isinstance(observation, Mapping)
                    or observation.get("query_ok") is not True
                    or observation.get("synchronized") is not True
                    or isinstance(offset, bool)
                    or not isinstance(offset, int)
                    or offset < 0
                    or offset > max_clock_offset_ns
                    or not isinstance(observation.get("source"), str)
                    or not observation.get("source")
                ):
                    gaps.append(prefix + ".clock_sync.{}".format(index))
    return sorted(set(gaps))


def cross_node_clock_probe_gaps(
    physical: Mapping[str, Any], service: Mapping[str, Any], max_bound_ns: int
) -> List[str]:
    gaps: List[str] = []
    physical_probes = physical.get("cross_node_clock_probe_observations")
    service_probes = service.get("cross_node_clock_probe_observations")
    physical_server = physical.get("clock_probe_server")
    service_server = service.get("clock_probe_server")
    physical_is_client = isinstance(physical_probes, list) and len(physical_probes) >= 2
    service_is_client = isinstance(service_probes, list) and len(service_probes) >= 2
    if physical_is_client == service_is_client:
        return ["clock_alignment.cross_node_probe_direction"]
    probes = physical_probes if physical_is_client else service_probes
    server = service_server if physical_is_client else physical_server
    if not isinstance(probes, list) or len(probes) < 2:
        gaps.append("clock_alignment.cross_node_probe_missing")
    else:
        for index, probe in enumerate(probes):
            best = probe.get("best_observation") if isinstance(probe, Mapping) else None
            low = best.get("offset_interval_low_ns") if isinstance(best, Mapping) else None
            high = best.get("offset_interval_high_ns") if isinstance(best, Mapping) else None
            bound = best.get("maximum_absolute_offset_bound_ns") if isinstance(best, Mapping) else None
            if (
                not isinstance(probe, Mapping)
                or probe.get("query_ok") is not True
                or not isinstance(best, Mapping)
                or isinstance(low, bool)
                or not isinstance(low, int)
                or isinstance(high, bool)
                or not isinstance(high, int)
                or low > high
                or isinstance(bound, bool)
                or not isinstance(bound, int)
                or bound > max_bound_ns
                or low > 0
                or high < 0
            ):
                gaps.append("clock_alignment.cross_node_probe.{}".format(index))
    if (
        not isinstance(server, Mapping)
        or server.get("stopped") is not True
        or server.get("errors") != []
        or not isinstance(server.get("queries_served"), int)
        or server.get("queries_served", 0) < 2
    ):
        gaps.append("clock_alignment.peer_probe_server")
    return sorted(set(gaps))


def cross_node_boundary_gaps(
    physical: Mapping[str, Any],
    service: Mapping[str, Any],
    epochs: Sequence[int],
    max_skew_ns: int,
) -> List[str]:
    def observations(raw: Mapping[str, Any]) -> Dict[int, int]:
        result: Dict[int, int] = {}
        for row in raw.get("samples", []):
            if not isinstance(row, Mapping):
                continue
            epoch = row.get("boundary_epoch_second")
            observed = row.get("observed_epoch_ns")
            if (
                isinstance(epoch, int)
                and not isinstance(epoch, bool)
                and isinstance(observed, int)
                and not isinstance(observed, bool)
                and epoch not in result
            ):
                result[epoch] = observed
        return result

    left = observations(physical)
    right = observations(service)
    gaps: List[str] = []
    boundaries = sorted(set(epochs) | {epoch + 1 for epoch in epochs})
    for epoch in boundaries:
        if epoch not in left or epoch not in right:
            gaps.append("clock_alignment.epoch.{}.missing_boundary".format(epoch))
        elif abs(left[epoch] - right[epoch]) > max_skew_ns:
            gaps.append("clock_alignment.epoch.{}.cross_node_skew".format(epoch))
    return gaps


def _cpu_fraction(before: Sequence[int], after: Sequence[int]) -> Optional[float]:
    if len(before) < 8 or len(after) != len(before):
        return None
    # guest/guest_nice are already included in user/nice by Linux and must not
    # be counted twice.  The first eight fields are the capacity denominator.
    deltas = [right - left for left, right in zip(before[:8], after[:8])]
    if any(value < 0 for value in deltas):
        return None
    total = sum(deltas)
    idle = deltas[3] + deltas[4]
    return (total - idle) / total if total > 0 else None


def normalize_resource_samples(
    raw: Mapping[str, Any],
    epochs: Sequence[int],
    max_skew_ns: int,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    role = raw.get("node_role")
    if role not in ("physical", "service") or not isinstance(raw.get("samples"), list):
        return [], ["resources.schema"]
    samples: Dict[int, Mapping[str, Any]] = {}
    gaps: List[str] = []
    for sample in raw["samples"]:
        if not isinstance(sample, Mapping):
            continue
        epoch = sample.get("boundary_epoch_second")
        observed = sample.get("observed_epoch_ns")
        finished = sample.get("sample_finished_epoch_ns")
        if (
            isinstance(epoch, bool)
            or not isinstance(epoch, int)
            or isinstance(observed, bool)
            or not isinstance(observed, int)
            or isinstance(finished, bool)
            or not isinstance(finished, int)
            or finished < observed
            or finished - observed > max_skew_ns
            or abs(observed - epoch * 1_000_000_000) > max_skew_ns
            or epoch in samples
        ):
            continue
        samples[epoch] = sample
    clock_ticks = raw.get("clock_ticks_per_second")
    cpu_count = raw.get("host_cpu_count")
    if (
        isinstance(clock_ticks, bool)
        or not isinstance(clock_ticks, int)
        or clock_ticks <= 0
        or isinstance(cpu_count, bool)
        or not isinstance(cpu_count, int)
        or cpu_count <= 0
    ):
        return [], ["resources.{}.host_capacity".format(role)]
    rows: List[Dict[str, Any]] = []
    for epoch in epochs:
        before = samples.get(epoch)
        after = samples.get(epoch + 1)
        prefix = "resources.{}.epoch.{}".format(role, epoch)
        if before is None or after is None:
            gaps.append(prefix + ".boundary_pair")
            continue
        host_fraction = _cpu_fraction(before.get("host_cpu", []), after.get("host_cpu", []))
        total = after.get("memory_total_bytes")
        available = after.get("memory_available_bytes")
        if (
            host_fraction is None
            or isinstance(total, bool)
            or not isinstance(total, int)
            or total <= 0
            or isinstance(available, bool)
            or not isinstance(available, int)
            or not 0 <= available <= total
        ):
            gaps.append(prefix + ".host_sample")
            continue
        row: Dict[str, Any] = {
            "epoch_second": epoch,
            "host_cpu_fraction": host_fraction,
            "host_memory_fraction": (total - available) / total,
            "source_boundary_start_epoch_ns": int(before["observed_epoch_ns"]),
            "source_boundary_end_epoch_ns": int(after["observed_epoch_ns"]),
        }
        if role == "physical":
            row["cpu_fraction"] = host_fraction
            row["memory_fraction"] = row["host_memory_fraction"]
        else:
            first = before.get("service")
            second = after.get("service")
            if not isinstance(first, Mapping) or not isinstance(second, Mapping):
                gaps.append(prefix + ".service_process")
                continue
            if first.get("pid") != second.get("pid") or first.get("start_ticks") != second.get("start_ticks"):
                gaps.append(prefix + ".service_process_identity")
                continue
            elapsed_ns = int(after["observed_epoch_ns"]) - int(before["observed_epoch_ns"])
            delta_ticks = second.get("cpu_ticks", -1) - first.get("cpu_ticks", 0)
            rss = second.get("rss_bytes")
            if elapsed_ns <= 0 or delta_ticks < 0 or not isinstance(rss, int) or rss < 0:
                gaps.append(prefix + ".service_process_counter")
                continue
            row["cpu_fraction"] = delta_ticks / clock_ticks / (elapsed_ns / 1e9) / cpu_count
            row["memory_fraction"] = rss / total
            row["service_pid"] = second.get("pid")
            row["service_process_start_ticks"] = second.get("start_ticks")
            nvidia = after.get("nvidia")
            if not isinstance(nvidia, Mapping) or nvidia.get("query_ok") is not True:
                gaps.append(prefix + ".gpu_attribution")
                continue
            applications = nvidia.get("compute_apps")
            if not isinstance(applications, list):
                gaps.append(prefix + ".gpu_attribution")
                continue
            pids = set(second.get("pids", []))
            attributed = [item for item in applications if isinstance(item, Mapping) and item.get("pid") in pids]
            engine = raw.get("runtime_inference_engine")
            if not attributed and engine in ("numpy_exact", "sklearn"):
                row["gpu_fraction"] = 0.0
                row["gpu_memory_fraction"] = 0.0
                row["service_gpu_process_present"] = False
                row["system_gpu_fraction"] = _finite(nvidia.get("gpu_fraction"))
            elif attributed:
                sm = [_finite(item.get("sm_fraction")) for item in attributed]
                if any(value is None for value in sm):
                    gaps.append(prefix + ".gpu_process_utilization")
                    continue
                memory_total = _finite(nvidia.get("gpu_memory_total_bytes"), 1)
                if memory_total is None:
                    gaps.append(prefix + ".gpu_memory_capacity")
                    continue
                row["gpu_fraction"] = min(1.0, sum(float(value) for value in sm if value is not None))
                row["gpu_memory_fraction"] = sum(float(item.get("memory_bytes", 0)) for item in attributed) / memory_total
                row["service_gpu_process_present"] = True
                row["system_gpu_fraction"] = _finite(nvidia.get("gpu_fraction"))
            else:
                gaps.append(prefix + ".gpu_attribution")
                continue
        rows.append(row)
    return rows, sorted(set(gaps))


def validate_quality_evidence(
    labels_path: Path,
    predictions_path: Path,
    prepare_receipt_path: Path,
) -> List[str]:
    gaps: List[str] = []
    if not _regular(labels_path):
        gaps.append("quality.labels.missing_or_symlinked")
        return gaps
    if not _regular(predictions_path):
        gaps.append("quality.predictions.missing_or_symlinked")
        return gaps
    labels = _load_json(labels_path)
    predictions = _load_json(predictions_path)
    prepared = _load_json(prepare_receipt_path)
    schema = labels.get("schema_version")
    expected_label_scope = LABEL_SCOPE_V2 if schema == 2 else LABEL_SCOPE
    expected_prediction_scope = PREDICTION_SCOPE_V2 if schema == 2 else PREDICTION_SCOPE
    if (
        schema not in (1, 2)
        or labels.get("scope") != expected_label_scope
        or labels.get("source_kind") not in ("official_labels", "independent_manual_labels")
        or labels.get("synthetic") is not False
        or labels.get("independent_holdout") is not True
        or not isinstance(labels.get("source_artifact_path"), str)
        or not labels.get("source_artifact_path")
        or not isinstance(labels.get("source_artifact_sha256"), str)
        or not SHA256_RE.fullmatch(str(labels.get("source_artifact_sha256")))
        or not isinstance(labels.get("source_record_locator"), str)
        or not labels.get("source_record_locator")
        or not isinstance(labels.get("records"), list)
    ):
        gaps.append("quality.labels.not_independent_nonsynthetic")
    source_path: Optional[Path] = None
    raw_source_path = labels.get("source_artifact_path")
    if isinstance(raw_source_path, str) and raw_source_path:
        source_path = Path(raw_source_path)
        if not source_path.is_absolute():
            source_path = labels_path.parent / source_path
    if (
        source_path is None
        or not _regular(source_path)
        or _sha256(source_path) != labels.get("source_artifact_sha256")
    ):
        gaps.append("quality.labels.source_artifact_binding")
    elif schema == 2:
        if Path(str(raw_source_path)).is_absolute() or PurePosixPath(str(raw_source_path)).name != raw_source_path:
            gaps.append("quality.labels.portable_source_path")
        source = _load_json(source_path)
        if (
            source.get("schema_version") != 1
            or source.get("scope") != QUALITY_SOURCE_SCOPE
            or source.get("source_kind") != "official_unsw_ground_truth_and_frozen_pcap_inputs"
            or source.get("synthetic") is not False
            or source.get("portable") is not True
            or source.get("eligible_events") != labels.get("eligible_events")
            or source.get("sample_event_relations") != labels.get("sample_event_relations")
            or not isinstance(source.get("embedded_input_hash_manifest"), Mapping)
        ):
            gaps.append("quality.labels.portable_source_schema")
    if (
        predictions.get("schema_version") != schema
        or predictions.get("scope") != expected_prediction_scope
        or predictions.get("synthetic") is not False
        or predictions.get("generation_kind") != "frozen_model_inference_on_independent_holdout"
        or predictions.get("source_artifact_sha256") != labels.get("source_artifact_sha256")
        or not isinstance(predictions.get("records"), list)
    ):
        gaps.append("quality.predictions.schema")
    artifact_sha = prepared.get("artifact_sha256")
    if not isinstance(artifact_sha, Mapping):
        gaps.append("quality.prepare_binding")
        artifact_sha = {}
    if (
        predictions.get("labels_sha256") != _sha256(labels_path)
        or predictions.get("model_sha256") != artifact_sha.get("model")
        or predictions.get("runtime_manifest_sha256") != artifact_sha.get("runtime_manifest")
    ):
        gaps.append("quality.predictions.hash_binding")
    if schema == 2 and (
        labels.get("prepare_receipt_sha256") != _sha256(prepare_receipt_path)
        or predictions.get("prepare_receipt_sha256") != _sha256(prepare_receipt_path)
    ):
        gaps.append("quality.prepare_receipt_hash_binding")
    if schema == 2:
        raw_prepare = labels.get("prepare_receipt_path")
        portable_prepare = labels_path.parent / str(raw_prepare)
        if (
            not isinstance(raw_prepare, str)
            or PurePosixPath(raw_prepare).name != raw_prepare
            or not _regular(portable_prepare)
            or _sha256(portable_prepare) != labels.get("prepare_receipt_sha256")
        ):
            gaps.append("quality.portable_prepare_receipt")
    label_ids: List[str] = []
    label_groups: Dict[str, str] = {}
    positive_ids = set()
    for row in labels.get("records", []):
        if (
            not isinstance(row, Mapping)
            or not isinstance(row.get("sample_id"), str)
            or isinstance(row.get("label"), bool)
            or row.get("label") not in (0, 1)
            or not isinstance(row.get("group"), str)
            or not row.get("group")
            or (
                schema == 1
                and (not isinstance(row.get("event_id"), str) or not row.get("event_id"))
            )
            or (schema == 2 and row.get("event_id") is not None)
        ):
            gaps.append("quality.labels.records")
            break
        label_ids.append(row["sample_id"])
        label_groups[row["sample_id"]] = row["group"]
        if row.get("label") == 1:
            positive_ids.add(row["sample_id"])
    prediction_ids: List[str] = []
    for row in predictions.get("records", []):
        score = _finite(row.get("score")) if isinstance(row, Mapping) else None
        if (
            not isinstance(row, Mapping)
            or not isinstance(row.get("sample_id"), str)
            or isinstance(row.get("prediction"), bool)
            or row.get("prediction") not in (0, 1)
            or score is None
            or score > 1.0
        ):
            gaps.append("quality.predictions.records")
            break
        prediction_ids.append(row["sample_id"])
    if (
        not label_ids
        or len(label_ids) != len(set(label_ids))
        or len(prediction_ids) != len(set(prediction_ids))
        or len(label_ids) != len(prediction_ids)
        or set(label_ids) != set(prediction_ids)
    ):
        gaps.append("quality.sample_set")
    if schema == 2:
        eligible = labels.get("eligible_events")
        relations = labels.get("sample_event_relations")
        event_keys = set()
        relation_keys = set()
        related_positive_ids = set()
        if not isinstance(eligible, list) or not eligible or not isinstance(relations, list):
            gaps.append("quality.labels.event_inventory")
        else:
            for row in eligible:
                if not isinstance(row, Mapping):
                    gaps.append("quality.labels.event_inventory")
                    break
                key = row.get("event_id")
                if (
                    not isinstance(key, str)
                    or not key
                    or key in event_keys
                ):
                    gaps.append("quality.labels.event_inventory")
                    break
                event_keys.add(key)
            for row in relations:
                if not isinstance(row, Mapping):
                    gaps.append("quality.labels.event_relations")
                    break
                relation = (row.get("sample_id"), row.get("group"), row.get("event_id"))
                if (
                    relation in relation_keys
                    or relation[0] not in positive_ids
                    or label_groups.get(relation[0]) != relation[1]
                    or relation[2] not in event_keys
                ):
                    gaps.append("quality.labels.event_relations")
                    break
                relation_keys.add(relation)
                related_positive_ids.add(relation[0])
            if positive_ids != related_positive_ids:
                gaps.append("quality.labels.event_relations")
    return sorted(set(gaps))


def _counter_observations(pipeline: Mapping[str, Any], names: Sequence[str]) -> Tuple[Dict[int, Dict[str, int]], List[str]]:
    raw = pipeline.get("counter_observations")
    if raw is None and isinstance(pipeline.get("pipeline_metrics"), Mapping):
        raw = pipeline["pipeline_metrics"].get("counter_observations")
    if not isinstance(raw, list):
        return {}, ["windows.timestamped_internal_counters_missing"]
    result: Dict[int, Dict[str, int]] = {}
    gaps: List[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            gaps.append("windows.internal_counter_observation.{}".format(index))
            continue
        epoch = item.get("boundary_epoch_second")
        counters = item.get("counters")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch in result or not isinstance(counters, Mapping):
            gaps.append("windows.internal_counter_observation.{}".format(index))
            continue
        parsed: Dict[str, int] = {}
        for name in names:
            value = counters.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                gaps.append("windows.internal_counter_observation.{}.{}".format(index, name))
                break
            parsed[name] = value
        if len(parsed) == len(names):
            result[epoch] = parsed
    return result, sorted(set(gaps))


def _external_observations(physical: Mapping[str, Any], names: Sequence[str]) -> Tuple[Dict[int, Dict[str, int]], List[str]]:
    result: Dict[int, Dict[str, int]] = {}
    gaps: List[str] = []
    raw = physical.get("samples")
    if not isinstance(raw, list):
        return {}, ["windows.timestamped_external_counters_missing"]
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            continue
        epoch = item.get("boundary_epoch_second")
        counters = item.get("external_counters")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch in result or not isinstance(counters, Mapping):
            continue
        parsed: Dict[str, int] = {}
        for name in names:
            value = counters.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                break
            parsed[name] = value
        if len(parsed) == len(names):
            result[epoch] = parsed
    if not result:
        gaps.append("windows.timestamped_external_counters_missing")
    return result, gaps


def _latency_receipts(
    pipeline: Mapping[str, Any],
    config: Mapping[str, Any],
) -> Tuple[Dict[int, Dict[str, List[Dict[str, Any]]]], List[str]]:
    metrics = pipeline.get("pipeline_metrics")
    if not isinstance(metrics, Mapping):
        return {}, ["windows.pipeline_metrics_missing"]
    receipts = metrics.get("raw_latency_sample_receipts")
    if not isinstance(receipts, list):
        return {}, ["windows.raw_latency_receipts_missing"]
    truncated = metrics.get("raw_latency_sample_receipts_truncated")
    gaps: List[str] = []
    if truncated != 0:
        gaps.append("windows.raw_latency_receipts_truncated")
    mapping = config.get("latency_metrics")
    if not isinstance(mapping, Mapping):
        raise CollectorError("collector latency metric mapping missing")
    result: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}
    seen: set = set()
    for index, item in enumerate(receipts):
        if not isinstance(item, Mapping):
            gaps.append("windows.raw_latency_receipt.{}".format(index))
            continue
        metric = mapping.get(item.get("metric"))
        source_id = item.get("source_id")
        epoch = item.get("window_id")
        observed = item.get("observed_epoch_us")
        value = _finite(item.get("value_us"))
        if metric is None:
            continue
        if (
            not isinstance(source_id, str)
            or not source_id
            or source_id in seen
            or isinstance(epoch, bool)
            or not isinstance(epoch, int)
            or isinstance(observed, bool)
            or not isinstance(observed, int)
            or observed // 1_000_000 != epoch
            or value is None
        ):
            gaps.append("windows.raw_latency_receipt.{}".format(index))
            continue
        seen.add(source_id)
        result.setdefault(epoch, {}).setdefault(str(metric), []).append(
            {
                "sample_id": "{}:{}".format(metric, source_id),
                "source_event_id": source_id,
                "value_us": value,
            }
        )
    return result, sorted(set(gaps))


def _longest_consecutive(values: Sequence[int]) -> List[int]:
    best: List[int] = []
    current: List[int] = []
    for value in sorted(set(values)):
        if not current or value == current[-1] + 1:
            current.append(value)
        else:
            if len(current) > len(best):
                best = current
            current = [value]
    return current if len(current) > len(best) else best


def normalize_windows(
    pipeline: Mapping[str, Any],
    physical: Mapping[str, Any],
    config: Mapping[str, Any],
    run_id: str,
    generator_run_id: str,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    internal_names = config.get("internal_counters")
    external_names = config.get("external_counters")
    minimums = config.get("minimum_latency_samples_per_window")
    if not isinstance(internal_names, list) or not isinstance(external_names, list) or not isinstance(minimums, Mapping):
        raise CollectorError("collector counter/sample config missing")
    internal, gaps = _counter_observations(pipeline, internal_names)
    external, external_gaps = _external_observations(physical, external_names)
    latency, latency_gaps = _latency_receipts(pipeline, config)
    gaps.extend(external_gaps)
    gaps.extend(latency_gaps)
    raw_epoch_counts = pipeline.get("epoch_second_counts")
    epoch_counts: Dict[int, int] = {}
    if not isinstance(raw_epoch_counts, Mapping):
        gaps.append("windows.pipeline_epoch_counts_missing")
    else:
        for raw_epoch, raw_count in raw_epoch_counts.items():
            try:
                epoch = int(raw_epoch)
            except (TypeError, ValueError):
                gaps.append("windows.pipeline_epoch_count.invalid_epoch")
                continue
            if (
                isinstance(raw_count, bool)
                or not isinstance(raw_count, int)
                or raw_count < 0
                or epoch in epoch_counts
            ):
                gaps.append("windows.pipeline_epoch_count.{}".format(raw_epoch))
                continue
            epoch_counts[epoch] = raw_count
    candidates: List[int] = []
    for epoch in sorted(set(internal) & set(external) & set(latency)):
        if epoch + 1 not in internal or epoch + 1 not in external:
            continue
        before = dict(external[epoch])
        before.update(internal[epoch])
        after = dict(external[epoch + 1])
        after.update(internal[epoch + 1])
        if any(after[name] < before[name] for name in before):
            gaps.append("windows.epoch.{}.counter_regression".format(epoch))
            continue
        packet_delta = internal[epoch + 1]["packets_received"] - internal[epoch]["packets_received"]
        if epoch not in epoch_counts:
            gaps.append("windows.epoch.{}.pipeline_epoch_count_missing".format(epoch))
            continue
        if epoch_counts[epoch] != packet_delta:
            gaps.append("windows.epoch.{}.pipeline_epoch_count_mismatch".format(epoch))
            continue
        series = latency[epoch]
        missing = [name for name, count in minimums.items() if len(series.get(name, [])) < int(count)]
        if missing:
            gaps.extend("windows.epoch.{}.{}.sample_count".format(epoch, name) for name in missing)
            continue
        candidates.append(epoch)
    selected = _longest_consecutive(candidates)
    if len(selected) < int(config["required_consecutive_windows"]):
        gaps.append("windows.insufficient_consecutive_complete")
        return None, sorted(set(gaps))
    rows: List[Dict[str, Any]] = []
    for epoch in selected:
        start = dict(external[epoch])
        start.update(internal[epoch])
        end = dict(external[epoch + 1])
        end.update(internal[epoch + 1])
        rows.append(
            {
                "epoch_second": epoch,
                "duration_ns": 1_000_000_000,
                "counters_start": start,
                "counters_end": end,
                **{name: latency[epoch][name] for name in minimums},
            }
        )
    return {
        "schema_version": 2,
        "scope": WINDOW_SCOPE,
        "run_id": run_id,
        "generator_run_id": generator_run_id,
        "normalization": "timestamped_cumulative_boundaries_and_raw_receipts_only",
        "windows": rows,
    }, sorted(set(gaps))


def _prepared_artifacts(
    path: Optional[Path], expected_config_sha256: str
) -> Tuple[Optional[Mapping[str, Any]], List[str]]:
    if path is None or not _regular(path):
        return None, [
            "missing:model",
            "missing:runtime_manifest",
            "missing:service_source",
            "missing:engine_source",
            "missing:service_launcher",
        ]
    receipt = _load_json(path)
    if receipt.get("scope") != PREPARE_SCOPE or receipt.get("gaps") != []:
        return None, [
            "missing:model",
            "missing:runtime_manifest",
            "missing:service_source",
            "missing:engine_source",
            "missing:service_launcher",
        ]
    root = path.parent.resolve()
    frozen_config = root / "frozen" / "collector_config.json"
    manifest_ref = receipt.get("prepare_manifest")
    if (
        receipt.get("collector_config_sha256") != expected_config_sha256
        or not _regular(frozen_config)
        or _sha256(frozen_config) != expected_config_sha256
        or not isinstance(manifest_ref, Mapping)
        or not isinstance(manifest_ref.get("path"), str)
        or not isinstance(manifest_ref.get("sha256"), str)
    ):
        return None, ["prepared_artifacts.collector_config_or_manifest"]
    manifest_posix = PurePosixPath(str(manifest_ref["path"]))
    if manifest_posix.is_absolute() or ".." in manifest_posix.parts:
        return None, ["prepared_artifacts.prepare_manifest_path"]
    manifest_path = root / Path(*manifest_posix.parts)
    if not _regular(manifest_path) or _sha256(manifest_path) != manifest_ref.get("sha256"):
        return None, ["prepared_artifacts.prepare_manifest_hash"]
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, Mapping):
        return None, ["prepared_artifacts.schema"]
    for name in ("model", "runtime_manifest", "service_source", "engine_source", "service_launcher"):
        ref = artifacts.get(name)
        if not isinstance(ref, Mapping):
            return None, ["prepared_artifacts.{}".format(name)]
        raw_path = ref.get("path")
        if not isinstance(raw_path, str):
            return None, ["prepared_artifacts.{}".format(name)]
        posix = PurePosixPath(raw_path)
        if posix.is_absolute() or ".." in posix.parts:
            return None, ["prepared_artifacts.{}".format(name)]
        artifact = root / Path(*posix.parts)
        if not _regular(artifact) or _sha256(artifact) != ref.get("sha256"):
            return None, ["prepared_artifacts.{}.hash".format(name)]
    return receipt, []


def _derive_identity(
    prepared: Mapping[str, Any],
    physical: Mapping[str, Any],
    service: Mapping[str, Any],
    evidence_dir: Path,
    campaign_id: str,
    candidate_id: str,
    backend: str,
    mode: str,
    repeat_index: int,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    gaps: List[str] = []
    pipeline = physical.get("pipeline_process_identity")
    generators = physical.get("generator_process_identities")
    runtime_identity = service.get("service_runtime_identity")
    physical_network = physical.get("physical_network_identity")
    hardware_sha = physical.get("hardware_identity_sha256")
    if not isinstance(pipeline, Mapping):
        gaps.append("identity.pipeline_process")
    if not isinstance(generators, list) or not generators:
        gaps.append("identity.generator_processes")
    if not isinstance(runtime_identity, Mapping):
        gaps.append("identity.service_runtime")
    if not isinstance(physical_network, Mapping):
        gaps.append("identity.physical_network")
    if not isinstance(hardware_sha, str) or not SHA256_RE.fullmatch(hardware_sha):
        gaps.append("identity.hardware")
    artifact_sha = prepared.get("artifact_sha256")
    prepared_runtime = prepared.get("runtime_identity")
    if not isinstance(artifact_sha, Mapping):
        gaps.append("identity.prepared_hashes")
    if not isinstance(prepared_runtime, Mapping):
        gaps.append("identity.prepared_runtime")
    if (
        prepared.get("campaign_id") != campaign_id
        or prepared.get("candidate_id") != candidate_id
        or prepared.get("backend") != backend
        or prepared.get("mode") != mode
        or prepared.get("repeat_index") != repeat_index
    ):
        gaps.append("identity.prepare_run_binding")
    if isinstance(runtime_identity, Mapping) and isinstance(artifact_sha, Mapping):
        if runtime_identity.get("manifest_actual_sha256") != artifact_sha.get("runtime_manifest"):
            gaps.append("identity.runtime_manifest_hash")
        process = runtime_identity.get("process")
        if not isinstance(process, Mapping) or process.get("pid") != runtime_identity.get("manifest_declared_pid"):
            gaps.append("identity.service_process")
        elif isinstance(prepared_runtime, Mapping):
            process_binding = (
                process.get("pid") == prepared_runtime.get("pid")
                and process.get("start_ticks") == prepared_runtime.get("process_start_ticks")
                and process.get("exe") == prepared_runtime.get("python_executable")
                and process.get("cwd") == prepared_runtime.get("working_directory")
                and process.get("cmdline_sha256") == prepared_runtime.get("command_sha256")
            )
            if not process_binding:
                gaps.append("identity.service_process_manifest_binding")
        live_artifacts = runtime_identity.get("live_artifacts")
        live_hashes = live_artifacts.get("sha256") if isinstance(live_artifacts, Mapping) else None
        if not isinstance(live_hashes, Mapping):
            gaps.append("identity.live_runtime_hashes")
        else:
            for name in ("model", "service_source", "engine_source"):
                if live_hashes.get(name) != artifact_sha.get(name):
                    gaps.append("identity.live_runtime_hash." + name)
            if (
                not isinstance(live_hashes.get("python_executable"), str)
                or not SHA256_RE.fullmatch(str(live_hashes.get("python_executable")))
                or live_artifacts.get("health_model_path_matches") is not True
                or live_artifacts.get("health_model_sha256") != live_hashes.get("model")
                or live_artifacts.get("health_inference_engine")
                != prepared_runtime.get("inference_engine")
            ):
                gaps.append("identity.live_runtime_health_binding")
        final_observation = runtime_identity.get("final_observation")
        final_process = final_observation.get("process") if isinstance(final_observation, Mapping) else None
        final_live = final_observation.get("live_artifacts") if isinstance(final_observation, Mapping) else None
        final_hashes = final_live.get("sha256") if isinstance(final_live, Mapping) else None
        final_listener = final_observation.get("listener_50051") if isinstance(final_observation, Mapping) else None
        final_health = final_observation.get("localhost_health") if isinstance(final_observation, Mapping) else None
        final_response = final_health.get("response") if isinstance(final_health, Mapping) else None
        if (
            not isinstance(final_process, Mapping)
            or not isinstance(process, Mapping)
            or final_process.get("pid") != process.get("pid")
            or final_process.get("start_ticks") != process.get("start_ticks")
            or final_process.get("exe") != process.get("exe")
            or final_process.get("cwd") != process.get("cwd")
            or final_process.get("cmdline_sha256") != process.get("cmdline_sha256")
            or not isinstance(final_hashes, Mapping)
            or final_hashes != live_hashes
            or not isinstance(final_listener, Mapping)
            or final_listener.get("query_ok") is not True
            or runtime_identity.get("manifest_declared_pid") not in final_listener.get("owner_pids", [])
            or not isinstance(final_response, Mapping)
            or final_response.get("ok") is not True
            or final_response.get("candidate_id") != "A09"
            or final_response.get("model_sha256") != live_hashes.get("model")
            or final_response.get("inference_engine") != prepared_runtime.get("inference_engine")
        ):
            gaps.append("identity.live_runtime_final_binding")
        listener = runtime_identity.get("listener_50051")
        if (
            not isinstance(listener, Mapping)
            or listener.get("query_ok") is not True
            or runtime_identity.get("manifest_declared_pid") not in listener.get("owner_pids", [])
        ):
            gaps.append("identity.listener_owner")
        health = runtime_identity.get("localhost_health")
        response = health.get("response") if isinstance(health, Mapping) else None
        counters = response.get("service_counters") if isinstance(response, Mapping) else None
        failures = (
            counters.get("failures")
            if isinstance(counters, Mapping)
            else response.get("failures") if isinstance(response, Mapping) else None
        )
        if (
            not isinstance(response, Mapping)
            or response.get("ok") is not True
            or response.get("candidate_id") != "A09"
            or failures not in (0, [])
        ):
            gaps.append("identity.localhost_health")
    if isinstance(physical_network, Mapping):
        health = physical_network.get("gpu_health")
        response = health.get("response") if isinstance(health, Mapping) else None
        counters = response.get("service_counters") if isinstance(response, Mapping) else None
        failures = (
            counters.get("failures")
            if isinstance(counters, Mapping)
            else response.get("failures") if isinstance(response, Mapping) else None
        )
        if (
            not isinstance(response, Mapping)
            or response.get("ok") is not True
            or response.get("candidate_id") != "A09"
            or failures not in (0, [])
        ):
            gaps.append("identity.physical_to_gpu_health")
        reverse = physical_network.get("reverse_socket")
        listener = reverse.get("listener") if isinstance(reverse, Mapping) else None
        pipeline_pid = pipeline.get("pid") if isinstance(pipeline, Mapping) else None
        if (
            not isinstance(reverse, Mapping)
            or reverse.get("query_ok") is not True
            or reverse.get("established") is not True
            or not isinstance(listener, Mapping)
            or listener.get("query_ok") is not True
            or pipeline_pid not in listener.get("owner_pids", [])
            or pipeline_pid not in reverse.get("established_owner_pids", [])
        ):
            gaps.append("identity.reverse_50052_chain")
    frozen_paths = {
        "runner": evidence_dir / "frozen" / "runner.sh",
        "config": evidence_dir / "frozen" / "config.json",
        "capture_binary": evidence_dir / "frozen" / "tpacket_v3_full_pipeline",
    }
    code_parts: Dict[str, str] = {}
    for name, path in frozen_paths.items():
        if not _regular(path):
            gaps.append("identity.code_artifact." + name)
        else:
            code_parts[name] = _sha256(path)
    if isinstance(artifact_sha, Mapping):
        code_parts.update({"gpu_" + str(name): str(value) for name, value in artifact_sha.items()})
    if isinstance(runtime_identity, Mapping):
        live_artifacts = runtime_identity.get("live_artifacts")
        live_hashes = live_artifacts.get("sha256") if isinstance(live_artifacts, Mapping) else None
        if isinstance(live_hashes, Mapping) and isinstance(live_hashes.get("python_executable"), str):
            code_parts["gpu_python_executable"] = str(live_hashes["python_executable"])
    if gaps:
        return None, sorted(set(gaps))
    assert isinstance(pipeline, Mapping)
    assert isinstance(generators, list)
    generator_rows = [row for row in generators if isinstance(row, Mapping)]
    if not generator_rows or any(not isinstance(row.get("start_ticks"), int) for row in generator_rows):
        return None, ["identity.generator_processes"]
    run_material = {
        "boot_id": physical.get("hardware_identity_material", {}).get("boot_id"),
        "pipeline": pipeline,
        "mode": mode,
        "repeat_index": repeat_index,
    }
    generator_material = {
        "boot_id": physical.get("hardware_identity_material", {}).get("boot_id"),
        "processes": generator_rows,
        "mode": mode,
        "repeat_index": repeat_index,
    }
    return {
        "schema_version": 2,
        "scope": IDENTITY_SCOPE,
        "campaign_id": campaign_id,
        "candidate_id": candidate_id,
        "backend": backend,
        "mode": mode,
        "repeat_index": repeat_index,
        "run_id": "run-" + _canonical_sha(run_material),
        "generator_run_id": "generator-" + _canonical_sha(generator_material),
        "generator_process_start_ticks": min(int(row["start_ticks"]) for row in generator_rows),
        "hardware_identity_sha256": hardware_sha,
        "code_tree_sha256": _canonical_sha(code_parts),
        "identity_derivation": "observed_boot_process_generator_and_frozen_hashes_v1",
        "gpu_runtime_manifest_sha256": artifact_sha["runtime_manifest"],
        "gpu_runtime_identity": runtime_identity,
    }, []


def _validate_fallback(path: Path, run_id: str, config: Mapping[str, Any]) -> List[str]:
    if not _regular(path):
        return ["fallback_events.missing_or_symlinked"]
    value = _load_json(path)
    events = value.get("events")
    required = config.get("fallback_required_steps")
    if (
        value.get("schema_version") != 2
        or value.get("scope") != FALLBACK_SCOPE
        or value.get("run_id") != run_id
        or not isinstance(events, list)
        or not isinstance(required, list)
        or [item.get("step") if isinstance(item, Mapping) else None for item in events] != required
    ):
        return ["fallback_events.schema_or_identity"]
    stamps = [item.get("monotonic_ns") for item in events]
    if any(isinstance(value, bool) or not isinstance(value, int) for value in stamps) or any(
        left >= right for left, right in zip(stamps, stamps[1:])
    ):
        return ["fallback_events.monotonic_order"]
    by_step = {
        item["step"]: item for item in events if isinstance(item, Mapping) and isinstance(item.get("step"), str)
    }
    faults = by_step.get("fault_injection_observed", {})
    local = by_step.get("local_fallback_activated", {})
    post = by_step.get("post_switch_traffic_observed", {})
    recovery = by_step.get("primary_recovered", {})
    final = by_step.get("final_state_verification", {})
    if (
        faults.get("source") != "external_fault_injector"
        or not isinstance(faults.get("injection_receipt_sha256"), str)
        or not SHA256_RE.fullmatch(str(faults.get("injection_receipt_sha256")))
        or local.get("backend_identity") in (None, "", "remote_retry", "remote_attempt")
        or local.get("backend_identity") == "none_without_equivalent_a09_model"
        or local.get("quality_qualified") is not True
        or not isinstance(post.get("local_completed_delta"), int)
        or isinstance(post.get("local_completed_delta"), bool)
        or post.get("local_completed_delta", 0) <= 0
        or post.get("remote_scored_delta") != 0
        or recovery.get("backend_identity") != "A09/schema_v1/ordered_v1"
        or final.get("key_flows_outstanding") != 0
        or final.get("key_flows_terminal_unresolved") != 0
    ):
        return ["fallback_events.not_verified_local_completion"]
    return []


def finalize_evidence(
    *,
    config_path: Path,
    output_dir: Path,
    evidence_dir: Path,
    campaign_id: str,
    candidate_id: str,
    backend: str,
    mode: str,
    repeat_index: int,
    prepare_receipt: Optional[Path] = None,
    physical_raw: Optional[Path] = None,
    service_raw: Optional[Path] = None,
    quality_labels: Optional[Path] = None,
    quality_predictions: Optional[Path] = None,
    fallback_events: Optional[Path] = None,
) -> Dict[str, Any]:
    config = _config(config_path)
    output = _new_directory(output_dir)
    evidence = evidence_dir.resolve()
    if not evidence.is_dir() or evidence_dir.is_symlink():
        raise CollectorError("evidence_dir is missing or symlinked")
    evidence_gaps: List[str] = []
    normalization_gaps: List[str] = []
    prepared, prepare_gaps = _prepared_artifacts(prepare_receipt, _sha256(config_path))
    evidence_gaps.extend(item for item in prepare_gaps if item.startswith("missing:"))
    normalization_gaps.extend(item for item in prepare_gaps if not item.startswith("missing:"))
    physical: Optional[Mapping[str, Any]] = None
    service: Optional[Mapping[str, Any]] = None
    if physical_raw is not None and _regular(physical_raw):
        candidate = _load_json(physical_raw)
        collection_gaps = validate_collection_receipt(
            candidate,
            "physical",
            _sha256(config_path),
            int(config["clock_sync_max_absolute_offset_ns"]),
        )
        normalization_gaps.extend(collection_gaps)
        if not collection_gaps:
            physical = candidate
    if service_raw is not None and _regular(service_raw):
        candidate = _load_json(service_raw)
        collection_gaps = validate_collection_receipt(
            candidate,
            "service",
            _sha256(config_path),
            int(config["clock_sync_max_absolute_offset_ns"]),
        )
        normalization_gaps.extend(collection_gaps)
        if not collection_gaps:
            service = candidate
    if physical is not None and service is not None:
        clock_probe_gaps = cross_node_clock_probe_gaps(
            physical,
            service,
            int(config["cross_node_clock_max_offset_bound_ns"]),
        )
        normalization_gaps.extend(clock_probe_gaps)
        if clock_probe_gaps:
            service = None
    identity: Optional[Dict[str, Any]] = None
    if prepared is not None and physical is not None and service is not None:
        identity, identity_gaps = _derive_identity(
            prepared,
            physical,
            service,
            evidence,
            campaign_id,
            candidate_id,
            backend,
            mode,
            repeat_index,
        )
        normalization_gaps.extend(identity_gaps)
    if identity is None:
        evidence_gaps.append("missing:identity_receipt")
    run_id = identity["run_id"] if identity is not None else ""
    generator_run_id = identity["generator_run_id"] if identity is not None else ""
    pipeline_path = evidence / "pipeline_raw.json"
    window_payload: Optional[Dict[str, Any]] = None
    selected_epochs: List[int] = []
    if _regular(pipeline_path) and physical is not None and identity is not None:
        pipeline = _load_json(pipeline_path)
        window_payload, window_gaps = normalize_windows(
            pipeline, physical, config, run_id, generator_run_id
        )
        normalization_gaps.extend(window_gaps)
        if window_payload is not None:
            selected_epochs = [int(row["epoch_second"]) for row in window_payload["windows"]]
    else:
        if not _regular(pipeline_path):
            normalization_gaps.append("windows.pipeline_raw_missing")
        if physical is None:
            normalization_gaps.append("windows.physical_raw_missing")
        # Audit old aggregate-only runs even without identity so their exact
        # scientific gaps are visible rather than hidden behind identity.
        if _regular(pipeline_path):
            pipeline = _load_json(pipeline_path)
            _unused, audit_gaps = normalize_windows(
                pipeline,
                physical or {},
                config,
                "unavailable",
                "unavailable",
            )
            normalization_gaps.extend(audit_gaps)
    if window_payload is None:
        evidence_gaps.append("missing:window_observations")
    physical_rows: List[Dict[str, Any]] = []
    service_rows: List[Dict[str, Any]] = []
    if physical is not None and selected_epochs:
        physical_rows, gaps = normalize_resource_samples(
            physical, selected_epochs, int(config["boundary_max_skew_ns"])
        )
        normalization_gaps.extend(gaps)
    if service is not None and selected_epochs:
        service_rows, gaps = normalize_resource_samples(
            service, selected_epochs, int(config["boundary_max_skew_ns"])
        )
        normalization_gaps.extend(gaps)
        if physical is not None:
            clock_gaps = cross_node_boundary_gaps(
                physical,
                service,
                selected_epochs,
                int(config["cross_node_boundary_max_skew_ns"]),
            )
            normalization_gaps.extend(clock_gaps)
            if clock_gaps:
                service_rows = []
    if len(physical_rows) != len(selected_epochs) or not selected_epochs:
        evidence_gaps.append("missing:physical_resources")
    if len(service_rows) != len(selected_epochs) or not selected_epochs:
        evidence_gaps.append("missing:service_resources")
    quality_ok = False
    if (
        quality_labels is not None
        and quality_predictions is not None
        and prepare_receipt is not None
        and prepared is not None
    ):
        quality_gaps = validate_quality_evidence(quality_labels, quality_predictions, prepare_receipt)
        normalization_gaps.extend(quality_gaps)
        quality_ok = not quality_gaps
    if not quality_ok:
        evidence_gaps.extend(["missing:quality_labels", "missing:quality_predictions"])
    fallback_ok = mode == "normal"
    if mode == "fallback":
        if fallback_events is None or identity is None:
            evidence_gaps.append("missing:fallback_events")
        else:
            fallback_gaps = _validate_fallback(fallback_events, run_id, config)
            normalization_gaps.extend(fallback_gaps)
            fallback_ok = not fallback_gaps
            if not fallback_ok:
                evidence_gaps.append("missing:fallback_events")
    elif fallback_events is not None:
        normalization_gaps.append("fallback_events.unexpected_in_normal_mode")
    staged = output / "staged"
    staged.mkdir(mode=0o700)
    adapter: Dict[str, Optional[str]] = {
        "model": None,
        "runtime_manifest": None,
        "service_source": None,
        "engine_source": None,
        "service_launcher": None,
        "identity_receipt": None,
        "window_observations": None,
        "physical_resources": None,
        "service_resources": None,
        "quality_labels": None,
        "quality_source": None,
        "quality_predictions": None,
        "fallback_events": None,
    }
    if prepared is not None and prepare_receipt is not None:
        source_root = prepare_receipt.parent.resolve()
        for name in ("model", "runtime_manifest", "service_source", "engine_source", "service_launcher"):
            ref = prepared["artifacts"][name]
            source = source_root / Path(*PurePosixPath(ref["path"]).parts)
            target = staged / source.name
            _copy_regular(source, target)
            if _sha256(target) != ref["sha256"]:
                raise CollectorError("prepared artifact drift during finalize: " + name)
            adapter[name] = str(target)
    if identity is not None:
        target = staged / "run_identity_receipt_v2.json"
        _atomic_json(target, identity)
        adapter["identity_receipt"] = str(target)
    if window_payload is not None:
        target = staged / "window_observations_v2.json"
        _atomic_json(target, window_payload)
        adapter["window_observations"] = str(target)
    if physical_rows and len(physical_rows) == len(selected_epochs):
        target = staged / "physical_resources_v2.json"
        _atomic_json(
            target,
            {
                "schema_version": 2,
                "scope": RESOURCE_SCOPE,
                "node_role": "physical",
                "run_id": run_id,
                "samples": physical_rows,
            },
        )
        adapter["physical_resources"] = str(target)
    if service_rows and len(service_rows) == len(selected_epochs):
        target = staged / "service_resources_v2.json"
        _atomic_json(
            target,
            {
                "schema_version": 2,
                "scope": RESOURCE_SCOPE,
                "node_role": "service",
                "run_id": run_id,
                "samples": service_rows,
            },
        )
        adapter["service_resources"] = str(target)
    if quality_ok and quality_labels is not None and quality_predictions is not None:
        label_target = staged / "independent_labels.json"
        prediction_target = staged / "independent_predictions.json"
        _copy_regular(quality_labels, label_target)
        _copy_regular(quality_predictions, prediction_target)
        label_value = _load_json(label_target)
        raw_source = label_value.get("source_artifact_path")
        if not isinstance(raw_source, str) or not raw_source:
            raise CollectorError("quality source path vanished during finalize")
        source = Path(raw_source)
        if not source.is_absolute():
            source = quality_labels.parent / source
        source_target = staged / source.name
        _copy_regular(source, source_target)
        if _sha256(source_target) != label_value.get("source_artifact_sha256"):
            raise CollectorError("quality source drift during finalize")
        if label_value.get("source_artifact_path") != source_target.name:
            label_value = dict(label_value)
            label_value["source_artifact_path"] = source_target.name
            _atomic_json(label_target, label_value)
            prediction_value = dict(_load_json(prediction_target))
            prediction_value["labels_sha256"] = _sha256(label_target)
            _atomic_json(prediction_target, prediction_value)
        raw_prepare = label_value.get("prepare_receipt_path")
        if isinstance(raw_prepare, str) and raw_prepare:
            source_prepare = quality_labels.parent / raw_prepare
            target_prepare = staged / Path(raw_prepare).name
            _copy_regular(source_prepare, target_prepare)
            if _sha256(target_prepare) != label_value.get("prepare_receipt_sha256"):
                raise CollectorError("portable prepare receipt drift during finalize")
        if prepare_receipt is None:
            raise CollectorError("prepare receipt vanished during quality staging")
        staged_quality_gaps = validate_quality_evidence(
            label_target, prediction_target, prepare_receipt
        )
        if staged_quality_gaps:
            raise CollectorError(
                "quality evidence drift during finalize: " + ",".join(staged_quality_gaps)
            )
        adapter["quality_labels"] = str(label_target)
        adapter["quality_source"] = str(source_target)
        adapter["quality_predictions"] = str(prediction_target)
    if fallback_ok and mode == "fallback" and fallback_events is not None:
        target = staged / "fallback_events_v2.json"
        _copy_regular(fallback_events, target)
        adapter["fallback_events"] = str(target)
    evidence_gaps = sorted(set(evidence_gaps))
    normalization_gaps = sorted(set(normalization_gaps))
    adapter_ready = not evidence_gaps and not normalization_gaps
    receipt: Dict[str, Any] = {
        "schema_version": 1,
        "scope": FINALIZE_SCOPE,
        "read_only_source_access": True,
        "service_started_or_stopped": False,
        "traffic_started_or_stopped": False,
        "campaign_id": campaign_id,
        "candidate_id": candidate_id,
        "backend": backend,
        "mode": mode,
        "repeat_index": repeat_index,
        "adapter_ready": adapter_ready,
        "run_qualified": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "evidence_gaps": evidence_gaps,
        "normalization_gaps": normalization_gaps,
        "adapter_arguments": adapter,
        "selected_window_epochs": selected_epochs,
    }
    _atomic_json(output / "finalize_receipt.json", receipt)
    return receipt


def _prepare_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("prepare", help="Freeze and hash-bind existing GPU runtime artifacts")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--backend", default="tpacket_v3")
    parser.add_argument("--mode", choices=("normal", "fallback"), required=True)
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--service-source", type=Path, required=True)
    parser.add_argument("--engine-source", type=Path, required=True)
    parser.add_argument("--service-launcher", type=Path, required=True)


def _collect_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("collect", help="Read one node at aligned one-second boundaries")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--role", choices=("physical", "service"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration-seconds", type=int, default=22)
    parser.add_argument("--interface")
    parser.add_argument("--pktgen-device", action="append", type=Path, default=[])
    parser.add_argument("--pipeline-identity-file", type=Path)
    parser.add_argument("--runtime-manifest", type=Path)
    parser.add_argument("--gpu-health-host")
    parser.add_argument("--gpu-health-port", type=int, default=50051)
    parser.add_argument("--reverse-port", type=int, default=50052)
    parser.add_argument("--clock-probe-host")
    parser.add_argument("--clock-probe-listen-host")
    parser.add_argument("--clock-probe-port", type=int, default=50053)


def _finalize_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("finalize", help="Normalize only complete timestamped evidence")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--backend", default="tpacket_v3")
    parser.add_argument("--mode", choices=("normal", "fallback"), required=True)
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--prepare-receipt", type=Path)
    parser.add_argument("--physical-raw", type=Path)
    parser.add_argument("--service-raw", type=Path)
    parser.add_argument("--quality-labels", type=Path)
    parser.add_argument("--quality-predictions", type=Path)
    parser.add_argument("--fallback-events", type=Path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="phase", required=True)
    _prepare_parser(subparsers)
    _collect_parser(subparsers)
    _finalize_parser(subparsers)
    args = parser.parse_args()
    try:
        if args.phase == "prepare":
            result = prepare_evidence(
                config_path=args.config,
                output_dir=args.output_dir,
                campaign_id=args.campaign_id,
                candidate_id=args.candidate_id,
                backend=args.backend,
                mode=args.mode,
                repeat_index=args.repeat_index,
                runtime_manifest=args.runtime_manifest,
                model=args.model,
                service_source=args.service_source,
                engine_source=args.engine_source,
                service_launcher=args.service_launcher,
            )
        elif args.phase == "collect":
            result = collect_node_evidence(
                config_path=args.config,
                role=args.role,
                output_path=args.output,
                duration_seconds=args.duration_seconds,
                interface=args.interface,
                pktgen_devices=args.pktgen_device,
                pipeline_identity_file=args.pipeline_identity_file,
                runtime_manifest=args.runtime_manifest,
                gpu_health_host=args.gpu_health_host,
                gpu_health_port=args.gpu_health_port,
                reverse_port=args.reverse_port,
                clock_probe_host=args.clock_probe_host,
                clock_probe_listen_host=args.clock_probe_listen_host,
                clock_probe_port=args.clock_probe_port,
            )
        else:
            result = finalize_evidence(
                config_path=args.config,
                output_dir=args.output_dir,
                evidence_dir=args.evidence_dir,
                campaign_id=args.campaign_id,
                candidate_id=args.candidate_id,
                backend=args.backend,
                mode=args.mode,
                repeat_index=args.repeat_index,
                prepare_receipt=args.prepare_receipt,
                physical_raw=args.physical_raw,
                service_raw=args.service_raw,
                quality_labels=args.quality_labels,
                quality_predictions=args.quality_predictions,
                fallback_events=args.fallback_events,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        if args.phase == "finalize":
            return 0 if result.get("adapter_ready") else 2
        return 0 if not result.get("gaps") and not result.get("errors") else 2
    except (CollectorError, OSError, UnicodeError, ValueError) as error:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "scope": "hft_mgbs_current_hardware_2_79_evidence_error_v1",
                    "phase": getattr(args, "phase", None),
                    "ok": False,
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "artifacts_emitted": False,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
