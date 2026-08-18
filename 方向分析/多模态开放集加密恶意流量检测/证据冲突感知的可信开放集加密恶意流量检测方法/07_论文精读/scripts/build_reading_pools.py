from __future__ import annotations

import csv
import re
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[5]
WORKFLOW = WORKSPACE / "zotero-workflow" / "local-index"
OUTPUT = Path(__file__).resolve().parents[1] / "00_检索与筛选"

KEEP = re.compile(
    r"encrypted|network traffic|intrusion|open.?set|open world|out.of.distribution|"
    r"malicious traffic|unknown attack|unknown class|zero.day|evidential|multi.?view|"
    r"multimodal|uncertainty|calibration|traffic classification|novelty detection|"
    r"Dirichlet|belief fusion|openmax|openauc|agnostophobia",
    re.I,
)
EXCLUDE = re.compile(
    r"medical|manufacturing|fault diagnosis|load monitoring|video anomaly|visual anomaly|"
    r"image anomaly|bearing|power system|remote sensing",
    re.I,
)

# 第一批已完成全文抽取的本地核心文献。“已抽取”不等于“已精读”。
EXTRACTED = {
    "paper\\10.1016_j.comnet.2024.110824.pdf",
    "paper\\10.1109_tifs.2025.3544067.pdf",
    "paper\\Dahanayaka2023_Robust_Open_Set_Traffic_Fingerprinting.pdf",
    "paper\\10.1109_TAI.2023.3244168.pdf",
    "paper\\10.1109_TIFS.2026.3653575.pdf",
    "paper\\10.1109_TIFS.2025.3612141.pdf",
    "paper\\10.1109_TNSM.2026.3693141.pdf",
    "paper\\10.1109_TIFS.2025.3608666.pdf",
    "paper\\10.1016_j.comnet.2024.110403.pdf",
    "paper\\10.48550_arXiv.1806.01768.pdf",
    "paper\\10.1145_3485447.3512217.pdf",
    "paper\\10.1609_aaai.v37i4.25674.pdf",
    "paper\\10.1016_j.comnet.2025.111184.pdf",
    "paper\\10.1016_j.array.2024.100349.pdf",
    "paper\\10.1109_TDSC.2026.3688655.pdf",
    "paper\\10.1038_s41598-025-08568-0.pdf",
    "paper\\10.1109_TON.2026.3674624.pdf",
    "paper\\10.1109_TIFS.2025.3574971.pdf",
    "paper\\10.1016_j.comnet.2023.109990.pdf",
    "paper\\10.1109_TON.2025.3648394.pdf",
    "paper\\10.1016_j.jpdc.2026.105240.pdf",
    "paper\\10.1109_TNET.2024.3413789.pdf",
    "paper\\10.1109_TDSC.2025.3649110.pdf",
    "paper\\10.1109_TNSM.2026.3652529.pdf",
    "paper\\10.1109_TCE.2026.3674715.pdf",
    "paper\\10.48550_arXiv.2505.21462.pdf",
    "paper\\10.1109_TIFS.2024.3515821.pdf",
    "paper\\10.1109_TIFS.2024.3426304.pdf",
    "paper\\10.1109_TNSM.2025.3565614.pdf",
    "paper\\10.1109_TNSM.2025.3600378.pdf",
    "paper\\10.3390_s24206507.pdf",
    "paper\\10.1016_j.comnet.2025.111499.pdf",
    "paper\\1511.06233.pdf",
    "paper\\1811.04110.pdf",
    "paper\\2110.06207.pdf",
    "paper\\2210.13458.pdf",
    "paper\\2204.11423.pdf",
    "paper\\2402.16897.pdf",
    "paper\\2412.18024.pdf",
    "paper\\10.48550_arXiv.2010.03759.pdf",
}

EXTERNAL = [
    ("paper\\1511.06233.pdf", "Towards Open Set Deep Networks", "10.48550/arXiv.1511.06233"),
    ("paper\\1811.04110.pdf", "Reducing Network Agnostophobia", "10.48550/arXiv.1811.04110"),
    ("paper\\2110.06207.pdf", "Open-Set Recognition: A Good Closed-Set Classifier is All You Need?", "10.48550/arXiv.2110.06207"),
    ("paper\\2210.13458.pdf", "OpenAUC: Towards AUC-Oriented Open-Set Recognition", "10.48550/arXiv.2210.13458"),
    ("paper\\2204.11423.pdf", "Trusted Multi-View Classification with Dynamic Evidential Fusion", "10.48550/arXiv.2204.11423"),
    ("paper\\2402.16897.pdf", "Reliable Conflictive Multi-View Learning", "10.48550/arXiv.2402.16897"),
    ("paper\\2412.18024.pdf", "Multimodal Learning with Uncertainty Quantification based on Discounted Belief Fusion", "10.48550/arXiv.2412.18024"),
]


