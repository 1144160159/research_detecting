#!/usr/bin/env python3
"""
Synchronize references with the current paper/ directory.

Inputs:
- paper/*.pdf
- code/papers_metadata.json
- existing 文献.md (only to preserve Code links)

Outputs:
- code/papers_metadata.json
- 文献.md
- 文献引用.txt
"""

from __future__ import annotations

import copy
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper"
METADATA_FILE = ROOT / "code" / "papers_metadata.json"
OUTPUT_MD = ROOT / "文献.md"
OUTPUT_TXT = ROOT / "文献引用.txt"

GENERATED_DATE = date.today().isoformat()


def strip_pdf_suffix(value: str) -> str:
    return value[:-4] if value.lower().endswith(".pdf") else value


def author(given: str, family: str) -> dict:
    return {"given": given, "family": family}


MANUAL_METADATA: dict[str, dict] = {
    "10.1109_TCE.2026.3656201.pdf": {
        "doi": "10.1109/tce.2026.3656201",
        "title": "XAI-EdgeSFL: Explainable Edge Intelligence With Adaptive Intrusion-Resilient Split Federated Learning for Consumer Healthcare Ecosystems",
        "year": 2026,
        "journal": "IEEE Transactions on Consumer Electronics",
        "volume": "72",
        "issue": "1",
        "pages": "2185-2196",
        "authors": [
            author("Yue", "Zhao"),
            author("Farhan", "Ullah"),
            author("Khalid", "Mahmood"),
            author("Saqib", "Saeed"),
            author("Nazeeruddin", "Mohammad"),
            author("Umar", "Raza"),
        ],
    },
    "10.1109_TDSC.2025.3621434_dup.pdf": {
        "doi": "10.1109/tdsc.2025.3621434",
        "title": "SParse: Semantic Tracking and Path Analysis for Attack Investigation in Real-Time",
        "year": 2026,
        "journal": "IEEE Transactions on Dependable and Secure Computing",
        "volume": "23",
        "issue": "2",
        "pages": "1865-1878",
        "authors": [
            author("Jie", "Ying"),
            author("Tiantian", "Zhu"),
            author("Wenrui", "Cheng"),
            author("Qixuan", "Yuan"),
            author("Mingjun", "Ma"),
            author("Chunlin", "Xiong"),
            author("Tieming", "Chen"),
            author("Mingqi", "Lv"),
            author("Yan", "Chen"),
        ],
    },
    "10.1109_TIFS.2025.3557741.pdf": {
        "doi": "10.1109/tifs.2025.3557741",
        "title": "GTAE-IDS: Graph Transformer-Based Autoencoder Framework for Real-Time Network Intrusion Detection",
        "year": 2025,
        "journal": "IEEE Transactions on Information Forensics and Security",
        "volume": "20",
        "issue": "",
        "pages": "4026-4041",
        "authors": [
            author("Jalal", "Ghadermazi"),
            author("Soumyadeep", "Hore"),
            author("Ankit", "Shah"),
            author("Nathaniel D.", "Bastian"),
        ],
    },
    "10.1109_TMLCN.2025.3555975.pdf": {
        "doi": "10.1109/tmlcn.2025.3555975",
        "title": "Spatio-Temporal Predictive Learning Using Crossover Attention for Communications and Networking Applications",
        "year": 2025,
        "journal": "IEEE Transactions on Machine Learning in Communications and Networking",
        "volume": "3",
        "issue": "",
        "pages": "479-490",
        "authors": [
            author("Ke", "He"),
            author("Thang Xuan", "Vu"),
            author("Lisheng", "Fan"),
            author("Symeon", "Chatzinotas"),
            author("Bjorn", "Ottersten"),
        ],
    },
    "10.1109_TMM.2025.3557682.pdf": {
        "doi": "10.1109/tmm.2025.3557682",
        "title": "Multimodal Evidential Learning for Open-World Weakly-Supervised Video Anomaly Detection",
        "year": 2025,
        "journal": "IEEE Transactions on Multimedia",
        "volume": "27",
        "issue": "",
        "pages": "3132-3143",
        "authors": [
            author("Chao", "Huang"),
            author("Weiliang", "Huang"),
            author("Qiuping", "Jiang"),
            author("Wei", "Wang"),
            author("Jie", "Wen"),
            author("Bob", "Zhang"),
        ],
    },
    "10.1109_TMM.2025.3632646.pdf": {
        "doi": "10.1109/tmm.2025.3632646",
        "title": "Multimodal Industrial Anomaly Detection via Attention-Enhanced Memory-Guided Network",
        "year": 2026,
        "journal": "IEEE Transactions on Multimedia",
        "volume": "28",
        "issue": "",
        "pages": "1133-1147",
        "authors": [
            author("Shuaibo", "Liu"),
            author("Xiaoli", "Luan"),
            author("Yueyang", "Li"),
        ],
    },
    "10.1109_TNNLS.2022.3184723.pdf": {
        "doi": "10.1109/tnnls.2022.3184723",
        "title": "Multiview Deep Anomaly Detection: A Systematic Exploration",
        "year": 2024,
        "journal": "IEEE Transactions on Neural Networks and Learning Systems",
        "volume": "35",
        "issue": "2",
        "pages": "1651-1665",
        "authors": [
            author("Siqi", "Wang"),
            author("Jiyuan", "Liu"),
            author("Guang", "Yu"),
            author("Xinwang", "Liu"),
            author("Sihang", "Zhou"),
            author("En", "Zhu"),
            author("Yuexiang", "Yang"),
            author("Jianping", "Yin"),
            author("Wenjing", "Yang"),
        ],
    },
    "10.1109_TNNLS.2023.3312655.pdf": {
        "doi": "10.1109/tnnls.2023.3312655",
        "title": "ARISE: Graph Anomaly Detection on Attributed Networks via Substructure Awareness",
        "year": 2024,
        "journal": "IEEE Transactions on Neural Networks and Learning Systems",
        "volume": "35",
        "issue": "12",
        "pages": "18172-18185",
        "authors": [
            author("Jingcan", "Duan"),
            author("Bin", "Xiao"),
            author("Siwei", "Wang"),
            author("Haifang", "Zhou"),
            author("Xinwang", "Liu"),
        ],
    },
    "10.1109_TNNLS.2024.3371109.pdf": {
        "doi": "10.1109/tnnls.2024.3371109",
        "title": "Fuzzy State-Driven Cross-Time Spatial Dependence Learning for Multivariate Time-Series Anomaly Detection",
        "year": 2025,
        "journal": "IEEE Transactions on Neural Networks and Learning Systems",
        "volume": "36",
        "issue": "3",
        "pages": "4532-4544",
        "authors": [
            author("Kun", "Zhu"),
            author("Pengyu", "Song"),
            author("Chunhui", "Zhao"),
        ],
    },
    "10.1109_TNNLS.2024.3439404.pdf": {
        "doi": "10.1109/tnnls.2024.3439404",
        "title": "AD-NEv: A Scalable Multilevel Neuroevolution Framework for Multivariate Anomaly Detection",
        "year": 2025,
        "journal": "IEEE Transactions on Neural Networks and Learning Systems",
        "volume": "36",
        "issue": "5",
        "pages": "8939-8953",
        "authors": [
            author("Marcin", "Pietron"),
            author("Dominik", "Zurek"),
            author("Kamil", "Faber"),
            author("Roberto", "Corizzo"),
        ],
    },
    "10.1109_TNSE.2025.3649259.pdf": {
        "doi": "10.1109/tnse.2025.3649259",
        "title": "Encrypted Traffic Detection in Resource Constrained IoT Networks: A Diffusion Model and LLM Integrated Framework",
        "year": 2026,
        "journal": "IEEE Transactions on Network Science and Engineering",
        "volume": "13",
        "issue": "",
        "pages": "5324-5344",
        "authors": [
            author("Hongjuan", "Li"),
            author("Hui", "Kang"),
            author("Chenbang", "Liu"),
            author("Ruolin", "Wang"),
            author("Jiahui", "Li"),
            author("Geng", "Sun"),
            author("Jiacheng", "Wang"),
            author("Shuang", "Liang"),
            author("Shiwen", "Mao"),
        ],
    },
    "10.1109_TNSE.2026.3672152.pdf": {
        "doi": "10.1109/tnse.2026.3672152",
        "title": "Silent-App-Aware Federated Machine Unlearning for Encrypted Network Traffic Classification",
        "year": 2026,
        "journal": "IEEE Transactions on Network Science and Engineering",
        "volume": "13",
        "issue": "",
        "pages": "7547-7564",
        "authors": [
            author("Zeyi", "Li"),
            author("Yuna", "Jiang"),
            author("Tianshun", "Wang"),
            author("Pan", "Wang"),
            author("Yimu", "Ji"),
        ],
    },
    "10.1109_TNSE.2026.3687554.pdf": {
        "doi": "10.1109/tnse.2026.3687554",
        "title": "LLM-HGAN: LLM-Enhanced Heterogeneous Graph Attention Networks for Advanced Persistent Threat Detection",
        "year": 2026,
        "journal": "IEEE Transactions on Network Science and Engineering",
        "volume": "13",
        "issue": "",
        "pages": "8892-8910",
        "authors": [
            author("Kun", "Lan"),
            author("Gaolei", "Li"),
            author("Wenkai", "Huang"),
            author("Jianhua", "Li"),
            author("Yantao", "Yu"),
        ],
    },
    "10.1109_TNSM.2023.3322861.pdf": {
        "doi": "10.1109/tnsm.2023.3322861",
        "title": "Classify Traffic Rather Than Flow: Versatile Multi-Flow Encrypted Traffic Classification With Flow Clustering",
        "year": 2024,
        "journal": "IEEE Transactions on Network and Service Management",
        "volume": "21",
        "issue": "2",
        "pages": "1446-1466",
        "authors": [
            author("Zihan", "Chen"),
            author("Guang", "Cheng"),
            author("Zijun", "Wei"),
            author("Dandan", "Niu"),
            author("Nan", "Fu"),
        ],
    },
    "10.1109_tsc.2026.3664705_mm1.pdf": {
        "doi": "10.1109/tsc.2026.3664705",
        "title": "Time Will Tell: Criss-Cross Transformer for Encrypted Traffic Analysis",
        "year": 2026,
        "journal": "IEEE Transactions on Services Computing",
        "volume": "19",
        "issue": "2",
        "pages": "1549-1562",
        "authors": [
            author("Hua", "Ding"),
            author("Lixing", "Chen"),
            author("Bo", "Zhang"),
            author("Shenghong", "Li"),
            author("Hao", "Peng"),
            author("Zhe", "Qu"),
            author("Yang", "Bai"),
        ],
    },
    "10.21203_rs.3.rs-6201348_v1.pdf": {
        "doi": "10.21203/rs.3.rs-6201348/v1",
        "title": "Unknown Intrusion Traffic Detection Method Based on Unsupervised Learning and Open-set Recognition",
        "year": 2025,
        "journal": "Research Square preprint",
        "volume": "",
        "issue": "",
        "pages": "",
        "authors": [
            author("Jun", "Fang"),
            author("Cunxiang", "Xie"),
        ],
    },
    "10.48550_arXiv.2307.11079.pdf": {
        "doi": "10.48550/arXiv.2307.11079",
        "title": "3D-IDS: Doubly Disentangled Dynamic Intrusion Detection",
        "year": 2023,
        "journal": "arXiv preprint",
        "volume": "",
        "issue": "",
        "pages": "",
        "authors": [
            author("Chenyang", "Qiu"),
            author("Yingsheng", "Geng"),
            author("Junrui", "Lu"),
            author("Kaida", "Chen"),
            author("Shitong", "Zhu"),
            author("Ya", "Su"),
            author("Guoshun", "Nan"),
            author("Can", "Zhang"),
            author("Junsong", "Fu"),
            author("Qimei", "Cui"),
            author("Xiaofeng", "Tao"),
        ],
    },
    "10.1016_j.knosys.2023.110626.pdf": {
        "doi": "10.1016/j.knosys.2023.110626",
        "title": "DI-NIDS: Domain invariant network intrusion detection system",
        "year": 2023,
        "journal": "Knowledge-Based Systems",
        "volume": "273",
        "issue": "",
        "pages": "110626",
        "authors": [
            author("Siamak", "Layeghy"),
            author("Mahsa", "Baktashmotlagh"),
            author("Marius", "Portmann"),
        ],
    },
    "10.1109_NOMS54207.2022.9789878.pdf": {
        "doi": "10.1109/NOMS54207.2022.9789878",
        "title": "E-GraphSAGE: A Graph Neural Network based Intrusion Detection System for IoT",
        "year": 2022,
        "journal": "NOMS 2022-2022 IEEE/IFIP Network Operations and Management Symposium",
        "volume": "",
        "issue": "",
        "pages": "",
        "authors": [
            author("Wai Weng", "Lo"),
            author("Siamak", "Layeghy"),
            author("Mohanad", "Sarhan"),
            author("Marcus", "Gallagher"),
            author("Marius", "Portmann"),
        ],
    },
    "10.14722_ndss.2022.24107.pdf": {
        "doi": "10.14722/ndss.2022.24107",
        "title": "EULER: Detecting Network Lateral Movement via Scalable Temporal Link Prediction",
        "year": 2022,
        "journal": "Proceedings 2022 Network and Distributed System Security Symposium",
        "volume": "",
        "issue": "",
        "pages": "",
        "authors": [
            author("Isaiah J.", "King"),
            author("H. Howie", "Huang"),
        ],
    },
    "CADE.pdf": {
        "doi": "",
        "title": "CADE: Detecting and Explaining Concept Drift Samples for Security Applications",
        "year": 2021,
        "journal": "30th USENIX Security Symposium",
        "volume": "",
        "issue": "",
        "pages": "2327-2344",
        "authors": [
            author("Limin", "Yang"),
            author("Wenbo", "Guo"),
            author("Qingying", "Hao"),
            author("Arridhana", "Ciptadi"),
            author("Ali", "Ahmadzadeh"),
            author("Xinyu", "Xing"),
            author("Gang", "Wang"),
        ],
    },
    "10.1109_JIOT.2023.3239872.pdf": {
        "doi": "10.1109/JIOT.2023.3239872",
        "title": "Heterogeneous Domain Adaptation for IoT Intrusion Detection: A Geometric Graph Alignment Approach",
        "year": 2023,
        "journal": "IEEE Internet of Things Journal",
        "volume": "10",
        "issue": "12",
        "pages": "10764-10777",
        "authors": [
            author("Jiashu", "Wu"),
            author("Hao", "Dai"),
            author("Yang", "Wang"),
            author("Kejiang", "Ye"),
            author("Chengzhong", "Xu"),
        ],
    },
    "10.48550_arXiv.2603.10051.pdf": {
        "doi": "10.48550/arXiv.2603.10051",
        "title": "Where Do Flow Semantics Reside? A Protocol-Native Tabular Pretraining Paradigm for Encrypted Traffic Classification",
        "year": 2026,
        "journal": "arXiv preprint",
        "volume": "",
        "issue": "",
        "pages": "",
        "authors": [
            author("Sizhe", "Huang"),
            author("Zitong", "Li"),
            author("Shujie", "Yang"),
        ],
    },
    "10.48550_arXiv.2504.04222.pdf": {
        "doi": "10.48550/arXiv.2504.04222",
        "title": "TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation",
        "year": 2025,
        "journal": "arXiv preprint",
        "volume": "",
        "issue": "",
        "pages": "",
        "authors": [
            author("Tianyu", "Cui"),
            author("Xinjie", "Lin"),
            author("Sijia", "Li"),
            author("Miao", "Chen"),
            author("Qilei", "Yin"),
            author("Qi", "Li"),
            author("Ke", "Xu"),
        ],
    },
}

