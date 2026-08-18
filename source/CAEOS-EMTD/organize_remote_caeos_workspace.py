from __future__ import annotations

import argparse
import json
import os
import signal
import time
from pathlib import Path
from typing import Any


BASE = Path("/opt/data/private/wangwt/ParkAttackKE")
CANONICAL = BASE / "CAEOS-EMTD"
STAGING = BASE / ".CAEOS-EMTD-unified-staging-20260729"
ACTIVE_NAMES = {
    "CAEOS-EMTD-strict-v4-20260717",
    "CAEOS-EMTD-selected-system-staging-20260727",
}
RELEASES_NAME = "CAEOS-EMTD-releases"
CURRENT_NAME = "CAEOS-EMTD-current"
DEPLOY_ARCHIVE_NAME = "CAEOS-EMTD-deploy.tar.gz"


def classify_destination(entry: Path) -> Path:
    if entry.name == CANONICAL.name:
        return STAGING / "legacy" / "CAEOS-EMTD-original"
    if entry.name == RELEASES_NAME:
        return STAGING / "releases"
    if entry.name == CURRENT_NAME:
        return STAGING / "aliases_previous" / entry.name
    if entry.name == DEPLOY_ARCHIVE_NAME:
        return STAGING / "legacy" / "artifacts" / entry.name
    if entry.name in ACTIVE_NAMES:
        return STAGING / "active" / entry.name
    return STAGING / "legacy" / entry.name


def matching_processes() -> list[dict[str, Any]]:
    roots = [str(BASE / name) for name in sorted(ACTIVE_NAMES)]
    matches: list[dict[str, Any]] = []
    own_pid = os.getpid()
    for proc_path in Path("/proc").iterdir():
        if not proc_path.name.isdigit():
            continue
        pid = int(proc_path.name)
        if pid == own_pid:
            continue
        try:
            command = (
                (proc_path / "cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode("utf-8", errors="replace")
                .strip()
            )
            cwd = os.readlink(proc_path / "cwd")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if any(root in command or cwd.startswith(root) for root in roots):
            matches.append({"pid": pid, "command": command, "cwd": cwd})
    return sorted(matches, key=lambda item: item["pid"])


def build_plan() -> dict[str, Any]:
    entries = sorted(BASE.glob("CAEOS-EMTD*"), key=lambda path: path.name)
    if STAGING.exists():
        raise RuntimeError(f"staging path already exists: {STAGING}")
    required = {
        CANONICAL,
        BASE / RELEASES_NAME,
        BASE / CURRENT_NAME,
        *(BASE / name for name in ACTIVE_NAMES),
    }
    missing = sorted(str(path) for path in required if not path.exists())
    if missing:
        raise RuntimeError(f"required source paths are missing: {missing}")

    current_target = (BASE / CURRENT_NAME).resolve(strict=True)
    release_root = (BASE / RELEASES_NAME).resolve(strict=True)
    if current_target.parent != release_root:
        raise RuntimeError("current does not resolve to a direct release child")

    devices = {
        entry.lstat().st_dev
        for entry in entries
        if entry.exists() or entry.is_symlink()
    }
    if len(devices) != 1:
        raise RuntimeError("source entries are not on one filesystem")

    moves = [
        {
            "source": str(entry),
            "destination": str(classify_destination(entry)),
            "kind": (
                "symlink"
                if entry.is_symlink()
                else "directory"
                if entry.is_dir()
                else "file"
            ),
        }
        for entry in entries
    ]
    return {
        "schema_version": "caeos_remote_workspace_migration_v1",
        "policy": "zero_delete_move_only",
        "base": str(BASE),
        "canonical": str(CANONICAL),
        "staging": str(STAGING),
        "current_release_name": current_target.name,
        "moves": moves,
        "active_processes": matching_processes(),
        "compatibility_links": {
            str(BASE / CURRENT_NAME): str(CANONICAL / "current"),
            **{
                str(BASE / name): str(CANONICAL / "active" / name)
                for name in sorted(ACTIVE_NAMES)
            },
        },
    }


def write_workspace_readme(root: Path) -> None:
    (root / "README_UNIFIED_WORKSPACE.md").write_text(
        "\n".join(
            [
                "# Unified CAEOS-EMTD GPU Workspace",
                "",
                "- `current`: validated release used by new experiments.",
                "- `releases`: immutable validated source releases.",
                "- `active`: workspaces still referenced by running watchers.",
                "- `legacy`: all inactive historical code, runs, caches, and archives.",
                "- `aliases_previous`: preserved pre-migration symlink objects.",
                "",
                "No source, result, cache, release, or archive was deleted during",
                "the 2026-07-29 consolidation. Top-level compatibility symlinks",
                "remain only for running processes and the previous current path.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def create_compatibility_links() -> None:
    links = {
        BASE / CURRENT_NAME: CANONICAL / "current",
        **{
            BASE / name: CANONICAL / "active" / name
            for name in sorted(ACTIVE_NAMES)
        },
    }
    for link, target in links.items():
        if link.exists() or link.is_symlink():
            continue
        if target.exists() or target.is_symlink():
            link.symlink_to(target, target_is_directory=True)


def execute_plan(plan: dict[str, Any]) -> None:
    stopped: list[int] = []
    STAGING.mkdir()
    for relative in (
        "active",
        "aliases_previous",
        "legacy",
        "legacy/artifacts",
    ):
        (STAGING / relative).mkdir(parents=True, exist_ok=True)
    (STAGING / "MIGRATION_PLAN.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    try:
        for _ in range(3):
            known = set(stopped)
            new_processes = [
                process
                for process in matching_processes()
                if int(process["pid"]) not in known
            ]
            if not new_processes:
                break
            for process in new_processes:
                pid = int(process["pid"])
                try:
                    os.kill(pid, signal.SIGSTOP)
                    stopped.append(pid)
                except ProcessLookupError:
                    continue
            time.sleep(0.5)

        for move in plan["moves"]:
            source = Path(move["source"])
            destination = Path(move["destination"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.rename(source, destination)

        os.rename(STAGING, CANONICAL)
        release_name = str(plan["current_release_name"])
        (CANONICAL / "current").symlink_to(
            Path("releases") / release_name,
            target_is_directory=True,
        )
        create_compatibility_links()
        write_workspace_readme(CANONICAL)
        (CANONICAL / "WORKSPACE_PATH_MAP.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    finally:
        create_compatibility_links()
        for pid in stopped:
            try:
                os.kill(pid, signal.SIGCONT)
            except ProcessLookupError:
                continue


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consolidate all CAEOS-EMTD-prefixed entries without deletion."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="perform the move-only migration; default is a dry run",
    )
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    plan = build_plan()
    rendered = json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if args.execute:
        execute_plan(plan)


if __name__ == "__main__":
    main()
