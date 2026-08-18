"""Read-only authoritative replay of an algorithm qualification campaign.

The formal campaign finalizer owns the validation rules for the frozen plan,
input hashes, raw repeats, run manifests, code manifests, result manifests,
candidate receipts, and the projected optimality audit.  This module invokes
that same finalizer while replacing its sole JSON writer with an in-memory
capture.  It then compares every would-be artifact with the already sealed
formal artifacts and proves that the campaign tree did not change.

No replay result is written to the campaign tree.  Callers may persist the
returned audit outside that tree if their own policy permits it.
"""

from __future__ import annotations

import builtins
import os
import stat
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

import hft_mgbs.algorithm_campaign as _campaign
from hft_mgbs.algorithm_campaign import (
    CampaignValidationError,
    _absolute_lexical,
    _assert_no_symlink_components,
    _directory_under,
    _mapping,
    _stable_file_bytes,
    _stable_file_hash_size,
    _strict_json_from_bytes,
    canonical_json_bytes,
    sha256_bytes,
)


REPLAY_SCOPE = "hft_mgbs_algorithm_qualification_campaign_raw_replay_v1"
FORMAL_RECEIPT_NAME = "campaign_receipt.json"
PROJECTION_NAME = "suggested_algorithm_search_projection.json"
EXPECTED_CANDIDATE_IDS = tuple("A{:02d}".format(index) for index in range(1, 11))
EXPECTED_INPUT_ENTRY_COUNT = 27
EXPECTED_RAW_REPEAT_COUNT = 10 * 2 * 3

# The replay temporarily replaces a module global used by the finalizer.  Keep
# that operation process-local and serialized so concurrent callers cannot see
# each other's capture function.
_REPLAY_LOCK = threading.RLock()


class AlgorithmCampaignReplayError(CampaignValidationError):
    """Raised when a sealed campaign cannot be replayed read-only."""


def _is_within(root: Path, value: object) -> bool:
    if isinstance(value, int):
        return False
    try:
        candidate = Path(os.fspath(value))
        # strict=False is necessary for attempted creates.  Existing parents
        # are still resolved, so a symlink cannot disguise a campaign child.
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
        return True
    except (OSError, RuntimeError, TypeError, ValueError):
        return False


