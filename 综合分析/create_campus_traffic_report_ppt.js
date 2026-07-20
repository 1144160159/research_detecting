const fs = require("fs");
const path = require("path");
const pptxgen = require("../.pptx_build/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "综合分析");
const CHARTS = path.join(OUT, "图表");
const ASSETS = path.join(OUT, "generated_assets");
const OUTPUT = path.join(OUT, "园区网络流量智能检测与分析专题汇报.pptx");

const pptx = new pptxgen();
pptx.author = "Codex";
pptx.company = "Quancheng Laboratory";
pptx.subject = "园区网络流量智能检测与分析专题汇报";
pptx.title = "园区网络流量智能检测与分析专题汇报";
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
  deep2: "0E1A22",
  bg: "F6F8FA",
  panel: "FFFFFF",
  panel2: "EEF6F5",
  teal: "087E8B",
  teal2: "00A3A3",
  blue: "2F6BFF",
  violet: "6557D2",
  coral: "E85D3D",
  amber: "D89614",
  lime: "B7D12A",
  gray: "5F6B7A",
  line: "D8E1E5",
  muted: "DCE8EA",
  redSoft: "FBEAE6",
  greenSoft: "E9F7EF",
  yellowSoft: "FFF7E3",
};

const src = {
  product: path.join(ASSETS, "product_architecture_imagegen.png"),
  technical: path.join(ASSETS, "technical_architecture_imagegen.png"),
  deployment: path.join(ASSETS, "deployment_topology_imagegen.png"),
  ai: path.join(ASSETS, "ai_detection_architecture_imagegen.png"),
  cat: path.join(CHARTS, "大类归类统计.png"),
  rel: path.join(CHARTS, "相关性分布.png"),
  code: path.join(CHARTS, "代码状态分布.png"),
  innov: path.join(CHARTS, "创新点分布.png"),
  science: path.join(CHARTS, "科学问题分布.png"),
  trend: path.join(CHARTS, "年度趋势.png"),
};

function bg(slide, dark = false) {
  slide.background = { color: dark ? C.deep : C.bg };
  if (!dark) {
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 0.16, h: H,
      fill: { color: C.teal }, line: { color: C.teal },
    });
  }
}

function footer(slide, n, dark = false) {
  slide.addText("园区网络流量智能检测与分析专题汇报 | 数据来源：远程 traffic-analysis-platform + 本地 858 篇论文/代码分析", {
    x: 0.45, y: 7.12, w: 10.2, h: 0.18,
    fontFace: "Microsoft YaHei", fontSize: 8.2,
    color: dark ? "A9BDC2" : C.gray, margin: 0,
  });
  slide.addText(String(n).padStart(2, "0"), {
    x: 12.35, y: 7.06, w: 0.55, h: 0.18,
    fontFace: "Aptos", fontSize: 9, bold: true,
    color: dark ? "A9BDC2" : C.gray, align: "right", margin: 0,
  });
}

function imageFooter(slide, n, dark = false) {
  const fill = dark ? "06131A" : "F6F8FA";
  const text = dark ? "B9CDD2" : C.gray;
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 7.03, w: W, h: 0.34,
    fill: { color: fill, transparency: 4 },
    line: { color: fill, transparency: 100 },
  });
  slide.addText("园区网络流量智能检测与分析专题汇报 | 架构图为生成底图 + 可编辑事实标签叠加", {
    x: 0.42, y: 7.15, w: 8.2, h: 0.12,
    fontFace: "Microsoft YaHei", fontSize: 7.8,
    color: text, margin: 0,
  });
  slide.addText(String(n).padStart(2, "0"), {
    x: 12.35, y: 7.12, w: 0.55, h: 0.13,
    fontFace: "Aptos", fontSize: 8.5, bold: true,
    color: text, align: "right", margin: 0,
  });
}

function title(slide, text, kicker = "") {
  if (kicker) {
    slide.addText(kicker, {
      x: 0.58, y: 0.32, w: 5.0, h: 0.22,
      fontFace: "Microsoft YaHei", fontSize: 10,
      color: C.teal, bold: true, margin: 0,
    });
  }
  slide.addText(text, {
    x: 0.58, y: 0.66, w: 12.0, h: 0.56,
    fontFace: "Microsoft YaHei", fontSize: 25,
    color: C.ink, bold: true, margin: 0, fit: "shrink",
  });
}

function bar(slide, x, y, w, h, color) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color }, line: { color },
  });
}

function card(slide, x, y, w, h, accent, head, body, opts = {}) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color: opts.fill || C.panel, transparency: opts.transparency || 0 },
    line: { color: opts.line || C.line, width: 0.7 },
    shadow: opts.shadow ? { type: "outer", color: "000000", opacity: 0.08, blur: 3, offset: 1, angle: 45 } : undefined,
  });
  if (accent) {
    slide.addShape(pptx.ShapeType.rect, {
      x, y, w: 0.08, h,
      fill: { color: accent }, line: { color: accent },
    });
  }
  slide.addText(head, {
    x: x + 0.22, y: y + 0.16, w: w - 0.36, h: Math.min(0.34, h - 0.16),
    fontFace: "Microsoft YaHei", fontSize: opts.headSize || 12.2,
    bold: true, color: opts.headColor || C.ink, margin: 0, fit: "shrink",
  });
  if (body) {
    slide.addText(body, {
      x: x + 0.22, y: y + 0.52, w: w - 0.36, h: Math.max(0.18, h - 0.62),
      fontFace: "Microsoft YaHei", fontSize: opts.bodySize || 10.2,
      color: opts.bodyColor || C.gray, margin: 0.02, fit: "shrink",
    });
  }
}

function metric(slide, value, label, x, y, w, color, dark = false) {
  slide.addText(String(value), {
    x, y, w, h: 0.55,
    fontFace: "Aptos Display", fontSize: 31,
    bold: true, color, margin: 0, fit: "shrink",
  });
  slide.addText(label, {
    x, y: y + 0.65, w, h: 0.28,
    fontFace: "Microsoft YaHei", fontSize: 9.8,
    color: dark ? C.muted : C.gray, margin: 0, fit: "shrink",
  });
}

function bullets(slide, items, x, y, w, h, size = 11.2, color = C.ink) {
  const runs = items.map((text, i) => ({
    text,
    options: { bullet: { indent: 13 }, breakLine: i < items.length - 1 },
  }));
  slide.addText(runs, {
    x, y, w, h,
    fontFace: "Microsoft YaHei", fontSize: size,
    color, margin: 0.02, fit: "shrink", paraSpaceAfterPt: 6,
  });
}

