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
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};

const W = 13.333;
const H = 7.5;
const C = {
  ink: "111827",
  deep: "17212B",
  bg: "F6F8FA",
  panel: "FFFFFF",
  panel2: "ECF5F4",
  teal: "087E8B",
  blue: "2F6BFF",
  violet: "6557D2",
  coral: "E85D3D",
  amber: "D89614",
  lime: "B7D12A",
  gray: "5F6B7A",
  line: "D8E1E5",
  muted: "DCE8EA",
};

function bg(slide, dark = false) {
  slide.background = { color: dark ? C.ink : C.bg };
  if (!dark) {
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 0.16, h: H,
      fill: { color: C.teal }, line: { color: C.teal },
    });
  }
}

function footer(slide, n, dark = false) {
  slide.addText("园区全流量采集分析系统 × AI驱动网络流量检测系统 | 融合分析", {
    x: 0.46, y: 7.12, w: 8.8, h: 0.18,
    fontFace: "Microsoft YaHei", fontSize: 8.5,
    color: dark ? "A9BDC2" : C.gray, margin: 0,
  });
  slide.addText(String(n).padStart(2, "0"), {
    x: 12.25, y: 7.05, w: 0.75, h: 0.2,
    fontFace: "Aptos", fontSize: 9, bold: true,
    color: dark ? "A9BDC2" : C.gray, margin: 0, align: "right",
  });
}

function title(slide, t, k = "") {
  if (k) {
    slide.addText(k, {
      x: 0.58, y: 0.32, w: 4.5, h: 0.22,
      fontFace: "Microsoft YaHei", fontSize: 10,
      color: C.teal, bold: true, margin: 0,
    });
  }
  slide.addText(t, {
    x: 0.58, y: 0.66, w: 12.0, h: 0.55,
    fontFace: "Microsoft YaHei", fontSize: 25,
    color: C.ink, bold: true, margin: 0, fit: "shrink",
  });
}

function card(slide, x, y, w, h, accent, head, body, opts = {}) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color: opts.fill || C.panel },
    line: { color: opts.line || C.line, width: 0.7 },
  });
  if (accent) {
    slide.addShape(pptx.ShapeType.rect, {
      x, y, w: 0.08, h,
      fill: { color: accent }, line: { color: accent },
    });
  }
  slide.addText(head, {
    x: x + 0.22, y: y + 0.18, w: w - 0.36, h: 0.24,
    fontFace: "Microsoft YaHei", fontSize: opts.headSize || 12.4,
    bold: true, color: opts.headColor || C.ink, margin: 0, fit: "shrink",
  });
  slide.addText(body, {
    x: x + 0.22, y: y + 0.55, w: w - 0.36, h: Math.max(0.18, h - 0.68),
    fontFace: "Microsoft YaHei", fontSize: opts.bodySize || 10.3,
    color: opts.bodyColor || C.gray, margin: 0.02, fit: "shrink",
  });
}

function label(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h: 0.28,
    fill: { color }, line: { color },
  });
  slide.addText(text, {
    x: x + 0.08, y: y + 0.075, w: w - 0.16, h: 0.1,
    fontFace: "Microsoft YaHei", fontSize: 8.2, bold: true,
    color: "FFFFFF", align: "center", margin: 0, fit: "shrink",
  });
}

function metric(slide, v, l, x, y, w, color, dark = false) {
  slide.addText(String(v), {
    x, y, w, h: 0.55,
    fontFace: "Aptos Display", fontSize: 30,
    bold: true, color, margin: 0, fit: "shrink",
  });
  slide.addText(l, {
    x, y: y + 0.63, w, h: 0.25,
    fontFace: "Microsoft YaHei", fontSize: 9.6,
    color: dark ? C.muted : C.gray, margin: 0, fit: "shrink",
  });
}

function bullets(slide, items, x, y, w, h, size = 11.1) {
  const runs = items.map((text, i) => ({
    text,
    options: { bullet: { indent: 13 }, breakLine: i < items.length - 1 },
  }));
  slide.addText(runs, {
    x, y, w, h,
    fontFace: "Microsoft YaHei", fontSize: size,
    color: C.ink, margin: 0.02, fit: "shrink", paraSpaceAfterPt: 6,
  });
}

function bar(slide, x, y, w, h, color) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color }, line: { color },
  });
}

function chart(slide, file, x, y, w, h) {
  const p = path.join(CHARTS, file);
  if (fs.existsSync(p)) {
    slide.addImage({ path: p, x, y, w, h, sizing: { type: "contain", x, y, w, h } });
  } else {
    card(slide, x, y, w, h, C.coral, file, "图表文件未找到");
  }
}

