from __future__ import annotations

import json
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
    )
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_pdf_qa.py input.pdf output_dir")

    pdf_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf = pdfium.PdfDocument(str(pdf_path))
    reader = PdfReader(str(pdf_path))
    page_texts = [(page.extract_text() or "") for page in reader.pages]

    captions: dict[str, list[int]] = {"图1": [], "图2": [], "图3": [], "图一": [], "图二": [], "图三": []}
    for index, text in enumerate(page_texts, start=1):
        for caption in captions:
            if caption in text:
                captions[caption].append(index)

    thumbnails: list[Image.Image] = []
    page_files: list[str] = []
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=1.35)
        image = bitmap.to_pil().convert("RGB")
        page_path = out_dir / f"page-{index + 1:02d}.png"
        image.save(page_path, optimize=True)
        page_files.append(str(page_path))

        thumb = image.copy()
        thumb.thumbnail((430, 610), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (454, 652), "white")
        tile.paste(thumb, ((454 - thumb.width) // 2, 28))
        draw = ImageDraw.Draw(tile)
        draw.text((14, 4), f"第{index + 1}页", fill="black", font=load_font(18))
        thumbnails.append(tile)

    columns = 4
    rows = (len(thumbnails) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 454, rows * 652), (225, 225, 225))
    for index, tile in enumerate(thumbnails):
        sheet.paste(tile, ((index % columns) * 454, (index // columns) * 652))
    sheet_path = out_dir / "contact-sheet.png"
    sheet.save(sheet_path, optimize=True)

    report = {
        "pdf": str(pdf_path),
        "page_count": len(pdf),
        "captions": captions,
        "contact_sheet": str(sheet_path),
        "page_files": page_files,
    }
    (out_dir / "render_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
