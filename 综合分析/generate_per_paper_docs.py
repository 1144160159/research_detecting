# -*- coding: utf-8 -*-
"""Generate one detailed Chinese analysis document for each paper.

The top-level 05_逐篇中文解析.md becomes an index. Per-paper documents are written to:
综合分析/逐篇中文解析/
"""

import json
import re
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "综合分析"
DATA = OUT / "_data"
TEXT_CACHE = DATA / "text_cache"
DETAIL_DIR = OUT / "逐篇中文解析"
INDEX = OUT / "05_逐篇中文解析.md"
BACKUP = OUT / "05_逐篇中文解析_旧版备份.md"


CATEGORY_MEANING = {
    "加密流量分类与应用识别": "直接对应系统中的加密流量识别、应用分类、协议/服务识别和网站指纹模块。",
    "恶意流量、暗网与攻击检测": "直接服务恶意通信发现、暗网流量刻画、隧道识别、僵尸网络和攻击流量检测。",
    "入侵检测与网络异常检测": "对应 NIDS/IDS、未知攻击检测、异常评分、告警筛选和网络安全运营主链路。",
    "网络流量监测、测量与工具": "支撑流量采集、测量、NetFlow/PCAP 处理、在线监测和工具链建设。",
    "IoT、车联网、工业互联网与边缘安全": "适合迁移到物联网、车联网、工业控制、边缘网关和 5G 场景。",
    "图学习、知识图谱与威胁情报": "适合构建主机-流-告警-实体-威胁情报的关联分析和溯源图层。",
    "时序、日志、KPI 与云原生异常检测": "可迁移到日志/KPI/微服务监控、时序异常检测和根因分析模块。",
    "多媒体、医学、遥感与视频异常检测": "主要提供跨域异常检测方法，可借鉴表征学习、弱监督和异常定位思路。",
    "联邦学习、隐私保护与分布式协同": "支撑多机构、多边界设备不共享原始流量的协同建模与隐私保护训练。",
    "数据集、基准、综述与开源工具": "适合做综述背景、评测基准、数据集选择、工具链选型和引用依据。",
    "基础理论、密码协议与安全机制": "提供密码协议、网络体系结构、安全机制等基础理论背景。",
    "其他AI安全与跨域异常检测": "可作为通用 AI 异常检测、鲁棒学习和跨域方法迁移参考。",
}


INNOVATION_EXPLAIN = {
    "表征学习、预训练与Transformer": "强调从字节、包、流、日志或实体序列中学习上下文表征，适合作为统一特征底座。",
    "图神经网络与关系建模": "强调节点、边、会话、主机、告警和情报实体之间的关系建模，适合关联检测与溯源。",
    "多模态、多视图与特征融合": "强调融合统计、时序、内容、图结构、上下文等多源信息以降低误报。",
    "自监督、对比学习与少样本学习": "强调减少人工标签依赖，适合未知攻击、低标注和类别不平衡场景。",
    "生成式增强、GAN与扩散模型": "强调合成少数类、增强训练样本或模拟攻击扰动，需要注意生成分布是否真实。",
    "联邦学习、隐私保护与协同训练": "强调多节点协同和隐私保护，适合跨机构安全数据不能直接共享的场景。",
    "在线、增量、开放集与概念漂移": "强调模型在真实网络变化中的持续更新、漂移感知和未知类处理。",
    "可解释性、规则抽取与因果分析": "强调让模型输出可被安全分析员理解、审计和转化为规则。",
    "轻量化、实时与高性能部署": "强调吞吐、延迟、资源占用和工程部署，适合在线检测链路。",
    "鲁棒性、对抗防御与可信检测": "强调抵抗规避、投毒、噪声和分布外样本，适合真实对抗环境。",
    "数据集、基准、工具与系统化评测": "强调复现、横向比较和工程评估，是构建 benchmark 的基础。",
    "应用场景与系统化验证": "强调问题定义、应用落地和系统组合，可作为场景设计参考。",
}


