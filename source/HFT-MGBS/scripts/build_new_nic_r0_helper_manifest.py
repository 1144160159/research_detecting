#!/usr/bin/env python3
"""Create a review candidate for the externally approved R0 helper manifest.

This tool is not an approver.  Its output still has to be pinned by an
independent approval record and trust receipt before the trust-profile
finalizer will accept it.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import tempfile
from pathlib import Path


HELPER_ROLES = (
    "xdp_runner", "dpdk_runner", "generator_runner", "resource_sampler",
    "fallback_orchestrator", "restore_helper", "campaign_executor", "trust_root_recorder",
)
CORE_PATHS = {
    "contract": Path("configs/new_nic_r0_campaign_contract_v1.json"),
    "runner": Path("scripts/run_new_nic_r0_campaign.sh"),
    "composer": Path("scripts/compose_new_nic_r0_acceptance.py"),
    "evaluator": Path("hft_mgbs/new_nic_r0.py"),
}


def stable_sha256(path: Path) -> str:
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink component rejected: " + str(path))
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    digest = hashlib.sha256()
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError("single-link regular artifact required: " + str(path))
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(1024 * 1024, remaining))
            if not block:
                raise ValueError("short read: " + str(path))
            digest.update(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise ValueError("artifact grew during read: " + str(path))
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda item: (
        item.st_dev, item.st_ino, item.st_mode, item.st_nlink, item.st_size,
        item.st_mtime_ns, item.st_ctime_ns,
    )
    if identity(before) != identity(after):
        raise ValueError("artifact changed during read: " + str(path))
    return digest.hexdigest()


def build_manifest(repo_root: Path, output: Path) -> str:
    root = repo_root.resolve(strict=True)
    artifacts = dict(CORE_PATHS)
    artifacts.update({
        role: Path("scripts/new_nic_helpers") / role for role in HELPER_ROLES
    })
    template = root / "scripts/new_nic_helpers/_template.py"
    template_sha = stable_sha256(template)
    rows = []
    for role, relative in sorted(artifacts.items()):
        path = (root / relative).absolute()
        path.resolve(strict=True).relative_to(root)
        digest = stable_sha256(path)
        if role in HELPER_ROLES and digest != template_sha:
            raise ValueError("helper is not a byte-identical frozen role copy: " + role)
        rows.append("{} {} {}".format(role, path, digest))
    raw = ("\n".join(rows) + "\n").encode("utf-8")
    if output.exists() or output.is_symlink():
        raise ValueError("helper manifest output must be new")
    parent = output.parent.resolve(strict=True)
    descriptor, temporary_raw = tempfile.mkstemp(prefix=output.name + ".", suffix=".tmp", dir=str(parent))
    temporary = Path(temporary_raw)
    created = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if output.exists() or output.is_symlink():
            raise ValueError("helper manifest output raced")
        os.link(str(temporary), str(output))
        created = True
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    if created:
        os.chmod(str(output), 0o400 if os.name != "nt" else 0o600)
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        digest = build_manifest(args.repo_root, args.output)
    except (OSError, ValueError) as error:
        print("helper manifest rejected: {}".format(error))
        return 74
    print("helper_manifest_sha256={}".format(digest))
    print("external_approval_required=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
