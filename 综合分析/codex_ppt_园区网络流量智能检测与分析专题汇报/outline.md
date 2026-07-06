# 园区网络流量智能检测与分析专题汇报 - codex-ppt 提纲草案

状态：提纲草案，等待用户确认。未创建 deck_spec.json、speech.md、prompts、slide_jobs、slide 图片或最终 PPTX。

## 资料基线

- 上一版 PPT：`F:/泉城实验室/二期/论文/异常检测/综合分析/园区网络流量智能检测与分析专题汇报.pptx`，27 页，用作内容基线。
- 本地论文材料：`综合分析/README.md`、`01_大类归类统计.md`、`02_创新点归类分析.md`、`04_科学问题归类分析.md`、`06_总结报告.md`、`07_代码对照总表.md`。
- 论文统计口径：858 篇论文；强相关 439 篇，中相关 251 篇，弱相关 168 篇；代码候选 145 条，已下载仓库记录 127 条，覆盖有已下载代码论文 120 篇。
- 远程系统：`root@10.0.5.8:/home/wangwt/phase_2/code/traffic-analysis-platform`，2026-07-06 复核，branch `main`，commit `e3316aec4`。
- 当前部署快照：Kubernetes 两节点 Ready，`8-2tb(10.0.5.8, control-plane)` 与 `zeus-server(10.0.5.9, worker)`，v1.29.15/openEuler；`traffic-analysis` namespace 中 Running Pod 13 个，另有历史 Completed 1 个、Error 1 个。
- 参考图：`C:/Users/LongShine/.codex/attachments/e0c0c8de-ce0b-4f94-96d4-497881068411/image-1.png`，作为 PPT 工具链与 QA 方法参考，不作为最终页面的内容图。

## 生成方式约束

- 使用 `codex-ppt` 工作流：每页最终为一张 16:9 全页图片，存放于 `origin_image/slide_XX.png`，再由技能脚本组装为 PPTX。
- 图片后端按技能要求后续确认：优先使用内置 `image_gen`，不使用本地 SVG、Pillow、HTML 截图或 PptxGenJS 手工绘制替代最终页。
- 产品架构图、技术架构图、部署图、AI 检测系统架构图必须基于已复核事实生成，不写未验证的吞吐、512Mpps、P95、准确率等达成口径。

## Slide 1: 封面

- Key points:
  - 题目：园区网络流量智能检测与分析专题汇报。
  - 副标题：从全流量采集分析平台到 AI 驱动检测、论文代码复用与验收证据闭环。
  - 标注资料来源：远程 `traffic-analysis-platform` + 本地 858 篇论文/代码分析。
- Visual idea: 深色科技感全景，园区网络、数据流、检测中枢和证据闭环形成主视觉。
- Layout role and intent: cover。
- Required images: 无。参考图仅作为制作方法参考。

## Slide 2: 汇报总览与结论先行

- Key points:
  - 本系统应定义为“园区全流量安全运营闭环”，不是单点抓包、IDS 或静态大屏。
  - 当前工程具备采集、流计算、存储、API、UI、取证、反馈与 MLOps 主链路证据。
  - AI 检测的汇报重点应落在流式检测、反馈学习、模型治理和论文代码可复测转化。
  - 验收口径必须分层，不能把架构支持写成任务书指标已达成。
- Visual idea: 结论卡片 + 三条证据链：系统、AI、论文代码。
- Layout role and intent: executive summary。
- Required images: 无。

## Slide 3: 汇报结构

- Key points:
  - 第一部分：全流量采集与分析系统整体介绍。
  - 第二部分：产品架构、技术架构、部署拓扑。
  - 第三部分：AI 驱动流量检测系统具体实现。
  - 第四部分：858 篇论文与 127 个代码仓库如何逐帧转化。
  - 第五部分：最终交付形态、验收证据与路线图。
- Visual idea: 五段式路线图，贯穿“可见、可判、可查、可学、可验”。
- Layout role and intent: agenda。
- Required images: 无。

## Slide 4: 系统定位：园区全流量安全运营闭环

