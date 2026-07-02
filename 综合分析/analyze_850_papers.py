# -*- coding: utf-8 -*-
"""
Generate a comprehensive analysis package for the 850-paper corpus.

Inputs:
- 文献.md
- paper/*.pdf
- source/_code_search/code_repositories_index.json (optional)

Outputs are written under 综合分析/.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "综合分析"
DATA = OUT / "_data"
TEXT_CACHE = DATA / "text_cache"
CHARTS = OUT / "图表"


CATEGORIES = [
    {
        "name": "加密流量分类与应用识别",
        "keywords": [
            "encrypted traffic", "traffic classification", "application classification",
            "app fingerprint", "fingerprinting", "website fingerprint", "tor", "vpn",
            "doh", "quic", "tls", "ssl", "flow sequence", "flow representation",
            "packet", "flow", "mobile-app", "anonymous traffic", "proxy traffic",
        ],
        "summary": "围绕加密/匿名/代理流量的应用识别、服务分类、网站指纹和行为识别。",
    },
    {
        "name": "恶意流量、暗网与攻击检测",
        "keywords": [
            "malicious traffic", "malicious encrypted", "darknet", "botnet", "attack",
            "ddos", "malware traffic", "command and control", "c2", "tunnel",
            "phishing", "abuse", "threat detection", "malicious platform",
        ],
        "summary": "面向恶意流量、暗网、隧道、僵尸网络、DDoS 和攻击活动的检测与刻画。",
    },
    {
        "name": "入侵检测与网络异常检测",
        "keywords": [
            "intrusion detection", "ids", "nids", "network anomaly", "anomaly detection",
            "network intrusion", "zero-day", "unknown attack", "abnormal",
            "industrial control", "programmable networks", "software-defined network",
            "sdn", "ivn", "in-vehicle network",
        ],
        "summary": "面向网络入侵、未知攻击、异常行为和安全事件的检测模型与系统。",
    },
    {
        "name": "网络流量监测、测量与工具",
        "keywords": [
            "traffic monitoring", "network monitoring", "measurement", "netflow",
            "traffic analysis tools", "packet capture", "traffic capture", "monitoring tools",
            "real-time monitoring", "network measurement", "traffic analysis",
        ],
        "summary": "关注流量采集、监测、测量、工具链、NetFlow 和高性能网络观测。",
    },
    {
        "name": "IoT、车联网、工业互联网与边缘安全",
        "keywords": [
            "iot", "internet of things", "iiot", "industrial internet", "v2x",
            "vehicular", "vehicle", "smart grid", "edge gateway", "edge", "wsn",
            "wireless sensor", "uav", "drone", "consumer electronics", "5g",
            "smart home", "cyber-physical", "cps",
        ],
        "summary": "面向物联网、车联网、工业互联网、边缘设备和 5G 场景的安全检测。",
    },
    {
        "name": "图学习、知识图谱与威胁情报",
        "keywords": [
            "graph", "gnn", "gcn", "graphsage", "graph neural", "knowledge graph",
            "threat intelligence", "cyber threat intelligence", "provenance",
            "entity alignment", "entity relation", "attack graph", "heterogeneous graph",
        ],
        "summary": "利用图神经网络、知识图谱、威胁情报和溯源图表达复杂关系。",
    },
    {
        "name": "时序、日志、KPI 与云原生异常检测",
        "keywords": [
            "time series", "timeseries", "log anomaly", "log-based", "kpi",
            "microservice", "cloud", "multivariate time", "temporal", "event log",
            "system logs", "service", "root cause",
        ],
        "summary": "针对日志、KPI、微服务、云平台和多变量时序的异常检测与诊断。",
    },
    {
        "name": "多媒体、医学、遥感与视频异常检测",
        "keywords": [
            "video anomaly", "medical", "image anomaly", "hyperspectral",
            "remote sensing", "segmentation", "surveillance", "mri", "pet",
            "cloth-changing", "visual", "image", "video", "object detection",
        ],
        "summary": "来自视觉、医学影像、遥感高光谱和视频异常检测方向的可迁移方法。",
    },
    {
        "name": "联邦学习、隐私保护与分布式协同",
        "keywords": [
            "federated", "privacy-preserving", "differential privacy", "collaborative",
            "distributed", "split learning", "secure aggregation", "blockchain",
            "zero trust", "honeypot-based", "incentivized",
        ],
        "summary": "关注隐私保护、跨域协同、联邦学习、区块链和分布式安全检测。",
    },
    {
        "name": "数据集、基准、综述与开源工具",
        "keywords": [
            "dataset", "benchmark", "survey", "review", "systematic literature",
            "transparency report", "state of", "tools", "taxonomy", "corpus",
            "labeled public", "annual report", "benchmarking",
        ],
        "summary": "提供数据集、基准评测、综述、工具和行业报告，为系统选型提供依据。",
    },
    {
        "name": "基础理论、密码协议与安全机制",
        "keywords": [
            "cryptography", "public-key", "digital signatures", "rsa", "protocol",
            "authentication", "encryption", "block cipher", "key exchange",
            "network architectures", "security protocol", "attribution",
        ],
        "summary": "偏基础理论、密码协议、网络体系结构和安全机制背景。",
    },
    {
        "name": "其他AI安全与跨域异常检测",
        "keywords": [
            "anomaly", "classification", "deep learning", "machine learning",
            "transformer", "autoencoder", "contrastive", "self-supervised",
        ],
        "summary": "不完全属于网络流量，但其 AI 异常检测方法可作为迁移参考。",
    },
]


INNOVATIONS = [
    ("表征学习、预训练与Transformer", [
        "transformer", "bert", "pre-training", "pretrained", "masked autoencoder",
        "representation", "embedding", "language model", "foundation model",
        "attention", "sequence model", "flow transformer",
    ]),
    ("图神经网络与关系建模", [
        "graph neural", "gnn", "gcn", "graphsage", "graph attention", "knowledge graph",
        "heterogeneous graph", "temporal graph", "provenance graph", "graph learning",
    ]),
    ("多模态、多视图与特征融合", [
        "multi-modal", "multimodal", "multi-view", "dual-modal", "fusion",
        "spatio-temporal", "spatial-temporal", "multi-source", "cross-modal",
    ]),
    ("自监督、对比学习与少样本学习", [
        "self-supervised", "contrastive", "few-shot", "zero-shot", "semi-supervised",
        "weakly supervised", "label-free", "pseudo-label", "minority detection",
    ]),
    ("生成式增强、GAN与扩散模型", [
        "gan", "generative", "cgan", "diffusion", "data augmentation",
        "synthetic", "adversarial generation", "vae", "variational",
    ]),
    ("联邦学习、隐私保护与协同训练", [
        "federated", "privacy-preserving", "differential privacy", "collaborative",
        "distributed", "secure aggregation", "blockchain", "zero trust",
    ]),
    ("在线、增量、开放集与概念漂移", [
        "online", "incremental", "concept drift", "open set", "open-set",
        "out-of-distribution", "ood", "evolving", "auto-updating", "continual",
    ]),
    ("可解释性、规则抽取与因果分析", [
        "explainable", "explain", "interpret", "rule extraction", "causal",
        "counterfactual", "attribution", "accountability", "xai", "prototype",
    ]),
    ("轻量化、实时与高性能部署", [
        "lightweight", "real-time", "fast", "efficient", "scalable", "terabit",
        "edge", "resource", "low latency", "high-performance", "online classification",
    ]),
    ("鲁棒性、对抗防御与可信检测", [
        "robust", "adversarial", "poisoning", "evasion", "certified robustness",
        "uncertainty", "defense", "anti-interference", "trust",
    ]),
    ("数据集、基准、工具与系统化评测", [
        "dataset", "benchmark", "survey", "tool", "framework", "system",
        "corpus", "labeled public", "evaluation", "measurement",
    ]),
]


SCIENCE_PROBLEMS = [
    ("加密与隐私保护造成可观测特征缺失", [
        "encrypted", "tls", "ssl", "vpn", "tor", "quic", "doh", "privacy",
        "anonymous", "fingerprint", "decryption",
    ]),
    ("标签稀缺、类别不平衡与长尾攻击", [
        "few-shot", "zero-shot", "semi-supervised", "weakly", "label", "imbalance",
        "minority", "small-sample", "low-quality labeled", "long-tail",
    ]),
    ("域迁移、概念漂移与真实网络分布变化", [
        "domain adaptation", "concept drift", "evolving", "dynamic", "transfer",
        "cross-domain", "distribution", "out-of-distribution", "generalization",
    ]),
    ("高速流量实时检测与资源约束", [
        "real-time", "online", "fast", "lightweight", "scalable", "terabit",
        "edge", "low latency", "resource", "efficient",
    ]),
    ("多源异构数据融合与上下文建模", [
        "multi-modal", "multi-view", "fusion", "heterogeneous", "knowledge graph",
        "graph", "provenance", "spatio-temporal", "context",
    ]),
    ("模型可解释、可信与可审计", [
        "explain", "interpret", "xai", "rule extraction", "counterfactual",
        "prototype", "attribution", "accountability", "trust",
    ]),
    ("对抗规避、污染与鲁棒性", [
        "adversarial", "evasion", "poisoning", "robust", "defense",
        "certified", "anti-interference", "attack generation",
    ]),
    ("数据集代表性、标准化评测与可复现", [
        "dataset", "benchmark", "survey", "review", "labeled public", "corpus",
        "evaluation", "reproduc", "tools", "transparency report",
    ]),
    ("边缘、IoT、车联网与工业场景约束", [
        "iot", "iiot", "v2x", "vehicular", "vehicle", "industrial", "edge",
        "smart grid", "wsn", "drone", "5g", "smart home",
    ]),
    ("开放世界未知攻击与误报控制", [
        "unknown", "zero-day", "open set", "open-set", "novel attack",
        "false positive", "false alarm", "anomaly-free", "unknown attacks",
    ]),
]


RELEVANCE_KEYWORDS = [
    "traffic", "flow", "packet", "encrypted", "network", "intrusion", "ids",
    "nids", "malicious", "darknet", "botnet", "tls", "vpn", "tor", "quic",
    "doh", "netflow", "monitoring", "anomaly detection", "attack", "ddos",
]


def ensure_dirs() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    TEXT_CACHE.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse_bibliography() -> list[dict]:
    path = ROOT / "文献.md"
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        m = re.match(r"^\*\*\[(\d+)\]\*\*\s+(.*)", line)
        if m:
            if current:
                entries.append(current)
            num = int(m.group(1))
            citation = m.group(2).strip()
            current = {
                "num": num,
                "citation": citation,
                "title": extract_title(citation),
                "year": extract_year(citation),
                "doi": extract_doi(citation),
                "venue": extract_venue(citation),
                "pdf": "",
            }
            continue
        if current is None:
            continue
        if "> PDF:" in line:
            m_pdf = re.search(r"\((paper/[^)]+)\)", line)
            if m_pdf:
                current["pdf"] = m_pdf.group(1)
        if "> DOI:" in line and not current.get("doi"):
            m_doi = re.search(r"https://doi\.org/([^\)]+)", line)
            if m_doi:
                current["doi"] = m_doi.group(1).strip()
    if current:
        entries.append(current)
    return entries


def extract_title(citation: str) -> str:
    m = re.search(r'"([^"]+)"', citation)
    if m:
        return clean_spaces(m.group(1))
    before_doi = re.split(r",\s*doi:\s*", citation, flags=re.I)[0]
    before_venue = before_doi.split("*")[0].strip(" ,")
    # Remove leading author-like fragments for no-quote entries when possible.
    parts = [p.strip() for p in before_venue.split(",") if p.strip()]
    if len(parts) > 1:
        return clean_spaces(parts[-1])
    return clean_spaces(before_venue)


def extract_year(citation: str) -> int | None:
    years = [int(x) for x in re.findall(r"\b(19\d{2}|20\d{2})\b", citation)]
    years = [y for y in years if 1970 <= y <= 2026]
    return years[-1] if years else None


def extract_doi(citation: str) -> str:
    m = re.search(r"doi:\s*([^\s]+)", citation, flags=re.I)
    return (m.group(1).strip().rstrip(".") if m else "")


def extract_venue(citation: str) -> str:
    venues = re.findall(r"\*([^*]+)\*", citation)
    return clean_spaces(venues[0]) if venues else ""


def extract_pdf_text(entry: dict, max_pages: int = 3, timeout_sec: int = 18) -> dict:
    num = entry["num"]
    cache = TEXT_CACHE / f"{num:03d}.txt"
    err_cache = TEXT_CACHE / f"{num:03d}.err"
    if cache.exists():
        return {"num": num, "text": cache.read_text(encoding="utf-8", errors="ignore"), "error": ""}
    pdf_rel = entry.get("pdf") or ""
    if not pdf_rel:
        err_cache.write_text("missing pdf path", encoding="utf-8")
        return {"num": num, "text": "", "error": "missing pdf path"}
    pdf_path = ROOT / pdf_rel
    if not pdf_path.exists():
        err_cache.write_text(f"missing file: {pdf_path}", encoding="utf-8")
        return {"num": num, "text": "", "error": "missing pdf file"}
    cmd = [
        "pdftotext",
        "-enc",
        "UTF-8",
        "-layout",
        "-f",
        "1",
        "-l",
        str(max_pages),
        str(pdf_path),
        "-",
    ]
    try:
        cp = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
        )
        text = cp.stdout or ""
        if not text.strip():
            # Fallback without layout. Some PDFs behave better this way.
            cmd2 = [
                "pdftotext",
                "-enc",
                "UTF-8",
                "-f",
                "1",
                "-l",
                str(max_pages),
                str(pdf_path),
                "-",
            ]
            cp = subprocess.run(
                cmd2,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_sec,
            )
            text = cp.stdout or ""
        cache.write_text(text[:16000], encoding="utf-8")
        if cp.stderr:
            err_cache.write_text(cp.stderr[-2000:], encoding="utf-8")
        return {"num": num, "text": text[:16000], "error": cp.stderr[-500:] if cp.stderr else ""}
    except subprocess.TimeoutExpired:
        err_cache.write_text("timeout", encoding="utf-8")
        return {"num": num, "text": "", "error": "timeout"}
    except Exception as exc:  # noqa: BLE001
        err_cache.write_text(str(exc), encoding="utf-8")
        return {"num": num, "text": "", "error": str(exc)}


def extract_abstract(text: str) -> str:
    if not text:
        return ""
    probe = text[:12000]
    patterns = [
        r"(?is)\babstract\b\s*[-—:.\n\r]*\s*(.*?)(?:\bindex\s+terms\b|\bkeywords\b|\bkey\s+words\b|\b1\.?\s+introduction\b|\bi\.?\s+introduction\b|\bintroduction\b)",
        r"(?is)\bsummary\b\s*[-—:.\n\r]*\s*(.*?)(?:\bkeywords\b|\bintroduction\b)",
    ]
    for pat in patterns:
        m = re.search(pat, probe)
        if m:
            value = clean_spaces(m.group(1))
            value = re.sub(r"^(abstract|summary)\s*[:.-]*\s*", "", value, flags=re.I)
            if 50 <= len(value) <= 5000:
                return value[:1800]
    return ""


def extract_keywords(text: str) -> str:
    if not text:
        return ""
    probe = text[:12000]
    m = re.search(
        r"(?is)\b(?:index\s+terms|keywords|key\s+words)\b\s*[-—:.\n\r]*\s*(.*?)(?:\b1\.?\s+introduction\b|\bi\.?\s+introduction\b|\bintroduction\b|\n\s*\n)",
        probe,
    )
    if not m:
        return ""
    return clean_spaces(m.group(1))[:600]


def weighted_keyword_score(text: str, title: str, keywords: list[str]) -> int:
    low = (text or "").lower()
    title_low = (title or "").lower()
    score = 0
    for kw in keywords:
        k = kw.lower()
        if k in title_low:
            score += 4 if len(k) > 4 else 2
        if k in low:
            score += 1
    return score


def assign_category(entry: dict, abstract: str, kw_text: str) -> tuple[str, list[str], dict[str, int]]:
    title = entry.get("title", "")
    text = " ".join([title, abstract, kw_text, entry.get("venue", "")])
    scores = {
        cat["name"]: weighted_keyword_score(text, title, cat["keywords"])
        for cat in CATEGORIES
    }
    # Manual boosts for common ambiguous cases.
    low_title = title.lower()
    if any(x in low_title for x in ["hyperspectral", "medical", "video anomaly", "image anomaly"]):
        scores["多媒体、医学、遥感与视频异常检测"] += 8
    if any(x in low_title for x in ["encrypted traffic", "traffic classification", "website fingerprint"]):
        scores["加密流量分类与应用识别"] += 8
    if any(x in low_title for x in ["intrusion detection", "network anomaly", "unknown attacks"]):
        scores["入侵检测与网络异常检测"] += 8
    if any(x in low_title for x in ["dataset", "benchmark", "survey", "review"]):
        scores["数据集、基准、综述与开源工具"] += 8
    primary = max(scores.items(), key=lambda item: (item[1], -list(scores).index(item[0])))[0]
    if scores[primary] == 0:
        primary = "其他AI安全与跨域异常检测"
    secondaries = [
        name
        for name, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
        if name != primary and score >= 4
    ][:2]
    return primary, secondaries, scores


def assign_multilabel(text: str, title: str, definitions: list[tuple[str, list[str]]], default: str) -> list[str]:
    scores = []
    for name, kws in definitions:
        score = weighted_keyword_score(text, title, kws)
        if score >= 2:
            scores.append((name, score))
    if not scores:
        return [default]
    return [name for name, _ in sorted(scores, key=lambda item: item[1], reverse=True)[:4]]


def method_keywords(title: str, abstract: str) -> list[str]:
    combined = f"{title} {abstract[:500]}"
    candidates = []
    for m in re.findall(r"\b[A-Z][A-Za-z0-9]*(?:[-_/][A-Za-z0-9]+)*\b", combined):
        if len(m) >= 3 and m.lower() not in {"the", "and", "for", "with", "this", "that"}:
            candidates.append(m)
    for phrase in [
        "Transformer", "BERT", "GNN", "GCN", "contrastive learning", "federated learning",
        "autoencoder", "GAN", "diffusion", "knowledge graph", "time series",
    ]:
        if phrase.lower() in combined.lower():
            candidates.append(phrase)
    seen = set()
    out = []
    for item in candidates:
        key = item.lower()
        if key not in seen:
            out.append(item)
            seen.add(key)
        if len(out) >= 8:
            break
    return out


def relevance(entry: dict, category: str, innovations: list[str], abstract: str) -> tuple[str, int, str]:
    text = f"{entry.get('title', '')} {abstract}".lower()
    score = 0
    for kw in RELEVANCE_KEYWORDS:
        if kw in text:
            score += 2 if kw in entry.get("title", "").lower() else 1
    if category in {
        "加密流量分类与应用识别",
        "恶意流量、暗网与攻击检测",
        "入侵检测与网络异常检测",
        "网络流量监测、测量与工具",
    }:
        score += 6
    if category in {
        "IoT、车联网、工业互联网与边缘安全",
        "图学习、知识图谱与威胁情报",
        "联邦学习、隐私保护与分布式协同",
        "时序、日志、KPI 与云原生异常检测",
    }:
        score += 3
    if any("实时" in x or "轻量化" in x or "图神经" in x for x in innovations):
        score += 1
    if score >= 10:
        tier = "强相关"
    elif score >= 5:
        tier = "中相关"
    else:
        tier = "弱相关"
    reason = {
        "强相关": "可直接支撑网络流量检测、加密流量识别、入侵/恶意流量检测或监测系统设计。",
        "中相关": "方法或场景可迁移到流量检测系统，如图学习、联邦协同、日志时序或边缘安全。",
        "弱相关": "主要提供背景理论、跨域异常检测方法或数据/综述参考，需二次适配。",
    }[tier]
    return tier, score, reason


def load_code_index() -> dict[int, list[dict]]:
    path = ROOT / "source/_code_search/code_repositories_index.json"
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}
    by_num: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        num = row.get("num")
        if isinstance(num, int):
            by_num[num].append(row)
    return by_num


def code_summary(num: int, code_by_num: dict[int, list[dict]]) -> tuple[str, str]:
    rows = code_by_num.get(num, [])
    if not rows:
        return "未发现", ""
    downloaded = [r for r in rows if r.get("status") == "downloaded"]
    partial = [r for r in rows if r.get("status") == "partial"]
    failed = [r for r in rows if r.get("status") in {"failed", "timeout"}]
    if downloaded:
        repos = "; ".join(
            f"{r.get('repo') or r.get('repo_full')} -> {r.get('target')}" for r in downloaded[:3]
        )
        return "已下载", repos
    if partial:
        return "部分下载", "; ".join(r.get("repo", "") for r in partial[:3])
    if failed:
        return "候选不可访问", "; ".join(r.get("repo", "") for r in failed[:3])
    return "有候选", "; ".join(r.get("repo", "") for r in rows[:3])


def chinese_interpretation(paper: dict) -> dict:
    title = paper["title"]
    category = paper["category"]
    innovations = paper["innovations"]
    problems = paper["science_problems"]
    methods = paper["method_keywords"]
    relevance_tier = paper["relevance_tier"]
    code_status = paper["code_status"]
    abstract = paper.get("abstract", "")

    abstract_hint = ""
    if abstract:
        abstract_hint = clean_spaces(abstract)[:260]
    else:
        abstract_hint = "PDF 前几页未稳定抽取到摘要，以下解读主要依据题名、发表信息和关键词规则。"

    overview = (
        f"该文聚焦“{category}”方向。题名显示其核心对象是“{title}”，"
        f"主要围绕{problems[0]}展开，适合作为{relevance_tier}文献纳入项目知识库。"
    )
    innovation = "、".join(innovations[:3])
    method = "、".join(methods[:6]) if methods else "题名未显式给出模型缩写"
    usage = {
        "强相关": "建议优先精读，可用于系统模块设计、特征工程、模型选型或实验对比。",
        "中相关": "建议按方法模块选读，提炼可迁移的训练策略、评测方法或部署约束。",
        "弱相关": "建议作为背景、综述、跨域方法或理论依据引用。",
    }[relevance_tier]
    if code_status == "已下载":
        usage += " 已发现并下载代码，可进一步复现实验或抽取工程实现。"
    return {
        "overview": overview,
        "abstract_hint": abstract_hint,
        "innovation": innovation,
        "method": method,
        "usage": usage,
    }


def enrich_papers(entries: list[dict], text_results: dict[int, dict]) -> list[dict]:
    code_by_num = load_code_index()
    papers = []
    for entry in entries:
        text = text_results.get(entry["num"], {}).get("text", "")
        abstract = extract_abstract(text)
        kw_text = extract_keywords(text)
        category, secondary, category_scores = assign_category(entry, abstract, kw_text)
        combined = " ".join([entry.get("title", ""), abstract, kw_text, entry.get("venue", "")])
        innovations = assign_multilabel(combined, entry.get("title", ""), INNOVATIONS, "应用场景与系统化验证")
        science = assign_multilabel(combined, entry.get("title", ""), SCIENCE_PROBLEMS, "开放世界未知攻击与误报控制")
        methods = method_keywords(entry.get("title", ""), abstract)
        rel_tier, rel_score, rel_reason = relevance(entry, category, innovations, abstract)
        c_status, c_repos = code_summary(entry["num"], code_by_num)
        paper = {
            **entry,
            "abstract": abstract,
            "keywords": kw_text,
            "text_extract_error": text_results.get(entry["num"], {}).get("error", ""),
            "category": category,
            "secondary_categories": secondary,
            "category_scores": category_scores,
            "innovations": innovations,
            "science_problems": science,
            "method_keywords": methods,
            "relevance_tier": rel_tier,
            "relevance_score": rel_score,
            "relevance_reason": rel_reason,
            "code_status": c_status,
            "code_repositories": c_repos,
        }
        paper["interpretation"] = chinese_interpretation(paper)
        papers.append(paper)
    return papers


def write_json_csv(papers: list[dict]) -> None:
    (DATA / "papers_enriched.json").write_text(
        json.dumps(papers, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with (DATA / "papers_enriched.jsonl").open("w", encoding="utf-8") as f:
        for paper in papers:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
    fieldnames = [
        "编号", "题名", "年份", "DOI", "PDF", "大类", "二级类", "创新点标签",
        "科学问题标签", "相关性", "相关性分数", "代码状态", "代码仓库", "方法关键词",
    ]
    with (OUT / "论文分析总表.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in papers:
            writer.writerow({
                "编号": p["num"],
                "题名": p["title"],
                "年份": p.get("year") or "",
                "DOI": p.get("doi") or "",
                "PDF": p.get("pdf") or "",
                "大类": p["category"],
                "二级类": "; ".join(p["secondary_categories"]),
                "创新点标签": "; ".join(p["innovations"]),
                "科学问题标签": "; ".join(p["science_problems"]),
                "相关性": p["relevance_tier"],
                "相关性分数": p["relevance_score"],
                "代码状态": p["code_status"],
                "代码仓库": p["code_repositories"],
                "方法关键词": "; ".join(p["method_keywords"]),
            })


def count_primary(papers: list[dict], key: str) -> Counter:
    return Counter(p[key] for p in papers)


def count_multilabel(papers: list[dict], key: str) -> Counter:
    counter = Counter()
    for p in papers:
        counter.update(p.get(key, []))
    return counter


def by_year_counts(papers: list[dict]) -> dict[int, int]:
    counter = Counter(p.get("year") for p in papers if p.get("year"))
    return dict(sorted(counter.items()))


def top_examples(papers: list[dict], category: str, n: int = 5) -> list[dict]:
    rows = [p for p in papers if p["category"] == category]
    rows.sort(key=lambda p: (p["relevance_score"], p.get("year") or 0), reverse=True)
    return rows[:n]


def write_category_report(papers: list[dict]) -> None:
    counter = count_primary(papers, "category")
    lines = [
        "# 01 大类归类统计",
        "",
        f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 总体分布",
        "",
        "| 大类 | 篇数 | 占比 | 定义 |",
        "|---|---:|---:|---|",
    ]
    cat_summary = {c["name"]: c["summary"] for c in CATEGORIES}
    total = len(papers)
    for name, count in counter.most_common():
        lines.append(f"| {name} | {count} | {count / total:.1%} | {cat_summary.get(name, '')} |")
    lines += [
        "",
        "## 年度趋势",
        "",
        "| 年份 | 篇数 |",
        "|---:|---:|",
    ]
    for year, count in by_year_counts(papers).items():
        lines.append(f"| {year} | {count} |")
    lines += ["", "## 各大类代表论文", ""]
    for name, count in counter.most_common():
        lines.append(f"### {name}（{count}篇）")
        for p in top_examples(papers, name):
            lines.append(f"- [{p['num']}] {p['title']}（{p.get('year') or '未知'}，{p['relevance_tier']}，代码: {p['code_status']}）")
        lines.append("")
    (OUT / "01_大类归类统计.md").write_text("\n".join(lines), encoding="utf-8")


def write_innovation_report(papers: list[dict]) -> None:
    counter = count_multilabel(papers, "innovations")
    lines = [
        "# 02 创新点归类分析",
        "",
        "## 创新点标签分布",
        "",
        "| 创新点类别 | 涉及篇数 | 典型价值 |",
        "|---|---:|---|",
    ]
    value_map = {
        "表征学习、预训练与Transformer": "提升原始字节、包序列、流序列和日志序列的统一表征能力。",
        "图神经网络与关系建模": "刻画主机、流、事件、实体、时序依赖等非欧结构关系。",
        "多模态、多视图与特征融合": "融合统计、序列、图、内容、上下文等多源信息降低误报。",
        "自监督、对比学习与少样本学习": "缓解安全场景标签稀缺、标注噪声和新类样本不足。",
        "生成式增强、GAN与扩散模型": "用于少数类增强、攻击样本合成和鲁棒性评测。",
        "联邦学习、隐私保护与协同训练": "支持多机构/多节点不共享原始流量的协同建模。",
        "在线、增量、开放集与概念漂移": "面向真实网络持续变化、新攻击出现和模型长期维护。",
        "可解释性、规则抽取与因果分析": "提升告警可审计性、分析员可理解性和溯源能力。",
        "轻量化、实时与高性能部署": "支撑在线检测、边缘设备、网关和高速链路部署。",
        "鲁棒性、对抗防御与可信检测": "应对逃逸、投毒、干扰和分布外样本。",
        "数据集、基准、工具与系统化评测": "提供可复现评测环境和横向比较依据。",
        "应用场景与系统化验证": "强调场景落地、系统组合或问题定义。",
    }
    for name, count in counter.most_common():
        lines.append(f"| {name} | {count} | {value_map.get(name, '')} |")
    lines += ["", "## 组合模式观察", ""]
    combo = Counter()
    for p in papers:
        labels = p.get("innovations", [])
        if len(labels) >= 2:
            combo[tuple(labels[:2])] += 1
    for (a, b), count in combo.most_common(12):
        lines.append(f"- {a} + {b}: {count} 篇")
    lines += ["", "## 对系统建设的启示", ""]
    lines += [
        "1. 预训练/Transformer 与自监督学习适合作为统一流量表征底座。",
        "2. 图学习适合承接主机-流-告警-威胁情报之间的关联分析。",
        "3. 轻量化和在线增量能力应作为工程化指标，而不是后处理优化。",
        "4. 可解释性、规则抽取和原型方法适合用于告警解释与分析员交互。",
        "5. 数据增强和生成式模型适合补齐少数攻击类，但需要严格防止分布偏移。",
    ]
    (OUT / "02_创新点归类分析.md").write_text("\n".join(lines), encoding="utf-8")


def write_relevance_report(papers: list[dict]) -> None:
    tier_counter = count_primary(papers, "relevance_tier")
    cat_tier = defaultdict(Counter)
    for p in papers:
        cat_tier[p["category"]][p["relevance_tier"]] += 1
    lines = [
        "# 03 论文相关性分析",
        "",
        "相关性以“AI驱动的网络流量检测分析系统”为目标对象，从研究对象、方法可迁移性、工程实现价值和代码可用性综合判断。",
        "",
        "## 相关性分层",
        "",
        "| 层级 | 篇数 | 定义 |",
        "|---|---:|---|",
        f"| 强相关 | {tier_counter.get('强相关', 0)} | 可直接支撑流量分类、加密流量识别、入侵检测、恶意流量检测或在线监测。 |",
        f"| 中相关 | {tier_counter.get('中相关', 0)} | 方法可迁移到系统某一模块，如图关联、日志时序、联邦协同、边缘部署。 |",
        f"| 弱相关 | {tier_counter.get('弱相关', 0)} | 主要作为理论、背景、综述、跨域异常检测或工程参考。 |",
        "",
        "## 大类-相关性交叉统计",
        "",
        "| 大类 | 强相关 | 中相关 | 弱相关 |",
        "|---|---:|---:|---:|",
    ]
    for cat, counts in sorted(cat_tier.items(), key=lambda kv: sum(kv[1].values()), reverse=True):
        lines.append(f"| {cat} | {counts.get('强相关', 0)} | {counts.get('中相关', 0)} | {counts.get('弱相关', 0)} |")
    strong = [p for p in papers if p["relevance_tier"] == "强相关"]
    strong.sort(key=lambda p: (p["code_status"] == "已下载", p["relevance_score"], p.get("year") or 0), reverse=True)
    lines += ["", "## 强相关优先精读清单（前60篇）", ""]
    for p in strong[:60]:
        lines.append(f"- [{p['num']}] {p['title']}（{p.get('year') or '未知'}，{p['category']}，代码: {p['code_status']}）")
    lines += [
        "",
        "## 相关性结论",
        "",
        "- 强相关论文构成系统的主体技术池，尤其是加密流量分类、恶意流量检测、IDS/NIDS、流量监测与实时检测方向。",
        "- 中相关论文提供可迁移机制，如图学习、日志/时序异常检测、联邦学习、边缘部署和隐私保护。",
        "- 弱相关论文不宜全部精读，可用于背景综述、方法借鉴或“异常检测通用范式”补充。",
    ]
    (OUT / "03_论文相关性分析.md").write_text("\n".join(lines), encoding="utf-8")

    cats = [c["name"] for c in CATEGORIES]
    innovs = [name for name, _ in INNOVATIONS] + ["应用场景与系统化验证"]
    matrix = defaultdict(Counter)
    for p in papers:
        for inv in p["innovations"]:
            matrix[p["category"]][inv] += 1
    with (OUT / "相关性矩阵_大类x创新点.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["大类"] + innovs)
        for cat in cats:
            writer.writerow([cat] + [matrix[cat].get(inv, 0) for inv in innovs])


def write_science_report(papers: list[dict]) -> None:
    counter = count_multilabel(papers, "science_problems")
    lines = [
        "# 04 科学问题归类分析",
        "",
        "## 科学问题分布",
        "",
        "| 科学问题 | 涉及篇数 | 对系统研究的意义 |",
        "|---|---:|---|",
    ]
    meaning = {
        "加密与隐私保护造成可观测特征缺失": "决定系统必须基于元数据、时序、统计、图关系和弱语义特征建模。",
        "标签稀缺、类别不平衡与长尾攻击": "要求引入自监督、半监督、少样本和数据增强能力。",
        "域迁移、概念漂移与真实网络分布变化": "要求系统具备持续学习、漂移检测和跨环境泛化能力。",
        "高速流量实时检测与资源约束": "要求模型压缩、流式推理、特征快速提取和分层检测架构。",
        "多源异构数据融合与上下文建模": "要求融合流量、主机、日志、告警和威胁情报。",
        "模型可解释、可信与可审计": "决定系统能否服务安全运营和人工研判闭环。",
        "对抗规避、污染与鲁棒性": "要求考虑攻击者自适应规避和训练数据污染。",
        "数据集代表性、标准化评测与可复现": "决定论文实验能否落到真实系统评测。",
        "边缘、IoT、车联网与工业场景约束": "要求适配设备异构、算力受限和协议差异。",
        "开放世界未知攻击与误报控制": "要求系统处理未知类、低误报和告警优先级排序。",
    }
    for name, count in counter.most_common():
        lines.append(f"| {name} | {count} | {meaning.get(name, '')} |")
    lines += [
        "",
        "## 建议凝练的核心科学问题",
        "",
        "1. 在加密不可解密、标签稀缺且流量分布持续变化的条件下，如何学习稳定、可迁移、可解释的网络流量表征？",
        "2. 如何将包/流时序、主机通信图、日志告警和威胁情报融合为统一的检测与溯源模型？",
        "3. 如何在高速链路和边缘设备约束下实现低延迟、低误报、可持续更新的在线异常检测？",
        "4. 如何评估模型面对未知攻击、对抗规避、概念漂移和数据污染时的鲁棒性与可信度？",
    ]
    (OUT / "04_科学问题归类分析.md").write_text("\n".join(lines), encoding="utf-8")


def write_per_paper_report(papers: list[dict]) -> None:
    lines = [
        "# 05 逐篇中文解析",
        "",
        "说明：每篇解析由题名、摘要抽取、关键词规则、代码索引和相关性评分自动生成，适合用于初筛和综述框架搭建；正式引用前建议结合原文复核。",
        "",
    ]
    for p in papers:
        interp = p["interpretation"]
        lines += [
            f"## [{p['num']}] {p['title']}",
            "",
            f"- 年份: {p.get('year') or '未知'}",
            f"- DOI: {p.get('doi') or '无'}",
            f"- PDF: `{p.get('pdf') or '无'}`",
            f"- 大类: {p['category']}",
            f"- 二级关联: {'; '.join(p['secondary_categories']) if p['secondary_categories'] else '无'}",
            f"- 创新点标签: {'; '.join(p['innovations'])}",
            f"- 科学问题标签: {'; '.join(p['science_problems'])}",
            f"- 相关性: {p['relevance_tier']}（分数 {p['relevance_score']}）",
            f"- 代码状态: {p['code_status']}{'；' + p['code_repositories'] if p['code_repositories'] else ''}",
            "",
            f"**中文概述**：{interp['overview']}",
            "",
            f"**摘要线索**：{interp['abstract_hint']}",
            "",
            f"**可能创新点**：{interp['innovation']}。",
            "",
            f"**方法/对象关键词**：{interp['method']}。",
            "",
            f"**对项目的使用建议**：{interp['usage']}",
            "",
        ]
    (OUT / "05_逐篇中文解析.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary_report(papers: list[dict]) -> None:
    category_counter = count_primary(papers, "category")
    innovation_counter = count_multilabel(papers, "innovations")
    science_counter = count_multilabel(papers, "science_problems")
    relevance_counter = count_primary(papers, "relevance_tier")
    code_counter = count_primary(papers, "code_status")
    lines = [
        "# 06 总结报告",
        "",
        "## 一、总体结论",
        "",
        f"本次共分析 {len(papers)} 篇论文。文献主题以“{category_counter.most_common(1)[0][0]}”为最大板块，同时覆盖加密流量识别、恶意流量检测、入侵检测、IoT/车联网安全、图学习/知识图谱、日志时序异常检测、隐私协同和跨域异常检测等方向。",
        "",
        f"相关性方面，强相关 {relevance_counter.get('强相关', 0)} 篇，中相关 {relevance_counter.get('中相关', 0)} 篇，弱相关 {relevance_counter.get('弱相关', 0)} 篇。代码状态方面，已下载 {code_counter.get('已下载', 0)} 篇相关代码，部分下载 {code_counter.get('部分下载', 0)} 篇，仍有一批论文只发现候选或未发现代码。",
        "",
        "## 二、主要研究脉络",
        "",
        "1. **从明文特征到加密流量表征**：研究重点从传统 DPI/统计特征逐渐转向字节序列、包序列、流序列和上下文图结构。",
        "2. **从单流分类到多源关联检测**：越来越多论文将流量、主机、日志、告警和威胁情报放入统一图或多模态框架。",
        "3. **从离线分类到在线自适应检测**：概念漂移、开放集、实时部署和增量更新成为真实系统必须处理的问题。",
        "4. **从准确率导向到可信运营导向**：可解释性、规则抽取、误报控制、鲁棒性和复现性开始成为核心指标。",
        "",
        "## 三、创新点高频方向",
        "",
    ]
    for name, count in innovation_counter.most_common(8):
        lines.append(f"- {name}: {count} 篇")
    lines += [
        "",
        "## 四、科学问题高频方向",
        "",
    ]
    for name, count in science_counter.most_common(8):
        lines.append(f"- {name}: {count} 篇")
    lines += [
        "",
        "## 五、对AI驱动网络流量检测分析系统的建议",
        "",
        "1. 构建统一数据底座：包级、流级、会话级、主机级、日志级和威胁情报级数据需要统一编号与时间对齐。",
        "2. 采用分层检测架构：高速链路先做轻量筛查，再将疑似流量送入深度模型、图模型和解释模块。",
        "3. 引入自监督预训练：使用大规模未标注流量学习通用表示，降低对标注样本的依赖。",
        "4. 建立图关联分析层：将 IP、域名、证书、会话、告警、进程和情报实体构造成动态图，用于溯源与横向移动识别。",
        "5. 强化持续学习机制：对概念漂移、未知类和新攻击进行监控，形成模型更新与人工审核闭环。",
        "6. 将解释性作为产品能力：输出触发特征、相似历史样本、原型流、规则摘要和攻击链上下文。",
        "7. 建立复现实验库：优先复现已下载代码的强相关论文，形成系统内部 benchmark。",
        "",
        "## 六、配套文件",
        "",
        "- `01_大类归类统计.md`",
        "- `02_创新点归类分析.md`",
        "- `03_论文相关性分析.md`",
        "- `04_科学问题归类分析.md`",
        "- `05_逐篇中文解析.md`",
        "- `论文分析总表.csv`",
        "- `图表/`",
        "- `科研汇报PPT_850篇论文综合分析.pptx`",
    ]
    (OUT / "06_总结报告.md").write_text("\n".join(lines), encoding="utf-8")


def chart_bar(counter: Counter, title: str, path: Path, top_n: int = 12) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    items = counter.most_common(top_n)
    labels = [i[0] for i in items][::-1]
    values = [i[1] for i in items][::-1]
    fig_h = max(5, 0.38 * len(labels) + 1.2)
    fig, ax = plt.subplots(figsize=(11, fig_h), dpi=160)
    colors = ["#1f7a8c" if idx % 2 == 0 else "#bfdb38" for idx in range(len(labels))]
    ax.barh(labels, values, color=colors)
    ax.set_title(title, fontsize=16, fontweight="bold")
    ax.set_xlabel("篇数")
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.01, i, str(v), va="center", fontsize=10)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_pie(counter: Counter, title: str, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    labels = list(counter.keys())
    values = list(counter.values())
    fig, ax = plt.subplots(figsize=(8, 6), dpi=160)
    colors = ["#0b3954", "#087e8b", "#bfd7ea", "#ff5a5f", "#c81d25"]
    ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=110, colors=colors[: len(values)])
    ax.set_title(title, fontsize=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_years(papers: list[dict], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    counts = by_year_counts(papers)
    years = list(counts.keys())
    vals = list(counts.values())
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=160)
    ax.plot(years, vals, color="#087e8b", marker="o", linewidth=2.5)
    ax.fill_between(years, vals, color="#bfd7ea", alpha=0.45)
    ax.set_title("年度论文数量趋势", fontsize=16, fontweight="bold")
    ax.set_xlabel("年份")
    ax.set_ylabel("篇数")
    ax.grid(axis="y", alpha=0.25)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def write_charts(papers: list[dict]) -> None:
    chart_bar(count_primary(papers, "category"), "大类归类统计", CHARTS / "大类归类统计.png", 12)
    chart_bar(count_multilabel(papers, "innovations"), "创新点标签分布", CHARTS / "创新点分布.png", 12)
    chart_bar(count_multilabel(papers, "science_problems"), "科学问题分布", CHARTS / "科学问题分布.png", 10)
    chart_pie(count_primary(papers, "relevance_tier"), "论文相关性分布", CHARTS / "相关性分布.png")
    chart_pie(count_primary(papers, "code_status"), "代码状态分布", CHARTS / "代码状态分布.png")
    chart_years(papers, CHARTS / "年度趋势.png")


def write_readme(papers: list[dict]) -> None:
    readme = f"""# 综合分析输出说明