function label(slide, text, x, y, w, color, opts = {}) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h: opts.h || 0.30,
    fill: { color, transparency: opts.transparency || 0 },
    line: { color, width: 0.5 },
  });
  slide.addText(text, {
    x: x + 0.07, y: y + (opts.h ? opts.h * 0.31 : 0.085), w: w - 0.14, h: 0.12,
    fontFace: "Microsoft YaHei", fontSize: opts.size || 8.4,
    bold: true, color: opts.textColor || "FFFFFF", align: "center",
    margin: 0, fit: "shrink",
  });
}

function img(slide, file, x, y, w, h, cover = false) {
  if (fs.existsSync(file)) {
    slide.addImage({ path: file, x, y, w, h, sizing: { type: cover ? "cover" : "contain", x, y, w, h } });
  } else {
    card(slide, x, y, w, h, C.coral, path.basename(file), "图像文件未找到");
  }
}

function miniStep(slide, n, head, body, x, y, w, color) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x, y, w: 0.46, h: 0.46,
    fill: { color }, line: { color },
  });
  slide.addText(String(n), {
    x, y: y + 0.13, w: 0.46, h: 0.1,
    fontFace: "Aptos", fontSize: 10.5, bold: true,
    color: "FFFFFF", align: "center", margin: 0,
  });
  card(slide, x + 0.62, y - 0.06, w - 0.62, 0.63, color, head, body, { bodySize: 8.4, headSize: 9.6 });
}

function tableRow(slide, cols, widths, x, y, h, fill, accent) {
  let cx = x;
  widths.forEach((w, i) => {
    slide.addShape(pptx.ShapeType.rect, {
      x: cx, y, w, h,
      fill: { color: fill || C.panel },
      line: { color: C.line, width: 0.5 },
    });
    if (i === 0 && accent) {
      bar(slide, cx, y, 0.06, h, accent);
    }
    slide.addText(cols[i], {
      x: cx + 0.12, y: y + 0.16, w: w - 0.2, h: h - 0.18,
      fontFace: "Microsoft YaHei", fontSize: i === 0 ? 9.7 : 9.2,
      bold: i === 0, color: i === 1 && accent ? accent : C.ink,
      margin: 0, fit: "shrink",
    });
    cx += w;
  });
}

let n = 1;

// 1. Cover
{
  const s = pptx.addSlide();
  bg(s, true);
  bar(s, 0, 0, 0.22, H, C.lime);
  img(s, src.ai, 6.75, 0.0, 6.58, 7.5, true);
  s.addShape(pptx.ShapeType.rect, { x: 6.2, y: 0, w: 7.2, h: H, fill: { color: C.deep, transparency: 24 }, line: { color: C.deep, transparency: 100 } });
  s.addText("园区网络流量智能检测与分析专题汇报", {
    x: 0.78, y: 1.25, w: 6.2, h: 1.15,
    fontFace: "Microsoft YaHei", fontSize: 34,
    bold: true, color: "FFFFFF", margin: 0, fit: "shrink",
  });
  s.addText("从全流量采集分析平台到 AI 驱动检测、论文代码复用与验收证据闭环", {
    x: 0.82, y: 2.75, w: 5.95, h: 0.54,
    fontFace: "Microsoft YaHei", fontSize: 14.2,
    color: C.muted, margin: 0, fit: "shrink",
  });
  [["远程系统", "/home/wangwt/phase_2/code/traffic-analysis-platform"], ["资料基线", "858 篇论文 + 145 条代码候选 + 127 个已下载仓库"], ["生成资产", "产品架构 / 技术架构 / 部署拓扑 / AI 检测实现底图"]].forEach((r, i) => {
    card(s, 0.9, 4.0 + i * 0.72, 5.65, 0.48, i === 0 ? C.teal : i === 1 ? C.violet : C.amber, r[0], r[1], {
      fill: "1B2A34", line: "2A4554", headColor: i === 0 ? C.lime : "FFFFFF", bodyColor: C.muted, headSize: 9.7, bodySize: 9.4,
    });
  });
  footer(s, n++, true);
}

// 2. Executive conclusion
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "汇报结论：这是一个“可运营、可学习、可验收”的全流量安全闭环", "EXECUTIVE SUMMARY");
  metric(s, "858", "已分析论文", 0.82, 1.45, 1.5, C.teal);
  metric(s, "439", "强相关论文", 2.55, 1.45, 1.7, C.coral);
  metric(s, "127", "本地可用代码仓库记录", 4.45, 1.45, 2.25, C.violet);
  metric(s, "2", "K8s Ready 节点", 7.0, 1.45, 1.7, C.blue);
  metric(s, "13", "traffic-analysis Running Pods", 8.9, 1.45, 2.45, C.amber);
  card(s, 0.82, 2.88, 3.75, 2.1, C.teal, "系统真实主链路", "Rust Probe -> Ingest Gateway -> Kafka -> Flink -> 多存储 -> Go APIs -> Web UI -> 反馈/MLOps。远程代码和 K8s 清单均可追踪。", { bodySize: 11.0, shadow: true });
  card(s, 4.82, 2.88, 3.75, 2.1, C.violet, "AI 检测落点", "当前工程已有规则、行为、CEP、告警、反馈和 XGBoost/LightGBM MLOps；DA-FDIDS 等论文模型应作为插件化增强接入。", { bodySize: 10.6, shadow: true });
  card(s, 8.82, 2.88, 3.75, 2.1, C.coral, "汇报口径边界", "功能链路具备强证据；10x100Gbps、512Mpps、P95<=60s、95%准确率/误报率<5%仍需专项验收和第三方盲测。", { bodySize: 10.6, shadow: true });
  card(s, 1.08, 5.75, 11.25, 0.68, C.lime, "最终呈现", "一套真实可演示的园区全流量采集分析平台 + 一条可解释、可反馈、可灰度发布的 AI 检测闭环 + 一份可复测的论文/代码/模型/验收证据包。", { fill: C.deep, line: C.deep, headColor: C.lime, bodyColor: "FFFFFF", bodySize: 11.6 });
  footer(s, n++);
}

