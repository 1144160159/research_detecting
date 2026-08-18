from __future__ import annotations

import csv
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
READING = Path(__file__).resolve().parents[1]
QUEUE = READING / "00_检索与筛选" / "120篇中文精读队列_2026-08-05.csv"
OUTPUT = READING / "04_120篇全文抽取"
MANIFEST = OUTPUT / "全文抽取清单.csv"


def safe_name(rank: str, title: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")[:72]
    return f"{int(rank):03d}_{stem or 'paper'}.txt"


def extract(row: dict[str, str], pdftotext: str) -> dict[str, str]:
    source = ROOT / row["file_path"]
    target = OUTPUT / safe_name(row["rank"], row["title"])
    result = dict(row)
    result["text_path"] = str(target.relative_to(ROOT))
    if not source.is_file():
        result["extract_status"] = "missing_pdf"
        result["extract_error"] = str(source)
        return result
    if target.is_file() and target.stat().st_size > 1000:
        result["extract_status"] = "ok_cached"
        result["extract_error"] = ""
        return result
    proc = subprocess.run(
        [pdftotext, "-layout", "-enc", "UTF-8", str(source), str(target)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode == 0 and target.is_file() and target.stat().st_size > 1000:
        result["extract_status"] = "ok"
        result["extract_error"] = proc.stderr.strip()[:500]
    else:
        result["extract_status"] = "failed"
        result["extract_error"] = proc.stderr.strip()[:500]
    return result


def main() -> None:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise SystemExit("pdftotext not found")
    with QUEUE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    completed: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(extract, row, pdftotext): row for row in rows}
        for index, future in enumerate(as_completed(futures), 1):
            completed.append(future.result())
            if index % 20 == 0:
                print(f"extracted={index}/{len(rows)}")
    completed.sort(key=lambda row: int(row["rank"]))
    fields = list(rows[0]) + ["text_path", "extract_status", "extract_error"]
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(completed)
    ok = sum(row["extract_status"].startswith("ok") for row in completed)
    print(f"ok={ok} total={len(completed)} manifest={MANIFEST}")
    if ok != len(completed):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
