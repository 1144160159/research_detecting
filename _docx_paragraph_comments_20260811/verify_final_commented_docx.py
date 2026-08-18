from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


BASE = Path(r"F:\泉城实验室\二期\论文\异常检测\_docx_paragraph_comments_20260811")
SOURCE = BASE / "source_2026.8.4.docx"
FINAL = BASE / "final_commented.docx"
SPECS = BASE / "paragraph_answer_specs.json"
REPORT = BASE / "final_structural_verification.json"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
W = f"{{{W_NS}}}"
M = f"{{{M_NS}}}"
REL = f"{{{REL_NS}}}"
CT = f"{{{CT_NS}}}"
W15 = f"{{{W15_NS}}}"
NS = {"w": W_NS, "m": M_NS}
MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def stripped_document_xml(data: bytes) -> bytes:
    root = etree.fromstring(data)
    for element in root.findall(".//" + W + "commentRangeStart"):
        element.getparent().remove(element)
    for element in root.findall(".//" + W + "commentRangeEnd"):
        element.getparent().remove(element)
    for reference in root.findall(".//" + W + "commentReference"):
        run = reference.getparent()
        run.getparent().remove(run)
    return etree.tostring(root, method="c14n", exclusive=False, with_comments=False)


def comment_prose(comment: etree._Element) -> str:
    parts = []
    for text_node in comment.xpath(".//w:t", namespaces=NS):
        if not any(ancestor.tag == M + "oMath" for ancestor in text_node.iterancestors()):
            parts.append(text_node.text or "")
    return "".join(parts)


