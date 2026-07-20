from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from pathlib import Path
from typing import Any

import requests

from common import clean_text, ensure_dir, latest_file, load_yaml, timestamp, write_csv, write_json


MCP_URL = "http://127.0.0.1:23120/mcp"
CONNECTOR_BASE = "http://127.0.0.1:23119"


def check_connector() -> None:
    last_error = ""
    for _ in range(5):
        try:
            resp = requests.get(f"{CONNECTOR_BASE}/connector/ping", timeout=10)
            if resp.status_code == 200:
                return
            last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"Zotero Connector is not available at {CONNECTOR_BASE}: {last_error}")


class MCPClient:
    def __init__(self) -> None:
        self.session_id = ""
        self.request_id = 1

    def start(self) -> None:
        body = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "codex-zotero-import", "version": "1.0"},
            },
        }
        self.request_id += 1
        resp = requests.post(
            MCP_URL,
            json=body,
            headers={"Accept": "application/json, text/event-stream"},
            timeout=30,
        )
        resp.raise_for_status()
        self.session_id = resp.headers.get("Mcp-Session-Id", "")
        if not self.session_id:
            raise RuntimeError("MCP server did not return Mcp-Session-Id")
        requests.post(
            MCP_URL,
            json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            headers=self.headers,
            timeout=30,
        )

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self.session_id,
        }

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        body = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        self.request_id += 1
        resp = requests.post(MCP_URL, json=body, headers=self.headers, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
        result = payload.get("result", {})
        content = result.get("content", [])
        if not content:
            return result
        text = content[0].get("text", "")
        try:
            return json.loads(text)
        except Exception:
            return text


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def make_connector_id(row: dict[str, str]) -> str:
    return "codex-" + clean_text(row.get("candidate_id") or row.get("rank") or str(time.time())).replace(" ", "-")


def tags_from_manifest(row: dict[str, str]) -> list[dict[str, str]]:
    raw = row.get("zotero_tags", "")
    return [{"tag": tag.strip()} for tag in raw.split(";") if tag.strip()]


def zotero_item_from_manifest(row: dict[str, str]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": make_connector_id(row),
        "itemType": "journalArticle",
        "title": row.get("title", "").strip() or "Untitled",
        "tags": tags_from_manifest(row),
        "notes": [],
        "creators": [],
    }
    if row.get("doi"):
        item["DOI"] = row["doi"].strip()
    if row.get("year"):
        item["date"] = row["year"].strip()
    if row.get("source"):
        item["libraryCatalog"] = row["source"].strip()
    extra = [
        "Imported by Codex Zotero workflow.",
        f"Candidate ID: {row.get('candidate_id', '')}",
        f"Original file: {row.get('file_path', '')}",
        f"Reason: {row.get('reason', '')}",
    ]
    item["extra"] = "\n".join(extra)
    return item


def backup_zotero_db(workspace: Path) -> str:
    db_path = Path(r"D:\soft\Zotero\data\zotero.sqlite")
    if not db_path.exists():
        return ""
    backup_dir = ensure_dir(workspace / "zotero-workflow" / "zotero-import" / "backups")
    backup_subdir = ensure_dir(backup_dir / f"{timestamp()}_before_connector_import")
    copied: list[str] = []
    for suffix in ("", "-wal", "-shm"):
        source = Path(str(db_path) + suffix)
        if not source.exists():
            continue
        target = backup_subdir / source.name
        shutil.copy2(source, target)
        copied.append(str(target))
    if not copied:
        return ""
    return str(backup_subdir)


def find_collection_recursive(collections: list[dict[str, Any]], parts: list[str]) -> dict[str, Any] | None:
    if not parts:
        return None
    for collection in collections:
        if collection.get("name") == parts[0]:
            if len(parts) == 1:
                return collection
            return find_collection_recursive(collection.get("subcollections", []) or [], parts[1:])
    return None


def ensure_collection_path(mcp: MCPClient, collection_path: str) -> str:
    parts = [part for part in collection_path.split("/") if part]
    parent_key = ""
    for index, part in enumerate(parts):
        collections = mcp.call_tool("get_collections", {"recursive": True})
        existing = find_collection_recursive(collections, parts[: index + 1])
        if existing:
            parent_key = existing["key"]
            continue
        args: dict[str, Any] = {"name": part}
        if parent_key:
            args["parentCollection"] = parent_key
        created = mcp.call_tool("create_collection", args)
        if isinstance(created, dict) and created.get("key"):
            parent_key = created["key"]
        else:
            collections = mcp.call_tool("get_collections", {"recursive": True})
            existing = find_collection_recursive(collections, parts[: index + 1])
            if not existing:
                raise RuntimeError(f"Failed to create/find collection path: {collection_path}")
            parent_key = existing["key"]
    return parent_key


def search_existing_item(mcp: MCPClient, row: dict[str, str]) -> str:
    title = row.get("title", "").strip()
    doi = row.get("doi", "").strip()
    if doi:
        result = mcp.call_tool("search_library", {"q": doi, "limit": 5, "mode": "minimal"})
        for item in result.get("results", []) if isinstance(result, dict) else []:
            if doi.lower() in json.dumps(item, ensure_ascii=False).lower():
                return item.get("key") or item.get("itemKey") or ""
    if title:
        result = mcp.call_tool(
            "search_library",
            {"title": title, "titleOperator": "exact", "limit": 5, "mode": "minimal"},
        )
        for item in result.get("results", []) if isinstance(result, dict) else []:
            return item.get("key") or item.get("itemKey") or ""
    return ""


def search_imported_keys(mcp: MCPClient, rows: list[dict[str, str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in rows:
        key = search_existing_item(mcp, row)
        if key:
            mapping[make_connector_id(row)] = key
    return mapping


def save_items(items: list[dict[str, Any]], session_id: str) -> None:
    body = {
        "sessionID": session_id,
        "uri": "https://codex.local/zotero-workflow/import",
        "items": items,
    }
    resp = requests.post(
        f"{CONNECTOR_BASE}/connector/saveItems",
        json=body,
        headers={"Zotero-Connector-API-Version": "3"},
        timeout=120,
    )
    if resp.status_code != 201:
        raise RuntimeError(f"saveItems failed: HTTP {resp.status_code} {resp.text[:500]}")


def attach_pdf(row: dict[str, str], session_id: str) -> tuple[bool, str]:
    path = Path(row.get("file_path", ""))
    if not path.exists() or path.suffix.lower() != ".pdf":
        return False, "no local pdf"
    metadata = {
        "sessionID": session_id,
        "parentItemID": make_connector_id(row),
        "title": "Full Text PDF",
        "url": path.as_uri(),
    }
    with path.open("rb") as f:
        resp = requests.post(
            f"{CONNECTOR_BASE}/connector/saveAttachment",
            data=f,
            headers={
                "Content-Type": "application/pdf",
                "X-Metadata": json.dumps(metadata, ensure_ascii=False),
                "Zotero-Connector-API-Version": "3",
            },
            timeout=180,
        )
    if resp.status_code != 201:
        return False, f"HTTP {resp.status_code}: {resp.text[:300]}"
    return True, "attached"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sources", default="")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workflow = workspace / "zotero-workflow"
    config = load_yaml(Path(args.config))
    manifest = latest_file(workflow / "zotero-import", "*_confirmed_keep_zotero_manifest.csv")
    if not manifest:
        raise FileNotFoundError("No confirmed keep manifest found")
    rows = read_csv(manifest)
    if args.limit > 0:
        rows = rows[: args.limit]

    collection_path = rows[0].get("zotero_collection") if rows else ""
    collection_path = collection_path or "异常检测/01_Core_核心证据"
    output_dir = ensure_dir(workflow / "zotero-import")
    stamp = timestamp()
    report_csv = output_dir / f"{stamp}_zotero_connector_import_report.csv"
    summary_json = output_dir / f"{stamp}_zotero_connector_import_summary.json"

    if args.dry_run:
        print(json.dumps({
            "stage": "zotero-import",
            "dry_run": True,
            "manifest": str(manifest),
            "items": len(rows),
            "collection_path": collection_path,
            "would_write": [str(report_csv), str(summary_json)],
        }, ensure_ascii=False, indent=2))
        return 0

    check_connector()
    backup_path = backup_zotero_db(workspace)
    print(f"[zotero-import] backup={backup_path}", flush=True)
    mcp = MCPClient()
    mcp.start()
    collection_key = ensure_collection_path(mcp, collection_path)
    print(f"[zotero-import] collection={collection_path} key={collection_key}", flush=True)

    report_rows: list[dict[str, Any]] = []
    new_rows: list[dict[str, str]] = []
    existing_keys: dict[str, str] = {}
    for index, row in enumerate(rows, start=1):
        print(f"[zotero-import] scan {index}/{len(rows)}", flush=True)
        existing_key = search_existing_item(mcp, row)
        if existing_key:
            existing_keys[make_connector_id(row)] = existing_key
            report_rows.append({
                "rank": row.get("rank", ""),
                "title": row.get("title", ""),
                "doi": row.get("doi", ""),
                "connector_id": make_connector_id(row),
                "item_key": existing_key,
                "created": "false",
                "attachment": "skipped_existing_item",
                "collection_added": "",
                "error": "",
            })
        else:
            new_rows.append(row)

    session_id = "codex-import-" + stamp
    if new_rows:
        print(f"[zotero-import] creating {len(new_rows)} new items", flush=True)
        save_items([zotero_item_from_manifest(row) for row in new_rows], session_id)
        for index, row in enumerate(new_rows, start=1):
            print(f"[zotero-import] attach {index}/{len(new_rows)}", flush=True)
            ok, message = attach_pdf(row, session_id)
            report_rows.append({
                "rank": row.get("rank", ""),
                "title": row.get("title", ""),
                "doi": row.get("doi", ""),
                "connector_id": make_connector_id(row),
                "item_key": "",
                "created": "true",
                "attachment": message if ok else f"failed: {message}",
                "collection_added": "",
                "error": "",
            })

    time.sleep(2)
    key_map = {**existing_keys, **search_imported_keys(mcp, rows)}
    item_keys = sorted(set(key for key in key_map.values() if key))
    if item_keys:
        print(f"[zotero-import] adding {len(item_keys)} items to collection", flush=True)
        mcp.call_tool("add_items_to_collection", {"collectionKey": collection_key, "itemKeys": item_keys})

    for report in report_rows:
        key = key_map.get(report["connector_id"], "")
        report["item_key"] = report.get("item_key") or key
        report["collection_added"] = "true" if key else "false"
        if not key:
            report["error"] = "Could not resolve Zotero item key after import"

    fields = [
        "rank", "title", "doi", "connector_id", "item_key",
        "created", "attachment", "collection_added", "error",
    ]
    write_csv(report_csv, report_rows, fields)
    summary = {
        "stage": "zotero-import",
        "manifest": str(manifest),
        "collection_path": collection_path,
        "collection_key": collection_key,
        "db_backup": backup_path,
        "requested_items": len(rows),
        "new_items": len(new_rows),
        "existing_items": len(existing_keys),
        "resolved_item_keys": len(item_keys),
        "attachments_attempted": sum(1 for row in new_rows if row.get("file_path")),
        "attachments_succeeded": sum(1 for row in report_rows if row.get("attachment") == "attached"),
        "report_csv": str(report_csv),
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
