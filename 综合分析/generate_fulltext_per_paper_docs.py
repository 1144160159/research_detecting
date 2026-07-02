# -*- coding: utf-8 -*-
"""Generate full-text based per-paper Chinese analysis documents.

This script upgrades the previous abstract-level paper notes. It extracts full
PDF text, recognizes coarse paper sections, and writes one structured Chinese
analysis file per paper under 综合分析/逐篇中文解析/.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import generate_per_paper_docs as base


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "综合分析"
DATA = OUT / "_data"
FULL_TEXT_CACHE = DATA / "full_text_cache_plain"
DETAIL_DIR = OUT / "逐篇中文解析"
INDEX = OUT / "05_逐篇中文解析.md"
BACKUP_INDEX = OUT / "05_逐篇中文解析_正文增强前备份.md"
MANIFEST = DATA / "per_paper_docs_manifest.json"
FULLTEXT_MANIFEST = DATA / "fulltext_analysis_manifest.json"
QUALITY_CSV = OUT / "正文解析质量统计.csv"
QUALITY_MD = OUT / "08_正文级逐篇解析质量报告.md"


SECTION_SPECS = [
    ("abstract", "摘要", r"^(abstract|summary|摘要|概要)\b"),
    ("introduction", "引言/问题背景", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(introduction|introductory|motivation|problem statement|overview)\b"),
    ("background", "背景/预备知识", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(background|preliminaries|preliminary|definitions|threat model|problem formulation)\b"),
    ("related_work", "相关工作", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(related work|literature review|prior work)\b"),
    ("method", "方法/模型/系统设计", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(method|methods|methodology|approach|proposed method|proposed approach|proposed model|proposed framework|model|models|framework|system|system design|system architecture|design|architecture|algorithm|scheme|implementation)\b"),
    ("experiment", "实验/评估/结果", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(experiment|experiments|experimental|comparison experiments|evaluation|performance evaluation|results|case study|empirical evaluation|implementation and evaluation|analysis of results)\b"),
    ("discussion", "讨论/消融/分析", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(discussion|ablation|ablation study|sensitivity analysis|analysis|security analysis)\b"),
    ("conclusion", "结论/未来工作", r"^(?:[0-9ivxIVX]+(?:\.[0-9]+)*[.)]?\s*)?(conclusion|conclusions|concluding remarks|future work|limitations|limitations and future work)\b"),
    ("references", "参考文献", r"^(references|bibliography|参考文献)\b"),
]

SECTION_CN = {k: v for k, v, _ in SECTION_SPECS}
SECTION_REGEX = [(k, v, re.compile(p, re.I)) for k, v, p in SECTION_SPECS]


PROBLEM_KEYWORDS = [
    "challenge", "problem", "difficult", "difficulty", "limitation", "limited",
    "however", "lack", "need", "require", "bottleneck", "privacy", "encrypted",
    "imbalance", "scarce", "few", "unknown", "drift", "evasion", "real-time",
]

CONTRIBUTION_KEYWORDS = [
    "we propose", "we present", "we introduce", "we design", "we develop",
    "this paper proposes", "this paper presents", "our approach", "our method",
    "our contributions", "contribution", "novel", "first", "new framework",
]

METHOD_KEYWORDS = [
    "model", "framework", "architecture", "algorithm", "feature", "embedding",
    "representation", "classifier", "neural", "transformer", "graph", "attention",
    "training", "optimization", "loss", "encoder", "decoder", "clustering",
]

EXPERIMENT_KEYWORDS = [
    "experiment", "evaluation", "dataset", "baseline", "accuracy", "precision",
    "recall", "f1", "auc", "roc", "false positive", "detection rate", "latency",
    "throughput", "outperform", "compare", "ablation",
]

CONCLUSION_KEYWORDS = [
    "conclusion", "conclude", "future work", "limitation", "in summary",
    "results show", "demonstrate", "remaining", "open problem", "further",
]

MODEL_TERMS = [
    "CNN", "RNN", "LSTM", "GRU", "Transformer", "BERT", "Autoencoder", "VAE",
    "GAN", "Diffusion", "GNN", "GCN", "GraphSAGE", "GAT", "HMM", "GMM",
    "SVM", "Random Forest", "XGBoost", "KNN", "Naive Bayes", "Decision Tree",
    "Markov", "Attention", "Contrastive", "Self-supervised", "Federated",
    "Blockchain", "Knowledge Graph", "Clustering", "PCA", "Isolation Forest",
]

BASELINE_TERMS = [
    "SVM", "Random Forest", "Decision Tree", "KNN", "Naive Bayes", "XGBoost",
    "CNN", "RNN", "LSTM", "GRU", "Transformer", "Autoencoder", "HMM", "GMM",
    "k-means", "DBSCAN", "Isolation Forest", "One-Class SVM", "MLP",
]

SURVEY_HINTS = ["survey", "review", "literature", "taxonomy", "tools", "benchmark", "dataset"]
THEORY_HINTS = ["cryptography", "public-key", "digital signature", "cryptosystem", "key exchange", "automata"]


SCIENCE_QUESTIONS = {
    "加密与隐私保护造成可观测特征缺失": "在不能解密或不应解密的条件下，如何只凭包长、方向、时序、握手元数据或关系上下文保持可判别性？",
    "标签稀缺、类别不平衡与长尾攻击": "在标注昂贵、少数类样本不足且攻击形态长尾的条件下，如何获得稳定监督信号？",
    "域迁移、概念漂移与真实网络分布变化": "当应用版本、网络环境和攻击策略持续变化时，模型如何识别分布漂移并保持跨域泛化？",
    "高速流量实时检测与资源约束": "在高吞吐、低延迟和边缘资源受限场景下，检测链路如何兼顾精度、速度和可部署性？",
    "多源异构数据融合与上下文建模": "如何把流量、主机、日志、告警、证书、域名和威胁情报组织成可学习的上下文证据链？",
    "模型可解释、可信与可审计": "如何让模型输出可被安全分析员复核的原因、相似样本、关键特征或规则证据？",
    "对抗规避、污染与鲁棒性": "面对规避、投毒、噪声标签和分布外样本，检测模型如何保持鲁棒性并给出风险边界？",
    "数据集代表性、标准化评测与可复现": "如何确保数据集、划分方式、指标和基线足以代表真实场景并支持可复现比较？",
    "边缘、IoT、车联网与工业场景约束": "在协议、设备、拓扑和算力高度异构的专用场景中，如何设计轻量且可靠的检测机制？",
    "开放世界未知攻击与误报控制": "在类别不封闭、未知攻击不断出现的真实网络中，如何发现新异常并控制误报成本？",
}


def ensure_dirs() -> None:
    OUT.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    FULL_TEXT_CACHE.mkdir(parents=True, exist_ok=True)
    DETAIL_DIR.mkdir(parents=True, exist_ok=True)


def clean_line(line: str) -> str:
    s = re.sub(r"\s+", " ", line.strip())
    s = s.strip(" .\t\r\n")
    return s


def repair_spaced_heading(text: str) -> str:
    """Repair headings extracted as 'I NTRODUCTION' or 'R ELATED W ORK'."""
    previous = None
    current = text
    while previous != current:
        previous = current
        current = re.sub(r"\b([A-Z])\s+([A-Z]{2,})\b", r"\1\2", current)
    return current


def normalize_pdf_text(text: str) -> str:
    text = text.replace("\x0c", "\n")
    text = re.sub(r"(?<=[A-Za-z])-\s*\n\s*(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_full_text(paper: dict, timeout_sec: int = 90) -> dict:
    num = int(paper["num"])
    cache = FULL_TEXT_CACHE / f"{num:03d}.txt"
    err_cache = FULL_TEXT_CACHE / f"{num:03d}.err"
    if cache.exists() and cache.stat().st_size > 80:
        text = cache.read_text(encoding="utf-8", errors="ignore")
        return {"num": num, "ok": True, "cached": True, "chars": len(text), "error": ""}

    pdf_rel = paper.get("pdf") or ""
    pdf_path = ROOT / pdf_rel
    if not pdf_path.exists():
        err = f"PDF not found: {pdf_rel}"
        err_cache.write_text(err, encoding="utf-8")
        return {"num": num, "ok": False, "cached": False, "chars": 0, "error": err}

    tmp = FULL_TEXT_CACHE / f"{num:03d}.tmp.txt"
    commands = [
        ["pdftotext", "-nopgbrk", str(pdf_path), str(tmp)],
        ["pdftotext", "-layout", "-nopgbrk", str(pdf_path), str(tmp)],
    ]
    last_err = ""
    for cmd in commands:
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
            if cp.returncode == 0 and tmp.exists():
                text = normalize_pdf_text(tmp.read_text(encoding="utf-8", errors="ignore"))
                cache.write_text(text, encoding="utf-8")
                try:
                    tmp.unlink()
                except OSError:
                    pass
                if err_cache.exists():
                    err_cache.unlink()
                return {"num": num, "ok": True, "cached": False, "chars": len(text), "error": ""}
            last_err = (cp.stderr or cp.stdout or f"return code {cp.returncode}").strip()[:600]
        except Exception as exc:
            last_err = str(exc)[:600]
    err_cache.write_text(last_err, encoding="utf-8")
    return {"num": num, "ok": False, "cached": False, "chars": 0, "error": last_err}


def read_full_text(num: int) -> str:
    path = FULL_TEXT_CACHE / f"{num:03d}.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def identify_heading(line: str) -> tuple[str, str] | None:
    s = clean_line(line)
    if not s or len(s) > 120:
        return None
    if sum(ch.isdigit() for ch in s) > max(8, len(s) // 2):
        return None
    # Remove page number leftovers and common section numbering.
    normalized = repair_spaced_heading(re.sub(r"^[\-–—]*\s*\d+\s*$", "", s))
    if not normalized:
        return None
    for key, cn, rx in SECTION_REGEX:
        if rx.match(normalized):
            return key, cn
    prefixed = re.match(r"^\s*(?:[0-9]+(?:\.[0-9]+)*|[IVX]+)[.)]\s+(.+)$", normalized, flags=re.I)
    if prefixed:
        heading_body = prefixed.group(1).lower()
        if any(term in heading_body for term in ["evaluation", "experiment", "result", "comparison"]):
            return "experiment", SECTION_CN["experiment"]
        if any(term in heading_body for term in ["conclusion", "future work"]):
            return "conclusion", SECTION_CN["conclusion"]
        if any(term in heading_body for term in ["discussion", "ablation", "analysis"]):
            return "discussion", SECTION_CN["discussion"]
        if any(term in heading_body for term in ["network", "model", "framework", "architecture", "algorithm", "method", "approach", "system", "scheme"]):
            return "method", SECTION_CN["method"]
    return None


def split_sections(raw_text: str) -> dict:
    text = normalize_pdf_text(raw_text)
    lines = text.splitlines()
    headings = []
    pos = 0
    for idx, line in enumerate(lines):
        hit = identify_heading(line)
        if hit:
            key, cn = hit
            headings.append({"line": idx, "pos": pos, "key": key, "cn": cn, "heading": clean_line(line)})
        pos += len(line) + 1

    if not headings:
        return {"sections": {}, "order": [], "body_text": text, "reference_start": None}

    # Drop likely table-of-contents heading clusters near the beginning.
    filtered = []
    for h in headings:
        if h["pos"] < 4000:
            nearby = [x for x in headings if abs(x["pos"] - h["pos"]) < 1200]
            if len(nearby) >= 5 and h["key"] not in {"abstract", "introduction"}:
                continue
        filtered.append(h)
    headings = filtered or headings

    reference_start = None
    for h in headings:
        if h["key"] == "references" and (h["pos"] > 9000 or h["pos"] > len(text) * 0.35):
            reference_start = h["pos"]
            break

    body_text = text[:reference_start].strip() if reference_start else text
    headings = [h for h in headings if h["pos"] < len(body_text)]

    sections = {}
    order = []
    for i, h in enumerate(headings):
        key = h["key"]
        if key == "references":
            continue
        start = h["pos"]
        end = len(body_text)
        for j in range(i + 1, len(headings)):
            if headings[j]["pos"] > start:
                end = headings[j]["pos"]
                break
        chunk = body_text[start:end].strip()
        if len(chunk) < 80:
            continue
        if key not in sections or len(chunk) > len(sections[key]):
            sections[key] = chunk
        if key not in order:
            order.append(key)
    return {"sections": sections, "order": order, "body_text": body_text, "reference_start": reference_start}


def compact_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def remove_citation_noise(text: str) -> str:
    text = re.sub(r"\[[0-9,\-\s]+\]", "", text)
    text = re.sub(r"\([A-Z][A-Za-z\-]+(?: et al\.)?,?\s+\d{4}[a-z]?\)", "", text)
    text = re.sub(r"https?://\S+", "", text)
    return compact_space(text)


def split_sentences(text: str) -> list[str]:
    text = remove_citation_noise(text)
    if not text:
        return []
    raw = re.split(r"(?<=[.!?。！？])\s+(?=[A-Z0-9(])", text)
    out = []
    for sent in raw:
        sent = compact_space(sent)
        if len(sent) < 35 or len(sent) > 650:
            continue
        if sent.count("@") or sent.lower().startswith(("figure ", "table ")):
            continue
        if len(re.findall(r"\d", sent)) > max(18, len(sent) // 4):
            continue
        out.append(sent)
    return out


def score_sentence(sent: str, keywords: list[str], idx: int) -> int:
    low = sent.lower()
    score = 0
    for keyword in keywords:
        if keyword in low:
            score += 4 if " " in keyword else 2
    if re.search(r"\b(we|this paper|our)\b", low):
        score += 1
    if idx < 8:
        score += 2
    elif idx < 25:
        score += 1
    if "copyright" in low or "permission" in low or "isbn" in low:
        score -= 5
    return score


def pick_sentences(text: str, keywords: list[str], count: int = 3) -> list[str]:
    sentences = split_sentences(text)
    scored = []
    for i, sent in enumerate(sentences):
        score = score_sentence(sent, keywords, i)
        if score > 0:
            scored.append((score, i, sent))
    scored.sort(key=lambda x: (-x[0], x[1]))
    chosen = []
    seen = set()
    for _, _, sent in scored:
        key = re.sub(r"[^a-z0-9]+", "", sent.lower())[:100]
        if key in seen:
            continue
        seen.add(key)
        chosen.append(sent)
        if len(chosen) >= count:
            break
    return chosen


def short_evidence(sent: str, max_chars: int = 180) -> str:
    sent = remove_citation_noise(sent)
    sent = sent.replace("|", "/")
    if len(sent) <= max_chars:
        return sent
    return sent[:max_chars].rstrip(" ,;:") + "..."


def contains_candidate(text: str, candidate: str) -> bool:
    if not text or not candidate:
        return False
    pattern = r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(candidate)
    return re.search(pattern, text, flags=re.I) is not None


def find_terms_case(text: str, candidates: list[str], limit: int = 18) -> list[str]:
    found = []
    for item in candidates:
        if contains_candidate(text, item) and item not in found:
            found.append(item)
        if len(found) >= limit:
            break
    return found


def title_acronyms(title: str) -> list[str]:
    title = title or ""
    parts = re.findall(
        r"\b[A-Z][A-Z0-9]{1,}(?:-[A-Z][A-Za-z0-9]{1,})*\b|\b[A-Z][A-Za-z0-9]{1,}-[A-Z][A-Za-z0-9]{1,}\b",
        title,
    )
    prefix = title.split(":", 1)[0].strip()
    if re.fullmatch(r"[A-Z][A-Za-z0-9]{1,}(?:-[A-Z][A-Za-z0-9]{1,})*", prefix):
        parts.insert(0, prefix)
    return list(dict.fromkeys(parts))[:6]


def is_survey_like(paper: dict, body_text: str) -> bool:
    title = (paper.get("title", "") or "").lower()
    category = paper.get("category", "")
    early = body_text[:2200].lower()
    if "数据集、基准、综述" in category:
        return True
    if any(h in title for h in SURVEY_HINTS):
        return True
    return bool(re.search(r"\b(this|our)\s+(survey|review|taxonomy)\b", early))


def is_theory_like(paper: dict, body_text: str) -> bool:
    blob = f"{paper.get('title', '')} {paper.get('category', '')}".lower()
    return any(h in blob for h in THEORY_HINTS) or "基础理论" in paper.get("category", "")


def digest_from_sentences(sentences: list[str], fallback: str, max_items: int = 3) -> list[str]:
    items = []
    for sent in sentences[:max_items]:
        items.append(short_evidence(sent))
    if not items:
        items.append(fallback)
    return items


def derive_problem_points(paper: dict, sections: dict, body_text: str) -> list[str]:
    intro_text = " ".join([sections.get("abstract", ""), sections.get("introduction", ""), sections.get("background", "")])
    sentences = pick_sentences(intro_text or body_text[:16000], PROBLEM_KEYWORDS, 4)
    low = (intro_text or body_text[:16000]).lower()
    points = []
    if "encrypted" in low or "privacy" in low or "tls" in low or "tor" in low:
        points.append("可观测信息受加密、匿名化或隐私约束限制，检测模型不能依赖明文载荷，只能利用时序、包长、方向、握手元数据或关系上下文。")
    if (
        "imbalance" in low
        or "few-shot" in low
        or "semi-supervised" in low
        or "scarce label" in low
        or "limited label" in low
        or "few label" in low
        or "lack of label" in low
        or "unlabeled" in low
    ):
        points.append("标注样本不足、类别不平衡或长尾攻击会削弱传统监督学习，需要更稳健的表征学习、半监督/自监督或样本增强机制。")
    if (
        "domain adaptation" in low
        or "cross-domain" in low
        or "concept drift" in low
        or "out-of-distribution" in low
        or "distribution shift" in low
        or "evolving network" in low
    ):
        points.append("真实网络分布会随时间、应用版本和部署环境变化，模型需要处理域迁移、概念漂移和泛化性能下降。")
    if "feature engineering" in low or "manual" in low and "feature" in low or "human effort" in low or "piece-wise" in low:
        points.append("传统方案依赖人工特征工程或把任务拆成多个子问题，特征选择、模型训练和最终分类目标之间缺少端到端联合优化。")
    if "real-time" in low or "online" in low or "latency" in low or "throughput" in low or "scalable" in low:
        points.append("检测链路需要满足在线吞吐、低延迟和资源开销约束，离线高准确率并不等同于工程可用。")
    if "explain" in low or "interpret" in low or "accountability" in low:
        points.append("安全运营场景要求模型输出可解释、可审计的证据，而不仅是一个黑盒分类标签。")
    if not points:
        object_text = base.infer_research_object(paper)
        points.append(f"正文将研究对象聚焦在“{object_text}”，核心是把该对象转化为可建模、可评测、可复核的安全分析问题。")
    for sent in sentences[:2]:
        points.append("正文动机线索：" + short_evidence(sent, 150))
    return list(dict.fromkeys(points))[:5]


def derive_innovation_points(paper: dict, sections: dict, body_text: str) -> list[str]:
    method_text = " ".join([
        sections.get("abstract", ""),
        sections.get("introduction", ""),
        sections.get("method", ""),
        sections.get("discussion", ""),
    ])
    sentences = pick_sentences(method_text or body_text[:25000], CONTRIBUTION_KEYWORDS + METHOD_KEYWORDS, 4)
    models = find_terms_case(method_text + " " + paper.get("title", ""), MODEL_TERMS, 10)
    acronyms = title_acronyms(paper.get("title", ""))
    points = []
    if acronyms:
        points.append("方法命名/系统缩写：" + "、".join(acronyms) + "，可作为检索代码、复现材料和同类工作的关键锚点。")
    if models:
        points.append("正文方法线索显示其使用或对比了：" + "、".join(models) + "；这些术语帮助定位模型结构、特征表示或基线选择。")
    for label in paper.get("innovations", [])[:3]:
        explain = base.INNOVATION_EXPLAIN.get(label, "该创新标签可作为方法设计或系统评估的参考。")
        points.append(f"{label}：{explain}")
    for sent in sentences[:2]:
        points.append("正文贡献线索：" + short_evidence(sent, 150))
    if not points:
        points.append("正文未抽取到清晰的贡献句，建议精读方法章节确认其真正增量；当前可按题名、摘要和分类标签定位其技术贡献。")
    return list(dict.fromkeys(points))[:6]


def derive_science_questions(paper: dict, problem_points: list[str], body_text: str) -> list[str]:
    questions = []
    theory_blob = f"{paper.get('title', '')} {body_text[:5000]}".lower()
    if is_theory_like(paper, body_text):
        if "public-key" in theory_blob or "key distribution" in theory_blob or "key exchange" in theory_blob:
            questions.append("开放网络中的密钥分发问题：在通信双方缺少预共享秘密的条件下，如何建立可信密钥或安全通信机制？")
        if "digital signature" in theory_blob or "signature" in theory_blob:
            questions.append("数字身份与不可否认性问题：如何让电子消息具备类似书面签名的认证、完整性和责任归属能力？")
        if "cryptography" in theory_blob or "encryption" in theory_blob:
            questions.append("密码机制的安全性边界问题：如何在明确攻击者能力、计算假设和协议目标后，判断方案能抵抗哪些攻击、不能抵抗哪些攻击？")
    for label in paper.get("science_problems", [])[:4]:
        q = SCIENCE_QUESTIONS.get(label) or base.SCIENCE_EXPLAIN.get(label)
        if q:
            questions.append(f"{label}：{q}")
    if not questions:
        category = paper.get("category", "")
        if "加密流量" in category:
            questions.append(SCIENCE_QUESTIONS["加密与隐私保护造成可观测特征缺失"])
        elif "入侵检测" in category or "恶意" in category:
            questions.append(SCIENCE_QUESTIONS["开放世界未知攻击与误报控制"])
        elif "数据集" in category:
            questions.append(SCIENCE_QUESTIONS["数据集代表性、标准化评测与可复现"])
        else:
            questions.append("如何把论文中的任务对象、约束条件和评价指标组织成可验证的科学假设，并避免只停留在经验性模型调参？")
    if problem_points:
        questions.append("从正文动机延伸出的追问：" + problem_points[0])
    return list(dict.fromkeys(questions))[:5]


def build_method_steps(paper: dict, sections: dict, body_text: str) -> list[str]:
    method_text = sections.get("method", "") or sections.get("background", "") or body_text[:22000]
    models = find_terms_case(method_text + " " + paper.get("title", ""), MODEL_TERMS, 10)
    is_theory = is_theory_like(paper, body_text) and not models
    is_survey = is_survey_like(paper, body_text) and not is_theory
    object_text = base.infer_research_object(paper)
    if is_survey:
        return [
            "界定综述或基准对象，明确任务边界、术语体系、应用场景和评价维度。",
            "按方法路线、数据来源、特征/模型、工具链或系统能力建立分类框架。",
            "横向比较代表性工作，提炼优缺点、适用条件、数据集偏差和复现难点。",
            "归纳开放问题，为后续系统设计、benchmark 构建和研究选题提供依据。",
        ]
    if is_theory:
        return [
            f"把“{object_text}”抽象成协议、机制、形式化模型或理论构造问题。",
            "给出关键概念、参与方、威胁/能力假设以及需要满足的安全或功能性质。",
            "通过推理、构造、反例或复杂度分析说明方案为什么可行、边界在哪里。",
            "将理论机制映射到后续网络安全系统时，需要再补充工程数据、评测指标和部署约束。",
        ]
    representation = "从原始流量/日志/样本中抽取统计特征、序列表示、字节/包级表示或图结构上下文。"
    image_scope = (paper.get("title", "") + " " + paper.get("category", "")).lower()
    if "image" in image_scope or "图像" in image_scope or "多媒体" in paper.get("category", ""):
        representation = "将样本或流量转换为图像/矩阵表示，再利用视觉模型提取局部模式。"
    if "graph" in method_text.lower():
        representation = "把主机、流、包、会话、告警或情报实体构造成图，并保留节点/边属性。"
    model_step = "构建分类、检测或异常评分模型，并用训练目标约束其区分正常/异常、应用类别或攻击类别。"
    if models:
        model_step = "围绕 " + "、".join(models[:6]) + " 等模型/基线构建检测或分类器，并比较不同结构的贡献。"
    return [
        f"明确输入对象：{object_text}，确定采集粒度、标签定义和训练/测试场景。",
        representation,
        model_step,
        "通过训练、验证和消融分析选择关键参数，必要时加入自监督、增强、图关系、联邦或漂移处理机制。",
        "在独立测试集或跨场景数据上评估效果，并把结果转化为可复现实验配置或工程模块。",
    ]


def dataset_phrase_summary(exp_text: str) -> list[str]:
    phrases = []
    strong = re.compile(
        r"\b(dataset|collected|collection|real-world|applications?|cross[- ]validation|training set|test set|campus|flows? referring|traffic flows)\b",
        re.I,
    )
    for sent in pick_sentences(
        exp_text,
        ["dataset", "collected", "real-world", "applications", "cross validation", "training set", "test set", "campus"],
        4,
    ):
        if not strong.search(sent):
            continue
        phrases.append(short_evidence(sent, 180))
    return phrases[:3]


def build_experiment_steps(paper: dict, sections: dict, body_text: str) -> tuple[list[str], dict]:
    exp_text = sections.get("experiment", "") or sections.get("discussion", "") or ""
    source = exp_text + " " + body_text[:30000]
    datasets = find_terms_case(source, base.KNOWN_DATASETS, 20)
    metric_candidates = base.METRIC_TERMS + [
        "tpr", "fpr", "ftf", "true positive rate", "false positive rate",
        "detection accuracy", "detection rate",
    ]
    metrics = find_terms_case(source, metric_candidates, 20)
    baselines = find_terms_case(source, BASELINE_TERMS, 12)
    dataset_phrases = dataset_phrase_summary(exp_text or source[:12000])
    has_exp_section = bool(sections.get("experiment"))
    survey = is_survey_like(paper, body_text)
    theory = is_theory_like(paper, body_text) and not has_exp_section
    if has_exp_section:
        steps = [
            "整理数据集/采集场景，确认样本单位、类别定义、训练/验证/测试划分和是否存在跨域测试。",
            "复现特征工程或表示学习流程，保证输入张量、包/流截断长度、归一化方式与论文设置一致。",
            "训练本文方法并运行基线模型，记录超参数、随机种子、类别不平衡处理和硬件环境。",
            "使用论文指标进行比较，重点检查误报率、检测率、F1/AUC、延迟/吞吐和消融实验是否支撑结论。",
        ]
    elif survey:
        steps = [
            "本文偏综述/基准/工具分析，实验重点不是单一模型训练，而是文献集合、工具能力或数据集维度的横向比较。",
            "复核时应检查纳入文献/工具的选择标准、分类维度、统计口径和是否覆盖最新应用场景。",
            "若要服务本项目，可把其分类表、评价维度和开放问题转化为系统需求或 benchmark 清单。",
        ]
    elif theory:
        steps = [
            "本文偏理论或机制研究，正文未识别到独立实验章节；评价通常依赖形式化推理、性质证明或机制对比。",
            "复核时应关注假设条件、威胁模型、复杂度、协议步骤和与真实系统结合时的额外工程约束。",
            "如需落地到检测系统，需要另外设计数据集、指标、基线和运行时开销实验。",
        ]
    else:
        steps = [
            "未稳定识别到完整实验章节，建议回到 PDF 的 Evaluation/Results/Experiment 附近人工核对。",
            "优先补齐数据集、划分方式、基线方法、指标定义和是否公开代码这四类复现要素。",
            "若正文只给出案例或系统描述，可将其作为架构/方法参考，而不是直接作为可复现实验结论。",
        ]
    info = {
        "datasets": datasets,
        "dataset_phrases": dataset_phrases,
        "metrics": metrics,
        "baselines": baselines,
        "has_experiment_section": has_exp_section,
    }
    return steps, info


def derive_summary_and_open_issues(paper: dict, sections: dict, body_text: str, exp_info: dict) -> tuple[list[str], list[str]]:
    conclusion_text = sections.get("conclusion", "") or sections.get("discussion", "") or body_text[-18000:]
    conclusion_sents = pick_sentences(conclusion_text, CONCLUSION_KEYWORDS + EXPERIMENT_KEYWORDS, 3)
    summary = [
        f"本文在“{paper.get('category', '')}”方向上的价值，是把“{base.infer_research_object(paper)}”进一步组织成可分析的问题、方法或系统评测对象。",
        f"与本项目的关系：{base.project_module(paper)}；相关性为{paper.get('relevance_tier', '')}，适合按该层级决定精读和复现优先级。",
    ]
    for sent in conclusion_sents[:2]:
        summary.append("正文结论线索：" + short_evidence(sent, 150))
    issues = base.limitation_points(paper, paper.get("abstract", ""), body_text[:6000])
    if not exp_info.get("datasets") and not exp_info.get("dataset_phrases"):
        issues.append("正文自动抽取未稳定识别到明确数据集，复现前需要人工核对实验数据来源与采集条件。")
    if not exp_info.get("metrics"):
        issues.append("正文自动抽取未稳定识别到完整评价指标，需确认是否报告误报率、召回率、F1/AUC、延迟或吞吐。")
    if paper.get("code_status") != "已下载":
        issues.append("当前没有本地可用代码，需要额外确认作者主页、GitHub、Zenodo 或补充实现成本。")
    return list(dict.fromkeys(summary))[:5], list(dict.fromkeys(issues))[:6]


def section_map_lines(section_info: dict) -> list[str]:
    sections = section_info["sections"]
    order = section_info["order"]
    if not sections:
        return ["- 未识别到稳定章节标题；已按全文正文、题录、摘要和关键词进行降级解析。"]
    lines = []
    for key in order:
        if key in sections:
            text = compact_space(sections[key])
            lines.append(f"- **{SECTION_CN.get(key, key)}**：约 {len(text)} 字符；用于解析“{section_usage(key)}”。")
    return lines[:10]


def section_usage(key: str) -> str:
    return {
        "abstract": "整体问题与贡献",
        "introduction": "具体问题、动机和挑战",
        "background": "任务假设、威胁模型和预备知识",
        "related_work": "技术谱系与差异点",
        "method": "科学方法、模型结构和算法流程",
        "experiment": "实验步骤、数据集、基线和评价指标",
        "discussion": "结果解释、消融和适用边界",
        "conclusion": "结论、限制和未来工作",
    }.get(key, "正文证据")


def make_fulltext_doc(paper: dict, filename: str, quality: dict) -> str:
    num = int(paper["num"])
    raw = read_full_text(num)
    if not raw:
        raw = base.read_cache(num)
    section_info = split_sections(raw)
    sections = section_info["sections"]
    body_text = section_info["body_text"] or raw

    problem_points = derive_problem_points(paper, sections, body_text)
    innovation_points = derive_innovation_points(paper, sections, body_text)
    science_questions = derive_science_questions(paper, problem_points, body_text)
    method_steps = build_method_steps(paper, sections, body_text)
    experiment_steps, exp_info = build_experiment_steps(paper, sections, body_text)
    summary_points, open_issues = derive_summary_and_open_issues(paper, sections, body_text, exp_info)

    quality.update({
        "chars": len(raw),
        "body_chars": len(body_text),
        "sections": ",".join(section_info["order"]),
        "section_count": len(sections),
        "has_method_section": bool(sections.get("method")),
        "has_experiment_section": bool(sections.get("experiment")),
        "has_conclusion_section": bool(sections.get("conclusion")),
        "dataset_count": len(exp_info["datasets"]) + len(exp_info.get("dataset_phrases", [])),
        "metric_count": len(exp_info["metrics"]),
    })

    title = paper.get("title", "")
    translated_title = base.term_translate_title(title)
    secondary = "、".join(paper.get("secondary_categories", [])) if paper.get("secondary_categories") else "无"
    code = paper.get("code_repositories") or "无"
    if exp_info["datasets"]:
        datasets = "、".join(exp_info["datasets"])
    elif exp_info.get("dataset_phrases"):
        datasets = "正文场景线索：" + "；".join(exp_info["dataset_phrases"][:2])
    else:
        datasets = "未稳定识别"
    metrics = "、".join(exp_info["metrics"]) if exp_info["metrics"] else "未稳定识别"
    baselines = "、".join(exp_info["baselines"]) if exp_info["baselines"] else "未稳定识别"

    lines = [
        f"# [{num:03d}] {title}",
        "",
        "## 1. 基本信息",
        "",
        f"- **原始题名**：{title}",
        f"- **题名中文释义**：{translated_title}",
        f"- **年份**：{paper.get('year') or '未知'}",
        f"- **DOI**：{paper.get('doi') or '无'}",
        f"- **来源/会议期刊**：{paper.get('venue') or '未识别'}",
        f"- **PDF**：`{paper.get('pdf') or '无'}`",
        f"- **大类**：{paper.get('category', '')}",
        f"- **二级关联**：{secondary}",
        f"- **相关性**：{paper.get('relevance_tier', '')}（分数 {paper.get('relevance_score', '')}）",
        f"- **代码状态**：{paper.get('code_status', '')}；{code}",
        "",
        "## 2. 正文阅读范围与章节地图",
        "",
        f"- **全文抽取状态**：缓存 `{FULL_TEXT_CACHE.name}/{num:03d}.txt`，约 {len(raw)} 字符；去除参考文献后的正文约 {len(body_text)} 字符。",
        f"- **正文解析依据**：优先使用 PDF 全文中的引言、方法、实验、讨论与结论章节；章节缺失时使用全文片段、题录、摘要和分类标签降级推断。",
        f"- **识别章节数**：{len(sections)}；参考文献截断：{'是' if section_info['reference_start'] else '否'}。",
        "",
    ]
    lines.extend(section_map_lines(section_info))
    lines += [
        "",
        "## 3. 具体问题与研究动机",
        "",
        f"本文主要面向**{base.infer_research_object(paper)}**。从正文看，它不是单纯讨论一个模型名称，而是在给定数据可见性、部署约束和评测口径下，尝试回答以下具体问题：",
        "",
    ]
    for item in problem_points:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 4. 创新点归纳",
        "",
        "结合题名、摘要、引言贡献句和方法章节，本文的创新点可归纳为：",
        "",
    ]
    for item in innovation_points:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 5. 科学问题抽象",
        "",
        "从项目视角，可把本文提升为以下科学问题，而不只是一篇单点应用论文：",
        "",
    ]
    for item in science_questions:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 6. 科学方法与技术路线",
        "",
        "正文中的方法可以按如下流程复盘：",
        "",
    ]
    for idx, step in enumerate(method_steps, 1):
        lines.append(f"{idx}. {step}")
    lines += [
        "",
        "## 7. 实验设计、数据与评价步骤",
        "",
        f"- **数据集/场景线索**：{datasets}",
        f"- **评价指标线索**：{metrics}",
        f"- **基线/对照线索**：{baselines}",
        f"- **是否识别到独立实验章节**：{'是' if exp_info['has_experiment_section'] else '否'}",
        "",
        "建议按以下步骤复核或复现实验：",
        "",
    ]
    for idx, step in enumerate(experiment_steps, 1):
        lines.append(f"{idx}. {step}")
    lines += [
        "",
        "## 8. 总结、精华与待解决问题",
        "",
        "### 8.1 本篇精华",
        "",
    ]
    for item in summary_points:
        lines.append(f"- {item}")
    lines += [
        "",
        "### 8.2 待解决问题与复核重点",
        "",
    ]
    for item in open_issues:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 9. 建议阅读方式",
        "",
        "1. 先读引言末尾的贡献段，确认本文声称解决的具体问题和增量。",
        "2. 再读方法章节，把输入、表示、模型、训练目标和输出逐项写成可复现流程。",
        "3. 精读实验章节，核对数据集、划分方式、基线、指标和消融实验是否支撑作者结论。",
        "4. 若代码已下载，优先对照 README、数据处理脚本、模型定义和训练入口，确认论文流程能否落到源码。",
        "",
        "[返回索引](../05_逐篇中文解析.md)",
        "",
    ]
    return "\n".join(lines)


def make_index(papers: list[dict], file_map: dict[int, str], quality_rows: list[dict]) -> str:
    index = base.make_index(papers, file_map)
    quality = {
        "with_method": sum(1 for r in quality_rows if r.get("has_method_section")),
        "with_experiment": sum(1 for r in quality_rows if r.get("has_experiment_section")),
        "with_conclusion": sum(1 for r in quality_rows if r.get("has_conclusion_section")),
        "avg_chars": int(sum(int(r.get("chars") or 0) for r in quality_rows) / max(1, len(quality_rows))),
    }
    replacement = (
        "本文件现在作为 850 篇论文正文级详细解析的总索引。每篇论文的独立文档已基于 PDF 全文文本、章节标题、"
        "引言/方法/实验/结论等正文线索重新生成，并在有开源代码时继续保留代码对照分析。"
    )
    index = re.sub(
        r"本文件现在作为 850 篇论文详细解析的总索引。.*?`逐篇中文解析/` 文件夹中。",
        replacement,
        index,
        count=1,
        flags=re.S,
    )
    insert = [
        "",
        "## 正文级解析质量概览",
        "",
        f"- 平均全文抽取长度：约 {quality['avg_chars']} 字符/篇",
        f"- 识别到方法/模型章节：{quality['with_method']} 篇",
        f"- 识别到实验/评估章节：{quality['with_experiment']} 篇",
        f"- 识别到结论/未来工作章节：{quality['with_conclusion']} 篇",
        f"- 质量明细：[`正文解析质量统计.csv`](正文解析质量统计.csv)、[`08_正文级逐篇解析质量报告.md`](08_正文级逐篇解析质量报告.md)",
        "",
    ]
    return index.replace("## 大类索引", "\n".join(insert) + "\n## 大类索引", 1)


def write_quality_reports(quality_rows: list[dict], extraction_results: list[dict]) -> None:
    fieldnames = [
        "num", "title", "chars", "body_chars", "section_count", "sections",
        "has_method_section", "has_experiment_section", "has_conclusion_section",
        "dataset_count", "metric_count", "extract_ok", "extract_error",
    ]
    with QUALITY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in quality_rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    ok = sum(1 for r in extraction_results if r.get("ok"))
    failed = [r for r in extraction_results if not r.get("ok")]
    section_counter = Counter()
    for row in quality_rows:
        for key in str(row.get("sections", "")).split(","):
            if key:
                section_counter[key] += 1
    lines = [
        "# 08 正文级逐篇解析质量报告",
        "",
        f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "本报告说明 `逐篇中文解析/` 下 850 个独立文档的正文级解析来源和自动抽取质量。解析以 PDF 全文为主，识别引言、方法、实验、讨论和结论等章节，再提炼具体问题、创新点、科学问题、科学方法、实验步骤、总结和待解决问题。",
        "",
        "## 抽取概况",
        "",
        f"- PDF 全文抽取成功：{ok} / {len(extraction_results)}",
        f"- 需要降级解析：{len(failed)} 篇",
        f"- 平均全文字符数：{int(sum(int(r.get('chars') or 0) for r in quality_rows) / max(1, len(quality_rows)))}",
        f"- 识别到方法/模型章节：{sum(1 for r in quality_rows if r.get('has_method_section'))} 篇",
        f"- 识别到实验/评估章节：{sum(1 for r in quality_rows if r.get('has_experiment_section'))} 篇",
        f"- 识别到结论/未来工作章节：{sum(1 for r in quality_rows if r.get('has_conclusion_section'))} 篇",
        "",
        "## 章节识别分布",
        "",
        "| 章节 | 篇数 |",
        "|---|---:|",
    ]
    for key, count in section_counter.most_common():
        lines.append(f"| {SECTION_CN.get(key, key)} | {count} |")
    if failed:
        lines += [
            "",
            "## 抽取失败或降级论文",
            "",
            "| 编号 | 错误 |",
            "|---:|---|",
        ]
        for r in failed[:80]:
            lines.append(f"| {r.get('num')} | {str(r.get('error') or '').replace('|', '/')} |")
        if len(failed) > 80:
            lines.append(f"| ... | 另有 {len(failed) - 80} 篇，详见 `_data/fulltext_analysis_manifest.json` |")
    lines += [
        "",
        "## 使用建议",
        "",
        "- 对强相关且有代码的论文，优先打开单篇文档中的“科学方法与技术路线”“实验设计、数据与评价步骤”“代码对照分析”。",
        "- 对未识别到实验章节的理论、综述、书籍和报告类文献，应把它们作为背景、分类框架或问题定义材料，而不是直接作为复现实验论文。",
        "- 自动抽取不能替代人工精读；当文档提示数据集、指标或章节未稳定识别时，需要回到原 PDF 对相应章节进行复核。",
        "",
    ]
    QUALITY_MD.write_text("\n".join(lines), encoding="utf-8")


def extract_all_full_text(papers: list[dict]) -> list[dict]:
    results = []
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_full_text, paper): paper for paper in papers}
        done = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            done += 1
            if done % 25 == 0 or done == len(papers):
                print(f"full-text extracted {done}/{len(papers)}")
    return sorted(results, key=lambda r: int(r["num"]))


def main() -> None:
    ensure_dirs()
    papers = base.load_papers()
    extraction_results = extract_all_full_text(papers)

    if INDEX.exists() and not BACKUP_INDEX.exists():
        shutil.copy2(INDEX, BACKUP_INDEX)

    for old in DETAIL_DIR.glob("*.md"):
        old.unlink()

    file_map: dict[int, str] = {}
    quality_rows: list[dict] = []
    for paper in papers:
        filename = base.safe_filename(int(paper["num"]), paper.get("title", ""))
        file_map[int(paper["num"])] = filename
        quality = {"num": paper["num"], "title": paper.get("title", "")}
        doc = make_fulltext_doc(paper, filename, quality)
        (DETAIL_DIR / filename).write_text(doc, encoding="utf-8")
        quality_rows.append(quality)

    INDEX.write_text(make_index(papers, file_map, quality_rows), encoding="utf-8")
    write_quality_reports(quality_rows, extraction_results)

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(papers),
        "detail_dir": str(DETAIL_DIR),
        "index": str(INDEX),
        "full_text_cache": str(FULL_TEXT_CACHE),
        "files": file_map,
        "quality_csv": str(QUALITY_CSV),
        "quality_md": str(QUALITY_MD),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    FULLTEXT_MANIFEST.write_text(
        json.dumps({
            "generated_at": manifest["generated_at"],
            "extraction_results": extraction_results,
            "quality_rows": quality_rows,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        "papers": len(papers),
        "detail_docs": len(list(DETAIL_DIR.glob("*.md"))),
        "fulltext_ok": sum(1 for r in extraction_results if r.get("ok")),
        "quality_csv": str(QUALITY_CSV),
        "quality_md": str(QUALITY_MD),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