COPY_METADATA_FROM_EXISTING = {
    "10.1109_tsc.2026.3671484_dup.pdf": "10.1109_TSC.2026.3671484.pdf",
    "10.1109_tnsm.2023.3332284_dup.pdf": "10.1109_TNSM.2023.3332284.pdf",
    "10.1109_tccn.2026.3695843_dup.pdf": "10.1109_TCCN.2026.3695843.pdf",
    "10.1109_tnsm.2026.3665647_dup.pdf": "10.1109_TNSM.2026.3665647.pdf",
    "10.1109_tdsc.2026.3677663_dup.pdf": "10.1109_TDSC.2026.3677663.pdf",
    "10.1109_tai.2024.3357791_dup.pdf": "10.1109_TAI.2024.3357791.pdf",
    "10.1109_TIFS.2026.3653575_dup.pdf": "10.1109_TIFS.2026.3653575.pdf",
    "10.1109_tnsm.2025.3642984_dup.pdf": "10.1109_TNSM.2025.3642984.pdf",
}


def filename_to_doi(filename: str) -> str:
    stem = strip_pdf_suffix(filename)
    idx = stem.find("_")
    if idx == -1:
        return stem
    return stem[:idx] + "/" + stem[idx + 1 :]


def clean_title(title: str, fallback: str) -> str:
    title = html.unescape(title or "")
    title = re.sub(r"<mml:math[^>]*>.*?</mml:math>", "", title, flags=re.DOTALL)
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    if not title or re.match(r"^10\.\d+[/.\s]", title):
        title = strip_pdf_suffix(fallback).replace("_", " ")
    return title