生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

本文件夹汇总 `paper/` 下 850 篇论文的自动化综合分析结果。

## 文件清单

- `01_大类归类统计.md`
- `02_创新点归类分析.md`
- `03_论文相关性分析.md`
- `04_科学问题归类分析.md`
- `05_逐篇中文解析.md`
- `06_总结报告.md`
- `论文分析总表.csv`
- `相关性矩阵_大类x创新点.csv`
- `图表/`
- `_data/papers_enriched.json`
- `_data/papers_enriched.jsonl`

## 方法说明

1. 从 `文献.md` 抽取编号、题名、年份、DOI 和 PDF 路径。
2. 用 `pdftotext` 抽取 PDF 前 3 页，识别摘要和关键词。
3. 基于题名、摘要、关键词和已有代码索引进行规则化多标签分类。
4. 分类结果用于生成统计、逐篇中文解析和科研汇报 PPT。

注意：逐篇解析用于批量初筛，正式论文综述或引用前仍建议核对原文。
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    entries = parse_bibliography()
    if len(entries) != 850:
        print(f"warning: parsed {len(entries)} entries, expected 850", file=sys.stderr)
    start = time.time()
    text_results: dict[int, dict] = {}
    max_workers = min(6, (os.cpu_count() or 4))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_pdf_text, entry): entry for entry in entries}
        done = 0
        for future in as_completed(futures):
            result = future.result()
            text_results[result["num"]] = result
            done += 1
            if done % 50 == 0 or done == len(entries):
                print(f"extracted {done}/{len(entries)} pdf text snippets")
    papers = enrich_papers(entries, text_results)
    write_json_csv(papers)
    write_category_report(papers)
    write_innovation_report(papers)
    write_relevance_report(papers)
    write_science_report(papers)
    write_per_paper_report(papers)
    write_summary_report(papers)
    write_charts(papers)
    write_readme(papers)
    elapsed = time.time() - start
    print(json.dumps({
        "papers": len(papers),
        "elapsed_sec": round(elapsed, 1),
        "categories": count_primary(papers, "category"),
        "relevance": count_primary(papers, "relevance_tier"),
    }, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
