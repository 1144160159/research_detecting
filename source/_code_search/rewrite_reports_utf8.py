# -*- coding: utf-8 -*-
import json
import time
from collections import Counter
from pathlib import Path


BASE = Path("source/_code_search")
SOURCE = Path("source")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path):
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip()
    ]


def md_escape(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def count_jsonl(path):
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())


def count_api_groups(path):
    total = 0
    for row in load_jsonl(path):
        if row.get("kind") == "group":
            total += 1
    return total


def brave_status(path):
    status = Counter()
    for row in load_jsonl(path):
        status[str(row.get("status"))] += 1
    return dict(status)


def table_downloaded(rows):
    return "\n".join(
        "| {num} | {repo} | `{target}` | {url} | {title} |".format(
            num=r.get("num", ""),
            repo=md_escape(r.get("repo") or r.get("repo_full")),
            target=md_escape(r.get("target")),
            url=md_escape(r.get("url")),
            title=md_escape(r.get("title")),
        )
        for r in rows
    )


def table_second_round(rows):
    return "\n".join(
        "| {num} | {repo} | `{target}` | {status} | {title} |".format(
            num=r.get("num", ""),
            repo=md_escape(r.get("repo_full")),
            target=md_escape(r.get("target")),
            status=md_escape(r.get("status")),
            title=md_escape(r.get("title")),
        )
        for r in rows
    )


def table_partial(rows):
    if not rows:
        return "| - | - | - | - | - |"
    return "\n".join(
        "| {num} | {repo} | `{target}` | {url} | {title} |".format(
            num=r.get("num", ""),
            repo=md_escape(r.get("repo")),
            target=md_escape(r.get("target")),
            url=md_escape(r.get("url")),
            title=md_escape(r.get("title")),
        )
        for r in rows
    )