// 3. Agenda
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "汇报结构：先讲系统，再讲 AI，再讲论文代码如何转化", "AGENDA");
  const items = [
    ["01", "系统整体介绍", "定位、产品能力、业务闭环、当前工程证据"],
    ["02", "真实架构拆解", "产品架构、技术架构、部署拓扑、核心实现"],
    ["03", "AI 检测实现", "流式推理、图/开放集增强、反馈学习、MLOps 热更新"],
    ["04", "858 篇论文与代码", "研究地图、强相关优先级、开源代码复用路线"],
    ["05", "最终交付形态", "演示系统、算法插件、论文专利、验收证据与路线图"],
  ];
  items.forEach((it, i) => {
    const y = 1.45 + i * 1.05;
    s.addShape(pptx.ShapeType.rect, { x: 0.92, y, w: 11.45, h: 0.75, fill: { color: i % 2 ? C.panel2 : C.panel }, line: { color: C.line } });
    label(s, it[0], 1.15, y + 0.22, 0.58, [C.teal, C.violet, C.coral, C.amber, C.blue][i], { size: 9.5 });
    s.addText(it[1], { x: 2.0, y: y + 0.18, w: 2.1, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.ink, margin: 0 });
    s.addText(it[2], { x: 4.25, y: y + 0.18, w: 7.35, h: 0.18, fontFace: "Microsoft YaHei", fontSize: 11.3, color: C.gray, margin: 0, fit: "shrink" });
  });
  footer(s, n++);
}

// 4. Product positioning
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "系统定位：不是抓包工具，而是园区全流量安全运营闭环", "SYSTEM POSITIONING");
  const chain = ["全流量可见", "多源融合", "智能检测", "告警研判", "PCAP/图谱取证", "反馈学习", "规则/模型治理", "验收证据"];
  chain.forEach((x, i) => {
    const w = i === 4 || i === 6 ? 1.35 : 1.1;
    const px = 0.52 + i * 1.55;
    label(s, x, px, 1.55, w, [C.teal, C.blue, C.violet, C.coral, C.amber, C.teal2, C.lime, C.ink][i], { size: 8.2 });
    if (i < chain.length - 1) {
      s.addShape(pptx.ShapeType.line, { x: px + w + 0.04, y: 1.7, w: 0.32, h: 0, line: { color: C.gray, width: 1.2, endArrowType: "triangle" } });
    }
  });
  const problems = [
    ["高带宽看不清", "探针、会话化、流量态势、采集健康"],
    ["告警多而不准", "规则 + 行为模型 + CEP + 多源上下文 + 反馈学习"],
    ["证据难回放", "Evidence、PCAP 索引/裁剪、对象 hash、下载审计"],
    ["关联依赖专家", "攻击链、实体图谱、资产/用户/日志上下文"],
    ["验收难闭环", "指标追溯、证据包、试点材料、第三方测试口径"],
  ];
  problems.forEach((p, i) => {
    const x = 0.75 + (i % 3) * 4.13;
    const y = i < 3 ? 2.72 : 4.75;
    card(s, x, y, 3.5, 1.18, [C.teal, C.coral, C.amber, C.violet, C.blue][i], p[0], p[1], { bodySize: 10.0, shadow: true });
  });
  footer(s, n++);
}

// 5. Product architecture image
{
  const s = pptx.addSlide();
  s.background = { color: "06131A" };
  img(s, src.product, 0, 0, W, H, true);
  s.addText("园区网络全流量采集与分析系统产品架构图", {
    x: 2.65, y: 0.28, w: 8.0, h: 0.42,
    fontFace: "Microsoft YaHei", fontSize: 19, bold: true,
    color: C.ink, align: "center", margin: 0, fit: "shrink",
  });
  label(s, "园区网络 / TAP-SPAN / 终端与服务器", 0.34, 0.92, 1.8, C.deep, { h: 0.44, size: 7.8 });
  label(s, "采集接入", 2.45, 2.65, 1.08, C.teal);
  const modules = [
    ["综合态势", 4.55, 2.05, C.teal],
    ["采集监测", 6.45, 2.05, C.teal2],
    ["威胁分析", 8.35, 2.05, C.lime],
    ["资产图谱", 4.55, 4.25, C.lime],
    ["检测运营", 6.45, 4.25, C.amber],
    ["审计配置", 8.35, 4.25, C.coral],
  ];
  modules.forEach((m) => {
    s.addText(m[0], { x: m[1], y: m[2], w: 1.15, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 12.5, bold: true, color: C.ink, align: "center", margin: 0 });
    s.addText(moduleBody(m[0]), { x: m[1] - 0.05, y: m[2] + 0.34, w: 1.28, h: 0.5, fontFace: "Microsoft YaHei", fontSize: 8.2, color: C.gray, align: "center", margin: 0.02, fit: "shrink" });
  });
  ["全流量可见", "多源融合", "智能检测", "告警研判", "取证回放", "反馈学习", "规则/模型治理"].forEach((t, i) => {
    label(s, t, 2.65 + i * 1.16, 6.05, i === 6 ? 1.12 : 0.92, [C.teal, C.teal2, C.violet, C.lime, C.amber, C.coral, C.blue][i], { size: 7.3 });
  });
  label(s, "运营驾驶舱", 10.82, 1.25, 1.32, C.teal);
  label(s, "验收证据包", 10.82, 5.65, 1.32, C.coral);
  imageFooter(s, n++, true);
}

function moduleBody(name) {
  return {
    "综合态势": "Dashboard\n态势大屏\n专题入口",
    "采集监测": "探针健康\n数据质量\n链路延迟",
    "威胁分析": "告警中心\n攻击链\n加密专题",
    "资产图谱": "资产台账\n通信关系\n基线画像",
    "检测运营": "规则/模型\n白名单\nMLOps",
    "审计配置": "合规审计\n通知策略\n系统治理",
  }[name] || "";
}

// 6. Product capability map
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "产品能力：六大业务域承接“发现-研判-取证-优化-验收”", "PRODUCT CAPABILITY");
  const items = [
    ["综合态势", "Dashboard、SituationalScreen、加密隧道/数据外传/APT 专题", C.teal],
    ["采集监测", "Probe 管理、DataQuality、吞吐/丢包/延迟/DLQ", C.blue],
    ["威胁分析", "Alerts、Campaigns、AttackChain、EncryptedTraffic、Forensics", C.coral],
    ["资产图谱", "AssetInventory、Graph、Fusion、Baselines", C.violet],
    ["检测运营", "Rules、Whitelist、Deployments、Models、MLOps、Playbooks", C.amber],
    ["审计配置", "Compliance、AuditLog、Notifications、Settings", C.ink],
  ];
  items.forEach((it, i) => {
    const x = 0.75 + (i % 2) * 6.05;
    const y = 1.55 + Math.floor(i / 2) * 1.62;
    card(s, x, y, 5.5, 1.12, it[2], it[0], it[1], { bodySize: 9.7, headSize: 12.0, shadow: true });
  });
  card(s, 1.08, 6.45, 11.25, 0.42, C.lime, "界面原则", "一级菜单按业务域组织；闭环阶段用于流程、状态机和验收 ID，不直接作为导航标签。", { fill: C.deep, line: C.deep, headColor: C.lime, bodyColor: "FFFFFF", bodySize: 9.6 });
  footer(s, n++);
}

