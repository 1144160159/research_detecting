const fs = require("fs");
const path = require("path");
const pptxgen = require("../.pptx_build/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "综合分析");
const CHARTS = path.join(OUT, "图表");
const OUTPUT = path.join(OUT, "两个系统融合分析_面向AI驱动网络流量检测系统.pptx");

const pptx = new pptxgen();
pptx.author = "Codex";
pptx.company = "Quancheng Laboratory";
pptx.subject = "园区全流量采集分析系统与AI驱动网络流量检测系统融合分析";
pptx.title = "两个系统融合分析";
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
  ink: "101820",
  deep: "16222E",
  bg: "F6F8FA",
  panel: "FFFFFF",
  panel2: "EEF5F6",
  teal: "087E8B",
  teal2: "21A6A6",
  lime: "B7D12A",
  coral: "F06543",
  amber: "F5B841",
  violet: "6C63FF",
  blue: "2F6BFF",
  gray: "64748B",
  line: "D6E0E3",
  lightText: "DCE8EA",
};

function shape(type, opts) {
  return { type, opts };
}

function addBg(slide, dark = false) {
  slide.background = { color: dark ? C.ink : C.bg };
  if (!dark) {
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 0.18, h: H,
      fill: { color: C.teal }, line: { color: C.teal },
    });
  }
}

function addFooter(slide, idx, dark = false) {
  slide.addText("园区全流量采集分析系统 × AI驱动网络流量检测系统 | 融合分析", {
    x: 0.45, y: 7.12, w: 8.8, h: 0.18,
    fontFace: "Microsoft YaHei", fontSize: 8.5,
    color: dark ? "99B7BC" : C.gray, margin: 0,
  });
  slide.addText(String(idx).padStart(2, "0"), {
    x: 12.32, y: 7.05, w: 0.68, h: 0.22,
    fontFace: "Aptos", fontSize: 9, bold: true,
    color: dark ? "99B7BC" : C.gray, align: "right", margin: 0,
  });
}

function addTitle(slide, title, kicker = "") {
  if (kicker) {
    slide.addText(kicker, {
      x: 0.58, y: 0.32, w: 4.4, h: 0.25,
      fontFace: "Microsoft YaHei", fontSize: 10, color: C.teal,
      bold: true, margin: 0,
    });
  }
  slide.addText(title, {
    x: 0.58, y: 0.66, w: 11.9, h: 0.55,
    fontFace: "Microsoft YaHei", fontSize: 25, color: C.ink,
    bold: true, margin: 0, fit: "shrink",
  });
}

function card(slide, x, y, w, h, fill = C.panel, line = C.line) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.05,
    fill: { color: fill },
    line: { color: line, width: 0.8 },
    shadow: { type: "outer", color: "000000", opacity: 0.07, blur: 3, offset: 1, angle: 45 },
  });
}

function smallLabel(slide, text, x, y, w, fill = C.teal, color = "FFFFFF") {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.32, rectRadius: 0.06,
    fill: { color: fill }, line: { color: fill },
  });
  slide.addText(text, {
    x: x + 0.08, y: y + 0.075, w: w - 0.16, h: 0.12,
    fontFace: "Microsoft YaHei", fontSize: 8.5, bold: true,
    color, align: "center", margin: 0, fit: "shrink",
  });
}

function boxText(slide, title, body, x, y, w, h, accent = C.teal, opts = {}) {
  card(slide, x, y, w, h, opts.fill || C.panel, opts.line || C.line);
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w: 0.08, h,
    fill: { color: accent }, line: { color: accent },
  });
  const titleY = y + Math.min(0.18, h * 0.24);
  const bodyY = y + Math.min(0.55, h * 0.5);
  const bodyH = Math.max(0.12, h - (bodyY - y) - 0.08);
  slide.addText(title, {
    x: x + 0.22, y: titleY, w: w - 0.38, h: Math.min(0.26, Math.max(0.12, h * 0.38)),
    fontFace: "Microsoft YaHei", fontSize: opts.titleSize || 12.8,
    bold: true, color: opts.titleColor || C.ink, margin: 0,
  });
  slide.addText(body, {
    x: x + 0.22, y: bodyY, w: w - 0.38, h: bodyH,
    fontFace: "Microsoft YaHei", fontSize: opts.bodySize || 10.3,
    color: opts.bodyColor || C.gray, margin: 0.01, fit: "shrink",
    breakLine: false,
  });
}

function metric(slide, value, label, x, y, w, color = C.teal, dark = false) {
  slide.addText(String(value), {
    x, y, w, h: 0.54,
    fontFace: "Aptos Display", fontSize: 30, bold: true,
    color, margin: 0, fit: "shrink",
  });
  slide.addText(label, {
    x, y: y + 0.62, w, h: 0.28,
    fontFace: "Microsoft YaHei", fontSize: 9.8,
    color: dark ? C.lightText : C.gray, margin: 0, fit: "shrink",
  });
}

function arrow(slide, x, y, w, color = C.teal) {
  slide.addShape(pptx.ShapeType.line, {
    x, y, w, h: 0,
    line: { color, width: 1.4, beginArrowType: "none", endArrowType: "triangle" },
  });
}

