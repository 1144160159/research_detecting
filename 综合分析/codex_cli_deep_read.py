# -*- coding: utf-8 -*-
"""Use Codex CLI to generate GPT-5.5 deep reading notes for each paper.

This script does not synthesize the analysis with local rules. It only builds a
reading packet (metadata, PDF text, and optional local code summary), sends that
packet to `codex exec`, and saves the model's final Markdown response.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "综合分析"
DATA = OUT / "_data"
PAPERS_JSON = DATA / "papers_enriched.json"
CODE_SUMMARY_JSON = DATA / "code_repository_summaries.json"
CODE_INDEX_JSON = ROOT / "source" / "_code_search" / "code_repositories_index.json"
MANIFEST_JSON = DATA / "per_paper_docs_manifest.json"

TEXT_CANDIDATE_DIRS = [
    DATA / "full_text_cache_plain",
    DATA / "full_text_cache",
    DATA / "text_cache",
]

WORK = DATA / "codex_cli_deep_read"
PROMPT_DIR = WORK / "prompts"
RAW_DIR = WORK / "raw_outputs"
LOG_PATH = WORK / "run_log.jsonl"
OUT_DIR = OUT / "GPT5.5逐篇精读"
INDEX_PATH = OUT / "09_GPT5.5逐篇精读索引.md"


REQUIRED_HEADINGS = [
    "## 1. 基本信息",
    "## 2. 中文翻译与核心摘要",
    "## 3. 论文解决的具体问题",
    "## 4. 创新点深度提炼",
    "## 5. 科学问题与研究假设",
    "## 6. 科学方法与技术路线",
    "## 7. 实验设计与实验步骤",
    "## 8. 关键结果、结论与证据",
    "## 9. 局限性与待解决问题",
    "## 10. 与本项目的关系",
    "## 11. 代码对照分析",
    "## 12. 本篇精华",
    "## 13. 建议精读路线",
]


def ensure_dirs() -> None:
    for path in [WORK, PROMPT_DIR, RAW_DIR, OUT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def safe_filename(num: int, title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\n\r\t()\[\]{}]+', "_", title or "untitled")
    name = re.sub(r"\s+", "_", name).strip("._ ")
    if not name:
        name = "paper"
    if len(name) > 92:
        name = name[:92].rstrip("._- ")
    return "%03d_%s.md" % (num, name)


def output_filename_map(papers: list[dict]) -> dict[int, str]:
    manifest = load_json(MANIFEST_JSON, {})
    files = manifest.get("files", {})
    out = {}
    for paper in papers:
        num = int(paper["num"])
        out[num] = files.get(str(num)) or files.get(num) or safe_filename(num, paper.get("title", ""))
    return out


def read_text_packet(num: int, max_chars: int) -> tuple[str, dict]:
    text = ""
    source = ""
    for directory in TEXT_CANDIDATE_DIRS:
        path = directory / ("%03d.txt" % num)
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            source = str(path.relative_to(ROOT))
            break
    text = text.strip()
    original_chars = len(text)
    truncated = False
    if max_chars > 0 and len(text) > max_chars:
        truncated = True
        head = int(max_chars * 0.58)
        tail = max_chars - head
        text = (
            text[:head].rstrip()
            + "\n\n[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]\n\n"
            + text[-tail:].lstrip()
        )
    return text, {
        "text_source": source,
        "original_chars": original_chars,
        "sent_chars": len(text),
        "truncated": truncated,
    }


def load_code_rows() -> dict[int, list[dict]]:
    data = load_json(CODE_INDEX_JSON, [])
    by_num: dict[int, list[dict]] = defaultdict(list)
    if isinstance(data, dict):
        rows = data.get("repositories", []) or data.get("items", []) or []
    else:
        rows = data
    for row in rows:
        try:
            num = int(row.get("num") or row.get("paper_num") or row.get("paper_id"))
        except Exception:
            continue
        by_num[num].append(row)
    return by_num


def code_packet(num: int, code_rows_by_num: dict[int, list[dict]], repo_summaries: dict) -> str:
    rows = code_rows_by_num.get(num, [])
    if not rows:
        return "未发现该论文对应的本地开源代码。"

    parts = []
    for row in rows[:6]:
        target = row.get("target") or ""
        summary = repo_summaries.get(target, {}) if target else {}
        parts.append(
            "\n".join([
                "- 仓库：%s" % (row.get("repo") or row.get("repo_full") or "未知"),
                "  - URL：%s" % (row.get("url") or ""),
                "  - 状态：%s" % (row.get("status") or ""),
                "  - 本地目录：%s" % target,
                "  - 顶层结构：%s" % "、".join(summary.get("top_level", [])[:30]),
                "  - 主要语言：%s" % "、".join("%s:%s" % (k, v) for k, v in list(summary.get("language_counts", {}).items())[:8]),
                "  - README 标题：%s" % "、".join(summary.get("readme", {}).get("headings", [])[:12]),
                "  - README 运行线索：%s" % "；".join(summary.get("readme", {}).get("run_hints", [])[:8]),
                "  - 关键文件：%s" % json.dumps(summary.get("key_files", {}), ensure_ascii=False),
                "  - 数据集线索：%s" % "、".join(summary.get("dataset_hints", [])[:12]),
            ])
        )
    return "\n".join(parts)


def paper_meta_block(paper: dict) -> str:
    secondary = "、".join(paper.get("secondary_categories", [])) if paper.get("secondary_categories") else "无"
    return "\n".join([
        "编号：%03d" % int(paper["num"]),
        "题名：%s" % (paper.get("title") or ""),
        "年份：%s" % (paper.get("year") or "未知"),
        "DOI：%s" % (paper.get("doi") or "无"),
        "来源：%s" % (paper.get("venue") or "未识别"),
        "PDF：%s" % (paper.get("pdf") or ""),
        "已有粗分类：%s" % (paper.get("category") or ""),
        "二级关联：%s" % secondary,
        "相关性：%s，分数 %s" % (paper.get("relevance_tier") or "", paper.get("relevance_score") or ""),
        "已有代码状态：%s；%s" % (paper.get("code_status") or "", paper.get("code_repositories") or "无"),
    ])


def build_prompt(paper: dict, text: str, text_info: dict, code_text: str) -> str:
    num = int(paper["num"])
    title = paper.get("title") or ""
    return f"""你是使用 GPT-5.5 的资深网络安全与异常检测论文精读助手。请真正阅读下面提供的论文正文包和代码包，理解后输出一篇中文深度解析 Markdown。

