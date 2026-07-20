"""Rank component candidates from the local enriched-paper JSONL corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


BUCKETS = {
    "高速捕获与测量": {
        "dpdk": 14, "af_xdp": 14, "af xdp": 14, "ebpf": 12, "xdp": 10,
        "p4": 9, "smartnic": 10, "programmable switch": 8, "packet capture": 8,
        "high-speed": 6, "high speed": 6, "line rate": 7, "zero-copy": 7,
        "network measurement": 5, "traffic measurement": 5, "sketch": 4,
    },
    "协议解析与表征": {
        "deep packet inspection": 10, "protocol identification": 10,
        "protocol inference": 9, "traffic representation": 6, "packet-level": 5,
        "packet level": 5, "byte-level": 5, "byte level": 5, "payload": 3,
        "quic": 4, "tls": 3, "transformer": 2,
    },
    "加密流量识别": {
        "encrypted traffic classification": 14, "encrypted traffic": 8,
        "website fingerprinting": 10, "application identification": 9,
        "early traffic classification": 10, "traffic classification": 6,
        "tls fingerprint": 9, "quic": 5, "burst": 4, "packet sequence": 5,
        "multimodal": 4, "self-supervised": 3,
    },
    "预算调度与降级": {
        "adaptive budget": 14, "budget": 8, "early exit": 12,
        "dynamic inference": 10, "load shedding": 11, "resource allocation": 9,
        "task offloading": 9, "adaptive monitoring": 9, "feature selection": 6,
        "packet sampling": 7, "sampling": 3, "online learning": 5,
        "reinforcement learning": 4, "resource-aware": 8,
    },
}


def searchable_text(paper):
    fields = [paper.get("title", ""), paper.get("abstract", ""), paper.get("keywords", ""),
              paper.get("category", ""), paper.get("relevance_reason", "")]
    fields.extend(paper.get("secondary_categories", []))
    fields.extend(paper.get("innovations", []))
    fields.extend(paper.get("science_problems", []))
    fields.extend(paper.get("method_keywords", []))
    return " ".join(str(value) for value in fields).lower()


def rank(corpus_path, limit):
    ranked = {bucket: [] for bucket in BUCKETS}
    with corpus_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            paper = json.loads(line)
            text = searchable_text(paper)
            for bucket, terms in BUCKETS.items():
                hits = [(term, weight) for term, weight in terms.items() if term in text]
                if not hits:
                    continue
                score = sum(weight for _, weight in hits)
                if paper.get("code_status") not in (None, "", "未发现"):
                    score += 4
                score += min(3, int(paper.get("relevance_score") or 0) // 2)
                ranked[bucket].append((score, hits, paper))
    for bucket in ranked:
        ranked[bucket].sort(key=lambda item: (-item[0], -int(item[2].get("year") or 0), item[2].get("title", "")))
        ranked[bucket] = ranked[bucket][:limit]
    return ranked


def emit_markdown(ranked, corpus_path):
    print("# 858篇论文候选组件自动初筛")
    print()
    print("来源：`{}`。该清单是关键词与代码状态驱动的初筛，必须结合全文/代码复核后才能进入实验矩阵。".format(corpus_path))
    for bucket, entries in ranked.items():
        print("\n## {}\n".format(bucket))
        print("| 分数 | 年份 | 论文 | 命中机制 | 代码状态 | DOI/代码 |")
        print("|---:|---:|---|---|---|---|")
        for score, hits, paper in entries:
            links = paper.get("code_repositories") or paper.get("doi") or paper.get("pdf") or "-"
            terms = "、".join(term for term, _ in hits)
            title = str(paper.get("title", "")).replace("|", "/")
            print("| {} | {} | {} | {} | {} | {} |".format(
                score, paper.get("year", ""), title, terms,
                paper.get("code_status", ""), str(links).replace("|", "/")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    emit_markdown(rank(args.corpus, args.limit), args.corpus)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