function connector(slide, x1, y1, x2, y2, color = "9CA3AF") {
  const midX = (x1 + x2) / 2;
  slide.addShape(pptx.ShapeType.line, {
    x: Math.min(x1, midX), y: y1, w: Math.abs(midX - x1), h: 0,
    line: { color, width: 1.0, transparency: 12 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: midX, y: Math.min(y1, y2), w: 0, h: Math.abs(y2 - y1),
    line: { color, width: 1.0, transparency: 12 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: Math.min(midX, x2), y: y2, w: Math.abs(x2 - midX), h: 0,
    line: { color, width: 1.0, transparency: 12 },
  });
}

function addBullets(slide, items, x, y, w, h, fontSize = 11.2, color = C.ink) {
  const runs = [];
  items.forEach((item, i) => {
    runs.push({ text: item, options: { bullet: { indent: 13 }, breakLine: i < items.length - 1 } });
  });
  slide.addText(runs, {
    x, y, w, h,
    fontFace: "Microsoft YaHei", fontSize, color,
    margin: 0.02, fit: "shrink", paraSpaceAfterPt: 6,
  });
}

function addHeaderTag(slide, text, x, y, color = C.teal) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x, y, w: 0.38, h: 0.38,
    fill: { color }, line: { color },
  });
  slide.addText(text.slice(0, 1), {
    x, y: y + 0.095, w: 0.38, h: 0.1,
    fontFace: "Microsoft YaHei", fontSize: 9,
    bold: true, color: "FFFFFF", align: "center", margin: 0,
  });
  slide.addText(text, {
    x: x + 0.5, y: y + 0.05, w: 4.2, h: 0.24,
    fontFace: "Microsoft YaHei", fontSize: 11.2,
    bold: true, color: C.ink, margin: 0,
  });
}

function addChartImage(slide, file, x, y, w, h) {
  const p = path.join(CHARTS, file);
  if (fs.existsSync(p)) {
    slide.addImage({ path: p, x, y, w, h, sizing: { type: "contain", x, y, w, h } });
  } else {
    boxText(slide, file, "图表文件未找到", x, y, w, h, C.coral);
  }
}

let idx = 1;

// 1. Cover
{
  const s = pptx.addSlide();
  addBg(s, true);
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.ink }, line: { color: C.ink } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.lime }, line: { color: C.lime } });
  s.addShape(pptx.ShapeType.ellipse, { x: 8.55, y: 0.12, w: 4.7, h: 4.7, fill: { color: C.ink }, line: { color: C.teal2, transparency: 8, width: 2 } });
  s.addShape(pptx.ShapeType.ellipse, { x: 9.4, y: 0.72, w: 3.25, h: 3.25, fill: { color: C.ink }, line: { color: C.lime, transparency: 16, width: 2 } });
  s.addText("园区全流量采集分析系统 × AI驱动网络流量检测系统", {
    x: 0.8, y: 1.04, w: 8.8, h: 0.42,
    fontFace: "Microsoft YaHei", fontSize: 17, bold: true,
    color: C.lime, margin: 0, fit: "shrink",
  });
  s.addText("两个系统融合分析", {
    x: 0.78, y: 1.72, w: 8.2, h: 0.9,
    fontFace: "Microsoft YaHei", fontSize: 42, bold: true,
    color: "FFFFFF", margin: 0,
  });
  s.addText("从全流量底座到可信开放集检测、动态图少样本检测、MLOps反馈学习与验收证据闭环", {
    x: 0.82, y: 2.98, w: 9.2, h: 0.42,
    fontFace: "Microsoft YaHei", fontSize: 14.5,
    color: C.lightText, margin: 0, fit: "shrink",
  });
  metric(s, "858", "本地论文知识库", 0.82, 4.45, 1.55, C.lime, true);
  metric(s, "439", "强相关论文", 2.55, 4.45, 1.55, "FFFFFF", true);
  metric(s, "120", "已下载代码资源", 4.28, 4.45, 1.85, C.lime, true);
  metric(s, "15", "核心Kafka主题", 6.25, 4.45, 1.75, "FFFFFF", true);
  s.addText("结论先行：全流量系统不是并列平台，而是AI检测系统的数据底座、执行环境、证据平台和反馈闭环。", {
    x: 0.84, y: 6.48, w: 9.7, h: 0.34,
    fontFace: "Microsoft YaHei", fontSize: 12.5,
    color: "BFD7EA", margin: 0, fit: "shrink",
  });
  addFooter(s, idx++, true);
}

// 2. Executive thesis
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "核心判断：两个系统应融合成一个“数据-模型-证据-反馈”闭环", "EXECUTIVE THESIS");
  boxText(s, "园区全流量采集分析系统", "定位为工程底座：采集、协议解析、会话化、Kafka/Flink实时处理、ClickHouse/Nebula/MinIO证据存储、Web安全运营台。", 0.68, 1.55, 5.75, 1.58, C.teal);
  boxText(s, "AI驱动网络流量检测系统", "定位为智能能力层：表征学习、动态图少样本检测、可信开放集拒识、多源融合、可解释告警和持续学习。", 6.88, 1.55, 5.75, 1.58, C.violet);
  arrow(s, 6.42, 2.32, 0.42, C.ink);
  s.addShape(pptx.ShapeType.roundRect, {
    x: 1.2, y: 3.78, w: 10.9, h: 1.15, rectRadius: 0.08,
    fill: { color: C.ink }, line: { color: C.ink },
  });
  s.addText("融合后的系统定义", {
    x: 1.48, y: 4.02, w: 1.75, h: 0.2,
    fontFace: "Microsoft YaHei", fontSize: 11, bold: true,
    color: C.lime, margin: 0,
  });
  s.addText("以全流量遥测为底座，以AI模型和多源图关联为检测核心，以PCAP证据、告警研判、反馈学习和盲测验收为闭环的园区网络智能检测分析系统。", {
    x: 3.18, y: 3.95, w: 8.45, h: 0.34,
    fontFace: "Microsoft YaHei", fontSize: 14.5,
    color: "FFFFFF", margin: 0, fit: "shrink",
  });
  boxText(s, "不建议", "另起一套AI平台，重复采集、重复存储、重复告警；这会造成数据口径、证据链和验收材料分裂。", 0.72, 5.55, 5.62, 0.78, C.coral);
  boxText(s, "建议", "把DA-FDIDS、Evidence-OpenEMTD、图融合和级联检测做成现有平台的模型插件、评测包和专题能力。", 6.92, 5.55, 5.62, 0.78, C.teal);
  addFooter(s, idx++);
}