def main() -> None:
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    specs_by_paragraph = {item["paragraph_index"]: item for item in specs}
    expected_targets = sorted(specs_by_paragraph)
    expected_formula_count = sum(len(MATH_RE.findall(item["text"])) for item in specs)

    checks: dict[str, object] = {}
    failures = []

    with ZipFile(SOURCE) as source_zip, ZipFile(FINAL) as final_zip:
        checks["zip_test"] = final_zip.testzip()
        if checks["zip_test"] is not None:
            failures.append(f"ZIP test failed at {checks['zip_test']}")

        source_names = set(source_zip.namelist())
        final_names = set(final_zip.namelist())
        added_parts = sorted(final_names - source_names)
        checks["added_parts"] = added_parts
        if "word/comments.xml" not in final_names:
            failures.append("word/comments.xml is missing")

        allowed_changed = {
            "[Content_Types].xml",
            "word/_rels/document.xml.rels",
            "word/document.xml",
        }
        changed_unexpectedly = []
        for name in sorted(source_names & final_names):
            if name not in allowed_changed and source_zip.read(name) != final_zip.read(name):
                changed_unexpectedly.append(name)
        checks["unexpected_changed_parts"] = changed_unexpectedly
        if changed_unexpectedly:
            failures.append(f"Unexpected source parts changed: {changed_unexpectedly}")

        media_names = sorted(name for name in source_names if name.startswith("word/media/"))
        media_match = all(
            name in final_names and digest(source_zip.read(name)) == digest(final_zip.read(name))
            for name in media_names
        )
        checks["media_count"] = len(media_names)
        checks["media_hashes_match"] = media_match
        if not media_match:
            failures.append("Media hashes do not match the source")

        body_unchanged = stripped_document_xml(source_zip.read("word/document.xml")) == stripped_document_xml(
            final_zip.read("word/document.xml")
        )
        checks["body_xml_unchanged_after_stripping_comment_anchors"] = body_unchanged
        if not body_unchanged:
            failures.append("Body XML differs after comment anchors are stripped")

        source_document = etree.fromstring(source_zip.read("word/document.xml"))
        final_document = etree.fromstring(final_zip.read("word/document.xml"))
        source_paragraphs = source_document.xpath("//w:p", namespaces=NS)
        final_paragraphs = final_document.xpath("//w:p", namespaces=NS)
        checks["source_paragraph_count"] = len(source_paragraphs)
        checks["final_paragraph_count"] = len(final_paragraphs)
        if len(source_paragraphs) != len(final_paragraphs):
            failures.append("Paragraph count changed")

        comments_root = etree.fromstring(final_zip.read("word/comments.xml"))
        comments = comments_root.findall(W + "comment")
        checks["comment_count"] = len(comments)
        if len(comments) != 35:
            failures.append(f"Expected 35 comments, found {len(comments)}")

        comment_ids = []
        authors = set()
        initials = set()
        comment_records = []
        formula_total = 0
        for comment in comments:
            comment_id = comment.get(W + "id")
            text = "".join(comment.xpath(".//w:t/text()", namespaces=NS))
            match = re.match(r"\[段落(\d{3})/35：整段答复\]", text)
            if not match:
                failures.append(f"Comment {comment_id} has an invalid prefix")
                continue
            paragraph_index = int(match.group(1))
            spec = specs_by_paragraph.get(paragraph_index)
            if spec is None:
                failures.append(f"Comment {comment_id} targets unexpected paragraph {paragraph_index}")
                continue
            expected_prose = MATH_RE.sub("", spec["text"])
            actual_prose = comment_prose(comment)
            local_formula_count = len(comment.findall(".//" + M + "oMath"))
            expected_local_formula_count = len(MATH_RE.findall(spec["text"]))
            formula_total += local_formula_count
            prose_matches = actual_prose == expected_prose
            formula_count_matches = local_formula_count == expected_local_formula_count
            required_labels = "定义核对：" in actual_prose and "答复：" in actual_prose
            if not prose_matches:
                failures.append(f"Comment for paragraph {paragraph_index} has altered prose")
            if not formula_count_matches:
                failures.append(f"Comment for paragraph {paragraph_index} has the wrong formula count")
            if not required_labels:
                failures.append(f"Comment for paragraph {paragraph_index} lacks definition/answer labels")
            if "[[MATH:" in actual_prose:
                failures.append(f"Comment for paragraph {paragraph_index} contains a raw math marker")
            comment_ids.append(comment_id)
            authors.add(comment.get(W + "author"))
            initials.add(comment.get(W + "initials"))
            comment_records.append(
                {
                    "paragraph_index": paragraph_index,
                    "comment_id": comment_id,
                    "prose_matches": prose_matches,
                    "formula_count": local_formula_count,
                    "formula_count_matches": formula_count_matches,
                    "definition_and_answer_labels": required_labels,
                }
            )

        checks["authors"] = sorted(value for value in authors if value is not None)
        checks["initials"] = sorted(value for value in initials if value is not None)
        if authors != {"王文同"} or initials != {"WWT"}:
            failures.append(f"Unexpected comment author metadata: {authors}/{initials}")
        checks["formula_count"] = formula_total
        if formula_total != expected_formula_count:
            failures.append(f"Expected {expected_formula_count} formulas, found {formula_total}")

        start_ids = [element.get(W + "id") for element in final_document.findall(".//" + W + "commentRangeStart")]
        end_ids = [element.get(W + "id") for element in final_document.findall(".//" + W + "commentRangeEnd")]
        reference_ids = [element.get(W + "id") for element in final_document.findall(".//" + W + "commentReference")]
        checks["anchor_counts"] = {
            "start": len(start_ids),
            "end": len(end_ids),
            "reference": len(reference_ids),
        }
        if sorted(start_ids) != sorted(comment_ids) or sorted(end_ids) != sorted(comment_ids) or sorted(reference_ids) != sorted(comment_ids):
            failures.append("Comment anchor IDs do not match comment IDs")

        actual_target_paragraphs = []
        for paragraph_index, paragraph in enumerate(final_paragraphs, start=1):
            starts = paragraph.findall(".//" + W + "commentRangeStart")
            if starts:
                actual_target_paragraphs.append(paragraph_index)
                if len(starts) != 1:
                    failures.append(f"Paragraph {paragraph_index} has multiple comment starts")
        checks["target_paragraphs"] = actual_target_paragraphs
        if actual_target_paragraphs != expected_targets:
            failures.append("Commented paragraph indexes do not match the red technical-question set")

        red_paragraphs = []
        for paragraph_index, paragraph in enumerate(source_paragraphs, start=1):
            has_red = bool(paragraph_text(paragraph)) and any(
                # The patent agent's question text uses the exact direct color
                # EE0000. The document also contains a legitimate FF0000
                # section heading, which is not an agent question.
                (color.get(W + "val") or "").upper() == "EE0000"
                for color in paragraph.findall(".//" + W + "color")
            )
            if has_red:
                red_paragraphs.append(paragraph_index)
        checks["red_paragraphs"] = red_paragraphs
        technical_red = [index for index in red_paragraphs if index not in {2, 3, 4}]
        checks["technical_red_paragraphs"] = technical_red
        if technical_red != expected_targets:
            failures.append("Red-font technical questions and comment specifications do not match")

        rels_root = etree.fromstring(final_zip.read("word/_rels/document.xml.rels"))
        comment_relationship_targets = {
            relationship.get("Target")
            for relationship in rels_root
            if "comments" in (relationship.get("Type") or "")
            or "people" in (relationship.get("Type") or "")
        }
        checks["comment_relationship_targets"] = sorted(comment_relationship_targets)
        for target in comment_relationship_targets:
            package_name = "word/" + target
            if package_name not in final_names:
                failures.append(f"Relationship target is missing: {package_name}")

        content_types_root = etree.fromstring(final_zip.read("[Content_Types].xml"))
        override_parts = {element.get("PartName") for element in content_types_root.findall(CT + "Override")}
        for part in added_parts:
            if part.startswith("word/comments") or part == "word/people.xml":
                if f"/{part}" not in override_parts:
                    failures.append(f"Content type override missing for {part}")

        if "word/people.xml" in final_names:
            people_root = etree.fromstring(final_zip.read("word/people.xml"))
            people_authors = {person.get(W15 + "author") for person in people_root.findall(W15 + "person")}
            checks["people_authors"] = sorted(value for value in people_authors if value is not None)
            if people_authors != {"王文同"}:
                failures.append(f"Unexpected people.xml author metadata: {people_authors}")

        checks["comment_records"] = sorted(comment_records, key=lambda item: item["paragraph_index"])

    report = {
        "source": str(SOURCE),
        "final": str(FINAL),
        "checks": checks,
        "failures": failures,
        "passed": not failures,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
