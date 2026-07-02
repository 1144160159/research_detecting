# [592] Accurate and Scalable Detection and Investigation of Cyber Persistence Threats

## 1. 基本信息

- 论文：Accurate and Scalable Detection and Investigation of Cyber Persistence Threats
- 年份：2026
- 来源：IEEE Transactions on Dependable and Secure Computing
- DOI：10.1109/TDSC.2026.3689905
- 作者：Qi Liu、Muhammad Shoaib、Mati Ur Rehman、Kaibin Bao、Veit Hagenmeyer、Wajih Ul Hassan
- 主题：APT 持久化威胁检测、数据溯源图、告警降噪、攻击调查
- 本地代码状态：未发现该论文对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文提出 Cyber Persistence Detector，简称 CPD，专门检测 APT 中的“持久化”威胁。作者认为现有 PIDS 和 SIEM 规则都没有真正理解持久化：它不是单个敏感动作，例如写注册表 Run Key，而是由“持久化设置”和“持久化执行”两个阶段组成。只有当某个设置动作后来导致攻击者重新连回、维持访问或继续执行远程通信时，它才构成真正有安全意义的持久化。

CPD 的核心做法是：先从审计日志中识别潜在持久化设置，再从远程连接相关进程出发做反向溯源，判断是否存在对应的持久化执行，最后用伪依赖边把原本断开的两个阶段连接起来。为了解决 Windows/Linux 日志缺失 IPC 或系统例程边的问题，论文还提出 expert-guided edges，用专家规则补上例如 `sc.exe` 与 `services.exe`、systemd service 文件与 cgroup 运行实体之间的语义连接。最后，CPD 用多阶段攻击上下文对伪边打分，减少 benign updater、OneDrive、Chrome 等正常程序带来的假阳性。

## 3. 论文解决的具体问题

论文瞄准的问题不是一般异常检测，而是企业终端中 APT 持久化行为的准确检测与调查。传统规则系统看到注册表自启动项、计划任务、服务创建等敏感行为就报警，但大量正常软件也会这样做，导致 SOC 告警疲劳。相反，如果规则为了降噪而大量 allowlist 标准目录或常见程序，又会漏掉攻击者滥用 LOLBins 和正常路径的攻击。

现有 provenance-based IDS 也有短板：学习型 PIDS 假设攻击行为偏离正常模式，但持久化常常使用系统合法机制，未必异常；启发式 PIDS 能重建局部攻击图，却容易被 APT 的“低速、分阶段、断开后重连”策略切断上下文。持久化恰好会跨时间、跨重启、跨日志片段发生，因此普通前向/后向追踪很难把设置和执行连成完整攻击图。

## 4. 创新点深度提炼

第一，论文把持久化重新定义为一个两阶段因果问题：setup 是准备，execution 才暴露攻击者继续访问的意图。这比“访问敏感功能即报警”的规则范式更接近攻击语义。

第二，CPD 引入 pseudo-dependency edge，将日志中没有真实依赖边的两个阶段人为连接起来。这不是随意拼接，而是基于 TTP 标签、时间先后、技术特定属性和远程连接可追溯性建立的语义边。

第三，expert-guided edges 解决了系统日志天然缺边的问题。作者没有简单要求采集 ALPC 等高成本 IPC 日志，而是把操作系统机制知识嵌入图重建，例如服务创建、systemd 启动路径等。

第四，论文把告警降噪从单点规则过滤提升为攻击链上下文排序：是否有凭证访问、发现、横向移动、工具传输、多种持久化组合、间接调用链等，都会影响伪边威胁分数。

第五，CPD 输出的是精简 persistence attack graph，而不是只有二分类告警。图中明确呈现设置、执行、远程连接和伪边，服务于调查而不仅是检测。

## 5. 科学问题与研究假设

核心科学问题是：在日志不完整、攻击分阶段且大量行为看似合法的情况下，能否用溯源图准确识别真正的持久化威胁，并显著降低误报？

论文的主要假设包括：持久化攻击普遍具有 setup 与 execution 两阶段；真正有意义的持久化 execution 通常会与远程连接、重连、远程服务或后续 C2 行为相关；MITRE ATT&CK 中的持久化技术可被抽象为相对稳定的行为规则，而不是易变 IOC；操作系统和日志基础设施处于可信计算基内；攻击者没有破坏 OS 内核、固件或日志服务本身。

另一个隐含假设是：APT 持久化往往不是孤立动作，而是与凭证访问、发现、横向移动、防御规避等阶段在因果图附近共同出现。因此上下文可以用于区分 benign persistence-like behavior 和 malicious persistence。