// 3. Current asset map
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "已有资产：工程系统主链路已成型，研究系统给出算法与评测路线", "ASSET MAP");
  const cols = [
    ["远程工程系统", "Probe、Kafka、Flink、ClickHouse、PostgreSQL、OpenSearch、NebulaGraph、Redis、MinIO、Go APIs、Web UI、MLOps。", C.teal],
    ["本地研究系统", "858篇论文地图、439篇强相关、120个代码资源、DA-FDIDS、Evidence-OpenEMTD、专利化方向。", C.violet],
    ["共同缺口", "检测质量冻结包、未知攻击召回、真实多源消融、高速链路预算、第三方签认与试点数据。", C.coral],
  ];
  cols.forEach((c, i) => {
    const x = 0.72 + i * 4.15;
    card(s, x, 1.55, 3.75, 4.65, C.panel);
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.22, y: 1.86, w: 0.62, h: 0.62, fill: { color: c[2] }, line: { color: c[2] } });
    s.addText(String(i + 1), { x: x + 0.22, y: 2.03, w: 0.62, h: 0.12, fontFace: "Aptos", fontSize: 13, bold: true, color: "FFFFFF", align: "center", margin: 0 });
    s.addText(c[0], { x: x + 0.98, y: 1.86, w: 2.45, h: 0.32, fontFace: "Microsoft YaHei", fontSize: 16, bold: true, color: C.ink, margin: 0 });
    s.addText(c[1], { x: x + 0.3, y: 2.7, w: 3.1, h: 1.55, fontFace: "Microsoft YaHei", fontSize: 12.2, color: C.gray, margin: 0.02, fit: "shrink" });
    const tagText = i === 0 ? "工程闭环" : i === 1 ? "科研供给" : "融合抓手";
    smallLabel(s, tagText, x + 0.3, 4.96, 1.25, c[2]);
  });
  s.addText("判断依据：工程侧已有真实链路、MLOps和证据目录；研究侧已把文献趋势压缩为可落地的模型与指标体系。", {
    x: 0.78, y: 6.62, w: 11.5, h: 0.24,
    fontFace: "Microsoft YaHei", fontSize: 11.2, color: C.gray, margin: 0,
  });
  addFooter(s, idx++);
}

// 4. Full traffic architecture
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "全流量系统主链路：AI能力应插入实时流处理和运营反馈之间", "ENGINEERING BACKBONE");
  const steps = [
    ["Probe", "AF_XDP/AF_PACKET\nPCAP归档\nDNS/DHCP/ARP"],
    ["Kafka", "flow.events.v1\nfeature.stat.v1\nmodel-updates"],
    ["Flink", "Session / Feature\nRule / Behavior\nCEP / Alert"],
    ["Storage", "ClickHouse\nNebulaGraph\nMinIO / OpenSearch"],
    ["Control", "Go APIs\nRule/Model Registry\nAudit/RBAC"],
    ["UI", "态势大屏\n告警研判\n取证/反馈"],
  ];
  steps.forEach((st, i) => {
    const x = 0.54 + i * 2.08;
    card(s, x, 2.05, 1.68, 2.2, i % 2 ? "F4FAFA" : C.panel);
    s.addText(st[0], { x: x + 0.16, y: 2.28, w: 1.35, h: 0.25, fontFace: "Aptos Display", fontSize: 15, bold: true, color: i === 2 ? C.coral : C.teal, align: "center", margin: 0 });
    s.addText(st[1], { x: x + 0.18, y: 2.86, w: 1.32, h: 0.82, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.gray, align: "center", margin: 0.01, fit: "shrink" });
    if (i < steps.length - 1) arrow(s, x + 1.72, 3.12, 0.28, C.gray);
  });
  boxText(s, "AI插入点 1：Flink在线推理", "消费 feature.stat.v1 / 特征批次，输出 detections.v1，满足低延迟和热更新。", 0.78, 5.18, 3.75, 0.88, C.coral);
  boxText(s, "AI插入点 2：MLOps训练评估", "从ClickHouse抽取特征和反馈，生成模型版本、阈值、指标和artifact。", 4.82, 5.18, 3.75, 0.88, C.violet);
  boxText(s, "AI插入点 3：证据解释层", "把不确定性、冲突度、原型距离、相似历史样本写入Evidence和告警详情。", 8.86, 5.18, 3.75, 0.88, C.teal);
  addFooter(s, idx++);
}

// 5. Research evidence
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "文献侧启示：系统路线应从单点精度转向持续运营架构", "RESEARCH SIGNAL");
  addChartImage(s, "创新点分布.png", 0.72, 1.45, 5.65, 4.45);
  addChartImage(s, "科学问题分布.png", 6.86, 1.45, 5.65, 4.45);
  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.92, y: 6.18, w: 11.35, h: 0.62, rectRadius: 0.05,
    fill: { color: C.ink }, line: { color: C.ink },
  });
  s.addText("组合趋势：Transformer/预训练解决表征，自监督解决标签稀缺，图学习解决关联，可解释与反馈解决安全运营闭环。", {
    x: 1.1, y: 6.38, w: 10.95, h: 0.18,
    fontFace: "Microsoft YaHei", fontSize: 12, bold: true,
    color: "FFFFFF", align: "center", margin: 0, fit: "shrink",
  });
  addFooter(s, idx++);
}

