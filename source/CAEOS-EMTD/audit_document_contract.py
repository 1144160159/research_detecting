from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from project_contract import load_delivery_contract


CANONICAL_DOCUMENTS = {
    "root": Path("README.md"),
    "roadmap": Path("00_总览/双交付线研究与工程路线图_2026-07-29.md"),
    "safety": Path(
        "02_实验设计/01_核心协议/"
        "自有算法95_5安全验收协议_2026-07-29.md"
    ),
    "metrics": Path(
        "02_实验设计/01_核心协议/"
        "已知识别与未知拒识联合评价协议_2026-07-29.md"
    ),
    "workspace": Path(
        "04_数据与运行/本地与GPU代码工作区统一记录_2026-07-29.md"
    ),
}
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_arguments() -> argparse.Namespace:
    contract = load_delivery_contract()
    parser = argparse.ArgumentParser(
        description="Audit canonical CAEOS document links and contract tokens."
    )
    parser.add_argument(
        "--docs-root",
        default=contract["source_of_truth"]["local_documents"],
    )
    return parser.parse_args()


def local_markdown_links(path: Path, text: str) -> list[Path]:
    targets: list[Path] = []
    for raw_target in LINK_PATTERN.findall(text):
        target = raw_target.strip().strip("<>")
        if (
            not target
            or target.startswith(("#", "http://", "https://", "mailto:"))
        ):
            continue
        target_without_anchor = target.split("#", 1)[0]
        targets.append((path.parent / target_without_anchor).resolve())
    return targets


def audit_documents(docs_root: Path) -> dict[str, Any]:
    root = docs_root.resolve()
    missing_documents = [
        str(relative)
        for relative in CANONICAL_DOCUMENTS.values()
        if not (root / relative).is_file()
    ]
    broken_links: list[dict[str, str]] = []
    texts: dict[str, str] = {}
    for name, relative in CANONICAL_DOCUMENTS.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        texts[name] = text
        for target in local_markdown_links(path, text):
            if not target.exists():
                broken_links.append(
                    {
                        "document": str(relative),
                        "target": str(target),
                    }
                )

    required_tokens = {
        "root": [
            "工程自有算法95%/5%",
            "论文多模态95%/5%",
            "CAEOS-EMTD/current",
        ],
        "roadmap": [
            "工程实现线",
            "论文研究线",
            "FPR_known@95TPR_unknown",
            "Unknown label Recall",
        ],
        "safety": [
            "caeos_delivery_contract_v1",
            "engineering_safety_95_5",
            "paper_full_open_set_95_5",
        ],
        "metrics": [
            "Known Macro-F1",
            "Unknown AUROC-Out",
            "FPR_known@95TPR_unknown",
            "OSCR",
        ],
        "workspace": [
            "CAEOS-EMTD/releases",
            "CAEOS-EMTD/current",
            "SOURCE_MANIFEST.sha256",
        ],
    }
    missing_tokens = [
        {"document": name, "token": token}
        for name, tokens in required_tokens.items()
        for token in tokens
        if token not in texts.get(name, "")
    ]
    return {
        "schema_version": "caeos_document_contract_audit_v1",
        "docs_root": str(root),
        "canonical_documents": {
            name: str(relative)
            for name, relative in CANONICAL_DOCUMENTS.items()
        },
        "missing_documents": missing_documents,
        "broken_links": broken_links,
        "missing_tokens": missing_tokens,
        "passed": not missing_documents and not broken_links and not missing_tokens,
    }


def main() -> None:
    args = parse_arguments()
    report = audit_documents(Path(args.docs_root))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