let n = 1;

// 1
{
  const s = pptx.addSlide();
  bg(s, true);
  bar(s, 0, 0, 0.22, H, C.lime);
  bar(s, 8.9, 0.0, 4.45, H, C.deep);
  bar(s, 9.25, 0.0, 0.08, H, C.teal);
  s.addText("园区全流量采集分析系统 × AI驱动网络流量检测系统", {
    x: 0.82, y: 1.05, w: 8.1, h: 0.35,
    fontFace: "Microsoft YaHei", fontSize: 16.5,
    bold: true, color: C.lime, margin: 0, fit: "shrink",
  });
  s.addText("两个系统融合分析", {
    x: 0.8, y: 1.75, w: 7.6, h: 0.88,
    fontFace: "Microsoft YaHei", fontSize: 42,
    bold: true, color: "FFFFFF", margin: 0,
  });
  s.addText("从全流量底座到可信开放集检测、动态图少样本检测、MLOps反馈学习与验收证据闭环", {
    x: 0.84, y: 3.0, w: 8.1, h: 0.36,
    fontFace: "Microsoft YaHei", fontSize: 13.5,
    color: C.muted, margin: 0, fit: "shrink",
  });
  metric(s, "858", "论文知识库", 0.85, 4.45, 1.3, C.lime, true);
  metric(s, "439", "强相关论文", 2.45, 4.45, 1.45, "FFFFFF", true);
  metric(s, "120", "已下载代码", 4.18, 4.45, 1.55, C.lime, true);
  metric(s, "15", "核心Kafka主题", 5.96, 4.45, 1.6, "FFFFFF", true);
  s.addText("结论先行：全流量系统不是并列平台，而是AI检测系统的数据底座、执行环境、证据平台和反馈闭环。", {
    x: 0.85, y: 6.45, w: 8.6, h: 0.32,
    fontFace: "Microsoft YaHei", fontSize: 11.8,
    color: "BFD7EA", margin: 0, fit: "shrink",
  });
  footer(s, n++, true);
}

// 2
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "核心判断：融合成一个“数据-模型-证据-反馈”闭环", "EXECUTIVE THESIS");
  card(s, 0.72, 1.55, 5.65, 1.55, C.teal, "园区全流量采集分析系统", "工程底座：采集、协议解析、会话化、Kafka/Flink实时处理、ClickHouse/Nebula/MinIO证据存储、Web安全运营台。");
  card(s, 6.9, 1.55, 5.65, 1.55, C.violet, "AI驱动网络流量检测系统", "智能能力层：表征学习、动态图少样本检测、可信开放集拒识、多源融合、可解释告警和持续学习。");
  bar(s, 6.42, 2.25, 0.34, 0.08, C.gray);
  card(s, 1.0, 3.65, 11.25, 1.0, C.lime, "融合后定义", "以全流量遥测为底座，以AI模型和多源图关联为检测核心，以PCAP证据、告警研判、反馈学习和盲测验收为闭环的园区网络智能检测分析系统。", { fill: C.ink, headColor: C.lime, bodyColor: "FFFFFF", headSize: 12.2, bodySize: 13.2 });
  card(s, 0.72, 5.45, 5.65, 0.8, C.coral, "不建议", "另起一套AI平台，重复采集、重复存储、重复告警，造成数据口径、证据链和验收材料分裂。", { bodySize: 9.8 });
  card(s, 6.9, 5.45, 5.65, 0.8, C.teal, "建议", "把DA-FDIDS、Evidence-OpenEMTD、图融合和级联检测做成现有平台的模型插件、评测包和专题能力。", { bodySize: 9.8 });
  footer(s, n++);
}

// 3
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "已有资产：工程系统主链路已成型，研究系统提供算法与评测路线", "ASSET MAP");
  const cols = [
    ["远程工程系统", "Probe、Kafka、Flink、ClickHouse、PostgreSQL、OpenSearch、NebulaGraph、Redis、MinIO、Go APIs、Web UI、MLOps。", C.teal, "工程闭环"],
    ["本地研究系统", "858篇论文地图、439篇强相关、120个代码资源、DA-FDIDS、Evidence-OpenEMTD、专利化方向。", C.violet, "科研供给"],
    ["共同缺口", "检测质量冻结包、未知攻击召回、真实多源消融、高速链路预算、第三方签认与试点数据。", C.coral, "融合抓手"],
  ];
  cols.forEach((c, i) => {
    const x = 0.74 + i * 4.12;
    card(s, x, 1.55, 3.65, 4.35, c[2], c[0], c[1], { bodySize: 11.2 });
    label(s, c[3], x + 0.24, 5.18, 1.15, c[2]);
  });
  card(s, 0.92, 6.32, 11.2, 0.46, C.teal, "判断依据", "工程侧已有真实链路、MLOps和证据目录；研究侧已把文献趋势压缩为可落地的模型与指标体系。", { bodySize: 10.4 });
  footer(s, n++);
}