// 7. Evidence from remote code
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "远程代码实证：仓库是多语言工程系统，不是单点算法 Demo", "REMOTE CODE EVIDENCE");
  const rows = [
    ["Rust 探针", "rust/probe-agent", "AF_XDP/AF_PACKET/PCAP 离线采集、流聚合、PCAP 归档、DNS/DHCP/ARP 解析"],
    ["Go 控制面", "go/control-plane", "ingest、auth、alert、rule、asset、graph、forensics、threat-intel 等 API 服务"],
    ["Java Flink", "java/flink-jobs", "session、feature、rule、behavior、CEP、alert-generator、log、pcap-index、user-behavior"],
    ["Web UI", "web/ui", "Vite + React + Ant Design + ECharts，30 个页面，真实 API 优先"],
    ["MLOps", "mlops + argo-events", "ClickHouse 特征提取、XGBoost/LightGBM、评估、注册、Kafka model-updates"],
    ["部署/契约", "deployments + proto + common", "K8s 清单、APISIX、Kafka topic、CH/PG DDL、跨语言 Protobuf 真源"],
  ];
  rows.forEach((r, i) => tableRow(s, r, [1.35, 2.45, 8.3], 0.72, 1.35 + i * 0.83, 0.58, i % 2 ? C.panel2 : C.panel, [C.teal, C.blue, C.violet, C.coral, C.amber, C.lime][i]));
  card(s, 0.92, 6.42, 11.6, 0.42, C.coral, "注意口径", "本页为静态代码/部署清单和 kubectl 快照归纳；性能、算法质量、第三方验收不由代码存在本身推出。", { bodySize: 9.3 });
  footer(s, n++);
}

// 8. Main data path
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "主数据链路：从包到告警，再回到规则和模型", "DATA FLOW");
  const steps = [
    ["Rust Probe", "镜像/TAP/SPAN\n流聚合/PCAP归档", C.teal],
    ["Ingest Gateway", "gRPC + mTLS\n批量接入/限流/DLQ", C.blue],
    ["Kafka Topics", "flow/session/feature\nalerts/feedback/model", C.violet],
    ["Flink Jobs", "会话化/特征/规则\n行为/CEP/告警生成", C.coral],
    ["Data Stores", "CH/PG/OS/Nebula\nRedis/MinIO", C.amber],
    ["Go APIs + UI", "告警/图谱/取证\n运营与验收", C.ink],
  ];
  steps.forEach((st, i) => {
    const x = 0.62 + i * 2.08;
    card(s, x, 2.0, 1.72, 1.72, st[2], st[0], st[1], { bodySize: 8.6, headSize: 10.5, fill: i % 2 ? C.panel2 : C.panel, shadow: true });
    if (i < steps.length - 1) {
      s.addShape(pptx.ShapeType.line, { x: x + 1.76, y: 2.82, w: 0.28, h: 0, line: { color: C.teal, width: 2, endArrowType: "triangle" } });
    }
  });
  s.addShape(pptx.ShapeType.line, { x: 10.05, y: 4.05, w: -6.8, h: 1.3, line: { color: C.coral, width: 2.2, dash: "dash", endArrowType: "triangle" } });
  card(s, 2.75, 5.25, 7.9, 0.85, C.coral, "反馈闭环", "Alert Feedback / Whitelist / Rule Review / MLOps 产出 rule.updates 和 model-updates，Flink 热更新后重新进入在线检测链路。", { bodySize: 10.2, fill: C.redSoft });
  footer(s, n++);
}

// 9. Technical architecture image
{
  const s = pptx.addSlide();
  s.background = { color: "FFFFFF" };
  img(s, src.technical, 0, 0, W, H, true);
  const labels = [
    ["采集层\nRust Probe", 0.25, 0.82, C.deep],
    ["接入安全\nIngest/mTLS", 0.25, 1.8, C.teal],
    ["消息总线\nKafka Topics", 0.25, 2.78, C.blue],
    ["流计算层\nFlink Jobs", 0.25, 3.75, C.violet],
    ["存储层\n多模态证据", 0.25, 4.72, C.amber],
    ["API层\nGo Services", 0.25, 5.7, C.teal],
    ["反馈/MLOps\n热更新", 0.25, 6.66, C.coral],
  ];
  labels.forEach((l) => label(s, l[0], l[1], l[2], 1.42, l[3], { h: 0.44, size: 7.5 }));
  [
    ["AF_XDP / AF_PACKET / PCAP / DNS-DHCP-ARP", 3.1, 0.68, 3.35, C.deep],
    ["Ingest Gateway -> Kafka", 7.0, 0.68, 2.45, C.teal],
    ["Session / Feature / Rule / Behavior / CEP / Alert / Log / PCAP Index / User Behavior", 2.35, 3.05, 6.8, C.violet],
    ["ClickHouse / PostgreSQL / OpenSearch / NebulaGraph / Redis / MinIO", 2.35, 4.88, 6.8, C.amber],
    ["Auth / Alert / Rule / Asset / Graph / Forensics / Ingest / Threat Intel", 2.35, 5.95, 6.8, C.teal],
    ["Web UI + Feedback + Whitelist + Rule Review + MLOps", 9.7, 4.1, 2.15, C.coral],
  ].forEach((l) => label(s, l[0], l[1], l[2], l[3], l[4], { h: 0.34, size: 7.3 }));
  imageFooter(s, n++);
}