SCIENCE_EXPLAIN = {
    "加密与隐私保护造成可观测特征缺失": "不能依赖明文内容，需要从流统计、包长时序、方向序列、证书/握手元数据和关系图中学习。",
    "标签稀缺、类别不平衡与长尾攻击": "安全样本标注昂贵且新攻击样本少，需要自监督、半监督、少样本和数据增强机制。",
    "域迁移、概念漂移与真实网络分布变化": "实验室数据与真实网络差异明显，模型需要跨域泛化、漂移检测和持续更新。",
    "高速流量实时检测与资源约束": "在线系统必须兼顾吞吐、延迟和计算成本，不能只追求离线准确率。",
    "多源异构数据融合与上下文建模": "单一流特征不足以解释复杂攻击，需要把流量、主机、日志、告警和情报关联起来。",
    "模型可解释、可信与可审计": "安全运营需要知道为什么告警、相似样本是什么、证据链在哪里。",
    "对抗规避、污染与鲁棒性": "攻击者会主动规避检测或污染数据，模型必须评估鲁棒性和风险边界。",
    "数据集代表性、标准化评测与可复现": "数据集老化和评测口径不一致会削弱结论，需要统一 benchmark 和复现实验。",
    "边缘、IoT、车联网与工业场景约束": "协议、设备、算力和业务约束不同，模型需要轻量化和场景适配。",
    "开放世界未知攻击与误报控制": "真实系统不断出现未知类，关键是发现新异常并控制误报成本。",
}


TECH_TERM_CN = [
    ("multi-instance encrypted traffic transformer", "多实例加密流量 Transformer"),
    ("flow sequence network", "流序列网络"),
    ("new directions in cryptography", "密码学的新方向"),
    ("digital signatures and public-key cryptosystems", "数字签名与公钥密码系统"),
    ("public-key cryptosystems", "公钥密码系统"),
    ("public-key", "公钥"),
    ("digital signatures", "数字签名"),
    ("computer network architectures and protocols", "计算机网络体系结构与协议"),
    ("secret communication", "秘密通信"),
    ("ancient times", "古代"),
    ("netflow services and applications", "NetFlow 服务与应用"),
    ("services and applications", "服务与应用"),
    ("network architectures", "网络体系结构"),
    ("network protocols", "网络协议"),
    ("mobile-app fingerprinting", "移动应用指纹识别"),
    ("traffic capture", "流量采集"),
    ("encrypted traffic classification", "加密流量分类"),
    ("encrypted malicious traffic", "恶意加密流量"),
    ("network traffic monitoring", "网络流量监测"),
    ("network traffic analysis", "网络流量分析"),
    ("intrusion detection system", "入侵检测系统"),
    ("intrusion detection", "入侵检测"),
    ("anomaly detection", "异常检测"),
    ("malware detection", "恶意软件检测"),
    ("malware classification", "恶意软件分类"),
    ("traffic classification", "流量分类"),
    ("application identification", "应用识别"),
    ("website fingerprinting", "网站指纹识别"),
    ("darknet traffic", "暗网流量"),
    ("malicious traffic", "恶意流量"),
    ("network anomaly", "网络异常"),
    ("time series", "时间序列"),
    ("knowledge graph", "知识图谱"),
    ("graph neural network", "图神经网络"),
    ("federated learning", "联邦学习"),
    ("self-supervised", "自监督"),
    ("semi-supervised", "半监督"),
    ("weakly supervised", "弱监督"),
    ("contrastive learning", "对比学习"),
    ("few-shot", "少样本"),
    ("zero-shot", "零样本"),
    ("open set", "开放集"),
    ("concept drift", "概念漂移"),
    ("transformer", "Transformer"),
    ("autoencoder", "自编码器"),
    ("generative adversarial network", "生成对抗网络"),
    ("deep learning", "深度学习"),
    ("machine learning", "机器学习"),
    ("convolutional neural network", "卷积神经网络"),
    ("recurrent neural network", "循环神经网络"),
    ("multi-modal", "多模态"),
    ("multimodal", "多模态"),
    ("multi-view", "多视图"),
    ("real-time", "实时"),
    ("online", "在线"),
    ("lightweight", "轻量化"),
    ("robust", "鲁棒"),
    ("explainable", "可解释"),
    ("privacy-preserving", "隐私保护"),
    ("dataset", "数据集"),
    ("benchmark", "基准"),
    ("survey", "综述"),
    ("review", "综述"),
    ("framework", "框架"),
    ("approach", "方法"),
    ("method", "方法"),
    ("model", "模型"),
    ("system", "系统"),
    ("classification", "分类"),
    ("detection", "检测"),
    ("analysis", "分析"),
    ("monitoring", "监测"),
    ("security", "安全"),
    ("network", "网络"),
    ("traffic", "流量"),
    ("based on", "基于"),
    ("using", "使用"),
    ("with", "结合"),
    ("for", "面向"),
    ("and", "与"),
    ("in", "在"),
    ("of", "的"),
]