重要要求：
1. 不要用模板化空话，不要说“程序自动抽取显示”。你需要像研究员读完论文后写读书笔记一样表达。
2. 必须围绕正文内容提炼：具体问题、创新点、科学问题、研究假设、科学方法、实验步骤、关键结论、局限与待解决问题。
3. 如果代码包存在，请把论文方法与代码目录、关键文件、运行线索对应起来，指出哪些源码文件可能对应数据预处理、模型、训练和评估。
4. 如果正文包被截断，必须在“局限性与待解决问题”中说明：本次理解基于提供的正文包，仍需回到 PDF 复核被截断部分。
5. 不要长篇复制英文原文。可以短引极少量关键词，但主体必须是中文理解和分析。
6. 输出必须是完整 Markdown，且必须包含下面 13 个二级标题，标题文字不得改名。
7. “实验设计与实验步骤”要写成可复核流程：数据、预处理、模型/基线、训练、指标、消融/敏感性、结果核查。
8. “本篇精华”要给出 5-8 条高密度要点，能直接服务综述或科研汇报。

必须使用的文档结构：
# [{num:03d}] {title}
## 1. 基本信息
## 2. 中文翻译与核心摘要
## 3. 论文解决的具体问题
## 4. 创新点深度提炼
## 5. 科学问题与研究假设
## 6. 科学方法与技术路线
## 7. 实验设计与实验步骤
## 8. 关键结果、结论与证据
## 9. 局限性与待解决问题
## 10. 与本项目的关系
## 11. 代码对照分析
## 12. 本篇精华
## 13. 建议精读路线

元数据：
{paper_meta_block(paper)}

正文包信息：
- 正文来源：{text_info.get("text_source") or "未找到全文缓存"}
- 原始字符数：{text_info.get("original_chars")}
- 本次发送字符数：{text_info.get("sent_chars")}
- 是否截断：{text_info.get("truncated")}

代码包：
{code_text}