## 6. 科学方法与技术路线

CPD 的技术路线可以概括为四步。第一步，针对 MITRE 持久化技术、威胁报告、Atomic Red Team、Sigma/Elastic 等规则库设计 persistence setup rules，生成 setup table。第二步，从所有有远程连接的进程出发做 backward tracing，检查路径上是否满足 persistence execution rules，生成 execution table。第三步，对 setup 与 execution 按 TTP 标签、时间顺序和技术特定属性对齐，提取两个 atomic graph，并创建 pseudo-edge。第四步，对伪边进行分类、上下文扩展、指标提取和威胁打分，按告警预算保留高风险结果。

关键技术对象有三类图：真实依赖图表示审计日志可见的因果关系；atomic graph 只保留持久化设置或执行的关键节点；dependency graph 在告警降噪阶段向前/向后扩展，用于寻找攻击链上下文指标。

## 7. 实验设计与实验步骤

数据：作者使用 DARPA E5 Fivedirections、DARPA OpTC、ATLASv2，以及自行严格复现 MITRE emulation plans 得到的 EP-APT29-1、EP-APT29-2、EP-Sandworm-1。数据规模从 24GB 到 380GB，事件数从 560 万到 14 亿不等。

预处理：Windows 侧使用 Sysmon、Windows Security Audit、必要时 ETW NT Kernel Logger；Linux 侧使用 Auditd。日志进入 Elasticsearch，通过 EQL 查询匹配规则，再按需用 NetworkX 生成溯源图，PyVis 可视化。

模型/基线：比较对象包括 Elastic、Sigma、Google Chronicle 的开源 SIEM 规则，VMware Carbon Black Cloud EDR，以及 KAIROS、FLASH、MAGIC、ORTHRUS、VELOX 等学习型 PIDS。

训练：CPD 本身不需要训练数据；学习型 PIDS 使用作者提供预训练模型，并在 OpTC 上调参，重复运行五次以缓解神经模型不稳定性。

指标：主要看 FP、FN、告警削减率、攻击是否检测到、运行时间、内存、专家引导边带来的日志削减率，以及 cPrecision@k、NDCG@k 评估威胁分数排序。

消融/敏感性：论文通过 CPD Stage 1/2/3 的结果比较展示各阶段贡献；expert-guided edges 的贡献用 ALPC 日志替代成本进行比较；Stage 3 的阈值以最低真实攻击分数为参考，另有告警预算 N 控制最终输出。

结果核查：真实攻击用数据集 ground truth 与 MITRE emulation 行为核对；图级结果通过示例图展示，例如 APT29 startup folder、OpTC WMI Event Subscription，以及 OneDrive 假阳性案例。

## 8. 关键结果、结论与证据

最重要结果是：CPD 相比现有方法平均降低 93% 假阳性，同时保持对真实持久化攻击的检测能力。表 V 中，CPD Stage 1 会产生数千到数万 FP，但 Stage 2 通过“setup 后必须存在可追溯远程 execution”大幅压缩，Stage 3 再通过上下文打分把 FP 压到个位数到几十级别。

与 SIEM 规则相比，Elastic 因 allowlist 和硬编码条件过强出现明显 FN；Sigma 因规则过泛和重复规则导致 FP 极高；Chronicle 介于两者之间但也有漏报。与 CBC EDR 在 ATLASv2 上比较，CPD Stage 2 将 FP 从 1602 降到 11，而 CBC 为 56。

与学习型 PIDS 在 OpTC Host 0501 上比较，CPD 同时检测到 persistence setup 和 execution，运行约 2 分钟；KAIROS、FLASH、MAGIC 多数只能碰到 setup，ORTHRUS 和 VELOX 连 setup 也未稳定检测到。CPD 还比这些 PIDS 快至少 39 倍，内存消耗也低。

expert-guided edges 使系统不必依赖高成本 ALPC 日志，在三个 emulation 数据集上日志削减率为 20%、38%、53%。这说明作者不是简单“多采日志换准确率”，而是在准确性与可部署性之间做了工程折中。

## 9. 局限性与待解决问题

正文包未截断，本次理解基于完整提供文本，不存在必须回 PDF 复核截断部分的问题。但论文仍是作者版 accepted manuscript，正式出版版可能有细节改动。

CPD 不覆盖全部 99 个 MITRE 持久化子技术，排除了 macOS、云基础设施、pre-OS boot/Bootkit 等场景。它依赖 OS 与日志系统可信，若攻击者获得内核级能力或破坏日志链路，CPD 不具备检测保证。