// 6. Fusion layer map
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "融合方式：不是系统拼接，而是分层嵌入", "LAYERED FUSION");
  const layers = [
    ["L0 数据底座", "Probe / Kafka / ClickHouse / MinIO", "提供真实流量、PCAP、会话、延迟和质量证据", C.teal],
    ["L1 特征底座", "FeatureStat / FeatureSeq / FeatureFingerprint", "支撑统计、序列、TLS/QUIC指纹和多粒度建模", C.blue],
    ["L2 检测模型", "DA-FDIDS / Evidence-OpenEMTD / 级联模型", "输出已知类、未知风险、低可信复核和模型版本", C.violet],
    ["L3 关联解释", "NebulaGraph / Evidence / PCAP / Threat Intel", "形成攻击链、相似样本、证据冲突和取证报告", C.coral],
    ["L4 运营闭环", "Feedback / Whitelist / MLOps / model-updates", "把TP/FP、未知候选和误报原因回流为模型迭代", C.amber],
  ];
  layers.forEach((l, i) => {
    const y = 1.38 + i * 1.05;
    s.addShape(pptx.ShapeType.rect, { x: 0.82 + i * 0.26, y, w: 11.35 - i * 0.52, h: 0.74, fill: { color: i % 2 ? "F4FAFA" : C.panel }, line: { color: C.line, width: 0.8 } });
    s.addShape(pptx.ShapeType.rect, { x: 0.82 + i * 0.26, y, w: 0.12, h: 0.74, fill: { color: l[3] }, line: { color: l[3] } });
    s.addText(l[0], { x: 1.05 + i * 0.26, y: y + 0.2, w: 1.6, h: 0.2, fontFace: "Microsoft YaHei", fontSize: 12.5, bold: true, color: l[3], margin: 0 });
    s.addText(l[1], { x: 2.72 + i * 0.26, y: y + 0.2, w: 3.65, h: 0.2, fontFace: "Aptos", fontSize: 11.5, bold: true, color: C.ink, margin: 0, fit: "shrink" });
    s.addText(l[2], { x: 6.72 + i * 0.26, y: y + 0.2, w: 4.35 - i * 0.26, h: 0.2, fontFace: "Microsoft YaHei", fontSize: 10.5, color: C.gray, margin: 0, fit: "shrink" });
  });
  boxText(s, "融合原则", "算法模块必须共享同一批特征、同一套模型版本、同一条证据链和同一个反馈闭环；否则验收指标和论文实验无法互证。", 0.9, 6.62, 11.55, 0.5, C.teal, { bodySize: 11.2 });
  addFooter(s, idx++);
}

// 7. Data contract
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "数据契约融合：现有特征已覆盖可信开放集检测的前三模态", "DATA CONTRACT");
  const mods = [
    ["FeatureStat", "持续时间、pps/bps、包长/IAT、TCP标志、上下行比例", "统计模态", C.teal],
    ["FeatureSeq", "包长序列hash、IAT序列hash、小波能量与熵、序列blob引用", "序列模态", C.blue],
    ["FeatureFingerprint", "TLS版本、JA3、SNI hash、证书sha256、payload熵", "协议指纹", C.violet],
    ["Graph Context", "IP/资产/域名/证书/告警/情报关系，来自NebulaGraph和Fusion", "图上下文", C.coral],
  ];
  mods.forEach((m, i) => {
    const x = 0.74 + (i % 2) * 6.05;
    const y = 1.52 + Math.floor(i / 2) * 2.15;
    boxText(s, m[0], m[1], x, y, 5.55, 1.45, m[3]);
    smallLabel(s, m[2], x + 3.85, y + 0.18, 1.22, m[3]);
  });
  s.addShape(pptx.ShapeType.roundRect, { x: 1.15, y: 6.0, w: 10.85, h: 0.55, rectRadius: 0.04, fill: { color: "EAF7F5" }, line: { color: "B6DFDA" } });
  s.addText("下一步契约扩展：在 Detection / Evidence 中显式加入 unknown_risk、uncertainty、conflict_score、prototype_distance、energy_score、candidate_cluster_id。", {
    x: 1.35, y: 6.18, w: 10.45, h: 0.16,
    fontFace: "Microsoft YaHei", fontSize: 10.8,
    color: C.ink, bold: true, align: "center", margin: 0, fit: "shrink",
  });
  addFooter(s, idx++);
}