def table_failed(rows):
    if not rows:
        return "| - | - | - | - |"
    return "\n".join(
        "| {num} | {repo} | {url} | {title} |".format(
            num=r.get("num", ""),
            repo=md_escape(r.get("repo")),
            url=md_escape(r.get("url")),
            title=md_escape(r.get("title")),
        )
        for r in rows[:80]
    )


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    index = load_json(BASE / "code_repositories_index.json")
    inventory_rows = (BASE / "source_local_repositories_inventory.tsv").read_text(
        encoding="utf-8", errors="ignore"
    ).splitlines()
    inventory_count = max(0, len(inventory_rows) - 1)
    git_count = sum(1 for line in inventory_rows[1:] if "\tTrue\t" in line)

    downloaded = [r for r in index if r.get("status") == "downloaded"]
    partial = [r for r in index if r.get("status") == "partial"]
    failed = [r for r in index if r.get("status") in {"failed", "timeout"}]
    downloaded_papers = {r.get("num") for r in downloaded if r.get("num") is not None}
    partial_papers = {r.get("num") for r in partial if r.get("num") is not None}
    status_counts = Counter(r.get("status") for r in index)

    pdf_count = len(list(Path("paper").glob("*.pdf")))
    paper_count = 850
    method_final = load_jsonl(BASE / "github_method_search_final_download_candidates.jsonl")
    method_results = load_jsonl(BASE / "download_github_method_results.jsonl")
    method_status = Counter(r.get("status") for r in method_results)

    report = f"""# 850篇论文开源代码检索下载报告

生成时间: {now}

## 处理范围

- 本地 `paper/` PDF 数量: {pdf_count}
- `文献.md` 条目数量: {paper_count}
- 第一轮已从 PDF 前 5 页抽取 GitHub/GitLab/Bitbucket/Zenodo/OSF 等公开资源链接，并下载高置信 GitHub 仓库。
- 第二轮对未下载论文重新生成方法名/系统名检索词，使用 GitHub Search API、README 原文验证和题名/DOI 重合度过滤。
- Browser 插件已按要求尝试连接，但当前环境没有可用 `iab` 实例，因此本轮采用命令行联网检索与 `git clone --depth 1` 下载。

## 汇总统计

- 代码候选仓库记录: {len(index)}
- 本地可用仓库记录: {len(downloaded)}
- 覆盖论文数: {len(downloaded_papers)} 篇
- 部分下载/需人工复核: {len(partial)} 条，涉及 {len(partial_papers)} 篇
- 失败/不可访问候选: {len(failed)} 条
- `source/` 子目录: {inventory_count} 个，其中 Git 仓库 {git_count} 个

状态分布: {", ".join(f"{k}={v}" for k, v in status_counts.items())}

## 第二轮检索结果

- 待复检队列: `web_search_queue.json` 中 751 篇未确认/未下载论文。
- Brave Web Search 批量检索受限: {brave_status(BASE / "web_search_brave_candidates.jsonl")}，主要为 429 限流，因此未作为最终依据。
- 精炼 GitHub 方法名队列: `github_method_search_queue_refined.json`，253 篇、263 个查询。
- GitHub API 组合检索: {count_api_groups(BASE / "github_method_search_api_candidates.jsonl")} 组查询，原始高分候选 {count_jsonl(BASE / "github_method_search_api_accepted.jsonl")} 条。
- README 验证: 检查 {count_jsonl(BASE / "github_method_search_readme_verified_all.jsonl")} 条精确/近似命中候选，合并严格候选 {count_jsonl(BASE / "github_method_search_api_strict_accepted.jsonl")} 条。
- 最终二轮下载候选: {len(method_final)} 条，覆盖 {len({r.get("num") for r in method_final})} 篇；本轮下载结果: {dict(method_status)}。

二轮最终候选如下:

| 编号 | GitHub | 本地目录 | 状态 | 论文题名 |
|---:|---|---|---|---|
{table_second_round(method_results)}

## 本地可用仓库清单

| 编号 | 仓库 | 本地目录 | URL | 论文题名 |
|---:|---|---|---|---|
{table_downloaded(downloaded)}

## 部分下载/需复核

| 编号 | 仓库 | 本地目录 | URL | 论文题名 |
|---:|---|---|---|---|
{table_partial(partial)}

## 失败或不可访问候选

| 编号 | 仓库 | URL | 论文题名 |
|---:|---|---|---|
{table_failed(failed)}

## 输出文件

- `source/_code_search/code_repositories_index.json`
- `source/_code_search/code_repositories_index.tsv`
- `source/_code_search/source_local_repositories_inventory.tsv`
- `source/_code_search/github_method_search_final_download_candidates.tsv`
- `source/_code_search/download_github_method_results.jsonl`
"""

    (SOURCE / "850篇论文开源代码检索下载报告.md").write_text(report, encoding="utf-8")

    english = f"""# Open Source Code Search Report

Generated: {now}

Scope: {paper_count} bibliography entries / {pdf_count} PDFs.

Summary:

- Repository candidate records: {len(index)}
- Locally available repository records: {len(downloaded)}
- Papers covered by locally available code: {len(downloaded_papers)}
- Partial records: {len(partial)}
- Failed or inaccessible candidates: {len(failed)}
- `source/` directories: {inventory_count}, Git repositories: {git_count}

Second round:

- Refined GitHub method-name queue: 253 papers / 263 queries.
- GitHub API search groups: {count_api_groups(BASE / "github_method_search_api_candidates.jsonl")}; raw accepted candidates before strict filtering: {count_jsonl(BASE / "github_method_search_api_accepted.jsonl")}.
- README verification candidates checked: {count_jsonl(BASE / "github_method_search_readme_verified_all.jsonl")}; final second-round download candidates: {len(method_final)}.
- Second-round download statuses: {dict(method_status)}.
- Browser plugin was attempted, but no in-app `iab` browser instance was available, so command-line web/API search was used.

Main index files:

- `source/_code_search/code_repositories_index.json`
- `source/_code_search/code_repositories_index.tsv`
- `source/_code_search/source_local_repositories_inventory.tsv`
"""
    (SOURCE / "OPEN_SOURCE_CODE_REPORT.md").write_text(english, encoding="utf-8")

    summary = f"""# 开源代码汇总报告

生成时间: {now}

- 论文总数: {paper_count}
- 本地可用开源代码仓库记录: {len(downloaded)}
- 覆盖论文数: {len(downloaded_papers)}
- `source/` 子目录: {inventory_count}，Git 仓库: {git_count}
- 第二轮新增确认候选: {len(method_final)} 条，覆盖 {len({r.get("num") for r in method_final})} 篇。

详情见: `source/850篇论文开源代码检索下载报告.md`。
"""
    (SOURCE / "开源代码汇总报告.md").write_text(summary, encoding="utf-8")

    print(
        json.dumps(
            {
                "records": len(index),
                "downloaded": len(downloaded),
                "downloaded_papers": len(downloaded_papers),
                "partial": len(partial),
                "failed": len(failed),
                "source_dirs": inventory_count,
                "git_dirs": git_count,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
