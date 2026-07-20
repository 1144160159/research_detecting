"""Enumerate a public Google Drive folder without downloading payload files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from gdown.download import _get_session
from gdown.download_folder import _download_and_parse_google_drive_link
from gdown.download_folder import _get_directory_structure
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--proxy")
    parser.add_argument(
        "--remaining-ok",
        action="store_true",
        help="Allow enumeration when a folder reaches Google Drive's 50-item page limit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = _get_session(
        proxy=args.proxy,
        use_cookies=True,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
        ),
    )
    retry = Retry(
        total=10,
        connect=10,
        read=10,
        status=6,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    success, root = _download_and_parse_google_drive_link(
        sess=session,
        url=args.folder_url,
        quiet=False,
        remaining_ok=args.remaining_ok,
        verify=True,
    )
    if not success or root is None:
        raise SystemExit("Google Drive folder enumeration failed")
    directory_structure = _get_directory_structure(root, previous_path="")
    files = [(file_id, path) for file_id, path in directory_structure if file_id]

    payload = {
        "folder_url": args.folder_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "enumeration_limit_per_folder": 50,
        "remaining_ok": args.remaining_ok,
        "file_count": len(files),
        "files": [
            {"id": file_id, "path": path, "download_url": f"https://drive.google.com/uc?id={file_id}"}
            for file_id, path in files
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "file_count": len(files)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
