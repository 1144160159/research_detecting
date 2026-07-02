# -*- coding: utf-8 -*-
"""Scan downloaded source repositories and inject paper-code comparison sections.

Outputs:
- 综合分析/_data/code_repository_summaries.json
- 综合分析/07_代码对照总表.md
- Updates 综合分析/逐篇中文解析/*.md by replacing/appending "## 9. 代码对照分析"
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "综合分析"
DATA = OUT / "_data"
DETAIL_DIR = OUT / "逐篇中文解析"
CODE_INDEX = ROOT / "source" / "_code_search" / "code_repositories_index.json"
PAPERS_JSON = DATA / "papers_enriched.json"
MANIFEST_JSON = DATA / "per_paper_docs_manifest.json"
CODE_SUMMARY_JSON = DATA / "code_repository_summaries.json"
CODE_SUMMARY_CSV = OUT / "代码对照总表.csv"
CODE_SUMMARY_MD = OUT / "07_代码对照总表.md"


SKIP_DIRS = {
    ".git", "__pycache__", ".ipynb_checkpoints", "node_modules", "venv", ".venv",
    "env", ".env", "dist", "build", "target", ".idea", ".vscode", "logs",
    "log", "runs", "wandb", "checkpoints", "checkpoint", "weights", "model_zoo",
    "pretrained", "pretrain", "dataset", "datasets", "data", "raw_data",
    "processed", "results", "result", "outputs", "output", "cache", ".cache",
}

TEXT_EXTS = {
    ".md", ".rst", ".txt", ".py", ".ipynb", ".yml", ".yaml", ".json", ".toml",
    ".ini", ".cfg", ".sh", ".bat", ".ps1", ".m", ".r", ".jl", ".js", ".ts",
    ".java", ".cpp", ".c", ".h", ".hpp", ".cu", ".go", ".rs",
}

LANG_EXTS = {
    ".py": "Python", ".ipynb": "Jupyter", ".m": "MATLAB", ".r": "R", ".jl": "Julia",
    ".js": "JavaScript", ".ts": "TypeScript", ".java": "Java", ".cpp": "C++",
    ".cc": "C++", ".cxx": "C++", ".c": "C", ".h": "C/C++ Header", ".hpp": "C++ Header",
    ".cu": "CUDA", ".go": "Go", ".rs": "Rust", ".sh": "Shell", ".bat": "Batch",
    ".ps1": "PowerShell", ".yaml": "YAML", ".yml": "YAML", ".json": "JSON",
}

ENTRY_PATTERNS = [
    ("训练入口", re.compile(r"(?:^|[/\\])(train|training|main_train|run_train|fit)[^/\\]*\.(py|ipynb|m|sh|bat)$", re.I)),
    ("评估/测试入口", re.compile(r"(?:^|[/\\])(eval|evaluate|test|testing|benchmark|validate|validation)[^/\\]*\.(py|ipynb|m|sh|bat)$", re.I)),
    ("推理/演示入口", re.compile(r"(?:^|[/\\])(infer|inference|predict|demo|example|run|main)[^/\\]*\.(py|ipynb|m|sh|bat)$", re.I)),
    ("数据处理入口", re.compile(r"(?:^|[/\\])(preprocess|process|prepare|feature|extract|dataset|dataloader|loader)[^/\\]*\.(py|ipynb|m|sh|bat)$", re.I)),
    ("模型定义", re.compile(r"(?:^|[/\\])(model|models|net|network|module|layers|architecture)[^/\\]*\.(py|m|java|cpp)$", re.I)),
    ("配置文件", re.compile(r"(?:^|[/\\])(config|configs|setting|settings|params|parameters)[^/\\]*\.(yaml|yml|json|toml|ini|cfg|py)$", re.I)),
    ("依赖环境", re.compile(r"(requirements|environment|env|conda|setup|pyproject|package|dockerfile|Dockerfile|Pipfile)", re.I)),
]

DATASET_HINT_RE = re.compile(
    r"(CICIDS|CICIoT|UNSW|NSL|KDD|ISCX|USTC|VPN|Tor|QUIC|MAWI|CAIDA|Bot-IoT|ToN|IoT-23|MIRAGE|CESNET|MVTec|SMD|SMAP|MSL|SWaT|WADI|CERT|DAPT)",
    re.I,
)

RUN_HINT_RE = re.compile(
    r"(python\s+[^`\n]+|bash\s+[^`\n]+|sh\s+[^`\n]+|matlab\s+[^`\n]+|pip\s+install[^`\n]+|conda\s+[^`\n]+|docker\s+[^`\n]+)",
    re.I,
)


def norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def safe_read(path: Path, max_chars: int = 30000) -> str:
    try:
        if path.stat().st_size > 2_500_000:
            return ""
        data = path.read_bytes()[: max_chars * 3]
        return data.decode("utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def git_remote(path: Path) -> str:
    if not (path / ".git").exists():
        return ""
    try:
        cp = subprocess.run(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if cp.returncode == 0:
            return cp.stdout.strip()
    except Exception:
        pass
    return ""


def git_head(path: Path) -> str:
    if not (path / ".git").exists():
        return ""
    try:
        cp = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if cp.returncode == 0:
            return cp.stdout.strip()
    except Exception:
        pass
    return ""


def rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def find_readmes(repo: Path) -> list[Path]:
    names = ["README.md", "readme.md", "README.rst", "README.txt", "Readme.md"]
    found = []
    for name in names:
        p = repo / name
        if p.exists() and p.is_file():
            found.append(p)
    if found:
        return found
    # Shallow fallback.
    for p in repo.glob("*README*"):
        if p.is_file():
            found.append(p)
    return found[:3]


def summarize_readme(text: str) -> dict:
    lines = text.splitlines()
    headings = []
    for line in lines:
        s = line.strip()
        if s.startswith("#"):
            headings.append(re.sub(r"^#+\s*", "", s)[:100])
        elif re.match(r"^[A-Z][A-Za-z0-9 _/-]{2,80}$", s) and len(headings) < 6:
            # Some rst/plain READMEs use bare headings.
            headings.append(s[:100])
        if len(headings) >= 10:
            break
    run_hints = [norm_text(x)[:160] for x in RUN_HINT_RE.findall(text)]
    datasets = sorted(set(m.group(0) for m in DATASET_HINT_RE.finditer(text)))
    return {
        "headings": headings[:10],
        "run_hints": run_hints[:8],
        "dataset_hints": datasets[:12],
        "excerpt": norm_text(text[:2500])[:1000],
    }


def scan_repo(repo_path: str) -> dict:
    repo = (ROOT / repo_path).resolve() if not Path(repo_path).is_absolute() else Path(repo_path)
    summary = {
        "target": repo_path,
        "exists": repo.exists(),
        "remote": "",
        "head": "",
        "own_git": False,
        "top_level": [],
        "file_count_scanned": 0,
        "dir_count_scanned": 0,
        "language_counts": {},
        "readme_files": [],
        "readme": {"headings": [], "run_hints": [], "dataset_hints": [], "excerpt": ""},
        "key_files": {},
        "dataset_hints": [],
        "notes": [],
    }
    if not repo.exists() or not repo.is_dir():
        summary["notes"].append("本地目录不存在或不是目录。")
        return summary
    summary["own_git"] = (repo / ".git").exists()
    summary["remote"] = git_remote(repo)
    summary["head"] = git_head(repo)
    try:
        summary["top_level"] = sorted(
            [p.name + ("/" if p.is_dir() else "") for p in repo.iterdir() if p.name != ".git"]
        )[:40]
    except Exception:
        pass

    readmes = find_readmes(repo)
    readme_text = ""
    for p in readmes:
        text = safe_read(p, 50000)
        if text:
            summary["readme_files"].append(rel(p, repo))
            readme_text += "\n\n" + text
    summary["readme"] = summarize_readme(readme_text)

    language_counter = Counter()
    key_files: dict[str, list[str]] = defaultdict(list)
    dataset_hints = set(summary["readme"]["dataset_hints"])
    file_count = 0
    dir_count = 0

    for current, dirs, files in os.walk(repo):
        cur = Path(current)
        depth = len(cur.relative_to(repo).parts) if cur != repo else 0
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_DIRS and not d.startswith(".") and depth < 4
        ]
        dir_count += len(dirs)
        for filename in files:
            if file_count >= 2500:
                summary["notes"].append("仓库文件较多，仅扫描前2500个非依赖文件。")
                break
            p = cur / filename
            if any(part in SKIP_DIRS for part in p.relative_to(repo).parts[:-1]):
                continue
            rp = rel(p, repo)
            suffix = p.suffix.lower()
            if suffix in LANG_EXTS:
                language_counter[LANG_EXTS[suffix]] += 1
            for label, pattern in ENTRY_PATTERNS:
                if pattern.search(rp):
                    key_files[label].append(rp)
            if suffix in TEXT_EXTS and p.stat().st_size <= 300000:
                # Scan small text files for dataset names, but do not read everything deeply.
                text = safe_read(p, 8000)
                for m in DATASET_HINT_RE.finditer(text):
                    dataset_hints.add(m.group(0))
            file_count += 1
        if file_count >= 2500:
            break

    summary["file_count_scanned"] = file_count
    summary["dir_count_scanned"] = dir_count
    summary["language_counts"] = dict(language_counter.most_common())
    summary["key_files"] = {k: v[:12] for k, v in sorted(key_files.items())}
    summary["dataset_hints"] = sorted(dataset_hints)[:20]
    if not summary["readme_files"]:
        summary["notes"].append("未发现 README 文件。")
    if not summary["key_files"]:
        summary["notes"].append("未从文件名中识别到明显训练/评估/数据处理入口。")
    return summary


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def group_code_records():
    rows = load_json(CODE_INDEX)
    by_num: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        num = row.get("num")
        if isinstance(num, int):
            by_num[num].append(row)
    return by_num, rows


def match_keywords(paper: dict, repo_summary: dict) -> list[str]:
    terms = []
    terms.extend(paper.get("method_keywords") or [])
    title = paper.get("title") or ""
    # Add acronym-like title prefix.
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9_-]{2,30})[:：]", title)
    if m:
        terms.append(m.group(1))
    blob = " ".join([
        repo_summary.get("target", ""),
        repo_summary.get("remote", ""),
        " ".join(repo_summary.get("top_level", [])),
        repo_summary.get("readme", {}).get("excerpt", ""),
        " ".join(repo_summary.get("readme", {}).get("headings", [])),
        " ".join(sum((v for v in repo_summary.get("key_files", {}).values()), [])),
    ]).lower()
    found = []
    for term in terms:
        t = str(term).strip()
        if len(t) < 3:
            continue
        if t.lower() in blob and t not in found:
            found.append(t)
    return found[:12]


def format_list(items: list[str], empty: str = "无") -> str:
    return "、".join(items) if items else empty


def merge_rows_by_target(rows: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for row in rows:
        target = row.get("target") or row.get("url") or row.get("repo") or ""
        item = grouped.setdefault(target, dict(row))
        repos = item.setdefault("_all_repos", [])
        urls = item.setdefault("_all_urls", [])
        repo_name = row.get("repo") or row.get("repo_full")
        url = row.get("url")
        if repo_name and repo_name not in repos:
            repos.append(repo_name)
        if url and url not in urls:
            urls.append(url)
        # Prefer the second-round verified URL/name when present, otherwise keep first.
        if row.get("source_pass") == "github_api_readme_second_round":
            for key in ["repo", "repo_full", "url", "source_pass"]:
                if row.get(key):
                    item[key] = row[key]
    return list(grouped.values())


def code_section_for_paper(paper: dict, code_rows: list[dict], repo_summaries: dict[str, dict]) -> str:
    lines = ["## 9. 代码对照分析", ""]
    downloaded = merge_rows_by_target([r for r in code_rows if r.get("status") == "downloaded"])
    partial = [r for r in code_rows if r.get("status") == "partial"]
    failed = [r for r in code_rows if r.get("status") in {"failed", "timeout"}]

    if not code_rows:
        lines += [
            "当前代码索引中未发现该论文对应的可用开源仓库。",
            "",
            "- **对照结论**：正文解析已基于 PDF 全文与章节线索完成；本节暂无源码可进一步核对方法实现、数据处理和实验脚本。",
            "- **后续建议**：若需要复现，可优先检索论文题名、方法缩写、第一作者主页和 GitHub/Zenodo/OSF。",
            "",
        ]
        return "\n".join(lines)

    if downloaded:
        lines.append("代码索引中存在本地已下载仓库，可与论文方法进行对照。")
        lines.append("")
        for idx, row in enumerate(downloaded, 1):
            target = row.get("target") or ""
            summary = repo_summaries.get(target) or scan_repo(target)
            matched = match_keywords(paper, summary)
            lang = ", ".join("%s:%s" % (k, v) for k, v in list(summary.get("language_counts", {}).items())[:6]) or "未识别"
            top_level = format_list(summary.get("top_level", [])[:12])
            readme = summary.get("readme", {})
            key_files = summary.get("key_files", {})
            lines += [
                "### 9.%d 仓库：%s" % (
                    idx,
                    " / ".join(row.get("_all_repos") or [row.get("repo") or row.get("repo_full") or row.get("url")])
                ),
                "",
                "- **本地目录**：`%s`" % target,
                "- **代码索引地址**：%s" % ("；".join(row.get("_all_urls") or [row.get("url") or "无"])),
                "- **本地 Git remote / HEAD**：%s / %s" % (
                    summary.get("remote") or "未检测到独立 .git（按源码快照分析）",
                    summary.get("head") or "-"
                ),
                "- **主要语言/文件类型**：%s" % lang,
                "- **顶层结构**：%s" % top_level,
                "- **README 文件**：%s" % format_list(summary.get("readme_files", [])),
                "- **README 标题线索**：%s" % format_list(readme.get("headings", [])[:8]),
                "- **数据集线索**：%s" % format_list(summary.get("dataset_hints", []) or readme.get("dataset_hints", [])),
                "- **论文关键词在代码中命中**：%s" % format_list(matched, "未明显命中，需人工打开代码进一步确认。"),
                "",
                "**关键入口文件对照**：",
                "",
            ]
            if key_files:
                for label in ["依赖环境", "数据处理入口", "模型定义", "训练入口", "评估/测试入口", "推理/演示入口", "配置文件"]:
                    values = key_files.get(label, [])
                    if values:
                        lines.append("- **%s**：%s" % (label, "；".join("`%s`" % v for v in values[:8])))
            else:
                lines.append("- 未通过文件名自动识别出训练、评估或数据处理入口。")
            lines += [
                "",
                "**README 运行线索**：",
                "",
            ]
            if readme.get("run_hints"):
                for hint in readme["run_hints"][:6]:
                    lines.append("- `%s`" % hint.replace("`", ""))
            else:
                lines.append("- README 中未稳定抽取到可直接执行的命令。")
            lines += [
                "",
                "**论文-代码对应关系判断**：",
                "",
                "- 若仓库中存在数据处理入口，应优先对应论文中的“数据预处理/特征提取”部分。",
                "- 若仓库中存在模型定义文件，应对应论文中的“模型结构/网络模块/损失函数”部分。",
                "- 若仓库中存在训练与评估脚本，应对应论文中的“实验设置/训练参数/评价指标”部分。",
                "- 复现时建议先记录环境依赖、数据路径、默认配置和输出指标，再与论文表格逐项比对。",
                "",
            ]
            if summary.get("notes"):
                lines.append("**自动扫描备注**：%s" % "；".join(summary["notes"]))
                lines.append("")
    if partial:
        lines += [
            "### 部分下载候选",
            "",
        ]
        for row in partial:
            lines.append("- `%s`：%s，状态为部分下载，建议后续人工检查目录完整性。" % (row.get("target"), row.get("url")))
        lines.append("")
    if failed:
        lines += [
            "### 未成功下载候选",
            "",
        ]
        for row in failed[:8]:
            lines.append("- %s：%s（状态：%s）" % (row.get("repo"), row.get("url"), row.get("status")))
        lines.append("")
    return "\n".join(lines)


def replace_or_insert_code_section(doc_text: str, section: str) -> str:
    # The generated docs currently have section 9 as reading advice. Move that to section 10.
    doc_text = re.sub(r"## 9\. 建议阅读方式", "## 10. 建议阅读方式", doc_text)
    pattern = r"\n## 9\. 代码对照分析\n.*?(?=\n## 10\. 建议阅读方式|\Z)"
    if re.search(pattern, doc_text, flags=re.S):
        return re.sub(pattern, lambda _m: "\n" + section.strip() + "\n", doc_text, flags=re.S)
    marker = "\n## 10. 建议阅读方式"
    if marker in doc_text:
        return doc_text.replace(marker, "\n" + section.strip() + "\n\n" + marker, 1)
    # Fallback before return link.
    marker = "\n[返回索引]"
    if marker in doc_text:
        return doc_text.replace(marker, "\n" + section.strip() + "\n" + marker, 1)
    return doc_text.rstrip() + "\n\n" + section.strip() + "\n"


def update_docs(papers: list[dict], by_num: dict[int, list[dict]], repo_summaries: dict[str, dict]) -> None:
    manifest = load_json(MANIFEST_JSON)
    files = manifest["files"]
    for paper in papers:
        num = paper["num"]
        filename = files.get(str(num))
        if not filename:
            continue
        doc_path = DETAIL_DIR / filename
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8", errors="ignore")
        section = code_section_for_paper(paper, by_num.get(num, []), repo_summaries)
        doc_path.write_text(replace_or_insert_code_section(text, section), encoding="utf-8")


def write_summary_reports(papers: list[dict], by_num: dict[int, list[dict]], repo_summaries: dict[str, dict]) -> None:
    rows = []
    for paper in papers:
        for row in by_num.get(paper["num"], []):
            target = row.get("target") or ""
            summary = repo_summaries.get(target, {})
            rows.append({
                "num": paper["num"],
                "title": paper.get("title", ""),
                "category": paper.get("category", ""),
                "relevance": paper.get("relevance_tier", ""),
                "repo": row.get("repo") or row.get("repo_full") or "",
                "url": row.get("url") or "",
                "status": row.get("status") or "",
                "target": target,
                "languages": ", ".join("%s:%s" % (k, v) for k, v in list(summary.get("language_counts", {}).items())[:5]),
                "datasets": "、".join(summary.get("dataset_hints", [])[:8]),
                "readme": "、".join(summary.get("readme_files", [])),
                "train_files": "；".join(summary.get("key_files", {}).get("训练入口", [])[:6]),
                "model_files": "；".join(summary.get("key_files", {}).get("模型定义", [])[:6]),
                "data_files": "；".join(summary.get("key_files", {}).get("数据处理入口", [])[:6]),
            })
    with CODE_SUMMARY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "num", "title", "category", "relevance", "repo", "url", "status",
            "target", "languages", "datasets", "readme", "train_files",
            "model_files", "data_files",
        ])
        writer.writeheader()
        writer.writerows(rows)

    downloaded = [r for r in rows if r["status"] == "downloaded"]
    lines = [
        "# 07 代码对照总表",
        "",
        "生成时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "本表汇总已发现代码仓库与论文解析之间的对应关系。每篇论文的详细代码对照已经写入 `逐篇中文解析/` 下对应文档的“代码对照分析”章节。",
        "",
        "## 汇总",
        "",
        "- 代码候选记录：%d" % len(rows),
        "- 已下载仓库记录：%d" % len(downloaded),
        "- 覆盖有已下载代码的论文：%d 篇" % len({r["num"] for r in downloaded}),
        "",
        "## 已下载代码仓库",
        "",
        "| 编号 | 论文 | 仓库 | 本地目录 | 语言 | 数据集线索 | 训练入口 | 模型文件 |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for r in downloaded:
        lines.append("| %s | %s | %s | `%s` | %s | %s | %s | %s |" % (
            r["num"],
            (r["title"] or "").replace("|", "\\|"),
            (r["repo"] or "").replace("|", "\\|"),
            (r["target"] or "").replace("|", "\\|"),
            (r["languages"] or "未识别").replace("|", "\\|"),
            (r["datasets"] or "无").replace("|", "\\|"),
            (r["train_files"] or "无").replace("|", "\\|"),
            (r["model_files"] or "无").replace("|", "\\|"),
        ))
    CODE_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    papers = load_json(PAPERS_JSON)
    by_num, all_code_rows = group_code_records()

    targets = sorted({r.get("target") for r in all_code_rows if r.get("status") in {"downloaded", "partial"} and r.get("target")})
    repo_summaries = {}
    for idx, target in enumerate(targets, 1):
        repo_summaries[target] = scan_repo(target)
        if idx % 25 == 0 or idx == len(targets):
            print("scanned %d/%d repositories" % (idx, len(targets)))

    CODE_SUMMARY_JSON.write_text(json.dumps(repo_summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    update_docs(papers, by_num, repo_summaries)
    write_summary_reports(papers, by_num, repo_summaries)
    print(json.dumps({
        "papers": len(papers),
        "code_records": len(all_code_rows),
        "scanned_repositories": len(repo_summaries),
        "summary_json": str(CODE_SUMMARY_JSON),
        "summary_md": str(CODE_SUMMARY_MD),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