KNOWN_DATASETS = [
    "CICIDS2017", "CICIDS2018", "CICIoT2023", "UNSW-NB15", "NSL-KDD",
    "KDD", "ISCX", "USTC-TFC", "ISCXVPN2016", "ISCXTor2016", "Bot-IoT",
    "ToN_IoT", "TON_IoT", "CTU-13", "MAWI", "CAIDA", "MIRAGE",
    "CESNET-QUIC22", "CSE-CIC-IDS2018", "Darknet2020", "VPN-nonVPN",
    "IoT-23", "Edge-IIoTset", "N-BaIoT", "BoT-IoT", "DAPT", "CERT",
    "SWaT", "WADI", "SMD", "SMAP", "MSL", "MVTec", "ShanghaiTech",
]


METRIC_TERMS = [
    "accuracy", "precision", "recall", "f1", "f1-score", "auc", "roc",
    "far", "fpr", "tpr", "detection rate", "false positive", "latency",
    "throughput", "macro-f1", "micro-f1",
]


def clean_spaces(text):
    return re.sub(r"\s+", " ", text or "").strip()


def safe_filename(num, title):
    name = re.sub(r'[<>:"/\\|?*\n\r\t()\[\]{}]+', "_", title or "untitled")
    name = re.sub(r"\s+", "_", name).strip("._ ")
    if not name:
        name = "paper"
    if len(name) > 92:
        name = name[:92].rstrip("._- ")
    return "%03d_%s.md" % (num, name)


def term_translate_title(title):
    text = title or ""
    translated = text
    for en, cn in sorted(TECH_TERM_CN, key=lambda x: len(x[0]), reverse=True):
        escaped = re.escape(en)
        if re.match(r"^[A-Za-z0-9]", en) and re.search(r"[A-Za-z0-9]$", en):
            pattern = r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % escaped
        else:
            pattern = escaped
        translated = re.sub(pattern, cn, translated, flags=re.IGNORECASE)
    translated = translated.replace(":", "：")
    translated = re.sub(r"\s+", " ", translated).strip()
    translated = translated.replace(" 基于 ", " 基于")
    return translated


def load_papers():
    path = DATA / "papers_enriched.json"
    return json.loads(path.read_text(encoding="utf-8"))


def read_cache(num):
    path = TEXT_CACHE / ("%03d.txt" % num)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def split_sentences(text):
    text = clean_spaces(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?。！？])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 20]


def pick_sentence(sentences, keywords, fallback_index=0):
    low_keywords = [k.lower() for k in keywords]
    for sent in sentences:
        low = sent.lower()
        if any(k in low for k in low_keywords):
            return sent
    if sentences:
        return sentences[min(fallback_index, len(sentences) - 1)]
    return ""


def concise_hint(sentence, max_len=260):
    sentence = clean_spaces(sentence)
    if len(sentence) <= max_len:
        return sentence
    return sentence[:max_len].rstrip() + "..."


