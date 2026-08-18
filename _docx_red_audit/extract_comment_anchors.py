from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def visible_text(node: ET.Element) -> str:
    parts: list[str] = []
    for item in node.iter():
        if item.tag == W + "t" and item.text:
            parts.append(item.text)
        elif item.tag == W + "tab":
            parts.append("\t")
        elif item.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def run_marks(run: ET.Element) -> tuple[bool, bool]:
    properties = run.find(W + "rPr")
    if properties is None:
        return False, False
    color = properties.find(W + "color")
    color_value = color.get(W + "val", "").upper() if color is not None else ""
    is_red = color_value in {"EE0000", "FF0000", "RED"}
    highlight = properties.find(W + "highlight")
    highlight_value = (
        highlight.get(W + "val", "").upper() if highlight is not None else ""
    )
    is_yellow = highlight_value == "YELLOW"
    return is_red, is_yellow


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: extract_comment_anchors.py INPUT.docx OUTPUT.json")

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    with zipfile.ZipFile(source) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        comments = ET.fromstring(archive.read("word/comments.xml"))

    comment_text = {
        item.get(W + "id", ""): visible_text(item)
        for item in comments.iter(W + "comment")
    }

    records: list[dict[str, object]] = []
    paragraph_index = -1
    heading = ""
    active: dict[str, dict[str, object]] = {}

    for paragraph in document.iter(W + "p"):
        paragraph_index += 1
        full_text = visible_text(paragraph)
        style = paragraph.find("./" + W + "pPr/" + W + "pStyle")
        style_id = style.get(W + "val", "") if style is not None else ""
        if style_id.lower().startswith(("heading", "a")) and full_text.strip():
            if len(full_text.strip()) <= 80:
                heading = full_text.strip()

        paragraph_ids: set[str] = set()
        for item in paragraph.iter():
            if item.tag == W + "commentRangeStart":
                comment_id = item.get(W + "id", "")
                active.setdefault(
                    comment_id,
                    {"parts": [], "red_parts": [], "yellow_parts": []},
                )
                paragraph_ids.add(comment_id)
            elif item.tag == W + "r":
                text = visible_text(item)
                if text:
                    is_red, is_yellow = run_marks(item)
                    for state in active.values():
                        state["parts"].append(text)
                        if is_red:
                            state["red_parts"].append(text)
                        if is_yellow:
                            state["yellow_parts"].append(text)
            elif item.tag == W + "commentRangeEnd":
                comment_id = item.get(W + "id", "")
                state = active.pop(
                    comment_id,
                    {"parts": [], "red_parts": [], "yellow_parts": []},
                )
                paragraph_ids.add(comment_id)
                records.append(
                    {
                        "comment_id": comment_id,
                        "paragraph_index": paragraph_index,
                        "heading": heading,
                        "paragraph_text": full_text,
                        "anchor_text": "".join(state["parts"]),
                        "red_anchor_text": "".join(state["red_parts"]),
                        "yellow_anchor_text": "".join(state["yellow_parts"]),
                        "comment_text": comment_text.get(comment_id, ""),
                    }
                )

        # Zero-width or malformed ranges may use a reference without a range.
        for ref in paragraph.iter(W + "commentReference"):
            comment_id = ref.get(W + "id", "")
            if comment_id not in paragraph_ids and not any(
                record["comment_id"] == comment_id for record in records
            ):
                records.append(
                    {
                        "comment_id": comment_id,
                        "paragraph_index": paragraph_index,
                        "heading": heading,
                        "paragraph_text": full_text,
                        "anchor_text": "",
                        "red_anchor_text": "",
                        "yellow_anchor_text": "",
                        "comment_text": comment_text.get(comment_id, ""),
                    }
                )

    present = {str(record["comment_id"]) for record in records}
    for comment_id, text in comment_text.items():
        if comment_id not in present:
            records.append(
                {
                    "comment_id": comment_id,
                    "paragraph_index": None,
                    "heading": "",
                    "paragraph_text": "",
                    "anchor_text": "",
                    "red_anchor_text": "",
                    "yellow_anchor_text": "",
                    "comment_text": text,
                }
            )

    records.sort(
        key=lambda item: (
            item["paragraph_index"] is None,
            item["paragraph_index"] if item["paragraph_index"] is not None else 10**9,
            int(str(item["comment_id"])) if str(item["comment_id"]).isdigit() else 10**9,
        )
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "source": str(source),
                "comment_count": len(comment_text),
                "anchor_record_count": len(records),
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
