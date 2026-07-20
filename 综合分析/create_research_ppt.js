const fs = require("fs");
const path = require("path");
const pptxgen = require("../.pptx_build/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "综合分析");
const DATA = path.join(OUT, "_data", "papers_enriched.json");
const CHARTS = path.join(OUT, "图表");

const papers = JSON.parse(fs.readFileSync(DATA, "utf8"));
const PAPER_COUNT = papers.length;
const OUTPUT = path.join(OUT, `科研汇报PPT_${PAPER_COUNT}篇论文综合分析.pptx`);

function countBy(key) {
  const c = {};
  for (const p of papers) c[p[key]] = (c[p[key]] || 0) + 1;
  return c;
}

function countMulti(key) {
  const c = {};
  for (const p of papers) {
    for (const v of p[key] || []) c[v] = (c[v] || 0) + 1;
  }
  return c;
}

function topEntries(counter, n = 6) {
  return Object.entries(counter).sort((a, b) => b[1] - a[1]).slice(0, n);
}

const categoryCounts = countBy("category");
const relevanceCounts = countBy("relevance_tier");
const innovationCounts = countMulti("innovations");
const scienceCounts = countMulti("science_problems");
const codeCounts = countBy("code_status");
const strongPapers = papers.filter(p => p.relevance_tier === "强相关").length;
const midPapers = papers.filter(p => p.relevance_tier === "中相关").length;
const weakPapers = papers.filter(p => p.relevance_tier === "弱相关").length;
const downloadedCode = papers.filter(p => p.code_status === "已下载").length;

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Codex";
pptx.company = "Quancheng Laboratory";
pptx.subject = `${PAPER_COUNT}篇论文综合分析`;
pptx.title = `${PAPER_COUNT}篇异常检测与网络流量安全论文综合分析`;
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";

const W = 13.333;
const H = 7.5;
const C = {
  ink: "132023",
  bg: "F7FAF8",
  panel: "FFFFFF",
  teal: "087E8B",
  tealDark: "0B3954",
  mint: "BFD7EA",
  lime: "BFDB38",
  coral: "FF5A5F",
  gray: "667085",
  line: "D9E2E1",
};

function addBg(slide, dark = false) {
  slide.background = { color: dark ? C.ink : C.bg };
  if (!dark) {
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 0.16, h: H,
      fill: { color: C.teal }, line: { color: C.teal },
    });
  }
}

function addFooter(slide, idx) {
  slide.addText(`${PAPER_COUNT}篇论文综合分析 | AI驱动网络流量检测分析系统`, {
    x: 0.45, y: 7.12, w: 8.7, h: 0.18,
    fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.gray, margin: 0,
  });
  slide.addText(String(idx).padStart(2, "0"), {
    x: 12.43, y: 7.06, w: 0.5, h: 0.22,
    fontFace: "Aptos", fontSize: 9, color: C.gray, bold: true, margin: 0, align: "right",
  });
}

function addTitle(slide, title, kicker = "") {
  if (kicker) {
    slide.addText(kicker, {
      x: 0.6, y: 0.32, w: 4.4, h: 0.25,
      fontFace: "Microsoft YaHei", fontSize: 10, color: C.tealDark,
      bold: true, charSpacing: 1.2, margin: 0,
    });
  }
  slide.addText(title, {
    x: 0.6, y: 0.68, w: 11.8, h: 0.55,
    fontFace: "Microsoft YaHei", fontSize: 25, color: C.ink,
    bold: true, margin: 0, fit: "shrink",
  });
}

function card(slide, x, y, w, h, fill = C.panel) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.05,
    fill: { color: fill },
    line: { color: C.line, width: 0.8 },
    shadow: { type: "outer", color: "000000", opacity: 0.08, blur: 3, offset: 1, angle: 45 },
  });
}

