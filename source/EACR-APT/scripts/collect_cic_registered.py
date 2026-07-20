#!/usr/bin/env python3
"""Collect a CIC dataset after the user has authorized form registration.

Credentials are read only from environment variables and are never written to
logs, manifests, or state files.  The authenticated cookie jar remains in
memory.  Dataset payloads must be written to the GPU-side ``--root`` path.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
from html.parser import HTMLParser
import http.cookiejar
import json
import os
from pathlib import Path, PurePosixPath
import threading
import time
from typing import Dict, Iterable, Mapping
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_BASE = "https://cicresearch.ca/IOTDataset/CICAPT-IIoT-Dataset"
REQUIRED_ENV = {
    "first_name": "CIC_FIRST_NAME",
    "last_name": "CIC_LAST_NAME",
    "email": "CIC_EMAIL",
    "institution": "CIC_INSTITUTION",
    "job_title": "CIC_JOB_TITLE",
    "country": "CIC_COUNTRY",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.hrefs.append(value)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_credentials() -> dict[str, str]:
    values = {field: os.environ.get(env_name, "").strip() for field, env_name in REQUIRED_ENV.items()}
    missing = [REQUIRED_ENV[field] for field, value in values.items() if not value]
    if missing:
        raise RuntimeError("missing required credential environment variables: " + ", ".join(missing))
    return values


def build_authenticated_opener(base_url: str, timeout: int) -> tuple[urllib.request.OpenerDirector, str]:
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [("User-Agent", "EACR-APT-public-dataset-collector/1.0")]
    payload = urllib.parse.urlencode(load_credentials()).encode("utf-8")
    request = urllib.request.Request(f"{base_url.rstrip('/')}/insert.php", data=payload, method="POST")
    with opener.open(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("ok") is not True:
        raise RuntimeError("CIC registration was not accepted: " + str(result.get("message", "unknown error")))
    cookie_header = "; ".join(f"{cookie.name}={cookie.value}" for cookie in cookie_jar)
    if not cookie_header:
        raise RuntimeError("CIC registration succeeded but no authenticated session cookie was returned")
    return opener, cookie_header


def read_page(opener: urllib.request.OpenerDirector, url: str, timeout: int) -> str:
    with opener.open(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def safe_relative_path(download_url: str) -> str:
    parsed = urllib.parse.urlparse(download_url)
    query = urllib.parse.parse_qs(parsed.query)
    source_path = query.get("file", [""])[0]
    pure = PurePosixPath(source_path)
    if pure.is_absolute() or not pure.parts or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError(f"unsafe CIC dataset path: {source_path!r}")
    parts = list(pure.parts)
    if parts[0] == "CICAPT-IIoT Dataset":
        parts = parts[1:]
    if not parts:
        raise ValueError(f"empty CIC dataset path: {source_path!r}")
    return PurePosixPath(*parts).as_posix()


def enumerate_files(
    opener: urllib.request.OpenerDirector,
    base_url: str,
    timeout: int,
) -> Dict[str, str]:
    base = base_url.rstrip("/") + "/"
    expected_host = urllib.parse.urlparse(base).netloc
    queue = [urllib.parse.urljoin(base, "browse.php?p=")]
    visited: set[str] = set()
    files: dict[str, str] = {}
    while queue:
        page_url = queue.pop(0)
        if page_url in visited:
            continue
        visited.add(page_url)
        parser = LinkParser()
        parser.feed(read_page(opener, page_url, timeout))
        for href in parser.hrefs:
            absolute = urllib.parse.urljoin(base, href)
            parsed = urllib.parse.urlparse(absolute)
            if parsed.netloc != expected_host:
                continue
            name = PurePosixPath(parsed.path).name
            if name == "browse.php" and "p=" in parsed.query and absolute not in visited:
                queue.append(absolute)
            elif name == "download.php" and "file=" in parsed.query:
                relative = safe_relative_path(absolute)
                previous = files.setdefault(relative, absolute)
                if previous != absolute:
                    raise RuntimeError(f"conflicting URLs for {relative}")
    if not files:
        raise RuntimeError("authenticated CIC browser returned no downloadable files")
    return dict(sorted(files.items()))


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_one(
    relative: str,
    url: str,
    raw_root: Path,
    cookie_header: str,
    timeout: int,
    max_retries: int,
) -> dict[str, object]:
    destination = raw_root.joinpath(*PurePosixPath(relative).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_name(destination.name + ".part")
    if destination.exists():
        return {
            "status": "verified",
            "size_actual": destination.stat().st_size,
            "sha256": sha256_file(destination),
            "url": url,
            "verified_at": utc_now(),
            "reused_existing": True,
        }

    last_error = ""
    for attempt in range(1, max_retries + 1):
        offset = part.stat().st_size if part.exists() else 0
        headers = {
            "Cookie": cookie_header,
            "User-Agent": "EACR-APT-public-dataset-collector/1.0",
        }
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                disposition = response.headers.get("Content-Disposition", "")
                if "attachment" not in disposition.lower():
                    raise RuntimeError("server response is not a dataset attachment")
                status = getattr(response, "status", response.getcode())
                if offset and status == 206:
                    mode = "ab"
                else:
                    mode = "wb"
                    offset = 0
                with part.open(mode) as handle:
                    while True:
                        block = response.read(8 * 1024 * 1024)
                        if not block:
                            break
                        handle.write(block)
            part.replace(destination)
            return {
                "status": "verified",
                "size_actual": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "url": url,
                "verified_at": utc_now(),
                "attempts": attempt,
                "range_supported": bool(offset),
            }
        except Exception as exc:  # network failures are recorded and retried
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(min(5 * attempt, 30))
    return {
        "status": "failed",
        "size_actual": part.stat().st_size if part.exists() else 0,
        "url": url,
        "error": last_error,
        "attempts": max_retries,
    }


def write_state(root: Path, files: Mapping[str, Mapping[str, object]], expected_count: int | None) -> None:
    manifests = root / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    complete = bool(files) and all(row.get("status") == "verified" for row in files.values())
    if expected_count is not None:
        complete = complete and len(files) == expected_count
    selection_size = sum(int(row.get("size_actual") or 0) for row in files.values())
    state = {
        "complete": complete,
        "source": DEFAULT_BASE,
        "expected_file_count": expected_count,
        "enumerated_file_count": len(files),
        "selection_size_bytes": selection_size,
        "generated_at": utc_now(),
        "credentials_persisted": False,
        "files": dict(sorted(files.items())),
    }
    (manifests / "collection_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (manifests / "source_files.tsv").open("w", encoding="utf-8", newline="") as handle:
        handle.write("relative_path\tsize_actual\tsha256\tstatus\turl\n")
        for relative, row in sorted(files.items()):
            handle.write(
                "\t".join(
                    [
                        relative,
                        str(row.get("size_actual") or ""),
                        str(row.get("sha256") or ""),
                        str(row.get("status") or ""),
                        str(row.get("url") or ""),
                    ]
                )
                + "\n"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=20)
    parser.add_argument("--expected-files", type=int, default=43)
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.root.mkdir(parents=True, exist_ok=True)
    opener, cookie_header = build_authenticated_opener(args.base_url, args.timeout)
    source_files = enumerate_files(opener, args.base_url, args.timeout)
    if args.expected_files and len(source_files) != args.expected_files:
        raise RuntimeError(
            f"CIC dataset file-count drift: expected {args.expected_files}, enumerated {len(source_files)}"
        )
    if args.metadata_only:
        rows = {relative: {"status": "metadata_only", "url": url} for relative, url in source_files.items()}
        write_state(args.root, rows, args.expected_files)
        print(json.dumps({"enumerated_files": len(rows), "metadata_only": True}))
        return 0

    raw_root = args.root / "raw"
    rows: dict[str, dict[str, object]] = {}
    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        future_map = {
            pool.submit(
                download_one,
                relative,
                url,
                raw_root,
                cookie_header,
                args.timeout,
                args.max_retries,
            ): relative
            for relative, url in source_files.items()
        }
        for future in concurrent.futures.as_completed(future_map):
            relative = future_map[future]
            try:
                row = future.result()
            except Exception as exc:
                row = {"status": "failed", "error": f"{type(exc).__name__}: {exc}", "url": source_files[relative]}
            with lock:
                rows[relative] = row
                write_state(args.root, rows, args.expected_files)
            print(json.dumps({"file": relative, "status": row.get("status"), "bytes": row.get("size_actual", 0)}))
    write_state(args.root, rows, args.expected_files)
    return 0 if all(row.get("status") == "verified" for row in rows.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
