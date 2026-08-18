from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
Q = lambda name: f"{{{W}}}{name}"
NS = {"w": W}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def node_text(node: ET.Element) -> str:
    parts: list[str] = []
    for child in node.iter():
        name = local_name(child.tag)
        if name in {"t", "delText", "instrText"} and child.text:
            parts.append(child.text)
        elif child.tag == Q("tab"):
            parts.append("\t")
        elif child.tag in {Q("br"), Q("cr")}:
            parts.append("\n")
    return "".join(parts)


def normalize(value: str | None) -> str:
    return (value or "").strip().upper().lstrip("#")


def is_red(value: str | None) -> bool:
    value = normalize(value)
    if value in {"RED"}:
        return True
    if not re.fullmatch(r"[0-9A-F]{6}", value):
        return False
    red, green, blue = int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16)
    return red >= 170 and red >= 1.45 * green and red >= 1.45 * blue and green <= 140 and blue <= 140


def is_yellow(value: str | None) -> bool:
    value = normalize(value)
    if value in {"YELLOW", "DARKYELLOW"}:
        return True
    if not re.fullmatch(r"[0-9A-F]{6}", value):
        return False
    red, green, blue = int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16)
    return red >= 210 and green >= 180 and blue <= 190 and red >= 1.15 * blue and green >= 1.05 * blue


def nearest_ancestor(
    node: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
    tag: str,
) -> ET.Element | None:
    current = node
    while current in parent_map:
        current = parent_map[current]
        if current.tag == tag:
            return current
    return None


def shading(node: ET.Element | None, xpath: str) -> str:
    if node is None:
        return ""
    item = node.find(xpath, NS)
    return normalize(item.get(Q("fill"))) if item is not None else ""


def run_marks(run: ET.Element, paragraph_yellow: bool) -> tuple[bool, bool]:
    color = run.find("./w:rPr/w:color", NS)
    highlight = run.find("./w:rPr/w:highlight", NS)
    fill = run.find("./w:rPr/w:shd", NS)
    red = is_red(color.get(Q("val"))) if color is not None else False
    yellow = paragraph_yellow
    if highlight is not None:
        yellow = yellow or is_yellow(highlight.get(Q("val")))
    if fill is not None:
        yellow = yellow or is_yellow(fill.get(Q("fill")))
    return red, yellow


def marked_spans(chars: list[dict[str, object]]) -> list[dict[str, object]]:
    spans: list[dict[str, object]] = []
    start: int | None = None
    current_marks: tuple[bool, bool] | None = None
    for index, char in enumerate(chars + [{"red": False, "yellow": False}]):
        marks = (bool(char["red"]), bool(char["yellow"]))
        marked = marks[0] or marks[1]
        if start is None and marked:
            start = index
            current_marks = marks
        elif start is not None and (not marked or marks != current_marks):
            segment = chars[start:index]
            text = "".join(str(item["char"]) for item in segment)
            comment_ids = sorted(
                {str(comment_id) for item in segment for comment_id in item["comments"]},
                key=lambda value: int(value) if value.isdigit() else 10**9,
            )
            covered = sum(bool(item["comments"]) for item in segment)
            spans.append(
                {
                    "start": start,
                    "end": index,
                    "text": text,
                    "red": bool(current_marks and current_marks[0]),
                    "yellow": bool(current_marks and current_marks[1]),
                    "length": len(segment),
                    "covered_characters": covered,
                    "coverage_ratio": covered / len(segment) if segment else 0,
                    "comment_ids": comment_ids,
                }
            )
            start = index if marked else None
            current_marks = marks if marked else None
    return spans