// 10. Technical layers detail
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "技术架构拆解：每层都有可追踪代码、契约和部署对象", "TECHNICAL DECOMPOSITION");
  const items = [
    ["采集与聚合", "hostNetwork + privileged Probe DaemonSet；接口 ens9f0、af_packet、flow_capacity 250000、batch_size 100"],
    ["消息与流计算", "Kafka topic 初始化覆盖 flow/session/feature/detections/alerts/feedback/rule/model/dlq；Flink 9 类作业"],
    ["存储与检索", "ClickHouse 2 shard x 2 replica + 3 Keeper；PG 元数据；OpenSearch 全文；Nebula 关系；Redis 缓存；MinIO PCAP/模型"],
    ["控制面服务", "Go 服务按 api/service/repository/config 分层，承接告警、规则、资产、图谱、取证、认证、威胁情报"],
    ["可观测与安全", "APISIX NodePort 30180；Kafka SASL_SSL；mTLS 探针接入；Keycloak/OIDC；Grafana/Loki"],
  ];
  items.forEach((it, i) => {
    miniStep(s, i + 1, it[0], it[1], 0.75, 1.48 + i * 1.04, 11.75, [C.teal, C.blue, C.violet, C.amber, C.coral][i]);
  });
  footer(s, n++);
}

// 11. Deployment topology image
{
  const s = pptx.addSlide();
  s.background = { color: "FFFFFF" };
  img(s, src.deployment, 0, 0, W, H, true);
  label(s, "园区网络 / TAP-SPAN 镜像", 0.35, 0.3, 1.58, C.teal, { size: 7.4 });
  label(s, "Probe Agent DaemonSet", 2.38, 1.05, 1.15, C.coral, { size: 7.2 });
  label(s, "Kubernetes 集群：8-2tb(10.0.5.8) + zeus-server(10.0.5.9)", 4.45, 0.32, 5.55, C.blue, { size: 8.3 });
  label(s, "APISIX NodePort 30180", 10.65, 1.05, 1.42, C.coral, { size: 7.2 });
  label(s, "traffic-analysis: Go APIs / Web UI / Probe / Queue", 4.22, 1.72, 3.05, C.teal, { size: 7.1 });
  label(s, "flink: JobManager + TaskManagers", 4.22, 3.18, 2.25, C.violet, { size: 7.1 });
  label(s, "middleware/databases/minio/iam/observability", 4.0, 4.88, 3.28, C.amber, { size: 7.0 });
  label(s, "浏览器/运维/验收人员", 10.85, 2.58, 1.35, C.deep, { size: 7.0 });
  label(s, "证据包 / 报告 / PCAP / 模型", 10.55, 5.3, 1.7, C.teal, { size: 7.0 });
  imageFooter(s, n++);
}

// 12. Live deployment facts
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "当前部署快照：两节点 Ready，业务服务以 K8s 工作负载运行", "DEPLOYMENT FACTS");
  card(s, 0.78, 1.45, 5.8, 1.2, C.blue, "节点", "8-2tb 10.0.5.8（control-plane）\nzeus-server 10.0.5.9（worker）\nKubernetes v1.29.15 / openEuler 22.03 / containerd", { bodySize: 10.2, fill: C.panel2 });
  card(s, 6.86, 1.45, 5.8, 1.2, C.teal, "traffic-analysis namespace", "13 个 Running Pod：alert、asset、auth、forensics、graph、ingest、probe(2)、rule、threat-intel、web-ui 等。另有历史 Completed/Error pod 记录，不作为现行服务能力声称。", { bodySize: 9.8, fill: C.panel2 });
  const svc = [
    ["入口", "gateway/apisix NodePort 30180"],
    ["消息", "middleware/kafka-0/1/2 + bootstrap"],
    ["流计算", "flink JobManager / TaskManager"],
    ["OLAP", "ClickHouse 1/2 + Keeper"],
    ["元数据", "PostgreSQL primary/replica"],
    ["对象/证据", "MinIO + minio-proxy"],
    ["图谱", "Nebula meta/storage/graph"],
    ["认证", "Keycloak / OIDC"],
    ["观测", "Grafana / Loki"],
  ];
  svc.forEach((r, i) => {
    const x = 0.78 + (i % 3) * 4.08;
    const y = 3.25 + Math.floor(i / 3) * 0.88;
    card(s, x, y, 3.55, 0.58, [C.teal, C.violet, C.amber][i % 3], r[0], r[1], { headSize: 9.2, bodySize: 8.6, fill: i % 2 ? C.panel : C.panel2 });
  });
  footer(s, n++);
}

// 13. AI architecture image
{
  const s = pptx.addSlide();
  s.background = { color: "06131A" };
  img(s, src.ai, 0, 0, W, H, true);
  label(s, "在线流式检测", 1.4, 0.26, 1.92, C.teal, { size: 8.2 });
  label(s, "特征工程 / 表征", 4.15, 0.26, 1.85, C.teal, { size: 8.2 });
  label(s, "模型决策与解释", 6.95, 0.26, 1.85, C.teal, { size: 8.2 });
  label(s, "规则 / 行为 / CEP / 图上下文 / 开放集评分", 3.15, 3.55, 4.65, C.violet, { h: 0.36, size: 7.8 });
  label(s, "TP/FP 反馈与人工审核", 3.9, 5.0, 2.15, C.coral, { size: 7.8 });
  label(s, "MLOps：抽取 -> 训练 -> 评估 -> 注册 -> 发布", 1.1, 6.05, 4.4, C.amber, { size: 7.8 });
  label(s, "Kafka model-updates / Flink 热更新", 6.65, 6.25, 2.3, C.amber, { size: 7.8 });
  label(s, "论文与代码资产库", 11.1, 0.78, 1.35, C.blue, { size: 7.2 });
  label(s, "Benchmark / 候选算法 / 预处理复用 / 验收证据", 10.6, 5.78, 1.9, C.lime, { h: 0.44, size: 6.4 });
  imageFooter(s, n++, true);
}

// 14. AI current vs target
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "AI 驱动检测：当前已具备工程闭环，重点补强模型质量与开放集能力", "AI IMPLEMENTATION");
  const cols = [
    ["当前已有", ["规则检测、行为检测、CEP、Alert Generator", "Alert Feedback、Whitelist、Rule Review", "MLOps：extract/train/evaluate/register", "XGBoost/LightGBM + F1/Precision/Recall/AUC", "MinIO/模型注册/ Kafka model-updates"]],
    ["需要补强", ["DA-FDIDS 动态图/少样本/域适应插件", "开放集拒识与 Unknown Recall", "图上下文与多源融合消融", "冻结盲测包与阈值锁", "Python/Java/Flink 离在线一致性"]],
    ["验收落点", ["准确率、误报率、Unknown Recall", "P95 端到端延迟", "模型版本、灰度、回滚、审计", "PCAP/证据/相似样本解释", "第三方可复测报告"]],
  ];
  cols.forEach((c, i) => {
    const x = 0.75 + i * 4.18;
    card(s, x, 1.55, 3.55, 4.78, [C.teal, C.violet, C.coral][i], c[0], "", { fill: i === 0 ? C.greenSoft : i === 1 ? C.panel2 : C.redSoft, headSize: 13.5, shadow: true });
    bullets(s, c[1], x + 0.28, 2.25, 2.95, 3.45, 10.2);
  });
  footer(s, n++);
}