// 4
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "全流量系统主链路：AI能力插入实时流处理和运营反馈之间", "ENGINEERING BACKBONE");
  const steps = [
    ["Probe", "AF_XDP/AF_PACKET\nPCAP归档\nDNS/DHCP/ARP"],
    ["Kafka", "flow.events.v1\nfeature.stat.v1\nmodel-updates"],
    ["Flink", "Session / Feature\nRule / Behavior\nCEP / Alert"],
    ["Storage", "ClickHouse\nNebulaGraph\nMinIO / OpenSearch"],
    ["Control", "Go APIs\nRule/Model Registry\nAudit/RBAC"],
    ["UI", "态势大屏\n告警研判\n取证/反馈"],
  ];
  steps.forEach((st, i) => {
    const x = 0.55 + i * 2.08;
    card(s, x, 2.02, 1.68, 2.05, i === 2 ? C.coral : C.teal, st[0], st[1], { headSize: 13.2, bodySize: 8.8, fill: i % 2 ? C.panel2 : C.panel });
    if (i < steps.length - 1) bar(s, x + 1.78, 3.02, 0.26, 0.08, C.gray);
  });
  card(s, 0.78, 5.15, 3.75, 0.92, C.coral, "插入点 1：Flink在线推理", "消费 feature.stat.v1 / 特征批次，输出 detections.v1，满足低延迟和热更新。", { bodySize: 9.4 });
  card(s, 4.82, 5.15, 3.75, 0.92, C.violet, "插入点 2：MLOps训练评估", "从ClickHouse抽取特征和反馈，生成模型版本、阈值、指标和artifact。", { bodySize: 9.4 });
  card(s, 8.86, 5.15, 3.75, 0.92, C.teal, "插入点 3：证据解释层", "把不确定性、冲突度、原型距离、相似历史样本写入Evidence和告警详情。", { bodySize: 9.4 });
  footer(s, n++);
}

// 5
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "文献侧启示：系统路线应从单点精度转向持续运营架构", "RESEARCH SIGNAL");
  chart(s, "创新点分布.png", 0.72, 1.45, 5.65, 4.45);
  chart(s, "科学问题分布.png", 6.86, 1.45, 5.65, 4.45);
  card(s, 0.92, 6.18, 11.35, 0.58, C.lime, "组合趋势", "Transformer/预训练解决表征，自监督解决标签稀缺，图学习解决关联，可解释与反馈解决安全运营闭环。", { fill: C.ink, headColor: C.lime, bodyColor: "FFFFFF", bodySize: 11.2 });
  footer(s, n++);
}

// 6
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "融合方式：不是系统拼接，而是分层嵌入", "LAYERED FUSION");
  const layers = [
    ["L0 数据底座", "Probe / Kafka / ClickHouse / MinIO", "提供真实流量、PCAP、会话、延迟和质量证据", C.teal],
    ["L1 特征底座", "FeatureStat / FeatureSeq / FeatureFingerprint", "支撑统计、序列、TLS/QUIC指纹和多粒度建模", C.blue],
    ["L2 检测模型", "DA-FDIDS / Evidence-OpenEMTD / 级联模型", "输出已知类、未知风险、低可信复核和模型版本", C.violet],
    ["L3 关联解释", "NebulaGraph / Evidence / PCAP / Threat Intel", "形成攻击链、相似样本、证据冲突和取证报告", C.coral],
    ["L4 运营闭环", "Feedback / Whitelist / MLOps / model-updates", "把TP/FP、未知候选和误报原因回流为模型迭代", C.amber],
  ];
  layers.forEach((l, i) => {
    const y = 1.45 + i * 1.0;
    const x = 0.82 + i * 0.22;
    s.addShape(pptx.ShapeType.rect, { x, y, w: 11.5 - i * 0.44, h: 0.72, fill: { color: i % 2 ? C.panel2 : C.panel }, line: { color: C.line } });
    bar(s, x, y, 0.1, 0.72, l[3]);
    s.addText(l[0], { x: x + 0.25, y: y + 0.22, w: 1.45, h: 0.16, fontFace: "Microsoft YaHei", fontSize: 11.5, bold: true, color: l[3], margin: 0 });
    s.addText(l[1], { x: x + 1.95, y: y + 0.22, w: 3.55, h: 0.16, fontFace: "Aptos", fontSize: 10.8, bold: true, color: C.ink, margin: 0, fit: "shrink" });
    s.addText(l[2], { x: x + 5.85, y: y + 0.22, w: 4.9 - i * 0.18, h: 0.16, fontFace: "Microsoft YaHei", fontSize: 9.6, color: C.gray, margin: 0, fit: "shrink" });
  });
  card(s, 0.92, 6.55, 11.2, 0.48, C.teal, "融合原则", "算法模块必须共享同一批特征、同一套模型版本、同一条证据链和同一个反馈闭环。", { bodySize: 10.4 });
  footer(s, n++);
}

