"""Build page-level extraction audit and temporary review packets for 71 PDFs.

This script does not decide scientific findings. It only validates PDFs,
extracts text page by page, locates likely method/evaluation/limitation pages,
and creates an auditable reading index for manual evidence-card synthesis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from pypdf import PdfReader


DIRECTION_REL = Path(
    "方向分析"
) / "复杂恶意攻击行为智能检测（APT、多阶段攻击链、异常行为基线）" / (
    "端点溯源图_日志_网络流联合APT攻击链重构"
)

EXTRAS: Sequence[Tuple[str, str]] = (
    (
        "EULER: Detecting Network Lateral Movement via Scalable Temporal Link Prediction, NDSS 2022",
        "paper/10.14722_ndss.2022.24107.pdf",
    ),
    (
        "End-to-End Attack Scene Reconstruction in a Host With Rules and Anomaly-Based Detection Models, IEEE TIFS 2025",
        "paper/10.1109_TIFS.2025.3588251.pdf",
    ),
    (
        "TeRed: Normal Behavior-Based Efficient Provenance Graph Reduction for Large-Scale Attack Forensics, IEEE TIFS 2025",
        "paper/10.1109_TIFS.2025.3601381.pdf",
    ),
    (
        "HADES: Detecting and Investigating Active Directory Attacks via Whole Network Provenance Analytics, IEEE TDSC 2025",
        "paper/10.1109_TDSC.2025.3611866.pdf",
    ),
    (
        "SParse: Semantic Tracking and Path Analysis for Attack Investigation in Real-Time, IEEE TDSC 2025",
        "paper/10.1109_TDSC.2025.3621434.pdf",
    ),
    (
        "Zoomer: An APT TTP Recognition System via Deep & Wide Provenance Graph Learning, IEEE TDSC 2025",
        "paper/10.1109_TDSC.2025.3646355.pdf",
    ),
    (
        "SAGA: Synthetic Audit Log Generation for APT Campaigns, IEEE TDSC 2025",
        "paper/10.1109_TDSC.2025.3640696.pdf",
    ),
)

SECTION_PATTERNS: Dict[str, re.Pattern[str]] = {
    "abstract": re.compile(r"^\s*(abstract)\s*$", re.I),
    "introduction": re.compile(r"^\s*(?:[ivx\d.]+\s+)?introduction\s*$", re.I),
    "background": re.compile(r"^\s*(?:[ivx\d.]+\s+)?(?:background|preliminar(?:y|ies))\s*$", re.I),
    "method": re.compile(
        r"^\s*(?:[ivx\d.]+\s+)?(?:method(?:ology)?|approach|design|architecture|system overview|our system)\s*$",
        re.I,
    ),
    "evaluation": re.compile(
        r"^\s*(?:[ivx\d.]+\s+)?(?:evaluation|experiments?|experimental evaluation|performance evaluation)\s*$",
        re.I,
    ),
    "discussion": re.compile(r"^\s*(?:[ivx\d.]+\s+)?discussion\s*$", re.I),
    "limitations": re.compile(r"^\s*(?:[ivx\d.]+\s+)?(?:limitations?|threats to validity)\s*$", re.I),
    "conclusion": re.compile(r"^\s*(?:[ivx\d.]+\s+)?conclusions?\s*$", re.I),
}

KEYWORDS: Dict[str, re.Pattern[str]] = {
    "dataset": re.compile(r"\b(dataset|data set|DARPA|CADETS|THEIA|TRACE|OpTC|StreamSpot|LANL)\b", re.I),
    "baseline": re.compile(r"\b(baseline|compare|comparison|state[- ]of[- ]the[- ]art)\b", re.I),
    "metric": re.compile(
        r"\b(precision|recall|F1|F-score|AUC|MCC|false positive|throughput|latency|memory|overhead)\b",
        re.I,
    ),
    "split": re.compile(r"\b(train|training|validation|test set|cross[- ]validation|split)\b", re.I),
    "limitation": re.compile(r"\b(limitation|threats? to validity|future work|does not|cannot)\b", re.I),
    "code_data": re.compile(r"\b(GitHub|source code|code is available|data is available|artifact)\b", re.I),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def clean_markdown(text: str) -> str:
    return re.sub(r"[*`]", "", text).strip()


def parse_manifest(path: Path) -> List[Tuple[str, str]]:
    records: List[Tuple[str, str]] = []
    row_re = re.compile(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*`(paper/[^`]+\.pdf)`\s*\|")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = row_re.match(line)
        if match:
            records.append((clean_markdown(match.group(2)), match.group(3)))
    if len(records) != 64:
        raise RuntimeError("expected 64 manifest records, got {}".format(len(records)))
    return records


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        value = " ".join(line.split())
        if len(value) >= 12:
            return value[:240]
    return ""


def locate_sections(pages: Sequence[str]) -> Dict[str, List[int]]:
    found: Dict[str, List[int]] = {key: [] for key in SECTION_PATTERNS}
    for index, text in enumerate(pages, start=1):
        for line in text.splitlines():
            normalized = " ".join(line.split())
            if len(normalized) > 80:
                continue
            for name, pattern in SECTION_PATTERNS.items():
                if pattern.match(normalized):
                    found[name].append(index)
    return {key: value for key, value in found.items() if value}


def locate_keywords(pages: Sequence[str]) -> Dict[str, List[int]]:
    return {
        name: [index for index, text in enumerate(pages, start=1) if pattern.search(text)]
        for name, pattern in KEYWORDS.items()
    }


def choose_review_pages(
    page_count: int,
    sections: Dict[str, List[int]],
    keywords: Dict[str, List[int]],
) -> List[int]:
    chosen = {1, 2, page_count}
    for name in ("method", "evaluation", "limitations", "discussion", "conclusion"):
        if sections.get(name):
            chosen.add(sections[name][0])
            if sections[name][0] + 1 <= page_count:
                chosen.add(sections[name][0] + 1)
    for name in ("dataset", "metric", "baseline", "split", "limitation"):
        pages = keywords.get(name, [])
        if pages:
            chosen.add(pages[0])
    return sorted(page for page in chosen if 1 <= page <= page_count)[:14]


def write_review_packet(path: Path, title: str, pages: Sequence[str], selected: Iterable[int]) -> None:
    chunks = ["TITLE: {}".format(title)]
    for page_number in selected:
        chunks.append("\n===== PDF PAGE {} =====\n{}".format(page_number, pages[page_number - 1]))
    path.write_text("\n".join(chunks), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--temp-root", type=Path)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    direction = workspace / DIRECTION_REL
    review_root = direction / "08_论文精读"
    index_root = review_root / "_索引"
    index_root.mkdir(parents=True, exist_ok=True)
    temp_root = (
        args.temp_root.resolve()
        if args.temp_root
        else Path(tempfile.gettempdir()) / "eacr_apt_deep_read_20260729"
    )
    temp_root.mkdir(parents=True, exist_ok=True)

    manifest = direction / "05_文献与证据" / "补充顶会顶刊PDF下载清单_20260729.md"
    records = parse_manifest(manifest) + list(EXTRAS)
    if len(records) != 71:
        raise RuntimeError("expected 71 papers, got {}".format(len(records)))

    audit: List[dict] = []
    packet_index: List[dict] = []
    seen_paths = set()
    for number, (title, relative_path) in enumerate(records, start=1):
        paper_id = "L{:02d}".format(number)
        if relative_path in seen_paths:
            raise RuntimeError("duplicate PDF path: {}".format(relative_path))
        seen_paths.add(relative_path)
        pdf_path = workspace / Path(relative_path)
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)
        with pdf_path.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise RuntimeError("invalid PDF header: {}".format(pdf_path))

        reader = PdfReader(str(pdf_path))
        page_texts = [(page.extract_text() or "") for page in reader.pages]
        nonempty = sum(1 for text in page_texts if len(text.strip()) >= 100)
        sections = locate_sections(page_texts)
        keywords = locate_keywords(page_texts)
        selected = choose_review_pages(len(page_texts), sections, keywords)
        packet_path = temp_root / "{}.txt".format(paper_id)
        write_review_packet(packet_path, title, page_texts, selected)

        record = {
            "paper_id": paper_id,
            "title": title,
            "pdf_path": relative_path,
            "pages": len(page_texts),
            "sha256": sha256(pdf_path),
            "pages_with_text": nonempty,
            "text_page_ratio": round(nonempty / max(1, len(page_texts)), 4),
            "text_chars": sum(len(text) for text in page_texts),
            "section_pages": sections,
            "keyword_pages": keywords,
            "selected_review_pages": selected,
            "first_page_preview": first_nonempty_line(page_texts[0] if page_texts else ""),
            "temporary_review_packet": str(packet_path),
        }
        audit.append(record)
        packet_index.append(
            {
                "paper_id": paper_id,
                "title": title,
                "packet": str(packet_path),
                "selected_review_pages": selected,
            }
        )
        print(
            "[{}/71] {} pages={} text_ratio={:.2f} packet_pages={}".format(
                paper_id, title[:70], len(page_texts), record["text_page_ratio"], selected
            )
        )

    (index_root / "全文提取审计.json").write_text(
        json.dumps(
            {
                "paper_count": len(audit),
                "temporary_packet_root": str(temp_root),
                "papers": audit,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    with (index_root / "阅读定位包.jsonl").open("w", encoding="utf-8") as stream:
        for record in packet_index:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    print("AUDIT={}".format(index_root / "全文提取审计.json"))
    print("PACKETS={}".format(temp_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