// 15. MLOps lifecycle
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "MLOps 实现链路：从告警反馈到模型热更新", "MLOPS LOOP");
  const stages = [
    ["1", "数据提取", "ClickHouse features_stat + alerts + alert_feedback\n输出 train/test parquet 与 metadata"],
    ["2", "模型训练", "XGBoost / LightGBM\n类别不平衡、早停、5 折交叉验证"],
    ["3", "模型评估", "Accuracy / Precision / Recall / F1\nAUC-ROC / AUC-PR / 混淆矩阵 / 阈值分析"],
    ["4", "模型注册", "MinIO artifact_uri + Model Registry\n版本、指标、状态和审计"],
    ["5", "热更新", "Kafka model-updates\nFlink 监听并重载模型/阈值"],
  ];
  stages.forEach((st, i) => {
    const x = 0.72 + i * 2.52;
    card(s, x, 1.75, 2.05, 3.2, [C.teal, C.blue, C.violet, C.amber, C.coral][i], st[0] + "  " + st[1], st[2], { bodySize: 9.0, headSize: 10.5, shadow: true, fill: i % 2 ? C.panel2 : C.panel });
    if (i < stages.length - 1) s.addShape(pptx.ShapeType.line, { x: x + 2.1, y: 3.28, w: 0.32, h: 0, line: { color: C.teal, width: 2, endArrowType: "triangle" } });
  });
  card(s, 1.2, 5.75, 10.85, 0.62, C.lime, "设计原则", "AI 结果必须可解释、可回放、可灰度、可回滚；不能只把离线模型分数堆到告警页面。", { fill: C.deep, headColor: C.lime, bodyColor: "FFFFFF", bodySize: 10.8 });
  footer(s, n++);
}

// 16. DA-FDIDS placement
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "DA-FDIDS 的正确落点：AI 检测模型插件，而不是全流量平台本身", "DA-FDIDS POSITION");
  card(s, 0.85, 1.55, 5.4, 1.25, C.violet, "模型定位", "域自适应基础表征增强的少样本动态网络入侵检测模型；在 DIDS-MFL 基线基础上增强 LoRA、cache、GRL、MMD、Stable-LoRA、RBF cache、MHA feature weighting。", { bodySize: 10.3, shadow: true });
  card(s, 6.85, 1.55, 5.4, 1.25, C.coral, "谨慎口径", "当前代码更接近 few-shot episode 分类；若称开放集/基础模型，需要补齐未知类拒识、真实预训练 checkpoint、host/time/domain-disjoint 实验。", { bodySize: 10.0, shadow: true });
  const mods = [
    ["TrafficEncoder", "统一流量表征"],
    ["LoRA", "支持集快速适配"],
    ["Cache Fusion", "相似样本检索增强"],
    ["GRL/MMD", "域对抗与分布对齐"],
    ["Stable-LoRA", "稳定性约束"],
    ["RBF/MHA", "漂移下特征加权"],
  ];
  mods.forEach((m, i) => {
    const x = 0.82 + (i % 3) * 4.12;
    const y = 3.45 + Math.floor(i / 3) * 1.08;
    card(s, x, y, 3.52, 0.68, [C.teal, C.blue, C.violet, C.coral, C.amber, C.lime][i], m[0], m[1], { headSize: 9.8, bodySize: 8.8, fill: i % 2 ? C.panel2 : C.panel });
  });
  card(s, 1.1, 6.15, 11.05, 0.5, C.teal, "工程接入方式", "将 DA-FDIDS 作为候选模型服务/离线训练插件接入 FeatureStat/FeatureSeq，输出 DetectionBatch/Evidence，由 MLOps 管版本、阈值、灰度和回滚。", { bodySize: 9.8 });
  footer(s, n++);
}

// 17. Paper statistics
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "858 篇论文研究地图：强相关主体集中在流量识别与 NIDS", "PAPER MAP");
  metric(s, "194", "加密流量分类与应用识别", 0.82, 1.35, 2.25, C.teal);
  metric(s, "184", "入侵检测与网络异常检测", 3.35, 1.35, 2.25, C.coral);
  metric(s, "68", "恶意流量、暗网与攻击检测", 5.9, 1.35, 2.25, C.violet);
  metric(s, "63", "图学习、知识图谱与威胁情报", 8.25, 1.35, 2.45, C.amber);
  metric(s, "52", "时序/日志/KPI/云原生异常", 10.85, 1.35, 2.15, C.blue);
  img(s, src.cat, 0.75, 2.75, 5.9, 3.45);
  img(s, src.trend, 7.05, 2.75, 5.3, 3.45);
  footer(s, n++);
}

// 18. Relevance and code status
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "论文使用优先级：439 篇强相关，120 篇已有可用代码覆盖", "RELEVANCE & CODE");
  img(s, src.rel, 0.82, 1.55, 5.35, 3.15);
  img(s, src.code, 7.05, 1.55, 5.15, 3.15);
  const rows = [
    ["强相关", "439 篇", "优先进入模型候选、基线复现、benchmark 与系统增强"],
    ["中相关", "251 篇", "用于图关联、时序日志、联邦协同、边缘部署等模块迁移"],
    ["弱相关", "168 篇", "主要服务背景综述、异常检测通用范式和评审补充"],
    ["代码状态", "127 个已下载仓库记录", "覆盖 120 篇论文；145 条代码候选用于持续核验"],
  ];
  rows.forEach((r, i) => tableRow(s, r, [1.25, 1.9, 8.2], 1.0, 5.18 + i * 0.42, 0.36, i % 2 ? C.panel2 : C.panel, [C.teal, C.blue, C.violet, C.coral][i]));
  footer(s, n++);
}