// 7
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "数据契约融合：现有特征已覆盖可信开放集检测的前三模态", "DATA CONTRACT");
  const mods = [
    ["FeatureStat", "持续时间、pps/bps、包长/IAT、TCP标志、上下行比例", "统计模态", C.teal],
    ["FeatureSeq", "包长序列hash、IAT序列hash、小波能量与熵、序列blob引用", "序列模态", C.blue],
    ["FeatureFingerprint", "TLS版本、JA3、SNI hash、证书sha256、payload熵", "协议指纹", C.violet],
    ["Graph Context", "IP/资产/域名/证书/告警/情报关系，来自NebulaGraph和Fusion", "图上下文", C.coral],
  ];
  mods.forEach((m, i) => {
    const x = 0.74 + (i % 2) * 6.05;
    const y = 1.52 + Math.floor(i / 2) * 2.15;
    card(s, x, y, 5.55, 1.45, m[3], m[0], m[1]);
    label(s, m[2], x + 3.86, y + 0.18, 1.18, m[3]);
  });
  card(s, 0.92, 6.05, 11.2, 0.62, C.coral, "下一步契约扩展", "在 Detection / Evidence 中显式加入 unknown_risk、uncertainty、conflict_score、prototype_distance、energy_score、candidate_cluster_id。", { bodySize: 10.3 });
  footer(s, n++);
}

// 8
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "模型接入点：研究算法以插件形式进入 Flink 与 MLOps", "MODEL INSERTION");
  const models = [
    ["DA-FDIDS", "动态图少样本检测 + GRL/MMD域适应 + LoRA在线适配。\n适合：跨域NIDS、少样本攻击、新环境快速适配。", C.violet],
    ["Evidence-OpenEMTD", "多模态证据、不确定性、模态冲突、原型距离、能量分数。\n适合：加密恶意流量、未知攻击、低可信复核。", C.teal],
    ["Cascade Budget Detector", "L0快速统计 -> L1序列 -> L2指纹 -> L3图 -> L4深度模型。\n适合：高速链路、资源约束、分层推理。", C.coral],
  ];
  models.forEach((m, i) => card(s, 0.75, 1.48 + i * 1.55, 5.7, 1.05, m[2], m[0], m[1], { bodySize: 9.5 }));
  const flow = [
    ["feature.stat.v1", "实时特征输入"],
    ["Flink Behavior Job", "异步推理 / 热更新"],
    ["detections.v1", "检测结果输出"],
    ["Alert + Evidence", "告警证据化"],
  ];
  flow.forEach((f, i) => {
    const y = 1.42 + i * 1.16;
    card(s, 7.05, y, 4.35, 0.65, i === 1 ? C.coral : C.teal, f[0], f[1], { bodySize: 8.8, headSize: 10.5, fill: i === 1 ? "FFF5ED" : C.panel });
    if (i < flow.length - 1) bar(s, 9.18, y + 0.75, 0.08, 0.28, C.gray);
  });
  footer(s, n++);
}

