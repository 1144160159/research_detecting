from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}


def q(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_of(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag in {q(W, "t"), q(M, "t")} and node.text:
            parts.append(node.text)
    return "".join(parts)


def visible_document_text(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    parts: list[str] = []
    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local in {"t", "delText", "instrText"} and node.text:
            parts.append(node.text)
        elif node.tag == q(W, "tab"):
            parts.append("\t")
        elif node.tag in {q(W, "br"), q(W, "cr")}:
            parts.append("\n")
    return "".join(parts)


def marked_document_text(xml_bytes: bytes, mode: str) -> str:
    root = ET.fromstring(xml_bytes)
    parts: list[str] = []
    for run in root.iter(q(W, "r")):
        properties = run.find(q(W, "rPr"))
        if properties is None:
            continue
        if mode == "red":
            color = properties.find(q(W, "color"))
            value = color.get(q(W, "val"), "").upper() if color is not None else ""
            selected = value in {"EE0000", "FF0000", "RED"}
        elif mode == "yellow":
            highlight = properties.find(q(W, "highlight"))
            value = highlight.get(q(W, "val"), "").upper() if highlight is not None else ""
            selected = value == "YELLOW"
        else:
            raise ValueError(mode)
        if selected:
            for node in run.iter():
                if node.tag in {q(W, "t"), q(W, "delText")} and node.text:
                    parts.append(node.text)
    return "".join(parts)


def comment_id(text: str) -> str | None:
    marked = re.match(r"^\[[^0-9]*(\d{3})/154", text)
    if marked:
        return f"M{int(marked.group(1)):03d}"
    supplemental = re.match(r"^\[[^0-9]*(\d{2})/26", text)
    if supplemental:
        return f"S{int(supplemental.group(1)):02d}"
    return None


def media_hashes(archive: zipfile.ZipFile) -> dict[str, str]:
    return {
        name: digest(archive.read(name))
        for name in archive.namelist()
        if name.startswith("word/media/") and not name.endswith("/")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("specs", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    specs = json.loads(args.specs.read_text(encoding="utf-8"))
    expected_formula_counts = {
        item["id"]: len(re.findall(r"\[\[MATH:(.*?)\]\]", item["text"]))
        for item in specs
    }
    expected_comment_count = len(specs)
    require_m051_structure = "M051" in expected_formula_counts

    with zipfile.ZipFile(args.source) as source_zip, zipfile.ZipFile(args.target) as target_zip:
        source_document = source_zip.read("word/document.xml")
        target_document = target_zip.read("word/document.xml")
        comments_xml = target_zip.read("word/comments.xml")
        comments_root = ET.fromstring(comments_xml)
        comments = comments_root.findall("w:comment", NS)

        ids: list[str] = []
        actual_formula_counts: dict[str, int] = {}
        formula_texts: list[str] = []
        invalid_comment_ids: list[int] = []
        m051_structure: dict[str, int] = {}

        for comment in comments:
            visible = text_of(comment)
            cid = comment_id(visible)
            if cid is None:
                invalid_comment_ids.append(int(comment.get(q(W, "id"), "-1")))
                continue
            ids.append(cid)
            maths = comment.findall(".//m:oMath", NS)
            actual_formula_counts[cid] = len(maths)
            formula_texts.extend(text_of(math) for math in maths)
            if cid == "M051":
                m051_structure = {
                    "formula_count": len(maths),
                    "fraction_count": len(comment.findall(".//m:f", NS)),
                    "function_count": len(comment.findall(".//m:func", NS)),
                    "subscript_count": len(comment.findall(".//m:sSub", NS)),
                }

        all_maths = comments_root.findall(".//m:oMath", NS)
        math_runs = comments_root.findall(".//m:oMath//m:r", NS)
        font_runs = 0
        size_runs = 0
        wrong_font_runs = 0
        wrong_size_runs = 0
        for run in math_runs:
            rpr = run.find("w:rPr", NS)
            if rpr is None:
                continue
            fonts = rpr.find("w:rFonts", NS)
            if fonts is not None:
                font_runs += 1
                values = [
                    fonts.get(q(W, "ascii")),
                    fonts.get(q(W, "hAnsi")),
                    fonts.get(q(W, "cs")),
                ]
                explicit = [value for value in values if value]
                if explicit and any(value != "Cambria Math" for value in explicit):
                    wrong_font_runs += 1
            size = rpr.find("w:sz", NS)
            if size is not None:
                size_runs += 1
                if size.get(q(W, "val")) != "21":
                    wrong_size_runs += 1

        pseudo_patterns = {
            "ascii_epsilon": re.compile(r"\bepsilon\b", re.I),
            "ascii_sum": re.compile(r"\bsum_", re.I),
            "ascii_set_operator": re.compile(r"\b(?:subseteq|setminus)\b", re.I),
            "pseudo_function": re.compile(r"\b(?:norm|abs|clip|nhat)\b", re.I),
            "ascii_inequality": re.compile(r"<=|>="),
            "placeholder": re.compile(r"\[\[MATH:"),
        }
        formula_blob = "\n".join(formula_texts)
        pseudo_hits = {
            name: pattern.findall(formula_blob)
            for name, pattern in pseudo_patterns.items()
            if pattern.search(formula_blob)
        }

        missing_ids = sorted(set(expected_formula_counts) - set(ids))
        extra_ids = sorted(set(ids) - set(expected_formula_counts))
        duplicate_ids = sorted(key for key, value in Counter(ids).items() if value != 1)
        formula_count_mismatches = {
            cid: {
                "expected": expected_formula_counts[cid],
                "actual": actual_formula_counts.get(cid, -1),
            }
            for cid in expected_formula_counts
            if expected_formula_counts[cid] != actual_formula_counts.get(cid, -1)
        }

        authors = Counter(comment.get(q(W, "author"), "") for comment in comments)
        initials = Counter(comment.get(q(W, "initials"), "") for comment in comments)
        source_media = media_hashes(source_zip)
        target_media = media_hashes(target_zip)

        structure_counts = {
            "fraction": len(comments_root.findall(".//m:f", NS)),
            "nary": len(comments_root.findall(".//m:nary", NS)),
            "subscript": len(comments_root.findall(".//m:sSub", NS)),
            "superscript": len(comments_root.findall(".//m:sSup", NS)),
            "subscript_superscript": len(comments_root.findall(".//m:sSubSup", NS)),
            "function": len(comments_root.findall(".//m:func", NS)),
            "delimiter": len(comments_root.findall(".//m:d", NS)),
        }

        report = {
            "source": str(args.source),
            "target": str(args.target),
            "source_zip_test": source_zip.testzip(),
            "target_zip_test": target_zip.testzip(),
            "document_xml_byte_equal": source_document == target_document,
            "body_visible_text_equal": visible_document_text(source_document)
            == visible_document_text(target_document),
            "red_visible_text_equal": marked_document_text(source_document, "red")
            == marked_document_text(target_document, "red"),
            "yellow_visible_text_equal": marked_document_text(source_document, "yellow")
            == marked_document_text(target_document, "yellow"),
            "document_xml_source_sha256": digest(source_document),
            "document_xml_target_sha256": digest(target_document),
            "media_hashes_equal": source_media == target_media,
            "media_count": len(target_media),
            "comment_count": len(comments),
            "authors": dict(authors),
            "initials": dict(initials),
            "math_object_count": len(all_maths),
            "expected_math_object_count": sum(expected_formula_counts.values()),
            "missing_ids": missing_ids,
            "extra_ids": extra_ids,
            "duplicate_ids": duplicate_ids,
            "invalid_comment_ids": invalid_comment_ids,
            "formula_count_mismatches": formula_count_mismatches,
            "math_placeholder_count": comments_xml.count(b"[[MATH:"),
            "pseudo_formula_hits": pseudo_hits,
            "structure_counts": structure_counts,
            "m051_structure": m051_structure,
            "math_run_count": len(math_runs),
            "math_font_run_count": font_runs,
            "math_size_run_count": size_runs,
            "wrong_math_font_runs": wrong_font_runs,
            "wrong_math_size_runs": wrong_size_runs,
        }

        report["passed"] = all(
            [
                report["source_zip_test"] is None,
                report["target_zip_test"] is None,
                report["body_visible_text_equal"],
                report["red_visible_text_equal"],
                report["yellow_visible_text_equal"],
                report["media_hashes_equal"],
                report["comment_count"] == expected_comment_count,
                report["authors"] == {"王文同": expected_comment_count},
                report["initials"] == {"WWT": expected_comment_count},
                report["math_object_count"] == report["expected_math_object_count"],
                not report["missing_ids"],
                not report["extra_ids"],
                not report["duplicate_ids"],
                not report["invalid_comment_ids"],
                not report["formula_count_mismatches"],
                report["math_placeholder_count"] == 0,
                not report["pseudo_formula_hits"],
                report["wrong_math_font_runs"] == 0,
                report["wrong_math_size_runs"] == 0,
                not require_m051_structure
                or report["m051_structure"].get("formula_count") == 4,
                not require_m051_structure
                or report["m051_structure"].get("fraction_count", 0) >= 1,
                not require_m051_structure
                or report["m051_structure"].get("function_count", 0) >= 2,
                not require_m051_structure
                or report["m051_structure"].get("subscript_count", 0) >= 4,
            ]
        )

    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