- Key points:
  - 核心价值链：全流量可见 -> 多源融合 -> 智能检测 -> 告警研判 -> PCAP/图谱取证 -> 反馈学习 -> 规则/模型治理 -> 第三方可复测证据。
  - 用户角色覆盖值班员、研判员、平台管理员、测试验收人员、园区负责人。
  - 产品必须同时服务日常运营、技术验证和课题验收。
- Visual idea: 闭环环形图，中间放“园区全流量安全运营闭环”。
- Layout role and intent: concept explanation。
- Required images: 无。

## Slide 5: 园区网络全流量采集与分析系统产品架构图

- Key points:
  - 产品一级域：综合态势、采集监测、威胁分析、资产图谱、检测运营、审计配置。
  - 业务闭环：态势入口、探针健康、告警研判、PCAP 证据、资产图谱、反馈学习、规则/模型治理、验收证据包。
  - 对外入口以 Web UI / APISIX 为主，面向运营、研判、管理和验收人员。
- Visual idea: image_gen 生成产品架构全页图，业务域分层，右侧展示角色和证据闭环。
- Layout role and intent: architecture diagram。
- Required images: 无。必须基于远程设计文档与前端信息架构事实。

## Slide 6: 产品能力拆解：六大业务域如何支撑闭环

- Key points:
  - 综合态势：Dashboard、态势大屏、加密隧道/数据外传/APT 专题入口。
  - 采集监测：Probe 管理、DataQuality、吞吐/丢包/延迟/DLQ。
  - 威胁分析：Alerts、Campaigns、AttackChain、EncryptedTraffic、Forensics。
  - 资产图谱：AssetInventory、Graph、Fusion、Baselines。
  - 检测运营：Rules、Whitelist、Deployments、Models、MLOps、Playbooks。
  - 审计配置：Compliance、AuditLog、Notifications、Settings。
- Visual idea: 六宫格能力地图，每格包含入口、动作、证据。
- Layout role and intent: product capability map。
- Required images: 无。

## Slide 7: 远程代码结构实证

- Key points:
  - 仓库路径：`/home/wangwt/phase_2/code/traffic-analysis-platform`，commit `e3316aec4`。
  - Rust：`rust/probe-agent`，承接采集、流聚合、PCAP、DNS/DHCP/ARP 等。
  - Go：`go/control-plane`，承接 ingest、auth、alert、rule、asset、graph、forensics、threat-intel 等服务。
  - Java：`java/flink-jobs`，承接 session、feature、rule、behavior、CEP、alert-generator、log、pcap-index、user-behavior。
  - Web/MLOps/Proto/Common/Deployments 形成跨语言契约和部署闭环。
- Visual idea: 代码仓库树状图 + 多语言模块色块。
- Layout role and intent: evidence slide。
- Required images: 无。

## Slide 8: 数据主链路：从包到告警再回到模型

- Key points:
  - 主链路：Rust Probe -> Ingest Gateway -> Kafka -> Flink -> ClickHouse/PostgreSQL/OpenSearch/NebulaGraph/Redis/MinIO -> Go APIs -> Web UI。
  - 反馈链路：Alert Feedback / Whitelist / Rule Review / MLOps -> `rule.updates` / `model-updates` -> Flink 热更新。
  - Topic 包括 `flow.events.v1`、`session.events.v1`、`feature.stat.v1`、`detections.v1`、`alerts.v1`、`pcap.index.v1`、`alert.feedback.v1`、`model-updates`、`dlq.v1` 等。
- Visual idea: 左到右流水线，底部是反馈回流。
- Layout role and intent: process flow。
- Required images: 无。

## Slide 9: 技术架构图

- Key points:
  - 采集层：Probe DaemonSet，hostNetwork/hostPID，privileged，接口 `ens9f0`，mode `af_packet`，metrics 9091。
  - 接入与消息：Ingest Gateway gRPC 50051、Kafka SASL_SSL/SCRAM。
  - 计算层：Flink 9 类作业，完成会话化、特征、规则、行为、CEP、告警、日志、PCAP 索引、用户行为。
  - 存储层：ClickHouse、PostgreSQL、OpenSearch、NebulaGraph、Redis、MinIO。
  - 服务与展现：Go control-plane APIs、React/Vite Web UI，实时和鉴权开启，mock 关闭。