def format_author_ieee(authors: list[dict]) -> str:
    if not authors:
        return ""
    formatted = []
    for item in authors:
        given = item.get("given", "")
        family = item.get("family", "")
        initials = " ".join([part[0].upper() + "." for part in re.split(r"[\s.-]+", given) if part])
        if initials and family:
            formatted.append(f"{initials} {family}")
        elif family:
            formatted.append(family)
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    if len(formatted) <= 6:
        return ", ".join(formatted[:-1]) + ", and " + formatted[-1]
    return ", ".join(formatted[:6]) + ", et al."


def format_ieee_citation(paper: dict) -> str:
    authors = format_author_ieee(paper.get("authors", []))
    title = clean_title(paper.get("title", ""), paper.get("_filename", "Untitled"))
    parts = []
    if authors:
        parts.append(authors)
    parts.append(f'"{title}"')

    journal = paper.get("journal", "")
    if journal:
        parts.append(f"*{html.unescape(journal)}*")

    vol_info = []
    if paper.get("volume"):
        vol_info.append(f"vol. {paper['volume']}")
    if paper.get("issue"):
        vol_info.append(f"no. {paper['issue']}")
    if paper.get("pages"):
        vol_info.append(f"pp. {paper['pages']}")
    if vol_info:
        parts.append(", ".join(vol_info))

    if paper.get("year"):
        parts.append(str(paper["year"]))

    doi = paper.get("doi", "")
    if doi and doi.startswith("10."):
        parts.append(f"doi: {doi}")

    citation = ", ".join([part for part in parts if part])
    citation = re.sub(r",\s*,", ",", citation)
    citation = re.sub(r"\s+", " ", citation).strip()
    return citation.rstrip(",")