def category(title: str) -> str:
    t = title.lower()
    if any(x in t for x in ("openauc", "openmax", "agnostophobia", "good closed-set", "energy-based")):
        return "开放集指标与基线"
    if any(x in t for x in ("evidential", "uncertainty", "belief fusion", "conflictive", "dirichlet", "confidence")):
        return "证据冲突与不确定性"
    if any(x in t for x in ("multimodal", "multi-modal", "multi-view", "dual-modal", "fusion")):
        return "多模态与融合"
    if any(x in t for x in ("open-set", "open set", "open world", "unknown", "novelty", "zero-day", "out-of-distribution")):
        return "开放集与未知检测"
    if any(x in t for x in ("bert", "transformer", "contrastive", "pre-train", "graph", "autoencoder")):
        return "流量表征与强基线"
    return "加密恶意流量检测"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["rank", "title", "category", "score", "doi", "file_path", "status", "source"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    score_path = max(WORKFLOW.glob("*_local_relevance_scores.csv"), key=lambda p: p.stat().st_mtime)
    with score_path.open(encoding="utf-8-sig", newline="") as handle:
        indexed = list(csv.DictReader(handle))

    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in indexed:
        path = item["file_path"]
        title = item["metadata_title"] or item["title_guess"] or Path(path).stem
        rows.append({
            "rank": "",
            "title": title,
            "category": category(title),
            "score": item.get("score", "0"),
            "doi": item.get("doi_guess", ""),
            "file_path": path,
            "status": "全文已抽取，中文精读中" if path in EXTRACTED else "已入库，待筛选",
            "source": "paper本地库",
        })
        seen.add(path.lower())

    for path, title, doi in EXTERNAL:
        if path.lower() not in seen:
            rows.append({
                "rank": "",
                "title": title,
                "category": category(title),
                "score": "100",
                "doi": doi,
                "file_path": path,
                "status": "全文已抽取，中文精读中",
                "source": "外部补缺后入paper库",
            })

    def score_value(row: dict[str, str]) -> int:
        try:
            return int(row["score"])
        except ValueError:
            return 0

    rows.sort(key=score_value, reverse=True)
    eligible = [r for r in rows if KEEP.search(r["title"]) and not EXCLUDE.search(r["title"])]
    extracted = [r for r in rows if r["file_path"] in EXTRACTED]

    def pool(size: int) -> list[dict[str, str]]:
        selected: list[dict[str, str]] = []
        used: set[str] = set()
        for row in extracted + eligible:
            key = row["file_path"].lower()
            if key in used:
                continue
            selected.append(dict(row))
            used.add(key)
            if len(selected) == size:
                break
        for rank, row in enumerate(selected, 1):
            row["rank"] = str(rank)
            if row["file_path"] not in EXTRACTED:
                row["status"] = "待中文全文精读" if size == 120 else "待结构化细读"
        return selected

    deep = pool(120)
    deep_paths = {row["file_path"].lower() for row in deep}
    for row in deep:
        row["status"] = "全文已抽取，中文精读v1完成，待Zotero页码/表号核验"
    structured = pool(300)
    for row in structured:
        if row["file_path"].lower() in deep_paths:
            row["status"] = "全文已抽取，中文精读v1完成，待Zotero页码/表号核验"
    for row in rows:
        if row["file_path"].lower() in deep_paths:
            row["status"] = "全文已抽取，中文精读v1完成，待Zotero页码/表号核验"
    for rank, row in enumerate(rows, 1):
        row["rank"] = str(rank)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT / "全库筛选清单_2026-08-05.csv", rows)
    write_csv(OUTPUT / "120篇中文精读队列_2026-08-05.csv", deep)
    write_csv(OUTPUT / "300篇结构化细读队列_2026-08-05.csv", structured)
    print(f"inventory={len(rows)} deep={len(deep)} structured={len(structured)} extracted={len(extracted)}")


if __name__ == "__main__":
    main()