// 9
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "反馈学习闭环：从告警研判回到模型版本和在线热更新", "MLOPS LOOP");
  const nodes = [
    ["告警研判", C.coral],
    ["TP/FP反馈", C.amber],
    ["样本池", C.teal],
    ["训练评估", C.violet],
    ["模型注册", C.blue],
    ["model-updates", C.ink],
  ];
  nodes.slice(0, 5).forEach((node, i) => {
    const x = 0.9 + i * 2.35;
    s.addShape(pptx.ShapeType.rect, { x, y: 2.05, w: 1.7, h: 0.68, fill: { color: node[1] }, line: { color: node[1] } });
    s.addText(node[0], { x: x + 0.08, y: 2.28, w: 1.54, h: 0.1, fontFace: "Microsoft YaHei", fontSize: 10.2, bold: true, color: "FFFFFF", align: "center", margin: 0, fit: "shrink" });
    if (i < 4) bar(s, x + 1.82, 2.35, 0.42, 0.08, C.gray);
  });
  s.addShape(pptx.ShapeType.rect, { x: 5.55, y: 4.05, w: 2.1, h: 0.72, fill: { color: C.ink }, line: { color: C.ink } });
  s.addText("model-updates", { x: 5.68, y: 4.31, w: 1.84, h: 0.1, fontFace: "Aptos", fontSize: 10.5, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  bar(s, 10.55, 2.74, 0.08, 0.55, C.gray);
  bar(s, 6.6, 3.29, 4.03, 0.08, C.gray);
  bar(s, 6.6, 3.37, 0.08, 0.58, C.gray);
  card(s, 0.78, 5.55, 5.62, 0.86, C.teal, "闭环关键字段", "alert_id、model_version、feature_set_id、feedback_label、reason_code、threshold-lock、artifact_uri、metrics、activation action。", { bodySize: 9.5 });
  card(s, 6.92, 5.55, 5.62, 0.86, C.coral, "融合要求", "研究模型必须接入同一套模型注册、灰度激活、回滚、审计和Flink广播热更新机制。", { bodySize: 9.5 });
  footer(s, n++);
}

// 10
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "可信开放集检测：把“未知攻击”做成可复核风险", "EVIDENCE-OPENEMTD");
  s.addShape(pptx.ShapeType.rect, {
    x: 0.95, y: 1.45, w: 11.4, h: 0.72,
    fill: { color: C.ink }, line: { color: C.ink },
  });
  bar(s, 0.95, 1.45, 0.08, 0.72, C.lime);
  s.addText("Unknown risk", {
    x: 1.2, y: 1.64, w: 1.55, h: 0.16,
    fontFace: "Aptos", fontSize: 14, bold: true,
    color: C.lime, margin: 0,
  });
  s.addText("unknown_risk = λ1·uncertainty + λ2·conflict + λ3·prototype_distance + λ4·energy + λ5·drift", {
    x: 3.05, y: 1.65, w: 8.85, h: 0.15,
    fontFace: "Aptos", fontSize: 13.2, bold: true,
    color: "FFFFFF", margin: 0, fit: "shrink",
  });
  const pipe = [
    ["多模态特征", "统计 / 序列 / 指纹 / 图", C.teal],
    ["证据意见", "belief / uncertainty", C.blue],
    ["冲突融合", "模态一致性与折扣", C.violet],
    ["风险分层", "known / review / unknown", C.coral],
    ["证据包", "相似样本 / 异常子图 / 复核建议", C.amber],
  ];
  pipe.forEach((p, i) => {
    const x = 0.72 + i * 2.48;
    card(s, x, 3.0, 1.85, 1.25, p[2], p[0], p[1], { bodySize: 8.5, headSize: 10.5 });
    if (i < pipe.length - 1) bar(s, x + 1.95, 3.6, 0.35, 0.08, C.gray);
  });
  card(s, 0.78, 5.38, 5.7, 0.92, C.teal, "产品落点", "告警详情页展示：未知风险、综合不确定性、模态冲突、最近已知原型、弱证据模态、建议复核动作。", { bodySize: 9.6 });
  card(s, 6.86, 5.38, 5.7, 0.92, C.violet, "论文落点", "模态缺失、模态污染、模态冲突、混合噪声标签、开放集留出、校准可信性和证据包复核实验。", { bodySize: 9.6 });
  footer(s, n++);
}