def parse_existing_code_links() -> dict[str, tuple[str, str]]:
    """Return filename -> (label, url) from the current Markdown bibliography."""
    if not OUTPUT_MD.exists():
        return {}
    links: dict[str, tuple[str, str]] = {}
    current_pdf = None
    pdf_re = re.compile(r"PDF: `([^`]+)`")
    code_re = re.compile(r"Code: `([^`]+)`\]\(([^)]+)\)")
    for line in OUTPUT_MD.read_text(encoding="utf-8").splitlines():
        pdf_match = pdf_re.search(line)
        if pdf_match:
            current_pdf = pdf_match.group(1)
            continue
        code_match = code_re.search(line)
        if current_pdf and code_match:
            links[current_pdf] = (code_match.group(1), code_match.group(2))
    return links


def sort_key(item: tuple[str, dict]) -> tuple[str, str, str]:
    filename, paper = item
    year = paper.get("year")
    year_key = str(year if year else "9999")
    authors = paper.get("authors") or []
    family = authors[0].get("family", "zzz") if authors else "zzz"
    return year_key, str(family), filename


def looks_like_doi_fallback(paper: dict) -> bool:
    title = clean_title(paper.get("title", ""), paper.get("_filename", ""))
    return bool(re.match(r"^10\.\d+", title, flags=re.IGNORECASE))


