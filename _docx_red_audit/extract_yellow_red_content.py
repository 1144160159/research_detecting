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


def text_of(node: ET.Element) -> str:
    parts = []
    for child in node.iter():
        local = local_name(child.tag)
        if local in {"t", "delText", "instrText"} and child.text:
            parts.append(child.text)
        elif child.tag == Q("tab"):
            parts.append("\t")
        elif child.tag in {Q("br"), Q("cr")}:
            parts.append("\n")
    return "".join(parts)


def normalize(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().upper().lstrip("#")


def is_red(value: str | None) -> bool:
    value = normalize(value)
    if not value or not re.fullmatch(r"[0-9A-F]{6}", value):
        return False
    r, g, b = int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16)
    return r >= 170 and r >= 1.45 * g and r >= 1.45 * b and g <= 140 and b <= 140


def is_yellow_fill(value: str | None) -> bool:
    value = normalize(value)
    if not value or value in {"AUTO", "NIL", "CLEAR"}:
        return False
    if value in {"YELLOW", "DARKYELLOW"}:
        return True
    if not re.fullmatch(r"[0-9A-F]{6}", value):
        return False
    r, g, b = int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16)
    return r >= 210 and g >= 180 and b <= 190 and r >= b * 1.15 and g >= b * 1.05


def nearest_ancestor(node: ET.Element, parent_map: dict[ET.Element, ET.Element], tag: str):
    current = node
    while current in parent_map:
        current = parent_map[current]
        if current.tag == tag:
            return current
    return None


def shading_fill(node: ET.Element | None, xpath: str) -> str | None:
    if node is None:
        return None
    shd = node.find(xpath, NS)
    return normalize(shd.get(Q("fill"))) if shd is not None else None


def highlight_value(run: ET.Element) -> str | None:
    item = run.find("./w:rPr/w:highlight", NS)
    return normalize(item.get(Q("val"))) if item is not None else None


def run_color(run: ET.Element) -> str | None:
    item = run.find("./w:rPr/w:color", NS)
    return normalize(item.get(Q("val"))) if item is not None else None


def main() -> int:
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    with zipfile.ZipFile(source) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))

    parent_map = {child: parent for parent in root.iter() for child in parent}
    highlight_values = Counter()
    shading_values = Counter()
    color_values = Counter()

    for node in root.iter():
        if node.tag == Q("highlight"):
            highlight_values[normalize(node.get(Q("val"))) or ""] += 1
        elif node.tag == Q("shd"):
            shading_values[normalize(node.get(Q("fill"))) or ""] += 1
        elif node.tag == Q("color"):
            color_values[normalize(node.get(Q("val"))) or ""] += 1

    records = []
    all_paragraphs = list(root.iter(Q("p")))
    heading = ""
    for index, paragraph in enumerate(all_paragraphs, start=1):
        full_text = text_of(paragraph)
        if not full_text.strip():
            continue
        p_style = paragraph.find("./w:pPr/w:pStyle", NS)
        p_style_id = p_style.get(Q("val")) if p_style is not None else ""
        if re.match(r"^(Heading|标题)", p_style_id, flags=re.I) or re.match(
            r"^\d+[、.]", full_text.strip()
        ):
            heading = full_text.strip()

        p_fill = shading_fill(paragraph, "./w:pPr/w:shd")
        tc = nearest_ancestor(paragraph, parent_map, Q("tc"))
        tc_fill = shading_fill(tc, "./w:tcPr/w:shd")
        p_yellow = is_yellow_fill(p_fill) or is_yellow_fill(tc_fill)

        yellow_segments = []
        red_segments = []
        yellow_red_segments = []
        for run in paragraph.iter(Q("r")):
            run_text = text_of(run)
            if not run_text:
                continue
            hi = highlight_value(run)
            run_fill = shading_fill(run, "./w:rPr/w:shd")
            yellow = p_yellow or is_yellow_fill(hi) or is_yellow_fill(run_fill)
            red = is_red(run_color(run))
            if yellow:
                yellow_segments.append(run_text)
            if red:
                red_segments.append(run_text)
            if yellow and red:
                yellow_red_segments.append(run_text)

        if p_yellow or yellow_segments or red_segments:
            records.append(
                {
                    "paragraph_index": index,
                    "heading": heading,
                    "paragraph_style": p_style_id,
                    "paragraph_fill": p_fill,
                    "cell_fill": tc_fill,
                    "full_text": full_text,
                    "yellow_segments": yellow_segments,
                    "red_segments": red_segments,
                    "yellow_red_segments": yellow_red_segments,
                }
            )

    yellow_records = [r for r in records if r["paragraph_fill"] or r["cell_fill"] or r["yellow_segments"]]
    red_records = [r for r in records if r["red_segments"]]
    both_records = [r for r in records if r["yellow_segments"] and r["red_segments"]]
    yellow_only_records = [r for r in records if (r["paragraph_fill"] or r["cell_fill"] or r["yellow_segments"]) and not r["red_segments"]]

    result = {
        "source": str(source),
        "highlight_values": dict(highlight_values),
        "shading_values": dict(shading_values),
        "font_color_values": dict(color_values),
        "yellow_paragraph_count": len(yellow_records),
        "red_paragraph_count": len(red_records),
        "yellow_and_red_paragraph_count": len(both_records),
        "yellow_only_paragraph_count": len(yellow_only_records),
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, ensure_ascii=False, indent=2))
    for record in records:
        flags = []
        if record["yellow_segments"] or is_yellow_fill(record["paragraph_fill"]) or is_yellow_fill(record["cell_fill"]):
            flags.append("YELLOW")
        if record["red_segments"]:
            flags.append("RED")
        print(f"\n[{record['paragraph_index']:04d}] {'+'.join(flags)} | {record['heading']}")
        if record["yellow_segments"]:
            print("Y:", " || ".join(record["yellow_segments"]))
        if record["red_segments"]:
            print("R:", " || ".join(record["red_segments"]))
        print("T:", record["full_text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
