from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from lxml import etree


BASE = Path(r"F:\泉城实验室\二期\论文\异常检测\_docx_paragraph_comments_20260811")
SOURCE = BASE / "source_2026.8.4.docx"
WORD_COMMENTS = BASE / "word_commented.docx"
SPECS = BASE / "paragraph_answer_specs.json"
OUTPUT = BASE / "final_commented.docx"
REPORT = BASE / "merge_comments_report.json"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
NS = {"w": W_NS}
W = f"{{{W_NS}}}"
R = f"{{{R_NS}}}"
W15 = f"{{{W15_NS}}}"

COMMENT_PARTS = (
    "word/comments.xml",
    "word/commentsExtended.xml",
    "word/commentsExtensible.xml",
    "word/commentsIds.xml",
    "word/people.xml",
)


def visible_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def add_comment_anchor(paragraph: etree._Element, comment_id: str) -> None:
    start = etree.Element(W + "commentRangeStart")
    start.set(W + "id", comment_id)
    end = etree.Element(W + "commentRangeEnd")
    end.set(W + "id", comment_id)

    insert_at = 1 if len(paragraph) and paragraph[0].tag == W + "pPr" else 0
    paragraph.insert(insert_at, start)
    paragraph.append(end)

    reference_run = etree.Element(W + "r")
    run_properties = etree.SubElement(reference_run, W + "rPr")
    run_style = etree.SubElement(run_properties, W + "rStyle")
    run_style.set(W + "val", "CommentReference")
    reference = etree.SubElement(reference_run, W + "commentReference")
    reference.set(W + "id", comment_id)
    paragraph.append(reference_run)


def merge_relationships(source_xml: bytes, word_xml: bytes) -> tuple[bytes, list[dict[str, str]]]:
    source_root = etree.fromstring(source_xml)
    word_root = etree.fromstring(word_xml)
    used_ids = {element.get("Id") for element in source_root}
    next_id = 1
    added = []

    for relationship in word_root:
        relationship_type = relationship.get("Type", "")
        if "comments" not in relationship_type and "people" not in relationship_type:
            continue
        while f"rId{next_id}" in used_ids:
            next_id += 1
        clone = deepcopy(relationship)
        clone.set("Id", f"rId{next_id}")
        used_ids.add(f"rId{next_id}")
        source_root.append(clone)
        added.append(
            {
                "id": clone.get("Id", ""),
                "type": clone.get("Type", ""),
                "target": clone.get("Target", ""),
            }
        )
        next_id += 1

    return etree.tostring(source_root, xml_declaration=True, encoding="UTF-8", standalone=True), added


def merge_content_types(
    source_xml: bytes, word_xml: bytes, available_parts: set[str]
) -> tuple[bytes, list[str]]:
    source_root = etree.fromstring(source_xml)
    word_root = etree.fromstring(word_xml)
    existing_parts = {element.get("PartName") for element in source_root}
    added = []

    for element in word_root:
        part_name = element.get("PartName") or ""
        if part_name not in {f"/{part}" for part in available_parts} or part_name in existing_parts:
            continue
        source_root.append(deepcopy(element))
        existing_parts.add(part_name)
        added.append(part_name)

    return etree.tostring(source_root, xml_declaration=True, encoding="UTF-8", standalone=True), added


def write_member(output_zip: ZipFile, info: ZipInfo, data: bytes) -> None:
    cloned_info = ZipInfo(info.filename, date_time=info.date_time)
    cloned_info.compress_type = info.compress_type
    cloned_info.comment = info.comment
    cloned_info.extra = info.extra
    cloned_info.internal_attr = info.internal_attr
    cloned_info.external_attr = info.external_attr
    cloned_info.create_system = info.create_system
    cloned_info.flag_bits = info.flag_bits
    output_zip.writestr(cloned_info, data)