def find_terms(text, candidates):
    low = text.lower()
    found = []
    for item in candidates:
        if item.lower() in low and item not in found:
            found.append(item)
    return found


def infer_research_object(paper):
    title = paper.get("title", "")
    category = paper.get("category", "")
    if "加密流量" in category:
        return "加密网络流量、应用行为或网站/代理访问模式"
    if "恶意流量" in category:
        return "恶意通信、暗网流量、攻击流量或隐蔽通道"
    if "入侵检测" in category:
        return "网络入侵、异常行为、未知攻击或告警事件"
    if "监测" in category:
        return "网络流量采集、测量、监测工具和分析链路"
    if "IoT" in category:
        return "IoT/车联网/工业互联网/边缘设备产生的安全数据"
    if "图学习" in category:
        return "流量实体、主机关系、威胁情报或安全事件图"
    if "时序" in category:
        return "日志、KPI、多变量时间序列或云原生运行状态"
    if "多媒体" in category:
        return "图像、视频、医学、遥感或其他跨域异常样本"
    if "联邦" in category:
        return "分布式节点、多机构数据或隐私受限的安全样本"
    if "数据集" in category:
        return "数据集、基准、综述对象或工具链"
    if "密码" in category:
        return "密码协议、网络安全机制或基础理论问题"
    return "与异常检测、安全分析或机器学习检测相关的研究对象"


def infer_method_route(paper):
    innovations = paper.get("innovations", [])
    methods = paper.get("method_keywords", [])
    pieces = []
    if any("表征学习" in x for x in innovations):
        pieces.append("先将原始数据转换为可学习的序列/向量表示")
    if any("图神经" in x for x in innovations):
        pieces.append("再利用图结构刻画实体之间的依赖关系")
    if any("多模态" in x for x in innovations):
        pieces.append("融合多源特征或多视图信息以增强判别能力")
    if any("自监督" in x for x in innovations):
        pieces.append("通过自监督/对比学习缓解标签不足")
    if any("生成式" in x for x in innovations):
        pieces.append("借助生成式模型进行样本增强或攻击模拟")
    if any("联邦" in x for x in innovations):
        pieces.append("通过联邦或分布式训练保护数据隐私")
    if any("在线" in x for x in innovations):
        pieces.append("面向在线增量、开放集或概念漂移进行持续适配")
    if any("可解释" in x for x in innovations):
        pieces.append("输出解释、规则或原型以支撑人工研判")
    if any("轻量化" in x for x in innovations):
        pieces.append("压缩计算链路以满足实时或边缘部署")
    if not pieces:
        pieces.append("围绕任务对象构建特征、模型、评测和应用验证流程")
    if methods:
        pieces.append("题名/摘要中出现的关键方法或对象包括：" + "、".join(methods[:8]))
    return "；".join(pieces) + "。"


def project_module(paper):
    category = paper.get("category", "")
    if "加密流量" in category:
        return "加密流量识别与应用分类模块"
    if "恶意流量" in category:
        return "恶意流量检测与威胁发现模块"
    if "入侵检测" in category:
        return "网络入侵检测与异常告警模块"
    if "监测" in category:
        return "流量采集、监测和数据治理模块"
    if "IoT" in category:
        return "IoT/车联网/边缘安全检测模块"
    if "图学习" in category:
        return "图关联分析、知识图谱和溯源模块"
    if "时序" in category:
        return "日志/KPI/时序异常检测模块"
    if "联邦" in category:
        return "隐私保护协同训练模块"
    if "数据集" in category:
        return "数据集、benchmark 和综述支撑模块"
    return "通用异常检测方法库或背景知识模块"


