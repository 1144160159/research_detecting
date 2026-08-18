#!/usr/bin/env python3
"""Hash-bound, vendor-neutral helpers for the new-NIC R0 campaign.

This file is copied byte-for-byte to the eight helper role names.  The frozen
basename selects the role.  Hardware-specific programs are never interpolated
through a shell: an independently pinned execution plan supplies absolute argv
arrays plus SHA-256 identities for every executable and supporting artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CHANGE_RE = re.compile(r"^[A-Za-z0-9._:-]{4,128}$")
HELPER_ROLES = (
    "xdp_runner",
    "dpdk_runner",
    "generator_runner",
    "resource_sampler",
    "fallback_orchestrator",
    "restore_helper",
    "campaign_executor",
    "trust_root_recorder",
)
PLAN_SCOPE = "hft_mgbs_new_nic_r0_execution_plan_v1"
PLAN_OPERATIONS = frozenset(("snapshot", "restore", "xdp_run", "dpdk_run", "fallback"))
RUN_BACKENDS = {
    "xdp_runner": "native_af_xdp_forced_zerocopy",
    "dpdk_runner": "dpdk_rss_tss_multiqueue",
}


class HelperError(RuntimeError):
    pass


def _pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise HelperError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise HelperError("non-finite JSON value: " + value)


def _sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _stable_bytes(path: Path, *, maximum: int = 128 * 1024 * 1024) -> bytes:
    if not path.is_absolute():
        path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise HelperError("symlink component rejected: {}".format(path))
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise HelperError("regular file required: {}".format(path))
        if before.st_size > maximum:
            raise HelperError("file exceeds evidence size limit: {}".format(path))
        chunks = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(1024 * 1024, remaining))
            if not block:
                raise HelperError("short read: {}".format(path))
            chunks.append(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise HelperError("file grew while being read: {}".format(path))
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda item: (
        item.st_dev,
        item.st_ino,
        item.st_mode,
        item.st_nlink,
        item.st_size,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )
    current = path.stat()
    current_identity = (
        current.st_dev,
        current.st_ino,
        current.st_nlink,
        current.st_size,
        current.st_mtime_ns,
    )
    before_path_identity = (
        before.st_dev,
        before.st_ino,
        before.st_nlink,
        before.st_size,
        before.st_mtime_ns,
    )
    if identity(before) != identity(after) or before_path_identity != current_identity:
        raise HelperError("file changed while being read: {}".format(path))
    return b"".join(chunks)


def _read_json(path: Path, *, maximum: int = 128 * 1024 * 1024) -> Dict[str, Any]:
    value = json.loads(
        _stable_bytes(path, maximum=maximum).decode("utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=_nonfinite,
    )
    if not isinstance(value, dict):
        raise HelperError("JSON object required: {}".format(path))
    return value


def _canonical_sha(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return _sha_bytes(raw)


def _seal(value: Dict[str, Any]) -> Dict[str, Any]:
    if "receipt_sha256" in value:
        raise HelperError("receipt was already sealed")
    value["receipt_sha256"] = _canonical_sha(value)
    return value


def _safe_parent(path: Path) -> Path:
    parent = path.parent.absolute()
    current = Path(parent.anchor)
    for part in parent.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise HelperError("output parent contains a symlink")
    resolved = parent.resolve(strict=True)
    if not resolved.is_dir():
        raise HelperError("output parent is not a directory")
    return resolved


def _create_json(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise HelperError("create-only output already exists: {}".format(path))
    parent = _safe_parent(path)
    rendered = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    descriptor, temporary_raw = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(parent))
    temporary = Path(temporary_raw)
    created = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise HelperError("create-only output raced: {}".format(path))
        os.link(str(temporary), str(path))
        created = True
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    if created:
        os.chmod(str(path), 0o400 if os.name != "nt" else 0o600)


def _create_text(path: Path, value: str) -> None:
    if path.exists() or path.is_symlink():
        raise HelperError("create-only output already exists: {}".format(path))
    parent = _safe_parent(path)
    descriptor = os.open(
        str(parent / path.name),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
        0o400,
    )
    try:
        os.write(descriptor, value.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _manifest(run_dir: Path) -> Dict[str, Tuple[Path, str]]:
    path = run_dir / "frozen_helper_manifest.txt"
    raw = _stable_bytes(path, maximum=1024 * 1024).decode("utf-8")
    result: Dict[str, Tuple[Path, str]] = {}
    for index, line in enumerate(raw.splitlines(), 1):
        fields = line.split()
        if len(fields) != 3 or not SHA_RE.fullmatch(fields[2]):
            raise HelperError("invalid helper manifest line {}".format(index))
        role, declared_path, digest = fields
        if role in result:
            raise HelperError("duplicate helper role: " + role)
        result[role] = (Path(declared_path), digest)
    if not set(HELPER_ROLES).issubset(result):
        raise HelperError("helper manifest omits executable roles")
    return result


def _verify_role(run_dir: Path, role: str, executable: Optional[Path] = None) -> str:
    manifest = _manifest(run_dir)
    if role not in manifest:
        raise HelperError("role is absent from helper manifest: " + role)
    path = executable.absolute() if executable is not None else Path(sys.argv[0]).absolute()
    expected = manifest[role][1]
    if _sha_bytes(_stable_bytes(path, maximum=16 * 1024 * 1024)) != expected:
        raise HelperError("frozen helper identity mismatch: " + role)
    return expected


def _plan(path: Path, run_dir: Path) -> Dict[str, Any]:
    raw = _stable_bytes(path, maximum=8 * 1024 * 1024)
    binding = (run_dir / "execution_plan.sha256").read_text(encoding="ascii").strip()
    if not SHA_RE.fullmatch(binding) or _sha_bytes(raw) != binding:
        raise HelperError("execution plan does not match its external trust root")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    if not isinstance(value, dict):
        raise HelperError("execution plan must be an object")
    required = {
        "schema_version",
        "scope",
        "campaign_id",
        "capture_host_id",
        "candidate_pci_addresses",
        "generator_identity",
        "topology",
        "operations",
    }
    if set(value) != required or value.get("schema_version") != 1 or value.get("scope") != PLAN_SCOPE:
        raise HelperError("execution plan envelope is not exact")
    if not isinstance(value.get("campaign_id"), str) or not value["campaign_id"]:
        raise HelperError("execution plan campaign_id is invalid")
    addresses = value.get("candidate_pci_addresses")
    if not isinstance(addresses, list) or not addresses or any(not isinstance(item, str) for item in addresses):
        raise HelperError("execution plan candidate PCI addresses are invalid")
    generator = value.get("generator_identity")
    if not isinstance(generator, dict) or set(generator) != {
        "generator_host_id",
        "generator_nic_serial",
        "physical_link_id",
        "marker_manifest_sha256",
    } or not SHA_RE.fullmatch(str(generator.get("marker_manifest_sha256", ""))):
        raise HelperError("execution plan generator identity is invalid")
    topology = value.get("topology")
    if not isinstance(topology, dict) or set(topology) != {
        "fallback_design",
        "same_pf_runtime_driver_rebind",
        "independent_generator",
        "same_adapter_loopback",
    } or topology.get("same_pf_runtime_driver_rebind") is not False \
      or topology.get("independent_generator") is not True \
      or topology.get("same_adapter_loopback") is not False:
        raise HelperError("execution plan topology is unsafe")
    operations = value.get("operations")
    if not isinstance(operations, dict) or set(operations) != PLAN_OPERATIONS:
        raise HelperError("execution plan operations are not exact")
    for name, operation in operations.items():
        if not isinstance(operation, dict) or set(operation) != {
            "argv",
            "executable_sha256",
            "bound_files",
            "timeout_seconds",
        }:
            raise HelperError("operation {} is not exact".format(name))
        argv = operation.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(item, str) or "\x00" in item for item in argv):
            raise HelperError("operation {} argv is invalid".format(name))
        if not Path(argv[0]).is_absolute() or not SHA_RE.fullmatch(str(operation.get("executable_sha256", ""))):
            raise HelperError("operation {} executable identity is invalid".format(name))
        timeout = operation.get("timeout_seconds")
        if type(timeout) is not int or timeout < 1 or timeout > 3600:
            raise HelperError("operation {} timeout is invalid".format(name))
        files = operation.get("bound_files")
        if not isinstance(files, list):
            raise HelperError("operation {} bound_files is invalid".format(name))
        seen = set()
        for item in files:
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                raise HelperError("operation {} bound file is invalid".format(name))
            bound = Path(str(item.get("path")))
            if not bound.is_absolute() or str(bound) in seen or not SHA_RE.fullmatch(str(item.get("sha256", ""))):
                raise HelperError("operation {} bound file identity is invalid".format(name))
            seen.add(str(bound))
    return value


def _expand(value: str, variables: Mapping[str, str]) -> str:
    result = value
    for name, replacement in variables.items():
        result = result.replace("{" + name + "}", replacement)
    if re.search(r"\{[A-Za-z0-9_]+\}", result):
        raise HelperError("unresolved execution-plan placeholder: " + result)
    return result


def _environment() -> Dict[str, str]:
    value = {
        "PATH": "/usr/sbin:/usr/bin:/sbin:/bin" if os.name != "nt" else os.environ.get("PATH", ""),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    for name in ("SYSTEMROOT", "WINDIR"):
        if name in os.environ:
            value[name] = os.environ[name]
    return value


def _run_operation(
    plan: Mapping[str, Any],
    name: str,
    variables: Mapping[str, str],
    run_dir: Path,
) -> Optional[Dict[str, Any]]:
    operation = plan["operations"][name]
    argv = [_expand(item, variables) for item in operation["argv"]]
    executable = Path(argv[0])
    expected = operation["executable_sha256"]
    if _sha_bytes(_stable_bytes(executable, maximum=256 * 1024 * 1024)) != expected:
        raise HelperError("operation executable drifted before launch: " + name)
    bound = [(Path(item["path"]), item["sha256"]) for item in operation["bound_files"]]
    for path, digest in bound:
        if _sha_bytes(_stable_bytes(path, maximum=256 * 1024 * 1024)) != digest:
            raise HelperError("operation bound file drifted before launch: {}".format(path))
    completed = subprocess.run(
        argv,
        cwd=str(run_dir),
        env=_environment(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=operation["timeout_seconds"],
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace")[-2048:]
        raise HelperError("operation {} failed rc={}: {}".format(name, completed.returncode, detail))
    if _sha_bytes(_stable_bytes(executable, maximum=256 * 1024 * 1024)) != expected:
        raise HelperError("operation executable drifted after launch: " + name)
    for path, digest in bound:
        if _sha_bytes(_stable_bytes(path, maximum=256 * 1024 * 1024)) != digest:
            raise HelperError("operation bound file drifted after launch: {}".format(path))
    raw_output = variables.get("raw_output")
    if raw_output is None:
        return None
    output_path = Path(raw_output)
    if not output_path.is_file() or output_path.is_symlink():
        raise HelperError("operation did not create its raw output: " + name)
    return _read_json(output_path)


def _base_variables(args: argparse.Namespace, raw_output: Optional[Path] = None) -> Dict[str, str]:
    values = {
        "run_dir": str(Path(args.run_dir).resolve()),
        "change_ticket": str(getattr(args, "change_ticket", "")),
        "campaign_id": str(getattr(args, "campaign_id", "")),
        "run_id": str(getattr(args, "run_id", "")),
        "trial_id": str(getattr(args, "trial_id", "")),
        "repeat_index": str(getattr(args, "repeat_index", "")),
        "packet_size": str(getattr(args, "packet_size", "")),
        "offered_mpps": str(getattr(args, "offered_mpps", "")),
        "duration_seconds": str(getattr(args, "duration_seconds", "")),
        "xdp_run_id": str(getattr(args, "xdp_run_id", "")),
        "dpdk_run_id": str(getattr(args, "dpdk_run_id", "")),
        "phase": str(getattr(args, "phase", "")),
    }
    if raw_output is not None:
        values["raw_output"] = str(raw_output)
    return values


def _nested_generator(
    plan: Mapping[str, Any], raw: Mapping[str, Any], campaign_id: str, run_id: str,
    producer_sha: str, *, transition: bool,
) -> Dict[str, Any]:
    generator = plan["generator_identity"]
    if transition:
        required = {
            "window_started_monotonic_ns",
            "window_completed_monotonic_ns",
            "requested_packets",
            "sent_packets",
            "tx_errors",
            "packets_before_fault",
            "packets_fault_to_recovery",
            "packets_after_recovery",
            "max_inter_packet_gap_us",
        }
        if set(raw) != required:
            raise HelperError("generator transition raw fields are not exact")
        value = {
            "schema_version": 1,
            "scope": "new_nic_r0_generator_transition_receipt",
            "campaign_id": campaign_id,
            "producer_role": "generator_runner",
            "producer_sha256": producer_sha,
            "trial_id": run_id,
            **generator,
            **dict(raw),
        }
    else:
        required = {"started_at_utc", "completed_at_utc", "requested_packets", "sent_packets", "tx_errors"}
        if set(raw) != required:
            raise HelperError("generator window raw fields are not exact")
        value = {
            "schema_version": 1,
            "scope": "new_nic_r0_generator_window_receipt",
            "campaign_id": campaign_id,
            "producer_role": "generator_runner",
            "producer_sha256": producer_sha,
            "run_id": run_id,
            **generator,
            **dict(raw),
        }
    return _seal(value)


def _nested_resource(
    raw: Mapping[str, Any], campaign_id: str, run_id: str, producer_sha: str,
    started: str, completed: str,
) -> Dict[str, Any]:
    if set(raw) != {"samples"} or not isinstance(raw.get("samples"), list):
        raise HelperError("resource raw fields are not exact")
    return _seal({
        "schema_version": 1,
        "scope": "new_nic_r0_resource_window_receipt",
        "campaign_id": campaign_id,
        "producer_role": "resource_sampler",
        "producer_sha256": producer_sha,
        "run_id": run_id,
        "started_at_utc": started,
        "completed_at_utc": completed,
        "samples": raw["samples"],
    })


def _work_path(run_dir: Path, name: str) -> Path:
    work = run_dir / ".helper-work"
    work.mkdir(mode=0o700, exist_ok=True)
    if work.is_symlink() or work.resolve().parent != run_dir.resolve():
        raise HelperError("unsafe helper work directory")
    path = work / name
    if path.exists() or path.is_symlink():
        raise HelperError("helper raw output already exists")
    return path


def _run_receipt(role: str, args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve(strict=True)
    producer_sha = _verify_role(run_dir, role)
    plan = _plan(Path(args.execution_plan), run_dir)
    if args.campaign_id != plan["campaign_id"]:
        raise HelperError("campaign identity differs from execution plan")
    operation = "xdp_run" if role == "xdp_runner" else "dpdk_run"
    raw_path = _work_path(run_dir, args.run_id + ".raw.json")
    try:
        raw = _run_operation(plan, operation, _base_variables(args, raw_path), run_dir)
        assert raw is not None
        required = {
            "started_at_utc",
            "completed_at_utc",
            "generator",
            "capture",
            "latency_histogram",
            "latency_proof",
            "resource",
            "key_flow",
            "backend_proof",
        }
        if set(raw) != required:
            raise HelperError("run adapter raw fields are not exact")
        hashes = _manifest(run_dir)
        generator = _nested_generator(
            plan, raw["generator"], plan["campaign_id"], args.run_id,
            hashes["generator_runner"][1], transition=False,
        )
        resource = _nested_resource(
            raw["resource"], plan["campaign_id"], args.run_id,
            hashes["resource_sampler"][1], raw["started_at_utc"], raw["completed_at_utc"],
        )
        receipt = _seal({
            "schema_version": 1,
            "scope": "new_nic_r0_run_receipt",
            "campaign_id": plan["campaign_id"],
            "producer_role": role,
            "producer_sha256": producer_sha,
            "run_id": args.run_id,
            "repeat_index": args.repeat_index,
            "backend": RUN_BACKENDS[role],
            "capture_host_id": plan["capture_host_id"],
            "candidate_pci_addresses": plan["candidate_pci_addresses"],
            "generator_host_id": plan["generator_identity"]["generator_host_id"],
            "generator_nic_serial": plan["generator_identity"]["generator_nic_serial"],
            "physical_link_id": plan["generator_identity"]["physical_link_id"],
            "started_at_utc": raw["started_at_utc"],
            "completed_at_utc": raw["completed_at_utc"],
            "packet_size_bytes": args.packet_size,
            "generator": generator,
            "capture": raw["capture"],
            "latency_histogram": raw["latency_histogram"],
            "latency_proof": raw["latency_proof"],
            "resource": resource,
            "key_flow": raw["key_flow"],
            "backend_proof": raw["backend_proof"],
        })
        _create_json(Path(args.output), receipt)
    finally:
        try:
            raw_path.unlink()
        except FileNotFoundError:
            pass


def _fallback(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve(strict=True)
    producer_sha = _verify_role(run_dir, "fallback_orchestrator")
    plan = _plan(Path(args.execution_plan), run_dir)
    raw_path = _work_path(run_dir, args.trial_id + ".raw.json")
    try:
        raw = _run_operation(plan, "fallback", _base_variables(args, raw_path), run_dir)
        assert raw is not None
        required = {
            "generator_transition",
            "fault_injected_monotonic_ns",
            "first_dpdk_packet_monotonic_ns",
            "transition",
        }
        if set(raw) != required:
            raise HelperError("fallback adapter raw fields are not exact")
        injected = raw["fault_injected_monotonic_ns"]
        recovered = raw["first_dpdk_packet_monotonic_ns"]
        if type(injected) is not int or type(recovered) is not int or recovered < injected:
            raise HelperError("fallback monotonic timestamps are invalid")
        generator_sha = _manifest(run_dir)["generator_runner"][1]
        generator = _nested_generator(
            plan, raw["generator_transition"], plan["campaign_id"], args.trial_id,
            generator_sha, transition=True,
        )
        receipt = _seal({
            "schema_version": 1,
            "scope": "new_nic_r0_fallback_trial_receipt",
            "campaign_id": plan["campaign_id"],
            "producer_role": "fallback_orchestrator",
            "producer_sha256": producer_sha,
            "trial_id": args.trial_id,
            "repeat_index": args.repeat_index,
            "xdp_run_id": args.xdp_run_id,
            "dpdk_run_id": args.dpdk_run_id,
            "fault_kind": "forced_xdp_primary_stop",
            "generator_continuous": True,
            "generator_transition": generator,
            "fault_injected_monotonic_ns": injected,
            "first_dpdk_packet_monotonic_ns": recovered,
            "reported_recovery_ms": (recovered - injected) / 1_000_000.0,
            "transition": raw["transition"],
        })
        _create_json(Path(args.output), receipt)
    finally:
        try:
            raw_path.unlink()
        except FileNotFoundError:
            pass


def _restore(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve(strict=True)
    producer_sha = _verify_role(run_dir, "restore_helper")
    if not CHANGE_RE.fullmatch(args.change_ticket):
        raise HelperError("change ticket is invalid")
    plan = _plan(Path(args.execution_plan), run_dir)
    if args.mode == "restore":
        _run_operation(plan, "restore", _base_variables(args), run_dir)
        return
    phase = "before" if args.mode == "snapshot-before" else "after"
    raw_path = _work_path(run_dir, "restoration-{}.raw.json".format(phase))
    try:
        raw = _run_operation(plan, "snapshot", _base_variables(args, raw_path), run_dir)
        assert raw is not None
        if set(raw) != {"state_domains"} or not isinstance(raw["state_domains"], dict):
            raise HelperError("restoration snapshot raw fields are not exact")
        receipt = _seal({
            "schema_version": 1,
            "scope": "new_nic_r0_restoration_snapshot",
            "campaign_id": plan["campaign_id"],
            "producer_role": "restore_helper",
            "producer_sha256": producer_sha,
            "phase": phase,
            "state_domains": raw["state_domains"],
        })
        _create_json(Path(args.output), receipt)
    finally:
        try:
            raw_path.unlink()
        except FileNotFoundError:
            pass


def _campaign(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve(strict=True)
    _verify_role(run_dir, "campaign_executor")
    plan = _plan(Path(args.execution_plan), run_dir)
    if not CHANGE_RE.fullmatch(args.change_ticket):
        raise HelperError("change ticket is invalid")
    helpers = {
        "xdp_runner": Path(args.xdp_runner),
        "dpdk_runner": Path(args.dpdk_runner),
        "generator_runner": Path(args.generator_runner),
        "resource_sampler": Path(args.resource_sampler),
        "fallback_orchestrator": Path(args.fallback_orchestrator),
    }
    for role, path in helpers.items():
        _verify_role(run_dir, role, path)
    for role in ("generator_runner", "resource_sampler"):
        subprocess.run(
            [sys.executable, "-I", "-S", str(helpers[role]), "--run-dir", str(run_dir)],
            check=True,
            cwd=str(run_dir),
            env=_environment(),
        )
    if args.packet_size != 64 or args.offered_mpps < 12.0 or args.duration_seconds < 15:
        raise HelperError("campaign arguments are below the frozen R0 floor")
    if (args.xdp_repeats, args.dpdk_repeats, args.fallback_trials) != (3, 3, 3):
        raise HelperError("campaign repeat counts must be exactly 3/3/3")
    campaign = {
        "schema_version": 1,
        "scope": "new_high_speed_nic_r0_campaign",
        "campaign_id": plan["campaign_id"],
        "capture_host_id": plan["capture_host_id"],
        "authorized_execution": True,
        "mutations_performed": True,
        "arrival_evidence_manifest_sha256": args.arrival_evidence_manifest_sha256,
        "candidate_pci_addresses": plan["candidate_pci_addresses"],
        "generator_identity": plan["generator_identity"],
        "topology": plan["topology"],
    }
    _create_json(run_dir / "campaign.json", campaign)
    common = [
        "--execution-plan", str(Path(args.execution_plan).resolve()),
        "--run-dir", str(run_dir),
        "--campaign-id", plan["campaign_id"],
        "--packet-size", str(args.packet_size),
        "--offered-mpps", str(args.offered_mpps),
        "--duration-seconds", str(args.duration_seconds),
        "--change-ticket", args.change_ticket,
    ]
    for role, count, prefix in (
        ("xdp_runner", args.xdp_repeats, "xdp"),
        ("dpdk_runner", args.dpdk_repeats, "dpdk"),
    ):
        for repeat in range(1, count + 1):
            subprocess.run(
                [sys.executable, "-I", "-S", str(helpers[role]), *common,
                 "--run-id", "{}-{}".format(prefix, repeat),
                 "--repeat-index", str(repeat), "--output", str(run_dir / "{}_run_{}.json".format(prefix, repeat))],
                check=True,
                cwd=str(run_dir),
                env=_environment(),
            )
    for repeat in range(1, args.fallback_trials + 1):
        subprocess.run(
            [sys.executable, "-I", "-S", str(helpers["fallback_orchestrator"]),
             "--execution-plan", str(Path(args.execution_plan).resolve()),
             "--run-dir", str(run_dir), "--campaign-id", plan["campaign_id"],
             "--change-ticket", args.change_ticket, "--trial-id", "fallback-{}".format(repeat),
             "--repeat-index", str(repeat), "--xdp-run-id", "xdp-{}".format(repeat),
             "--dpdk-run-id", "dpdk-{}".format(repeat),
             "--packet-size", str(args.packet_size), "--offered-mpps", str(args.offered_mpps),
             "--duration-seconds", str(args.duration_seconds),
             "--output", str(run_dir / "fallback_trial_{}.json".format(repeat))],
            check=True,
            cwd=str(run_dir),
            env=_environment(),
        )


def _trust_root(args: argparse.Namespace) -> None:
    campaign_dir = Path(args.campaign_dir).resolve(strict=True)
    _verify_role(campaign_dir, "trust_root_recorder")
    if not CHANGE_RE.fullmatch(args.change_ticket) or not SHA_RE.fullmatch(args.sha256):
        raise HelperError("trust-root request is invalid")
    manifest = Path(args.manifest).resolve(strict=True)
    try:
        manifest.relative_to(campaign_dir)
    except ValueError as exc:
        raise HelperError("evidence manifest is outside campaign directory") from exc
    if _sha_bytes(_stable_bytes(manifest)) != args.sha256:
        raise HelperError("evidence manifest differs from requested trust root")
    output = Path(args.output).absolute()
    try:
        output.resolve(strict=False).relative_to(campaign_dir)
    except ValueError:
        pass
    else:
        raise HelperError("trust-root output must be outside campaign directory")
    _create_text(output, args.sha256 + "\n")


def _parser(role: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    if role in RUN_BACKENDS:
        parser.add_argument("--execution-plan", required=True)
        parser.add_argument("--run-dir", required=True)
        parser.add_argument("--campaign-id", required=True)
        parser.add_argument("--change-ticket", required=True)
        parser.add_argument("--run-id", required=True)
        parser.add_argument("--repeat-index", required=True, type=int)
        parser.add_argument("--packet-size", required=True, type=int)
        parser.add_argument("--offered-mpps", required=True, type=float)
        parser.add_argument("--duration-seconds", required=True, type=int)
        parser.add_argument("--output", required=True)
    elif role == "fallback_orchestrator":
        parser.add_argument("--execution-plan", required=True)
        parser.add_argument("--run-dir", required=True)
        parser.add_argument("--campaign-id", required=True)
        parser.add_argument("--change-ticket", required=True)
        parser.add_argument("--trial-id", required=True)
        parser.add_argument("--repeat-index", required=True, type=int)
        parser.add_argument("--xdp-run-id", required=True)
        parser.add_argument("--dpdk-run-id", required=True)
        parser.add_argument("--packet-size", required=True, type=int)
        parser.add_argument("--offered-mpps", required=True, type=float)
        parser.add_argument("--duration-seconds", required=True, type=int)
        parser.add_argument("--output", required=True)
    elif role == "restore_helper":
        parser.add_argument("--mode", required=True, choices=("snapshot-before", "restore", "snapshot-after"))
        parser.add_argument("--execution-plan", required=True)
        parser.add_argument("--change-ticket", required=True)
        parser.add_argument("--run-dir", required=True)
        parser.add_argument("--output")
    elif role == "campaign_executor":
        parser.add_argument("--contract", required=True)
        parser.add_argument("--execution-plan", required=True)
        parser.add_argument("--xdp-runner", required=True)
        parser.add_argument("--dpdk-runner", required=True)
        parser.add_argument("--generator-runner", required=True)
        parser.add_argument("--resource-sampler", required=True)
        parser.add_argument("--fallback-orchestrator", required=True)
        parser.add_argument("--arrival-evidence-manifest-sha256", required=True)
        parser.add_argument("--change-ticket", required=True)
        parser.add_argument("--run-dir", required=True)
        parser.add_argument("--packet-size", required=True, type=int)
        parser.add_argument("--offered-mpps", required=True, type=float)
        parser.add_argument("--duration-seconds", required=True, type=int)
        parser.add_argument("--xdp-repeats", required=True, type=int)
        parser.add_argument("--dpdk-repeats", required=True, type=int)
        parser.add_argument("--fallback-trials", required=True, type=int)
    elif role == "trust_root_recorder":
        parser.add_argument("--change-ticket", required=True)
        parser.add_argument("--campaign-dir", required=True)
        parser.add_argument("--manifest", required=True)
        parser.add_argument("--sha256", required=True)
        parser.add_argument("--output", required=True)
    else:
        parser.add_argument("--mode", choices=("identity",), default="identity")
        parser.add_argument("--run-dir", required=True)
    return parser


def main() -> int:
    role = Path(sys.argv[0]).name
    if role not in HELPER_ROLES:
        raise HelperError("helper basename does not select a frozen role: " + role)
    args = _parser(role).parse_args()
    if role in RUN_BACKENDS:
        _run_receipt(role, args)
    elif role == "fallback_orchestrator":
        _fallback(args)
    elif role == "restore_helper":
        if args.mode != "restore" and not args.output:
            raise HelperError("snapshot mode requires --output")
        _restore(args)
    elif role == "campaign_executor":
        _campaign(args)
    elif role == "trust_root_recorder":
        _trust_root(args)
    else:
        _verify_role(Path(args.run_dir).resolve(strict=True), role)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HelperError, OSError, ValueError, subprocess.SubprocessError) as error:
        print("{}: {}".format(Path(sys.argv[0]).name, error), file=sys.stderr)
        raise SystemExit(74)