- Visual idea: image_gen 生成分层技术架构全页图，突出数据契约、topic、存储和 API。
- Layout role and intent: architecture diagram。
- Required images: 无。必须基于远程 YAML、topic 清单和代码目录事实。

## Slide 10: 技术分层详解：每层的代码与证据

- Key points:
  - `proto/traffic/v1` 是跨语言契约真源，覆盖 alert、asset、audit、campaign、detection、feature、flow、graph、ingest、pcap、session。
  - Kafka topic 初始化清单包含实时流、检测、反馈、规则、模型、审计、资产、日志、用户事件和 DLQ。
  - ClickHouse/PG/OpenSearch/Nebula/Redis/MinIO 分别承接分析、元数据、全文检索、图关系、缓存和对象证据。
  - 安全要求体现在 mTLS、JWT/OIDC、Kafka TLS/SASL、ExternalSecret、审计和入口收敛。
- Visual idea: 四层证据矩阵：代码、契约、部署、运行状态。
- Layout role and intent: technical decomposition。
- Required images: 无。

## Slide 11: 部署图

- Key points:
  - 集群节点：`8-2tb(10.0.5.8)` control-plane 与 `zeus-server(10.0.5.9)` worker，均 Ready。
  - 业务 namespace：`traffic-analysis` 中 13 个 Running Pod，包括 alert、asset、auth、forensics、graph、ingest、probe、rule、threat-intel、web-ui 等。
  - 入口：`gateway/apisix` NodePort `30180`；业务服务多为 ClusterIP。
  - 中间件：Kafka 0/1/2/bootstrap、ClickHouse 1/2/Keeper、PostgreSQL primary/replica、Redis、MinIO、Keycloak、Grafana、NebulaGraph 等。
- Visual idea: image_gen 生成 K8s 部署拓扑图，两节点、namespace、入口、数据平面与中间件分区。
- Layout role and intent: deployment topology。
- Required images: 无。必须标明 Completed/Error 为历史记录，不作为当前运行服务能力。

## Slide 12: 当前部署快照与边界

- Key points:
  - Running Pod 13 个；历史 Completed 1 个、Error 1 个需在汇报中如实说明。
  - `web-ui` 镜像为 `traffic/web-ui:ui-screen-login-clean-shield-20260706-r50`，`USE_MOCK=false`，`AUTH_ENABLED=true`，`ENABLE_REALTIME=true`。
  - APISIX 暴露 `9080:30180/TCP`，对外入口收敛到网关。
  - 不能把当前运行快照写成性能、算法、生产安全和 HA 指标已验收。
- Visual idea: 运行事实卡片 + 风险边界标识。
- Layout role and intent: factual snapshot。
- Required images: 无。

## Slide 13: 面向 AI 驱动的流量检测系统架构图

- Key points:
  - 在线检测：flow/session/feature 输入，规则、行为、CEP 与模型推理并行。
  - 表征工程：统计特征、序列特征、图上下文、资产/日志/用户行为融合。
  - 决策解释：规则命中、模型分数、相似样本、图路径、证据链接。
  - 反馈学习：TP/FP、白名单、规则复审、训练集抽取、模型评估、注册、发布、回滚。
  - 外部资产：858 篇论文、127 个已下载仓库用于 benchmark、候选模型和消融验证。
- Visual idea: image_gen 生成 AI 检测实现架构图，突出在线流式检测和 MLOps 闭环。
- Layout role and intent: architecture diagram。
- Required images: 无。必须区分“当前已有”与“建议补强”。

## Slide 14: AI 检测现状与增强方向

- Key points:
  - 当前已有：规则检测、行为检测、CEP、Alert Generator、Feedback、Whitelist、Rule Review、MLOps extract/train/evaluate/register、`model-updates`。
  - 当前可用模型工程：XGBoost/LightGBM、Precision/Recall/F1/AUC、MinIO 模型存储、Kafka 热更新接口。
  - 重点补强：DA-FDIDS、图关系模型、开放集拒识、少样本适配、跨域漂移、解释性。
  - 评估指标要加入 Unknown Recall、FPR 约束阈值、离在线一致性和冻结盲测包。