def limitation_points(paper, abstract, text):
    points = []
    low = (paper.get("title", "") + " " + abstract + " " + text[:2000]).lower()
    if "dataset" in low or "benchmark" in low:
        points.append("需要核对数据集年份、采集环境和类别定义是否与当前真实网络一致。")
    if "encrypted" in low or "traffic" in low:
        points.append("需要关注实验流量是否存在采集环境偏差，以及在跨网络、跨应用版本上的泛化能力。")
    if "deep" in low or "transformer" in low or "gnn" in low:
        points.append("需要复核模型复杂度、推理延迟和资源消耗，避免只在离线指标上成立。")
    if "federated" in low or "privacy" in low:
        points.append("需要进一步验证通信开销、节点异构、隐私预算和异常客户端鲁棒性。")
    if "explain" in low or "interpret" in low:
        points.append("需要检查解释结果是否能被安全分析员稳定理解，而不仅是模型内部可视化。")
    if not points:
        points.append("需要回到原文核对实验设置、对比基线、数据规模和评价指标，确认结论的可迁移边界。")
    return points[:4]


def essence_points(paper):
    module = project_module(paper)
    category = paper.get("category", "")
    innovations = paper.get("innovations", [])
    science = paper.get("science_problems", [])
    points = [
        "这篇文章的核心价值在于把“%s”问题落到“%s”方向中，为%s提供参考。" % (
            science[0] if science else "安全检测",
            category,
            module,
        )
    ]
    if innovations:
        points.append("方法精华是“%s”，可抽象为系统中的可复用技术组件。" % " + ".join(innovations[:2]))
    if paper.get("code_status") == "已下载":
        points.append("已发现并下载代码，适合优先进入复现实验和工程比对。")
    elif paper.get("relevance_tier") == "强相关":
        points.append("虽未必有可用代码，但主题强相关，适合作为模型设计或实验对比的重要参考。")
    else:
        points.append("更适合作为综述背景、方法迁移或问题定义的支撑材料。")
    return points


def evidence_block(paper, abstract, text):
    sentences = split_sentences(abstract or text[:2500])
    problem = pick_sentence(sentences, ["challenge", "problem", "difficult", "however", "lack", "need", "privacy", "encrypted"], 0)
    method = pick_sentence(sentences, ["propose", "present", "develop", "design", "framework", "model", "method", "approach"], 1)
    result = pick_sentence(sentences, ["experiment", "evaluation", "result", "outperform", "achieve", "accuracy", "f1", "auc"], 2)
    # Keep these as summarized evidence clues, not long verbatim quotes.
    items = []
    if problem:
        items.append("问题线索：" + concise_hint(problem, 220))
    if method and method != problem:
        items.append("方法线索：" + concise_hint(method, 220))
    if result and result not in {problem, method}:
        items.append("实验/结论线索：" + concise_hint(result, 220))
    if not items:
        items.append("PDF 前几页未抽取到稳定摘要，当前解析主要依据题名、分类标签、年份、DOI 和代码索引。")
    return items