// 8. Algorithm insertion
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "模型接入点：研究算法以插件形式进入 Flink 与 MLOps", "MODEL INSERTION");
  const left = [
    ["DA-FDIDS", "动态图少样本检测 + GRL/MMD域适应 + LoRA在线适配\n适合：跨域NIDS、少样本攻击、新环境快速适配"],
    ["Evidence-OpenEMTD", "多模态证据、不确定性、模态冲突、原型距离、能量分数\n适合：加密恶意流量、未知攻击、低可信复核"],
    ["Cascade Budget Detector", "L0快速统计 -> L1序列 -> L2指纹 -> L3图 -> L4深度模型\n适合：高速链路、资源约束、分层推理"],
  ];
  left.forEach((m, i) => {
    boxText(s, m[0], m[1], 0.7, 1.55 + i * 1.55, 5.65, 1.05, [C.violet, C.teal, C.coral][i], { bodySize: 9.7 });
  });
  const stages = [
    ["feature.stat.v1", "实时特征输入"],
    ["Flink Behavior Job", "异步推理 / 热更新"],
    ["detections.v1", "检测结果输出"],
    ["Alert + Evidence", "告警证据化"],
  ];
  stages.forEach((st, i) => {
    const x = 7.0;
    const y = 1.35 + i * 1.22;
    card(s, x, y, 4.6, 0.72, i === 1 ? "FFF7ED" : C.panel);
    s.addText(st[0], { x: x + 0.22, y: y + 0.13, w: 1.9, h: 0.18, fontFace: "Aptos", fontSize: 11.5, bold: true, color: i === 1 ? C.coral : C.teal, margin: 0 });
    s.addText(st[1], { x: x + 2.25, y: y + 0.13, w: 2.1, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 10.5, color: C.gray, margin: 0 });
    if (i < stages.length - 1) {
      s.addShape(pptx.ShapeType.line, { x: x + 2.3, y: y + 0.76, w: 0, h: 0.35, line: { color: C.gray, width: 1.2, beginArrowType: "none", endArrowType: "triangle" } });
    }
  });
  addFooter(s, idx++);
}

// 9. Closed loop
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "反馈学习闭环：从告警研判回到模型版本和在线热更新", "MLOPS LOOP");
  const nodes = [
    ["告警研判", 1.1, 1.65, C.coral],
    ["TP / FP反馈", 3.35, 1.65, C.amber],
    ["样本池", 5.55, 1.65, C.teal],
    ["训练评估", 7.55, 1.65, C.violet],
    ["模型注册", 9.65, 1.65, C.blue],
    ["model-updates", 5.45, 4.05, C.ink],
  ];
  nodes.forEach((n) => {
    s.addShape(pptx.ShapeType.roundRect, { x: n[1], y: n[2], w: 1.55, h: 0.72, rectRadius: 0.08, fill: { color: n[3] }, line: { color: n[3] } });
    s.addText(n[0], { x: n[1] + 0.08, y: n[2] + 0.25, w: 1.39, h: 0.12, fontFace: "Microsoft YaHei", fontSize: 10.2, bold: true, color: "FFFFFF", align: "center", margin: 0, fit: "shrink" });
  });
  for (let i = 0; i < 4; i++) arrow(s, nodes[i][1] + 1.62, 2.0, 0.62, C.gray);
  s.addShape(pptx.ShapeType.line, { x: 10.42, y: 2.39, w: 0, h: 1.26, line: { color: C.gray, width: 1.2 } });
  s.addShape(pptx.ShapeType.line, { x: 6.98, y: 3.65, w: 3.44, h: 0, line: { color: C.gray, width: 1.2 } });
  s.addShape(pptx.ShapeType.line, { x: 5.48, y: 3.65, w: 1.5, h: 0, line: { color: C.gray, width: 1.2, beginArrowType: "none", endArrowType: "triangle" } });
  s.addShape(pptx.ShapeType.line, { x: 1.95, y: 2.39, w: 0, h: 1.18, line: { color: C.gray, width: 1.2 } });
  s.addShape(pptx.ShapeType.line, { x: 1.95, y: 3.57, w: 3.38, h: 0, line: { color: C.gray, width: 1.2, beginArrowType: "none", endArrowType: "triangle" } });
  boxText(s, "闭环关键字段", "alert_id、model_version、feature_set_id、feedback_label、reason_code、threshold-lock、artifact_uri、metrics、activation action。", 0.78, 5.35, 5.62, 0.96, C.teal);
  boxText(s, "融合要求", "研究模型必须接入同一套模型注册、灰度激活、回滚、审计和Flink广播热更新机制，不能脱离平台单跑。", 6.92, 5.35, 5.62, 0.96, C.coral);
  addFooter(s, idx++);
}

// 10. Trusted open-set workflow
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "可信开放集检测：把“未知攻击”做成可复核风险，而不是低置信标签", "EVIDENCE-OPENEMTD");
  const formula = "unknown_risk = λ1·uncertainty + λ2·conflict + λ3·prototype_distance + λ4·energy + λ5·drift";
  s.addShape(pptx.ShapeType.roundRect, { x: 0.92, y: 1.45, w: 11.45, h: 0.62, rectRadius: 0.06, fill: { color: C.ink }, line: { color: C.ink } });
  s.addText(formula, { x: 1.1, y: 1.66, w: 11.1, h: 0.14, fontFace: "Aptos", fontSize: 16, bold: true, color: "FFFFFF", align: "center", margin: 0, fit: "shrink" });
  const pipeline = [
    ["多模态特征", "统计 / 序列 / 指纹 / 图"],
    ["证据意见", "belief / uncertainty"],
    ["冲突融合", "模态一致性与折扣"],
    ["风险分层", "known / review / unknown"],
    ["证据包", "相似样本 / 异常子图 / 复核建议"],
  ];
  pipeline.forEach((p, i) => {
    const x = 0.72 + i * 2.45;
    card(s, x, 3.02, 1.85, 1.38, C.panel);
    s.addText(p[0], { x: x + 0.12, y: 3.25, w: 1.6, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 12.2, bold: true, color: [C.teal, C.blue, C.violet, C.coral, C.amber][i], align: "center", margin: 0, fit: "shrink" });
    s.addText(p[1], { x: x + 0.16, y: 3.75, w: 1.52, h: 0.34, fontFace: "Microsoft YaHei", fontSize: 9.4, color: C.gray, align: "center", margin: 0, fit: "shrink" });
    if (i < pipeline.length - 1) arrow(s, x + 1.92, 3.7, 0.4, C.gray);
  });
  boxText(s, "产品落点", "告警详情页展示：未知风险、综合不确定性、模态冲突、最近已知原型、弱证据模态、建议复核动作。", 0.78, 5.38, 5.7, 0.92, C.teal);
  boxText(s, "论文落点", "模态缺失、模态污染、模态冲突、混合噪声标签、开放集留出、校准可信性和证据包复核实验。", 6.86, 5.38, 5.7, 0.92, C.violet);
  addFooter(s, idx++);
}

