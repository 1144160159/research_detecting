from __future__ import annotations

import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from finalize_and_verify_commented_patent import (
    M,
    QW,
    patch_docx,
    red_visible_text,
    sha256,
    visible_text,
)


def verify(source: Path, target: Path) -> dict:
    with zipfile.ZipFile(source) as source_zip, zipfile.ZipFile(target) as target_zip:
        source_doc = source_zip.read("word/document.xml")
        target_doc = target_zip.read("word/document.xml")
        comments_xml = target_zip.read("word/comments.xml")
        comments_root = ET.fromstring(comments_xml)
        comments = list(comments_root.iter(QW("comment")))
        authors = Counter(c.get(QW("author"), "") for c in comments)
        initials = Counter(c.get(QW("initials"), "") for c in comments)
        comment_texts = [visible_text(ET.tostring(c, encoding="utf-8")) for c in comments]

        expected_prefixes = (
            [f"[标红问题{i}/35" for i in range(1, 36)]
            + [f"[补充问题{i}/6" for i in range(1, 7)]
            + [f"[遗漏补充{i}/48" for i in range(1, 49)]
        )
        prefix_counts = {
            prefix: sum(prefix in text for text in comment_texts) for prefix in expected_prefixes
        }

        source_media = {
            name: sha256(source_zip.read(name))
            for name in source_zip.namelist()
            if name.startswith("word/media/")
        }
        target_media = {
            name: sha256(target_zip.read(name))
            for name in target_zip.namelist()
            if name.startswith("word/media/")
        }

        result = {
            "zip_test": target_zip.testzip(),
            "comment_count": len(comments),
            "authors": dict(authors),
            "initials": dict(initials),
            "missing_comment_prefixes": [k for k, v in prefix_counts.items() if v == 0],
            "duplicated_comment_prefixes": [k for k, v in prefix_counts.items() if v > 1],
            "math_object_count_in_comments": comments_xml.count(b"<m:oMath"),
            "math_placeholder_count": comments_xml.count(b"[[MATH:"),
            "body_visible_text_equal": visible_text(source_doc) == visible_text(target_doc),
            "source_visible_text_length": len(visible_text(source_doc)),
            "target_visible_text_length": len(visible_text(target_doc)),
            "red_visible_text_equal": red_visible_text(source_doc) == red_visible_text(target_doc),
            "source_red_visible_text_length": len(red_visible_text(source_doc)),
            "target_red_visible_text_length": len(red_visible_text(target_doc)),
            "media_hashes_equal": source_media == target_media,
            "source_media_hashes": source_media,
            "target_media_hashes": target_media,
        }
        result["passed"] = all(
            [
                result["zip_test"] is None,
                result["comment_count"] == 89,
                result["authors"] == {"王文同": 89},
                result["initials"] == {"WWT": 89},
                not result["missing_comment_prefixes"],
                not result["duplicated_comment_prefixes"],
                result["math_object_count_in_comments"] > 121,
                result["math_placeholder_count"] == 0,
                result["body_visible_text_equal"],
                result["red_visible_text_equal"],
                result["media_hashes_equal"],
            ]
        )
        return result


def main() -> int:
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    report_path = Path(sys.argv[3])
    patch_docx(source, target)
    report = verify(source, target)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
