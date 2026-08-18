from __future__ import annotations

import argparse
import datetime as dt
import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36"
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def api_path(function: str, server_relative_path: str, suffix: str = "") -> str:
    encoded_path = urllib.parse.quote(server_relative_path, safe="/")
    return f"/_api/web/{function}(%27{encoded_path}%27){suffix}"


def safe_relative_path(root: str, item: str) -> Path:
    root_path = PurePosixPath(root)
    item_path = PurePosixPath(item)
    try:
        relative = item_path.relative_to(root_path)
    except ValueError as error:
        raise ValueError(f"item is outside requested root: {item}") from error
    if not relative.parts or any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError(f"unsafe SharePoint item path: {item}")
    return Path(*relative.parts)


class SharePointFolderDownloader:
    def __init__(
        self,
        share_url: str,
        root_server_relative_url: str,
        destination: Path,
        retries: int = 5,
        chunk_size: int = 8 * 1024 * 1024,
    ) -> None:
        parsed = urllib.parse.urlsplit(share_url)
        if parsed.scheme != "https" or not parsed.netloc.endswith(
            ".sharepoint.com"
        ):
            raise ValueError("share URL must be an HTTPS SharePoint URL")
        self.share_url = share_url
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.root = root_server_relative_url.rstrip("/")
        self.destination = destination.resolve()
        self.retries = retries
        self.chunk_size = chunk_size
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies)
        )

    @staticmethod
    def _request(url: str, headers: dict[str, str] | None = None) -> urllib.request.Request:
        combined = {"User-Agent": USER_AGENT}
        if headers:
            combined.update(headers)
        return urllib.request.Request(url, headers=combined)

    def bootstrap(self) -> None:
        with self.opener.open(self._request(self.share_url), timeout=120) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"SharePoint bootstrap returned HTTP {response.status}"
                )
            response.read(1)

    def _json(self, relative_url: str) -> dict[str, Any]:
        request = self._request(
            self.origin + relative_url,
            {"Accept": "application/json;odata=nometadata"},
        )
        with self.opener.open(request, timeout=120) as response:
            return json.load(response)

    def enumerate_files(self) -> list[dict[str, Any]]:
        pending = [self.root]
        files: list[dict[str, Any]] = []
        while pending:
            folder = pending.pop()
            metadata = self._json(
                api_path(
                    "GetFolderByServerRelativeUrl",
                    folder,
                    "?%24expand=Folders%2CFiles",
                )
            )
            for child in metadata.get("Folders", []):
                pending.append(str(child["ServerRelativeUrl"]))
            for item in metadata.get("Files", []):
                server_path = str(item["ServerRelativeUrl"])
                files.append(
                    {
                        "name": str(item["Name"]),
                        "server_relative_url": server_path,
                        "relative_path": safe_relative_path(
                            self.root, server_path
                        ).as_posix(),
                        "length": int(item["Length"]),
                        "unique_id": str(item["UniqueId"]),
                        "time_last_modified": str(item["TimeLastModified"]),
                    }
                )
        return sorted(files, key=lambda item: item["relative_path"])

    def _download_once(
        self,
        item: dict[str, Any],
        part_path: Path,
    ) -> None:
        expected = int(item["length"])
        offset = part_path.stat().st_size if part_path.exists() else 0
        if offset > expected:
            raise RuntimeError(
                f"partial file exceeds expected size: {part_path}"
            )
        headers = {}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        download_url = self.origin + api_path(
            "GetFileByServerRelativeUrl",
            str(item["server_relative_url"]),
            "/%24value",
        )
        request = self._request(download_url, headers)
        with self.opener.open(request, timeout=300) as response:
            status = int(response.status)
            if offset and status == 206:
                mode = "ab"
            elif status == 200:
                mode = "wb"
            else:
                raise RuntimeError(
                    f"unexpected HTTP {status} for {item['relative_path']}"
                )
            with part_path.open(mode) as handle:
                while True:
                    block = response.read(self.chunk_size)
                    if not block:
                        break
                    handle.write(block)
                handle.flush()
                os.fsync(handle.fileno())
        actual = part_path.stat().st_size
        if actual != expected:
            raise RuntimeError(
                f"size mismatch for {item['relative_path']}: "
                f"expected {expected}, got {actual}"
            )

    def download_file(self, item: dict[str, Any]) -> str:
        relative = Path(str(item["relative_path"]))
        target = (self.destination / relative).resolve()
        try:
            target.relative_to(self.destination)
        except ValueError as error:
            raise ValueError(f"unsafe local target: {target}") from error
        target.parent.mkdir(parents=True, exist_ok=True)
        expected = int(item["length"])
        if target.exists():
            if target.stat().st_size == expected:
                return "skipped_existing_same_size"
            raise FileExistsError(
                f"refusing to overwrite different existing file: {target}"
            )
        part_path = target.with_name(target.name + ".part")
        for attempt in range(1, self.retries + 1):
            try:
                self._download_once(item, part_path)
                os.replace(part_path, target)
                return "downloaded"
            except (
                OSError,
                RuntimeError,
                urllib.error.URLError,
                urllib.error.HTTPError,
            ):
                if attempt == self.retries:
                    raise
                time.sleep(min(60, 2**attempt))
        raise AssertionError("retry loop terminated unexpectedly")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--share-url", required=True)
    parser.add_argument("--root-server-relative-url", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--retries", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    downloader = SharePointFolderDownloader(
        args.share_url,
        args.root_server_relative_url,
        args.destination,
        retries=args.retries,
    )
    downloader.bootstrap()
    files = downloader.enumerate_files()
    manifest: dict[str, Any] = {
        "schema_version": "sharepoint_recursive_download_manifest_v1",
        "source": {
            "share_url": args.share_url,
            "root_server_relative_url": args.root_server_relative_url,
        },
        "destination": str(args.destination.resolve()),
        "enumerated_at_utc": utc_now(),
        "file_count": len(files),
        "total_bytes": sum(int(item["length"]) for item in files),
        "files": files,
        "state": "audit_complete" if args.audit_only else "downloading",
        "progress": {
            "completed_files": 0,
            "downloaded_files": 0,
            "skipped_existing_files": 0,
            "completed_bytes": 0,
        },
    }
    atomic_json(args.manifest, manifest)
    if args.audit_only:
        print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
        return
    for item in files:
        outcome = downloader.download_file(item)
        item["download_outcome"] = outcome
        manifest["progress"]["completed_files"] += 1
        manifest["progress"]["completed_bytes"] += int(item["length"])
        if outcome == "downloaded":
            manifest["progress"]["downloaded_files"] += 1
        else:
            manifest["progress"]["skipped_existing_files"] += 1
        manifest["updated_at_utc"] = utc_now()
        atomic_json(args.manifest, manifest)
        print(
            json.dumps(
                {
                    "relative_path": item["relative_path"],
                    "bytes": item["length"],
                    "outcome": outcome,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )
    manifest["state"] = "completed"
    manifest["completed_at_utc"] = utc_now()
    atomic_json(args.manifest, manifest)
    print(json.dumps(manifest["progress"], sort_keys=True))


if __name__ == "__main__":
    main()