// 19. Innovation and science problems
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "论文启示：工程系统必须同时处理可观测缺失、实时约束和真实漂移", "RESEARCH SIGNALS");
  img(s, src.innov, 0.72, 1.42, 5.8, 3.55);
  img(s, src.science, 6.86, 1.42, 5.85, 3.55);
  card(s, 0.9, 5.55, 3.65, 0.76, C.teal, "表征学习", "字节/包/流/图统一表征，适合进入 FeatureSeq 与模型插件。", { bodySize: 8.8 });
  card(s, 4.85, 5.55, 3.65, 0.76, C.coral, "开放世界", "未知攻击、低误报、漂移适配需要独立指标和阈值锁。", { bodySize: 8.8 });
  card(s, 8.8, 5.55, 3.65, 0.76, C.amber, "系统评测", "Benchmark、回放、第三方盲测比单点高分更重要。", { bodySize: 8.8 });
  footer(s, n++);
}

// 20. How to use papers frame by frame
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "逐帧使用论文：从“读文献”转成“系统组件证据链”", "PAPER-TO-SYSTEM FRAMES");
  const frames = [
    ["Frame 1", "需求与科学问题", "用 10 类科学问题解释为什么需要加密流量表征、图融合、开放集和持续学习。"],
    ["Frame 2", "技术路线筛选", "强相关论文先进入加密流量、NIDS、恶意流量、图学习、在线部署五个技术簇。"],
    ["Frame 3", "模型与基线复现", "优先复现强相关 + 已下载代码，形成 FS-Net/ET-BERT/TrafficFormer/FIR-GNN/HyperVision 等 benchmark。"],
    ["Frame 4", "工程接入设计", "把论文方法映射到 FeatureStat/FeatureSeq、DetectionBatch、Evidence、MLOps、model-updates。"],
    ["Frame 5", "验收与论文输出", "冻结盲测包、复现表、消融、错误分析、第三方报告共同支撑论文/专利/软著/验收。"],
  ];
  frames.forEach((f, i) => {
    miniStep(s, i + 1, f[0] + "  " + f[1], f[2], 0.75, 1.45 + i * 1.02, 11.72, [C.teal, C.blue, C.violet, C.coral, C.amber][i]);
  });
  footer(s, n++);
}

// 21. Code repository usage
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "开源代码使用方式：不是直接搬模型，而是形成可复现组件库", "OPEN SOURCE REUSE");
  const groups = [
    ["表征与预训练", "ET-BERT、TrafficFormer、TrafficLLM、YaTC、UniNet、FS-Net", "构建字节/包/流序列表征、tokenizer、预训练/微调基线"],
    ["图与开放集", "FIR-GNN、HyperVision、DawnGuard、ERFS、FeCoGraph、Sieve、Open-Detect", "抽取图构造、few-shot、未知/噪声标签处理和关系建模方法"],
    ["实时与工具", "Marina、NTLFlowLyzer、FastTraffic、CENTIME", "复用高性能特征、流量切分、轻量分类和数据集生成思路"],
    ["漂移与鲁棒", "Rosetta、Argus、ReCDA、PANTS、MAML-Training-ETC", "支撑跨域、漂移、自适应、对抗鲁棒和动态网络实验"],
    ["知识与取证", "Open-CyKG、Krystal、TeRed、TraceCluster", "补强图谱、威胁情报、因果/溯源和证据解释"],
  ];
  groups.forEach((g, i) => {
    const y = 1.35 + i * 1.05;
    tableRow(s, g, [1.55, 4.05, 6.15], 0.72, y, 0.68, i % 2 ? C.panel2 : C.panel, [C.teal, C.violet, C.amber, C.coral, C.blue][i]);
  });
  card(s, 0.98, 6.55, 11.15, 0.42, C.coral, "使用原则", "先做统一数据适配与指标复现，再做模型裁剪和在线接入；不把论文仓库原样放进生产链路。", { bodySize: 9.4 });
  footer(s, n++);
}

// 22. Representative strong papers
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "强相关优先清单：先打通对系统最有价值的复现闭环", "PRIORITY PAPERS");
  const rows = [
    ["DawnGuard", "多流时序图，早期加密恶意流量检测", "图/早期检测/恶意加密流量"],
    ["SnifferDog", "异构特征综合学习识别恶意流", "多视图特征融合"],
    ["FIR-GNN", "基于流交互关系的图神经网络 IDS", "图结构入侵检测"],
    ["HyperVision", "未知加密恶意流量实时图分析", "开放集/未知攻击"],
    ["Marina", "Terabit 级 ML 驱动实时网络监测", "高速监测工程参考"],
    ["TrafficLLM", "面向网络流量分析的大模型表征", "LLM/通用表示扩展"],
  ];
  rows.forEach((r, i) => tableRow(s, r, [1.55, 4.55, 5.7], 0.72, 1.35 + i * 0.78, 0.54, i % 2 ? C.panel2 : C.panel, [C.teal, C.blue, C.violet, C.coral, C.amber, C.lime][i]));
  card(s, 1.0, 6.28, 11.2, 0.52, C.teal, "复现产物", "每篇形成：数据适配脚本、训练/推理入口、指标 JSON、错误样本、可接入平台的特征/模型接口说明。", { bodySize: 10.2 });
  footer(s, n++);
}

// 23. Acceptance boundaries
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "验收口径：功能主链路与任务书指标必须分层表达", "ACCEPTANCE BOUNDARY");
  const rows = [
    ["功能主链路", "有较强证据", "远程记录显示 full/live/python-test 通过，业务 Pod 正常运行；可用于演示和功能回归。", C.teal],
    ["P95 <= 60s", "待专项证据", "需要 event_ts、ingest_ts、kafka_ts、flink_out_ts、api_seen_ts、ui_seen_ts 的端到端统计。", C.amber],
    ["10 x 100Gbps / 512Mpps", "待压测", "需要硬件拓扑、包长分布、丢包率、CPU/NUMA、Kafka lag、Flink backpressure 报告。", C.coral],
    ["95% 准确率 / <5% 误报率", "待第三方盲测", "需要冻结样本、标签、阈值锁、混淆矩阵、Unknown Recall 和置信区间。", C.coral],
    ["生产安全与 HA", "持续加固", "Kafka SASL_SSL、ExternalSecret、mTLS、NetworkPolicy、故障演练、RTO/RPO。", C.amber],
  ];
  rows.forEach((r, i) => tableRow(s, [r[0], r[1], r[2]], [2.0, 1.55, 8.45], 0.72, 1.45 + i * 0.88, 0.62, i % 2 ? C.panel2 : C.panel, r[3]));
  card(s, 0.98, 6.2, 11.25, 0.54, C.lime, "汇报红线", "不能把“架构支持”“小样本演示”“代码存在”写成“指标已经全部达成”。", { fill: C.deep, line: C.deep, headColor: C.lime, bodyColor: "FFFFFF", bodySize: 10.5 });
  footer(s, n++);
}