def make_doc(paper, filename):
    num = paper["num"]
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    text = read_cache(num)
    source_text = " ".join([title, abstract, paper.get("keywords", ""), text[:6000]])
    datasets = find_terms(source_text, KNOWN_DATASETS)
    metrics = find_terms(source_text, METRIC_TERMS)
    translated_title = term_translate_title(title)
    interp = paper.get("interpretation", {})
    evidence = evidence_block(paper, abstract, text)
    limitations = limitation_points(paper, abstract, text)
    essence = essence_points(paper)

    innovation_lines = []
    for item in paper.get("innovations", []):
        innovation_lines.append("- **%s**：%s" % (item, INNOVATION_EXPLAIN.get(item, "该标签指向可复用的方法或系统设计思路。")))
    science_lines = []
    for item in paper.get("science_problems", []):
        science_lines.append("- **%s**：%s" % (item, SCIENCE_EXPLAIN.get(item, "该问题需要结合原文进一步确认。")))

    dataset_text = "、".join(datasets) if datasets else "未在前几页稳定抽取到明确数据集名称，需回到实验章节复核。"
    metric_text = "、".join(metrics) if metrics else "未在前几页稳定抽取到明确指标；通常需核对 Accuracy、F1、AUC、误报率、检测率、延迟等指标。"
    code = paper.get("code_repositories") or "无"
    secondary = "、".join(paper.get("secondary_categories", [])) if paper.get("secondary_categories") else "无"
    methods = "、".join(paper.get("method_keywords", [])) if paper.get("method_keywords") else "未从题名/摘要中抽取到稳定方法缩写"

    lines = [
        "# [%03d] %s" % (num, title),
        "",
        "## 1. 基本信息",
        "",
        "- **原始题名**：%s" % title,
        "- **题名中文释义**：%s" % translated_title,
        "- **年份**：%s" % (paper.get("year") or "未知"),
        "- **DOI**：%s" % (paper.get("doi") or "无"),
        "- **来源/会议期刊**：%s" % (paper.get("venue") or "未识别"),
        "- **PDF**：`%s`" % (paper.get("pdf") or "无"),
        "- **大类**：%s" % paper.get("category", ""),
        "- **二级关联**：%s" % secondary,
        "- **相关性**：%s（分数 %s）" % (paper.get("relevance_tier", ""), paper.get("relevance_score", "")),
        "- **代码状态**：%s；%s" % (paper.get("code_status", ""), code),
        "",
        "## 2. 论文解决的核心问题",
        "",
        "本文主要面向**%s**。在当前文献库中，它被归入“%s”，说明其与“AI驱动的网络流量检测分析系统”的关系是：%s" % (
            infer_research_object(paper),
            paper.get("category", ""),
            CATEGORY_MEANING.get(paper.get("category", ""), "可作为相关技术或背景材料。"),
        ),
        "",
        "从科学问题看，本文至少触及以下问题：",
        "",
    ]
    lines.extend(science_lines)
    lines += [
        "",
        "## 3. 方法路线与技术抓手",
        "",
        infer_method_route(paper),
        "",
        "- **方法/对象关键词**：%s" % methods,
        "- **创新点标签**：%s" % "、".join(paper.get("innovations", [])),
        "",
        "具体来看：",
        "",
    ]
    lines.extend(innovation_lines)
    lines += [
        "",
        "## 4. 摘要与内容线索的中文解读",
        "",
    ]
    if abstract:
        lines += [
            "PDF 前几页抽取到摘要。摘要显示，本文围绕任务背景、模型/框架设计和实验验证展开。为了避免把原文长段落直接搬运，这里提炼为三类线索：",
            "",
        ]
    else:
        lines += [
            "未从 PDF 前几页稳定抽取到摘要，以下依据题名、分类标签、关键词和文献索引进行结构化解读：",
            "",
        ]
    for item in evidence:
        lines.append("- %s" % item)
    lines += [
        "",
        "## 5. 实验、数据与评价线索",
        "",
        "- **数据集/场景线索**：%s" % dataset_text,
        "- **评价指标线索**：%s" % metric_text,
        "- **复现优先级判断**：%s" % (
            "高。该文强相关且已有本地代码，可优先检查 README、数据预处理脚本和训练入口。"
            if paper.get("relevance_tier") == "强相关" and paper.get("code_status") == "已下载"
            else "中。建议先核对实验数据、指标和基线，再决定是否复现。"
            if paper.get("relevance_tier") == "强相关"
            else "视综述需要而定，可作为方法或背景补充。"
        ),
        "",
        "## 6. 对本项目的价值",
        "",
        "- **可服务模块**：%s。" % project_module(paper),
        "- **可借鉴点**：%s" % (interp.get("usage") or paper.get("relevance_reason") or "可结合原文进一步判断。"),
        "- **工程化启发**：如果纳入系统实现，应重点关注数据输入格式、特征构造、模型复杂度、在线推理成本和告警解释方式。",
        "",
        "## 7. 局限与复核要点",
        "",
    ]
    for item in limitations:
        lines.append("- %s" % item)
    lines += [
        "",
        "## 8. 本篇精华总结",
        "",
    ]
    for item in essence:
        lines.append("- %s" % item)
    lines += [
        "",
        "## 9. 建议阅读方式",
        "",
        "1. 先读摘要和引言，确认问题定义与应用场景。",
        "2. 再读方法部分，提取输入特征、模型结构和训练目标。",
        "3. 精读实验设置，记录数据集、类别划分、基线方法和指标。",
        "4. 若代码已下载，优先跑通数据预处理和最小训练/推理流程。",
        "",
        "[返回索引](../05_逐篇中文解析.md)",
        "",
    ]
    return "\n".join(lines)