- Visual idea: “已有能力 vs 补强能力”对照图。
- Layout role and intent: comparison。
- Required images: 无。

## Slide 15: MLOps 闭环：从告警反馈到模型热更新

- Key points:
  - 数据抽取：ClickHouse features/alerts/feedback，生成训练与测试数据。
  - 训练评估：XGBoost/LightGBM、类别不平衡、交叉验证、阈值分析、混淆矩阵。
  - 注册发布：模型版本、部署记录、MinIO 对象、`model-updates`。
  - 线上回流：Flink 热更新、告警质量回看、回滚与审计。
- Visual idea: 四阶段闭环，带版本号、模型包和指标看板。
- Layout role and intent: process and governance。
- Required images: 无。

## Slide 16: DA-FDIDS 的系统落点

- Key points:
  - DA-FDIDS 应作为“AI 检测模型插件”，不是全流量平台本体。
  - 可落点：FeatureSeq/GraphContext 输入、DetectionBatch 输出、Evidence 解释、MLOps 训练发布。
  - 谨慎口径：若称开放集/基础模型，需要补齐未知类拒识、真实预训练 checkpoint、host/time/domain-disjoint 实验。
  - 与平台关系：平台提供数据、回放、评估和发布；模型提供表征、分类、拒识和解释。
- Visual idea: 插件式模型卡片嵌入平台流水线。
- Layout role and intent: technical positioning。
- Required images: 无。

## Slide 17: 858 篇论文研究地图

- Key points:
  - 最大板块：加密流量分类与应用识别 194 篇，入侵检测与网络异常检测 184 篇。
  - 其他关键板块：恶意流量/暗网/攻击检测 68 篇，图学习/知识图谱/威胁情报 63 篇，时序/日志/KPI/云原生异常 52 篇。
  - 论文分布说明系统建设要同时覆盖加密特征缺失、实时检测、多源融合和开放世界问题。
- Visual idea: 研究地图气泡图，按论文数量和系统价值排序。
- Layout role and intent: data evidence。
- Required images: 无。

## Slide 18: 相关性与代码可用性

- Key points:
  - 强相关 439 篇，中相关 251 篇，弱相关 168 篇。
  - 代码候选记录 145 条，已下载仓库记录 127 条，覆盖有已下载代码论文 120 篇。
  - 强相关 + 已下载代码优先进入复现、benchmark 和系统插件候选。
  - 中弱相关用于方法迁移、背景综述、鲁棒性和评审补充。
- Visual idea: 漏斗图：858 -> 439 强相关 -> 120 已下载代码覆盖 -> 复现候选池。
- Layout role and intent: data evidence。
- Required images: 无。

## Slide 19: 论文科学问题如何映射到系统需求

- Key points:
  - 加密与隐私造成可观测特征缺失 320 篇，要求元数据、时序、统计、图关系建模。
  - 高速流量实时检测与资源约束 249 篇，要求轻量特征、分层检测和流式推理。
  - 多源异构融合与上下文建模 241 篇，要求流量、资产、日志、告警、威胁情报统一。
  - 开放世界、漂移、标签稀缺、对抗规避和可解释性需要独立门禁。
- Visual idea: 科学问题到系统组件的 Sankey 映射。
- Layout role and intent: research-to-system mapping。
- Required images: 无。

## Slide 20: 论文创新点如何转化为工程模块

- Key points:
  - 数据集、基准、工具与系统化评测 442 篇 -> 验收样本、benchmark、回放脚本。
  - 轻量化、实时与高性能部署 231 篇 -> Probe/Flink/模型压缩/分层检测。
  - 表征学习、预训练与 Transformer 206 篇 -> 统一流量表征和自监督预训练。
  - 图神经网络与关系建模 109 篇 -> 主机-流-告警-情报图谱。
  - 在线、增量、开放集与漂移 67 篇 -> MLOps、阈值锁、拒识、回滚。
- Visual idea: 五条“论文簇 -> 工程模块 -> 验收证据”链路。
- Layout role and intent: research-to-engineering。
- Required images: 无。

