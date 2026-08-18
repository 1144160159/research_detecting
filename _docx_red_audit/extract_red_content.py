from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
Q = lambda name: f"{{{W}}}{name}"


def node_text(node: ET.Element) -> str:
    parts: list[str] = []
    for child in node.iter():
        local_name = child.tag.rsplit("}", 1)[-1]
        if local_name in {"t", "delText", "instrText"} and child.text:
            parts.append(child.text)
        elif child.tag == Q("tab"):
            parts.append("\t")
        elif child.tag in {Q("br"), Q("cr")}:
            parts.append("\n")
    return "".join(parts)


def normalize_color(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().upper().lstrip("#")
    if value == "AUTO":
        return value
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return value


def direct_run_color(run: ET.Element) -> str | None:
    color = run.find("./w:rPr/w:color", NS)
    if color is None:
        return None
    return normalize_color(color.get(Q("val")))


def style_maps(styles_root: ET.Element | None):
    styles: dict[str, dict[str, str | None]] = {}
    defaults = None
    if styles_root is None:
        return styles, defaults
    default_color = styles_root.find("./w:docDefaults/w:rPrDefault/w:rPr/w:color", NS)
    if default_color is not None:
        defaults = normalize_color(default_color.get(Q("val")))
    for style in styles_root.findall("./w:style", NS):
        sid = style.get(Q("styleId"))
        if not sid:
            continue
        based_on = style.find("./w:basedOn", NS)
        color = style.find("./w:rPr/w:color", NS)
        styles[sid] = {
            "based_on": based_on.get(Q("val")) if based_on is not None else None,
            "color": normalize_color(color.get(Q("val"))) if color is not None else None,
        }
    return styles, defaults


def resolved_style_color(style_id: str | None, styles, default_color) -> str | None:
    seen: set[str] = set()
    current = style_id
    while current and current not in seen:
        seen.add(current)
        record = styles.get(current)
        if not record:
            break
        if record["color"]:
            return record["color"]
        current = record["based_on"]
    return default_color


def effective_color(run: ET.Element, paragraph: ET.Element, styles, default_color):
    color = direct_run_color(run)
    if color:
        return color, "direct"
    rstyle = run.find("./w:rPr/w:rStyle", NS)
    if rstyle is not None:
        style_id = rstyle.get(Q("val"))
        color = resolved_style_color(style_id, styles, default_color)
        if color:
            return color, f"run-style:{style_id}"
    pstyle = paragraph.find("./w:pPr/w:pStyle", NS)
    if pstyle is not None:
        style_id = pstyle.get(Q("val"))
        color = resolved_style_color(style_id, styles, default_color)
        if color:
            return color, f"paragraph-style:{style_id}"
    return default_color, "default"


def is_red(color: str | None) -> bool:
    if not color or color == "AUTO" or not re.fullmatch(r"[0-9A-F]{6}", color):
        return False
    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    return r >= 170 and r >= g * 1.45 and r >= b * 1.45 and g <= 130 and b <= 130


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: extract_red_content.py INPUT.docx OUTPUT_DIR", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(source) as archive:
        styles_root = None
        if "word/styles.xml" in archive.namelist():
            styles_root = ET.fromstring(archive.read("word/styles.xml"))
        styles, default_color = style_maps(styles_root)

        xml_parts = [
            name
            for name in archive.namelist()
            if name.startswith("word/")
            and name.endswith(".xml")
            and re.search(
                r"(?:document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$",
                name,
            )
        ]

        direct_colors = Counter()
        effective_colors = Counter()
        records = []
        paragraph_global_index = 0

        for part_name in xml_parts:
            root = ET.fromstring(archive.read(part_name))
            for local_index, paragraph in enumerate(root.iter(Q("p")), start=1):
                paragraph_global_index += 1
                full_text = node_text(paragraph)
                if not full_text.strip():
                    continue

                segments = []
                active_text: list[str] = []
                active_color = None
                active_source = None

                for run in paragraph.iter(Q("r")):
                    text = node_text(run)
                    if not text:
                        continue
                    direct = direct_run_color(run)
                    if direct:
                        direct_colors[direct] += len(text)
                    color, source_kind = effective_color(run, paragraph, styles, default_color)
                    if color:
                        effective_colors[color] += len(text)
                    if is_red(color):
                        if active_text and (color != active_color or source_kind != active_source):
                            segments.append(
                                {
                                    "text": "".join(active_text),
                                    "color": active_color,
                                    "color_source": active_source,
                                }
                            )
                            active_text = []
                        active_text.append(text)
                        active_color = color
                        active_source = source_kind
                    elif active_text:
                        segments.append(
                            {
                                "text": "".join(active_text),
                                "color": active_color,
                                "color_source": active_source,
                            }
                        )
                        active_text = []
                        active_color = None
                        active_source = None

                if active_text:
                    segments.append(
                        {
                            "text": "".join(active_text),
                            "color": active_color,
                            "color_source": active_source,
                        }
                    )

                if segments:
                    records.append(
                        {
                            "part": part_name,
                            "paragraph_global_index": paragraph_global_index,
                            "paragraph_part_index": local_index,
                            "full_text": full_text,
                            "red_segments": segments,
                        }
                    )

    result = {
        "source": str(source),
        "direct_colors_by_character_count": dict(direct_colors.most_common()),
        "effective_colors_by_character_count": dict(effective_colors.most_common()),
        "red_paragraph_count": len(records),
        "red_segment_count": sum(len(item["red_segments"]) for item in records),
        "records": records,
    }
    output_path = output_dir / "red_content.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({k: v for k, v in result.items() if k != "records"}, ensure_ascii=False, indent=2))
    for index, record in enumerate(records, start=1):
        red_text = " || ".join(segment["text"] for segment in record["red_segments"])
        print(f"\n[{index}] {record['part']} p{record['paragraph_part_index']}")
        print(f"RED: {red_text}")
        print(f"CTX: {record['full_text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
