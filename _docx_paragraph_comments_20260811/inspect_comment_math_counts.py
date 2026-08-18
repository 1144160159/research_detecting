import json
import re
import difflib
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


BASE = Path(r"F:\泉城实验室\二期\论文\异常检测\_docx_paragraph_comments_20260811")
DOCX = BASE / "final_commented.docx"
SPECS = BASE / "paragraph_answer_specs.json"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}


specs = json.loads(SPECS.read_text(encoding="utf-8"))
expected = {item["paragraph_index"]: item["text"].count("[[MATH:") for item in specs}
expected_prose = {
    item["paragraph_index"]: re.sub(r"\[\[MATH:.*?\]\]", "", item["text"])
    for item in specs
}

with ZipFile(DOCX) as package:
    root = etree.fromstring(package.read("word/comments.xml"))

records = []
for comment in root.findall(W + "comment"):
    text = "".join(comment.xpath(".//w:t/text()", namespaces=NS))
    match = re.match(r"\[段落(\d{3})/35：整段答复\]", text)
    paragraph_index = int(match.group(1)) if match else -1
    actual = len(comment.findall(".//" + M + "oMath"))
    actual_prose_parts = []
    for text_node in comment.xpath(".//w:t", namespaces=NS):
        if not any(ancestor.tag == M + "oMath" for ancestor in text_node.iterancestors()):
            actual_prose_parts.append(text_node.text or "")
    actual_prose = "".join(actual_prose_parts)
    records.append(
        {
            "paragraph_index": paragraph_index,
            "expected_markers": expected.get(paragraph_index),
            "actual_omath": actual,
            "delta": actual - expected.get(paragraph_index, 0),
            "prose_matches": actual_prose == expected_prose.get(paragraph_index),
            "expected_prose_length": len(expected_prose.get(paragraph_index, "")),
            "actual_prose_length": len(actual_prose),
        }
    )

    if actual_prose != expected_prose.get(paragraph_index):
        print(f"PROSE_DIFF_{paragraph_index}")
        for operation in difflib.SequenceMatcher(
            None, expected_prose.get(paragraph_index, ""), actual_prose
        ).get_opcodes():
            tag, i1, i2, j1, j2 = operation
            if tag != "equal":
                print(
                    tag,
                    repr(expected_prose.get(paragraph_index, "")[i1:i2]),
                    repr(actual_prose[j1:j2]),
                )

    if paragraph_index == 51:
        print("P051_CHILDREN")
        for paragraph in comment.findall(".//" + W + "p"):
            for child in paragraph:
                local_name = etree.QName(child).localname
                child_text = "".join(child.itertext())
                print(local_name, repr(child_text))

print(json.dumps(records, ensure_ascii=False, indent=2))