// 11
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "DA-FDIDS 的正确融入方式：动态少样本与跨域适配插件", "DA-FDIDS");
  card(s, 0.78, 1.5, 5.65, 1.65, C.teal, "适合做什么", "动态图入侵检测：基于通信实体和流事件的时序关系建模。\n少样本攻击识别：support/query episode 适配新类别或小样本攻击。\n跨域泛化：GRL/MMD/Stable-LoRA 缓解园区、时间、协议和设备分布偏移。", { bodySize: 9.5 });
  card(s, 0.78, 3.95, 5.65, 1.65, C.coral, "不应夸大什么", "不是完整全流量采集工程，不替代 Probe/Kafka/Flink。\n当前更接近闭集 few-shot episode 分类，不能直接等同开放集拒识。\nTrafficEncoder 若无真实预训练权重，不宜直接称为流量基础大模型。", { bodySize: 9.5 });
  const modules = [["B0", "DIDS-MFL"], ["B1", "TrafficEncoder"], ["B2", "LoRA"], ["B4", "GRL"], ["B5", "MMD"], ["B8", "Full DA-FDIDS"]];
  modules.forEach((m, i) => {
    const y = 1.48 + i * 0.72;
    s.addShape(pptx.ShapeType.rect, { x: 7.05, y, w: 3.75, h: 0.42, fill: { color: i === 5 ? C.ink : C.panel2 }, line: { color: i === 5 ? C.ink : C.line } });
    s.addText(m[0], { x: 7.22, y: y + 0.12, w: 0.5, h: 0.1, fontFace: "Aptos", fontSize: 9.5, bold: true, color: i === 5 ? C.lime : C.violet, margin: 0 });
    s.addText(m[1], { x: 7.82, y: y + 0.1, w: 2.65, h: 0.1, fontFace: "Microsoft YaHei", fontSize: 9.7, bold: true, color: i === 5 ? "FFFFFF" : C.ink, margin: 0, fit: "shrink" });
  });
  card(s, 6.9, 6.0, 4.45, 0.66, C.coral, "实验门槛", "必须补 cross-domain、host-disjoint、time-disjoint、flow-disjoint 和 B0-B8 消融。", { bodySize: 9.3 });
  footer(s, n++);
}

// 12
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "多源融合：把模型分数变成攻击上下文和误报消解能力", "GRAPH FUSION");
  s.addShape(pptx.ShapeType.rect, { x: 5.55, y: 2.85, w: 2.05, h: 0.72, fill: { color: C.ink }, line: { color: C.ink } });
  s.addText("安全实体图", { x: 5.75, y: 3.12, w: 1.65, h: 0.1, fontFace: "Microsoft YaHei", fontSize: 11, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  const pts = [
    ["Flow/Session", 0.95, 1.55, C.teal],
    ["Asset", 5.1, 1.25, C.blue],
    ["Device Log", 9.3, 1.55, C.violet],
    ["User Event", 9.3, 4.65, C.coral],
    ["Threat Intel", 5.1, 5.35, C.amber],
    ["Alert/Evidence", 0.95, 4.65, C.ink],
  ];
  pts.forEach((p) => {
    s.addShape(pptx.ShapeType.rect, { x: p[1], y: p[2], w: 2.1, h: 0.56, fill: { color: p[3] }, line: { color: p[3] } });
    s.addText(p[0], { x: p[1] + 0.1, y: p[2] + 0.19, w: 1.9, h: 0.1, fontFace: "Aptos", fontSize: 10, bold: true, color: "FFFFFF", align: "center", margin: 0, fit: "shrink" });
  });
  bar(s, 3.05, 1.82, 2.5, 0.06, C.gray);
  bar(s, 7.6, 1.82, 1.72, 0.06, C.gray);
  bar(s, 3.05, 4.92, 2.5, 0.06, C.gray);
  bar(s, 7.6, 4.92, 1.72, 0.06, C.gray);
  bar(s, 6.12, 1.82, 0.06, 1.02, C.gray);
  bar(s, 6.12, 3.57, 0.06, 1.78, C.gray);
  card(s, 0.78, 6.25, 5.75, 0.58, C.teal, "检测增益", "图上下文补齐单流模型看不到的资产重要性、账号行为、IOC命中、横向移动路径和历史相似告警。", { bodySize: 9.6 });
  card(s, 6.88, 6.25, 5.75, 0.58, C.violet, "科研切入", "做单源/多源消融，量化误报下降、检出提前量和MTTR下降。", { bodySize: 9.6 });
  footer(s, n++);
}

// 13
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "高速全流量约束：用级联检测和预算调度兼顾吞吐与精度", "HIGH-SPEED PATH");
  const levels = [
    ["L0", "快速统计", "pps/bps、包长、IAT、端口、方向", C.teal],
    ["L1", "序列特征", "前N包长度/方向/时间间隔", C.blue],
    ["L2", "协议指纹", "TLS/QUIC、JA3、SNI、证书", C.violet],
    ["L3", "图关系", "通信邻域、资产、情报、历史告警", C.coral],
    ["L4", "深度证据", "开放集、原型、能量、不确定性", C.amber],
  ];
  levels.forEach((l, i) => {
    const x = 0.75 + i * 2.48;
    s.addShape(pptx.ShapeType.rect, { x, y: 2.1, w: 2.05, h: 1.15, fill: { color: l[3] }, line: { color: l[3] } });
    s.addText(l[0], { x: x + 0.18, y: 2.3, w: 0.45, h: 0.14, fontFace: "Aptos", fontSize: 13.5, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(l[1], { x: x + 0.62, y: 2.29, w: 1.05, h: 0.14, fontFace: "Microsoft YaHei", fontSize: 10.2, bold: true, color: "FFFFFF", margin: 0, fit: "shrink" });
    s.addText(l[2], { x: x + 0.22, y: 2.72, w: 1.48, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 7.8, color: "FFFFFF", align: "center", margin: 0, fit: "shrink" });
  });
  card(s, 0.82, 4.55, 5.75, 0.95, C.teal, "预算调度规则", "队列长度、CPU/GPU负载、Flink backpressure、Kafka lag、初筛风险和不确定性共同决定是否升级到高成本特征。", { bodySize: 9.6 });
  card(s, 6.85, 4.55, 5.75, 0.95, C.coral, "验收价值", "将10×100Gbps/512Mpps从“所有流量跑深度模型”的不现实假设，改成可证明的线速筛查+疑似深检方案。", { bodySize: 9.6 });
  footer(s, n++);
}

// 14
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "产品融合：AI检测结果要落在现有安全运营页面中", "PRODUCT WORKFLOW");
  const pages = [
    ["综合态势", "展示未知风险趋势、模型健康、证据完整度", C.teal],
    ["加密流量", "查看TLS/QUIC指纹、异常外联、开放集风险", C.violet],
    ["告警中心", "按known/review/unknown分层研判和反馈", C.coral],
    ["取证分析", "PCAP、Session、证据hash、相似样本", C.blue],
    ["模型管理", "版本、阈值、指标、激活、回滚", C.amber],
    ["MLOps编排", "标注、训练、盲测、注册、发布", C.ink],
  ];
  pages.forEach((p, i) => {
    const x = 0.74 + (i % 3) * 4.15;
    const y = 1.55 + Math.floor(i / 3) * 2.05;
    card(s, x, y, 3.65, 1.25, p[2], p[0], p[1], { bodySize: 9.6 });
  });
  card(s, 0.95, 6.1, 11.28, 0.5, C.teal, "页面原则", "不新增孤立“AI演示页”，而是在告警、取证、图谱、模型和MLOps页面中呈现可操作、可审计、可反馈的AI结果。", { bodySize: 10.1 });
  footer(s, n++);
}