// 24. What final presentation should show
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "最终应该呈现出的成果形态", "TARGET OUTPUT");
  const outputs = [
    ["可演示系统", "Web UI 真实 API、态势大屏、告警、图谱、PCAP 取证、反馈与模型管理闭环。", C.teal],
    ["可运行链路", "Probe/Kafka/Flink/CH/PG/OS/Nebula/Redis/MinIO/Go API/K8s 清单可追踪。", C.blue],
    ["AI 模型包", "规则+行为+CEP 当前可用；DA-FDIDS/图/开放集/预训练模型以插件方式进入 MLOps。", C.violet],
    ["论文代码证据", "858 篇研究地图、强相关复现清单、127 个代码仓库、benchmark 与消融表。", C.amber],
    ["验收证据包", "基线、样本、标签、指标、P95、压测、安全、HA、第三方盲测和试点报告。", C.coral],
    ["科研输出", "论文、专利、软著和技术报告共享同一真实工程证据链。", C.ink],
  ];
  outputs.forEach((o, i) => {
    const x = 0.72 + (i % 2) * 6.05;
    const y = 1.45 + Math.floor(i / 2) * 1.6;
    card(s, x, y, 5.5, 1.08, o[2], o[0], o[1], { bodySize: 9.8, shadow: true, fill: i % 2 ? C.panel2 : C.panel });
  });
  footer(s, n++);
}

// 25. Roadmap
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "实施路线：先闭环可信最小系统，再扩展高速与第三方验收", "ROADMAP");
  const phases = [
    ["M1", "架构与证据冻结", "固化当前代码、镜像、K8s、topic、DDL、样本和 PPT 架构口径。", C.teal],
    ["M2", "AI 检测 MVP", "FeatureStat/Seq -> DetectionBatch -> Evidence -> UI，接入 XGBoost/LightGBM 和 1-2 个论文模型。", C.violet],
    ["M3", "开放集与图增强", "DA-FDIDS/图关系/开放集评分/相似样本解释，完成离线消融和错误分析。", C.coral],
    ["M4", "MLOps 与灰度", "反馈样本池、阈值锁、模型注册、热更新、回滚和审计报告。", C.blue],
    ["M5", "专项验收", "P95、100G/512Mpps、95%/5%、安全/HA/第三方盲测与试点报告。", C.amber],
  ];
  phases.forEach((p, i) => {
    const x = 0.68 + i * 2.52;
    card(s, x, 1.62, 2.05, 4.55, p[3], p[0] + "  " + p[1], p[2], { bodySize: 9.0, headSize: 10.2, fill: i % 2 ? C.panel2 : C.panel, shadow: true });
  });
  footer(s, n++);
}

// 26. Risks and controls
{
  const s = pptx.addSlide();
  bg(s);
  title(s, "风险控制：防止“论文、模型、平台、验收”四张皮", "RISK CONTROL");
  const risks = [
    ["模型离线高分，线上无证据", "统一 Feature 契约、离在线一致性测试、Evidence 可追溯。"],
    ["论文代码难复现", "先选强相关+已下载代码；输出数据适配、指标 JSON 和复现日志。"],
    ["架构图脱离实际", "所有图中组件只取自远程代码、K8s 清单、proto、topic、DDL 和 kubectl 快照。"],
    ["验收指标被过度承诺", "功能证据、专项压测、第三方盲测分层汇报，不混用。"],
    ["反馈学习失控", "模型版本、阈值锁、灰度、回滚、审计和人工审核。"],
  ];
  risks.forEach((r, i) => {
    const y = 1.42 + i * 1.02;
    card(s, 0.85, y, 5.25, 0.68, C.coral, "风险 " + (i + 1), r[0], { headSize: 9.2, bodySize: 9.2, fill: C.redSoft });
    card(s, 6.35, y, 5.95, 0.68, C.teal, "控制", r[1], { headSize: 9.2, bodySize: 9.2, fill: C.greenSoft });
  });
  footer(s, n++);
}

// 27. Closing
{
  const s = pptx.addSlide();
  bg(s, true);
  bar(s, 0, 0, 0.22, H, C.lime);
  s.addText("结论", {
    x: 0.82, y: 0.82, w: 2.2, h: 0.45,
    fontFace: "Microsoft YaHei", fontSize: 28,
    color: C.lime, bold: true, margin: 0,
  });
  s.addText("用真实全流量工程底座承接 AI 检测，用论文代码证据链支撑可复测创新", {
    x: 0.82, y: 1.65, w: 10.8, h: 0.78,
    fontFace: "Microsoft YaHei", fontSize: 30,
    color: "FFFFFF", bold: true, margin: 0, fit: "shrink",
  });
  const lines = [
    ["系统", "当前平台已具备采集、流计算、存储、API、UI、取证、反馈和 MLOps 主链路。", C.teal],
    ["AI", "AI 模型应作为可灰度发布的检测插件接入，而不是游离于平台之外的离线脚本。", C.violet],
    ["论文", "858 篇论文和 127 个代码仓库要落成 benchmark、候选算法、实验报告和验收证据。", C.amber],
    ["验收", "所有指标必须通过冻结样本、压测、第三方盲测和现场试点闭环。", C.coral],
  ];
  lines.forEach((l, i) => {
    const y = 3.05 + i * 0.78;
    label(s, l[0], 0.95, y + 0.18, 0.7, l[2]);
    s.addText(l[1], { x: 1.9, y: y + 0.18, w: 9.75, h: 0.16, fontFace: "Microsoft YaHei", fontSize: 12.2, color: "FFFFFF", bold: true, margin: 0, fit: "shrink" });
  });
  s.addText("最终目标：看得见、判得准、查得到、说得清、学得动、验得过。", {
    x: 1.1, y: 6.35, w: 10.8, h: 0.32,
    fontFace: "Microsoft YaHei", fontSize: 18,
    color: C.lime, bold: true, align: "center", margin: 0,
  });
  footer(s, n++, true);
}

pptx.writeFile({ fileName: OUTPUT })
  .then(() => console.log(OUTPUT))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