function metric(slide, x, y, value, label, color = C.teal) {
  slide.addText(String(value), {
    x, y, w: 1.75, h: 0.62,
    fontFace: "Aptos Display", fontSize: 31, bold: true,
    color, margin: 0, fit: "shrink",
  });
  slide.addText(label, {
    x, y: y + 0.68, w: 2.0, h: 0.32,
    fontFace: "Microsoft YaHei", fontSize: 10.5, color: C.gray,
    margin: 0, fit: "shrink",
  });
}

function bulletList(slide, items, x, y, w, h, fontSize = 13.5, color = C.ink) {
  const runs = [];
  items.forEach((item, idx) => {
    runs.push({ text: item, options: { bullet: { indent: 13 }, breakLine: idx < items.length - 1 } });
  });
  slide.addText(runs, {
    x, y, w, h,
    fontFace: "Microsoft YaHei", fontSize, color,
    breakLine: false, fit: "shrink", paraSpaceAfterPt: 8,
    margin: 0.02,
  });
}

function img(slide, filename, x, y, w, h) {
  slide.addImage({
    path: path.join(CHARTS, filename),
    x, y, w, h,
    sizing: { type: "contain", x, y, w, h },
  });
}

function pill(slide, x, y, text, fill, color = "FFFFFF", w = 1.4) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.32,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: fill },
  });
  slide.addText(text, {
    x: x + 0.08, y: y + 0.07, w: w - 0.16, h: 0.12,
    fontFace: "Microsoft YaHei", fontSize: 8.5, bold: true,
    color, align: "center", margin: 0,
  });
}

function sectionNumber(slide, n, label) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 0.62, y: 1.55, w: 0.48, h: 0.48,
    fill: { color: C.teal }, line: { color: C.teal },
  });
  slide.addText(String(n), {
    x: 0.62, y: 1.67, w: 0.48, h: 0.12,
    fontFace: "Aptos", fontSize: 12, bold: true, color: "FFFFFF",
    align: "center", margin: 0,
  });
  slide.addText(label, {
    x: 1.22, y: 1.56, w: 3.8, h: 0.34,
    fontFace: "Microsoft YaHei", fontSize: 13, color: C.tealDark,
    bold: true, margin: 0,
  });
}

let s, idx = 2;

// 1 Cover
s = pptx.addSlide();
addBg(s, true);
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.ink }, line: { color: C.ink } });
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.lime }, line: { color: C.lime } });
s.addShape(pptx.ShapeType.arc, { x: 8.5, y: -0.2, w: 4.8, h: 4.8, line: { color: C.teal, transparency: 10, width: 2 }, adjustPoint: 0.25 });
s.addShape(pptx.ShapeType.arc, { x: 9.35, y: 0.72, w: 3.2, h: 3.2, line: { color: C.lime, transparency: 20, width: 2 }, adjustPoint: 0.3 });
s.addText(`${PAPER_COUNT}篇异常检测与网络流量安全论文`, {
  x: 0.8, y: 1.2, w: 7.4, h: 0.46,
  fontFace: "Microsoft YaHei", fontSize: 20, color: C.lime, bold: true, margin: 0,
});
s.addText("综合分析与科研汇报", {
  x: 0.78, y: 1.82, w: 8.2, h: 1.0,
  fontFace: "Microsoft YaHei", fontSize: 42, color: "FFFFFF", bold: true, margin: 0, fit: "shrink",
});
s.addText("大类归类 | 创新点 | 相关性 | 科学问题 | 逐篇中文解析 | 开源代码支撑", {
  x: 0.82, y: 3.08, w: 8.6, h: 0.38,
  fontFace: "Microsoft YaHei", fontSize: 15, color: "DDEEEA", margin: 0,
});
metric(s, 0.84, 4.45, String(PAPER_COUNT), "论文总数", C.lime);
metric(s, 2.72, 4.45, strongPapers, "强相关论文", "FFFFFF");
metric(s, 4.6, 4.45, downloadedCode, "已下载代码", C.lime);
s.addText("面向 AI驱动网络流量检测分析系统 的文献地图", {
  x: 0.84, y: 6.64, w: 7.4, h: 0.28,
  fontFace: "Microsoft YaHei", fontSize: 11.5, color: "BFD7EA", margin: 0,
});