// 15
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "验收融合：科研指标必须落到平台证据包和第三方盲测", "ACCEPTANCE");
  const rows = [
    ["功能主链路", "已较强", "Probe/Kafka/Flink/API/UI真实链路、PCAP下载、反馈、MLOps", C.teal],
    ["P95 <= 60s", "已闭环", "事件时间链、API/UI seen时间、分段P95", C.teal],
    ["95%/5%", "未闭环", "需冻结样本、阈值锁、labels/predictions、第三方签认", C.coral],
    ["Unknown Recall", "未闭环", "开放集留出、未知攻击样本、OSCR/FPR@95TPR", C.coral],
    ["100G/512Mpps", "未闭环", "硬件窗口、流量profile、资源水位、丢包/Kafka lag", C.coral],
    ["多源融合价值", "结构门通过", "仍需真实消融、误报下降、MTTR下降、试点签认", C.amber],
  ];
  rows.forEach((r, i) => {
    const y = 1.42 + i * 0.75;
    s.addShape(pptx.ShapeType.rect, { x: 0.72, y, w: 11.88, h: 0.55, fill: { color: i % 2 ? C.panel2 : C.panel }, line: { color: C.line } });
    bar(s, 0.72, y, 0.08, 0.55, r[3]);
    s.addText(r[0], { x: 0.95, y: y + 0.18, w: 1.55, h: 0.1, fontFace: "Microsoft YaHei", fontSize: 9.6, bold: true, color: C.ink, margin: 0 });
    s.addText(r[1], { x: 2.75, y: y + 0.18, w: 1.1, h: 0.1, fontFace: "Microsoft YaHei", fontSize: 9.6, bold: true, color: r[3], margin: 0 });
    s.addText(r[2], { x: 4.15, y: y + 0.18, w: 7.95, h: 0.1, fontFace: "Microsoft YaHei", fontSize: 9.4, color: C.gray, margin: 0, fit: "shrink" });
  });
  card(s, 0.92, 6.15, 11.2, 0.52, C.coral, "关键结论", "AI模型不能只报告训练集Accuracy；必须进入冻结盲测包，按Detection rate、FPR、Unknown recall、置信区间和第三方签认闭环。", { bodySize: 10.1 });
  footer(s, n++);
}