规则和指标仍需维护。作者强调使用的是较稳定的行为与路径/注册表位置，但 MITRE ATT&CK 会扩展，新的持久化技术和云原生持久化方式需要补充。expert-guided edges 当前也主要靠专家知识，不是自动学习得到，扩展到更多 OS 机制、更多软件生态时会有维护成本。

Stage 3 的威胁排序不是绝对分类器，而是服务于告警预算的优先级系统。表 VI 中 EP-APT29-2 的 cPrecision@5 为 0，说明在某些场景下真实攻击未排进前 5，SOC 若预算过小仍可能漏看。

## 10. 与本项目的关系

该论文与“恶意流量、暗网与攻击检测”的关系很强，但更准确地说，它是“主机溯源 + 持久化检测 + 远程连接语义”的交叉工作。它没有只看网络流量，而是把远程连接作为 persistence execution 的关键证据，再回到主机事件中追溯触发来源。

如果本项目关注异常检测综述，CPD 可以作为一个反例提醒：不是所有安全检测都适合纯异常学习。APT 持久化经常使用正常机制，异常分数未必可靠，语义建模和攻击链上下文更关键。

如果本项目做实验系统，CPD 的可借鉴点是：先用高召回规则定位敏感 setup，再用因果图和远程连接确认 execution，最后用上下文排序降噪。这条路线比直接训练图神经网络更可解释，也更贴近 SOC 调查流程。

## 11. 代码对照分析

本地未发现论文对应开源代码包，因此不能做真实源码级定位。根据论文实现描述，CPD 原型约 6000 行 Python，运行在 Ubuntu 23.04，依赖 Elasticsearch/EQL、NetworkX、PyVis，并处理 Sysmon、Windows Security Audit、Auditd、ETW ALPC 日志。

若代码存在，最可能对应如下模块：日志接入与标准化模块负责解析 Sysmon/Security Audit/Auditd/ETW；规则模块保存 persistence setup rules 与 execution rules，并将其转换为 EQL；图构建模块基于进程、文件、注册表、socket 事件创建溯源图；追踪模块实现 backward/forward traversal；pseudo-edge 模块实现 Algorithm 1；expert-guided edge 模块实现 Algorithm 2；triage/scoring 模块实现 Algorithm 3 和三类伪边指标；evaluation 模块复现表 V-X 的 FP/FN、运行时间、内存与排序指标。

运行线索大致应是：先将数据集日志导入 Elasticsearch，执行 setup 规则生成表；枚举远程连接进程并反向追踪；对齐 setup/execution 生成伪边与 atomic graph；扩展 dependency graph 计算威胁分数；最后导出告警列表和 PyVis 图。

## 12. 本篇精华

- 持久化检测的关键不是“是否写了敏感位置”，而是“敏感设置是否导致后续远程重连或 C2 执行”。
- CPD 用 pseudo-edge 把跨时间、跨重启、日志中天然断开的 setup 与 execution 连成可调查攻击图。
- expert-guided edges 是很实用的工程贡献：用 OS 机制知识替代高成本 IPC 全量采集。
- CPD 的检测策略是高召回规则 + 溯源确认 + 上下文排序，而不是单纯规则匹配或端到端图学习。
- 学习型 PIDS 在持久化场景容易只发现 setup，无法理解 execution 与重连语义。
- 正常软件更新器是持久化检测最大的假阳性来源之一，必须结合攻击链上下文降噪。
- 论文的实验价值在于补足公共数据集缺少真实持久化的缺陷，复现了 APT29 和 Sandworm 的 MITRE emulation plans。
- 对 SOC 来说，CPD 的产物不是孤立告警，而是带 setup、execution、远程连接和上下文的精简调查图。

## 13. 建议精读路线

先读 Introduction 和 Motivation，重点理解作者为什么说持久化被现有研究误解，尤其是 setup、code linkage、remote execution 三个条件。

第二遍读 System Design，画出四阶段流程：setup table、remote-process backward tracing、pseudo-edge creation、false positive reduction。Algorithm 1-3 是全文核心。

第三遍读 Table III、Figure 3、Figure 5、Figure 8。它们分别对应规则敏感性、真阳性攻击图、正常软件假阳性、WMI 持久化案例，比公式更能帮助理解 CPD 的判断逻辑。

最后读 Evaluation 和 Limitations。关注表 V、VIII、IX：它们分别回答 CPD 是否比规则系统准、是否比学习型 PIDS 更适合持久化、expert-guided edges 是否有工程价值。

<!-- codex-cli-deep-read: complete -->
