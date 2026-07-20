"""Collect a fixed HTTP manifest on the GPU server.

The manifest is intentionally small and lives with the source code.  Archives,
resolved metadata and runtime state are written only below ``--root``.  Direct
file lists and stable Apache auto-index pages are supported without third-party
Python packages.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath
from threading import Lock
from typing import Any, Callable
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

try:  # Script execution from ``scripts/``.
    from collect_zenodo_dataset import atomic_json, digest_file, utc_now
except ModuleNotFoundError:  # Import as ``scripts.collect_http_manifest`` in tests.
    from scripts.collect_zenodo_dataset import atomic_json, digest_file, utc_now


USER_AGENT = "EACR-APT-dataset-collector/1.0"
APACHE_ROW = re.compile(
    r'href=["\'](?P<href>[^"\']+)["\'][^>]*>.*?</a>'
    r"\s+\d{2}-[A-Za-z]{3}-\d{4}\s+\d{2}:\d{2}\s+(?P<size>\d+)",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path, help="GPU-only dataset root")
    parser.add_argument("--connections", type=int, default=2)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument(
        "--proxy",
        default=os.environ.get("EACR_DATASET_PROXY"),
        help="Optional socks5:// or socks5h:// proxy; credentials are never persisted",
    )
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def safe_name(value: str) -> str:
    """Return a normalized relative POSIX path or reject path traversal."""

    candidate = PurePosixPath(value.replace("\\", "/"))
    if not value or candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe manifest filename: {value!r}")
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        raise ValueError(f"Unsafe manifest filename: {value!r}")
    return normalized


def validate_proxy(proxy: str | None) -> str | None:
    if not proxy:
        return None
    parsed = urlparse(proxy)
    if parsed.scheme not in {"socks5", "socks5h", "http", "https"} or not parsed.hostname:
        raise ValueError("--proxy must be socks5[h]://HOST:PORT or http[s]://HOST:PORT")
    return proxy


def redacted_proxy(proxy: str | None) -> dict[str, Any]:
    if not proxy:
        return {"configured": False}
    parsed = urlparse(proxy)
    return {
        "configured": True,
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
    }


def fetch_text(url: str, proxy: str | None = None) -> str:
    """Fetch index metadata, using curl when a SOCKS proxy is requested."""

    if proxy and urlparse(proxy).scheme in {"socks5", "socks5h"}:
        result = subprocess.run(
            [
                "curl",
                "--fail",
                "--silent",
                "--show-error",
                "--location",
                "--connect-timeout",
                "30",
                "--max-time",
                "120",
                "--proxy",
                proxy,
                "--user-agent",
                USER_AGENT,
                url,
            ],
            check=True,
            capture_output=True,
        )
        return result.stdout.decode("utf-8", errors="replace")
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_apache_index(
    page: str,
    base_url: str,
    path_prefix: str = "",
    include_regex: str = r".*",
) -> list[dict[str, Any]]:
    """Resolve filename, URL and exact bytes from a standard Apache index."""

    include = re.compile(include_regex)
    prefix = safe_name(path_prefix) if path_prefix else ""
    files: list[dict[str, Any]] = []
    for match in APACHE_ROW.finditer(page):
        href = html.unescape(match.group("href"))
        parsed = urlparse(href)
        leaf = unquote(PurePosixPath(parsed.path).name)
        if not leaf or leaf in {".", ".."} or not include.search(leaf):
            continue
        name = safe_name(f"{prefix}/{leaf}" if prefix else leaf)
        files.append(
            {
                "name": name,
                "url": urljoin(base_url, href),
                "expected_bytes": int(match.group("size")),
            }
        )
    return files


def _validate_file(item: dict[str, Any]) -> dict[str, Any]:
    name = safe_name(str(item.get("name", "")))
    url = str(item.get("url", ""))
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Unsupported URL for {name!r}: {url!r}")
    expected_bytes = int(item.get("expected_bytes", 0))
    if expected_bytes <= 0:
        raise ValueError(f"expected_bytes must be positive for {name!r}")
    normalized = {"name": name, "url": url, "expected_bytes": expected_bytes}
    checksum = item.get("checksum")
    if checksum:
        algorithm, separator, digest = str(checksum).partition(":")
        if not separator or not algorithm or not digest:
            raise ValueError(f"Checksum must use algorithm:hex for {name!r}")
        hashlib.new(algorithm.lower())
        normalized["checksum"] = f"{algorithm.lower()}:{digest.lower()}"
    magic_hex = item.get("magic_hex")
    if magic_hex:
        try:
            bytes.fromhex(str(magic_hex))
        except ValueError as exc:
            raise ValueError(f"magic_hex must contain hexadecimal bytes for {name!r}") from exc
        normalized["magic_hex"] = str(magic_hex).lower()
    return normalized


def resolve_manifest(
    manifest: dict[str, Any],
    proxy: str | None = None,
    fetcher: Callable[[str, str | None], str] = fetch_text,
) -> dict[str, Any]:
    """Expand index sources and enforce file-count and byte invariants."""

    if int(manifest.get("schema_version", 0)) != 1:
        raise ValueError("Only HTTP manifest schema_version=1 is supported")
    dataset_id = safe_name(str(manifest.get("dataset_id", "")))
    if "/" in dataset_id:
        raise ValueError("dataset_id must be a single path component")

    files = [_validate_file(dict(item)) for item in manifest.get("files", [])]
    index_resolutions: list[dict[str, Any]] = []
    for source in manifest.get("apache_indexes", []):
        url = str(source["url"])
        resolved = parse_apache_index(
            fetcher(url, proxy),
            url,
            str(source.get("path_prefix", "")),
            str(source.get("include_regex", r".*")),
        )
        if source.get("magic_hex"):
            for item in resolved:
                item["magic_hex"] = source["magic_hex"]
        expected_files = int(source.get("expected_files", len(resolved)))
        expected_bytes = int(
            source.get("expected_bytes", sum(item["expected_bytes"] for item in resolved))
        )
        actual_bytes = sum(item["expected_bytes"] for item in resolved)
        if len(resolved) != expected_files or actual_bytes != expected_bytes:
            raise ValueError(
                f"Apache index drift at {url}: files {len(resolved)}/{expected_files}, "
                f"bytes {actual_bytes}/{expected_bytes}"
            )
        files.extend(_validate_file(item) for item in resolved)
        index_resolutions.append(
            {
                "url": url,
                "file_count": len(resolved),
                "expected_bytes": actual_bytes,
                "resolved_at": utc_now(),
            }
        )

    names = [item["name"] for item in files]
    if not files:
        raise ValueError("Manifest resolves to zero files")
    if len(names) != len(set(names)):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"Duplicate manifest filenames: {duplicates}")

    actual_bytes = sum(item["expected_bytes"] for item in files)
    expected_bytes = int(manifest.get("expected_bytes", actual_bytes))
    expected_files = int(manifest.get("expected_files", len(files)))
    if len(files) != expected_files or actual_bytes != expected_bytes:
        raise ValueError(
            f"Manifest invariant failed: files {len(files)}/{expected_files}, "
            f"bytes {actual_bytes}/{expected_bytes}"
        )
    return {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "source": manifest.get("source"),
        "expected_files": expected_files,
        "expected_bytes": expected_bytes,
        "files": files,
        "apache_indexes": index_resolutions,
    }


def load_manifest(path: Path, proxy: str | None = None) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("HTTP manifest root must be a JSON object")
    return resolve_manifest(value, proxy)


def write_source_files(path: Path, files: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["name", "size_bytes", "source_checksum", "url"])
        for item in files:
            writer.writerow(
                [item["name"], item["expected_bytes"], item.get("checksum", ""), item["url"]]
            )


def matches_magic(path: Path, magic_hex: str | None) -> bool:
    if not magic_hex:
        return True
    expected = bytes.fromhex(magic_hex)
    with path.open("rb") as handle:
        return handle.read(len(expected)) == expected


def download_command(
    url: str,
    destination: Path,
    connections: int,
    proxy: str | None,
) -> list[str]:
    """Build an argv-only command; no manifest value is evaluated by a shell."""

    if proxy and urlparse(proxy).scheme in {"socks5", "socks5h"}:
        return [
            "curl",
            "--fail",
            "--show-error",
            "--location",
            "--continue-at",
            "-",
            "--retry",
            "1000000",
            "--retry-delay",
            "15",
            "--connect-timeout",
            "30",
            "--speed-limit",
            "1024",
            "--speed-time",
            "60",
            "--max-time",
            "0",
            "--proxy",
            proxy,
            "--user-agent",
            USER_AGENT,
            "--output",
            str(destination),
            url,
        ]
    command = [
        "aria2c",
        "--continue=true",
        "--auto-file-renaming=false",
        "--allow-overwrite=false",
        "--file-allocation=none",
        f"--max-connection-per-server={max(1, connections)}",
        f"--split={max(1, connections)}",
        "--min-split-size=64M",
        "--max-tries=0",
        "--retry-wait=15",
        "--connect-timeout=30",
        "--timeout=120",
        "--summary-interval=60",
    ]
    if proxy:
        command.append(f"--all-proxy={proxy}")
    command.extend([f"--dir={destination.parent}", f"--out={destination.name}", url])
    return command


def run_download(
    url: str,
    destination: Path,
    connections: int,
    proxy: str | None,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = download_command(url, destination, connections, proxy)
    transient_curl_codes = {5, 6, 7, 18, 28, 35, 47, 52, 55, 56, 92}
    while True:
        result = subprocess.run(command, check=False)
        if result.returncode == 0:
            return
        if command[0] != "curl" or result.returncode not in transient_curl_codes:
            result.check_returncode()
        time.sleep(15)


def load_previous_state(path: Path, dataset_id: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return value if value.get("dataset_id") == dataset_id else {}


def main() -> int:
    args = parse_args()
    proxy = validate_proxy(args.proxy)
    resolved = load_manifest(args.manifest.resolve(), proxy)
    root = args.root.resolve()
    raw_dir = root / "raw"
    metadata_dir = root / "metadata"
    manifest_dir = root / "manifests"
    state_path = manifest_dir / "collection_state.json"
    raw_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(metadata_dir / "resolved_http_manifest.json", resolved)
    write_source_files(manifest_dir / "source_files.tsv", resolved["files"])

    previous = load_previous_state(state_path, resolved["dataset_id"])
    previous_files = previous.get("files", {})
    state: dict[str, Any] = {
        "dataset_id": resolved["dataset_id"],
        "source": resolved.get("source"),
        "generated_at": utc_now(),
        "root": str(root),
        "expected_file_count": resolved["expected_files"],
        "selection_size_bytes": resolved["expected_bytes"],
        "parallel_jobs": max(1, args.jobs),
        "connections_per_file": max(1, args.connections),
        "proxy": redacted_proxy(proxy),
        "files": {},
    }
    for item in resolved["files"]:
        name = item["name"]
        target = raw_dir.joinpath(*PurePosixPath(name).parts)
        old = previous_files.get(name, {})
        entry: dict[str, Any] = {
            "size_expected": item["expected_bytes"],
            "source_checksum": item.get("checksum"),
            "magic_hex": item.get("magic_hex"),
            "url": item["url"],
            "status": "metadata_only" if args.metadata_only else "pending",
        }
        if (
            not args.metadata_only
            and old.get("status") == "verified"
            and old.get("url") == entry["url"]
            and old.get("size_expected") == entry["size_expected"]
            and old.get("source_checksum") == entry["source_checksum"]
            and old.get("magic_hex") == entry["magic_hex"]
            and target.is_file()
            and target.stat().st_size == entry["size_expected"]
            and matches_magic(target, entry["magic_hex"])
        ):
            entry.update(old)
        state["files"][name] = entry

    lock = Lock()

    def save_state() -> None:
        with lock:
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    def update(name: str, **values: Any) -> None:
        with lock:
            state["files"][name].update(values)
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    save_state()

    def collect(item: dict[str, Any]) -> str:
        name = item["name"]
        entry = state["files"][name]
        target = raw_dir.joinpath(*PurePosixPath(name).parts)
        partial = Path(f"{target}.part")
        if entry.get("status") in {"verified", "metadata_only"}:
            return name
        if target.is_file() and target.stat().st_size > entry["size_expected"]:
            raise RuntimeError(f"Existing file exceeds expected_bytes: {target}")
        if target.is_file() and target.stat().st_size < entry["size_expected"]:
            if partial.exists():
                raise RuntimeError(f"Both legacy partial and .part file exist for {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.replace(partial)

        candidate = target
        if not target.is_file() or target.stat().st_size != entry["size_expected"]:
            if partial.is_file() and partial.stat().st_size > entry["size_expected"]:
                raise RuntimeError(f"Partial file exceeds expected_bytes: {partial}")
            if partial.is_file() and not matches_magic(partial, entry.get("magic_hex")):
                rejected = Path(f"{partial}.rejected-{utc_now().replace(':', '')}")
                partial.replace(rejected)
            candidate = partial
            if not partial.is_file() or partial.stat().st_size != entry["size_expected"]:
                update(name, status="downloading", error=None)
                run_download(entry["url"], partial, max(1, args.connections), proxy)

        update(name, status="verifying")
        checksum = entry.get("source_checksum")
        expected_algorithm = checksum.split(":", 1)[0] if checksum else None
        algorithms = list(dict.fromkeys(filter(None, [expected_algorithm, "sha256"])))
        digests = digest_file(candidate, algorithms)
        size_actual = candidate.stat().st_size
        verified = (
            size_actual == entry["size_expected"]
            and matches_magic(candidate, entry.get("magic_hex"))
        )
        if checksum:
            expected_digest = checksum.split(":", 1)[1]
            verified = verified and digests[expected_algorithm].lower() == expected_digest
        if verified and candidate != target:
            os.replace(candidate, target)
        update(
            name,
            size_actual=size_actual,
            digests=digests,
            verified_at=utc_now(),
            status="verified" if verified else "checksum_failed",
        )
        if not verified:
            raise RuntimeError(f"Integrity verification failed for {candidate}")
        return name

    errors: list[str] = []
    if not args.metadata_only:
        pending = [
            item
            for item in resolved["files"]
            if state["files"][item["name"]].get("status") != "verified"
        ]
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            futures = {executor.submit(collect, item): item["name"] for item in pending}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    update(name, status="failed", error=repr(exc), failed_at=utc_now())
                    errors.append(f"{name}: {exc!r}")

    state["complete"] = not errors and all(
        value.get("status") in {"verified", "metadata_only"}
        for value in state["files"].values()
    )
    save_state()
    print(json.dumps({"state": str(state_path), "complete": state["complete"]}))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
