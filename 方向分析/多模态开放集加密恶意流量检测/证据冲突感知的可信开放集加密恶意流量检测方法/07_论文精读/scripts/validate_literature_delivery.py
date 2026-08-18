from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TARGET = Path(__file__).resolve().parents[2]
READING = TARGET / "07_论文精读"
WRITING = TARGET / "08_论文写作"


def csv_rows(path: Path) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    deep_queue_path = READING / "00_检索与筛选" / "120篇中文精读队列_2026-08-05.csv"
    checks = {
        "paper_pdfs": len(list((ROOT / "paper").glob("*.pdf"))),
        "inventory_rows": csv_rows(READING / "00_检索与筛选" / "全库筛选清单_2026-08-05.csv"),
        "deep_queue_rows": csv_rows(deep_queue_path),
        "structured_queue_rows": csv_rows(READING / "00_检索与筛选" / "300篇结构化细读队列_2026-08-05.csv"),
        "extracted_texts": len(list((READING / "03_全文抽取缓存").glob("[0-9][0-9]_*.txt"))),
        "deep_pool_texts": len(list((READING / "04_120篇全文抽取").glob("[0-9][0-9][0-9]_*.txt"))),
    }
    expected = {
        "paper_pdfs": 931,
        "inventory_rows": 931,
        "deep_queue_rows": 120,
        "structured_queue_rows": 300,
        "extracted_texts": 40,
        "deep_pool_texts": 120,
    }
    card_files = sorted((READING / "01_核心论文精读").glob("*中文精读证据卡_2026-08-05.md"))
    checks["chinese_cards"] = sum(
        1
        for card_file in card_files
        for line in card_file.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ") and line[3:4].isdigit()
    )
    expected["chinese_cards"] = 120
    for key, value in checks.items():
        print(f"{key}={value} expected={expected[key]}")
        if value != expected[key]:
            raise SystemExit(f"FAILED: {key}")

    required = [
        READING / "README.md",
        READING / "01_核心论文精读" / "第一批40篇中文精读证据卡_2026-08-05.md",
        READING / "02_证据矩阵" / "文献综合与算法纠偏结论_2026-08-05.md",
        WRITING / "README.md",
        WRITING / "01_写作规划" / "论文结构与论证主线_2026-08-05.md",
        WRITING / "02_证据映射" / "主张证据结果矩阵_2026-08-05.md",
        WRITING / "03_引用" / "待Zotero核验引用清单_2026-08-05.csv",
        WRITING / "04_实验缺口" / "写作前实验闭环清单_2026-08-05.md",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("FAILED missing files:\n" + "\n".join(missing))
    print(f"required_files={len(required)} status=ok")

    with deep_queue_path.open(encoding="utf-8-sig", newline="") as handle:
        deep_rows = list(csv.DictReader(handle))
    if any("中文精读v1完成" not in row["status"] for row in deep_rows):
        raise SystemExit("FAILED: deep queue contains unfinished status")
    print("deep_queue_status=status=ok")

    broken_links: list[str] = []
    for readme in (TARGET / "README.md", READING / "README.md", WRITING / "README.md"):
        for link in re.findall(r"\]\(([^)]+)\)", readme.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            if not (readme.parent / link).exists():
                broken_links.append(f"{readme}: {link}")
    if broken_links:
        raise SystemExit("FAILED broken links:\n" + "\n".join(broken_links))
    print("readme_links=status=ok")


if __name__ == "__main__":
    main()
