from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SOURCE = Path(
    r"F:\泉城实验室\二期\论文\异常检测\_docx_red_audit\output\rendered_lo_round3_final"
)
PAGES_PER_SHEET = 8
COLS = 4
THUMB_SIZE = (354, 500)
LABEL_HEIGHT = 34


def page_number(path: Path) -> int:
    return int(path.stem.split("-")[1])


pages = sorted(SOURCE.glob("page-*.png"), key=page_number)
font = ImageFont.load_default(size=20)

for start in range(0, len(pages), PAGES_PER_SHEET):
    batch = pages[start : start + PAGES_PER_SHEET]
    rows = (len(batch) + COLS - 1) // COLS
    sheet = Image.new(
        "RGB",
        (COLS * THUMB_SIZE[0], rows * (THUMB_SIZE[1] + LABEL_HEIGHT)),
        "white",
    )
    draw = ImageDraw.Draw(sheet)

    for index, path in enumerate(batch):
        image = Image.open(path).convert("RGB")
        image.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
        col = index % COLS
        row = index // COLS
        x = col * THUMB_SIZE[0] + (THUMB_SIZE[0] - image.width) // 2
        y = row * (THUMB_SIZE[1] + LABEL_HEIGHT) + LABEL_HEIGHT
        sheet.paste(image, (x, y))
        label = f"Page {page_number(path)}"
        draw.text((col * THUMB_SIZE[0] + 8, row * (THUMB_SIZE[1] + LABEL_HEIGHT) + 6), label, fill="black", font=font)

    first = page_number(batch[0])
    last = page_number(batch[-1])
    sheet.save(SOURCE / f"contact-{first:02d}-{last:02d}.png", optimize=True)