## Slide 21: 逐帧使用论文 - Frame 1 需求与科学问题

- Key points:
  - 先用论文统计定义为什么系统必须处理加密、实时、多源、开放集、漂移、标签稀缺和可解释性。
  - 输出物：需求追溯矩阵、科学问题矩阵、验收指标边界。
  - 避免做法：只列论文标题，不说明每类论文如何改变系统设计。
- Visual idea: 文献证据板 + 系统需求矩阵。
- Layout role and intent: paper-use frame。
- Required images: 无。

## Slide 22: 逐帧使用论文 - Frame 2 技术路线筛选

- Key points:
  - 将 439 篇强相关论文分到加密流量、NIDS、恶意流量、图学习、在线部署、MLOps/评测等簇。
  - 每簇选择 3-5 个可落地候选：有代码、数据线索、训练入口、模型文件或可复现指标者优先。
  - 输出物：模型候选池、特征候选池、评估协议候选池。
- Visual idea: 技术路线雷达 + 候选池卡片。
- Layout role and intent: paper-use frame。
- Required images: 无。

## Slide 23: 逐帧使用论文 - Frame 3 开源代码复现库

- Key points:
  - 表征与预训练：FS-Net、ET-BERT、TrafficFormer、TrafficLLM、YaTC、UniNet。
  - 图与开放集：FIR-GNN、HyperVision、DawnGuard、ERFS、FeCoGraph、Sieve、Open-Detect。
  - 实时与工具：Marina、NTLFlowLyzer、FastTraffic、CENTIME。
  - 漂移与鲁棒：CADE、DAIR-FedMoE、Rosetta、BPF-DAG 等。
  - 输出物：repo 体检表、依赖镜像、数据适配器、训练/评估脚本。
- Visual idea: 开源组件库货架图，按复用类型分区。
- Layout role and intent: open-source reuse。
- Required images: 无。

## Slide 24: 逐帧使用论文 - Frame 4 Benchmark 与消融实验

- Key points:
  - 构建统一输入契约：FlowEvent、Session、FeatureStat、FeatureSeq、GraphContext。
  - 构建统一输出契约：DetectionBatch、Evidence、ReasonCode、ModelVersion。
  - 对比指标：Accuracy、Precision、Recall、F1、AUC、FPR、Unknown Recall、P95、资源开销。
  - 输出物：冻结数据包、标签规范、消融表、错误样本库。
- Visual idea: Benchmark 工厂流水线。
- Layout role and intent: evaluation design。
- Required images: 无。

## Slide 25: 逐帧使用论文 - Frame 5 系统插件化接入

- Key points:
  - 把论文模型从离线脚本改造成可注册、可回放、可灰度、可回滚的检测插件。
  - 插件边界：输入特征、模型文件、阈值、原因码、解释证据、资源预算。
  - 接入位置：Flink 侧在线推理、Go API 模型管理、MLOps 训练发布、Web UI 展示解释。
  - 输出物：模型插件规范、推理服务接口、离在线一致性测试。
- Visual idea: 模型插件卡接入平台总线。
- Layout role and intent: implementation frame。
- Required images: 无。

## Slide 26: 逐帧使用论文 - Frame 6 验收证据与第三方复测

- Key points:
  - 论文和代码最终不是“引用列表”，而是验收证据包的算法、样本、指标和报告来源。
  - 必须固化 commit、镜像、manifest、DDL、topic、样本、标签、模型、规则和报告。
  - 第三方复测需要冻结盲测包、P95 统计、压测报告、混淆矩阵、未知类召回、审计记录。
  - 输出物：可复现实验包、验收报告模板、现场试点材料。
- Visual idea: 证据包封装图，论文/代码/系统/指标进入同一封包。
- Layout role and intent: acceptance frame。
- Required images: 无。

## Slide 27: 强相关优先清单与落地顺序

