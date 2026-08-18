from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "03_全文抽取缓存"
OUTPUT = TEXT_DIR / "_40篇证据定位摘要.md"


def block(text: str, pattern: str, length: int = 3500) -> str:
    match = re.search(pattern, text, flags=re.I)
    if not match:
        return "[未自动定位，需人工查页]"
    start = max(0, match.start() - 100)
    return text[start : start + length].strip()


def metric_lines(text: str) -> str:
    keep = []
    for number, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        has_metric = any(k in low for k in ("auroc", "oscr", "fpr95", "fpr@", "macro-f1", "accuracy", "ece", "brier"))
        has_number = bool(re.search(r"\d+(?:\.\d+)?\s*%", line))
        if has_metric and has_number:
            keep.append(f"L{number}: {line.strip()}")
        if len(keep) >= 18:
            break
    return "\n".join(keep) if keep else "[未自动定位带数值的指标行]"


def main() -> None:
    chunks = ["# 40篇核心论文证据定位摘要", "", "本文件为精读辅助定位，不是中文精读结论。", ""]
    for path in sorted(TEXT_DIR.glob("[0-9][0-9]_*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        chunks.extend([
            f"## {path.stem}",
            "",
            "### Abstract定位",
            "```text",
            block(text, r"\bAbstract\b"),
            "```",
            "",
            "### 结论/局限定位",
            "```text",
            block(text, r"\b(?:Conclusion|Conclusions|Limitations?|Discussion)\b"),
            "```",
            "",
            "### 定量指标定位",
            "```text",
            metric_lines(text),
            "```",
            "",
        ])
    OUTPUT.write_text("\n".join(chunks), encoding="utf-8")
    print(f"papers={len(list(TEXT_DIR.glob('[0-9][0-9]_*.txt')))} output={OUTPUT}")


if __name__ == "__main__":
    main()
