from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyYAML is required. Use the paper-search-mcp uv Python or install pyyaml.") from exc
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\x00", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(title: str) -> str:
    title = clean_text(title).lower()
    title = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def stable_id(*parts: str) -> str:
    raw = "|".join(clean_text(p) for p in parts if clean_text(p))
    return hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]


def doi_from_filename(path: Path) -> str:
    stem = path.stem
    if not stem.lower().startswith("10."):
        return ""
    match = re.match(r"^(10\.\d{4,9})_(.+)$", stem)
    if not match:
        return stem.replace("_", "/", 1)
    return match.group(1) + "/" + match.group(2).replace("_", ".")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def run_command(args: list[str], timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def keyword_groups(queries_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    groups = queries_config.get("keyword_groups", {})
    if not isinstance(groups, dict):
        return {}
    return groups


def score_text(text: str, groups: dict[str, dict[str, Any]]) -> tuple[int, list[str], list[str]]:
    low = text.lower()
    score = 0
    matched_groups: list[str] = []
    matched_terms: list[str] = []
    for group_name, group_config in groups.items():
        terms = group_config.get("terms", []) if isinstance(group_config, dict) else []
        weight = int(group_config.get("weight", 1)) if isinstance(group_config, dict) else 1
        hits = []
        for term in terms:
            term_s = str(term).lower()
            if term_s and term_s in low:
                hits.append(str(term))
        if hits:
            matched_groups.append(group_name)
            matched_terms.extend(hits[:8])
            score += weight * min(len(hits), 5)

    group_set = set(matched_groups)
    if {"open_set", "encrypted_traffic"} <= group_set:
        score += 8
    if {"encrypted_traffic", "malicious"} <= group_set:
        score += 5
    if {"open_set", "anomaly_detection"} <= group_set:
        score += 5
    if {"self_supervised", "encrypted_traffic"} <= group_set:
        score += 4
    if {"multimodal", "encrypted_traffic"} <= group_set:
        score += 4
    if {"boundary", "open_set"} <= group_set:
        score += 4

    return score, matched_groups, sorted(set(matched_terms), key=str.lower)