// 2 Method
s = pptx.addSlide();
addBg(s);
addTitle(s, "分析流程：从PDF语料到系统知识地图", "WORKFLOW");
sectionNumber(s, 1, "自动化处理链路");
const steps = [
  ["文献元数据", "解析 文献.md\n编号、题名、年份、DOI、PDF路径"],
  ["PDF抽取", "pdftotext 抽取前3页\n摘要、关键词、方法缩写"],
  ["多标签归类", "大类、创新点、科学问题\n相关性与代码状态"],
  ["交付输出", "Markdown / CSV / JSON / 图表\n科研汇报PPT"],
];
steps.forEach((st, i) => {
  const x = 0.85 + i * 3.05;
  card(s, x, 2.25, 2.58, 2.1);
  pill(s, x + 0.22, 2.48, `0${i + 1}`, i % 2 ? C.tealDark : C.teal, "FFFFFF", 0.62);
  s.addText(st[0], { x: x + 0.25, y: 2.94, w: 2.0, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 15, bold: true, color: C.ink, margin: 0 });
  s.addText(st[1], { x: x + 0.25, y: 3.38, w: 2.05, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 10.8, color: C.gray, margin: 0, fit: "shrink" });
  if (i < steps.length - 1) {
    s.addShape(pptx.ShapeType.line, { x: x + 2.7, y: 3.28, w: 0.55, h: 0, line: { color: C.teal, width: 2, beginArrowType: "none", endArrowType: "triangle" } });
  }
});
s.addText("分类结果用于快速定位“直接可用技术池、可迁移方法池、背景综述池”，并与开源代码索引打通。", {
  x: 1.0, y: 5.25, w: 11.2, h: 0.45, fontFace: "Microsoft YaHei", fontSize: 15, color: C.tealDark, bold: true, align: "center", margin: 0,
});
addFooter(s, idx++);

// 3 Executive metrics
s = pptx.addSlide();
addBg(s);
addTitle(s, "总体画像：强相关论文接近半数，代码资源具备复现基础", "EXECUTIVE SNAPSHOT");
const metricData = [
  [String(PAPER_COUNT), "论文总量", C.teal],
  [strongPapers, "强相关", C.coral],
  [midPapers, "中相关", C.tealDark],
  [weakPapers, "弱相关", C.gray],
  [downloadedCode, "已下载代码", C.lime],
];
metricData.forEach((m, i) => {
  const x = 0.72 + i * 2.52;
  card(s, x, 1.65, 2.08, 1.62);
  metric(s, x + 0.28, 1.92, m[0], m[1], m[2]);
});
card(s, 0.78, 4.05, 5.75, 1.5, "F2F8F8");
card(s, 6.78, 4.05, 5.75, 1.5, "F8FBF0");
bulletList(s, [
  "主线集中在加密流量分类、网络异常/入侵检测和恶意流量检测",
  "图学习、预训练、自监督、联邦协同是高频方法族",
  "代码仓库已形成可复现实验的初始资源池",
], 1.1, 4.38, 5.0, 0.78, 11.5);
bulletList(s, [
  "后续综述不宜平均用力，应按强/中/弱相关分层精读",
  "系统建设应优先复现强相关且代码已下载的论文",
  "弱相关论文更适合作为背景、理论或跨域方法引用",
], 7.1, 4.38, 5.0, 0.78, 11.5);
addFooter(s, idx++);

// 4 Category distribution
s = pptx.addSlide();
addBg(s);
addTitle(s, "大类归类：流量安全与异常检测构成主体", "CATEGORY MAP");
img(s, "大类归类统计.png", 0.65, 1.35, 7.0, 5.25);
card(s, 8.0, 1.55, 4.55, 4.75);
s.addText("主导方向", { x: 8.35, y: 1.9, w: 3.7, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 16, bold: true, color: C.ink, margin: 0 });
bulletList(s, topEntries(categoryCounts, 5).map(([k, v]) => `${k}: ${v}篇`), 8.35, 2.42, 3.85, 1.7, 12);
s.addShape(pptx.ShapeType.rect, { x: 8.35, y: 4.68, w: 3.8, h: 0.03, fill: { color: C.line }, line: { color: C.line } });
s.addText("解读", { x: 8.35, y: 4.92, w: 3.7, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.tealDark, margin: 0 });
s.addText("语料不是单纯异常检测集合，而是覆盖“加密流量识别、入侵检测、恶意流量、跨域异常检测、图与知识图谱”的复合知识库。", {
  x: 8.35, y: 5.25, w: 3.75, h: 0.7, fontFace: "Microsoft YaHei", fontSize: 11, color: C.gray, margin: 0, fit: "shrink",
});
addFooter(s, idx++);