def normalize_comment_authors(word_zip: ZipFile) -> dict[str, bytes]:
    available = set(word_zip.namelist())
    parts = {part: word_zip.read(part) for part in COMMENT_PARTS if part in available}
    if "word/comments.xml" not in parts:
        raise RuntimeError("The comment source has no word/comments.xml part.")

    comments_root = etree.fromstring(parts["word/comments.xml"])
    for comment in comments_root.findall(W + "comment"):
        comment.set(W + "author", "王文同")
        comment.set(W + "initials", "WWT")
    parts["word/comments.xml"] = etree.tostring(
        comments_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    if "word/people.xml" in parts:
        people_root = etree.fromstring(parts["word/people.xml"])
        for person in people_root.findall(W15 + "person"):
            person.set(W15 + "author", "王文同")
        parts["word/people.xml"] = etree.tostring(
            people_root, xml_declaration=True, encoding="UTF-8", standalone=True
        )
    return parts


def main() -> None:
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    expected_paragraphs = {item["paragraph_index"]: item["id"] for item in specs}

    with ZipFile(SOURCE) as source_zip, ZipFile(WORD_COMMENTS) as word_zip:
        comment_parts = normalize_comment_authors(word_zip)
        comments_root = etree.fromstring(comment_parts["word/comments.xml"])
        prefix_to_comment_id = {}
        comment_authors = []
        for comment in comments_root.findall(W + "comment"):
            comment_text = "".join(comment.xpath(".//w:t/text()", namespaces=NS))
            match = re.match(r"\[段落(\d{3})/35：整段答复\]", comment_text)
            if not match:
                raise RuntimeError(f"Unexpected comment prefix: {comment_text[:50]}")
            prefix_to_comment_id[int(match.group(1))] = comment.get(W + "id")
            comment_authors.append((comment.get(W + "author"), comment.get(W + "initials")))

        if set(prefix_to_comment_id) != set(expected_paragraphs):
            raise RuntimeError("Comment prefixes do not match the specified paragraph indexes.")

        document_root = etree.fromstring(source_zip.read("word/document.xml"))
        paragraphs = document_root.xpath("//w:p", namespaces=NS)
        anchors = []
        for paragraph_index in sorted(expected_paragraphs):
            if paragraph_index < 1 or paragraph_index > len(paragraphs):
                raise RuntimeError(f"Paragraph index out of range: {paragraph_index}")
            paragraph = paragraphs[paragraph_index - 1]
            comment_id = prefix_to_comment_id[paragraph_index]
            anchor_text = visible_text(paragraph)
            add_comment_anchor(paragraph, comment_id)
            anchors.append(
                {
                    "paragraph_index": paragraph_index,
                    "spec_id": expected_paragraphs[paragraph_index],
                    "comment_id": comment_id,
                    "anchor_text": anchor_text,
                }
            )

        document_xml = etree.tostring(
            document_root, xml_declaration=True, encoding="UTF-8", standalone=True
        )
        rels_xml, added_relationships = merge_relationships(
            source_zip.read("word/_rels/document.xml.rels"),
            word_zip.read("word/_rels/document.xml.rels"),
        )
        content_types_xml, added_content_types = merge_content_types(
            source_zip.read("[Content_Types].xml"),
            word_zip.read("[Content_Types].xml"),
            set(comment_parts),
        )

        replacements = {
            "word/document.xml": document_xml,
            "word/_rels/document.xml.rels": rels_xml,
            "[Content_Types].xml": content_types_xml,
        }

        if OUTPUT.exists():
            OUTPUT.unlink()
        with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as output_zip:
            for info in source_zip.infolist():
                data = replacements.get(info.filename, source_zip.read(info.filename))
                write_member(output_zip, info, data)
            for part, data in comment_parts.items():
                output_zip.writestr(part, data, compress_type=ZIP_DEFLATED)

    report = {
        "source": str(SOURCE),
        "word_comment_source": str(WORD_COMMENTS),
        "output": str(OUTPUT),
        "comment_count": len(prefix_to_comment_id),
        "paragraph_count": len(paragraphs),
        "authors": sorted({f"{author}/{initials}" for author, initials in comment_authors}),
        "added_relationships": added_relationships,
        "added_content_types": added_content_types,
        "anchors": anchors,
        "passed": len(prefix_to_comment_id) == 35 and len(anchors) == 35,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
