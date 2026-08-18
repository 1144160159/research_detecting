from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
QW = lambda name: f"{{{W}}}{name}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def visible_text(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    parts: list[str] = []
    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local in {"t", "delText", "instrText"} and node.text:
            parts.append(node.text)
        elif node.tag == QW("tab"):
            parts.append("\t")
        elif node.tag in {QW("br"), QW("cr")}:
            parts.append("\n")
    return "".join(parts)


def marked_visible_text(xml_bytes: bytes, mode: str) -> str:
    root = ET.fromstring(xml_bytes)
    parts: list[str] = []
    for run in root.iter(QW("r")):
        properties = run.find(QW("rPr"))
        if properties is None:
            continue
        if mode == "red":
            color = properties.find(QW("color"))
            value = color.get(QW("val"), "").upper() if color is not None else ""
            selected = value in {"EE0000", "FF0000", "RED"}
        elif mode == "yellow":
            highlight = properties.find(QW("highlight"))
            value = (
                highlight.get(QW("val"), "").upper()
                if highlight is not None
                else ""
            )
            selected = value == "YELLOW"
        else:
            raise ValueError(mode)
        if not selected:
            continue
        for node in run.iter():
            if node.tag in {QW("t"), QW("delText")} and node.text:
                parts.append(node.text)
    return "".join(parts)


def patch(
    commented: Path,
    target: Path,
    replacement_image: Path,
) -> None:
    replacement = replacement_image.read_bytes()
    temp = target.with_suffix(".tmp.docx")
    with zipfile.ZipFile(commented) as source_zip, zipfile.ZipFile(temp, "w") as out_zip:
        for info in source_zip.infolist():
            data = source_zip.read(info.filename)
            if info.filename == "word/comments.xml":
                text = data.decode("utf-8")
                text = re.sub(r'w:author="[^"]*"', 'w:author="王文同"', text)
                text = re.sub(r'w:initials="[^"]*"', 'w:initials="WWT"', text)
                data = text.encode("utf-8")
            elif info.filename == "word/media/image1.png":
                data = replacement
            out_zip.writestr(info, data)
    shutil.move(temp, target)


def verify(
    original: Path,
    target: Path,
    replacement_image: Path,
) -> dict[str, object]:
    with zipfile.ZipFile(original) as original_zip, zipfile.ZipFile(target) as target_zip:
        original_doc = original_zip.read("word/document.xml")
        target_doc = target_zip.read("word/document.xml")
        comments_xml = target_zip.read("word/comments.xml")
        comments_root = ET.fromstring(comments_xml)
        comments = list(comments_root.iter(QW("comment")))
        comment_texts = [visible_text(ET.tostring(item, encoding="utf-8")) for item in comments]
        authors = Counter(item.get(QW("author"), "") for item in comments)
        initials = Counter(item.get(QW("initials"), "") for item in comments)

        marked_prefixes = [f"[标记事项{index:03d}/154" for index in range(1, 155)]
        supplemental_prefixes = [f"[补充事项{index:02d}/26" for index in range(1, 27)]
        prefix_counts = {
            prefix: sum(prefix in text for text in comment_texts)
            for prefix in marked_prefixes + supplemental_prefixes
        }

        original_media = {
            name: sha256(original_zip.read(name))
            for name in original_zip.namelist()
            if name.startswith("word/media/")
        }
        target_media = {
            name: sha256(target_zip.read(name))
            for name in target_zip.namelist()
            if name.startswith("word/media/")
        }
        replacement_hash = sha256(replacement_image.read_bytes())
        unchanged_media = {
            name: original_media[name] == target_media.get(name)
            for name in original_media
            if name != "word/media/image1.png"
        }

        image_bytes = target_zip.read("word/media/image1.png")
        with Image.open(io.BytesIO(image_bytes)) as image:
            image_size = list(image.size)

        report: dict[str, object] = {
            "zip_test": target_zip.testzip(),
            "comment_count": len(comments),
            "authors": dict(authors),
            "initials": dict(initials),
            "missing_prefixes": [key for key, value in prefix_counts.items() if value == 0],
            "duplicate_prefixes": [key for key, value in prefix_counts.items() if value > 1],
            "math_object_count": comments_xml.count(b"<m:oMath"),
            "math_placeholder_count": comments_xml.count(b"[[MATH:"),
            "body_visible_text_equal": visible_text(original_doc) == visible_text(target_doc),
            "red_visible_text_equal": marked_visible_text(original_doc, "red")
            == marked_visible_text(target_doc, "red"),
            "yellow_visible_text_equal": marked_visible_text(original_doc, "yellow")
            == marked_visible_text(target_doc, "yellow"),
            "replacement_image_hash_matches": target_media.get("word/media/image1.png")
            == replacement_hash,
            "replacement_image_size": image_size,
            "other_media_unchanged": unchanged_media,
            "original_media_hashes": original_media,
            "target_media_hashes": target_media,
        }
        report["passed"] = all(
            [
                report["zip_test"] is None,
                report["comment_count"] == 180,
                report["authors"] == {"王文同": 180},
                report["initials"] == {"WWT": 180},
                not report["missing_prefixes"],
                not report["duplicate_prefixes"],
                report["math_object_count"] >= 180,
                report["math_placeholder_count"] == 0,
                report["body_visible_text_equal"],
                report["red_visible_text_equal"],
                report["yellow_visible_text_equal"],
                report["replacement_image_hash_matches"],
                report["replacement_image_size"] == [3840, 2160],
                all(unchanged_media.values()),
            ]
        )
        return report


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit(
            "usage: finalize_atomic_patent.py ORIGINAL COMMENTED IMAGE OUTPUT REPORT"
        )
    original = Path(sys.argv[1])
    commented = Path(sys.argv[2])
    replacement_image = Path(sys.argv[3])
    target = Path(sys.argv[4])
    report_path = Path(sys.argv[5])
    patch(commented, target, replacement_image)
    report = verify(original, target, replacement_image)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