// 5 Year trend
s = pptx.addSlide();
addBg(s);
addTitle(s, "时间趋势：近年研究明显转向预训练、图学习和真实场景部署", "TREND");
img(s, "年度趋势.png", 0.7, 1.35, 7.6, 4.65);
card(s, 8.65, 1.55, 3.9, 4.45, "F9FBF7");
bulletList(s, [
  "早期文献提供密码协议、网络监测和流量分类基础",
  "2018年后加密流量、IoT安全和深度学习方法快速增长",
  "2023年后出现更多开放集、联邦、可解释、在线检测与工程部署研究",
], 9.0, 2.0, 3.15, 1.65, 12);
s.addText("趋势判断", { x: 9.0, y: 4.45, w: 2.9, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 14, color: C.tealDark, bold: true, margin: 0 });
s.addText("系统路线应从“单点模型精度”升级为“数据-模型-解释-更新”的持续运营架构。", {
  x: 9.0, y: 4.82, w: 3.1, h: 0.6, fontFace: "Microsoft YaHei", fontSize: 12, color: C.ink, bold: true, margin: 0,
});
addFooter(s, idx++);

// 6 Innovation
s = pptx.addSlide();
addBg(s);
addTitle(s, "创新点归类：预训练、自监督、图学习与融合建模是方法核心", "INNOVATION");
img(s, "创新点分布.png", 0.65, 1.25, 7.15, 5.35);
const invTop = topEntries(innovationCounts, 4);
invTop.forEach(([name, value], i) => {
  const x = 8.1 + (i % 2) * 2.25;
  const y = 1.58 + Math.floor(i / 2) * 1.72;
  card(s, x, y, 2.05, 1.25, i % 2 ? "F8FBF0" : "F2F8F8");
  s.addText(String(value), { x: x + 0.18, y: y + 0.18, w: 1.0, h: 0.38, fontFace: "Aptos Display", fontSize: 23, bold: true, color: i % 2 ? C.tealDark : C.teal, margin: 0 });
  s.addText(name, { x: x + 0.18, y: y + 0.62, w: 1.65, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9.2, color: C.ink, bold: true, fit: "shrink", margin: 0 });
});
card(s, 8.12, 5.08, 4.32, 0.86, "FFFFFF");
s.addText("组合趋势：Transformer/预训练解决表征，自监督解决标签稀缺，图学习解决关联，解释模块解决安全运营闭环。", {
  x: 8.42, y: 5.32, w: 3.78, h: 0.34, fontFace: "Microsoft YaHei", fontSize: 10.5, color: C.gray, margin: 0, fit: "shrink",
});
addFooter(s, idx++);

