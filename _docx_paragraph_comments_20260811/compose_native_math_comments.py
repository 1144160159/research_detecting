from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from lxml import etree


BASE = Path(r"F:\泉城实验室\二期\论文\异常检测\_docx_paragraph_comments_20260811")
PLAIN = BASE / "plain_commented.docx"
FORMULA_LIBRARY = BASE / "formula_library.docx"
SPECS = BASE / "paragraph_answer_specs.json"
OUTPUT = BASE / "word_commented.docx"
REPORT = BASE / "native_math_comments_report.json"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
W = f"{{{W_NS}}}"
M = f"{{{M_NS}}}"
W15 = f"{{{W15_NS}}}"
NS = {"w": W_NS, "m": M_NS}
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
MATH_RE = re.compile(r"\[\[MATH:(.*?)\]\]")


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


def make_prose_run(text: str) -> etree._Element:
    run = etree.Element(W + "r")
    properties = etree.SubElement(run, W + "rPr")
    fonts = etree.SubElement(properties, W + "rFonts")
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(W + attribute, "宋体")
    size = etree.SubElement(properties, W + "sz")
    size.set(W + "val", "21")
    size_cs = etree.SubElement(properties, W + "szCs")
    size_cs.set(W + "val", "21")
    language = etree.SubElement(properties, W + "lang")
    language.set(W + "eastAsia", "zh-CN")
    text_element = etree.SubElement(run, W + "t")
    if text[:1].isspace() or text[-1:].isspace():
        text_element.set(XML_SPACE, "preserve")
    text_element.text = text
    return run


def keep_comment_reference(paragraph: etree._Element) -> list[etree._Element]:
    kept = []
    paragraph_properties = paragraph.find(W + "pPr")
    if paragraph_properties is not None:
        kept.append(deepcopy(paragraph_properties))
    for run in paragraph.findall(W + "r"):
        if run.find(".//" + W + "annotationRef") is not None:
            kept.append(deepcopy(run))
    return kept


def non_math_prose(comment: etree._Element) -> str:
    parts = []
    for text_node in comment.xpath(".//w:t", namespaces=NS):
        if not any(ancestor.tag == M + "oMath" for ancestor in text_node.iterancestors()):
            parts.append(text_node.text or "")
    return "".join(parts)


def main() -> None:
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    specs_by_paragraph = {item["paragraph_index"]: item for item in specs}
    expected_formula_count = sum(len(MATH_RE.findall(item["text"])) for item in specs)

    with ZipFile(FORMULA_LIBRARY) as formula_zip:
        formula_root = etree.fromstring(formula_zip.read("word/document.xml"))
        formula_cells = formula_root.findall(".//" + W + "tc")
        formulas = []
        for index, cell in enumerate(formula_cells, start=1):
            cell_formulas = cell.findall(".//" + M + "oMath")
            if len(cell_formulas) != 1:
                raise RuntimeError(f"Formula cell {index} has {len(cell_formulas)} OMath nodes.")
            formulas.append(deepcopy(cell_formulas[0]))
    if len(formulas) != expected_formula_count:
        raise RuntimeError(
            f"Formula library count {len(formulas)} != expected {expected_formula_count}."
        )

    with ZipFile(PLAIN) as plain_zip:
        comments_root = etree.fromstring(plain_zip.read("word/comments.xml"))
        comment_records = []
        formula_cursor = 0

        for comment in comments_root.findall(W + "comment"):
            original_text = "".join(comment.xpath(".//w:t/text()", namespaces=NS))
            prefix_match = re.match(r"\[段落(\d{3})/35：整段答复\]", original_text)
            if not prefix_match:
                raise RuntimeError(f"Unexpected comment prefix: {original_text[:60]}")
            paragraph_index = int(prefix_match.group(1))
            spec = specs_by_paragraph.get(paragraph_index)
            if spec is None:
                raise RuntimeError(f"No specification for paragraph {paragraph_index}.")

            paragraphs = comment.findall(W + "p")
            if not paragraphs:
                raise RuntimeError(f"Comment for paragraph {paragraph_index} has no paragraph.")
            paragraph = paragraphs[0]
            preserved = keep_comment_reference(paragraph)
            for child in list(paragraph):
                paragraph.remove(child)
            for child in preserved:
                paragraph.append(child)
            for extra_paragraph in paragraphs[1:]:
                comment.remove(extra_paragraph)

            position = 0
            local_formula_count = 0
            for match in MATH_RE.finditer(spec["text"]):
                prose = spec["text"][position : match.start()]
                if prose:
                    paragraph.append(make_prose_run(prose))
                if formula_cursor >= len(formulas):
                    raise RuntimeError("Formula library exhausted early.")
                paragraph.append(deepcopy(formulas[formula_cursor]))
                formula_cursor += 1
                local_formula_count += 1
                position = match.end()
            trailing = spec["text"][position:]
            if trailing:
                paragraph.append(make_prose_run(trailing))

            comment.set(W + "author", "王文同")
            comment.set(W + "initials", "WWT")
            expected_prose = MATH_RE.sub("", spec["text"])
            actual_prose = non_math_prose(comment)
            comment_records.append(
                {
                    "paragraph_index": paragraph_index,
                    "comment_id": comment.get(W + "id"),
                    "formula_count": local_formula_count,
                    "prose_matches": actual_prose == expected_prose,
                }
            )

        if formula_cursor != len(formulas):
            raise RuntimeError(
                f"Only consumed {formula_cursor} of {len(formulas)} formula nodes."
            )

        replacements = {
            "word/comments.xml": etree.tostring(
                comments_root, xml_declaration=True, encoding="UTF-8", standalone=True
            )
        }
        if "word/people.xml" in plain_zip.namelist():
            people_root = etree.fromstring(plain_zip.read("word/people.xml"))
            for person in people_root.findall(W15 + "person"):
                person.set(W15 + "author", "王文同")
            replacements["word/people.xml"] = etree.tostring(
                people_root, xml_declaration=True, encoding="UTF-8", standalone=True
            )

        if OUTPUT.exists():
            OUTPUT.unlink()
        with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as output_zip:
            for info in plain_zip.infolist():
                write_member(
                    output_zip,
                    info,
                    replacements.get(info.filename, plain_zip.read(info.filename)),
                )

    report = {
        "output": str(OUTPUT),
        "comment_count": len(comment_records),
        "formula_count": formula_cursor,
        "prose_mismatch_count": sum(not item["prose_matches"] for item in comment_records),
        "records": comment_records,
        "passed": (
            len(comment_records) == 35
            and formula_cursor == expected_formula_count
            and all(item["prose_matches"] for item in comment_records)
        ),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