def needs_metadata_repair(paper: dict) -> bool:
    return (
        looks_like_doi_fallback(paper)
        or not paper.get("year")
        or not paper.get("journal")
        or not paper.get("authors")
    )


def main() -> None:
    with METADATA_FILE.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    pdf_files = sorted(path.name for path in PAPER_DIR.glob("*.pdf"))
    code_links = parse_existing_code_links()

    added = []
    repaired = []
    for filename in pdf_files:
        if filename in metadata:
            if filename in COPY_METADATA_FROM_EXISTING and needs_metadata_repair(metadata[filename]):
                source = COPY_METADATA_FROM_EXISTING[filename]
                if source not in metadata:
                    raise KeyError(f"Cannot copy metadata for {filename}: missing {source}")
                metadata[filename] = copy.deepcopy(metadata[source])
                metadata[filename]["_filename"] = filename
                repaired.append(filename)
            elif filename in MANUAL_METADATA and needs_metadata_repair(metadata[filename]):
                record = copy.deepcopy(MANUAL_METADATA[filename])
                record["_filename"] = filename
                metadata[filename] = record
                repaired.append(filename)
            continue
        if filename in COPY_METADATA_FROM_EXISTING:
            source = COPY_METADATA_FROM_EXISTING[filename]
            if source not in metadata:
                raise KeyError(f"Cannot copy metadata for {filename}: missing {source}")
            metadata[filename] = copy.deepcopy(metadata[source])
            metadata[filename]["_filename"] = filename
            added.append(filename)
            continue
        if filename in MANUAL_METADATA:
            record = copy.deepcopy(MANUAL_METADATA[filename])
            record["_filename"] = filename
            metadata[filename] = record
            added.append(filename)
            continue

        metadata[filename] = {
            "_filename": filename,
            "doi": filename_to_doi(filename),
            "title": strip_pdf_suffix(filename).replace("_", " "),
            "year": None,
            "journal": "",
            "volume": "",
            "issue": "",
            "pages": "",
            "authors": [],
        }
        added.append(filename)

    # Generate references from PDFs currently present in paper/.
    active_metadata = {filename: metadata[filename] for filename in pdf_files}
    sorted_papers = sorted(active_metadata.items(), key=sort_key)

    md_lines = [
        "# 参考文献列表 (IEEE格式)",
        "",
        f"**总计**: {len(sorted_papers)} 篇文献",
        f"**生成日期**: {GENERATED_DATE}",
        "",
        "---",
        "",
    ]
    txt_lines = [
        "参考文献列表 (IEEE格式)",
        f"总计: {len(sorted_papers)} 篇文献",
        f"生成日期: {GENERATED_DATE}",
    ]

    for idx, (filename, paper) in enumerate(sorted_papers, 1):
        citation = format_ieee_citation(paper)
        md_lines.append(f"**[{idx}]** {citation}")
        md_lines.append("")
        md_lines.append(f"> 📄 [PDF: `{filename}`](paper/{filename})")
        doi = paper.get("doi", "")
        if doi and doi.startswith("10."):
            md_lines.append(f"> 🔗 DOI: [{doi}](https://doi.org/{doi})")
        if filename in code_links:
            label, url = code_links[filename]
            md_lines.append(f"> 💻 [Code: `{label}`]({url})")
        md_lines.append("")
        txt_lines.append(f"[{idx}] {citation}")

    with METADATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        f.write("\n")
    OUTPUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    OUTPUT_TXT.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print(f"PDF files: {len(pdf_files)}")
    print(f"Metadata entries: {len(metadata)}")
    print(f"Added metadata entries: {len(added)}")
    if added:
        for filename in added:
            print(f"  + {filename}")
    print(f"Repaired metadata entries: {len(repaired)}")
    if repaired:
        for filename in repaired:
            print(f"  * {filename}")
    print(f"Written: {OUTPUT_MD.name}, {OUTPUT_TXT.name}")


if __name__ == "__main__":
    main()