// 7 Science problems
s = pptx.addSlide();
addBg(s);
addTitle(s, "科学问题：真实网络的难点不是单一精度，而是多约束协同", "SCIENTIFIC QUESTIONS");
img(s, "科学问题分布.png", 0.65, 1.25, 7.05, 5.4);
card(s, 8.08, 1.45, 4.45, 4.95, "F2F8F8");
s.addText("可凝练为四个核心问题", { x: 8.42, y: 1.82, w: 3.8, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 15, bold: true, color: C.ink, margin: 0 });
bulletList(s, [
  "加密不可解密条件下的稳定表征学习",
  "标签稀缺、漂移和未知攻击下的持续检测",
  "多源异构流量/日志/图谱的统一建模",
  "高速链路约束下的可解释、低误报在线运营",
], 8.45, 2.42, 3.65, 1.6, 12);
s.addShape(pptx.ShapeType.rect, { x: 8.42, y: 4.65, w: 3.7, h: 0.03, fill: { color: "CCE3E1" }, line: { color: "CCE3E1" } });
s.addText("研究落点", { x: 8.42, y: 4.9, w: 3.5, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.tealDark, margin: 0 });
s.addText("把模型问题转化为“可观测、可训练、可解释、可更新、可部署”的系统科学问题。", {
  x: 8.42, y: 5.24, w: 3.55, h: 0.58, fontFace: "Microsoft YaHei", fontSize: 11.2, color: C.ink, bold: true, margin: 0,
});
addFooter(s, idx++);

// 8 Relevance
s = pptx.addSlide();
addBg(s);
addTitle(s, "论文相关性：强相关论文是项目技术路线的主矿脉", "RELEVANCE");
img(s, "相关性分布.png", 0.8, 1.42, 5.25, 4.55);
card(s, 6.55, 1.42, 5.95, 4.58);
metric(s, 7.0, 1.9, strongPapers, "强相关：直接支撑流量检测", C.coral);
metric(s, 9.15, 1.9, midPapers, "中相关：方法可迁移", C.teal);
metric(s, 11.05, 1.9, weakPapers, "弱相关：背景/跨域参考", C.gray);
s.addShape(pptx.ShapeType.rect, { x: 7.0, y: 3.35, w: 4.92, h: 0.03, fill: { color: C.line }, line: { color: C.line } });
bulletList(s, [
  "优先精读强相关论文，形成模型与实验基线",
  "中相关论文用于补充图学习、时序、联邦、解释模块",
  "弱相关论文用于综述背景和跨域异常检测方法借鉴",
], 7.0, 3.75, 4.75, 1.2, 12);
addFooter(s, idx++);

// 9 Code
s = pptx.addSlide();
addBg(s);
addTitle(s, "开源代码：已形成可复现实验的初始资源池", "CODE ASSETS");
img(s, "代码状态分布.png", 0.8, 1.38, 5.2, 4.55);
card(s, 6.5, 1.38, 5.95, 4.65, "F9FBF7");
s.addText("复现优先级", { x: 6.9, y: 1.85, w: 3.8, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 16, color: C.ink, bold: true, margin: 0 });
bulletList(s, [
  "第一批：强相关 + 已下载代码 + 数据处理链路清晰",
  "第二批：强相关但代码缺失，复现模型结构与指标",
  "第三批：中相关方法模块，作为系统组件候选",
  "第四批：综述/数据集/工具类，补充评测与引用",
], 6.9, 2.42, 4.95, 1.65, 12);
s.addText("建议把 `source/` 仓库与 `论文分析总表.csv` 编号绑定，形成可检索的复现实验台账。", {
  x: 6.9, y: 5.05, w: 4.95, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 11.5, color: C.tealDark, bold: true, margin: 0,
});
addFooter(s, idx++);

