from pathlib import Path
from zipfile import ZipFile

from lxml import etree


BASE = Path(r"F:\泉城实验室\二期\论文\异常检测\_docx_paragraph_comments_20260811")
SOURCE = BASE / "source_2026.8.4.docx"
WORD = BASE / "word_commented.docx"


with ZipFile(SOURCE) as source_zip, ZipFile(WORD) as word_zip:
    source_names = set(source_zip.namelist())
    word_names = set(word_zip.namelist())

    print("NEW_PARTS")
    for name in sorted(word_names - source_names):
        print(name)

    print("MISSING_PARTS")
    for name in sorted(source_names - word_names):
        print(name)

    print("CHANGED_PARTS")
    for name in sorted(source_names & word_names):
        if source_zip.read(name) != word_zip.read(name):
            print(name)

    for name in ("word/_rels/document.xml.rels", "[Content_Types].xml", "word/styles.xml"):
        print(f"\n### {name}")
        source_root = etree.fromstring(source_zip.read(name))
        word_root = etree.fromstring(word_zip.read(name))

        if name.endswith(".rels"):
            for element in word_root:
                rel_type = element.get("Type", "").lower()
                if "comment" in rel_type or "people" in rel_type:
                    print(etree.tostring(element, encoding="unicode"))
        elif name == "[Content_Types].xml":
            source_entries = {
                (element.tag, element.get("PartName"), element.get("Extension"), element.get("ContentType"))
                for element in source_root
            }
            for element in word_root:
                entry = (
                    element.tag,
                    element.get("PartName"),
                    element.get("Extension"),
                    element.get("ContentType"),
                )
                part_name = (element.get("PartName") or "").lower()
                if entry not in source_entries and ("comment" in part_name or "people" in part_name):
                    print(etree.tostring(element, encoding="unicode"))
        else:
            word_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            for style in word_root.findall(word_ns + "style"):
                style_id = style.get(word_ns + "styleId", "")
                if "Comment" in style_id:
                    print(style_id)