def question_clauses(chars: list[dict[str, object]]) -> list[dict[str, object]]:
    text = "".join(str(item["char"]) for item in chars)
    clauses: list[dict[str, object]] = []
    hard_delimiters = "。！？!?；;\n"
    soft_delimiters = "（("
    for match in re.finditer(r"[？?]", text):
        question_at = match.start()
        if not (bool(chars[question_at]["red"]) or bool(chars[question_at]["yellow"])):
            continue
        start = 0
        for index in range(question_at - 1, -1, -1):
            if text[index] in hard_delimiters or text[index] in soft_delimiters:
                start = index + 1
                break
        segment = chars[start : question_at + 1]
        comment_ids = sorted(
            {str(comment_id) for item in segment for comment_id in item["comments"]},
            key=lambda value: int(value) if value.isdigit() else 10**9,
        )
        marked_segment = [item for item in segment if bool(item["red"]) or bool(item["yellow"])]
        covered_marked = sum(bool(item["comments"]) for item in marked_segment)
        clauses.append(
            {
                "start": start,
                "end": question_at + 1,
                "text": text[start : question_at + 1],
                "question_mark_covered": bool(chars[question_at]["comments"]),
                "marked_character_count": len(marked_segment),
                "covered_marked_characters": covered_marked,
                "coverage_ratio": covered_marked / len(marked_segment) if marked_segment else 0,
                "comment_ids": comment_ids,
            }
        )
    return clauses


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_marked_comment_coverage.py input.docx output.json")

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    with zipfile.ZipFile(source) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        comments_root = ET.fromstring(archive.read("word/comments.xml"))

    parent_map = {child: parent for parent in document.iter() for child in parent}
    comment_text = {
        item.get(Q("id"), ""): node_text(item)
        for item in comments_root.iter(Q("comment"))
    }

    paragraphs: list[dict[str, object]] = []
    all_characters = 0
    marked_characters = 0
    covered_marked_characters = 0
    active: set[str] = set()

    for paragraph_index, paragraph in enumerate(document.iter(Q("p")), start=1):
        paragraph_fill = shading(paragraph, "./w:pPr/w:shd")
        table_cell = nearest_ancestor(paragraph, parent_map, Q("tc"))
        cell_fill = shading(table_cell, "./w:tcPr/w:shd")
        paragraph_yellow = is_yellow(paragraph_fill) or is_yellow(cell_fill)

        chars: list[dict[str, object]] = []
        for item in paragraph.iter():
            if item.tag == Q("commentRangeStart"):
                active.add(item.get(Q("id"), ""))
            elif item.tag == Q("commentRangeEnd"):
                active.discard(item.get(Q("id"), ""))
            elif item.tag == Q("r"):
                text = node_text(item)
                if not text:
                    continue
                red, yellow = run_marks(item, paragraph_yellow)
                for char in text:
                    chars.append(
                        {
                            "char": char,
                            "red": red,
                            "yellow": yellow,
                            "comments": sorted(active),
                        }
                    )

        text = "".join(str(item["char"]) for item in chars)
        spans = marked_spans(chars)
        questions = question_clauses(chars)
        if not spans and not questions:
            all_characters += len(chars)
            continue

        marked_in_paragraph = [item for item in chars if bool(item["red"]) or bool(item["yellow"])]
        covered_in_paragraph = [item for item in marked_in_paragraph if bool(item["comments"])]
        all_characters += len(chars)
        marked_characters += len(marked_in_paragraph)
        covered_marked_characters += len(covered_in_paragraph)
        comment_ids = sorted(
            {str(comment_id) for item in chars for comment_id in item["comments"]},
            key=lambda value: int(value) if value.isdigit() else 10**9,
        )
        paragraphs.append(
            {
                "paragraph_index": paragraph_index,
                "text": text,
                "marked_character_count": len(marked_in_paragraph),
                "covered_marked_characters": len(covered_in_paragraph),
                "coverage_ratio": len(covered_in_paragraph) / len(marked_in_paragraph) if marked_in_paragraph else 0,
                "comment_ids": comment_ids,
                "spans": spans,
                "questions": questions,
            }
        )

    span_records = [
        {"paragraph_index": paragraph["paragraph_index"], **span}
        for paragraph in paragraphs
        for span in paragraph["spans"]
    ]
    question_records = [
        {"paragraph_index": paragraph["paragraph_index"], **question}
        for paragraph in paragraphs
        for question in paragraph["questions"]
    ]
    uncovered_spans = [item for item in span_records if item["coverage_ratio"] < 1.0]
    uncovered_questions = [
        item
        for item in question_records
        if item["coverage_ratio"] < 1.0 or not item["question_mark_covered"]
    ]
    completely_uncovered_spans = [item for item in span_records if item["coverage_ratio"] == 0]

    comment_usage = Counter(
        str(comment_id)
        for paragraph in paragraphs
        for comment_id in paragraph["comment_ids"]
    )
    result = {
        "source": str(source),
        "comment_count": len(comment_text),
        "marked_paragraph_count": len(paragraphs),
        "marked_character_count": marked_characters,
        "covered_marked_character_count": covered_marked_characters,
        "marked_character_coverage_ratio": covered_marked_characters / marked_characters if marked_characters else 1,
        "marked_span_count": len(span_records),
        "partially_or_fully_uncovered_span_count": len(uncovered_spans),
        "completely_uncovered_span_count": len(completely_uncovered_spans),
        "marked_question_count": len(question_records),
        "uncovered_question_count": len(uncovered_questions),
        "comments_without_marked_paragraph_overlap": sorted(set(comment_text) - set(comment_usage)),
        "uncovered_spans": uncovered_spans,
        "uncovered_questions": uncovered_questions,
        "paragraphs": paragraphs,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in {"uncovered_spans", "uncovered_questions", "paragraphs"}},
            ensure_ascii=True,
            indent=2,
        )
    )
    print(json.dumps({"uncovered_spans": uncovered_spans, "uncovered_questions": uncovered_questions}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