// 11. DA-FDIDS integration
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "DA-FDIDS 的正确融入方式：动态少样本与跨域适配插件", "DA-FDIDS");
  addHeaderTag(s, "适合做什么", 0.78, 1.5, C.teal);
  addBullets(s, [
    "动态图入侵检测：基于通信实体和流事件的时序关系建模。",
    "少样本攻击识别：support/query episode 适配新类别或小样本攻击。",
    "跨域泛化：GRL/MMD/Stable-LoRA 缓解园区、时间、协议和设备分布偏移。",
  ], 0.9, 2.0, 5.35, 1.35, 11.2);
  addHeaderTag(s, "不应夸大什么", 0.78, 4.05, C.coral);
  addBullets(s, [
    "不是完整全流量采集工程，不替代 Probe/Kafka/Flink。",
    "当前更接近闭集 few-shot episode 分类，不能直接等同开放集拒识。",
    "TrafficEncoder 若无真实预训练权重，不宜直接称为流量基础大模型。",
  ], 0.9, 4.55, 5.35, 1.25, 11.2);
  const modules = [
    ["B0", "DIDS-MFL"],
    ["B1", "TrafficEncoder"],
    ["B2", "LoRA"],
    ["B4", "GRL"],
    ["B5", "MMD"],
    ["B8", "Full DA-FDIDS"],
  ];
  modules.forEach((m, i) => {
    const y = 1.52 + i * 0.78;
    s.addShape(pptx.ShapeType.roundRect, { x: 7.05, y, w: 3.75, h: 0.42, rectRadius: 0.04, fill: { color: i === 5 ? C.ink : "F4FAFA" }, line: { color: i === 5 ? C.ink : C.line } });
    s.addText(m[0], { x: 7.22, y: y + 0.12, w: 0.45, h: 0.1, fontFace: "Aptos", fontSize: 9.5, bold: true, color: i === 5 ? C.lime : C.violet, margin: 0 });
    s.addText(m[1], { x: 7.82, y: y + 0.1, w: 2.65, h: 0.12, fontFace: "Microsoft YaHei", fontSize: 9.8, bold: true, color: i === 5 ? "FFFFFF" : C.ink, margin: 0, fit: "shrink" });
  });
  boxText(s, "实验门槛", "必须补 cross-domain、host-disjoint、time-disjoint、flow-disjoint 和 B0-B8 消融，否则容易被质疑为随机划分高分。", 6.9, 6.1, 4.2, 0.68, C.coral, { bodySize: 10.2 });
  addFooter(s, idx++);
}