@contextmanager
def _deny_campaign_writes(root: Path) -> Iterator[None]:
    """Reject Python filesystem mutations aimed anywhere below ``root``."""

    root = root.resolve(strict=True)
    original_path_open = Path.open
    original_write_bytes = Path.write_bytes
    original_write_text = Path.write_text
    original_mkdir = Path.mkdir
    original_touch = Path.touch
    original_unlink = Path.unlink
    original_rename = Path.rename
    original_replace = Path.replace
    original_chmod = Path.chmod
    original_rmdir = Path.rmdir
    original_symlink_to = Path.symlink_to
    original_builtin_open = builtins.open
    original_os_open = os.open
    original_os_mkdir = os.mkdir
    original_os_remove = os.remove
    original_os_unlink = os.unlink
    original_os_rename = os.rename
    original_os_replace = os.replace
    original_os_rmdir = os.rmdir
    original_os_chmod = os.chmod
    original_os_utime = os.utime
    original_os_truncate = os.truncate
    original_os_link = os.link
    original_os_symlink = os.symlink

    def deny(value: object) -> None:
        if _is_within(root, value):
            raise AlgorithmCampaignReplayError(
                "campaign write attempted during read-only replay: {}".format(value)
            )

    def path_open(path: Path, mode: str = "r", *args: object, **kwargs: object):
        if any(character in mode for character in "wax+"):
            deny(path)
        return original_path_open(path, mode, *args, **kwargs)

    def write_bytes(path: Path, data: bytes) -> int:
        deny(path)
        return original_write_bytes(path, data)

    def write_text(path: Path, data: str, *args: object, **kwargs: object) -> int:
        deny(path)
        return original_write_text(path, data, *args, **kwargs)

    def mkdir(path: Path, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_mkdir(path, *args, **kwargs)

    def touch(path: Path, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_touch(path, *args, **kwargs)

    def unlink(path: Path, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_unlink(path, *args, **kwargs)

    def rename(path: Path, target: object):
        deny(path)
        deny(target)
        return original_rename(path, target)

    def replace(path: Path, target: object):
        deny(path)
        deny(target)
        return original_replace(path, target)

    def chmod(path: Path, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_chmod(path, *args, **kwargs)

    def rmdir(path: Path) -> None:
        deny(path)
        return original_rmdir(path)

    def symlink_to(
        path: Path, target: object, *args: object, **kwargs: object
    ) -> None:
        deny(path)
        return original_symlink_to(path, target, *args, **kwargs)

    def builtin_open(
        path: object, mode: str = "r", *args: object, **kwargs: object
    ):
        if any(character in mode for character in "wax+"):
            deny(path)
        return original_builtin_open(path, mode, *args, **kwargs)

    def os_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        write_flags = (
            os.O_WRONLY
            | os.O_RDWR
            | os.O_CREAT
            | os.O_TRUNC
            | os.O_APPEND
        )
        if flags & write_flags:
            deny(path)
        return original_os_open(path, flags, *args, **kwargs)

    def os_mkdir(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_mkdir(path, *args, **kwargs)

    def os_remove(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_remove(path, *args, **kwargs)

    def os_unlink(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_unlink(path, *args, **kwargs)

    def os_rename(
        source: object, destination: object, *args: object, **kwargs: object
    ) -> None:
        deny(source)
        deny(destination)
        return original_os_rename(source, destination, *args, **kwargs)

    def os_replace(
        source: object, destination: object, *args: object, **kwargs: object
    ) -> None:
        deny(source)
        deny(destination)
        return original_os_replace(source, destination, *args, **kwargs)

    def os_rmdir(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_rmdir(path, *args, **kwargs)

    def os_chmod(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_chmod(path, *args, **kwargs)

    def os_utime(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_utime(path, *args, **kwargs)

    def os_truncate(path: object, *args: object, **kwargs: object) -> None:
        deny(path)
        return original_os_truncate(path, *args, **kwargs)

    def os_link(
        source: object, destination: object, *args: object, **kwargs: object
    ) -> None:
        deny(source)
        deny(destination)
        return original_os_link(source, destination, *args, **kwargs)

    def os_symlink(
        source: object, destination: object, *args: object, **kwargs: object
    ) -> None:
        deny(destination)
        return original_os_symlink(source, destination, *args, **kwargs)

    Path.open = path_open  # type: ignore[assignment]
    Path.write_bytes = write_bytes  # type: ignore[assignment]
    Path.write_text = write_text  # type: ignore[assignment]
    Path.mkdir = mkdir  # type: ignore[assignment]
    Path.touch = touch  # type: ignore[assignment]
    Path.unlink = unlink  # type: ignore[assignment]
    Path.rename = rename  # type: ignore[assignment]
    Path.replace = replace  # type: ignore[assignment]
    Path.chmod = chmod  # type: ignore[assignment]
    Path.rmdir = rmdir  # type: ignore[assignment]
    Path.symlink_to = symlink_to  # type: ignore[assignment]
    builtins.open = builtin_open  # type: ignore[assignment]
    os.open = os_open  # type: ignore[assignment]
    os.mkdir = os_mkdir  # type: ignore[assignment]
    os.remove = os_remove  # type: ignore[assignment]
    os.unlink = os_unlink  # type: ignore[assignment]
    os.rename = os_rename  # type: ignore[assignment]
    os.replace = os_replace  # type: ignore[assignment]
    os.rmdir = os_rmdir  # type: ignore[assignment]
    os.chmod = os_chmod  # type: ignore[assignment]
    os.utime = os_utime  # type: ignore[assignment]
    os.truncate = os_truncate  # type: ignore[assignment]
    os.link = os_link  # type: ignore[assignment]
    os.symlink = os_symlink  # type: ignore[assignment]
    try:
        yield
    finally:
        Path.open = original_path_open  # type: ignore[assignment]
        Path.write_bytes = original_write_bytes  # type: ignore[assignment]
        Path.write_text = original_write_text  # type: ignore[assignment]
        Path.mkdir = original_mkdir  # type: ignore[assignment]
        Path.touch = original_touch  # type: ignore[assignment]
        Path.unlink = original_unlink  # type: ignore[assignment]
        Path.rename = original_rename  # type: ignore[assignment]
        Path.replace = original_replace  # type: ignore[assignment]
        Path.chmod = original_chmod  # type: ignore[assignment]
        Path.rmdir = original_rmdir  # type: ignore[assignment]
        Path.symlink_to = original_symlink_to  # type: ignore[assignment]
        builtins.open = original_builtin_open  # type: ignore[assignment]
        os.open = original_os_open  # type: ignore[assignment]
        os.mkdir = original_os_mkdir  # type: ignore[assignment]
        os.remove = original_os_remove  # type: ignore[assignment]
        os.unlink = original_os_unlink  # type: ignore[assignment]
        os.rename = original_os_rename  # type: ignore[assignment]
        os.replace = original_os_replace  # type: ignore[assignment]
        os.rmdir = original_os_rmdir  # type: ignore[assignment]
        os.chmod = original_os_chmod  # type: ignore[assignment]
        os.utime = original_os_utime  # type: ignore[assignment]
        os.truncate = original_os_truncate  # type: ignore[assignment]
        os.link = original_os_link  # type: ignore[assignment]
        os.symlink = original_os_symlink  # type: ignore[assignment]


def _regular_canonical_json(path: Path, name: str) -> Tuple[Mapping[str, object], bytes, str]:
    raw = _stable_file_bytes(path, name)
    payload = _mapping(_strict_json_from_bytes(raw, name), name)
    if raw != canonical_json_bytes(payload):
        raise AlgorithmCampaignReplayError("{} is not canonical JSON".format(name))
    return payload, raw, sha256_bytes(raw)


def _tree_snapshot(root: Path) -> Tuple[Dict[str, object], Tuple[Tuple[object, ...], ...]]:
    """Hash a campaign tree without following links or accepting special files."""

    root = _assert_no_symlink_components(root, "campaign replay root")
    if not root.is_dir():
        raise AlgorithmCampaignReplayError("campaign replay root is not a directory")
    records: List[Tuple[object, ...]] = []

    def walk(directory: Path, relative: str) -> None:
        directory_status = os.lstat(str(directory))
        if not stat.S_ISDIR(directory_status.st_mode):
            raise AlgorithmCampaignReplayError(
                "campaign tree directory changed type: {}".format(relative or ".")
            )
        records.append(
            (
                relative or ".",
                "directory",
                directory_status.st_dev,
                directory_status.st_ino,
                stat.S_IMODE(directory_status.st_mode),
                directory_status.st_size,
                directory_status.st_mtime_ns,
            )
        )
        try:
            entries = sorted(os.scandir(str(directory)), key=lambda item: item.name)
        except OSError as error:
            raise AlgorithmCampaignReplayError(
                "cannot enumerate campaign tree: {}".format(relative or ".")
            ) from error
        for entry in entries:
            if any(character in entry.name for character in "\r\n\x00"):
                raise AlgorithmCampaignReplayError("unsafe campaign tree entry name")
            child = directory / entry.name
            child_relative = entry.name if not relative else relative + "/" + entry.name
            child_status = os.lstat(str(child))
            if stat.S_ISLNK(child_status.st_mode):
                raise AlgorithmCampaignReplayError(
                    "campaign tree contains a symlink: {}".format(child_relative)
                )
            if stat.S_ISDIR(child_status.st_mode):
                walk(child, child_relative)
                continue
            if not stat.S_ISREG(child_status.st_mode):
                raise AlgorithmCampaignReplayError(
                    "campaign tree contains a special file: {}".format(child_relative)
                )
            if child_status.st_nlink != 1:
                raise AlgorithmCampaignReplayError(
                    "campaign tree contains a multiply-linked file: {}".format(
                        child_relative
                    )
                )
            digest, size = _stable_file_hash_size(child, "campaign tree file")
            current = os.lstat(str(child))
            identity_before = (
                child_status.st_dev,
                child_status.st_ino,
                child_status.st_size,
                child_status.st_mtime_ns,
            )
            identity_after = (
                current.st_dev,
                current.st_ino,
                current.st_size,
                current.st_mtime_ns,
            )
            if identity_before != identity_after or not stat.S_ISREG(current.st_mode):
                raise AlgorithmCampaignReplayError(
                    "campaign tree file changed during snapshot: {}".format(
                        child_relative
                    )
                )
            records.append(
                (
                    child_relative,
                    "file",
                    current.st_dev,
                    current.st_ino,
                    stat.S_IMODE(current.st_mode),
                    size,
                    current.st_mtime_ns,
                    digest,
                )
            )

    walk(root, "")
    frozen = tuple(records)
    encoded = canonical_json_bytes([list(record) for record in frozen])
    summary = {
        "entry_count": len(frozen),
        "sha256": sha256_bytes(encoded),
    }
    return summary, frozen


def _exact_child(root: Path, value: object, expected: Path, name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise AlgorithmCampaignReplayError("{} path is missing".format(name))
    candidate = _assert_no_symlink_components(Path(value), name)
    candidate = _directory_safe_file(root, candidate, name)
    _assert_no_symlink_components(expected, name)
    expected_absolute = expected.resolve(strict=True)
    if candidate != expected_absolute:
        raise AlgorithmCampaignReplayError("{} path is not exact".format(name))
    return candidate


def _directory_safe_file(root: Path, candidate: Path, name: str) -> Path:
    root_absolute = _assert_no_symlink_components(
        root, "campaign replay root"
    ).resolve(strict=True)
    candidate_absolute = _assert_no_symlink_components(
        candidate, name
    ).resolve(strict=True)
    try:
        candidate_absolute.relative_to(root_absolute)
    except ValueError as error:
        raise AlgorithmCampaignReplayError("{} escapes campaign root".format(name)) from error
    if not candidate_absolute.is_file():
        raise AlgorithmCampaignReplayError("{} is not a regular file".format(name))
    return candidate_absolute


def _formal_paths(
    campaign_root: Path,
    formal_receipt_path: Path,
    formal_receipt: Mapping[str, object],
) -> Tuple[Path, Dict[str, Path]]:
    root = _directory_under(campaign_root, campaign_root, "campaign replay directory")
    formal_path = _exact_child(
        root,
        str(formal_receipt_path),
        root / "receipts" / FORMAL_RECEIPT_NAME,
        "formal campaign receipt",
    )
    projection_reference = _mapping(
        formal_receipt.get("suggested_algorithm_search_projection"),
        "formal receipt projection reference",
    )
    projection_path = _exact_child(
        root,
        projection_reference.get("path"),
        root / PROJECTION_NAME,
        "formal algorithm projection",
    )
    candidate_references = formal_receipt.get("candidate_receipts")
    if not isinstance(candidate_references, list) or len(candidate_references) != 10:
        raise AlgorithmCampaignReplayError("formal receipt candidate set is incomplete")
    candidates: Dict[str, Path] = {}
    for raw_reference in candidate_references:
        reference = _mapping(raw_reference, "formal candidate receipt reference")
        candidate_id = reference.get("candidate_id")
        if candidate_id not in EXPECTED_CANDIDATE_IDS or candidate_id in candidates:
            raise AlgorithmCampaignReplayError(
                "formal receipt has invalid or duplicate candidate identity"
            )
        path = _exact_child(
            root,
            reference.get("path"),
            root / "receipts" / "{}.json".format(candidate_id),
            "candidate {} receipt".format(candidate_id),
        )
        _payload, _raw, actual_hash = _regular_canonical_json(
            path, "candidate {} receipt".format(candidate_id)
        )
        if reference.get("sha256") != actual_hash:
            raise AlgorithmCampaignReplayError(
                "candidate {} receipt reference hash drift".format(candidate_id)
            )
        candidates[str(candidate_id)] = path
    if tuple(sorted(candidates)) != EXPECTED_CANDIDATE_IDS:
        raise AlgorithmCampaignReplayError("formal receipt candidate identities are not exact")
    _projection, _projection_raw, projection_hash = _regular_canonical_json(
        projection_path, "formal algorithm projection"
    )
    if projection_reference.get("sha256") != projection_hash:
        raise AlgorithmCampaignReplayError("formal projection reference hash drift")
    input_reference = _mapping(
        formal_receipt.get("input_hash_manifest"), "formal input hash manifest"
    )
    _exact_child(
        root,
        input_reference.get("path"),
        root / "input_sha256.json",
        "formal input hash manifest",
    )
    return projection_path, candidates


def _compare_captured(
    paths: Sequence[Path], captured: Mapping[str, Tuple[bytes, Mapping[str, object]]]
) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    for path in paths:
        key = str(_absolute_lexical(path))
        generated = captured.get(key)
        if generated is None:
            raise AlgorithmCampaignReplayError(
                "finalizer did not regenerate {}".format(path.name)
            )
        generated_raw, generated_payload = generated
        actual_payload, actual_raw, actual_hash = _regular_canonical_json(
            path, "sealed replay artifact"
        )
        if actual_payload != generated_payload:
            raise AlgorithmCampaignReplayError(
                "sealed artifact field drift: {}".format(path.name)
            )
        generated_hash = sha256_bytes(generated_raw)
        if actual_hash != generated_hash or actual_raw != generated_raw:
            raise AlgorithmCampaignReplayError(
                "sealed artifact canonical SHA-256 drift: {}".format(path.name)
            )
        hashes[key] = actual_hash
    if set(captured) != set(hashes):
        unexpected = sorted(set(captured) - set(hashes))
        missing = sorted(set(hashes) - set(captured))
        raise AlgorithmCampaignReplayError(
            "finalizer write set is not exact; unexpected={}, missing={}".format(
                unexpected, missing
            )
        )
    return hashes


def _run_replay(
    repo_root: Path,
    contract_path: Path,
    campaign_root: Path,
    formal_receipt_path: Path,
    search_path: Optional[Path],
) -> Dict[str, object]:
    campaign_root = _directory_under(
        campaign_root, campaign_root, "campaign replay directory"
    )
    formal_receipt_path = _assert_no_symlink_components(
        formal_receipt_path, "formal campaign receipt"
    ).resolve(strict=True)
    formal_receipt, _formal_raw, formal_sha = _regular_canonical_json(
        formal_receipt_path, "formal campaign receipt"
    )
    projection_path, candidate_paths = _formal_paths(
        campaign_root, formal_receipt_path, formal_receipt
    )
    expected_paths = [candidate_paths[name] for name in EXPECTED_CANDIDATE_IDS]
    expected_paths.extend([projection_path, formal_receipt_path])
    allowed = {str(path.resolve(strict=True)) for path in expected_paths}
    captured: Dict[str, Tuple[bytes, Mapping[str, object]]] = {}

    def capture_json(path: Path, value: object) -> str:
        # All expected destinations already exist in a sealed campaign, so
        # resolving here normalizes platform aliases without creating files.
        absolute = str(
            _assert_no_symlink_components(path, "captured output path").resolve(
                strict=True
            )
        )
        if absolute not in allowed:
            raise AlgorithmCampaignReplayError(
                "finalizer attempted an unexpected write: {}".format(absolute)
            )
        if absolute in captured:
            raise AlgorithmCampaignReplayError(
                "finalizer attempted a duplicate write: {}".format(absolute)
            )
        payload = _mapping(value, "captured finalizer artifact")
        raw = canonical_json_bytes(payload)
        # Decode a fresh immutable-equivalent structure so later mutation of a
        # finalizer-owned dictionary cannot change what was captured.
        frozen_payload = _mapping(
            _strict_json_from_bytes(raw, "captured finalizer artifact"),
            "captured finalizer artifact",
        )
        captured[absolute] = (raw, frozen_payload)
        return sha256_bytes(raw)

    with _REPLAY_LOCK:
        original_writer = _campaign.write_json_atomic
        _campaign.write_json_atomic = capture_json
        try:
            with _deny_campaign_writes(campaign_root):
                regenerated = _campaign.finalize_campaign(
                    repo_root,
                    contract_path,
                    campaign_root,
                    formal_receipt_path,
                    projection_path,
                    search_path,
                    formal_receipt.get("external_trust_root_sha256"),
                )
        finally:
            _campaign.write_json_atomic = original_writer

    regenerated_errors = regenerated.get("errors")
    if regenerated_errors != []:
        raise AlgorithmCampaignReplayError(
            "finalizer raw replay failed: {}".format(regenerated_errors)
        )
    hashes = _compare_captured(expected_paths, captured)
    if regenerated != captured[str(formal_receipt_path)][1]:
        raise AlgorithmCampaignReplayError(
            "finalizer return value differs from regenerated formal receipt"
        )
    input_manifest = _mapping(
        regenerated.get("input_hash_manifest"), "regenerated input hash manifest"
    )
    if input_manifest.get("entry_count") != EXPECTED_INPUT_ENTRY_COUNT:
        raise AlgorithmCampaignReplayError("input manifest does not contain exactly 27 paths")
    if regenerated.get("expected_candidate_count") != 10 or regenerated.get(
        "evaluated_candidate_count"
    ) != 10:
        raise AlgorithmCampaignReplayError("regenerated evaluated candidate count is not 10")
    feasible_count = regenerated.get("feasible_candidate_count")
    qualified_count = regenerated.get("qualified_candidate_count")
    if (
        not isinstance(feasible_count, int)
        or isinstance(feasible_count, bool)
        or not 0 <= feasible_count <= 10
        or qualified_count != feasible_count
    ):
        raise AlgorithmCampaignReplayError(
            "regenerated feasible/qualified candidate accounting is invalid"
        )
    if regenerated.get("campaign_evidence_complete") is not True:
        raise AlgorithmCampaignReplayError("regenerated campaign evidence is incomplete")

    raw_repeat_count = 0
    for candidate_id in EXPECTED_CANDIDATE_IDS:
        candidate = captured[str(candidate_paths[candidate_id])][1]
        if candidate.get("candidate_id") != candidate_id:
            raise AlgorithmCampaignReplayError("candidate identity drift")
        if candidate.get("campaign_id") != regenerated.get("campaign_id") or candidate.get(
            "campaign_run_id"
        ) != regenerated.get("campaign_run_id"):
            raise AlgorithmCampaignReplayError("candidate campaign identity drift")
        mode_contract = _mapping(candidate.get("mode_contract"), "candidate mode contract")
        if mode_contract.get("repeat_seeds_by_mode") != {
            "normal": [7, 11, 19],
            "fallback": [7, 11, 19],
        }:
            raise AlgorithmCampaignReplayError("candidate seed matrix drift")
        evidence_files = candidate.get("evidence_files")
        if not isinstance(evidence_files, list) or len(evidence_files) != 7:
            raise AlgorithmCampaignReplayError("candidate evidence file set is incomplete")
        raw_repeat_count += sum(
            1
            for item in evidence_files
            if isinstance(item, Mapping)
            and isinstance(item.get("path"), str)
            and (
                Path(str(item["path"])).name.startswith("normal_repeat")
                or Path(str(item["path"])).name.startswith("fallback_repeat")
            )
        )
    if raw_repeat_count != EXPECTED_RAW_REPEAT_COUNT:
        raise AlgorithmCampaignReplayError("raw repeat matrix is not exactly 10x2x3")
    projection = captured[str(projection_path)][1]
    selected_candidate = projection.get("selected_candidate")
    if regenerated.get("accepted") is True and selected_candidate not in EXPECTED_CANDIDATE_IDS:
        raise AlgorithmCampaignReplayError(
            "accepted formal campaign has no exact selected candidate"
        )
    environment_identity = _mapping(
        regenerated.get("environment_identity"),
        "regenerated environment identity",
    )
    environment_files = _mapping(
        environment_identity.get("environment_files_manifest"),
        "regenerated environment files manifest",
    )
    external_tools = _mapping(
        environment_identity.get("external_tools_manifest"),
        "regenerated external tools manifest",
    )
    runtime_bootstrap = _mapping(
        environment_identity.get("runtime_bootstrap_identity"),
        "regenerated runtime bootstrap identity",
    )
    environment_identity_path = campaign_root / "environment_identity.json"
    environment_identity_raw = _stable_file_bytes(
        environment_identity_path, "sealed environment identity"
    )
    environment_identity_payload = _mapping(
        _strict_json_from_bytes(
            environment_identity_raw, "sealed environment identity"
        ),
        "sealed environment identity",
    )
    if sha256_bytes(environment_identity_raw) != environment_identity.get("sha256"):
        raise AlgorithmCampaignReplayError(
            "sealed environment identity SHA-256 drift"
        )
    python_identity = _mapping(
        environment_identity_payload.get("python"),
        "sealed Python identity",
    )
    first_candidate = captured[str(candidate_paths[EXPECTED_CANDIDATE_IDS[0]])][1]
    input_stat_identity = _mapping(
        first_candidate.get("input_stat_identity"),
        "regenerated input stat identity",
    )

    return {
        "formal_receipt_sha256": formal_sha,
        "campaign_id": regenerated.get("campaign_id"),
        "campaign_run_id": regenerated.get("campaign_run_id"),
        "contract_sha256": regenerated.get("contract_sha256"),
        "algorithm_search_sha256": regenerated.get("algorithm_search_sha256"),
        "environment_identity_sha256": environment_identity.get("sha256"),
        "environment_prefix": environment_identity.get("environment_prefix"),
        "python_executable": python_identity.get("executable"),
        "python_executable_sha256": python_identity.get("executable_sha256"),
        "python_site_packages": python_identity.get("site_packages"),
        "environment_files_manifest_sha256": environment_files.get("sha256"),
        "external_tools_manifest_sha256": external_tools.get("sha256"),
        "runtime_bootstrap_identity_sha256": runtime_bootstrap.get("sha256"),
        "input_stat_identity_sha256": input_stat_identity.get("sha256"),
        "input_manifest_entry_count": input_manifest.get("entry_count"),
        "candidate_count": 10,
        "evaluated_candidate_count": regenerated.get(
            "evaluated_candidate_count"
        ),
        "feasible_candidate_count": feasible_count,
        "qualified_candidate_count": qualified_count,
        "mode_count": 2,
        "repeats_per_mode": 3,
        "raw_repeat_count": raw_repeat_count,
        "regenerated_artifact_count": len(hashes),
        "formal_algorithm_only_accepted": regenerated.get("accepted") is True,
        "selected_candidate": selected_candidate,
    }


def verify_algorithm_campaign_raw_replay(
    repo_root: Path,
    contract_path: Path,
    campaign_root: Path,
    formal_receipt_path: Path,
    search_path: Optional[Path] = None,
) -> Dict[str, object]:
    """Replay a sealed campaign without writing it and return a fail-closed audit."""

    before_summary: Optional[Dict[str, object]] = None
    before_records: Optional[Tuple[Tuple[object, ...], ...]] = None
    after_summary: Optional[Dict[str, object]] = None
    after_records: Optional[Tuple[Tuple[object, ...], ...]] = None
    details: Dict[str, object] = {}
    errors: List[str] = []
    try:
        before_summary, before_records = _tree_snapshot(campaign_root)
        details = _run_replay(
            repo_root,
            contract_path,
            campaign_root,
            formal_receipt_path,
            search_path,
        )
    except (
        OSError,
        UnicodeError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
        CampaignValidationError,
    ) as error:
        errors.append("{}:{}".format(type(error).__name__, error))
    finally:
        if before_records is not None:
            try:
                after_summary, after_records = _tree_snapshot(campaign_root)
            except (
                OSError,
                UnicodeError,
                RuntimeError,
                TypeError,
                ValueError,
                CampaignValidationError,
            ) as error:
                errors.append("tree_after:{}:{}".format(type(error).__name__, error))
            else:
                if before_records != after_records:
                    errors.append("campaign_tree_changed_during_raw_replay")

    tree_unchanged = (
        before_records is not None
        and after_records is not None
        and before_records == after_records
    )
    complete = not errors and tree_unchanged and bool(details)
    return {
        "schema_version": 1,
        "scope": REPLAY_SCOPE,
        "campaign_id": details.get("campaign_id"),
        "campaign_run_id": details.get("campaign_run_id"),
        "contract_sha256": details.get("contract_sha256"),
        "algorithm_search_sha256": details.get("algorithm_search_sha256"),
        "environment_identity_sha256": details.get(
            "environment_identity_sha256"
        ),
        "environment_prefix": details.get("environment_prefix"),
        "python_executable": details.get("python_executable"),
        "python_executable_sha256": details.get("python_executable_sha256"),
        "python_site_packages": details.get("python_site_packages"),
        "environment_files_manifest_sha256": details.get(
            "environment_files_manifest_sha256"
        ),
        "external_tools_manifest_sha256": details.get(
            "external_tools_manifest_sha256"
        ),
        "runtime_bootstrap_identity_sha256": details.get(
            "runtime_bootstrap_identity_sha256"
        ),
        "input_stat_identity_sha256": details.get(
            "input_stat_identity_sha256"
        ),
        "formal_receipt": {
            "path": str(_absolute_lexical(formal_receipt_path)),
            "sha256": details.get("formal_receipt_sha256"),
        },
        "campaign_tree_before": before_summary,
        "campaign_tree_after": after_summary,
        "campaign_tree_unchanged": tree_unchanged,
        "input_manifest_entry_count": details.get("input_manifest_entry_count"),
        "candidate_count": details.get("candidate_count", 0),
        "evaluated_candidate_count": details.get("evaluated_candidate_count", 0),
        "feasible_candidate_count": details.get("feasible_candidate_count", 0),
        "qualified_candidate_count": details.get("qualified_candidate_count", 0),
        "mode_count": details.get("mode_count", 0),
        "repeats_per_mode": details.get("repeats_per_mode", 0),
        "raw_repeat_count": details.get("raw_repeat_count", 0),
        "regenerated_artifact_count": details.get("regenerated_artifact_count", 0),
        "formal_algorithm_only_accepted": details.get(
            "formal_algorithm_only_accepted", False
        ),
        "selected_candidate": details.get("selected_candidate"),
        "candidate_receipts_match_raw_replay": complete,
        "projection_matches_raw_replay": complete,
        "formal_receipt_matches_raw_replay": complete,
        "authoritative_raw_replay_complete": complete,
        "accepted": complete,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
        "writes_campaign_tree": False,
        "errors": sorted(set(errors)),
    }


__all__ = [
    "AlgorithmCampaignReplayError",
    "REPLAY_SCOPE",
    "verify_algorithm_campaign_raw_replay",
]
