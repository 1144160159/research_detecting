from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).with_name("output") / "figure1_system_4k.png"
WIDTH, HEIGHT = 3840, 2160
FONT_PATH = Path(r"C:\Windows\Fonts\simhei.ttf")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


F_TITLE = font(58)
F_TITLE_MEDIUM = font(50)
F_TITLE_COMPACT = font(44)
F_ITEM = font(42)
F_SMALL = font(36)
F_GROUP = font(54)


BG = "#FBFCFD"
TEXT = "#16191D"
BLUE = "#527BA8"
BLUE_FILL = "#EEF4FA"
GREEN = "#64886A"
GREEN_FILL = "#F0F6F0"
ORANGE = "#A97A50"
ORANGE_FILL = "#FAF3EC"
GRAY = "#7A828A"
GRAY_FILL = "#F3F5F6"
LINE = "#456D9C"


img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)


def rounded_box(
    xy: tuple[int, int, int, int],
    fill: str,
    outline: str,
    radius: int = 22,
    width: int = 5,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered_text(
    xy: tuple[int, int, int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str = TEXT,
    spacing: int = 10,
) -> None:
    x1, y1, x2, y2 = xy
    bbox = draw.multiline_textbbox((0, 0), text, font=fnt, align="center", spacing=spacing)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(
        ((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2),
        text,
        font=fnt,
        fill=fill,
        align="center",
        spacing=spacing,
    )


def arrow(
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = LINE,
    width: int = 10,
    head: int = 28,
) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        points = [(x2, y2), (x2 - direction * head, y2 - head // 2), (x2 - direction * head, y2 + head // 2)]
    else:
        direction = 1 if y2 >= y1 else -1
        points = [(x2, y2), (x2 - head // 2, y2 - direction * head), (x2 + head // 2, y2 - direction * head)]
    draw.polygon(points, fill=color)


def poly_arrow(points: list[tuple[int, int]], color: str = LINE, width: int = 9) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    arrow(points[-2], points[-1], color=color, width=width, head=26)


def dashed_box(xy: tuple[int, int, int, int], color: str, width: int = 4, dash: int = 22) -> None:
    x1, y1, x2, y2 = xy
    for x in range(x1, x2, dash * 2):
        draw.line((x, y1, min(x + dash, x2), y1), fill=color, width=width)
        draw.line((x, y2, min(x + dash, x2), y2), fill=color, width=width)
    for y in range(y1, y2, dash * 2):
        draw.line((x1, y, x1, min(y + dash, y2)), fill=color, width=width)
        draw.line((x2, y, x2, min(y + dash, y2)), fill=color, width=width)


def module(
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    items: Iterable[str],
    outline: str,
    fill: str,
    item_font: ImageFont.FreeTypeFont = F_ITEM,
) -> tuple[int, int, int, int]:
    rounded_box((x, y, x + w, y + h), fill, outline, radius=24, width=5)
    header_h = 110
    draw.rounded_rectangle((x, y, x + w, y + header_h), radius=24, fill="#FFFFFF", outline=outline, width=5)
    draw.rectangle((x + 3, y + header_h - 24, x + w - 3, y + header_h + 3), fill="#FFFFFF")
    draw.line((x, y + header_h, x + w, y + header_h), fill=outline, width=4)
    if len(title) >= 7:
        title_font = F_TITLE_COMPACT
    elif len(title) >= 6:
        title_font = F_TITLE_MEDIUM
    else:
        title_font = F_TITLE
    centered_text((x + 12, y + 10, x + w - 12, y + header_h - 5), title, title_font)

    values = list(items)
    if values:
        gap = 16
        inner_top = y + header_h + 24
        inner_bottom = y + h - 24
        item_h = int((inner_bottom - inner_top - gap * (len(values) - 1)) / len(values))
        for index, value in enumerate(values):
            iy1 = inner_top + index * (item_h + gap)
            iy2 = iy1 + item_h
            draw.rounded_rectangle(
                (x + 22, iy1, x + w - 22, iy2),
                radius=14,
                fill="#FFFFFF",
                outline=outline,
                width=3,
            )
            centered_text((x + 32, iy1 + 5, x + w - 32, iy2 - 5), value, item_font)
    return (x, y, x + w, y + h)


top_y = 170
top_h = 720
module_w = 340
x_positions = [70, 485, 900, 1315, 1730, 2145, 2560, 2975, 3390]

boxes = []
boxes.append(module(x_positions[0], top_y, module_w, top_h, "流量接入", ["网络流量", "会话构造", "流索引 FID"], BLUE, BLUE_FILL))
boxes.append(module(x_positions[1], top_y, module_w, top_h, "特征抽取", ["包序列特征", "流统计特征", "协议可见特征", "历史上下文"], BLUE, BLUE_FILL))
boxes.append(module(x_positions[2], top_y, module_w, top_h, "恶意流量检测", ["轻量分类", "原型异常", "规则命中", "风险与不确定性"], BLUE, BLUE_FILL, F_SMALL))
boxes.append(module(x_positions[3], top_y, module_w, top_h, "告警标准化", ["告警索引 AID", "风险校准", "模型版本", "特征贡献"], BLUE, BLUE_FILL, F_SMALL))
boxes.append(module(x_positions[4], top_y, module_w, top_h, "结构化证据包", ["流量 / 模型证据", "环境 / 历史证据", "负证据", "编号与版本"], ORANGE, ORANGE_FILL, F_SMALL))
boxes.append(module(x_positions[5], top_y, module_w, top_h, "路径调度", ["覆盖率", "负证据压力", "预算约束", "选择处理路径"], ORANGE, ORANGE_FILL, F_SMALL))
boxes.append(module(x_positions[6], top_y, module_w, top_h, "受控生成", ["证据约束提示", "流量大模型", "关键结论命题化", "证据编号引用"], GREEN, GREEN_FILL, F_SMALL))
boxes.append(module(x_positions[7], top_y, module_w, top_h, "幻觉校验", ["结构 / 引用", "支持度 / IOC", "归因 / 一致性", "风险越界"], GREEN, GREEN_FILL, F_SMALL))
boxes.append(module(x_positions[8], top_y, 380, top_h, "可信输出", ["可信解释", "降级解释", "证据缺口"], GREEN, GREEN_FILL))

for left, right in zip(boxes, boxes[1:]):
    arrow((left[2] + 8, (left[1] + left[3]) // 2), (right[0] - 8, (right[1] + right[3]) // 2))


# Bottom-left: environment evidence is explicitly separated from detection input.
env = (90, 1110, 1320, 1710)
dashed_box(env, ORANGE)
centered_text((env[0], env[1] + 18, env[2], env[1] + 105), "环境证据与补证输入", F_GROUP)
env_items = [
    ("主机日志", 150, 1250),
    ("安全设备日志", 455, 1250),
    ("应用日志", 790, 1250),
    ("资产基线", 150, 1465),
    ("历史事件", 455, 1465),
    ("业务白名单", 790, 1465),
]
for label, x, y in env_items:
    rounded_box((x, y, x + 270, y + 150), "#FFFFFF", ORANGE, radius=18, width=4)
    centered_text((x + 10, y + 10, x + 260, y + 140), label, F_ITEM)


# Bottom-middle: deterministic evidence services.
services = (1410, 1110, 2560, 1710)
dashed_box(services, BLUE)
centered_text((services[0], services[1] + 18, services[2], services[1] + 105), "证据计算与索引服务", F_GROUP)
service_items = [
    ("证据存储与索引", 1470, 1250),
    ("证据排序与压缩", 1835, 1250),
    ("覆盖率计算", 1470, 1465),
    ("支持度与冲突", 1835, 1465),
]
for label, x, y in service_items:
    rounded_box((x, y, x + 320, y + 150), "#FFFFFF", BLUE, radius=18, width=4)
    centered_text((x + 10, y + 10, x + 310, y + 140), label, F_ITEM)


# Bottom-right: controlled feedback, no direct self-training from LLM output.
feedback = (2650, 1110, 3745, 1710)
dashed_box(feedback, GREEN)
centered_text((feedback[0], feedback[1] + 18, feedback[2], feedback[1] + 105), "受控反馈更新", F_GROUP)
feedback_items = [
    ("强校验通过样本", 2710, 1250),
    ("影子参数更新", 3075, 1250),
    ("固定验证集评估", 2710, 1465),
    ("发布与回滚", 3075, 1465),
]
for label, x, y in feedback_items:
    rounded_box((x, y, x + 320, y + 150), "#FFFFFF", GREEN, radius=18, width=4)
    centered_text((x + 10, y + 10, x + 310, y + 140), label, F_ITEM)


# Cross-layer arrows.
poly_arrow([(1165, 1110), (1165, 1010), (1900, 1010), (1900, 900)], color=ORANGE)
poly_arrow([(1985, 1110), (1985, 1030), (2315, 1030), (2315, 900)], color=BLUE)
poly_arrow([(3200, 1110), (3200, 1015), (3145, 1015), (3145, 900)], color=GREEN)
poly_arrow([(3500, 1710), (3500, 1940), (1080, 1940), (1080, 900)], color=GREEN)
poly_arrow([(3000, 1710), (3000, 1840), (2315, 1840), (2315, 900)], color=GREEN)


# Footer notes remain part of the diagram, with large readable text.
rounded_box((120, 1810, 1140, 2040), GRAY_FILL, GRAY, radius=20, width=4)
centered_text((145, 1830, 1115, 2020), "检测输入：仅网络流量\n环境数据：仅用于构包与补证", F_ITEM)
rounded_box((1370, 1810, 2470, 2040), GRAY_FILL, GRAY, radius=20, width=4)
centered_text((1395, 1830, 2445, 2020), "主链输出均绑定 AID、FID\n证据编号、模型及策略版本", F_ITEM)
rounded_box((2700, 1810, 3720, 2040), GRAY_FILL, GRAY, radius=20, width=4)
centered_text((2725, 1830, 3695, 2020), "反馈仅使用具有确认标签且\n通过全部强校验的样本", F_ITEM)


OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, format="PNG", optimize=True, dpi=(300, 300))
print(f"OUTPUT={OUT}")
print(f"SIZE={WIDTH}x{HEIGHT}")