// 10 Cluster map
s = pptx.addSlide();
addBg(s);
addTitle(s, "技术簇：从流量识别到安全运营闭环", "CLUSTER MAP");
const clusters = [
  ["加密流量识别", "字节/包/流序列\n应用/网站/代理识别", C.teal],
  ["恶意流量检测", "暗网、隧道、DDoS\n恶意加密通信", C.coral],
  ["入侵异常检测", "NIDS、未知攻击\n低误报告警", C.tealDark],
  ["图与情报融合", "通信图、知识图谱\n威胁溯源", "6C5CE7"],
  ["在线与边缘部署", "实时、轻量、漂移\n持续学习", "2F9E44"],
];
clusters.forEach((c, i) => {
  const x = 0.85 + (i % 3) * 4.05;
  const y = i < 3 ? 1.65 : 4.08;
  card(s, x, y, 3.35, 1.55, "FFFFFF");
  s.addShape(pptx.ShapeType.ellipse, { x: x + 0.25, y: y + 0.35, w: 0.62, h: 0.62, fill: { color: c[2] }, line: { color: c[2] } });
  s.addText(String(i + 1), { x: x + 0.25, y: y + 0.51, w: 0.62, h: 0.12, fontFace: "Aptos", fontSize: 12, color: "FFFFFF", bold: true, align: "center", margin: 0 });
  s.addText(c[0], { x: x + 1.05, y: y + 0.28, w: 1.95, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 15, color: C.ink, bold: true, margin: 0 });
  s.addText(c[1], { x: x + 1.05, y: y + 0.72, w: 1.95, h: 0.48, fontFace: "Microsoft YaHei", fontSize: 10.8, color: C.gray, margin: 0, fit: "shrink" });
});
s.addShape(pptx.ShapeType.line, { x: 2.52, y: 3.32, w: 7.75, h: 0, line: { color: C.line, width: 1.5, dash: "dash" } });
s.addText("系统化组合：流量观测 -> 表征学习 -> 检测分类 -> 关联溯源 -> 解释更新", {
  x: 2.1, y: 6.25, w: 9.2, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 15, color: C.tealDark, bold: true, align: "center", margin: 0,
});
addFooter(s, idx++);

// 11 Architecture
s = pptx.addSlide();
addBg(s);
addTitle(s, "建议系统架构：分层检测 + 图关联 + 解释更新", "SYSTEM BLUEPRINT");
const arch = [
  ["数据接入", "PCAP / NetFlow / 日志 / 情报"],
  ["特征与表征", "统计特征 / 字节序列 / 流序列 / 图结构"],
  ["检测模型", "轻量筛查 / Transformer / GNN / 自监督"],
  ["分析解释", "原型样本 / 规则抽取 / 攻击链上下文"],
  ["持续运营", "漂移监控 / 人工反馈 / 模型更新"],
];
arch.forEach((a, i) => {
  const x = 0.7 + i * 2.52;
  card(s, x, 2.05, 2.18, 1.62, i % 2 ? "F9FBF7" : "F2F8F8");
  s.addText(a[0], { x: x + 0.22, y: 2.36, w: 1.6, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 14.5, color: C.ink, bold: true, align: "center", margin: 0 });
  s.addText(a[1], { x: x + 0.18, y: 2.86, w: 1.72, h: 0.45, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.gray, align: "center", margin: 0, fit: "shrink" });
  if (i < arch.length - 1) {
    s.addShape(pptx.ShapeType.line, { x: x + 2.28, y: 2.86, w: 0.4, h: 0, line: { color: C.teal, width: 2, endArrowType: "triangle" } });
  }
});
card(s, 1.15, 4.65, 11.0, 1.05);
s.addText("关键设计原则", { x: 1.55, y: 4.95, w: 1.8, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.tealDark, margin: 0 });
bulletList(s, [
  "先轻量过滤再深度研判，兼顾吞吐与精度",
  "用图层承接跨流、跨主机、跨告警关联",
  "解释与反馈必须内置，形成可运营闭环",
], 3.45, 4.87, 7.95, 0.45, 10.5);
addFooter(s, idx++);

