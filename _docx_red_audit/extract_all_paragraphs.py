from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
Q = lambda name: f"{{{W}}}{name}"


def text_of(node: ET.Element) -> str:
    parts = []
    for child in node.iter():
        local = child.tag.rsplit("}", 1)[-1]
        if local in {"t", "delText", "instrText"} and child.text:
            parts.append(child.text)
        elif child.tag == Q("tab"):
            parts.append("\t")
        elif child.tag in {Q("br"), Q("cr")}:
            parts.append("\n")
    return "".join(parts)


source = Path(sys.argv[1])
output = Path(sys.argv[2])
with zipfile.ZipFile(source) as archive:
    root = ET.fromstring(archive.read("word/document.xml"))
    lines = []
    for index, paragraph in enumerate(root.iter(Q("p")), start=1):
        text = text_of(paragraph)
        lines.append(f"[{index:04d}] {text}")
output.write_text("\n".join(lines), encoding="utf-8")
print(output)