// 16
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "实施路线：先打通最小可信闭环，再扩展图融合与高速预算", "ROADMAP");
  const phases = [
    ["M1", "特征契约对齐", "确认FeatureStat/Seq/Fingerprint字段；设计Detection扩展与Evidence metrics_json。", C.teal],
    ["M2", "Evidence-OpenEMTD MVP", "三模态evidence、uncertainty、conflict、unknown_risk；离线盲测脚本。", C.violet],
    ["M3", "在线推理接入", "Flink消费feature.stat.v1；输出detections.v1；告警详情展示AI证据。", C.coral],
    ["M4", "MLOps闭环", "反馈样本池、阈值锁、模型注册、model-updates热更新、回滚。", C.blue],
    ["M5", "扩展增强", "图模态、多源消融、高速级联预算、第三方盲测与试点报告。", C.amber],
  ];
  phases.forEach((p, i) => {
    const x = 0.68 + i * 2.52;
    card(s, x, 1.65, 2.05, 4.45, p[3], p[0] + "  " + p[1], p[2], { bodySize: 9.0, headSize: 10.6, fill: i % 2 ? C.panel2 : C.panel });
  });
  footer(s, n++);
}

// 17
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "融合后的科研与成果输出：论文、专利、软著、验收证据互相支撑", "OUTPUTS");
  const outputs = [
    ["论文方向 1", "Evidence-OpenEMTD：证据冲突感知的可信开放集多模态加密恶意流量检测。", C.violet],
    ["论文方向 2", "DA-FDIDS：域自适应基础表征增强的少样本动态网络入侵检测框架。", C.teal],
    ["专利方向", "可信开放集检测、多粒度预算调度、多源知识图谱置信融合、LLM证据包幻觉校验。", C.coral],
    ["工程证据", "盲测包、P95链路、模型热更新、PCAP证据、融合价值报告、第三方签认。", C.amber],
  ];
  outputs.forEach((o, i) => {
    const x = 0.78 + (i % 2) * 6.0;
    const y = 1.62 + Math.floor(i / 2) * 2.15;
    card(s, x, y, 5.55, 1.38, o[2], o[0], o[1], { bodySize: 10.5 });
  });
  card(s, 1.12, 6.1, 11.0, 0.5, C.lime, "统一证据链", "同一条真实链路同时支撑论文实验、专利实施例、系统演示和验收报告，避免科研与工程两张皮。", { fill: C.ink, headColor: C.lime, bodyColor: "FFFFFF", bodySize: 10.6 });
  footer(s, n++);
}

// 18
{
  const s = pptx.addSlide();
  bg(s, true);
  bar(s, 0, 0, 0.22, H, C.lime);
  s.addText("结论与下一步", {
    x: 0.78, y: 0.72, w: 5.4, h: 0.52,
    fontFace: "Microsoft YaHei", fontSize: 30, bold: true,
    color: "FFFFFF", margin: 0,
  });
  const lines = [
    ["风险", "两个系统分裂建设，导致数据、模型、告警和证据口径不一致。", C.coral],
    ["控制", "算法以插件方式接入现有Feature、Detection、Evidence、MLOps和model-updates链路。", C.teal],
    ["优先", "先做三模态Evidence-OpenEMTD MVP和检测质量冻结包，再扩展图融合与高速预算。", C.amber],
  ];
  lines.forEach((l, i) => {
    const y = 1.75 + i * 1.25;
    s.addShape(pptx.ShapeType.rect, { x: 0.9, y, w: 11.2, h: 0.78, fill: { color: i === 0 ? "2B1D1D" : "172D32" }, line: { color: l[2] } });
    label(s, l[0], 1.15, y + 0.25, 0.8, l[2]);
    s.addText(l[1], { x: 2.15, y: y + 0.25, w: 9.6, h: 0.12, fontFace: "Microsoft YaHei", fontSize: 13.2, bold: true, color: "FFFFFF", margin: 0, fit: "shrink" });
  });
  s.addText("最终目标：把全流量系统从“看得见、查得到”升级为“可检测、可解释、可学习、可验收”。", {
    x: 0.92, y: 6.16, w: 10.9, h: 0.35,
    fontFace: "Microsoft YaHei", fontSize: 17.5,
    bold: true, color: C.lime, align: "center", margin: 0, fit: "shrink",
  });
  footer(s, n++, true);
}

pptx.writeFile({ fileName: OUTPUT })
  .then(() => console.log(OUTPUT))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