论文正文包开始：
<<<PAPER_TEXT
{text}
PAPER_TEXT
"""


def strip_wrapping_fence(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:markdown|md)?\s*", "", s, flags=re.I)
        s = re.sub(r"\s*```$", "", s)
    return s.strip() + "\n"


def validate_markdown(text: str) -> list[str]:
    missing = [h for h in REQUIRED_HEADINGS if h not in text]
    if not text.lstrip().startswith("# "):
        missing.append("top_level_title")
    if len(text) < 1800:
        missing.append("too_short")
    return missing


def run_codex(prompt: str, output_path: Path, model: str | None, timeout: int) -> tuple[int, str, str, float]:
    cmd = [
        "codex",
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "-C",
        str(ROOT),
        "-o",
        str(output_path),
    ]
    if model:
        cmd.extend(["-m", model])
    cmd.append("-")
    start = time.time()
    cp = subprocess.run(
        cmd,
        input=prompt,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return cp.returncode, cp.stdout, cp.stderr, time.time() - start


def write_index(papers: list[dict], file_map: dict[int, str]) -> None:
    completed = {p.name for p in OUT_DIR.glob("*.md")}
    lines = [
        "# 09 GPT5.5逐篇精读索引",
        "",
        "生成时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "本索引对应 `GPT5.5逐篇精读/` 目录。该目录中的文档由 Codex CLI 逐篇读取论文正文包和代码包后生成，不再使用规则脚本拼接分析内容。",
        "",
        "- 论文总数：%d" % len(papers),
        "- 已完成：%d" % len(completed),
        "- 未完成：%d" % (len(papers) - len(completed)),
        "",
        "| 编号 | 状态 | 论文 | 大类 | 相关性 |",
        "|---:|---|---|---|---|",
    ]
    for paper in sorted(papers, key=lambda x: int(x["num"])):
        num = int(paper["num"])
        filename = file_map[num]
        title = (paper.get("title") or "").replace("|", "\\|")
        if filename in completed:
            link = f"[{title}](GPT5.5逐篇精读/{filename.replace(' ', '%20')})"
            status = "已完成"
        else:
            link = title
            status = "未完成"
        lines.append("| %d | %s | %s | %s | %s |" % (
            num,
            status,
            link,
            (paper.get("category") or "").replace("|", "\\|"),
            paper.get("relevance_tier") or "",
        ))
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_log(record: dict) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def selected_papers(papers: list[dict], args) -> list[dict]:
    out = []
    for paper in sorted(papers, key=lambda x: int(x["num"])):
        num = int(paper["num"])
        if args.start and num < args.start:
            continue
        if args.end and num > args.end:
            continue
        if args.nums and num not in args.nums:
            continue
        out.append(paper)
    if args.limit:
        out = out[: args.limit]
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--num", dest="nums", action="append", type=int)
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--max-chars", type=int, default=140000)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    papers = load_json(PAPERS_JSON, [])
    file_map = output_filename_map(papers)
    repo_summaries = load_json(CODE_SUMMARY_JSON, {})
    code_rows_by_num = load_code_rows()
    todo = selected_papers(papers, args)

    if not todo:
        print("No papers selected.")
        return 0

    for idx, paper in enumerate(todo, 1):
        num = int(paper["num"])
        filename = file_map[num]
        final_path = OUT_DIR / filename
        raw_path = RAW_DIR / filename
        prompt_path = PROMPT_DIR / ("%03d_prompt.md" % num)

        if final_path.exists() and not args.overwrite:
            print("skip %03d existing" % num)
            continue

        text, text_info = read_text_packet(num, args.max_chars)
        code_text = code_packet(num, code_rows_by_num, repo_summaries)
        prompt = build_prompt(paper, text, text_info, code_text)
        prompt_path.write_text(prompt, encoding="utf-8")

        if args.dry_run:
            print("dry-run prepared %03d prompt=%s" % (num, prompt_path))
            continue

        print("codex deep-reading %03d (%d/%d) %s" % (num, idx, len(todo), paper.get("title", "")[:80]))
        try:
            rc, stdout, stderr, elapsed = run_codex(prompt, raw_path, args.model or None, args.timeout)
        except subprocess.TimeoutExpired:
            append_log({"num": num, "status": "timeout", "timeout": args.timeout, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
            print("timeout %03d" % num)
            continue

        record = {
            "num": num,
            "returncode": rc,
            "elapsed_sec": round(elapsed, 2),
            "raw_output": str(raw_path),
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if stdout:
            record["stdout_tail"] = stdout[-1200:]
        if stderr:
            record["stderr_tail"] = stderr[-1200:]

        if rc != 0 or not raw_path.exists():
            record["status"] = "failed"
            append_log(record)
            print("failed %03d rc=%s" % (num, rc))
            continue

        md = strip_wrapping_fence(raw_path.read_text(encoding="utf-8", errors="ignore"))
        missing = validate_markdown(md)
        if missing:
            record["status"] = "invalid"
            record["missing"] = missing
            append_log(record)
            print("invalid %03d missing=%s" % (num, ",".join(missing)))
            continue

        md = md.rstrip() + "\n\n<!-- codex-cli-deep-read: complete -->\n"
        final_path.write_text(md, encoding="utf-8")
        record["status"] = "ok"
        record["final_output"] = str(final_path)
        append_log(record)
        print("ok %03d %.1fs" % (num, elapsed))

    write_index(papers, file_map)
    print(json.dumps({
        "selected": len(todo),
        "completed_docs": len(list(OUT_DIR.glob("*.md"))),
        "output_dir": str(OUT_DIR),
        "index": str(INDEX_PATH),
        "log": str(LOG_PATH),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