def make_index(papers, file_map):
    category_counter = Counter(p.get("category", "") for p in papers)
    relevance_counter = Counter(p.get("relevance_tier", "") for p in papers)
    code_counter = Counter(p.get("code_status", "") for p in papers)
    lines = [
        "# 05 逐篇中文解析索引",
        "",
        "生成时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "本文件现在作为 %d 篇论文详细解析的总索引。每篇论文的详细中文解析已拆分为独立 Markdown 文档，存放在 `逐篇中文解析/` 文件夹中。" % len(papers),
        "",
        "## 总览",
        "",
        "- 论文总数：%d" % len(papers),
        "- 大类数量：%d" % len(category_counter),
        "- 相关性分布：%s" % "；".join("%s %d篇" % (k, v) for k, v in relevance_counter.most_common()),
        "- 代码状态分布：%s" % "；".join("%s %d篇" % (k, v) for k, v in code_counter.most_common()),
        "",
        "## 大类索引",
        "",
    ]
    grouped = defaultdict(list)
    for paper in papers:
        grouped[paper.get("category", "")].append(paper)
    for category, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        lines += [
            "### %s（%d篇）" % (category, len(group)),
            "",
            "| 编号 | 详细解析 | 年份 | 相关性 | 代码 | 创新点 |",
            "|---:|---|---:|---|---|---|",
        ]
        for p in sorted(group, key=lambda x: x["num"]):
            rel = p.get("relevance_tier", "")
            code = p.get("code_status", "")
            inv = "、".join(p.get("innovations", [])[:2])
            rel_path = "逐篇中文解析/" + file_map[p["num"]]
            lines.append("| %d | [%s](%s) | %s | %s | %s | %s |" % (
                p["num"],
                p.get("title", "").replace("|", "\\|"),
                rel_path.replace(" ", "%20"),
                p.get("year") or "",
                rel,
                code,
                inv.replace("|", "\\|"),
            ))
        lines.append("")
    lines += [
        "## 按编号索引",
        "",
        "| 编号 | 详细解析 | 大类 | 相关性 |",
        "|---:|---|---|---|",
    ]
    for p in sorted(papers, key=lambda x: x["num"]):
        rel_path = "逐篇中文解析/" + file_map[p["num"]]
        lines.append("| %d | [%s](%s) | %s | %s |" % (
            p["num"],
            p.get("title", "").replace("|", "\\|"),
            rel_path.replace(" ", "%20"),
            p.get("category", "").replace("|", "\\|"),
            p.get("relevance_tier", ""),
        ))
    lines.append("")
    return "\n".join(lines)


def main():
    papers = load_papers()
    DETAIL_DIR.mkdir(parents=True, exist_ok=True)
    for old in DETAIL_DIR.glob("*.md"):
        old.unlink()
    if INDEX.exists() and not BACKUP.exists():
        shutil.copy2(INDEX, BACKUP)

    file_map = {}
    for paper in papers:
        filename = safe_filename(paper["num"], paper.get("title", ""))
        file_map[paper["num"]] = filename
        doc = make_doc(paper, filename)
        (DETAIL_DIR / filename).write_text(doc, encoding="utf-8")

    INDEX.write_text(make_index(papers, file_map), encoding="utf-8")

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(papers),
        "detail_dir": str(DETAIL_DIR),
        "index": str(INDEX),
        "files": file_map,
    }
    (DATA / "per_paper_docs_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        "papers": len(papers),
        "detail_docs": len(list(DETAIL_DIR.glob("*.md"))),
        "index": str(INDEX),
        "backup": str(BACKUP) if BACKUP.exists() else "",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