// 12. Multi-source graph fusion
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "多源融合：把模型分数变成攻击上下文和误报消解能力", "GRAPH FUSION");
  const centerX = 6.35, centerY = 3.15;
  s.addShape(pptx.ShapeType.ellipse, { x: centerX - 0.8, y: centerY - 0.45, w: 1.6, h: 0.9, fill: { color: C.ink }, line: { color: C.ink } });
  s.addText("安全实体图", { x: centerX - 0.66, y: centerY - 0.13, w: 1.32, h: 0.12, fontFace: "Microsoft YaHei", fontSize: 11, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  const points = [
    ["Flow/Session", 1.0, 1.4, C.teal],
    ["Asset", 5.6, 1.05, C.blue],
    ["Device Log", 9.8, 1.45, C.violet],
    ["User Event", 10.1, 4.85, C.coral],
    ["Threat Intel", 5.6, 5.55, C.amber],
    ["Alert/Evidence", 1.0, 4.8, C.ink],
  ];
  points.forEach((p) => {
    s.addShape(pptx.ShapeType.roundRect, { x: p[1], y: p[2], w: 2.05, h: 0.6, rectRadius: 0.06, fill: { color: p[3] }, line: { color: p[3] } });
    s.addText(p[0], { x: p[1] + 0.12, y: p[2] + 0.2, w: 1.8, h: 0.1, fontFace: "Aptos", fontSize: 10.4, bold: true, color: "FFFFFF", align: "center", margin: 0, fit: "shrink" });
    connector(s, p[1] + 1.02, p[2] + 0.3, centerX, centerY);
  });
  boxText(s, "检测增益", "图上下文补齐单流模型看不到的资产重要性、账号行为、IOC命中、横向移动路径和历史相似告警。", 0.78, 6.35, 5.75, 0.58, C.teal, { bodySize: 10.6 });
  boxText(s, "科研切入", "做单源/多源消融：只流量 vs 流量+资产 vs 流量+日志+用户行为+情报，量化误报下降和提前量。", 6.88, 6.35, 5.75, 0.58, C.violet, { bodySize: 10.6 });
  addFooter(s, idx++);
}

// 13. High-speed cascade
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "高速全流量约束：用级联检测和预算调度兼顾吞吐与精度", "HIGH-SPEED PATH");
  const levels = [
    ["L0", "快速统计", "pps/bps、包长、IAT、端口、方向", C.teal],
    ["L1", "序列特征", "前N包长度/方向/时间间隔", C.blue],
    ["L2", "协议指纹", "TLS/QUIC、JA3、SNI、证书", C.violet],
    ["L3", "图关系", "通信邻域、资产、情报、历史告警", C.coral],
    ["L4", "深度证据", "开放集、原型、能量、不确定性", C.amber],
  ];
  levels.forEach((l, i) => {
    const x = 0.75 + i * 2.48;
    s.addShape(pptx.ShapeType.roundRect, { x, y: 2.15, w: 2.05, h: 1.18, rectRadius: 0.05, fill: { color: l[3] }, line: { color: l[3] } });
    s.addText(l[0], { x: x + 0.2, y: 2.36, w: 0.5, h: 0.18, fontFace: "Aptos", fontSize: 14, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(l[1], { x: x + 0.62, y: 2.34, w: 1.02, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 11, bold: true, color: "FFFFFF", margin: 0, fit: "shrink" });
    s.addText(l[2], { x: x + 0.25, y: 2.78, w: 1.35, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 8.2, color: "FFFFFF", margin: 0, fit: "shrink", align: "center" });
  });
  boxText(s, "预算调度规则", "队列长度、CPU/GPU负载、Flink backpressure、Kafka lag、初筛风险和不确定性共同决定是否升级到高成本特征。", 0.82, 4.55, 5.75, 0.95, C.teal);
  boxText(s, "验收价值", "将10×100Gbps/512Mpps能力从“所有流量跑深度模型”的不现实假设，改成可证明的线速筛查+疑似深检方案。", 6.85, 4.55, 5.75, 0.95, C.coral);
  addFooter(s, idx++);
}

// 14. Product/UI workflow
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "产品融合：AI检测结果要落在现有安全运营页面中", "PRODUCT WORKFLOW");
  const pages = [
    ["综合态势", "展示未知风险趋势、模型健康、证据完整度"],
    ["加密流量", "查看TLS/QUIC指纹、异常外联、开放集风险"],
    ["告警中心", "按known/review/unknown分层研判和反馈"],
    ["取证分析", "PCAP、Session、证据hash、相似样本"],
    ["模型管理", "版本、阈值、指标、激活、回滚"],
    ["MLOps编排", "标注、训练、盲测、注册、发布"],
  ];
  pages.forEach((p, i) => {
    const x = 0.74 + (i % 3) * 4.15;
    const y = 1.55 + Math.floor(i / 3) * 2.05;
    boxText(s, p[0], p[1], x, y, 3.65, 1.28, [C.teal, C.violet, C.coral, C.blue, C.amber, C.ink][i], { bodySize: 9.8 });
  });
  s.addShape(pptx.ShapeType.roundRect, { x: 0.95, y: 6.2, w: 11.28, h: 0.46, rectRadius: 0.04, fill: { color: "EAF7F5" }, line: { color: "B6DFDA" } });
  s.addText("页面原则：不新增孤立“AI演示页”，而是在告警、取证、图谱、模型和MLOps页面中呈现可操作、可审计、可反馈的AI结果。", {
    x: 1.15, y: 6.35, w: 10.9, h: 0.12,
    fontFace: "Microsoft YaHei", fontSize: 10.6,
    color: C.ink, bold: true, align: "center", margin: 0, fit: "shrink",
  });
  addFooter(s, idx++);
}

// 15. Acceptance matrix
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "验收融合：科研指标必须落到平台证据包和第三方盲测", "ACCEPTANCE");
  const rows = [
    ["功能主链路", "已较强", "Probe/Kafka/Flink/API/UI真实链路、PCAP下载、反馈、MLOps"],
    ["P95 <= 60s", "已闭环", "事件时间链、API/UI seen 时间、分段P95"],
    ["95%/5%", "未闭环", "需冻结样本、阈值锁、labels/predictions、第三方签认"],
    ["Unknown Recall", "未闭环", "开放集留出、未知攻击样本、OSCR/FPR@95TPR"],
    ["100G/512Mpps", "未闭环", "硬件窗口、流量profile、资源水位、丢包/Kafka lag"],
    ["多源融合价值", "结构门通过", "仍需真实消融、误报下降、MTTR下降、试点签认"],
  ];
  const table = [
    [
      { text: "门禁项", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
      { text: "状态", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
      { text: "融合后的证据要求", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
    ],
    ...rows.map((r) => [
      { text: r[0], options: { bold: true, color: C.ink } },
      { text: r[1], options: { color: r[1].includes("未") ? C.coral : C.teal, bold: true } },
      { text: r[2], options: { color: C.gray } },
    ]),
  ];
  s.addTable(table, {
    x: 0.72, y: 1.45, w: 11.86, h: 4.7,
    colW: [2.1, 1.45, 8.31],
    rowH: [0.45, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55],
    border: { pt: 0.6, color: C.line },
    margin: 0.08,
    fontFace: "Microsoft YaHei",
    fontSize: 9.2,
    valign: "mid",
    fit: "shrink",
  });
  boxText(s, "关键结论", "AI模型不能只报告训练集Accuracy；必须进入冻结盲测包，按Detection rate、FPR、Unknown recall、置信区间和第三方签认闭环。", 0.92, 6.42, 11.2, 0.5, C.coral, { bodySize: 10.5 });
  addFooter(s, idx++);
}

// 16. Roadmap
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "实施路线：先打通最小可信闭环，再扩展图融合与高速预算", "ROADMAP");
  const phases = [
    ["M1", "2周", "特征契约对齐", "确认FeatureStat/Seq/Fingerprint字段；设计Detection扩展与Evidence metrics_json。"],
    ["M2", "4周", "Evidence-OpenEMTD MVP", "三模态evidence、uncertainty、conflict、unknown_risk；离线盲测脚本。"],
    ["M3", "6-8周", "在线推理接入", "Flink消费feature.stat.v1；输出detections.v1；告警详情展示AI证据。"],
    ["M4", "8-12周", "MLOps闭环", "反馈样本池、阈值锁、模型注册、model-updates热更新、回滚。"],
    ["M5", "12周+", "扩展增强", "图模态、多源消融、高速级联预算、第三方盲测与试点报告。"],
  ];
  phases.forEach((p, i) => {
    const x = 0.68 + i * 2.52;
    s.addShape(pptx.ShapeType.roundRect, { x, y: 1.65, w: 2.05, h: 4.55, rectRadius: 0.05, fill: { color: i % 2 ? "F4FAFA" : C.panel }, line: { color: C.line } });
    s.addText(p[0], { x: x + 0.18, y: 1.93, w: 0.6, h: 0.22, fontFace: "Aptos Display", fontSize: 18, bold: true, color: [C.teal, C.blue, C.violet, C.coral, C.amber][i], margin: 0 });
    s.addText(p[1], { x: x + 1.02, y: 1.99, w: 0.76, h: 0.12, fontFace: "Microsoft YaHei", fontSize: 8.8, color: C.gray, margin: 0, align: "right" });
    s.addText(p[2], { x: x + 0.18, y: 2.58, w: 1.62, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.ink, margin: 0, fit: "shrink" });
    s.addText(p[3], { x: x + 0.18, y: 3.2, w: 1.62, h: 1.28, fontFace: "Microsoft YaHei", fontSize: 9.3, color: C.gray, margin: 0.01, fit: "shrink" });
  });
  addFooter(s, idx++);
}

