from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
QW = lambda name: f"{{{W}}}{name}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def visible_text(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    parts = []
    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local in {"t", "delText", "instrText"} and node.text:
            parts.append(node.text)
        elif node.tag == QW("tab"):
            parts.append("\t")
        elif node.tag in {QW("br"), QW("cr")}:
            parts.append("\n")
    return "".join(parts)


def red_visible_text(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    parts = []
    for run in root.iter(QW("r")):
        color = run.find("./w:rPr/w:color", {"w": W})
        if color is None or color.get(QW("val"), "").upper() != "EE0000":
            continue
        for node in run.iter():
            local = node.tag.rsplit("}", 1)[-1]
            if local in {"t", "delText"} and node.text:
                parts.append(node.text)
    return "".join(parts)


def patch_docx(source: Path, target: Path) -> None:
    temp = target.with_suffix(".tmp.docx")
    with zipfile.ZipFile(source) as source_zip, zipfile.ZipFile(target) as target_zip:
        source_media = {
            name: source_zip.read(name)
            for name in source_zip.namelist()
            if name.startswith("word/media/")
        }
        comments = target_zip.read("word/comments.xml").decode("utf-8")
        comments = re.sub(r'w:author="[^"]*"', 'w:author="王文同"', comments)
        comments = re.sub(r'w:initials="[^"]*"', 'w:initials="WWT"', comments)

        with zipfile.ZipFile(temp, "w") as output_zip:
            for info in target_zip.infolist():
                data = target_zip.read(info.filename)
                if info.filename == "word/comments.xml":
                    data = comments.encode("utf-8")
                elif info.filename in source_media:
                    data = source_media[info.filename]
                output_zip.writestr(info, data)
    shutil.move(temp, target)


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

        expected_prefixes = [f"[标红问题{i}/35" for i in range(1, 36)] + [
            f"[补充问题{i}/6" for i in range(1, 7)
        ]
        missing_prefixes = [
            prefix for prefix in expected_prefixes if not any(prefix in text for text in comment_texts)
        ]
        duplicated_prefixes = [
            prefix
            for prefix in expected_prefixes
            if sum(prefix in text for text in comment_texts) != 1
        ]

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

        source_root = ET.fromstring(source_doc)
        target_root = ET.fromstring(target_doc)
        source_red = sum(
            1
            for color in source_root.iter(QW("color"))
            if color.get(QW("val"), "").upper() == "EE0000"
        )
        target_red = sum(
            1
            for color in target_root.iter(QW("color"))
            if color.get(QW("val"), "").upper() == "EE0000"
        )

        result = {
            "zip_test": target_zip.testzip(),
            "comment_count": len(comments),
            "authors": dict(authors),
            "initials": dict(initials),
            "missing_comment_prefixes": missing_prefixes,
            "duplicated_comment_prefixes": duplicated_prefixes,
            "math_object_count_in_comments": comments_xml.count(b"<m:oMath"),
            "math_placeholder_count": comments_xml.count(b"[[MATH:"),
            "body_visible_text_equal": visible_text(source_doc) == visible_text(target_doc),
            "source_visible_text_length": len(visible_text(source_doc)),
            "target_visible_text_length": len(visible_text(target_doc)),
            "source_red_run_count": source_red,
            "target_red_run_count": target_red,
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
                result["comment_count"] == 41,
                result["authors"] == {"王文同": 41},
                result["initials"] == {"WWT": 41},
                not result["missing_comment_prefixes"],
                not result["duplicated_comment_prefixes"],
                result["math_object_count_in_comments"] > 0,
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