// 12 Priority plan
s = pptx.addSlide();
addBg(s);
addTitle(s, "复现与精读路线：先打穿强相关闭环", "ACTION PLAN");
const plans = [
  ["第1阶段", "强相关+代码已下载", "复现数据处理、模型训练、指标脚本"],
  ["第2阶段", "加密流量与IDS基线", "建立统一 benchmark 和对比表"],
  ["第3阶段", "图学习/解释/漂移模块", "形成系统增强插件池"],
  ["第4阶段", "真实流量试验", "在线推理、误报分析、人工反馈"],
];
plans.forEach((p, i) => {
  const y = 1.55 + i * 1.22;
  s.addShape(pptx.ShapeType.ellipse, { x: 0.95, y: y + 0.05, w: 0.42, h: 0.42, fill: { color: i === 0 ? C.coral : C.teal }, line: { color: i === 0 ? C.coral : C.teal } });
  s.addText(String(i + 1), { x: 0.95, y: y + 0.16, w: 0.42, h: 0.1, fontFace: "Aptos", fontSize: 10, color: "FFFFFF", bold: true, align: "center", margin: 0 });
  card(s, 1.6, y, 10.65, 0.82, i % 2 ? "F9FBF7" : "FFFFFF");
  s.addText(p[0], { x: 1.95, y: y + 0.18, w: 1.3, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 12.5, bold: true, color: C.tealDark, margin: 0 });
  s.addText(p[1], { x: 3.45, y: y + 0.18, w: 2.4, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 12.5, bold: true, color: C.ink, margin: 0 });
  s.addText(p[2], { x: 6.1, y: y + 0.18, w: 5.6, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 11.5, color: C.gray, margin: 0, fit: "shrink" });
});
s.addText("目标：把文献综述、代码复现、系统原型和科研问题凝练连接起来。", {
  x: 1.55, y: 6.58, w: 10.5, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 15, color: C.tealDark, bold: true, align: "center", margin: 0,
});
addFooter(s, idx++);

// 13 Research questions
s = pptx.addSlide();
addBg(s);
addTitle(s, "可写入课题/论文的科学问题表达", "RESEARCH QUESTIONS");
const questions = [
  "加密不可解密、标签稀缺且流量分布持续变化时，如何学习稳定可迁移的流量表征？",
  "如何融合包/流时序、主机通信图、日志告警与威胁情报，形成统一检测与溯源模型？",
  "高速链路和边缘约束下，如何实现低延迟、低误报、可解释的在线异常检测？",
  "面对未知攻击、规避攻击、概念漂移和数据污染，如何评估并提升模型可信度？",
];
questions.forEach((q, i) => {
  const x = 0.9 + (i % 2) * 6.0;
  const y = 1.65 + Math.floor(i / 2) * 2.1;
  card(s, x, y, 5.35, 1.45, i % 2 ? "F8FBF0" : "F2F8F8");
  pill(s, x + 0.25, y + 0.24, `RQ${i + 1}`, i % 2 ? C.tealDark : C.teal, "FFFFFF", 0.72);
  s.addText(q, { x: x + 0.25, y: y + 0.72, w: 4.75, h: 0.42, fontFace: "Microsoft YaHei", fontSize: 12.2, bold: true, color: C.ink, margin: 0, fit: "shrink" });
});
s.addText("这些问题可以分别对应：表征学习、多源融合、系统部署、鲁棒可信四条研究线。", {
  x: 1.1, y: 6.38, w: 11.0, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 14, color: C.tealDark, bold: true, align: "center", margin: 0,
});
addFooter(s, idx++);

// 14 Closing
s = pptx.addSlide();
addBg(s, true);
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.ink }, line: { color: C.ink } });
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.lime }, line: { color: C.lime } });
s.addText("结论", { x: 0.82, y: 0.95, w: 2.0, h: 0.38, fontFace: "Microsoft YaHei", fontSize: 18, color: C.lime, bold: true, margin: 0 });
s.addText(`${PAPER_COUNT}篇论文已经转化为可检索、可统计、可汇报的研究地图`, {
  x: 0.82, y: 1.55, w: 9.3, h: 0.8, fontFace: "Microsoft YaHei", fontSize: 31, color: "FFFFFF", bold: true, margin: 0, fit: "shrink",
});
card(s, 0.88, 3.1, 11.5, 2.1, "FFFFFF");
bulletList(s, [
  "强相关论文支撑系统主体技术路线，中相关论文补充方法模块，弱相关论文服务背景与综述。",
  "优先推进“强相关 + 已下载代码”的复现实验，形成 benchmark 和系统组件库。",
  "最终目标不是堆模型，而是形成可观测、可解释、可更新、可部署的安全分析系统。",
], 1.25, 3.48, 10.7, 1.0, 14, C.ink);
s.addText("输出目录：综合分析/", { x: 0.92, y: 6.45, w: 4.5, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 12, color: "BFD7EA", margin: 0 });

pptx.writeFile({ fileName: OUTPUT });