// 17. Research and IP outputs
{
  const s = pptx.addSlide();
  addBg(s);
  addTitle(s, "融合后的科研与成果输出：论文、专利、软著、验收证据互相支撑", "OUTPUTS");
  const outputs = [
    ["论文方向 1", "Evidence-OpenEMTD：证据冲突感知的可信开放集多模态加密恶意流量检测。", C.violet],
    ["论文方向 2", "DA-FDIDS：域自适应基础表征增强的少样本动态网络入侵检测框架。", C.teal],
    ["专利方向", "可信开放集检测、多粒度预算调度、多源知识图谱置信融合、LLM证据包幻觉校验。", C.coral],
    ["工程证据", "盲测包、P95链路、模型热更新、PCAP证据、融合价值报告、第三方签认。", C.amber],
  ];
  outputs.forEach((o, i) => {
    const x = 0.78 + (i % 2) * 6.0;
    const y = 1.62 + Math.floor(i / 2) * 2.15;
    boxText(s, o[0], o[1], x, y, 5.55, 1.38, o[2], { bodySize: 10.6 });
  });
  s.addShape(pptx.ShapeType.roundRect, { x: 1.12, y: 6.15, w: 11.0, h: 0.5, rectRadius: 0.04, fill: { color: C.ink }, line: { color: C.ink } });
  s.addText("同一条真实链路同时支撑论文实验、专利实施例、系统演示和验收报告，避免科研与工程两张皮。", {
    x: 1.35, y: 6.32, w: 10.55, h: 0.12,
    fontFace: "Microsoft YaHei", fontSize: 11.2,
    bold: true, color: "FFFFFF", align: "center", margin: 0,
  });
  addFooter(s, idx++);
}

// 18. Risks and conclusion
{
  const s = pptx.addSlide();
  addBg(s, true);
  s.addText("结论与下一步", {
    x: 0.78, y: 0.72, w: 5.4, h: 0.52,
    fontFace: "Microsoft YaHei", fontSize: 30, bold: true,
    color: "FFFFFF", margin: 0,
  });
  const risks = [
    ["风险", "两个系统分裂建设，导致数据、模型、告警和证据口径不一致。"],
    ["控制", "算法以插件方式接入现有Feature、Detection、Evidence、MLOps和model-updates链路。"],
    ["优先", "先做三模态Evidence-OpenEMTD MVP和检测质量冻结包，再扩展图融合与高速预算。"],
  ];
  risks.forEach((r, i) => {
    const y = 1.75 + i * 1.25;
    s.addShape(pptx.ShapeType.roundRect, { x: 0.9, y, w: 11.2, h: 0.78, rectRadius: 0.05, fill: { color: i === 0 ? "2B1D1D" : "172D32" }, line: { color: i === 0 ? C.coral : C.teal } });
    smallLabel(s, r[0], 1.15, y + 0.23, 0.8, i === 0 ? C.coral : C.teal);
    s.addText(r[1], { x: 2.15, y: y + 0.23, w: 9.6, h: 0.16, fontFace: "Microsoft YaHei", fontSize: 13.5, bold: true, color: "FFFFFF", margin: 0, fit: "shrink" });
  });
  s.addText("最终目标：把全流量系统从“看得见、查得到”升级为“可检测、可解释、可学习、可验收”。", {
    x: 0.92, y: 6.16, w: 10.9, h: 0.35,
    fontFace: "Microsoft YaHei", fontSize: 18,
    bold: true, color: C.lime, align: "center", margin: 0, fit: "shrink",
  });
  addFooter(s, idx++, true);
}

pptx.writeFile({ fileName: OUTPUT })
  .then(() => {
    console.log(OUTPUT);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