- Key points:
  - 第一优先：加密流量与恶意流量早期检测，如 DawnGuard、SnifferDog、HyperVision、BPF-DAG。
  - 第二优先：NIDS 与图关系，如 FIR-GNN、E-GraphSAGE、TFE-GNN、Open-CyKG/Krystal。
  - 第三优先：预训练与表征，如 ET-BERT、TrafficFormer、YaTC、TrafficLLM。
  - 第四优先：实时工具与特征，如 FastTraffic、CENTIME、NTLFlowLyzer。
  - 所有优先项必须经过可复现、可解释、可上线、可回滚四道门。
- Visual idea: 优先级路线板。
- Layout role and intent: prioritization。
- Required images: 无。

## Slide 28: 验收边界：哪些可以讲，哪些不能提前承诺

- Key points:
  - 可讲：功能主链路具备强证据，远程运行和代码结构支持演示与功能回归。
  - 需专项验证：10 x 100Gbps、512Mpps、P95 <= 60s。
  - 需第三方验证：准确率 >=95%、误报率 <5%、Unknown Recall、生产安全与 HA。
  - 汇报中必须把“工程链路已具备”和“任务书指标已验收”分开。
- Visual idea: 红黄绿验收边界表。
- Layout role and intent: risk and acceptance。
- Required images: 无。

## Slide 29: 最终应该呈现出的成果形态

- Key points:
  - 可演示系统：真实 API、态势大屏、告警、图谱、PCAP、反馈、模型管理。
  - 可运行链路：Probe/Kafka/Flink/CH/PG/OS/Nebula/Redis/MinIO/Go API/K8s manifest 可追踪。
  - AI 模型包：规则+行为+CEP 已有链路，DA-FDIDS/图/开放集/预训练模型以插件化进入 MLOps。
  - 论文代码证据：858 篇研究地图、127 个仓库、benchmark、复现日志、消融表。
  - 验收证据包：指标、压测、第三方盲测、试点、经济效益和审计材料。
- Visual idea: 五件最终交付物并列。
- Layout role and intent: target deliverables。
- Required images: 无。

## Slide 30: 实施路线图

- Key points:
  - M1：冻结架构与证据，固化 commit、镜像、K8s、topic、DDL、样本和口径。
  - M2：AI 检测 MVP，打通 FeatureStat/Seq -> DetectionBatch -> Evidence -> UI。
  - M3：开放集与图增强，完成 DA-FDIDS/图上下文/相似样本解释的离线消融。
  - M4：MLOps 与灰度，完成反馈样本池、阈值锁、注册、热更新、回滚和审计。
  - M5：专项验收，完成 P95、100G/512Mpps、95%/5%、安全/HA、第三方盲测和试点报告。
- Visual idea: 五阶段路线图，标明每阶段产出。
- Layout role and intent: roadmap。
- Required images: 无。

## Slide 31: 风险控制

- Key points:
  - 风险 1：模型离线高分但线上无证据；控制：统一特征契约、离在线一致性、Evidence 可追溯。
  - 风险 2：论文代码难复现；控制：强相关+已下载代码优先，输出数据适配、指标 JSON、复现日志。
  - 风险 3：架构图脱离实际；控制：每个图节点绑定远程代码、YAML、topic 或服务事实。
  - 风险 4：指标提前承诺；控制：汇报口径按功能主链路、专项验证、第三方验证分层。
- Visual idea: 风险-控制矩阵。
- Layout role and intent: risk control。
- Required images: 无。

## Slide 32: 结论

- Key points:
  - 用真实全流量工程底座承接 AI 检测。
  - 用论文代码证据链支撑可复测创新。
  - 用 MLOps 与反馈闭环解决长期运营。
  - 用验收证据包确保“看得见、判得准、查得到、说得清、学得动、验得过”。
- Visual idea: 深色收束页，六个关键词形成闭环。
- Layout role and intent: closing。
- Required images: 无。

## 需要用户确认的事项

1. 是否批准以上 32 页提纲作为 `codex-ppt` 版正式结构。
2. 是否同意把参考图 `image-1.png` 仅作为方法参考，而不放入最终 PPT 页面。
3. 是否同意后续每页均按 `codex-ppt` 工作流生成整页图片，再组装为 PPTX。

确认后才能进入下一阶段：视觉风格确认、图片后端确认、生成 1 页样张。
